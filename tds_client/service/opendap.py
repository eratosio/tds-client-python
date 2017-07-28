
from .service import StandardService

from pydap.client import open_url as get_dataset

class OPeNDAPService(StandardService):
    name = 'OPeNDAP'
    description = ''
    path = 'dodsC'
    
    def get_dataset(self, session=None):
        return get_dataset(self.url, session=(session or self._session))
