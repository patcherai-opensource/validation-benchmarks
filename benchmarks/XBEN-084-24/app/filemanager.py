"""
File manager for the contents service.

Handles file system operations for the REST API, mirroring
jupyter_server.services.contents.filemanager behavior.
"""

import os
import stat
import base64
import mimetypes
from datetime import datetime, timezone


class FileContentsManager:
    """Serves contents of files from the local filesystem."""

    def __init__(self, root_dir, allow_hidden=False):
        self.root_dir = os.path.realpath(root_dir)
        self.allow_hidden = allow_hidden

    def _get_os_path(self, path):
        """Convert an API path to a filesystem path."""
        path = path.strip("/")
        os_path = os.path.join(self.root_dir, path)
        os_path = os.path.realpath(os_path)
        return os_path

    def _is_hidden(self, os_path):
        """Check if a file or directory is hidden.

        A path is hidden if any component of the path starts with a dot.
        """
        rel = os.path.relpath(os_path, self.root_dir)
        parts = rel.split(os.sep)
        for part in parts:
            if part.startswith(".") and part not in (".", ".."):
                return True
        return False

    def _base_model(self, os_path, path):
        """Build the common model fields."""
        info = os.stat(os_path)
        model = {
            "name": os.path.basename(os_path) or path,
            "path": path,
            "last_modified": datetime.fromtimestamp(
                info.st_mtime, tz=timezone.utc
            ).isoformat(),
            "created": datetime.fromtimestamp(
                info.st_ctime, tz=timezone.utc
            ).isoformat(),
            "writable": os.access(os_path, os.W_OK),
            "mimetype": None,
            "content": None,
            "format": None,
        }
        return model

    def _dir_model(self, os_path, path, content=True):
        """Build the model for a directory."""
        model = self._base_model(os_path, path)
        model["type"] = "directory"
        model["size"] = None

        if content:
            contents = []
            for name in sorted(os.listdir(os_path)):
                child_os_path = os.path.join(os_path, name)
                child_path = os.path.join(path, name) if path else name

                # Filter hidden files from directory listings
                if self._is_hidden(child_os_path) and not self.allow_hidden:
                    continue

                try:
                    if os.path.isdir(child_os_path):
                        entry = self._dir_model(child_os_path, child_path, content=False)
                    else:
                        entry = self._file_model(child_os_path, child_path, content=False)
                    contents.append(entry)
                except OSError:
                    pass

            model["content"] = contents
            model["format"] = "json"

        return model

    def _file_model(self, os_path, path, content=True):
        """Build the model for a file."""
        model = self._base_model(os_path, path)
        model["size"] = os.path.getsize(os_path)

        mime, _ = mimetypes.guess_type(os_path)
        model["mimetype"] = mime or "application/octet-stream"

        if os_path.endswith(".ipynb"):
            model["type"] = "notebook"
        else:
            model["type"] = "file"

        if content:
            # Try to read as text first
            try:
                with open(os_path, "r", encoding="utf-8") as f:
                    model["content"] = f.read()
                model["format"] = "text"
                if model["type"] == "notebook":
                    model["format"] = "json"
            except (UnicodeDecodeError, ValueError):
                with open(os_path, "rb") as f:
                    model["content"] = base64.b64encode(f.read()).decode("ascii")
                model["format"] = "base64"

        return model

    def is_hidden(self, path):
        """Public method to check if path is hidden."""
        os_path = self._get_os_path(path)
        return self._is_hidden(os_path)

    def exists(self, path):
        """Check if a path exists."""
        os_path = self._get_os_path(path)
        return os.path.exists(os_path)

    def get(self, path, content=True, type=None):
        """Get a file or directory model."""
        os_path = self._get_os_path(path)

        if not os.path.exists(os_path):
            return None

        # Validate the path is within root_dir
        if not os_path.startswith(self.root_dir):
            return None

        if os.path.isdir(os_path):
            model = self._dir_model(os_path, path, content=content)
        else:
            model = self._file_model(os_path, path, content=content)

        return model

    def save(self, path, model):
        """Save a file.

        Hidden file check is applied here (save operations check).
        """
        os_path = self._get_os_path(path)

        if not os_path.startswith(self.root_dir):
            return None, "Cannot write outside root directory"

        if self._is_hidden(os_path) and not self.allow_hidden:
            return None, "Cannot write to hidden files or directories"

        file_type = model.get("type", "file")
        if file_type == "directory":
            os.makedirs(os_path, exist_ok=True)
        else:
            fmt = model.get("format", "text")
            content = model.get("content", "")
            parent = os.path.dirname(os_path)
            os.makedirs(parent, exist_ok=True)

            if fmt == "base64":
                with open(os_path, "wb") as f:
                    f.write(base64.b64decode(content))
            else:
                with open(os_path, "w", encoding="utf-8") as f:
                    f.write(content)

        return self.get(path, content=False), None

    def delete_file(self, path):
        """Delete a file or empty directory.

        Hidden file check is applied here.
        """
        os_path = self._get_os_path(path)

        if not os_path.startswith(self.root_dir):
            return "Cannot delete outside root directory"

        if self._is_hidden(os_path) and not self.allow_hidden:
            return "Cannot delete hidden files or directories"

        if not os.path.exists(os_path):
            return "File not found"

        if os.path.isdir(os_path):
            os.rmdir(os_path)
        else:
            os.unlink(os_path)

        return None

    def rename_file(self, old_path, new_path):
        """Rename a file or directory.

        Hidden file check is applied here.
        """
        old_os_path = self._get_os_path(old_path)
        new_os_path = self._get_os_path(new_path)

        if not old_os_path.startswith(self.root_dir):
            return "Cannot rename outside root directory"
        if not new_os_path.startswith(self.root_dir):
            return "Cannot rename outside root directory"

        if self._is_hidden(old_os_path) and not self.allow_hidden:
            return "Cannot rename hidden files or directories"
        if self._is_hidden(new_os_path) and not self.allow_hidden:
            return "Cannot rename to hidden path"

        if not os.path.exists(old_os_path):
            return "File not found"

        os.rename(old_os_path, new_os_path)
        return None
