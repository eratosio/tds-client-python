
from tds_client.service import StandardService

from pydap.client import open_url as get_dataset

class OPeNDAPService(StandardService):
    service_type = 'OpenDAP'
    name = 'OPeNDAP'
    
    def get_dataset(self, session=None):
        return get_dataset(self.url, session=(session or self._session))
