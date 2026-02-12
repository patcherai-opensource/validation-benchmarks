"""copyparty auth service - manages accounts and permissions"""

import hashlib
import os
import time


class AuthSrv:
    def __init__(self, cfg=None):
        self.accounts = {}
        self.sessions = {}
        self.acl = {}

    def add_account(self, username, password):
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        self.accounts[username] = {
            "pw": pw_hash,
            "created": int(time.time()),
        }

    def check_pw(self, username, password):
        acc = self.accounts.get(username)
        if not acc:
            return False
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        return acc["pw"] == pw_hash

    def get_perm(self, username, vpath):
        if username == "*":
            return "r"
        acl = self.acl.get(vpath, {})
        return acl.get(username, acl.get("*", "r"))
