
CATALOG = 'http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0'
XLINK = 'http://www.w3.org/1999/xlink'

def namespaced_name(name, namespace):
    return '{' + namespace + '}' + name
