"""
Core block and component classes for the Gradio-compatible ML interface.
"""

import os
import shutil
import hashlib
import uuid
import json
from typing import Any, Optional, Dict, List


CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "upload_cache")


class BlockContext:
    """Manages the registry of all blocks/components in the application."""

    def __init__(self):
        self.blocks: Dict[int, "Block"] = {}
        self._id_counter = 0

    def register(self, block: "Block") -> int:
        block_id = self._id_counter
        self.blocks[block_id] = block
        self._id_counter += 1
        return block_id

    def get_block(self, block_id: int) -> Optional["Block"]:
        return self.blocks.get(block_id)


class Block:
    """Base class for all UI blocks/components."""

    def __init__(self, context: BlockContext, **kwargs):
        self.elem_id = kwargs.get("elem_id", None)
        self.visible = kwargs.get("visible", True)
        self.interactive = kwargs.get("interactive", True)
        self._id = context.register(self)
        self._context = context

    def move_resource_to_block_cache(self, path: str, block: Optional[Any] = None) -> str:
        """Move a resource file into the block cache directory for serving."""
        abs_path = os.path.abspath(path)

        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Resource not found: {path}")

        os.makedirs(CACHE_DIR, exist_ok=True)

        file_hash = hashlib.sha256(abs_path.encode()).hexdigest()[:16]
        basename = os.path.basename(abs_path)
        cache_subdir = os.path.join(CACHE_DIR, file_hash)
        os.makedirs(cache_subdir, exist_ok=True)
        dest = os.path.join(cache_subdir, basename)

        shutil.copy2(abs_path, dest)

        return f"/upload_cache/{file_hash}/{basename}"

    def get_config(self) -> dict:
        return {
            "id": self._id,
            "type": self.__class__.__name__.lower(),
            "props": {
                "visible": self.visible,
                "interactive": self.interactive,
                "elem_id": self.elem_id,
            }
        }


class Textbox(Block):
    """Text input component."""

    def __init__(self, context: BlockContext, **kwargs):
        self.value = kwargs.get("value", "")
        self.placeholder = kwargs.get("placeholder", "")
        self.label = kwargs.get("label", "")
        self.lines = kwargs.get("lines", 1)
        self.max_lines = kwargs.get("max_lines", 20)
        super().__init__(context, **kwargs)

    def preprocess(self, x: Any) -> str:
        if x is None:
            return ""
        return str(x)

    def postprocess(self, y: Any) -> str:
        if y is None:
            return ""
        return str(y)

    def get_config(self) -> dict:
        config = super().get_config()
        config["props"].update({
            "value": self.value,
            "placeholder": self.placeholder,
            "label": self.label,
            "lines": self.lines,
            "max_lines": self.max_lines,
        })
        return config


class Image(Block):
    """Image display/upload component."""

    def __init__(self, context: BlockContext, **kwargs):
        self.value = kwargs.get("value", None)
        self.label = kwargs.get("label", "")
        self.image_mode = kwargs.get("image_mode", "RGB")
        self.source = kwargs.get("source", "upload")
        self.type = kwargs.get("type", "numpy")
        super().__init__(context, **kwargs)

    def preprocess(self, x: Any) -> Any:
        return x

    def postprocess(self, y: Any) -> Any:
        if y is None:
            return None
        return y

    def get_config(self) -> dict:
        config = super().get_config()
        config["props"].update({
            "value": self.value,
            "label": self.label,
            "image_mode": self.image_mode,
            "source": self.source,
        })
        return config


class Number(Block):
    """Number input component."""

    def __init__(self, context: BlockContext, **kwargs):
        self.value = kwargs.get("value", 0)
        self.label = kwargs.get("label", "")
        self.minimum = kwargs.get("minimum", None)
        self.maximum = kwargs.get("maximum", None)
        super().__init__(context, **kwargs)

    def preprocess(self, x: Any) -> float:
        if x is None:
            return 0.0
        return float(x)

    def postprocess(self, y: Any) -> float:
        if y is None:
            return 0.0
        return float(y)

    def get_config(self) -> dict:
        config = super().get_config()
        config["props"].update({
            "value": self.value,
            "label": self.label,
            "minimum": self.minimum,
            "maximum": self.maximum,
        })
        return config


class Label(Block):
    """Label/output display component."""

    def __init__(self, context: BlockContext, **kwargs):
        self.value = kwargs.get("value", "")
        self.label = kwargs.get("label", "")
        self.num_top_classes = kwargs.get("num_top_classes", None)
        super().__init__(context, **kwargs)

    def preprocess(self, x: Any) -> Any:
        return x

    def postprocess(self, y: Any) -> Any:
        if isinstance(y, dict):
            return y
        return {"label": str(y), "confidences": []}

    def get_config(self) -> dict:
        config = super().get_config()
        config["props"].update({
            "value": self.value,
            "label": self.label,
            "num_top_classes": self.num_top_classes,
        })
        return config


class Button(Block):
    """Button component."""

    def __init__(self, context: BlockContext, **kwargs):
        self.value = kwargs.get("value", "Submit")
        self.variant = kwargs.get("variant", "primary")
        super().__init__(context, **kwargs)

    def get_config(self) -> dict:
        config = super().get_config()
        config["props"].update({
            "value": self.value,
            "variant": self.variant,
        })
        return config
