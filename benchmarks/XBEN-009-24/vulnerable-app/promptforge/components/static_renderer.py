"""
StaticRenderer is designed for rendering pre-configured prompt templates.

Unlike TemplateRenderer which accepts dynamic template strings at runtime,
StaticRenderer uses a fixed template configured at initialization. This provides
a more constrained approach to prompt rendering.
"""

from typing import Any, Dict, List, Optional, Set

from jinja2 import meta
from jinja2.sandbox import SandboxedEnvironment


class StaticRenderer:
    """
    StaticRenderer renders a pre-configured Jinja2 template with provided variables.

    The template is fixed at initialization and cannot be changed at runtime.
    Variables can be provided at render time to fill in template placeholders.
    """

    def __init__(self, template: str, required_variables: Optional[List[str]] = None):
        self._template_string = template
        self.required_variables = required_variables or []

        self._env = SandboxedEnvironment()
        self.template = self._env.from_string(template)

        ast = self._env.parse(template)
        self._discovered_variables = list(meta.find_undeclared_variables(ast))

    def execute(self, template_variables: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Renders the static template with provided variables.

        :param template_variables: Optional dictionary of template variables.
        :param kwargs: Additional variables provided as keyword arguments.
        :returns: The rendered template string.
        """
        variables = {**kwargs, **(template_variables or {})}
        self._check_required(set(variables.keys()))
        return self.template.render(variables)

    def get_variables(self):
        """Returns the list of discovered template variables."""
        return self._discovered_variables

    def _check_required(self, provided: Set[str]):
        """Validates that all required variables are present."""
        missing = [v for v in self.required_variables if v not in provided]
        if missing:
            raise ValueError(
                f"Missing required variables in StaticRenderer: {', '.join(missing)}. "
                f"Required: {self.required_variables}. Provided: {provided}."
            )
