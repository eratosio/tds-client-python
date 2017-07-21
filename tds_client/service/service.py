
from ..util import urls
from pkg_resources import iter_entry_points
import re

_path_split_pattern = re.compile(r'^{0}|[^{0}]+{0}|[^{0}]+$'.format(urls.path.sep))

_service_classes = None

def get_service_classes(refresh=False):
    global _service_classes # TODO: refactor
    if _service_classes is None or refresh:
        _service_classes = { e.name:e.load() for e in iter_entry_points(group='tds_client.service') }
    return _service_classes

def split_service_url(url):
    result = []
    for service_class in get_service_classes().itervalues():
        try:
            result.append((service_class.name, service_class.split_url(url)))
        except (NotImplementedError, ValueError):
            pass
    
    if not result:
        raise ValueError('Service URL "{}" does not correspond to a known service.'.format(url))
    elif len(result) > 1:
        services = ', '.join(name for name,_ in result)
        raise ValueError('Service URL "{}" matches multiple services: {}'.format(url, services))
    
    _, urls = result[0]
    return urls

class Service(object):
    def __init__(self, dataset):
        self._dataset = dataset
    
    @classmethod
    def split_url(cls, url):
        raise NotImplementedError()
    
    @property
    def client(self):
        return self._dataset.client
    
    @property
    def _session(self):
        return self.client.session
    
    def _resolve_url(self, service_path):
        # Ensure service path has a trailing path separator but no leading one.
        service_path = urls.path.join(service_path.strip(urls.path.sep), '')
        
        # Combine dataset's context URL, the service path, and the dataset path.
        context_parts = urls.urlparse(self.client.context_url)
        dataset_parts = urls.urlparse(self._dataset.url)
        final_path = urls.path.join(context_parts.path, service_path, dataset_parts.path.lstrip(urls.path.sep))
        
        # Return final URL, consisting of the context's scheme and netloc, the
        # combined path from the previous step, and the dataset URL's params,
        # query and fragment.
        # TODO: should it be possible to keep context query params too?
        return urls.urlunparse((context_parts.scheme, context_parts.netloc, final_path, dataset_parts.params, dataset_parts.query, dataset_parts.fragment))
        
class StandardService(Service):
    @classmethod
    def split_url(cls, url):
        # Given URL must be fully qualified and have a path.
        url_parts = urls.urlparse(url)
        if not all(map(bool, url_parts[0:3])):
            raise ValueError('Cannot split partially-qualified service URL "{}".'.format(url)) # TODO: more descriptive.
        
        # The URL path must contain the service path as a non-leaf element.
        service_path = urls.path.join(cls.path.strip(urls.path.sep), '')
        path_parts = _path_split_pattern.findall(url_parts.path)
        try:
            service_index = path_parts.index(service_path)
        except ValueError:
            raise ValueError('Service URL "{}" does not contain service path "{}".'.format(url, cls.path))
        
        # The "context" path is the portion of the path preceeding the service
        # path, and the dataset path is the portion following it.
        context_path = urls.path.join(*path_parts[0:service_index]) if service_index > 0 else ''
        dataset_path = urls.path.join(*path_parts[service_index+1:])
        
        # The "context URL" is the context path concatenated to the original
        # URL's scheme and netloc.
        context_url = urls.urlunparse(url_parts[0:2] + (context_path, '', '', ''))
        
        # The "dataset URL" is the dataset path and any params, query and/or
        # fragment from the original URL.
        dataset_url = urls.urlunparse(('', '', dataset_path) + url_parts[3:6])
        
        return context_url, cls.path, dataset_url
    
    @property
    def url(self):
        return self._resolve_url(self.path)
