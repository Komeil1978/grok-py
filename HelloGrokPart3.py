#!/usr/bin/env python

##############################################################################
# Hello Grok - Part Three
#
# In this tutorial we will explore advanced streams. We will:
#  Create a Project to organise our models.
#  Join data with Grok's a public data source:
#    Weather

##############################################################################

import time
import csv
import os
import signal
import sys
import json
import grokpy

from math import floor

##############################################################################
# Configuration Settings

API_KEY = 'YOUR_KEY_HERE'
SWARM_INPUT_CSV = 'data/rec-center-advanced-swarm.csv'
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
  print 'Connecting to Grok ...'
  grok = grokpy.Client(API_KEY)
  now = time.time()

  ##############################################################################
  # Create a Project
  #
  # Projects are an organizational structure like folders for models. They
  # provide all the same methods as the top level client.
  print 'Creating a Project ...'
  myProject = grok.createProject('Hello Grok Part 3' + str(now))

  ##############################################################################
  # Create our stream specification
  #
  # Previously we pulled the specification for our stream out of json file.
  # Here we will build it up as an object, both to demonstrate the alternate
  # method and so we can explain each step as we add in public data sources
  #
  # Note: Until we call createStream(streamSpec) all these operations are local.
  print 'Defining our stream ...'
  streamSpec = grokpy.StreamSpecification()
  streamSpec.setName('Advanced Stream ' + str(now))

  ##############################################################################
  # Local Data

  # Create our local data source
  local = grokpy.LocalDataSource()
  local.setName('Local CSV Data')

  # Create each of our fields
  timestamp = grokpy.DataSourceField()
  timestamp.setName('timestamp')
  timestamp.setType(grokpy.DataType.DATETIME)
  timestamp.setFlag(grokpy.DataFlag.TIMESTAMP)

  consumption = grokpy.DataSourceField()
  consumption.setName('consumption')
  consumption.setType(grokpy.DataType.SCALAR)

  zipcode = grokpy.DataSourceField()
  zipcode.setName('zipcode')
  zipcode.setType(grokpy.DataType.CATEGORY)
  zipcode.setFlag(grokpy.DataFlag.LOCATION)

  dayOfWeek = grokpy.DataSourceField()
  dayOfWeek.setName('dayOfWeek')
  dayOfWeek.setType(grokpy.DataType.CATEGORY)

  # Add our fields to our source
  local.addField(timestamp)
  local.addField(consumption)
  local.addField(zipcode)
  local.addField(dayOfWeek)

  # Add our source to the stream specification
  streamSpec.addDataSource(local)

  ##############################################################################
  # Public Data Sources
  #
  # Grok provides a few Public Data Sources. These are databases from which
  # we can pull useful information to be joined with your stream.
  #
  # Today we have public data sources for:
  #     Weather
  #     Stocks
  #     Holidays
  #
  # We'll use weather data in this example.

  ##############################################################################
  # Add weather data to the stream
  #
  # Our advanced dataset contains a location field. In this case a
  # zipcode. Using a zipcode Grok can look up what the weather was like near
  # that location for a given timestamp and return a set of weather values like
  # temperature, or visibility.
  #
  # For each record that we send in with location and time, we get weather
  # data with very little effort! Here we will add in the average temperature.

  weather = grokpy.WeatherDataSource()
  weather.addMeasurement(grokpy.WeatherDataType.TEMPERATURE)

  # Update the stream spec
  print 'Adding Public Data Source: Weather'
  streamSpec.addDataSource(weather)

  ##############################################################################
  # Create and configure our Stream within this project.
  #
  # Note this makes an actual call to the API

  print 'Creating the stream ...'
  newStream = myProject.createStream(streamSpec)

  ##############################################################################
  # Add local data to the stream
  #
  # As soon as Grok receives records it will begin joining in data from the
  # file we uploaded, and Grok weather data, creating an UBER stream.
  # (Note: Not actually called an uber-stream)

  print 'Adding local records to stream ...'
  fileHandle = open(SWARM_INPUT_CSV, 'rU')
  recCenterData = [row for row in csv.reader(fileHandle)]
  fileHandle.close()
  newStream.addRecords(recCenterData)

  #############################################################################
  # Create and configure our Model within this project.
  #
  # This time we will build up our model spec in a higher level OO way.
  # Grokpy provides a ModelSpecification class for this purpose.

  print 'Defining a model ...'
  modelSpec = grokpy.ModelSpecification()
  # Give the model a name
  modelSpec.setName("Advanced Model " + str(time.time()))
  # Set which field this model will predict and optimize for
  modelSpec.setPredictedField("consumption")
  # Set which stream this model will listen to
  modelSpec.setStream(newStream.id)

  print 'Creating that model ...'
  advancedModel = myProject.createModel(modelSpec)
  print "Done. Your model's Id is: %s" % advancedModel.id

  # Start the Swarm
  print 'Starting Grok Swarm'
  advancedModel.startSwarm()

  # Monitor Progress
  swarmStarted = False
  while True:
    state = advancedModel.getSwarmState()
    jobStatus = state['status']
    results = state['details']
    if 'numRecords' in results:
      recordsSeen = results['numRecords']
    else:
      recordsSeen = 0

    if jobStatus == grokpy.SwarmStatus.COMPLETED:
      # Swarm is done
      bestConfig = results['bestModel']
      print '\nYou win! Your Grok Swarm is complete.'
      print '\tBest Configuration: ' + str(bestConfig)
      print '\tWith an Error of: ' + str(results['bestValue'])
      print ('\tThis model uses the following field(s): '
             + str(results['fieldsUsed']))
      print
      # Exit the loop
      break
    elif jobStatus == grokpy.SwarmStatus.RUNNING and swarmStarted == False:
      # The first time we see that the swarm is running
      swarmStarted = True
      print 'Swarm started.'
    elif jobStatus == grokpy.SwarmStatus.STARTING:
      print 'Swarm is starting up ...'
      time.sleep(2)
    else:
      print ".",
      sys.stdout.flush()
      time.sleep(2)

  print "Getting full results from Swarm ..."
  headers, resultRows = advancedModel.getModelOutput(limit = 2500)

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

  #### HACK ####
  print 'Sleep a bit ...'
  time.sleep(5)

  print 'Promoting model and updating model id ...'
  advancedModel.promote()

  # Data in, predictions out
  fileHandle= open(PRODUCTION_INPUT_CSV)
  newRecords = [row for row in csv.reader(fileHandle)]
  fileHandle.close()

  print 'Adding new data ...'
  newStream.addRecords(newRecords)

  print 'Monitoring predictions ...'
  lastRecordSeen = None
  counter = 0
  while True:
    headers, resultRows = advancedModel.getModelOutput(limit = 20)
    latestRowId = resultRows[-2][0]

    if latestRowId == lastRecordSeen:
      if counter > 10:
        print 'Looks like we will not get any more predictions'
        break
      else:
        print 'No new records in this step ...'
        counter += 1
        time.sleep(1)
        continue
    else:
      lastRecordSeen = latestRowId
      print 'Records seen ' + str(lastRecordSeen)
      counter = 0
      # Don't spam the server
      time.sleep(0.5)

  # Align predictions with actuals
  headers, resultRows = advancedModel.getModelOutput(limit = 2500)
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

  print "\n\nFantasmic! You've completed Part Three."
  print ("Now it's time to start working with your own data. Get to it!")

if __name__ == '__main__':
  HelloGrokPart3()
