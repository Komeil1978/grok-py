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

from grokpy import Client

##############################################################################
# Configuration Settings

API_KEY = 'YOUR_KEY_HERE'
PROJECT_ID = 'YOUR_PROJECT_ID_HERE'
MODEL_ID = 'YOUR_MODEL_ID_HERE'
OUTPUT_CSV = 'output/newPredictions.csv'

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
  #

  print 'Connecting to Grok ...'
  grok = Client(API_KEY)
  print 'Retrieving Project ...'
  myProject = grok.getProject(PROJECT_ID)
  print 'Retrieving Model ...'
  recCenterEnergyModel = myProject.getModel(MODEL_ID)
  
  ##############################################################################
  # Promote our model
  #
  # Production models are long running processes.
  # Once started you can:
  #       - Send new data directly and get back predictions (Shown below)
  #       - Set a stream to which the model will continually listen.
  #
  # NOTE: Production models may incur charges even if not being sent new data.
  #       Please remember to stop your models if you do not intend to use them.
  
  # Create and start a production model
  print 'Promoting model and updating model id ...'
  recCenterEnergyModel.promote()
  
  ##############################################################################
  # Data in, predictions out
  
  exampleRecords = [["2010-07-02 00:00:00.0","5.3"],
                    ["2010-07-02 00:15:00.0","5.5"],
                    ["2010-07-02 00:30:00.0","5.1"],
                    ["2010-07-02 00:45:00.0","5.3"],
                    ["2010-07-02 01:00:00.0","5.2"],
                    ["2010-07-02 01:15:00.0","5.5"],
                    ["2010-07-02 01:30:00.0","4.5"],
                    ["2010-07-02 01:45:00.0","1.2"],
                    ["2010-07-02 02:00:00.0","1.1"],
                    ["2010-07-02 02:15:00.0","1.2"],
                    ["2010-07-02 02:30:00.0","1.2"],
                    ["2010-07-02 02:45:00.0","1.2"],
                    ["2010-07-02 03:00:00.0","1.2"]]
  
  # Send data. (Recall that this model will aggregate into hourly buckets)
  print 'Sending new data ...'
  recCenterEnergyModel.sendRecords(exampleRecords)

  # Get all the latest predictions (the next hour in this case)
  print 'Getting new predictions ...'
  
  # TODO: Replace with callback
  while True:
    response = recCenterEnergyModel.getPredictions()
    if 'code' in response and response['code'] == 'I00003':
      print 'Predictions not yet ready'
      time.sleep(1)
    elif not response['rows']:
      print 'Predictions not yet ready'
      time.sleep(1)
    else:
      break
  
  headers = response['columnNames']
  resultRows = response['rows']
  
  # Align predictions with actuals
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
  
  ##############################################################################
  # Cleanup
  myProject.stopAllModels()
  
  # recCenterEnergyModel.stop() # Un-commment if you need to leave some running
  
  
  print "\n\nWonderful! You've completed Part Two!"
  print ('Why not take a moment to examine the predictions generated by your '
         'trained model? Then you can move on to Part Three!')
  print 'IMPORTANT NOTE: There is no Part Three.'

if __name__ == '__main__':
  HelloGrokPart2()