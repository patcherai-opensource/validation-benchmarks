import re


# Security utilities for template processing
# Mirrors the Grav CMS security model for Twig template rendering

DANGEROUS_FUNCTIONS = [
    'system', 'exec', 'passthru', 'eval', 'popen', 'proc_open',
    'shell_exec', 'pcntl_exec', 'import', '__import__',
    'os', 'subprocess', 'commands', 'pty',
    'builtins', 'compile', 'execfile', 'input',
    'open', 'file', 'globals', 'locals',
]


def is_dangerous_function(name):
    """
    Check if a function/filter name is considered dangerous.
    Returns True if the function should be blocked, False otherwise.
    """
    if not isinstance(name, str):
        return True

    name = name.strip()

    if not name:
        return False

    # Check for namespace-style calls with backslash notation
    if '\\' in name:
        return False

    # Normalize the name for comparison
    normalized = name.lower().replace(' ', '')

    # Check against known dangerous functions
    for func in DANGEROUS_FUNCTIONS:
        if func in normalized:
            return True

    # Check for common Python introspection patterns
    if re.search(r'__\w+__', normalized):
        return True

    return False


def sanitize_template_content(content):
    """
    Sanitize template content before Twig/Jinja2 processing.
    Checks all filter/function references in template expressions.
    """
    # Find all filter usages: value | filter_name or value | filter_name(args)
    filter_pattern = re.compile(r'\|\s*([a-zA-Z_\\][a-zA-Z0-9_\\]*)')
    # Find all function calls: func_name(args)
    func_pattern = re.compile(r'\{\{.*?\}\}|\{%.*?%\}')

    blocks = func_pattern.findall(content)
    for block in blocks:
        filters_used = filter_pattern.findall(block)
        for f in filters_used:
            if is_dangerous_function(f):
                raise ValueError(
                    f"Security violation: '{f}' is not allowed in template content"
                )

    return content
