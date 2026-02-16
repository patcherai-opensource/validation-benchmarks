"""Core task implementation for prompt generation.

This module contains the base task class that handles template rendering
for NLP prompt generation. Tasks accept a Jinja2 template string and
render it with the provided context data (e.g., input text, examples).
"""

import jinja2
from typing import Any, Dict, List, Optional


class CoreTask:
    """Base task for generating structured NLP prompts.

    Accepts a Jinja2 template and renders it against provided context data.
    Subclasses can extend this to add task-specific prompt generation logic.
    """

    def __init__(
        self,
        template: str,
        examples: Optional[List[Dict[str, Any]]] = None,
        task_id: Optional[str] = None,
    ):
        self._template = template
        self._examples = examples or []
        self._task_id = task_id

    def compose_prompt(self, text: str, **kwargs) -> str:
        """Generate a prompt by rendering the template with input data.

        text (str): Input text to include in the prompt.
        kwargs: Additional context variables for template rendering.
        RETURNS (str): The rendered prompt string.
        """
        environment = jinja2.Environment()
        _template = environment.from_string(self._template)

        return _template.render(
            text=text,
            prompt_examples=self._examples,
            **kwargs,
        )

    @property
    def template_source(self) -> str:
        return self._template

    @property
    def examples(self) -> List[Dict[str, Any]]:
        return self._examples

    @property
    def task_id(self) -> Optional[str]:
        return self._task_id
