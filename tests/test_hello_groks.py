import os
import re
import subprocess
from optparse import OptionParser
import unittest
import xmlrunner

globaloptions = {}

def sed(filename,patterns):
  def do_sed(string):
    outstring = string
    for pattern, repl in patterns:
      outstring = re.sub(pattern,repl,outstring)
    return outstring

  text = None
  with open(filename,'r') as f:
    text = f.read()
  transformed = map(do_sed,text.splitlines())
  with open(filename,'w') as f:
    f.write("\n".join(transformed))

def transform_code(patterns,filename):
  sed(filename,patterns)
 
class HelloGrokTest(unittest.TestCase):
 
  def __init__(self, testname, options):
    self.options = options
    super(HelloGrokTest, self).__init__(testname)

  def test_hellogrok_1(self):
    options = self.options
    patterns = [("YOUR_KEY_HERE", options.key),
                ("Client\(API_KEY\)", "Client(API_KEY,\"%s\")" % options.domain)]
    transform_code(patterns,"HelloGrok.py")
    output = subprocess.Popen("python HelloGrok.py",
        stdout=subprocess.PIPE,
        shell=True).stdout.read()
    model_id = None
    for line in output.splitlines():
      m = re.search("MODEL_ID\:\s*(.+)$",line)
      if m is not None:
        model_id = m.group(1)
        break
    self.assertTrue(model_id != None)
    globaloptions['model_id'] = model_id
  
  def test_hellogrok_2(self):
    options = self.options
    patterns = [("YOUR_KEY_HERE", options.key),
                ("Client\(API_KEY\)", "Client(API_KEY,\"%s\")" % options.domain),
                ("YOUR_MODEL_ID_HERE", options.model_id)]
    transform_code(patterns,"HelloGrokPart2.py")
    output = subprocess.Popen("python HelloGrokPart2.py",
        stdout=subprocess.PIPE,
        shell=True).stdout.read()
    m = re.search("Wonderful",output)
    self.assertTrue(m != None)
    
  
  def test_hellogrok_3(self):
    options = self.options
    print "Starting part 3:"
    print options
    patterns = [("YOUR_KEY_HERE", options.key),
                ("Client\(API_KEY\)", "Client(API_KEY,\"%s\")" % options.domain)]
    transform_code(patterns,"HelloGrokPart3.py")
    output = subprocess.Popen("python HelloGrokPart3.py",
        stdout=subprocess.PIPE,
        shell=True).stdout.read()
    print output

parser = OptionParser()
parser.add_option("-d", "--domain", dest="domain", 
    default="http://api.numenta.com",
    help="domain to target tests to")
parser.add_option("-k", "--key", dest="key",
    default='fakeApiKey', help="API key to use")
parser.add_option("-m", "--model", dest="model_id",
    default=None, help="model_id to use for part2")
(options, args) = parser.parse_args()

if not getattr(options,"model_id"):
  suite = unittest.TestSuite()
  suite.addTest(HelloGrokTest("test_hellogrok_1", options))
  xmlrunner.XMLTestRunner(output='results').run(suite)
  options.model_id = globaloptions['model_id']
if getattr(options,"model_id"):
  suite = unittest.TestSuite()
  suite.addTest(HelloGrokTest("test_hellogrok_2", options))
  xmlrunner.XMLTestRunner(output='results').run(suite)

suite = unittest.TestSuite()
suite.addTest(HelloGrokTest("test_hellogrok_3", options))
xmlrunner.XMLTestRunner(output='results').run(suite)
