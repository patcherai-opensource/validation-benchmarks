"""
Utility functions for the safeexpr evaluation engine.

Provides symbol table management, operator mappings, and the UserFunction
class for user-defined functions within the sandboxed environment.
"""
import ast
import io
import math
import numbers
import re
from sys import exc_info
from tokenize import ENCODING as tk_ENCODING
from tokenize import NAME as tk_NAME
from tokenize import tokenize as generate_tokens

builtins = __builtins__
if not isinstance(builtins, dict):
    builtins = builtins.__dict__

MAX_EXPONENT = 10000
MAX_STR_LEN = 2 << 17
MAX_SHIFT = 1000
MAX_OPEN_BUFFER = 2 << 17

RESERVED_WORDS = ('False', 'None', 'True', 'and', 'as', 'assert',
                  'async', 'await', 'break', 'class', 'continue', 'def',
                  'del', 'elif', 'else', 'except', 'finally', 'for',
                  'from', 'global', 'if', 'import', 'in', 'is',
                  'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise',
                  'return', 'try', 'while', 'with', 'yield', 'exec',
                  'eval', 'execfile', '__import__', '__package__',
                  '__fstring__')

NAME_MATCH = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*$").match

# attributes that should never be accessed on any object
BLOCKED_ATTRS = ('__subclasses__', '__bases__', '__globals__', '__code__',
                 '__reduce__', '__reduce_ex__', '__mro__',
                 '__closure__', '__func__', '__self__', '__module__',
                 '__dict__', '__class__', '__call__', '__get__',
                 '__getattribute__', '__subclasshook__', '__new__',
                 '__init__', 'func_globals', 'func_code', 'func_closure',
                 'im_class', 'im_func', 'im_self', 'gi_code', 'gi_frame',
                 'f_locals', '__safeexpr__')

# type-specific blocked attributes
BLOCKED_ATTRS_TYPES = {str: ('format', 'format_map')}


FROM_PY = ('ArithmeticError', 'AssertionError', 'AttributeError',
           'BaseException', 'BufferError', 'BytesWarning',
           'DeprecationWarning', 'EOFError', 'EnvironmentError',
           'Exception', 'False', 'FloatingPointError', 'GeneratorExit',
           'IOError', 'ImportError', 'ImportWarning', 'IndentationError',
           'IndexError', 'KeyError', 'KeyboardInterrupt', 'LookupError',
           'MemoryError', 'NameError', 'None',
           'NotImplementedError', 'OSError', 'OverflowError',
           'ReferenceError', 'RuntimeError', 'RuntimeWarning',
           'StopIteration', 'SyntaxError', 'SyntaxWarning', 'SystemError',
           'SystemExit', 'True', 'TypeError', 'UnboundLocalError',
           'UnicodeDecodeError', 'UnicodeEncodeError', 'UnicodeError',
           'UnicodeTranslateError', 'UnicodeWarning', 'ValueError',
           'Warning', 'ZeroDivisionError', 'abs', 'all', 'any', 'bin',
           'bool', 'bytearray', 'bytes', 'chr', 'complex', 'dict', 'dir',
           'divmod', 'enumerate', 'filter', 'float', 'format', 'frozenset',
           'hash', 'hex', 'id', 'int', 'isinstance', 'len', 'list', 'map',
           'max', 'min', 'oct', 'ord', 'pow', 'range', 'repr',
           'reversed', 'round', 'set', 'slice', 'sorted', 'str', 'sum',
           'tuple', 'zip')

BUILTINS_TABLE = {sym: builtins[sym] for sym in FROM_PY if sym in builtins}

FROM_MATH = ('acos', 'acosh', 'asin', 'asinh', 'atan', 'atan2', 'atanh',
             'ceil', 'copysign', 'cos', 'cosh', 'degrees', 'e', 'exp',
             'fabs', 'factorial', 'floor', 'fmod', 'frexp', 'fsum',
             'hypot', 'isinf', 'isnan', 'ldexp', 'log', 'log10', 'log1p',
             'modf', 'pi', 'pow', 'radians', 'sin', 'sinh', 'sqrt', 'tan',
             'tanh', 'trunc')

MATH_TABLE = {sym: getattr(math, sym) for sym in FROM_MATH if hasattr(math, sym)}

import operator
OPERATORS = {ast.Add: operator.add, ast.Sub: operator.sub,
             ast.Mult: operator.mul, ast.Div: operator.truediv,
             ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
             ast.Pow: operator.pow, ast.BitAnd: operator.and_,
             ast.BitOr: operator.or_, ast.BitXor: operator.xor,
             ast.LShift: operator.lshift, ast.RShift: operator.rshift,
             ast.Eq: operator.eq, ast.NotEq: operator.ne,
             ast.Gt: operator.gt, ast.GtE: operator.ge,
             ast.Lt: operator.lt, ast.LtE: operator.le,
             ast.Is: operator.is_, ast.IsNot: operator.is_not,
             ast.In: lambda a, b: a in b,
             ast.NotIn: lambda a, b: a not in b,
             ast.And: lambda a, b: a and b,
             ast.Or: lambda a, b: a or b,
             ast.Invert: operator.invert,
             ast.Not: operator.not_,
             ast.UAdd: operator.pos,
             ast.USub: operator.neg,
             ast.MatMult: operator.matmul}


def op2func(op):
    """Return function for operator node."""
    return OPERATORS.get(op.__class__, None)


class ExceptionHolder:
    """Hold exception info."""
    def __init__(self, node=None, exc=None, msg='', expr=None, lineno=None):
        self.node = node
        self.exc = exc
        self.msg = msg
        self.expr = expr
        self.lineno = lineno

    def get_error(self):
        exc_name = self.exc.__name__ if self.exc is not None else 'Error'
        return (exc_name, f"{exc_name}: {self.msg}")


class ReturnedNone:
    """Sentinel for None return values."""
    pass


class Empty:
    """Sentinel for empty symbol."""
    pass


def check_symbol_name(name):
    """Check if name is valid for a symbol."""
    if name in RESERVED_WORDS:
        return False
    return NAME_MATCH(name) is not None


def build_symbol_table(use_numpy=False, **extras):
    """Build initial symbol table with standard functions."""
    symtable = {}
    symtable.update(BUILTINS_TABLE)
    symtable.update(MATH_TABLE)

    symtable['print'] = _safeprint

    for key, val in extras.items():
        symtable[key] = val
    return symtable


class _Writer:
    """Simple output buffer."""
    def __init__(self):
        self.buffer = []

    def write(self, text):
        self.buffer.append(str(text))

    def flush(self):
        pass

    def getvalue(self):
        return ''.join(self.buffer)

    def clear(self):
        self.buffer = []


def _safeprint(*args, **kwargs):
    """Safe print function."""
    pass


class NameResolver(ast.NodeVisitor):
    """Find all Names in an AST tree."""
    def __init__(self):
        self.names = []

    def generic_visit(self, node):
        if node.__class__.__name__ == 'Name':
            if node.id not in self.names:
                self.names.append(node.id)
        ast.NodeVisitor.generic_visit(self, node)


def resolve_names(text):
    """Return list of symbol names in expression text."""
    nf = NameResolver()
    nf.generic_visit(ast.parse(text))
    return nf.names


class UserFunction:
    """User-defined function for the expression engine.

    Stores the parsed AST nodes from a function definition for later
    evaluation within the sandboxed environment.
    """

    def __init__(self, name, engine, doc=None, lineno=0,
                 body=None, args=None, kwargs=None,
                 vararg=None, varkws=None):
        self.name = name
        self.__name__ = self.name
        self.__safeexpr__ = engine
        self.__raise_exc__ = self.__safeexpr__.raise_exception
        self.__doc__ = doc
        self.body = body
        self.__argnames__ = args
        self.__kwargs__ = kwargs
        self.__vararg__ = vararg
        self.__varkws__ = varkws
        self.lineno = lineno

    def __dir__(self):
        return ['name', 'argnames', 'kwargs', 'vararg', 'varkws']

    def __repr__(self):
        sig = self.__signature__()
        rep = f"<UserFunction {sig}>"
        doc = self.__doc__
        if isinstance(doc, ast.Constant):
            doc = doc.value
        if doc is not None:
            rep = f"{rep}\n {doc}"
        return rep

    def __signature__(self):
        sig = ""
        if len(self.__argnames__) > 0:
            sig = sig + ', '.join(self.__argnames__)
        if self.__vararg__ is not None:
            sig = sig + f"*{self.__vararg__}"
        if len(self.__kwargs__) > 0:
            if len(sig) > 0:
                sig = f"{sig}, "
            _kw = [f"{k}={v}" for k, v in self.__kwargs__]
            sig = f"{sig}{', '.join(_kw)}"
            if self.__varkws__ is not None:
                sig = f"{sig}, **{self.__varkws__}"
        return f"{self.name}({sig})"

    def __call__(self, *args, **kwargs):
        symlocals = {}

        args = list(args)
        nargs = len(args)
        nkws = len(kwargs)
        nargs_expected = len(self.__argnames__)

        if (nargs < nargs_expected) and nkws > 0:
            for name in self.__argnames__[nargs:]:
                if name in kwargs:
                    args.append(kwargs.pop(name))
            nargs = len(args)
            nargs_expected = len(self.__argnames__)
            nkws = len(kwargs)

        if nargs < nargs_expected:
            msg = f"{self.name}() takes at least"
            msg = f"{msg} {nargs_expected} arguments, got {nargs}"
            self.__raise_exc__(None, exc=TypeError, msg=msg)

        if len(self.__argnames__) > 0 and kwargs is not None:
            for targ in self.__argnames__:
                if targ in kwargs:
                    msg = f"multiple values for keyword argument '{targ}' in {self.name}"
                    self.__raise_exc__(None, exc=TypeError, msg=msg,
                                       lineno=self.lineno)

        if nargs != nargs_expected:
            if nargs < nargs_expected:
                msg = f"not enough arguments for {self.name}()"
                msg = f"{msg} (expected {nargs_expected}, got {nargs})"
                self.__raise_exc__(None, exc=TypeError, msg=msg)

        if nargs > nargs_expected and self.__vararg__ is None:
            if nargs - nargs_expected > len(self.__kwargs__):
                msg = f"too many arguments for {self.name}() expected at most"
                msg = f"{msg} {len(self.__kwargs__)+nargs_expected}, got {nargs}"
                self.__raise_exc__(None, exc=TypeError, msg=msg)

            for i, xarg in enumerate(args[nargs_expected:]):
                kw_name = self.__kwargs__[i][0]
                if kw_name not in kwargs:
                    kwargs[kw_name] = xarg

        for argname in self.__argnames__:
            symlocals[argname] = args.pop(0)

        try:
            if self.__vararg__ is not None:
                symlocals[self.__vararg__] = tuple(args)

            for key, val in self.__kwargs__:
                if key in kwargs:
                    val = kwargs.pop(key)
                symlocals[key] = val

            if self.__varkws__ is not None:
                symlocals[self.__varkws__] = kwargs

            elif len(kwargs) > 0:
                msg = f"extra keyword arguments for {self.name}: "
                msg = msg + ','.join(list(kwargs.keys()))
                self.__raise_exc__(None, msg=msg, exc=TypeError,
                                   lineno=self.lineno)

        except (ValueError, LookupError, TypeError,
                NameError, AttributeError):
            msg = f"incorrect arguments for {self.name}"
            self.__raise_exc__(None, msg=msg, lineno=self.lineno)

        save_symtable = self.__safeexpr__.symtable.copy()
        self.__safeexpr__.symtable.update(symlocals)

        self.__safeexpr__.retval = None
        self.__safeexpr__._calldepth += 1
        retval = None

        for node in self.body:
            self.__safeexpr__.run(node, expr='<>', lineno=self.lineno)
            if len(self.__safeexpr__.error) > 0:
                break
            if self.__safeexpr__.retval is not None:
                retval = self.__safeexpr__.retval
                self.__safeexpr__.retval = None
                if retval is ReturnedNone:
                    retval = None
                break

        self.__safeexpr__.symtable = save_symtable
        self.__safeexpr__._calldepth -= 1
        symlocals = None
        return retval
