#!/usr/bin/env python

##############################################################################
# Hello Grok - Part Three
#
# In this tutorial we will explore advanced streams. We will:
#  Join data with a file we upload, using it as a lookup table
#  Join data with Grok's public data sources:
#    Weather
#    Twitter

##############################################################################

import time
import csv
import os
import signal
import sys
import json
import grokpy

from grokpy import Client

##############################################################################
# Configuration Settings

API_KEY = 'YOUR_KEY_HERE'
JOIN_FILE = 'data/workSchedule.csv'
JOIN_FILE_SPEC = 'data/joinFileSpecification.json'
SWARM_INPUT_CSV = 'data/rec-center-advanced-swarm.csv'
STREAM_SPEC = 'data/advancedSpec.json'
SWARM_OUTPUT_CSV = 'output/advancedSwarmOutput.csv'
PRODUCTION_INPUT_CSV = 'data/rec-center-advanced-stream.csv'
PRODUCTION_OUTPUT_CSV = 'output/advancedStreamOutput.csv'

##############################################################################
# API KEY NOTE: A more secure method is to store your API key in your
# shell environment.
#
# From the command line:
#  echo "export GROK_API_KEY=YOUR_KEY_HERE" >> ~/.bashrc
#  source ~/.bashrc

def HelloGrokPart3():

  # Setup
  grok = Client(API_KEY)
  now = time.time()
  myProject = grok.createProject('FileProvTesting' + str(now))

  ##############################################################################
  # Create a new model
  #
  # When dealing with new ways to look at data in a stream you will need to
  # create a new model to work with. In this case we're adding in new types of
  # data so we'll need a new stream as well.
  print 'Creating a new model ...'
  advancedModel = myProject.createModel()

  print 'Creating a new stream ...'
  newStream = myProject.createStream()
  newStream.configure(STREAM_SPEC)

  ##############################################################################
  # Upload a file to use as a lookup table.
  #
  # Data can be added to a stream dynamically by Grok. First we're going to
  # give Grok a file to use as its database. Later we'll configure our stream
  # so that each time a new record comes in, Grok will automatically add in
  # data pulled from this file. Here we want to know who was managing the
  # rec center on a given day, so our file lists days and who works on each of
  # them.

  myJoinFile = myProject.createJoinFile(JOIN_FILE, JOIN_FILE_SPEC)

  # Which field in our join file should serve as the primary key?
  myJoinFile.setFileKey('day')

  # Which field in the stream we want to join to that key
  myJoinFile.setStreamKey('dayOfWeek')
  newStream.useJoinFile(myJoinFile)

  ##############################################################################
  # Public Data Sources
  #
  # Grok provides a few Public Data Sources. These are databases from which
  # we can pull useful information to be joined with your stream. Let's take
  # a look at what Public Data Sources are available.

  publicDataSources = grok.listPublicDataSources()
  print 'Available Public Data Sources:'
  for pds in publicDataSources:
    print '\t', pds.name, ':', pds.longDescription, 'Id:', pds.id

  ##############################################################################
  # Add weather data to the stream
  #
  # Our advanced dataset contains a location field. In this case a
  # zipcode. Using a zipcode* Grok can look up what the weather was like near
  # that location for a given timestamp and return a set of weather values like
  # temperature, or visibility.
  #
  # For each record that we send in with location and time, we get weather
  # data with very little effort!
  #
  # * Or a 'lat,long' pair, or an IP address.

  weather = grok.getPublicDataSource('weather')
  weather.useField('TEMP')
  # Weather provider needs to know where the location field is, you can also
  # pass in the field index if you know it.
  weather.setConfiguration(locationFieldName = 'zipcode')

  # Add it to the stream
  print 'Adding Public Data Source: Weather'
  newStream.usePublicDataSource(weather)

  ##############################################################################
  # Add twitter data to the stream
  #
  # It may be that the trends on Twitter are related to what you want to
  # predict. Grok gives you the ability to explore Twitter keyword trends with
  # the data you provide. Here we will ask Grok to count how many mentions
  # the words 'gym' and 'excercise' appeared on Twitter for the time period of
  # each record.

  twitter = grok.getPublicDataSource('twitter')

  keywords = ['gym','exercise']
  twitter.setConfiguration(keywords)

  print 'Adding Public Data Source: Twitter'
  newStream.usePublicDataSource(twitter)

  ##############################################################################
  # Add local data to the stream
  #
  # As soon as Grok receives records it will begin joining in data from the
  # file we uploaded, Grok weather data, and Grok Twitter data, creating an UBER
  # stream. (Note: Not actually called an uber-stream)

  print 'Adding local records to stream ...'
  fileHandle = open(SWARM_INPUT_CSV, 'rU')
  recCenterData = [row for row in csv.reader(fileHandle)]
  fileHandle.close()
  newStream.addRecords(recCenterData)

  # Set which stream this model will listen to.
  print 'Attaching model to stream ...'
  advancedModel.setStream(newStream)

  # Define how our Model will use our Stream
  advancedModel.setTemporalField('timestamp')
  advancedModel.setPredictionField('consumption')
  advancedModel.setTimeAggregation('HOURS')

  # Start the Swarm
  print 'Starting Grok Swarm'
  advancedModel.startSwarm()

  # Monitor the swarm
  started = False

  # Catch ctrl-c to terminate remote long-running processes
  signal.signal(signal.SIGINT, signal_handler)

  while True:
    SwarmState = advancedModel.getSwarmProgress()
    jobStatus = SwarmState['jobStatus']
    results = SwarmState['results']
    #print SwarmState

    if jobStatus == grokpy.Status.COMPLETED:
      if SwarmState['completionReason'] == 'ERROR':
        errorMsg = SwarmState['completionMessage']
        print 'Oh no! Something went wrong: ' + errorMsg
        sys.exit(1)
      else:
        print 'You win! Your Grok Swarm is complete.'
        break
    if jobStatus == grokpy.Status.RUNNING and started == False:
      started = True
      print 'Swarm started.'
    if not started:
      print 'Swarm is starting up ...'
      time.sleep(2)
      continue
    if not results:
      print 'Initial records are being processed ...'
      time.sleep(2)
      continue

    bestConf = str(results['bestModel'])
    bestValue = results['bestValue']
    print ("Current best model: " + bestConf + " - ErrorScore %.2f" % bestValue)
    time.sleep(1)

  # Retrieve Swarm results
  print "Getting results from Swarm ..."
  swarmResults = advancedModel.getSwarmResults()
  headers = swarmResults['columnNames']
  resultRows = swarmResults['rows']

  # Align predictions with actuals
  resultRows = grok.alignPredictions(headers, resultRows)

  # Write results out to a CSV
  if not os.path.exists('output'):
    print 'Output directory not found, creating ...'
    os.mkdir('output')
  print "Saving results to " + SWARM_OUTPUT_CSV
  fileHandle = open(SWARM_OUTPUT_CSV, 'w')
  writer = csv.writer(fileHandle)
  writer.writerow(headers)
  writer.writerows(resultRows)
  fileHandle.close()

  ##############################################################################
  # Promote and use your advanced model

  print 'Promoting model and updating model id ...'
  advancedModel.promote()

  # Data in, predictions out
  fileHandle= open(PRODUCTION_INPUT_CSV)
  newRecords = [row for row in csv.reader(fileHandle)]
  fileHandle.close()

  print 'Sending new data ...'
  advancedModel.sendRecords(newRecords)

  # Get all the new predictions
  then = time.time()
  headers, resultRows = advancedModel.monitorPredictions(endRow = 1462)

  # Align predictions with actuals
  resultRows = grok.alignPredictions(headers, resultRows)

  # Write out predictions to a CSV
  if not os.path.exists('output'):
    print 'Output directory not found, creating ...'
    os.mkdir('output')
  print "Saving results to " + PRODUCTION_OUTPUT_CSV
  fileHandle = open(PRODUCTION_OUTPUT_CSV, 'w')
  writer = csv.writer(fileHandle)
  writer.writerow(headers)
  writer.writerows(resultRows)
  fileHandle.close()

  # Cleanup
  myProject.stopAllModels()

  print "\n\nFantasmic! You've completed Part Three."
  print ("Now it's time to start working with your own data. Get to it!")

def signal_handler(signal, frame):
  model = frame.f_locals.get('advancedModel')
  if model:
    model.stopSwarm()
  else:
    print 'Caught ctrl-c but failed to stop in progress swarm. :('
  sys.exit(0)

if __name__ == '__main__':
  HelloGrokPart3()
