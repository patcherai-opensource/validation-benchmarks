# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Any, Dict, List, Optional

from jinja2 import Environment, meta

logger = logging.getLogger(__name__)


class ChatMessage:
    """Minimal ChatMessage implementation for prompt building."""

    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}

    @classmethod
    def from_user(cls, content: str) -> "ChatMessage":
        return cls(role="user", content=content)

    @classmethod
    def from_system(cls, content: str) -> "ChatMessage":
        return cls(role="system", content=content)

    @classmethod
    def from_assistant(cls, content: str) -> "ChatMessage":
        return cls(role="assistant", content=content)


class ChatPromptBuilder:
    """
    Renders chat prompt templates from a list of ChatMessage objects.

    Each message's content is treated as a Jinja2 template and rendered
    with the provided variables.

    Usage:
        messages = [ChatMessage.from_user("Tell me about {{ topic }}")]
        builder = ChatPromptBuilder(template=messages)
        result = builder.run(template_variables={"topic": "Berlin"})
    """

    def __init__(
        self,
        template: Optional[List[ChatMessage]] = None,
        required_variables: Optional[List[str]] = None,
    ):
        self._template = template or []
        self.required_variables = required_variables or []
        self._env = Environment()

    def _validate_template(self, template_text: str):
        """Compile and validate a Jinja2 template string."""
        compiled = self._env.parse(template_text)
        variables = meta.find_undeclared_variables(compiled)
        return self._env.from_string(template_text), variables

    def run(
        self,
        template: Optional[List[ChatMessage]] = None,
        template_variables: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, List[Dict[str, str]]]:
        """
        Renders chat prompt messages with provided variables.

        :param template: Optional list of ChatMessage to override default.
        :param template_variables: Variables for rendering.
        :returns: Dict with 'prompt' key containing rendered messages.
        """
        template_variables = template_variables or {}
        combined_vars = {**kwargs, **template_variables}
        messages = template if template is not None else self._template

        rendered_messages = []
        for msg in messages:
            compiled, _ = self._validate_template(msg.content)
            rendered_content = compiled.render(**combined_vars)
            rendered_messages.append({"role": msg.role, "content": rendered_content})

        return {"prompt": rendered_messages}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "haystack.components.builders.ChatPromptBuilder",
            "init_parameters": {
                "template": [m.to_dict() for m in self._template],
                "required_variables": self.required_variables,
            },
        }
