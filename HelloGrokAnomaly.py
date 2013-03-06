#!/usr/bin/env python

##############################################################################
# Welcome to the Hello Grok Anomaly Tutorial!
#
# In this tutorial we will:
#
# Create an anomaly detector model, promote it to production ready,
# stream in new records and retrieve anomaly scores. We also explicitly add
# in some artificial anomalies on December 1 2010
##############################################################################

import time
import csv
import os
import signal
import sys
import json
import grokpy

from math import floor

from grokpy import Client, GrokError


##############################################################################
# Configuration Settings

API_KEY = None
INPUT_CSV = 'data/rec-center-swarm.csv'
OUTPUT_CSV_SWARM = 'output/SwarmOutput.csv'
NEW_RECORDS = 'data/rec-center-stream.csv'
OUTPUT_CSV = 'output/streamPredictions.csv'

##############################################################################
# API KEY NOTE: A slightly more secure method is to store your API key in your
# shell environment GROK_API_KEY

def HelloGrokAnomalySwarm(swarmSize = "medium"):
  """
  This function creates an anomaly detector model using the rec-center dataset.
  It is almost identical to HelloGrok.py with the exception of the call to
  modelSpec.setType() when setting up the model object.  
  """

  ##############################################################################
  # Connect to Grok

  print 'Connecting to Grok ...'
  grok = grokpy.Client(API_KEY)
  now = time.time()

  ##############################################################################
  # Create our stream specification
  #
  # This is identical to HelloGrok.py
  print 'Defining our stream ...'
  streamSpec = grokpy.StreamSpecification()
  streamSpec.setName('Recreation Center Stream ' + str(now))

  # Create a Data Source and specify fields
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
  consumption.setMax(100.0)
  consumption.setMin(0.0)

  # Add our fields to our source
  local.addField(timestamp)
  local.addField(consumption)

  # Add our source to the stream specification
  streamSpec.addDataSource(local)
  
  # Create an empty stream using our streamSpec object
  # Note this makes an actual call to the API
  print 'Creating the stream ...'
  myStream = grok.createStream(streamSpec)

  # Add data to the stream from a csv
  print 'Adding records to stream ...'
  fileHandle = open(INPUT_CSV, 'rU')
  recCenterData = [row for row in csv.reader(fileHandle)]
  fileHandle.close()
  myStream.addRecords(recCenterData)

  ##############################################################################
  # Create and configure your Model
  #
  # The main difference from HelloGrok.py is the call to modelSpec.setType()

  print 'Defining a model ...'
  modelSpec = grokpy.ModelSpecification()
  modelSpec.setName("Recreaction Center Model " + str(time.time()))
  modelSpec.setPredictedField("consumption")
  modelSpec.setStream(myStream.id)

  # Set model to be an anomaly detection model
  modelSpec.setType(grokpy.ModelType.ANOMALY)

  # We want to get predictions every hour.
  modelSpec.setAggregationInterval({"hours": 1})

  # Create that model using our specification
  recCenterEnergyModel = grok.createModel(modelSpec)
  print "Done. Your model's Id is: %s" % recCenterEnergyModel.id

  ##############################################################################
  # Start the Swarm
  #

  print 'Starting Grok Swarm'
  recCenterEnergyModel.startSwarm(size = swarmSize)

  ##############################################################################
  # Monitor Progress
  #
  # Here we print out the error over time

  swarmStarted = False
  while True:
    state = recCenterEnergyModel.getSwarmState()
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
      if results.has_key('bestValue'):
        print 'Current swarm error: ' + str(results['bestValue'])
        sys.stdout.flush()
      else:
        print 'Swarm is starting up ...'        
      time.sleep(5)

  ##############################################################################
  # Retrieve Swarm results

  print "Getting full results from Swarm ..."
  headers, resultRows, resultMetadata = recCenterEnergyModel.getModelOutput(limit = 2500)

  # Write results out to a CSV
  if not os.path.exists('output'):
    print 'Output directory not found, creating ...'
    os.mkdir('output')
  print "Saving results to " + OUTPUT_CSV_SWARM
  fileHandle = open(OUTPUT_CSV_SWARM, 'w')
  writer = csv.writer(fileHandle)
  writer.writerow(headers)
  writer.writerows(resultRows)
  fileHandle.close()

  # Return the model ID
  return recCenterEnergyModel.id


def HelloGrokAnomalyProduction(modelId = None):

  ##############################################################################
  # Setup

  print 'Connecting to Grok ...'
  grok = grokpy.Client(API_KEY)

  print 'Retrieving Model ...'
  recCenterEnergyModel = grok.getModel(modelId)

  print 'Retrieving Stream ...'
  myStream = recCenterEnergyModel.getStream()

  ##############################################################################
  # Promote the model

  print 'Promoting our model. This may take a few seconds ...'
  recCenterEnergyModel.promote()

  ##############################################################################
  # Sending new records

  # Get the records from a local file
  fileHandle= open(NEW_RECORDS)
  newRecords = [row for row in csv.reader(fileHandle)]
  fileHandle.close()
  
  # Add a little wonkiness to the data for December 1, 2010. We add +/- 5 to the
  # energy reading and a small scale factor. This should show up as unpredicted,
  # and therefore have higher than normal anomaly scores. Note that a threshold
  # based system would not detect this behavior as an anomaly.
  print "Adding some artificial anomalies on December 1 2010 ..."
  offset= [-5, -5, -5, -5, 5, 5, 5, 5]
  for i in range(5890,5931):
    newRecords[i] = [newRecords[i][0], str(0.75*float(newRecords[i][1]) + offset[i%8])]
  
  # Send data. (Recall that our model will aggregate into hourly buckets)
  print 'Sending new data ...'
  # This method will send a maximum of 5k records per request.
  myStream.addRecords(newRecords)

  ##############################################################################
  # Retrieving predictions
  #
  # We will poll until no new predictions are generated
  
  print 'Monitoring predictions ...'
  lastRecordSeen = None
  counter = 0
  while True:
    headers, resultRows, resultMetadata = recCenterEnergyModel.getModelOutput(limit = 20)
    latestRowId = resultRows[-2][0]
    if latestRowId == lastRecordSeen:
      if counter > 3:
        print 'Looks like we will not get any more predictions'
        break
      else:
        print 'No new records in this step ...'
        counter += 1
        time.sleep(4)
        continue
    else:
      lastRecordSeen = latestRowId
      print 'Records seen ' + str(lastRecordSeen)
      counter = 0
      # Don't spam the server
      time.sleep(2)

  # Align predictions with actuals
  print 'Retrieving results ...'
  headers, resultRows, resultMetadata = recCenterEnergyModel.getModelOutput(limit = 2500)

  #############################################################################
  # Write out predictions to a CSV

  if not os.path.exists('output'):
    print 'Output directory not found, creating ...'
    os.mkdir('output')
  print "Saving results to " + OUTPUT_CSV
  fileHandle = open(OUTPUT_CSV, 'w')
  writer = csv.writer(fileHandle)
  writer.writerow(headers)
  writer.writerows(resultRows)
  fileHandle.close()

  print "\n\nWonderful! You've completed HelloGrokAnomaly!!"
  print ('Why not take a moment to examine the anomaly scores generated by your '
         'trained model?')

if __name__ == '__main__':

  # Run the swarm. Set swarmSize to "small" for debugging
  modelId = HelloGrokAnomalySwarm(swarmSize = "medium")
  
  # Promote the model and compute new anomaly scores
  HelloGrokAnomalyProduction(modelId = modelId)

