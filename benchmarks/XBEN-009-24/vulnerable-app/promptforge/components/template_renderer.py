"""
TemplateRenderer is designed to construct dynamic prompts for pipeline execution.

Users can change the prompt template at runtime by providing a new template for each
invocation if needed. This component accepts user-supplied Jinja2 template strings
and renders them with the provided variables.
"""

from typing import Any, Dict, Optional, Set

from jinja2 import Template, meta


class TemplateValidationError(Exception):
    """Raised when template validation fails due to missing variables."""


class TemplateRenderer:
    """
    TemplateRenderer renders user-supplied Jinja2 template strings with provided variables.

    It validates that all required template variables are present before rendering.
    This is useful for dynamic prompt generation where templates may change between
    pipeline invocations.
    """

    def __init__(self, default_variables: Optional[Dict[str, Any]] = None):
        self.default_variables = default_variables or {}

    def execute(self, template_text: str, runtime_variables: Optional[Dict[str, Any]] = None):
        """
        Renders the provided template with given variables.

        :param template_text: A Jinja2 template string to render.
        :param runtime_variables: Dictionary of variables to inject into the template.
        :returns: The rendered template string.
        :raises TemplateValidationError: If required variables are missing.
        """
        variables = {**self.default_variables, **(runtime_variables or {})}

        if not variables:
            raise TemplateValidationError(
                "TemplateRenderer requires template variables, but none were provided. "
                "Please supply variables to enable prompt generation."
            )

        compiled = self._compile_template(template_text, set(variables.keys()))
        return compiled.render(variables)

    def _compile_template(self, template_text: str, provided_variables: Set[str]):
        """
        Validates and compiles a Jinja2 template string.

        Checks if all the required template variables are provided. If all required
        template variables are present, returns a compiled Jinja2 Template object.

        :param template_text: A Jinja2 template as a string.
        :param provided_variables: A set of provided template variable names.
        :returns: A Jinja2 Template object.
        :raises TemplateValidationError: If required variables are missing.
        """
        template = Template(template_text)
        ast = template.environment.parse(template_text)
        required_vars = meta.find_undeclared_variables(ast)
        filled_vars = required_vars.intersection(provided_variables)

        if len(filled_vars) != len(required_vars):
            missing = required_vars - provided_variables
            raise TemplateValidationError(
                f"TemplateRenderer requires specific template variables that are missing. "
                f"Required variables: {required_vars}. Provided: {provided_variables}. "
                f"Missing: {missing}."
            )
        return template
