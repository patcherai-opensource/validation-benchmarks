#!/usr/bin/env python3
import yaml
import os

from app import create_app

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

app = create_app(config)

if __name__ == "__main__":
    app.run(
        host=config["server"]["host"],
        port=config["server"]["port"],
        debug=False,
        use_reloader=False
    )