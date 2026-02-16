"""
Content security validation for template processing.

Validates that user-supplied template content does not contain
calls to dangerous Python functions or modules. This check is applied
before any template string is rendered through the Jinja2 engine.
"""

import re
import builtins


# Functions that allow arbitrary command execution
BLOCKED_EXEC_FUNCTIONS = [
    'exec',
    'eval',
    'execfile',
    'compile',
    '__import__',
]

# Functions that allow OS-level command execution
BLOCKED_SYSTEM_FUNCTIONS = [
    'system',
    'popen',
    'popen2',
    'popen3',
    'popen4',
    'fdopen',
    'tmpfile',
    'fchmod',
    'fchown',
    'subprocess',
]

# Functions that allow reading filesystem or process data
BLOCKED_IO_FUNCTIONS = [
    'open',
    'file',
    'input',
    'raw_input',
]

# Functions that allow introspection
BLOCKED_INTROSPECTION_FUNCTIONS = [
    'getattr',
    'setattr',
    'delattr',
    'globals',
    'locals',
    'vars',
    'dir',
    'type',
    'reload',
]

# Dangerous module references
BLOCKED_MODULES = [
    'os',
    'subprocess',
    'sys',
    'importlib',
    'builtins',
    'shutil',
    'signal',
    'socket',
    'ctypes',
    'code',
    'codeop',
    'compileall',
    'commands',
    'pty',
    'posix',
]

# Dangerous class/attribute access patterns
BLOCKED_ATTRIBUTES = [
    '__class__',
    '__bases__',
    '__subclasses__',
    '__mro__',
    '__globals__',
    '__builtins__',
    '__init__',
    '__dict__',
    '__getattribute__',
    '__import__',
    '_module',
    '__code__',
    '__func__',
    '__self__',
    '__wrapped__',
]


def is_restricted_callable(name):
    """
    Check if a callable name appears in the blocked lists.
    Returns True if the callable is considered dangerous.
    """
    if not isinstance(name, str):
        return False

    name = name.strip()

    if name in BLOCKED_EXEC_FUNCTIONS:
        return True

    if name in BLOCKED_SYSTEM_FUNCTIONS:
        return True

    if name in BLOCKED_IO_FUNCTIONS:
        return True

    if name in BLOCKED_INTROSPECTION_FUNCTIONS:
        return True

    return False


def check_template_safety(content):
    """
    Validate template content for dangerous patterns before rendering.
    Returns dict with 'safe' boolean and optional 'reason' string.
    """
    if not content:
        return {'safe': True}

    # Check for blocked attribute access patterns
    for attr in BLOCKED_ATTRIBUTES:
        if attr in content:
            return {
                'safe': False,
                'reason': f'Access to "{attr}" is not permitted in template content'
            }

    # Check for dangerous module references in template expressions
    for module in BLOCKED_MODULES:
        pattern = r"(?:import\s+|from\s+)" + re.escape(module)
        if re.search(pattern, content):
            return {
                'safe': False,
                'reason': f'Module "{module}" is not permitted in template content'
            }

    # Scan for function calls within template expression blocks
    template_expr = re.findall(r'\{\{(.*?)\}\}|\{%(.*?)%\}', content, re.DOTALL)
    for groups in template_expr:
        for expr in groups:
            if not expr:
                continue

            # Extract function-like calls: word followed by (
            func_calls = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', expr)
            for func_name in func_calls:
                if is_restricted_callable(func_name):
                    return {
                        'safe': False,
                        'reason': f'Function "{func_name}" is not permitted in template content'
                    }

            # Check pipe filter usage with dangerous function names
            filter_calls = re.findall(
                r'\|\s*(?:apply_func|transform_each|filter|map|reject|select)\s*\(\s*[\'"]([a-zA-Z_][a-zA-Z0-9_.]*)[\'"]',
                expr
            )
            for func_name in filter_calls:
                if is_restricted_callable(func_name):
                    return {
                        'safe': False,
                        'reason': f'Function "{func_name}" is not permitted as a filter callback'
                    }

    return {'safe': True}
