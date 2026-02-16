import os
import pickle
import hashlib
import logging
from base64 import urlsafe_b64encode, urlsafe_b64decode
from cryptography.fernet import Fernet
import brotli


class Config:
    def __init__(self, **kwargs):
        self.lang_results = os.getenv('SEARCH_CONFIG_LANGUAGE', '')
        self.lang_ui = os.getenv('SEARCH_CONFIG_UI_LANGUAGE', '')
        self.region = os.getenv('SEARCH_CONFIG_REGION', '')
        self.theme = os.getenv('SEARCH_CONFIG_THEME', 'system')
        self.safe_search = self._read_bool('SEARCH_CONFIG_SAFE')
        self.open_links_new_tab = self._read_bool('SEARCH_CONFIG_NEW_TAB')
        self.show_images = self._read_bool('SEARCH_CONFIG_IMAGES')
        self.use_get = self._read_bool('SEARCH_CONFIG_GET_ONLY')
        self.strip_trackers = self._read_bool('SEARCH_CONFIG_STRIP_TRACKERS', True)
        self.custom_css = os.getenv('SEARCH_CONFIG_STYLE', '')
        self.time_range = os.getenv('SEARCH_CONFIG_TIME_RANGE', '')
        self.settings_encrypted = self._read_bool('SEARCH_CONFIG_SETTINGS_ENCRYPTED')
        self.settings_key = os.getenv('SEARCH_CONFIG_SETTINGS_KEY', '')

        self.safe_keys = [
            'lang_results',
            'lang_ui',
            'region',
            'theme',
            'safe_search',
            'open_links_new_tab',
            'show_images',
            'strip_trackers',
            'time_range',
            'settings_encrypted',
        ]

        if kwargs:
            mutable_attrs = self._get_mutable_attrs()
            for attr in mutable_attrs:
                if attr in kwargs:
                    setattr(self, attr, kwargs[attr])
                elif mutable_attrs[attr] == bool:
                    setattr(self, attr, False)

    @staticmethod
    def _read_bool(env_key, default=False):
        val = os.getenv(env_key, str(default).lower())
        return val.lower() in ('true', '1', 'yes')

    def __getitem__(self, name):
        return getattr(self, name)

    def __setitem__(self, name, value):
        return setattr(self, name, value)

    def __delitem__(self, name):
        return delattr(self, name)

    def __contains__(self, name):
        return hasattr(self, name)

    def _get_mutable_attrs(self):
        return {name: type(attr) for name, attr in self.__dict__.items()
                if not name.startswith("__")
                and (type(attr) is bool or type(attr) is str)}

    def get_attrs(self):
        return {name: attr for name, attr in self.__dict__.items()
                if not name.startswith("__")
                and (type(attr) is bool or type(attr) is str)}

    def is_safe_key(self, key):
        return key in self.safe_keys

    @property
    def settings(self):
        if self.settings_encrypted:
            self.settings_encrypted = bool(self.settings_key)
        encrypted_flag = "e" if self.settings_encrypted else "u"
        settings_digest = self._encode_settings()
        return f"{encrypted_flag}{settings_digest}"

    def apply_params(self, params):
        if 'settings' in params:
            params_new = self._decode_settings(params['settings'])
            if len(params_new):
                params = params_new

        for param_key in params.keys():
            if not self.is_safe_key(param_key):
                continue
            param_val = params.get(param_key)
            if param_val == 'off':
                param_val = False
            elif isinstance(param_val, str):
                if param_val.isdigit():
                    param_val = int(param_val)
            self[param_key] = param_val
        return self

    def to_params(self, keys=None):
        if keys is None:
            keys = self.safe_keys
        param_str = ''
        for safe_key in keys:
            if not self[safe_key]:
                continue
            param_str = param_str + f'&{safe_key}={self[safe_key]}'
        return param_str

    def _get_fernet_key(self, password):
        hash_object = hashlib.md5(password.encode())
        key = urlsafe_b64encode(hash_object.hexdigest().encode())
        return key

    def _encode_settings(self):
        encoded_settings = brotli.compress(pickle.dumps(self.get_attrs()))
        if self.settings_encrypted:
            if self.settings_key != '':
                key = self._get_fernet_key(self.settings_key)
                encoded_settings = Fernet(key).encrypt(encoded_settings)
                encoded_settings = brotli.compress(encoded_settings)
        return urlsafe_b64encode(encoded_settings).decode()

    def _decode_settings(self, settings):
        mode = settings[0]
        settings = settings[1:]
        if mode == 'e':
            try:
                key = self._get_fernet_key(self.settings_key)
                config = Fernet(key).decrypt(
                    brotli.decompress(urlsafe_b64decode(
                        settings.encode() + b'==')))
                config = pickle.loads(brotli.decompress(config))
            except Exception:
                config = {}
        elif mode == 'u':
            config = pickle.loads(
                brotli.decompress(urlsafe_b64decode(
                    settings.encode() + b'==')))
        else:
            config = {}
        return config
