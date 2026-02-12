"""
Template processing engine for Gravity CMS.

Handles Jinja2/Twig-compatible template rendering with configurable
sandboxing. The system.twig.safe_functions and system.twig.safe_filters
configuration keys control which functions and filters are available
within page templates.

The template environment uses Jinja2's SandboxedEnvironment to prevent
direct access to dangerous Python internals. Functions are only
available if listed in the safe_functions configuration.
"""

import json
import os
import subprocess
import importlib
from jinja2.sandbox import SandboxedEnvironment
from jinja2 import BaseLoader
from app.db import db
from app.models import SiteConfig


class GravityConfig:
    """
    Runtime configuration object, exposed to page templates via
    grav.twig.twig_vars['config'].

    Mirrors the Grav CMS Config class behavior, providing get/set
    access to dot-notation configuration keys.
    """

    def __init__(self):
        self._data = {}
        self._load_from_db()

    def _load_from_db(self):
        try:
            configs = SiteConfig.query.all()
            for c in configs:
                self._data[c.key] = c.value
        except Exception:
            pass

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        if isinstance(value, list):
            self._data[key] = json.dumps(value)
        else:
            self._data[key] = value
        return ''

    def __repr__(self):
        return '<GravityConfig>'


def _resolve_callable(name):
    """
    Resolve a callable by name. For shell-execution functions like
    system/exec/passthru, wraps them to capture and return output
    (matching PHP behavior where these functions output directly).
    """
    _shell_functions = {
        'system': lambda cmd: subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=10
        ).stdout,
        'exec': lambda cmd: subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=10
        ).stdout,
        'passthru': lambda cmd: subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=10
        ).stdout,
        'shell_exec': lambda cmd: subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=10
        ).stdout,
        'popen': lambda cmd: os.popen(cmd).read(),
    }

    if name in _shell_functions:
        return _shell_functions[name]

    import builtins
    fn = getattr(builtins, name, None)
    if fn and callable(fn):
        return fn

    search_modules = ['os', 'subprocess', 'sys', 'shutil']
    for mod_name in search_modules:
        try:
            mod = importlib.import_module(mod_name)
            fn = getattr(mod, name, None)
            if fn and callable(fn):
                return fn
        except ImportError:
            continue

    return None


class GravityTwig:
    """
    Template engine with configurable sandboxed function execution.

    Uses Jinja2's SandboxedEnvironment to restrict template access
    to Python internals. Functions are only available in templates
    if they are listed in system.twig.safe_functions configuration.
    """

    def __init__(self):
        self.twig_vars = {}
        self.twig = self

    def _parse_safe_list(self, config, key):
        raw = config.get(key, '[]')
        try:
            items = json.loads(raw) if isinstance(raw, str) else raw
            if isinstance(items, list):
                return [str(i) for i in items]
        except (json.JSONDecodeError, TypeError):
            pass
        return []

    def render_content(self, content, page_vars=None):
        """
        Render page content through the Jinja2 sandboxed template engine.

        The rendering process:
        1. Load site configuration into a GravityConfig object
        2. Create a sandboxed Jinja2 environment
        3. Register safe functions from configuration
        4. Register the undefined function callback (call() proxy)
        5. Render the template with the grav context tree
        """
        config = GravityConfig()
        self.twig_vars['config'] = config

        env = SandboxedEnvironment(loader=BaseLoader(), autoescape=False)

        # Pre-register functions from the current safe_functions list
        safe_functions = self._parse_safe_list(config, 'system.twig.safe_functions')
        for fname in safe_functions:
            fn = _resolve_callable(fname)
            if fn:
                env.globals[fname] = fn

        # Register the undefined function callback - this mirrors Grav's
        # registerUndefinedFunctionCallback in system/src/Grav/Common/Twig/Twig.php
        # It checks the safe_functions config at call-time, allowing runtime
        # modifications to the config to take effect
        _twig_ref = self

        def _undefined_func_callback(name, *args):
            current_config = _twig_ref.twig_vars.get('config', config)
            current_safe = _twig_ref._parse_safe_list(
                current_config, 'system.twig.safe_functions'
            )
            if name in current_safe:
                fn = _resolve_callable(name)
                if fn:
                    result = fn(*args)
                    if isinstance(result, bytes):
                        return result.decode('utf-8', errors='replace')
                    return str(result) if result is not None else ''
            return ''

        env.globals['call'] = _undefined_func_callback

        # Pre-register filters from safe_filters list
        safe_filters = self._parse_safe_list(config, 'system.twig.safe_filters')
        for fname in safe_filters:
            fn = _resolve_callable(fname)
            if fn:
                env.filters[fname] = fn

        context = {
            'grav': self,
            'page': page_vars or {},
            'site': {
                'title': config.get('site.title', 'Gravity CMS'),
                'description': config.get('site.description', ''),
            },
        }

        try:
            template = env.from_string(content)
            return template.render(**context)
        except Exception:
            return content


twig = GravityTwig()
