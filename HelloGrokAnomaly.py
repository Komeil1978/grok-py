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

# Anomaly scores above this are considered anomalies
ANOMALY_THRESHOLD = 0.8

# Number of records to wait before labeling anomalies
ANOMALY_WAIT_RECORDS = 1000 

INPUT_CSV = 'data/rec-center-swarm.csv'
NEW_RECORDS = 'data/rec-center-stream.csv'
OUTPUT_CSV = 'output/anomaly_scores.csv'

# API KEY NOTE: Add your API key here. If set to None, grokpy will
# use the value of environment variable GROK_API_KEY
API_KEY = None

def waitForPredictions(model):
  """
  This function waits until there are no new predictions from this model.
  """
  lastRowID = -1
  while True:
    time.sleep(5)
    headers, rows, _ = model.getModelOutput(1, shift = False)
    if rows[0][0] == lastRowID:
      print "Done: predictions have not advanced in 5 secs"
      break
    else:
      lastRowID = rows[0][0]
      print "Records seen:",lastRowID


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
  swarmStartTime = time.time()
  recCenterEnergyModel.startSwarm(size = swarmSize)

  ##############################################################################
  # Monitor Progress
  #
  # Here we print out the error over time

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
      print '\tSwarm completed with an Error of: ' + str(results['bestValue'])
      print ('\tThis model uses the following field(s): '
             + str(results['fieldsUsed']))
      print '\tSwarm duration: %g seconds' %(time.time() - swarmStartTime)
      print
      break
    elif jobStatus == grokpy.SwarmStatus.STARTING or \
         not results.has_key('bestValue'):
      print 'Swarm is starting up ...'
      time.sleep(5)
    else:
      print 'Current swarm error: ' + str(results['bestValue'])
      sys.stdout.flush()
      
      # If we've already reached our error threshold, we can stop the swarm
      # This only works if you already have a sense of the error ahead of time
      # but does speed up the swarm process significantly
      # Note: with a large swarm you can get down to an even lower error.
      if results['bestValue'] < 14:
        recCenterEnergyModel.stop()

      time.sleep(5)

  # Return the model ID
  return recCenterEnergyModel.id


def HelloGrokAnomalyProduction(modelId = None):

  ##############################################################################
  # Setup
  print 'Retrieving Model and Stream'
  grok = grokpy.Client(API_KEY)
  recCenterEnergyModel = grok.getModel(modelId)
  myStream = recCenterEnergyModel.getStream()

  ##############################################################################
  # Setup the production model, set anomaly score threshold and set the
  # initial wait period for anomaly detection

  print 'Promoting our model. This may take a few seconds ...'
  recCenterEnergyModel.promote()

  print 'Setting our anomaly score threshold to %s.' % (ANOMALY_THRESHOLD)
  recCenterEnergyModel.setAnomalyAutoDetectThreshold(ANOMALY_THRESHOLD)

  print 'Setting our model to wait %s records before labeling anomalies.' % \
    (ANOMALY_WAIT_RECORDS)
  recCenterEnergyModel.setAnomalyAutoDetectWaitRecords(ANOMALY_WAIT_RECORDS)

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
  
  print 'Sending new data ...'
  myStream.addRecords(newRecords)

  ##############################################################################
  # Retrieving predictions
  
  print 'Waiting for Grok to process all data...'
  waitForPredictions(recCenterEnergyModel)

  # Get the full set of anomaly scores
  print 'Retrieving anomaly scores...'
  headers, resultRows, _ = recCenterEnergyModel.getModelOutput(limit = 5000)

  # Get and align anomalies
  print 'Retrieving anomalies ...'
  anomalyRows     = recCenterEnergyModel.getLabels()
  firstROWID      = resultRows[0][0]
  anomalyLabelID  = headers.index('Anomaly Label')
  for anomaly in anomalyRows['recordLabels']:
    resultID      = anomaly['ROWID'] - firstROWID
    resultRows[resultID][anomalyLabelID] = anomaly['labels']

  #############################################################################
  # Write out anomaly scores to a CSV

  if not os.path.exists('output'):
    print 'Output directory not found, creating ...'
    os.mkdir('output')
  print "Saving results to " + OUTPUT_CSV
  fileHandle = open(OUTPUT_CSV, 'w')
  writer = csv.writer(fileHandle)
  
  # Write out the specific fields we want from the model output results
  rowID       = headers.index('ROWID')
  timestamp   = headers.index('timestamp')
  consumption = headers.index('consumption')
  labelID     = headers.index('Anomaly Label')
  score       = headers.index('Anomaly Score')

  writer.writerow([headers[rowID],headers[timestamp],headers[consumption],
                   headers[labelID],headers[score]])
  for r in resultRows:
    writer.writerow([r[rowID],r[timestamp],r[consumption],r[labelID],r[score]])
  fileHandle.close()
  
  #############################################################################
  # Clean up
  recCenterEnergyModel.delete()
  myStream.delete()

  print "\n\nWonderful! You've completed HelloGrokAnomaly!!"
  print ('Why not take a moment to examine the anomaly scores generated by your '
         'trained model?')
  print "Open the file %s and look at the 'Anomaly Score' column" % (OUTPUT_CSV)


if __name__ == '__main__':

  # Run the swarm. Set swarmSize to "small" for debugging
  modelId = HelloGrokAnomalySwarm(swarmSize = "medium")
  
  # Promote the model and compute new anomaly scores
  HelloGrokAnomalyProduction(modelId = modelId)

