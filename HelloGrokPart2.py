#!/usr/bin/env python

##############################################################################
# Welcome to part two of the Hello Grok Tutorial!
#
# In this tutorial we will:
#
# Promote a model to production ready status
# Stream new records in bulk and get predictions
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

API_KEY = 'YOUR_KEY_HERE'
MODEL_ID = '2799de3da4c94df494e3406df1bd'
NEW_RECORDS = 'data/rec-center-stream.csv'
OUTPUT_CSV = 'output/streamPredictions.csv'

##############################################################################
# API KEY NOTE: A slightly more secure method is to store your API key in your
# shell environment.
#
# From the command line:
#  echo "export GROK_API_KEY=YOUR_KEY_HERE" >> ~/.bashrc
#  source ~/.bashrc

def HelloGrokPart2():

  ##############################################################################
  # Setup

  print 'Connecting to Grok ...'
  grok = grokpy.Client(API_KEY)

  print 'Retrieving Model ...'
  recCenterEnergyModel = grok.getModel(MODEL_ID)

  print 'Retrieving Stream ...'
  myStream = recCenterEnergyModel.getStream()

  ##############################################################################
  # Promote the model
  #
  # Note: This will soon go away in favor of automatic promotion
  #
  # When you promote a model you are taking it from the swarm into a
  # production ready state. You can then train the model further by sending
  # it more records (as we will do below) or you can start streaming your
  # live data right away.

  print 'Promoting our model. This may take a few seconds ...'
  recCenterEnergyModel.promote()

  ##############################################################################
  # Sending new records

  # Get the records from a local file
  fileHandle= open(NEW_RECORDS)
  newRecords = [row for row in csv.reader(fileHandle)]
  fileHandle.close()

  # Send data. (Recall that our model will aggregate into hourly buckets)
  print 'Sending new data ...'
  # This method will send a maximum of 5k records per request.
  myStream.addRecords(newRecords)

  ##############################################################################
  # Retrieving predictions
  #
  # We will poll for new predictions. We will time out if we haven't seen
  # new predictions in a while and call this 'done.' In the near future this
  # will be replaced with a more definitive mechanism.
  #
  # This method is only for batch processing. In a streaming case you would
  # continually poll the model output and parse the data as it came in.

  print 'Monitoring predictions ...'
  lastRecordSeen = None
  counter = 0
  while True:
    headers, resultRows = recCenterEnergyModel.getModelOutput()
    latestRowId = resultRows[-1][0]
    if latestRowId == lastRecordSeen:
      if counter > 15:
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
      time.sleep(1)

  # Align predictions with actuals
  print 'Aligning predictions ...'
  resultRows = grok.alignPredictions(headers, resultRows)

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

  print "\n\nWonderful! You've completed Part Two!"
  print ('Why not take a moment to examine the predictions generated by your '
         'trained model? Then you can move on to Part Three!')

if __name__ == '__main__':
  HelloGrokPart2()
