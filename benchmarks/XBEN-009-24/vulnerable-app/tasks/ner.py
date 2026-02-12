"""Named Entity Recognition task."""

from typing import Any, Dict, List, Optional

from .builtin_task import BuiltinTask, read_template

DEFAULT_NER_TEMPLATE = read_template("ner.v1")

DEFAULT_NER_LABELS = [
    "PERSON", "ORG", "GPE", "DATE", "MONEY", "PRODUCT", "EVENT", "LOC"
]


class NERTask(BuiltinTask):
    """NER task for extracting named entities from text."""

    def __init__(
        self,
        template: str = DEFAULT_NER_TEMPLATE,
        labels: Optional[List[str]] = None,
        label_definitions: Optional[Dict[str, str]] = None,
        prompt_examples: Optional[List[Dict[str, Any]]] = None,
    ):
        super().__init__(template=template, prompt_examples=prompt_examples)
        self._labels = labels or DEFAULT_NER_LABELS
        self._label_definitions = label_definitions

    def _get_prompt_data(self, text: str, **kwargs) -> Dict[str, Any]:
        return {
            "labels": kwargs.get("labels", self._labels),
            "label_definitions": kwargs.get(
                "label_definitions", self._label_definitions
            ),
        }
