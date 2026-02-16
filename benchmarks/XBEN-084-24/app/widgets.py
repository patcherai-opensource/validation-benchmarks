"""
Widget system for DataCanvas interactive ML demo platform.
Widgets are the building blocks of DataCanvas applications.
"""

import hashlib
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Optional


DATACANVAS_CACHE = os.environ.get("DATACANVAS_TEMP_DIR") or str(
    (Path(tempfile.gettempdir()) / "datacanvas").resolve()
)


def _hash_file(file_path: str) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def _hash_string(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:16]


class Widget:
    """Base class for all DataCanvas widgets."""

    _widget_counter = 0

    def __init__(
        self,
        elem_id: Optional[str] = None,
        elem_classes: Optional[list] = None,
        visible: bool = True,
        interactive: bool = True,
        render: bool = True,
    ):
        Widget._widget_counter += 1
        self._id = Widget._widget_counter
        self.elem_id = elem_id
        self.elem_classes = elem_classes or []
        self.visible = visible
        self.interactive = interactive
        self._render = render
        self.temp_files: set = set()

    @property
    def widget_id(self) -> int:
        return self._id

    def get_config(self) -> dict:
        return {
            "id": self._id,
            "type": self.__class__.__name__.lower(),
            "props": {
                "elem_id": self.elem_id,
                "visible": self.visible,
                "interactive": self.interactive,
            },
        }

    def transfer_asset_to_widget_cache(
        self, url_or_file_path: Optional[str] = None
    ) -> Optional[str]:
        """Moves a file or downloads a resource to the widget's cache directory,
        adds it to the widget's temp_files, and returns the path to the
        cached file. This ensures the file is accessible to the Widget
        and can be served to users.
        """
        if url_or_file_path is None:
            return None

        url_or_file_path = str(url_or_file_path)

        if url_or_file_path.startswith(("http://", "https://")):
            import httpx
            temp_dir_name = _hash_string(url_or_file_path)
            temp_dir = Path(DATACANVAS_CACHE) / temp_dir_name
            temp_dir.mkdir(exist_ok=True, parents=True)
            name = Path(url_or_file_path).name or "downloaded"
            full_path = str((temp_dir / name).resolve())
            if not Path(full_path).exists():
                with httpx.stream("GET", url_or_file_path) as r:
                    with open(full_path, "wb") as f:
                        for chunk in r.iter_raw():
                            f.write(chunk)
            self.temp_files.add(full_path)
            return full_path
        else:
            abs_path = str(Path(url_or_file_path).resolve())
            if not Path(abs_path).is_file():
                return None
            if not abs_path.startswith(DATACANVAS_CACHE):
                file_hash = _hash_file(abs_path)
                temp_dir = Path(DATACANVAS_CACHE) / file_hash
                temp_dir.mkdir(exist_ok=True, parents=True)
                name = Path(abs_path).name
                full_temp_path = str((temp_dir / name).resolve())
                if not Path(full_temp_path).exists():
                    shutil.copy2(abs_path, full_temp_path)
                self.temp_files.add(full_temp_path)
                return full_temp_path
            else:
                self.temp_files.add(abs_path)
                return abs_path

    def preprocess(self, data: Any) -> Any:
        return data

    def postprocess(self, data: Any) -> Any:
        return data


class TextInput(Widget):
    """Single-line text input widget."""

    def __init__(
        self,
        value: str = "",
        placeholder: str = "",
        label: str = "",
        max_length: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.value = value
        self.placeholder = placeholder
        self.label = label
        self.max_length = max_length

    def get_config(self) -> dict:
        config = super().get_config()
        config["props"].update({
            "value": self.value,
            "placeholder": self.placeholder,
            "label": self.label,
            "max_length": self.max_length,
        })
        return config

    def validate(self, data: str) -> bool:
        if self.max_length and len(data) > self.max_length:
            return False
        return True


class TextArea(Widget):
    """Multi-line text area widget."""

    def __init__(
        self,
        value: str = "",
        placeholder: str = "",
        label: str = "",
        lines: int = 5,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.value = value
        self.placeholder = placeholder
        self.label = label
        self.lines = lines

    def get_config(self) -> dict:
        config = super().get_config()
        config["props"].update({
            "value": self.value,
            "placeholder": self.placeholder,
            "label": self.label,
            "lines": self.lines,
        })
        return config


class ImageDisplay(Widget):
    """Image display widget."""

    def __init__(
        self,
        value: Optional[str] = None,
        label: str = "",
        image_mode: str = "RGB",
        height: Optional[int] = None,
        width: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.value = value
        self.label = label
        self.image_mode = image_mode
        self.height = height
        self.width = width
        if value:
            self.transfer_asset_to_widget_cache(value)

    def get_config(self) -> dict:
        config = super().get_config()
        config["props"].update({
            "value": self.value,
            "label": self.label,
            "image_mode": self.image_mode,
            "height": self.height,
            "width": self.width,
        })
        return config


class Label(Widget):
    """Label display widget."""

    def __init__(
        self,
        value: str = "",
        label: str = "",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.value = value
        self.label = label

    def get_config(self) -> dict:
        config = super().get_config()
        config["props"].update({
            "value": self.value,
            "label": self.label,
        })
        return config


class NumberInput(Widget):
    """Number input widget."""

    def __init__(
        self,
        value: float = 0,
        label: str = "",
        minimum: Optional[float] = None,
        maximum: Optional[float] = None,
        step: float = 1,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.value = value
        self.label = label
        self.minimum = minimum
        self.maximum = maximum
        self.step = step

    def get_config(self) -> dict:
        config = super().get_config()
        config["props"].update({
            "value": self.value,
            "label": self.label,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "step": self.step,
        })
        return config


class Dropdown(Widget):
    """Dropdown selector widget."""

    def __init__(
        self,
        choices: Optional[list] = None,
        value: Optional[str] = None,
        label: str = "",
        multiselect: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.choices = choices or []
        self.value = value
        self.label = label
        self.multiselect = multiselect

    def get_config(self) -> dict:
        config = super().get_config()
        config["props"].update({
            "choices": self.choices,
            "value": self.value,
            "label": self.label,
            "multiselect": self.multiselect,
        })
        return config


class FileUpload(Widget):
    """File upload widget."""

    def __init__(
        self,
        label: str = "",
        file_types: Optional[list] = None,
        file_count: str = "single",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.label = label
        self.file_types = file_types
        self.file_count = file_count

    def get_config(self) -> dict:
        config = super().get_config()
        config["props"].update({
            "label": self.label,
            "file_types": self.file_types,
            "file_count": self.file_count,
        })
        return config


class Slider(Widget):
    """Slider widget."""

    def __init__(
        self,
        value: float = 50,
        label: str = "",
        minimum: float = 0,
        maximum: float = 100,
        step: float = 1,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.value = value
        self.label = label
        self.minimum = minimum
        self.maximum = maximum
        self.step = step

    def get_config(self) -> dict:
        config = super().get_config()
        config["props"].update({
            "value": self.value,
            "label": self.label,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "step": self.step,
        })
        return config
