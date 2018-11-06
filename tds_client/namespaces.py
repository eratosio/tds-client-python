
CATALOG = 'http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0'
XLINK = 'http://www.w3.org/1999/xlink'

def namespaced_name(name, namespace):
    return '{' + namespace + '}' + name

def get_attr(xml, attr, namespace, default=None):
    try:
        return xml.attrib[namespaced_name(attr, namespace)]
    except KeyError:
        return xml.attrib.get(attr, default)
