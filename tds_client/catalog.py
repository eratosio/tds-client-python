
from tds_client import namespaces
from tds_client.util import urls

from xml.etree import cElementTree as ElementTree

import re

METADATA_TAG = '{' + namespaces.CATALOG + '}metadata'
SERVICE_TAG = '{' + namespaces.CATALOG + '}service'
SERVICE_NAME_TAG = '{' + namespaces.CATALOG + '}serviceName'
XLINK_HREF_ATTR = '{' + namespaces.XLINK + '}href'

_NAMESPACE_PATTERN = re.compile(r'^\s*(?:{([^}]+)})?(\w+)\s*$')

class CatalogEntity(object):
    def _get_attribute(self, attr, force_reload=False, namespace=namespaces.CATALOG, default=None):
        return namespaces.get_attr(self._get_xml(force_reload), attr, namespace, default)

def _resolve_services(xml, service_ids, base_url, include_all=False):
    services = {}
    
    for service_xml in xml.iterfind(SERVICE_TAG):
        name = namespaces.get_attr(service_xml, 'name', namespaces.CATALOG)
        type_ = namespaces.get_attr(service_xml, 'serviceType', namespaces.CATALOG).lower()
        base = namespaces.get_attr(service_xml, 'base', namespaces.CATALOG)
        
        # TODO: update following to properly conform to https://www.unidata.ucar.edu/software/thredds/v4.6/tds/catalog/InvCatalogSpec.html#constructingURLs
        service_url = base if urls.classify_url(base) == urls.ABSOLUTE_URL else urls.resolve_path(base_url, base)
        
        match = name in service_ids
        if type_ == 'compound':
            services.update(_resolve_services(service_xml, service_ids, service_url, include_all or match))
        elif match or include_all:
            services[type_] = service_url
    
    return services

class Catalog(CatalogEntity):
    def __init__(self, url, client):
        self._url = url
        self._client = client
        
        self._xml = None
    
    def __str__(self):
        return 'Catalog(url="{}", name="{}")'.format(self.url, self.name)
    
    def iter_datasets(self, force_reload=False):
        pass # TODO
    
    def iter_catalogs(self, force_reload=False):
        pass # TODO
    
    def get_name(self, force_reload=False):
        return self._get_attribute('name', force_reload)
    
    def get_version(self, force_reload=False):
        return self._get_attribute('version', force_reload)
    
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
    
    def _resolve_dataset(self, dataset, force_reload=False):
        self._get_xml(force_reload)
        return self._find_and_update_dataset(dataset, self._xml, force_reload, [])
    
    def _resolve_services(self, service_ids):
        return _resolve_services(self._get_xml(), service_ids, self.url)
    
    def _get_xml(self, force_reload=False):
        if (self._xml is None) or force_reload:
            response = self._client.session.get(self._url)
            response.raise_for_status()
            
            self._url = response.url # In case a redirect occurs
            self._xml = ElementTree.fromstring(response.content)
        
        return self._xml
    
    def _find_and_update_dataset(self, dataset, xml, force_reload, ancestors):
        # TODO: is there a smart way to prioritise which datasets and/or catalog
        # refs to recurse into, to minimise requests to the TDS?
        
        # First try to find the dataset as a direct child of the given element.
        dataset_url = dataset.url.lstrip(urls.path.sep)
        filter = lambda tag: tag.attrib.get('urlPath', '').lstrip(urls.path.sep) == dataset_url
        matches = list(Catalog._iter_children(xml, 'dataset', filter))
        if len(matches) == 1:
            self._update_dataset(dataset, matches[0], ancestors)
            return True
        elif len(matches) > 1:
            raise ValueError('Illegal catalog: duplicate datasets detected.')
        
        # Failing that, recurse into ALL child datasets (in case the target
        # dataset is nested).
        for child_dataset_xml in Catalog._iter_children(xml, 'dataset'):
            if self._find_and_update_dataset(dataset, child_dataset_xml, force_reload, ancestors + [child_dataset_xml]):
                return True
        
        # If that still hasn't found the dataset, try recursing into any catalog
        # refs.
        for catalog_ref_xml in Catalog._iter_children(xml, 'catalogRef'):
            catalog_url = catalog_ref_xml.attrib.get(XLINK_HREF_ATTR)
            if catalog_url is not None:
                catalog = Catalog(urls.resolve_path(self.url, '../', catalog_url), self._client)
                
                if catalog._resolve_dataset(dataset, force_reload):
                    return True
        
        return False
    
    def _update_dataset(self, dataset, dataset_xml, ancestors_xml):
        dataset._catalog = self
        dataset._xml = dataset_xml
        
        # Determine service names from metadata.
        dataset._service_ids = service_names = set()
        for ancestor_xml in ancestors_xml:
            for service_name_xml in ancestor_xml.iterfind(METADATA_TAG + "[@inherited='true']/" + SERVICE_NAME_TAG):
                service_names.add(''.join(service_name_xml.itertext()))
    
    @staticmethod
    def _iter_children(xml, target_tag, filter=lambda tag: True):
        namespace, _ = Catalog._split_namespace(xml.tag)
        # TODO: validate namespace against known TDS catalog namespace URIs?
        
        for child in xml:
            child_namespace, child_tag = Catalog._split_namespace(child.tag)
            if (child_namespace == namespace) and (child_tag == target_tag) and filter(child):
                yield child
    
    @staticmethod
    def _split_namespace(tag):
        m = _NAMESPACE_PATTERN.match(tag)
        if not m:
            raise ValueError('Invalid tag "{}" detected.'.format(tag))
        return m.groups()
