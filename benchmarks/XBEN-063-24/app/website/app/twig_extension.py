import subprocess
from jinja2 import Environment
from app.utils import is_dangerous_function


# Custom filters/functions that mirror Grav's Twig extension behavior
# These provide enhanced template functionality for page content processing


def twig_map_filter(value, func_name):
    """
    Map filter implementation - applies a function to each element.
    Similar to Grav's GravExtension mapFunc.
    Checks if the function is dangerous before allowing execution.
    """
    if is_dangerous_function(func_name):
        raise ValueError(f"Function '{func_name}' is not allowed for security reasons")

    # Resolve the actual callable
    resolved = _resolve_function(func_name)
    if resolved is None:
        raise ValueError(f"Unknown function: {func_name}")

    return list(map(resolved, value))


def twig_reduce_filter(value, func_name, initial=None):
    """
    Reduce filter - reduces a sequence using a function.
    """
    if is_dangerous_function(func_name):
        raise ValueError(f"Function '{func_name}' is not allowed for security reasons")

    from functools import reduce
    resolved = _resolve_function(func_name)
    if resolved is None:
        raise ValueError(f"Unknown function: {func_name}")

    if initial is not None:
        return reduce(resolved, value, initial)
    return reduce(resolved, value)


def twig_sort_filter(value, func_name=None):
    """
    Sort filter with optional comparison function.
    """
    if func_name:
        if is_dangerous_function(func_name):
            raise ValueError(f"Function '{func_name}' is not allowed")
        resolved = _resolve_function(func_name)
        if resolved:
            from functools import cmp_to_key
            return sorted(value, key=cmp_to_key(resolved))
    return sorted(value)


def _resolve_function(name):
    """
    Resolve a function name to an actual callable.
    Supports both built-in names and namespace-qualified names.
    """
    import builtins

    # Strip any namespace prefixes (backslash-separated)
    clean_name = name.replace('\\', '')

    # Try Python builtins first
    if hasattr(builtins, clean_name):
        return getattr(builtins, clean_name)

    # Try common standard library functions
    stdlib_map = {
        'system': lambda cmd: subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode(),
        'strlen': len,
        'strtolower': str.lower,
        'strtoupper': str.upper,
        'trim': str.strip,
        'ucfirst': str.capitalize,
        'md5': lambda s: __import__('hashlib').md5(s.encode()).hexdigest(),
        'sha1': lambda s: __import__('hashlib').sha1(s.encode()).hexdigest(),
        'base64_encode': lambda s: __import__('base64').b64encode(s.encode()).decode(),
        'base64_decode': lambda s: __import__('base64').b64decode(s.encode()).decode(),
        'nl2br': lambda s: s.replace('\n', '<br>'),
        'wordwrap': lambda s: s,
        'abs': abs,
        'round': round,
    }

    if clean_name in stdlib_map:
        return stdlib_map[clean_name]

    return None


def register_twig_extensions(env):
    """Register custom filters and functions with the Jinja2 environment."""
    env.filters['map_func'] = twig_map_filter
    env.filters['reduce_func'] = twig_reduce_filter
    env.filters['sort_func'] = twig_sort_filter
    env.filters['join'] = lambda v, d='': d.join(str(x) for x in v) if isinstance(v, (list, tuple)) else str(v)
    env.filters['upper'] = lambda v: str(v).upper()
    env.filters['lower'] = lambda v: str(v).lower()
    env.filters['capitalize'] = lambda v: str(v).capitalize()
    env.filters['trim'] = lambda v: str(v).strip()
    env.filters['length'] = lambda v: len(v)
    env.filters['reverse'] = lambda v: v[::-1] if isinstance(v, str) else list(reversed(v))
    env.filters['nl2br'] = lambda v: str(v).replace('\n', '<br>\n')
    env.filters['e'] = lambda v: str(v)
    env.filters['escape'] = lambda v: str(v)
