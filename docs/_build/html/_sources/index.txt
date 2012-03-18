.. Grokpy documentation master file, created by
   sphinx-quickstart on Wed Feb 29 11:45:06 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


==========================
Grok Python Client Library
==========================

Grokpy is the Python client for Grok, Numenta's Prediction Service. It wraps
the `Grok HTTP API <http://grok.numenta.com/resources>`_ in a convenient Python
library.

.. _installation:

Installation
============

With Example Apps (Recommended)
-------------------------------

Grab `the latest stable build`_ and install it. ::

    $ python setup.py install

.. _the latest stable build: http://github.com/numenta/grok-py/downloads

Or, you can clone the repo. (Master is always stable.) ::

    $ git clone git@github.com:numenta/grok-py.git
    $ cd grok-py
    $ python setup.py install

Just the Client Library
-----------------------

Install using pip, a package manager for Python. ::

    $ pip install grokpy

Don't have pip installed? You should! ::

    $ curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python

Getting Started
================

After you have installed the client library you should read through the source
of the sample application HelloGrok.

The sample app is laid out as a tutorial and has extensive comments to get you
up to speed on using Grok.

Once you have read through the code please run::

  $ python HelloGrok.py

Hopefully with minor modifications to the sample app you will be able to build
useful predictive models of your data.

.. _user-guide:

User Guide
==================

these are more words

API Reference
==================

A complete guide to all public APIs found in `grok-py`. Auto-generated.

.. toctree::
   :numbered:
   :maxdepth: 2

   grokpy

Support and Development
==========================

Bug reports and questions: support@numenta.com

A note about releases:

Development of Grok client libraries happens internally and are then released
to github master at the same time as we release server side code. Github master
 can thus be considered STABLE.

Changelog: `<https://github.com/numenta/grok-py/blob/master/CHANGES>`_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
