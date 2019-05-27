
from tds_client.util import urls


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

    @classmethod
    def get_all_aliases(cls):
        return frozenset([cls.service_type] + getattr(cls, 'aliases', []))


class StandardService(Service):
    @property
    def url(self):
        dataset_path = self._dataset.url.lstrip(urls.path.sep)  # strip leading separators - the path should ALWAYS be relative
        return urls.resolve_path(self.base_url, dataset_path)
