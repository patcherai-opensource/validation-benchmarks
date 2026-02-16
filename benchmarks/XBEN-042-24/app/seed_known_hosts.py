#!/usr/bin/env python3
"""Seed known_hosts with the local SSH server's host key fingerprints."""
import json
import hashlib
import glob
import os
import paramiko

def load_all_host_keys():
    results = []
    key_loaders = {
        'rsa': paramiko.RSAKey,
        'ecdsa': paramiko.ECDSAKey,
        'ed25519': paramiko.Ed25519Key,
    }
    
    for key_type, loader in key_loaders.items():
        key_file = f'/etc/ssh/ssh_host_{key_type}_key'
        if os.path.exists(key_file):
            try:
                key = loader.from_private_key_file(key_file)
                key_bytes = key.asbytes()
                fp = hashlib.sha256(key_bytes).hexdigest()
                results.append((fp, key.get_name()))
            except Exception:
                continue
    return results

keys = load_all_host_keys()
known_hosts = []
for fp, kt in keys:
    known_hosts.append({
        'host': 'localhost',
        'port': 22,
        'fingerprint': fp,
        'key_type': kt,
        'added_at': '2024-09-15T08:31:00',
    })

os.makedirs('/app/data', exist_ok=True)
with open('/app/data/known_hosts.json', 'w') as f:
    json.dump(known_hosts, f, indent=2)
