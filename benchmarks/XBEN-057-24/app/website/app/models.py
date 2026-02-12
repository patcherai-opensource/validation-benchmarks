import pickle
import brotli
from base64 import urlsafe_b64decode, urlsafe_b64encode


class Config:
    """Application configuration that can be customized per-user via preferences."""

    def __init__(self, **kwargs):
        self.url = kwargs.get('url', 'https://www.google.com/search')
        self.lang_search = kwargs.get('lang_search', '')
        self.lang_interface = kwargs.get('lang_interface', '')
        self.style = kwargs.get('style', ':root { --whoogle-result-bgcolor: #fff; }')
        self.block = kwargs.get('block', '')
        self.dark = kwargs.get('dark', False)
        self.safe = kwargs.get('safe', False)
        self.nojs = kwargs.get('nojs', False)
        self.near = kwargs.get('near', '')
        self.theme = kwargs.get('theme', 'system')
        self.alts = kwargs.get('alts', False)
        self.new_tab = kwargs.get('new_tab', False)
        self.get_only = kwargs.get('get_only', False)
        self.accept_language = kwargs.get('accept_language', False)

    def from_params(self, params):
        """Update config from request parameters."""
        if 'preferences' in params:
            pref = self._decode_preferences(params['preferences'])
            if pref:
                for k, v in pref.items():
                    if hasattr(self, k):
                        setattr(self, k, v)
        for k, v in params.items():
            if k != 'preferences' and hasattr(self, k):
                setattr(self, k, v)
        return self

    @staticmethod
    def _encode_preferences(config_dict):
        """Encode a preferences dictionary for URL-safe transmission."""
        serialized = pickle.dumps(config_dict)
        compressed = brotli.compress(serialized)
        encoded = urlsafe_b64encode(compressed).decode()
        return 'u' + encoded

    def _decode_preferences(self, preferences):
        """Decode preferences from a URL-safe string representation.

        Supports two encoding modes:
          'e' - encrypted preferences (requires key, not currently used)
          'u' - url-safe base64 encoded, brotli compressed
        """
        if not preferences or len(preferences) < 2:
            return {}

        mode = preferences[0]
        data = preferences[1:]

        try:
            if mode == 'u':
                # URL-safe base64 decode with padding, then brotli decompress
                padded = data.encode() + b'=='
                config = pickle.loads(brotli.decompress(urlsafe_b64decode(padded)))
                return config
            elif mode == 'e':
                # Encrypted mode - would require key, return empty for now
                return {}
        except Exception:
            return {}

        return {}

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
