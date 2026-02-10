#!/usr/bin/env python3
"""
Background worker that simulates periodic admin authentication.
This creates the race condition window that an attacker can exploit.
Similar to CVE-2023-1907 where the vulnerable scenario requires 
multiple users authenticating simultaneously.
"""
import time
import requests
import random
import sys

TARGET_URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:80'

def admin_check():
    """Trigger admin authentication via internal endpoint"""
    try:
        response = requests.post(f'{TARGET_URL}/internal/admin_check', timeout=5)
        return response.status_code == 200
    except Exception as e:
        return False

def main():
    print(f"[*] Admin worker started, targeting: {TARGET_URL}")
    
    # Wait for app to be ready
    time.sleep(5)
    
    while True:
        # Random interval between 0.1 and 0.5 seconds to create race opportunities
        interval = random.uniform(0.1, 0.5)
        time.sleep(interval)
        
        success = admin_check()
        if not success:
            # If failed, wait a bit longer before retry
            time.sleep(1)

if __name__ == '__main__':
    main()
