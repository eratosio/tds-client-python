
from tds_client.service import StandardService

DEFAULT_CHUNK_SIZE = 16384  # 16 KiB


class HttpServerService(StandardService):
    service_type = 'HTTPServer'
    name = 'Http Server'
    aliases = ['http']

    def download(self, local_path, session=None, chunk_size=DEFAULT_CHUNK_SIZE):
        with open(local_path, 'wb') as f, (session or self._session).get(self.url, stream=True) as response:
            response.raise_for_status()
            for chunk in response.iter_content(chunk_size=chunk_size):
                f.write(chunk)
