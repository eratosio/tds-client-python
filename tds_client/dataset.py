
from __future__ import print_function

from tds_client.catalog import CatalogEntity
from tds_client.service import get_service_classes

import warnings

class DatasetUrlWarning(UserWarning):
    pass

class Dataset(CatalogEntity):
    def __init__(self, catalog, url):
        if url.lower().endswith('.html'):
            warnings.warn('The provided dataset URL {} ends with ".html". This is almost certainly not intended.'.format(url), DatasetUrlWarning)

        self._reference_catalog = catalog
        self._url = url

        self._catalog = None
        self._parent = None
        self._xml = None

        self._service_ids = set()

    def __getattr__(self, attr):
        try:
            return self.services[attr]
        except KeyError:
            raise AttributeError()

    def __str__(self):
        return 'Dataset(id="{}", name="{}")'.format(self.id, self.name)

    def get_id(self, force_reload=False):
        return self._get_attribute('ID', force_reload)

    def get_name(self, force_reload=False):
        return self._get_attribute('name', force_reload)

    def get_restrict_access(self, force_reload=False):
        return self._get_attribute('restrictAccess', force_reload)

    def get_catalog(self, force_reload=False):
        if not self._reference_catalog._resolve_dataset(self, force_reload):
            raise ValueError('Unable to find dataset "{}" in catalog hierarchy at {}.'.format(self.url, self._reference_catalog.url))
        return self._catalog

    def get_services(self, force_reload=False):
        catalog = self.get_catalog(force_reload)
        service_bases = catalog._resolve_services(self._service_ids)
        print(service_bases, self.url)

        services = {}
        for service_type, service_class in get_service_classes(force_reload).items():
            try:
                service_base = service_bases[service_type.lower()]

                services[service_type] = service_instance = service_class(self, service_base)
                for alias in getattr(service_class, 'aliases', []):
                    services[alias] = service_instance
            except KeyError:
                pass

        return services

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
    def restrict_access(self):
        return self.get_restrict_access()

    @property
    def catalog(self):
        return self.get_catalog()

    @property
    def services(self):
        return self.get_services()

    def _get_xml(self, force_reload):
        self._reference_catalog._resolve_dataset(self, force_reload)
        return self._xml
