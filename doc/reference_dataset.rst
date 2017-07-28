Dataset
=======

.. class:: tds_client.Dataset(client, url)

   Provides a representation of a TDS dataset.
   
   The ``client`` constructor parameter must be an instance of the ``Client``
   class, which will be used to access the dataset's service endpoints.
   
   The ``url`` constructor parameter must be a partial URL (without any scheme,
   host, port, username or password) identifying the TDS dataset. This URL
   will be resolved against the client's ``context_url`` to determine the final
   URL of each of the dataset's service endpoints. Requests made to these URLs
   will use the client's ``session``.
   
   Typically there should be no need to directly instantiate this class. The
   ``from_url`` static method should be used if it is necessary to manually
   create an instance of this class.
   
   .. attribute:: client
      
      A Client instance to be used to interact with the TDS dataset. When
      accessing services, this dataset's URL is resolved relative to the client
      URL, and the client's ``session`` is used when making HTTP requests.
   
   .. attribute:: url
      
      The dataset's URL (see the ``url`` parameter of the class constructor), as
      a **read-only** property.
   
   .. attribute:: services
      
      A dictionary mapping service IDs to instances of the corresponding service
      class. For example ``my_dataset.services['opendap']`` is an instance of
      the ``OPeNDAPService`` class, providing access to the dataset's OPeNDAP
      endpoint.
      
      See the service documentation for more information regarding services and
      service IDs.
      
      Note that the ``Dataset`` class also provides attribute-style access to
      services - for example, the same service could have been accessed as
      ``my_dataset.opendap``. As such, the ``services`` attribute is mostly
      useful as a way of enumerating the services available for a given dataset.
   
   .. method:: __getattr__(attr)
      
      Used to provide attribute-style access to the dataset's services. For
      example, a dataset's OPeNDAP endpoint can be queried by obtaining the
      corresponding service object from the dataset's ``opendap`` attribute.
   
   .. staticmethod:: from_url(dataset_url, context_url=None, session=None, client=None)
      
      Given a dataset URL (either as a partially-qualified URL path, or as a
      fully-qualified URL to one of the dataset's services), returns a
      corresponding ``Dataset`` instance.
      
      If the given dataset URL is not fully qualified (i.e. has no scheme, host,
      port, username and password), then either the ``context_url`` or
      ``client`` parameters must be supplied.
      
      If the ``context_url`` parameter is supplied, it must be the TDS server's
      application URL (e.g. ``http://example.com/thredds``), or the URL to the
      TDS server's root catalog
      (e.g. ``http://example.com/thredds/catalog.xml``). This URL is then used
      as the "context URL" to fully resolve the dataset URL when accessing
      services.
      
      If, instead, the ``client`` parameter is supplied, it must be an instance
      of the ``Client`` class. The client's ``context_url`` property is then
      used as the dataset's context URL.
      
      If the dataset URL is a fully qualified URL to one of the dataset's
      available services, the context URL is derived by splitting the URL based
      on the position of the service's URL path component - for example,
      the context URL ``http://example.com/thredds`` is derived from
      ``http://example.com/thredds/dodsC/dataset.nc`` by noting the location of
      the ``dodsC`` path component corresponding to the OPeNDAP service. The
      remaining portion after the service path component (i.e. ``dataset.nc`` in
      this case) is then used as the canonical dataset URL.
      
      If the dataset URL is fully qualified and either the ``context_url`` or
      ``client`` parameters are given, it is an error if the context URL derived
      as described in the preceding paragraph doesn't match that of the
      ``context_url`` parameter or the client's ``context_url`` attribute.
      
      If no ``client`` is given, a new ``Client`` instance is created from the
      context URL (as determined from the above rules) and the given ``session``
      (if any).
      
      A new ``Dataset`` instance is then returned, using the client instance and
      dataset URL as determined through the above process.
      
      .. note::
         
         If the ``context_url`` and/or ``session`` parameters are supplied *as
         well as* the ``client`` parameter, a warning will be issued as the
         values supplied by the client will be used in preference.
