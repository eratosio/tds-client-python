
import urls

class Service(object):
    def __init__(self, name, description, url_path):
        self._name = name
        self._description = description
        self._url_path = url_path
    
    def resolve_url(self, base_url, dataset_url):
        # If no base URL given, assume dataset URL is fully qualified.
        if base_url is None:
            return dataset_url
        
        # Otherwise, merge service URL and dataset path.
        service_url = urls.resolve_path(base_url, self._url_path)
        return urls.merge(service_url, dataset_url)
            
    @property
    def name(self):
        return self._name
    
    @property
    def description(self):
        return self._description
    
    @property
    def url_path(self):
        return self._url_path
            
            
            

NETCDF_SUBSET_SERVICE = Service(
    'NetCDF Subset Service',
    '',
    'ncss'
)

OPENDAP = Service(
    'OPeNDAP',
    '',
    'dodsC'
)

WEB_COVERAGE_SERVICE = Service(
    'Web Coverage Service',
    '',
    'wcs'
)

WEB_MAP_SERVICE = Service(
    'Web Map Service',
    '',
    'wms'
)


HTTP_FILE_DOWNLOAD = Service(
    'HTTP File Download',
    '',
    'fileServer'
)
