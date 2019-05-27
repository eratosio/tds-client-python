Dataset
=======

.. class:: tds_client.Dataset(client, url)

   Provides a representation of a TDS dataset.
   
   The ``client`` constructor parameter must be an instance of the :class:`Client` class, which will be used to access
   the dataset's service endpoints.
   
   The ``url`` constructor parameter must be a partial URL (without any scheme, host, port, username or password)
   identifying the TDS dataset. This URL will be resolved against the client's ``context_url`` to determine the final
   URL of each of the dataset's service endpoints. Requests made to these URLs will use the client's ``session``.

   Each dataset has associated with it a number of services which can be used to access the dataset's data. This class
   exposes these services with a dictionary-like interface. As an added convenience, service lookup is case-insensitive,
   allows using some common aliases, and also supports attribute-style lookup. For example, given a ``Dataset`` object
   ``my_dataset``, the following are all valid ways of obtaining its NetCDF subset service.

   ::

     my_dataset['NetCDFSubset'] # Dictionary-style lookup
     my_dataset['netcdfsubset'] # Dictionary-style lookup, case-insensitve
     my_dataset['ncss']         # Dictionary-style lookup, with "ncss" alias
     my_dataset.ncss            # Attribute-style lookup, with "ncss" alias

   All the services available for the dataset may be enumerated by enumerating over the dataset itself:

   ::

     for service in my_dataset.values():
       print('{}: {}'.format(service.service_type, service.name))

   Accessing services using dictionary-style always uses a "lazy" lookup algorithm: if the service configuration has
   previously loaded from the Thredds server, it won't bother reloading it. If the configuration does need to be loaded,
   the globally-configured catalog search algorithm is used (see Global Configuration for more information). If
   necessary, the :func:`get_service` method can be used to override these
   behaviours while obtaining a service.

   .. rubric:: Attributes

   .. attribute:: url

      The dataset's URL (see the ``url`` parameter of the class constructor), as a **read-only** property.

   .. attribute:: client
      
      A Client instance to be used to interact with the TDS dataset. When accessing services, this dataset's URL is
      resolved relative to the client URL, and the client's ``session`` is used when making HTTP requests.

   .. attribute:: id

      The dataset's ID. Equivalent to passing ``False`` to :func:`get_id`.

   .. attribute:: name

      The dataset's name. Equivalent to passing ``False`` to :func:`get_name`.

   .. attribute:: catalog

      The :class:`Catalog` that contains the dataset. Equivalent to passing ``False`` to :func:`get_catalog`.

   .. rubric:: Methods

   .. method:: get_id(force_reload=False)

      Get the dataset's "ID" property. The dataset's XML representation is loaded from the Thredds server if it hasn't
      been loaded previously, or if ``force_reload`` is set to ``True``.

   .. method:: get_name(force_reload=False)

      Get the dataset's "name" property. The dataset's XML representation is loaded from the Thredds server if it hasn't
      been loaded previously, or if ``force_reload`` is set to ``True``.

   .. method:: get_catalog(force_reload=False)

      Get the :class:`Catalog` containing the dataset. If the Catalog passed to the dataset's constructor represents an
      ancestor catalog in the Thredds server's catalog hierarchy (rather than the catalog actually containing the
      dataset), then the server's catalog hierarchy will be examined to find the actual catalog declaring the dataset.

      If ``force_reload`` is ``True``, the catalog will be loaded from the Thredds server even if it has been loaded
      previously.

   .. method:: get_service(service_key, quick_search=None, force_reload=False)

      Get a dataset service.

      This method will cause the service configuration to be loaded from the Thredds server if it hasn't been previously
      loaded, or if the ``force_reload`` parameter is set to ``True``. If the ``force_reload`` parameter is set to
      ``False`` (the default), then the configuration is only loaded if it hasn't been previously loaded.

      The choice of algorithm for loading the service configuration depends on the value of the ``quick_search``
      parameter. If set to ``False``, then the entire Thredds catalog hierarchy is searched for the catalog containing
      the dataset, starting from the catalog passed in the ``Dataset``'s constructor. This may require a large number of
      requests to the Thredds server (potentially taking a long time) if the server has a complex catalog hierarchy, but
      is guaranteed to find the correct service configuration.

      Setting ``quick_search`` to ``True`` will minimise the number of requests to the Thredds server by instead
      stopping as soon as a matching service configuration is found. Although this may reduce the number of queries by
      stopping earlier, it isn't guaranteed that the service configuration found will be the same as that actually
      intended for the dataset. There are two potential problems that may arise from using this option:

      - The service configuration discovered through this means may be incorrect, if the Thredds catalog contains
        references to external Thredds servers.
      - The check on whether the dataset has the corresponding service enabled may be skipped. If it turns out the
        service actually isn't enabled for the given dataset, this may cause errors.

      If problems do occur, setting ``quick_search`` to ``False`` should resolve them.

      If ``quick_search`` is set to ``None`` (the default), then the global ``quick_search`` configuration option is
      used.