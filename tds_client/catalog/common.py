
from tds_client.util import abc, xml


class CatalogEntity(abc.ABC):
    @abc.abstractmethod
    def as_xml_tree(self, force_reload=False):
        pass

    def _get_attribute(self, attr, force_reload=False, namespace=xml.CATALOG, default=None):
        return xml.get_attr(self.as_xml_tree(force_reload), attr, namespace, default)