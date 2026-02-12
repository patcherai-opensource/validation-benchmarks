"""Raw task for arbitrary prompt generation."""

from typing import Any, Dict, List, Optional

from .builtin_task import BuiltinTask, read_template

DEFAULT_RAW_TEMPLATE = read_template("raw.v1")


class RawTask(BuiltinTask):
    """Raw task. Allows fully custom prompt templates without built-in
    instructions. Users provide their own template and the text content
    is rendered directly.

    This task is useful when the user wants complete control over
    prompt formatting.
    """

    def __init__(
        self,
        template: str = DEFAULT_RAW_TEMPLATE,
        field: str = "llm_reply",
        prompt_examples: Optional[List[Dict[str, Any]]] = None,
    ):
        super().__init__(template=template, prompt_examples=prompt_examples)
        self._field = field

    def _get_prompt_data(self, text: str, **kwargs) -> Dict[str, Any]:
        return {}

    @property
    def field(self) -> str:
        return self._field
