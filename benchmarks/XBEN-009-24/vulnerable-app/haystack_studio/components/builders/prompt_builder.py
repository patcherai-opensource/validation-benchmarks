# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Any, Dict, List, Optional, Set

from jinja2 import Environment, TemplateSyntaxError, meta

logger = logging.getLogger(__name__)


class PromptBuilder:
    """
    Renders prompt templates with provided variables using Jinja2 syntax.

    The PromptBuilder takes a template string and a set of template variables,
    renders the template, and returns the final prompt string. Variables in the
    default template are optional unless specified otherwise.

    Usage:
        builder = PromptBuilder(template="Summarize: {{ document }}")
        result = builder.run(template_variables={"document": "Some text..."})
    """

    def __init__(
        self,
        template: str,
        required_variables: Optional[List[str]] = None,
    ):
        self._template_string = template
        self.required_variables = required_variables or []
        self._env = Environment()
        self.template = self._env.from_string(template)

    def _validate_template(self, template_text: str):
        """Compile and validate a Jinja2 template string."""
        compiled = self._env.parse(template_text)
        variables = meta.find_undeclared_variables(compiled)
        return self._env.from_string(template_text), variables

    def _validate_variables(self, provided_variables: Set[str]):
        """Check that all required variables are provided."""
        missing = set(self.required_variables) - provided_variables
        if missing:
            raise ValueError(
                f"Missing required template variables: {missing}. "
                f"Provided: {provided_variables}"
            )

    def run(
        self,
        template: Optional[str] = None,
        template_variables: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, str]:
        """
        Renders the prompt template with the provided variables.

        :param template: An optional template string to override the default.
        :param template_variables: Optional dict of variables for rendering.
        :param kwargs: Additional variables for rendering.
        :returns: Dict with 'prompt' key containing the rendered prompt.
        """
        kwargs = kwargs or {}
        template_variables = template_variables or {}
        combined_vars = {**kwargs, **template_variables}
        self._validate_variables(set(combined_vars.keys()))

        compiled_template = self.template
        if template is not None:
            compiled_template, _ = self._validate_template(template)

        rendered = compiled_template.render(**combined_vars)
        return {"prompt": rendered}

    def get_template_variables(self, template_text: Optional[str] = None) -> List[str]:
        """Extract variable names from a template string."""
        text = template_text or self._template_string
        ast = self._env.parse(text)
        return list(meta.find_undeclared_variables(ast))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "haystack.components.builders.PromptBuilder",
            "init_parameters": {
                "template": self._template_string,
                "required_variables": self.required_variables,
            },
        }
