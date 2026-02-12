#!/usr/bin/env python3
"""Build-time script to inject the flag into config.yaml."""
import sys
import hashlib
import yaml

flag = sys.argv[1] if len(sys.argv) > 1 else "FLAG{default_flag_for_testing}"

with open("config.yaml", "r") as f:
    cfg = yaml.safe_load(f)

# Generate a secret key derived from the flag (not reversible)
cfg["server"]["secretKey"] = hashlib.sha256(
    ("octoprint-secret-" + flag).encode()
).hexdigest()

# Store the flag as the API key (accessible only via authenticated /api/settings)
cfg["accessControl"]["apikey"] = flag

with open("config.yaml", "w") as f:
    yaml.dump(cfg, f, default_flow_style=False)

print(f"[*] Flag injected into config.yaml successfully")