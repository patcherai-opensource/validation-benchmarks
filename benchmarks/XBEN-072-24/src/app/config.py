import os
import yaml


_settings = None


def load_settings():
    global _settings
    if _settings is not None:
        return _settings

    config_path = os.path.join(
        os.path.dirname(__file__), "..", "config", "settings.yaml"
    )
    with open(config_path, "r") as f:
        _settings = yaml.safe_load(f)

    return _settings


def get_settings():
    if _settings is None:
        return load_settings()
    return _settings