"""
Base task implementing core prompt generation logic.

All built-in tasks inherit from BuiltinTask, which handles template
loading and rendering via Jinja2.
"""

import abc
from pathlib import Path
from typing import Any, Dict, List, Optional

import jinja2


TEMPLATE_DIR = Path(__file__).parent / "templates"


def read_template(name: str) -> str:
    """Read a built-in template by name."""
    path = TEMPLATE_DIR / f"{name}.jinja"
    if not path.exists():
        raise ValueError(f"{name} is not a valid built-in template.")
    return path.read_text()


class BuiltinTask(abc.ABC):
    """Abstract base task implementing prompt generation via Jinja2 templates.

    Built-in tasks provide:
    - Working prompt template strings
    - Swappable prompt examples for few-shot learning
    - Template rendering with task-specific context
    """

    def __init__(
        self,
        template: str,
        prompt_examples: Optional[List[Dict[str, Any]]] = None,
    ):
        self._template = template
        self._prompt_examples = prompt_examples or []

    def generate_prompt(self, text: str, **kwargs) -> str:
        """Generate a prompt by rendering the template with provided context.

        text (str): Input text to include in the prompt.
        **kwargs: Additional context variables for rendering.
        RETURNS (str): Rendered prompt string.
        """
        environment = jinja2.Environment()
        _template = environment.from_string(self._template)
        return _template.render(
            text=text,
            prompt_examples=self._prompt_examples,
            **self._get_prompt_data(text, **kwargs),
        )

    @abc.abstractmethod
    def _get_prompt_data(self, text: str, **kwargs) -> Dict[str, Any]:
        """Return task-specific template context variables."""

    @property
    def template(self) -> str:
        return self._template

    @template.setter
    def template(self, value: str):
        self._template = value

    @property
    def task_type(self) -> str:
        return self.__class__.__name__.replace("Task", "").lower()
