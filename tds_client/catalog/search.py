
from tds_client.util import abc, urls

from difflib import SequenceMatcher
from functools import partial


class CatalogSearch(abc.ABC):
    @abc.abstractmethod
    def search(self, catalog, force_reload=False):
        pass


class RecursiveSearch(CatalogSearch):
    def __init__(self, dataset_url):
        self.__dataset_url = dataset_url

    def search(self, catalog, force_reload=False):
        # If requested, reload the catalog.
        if force_reload:
            catalog.reload()

        # If the current catalog is a match, return it.
        if self.is_match(catalog):
            return catalog

        # Otherwise, recurse into the catalog's child catalogs.
        matcher = SequenceMatcher(None, '', self.__dataset_url)
        key = partial(RecursiveSearch._catalog_sort_order, matcher)
        for child_catalog in sorted(catalog.get_child_catalogs(False), key=key, reverse=True):
            child_result = self.search(child_catalog, force_reload)
            if child_result:
                return child_result

    @abc.abstractmethod
    def is_match(self, catalog):
        pass

    @staticmethod
    def _catalog_sort_order(matcher, catalog):
        matcher.set_seq1(urls.urlparse(catalog.url).path)
        return matcher.quick_ratio()


class DatasetSearch(RecursiveSearch):
    def __init__(self, dataset_url):
        super(DatasetSearch, self).__init__(dataset_url)

        self._dataset_url = dataset_url

    def is_match(self, catalog):
        return self._dataset_url in catalog.get_datasets(False)


class ServiceSearch(RecursiveSearch):
    def __init__(self, service_type, dataset_url):
        super(ServiceSearch, self).__init__(dataset_url)

        self._service_type = service_type

    def is_match(self, catalog):
        return len(catalog.get_services(self._service_type)) == 1


