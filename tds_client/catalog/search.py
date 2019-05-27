
from tds_client.util import abc, urls

from difflib import SequenceMatcher
from functools import partial
from requests import HTTPError


class SearchStrategy(abc.ABC):
    def find_dataset(self, catalog, dataset_url):
        return self._search(catalog, self.catalog_has_dataset, dataset_url)

    def find_service(self, catalog, service_type, dataset_url):
        return self._search(catalog, self.catalog_has_service, dataset_url, service_type)

    # noinspection PyMethodMayBeStatic
    def get_next_candidates(self, catalog, dataset_url):
        matcher = SequenceMatcher(None, '', dataset_url)
        key = partial(SearchStrategy._catalog_sort_order, matcher)
        return [catalog] + sorted(catalog.get_child_catalogs(False), key=key, reverse=True)

    @abc.abstractmethod
    def catalog_has_dataset(self, catalog, dataset_url):
        pass

    @abc.abstractmethod
    def catalog_has_service(self, catalog, service_type, dataset_url):
        pass

    def _search(self, catalog, predicate, dataset_url, *args):
        for candidate in self.get_next_candidates(catalog, dataset_url):
            try:
                if predicate(candidate, *(args + (dataset_url,))):
                    return candidate

                if candidate.url != catalog.url:
                    result = self._search(candidate, predicate, dataset_url, *args)
                    if result is not None:
                        return result
            except HTTPError as e:
                pass  # TODO: handle exceptions more intelligently

    @staticmethod
    def _catalog_sort_order(matcher, catalog):
        matcher.set_seq1(urls.urlparse(catalog.url).path)
        return matcher.quick_ratio()


class QuickSearchStrategy(SearchStrategy):
    def catalog_has_dataset(self, catalog, dataset_url):
        return dataset_url in catalog.get_datasets(False)

    def catalog_has_service(self, catalog, service_type, dataset_url):
        # NOTE: the dataset URL is intentionally ignored, that's what makes this algorithm "quick".
        return len(catalog.get_services(service_type)) == 1


class ExhaustiveSearchStrategy(QuickSearchStrategy):
    def catalog_has_service(self, catalog, service_type, dataset_url):
        return super(ExhaustiveSearchStrategy, self).catalog_has_service(catalog, service_type, dataset_url) and self.catalog_has_dataset(catalog, dataset_url)













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


