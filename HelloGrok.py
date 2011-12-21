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
  * Configure a Project for the sample energy use data
  * Create a Model
  * Stream data to that Model
  * Start a Grok Swarm to optimize that Model
  * Get results from the Swarm
  
  We'll end up with a CSV we can examine to see how well Grok learned and
  predicted the energy use for this business.
  
  #############################################################################
'''

import time
import csv

from grokpy import Grokpy

def HelloGrok():
  
  '''
  API KEY NOTE: A slightly more secure method is to store your API key in your shell
  environment.
  
  From the command line:
    echo "export GROK_API_KEY=YOUR_KEY_HERE" >> ~/.bashrc
    source ~/.bashrc
  '''
  # Enter your API key here
  key = 'YOUR_KEY_HERE' 
  
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
  
  # Create an empty stream of data
  myStream = grok.createStream()
  
  '''
  Add data and define our Stream
  
  For Grok to use your data we need a careful specification of that data to
  work with. The combination of your data and it's specification is what
  we call a 'Stream'.
  '''
  # Add data from a local source
  with open('data/rec-center.csv', 'rU') as fileHandle:
    reader = csv.reader(fileHandle)
    recCenterData = [row for row in reader]
  
  print myStream.addRecords(recCenterData)
  
  # Define Stream specification
  timestampField = {
          "aggregationFunction":"first",
          "dataFormat":{
            "dataType":"DATETIME",
            "formatString":"sdf/yyyy-MM-dd H:m:s.S"
          },
          "dataType":"DATETIME",
          "fieldRange": None,
          "fieldSubset": None,
          "flag":"TIMESTAMP",
          "index":0,
          "name":"timestamp",
          "useField": True
        }
  
  consumptionField = {
          "aggregationFunction":"mean",
          "dataFormat":{
            "dataType":"SCALAR",
            "formatString": None
          },
          "dataType":"SCALAR",
          "fieldRange": None,
          "fieldSubset": None,
          "flag":"NONE",
          "index":1,
          "name":"consumption",
          "useField": True
        }
  
  # Add fields
  myStream.addField(timestampField)
  myStream.addField(consumptionField)
  
  # Top level Stream configuration
  myStream.setTemporalFieldIndex(0)
  myStream.setPredictionFieldIndex(1)
  
  '''
  Marry the model to the Stream
  
  Once a model is tied to a stream of data it is set with that configuration
  '''
  recCenterEnergyModel.addStream(myStream)
  
  '''
  Now we have a project, a stream with data, and a model configured for that
  stream. Lets start a Grok Swarm to find the best configuration of our model
  to predict the data that exist in the stream.
  
  '''
  print 'Starting Grok Swarm'
  recCenterEnergyModel.startSwarm()
  
  # Monitor the swarm
  print 'Swarm started. Progress follows:'
  while True:
    SwarmState = recCenterEnergyModel.getSwarmProgress()
    print SwarmState['jobStatus']
    print len(SwarmState['models'])
    print len(SwarmState['results'])
    print 'Sleeping for 5 seconds ...'
    time.sleep(5)

if __name__ == '__main__':
  HelloGrok()