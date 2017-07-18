

try:
    from urlparse import urlparse, urlunparse, parse_qsl
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

import posixpath



def _merge_values(value0, value1):
    if value0 and value1 and value0 != value1:
        raise ValueError() # TODO: more useful error
    return value0 or value1

def resolve_path(base_url, path):
    parts = list(urlparse(base_url))
    parts[2] = posixpath.join(parts[2], path) # parts[2] is URL path
    return urlunparse(parts)

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
    
    # Compute new "netloc".
    netloc = ''
    if username:
        netloc += username
        if password:
            netloc += ':' + password
        netloc += '@'
    netloc += hostname
    if port and port > 0:
        netloc += ':' + str(port)
    
    return urlunparse((scheme, netloc, path, params, query, fragment))
    
    
    
