import logging
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any, List

from fastapi import UploadFile

logger = logging.getLogger(__name__)

EXTENSIONS_DIR = os.environ.get("EXTENSIONS_DIR", "/app/data/extensions")
DEFAULT_USER = "default"


class ExtensionManager:
    def __init__(self, ext_dir: str) -> None:
        os.makedirs(ext_dir, exist_ok=True)
        self.ext_dir = ext_dir

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize the uploaded filename to prevent directory traversal."""
        if not filename:
            raise ValueError("Empty filename")

        # Extract basename only
        basename = os.path.basename(filename)

        # Remove potentially dangerous characters, keep alphanumerics, dots, hyphens, underscores
        sanitized = re.sub(r"[^\w\-.]", "_", basename)

        if not sanitized or sanitized.startswith("."):
            raise ValueError("Invalid filename after sanitization")

        # Verify allowed file extensions
        allowed_ext = (".zip", ".py")
        if not sanitized.lower().endswith(allowed_ext):
            raise ValueError(f"Only {', '.join(allowed_ext)} files are accepted")

        return sanitized

    def _load_extension_modules(self, file_path: str) -> list:
        """Load extension modules from a zip file to enumerate metadata."""
        from zipimport import zipimporter

        loaded = []
        if not file_path.endswith(".zip"):
            return loaded

        import zipfile
        try:
            with zipfile.ZipFile(file_path, "r") as zf:
                init_files = [
                    n for n in zf.namelist()
                    if n.endswith("__init__.py") and not n.startswith("__MACOSX")
                ]
        except zipfile.BadZipFile:
            return loaded

        for module_path in init_files:
            try:
                pkg_name = str(Path(module_path).parent)
                zimp = zipimporter(file_path)
                mod = zimp.load_module(pkg_name)
                for key in dir(mod):
                    if key.startswith("__"):
                        continue
                    attr = getattr(mod, key)
                    if hasattr(attr, "_name") and hasattr(attr, "_version"):
                        loaded.append(attr)
            except Exception as exc:
                logger.warning(f"Failed to load module from {module_path}: {exc}")

        return loaded

    async def submit_extension(self, doc_file: UploadFile, user: Any = DEFAULT_USER):
        """Handle extension file upload and registration."""
        try:
            safe_filename = self._sanitize_filename(doc_file.filename)
        except ValueError as e:
            raise ValueError(f"Invalid extension file: {str(e)}")

        file_path = os.path.join(self.ext_dir, safe_filename)

        # Verify the resolved path stays within extensions directory
        if not Path(file_path).resolve().is_relative_to(Path(self.ext_dir).resolve()):
            raise ValueError("Invalid file path")

        if os.path.exists(file_path):
            os.remove(file_path)

        # Write uploaded content to a temp file first, then move
        tmp_fd, tmp_path = tempfile.mkstemp(dir=self.ext_dir)
        try:
            with os.fdopen(tmp_fd, "wb") as tmp:
                content = await doc_file.read()
                tmp.write(content)
            shutil.move(tmp_path, file_path)
        except Exception as e:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise e

        # Load and register the extension
        try:
            ext_modules = self._load_extension_modules(file_path)
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise ValueError(f"Invalid extension package: {str(e)}")

        return {
            "filename": safe_filename,
            "modules_loaded": len(ext_modules),
            "user": user if user else DEFAULT_USER,
        }

    def list_installed(self) -> list:
        """List all installed extension files."""
        extensions = []
        ext_path = Path(self.ext_dir)
        for f in ext_path.glob("*.zip"):
            extensions.append({
                "name": f.stem,
                "file_name": f.name,
                "size": f.stat().st_size,
            })
        for f in ext_path.glob("*.py"):
            extensions.append({
                "name": f.stem,
                "file_name": f.name,
                "size": f.stat().st_size,
            })
        return extensions

    def remove_extension(self, filename: str) -> bool:
        """Remove an installed extension."""
        safe = self._sanitize_filename(filename)
        file_path = os.path.join(self.ext_dir, safe)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False


extension_manager = ExtensionManager(EXTENSIONS_DIR)
