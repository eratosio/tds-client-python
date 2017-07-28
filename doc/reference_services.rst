Services
========

Overview
--------

A TDS server typically exposes multiple services for each dataset, which can be
used to obtain data in a variety of formats. For example, the OPeNDAP service
can be used to obtain the raw grid data, the Web Map Service can be used to
obtain geospatially-referenced bitmap images representing the data, etc.

The TDS client library exposes these services as "service" objects attached to
each dataset. These are specialised classes subclassing the client's `Service`
class, each implementing a particular service. These classes each have a
"service ID", used to uniquely identify the service among all those present on a
particular dataset.

As a concrete example, the `OPeNDAPService` class provides access to raw data
using the TDS OPeNDAP service. It exposes a single method ``get_dataset``, which
can be used to retrieve the dataset's data. It has a service ID of ``opendap``.
As such, given a `Dataset` instance ``my_dataset`` pointing to a TDS dataset
which supports OPeNDAP, the following line of code can be used to retrieve the
dataset's data::

   data = my_dataset.opendap.get_dataset()

Current Built-In Services
-------------------------

At present, the following services have built-in support:

+-----------------------------------------------+-------------+----------------------------------------+
| Service                                       | Service ID  | Service Class                          |
+===============================================+=============+========================================+
| :doc:`NetCDF Subset Service <reference_ncss>` | ``ncss``    | `NetCDFSubsetService`                  |
+-----------------------------------------------+-------------+----------------------------------------+
| :doc:`OPeNDAP <reference_opendap>`            | ``opendap`` | `OPeNDAPService`                       |
+-----------------------------------------------+-------------+----------------------------------------+

For details of the operations supported by each service, please refer to the
documentation linked in the above table.

Implementing Additional Services
--------------------------------

The client uses `setuptools <https://setuptools.readthedocs.io/en/latest/>`_
`"entry points" <http://setuptools.readthedocs.io/en/latest/pkg_resources.html#entry-points>`_
functionality to dynamically discover and load service classes. As such,
implementing a new service consists of implementing the service class, and
writing a ``setup.py`` script to install the class and register the class as a
valid service class entrypoint.

The first step is fairly simple: you need only implement a class that extends
`Service` or `StandardService` (see following section). If your class declares
a constructor, it must ensure to pass all parameters to the superclass
constructor.

As a simple example, consider service that does nothing but return a count of
how many times it has been called:

.. code-block:: python
   
   from tds_client.service import Service
   
   class CountService(Service):
       name = 'Count Service'
       description = 'Counts how many times the count() method is called.'
       
       def __init__(self, *args, **kwargs):
           super(CountService, self).__init__(*args, **kwargs)
           
           self._count = 0
       
       def count(self):
           self._count += 1
           return self._count

The points of interest in the above code:

1) The service extends `Service`, since it isn't a "standard" TDS service.
2) The class declares two attributes ``name`` and ``description`` that provide
   human-readable information for clients. **These properties are mandatory.**
3) The constructor accepts generic ``*args`` and ``**kwargs`` and passes them on
   untouched to the superclass using ``super``.
4) The constructor initialises the class' ``_count`` property to zero.
5) The class implements a ``count`` method which simply increments and returns
   ``_count``.

With the service class written, the next step is to write the ``setup.py`` file.
If we assume the service is contained in a package ``tds_count_service``, then
a minimal ``setup.py`` would look something like the following:

.. code-block:: python
   
   from setuptools import setup, find_packages
   
   setup(
       name = 'tds_count_service',
       packages = find_packages(),
       entry_points = {
           'tds_client.service': [
               'count = tds_count_service:CountService'
           ]
       }
   )

The important part here is the ``entry_points`` declaration. The client's
service loader mechanism looks for entry points declared in the
``tds_client.service`` group, so that's the group the setup script uses.
Following the entry point group name is a list of the actual entry points that
are to be installed - in this case, just the ``CountService`` entry point. In
the entry point declaration, the key ``count`` is used as the service ID, and
the value ``tds_count_service:CountService`` is the module name and class name
of the service class, separated with a colon.

The above setup script can then be used to install the new service, at which
point it becomes available to datasets. In this case, since the service entry
point was declared with the ID ``count``, the service will be available in the
``count`` key of each dataset's ``services`` property, or as a ``count``
property on the dataset itself:

.. code-block:: python
   
   from tds_client import Dataset
   
   # Get dataset.
   dataset = Dataset.from_url('http://example.com/thredds/dodsC/dataset.nc')
   
   # Get count service.
   count_svc = dataset.services['count']
   # Or, alternatively, count_svc = dataset.count
   
   # Call the count service a few times.
   print count_svc.count() # Prints 1
   print count_svc.count() # Prints 2
   print count_svc.count() # Prints 3
   
Note that datasets each have their own unique instances of each service, so
state stored in the service instance is not shared across datasets. If state
needs to be shared, use class properties instead of instance properties.
           
Class Reference
---------------

The client declares two base classes for services, both in package
``tds_client.service``: `Service` and `StandardService`.

The decision whether to subclass `Service` or `StandardService` revolves around
whether the service being implemented is one of the "standard" services directly
exposed by thredds (e.g. OPeNDAP, WMS, WCS, etc). Standard services are those
services that can be declared available on a dataset within the TDS catalog
configuration, and which have a well-defined URL path component that identifies
the location of that service's endpoints on the TDS server (e.g. the ``dodsC``
path that OPeNDAP resides at). If implementing such a service, it should
subclass `StandardService`, otherwise it should subclass `Service` directly.

In either case, there a few requirements that the service class **must** adhere
to:

- It must declare class or instance level ``name`` and ``description``
  properties, used to provide human-readable documentation for users.
- If it declares a constructor, it must pass any received parameters to the 
  superclass constructor unmodified.

In the case of services derived from `StandardService`, the class must also
declare a class-level ``path`` attribute containing the service's URL path
component as a string (e.g. the `OPeNDAPService` class's ``path`` attribute is
``"dodsC"``).

.. class:: Service
   
   The base class for all services. Subclass this directly if not implementing a
   "standard" service.
   
   Of the following documented members of this class, those beginning with
   underscores may be used by subclasses in order to implement their
   functionality, but are not intended to be used by end-users of the service.
   
   .. attribute:: _dataset
      
      The dataset to which the service is attached. Read-only.
   
   .. attribute:: client
      
      The attached dataset's `Client` instance. Read-only.
   
   .. attribute:: _session
      
      The ``requests`` session object to use for HTTP requests, as obtained from
      the dataset's client instance. Read-only.
   
   .. method:: _resolve_url(service_path):
      
      Given a URL path component (typically the service's path component),
      construct a fully-qualified URL consisting of the dataset's client's
      context URL, the given URL path, and the dataset's URL path.
   
   .. classmethod:: split_url(url)
      
      Given a fully-qualified URL, attempts to split the URL into three
      components: a TDS server context URL, a service path component, and a
      dataset path.
      
      Subclasses should override the default implementation if able - the
      default implementation simply throws ``NotImplementedError``.
      
      See `StandardService.split_url` for a concrete implementation.
      
      Implementations should return the result as a 3-tuple in the order TDS
      context URL, service path component, dataset path. If the URL is valid but
      the service class is unable to split it, it may throw ``ValueError`` or
      return ``None``.

.. class:: StandardService
   
   A base class for services that have a well-defined URL path on a TDS server.
   For example, the built-in class implementing OPeNDAP functionality,
   `OPeNDAPService`, extends this class since OPeNDAP is a core TDS service that
   is available under the ``dodsC`` URL path.
   
   This inherits all the attributes and methods of the `Service` class, and adds
   the following members.
   
   .. attribute:: url
      
      The fully-qualified URL of the service endpoint for the dataset to which
      the service is attached. For example, given a dataset ``dataset.nc``
      attached to a client for the TDS server ``http://example.com/thredds``,
      the OPeNDAP service (which is a `StandardService` subclass with a ``path``
      attribute of ``"dodsC"``) has a ``url`` of
      ``http://example.com/thredds/dodsC/dataset.nc``.
      
      The URL is computed as the service's ``path`` attribute and the attached
      dataset's path concatenated to the dataset's client's context URL.
   
   .. classmethod:: split_url(url)
      
      Overrides the `Service.split_url` method to perform splitting based on the
      service's ``path`` attribute.
