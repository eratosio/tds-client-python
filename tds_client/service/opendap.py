
from .service import StandardService

from pydap.client import open_url

class OPeNDAPService(StandardService):
    name = 'OPeNDAP'
    description = ''
    path = 'dodsC'
    
    def get_dataset(self, session=None):
        session = session or self._session
        
        return open_url(self.url, session=session)
