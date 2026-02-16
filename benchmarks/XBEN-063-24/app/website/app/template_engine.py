"""
Template processing engine for page content rendering.
Provides a sandboxed Jinja2 environment with custom filters
for dynamic content generation.
"""

import importlib
from jinja2 import Environment, BaseLoader, TemplateSyntaxError, UndefinedError
from markupsafe import Markup

from app.security import is_blocked_callable


def _resolve_callable(name):
    """Resolve a string callable name to an actual Python callable."""
    clean = name.replace('\\', '')

    if '.' in clean:
        parts = clean.rsplit('.', 1)
        try:
            mod = importlib.import_module(parts[0])
            return getattr(mod, parts[1])
        except (ImportError, AttributeError):
            return None
    else:
        import builtins
        return getattr(builtins, clean, None)


def _apply_filter(items, func_name):
    """
    Custom filter that applies a named function to each element
    in the provided iterable. Validates the function name against
    the security blocklist before execution.
    """
    if not isinstance(func_name, str):
        raise ValueError('Function argument must be a string identifier')

    if is_blocked_callable(func_name):
        raise RuntimeError(
            'Function "' + func_name + '" is not permitted in template context'
        )

    fn = _resolve_callable(func_name)
    if fn is None:
        raise RuntimeError('Unable to resolve function: ' + func_name)

    if isinstance(items, (list, tuple)):
        return [fn(item) for item in items]
    else:
        return fn(items)


def _join_filter(items, separator=''):
    """Join iterable items into a string."""
    if isinstance(items, (list, tuple)):
        return separator.join(str(i) for i in items)
    return str(items)


def _upper_filter(value):
    return str(value).upper()


def _lower_filter(value):
    return str(value).lower()


def _trim_filter(value):
    return str(value).strip()


def _length_filter(value):
    return len(value)


def _default_filter(value, default_value=''):
    if value is None or (isinstance(value, str) and not value.strip()):
        return default_value
    return value


def _date_filter(value, fmt='%Y-%m-%d'):
    try:
        return value.strftime(fmt)
    except Exception:
        return str(value)


def render_page_content(content, context=None):
    """
    Render page content through the template engine with
    sandboxed filters and context variables.
    """
    if context is None:
        context = {}

    env = Environment(loader=BaseLoader(), autoescape=False)

    env.filters['apply'] = _apply_filter
    env.filters['join'] = _join_filter
    env.filters['upper'] = _upper_filter
    env.filters['lower'] = _lower_filter
    env.filters['trim'] = _trim_filter
    env.filters['length'] = _length_filter
    env.filters['default'] = _default_filter
    env.filters['date'] = _date_filter

    try:
        template = env.from_string(content)
        return template.render(**context)
    except TemplateSyntaxError as e:
        return '<p class="text-danger">Template syntax error: ' + str(e.message) + '</p>'
    except UndefinedError as e:
        return '<p class="text-danger">Template variable error: ' + str(e.message) + '</p>'
    except RuntimeError as e:
        return '<p class="text-danger">Template processing error: ' + str(e) + '</p>'
    except Exception:
        return '<p class="text-danger">An error occurred while processing the template.</p>'
