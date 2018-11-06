
from tds_client.util import urls
from pkg_resources import iter_entry_points
import re

_path_split_pattern = re.compile(r'^{0}|[^{0}]+{0}|[^{0}]+$'.format(urls.path.sep))

_service_classes = None

def get_service_classes(refresh=False):
    global _service_classes # TODO: refactor
    
    if _service_classes is None or refresh:
        _service_classes = { e.name:e.load() for e in iter_entry_points(group='tds_client.service') }
    
    return _service_classes

class Service(object):
    def __init__(self, dataset, base_url):
        self.__dataset = dataset
        self.__base_url = base_url
    
    @property
    def client(self):
        return self._dataset.client
    
    @property
    def _session(self):
        return self.client.session
    
    @property
    def _dataset(self):
        return self.__dataset
    
    @property
    def base_url(self):
        return self.__base_url

class StandardService(Service):
    @property
    def url(self):
        return urls.resolve_path(self.base_url, self._dataset.url)
