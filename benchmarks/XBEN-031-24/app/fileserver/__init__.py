"""
Salt fileserver subsystem - manages serving files from configured backends.
"""

import os
import hashlib
import logging

from config import MASTER_CONFIG

log = logging.getLogger(__name__)


def find_file(path, saltenv="base", **kwargs):
    """
    Search the configured file_roots for the requested file.
    Returns a dict with file path info or an empty dict if not found.
    """
    # Reject absolute paths
    if os.path.isabs(path):
        log.warning("Absolute path requested: %s", path)
        return {}

    fnd = {}
    file_roots = MASTER_CONFIG.get("file_roots", {})
    env_roots = file_roots.get(saltenv, [])

    for root in env_roots:
        full_path = os.path.join(root, path)
        if os.path.isfile(full_path):
            fnd["path"] = full_path
            fnd["rel"] = path
            fnd["saltenv"] = saltenv
            return fnd

    return fnd


def serve_file(path, saltenv="base", **kwargs):
    """
    Serve a file from the file_roots. Returns file content and metadata.
    """
    fnd = find_file(path, saltenv=saltenv, **kwargs)
    if not fnd:
        return {"content": None, "error": "File not found"}

    full_path = fnd["path"]

    try:
        with open(full_path, "rb") as fp:
            content = fp.read()

        file_hash = hashlib.sha256(content).hexdigest()

        return {
            "content": content.decode("utf-8", errors="replace"),
            "hash": file_hash,
            "hash_type": MASTER_CONFIG.get("hash_type", "sha256"),
            "saltenv": saltenv,
            "rel": fnd.get("rel", path),
        }
    except (IOError, OSError) as exc:
        log.error("Error serving file %s: %s", full_path, exc)
        return {"content": None, "error": "Unable to read file"}


def file_hash(path, saltenv="base", **kwargs):
    """
    Return the hash of a file in the file_roots.
    """
    fnd = find_file(path, saltenv=saltenv, **kwargs)
    if not fnd:
        return {"hash": None, "error": "File not found"}

    full_path = fnd["path"]
    try:
        with open(full_path, "rb") as fp:
            content = fp.read()
        h = hashlib.sha256(content).hexdigest()
        return {
            "hash": h,
            "hash_type": MASTER_CONFIG.get("hash_type", "sha256"),
        }
    except (IOError, OSError) as exc:
        log.error("Error hashing file %s: %s", full_path, exc)
        return {"hash": None, "error": "Unable to hash file"}


def file_list(saltenv="base", **kwargs):
    """
    List files available in the given salt environment.
    """
    file_roots = MASTER_CONFIG.get("file_roots", {})
    env_roots = file_roots.get(saltenv, [])
    result = []

    for root in env_roots:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            for fn in filenames:
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, root)
                result.append(rel)

    return sorted(result)


def envs():
    """
    Return a list of available salt environments.
    """
    file_roots = MASTER_CONFIG.get("file_roots", {})
    return list(file_roots.keys())
