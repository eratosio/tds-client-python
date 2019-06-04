
from tds_client.util import xml
from abc import ABCMeta, abstractmethod

ABC = ABCMeta('ABC', (object,), {'__slots__': ()})  # compatible with Python 2 *and* 3


class CatalogEntity(ABC):
    @abstractmethod
    def as_xml_tree(self, force_reload=False):
        pass

    def _get_attribute(self, attr, force_reload=False, namespace=xml.CATALOG, default=None):
        return xml.get_attr(self.as_xml_tree(force_reload), attr, namespace, default)