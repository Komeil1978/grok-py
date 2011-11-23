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

import grokpy

def HelloPredictions():
  
  '''
  The first thing that you'll need is your API key. You've created an account
  at grok.numenta.com right?
  
  Go to grok.numenta.com/account and look for your API key now. I'll wait ...
  
  Back? Good! Enter that key below

  NOTE: A slightly more secure method is to store your API key in your shell
  environment.
  
  From the command line:

    echo "export grok_API_KEY=PUT_YOUR_KEY_HERE" >> ~/.bashrc
    source ~/.bashrc
  '''
  
  key = 'PUT_YOUR_KEY_HERE'
  
  '''
  Now we need to instantiate a client object. This will be the single point of
  entry for all your code that interacts with the Grok Prediction Service.
  '''
  
  c = grokpy.Client(key)
  
  url = 'version/1/service/providerList'
  
  services = c.availableServices()
  
  print 'The following services are available from the Grok API:'
  for service in services:
    print service

if __name__ == '__main__':
  HelloPredictions()