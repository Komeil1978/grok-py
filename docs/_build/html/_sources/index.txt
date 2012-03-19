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

Grab `the latest stable build`_ by clicking either 'Download as zip' or
'Download as tar.gz' on the linked page. After uncompressing that file you
can then install the grokpy library.::

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

`Send Feedback on Installation <mailto:support@numenta.com?subject=Python-docs
-feedback:Installation>`_

.. _getting started:

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

`Send Feedback on Getting Started <mailto:support@numenta.com?subject=Python-docs
-feedback:GettingStarted>`_

.. _api reference:

API Reference
==================

A complete guide to all public APIs found in `grok-py`. Auto-generated.

.. toctree::
   :numbered:
   :maxdepth: 2

   grokpy

`Send Feedback on API Reference <mailto:support@numenta.com?subject=Python-docs
-feedback:APIReference>`_

.. _support and development:

Support and Development
==========================

Questions? Bugs?
----------------

We welcome all feedback and bug reports! Please send us an email at:
support@numenta.com

Releases
--------

Development of Grok client libraries happens internally and are then released
to github master at the same time as we release server side code. Github master
can thus be considered STABLE.

Code is pushed Tuesday afternoons (pst).

Changelog
---------

`<https://github.com/numenta/grok-py/blob/master/CHANGES>`_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
