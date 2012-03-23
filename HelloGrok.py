#!/usr/bin/env python

##############################################################################
# Welcome to Grok!
#
# In this sample application we'll be creating a model of energy use for a
# local business, in this case a Recreation Center.
#
# Spiking energy use can be a sign of waste for a business. To save energy, and
# money, we need a way to predict what our energy consumption will be like in
# the next hour, so we can take action *now* to prevent wasting power.
#
# In this application we will:
#
# * Create a Model
# * Create a Stream of our energy use data
# * Configure how we want our Model to use our Stream
# * Start a Grok Swarm to optimize our Model for the given Stream
# * Get results from the Swarm
#
# We'll end up with a CSV we can examine to see how well Grok learned and
# predicted the energy use for this business.
#
##############################################################################

import time
import csv
import os
import signal
import sys

import grokpy

##############################################################################
# Configuration Settings

API_KEY = 'YOUR_KEY_HERE'
STREAM_SPEC = 'data/streamSpecification.json'
INPUT_CSV = 'data/rec-center-swarm.csv'
OUTPUT_CSV = 'output/SwarmOutput.csv'

##############################################################################
# API KEY NOTE: A more secure method is to store your API key in your
# shell environment.
#
# From the command line:
#  echo "export GROK_API_KEY=YOUR_KEY_HERE" >> ~/.bashrc
#  source ~/.bashrc
#
# After doing so you do not need to pass a key to instantiate a client.
# e.g. grok = grokpy.Client()

def HelloGrok():

  ##############################################################################
  # Setup
  #
  # This is where we will create all the top level objects we'll be working
  # with in this application.
  #
  # grokpy.DEBUG = True # Uncomment this line if you want more verbose output

  # Connect to Grok
  print 'Connecting to Grok ...'
  grok = grokpy.Client(API_KEY)

  ##############################################################################
  # Create and configure our Stream
  #
  # For Grok to use your data we need a careful specification of that data to
  # work with. The combination of your data and its specification is what
  # we call a 'Stream'.

  # Create an empty stream using our JSON definition
  myStream = grok.createStream(STREAM_SPEC)

  # Add data to the stream from a local source
  print 'Adding records to stream ...'
  fileHandle = open(INPUT_CSV, 'rU')
  recCenterData = [row for row in csv.reader(fileHandle)]
  fileHandle.close()
  myStream.addRecords(recCenterData)

  ##############################################################################
  # Create and configure our Model
  #
  # Your models can listen to your streams in many different ways. Here we
  # tell the model how to deal with each field and which field we want to
  # optimize our predictions for.

  # This time we'll build up a dictionary to spec out the model.
  #
  # Both models and streams can take specs from either dictionaries or JSON
  # files.

  modelSpec = {"name": "Model of Fun " + str(time.time()),
               "predictedField": "consumption",
               "streamId": myStream.id,
               "aggregation": {"interval": grokpy.Aggregation.HOURS}}

  # Create that model for the given stream
  print 'Creating an empty model ...'
  recCenterEnergyModel = grok.createModel(modelSpec)

  ##############################################################################
  # Start the Swarm
  #
  # Now we have a project, a stream with data, and a model configured for that
  # stream. We can start a Grok Swarm! The Swarm will find the best
  # configuration of our model to predict the data that exist in the stream.

  print 'Starting Grok Swarm'
  recCenterEnergyModel.startSwarm()

  ##############################################################################
  # Monitor Progress
  #
  # To know when our Swarm is complete we will poll for the state of the swarm

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
      print 'You win! Your Grok Swarm is complete.'
      print '\tBest Configuration: ' + str(bestConfig)
      print '\tWith an Error of: ' + str(results['bestValue'])
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
      print "Latest record seen: " + str(recordsSeen)
      time.sleep(2)

  ##############################################################################
  # Retrieve Swarm results

  print "Getting full results from Swarm ..."
  headers, resultRows = recCenterEnergyModel.getModelOutput()

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

  ##############################################################################
  # Next steps ...
  #
  # Now would be a good time to explore the results of the Swarm and familiarize
  # yourself with their format. After that, you can take the Project id and
  # Model id printed out below and head over to part two!

  print """
=====================================================================
On to Part Two!
  Take this, the wizard will ask for it:
  MODEL_ID: %s

Please edit HelloGrokPart2.py, adding in the MODEL_ID.
Then run:
  python HelloGrokPart2.py""" % recCenterEnergyModel.id

if __name__ == '__main__':
  HelloGrok()
