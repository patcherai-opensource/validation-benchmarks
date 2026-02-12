from .builtin_task import BuiltinTask
from .ner import NERTask
from .sentiment import SentimentTask
from .textcat import TextCatTask
from .summarization import SummarizationTask
from .raw import RawTask

TASK_REGISTRY = {
    "ner": NERTask,
    "sentiment": SentimentTask,
    "textcat": TextCatTask,
    "summarization": SummarizationTask,
    "raw": RawTask,
}

__all__ = [
    "BuiltinTask",
    "NERTask",
    "SentimentTask",
    "TextCatTask",
    "SummarizationTask",
    "RawTask",
    "TASK_REGISTRY",
]
