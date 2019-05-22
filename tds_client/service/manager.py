
from pkg_resources import iter_entry_points
from collections.abc import Mapping

from tds_client.service.ncss import NetCDFSubsetService
from tds_client.service.opendap import OPeNDAPService


class ServiceManager(Mapping):
    def __init__(self):
        self._service_classes = set()
        self._service_lookup = {}

    def __getitem__(self, key):
        return self._service_lookup[key]

    def __iter__(self):
        return iter(self._service_lookup)

    def __len__(self):
        return len(self._service_lookup)

    def register_class(self, cls):
        self._service_classes.add(cls)

        self._service_lookup[cls.service_type] = cls
        for alias in getattr(cls, 'aliases', []):
            self._service_lookup[alias] = cls

    def load_plugins(self):
        for entry_point in iter_entry_points(group='tds_client.service'):
            self.register_service_class(entry_point.load())

    @property
    def classes(self):
        return self._service_classes


SERVICE_CLASSES = ServiceManager()
SERVICE_CLASSES.register_class(NetCDFSubsetService)
SERVICE_CLASSES.register_class(OPeNDAPService)