
import services, urls
import os, requests, shutil, tempfile, types

from pydap.client import open_url
from pydap.handlers.netcdf import NetCDFHandler

# List of all the keyword arguments supported by the get_subset() client method.
_SUPPORTED_SUBSET_PARAMS = {
    # Parameters named in the NCSS documentation.
    'var', 'latitude', 'longitude', 'north', 'east', 'south', 'west', 'minx',
    'miny', 'maxx', 'maxy', 'horizStride', 'addLatLon', 'time', 'time_start',
    'time_end', 'time_duration', 'temporal', 'timeStride', 'vertCoord',
    'subset', 'stns',
    # Some more Pythonic aliases.
    'vars', 'lat', 'lon', 'n', 's', 'e', 'w', 'min_x', 'miny', 'max_x', 'max_y',
    'horiz_stride', 'add_lat_lon', 'time_stride', 'vert_coord'
    # TODO: compound arguments (e.g. bbox, point, etc)
}

# Define mapping from get_subset() alias arguments to the equivalent NCSS
# parameter name.
_SUBSET_PARAM_ALIASES = {
    'vars': 'var',
    'lat': 'latitude',
    'lon': 'longitude',
    'n': 'north',
    'e': 'east',
    's': 'south',
    'w': 'west',
    'min_x': 'minx',
    'min_y': 'miny',
    'max_x': 'maxx',
    'max_y': 'maxy',
    'horiz_stride': 'horizStride',
    'add_lat_lon': 'addLatLon',
    'time_stride': 'timeStride',
    'vert_coord': 'vertCoord'
}

def _safe_rm(path):
    try:
        os.remove(path)
    except IOError as e:
        pass # TODO: check errno.

def _check_dependent_params(params, param_set):
    present = param_set.intersection(params.keys())
    absent = param_set - present
    if present and absent:
        raise ValueError('If one of {} is provided, all must be.'.format(', '.join(param_set)))

def _check_exclusive_params(params, param_set_1, param_set_2):
    if param_set_1.intersection(params.keys()) and param_set_2.intersection(params.keys()):
        raise ValueError('The parameter sets {} and {} are mutually exclusive.'.format(', '.join(param_set_1), ', '.join(param_set_2)))

class Dataset(object):
    pass

class Client(object):
    def __init__(self, url, session=None):
        self.session = session or requests.Session()
        
        # Examine supplied URL to determine TDS application's context path. If
        # the given URL points to the catalog, use the portion before catalog
        # file name. Otherwise, use the complete URL path.
        parts = urls.urlparse(url)
        context_path = parts.path
        head, tail = urls.path.split(context_path)
        if tail.lower() == 'catalog.xml':
            context_path = head
        
        # The catalog path is always 'catalog.xml' appended to the context path.
        catalog_path = urls.path.join(context_path, 'catalog.xml')
        
        self._context_url = urls.override(url, path=context_path)
        self._catalog_url = urls.override(url, path=catalog_path)
    
    def get_dataset(self, url):
        url = services.OPENDAP.resolve_url(self._context_url, url)
        
        # Obtain dataset and monkey-patch to add a dummy delete() method (for
        # consistency).
        dataset = open_url(url, session=self.session)
        dataset.delete = types.MethodType(lambda instance: None, dataset)
        
        return dataset
    
    def get_subset(self, url, **kwargs):
        url = services.NETCDF_SUBSET_SERVICE.resolve_url(self._context_url, url)
        
        # Ignore parameters set to None.
        params = { k:v for k,v in kwargs.iteritems() if v is not None }
        
        # Check for unknown parameters.
        unknown_args = set(params.keys()) - _SUPPORTED_SUBSET_PARAMS
        if unknown_args:
            raise TypeError('Unsupported keyword argument(s): {}'.format(', '.join(unknown_args)))
        
        # TODO: Check for duplicate parameter definitions due to aliasing.
        
        # Resolve aliases.
        params = { _SUBSET_PARAM_ALIASES.get(k, k): v for k,v in params.iteritems() }
        
        # Check for required parameters.
        missing_required = set(['var']).difference(params.keys())
        if missing_required:
            raise ValueError('Missing required parameter(s): {}'.format(', '.join(missing_required)))
        
        # Check for mutually dependent parameters.
        _check_dependent_params(params, { 'latitude', 'longitude' })
        _check_dependent_params(params, { 'north', 'east', 'south', 'west' })
        
        # Check for mutually exclusive parameters.
        _check_exclusive_params(params, { 'latitude', 'longitude' }, { 'north', 'east', 'south', 'west' })
        
        # Download the subsetted data from the NCSS.
        params['accept'] = 'netCDF'
        response = self.session.get(url, params=params, stream=True)
        response.raise_for_status()
        fd, path = tempfile.mkstemp(prefix='ncss_', suffix='.nc')
        with os.fdopen(fd, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        
        # Create dataset and monkey-patch to add a delete() method.
        dataset = NetCDFHandler(path).dataset
        dataset.delete = types.MethodType(lambda instance: _safe_rm(path), dataset)
        
        return dataset
    
    @property
    def context_url(self):
        return self._context_url
    
    @property
    def catalog_url(self):
        return self._catalog_url
