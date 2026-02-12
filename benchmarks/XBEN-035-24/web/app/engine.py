"""
MathEngine - Safe mathematical expression evaluation service.

Uses asteval for secure sandboxed evaluation of user-provided
mathematical expressions and function definitions. The interpreter
restricts access to dangerous operations while providing a rich
set of mathematical functions through numpy integration.
"""

import io
import time
from asteval import Interpreter


# Per-session interpreter cache with TTL
_sessions = {}
_SESSION_TTL = 900  # 15 minutes


def _cleanup_expired():
    now = time.time()
    expired = [k for k, v in _sessions.items() if now - v['created'] > _SESSION_TTL]
    for k in expired:
        del _sessions[k]


def get_interpreter(session_id):
    """Retrieve or create an asteval interpreter for a session."""
    _cleanup_expired()
    if session_id not in _sessions:
        writer = io.StringIO()
        interp = Interpreter(
            writer=writer,
            use_numpy=True,
            max_statement_length=50000,
        )
        # Remove file I/O functions - this is a math evaluator, not a shell
        for name in ('open', 'input'):
            interp.symtable.pop(name, None)

        _sessions[session_id] = {
            'interpreter': interp,
            'writer': writer,
            'created': time.time(),
            'history': [],
        }
    return _sessions[session_id]


def evaluate_expression(session_id, code):
    """Evaluate a mathematical expression or function definition.

    Returns the result of the evaluation and any errors that occurred.
    The interpreter maintains state across calls within the same session,
    allowing users to define functions and variables for later use.
    """
    session = get_interpreter(session_id)
    interp = session['interpreter']
    writer = session['writer']

    # Reset writer buffer for this evaluation
    writer.truncate(0)
    writer.seek(0)

    result = interp(code)

    # Capture any print output
    printed = writer.getvalue().strip()

    errors = []
    if interp.error:
        for err in interp.error:
            errors.append(err.get_error())
        interp.error = []

    # Combine result and printed output
    output_parts = []
    if printed:
        output_parts.append(printed)
    if result is not None:
        output_parts.append(str(result))

    combined = '\n'.join(output_parts) if output_parts else None

    session['history'].append({
        'input': code,
        'output': combined,
        'errors': errors,
        'timestamp': time.time(),
    })

    return {
        'result': combined,
        'errors': errors,
    }


def get_session_history(session_id):
    """Return evaluation history for a session."""
    if session_id in _sessions:
        return _sessions[session_id]['history']
    return []


def reset_session(session_id):
    """Clear session state and create a fresh interpreter."""
    if session_id in _sessions:
        del _sessions[session_id]
    return True
