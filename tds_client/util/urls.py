
try:
    from urlparse import urlparse, urlunparse, parse_qsl
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

try:
    from types import StringTypes
except ImportError:
    StringTypes = (str,)

import posixpath

path = posixpath # useful alias for users of the module.

# Different URL types.
ABSOLUTE_URL = 'absolute_url'   # Fully resolvable URL (i.e. including scheme and netloc).
ABSOLUTE_PATH = 'absolute_path' # Non-resolvable URL with absolute path (i.e. path starts with a slash).
RELATIVE_PATH = 'relative_path' # Non-resolvable URL with relative path (i.e. path does not start with a slash).

# Rules for merging the various parts of two URLs.
KEEP = 'keep'           # Always keep the value from the first URL
DELETE = 'delete'       # Use a default value instead of a value from either URL
OVERWRITE = 'overwrite' # If the second URL has the given part, it overrides that of the first URL. Otherwise, the default value is used.
MERGE = 'merge'         # If only one or the other URL has the given part, it is used. If neither do, the default is used. If both do, a part-specific merge algorithm is used (in most cases, the second URL wins)

def classify_url(url):
    parts = urlparse(url)
    
    if parts.scheme and parts.netloc:
        return ABSOLUTE_URL
    elif parts.path and parts.path[0] == path.sep:
        return ABSOLUTE_PATH
    else:
        return RELATIVE_PATH

def _default_merger(value0, value1, default):
    return value1 or value0 or default

def _path_merger(path0, path1, default):
    return posixpath.normpath(posixpath.join(path0, path1))

def _query_merger(query0, query1, default):
    query = dict(parse_qsl(parts0.query, True))
    query.update(parse_qsl(parts1.query, True))
    return urlencode(query)

def _merge(value0, value1, rule, default, merger=_default_merger):
    if rule == KEEP:
        return value0
    elif rule == DELETE:
        return default
    elif rule == OVERWRITE:
        return value1 or default
    elif rule == MERGE:
        return merger(value0, value1, default)

def same_resource(url0, url1):
    # Scheme and netloc must match.
    parts0 = urlparse(url0)
    parts1 = urlparse(url1)
    if parts0[0:2] != parts1[0:2]:
        return False
    
    # Normalised paths must match.
    return posixpath.normpath(parts0.path) == posixpath.normpath(parts1.path)

def resolve_path(base_url, *args):
    parts = list(urlparse(base_url))
    parts[2] = posixpath.normpath(posixpath.join(parts[2], *args)) # parts[2] is URL path
    return urlunparse(parts)

def override(url, scheme=None, username=None, password=None, hostname=None, port=None, path=None, params=None, query=None, fragment=None):
    parts = urlparse(url)
    
    return _generate_url(
        scheme or parts.scheme,
        username or parts.username,
        password or parts.password,
        hostname or parts.hostname,
        port or parts.port,
        path or parts.path, 
        params or parts.params,
        query or parts.query,
        fragment or parts.fragment
    )

def merge(url0, url1, scheme=MERGE, username=MERGE, password=MERGE, hostname=MERGE, port=MERGE, path=MERGE, params=MERGE, query=MERGE, fragment=MERGE):
    parts0 = urlparse(url0)
    parts1 = urlparse(url1)
    
    # Merge various parts of the URLs.
    scheme = _merge(parts0.scheme, parts1.scheme, scheme, 'http')
    username = _merge(parts0.username, parts1.username, username, None)
    password = _merge(parts0.password, parts1.password, password, None)
    hostname = _merge(parts0.hostname, parts1.hostname, hostname, None)
    port = _merge(parts0.port, parts1.port, port, None)
    path = _merge(parts0.path, parts1.path, path, '', _path_merger)
    params = _merge(parts0.params, parts1.params, params, '')
    query = _merge(parts0.query, parts1.query, query, '', _query_merger)
    #query = urlencode(parse_qsl(parts0.query, True) + parse_qsl(parts1.query, True))
    fragment = _merge(parts0.fragment, parts1.fragment, fragment, '')
    
    return _generate_url(scheme, username, password, hostname, port, path, params, query, fragment)

def _generate_url(scheme=None, username=None, password=None, hostname=None, port=None, path=None, params=None, query=None, fragment=None):
    # Compute "netloc".
    netloc = ''
    if username:
        netloc += username
        if password:
            netloc += ':' + password
        netloc += '@'
    netloc += hostname
    if port and port > 0:
        netloc += ':' + str(port)
    
    # If query is not a string, convert it.
    if not isinstance(query, StringTypes):
        query = urlencode(query)
    
    return urlunparse((scheme, netloc, path, params, query, fragment))
