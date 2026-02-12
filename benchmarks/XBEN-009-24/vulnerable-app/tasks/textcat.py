"""Text categorization task."""

from typing import Any, Dict, List, Optional

from .builtin_task import BuiltinTask, read_template

DEFAULT_TEXTCAT_TEMPLATE = read_template("textcat.v1")

DEFAULT_TEXTCAT_LABELS = [
    "POSITIVE", "NEGATIVE", "NEUTRAL", "MIXED"
]


class TextCatTask(BuiltinTask):
    """Text categorization task for classifying text into predefined labels."""

    def __init__(
        self,
        template: str = DEFAULT_TEXTCAT_TEMPLATE,
        labels: Optional[List[str]] = None,
        exclusive_classes: bool = True,
        prompt_examples: Optional[List[Dict[str, Any]]] = None,
    ):
        super().__init__(template=template, prompt_examples=prompt_examples)
        self._labels = labels or DEFAULT_TEXTCAT_LABELS
        self._exclusive_classes = exclusive_classes

    def _get_prompt_data(self, text: str, **kwargs) -> Dict[str, Any]:
        return {
            "labels": kwargs.get("labels", self._labels),
            "exclusive_classes": self._exclusive_classes,
        }
