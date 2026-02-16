"""
The default content backend for Conductor file distribution.

This backend serves files from the Master node's local filesystem. Content
environments are defined using the content_roots configuration option.

Example configuration:

    content_roots:
      production:
        - /srv/conductor/content/production
      staging:
        - /srv/conductor/content/staging
"""

import errno
import logging
import os

import config

log = logging.getLogger(__name__)


def is_file_ignored(filepath):
    """Check if a file matches any of the ignore patterns."""
    basename = os.path.basename(filepath)
    for pattern in config.IGNORED_PATTERNS:
        if pattern.startswith("*"):
            if basename.endswith(pattern[1:]):
                return True
        elif basename == pattern:
            return True
    return False


def locate_content(path, content_env="production", **kwargs):
    """
    Search the environment for the relative path and return the
    result structure. This structure is passed to other backend
    interfaces for content retrieval.
    """
    actual_env = content_env
    if "env" in kwargs:
        kwargs.pop("env")

    path = os.path.normpath(path)
    result = {"path": "", "rel": ""}
    if os.path.isabs(path):
        return result
    if content_env not in config.CONTENT_ROOTS:
        if "__env__" in config.CONTENT_ROOTS:
            log.debug(
                "content environment '%s' maps to __env__ content_roots directory",
                content_env,
            )
            content_env = "__env__"
        else:
            return result

    def _add_file_stat(result):
        """
        Stat the file and add to the return dict.
        """
        try:
            result["stat"] = list(os.stat(result["path"]))
        except Exception as exc:
            log.error("Unable to stat file: %s", exc)
        return result

    if "index" in kwargs:
        try:
            root = config.CONTENT_ROOTS[content_env][int(kwargs["index"])]
        except IndexError:
            return result
        except ValueError:
            return result
        full = os.path.join(root, path)
        if os.path.isfile(full) and not is_file_ignored(full):
            result["path"] = full
            result["rel"] = path
            return _add_file_stat(result)
        return result

    for root in config.CONTENT_ROOTS[content_env]:
        if content_env == "__env__":
            root = root.replace("__env__", actual_env)
        full = os.path.join(root, path)
        if os.path.isfile(full) and not is_file_ignored(full):
            result["path"] = full
            result["rel"] = path
            return _add_file_stat(result)
    return result


def retrieve_content(load, fnd):
    """
    Return a chunk from a file based on the data received.
    """
    if "env" in load:
        load.pop("env")

    ret = {"data": "", "dest": ""}
    if "path" not in load or "loc" not in load or "content_env" not in load:
        return ret
    if not fnd["path"]:
        return ret
    ret["dest"] = fnd["rel"]
    fpath = os.path.normpath(fnd["path"])
    try:
        with open(fpath, "rb") as fp:
            fp.seek(load["loc"])
            data = fp.read(config.FILE_BUFFER_SIZE)
            ret["data"] = data
    except Exception as exc:
        log.error("Error reading file %s: %s", fpath, exc)
    return ret


def list_environments():
    """
    Return the available content environments.
    """
    return sorted(config.CONTENT_ROOTS.keys())


def list_content(content_env="production"):
    """
    Return a list of all files in a specified environment.
    """
    files = []
    if content_env not in config.CONTENT_ROOTS:
        return files
    for root in config.CONTENT_ROOTS[content_env]:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                if not is_file_ignored(full_path):
                    rel = os.path.relpath(full_path, root)
                    files.append(rel)
    return sorted(files)
