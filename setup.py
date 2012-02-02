#!/usr/bin/python
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from grokpy import __version__

# 2.5 compatability - don't use with
f = open(os.path.join(os.path.dirname(__file__), 'README.md'))
long_description = f.read()
f.close()

sdict = {
    'name' : 'grokpy',
    'version' : __version__,
    'description' : 'Python client for Grok Prediction Service',
    'long_description' : long_description,
    'url': 'http://github.com/numenta/grok-py',
    'download_url' : 'http://cloud.github.com/downloads/numenta/grok-py/grokpy-%s.tar.gz' % __version__,
    'author' : 'Ian Danforth',
    'author_email' : 'idanforth@numenta.com',
    'maintainer' : 'Ian Danforth',
    'maintainer_email' : 'idanforth@numenta.com',
    'keywords' : ['numenta', 'prediction'],
    'license' : 'MIT',
    'packages' : ['grokpy', 'grokpy.httplib2'],
    'classifiers' : [
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python'],
}

setup(**sdict)
