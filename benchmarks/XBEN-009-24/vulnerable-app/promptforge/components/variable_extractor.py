"""
VariableExtractor analyzes Jinja2 template strings to discover variables.

This utility component is used in the pipeline to validate templates before
rendering, ensuring all required variables are available.
"""

from typing import List, Set

from jinja2 import Environment, TemplateSyntaxError, meta


class VariableExtractor:
    """
    VariableExtractor parses a Jinja2 template string and extracts all undeclared
    variables. This is useful for building UIs that can prompt users for required
    variable values.
    """

    def __init__(self):
        self._env = Environment()

    def extract(self, template_text: str) -> List[str]:
        """
        Extracts variable names from a Jinja2 template string.

        :param template_text: A Jinja2 template string.
        :returns: A sorted list of variable names found in the template.
        :raises ValueError: If the template syntax is invalid.
        """
        try:
            ast = self._env.parse(template_text)
        except TemplateSyntaxError as e:
            raise ValueError(f"Invalid template syntax: {e}")
        variables: Set[str] = meta.find_undeclared_variables(ast)
        return sorted(variables)

    def validate_syntax(self, template_text: str) -> bool:
        """
        Checks if a template string has valid Jinja2 syntax.

        :param template_text: A Jinja2 template string.
        :returns: True if valid, False otherwise.
        """
        try:
            self._env.parse(template_text)
            return True
        except TemplateSyntaxError:
            return False
