from tds_client.catalog.common import CatalogEntity
from tds_client.dataset import Dataset
from tds_client.util import urls, xml

try:
    from xml.etree import cElementTree as ElementTree  # older python versions
except ImportError:
    from xml.etree import ElementTree
from requests.structures import CaseInsensitiveDict

# Rules to apply when merging URLs resulting from redirects.
_REDIRECT_MERGE_RULES = {
    "scheme": urls.MERGE,
    "username": urls.MERGE,
    "password": urls.MERGE,
    "hostname": urls.MERGE,
    "port": urls.MERGE,
    "path": urls.OVERWRITE,
    "params": urls.KEEP,
    "query": urls.KEEP,
    "fragment": urls.MERGE,
}


class ServiceSpec(object):
    def __init__(self, name, type_, url_base, children):
        self._name = name
        self._type = type_
        self._url_base = url_base
        self._children = children

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def url_base(self):
        return self._url_base

    @property
    def children(self):
        return self._children

    @staticmethod
    def services_from_xml(root_element, base_url, namespace):
        result = CaseInsensitiveDict()

        for service_element in root_element.iterfind(
            xml.namespaced_name("service", namespace)
        ):
            name = xml.get_attr(service_element, "name", namespace)
            type_ = xml.get_attr(service_element, "serviceType", namespace)
            base = xml.get_attr(service_element, "base", namespace)

            if urls.classify_url(base) == urls.ABSOLUTE_URL:
                url = base_url = base
            else:
                url = urls.resolve_path(base_url, base)

            children = ServiceSpec.services_from_xml(
                service_element, base_url, namespace
            )

            result[name] = ServiceSpec(name, type_, url, CaseInsensitiveDict(children))
            result.update(children)

        return result


class Catalog(CatalogEntity):
    def __init__(self, url, client):
        self._url = url
        self._client = client

        self._xml = None

        self._child_catalogs = None
        self._services = None
        self._datasets = None

    def __str__(self):
        return 'Catalog(url="{}", name="{}")'.format(self.url, self.name)

    def get_name(self, force_reload=False):
        return self._get_attribute("name", force_reload)

    def get_version(self, force_reload=False):
        return self._get_attribute("version", force_reload)

    def get_child_catalogs(self, force_reload=False):
        if force_reload or not self._child_catalogs:  # (self._child_catalogs is None):
            self._child_catalogs = []

            for catalog_ref_xml in xml.search(
                self.as_xml_tree(force_reload), "catalogref", "dataset"
            ):
                catalog_url = xml.get_attr(catalog_ref_xml, "href", xml.XLINK)
                if catalog_url is not None:
                    self._child_catalogs.append(
                        Catalog(
                            urls.resolve_path(self.url, "..", catalog_url), self._client
                        )
                    )

        return self._child_catalogs

    def get_service(self, name, force_reload=False):
        return self._get_services(force_reload).get(name)

    def get_services(self, type_, force_reload=False):
        type_ = type_.lower()
        return [
            s
            for s in self._get_services(force_reload).values()
            if s.type.lower() == type_
        ]

    def get_datasets(self, force_reload=False):
        if force_reload or (self._datasets is None):
            self._datasets = {}

            for dataset_xml in xml.search(
                self.as_xml_tree(force_reload), "dataset", "dataset"
            ):
                url_path = xml.get_attr(dataset_xml, "urlPath", xml.CATALOG)
                if url_path:
                    self._datasets[url_path] = Dataset(self, url_path)

        return self._datasets

    def reload(self):
        self.as_xml_tree(True)

    def as_xml_tree(self, force_reload=False):
        if force_reload or (self._xml is None):
            response = self._client.session.get(self._url)
            response.raise_for_status()
            self._url = urls.merge(
                self._url, response.url, **_REDIRECT_MERGE_RULES
            )  # In case a redirect occurred
            self._xml = ElementTree.fromstring(response.content)

        return self._xml

    @property
    def client(self):
        return self._client

    @property
    def url(self):
        return self._url

    @property
    def name(self):
        return self.get_name()

    @property
    def version(self):
        return self.get_version()

    @property
    def child_catalogs(self):
        return self.get_child_catalogs()

    @property
    def datasets(self):
        return self.get_datasets()

    def _get_services(self, force_reload):
        if force_reload or (self._services is None):
            catalog_xml = self.as_xml_tree(force_reload)
            namespace, _ = xml.split_namespace(catalog_xml.tag, xml.CATALOG)
            self._services = ServiceSpec.services_from_xml(
                catalog_xml, self.url, namespace
            )

        return self._services
