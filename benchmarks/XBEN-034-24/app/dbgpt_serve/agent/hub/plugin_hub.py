"""Plugin Hub - manages plugin storage, upload, and retrieval."""

import logging
import os
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from dbgpt_serve.agent.resource.tool.autogpt.plugins_util import scan_plugins

logger = logging.getLogger(__name__)

DEFAULT_PLUGINS_DIR = os.environ.get(
    "PLUGINS_DIR", "/app/plugins"
)


def _sanitize_filename(filename: str) -> str:
    """Sanitize the uploaded filename to prevent directory traversal."""
    # Remove any path components
    filename = os.path.basename(filename)
    # Remove potentially dangerous characters
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    return filename


def get_plugins_dir() -> str:
    """Return the configured plugins directory."""
    os.makedirs(DEFAULT_PLUGINS_DIR, exist_ok=True)
    return DEFAULT_PLUGINS_DIR


def upload_my_plugin(
    file_content: bytes,
    filename: str,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Upload a plugin file to the plugins directory.

    Args:
        file_content: Raw bytes of the uploaded file.
        filename: Original filename from the upload.
        user_id: Optional user identifier for logging.

    Returns:
        Dictionary with upload result information.
    """
    plugins_dir = get_plugins_dir()
    safe_filename = _sanitize_filename(filename)

    if not safe_filename:
        raise ValueError("Invalid filename provided")

    dest_path = os.path.join(plugins_dir, safe_filename)

    # Write the file to the plugins directory
    with open(dest_path, "wb") as f:
        f.write(file_content)

    logger.info(
        "Plugin uploaded: %s (by user: %s)",
        safe_filename,
        user_id or "anonymous",
    )

    return {
        "filename": safe_filename,
        "path": dest_path,
        "size": len(file_content),
    }


def refresh_plugins() -> List[Dict[str, Any]]:
    """Refresh the plugin list by scanning the plugins directory.

    This will load and inspect all plugins to extract their metadata.
    """
    plugins_dir = get_plugins_dir()
    plugins = scan_plugins(plugins_dir)
    logger.info("Discovered %d plugins", len(plugins))
    return plugins


def list_plugins() -> List[Dict[str, Any]]:
    """List all plugin files in the plugins directory without loading them."""
    plugins_dir = get_plugins_dir()
    result = []

    if not os.path.exists(plugins_dir):
        return result

    for entry in os.scandir(plugins_dir):
        if entry.is_file() and (entry.name.endswith(".zip") or entry.name.endswith(".py")):
            result.append({
                "filename": entry.name,
                "size": entry.stat().st_size,
                "path": entry.path,
            })
        elif entry.is_dir() and not entry.name.startswith("."):
            result.append({
                "filename": entry.name,
                "size": 0,
                "path": entry.path,
                "type": "directory",
            })

    return result


def delete_plugin(plugin_name: str) -> bool:
    """Delete a plugin by name."""
    plugins_dir = get_plugins_dir()
    safe_name = _sanitize_filename(plugin_name)
    target = os.path.join(plugins_dir, safe_name)

    if os.path.exists(target):
        if os.path.isdir(target):
            shutil.rmtree(target)
        else:
            os.remove(target)
        # Clean up extracted directories
        extracted = os.path.join(plugins_dir, f".{Path(safe_name).stem}_extracted")
        if os.path.exists(extracted):
            shutil.rmtree(extracted)
        return True

    return False
