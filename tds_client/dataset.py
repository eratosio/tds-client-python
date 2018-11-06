
from tds_client.catalog import CatalogEntity

class Dataset(CatalogEntity):
    def __init__(self, catalog, url):
        self._reference_catalog = catalog
        self._url = url
        
        self._catalog = None
        self._xml = None
        self._services = {}
    
    def __str__(self):
        print self._get_xml(False).attrib
        return 'Dataset(id="{}", name="{}")'.format(self.id, self.name)
    
    def get_id(self, force_reload=False):
        return self._get_attribute('ID', force_reload)
    
    def get_name(self, force_reload=False):
        return self._get_attribute('name', force_reload)
    
    def get_restrict_access(self, force_reload=False):
        return self._get_attribute('restrictAccess', force_reload)
    
    def get_catalog(self, force_reload=False):
        self._reference_catalog._resolve_dataset(self, force_reload)
        return self._catalog
    
    def get_service(self, service_id, force_reload=True):
        if not force_reload and service_id in self._services:
            return self._services[service_id]
    
        catalog = self.get_catalog(force_reload)
        
        # Locate service from catalog.
        
        # If service located and compatible service class available, instantiate
        # it.
    
    @property
    def url(self):
        return self._url
    
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
    
    def _get_xml(self, force_reload):
        self._reference_catalog._resolve_dataset(self, force_reload)
        return self._xml
