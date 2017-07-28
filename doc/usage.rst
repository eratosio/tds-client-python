Using the Client
================

Creating the Client
-------------------

At the heart of the client library is the `Client` class. This class is used to
store the connection details for communicating with a TDS server - in
particular, the URLs of the server and of its root catalog, and a
``requests.Session`` object that is used to manage HTTP requests to the server.

The simplest approach to creating a new client is to simply pass the TDS
server's URL to the `Client` constructor:

.. code-block:: python
   
   from tds_client import Client
   
   client = Client('http://example.com/thredds')

For flexibility, the constructor also accepts the TDS server's root catalog URL.
For example, the following code will create a `Client` configured to connect to
the same TDS server as the previous example:

.. code-block:: python
   
   client = Client('http://example.com/thredds/catalog.xml')

The server URL and catalog URL of the server can be obtained through the
client's ``context_url`` and ``catalog_url`` parameters respectively:

.. code-block:: python
   
   print client.context_url # prints http://example.com/thredds
   print client.catalog_url # prints http://example.com/thredds/catalog.xml

The client may also be passed a ``requests.Session`` object when it is
constructed. This is useful, for example, to implement authentication on
requests:

.. code-block:: python
    
    from requests import Session
    from tds_client import Client
    
    # Setup session with HTTP basic authentication.
    session = Session()
    session.auth = ('username', 'password')
    
    # Create client using authenticated session.
    client = Client('http://example.com/thredds', session)

If no session is passed at construction, the client uses a default-initialised
session object.

Although a client's ``context_url`` and ``catalog_url`` are fixed at
construction, the ``session`` may be altered as required by either modifying the
session in place, or replacing with a new session:

.. code-block:: python
    
    from requests import Session
    from tds_client import Client
    
    # Create client with default session configuration.
    client = Client('http://example.com/thredds')
    
    # Add basic authentication in-place.
    client.session.auth = ('username', 'password')
    
    # Or, replace with new session.
    session = Session()
    session.auth = ('username', 'password')
    client.session = session

Please refer to the ``requests`` documentation for more detail on using
sessions.

Obtaining a Dataset
-------------------

Conceptually, a TDS dataset consists of some data stored on the TDS server, and
a number of services that can be used to access that data. The TDS server is
identified by its URL (e.g. ``http://example.com/thredds``) and the dataset by
its relative URL path (e.g. ``dataset.nc``). The client's `Dataset` class is
used to represent such a dataset.

The simplest approach for obtaining a `Dataset` instance corresponding to a
known dataset is to use the `Dataset.from_url` static method, passing in the
TDS server's URL and the relative path of the dataset:

.. code-block:: python
   
   from tds_client import Dataset
   
   dataset = Dataset.from_url('dataset.nc', context_url='http://example.com/thredds')

Internally, this creates a new default-configured `Client` instance for the
``http://example.com/thredds`` TDS server, then creates the new `Dataset`
representing the dataset ``dataset.nc`` on that server.

The method also accepts a ``session`` keyword argument which can be used to
set the session of the newly created client.

Of course, it's not necessary to create a new `Client` instance if you already
have an appropriate client configured. To use a pre-existing client instead of
creating a new one, simply pass it as the method's ``client`` parameter instead
of supplying a ``context_url``:

.. code-block:: python
   
   from tds_client import Client, Dataset
   
   client = Client('http://example.com/thredds')
   
   dataset = Dataset.from_url('dataset.nc', client=client)

The new dataset now uses the given client's configuration (base URL, session
properties, etc) for all requests.

As a further convenience, it's possible to obtain a `Dataset` instance from a
fully-qualified TDS service URL. For example, given the URL
``http://example.com/thredds/dodsC/dataset.nc`` representing the OPeNDAP service
for the dataset ``dataset.nc`` hosted on the TDS server at
``http://example.com/thredds``, it's possible to obtain an corresponding
`Dataset` instance as follows:

.. code-block:: python
   
   from tds_client import Dataset
   
   dataset = Dataset.from_url('http://example.com/thredds/dodsC/dataset.nc')

This splits the URL into its TDS server URL and datset path based on the
``dodsC`` path component (indicating the OPeNDAP service endpoint), then creates
the new `Dataset` instance as described previously.

As with the first example, this creates a new default-configured `Client`
instance for the ``http://example.com/thredds`` TDS server. The ``client``
parameter may still be used to supply a pre-configured client, even when using
a fully-qualified service URL. However, the TDS server URL determined from the
service URL **must** match that of the client:

.. code-block:: python
   
   from tds_client import Client, Dataset
   
   client = Client('http://example.com/thredds')
   
   # OK: TDS URLs match.
   dataset = Dataset.from_url('http://example.com/thredds/dodsC/dataset.nc', client=client)
   
   # Not OK: TDS URLs don't match.
   dataset = Dataset.from_url('http://example.org/thredds/dodsC/dataset.nc', client=client)

Note that datasets obtained using fully-qualified service URLs behave exactly
the same as any other dataset - in particular, they are not in any way
restricted to only accessing the service whose URL was supplied.

.. note::
   
   At present the `Dataset.from_url` method is the only supported approach for
   obtaining a `Dataset` instance. It is intended that future versions of the
   client will allow dynamic discovery of datasets through the TDS server's
   catalog.

Accessing Dataset Services
--------------------------

Having obtained a `Dataset` object, the next step is to obtain the corresponding
data using one or more of the dataset's available services.

The dataset's available services are listed in its ``services`` property, which
contains a Python dictionary object in which each key is a "service ID", and the
corresponding value is a "service object" providing access to the dataset's data
via that service:

.. code-block:: python
   
   from tds_client import Dataset
   
   # Obtain dataset.
   dataset = Dataset.from_url('http://example.com/thredds/dodsC/dataset.nc')
   
   # List available services.
   for service_id in dataset.services:
       service = dataset.services[service_id]
       
       print '{}: {}'.format(service_id, service.name)
   
   # Prints, for example, 'ncss: NetCDF Subset Service'
   # and 'opendap: OPeNDAP'

As demonstrated above, each service has a ``name`` and ``description`` property,
providing a human-friendly description of the service. Each service is of a
different class, and provides different methods - for example, the ``ncss``
service is implemented by the `NetCDFSubsetService` class, and provides a
:meth:`get_subset` method for obtaining data. Please refer to the following
documentation for more information regarding the built in services.

The `Dataset` class also allows attribute-style access to services as a
convenience. For example, if it is known that your dataset exposes a NetCDF
Subset Service endpoint, you can access that service more simply by using the
dataset's ``ncss`` attribute:

.. code-block:: python
   
   from tds_client import Dataset
   
   # Obtain dataset.
   dataset = Dataset.from_url('http://example.com/thredds/dodsC/dataset.nc')
   
   # Obtain NCSS service.
   ncss = dataset.ncss
   # equivalent to dataset.services['ncss']

Requesting Data via OPeNDAP
---------------------------

OPeNDAP provides basic access to datasets hosted under TDS, allowing extraction
of the raw numeric data and it's accociated key/value metdata.

The client's OPeNDAP functionality is contained within the `OPeNDAPService`
class, which exposes a :meth:`get_dataset` method for obtaining the dataset's
data:

.. code-block:: python
   
   from tds_client import Dataset
   
   # Obtain dataset.
   dataset = Dataset.from_url('http://example.com/thredds/dodsC/dataset.nc')
   
   # Use OPeNDAP service to obtain data.
   data = data.opendap.get_dataset()
   
   # Print the dataset's "testattr" attribute.
   print data.testattr
   
   # Print the values in the dataset's "testvar" variable.
   print data.testvar.array[:].data

The "data" returned by the :meth:`get_dataset` method is, in fact, an instance
of a - |pydap|_ dataset object. Please refer to the ``pydap`` documentation for
more details on extracting data from the returned dataset object.

Requesting Data via NCSS
------------------------

The NetCDF Subset Service (NCSS) provides access to the raw numeric data of
datasets hosted under TDS, with the added functionality of also allowing a
geographically or temporally bound subset of the data to be defined.

The client's NCSS functionality is contained within the `NetCDFSubsetService`
class, which exposes a :meth:`get_subset` method for obtaining the dataset's
data:

.. code-block:: python
   
   from tds_client import Dataset
   
   # Obtain dataset.
   dataset = Dataset.from_url('http://example.com/thredds/dodsC/dataset.nc')
   
   # Use NCSS service to obtain data points within
   # +/- 10 degrees of (0,0) lat/lon.
   data = data.ncss.get_dataset(var='testvar', north=10,
       south=-10, eash=10, west=-10)
   
   # Print the dataset's "testattr" attribute.
   print data.testattr
   
   # Print the values in the dataset's "testvar" variable.
   print data.testvar.array[:].data

As with the OPeNDAP service, the returned data is a ``pydap`` dataset object.

.. |pydap| replace:: ``pydap``
.. _pydap: http://pydap.readthedocs.io/en/latest/
