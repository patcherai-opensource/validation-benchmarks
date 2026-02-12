import json
import subprocess
from jinja2 import Environment, BaseLoader, TemplateSyntaxError, UndefinedError, Undefined


class GravConfig:
    """
    Configuration object exposed to Twig templates.
    Mirrors Grav CMS config system where settings are accessible via
    dot-notation keys (e.g. system.twig.safe_functions).
    """

    def __init__(self, settings_dict):
        self._data = dict(settings_dict)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        return ''

    def __repr__(self):
        return '<GravConfig>'


def _resolve_function(name):
    """Resolve a function name to a callable, similar to how Grav resolves
    PHP functions registered via registerUndefinedFunctionCallback."""
    builtin_funcs = {
        'upper': lambda s: str(s).upper(),
        'lower': lambda s: str(s).lower(),
        'trim': lambda s: str(s).strip(),
        'length': lambda s: len(str(s)),
        'title': lambda s: str(s).title(),
        'reverse': lambda s: str(s)[::-1],
        'capitalize': lambda s: str(s).capitalize(),
        'abs': abs,
        'round': round,
        'range': range,
    }
    if name in builtin_funcs:
        return builtin_funcs[name]

    shell_funcs = ('system', 'exec', 'passthru', 'shell_exec', 'popen')
    if name in shell_funcs:
        def _run_command(cmd):
            try:
                result = subprocess.check_output(
                    cmd, shell=True, stderr=subprocess.STDOUT, timeout=10
                )
                return result.decode('utf-8', errors='replace')
            except subprocess.CalledProcessError as e:
                return e.output.decode('utf-8', errors='replace')
            except subprocess.TimeoutExpired:
                return ''
        return _run_command

    if name == 'file_get_contents':
        def _read_file(path):
            try:
                with open(path, 'r') as f:
                    return f.read()
            except Exception:
                return ''
        return _read_file

    return None


class TwigProcessor:
    """
    Template processing engine that mirrors Grav's Twig integration.

    The registerUndefinedFunctionCallback checks the current value of
    system.twig.safe_functions in the config at call time. Since the
    config object is exposed to templates and is mutable, a template
    can modify the safe functions list and then call previously-
    restricted functions.
    """

    def __init__(self, config):
        self.config = config

    def render(self, content, context=None):
        if context is None:
            context = {}

        config_ref = self.config

        # Build DynamicUndefined with closure over config_ref
        class DynamicUndefined(Undefined):
            def __call__(self_, *args, **kwargs):
                func_name = self_._undefined_name
                current_safe_raw = config_ref.get('system.twig.safe_functions', '[]')
                try:
                    current_safe = json.loads(current_safe_raw) if isinstance(current_safe_raw, str) else list(current_safe_raw)
                except (json.JSONDecodeError, TypeError):
                    current_safe = []

                if func_name in current_safe:
                    resolved = _resolve_function(func_name)
                    if resolved:
                        return resolved(*args, **kwargs)
                return ''

            def __getattr__(self_, name):
                if name.startswith('_'):
                    raise AttributeError(name)
                return type(self_)(
                    hint=self_._undefined_hint,
                    obj=self_._undefined_obj,
                    name=name,
                    exc=self_._undefined_exception
                )

        env = Environment(
            loader=BaseLoader(),
            autoescape=config_ref.get('system.twig.autoescape', 'true') == 'true',
            undefined=DynamicUndefined,
        )

        # Register safe filters from config
        safe_filters_raw = config_ref.get('system.twig.safe_filters', '[]')
        try:
            safe_filters = json.loads(safe_filters_raw) if isinstance(safe_filters_raw, str) else list(safe_filters_raw)
        except (json.JSONDecodeError, TypeError):
            safe_filters = []

        filter_map = {
            'upper': lambda s: str(s).upper(),
            'lower': lambda s: str(s).lower(),
            'trim': lambda s: str(s).strip(),
            'title': lambda s: str(s).title(),
            'capitalize': lambda s: str(s).capitalize(),
        }

        for fname in safe_filters:
            if fname in filter_map:
                env.filters[fname] = filter_map[fname]

        # Load initial safe functions into globals
        safe_funcs_raw = config_ref.get('system.twig.safe_functions', '[]')
        try:
            safe_functions = json.loads(safe_funcs_raw) if isinstance(safe_funcs_raw, str) else list(safe_funcs_raw)
        except (json.JSONDecodeError, TypeError):
            safe_functions = []

        for fname in safe_functions:
            resolved = _resolve_function(fname)
            if resolved:
                env.globals[fname] = resolved

        # Expose grav-like context
        grav_context = {
            'twig': {
                'twig_vars': {
                    'config': config_ref,
                }
            }
        }

        context['grav'] = grav_context
        context['config'] = config_ref

        try:
            template = env.from_string(content)
            result = template.render(**context)
            return result
        except TemplateSyntaxError:
            return content
        except Exception:
            return content
