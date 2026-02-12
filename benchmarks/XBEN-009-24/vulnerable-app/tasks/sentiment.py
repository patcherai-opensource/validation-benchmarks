"""Sentiment analysis task."""

from typing import Any, Dict, List, Optional

from .builtin_task import BuiltinTask, read_template

DEFAULT_SENTIMENT_TEMPLATE = read_template("sentiment.v1")


class SentimentTask(BuiltinTask):
    """Sentiment analysis task producing a score between 0 and 1."""

    def __init__(
        self,
        template: str = DEFAULT_SENTIMENT_TEMPLATE,
        prompt_examples: Optional[List[Dict[str, Any]]] = None,
    ):
        super().__init__(template=template, prompt_examples=prompt_examples)

    def _get_prompt_data(self, text: str, **kwargs) -> Dict[str, Any]:
        return {}
