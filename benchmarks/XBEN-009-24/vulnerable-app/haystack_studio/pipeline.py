# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from haystack_studio.components.builders.prompt_builder import PromptBuilder
from haystack_studio.components.builders.chat_prompt_builder import (
    ChatPromptBuilder,
    ChatMessage,
)

logger = logging.getLogger(__name__)

COMPONENT_REGISTRY = {
    "PromptBuilder": {
        "type": "haystack.components.builders.PromptBuilder",
        "description": "Renders prompt templates with Jinja2 syntax",
        "parameters": {
            "template": {"type": "str", "required": True},
            "required_variables": {"type": "list", "required": False},
        },
    },
    "ChatPromptBuilder": {
        "type": "haystack.components.builders.ChatPromptBuilder",
        "description": "Renders chat prompt templates from message lists",
        "parameters": {
            "template": {"type": "list[ChatMessage]", "required": False},
            "required_variables": {"type": "list", "required": False},
        },
    },
    "DocumentJoiner": {
        "type": "haystack.components.joiners.DocumentJoiner",
        "description": "Joins documents from multiple inputs",
        "parameters": {
            "join_mode": {"type": "str", "required": False, "default": "concatenate"},
        },
    },
    "TextFileConverter": {
        "type": "haystack.components.converters.TextFileConverter",
        "description": "Converts text files to Document objects",
        "parameters": {
            "encoding": {"type": "str", "required": False, "default": "utf-8"},
        },
    },
    "DocumentSplitter": {
        "type": "haystack.components.preprocessors.DocumentSplitter",
        "description": "Splits documents into smaller chunks",
        "parameters": {
            "split_by": {"type": "str", "required": False, "default": "word"},
            "split_length": {"type": "int", "required": False, "default": 200},
        },
    },
}


class Pipeline:
    """Represents a Haystack pipeline with connected components."""

    def __init__(self, name: str, pipeline_id: Optional[str] = None):
        self.id = pipeline_id or str(uuid.uuid4())
        self.name = name
        self.components: Dict[str, Any] = {}
        self.connections: List[Dict[str, str]] = []
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = self.created_at

    def add_component(self, name: str, component: Any) -> None:
        self.components[name] = component
        self.updated_at = datetime.utcnow().isoformat()

    def connect(self, sender: str, receiver: str) -> None:
        self.connections.append({"sender": sender, "receiver": receiver})
        self.updated_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        components = {}
        for name, comp in self.components.items():
            if hasattr(comp, "to_dict"):
                components[name] = comp.to_dict()
            else:
                components[name] = {"type": type(comp).__name__}

        return {
            "id": self.id,
            "name": self.name,
            "components": components,
            "connections": self.connections,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class PipelineManager:
    """Manages pipeline lifecycle - creation, storage, execution."""

    def __init__(self):
        self._pipelines: Dict[str, Pipeline] = {}
        self._init_default_pipelines()

    def _init_default_pipelines(self):
        """Create example pipelines to demonstrate the system."""
        # RAG prompt pipeline
        rag_pipeline = Pipeline(name="rag-question-answering", pipeline_id="rag-qa-1")
        rag_builder = PromptBuilder(
            template=(
                "Given the following documents, answer the question.\n"
                "Documents:\n{% for doc in documents %}- {{ doc }}\n{% endfor %}\n"
                "Question: {{ query }}\nAnswer:"
            )
        )
        rag_pipeline.add_component("prompt_builder", rag_builder)
        self._pipelines[rag_pipeline.id] = rag_pipeline

        # Translation pipeline
        translate_pipeline = Pipeline(
            name="translation-pipeline", pipeline_id="translate-1"
        )
        translate_builder = PromptBuilder(
            template="Translate the following text to {{ target_language }}:\n\n{{ text }}\n\nTranslation:"
        )
        translate_pipeline.add_component("prompt_builder", translate_builder)
        self._pipelines[translate_pipeline.id] = translate_pipeline

        # Summarization pipeline
        summary_pipeline = Pipeline(
            name="document-summarizer", pipeline_id="summarize-1"
        )
        summary_builder = PromptBuilder(
            template="Summarize the following document in {{ style }} style:\n\n{{ document }}\n\nSummary:"
        )
        summary_pipeline.add_component("prompt_builder", summary_builder)
        self._pipelines[summary_pipeline.id] = summary_pipeline

    def list_pipelines(self) -> List[Dict[str, Any]]:
        return [p.to_dict() for p in self._pipelines.values()]

    def get_pipeline(self, pipeline_id: str) -> Optional[Pipeline]:
        return self._pipelines.get(pipeline_id)

    def create_pipeline(self, name: str) -> Pipeline:
        pipeline = Pipeline(name=name)
        self._pipelines[pipeline.id] = pipeline
        return pipeline

    def delete_pipeline(self, pipeline_id: str) -> bool:
        if pipeline_id in self._pipelines:
            del self._pipelines[pipeline_id]
            return True
        return False

    def add_component_to_pipeline(
        self,
        pipeline_id: str,
        component_name: str,
        component_type: str,
        init_params: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        pipeline = self._pipelines.get(pipeline_id)
        if not pipeline:
            return None

        if component_type == "PromptBuilder":
            component = PromptBuilder(
                template=init_params.get("template", ""),
                required_variables=init_params.get("required_variables"),
            )
        elif component_type == "ChatPromptBuilder":
            messages = []
            for msg_data in init_params.get("template", []):
                messages.append(
                    ChatMessage(
                        role=msg_data.get("role", "user"),
                        content=msg_data.get("content", ""),
                    )
                )
            component = ChatPromptBuilder(
                template=messages,
                required_variables=init_params.get("required_variables"),
            )
        else:
            return None

        pipeline.add_component(component_name, component)
        return pipeline.to_dict()
