#!/usr/bin/python
import os
from ntabeta import __version__
 
f = open(os.path.join(os.path.dirname(__file__), 'README.md'))
long_description = f.read()
f.close()

sdict = {
    'name' : 'ntabeta',
    'version' : __version__,
    'description' : 'Python client for ntabeta Prediction Service',
    'long_description' : long_description,
    'url': 'http://github.com/numenta/ntabeta-py',
    #'download_url' : 'http://cloud.github.com/downloads/andymccurdy/redis-py/redis-%s.tar.gz' % __version__,
    'author' : 'Ian Danforth',
    'author_email' : 'idanforth@numenta.com',
    'maintainer' : 'Ian Danforth',
    'maintainer_email' : 'idanforth@numenta.com',
    'keywords' : ['numenta', 'prediction'],
    'license' : 'MIT',
    'packages' : ['ntabeta'],
    'test_suite' : 'tests.all_tests',
    'classifiers' : [
        'Development Status :: 1 - Planning Development Status',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'],
}

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(**sdict)
