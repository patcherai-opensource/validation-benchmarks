import os
import yaml


def load_master_config():
    """Load the Salt master configuration."""
    config_path = os.environ.get("SALT_MASTER_CONFIG", "/etc/salt/master")
    defaults = {
        "interface": "0.0.0.0",
        "publish_port": 4505,
        "ret_port": 4506,
        "api_port": 80,
        "worker_threads": 5,
        "file_roots": {
            "base": ["/srv/salt"],
        },
        "pillar_roots": {
            "base": ["/srv/pillar"],
        },
        "cachedir": "/var/cache/salt/master",
        "pki_dir": "/etc/salt/pki/master",
        "log_file": "/var/log/salt/master",
        "log_level": "warning",
        "api_logfile": "/var/log/salt/api",
        "token_expire": 43200,
        "external_auth": {
            "pam": {
                "saltadmin": [".*"],
                "saltops": [".*", "@runner"],
            }
        },
        "rest_cherrypy": {
            "port": 80,
            "ssl_crt": None,
            "ssl_key": None,
            "disable_ssl": True,
        },
        "fileserver_backend": ["roots"],
        "hash_type": "sha256",
    }

    if os.path.isfile(config_path):
        with open(config_path, "r") as f:
            user_config = yaml.safe_load(f) or {}
        defaults.update(user_config)

    return defaults


MASTER_CONFIG = load_master_config()
