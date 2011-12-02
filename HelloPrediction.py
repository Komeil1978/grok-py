#!/usr/bin/env python
'''
  #############################################################################
  HELLO PREDICTIONS!
  
  Welcome to the Grok Prediction Service!
  
  We hope this example application will serve as inspiration for your own
  creative uses of our service.
  
  This application will go through all the steps you'll need to create models
  for your own data sets and start getting predictions back in just a few
  minutes.
  
  #############################################################################
'''

from grokpy import Grokpy
import time

def HelloPredictions():
  
  '''
  The first thing that you'll need is your API key. You've created an account
  at grok.numenta.com right?
  
  Go to grok.numenta.com/account/profile and look for your API key now.
  
  Back? Good! Enter that key below

  NOTE: A slightly more secure method is to store your API key in your shell
  environment.
  
  From the command line:

    echo "export GROK_API_KEY=PUT_YOUR_KEY_HERE" >> ~/.bashrc
    source ~/.bashrc
  '''
  
  key = 'PUT_YOUR_KEY_HERE'
  
  '''
  Now we need a way to interact with the prediction service. That is going to
  be through a grokpy object. After we give it our credentials we'll have
  full access to all the functionality of the API.
  '''


  grok = Grokpy(key, baseURL, credentials)
    
  '''
  The working areas, where you'll build models, stream in data, and launch
  swarms (searches) is called a 'project.' Lets see if we have any projects.
  '''
  now = time.time()
  projectName = 'HelloPrediction' + str(now)
  
  myProject = grok.createProject(projectName)

  print myProject.getDescription()
  
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
            "formatString":"sdf\/yyyy-MM-dd H:m:s.S"
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
  
  myModel = project.createModel()
  

if __name__ == '__main__':
  HelloPredictions()