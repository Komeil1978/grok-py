#!/usr/bin/env python
'''
  #############################################################################
  Welcome to Grok!
  
  In this sample application we'll be creating a model of energy use for a
  local business, in this case a Recreation Center.
  
  Spiking energy use can be a sign of waste for a business. To save energy, and
  money, we need a way to predict what our energy consumption will be like in
  the next hour, so we can take action *now* to prevent wasting power.
  
  In this application we will:
  
  * Create a Project
  * Create a Model
  * Create a Stream of our energy use data
  * Configure how we want our Model to use our Stream
  * Start a Grok Swarm to optimize our Model for the given Stream
  * Get results from the Swarm
  
  We'll end up with a CSV we can examine to see how well Grok learned and
  predicted the energy use for this business.
  
  #############################################################################
'''

import time
import csv
import os
import signal
import sys
import json

from grokpy import Grokpy

def HelloGrok():
  
  # Enter your API key here
  key = 'YOUR_KEY_HERE' 
  '''
  API KEY NOTE: A slightly more secure method is to store your API key in your
  shell environment.
  
  From the command line:
    echo "export GROK_API_KEY=YOUR_KEY_HERE" >> ~/.bashrc
    source ~/.bashrc
  '''
  
  # Connect to Grok
  print 'Connecting to Grok ...'
  grok = Grokpy(key)
  
  # Create a project to hold our predictive models
  now = time.time()
  projectName = 'HelloGrok ' + str(now)
  print 'Creating an initial project: ' + projectName
  myProject = grok.createProject(projectName)
    
  # Create a blank model in that project
  print 'Creating an empty model ...'
  recCenterEnergyModel = myProject.createModel()
  
  '''
  Define our Stream and add data
  
  For Grok to use your data we need a careful specification of that data to
  work with. The combination of your data and its specification is what
  we call a 'Stream'.
  '''
  # Create an empty stream
  print 'Creating an empty stream ...'
  myStream = myProject.createStream()
  
  # Specify the format of the stream using a JSON document
  myStream.configure('data/streamConfig.json')
  
  # Add data to the stream from a local source
  print 'Adding records to stream ...'
  fileHandle = open('data/rec-center.csv', 'rU')
  recCenterData = [row for row in csv.reader(fileHandle)]
  fileHandle.close()
  myStream.addRecords(recCenterData)
  
  '''
  Marry the model to the Stream
  
  Once a model is tied to a stream of data it is set with that configuration
  '''
  print 'Adding stream to model and configuring ...'
  recCenterEnergyModel.addStream(myStream)
  
  '''
  Specify how our model should use that stream of data
  '''
  recCenterEnergyModel.setTemporalFieldIndex(0)
  recCenterEnergyModel.setPredictionFieldIndex(1)
  recCenterEnergyModel.setTimeAggregation('HOURS')
  
  '''
  Now we have a project, a stream with data, and a model configured for that
  stream. Lets start a Grok Swarm to find the best configuration of our model
  to predict the data that exist in the stream.
  
  '''
  print 'Starting Grok Swarm'
  recCenterEnergyModel.startSwarm()
  
  # Monitor the swarm
  started = False

  # Catch ctrl-c to terminate remote long-running processes
  signal.signal(signal.SIGINT, signal_handler)
  
  # TODO: Replace with callback
  while True:
    SwarmState = recCenterEnergyModel.getSwarmProgress()
    jobStatus = SwarmState['jobStatus']
    results = SwarmState['results']
    
    if jobStatus == 'COMPLETED':
      print 'You win! Your Grok Swarm is complete.'
      break
    if jobStatus == 'RUNNING' and started == False:
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
    print ("Current best model: " + bestConf + " - Score %.2f" % bestValue)
    time.sleep(1)
    
  # Retrieve Swarm results
  print "Getting results from Swarm ..."
  
  swarmResults = recCenterEnergyModel.getSwarmResults()
  
  headers = swarmResults['columnNames']
  resultRows = swarmResults['rows']
  
  # Write results out to a CSV
  outputFilePath = "output/SwarmOutput.csv";
  if not os.path.exists('output'):
    print 'Output directory not found, creating ...'
    os.mkdir('output')
  print "Saving results to " + outputFilePath
  fileHandle = open(outputFilePath, 'w')
  writer = csv.writer(fileHandle)
  writer.writerow(headers)
  for row in resultRows:
    writer.writerow(row)
  fileHandle.close()
  
def signal_handler(signal, frame):
        model = frame.f_locals.get('recCenterEnergyModel')
        swarmStatus = frame.f_locals.get('jobStatus')
        # Shut down any running swarms
        if model and swarmStatus == 'RUNNING':
          print 'Caught Ctrl-C during Swarm'
          print 'Stopping in-progress Swarm ...'
          model.stopSwarm()
        sys.exit(0)

if __name__ == '__main__':
  HelloGrok()