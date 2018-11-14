
from tds_client.util import urls
import requests

class Client(object):
    def __init__(self, url, session=None):
        self.session = session or requests.Session()
        
        # Given URL must be fully qualified (otherwise it's not useful for
        # anything).
        url_parts = urls.urlparse(url)
        if not all(map(bool, url_parts[0:2])):
            raise ValueError('Client URL "{}" is not fully qualified.'.format(url))
        
        # Determine context and catalog URLs from given context URL.
        head, tail = urls.path.split(url_parts.path)
        context_path = head if tail == 'catalog.xml' else url_parts.path
        self._context_url = urls.override(url, path=context_path)
        self._catalog_url = urls.override(url, path=urls.path.join(context_path, 'catalog.xml'))
    
    @property
    def context_url(self):
        return self._context_url
    
    @property
    def catalog_url(self):
        return self._catalog_url
