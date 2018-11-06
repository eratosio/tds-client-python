
class Dataset(object):
    def __init__(self, catalog, url):
        self._reference_catalog = catalog
        self._url = url
        
        self._catalog = None
        self._services = {}
    
    def get_catalog(self, force=False):
        self._reference_catalog._resolve_dataset(self, force)
        return self._catalog
    
    def get_service(self, service_id, force=True):
        if not force and service_id in self._services:
            return self._services[service_id]
    
        catalog = self.get_catalog(reload_catalog)
        
        # Locate service from catalog.
        
        # If service located and compatible service class available, instantiate
        # it.
    
    @property
    def url(self):
        return self._url
    
    @property
    def catalog(self):
        return self.get_catalog()
