"""
Expression evaluation engine.

Uses the asteval library to provide safe mathematical expression evaluation.
The asteval interpreter restricts Python to a safe subset suitable for
mathematical computations - no imports, no exec/eval, no class definitions.
"""
import io
import time
from asteval import Interpreter


# Maximum allowed expression length
MAX_EXPR_LENGTH = 50000

# Maximum execution time in seconds
MAX_EXEC_TIME = 10


class EvaluationResult:
    """Container for evaluation results."""

    def __init__(self, value=None, output=None, error=None, elapsed=None):
        self.value = value
        self.output = output
        self.error = error
        self.elapsed = elapsed

    def to_dict(self):
        result = {}
        if self.value is not None:
            result['result'] = str(self.value)
        if self.output:
            result['output'] = self.output
        if self.error:
            result['error'] = self.error
        if self.elapsed is not None:
            result['elapsed_ms'] = round(self.elapsed * 1000, 2)
        return result


class ComputeSession:
    """
    A computation session that maintains state across evaluations.
    Users can define variables and functions that persist within a session.
    """

    def __init__(self, session_id=None):
        self.session_id = session_id
        self._writer = io.StringIO()
        self._interpreter = Interpreter(
            writer=self._writer,
            use_numpy=False,
            max_statement_length=MAX_EXPR_LENGTH,
        )
        # Remove file I/O functions - not needed for mathematical computation
        for fn_name in ('open', '_open'):
            self._interpreter.symtable.pop(fn_name, None)
        self._created = time.time()

    def evaluate(self, expression):
        """Evaluate a mathematical expression or statement."""
        if not expression or not expression.strip():
            return EvaluationResult(error='Empty expression')

        if len(expression) > MAX_EXPR_LENGTH:
            return EvaluationResult(
                error=f'Expression exceeds maximum length of {MAX_EXPR_LENGTH} characters'
            )

        self._writer.truncate(0)
        self._writer.seek(0)

        start = time.time()
        result = self._interpreter(expression)
        elapsed = time.time() - start

        output = self._writer.getvalue()

        errors = self._interpreter.error
        if errors:
            error_msgs = []
            for err in errors:
                error_msgs.append(str(err.get_error()[1]))
            self._interpreter.error = []
            return EvaluationResult(
                error='; '.join(error_msgs),
                output=output if output else None,
                elapsed=elapsed
            )

        return EvaluationResult(
            value=result,
            output=output if output else None,
            elapsed=elapsed
        )

    def get_symbols(self):
        """Return user-defined symbols in the session."""
        from asteval import make_symbol_table
        defaults = set(make_symbol_table().keys())
        defaults.update(['open', '_open'])
        return {
            k: str(type(v).__name__)
            for k, v in self._interpreter.symtable.items()
            if k not in defaults and not k.startswith('_')
        }

    def reset(self):
        """Reset the session to initial state."""
        self._writer = io.StringIO()
        self._interpreter = Interpreter(
            writer=self._writer,
            use_numpy=False,
            max_statement_length=MAX_EXPR_LENGTH,
        )
        for fn_name in ('open', '_open'):
            self._interpreter.symtable.pop(fn_name, None)


# Session pool for concurrent users
_sessions = {}
_max_sessions = 256


def get_session(session_id):
    """Get or create a computation session."""
    if session_id not in _sessions:
        if len(_sessions) >= _max_sessions:
            oldest_key = min(_sessions, key=lambda k: _sessions[k]._created)
            del _sessions[oldest_key]
        _sessions[session_id] = ComputeSession(session_id=session_id)
    return _sessions[session_id]


def remove_session(session_id):
    """Remove a computation session."""
    _sessions.pop(session_id, None)
