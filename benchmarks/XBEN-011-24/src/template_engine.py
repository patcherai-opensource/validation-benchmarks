"""
Simple template engine with Smarty-like syntax.
Supports variable interpolation with modifiers:
  {$varname}                    - raw output
  {$varname|escape:"html"}      - HTML entity escaping
  {$varname|escape:"javascript"} - JavaScript string escaping
  {$varname|escape:"url"}       - URL encoding
  {$varname|upper}              - uppercase
  {$varname|lower}              - lowercase
  {$varname|truncate:N}         - truncate to N chars
"""

import re
import html
import urllib.parse


class TemplateEngine:

    # Pattern: {$variable_name} or {$variable_name|modifier:"arg"} or chained
    _VAR_PATTERN = re.compile(
        r'\{\$([a-zA-Z_][a-zA-Z0-9_]*)((?:\|[a-zA-Z_]+(?::["\']?[^}]*?["\']?)?)*)\}'
    )

    def render(self, source, variables):
        """Render template source with the given variable dict."""
        def replace_var(match):
            var_name = match.group(1)
            modifiers_str = match.group(2)
            value = variables.get(var_name, '')
            if not isinstance(value, str):
                value = str(value)
            if modifiers_str:
                value = self._apply_modifiers(value, modifiers_str)
            return value

        return self._VAR_PATTERN.sub(replace_var, source)

    def _apply_modifiers(self, value, modifiers_str):
        """Parse and apply modifier chain like |escape:"html"|upper"""
        # Split on | but skip the first empty element
        parts = modifiers_str.split('|')[1:]
        for part in parts:
            if ':' in part:
                mod_name, mod_arg = part.split(':', 1)
                mod_arg = mod_arg.strip('"').strip("'")
            else:
                mod_name = part.strip()
                mod_arg = None
            value = self._apply_single_modifier(value, mod_name, mod_arg)
        return value

    def _apply_single_modifier(self, value, modifier, arg):
        if modifier == 'escape':
            return self._escape(value, arg or 'html')
        elif modifier == 'upper':
            return value.upper()
        elif modifier == 'lower':
            return value.lower()
        elif modifier == 'truncate':
            try:
                n = int(arg) if arg else 80
                return value[:n] + ('...' if len(value) > n else '')
            except ValueError:
                return value
        elif modifier == 'nl2br':
            return value.replace('\n', '<br />\n')
        elif modifier == 'strip_tags':
            return re.sub(r'<[^>]+>', '', value)
        elif modifier == 'count':
            return str(len(value))
        else:
            return value

    def _escape(self, value, escape_type):
        """Escape value based on type.

        Supported types:
          html       - HTML entity encoding
          htmlall    - HTML entity encoding (all characters)
          url        - URL percent encoding
          urlpathinfo - URL path encoding
          quotes     - escape single/double quotes
          javascript - JavaScript string escaping
        """
        if escape_type == 'html':
            return html.escape(value, quote=True)

        elif escape_type == 'htmlall':
            return ''.join('&#{};'.format(ord(c)) for c in value)

        elif escape_type == 'url':
            return urllib.parse.quote(value, safe='')

        elif escape_type == 'urlpathinfo':
            return urllib.parse.quote(value, safe='/')

        elif escape_type == 'quotes':
            return value.replace("'", "\\'").replace('"', '\\"')

        elif escape_type == 'javascript':
            return self._escape_javascript(value)

        else:
            return html.escape(value, quote=True)

    def _escape_javascript(self, value):
        """JavaScript string escaping — mirrors Smarty's modifier.escape.php
        implementation for the 'javascript' escape type.

        Escapes characters that are dangerous in JavaScript string contexts
        using the strtr()-equivalent character mapping.
        """
        replacements = {
            '\\': '\\\\',
            "'": "\\'",
            '"': '\\"',
            '\r': '\\r',
            '\n': '\\n',
            '<': '\\u003C',
            '>': '\\u003E',
            '&': '\\u0026',
            '/': '\\/',
        }
        result = []
        for ch in value:
            if ch in replacements:
                result.append(replacements[ch])
            else:
                result.append(ch)
        return ''.join(result)
