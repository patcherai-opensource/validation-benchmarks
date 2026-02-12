"""Summarization task."""

from typing import Any, Dict, List, Optional

from .builtin_task import BuiltinTask, read_template

DEFAULT_SUMMARIZATION_TEMPLATE = read_template("summarization.v1")


class SummarizationTask(BuiltinTask):
    """Text summarization task."""

    def __init__(
        self,
        template: str = DEFAULT_SUMMARIZATION_TEMPLATE,
        max_length: int = 100,
        prompt_examples: Optional[List[Dict[str, Any]]] = None,
    ):
        super().__init__(template=template, prompt_examples=prompt_examples)
        self._max_length = max_length

    def _get_prompt_data(self, text: str, **kwargs) -> Dict[str, Any]:
        return {
            "max_length": kwargs.get("max_length", self._max_length),
        }
