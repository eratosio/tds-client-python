.. TDS Client documentation master file, created by
   sphinx-quickstart on Tue Jul 25 12:55:58 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

TDS Client
==========

TDS Client is a client library for the `Thredds Data Server <http://www.unidata.ucar.edu/software/thredds/current/tds/>`_ (TDS).

Installation
------------

You can find the latest source code for the TDS Client library in its official Bitbucket repository.

Having cloned or downloaded the source, you can install the library locally using its ``setup.py`` file:

.. code-block:: bash

    $ sudo python setup.py install

Third-Party Dependencies
------------------------

The client employs two third-party libraries under the hood:

- |requests|_ is used for performing HTTP requests.
- |pydap|_ is used for interacting with NetCDF datasets.

There is no need to manually install these libraries - they are both
automatically installed as part of the installation process described above.
However, it may be useful to gain some familiarity with these libraries before
using the TDS client, as there are places where objects from these libraries are
accepted and/or returned by the TDS client library.

Contents
--------

.. toctree::
   :maxdepth: 3
   
   usage
   reference
   licence

.. |requests| replace:: ``requests``
.. _requests: http://docs.python-requests.org/en/master/

.. |pydap| replace:: ``pydap``
.. _pydap: http://pydap.readthedocs.io/en/latest/
