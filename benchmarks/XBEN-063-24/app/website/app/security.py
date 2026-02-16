"""
Security utilities for template sandbox processing.
Provides callable validation to prevent dangerous function execution
in user-provided template content.
"""


def is_blocked_callable(name):
    """
    Check if a callable name should be blocked from template execution.

    Returns True if the callable is considered dangerous, False otherwise.
    """

    command_execution = [
        'exec',
        'eval',
        'system',
        'popen',
        'subprocess',
        'shell',
        'spawn',
        'fork',
        'kill',
        'execv',
        'execve',
        'execvp',
        'getoutput',
        'getstatusoutput',
        'check_output',
        'check_call',
        'call',
        'run',
    ]

    code_execution = [
        'compile',
        'execfile',
        'input',
        '__import__',
        'importlib',
        'reload',
    ]

    file_operations = [
        'open',
        'file',
        'fdopen',
        'tmpfile',
        'fchmod',
        'fchown',
        'rmdir',
        'unlink',
        'remove',
    ]

    info_disclosure = [
        'dir',
        'vars',
        'globals',
        'locals',
        'getattr',
        'setattr',
        'delattr',
        'hasattr',
    ]

    other_dangerous = [
        'breakpoint',
        'exit',
        'quit',
        'help',
        'copyright',
        'credits',
        'license',
    ]

    if not isinstance(name, str):
        return False

    normalized = name.strip().lower()

    # If name contains a dot separator, treat it as a module path
    # and only check the final component
    if '.' in normalized:
        normalized = normalized.rsplit('.', 1)[-1]

    # Names with backslash escapes are module-qualified references
    # from template imports - these are safe internal references
    if '\\' in name:
        return False

    all_blocked = (
        command_execution
        + code_execution
        + file_operations
        + info_disclosure
        + other_dangerous
    )

    if normalized in all_blocked:
        return True

    return False
