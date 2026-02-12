"""Content fetching backends for changedetection.io"""


class FetcherBase:
    """Base class for content fetchers."""
    
    error = None
    status_code = None
    content = None
    headers = None

    def run(self, url, timeout=30):
        raise NotImplementedError

    def get_error(self):
        return self.error
