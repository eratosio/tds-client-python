:orphan:

OPeNDAP Service
===============

Overview
--------

The `Open-source Project for a Network Data Access Protocol
<https://www.opendap.org/>`_ (OPeNDAP) protocol allows access to a dataset's
metadata and raw data values. Data is loaded from the remote server on an
as-needed basis, allowing for efficient usage of bandwidth.

This library provides access to OPeNDAP services using the `OPeNDAPService`
class, described below. There is typically no need to instantiate this class
directly, instead instances of the class are typically obtained by accessing the
``opendap`` attribute of a `Dataset` object, or by accessing the ``opendap`` key
of the dataset's ``services`` attribute. Please refer to the following section
for examples.

This service is a thin wrapper around the `pydap 
<http://pydap.readthedocs.io/en/latest/>`_ library. It returns instances of the
``pydap.model.DatasetType`` class as a result of the ``get_dataset`` operation -
please refer to the ``pydap`` documentation for more details.

Usage Example
-------------

The following code demonstrates how to access the raw data for a variable
``testvar`` of a dataset ``test/dataset.nc`` hosted on a TDS server located at
``http://example.com/thredds``:

.. code-block:: python
   
   from tds_client import Dataset
   
   # Create dataset object.
   tds_dataset = Dataset.from_url('test/dataset.nc',
       context_url='http://example.com/thredds')
   
   # Obtain pydap dataset object via OPeNDAP.
   dap_dataset = tds_dataset.opendap.get_dataset()
   # Alternatively: tds_dataset.services['opendap'].get_dataset()
   
   # Obtain the raw data for the variable `testvar`.
   # See the pydap documentation for more explanation.
   data = dap_dataset.testvar.array[:].data

If the full OPeNDAP URL of the dataset is known, it is possible to use the
:func:`get_dataset` method to achieve the same result:

.. code-block:: python
   
   from tds_client.service import opendap
   
   url = 'http://example.com/thredds/dodsC/dataset.nc'
   dap_dataset = opendap.get_dataset(url)
   data = dap_dataset.testvar.array[:].data

Reference
---------

.. warning::
      
      The ``OPeNDAPService`` class is not intended to be directly instantiated,
      and should only by accessed through the ``opendap`` property of a
      `Dataset` object, or through the ``opendap`` key of a dataset's
      ``services`` property.

The client's OPeNDAP functionality can be found in the
``tds_client.services.opendap`` module. The service ID of the `OPeNDAPService`
class is ``opendap``.

.. class:: OPeNDAPService
   
   This is the OPeNDAP service class. An instance of this class corresponding
   to a dataset's OPeNDAP service endpoint can be found in the dataset's
   ``opendap`` property.
   
   .. method:: get_dataset(session=None)
      
      Used to obtain a `pydap <http://pydap.readthedocs.io/en/latest/>`_
      dataset object representing the dataset the service is attached to, via
      OPeNDAP.
      
      By default, the service uses the dataset's client's session object to make
      HTTP requests. If necessary, this behaviour can be overridden by providing
      a ``requests.Session`` object as the value of this method's ``session``
      parameter.
      
      Returns a ``pydap`` dataset corresponding to the dataset the service is
      attached to.
      
      Note that this method internally is a simple wrapper around the
      :func:`get_dataset` function (see below) which simply computes the
      appropriate URL from the dataset, and passes the appropriate session
      object.

.. function:: get_dataset(url, session=None)
   
   This helper function can be used to directly obtain a ``pydap`` dataset
   object if the full URL of a dataset's OPeNDAP endpoint is known.
   
   The ``url`` parameter **must** be a fully-qualified URL to an OPeNDAP service
   endpoint (e.g. ``http://example.com/thredds/dodsC/dataset.nc``). This is
   *not* checked client-side, and invalid URLs may result in an error response
   from the TDS server.
   
   If provided, the ``session`` parameter must be a ``requests.Session`` object,
   which is used to make the HTTP requests to the server.
   
   Returns a ``pydap`` dataset corresponding to the given dataset.
