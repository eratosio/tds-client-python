
from __future__ import print_function

from tds_client.catalog.common import CatalogEntity
from tds_client.service import SERVICE_CLASSES
from tds_client.catalog.search import DatasetSearch, ServiceSearch
from tds_client import settings
from tds_client.util import xml, strings

import warnings
from collections.abc import Mapping


class DatasetUrlWarning(UserWarning):
    pass


class QuickSearchWarning(UserWarning):
    pass


class Dataset(CatalogEntity, Mapping):
    def __init__(self, catalog, url):
        if url.lower().endswith('.html'):
            warnings.warn('The provided dataset URL {} ends with ".html". This is almost certainly not intended.'.format(url), DatasetUrlWarning)

        self._reference_catalog = catalog
        self._url = url

        self._catalog = None
        self._parent = None
        self._xml = None

        self._service_ids = set()
        self._service_lookup = {}

    def __getattr__(self, key):
        return self[key]

    def __getitem__(self, key):
        return self.get_service(key)

    def __iter__(self):
        return iter(self.service_ids)

    def __len__(self):
        return len(self.service_ids)

    def __str__(self):
        return 'Dataset(id="{}", name="{}", service_ids={})'.format(self.id, self.name, self.service_ids)

    def get_id(self, force_reload=False):
        return self._get_attribute('ID', force_reload)

    def get_name(self, force_reload=False):
        return self._get_attribute('name', force_reload)

    def get_catalog(self, force_reload=False):
        self._catalog = self._find_catalog(force_reload, DatasetSearch(self.url))
        if self._catalog is None:
            raise RuntimeError('Unable to find dataset "{}" in catalog hierarchy at {}.'.format(self.url, self._reference_catalog.url))

        return self._catalog

    def get_service(self, service_key, quick_search=None, force_reload=False):
        key = strings.normalise(service_key)

        service = self._service_lookup.get(key)
        if not force_reload and service is not None:
            return service

        try:
            service_class = SERVICE_CLASSES[service_key]
        except KeyError:
            raise ValueError('Unsupported service "{}"'.format(service_key))

        if quick_search is None:
            quick_search = settings.quick_search

        search = ServiceSearch(service_class.service_type, self.url) if quick_search else DatasetSearch(self.url)
        catalog = self._find_catalog(False, search) # TODO: properly set the force_reload parameter

        if catalog is None:
            raise RuntimeError('Unable to find definition of {} service in catalog hierarchy at {}.'.format(service_key, self._reference_catalog.url))

        service_specs = catalog.get_services(service_class.service_type)
        if not service_specs:
            raise RuntimeError('Service lookup for {} resolved to catalog at {}, but was unable to find the service in the catalog.'.format(service_key, catalog.url))
        elif len(service_specs) > 1:
            raise RuntimeError('Service lookup for {} found multiple matching services in the catalog at {}.'.format(service_key, catalog.url))

        if self.url not in catalog.get_datasets(False): # TODO: properly set the force_reload parameter
            warnings.warn('Found {} service for dataset {} using quick-search algorithm: this may not work correctly. If problems occur, change the "quick_search" parameter to False.'.format(service_key, self.url), QuickSearchWarning)

        # TODO: if the resolved catalog contains the dataset, confirm that the requested service is enabled for the dataset.

        service = self._service_lookup[key] = service_class(self, service_specs[0].url_base)
        self._service_ids.add(service_key)
        for alias in getattr(service_class, 'aliases', []):
            self._service_lookup[strings.normalise(alias)] = service

        return service

    def as_xml_tree(self, force_reload):
        if force_reload or self._xml is None:
            catalog = self.get_catalog(force_reload)
            catalog_xml = catalog.as_xml_tree(False)
            namespace, _ = xml.split_namespace(catalog_xml.tag, xml.CATALOG)

            for dataset_xml in xml.search(catalog_xml, 'dataset', 'dataset'):
                url_path = xml.get_attr(dataset_xml, 'urlPath', namespace)
                if url_path == self.url:
                    self._xml = dataset_xml
                    break

            if self._xml is None:
                raise RuntimeError('Resolved catalog {} for dataset {}, but was unable to find the dataset in that catalog.'.format(catalog.url, self.url))

        return self._xml

    def _find_catalog(self, force_reload, search):
        return search.search(self._reference_catalog) if force_reload or (self._catalog is None) else self._catalog

    @property
    def url(self):
        return self._url if self._xml is None else self._xml.attrib.get('urlPath', self._url)

    @property
    def client(self):
        return self._reference_catalog.client

    @property
    def id(self):
        return self.get_id()

    @property
    def name(self):
        return self.get_name()

    @property
    def catalog(self):
        return self.get_catalog()

    @property
    def service_ids(self):
        for service_type in SERVICE_CLASSES.keys():
            self.get_service(service_type, force_reload=False)

        return self._service_ids
