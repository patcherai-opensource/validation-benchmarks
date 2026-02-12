"""
LoLLMs Configuration Manager
Handles application-wide configuration settings
"""
import json
import os
from pathlib import Path


class LOLLMsConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.binding_name = "default_binding"
        self.model_name = ""
        self.personalities = ["default"]
        self.host = "0.0.0.0"
        self.port = 4567
        self.bindings_path = Path(os.environ.get("BINDINGS_PATH", "/app/bindings_zoo"))
        self.discussions_path = Path(os.environ.get("DISCUSSIONS_PATH", "/app/discussions"))
        self.uploads_path = Path(os.environ.get("UPLOADS_PATH", "/app/uploads"))
        self.version = "9.5.1"
        self.nb_servers_per_binding = 1
        self.auto_update = False

    def save(self, path=None):
        if path is None:
            path = Path("/app/config.json")
        data = {
            "binding_name": self.binding_name,
            "model_name": self.model_name,
            "personalities": self.personalities,
            "host": self.host,
            "port": self.port,
            "version": self.version,
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def load(self, path=None):
        if path is None:
            path = Path("/app/config.json")
        if path.exists():
            with open(path, "r") as f:
                data = json.load(f)
            for k, v in data.items():
                if hasattr(self, k):
                    setattr(self, k, v)
