"""Utilities for scanning and loading AutoGPT-compatible plugins."""

import importlib
import importlib.util
import inspect
import logging
import os
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


def _is_valid_plugin_package(zip_path: str) -> bool:
    """Check if a ZIP file contains a valid plugin package structure."""
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
            has_init = any(
                n.endswith("__init__.py") for n in names
            )
            has_python = any(n.endswith(".py") for n in names)
            return has_init or has_python
    except zipfile.BadZipFile:
        return False


def scan_plugins(plugins_dir: str) -> List[Dict[str, Any]]:
    """Scan the plugins directory for installed plugins and return metadata.

    This function discovers plugin packages (ZIP files and directories)
    in the specified directory, loads them, and extracts their metadata.
    """
    discovered = []
    plugins_path = Path(plugins_dir)

    if not plugins_path.exists():
        logger.warning("Plugins directory does not exist: %s", plugins_dir)
        return discovered

    for entry in plugins_path.iterdir():
        try:
            if entry.suffix == ".zip":
                plugin_info = _load_plugin_from_zip(str(entry))
                if plugin_info:
                    discovered.append(plugin_info)
            elif entry.is_dir() and (entry / "__init__.py").exists():
                plugin_info = _load_plugin_from_directory(str(entry))
                if plugin_info:
                    discovered.append(plugin_info)
        except Exception as e:
            logger.error("Error scanning plugin %s: %s", entry.name, str(e))
            continue

    return discovered


def _load_plugin_from_zip(zip_path: str) -> Optional[Dict[str, Any]]:
    """Load a plugin from a ZIP file and return its metadata."""
    if not _is_valid_plugin_package(zip_path):
        return None

    zip_name = Path(zip_path).stem
    extract_dir = Path(zip_path).parent / f".{zip_name}_extracted"

    # Extract ZIP contents
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(str(extract_dir))

    # Find the plugin module
    init_file = None
    for root, dirs, files in os.walk(str(extract_dir)):
        if "__init__.py" in files:
            init_file = os.path.join(root, "__init__.py")
            break
        for f in files:
            if f.endswith(".py"):
                init_file = os.path.join(root, f)
                break
        if init_file:
            break

    if not init_file:
        return None

    # Load the module to extract metadata
    module_name = f"plugin_{zip_name}"
    spec = importlib.util.spec_from_file_location(module_name, init_file)
    if spec is None or spec.loader is None:
        return None

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    # Extract plugin metadata
    plugin_info = {
        "name": getattr(module, "PLUGIN_NAME", zip_name),
        "version": getattr(module, "PLUGIN_VERSION", "0.1.0"),
        "description": getattr(module, "PLUGIN_DESCRIPTION", ""),
        "author": getattr(module, "PLUGIN_AUTHOR", "unknown"),
        "path": zip_path,
        "type": "zip",
    }

    return plugin_info


def _load_plugin_from_directory(dir_path: str) -> Optional[Dict[str, Any]]:
    """Load a plugin from a directory and return its metadata."""
    init_file = os.path.join(dir_path, "__init__.py")
    if not os.path.exists(init_file):
        return None

    dir_name = Path(dir_path).name
    module_name = f"plugin_{dir_name}"

    spec = importlib.util.spec_from_file_location(module_name, init_file)
    if spec is None or spec.loader is None:
        return None

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    plugin_info = {
        "name": getattr(module, "PLUGIN_NAME", dir_name),
        "version": getattr(module, "PLUGIN_VERSION", "0.1.0"),
        "description": getattr(module, "PLUGIN_DESCRIPTION", ""),
        "author": getattr(module, "PLUGIN_AUTHOR", "unknown"),
        "path": dir_path,
        "type": "directory",
    }

    return plugin_info
