
from tds_client import namespaces
from tds_client.util import urls

from xml.etree import cElementTree as ElementTree

CATALOG_REF_TAG = '{' + namespaces.CATALOG + '}catalogRef'
DATASET_TAG = '{' + namespaces.CATALOG + '}dataset'
XLINK_HREF_ATTR = '{' + namespaces.XLINK + '}href'

class Catalog(object):
    def __init__(self, url, client):
        self._url = url
        self._client = client
        
        self._xml = None
    
    def __str__(self):
        return 'Catalog(url="{}", name="{}")'.format(self.url, self.name)
    
    def iter_datasets(self, force=False):
        pass
    
    def iter_catalogs(self, force=False):
        pass
    
    def get_name(self, force=False):
        return self._get_xml(force).attrib.get('name')
    
    def get_version(self, force=False):
        return self._get_xml(force).attrib.get('version')
    
    @property
    def url(self):
        return self._url
    
    @property
    def name(self):
        return self.get_name()
    
    @property
    def version(self):
        return self.get_version()
    
    def _resolve_dataset(self, dataset, force=False):
        self._get_xml(force)
        
        # Try to find the dataset in this catalog.
        dataset_xml = Catalog._find_dataset_xml(self._xml, dataset.url)
        if dataset_xml is not None:
            dataset._catalog = self
            # TODO: update other properties
            return True
        
        # Otherwise, recurse into child catalogs.
        for catalog_ref_xml in self._xml.iterfind(CATALOG_REF_TAG):
            catalog_url = catalog_ref_xml.attrib.get(XLINK_HREF_ATTR)
            if catalog_url is not None:
                catalog = Catalog(urls.resolve_path(self.url, catalog_url), self._client)
                
                if catalog._resolve_dataset(dataset, force):
                    return True
        
        return False
    
    def _get_xml(self, force=False):
        if (self._xml is None) or force:
            response = self._client.session.get(self._url)
            response.raise_for_status()
            
            self._xml = ElementTree.fromstring(response.content)
        
        return self._xml
    
    @staticmethod
    def _find_dataset_xml(xml, url_path):
        # First try to find the dataset as a direct child of the given element.
        matches = xml.findall(DATASET_TAG + "[@urlPath='" + url_path + "']")
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            raise ValueError('Illegal catalog: duplicate datasets detected.')
        
        # Failing that, recurse into all child datasets (in case the target
        # dataset is nested).
        for dataset in xml.iterfind(DATASET_TAG):
            dataset_xml = Catalog._find_dataset_xml(dataset, url_path)
            if dataset_xml is not None:
                return dataset_xml
