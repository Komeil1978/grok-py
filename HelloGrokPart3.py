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
PROJECT_ID = '285'
JOIN_FILE = 'data/workSchedule.csv'
JOIN_FILE_SPEC = 'data/joinFileSpecification.json'
INPUT_CSV = 'data/rec-center-advanced-tiny.csv'
STREAM_SPEC = 'data/advancedSpec.json'
OUTPUT_CSV = 'output/SwarmOutputPart3.csv'

##############################################################################
# API KEY NOTE: A more secure method is to store your API key in your
# shell environment.
#
# From the command line:
#  echo "export GROK_API_KEY=YOUR_KEY_HERE" >> ~/.bashrc
#  source ~/.bashrc

def HelloGrokPart3():

  # Setup
  grok = Client(API_KEY, 'http://dailystaging.numenta.com:1961')
  now = time.time()
  myProject = grok.createProject('FileProvTesting' + str(now))

  print 'STARTING PROJECT DEF'
  print myProject.getDescription()
  print '=' * 40

  ##############################################################################
  # Create a new model
  #
  # When dealing with new way to look at a data in a stream you will need to
  # create a new model to work with. In this case we're adding in new types of
  # data so we'll need a new stream as well.
  print 'Creating an new model ...'
  advancedModel = myProject.createModel()

  print 'Creating an new stream ...'
  newStream = myProject.createStream()
  newStream.configure(STREAM_SPEC)

  ##############################################################################
  # Upload a file to use as a lookup table.
  #
  # Data can be added to a stream dynamically by Grok. First we're going to
  # give Grok a file to use as its database. Later we'll configure our stream
  # so that each time a new record comes in, Grok will automatically add in
  # data pulled from this file. Here we want to know who was managing the
  # rec center on a given day, so our file lists days and who works them.

  myJoinFile = myProject.createJoinFile(JOIN_FILE, JOIN_FILE_SPEC)

  # Which field in our join file should serve as the primary key?
  joinFileKey = 'day'
  # Which field in the stream we want to join to that key
  streamKey = 'dayOfWeek'
  newStream.useJoinFile(myJoinFile, joinFileKey, streamKey)

  # Take a look at available Public Data Sources
  publicDataSources = grok.listPublicDataSources()
  for pds in publicDataSources:
    print pds.name, ':', pds.longDescription, 'Id:', pds.id


  ##############################################################################
  # Add weather data to the stream
  #
  # Our advanced dataset now contains a geolocation field. In this case a
  # zipcode. Using a zipcode, or lat,long pair, or an IP address Grok can
  # look up what the weather was like near that location for a given timestamp
  # and return a set of weather values like temperature, or visibility.
  # So for each record that we send in with location and time, we get weather
  # data with very little effort!

  # Get a Public Data Source to configure
  weather = grok.getPublicDataSource('weather')

  '''
  weather = {
    sourceId: 'lsk3lkjdkj2l3kjndk',
    locationFieldName: 'zip',
    timeFieldName: 'timestamp',
    weatherTypes: ['TEMP', 'VIS']
  }
  newStream.usePublicDataSource(weather)

  ##############################################################################
  # Add twitter data to the stream
  #
  # It may be that the trends on Twitter are related to what you want to
  # predict. Grok gives you the ability to explore Twitter keyword trends with
  # the data you provide. Here we will ask Grok to count how many mentions
  # the words 'gym' and 'excercise' have on Twitter for the time period of
  # each record. (Pre-aggregated to one hour)

  twitter = {
    sourceId: 'lkj2kl#$@#Clkjsdkjf',
    timeFieldName: 'timestamp',
    keywords: ['gym', 'exercise']
  }

  newStream.usePublicDataSource(twitter)
  '''
  ##############################################################################
  # Add local data to the stream
  #
  # As soon as Grok receives records it will begin joining in data from the
  # file we uploaded, Grok weather data, and Grok Twitter data, creating an uber
  # stream.

  print 'Adding local records to stream ...'
  fileHandle = open(INPUT_CSV, 'rU')
  recCenterData = [row for row in csv.reader(fileHandle)]
  fileHandle.close()
  newStream.addRecords(recCenterData)

  # Set which stream this model will listen to.
  print 'Attaching model to stream ...'
  advancedModel.setStream(newStream)

  # Define how our Model will use our Stream
  advancedModel.setTemporalField('timestamp')
  advancedModel.setPredictionField('consumption')

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

    if jobStatus == grokpy.Status.COMPLETED:
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

  ##############################################################################
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
  print "Saving results to " + OUTPUT_CSV
  fileHandle = open(OUTPUT_CSV, 'w')
  writer = csv.writer(fileHandle)
  writer.writerow(headers)
  writer.writerows(resultRows)
  fileHandle.close()

def signal_handler(signal, frame):
  print frame.f_locals
  model = frame.f_locals.get('advancedModel')
  if model:
    model.stopSwarm()
  sys.exit(0)

if __name__ == '__main__':
  HelloGrokPart3()
