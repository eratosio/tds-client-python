
from .util import urls
from .client import Client
from . import service

import warnings

class Dataset(object):
    def __init__(self, client, url):
        self.client = client
        self._url = url
        
        self.services = { k:v(self) for k,v in service.get_service_classes().iteritems() }
    
    def __getattr__(self, attr):
        try:
            return self.services[attr]
        except KeyError:
            raise AttributeError()
    
    @staticmethod
    def from_url(dataset_url, context_url=None, session=None, client=None):
        # Log a warning if the context URL and/or session are supplied as well
        # as the client (as the client will override them).
        if client is not None and context_url is not None:
            warnings.warn('Context URL passed to `Dataset.from_url()` will be overriden by passed client.')
        if client is not None and session is not None:
            warnings.warn('Session passed to `Dataset.from_url()` will be overriden by passed client.')
        
        # The dataset URL must, at a minimum, have a path component.
        dataset_parts = urls.urlparse(dataset_url)
        if not dataset_parts.path:
            raise ValueError('Dataset URL "{}" does not contain a path component.'.format(dataset_url))
        
        # If client given, use its context URL.
        if client is not None:
            context_url = client.context_url
        # Otherise, ensure that the context URL, if given, doesn't point at the
        # catalog.
        elif context_url:
            context_parts = urls.urlparse(context_url)
            head, tail = urls.path.split(context_parts.path)
            if tail == 'catalog.xml':
                context_url = urls.override(context_url, path=head)
            
        # If the dataset URL is fully qualified, split it into its parts.
        if all(map(bool, dataset_parts[0:2])):
            dataset_context, service_path, dataset_path = service.split_service_url(dataset_url)
            
            # If no context URL specified, use the dataset's context URL.
            if not context_url:
                context_url = dataset_context
            # Otherwise, the dataset context URL must match the context URL.
            elif not urls.same_resource(context_url, dataset_context):
                raise ValueError('Dataset URL "{}" names different server to context URL "{}".'.format(dataset_url, context_url))
        # Otherwise the dataset path is just the supplied dataset URL without
        # any scheme or netloc that is present.
        else:
            dataset_path = urls.urlunparse(('', '') + dataset_parts[2:])
        
        if client is None:
            client = Client(context_url, session)
        
        return Dataset(client, dataset_path)
    
    @property
    def url(self):
        return self._url
