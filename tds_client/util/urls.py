
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

def classify_url(url):
    parts = urlparse(url)
    
    if parts.scheme and parts.netloc:
        return ABSOLUTE_URL
    elif parts.path and parts.path[0] == path.sep:
        return ABSOLUTE_PATH
    else:
        return RELATIVE_PATH

def _merge_values(value0, value1):
    if value0 and value1 and value0 != value1:
        raise ValueError() # TODO: more useful error
    return value0 or value1

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
    parts[2] = posixpath.join(parts[2], *args) # parts[2] is URL path
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

def merge(url0, url1):
    parts0 = urlparse(url0)
    parts1 = urlparse(url1)
    
    # Merge various parts of the URLs.
    scheme = _merge_values(parts0.scheme, parts1.scheme)
    username = _merge_values(parts0.username, parts1.username)
    password = _merge_values(parts0.password, parts1.password)
    hostname = _merge_values(parts0.hostname, parts1.hostname)
    port = _merge_values(parts0.port, parts1.port)
    path = posixpath.join(parts0.path, parts1.path)
    params = parts0.params or parts1.params
    query = urlencode(parse_qsl(parts0.query, True) + parse_qsl(parts1.query, True))
    fragment = parts0.fragment or parts1.fragment
    
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
