
from tds_client.util.strings import normalise

import re

CATALOG = 'http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0'
XLINK = 'http://www.w3.org/1999/xlink'

_NAMESPACE_PATTERN = re.compile(r'^\s*(?:{([^}]+)})?(\w+)\s*$')


def namespaced_name(name, namespace):
    return '{' + namespace + '}' + name


def get_attr(element, attr, namespace, default=None):
    try:
        return element.attrib[namespaced_name(attr, namespace)]
    except KeyError:
        return element.attrib.get(attr, default)


def split_namespace(tag_name, default_namespace=None):
    m = _NAMESPACE_PATTERN.match(tag_name)
    if not m:
        raise ValueError('Invalid tag "{}" detected.'.format(tag_name))

    namespace, tag = m.groups()
    return namespace or default_namespace, tag


def search(element, yield_tag, recurse_tag=None):
    yield_tag = normalise(yield_tag)
    recurse_tag = normalise(recurse_tag)

    namespace, _ = split_namespace(element.tag)

    for child_xml in element:
        child_namespace, child_tag = split_namespace(child_xml.tag)
        if child_namespace != namespace:
            continue

        child_tag = normalise(child_tag)
        if child_tag == yield_tag:
            yield child_xml

        if child_tag == recurse_tag:
            for descendant_xml in search(child_xml, yield_tag, recurse_tag):
                yield descendant_xml
