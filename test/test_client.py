import unittest

from tds_client import Client


# TODO: more tests...
class Tests(unittest.TestCase):
    def setUp(self):
        self.subject = Client(url='https://senaps.io/thredds/')

    def test_init(self):
        self.assertEqual('https://senaps.io/thredds/catalog.xml', self.subject.catalog_url)