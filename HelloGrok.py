#!/usr/bin/env python
'''
  #############################################################################
  HELLO GROK!
  
  Welcome to the Grok Prediction Service!
  
  We hope this example application will serve as inspiration for your own
  creative uses of our service.
  
  This application will go through all the steps you'll need to create models
  for your own data sets and start getting predictions back in just a few
  minutes.
  
  #############################################################################
'''

import time
import Queue
import threading

from grokpy import Grokpy

def HelloPredictions():
  
  '''
  The first thing that you'll need is your API key. You should have been
  given a key as part of the sign up process.
  
  You can enter that key below.

  NOTE: A slightly more secure method is to store your API key in your shell
  environment.
  
  From the command line:

    echo "export GROK_API_KEY=YOUR_KEY_HERE" >> ~/.bashrc
    source ~/.bashrc
  '''
  
  key = 'YOUR_KEY_HERE'
  
  '''
  Now we need a way to interact with the prediction service. That is going to
  be through a grokpy object. After we give it our credentials we'll have
  full access to all the functionality of the API.
  '''
  key = '' 
  
  grok = Grokpy(key, '')
    
  '''
  The working areas, where you'll build models, stream in data, and launch
  Swarms is called a 'project.' Let's create one now.
  '''
  now = time.time()
  projectName = 'HelloGrok' + str(now)
  myProject = grok.createProject(projectName)
  
  '''
  Now lets get a list of all the projects we have
  '''
  projects = grok.listProjects()
  for project in projects:
    print project.id
  
  '''
  Now lets remove all those projects
  '''  
  for project in projects:
    project.delete()
  
  '''
  Make sure they are all gone
  '''
  projects = grok.listProjects()
  assert (len(projects) == 0)
  print 'All gone!'
  
  '''
  Make another project to work with
  '''
  myProject = grok.createProject('Happy Project')

  '''
  Update the name of that project, just for fun
  '''
  myProject.setName('Joyus Chorus - 2')
  
  '''
  Next we need to configure our project so that it knows what data to expect.
  
  WARNING: This is the really hard part!
  '''
  gymField = {
          "aggregationFunction":"first",
          "dataFormat":{
            "dataType":"ENUMERATION",
            "formatString": None
          },
          "dataType":"ENUMERATION",
          "fieldRange":None,
          "fieldSubset":None,
          "flag":"NONE",
          "index":0,
          "name":"gym",
          "useField": True
        }
  
  addressField = {
          "aggregationFunction":"first",
          "dataFormat":{
            "dataType":"ENUMERATION",
            "formatString": None
          },
          "dataType":"ENUMERATION",
          "fieldRange": None,
          "fieldSubset": None,
          "flag":"NONE",
          "index":1,
          "name":"address",
          "useField": True
        }
  
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
          "index":2,
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
          "index":3,
          "name":"consumption",
          "useField": True
        }
  
  config = {
      "locationFieldIndex":1,
      "predictionFieldIndex":3,
      "temporalFieldIndex":2,
      "timeAggregation":"RECORD"
      }

  config['fields'] = [gymField, addressField, timestampField, consumptionField]
  
  myProject.configure(**config)
  
  print '=' * 40
  
  '''
  Now we have to create a model
  '''
  myModel = myProject.createModel()
  
  print 'Setting Model Name'
  myModel.setName('Fun times!')
  print 'Setting Model Note'
  myModel.setNote('This is a neat model of stuff')
  
  '''
  Lets upload some data!
  
  We want to be able to monitor the upload progress so we're going to take
  advantage of the threading library to upload in one thread, and monitor in
  another.
  '''
  
  # Create our queue
  queue = Queue.Queue()
  
  # Time how long this takes
  startTime = time.time()
  
  # How many threads we need to kick off
  numThreads = 2
  
  # Start up our threads. They will poll the queue until we populate it.
  for i in range(numThreads):
    t = ThreadRunner(queue)
    t.setDaemon(True)
    t.start()
  
  # Put all our calls into the queue  
  queue.put((myModel.upload, 'hotgym_small_headless.csv'))
  queue.put((myModel.monitorUpload, None))
 
  # Block until queue is empty then continue   
  queue.join()
  
  
  
  print 'Uploading data'
  myModel.upload('hotgym_small_headless.csv')
  
  '''
  Lets train this bitch!
  '''
  print 'Starting training swarm'
  myModel.swarm()

if __name__ == '__main__':
  HelloPredictions()