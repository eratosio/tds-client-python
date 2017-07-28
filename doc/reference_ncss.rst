:orphan:

NetCDF Subset Service
=====================

Overview
--------

The `NetCDF Subset Service <http://www.unidata.ucar.edu/software/thredds/current/tds/reference/NetcdfSubsetServiceReference.html>`_
(NCSS) protocol allows access to a dataset's metadata and raw data values,
similar to the :doc:`OPeNDAP <reference_opendap>` protocol. However, there are
two key differences between the two:

- NCSS allows for spatio-temporal subsetting. That is, it is possible with the
  NCSS to extract a subset of the dataset whose data is limited to a geographic
  bounding box or to a temporal window.
- NCSS doesn't support lazy loading of data from the server - once the request
  has been made, all of the relevant data is returned from the server, whether
  it is subsequently used or not.

This library provides access to NCSS services using the `NetCDFSubsetService`
class, described below. There is typically no need to instantiate this class
directly, instead instances of the class are typically obtained by accessing the
``ncss`` attribute of a `Dataset` object, or by accessing the ``ncss`` key of
the dataset's ``services`` attribute. Please refer to the following section for
examples.

This service is a thin wrapper around the `pydap 
<http://pydap.readthedocs.io/en/latest/>`_ library. It returns instances of the
``pydap.model.DatasetType`` class as a result of the ``get_subset`` operation -
please refer to the ``pydap`` documentation for more details.

Usage Example
-------------

The following code demonstrates how to access the raw data for a variable
``testvar`` of a dataset ``test/dataset.nc`` hosted on a TDS server located at
``http://example.com/thredds``. The dataset is limited to a bounding box
spanning longitudes from 10 degrees west to 10 degrees east of the datum, and
latitudes from 10 degrees south to 10 degrees north of the datum.

.. code-block:: python
   
   from tds_client import Dataset
   
   # Create dataset object.
   tds_dataset = Dataset.from_url('test/dataset.nc',
       context_url='http://example.com/thredds')
   
   # Obtain pydap dataset object via NCSS.
   ncss_dataset = tds_dataset.ncss.get_dataset(var='testvar',
       north=10, south=-10, east=10, west=-10)
   # Alternatively: tds_dataset.services['opendap'].get_subset(...)
   
   # Obtain the raw data for the variable `testvar`.
   # See the pydap documentation for more explanation.
   data = ncss_dataset.testvar.array[:].data

If the full NCSS URL of the dataset is known, it is possible to use the
:func:`get_subset` method to achieve the same result:

.. code-block:: python
   
   from tds_client.service import ncss
   
   url = 'http://example.com/thredds/ncss/dataset.nc'
   dap_dataset = ncss.get_subset(url, var='testvar', north=10,
       south=-10, east=10, west=-10)
   data = dap_dataset.testvar.array[:].data

Reference
---------

.. note::
      
      The ``NetCDFSubsetService`` class is not intended to be directly
      instantiated, and should only by accessed through the ``ncss`` property of
      a `Dataset` object, or through the ``ncss`` key of a dataset's
      ``services`` property.

The client's NetCDF Subset Service functionality can be found in the
``tds_client.services.ncss`` module. The service ID of the `NetCDFSubsetService`
class is ``ncss``.

.. class:: NetCDFSubsetService
   
   This is the NetCDF Subset Service class. An instance of this class
   corresponding to a dataset's NCSS endpoint can be found in the dataset's
   ``ncss`` property.
   
   .. method:: get_subset(session=None, **kwargs)
      
      Used to obtain a `pydap <http://pydap.readthedocs.io/en/latest/>`_
      dataset object representing the dataset the service is attached to, via
      NCSS.
      
      By default, the service uses the dataset's client's session object to make
      HTTP requests. If necessary, this behaviour can be overridden by providing
      a ``requests.Session`` object as the value of this method's ``session``
      parameter.
      
      The method accepts a large number of keyword arguments to define the
      subset of the dataset to return - please refer to the documentation of the
      :func:`get_subset` function for complete details.
      
      Returns a ``pydap`` dataset corresponding to selected subset of the
      dataset the service is attached to.
      
      Note that this method internally is a simple wrapper around the
      :func:`get_subset` function (see below) which simply computes the
      appropriate URL from the dataset, and passes the appropriate session
      object.

.. function:: get_subset(url, session=None, **kwargs)
      
   This helper function can be used to directly obtain a ``pydap`` dataset
   object if the full URL of a dataset's NCSS endpoint is known.
   
   The ``url`` parameter **must** be a fully-qualified URL to an NCSS endpoint
   (e.g. ``http://example.com/thredds/ncss/dataset.nc``). This is *not* checked
   client-side, and invalid URLs may result in an error response from the TDS
   server.
   
   If provided, the ``session`` parameter must be a ``requests.Session`` object,
   which is used to make the HTTP requests to the server.
   
   This function accepts a large number of keyword arguments, corresponding to
   the `NCSS protocol request parameters <http://www.unidata.ucar.edu/software/thredds/current/tds/reference/NetcdfSubsetServiceReference.html#Common>`_.
   The following table summarises the available keyword arguments and their
   purpose, please refer to the NCSS documentation for canonical interpretation
   of these parameters.
   
   +-----------------------+---------------------------------------------------+
   | Parameter             | Purpose                                           |
   +=======================+===================================================+
   | ``var``               | Accepts a comma-delimited string listing the      |
   |                       | dataset variables that should be included in the  |
   |                       | returned dataset.                                 |
   +-----------------------+---------------------------------------------------+
   | ``latitude``,         | Used to obtain a "point" dataset, limited to data |
   | ``longitude``         | occurring at the given geographical point.        |
   +-----------------------+---------------------------------------------------+
   | ``north``, ``south``, | Used to define a geographic bounding box for the  |
   | ``east``, ``west``    | returned dataset.                                 |
   +-----------------------+---------------------------------------------------+
   | ``minx``, ``maxx``,   | Used to define a bounding box in projection       |
   | ``miny``, ``maxy``    | coordinates.                                      |
   +-----------------------+---------------------------------------------------+
   | ``horizStride``,      | Used to declare the "stride" in the horizontal    |
   | ``timeStride``        | plane and time dimension respectively. For        |
   |                       | example, ``horizStride=2`` means "take data from  |
   |                       | every second location in the horizontal plane".   |
   +-----------------------+---------------------------------------------------+
   | ``addLatLon``         | If set to ``True``, causes missing lat/lon        |
   |                       | coordinates to be automatically generated.        |
   +-----------------------+---------------------------------------------------+
   | ``time``              | When given a date/time in ISO 8601 format, the    |
   |                       | returned data consists of a single slice in       |
   |                       | temporal dimension, corresponding to the data     |
   |                       | closest in time to the given date/time.           |
   +-----------------------+---------------------------------------------------+
   | ``time_start``,       | Used to define a temporal range for the returned  |
   | ``time_end``,         | dataset. The ``time_start`` and ``time_end`` must |
   | ``time_duration``     | be ISO 8601 date-time strings, and the            |
   |                       | ``time_duration`` must be an ISO 8601 duration    |
   |                       | string. Any two of these three parameters may be  |
   |                       | used to declare the time window of interest.      |
   +-----------------------+---------------------------------------------------+
   | ``temporal``          | If provided with the string ``"all"``, then the   |
   |                       | returned data will span the entire temporal       |
   |                       | range.                                            |
   +-----------------------+---------------------------------------------------+
   | ``vertCoord``         | For dataset that have more than one vertical      |
   |                       | coordinate, may be used to specify which one to   |
   |                       | return.                                           |
   +-----------------------+---------------------------------------------------+
   | ``subset``            | Used for determining the subsetting type when     |
   |                       | obtaining a "station" dataset.                    |
   +-----------------------+---------------------------------------------------+
   | ``stns``              | Used to list the stations to return when          |
   |                       | obtaining a "station" dataset.                    |
   +-----------------------+---------------------------------------------------+
   
   In addition to these parameters, the method also accepts a number of "alias"
   parameters, that serve as more compact and/or more Pythonic equivalents to
   the official parameters described above (which all follow the official NCSS
   naming scheme):
   
   +------------------+--------------------------------------------------------+
   | Parameter        | Is Equivalent To                                       |
   +==================+========================================================+
   | ``vars``         | ``var``                                                |
   +------------------+--------------------------------------------------------+
   | ``lat``          | ``latitude``                                           |
   +------------------+--------------------------------------------------------+
   | ``lon``          | ``longitude``                                          |
   +------------------+--------------------------------------------------------+
   | ``n``            | ``north``                                              |
   +------------------+--------------------------------------------------------+
   | ``e``            | ``east``                                               |
   +------------------+--------------------------------------------------------+
   | ``s``            | ``south``                                              |
   +------------------+--------------------------------------------------------+
   | ``w``            | ``west``                                               |
   +------------------+--------------------------------------------------------+
   | ``min_x``        | ``minx``                                               |
   +------------------+--------------------------------------------------------+
   | ``min_y``        | ``miny``                                               |
   +------------------+--------------------------------------------------------+
   | ``max_x``        | ``maxx``                                               |
   +------------------+--------------------------------------------------------+
   | ``max_y``        | ``maxy``                                               |
   +------------------+--------------------------------------------------------+
   | ``horiz_stride`` | ``horizStride``                                        |
   +------------------+--------------------------------------------------------+
   | ``add_lat_lon``  | ``addLatLon``                                          |
   +------------------+--------------------------------------------------------+
   | ``time_stride``  | ``timeStride``                                         |
   +------------------+--------------------------------------------------------+
   | ``vert_coord``   | ``vertCoord``                                          |
   +------------------+--------------------------------------------------------+
   
   There are a few caveats concerning which of these parameters may be present
   or absent on any given request:
   
   - The ``var`` parameter (or its alias ``vars``) must *always* be supplied.
   - Some groups of parameters are mutually exclusive: for example, it is an
     error to supply both the ``latitude``/``longitude`` parameters at the same
     time as the ``north``/``south``/``east``/``west`` parameters, since they
     represent different methods of geospatial subsetting.
   - Some parameters are mutually dependent, for example if either of the
     ``latitude`` or ``longitude`` parameters are supplied, then they both must
     be supplied.
   - The ``time_start``, ``time_end`` and ``time_duration`` parameters are a
     special case: either none of these parameters should be supplied, or any
     two (no more or less) must be supplied.
   - A parameter and its aliased version should not appear in the same request -
      for example, it is an error to supply both the ``n`` and ``north``
      parameters on the same request.
   
   The service class makes a best-effort attempt to catch these situations and
   throw a meaningful ``ValueError`` exception describing the problem. It is
   possible that not all such errors are covered, and invalid parameter
   combinations may instead result in an error returned by the TDS server.
   
   Returns a ``pydap`` dataset corresponding to selected subset of the dataset.
