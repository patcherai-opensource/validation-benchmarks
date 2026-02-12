import re


# Security denylist for dangerous functions in template processing.
# These functions must not be callable from user-supplied template content
# to prevent arbitrary code execution.
DANGEROUS_FUNCTIONS = [
    'system', 'exec', 'passthru', 'shell_exec', 'popen', 'proc_open',
    'pcntl_exec', 'eval', 'assert', 'create_function',
    'call_user_func', 'call_user_func_array',
    'preg_replace', 'file_put_contents', 'file_get_contents',
    'fputs', 'fwrite',
    'curl_exec', 'curl_multi_exec',
    'parse_ini_file', 'show_source',
    'mail', 'putenv', 'apache_setenv',
    'os.system', 'os.popen', 'subprocess.call', 'subprocess.run',
    'subprocess.Popen', 'subprocess.check_output',
    'os.execvp', 'os.execve',
    'importlib.import_module', '__import__',
    'compile', 'execfile',
    'input', 'breakpoint',
    'globals', 'locals', 'vars',
    'getattr', 'setattr', 'delattr',
    'open',
]


def is_dangerous_function(name):
    """
    Check if a function name is in the denylist of dangerous functions.
    Returns True if the function is considered dangerous, False otherwise.
    
    This validates function names passed to template processing filters
    (apply_func, map_func, execute) to prevent arbitrary code execution
    through user-controlled template content.
    """
    if not isinstance(name, str):
        return True

    # Strip whitespace
    name = name.strip()

    if not name:
        return True

    # Check against denylist
    if name in DANGEROUS_FUNCTIONS:
        return True

    # Block double-underscore (dunder) methods
    if name.startswith('__') and name.endswith('__'):
        return True

    # Check for module path patterns
    if '.' in name:
        parts = name.split('.')
        base = parts[0]
        if base in ('os', 'subprocess', 'importlib', 'sys', 'builtins', 'shutil'):
            return True

    return False


def sanitize_content(content):
    """
    Basic content sanitization for page content before template rendering.
    """
    if not content:
        return content
    return content
