import logging
import os
import pathlib

logger = logging.getLogger("vizboard.assets")

proxy_url_prefix = "_platform/cache"


def store_in_cache(base_cache_dir: pathlib.Path, path, data: bytes):
    cache_path = base_cache_dir / path
    pathlib.Path(cache_path.parent).mkdir(parents=True, exist_ok=True)
    try:
        logger.info("Writing cache file: %s", cache_path)
        cache_path.write_bytes(data)
    except FileNotFoundError:
        logger.info("Failed writing cache file: %s", cache_path)


def read_from_cache(base_cache_dir: pathlib.Path, path):
    cache_path = pathlib.Path(base_cache_dir / path)
    try:
        logger.info("Opening cache file: %s", cache_path)
        return cache_path.read_bytes()
    except (FileNotFoundError, IsADirectoryError):
        pass


def resolve_asset(base_cache_dir: pathlib.Path, path):
    parts = path.replace("\\", "/").split("/")
    store_path = path if len(parts) != 1 else pathlib.Path(path) / "index.js"

    content = read_from_cache(base_cache_dir, store_path)
    if content:
        return content

    return None
