try:
    from collections.abc import Mapping  # python3
except ImportError:
    from collections import Mapping  # python2

from tds_client.service.httpserver import HttpServerService
from tds_client.service.ncss import NetCDFSubsetService
from tds_client.service.opendap import OPeNDAPService
from tds_client.util.strings import normalise


class ServiceManager(Mapping):
    def __init__(self):
        self._service_types = set()
        self._service_lookup = {}

    def __getitem__(self, key):
        return self._service_lookup[normalise(key)]

    def __iter__(self):
        return iter(self._service_types)

    def __len__(self):
        return len(self._service_types)

    def register_class(self, cls):
        self._service_types.add(cls.service_type)

        for alias in cls.get_all_aliases():
            self._service_lookup[normalise(alias)] = cls


SERVICE_CLASSES = ServiceManager()
SERVICE_CLASSES.register_class(HttpServerService)
SERVICE_CLASSES.register_class(NetCDFSubsetService)
SERVICE_CLASSES.register_class(OPeNDAPService)
