"""Gradio Blocks implementation."""

import os
import json
from typing import Optional, Set


class BlocksConfig:
    """Configuration for a Gradio Blocks app."""

    def __init__(
        self,
        title: str = "Gradio",
        analytics_enabled: bool = True,
        mode: str = "blocks",
        theme: str = "default",
        css: Optional[str] = None,
    ):
        self.title = title
        self.analytics_enabled = analytics_enabled
        self.mode = mode
        self.theme = theme
        self.css = css


class Blocks:
    """Main Blocks class for Gradio applications."""

    def __init__(
        self,
        title: str = "Gradio",
        analytics_enabled: bool = True,
        mode: str = "blocks",
        theme: str = "default",
        css: Optional[str] = None,
    ):
        self.title = title
        self.analytics_enabled = analytics_enabled
        self.mode = mode
        self.theme = theme
        self.css = css
        self.share = False
        self.enable_queue = True
        self.show_error = False
        self.proxy_urls: Set[str] = set()
        self.root = ""
        self.app_id = os.urandom(8).hex()
        self._components = []
        self._dependencies = []

    def get_config(self) -> dict:
        """Generate the configuration dictionary."""
        return {
            "mode": self.mode,
            "dev_mode": False,
            "analytics_enabled": self.analytics_enabled,
            "components": self._components,
            "dependencies": self._dependencies,
            "title": self.title,
            "theme": self.theme,
            "css": self.css,
            "is_space": False,
            "enable_queue": self.enable_queue,
            "show_error": self.show_error,
            "app_id": self.app_id,
            "root": self.root,
        }

    def launch(self, **kwargs):
        """Launch the Gradio app."""
        pass

    def add_component(self, component_id: str, component_type: str, props: dict):
        """Register a component."""
        self._components.append({
            "id": component_id,
            "type": component_type,
            "props": props,
        })

    def add_dependency(self, fn_index: int, inputs: list, outputs: list):
        """Register a dependency."""
        self._dependencies.append({
            "fn_index": fn_index,
            "inputs": inputs,
            "outputs": outputs,
        })
