#!/usr/bin/env python3
"""Seed connection profiles database."""
import json
import uuid
import os

flag = ''
flag_path = '/tmp/.flag_tmp'
if os.path.exists(flag_path):
    with open(flag_path, 'r') as f:
        flag = f.read().strip()

profiles = [
    {
        'id': str(uuid.uuid4()),
        'name': 'production-bastion',
        'host': 'localhost',
        'port': 22,
        'user': 'svcuser',
        'credential': 'internalsvc2024',
        'auth_type': 'password',
        'created_at': '2024-09-15T08:30:00',
    },
    {
        'id': 'a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d',
        'name': 'vault-primary',
        'host': '10.0.50.10',
        'port': 22,
        'user': 'vault-admin',
        'credential': flag,
        'auth_type': 'password',
        'created_at': '2024-09-12T14:22:00',
    },
    {
        'id': str(uuid.uuid4()),
        'name': 'monitoring-node',
        'host': '10.0.30.5',
        'port': 2222,
        'user': 'monitor',
        'credential': 'monPr0b3!',
        'auth_type': 'password',
        'created_at': '2024-10-01T11:05:00',
    },
]

os.makedirs('/app/data', exist_ok=True)
with open('/app/data/profiles.json', 'w') as f:
    json.dump(profiles, f, indent=2)
