"""Task registry for managing predefined NLP task configurations."""

import os
from typing import Dict, Optional
from .core_task import CoreTask


# Built-in task templates
_BUILTIN_TEMPLATES: Dict[str, str] = {}


def _load_builtin_templates():
    """Load built-in task templates from the templates directory."""
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    if os.path.isdir(templates_dir):
        for fname in os.listdir(templates_dir):
            if fname.endswith(".jinja"):
                task_name = fname.replace(".jinja", "")
                with open(os.path.join(templates_dir, fname), "r") as f:
                    _BUILTIN_TEMPLATES[task_name] = f.read()


_load_builtin_templates()


class TaskRegistry:
    """Registry for predefined NLP task types."""

    _tasks: Dict[str, dict] = {}

    @classmethod
    def register(cls, name: str, template: str, description: str = ""):
        cls._tasks[name] = {
            "template": template,
            "description": description,
        }

    @classmethod
    def get_task(cls, name: str) -> Optional[CoreTask]:
        if name in cls._tasks:
            return CoreTask(
                template=cls._tasks[name]["template"],
                task_id=name,
            )
        if name in _BUILTIN_TEMPLATES:
            return CoreTask(
                template=_BUILTIN_TEMPLATES[name],
                task_id=name,
            )
        return None

    @classmethod
    def list_tasks(cls) -> Dict[str, str]:
        result = {}
        for name, info in cls._tasks.items():
            result[name] = info.get("description", "")
        for name in _BUILTIN_TEMPLATES:
            if name not in result:
                result[name] = f"Built-in template: {name}"
        return result


# Register default task types
TaskRegistry.register(
    "ner",
    description="Named Entity Recognition prompt",
    template=(
        "You are an expert NLP annotator. Identify all named entities in the text below.\n"
        "Classify each entity as one of: PERSON, ORGANIZATION, LOCATION, DATE, MISC.\n"
        "{% if prompt_examples %}\nExamples:\n"
        "{% for ex in prompt_examples %}\n"
        "Input: {{ ex.text }}\nEntities: {{ ex.entities }}\n{% endfor %}\n{% endif %}\n"
        "Input: {{ text }}\nEntities:"
    ),
)

TaskRegistry.register(
    "sentiment",
    description="Sentiment Analysis prompt",
    template=(
        "Analyze the sentiment of the following text. "
        "Respond with one of: POSITIVE, NEGATIVE, NEUTRAL.\n"
        "{% if prompt_examples %}\nExamples:\n"
        "{% for ex in prompt_examples %}\n"
        "Text: {{ ex.text }}\nSentiment: {{ ex.sentiment }}\n{% endfor %}\n{% endif %}\n"
        "Text: {{ text }}\nSentiment:"
    ),
)

TaskRegistry.register(
    "summarization",
    description="Text Summarization prompt",
    template=(
        "Summarize the following text in a concise manner.\n"
        "{% if prompt_examples %}\nExamples:\n"
        "{% for ex in prompt_examples %}\n"
        "Text: {{ ex.text }}\nSummary: {{ ex.summary }}\n{% endfor %}\n{% endif %}\n"
        "Text: {{ text }}\nSummary:"
    ),
)

TaskRegistry.register(
    "textcat",
    description="Text Classification prompt",
    template=(
        "Classify the following text into one of the given categories.\n"
        "{% if categories %}Categories: {{ categories | join(', ') }}\n{% endif %}"
        "{% if prompt_examples %}\nExamples:\n"
        "{% for ex in prompt_examples %}\n"
        "Text: {{ ex.text }}\nCategory: {{ ex.category }}\n{% endfor %}\n{% endif %}\n"
        "Text: {{ text }}\nCategory:"
    ),
)
