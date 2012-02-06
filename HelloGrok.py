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
# * Create a Project
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
import json

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

def HelloGrok():

  ##############################################################################
  # Setup
  #
  # This is where we will create all the top level objects we'll be working
  # with in this application.

  # Connect to Grok
  print 'Connecting to Grok ...'
  grok = grokpy.Client(API_KEY)

  # Create a project to hold our predictive models
  now = time.time()
  projectName = 'HelloGrok ' + str(now)
  print 'Creating an initial project: ' + projectName
  myProject = grok.createProject(projectName)

  # Create a blank model in that project
  print 'Creating an empty model ...'
  recCenterEnergyModel = myProject.createModel()

  # Create an empty stream
  print 'Creating an empty stream ...'
  myStream = myProject.createStream()

  ##############################################################################
  # Define our Stream and add data
  #
  # For Grok to use your data we need a careful specification of that data to
  # work with. The combination of your data and its specification is what
  # we call a 'Stream'.

  # Specify the format of the stream using a JSON document
  myStream.configure(STREAM_SPEC)

  # Add data to the stream from a local source
  print 'Adding records to stream ...'
  fileHandle = open(INPUT_CSV, 'rU')
  recCenterData = [row for row in csv.reader(fileHandle)]
  fileHandle.close()
  myStream.addRecords(recCenterData)

  # Associate our model with this stream.
  print 'Attaching model to stream and configuring ...'
  recCenterEnergyModel.setStream(myStream)

  ##############################################################################
  # Define how our Model will use our Stream
  #
  # Your models can listen to your streams in many different ways. Here we
  # tell the model how to deal with each field and which field we want to
  # optimize our predictions for etc.

  recCenterEnergyModel.setTemporalField('timestamp')
  recCenterEnergyModel.setPredictionField('consumption')
  recCenterEnergyModel.setTimeAggregation(grokpy.Aggregation.HOURS)

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
  # Every second we want to get an update on the state of our swarm. We might
  # want to know how many configurations the swarm has tried, or what the
  # average error of the best configuration is. Below you'll find a definition
  # of a SwarmMonitor which extends the general functionality of the
  # grokpy.streaming.StreamMonitor class.

  # Catch ctrl-c to terminate remote long-running processes
  signal.signal(signal.SIGINT, signal_handler)

  monitor = SwarmMonitor()
  recCenterEnergyModel.monitorSwarm(monitor)

  ##############################################################################
  # Retrieve Swarm results

  print "\nGetting full results from Swarm ..."
  swarmResults = recCenterEnergyModel.getSwarmResults()
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

  ##############################################################################
  # Next steps ...
  #
  # Now would be a good time to explore the results of the Swarm and familiarize
  # yourself with their format. After that, you can take the Project id and
  # Model id printed out below and head over to part two!

  print '\n\nOn to Part Two!'
  print 'Take these, the wizard will ask for them:'
  print '\t MODEL_ID: ' + recCenterEnergyModel.id
  print '\t PROJECT_ID: ' + myProject.id

class SwarmMonitor(grokpy.StreamMonitor):

    def __init__(self):
        # Loop information
        self.started = False

        self.configurations = {}
        self.highestRecordCount = 0

    def on_state(self, state):
        '''
        Called when a new state is received from connection.

        Override this method if you wish to manually handle
        the stream data. Return False to stop stream and close connection.
        '''

        jobStatus = state['jobStatus']
        results = state['results']
        configurations = state['models']

        if jobStatus == grokpy.Status.COMPLETED:
          bestConfig = results['bestModel']
          fieldsUsed = self.configurations[bestConfig]['fields']
          print 'Best Configuration: ' + str(bestConfig)
          print 'Using Field(s): ' + str(fieldsUsed)
          if len(fieldsUsed) > 1:
            fieldContributions = state['fieldContributions']
            print 'Field Contributions:'
            for field in fieldContributions:
              if field['contribution'] > 0:
                print('\tUsing ' + field['name'] + ' improved accuracy by ' +
                      str(field['contribution']) + ' percent.')

          print 'With an Error of: ' + str(results['bestValue'])
          print 'You win! Your Grok Swarm is complete.'
          # Exit the loop
          return False
        if jobStatus == grokpy.Status.RUNNING and self.started == False:
          self.started = True
          print 'Swarm started.'
        if not self.started:
          print 'Swarm is starting up ...'
          time.sleep(2)
          return True
        if not results:
          print 'Initial records are being loaded ...'
          time.sleep(2)
          return True

        for config in configurations:
          if config['numRecords'] > self.highestRecordCount:
            self.highestRecordCount = config['numRecords']
          if config['status'] == grokpy.Status.COMPLETED:
            self.configurations[config['modelId']] = config

        if self.configurations:
          print ('Grok has evaluated ' + str(len(self.configurations)) +
                 ' model configurations.')
        else:
          print ('First models are processing records. Latest record seen: ' +
                 str(self.highestRecordCount))

        time.sleep(2)
        return True

def signal_handler(signal, frame):
  model = frame.f_locals.get('recCenterEnergyModel')
  swarmStatus = frame.f_locals.get('jobStatus')
  # Shut down any running swarms
  if model and swarmStatus == grokpy.Status.RUNNING:
    print 'Caught Ctrl-C during Swarm'
    print 'Stopping in-progress Swarm ...'
    model.stopSwarm()
  sys.exit(0)

if __name__ == '__main__':
  HelloGrok()
