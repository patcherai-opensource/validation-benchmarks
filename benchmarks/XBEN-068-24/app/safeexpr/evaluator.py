"""
Safe expression evaluation engine using Python's ast module.

Provides an ExpressionEngine class that compiles a restricted set of
Python expressions and statements to Python's AST representation, and then
executes that representation using values held in a symbol table.

The symbol table is a simple dictionary, giving a flat namespace. This comes
pre-loaded with many functions from Python's builtin and math module.
Additional symbols can be added when an engine is created, but the user
will not be able to import additional modules.

Expressions, including loops, conditionals, and function definitions can be
compiled into AST nodes and then evaluated later, using the current values
in the symbol table.

The result is a restricted, simplified version of Python meant for numerical
calculations that is safer than 'eval' because many unsafe operations are
simply not allowed, and others (such as 'import') are disabled by default.

Supported syntax elements:
     for loops, while loops, if-then-elif-else conditionals, with,
     try-except-finally, function definitions with def
     advanced slicing, if-expressions, list/dict/set comprehension

Not supported:
     Import, Exec, Lambda, Class, Global, Generators,
     Yield, Decorators
"""
import ast
import sys
import copy
import time
from sys import exc_info, stderr, stdout

from .helpers import (BLOCKED_ATTRS, BLOCKED_ATTRS_TYPES,
                      ExceptionHolder, ReturnedNone, Empty, build_symbol_table,
                      op2func, check_symbol_name, UserFunction)

ALL_NODES = ['arg', 'assert', 'assign', 'attribute', 'augassign', 'binop',
             'boolop', 'break', 'bytes', 'call', 'compare', 'constant',
             'continue', 'delete', 'dict', 'dictcomp', 'ellipsis',
             'excepthandler', 'expr', 'extslice', 'for', 'functiondef', 'if',
             'ifexp', 'import', 'importfrom', 'index', 'interrupt', 'list',
             'listcomp', 'module', 'name', 'nameconstant', 'num', 'pass',
             'raise', 'repr', 'return', 'set', 'setcomp', 'slice', 'str',
             'subscript', 'try', 'tuple', 'unaryop', 'while', 'with',
             'formattedvalue', 'joinedstr']

MINIMAL_CONFIG = {'import': False, 'importfrom': False}
DEFAULT_CONFIG = {'import': False, 'importfrom': False}

for _tnode in ('assert', 'augassign', 'delete', 'if', 'ifexp', 'for',
             'formattedvalue', 'functiondef', 'print', 'raise', 'listcomp',
             'dictcomp', 'setcomp', 'try', 'while', 'with'):
    MINIMAL_CONFIG[_tnode] = False
    DEFAULT_CONFIG[_tnode] = True


class ExpressionEngine:
    """A restricted, simplified interpreter of mathematical expressions
    using Python syntax.

    Parameters
    ----------
    symtable : dict or None
        dictionary to use as symbol table (if None, one will be created).
    user_symbols : dict or None
        dictionary of user-defined symbols to add to symbol table.
    writer : file-like or None
        callable file-like object where standard output will be sent.
    err_writer : file-like or None
        callable file-like object where standard error will be sent.
    max_statement_length : int
        maximum length of expression allowed [50,000 characters]
    readonly_symbols : iterable or None
        symbols that the user can not assign to
    builtins_readonly : bool
        whether to blacklist all symbols that are in the initial symtable
    minimal : bool
        create a minimal interpreter: disable many nodes.
    config : dict
        dictionary listing which nodes to support.
    max_time : float
        maximum execution time in seconds (0 = unlimited)
    """

    def __init__(self, symtable=None, user_symbols=None,
                 writer=None, err_writer=None,
                 max_statement_length=50000,
                 readonly_symbols=None,
                 builtins_readonly=False,
                 minimal=False,
                 config=None,
                 max_time=0):
        self.config = DEFAULT_CONFIG.copy()
        if minimal:
            self.config = MINIMAL_CONFIG.copy()
        if config is not None:
            self.config.update(config)

        if symtable is None:
            symtable = build_symbol_table()
        self.symtable = symtable

        if user_symbols is not None:
            self.symtable.update(user_symbols)

        self.error = []
        self.error_msg = None
        self.expr = None
        self.retval = None
        self.lineno = 0
        self.start_time = time.time()
        self.max_time = max(0, max_time)
        self.max_statement_length = max(1, max_statement_length)
        self._calldepth = 0
        self._interrupt = None
        self.no_deepcopy = []

        if writer is None:
            writer = stdout
        if err_writer is None:
            err_writer = stderr
        self.writer = writer
        self.err_writer = err_writer

        self.readonly_symbols = set()
        if readonly_symbols is not None:
            self.readonly_symbols = set(readonly_symbols)
        if builtins_readonly:
            self.readonly_symbols |= set(self.symtable.keys())

        nodes = ALL_NODES[:]
        for node in self.config:
            if node in nodes and not self.config[node]:
                nodes.remove(node)

        self.node_handlers = dict(((node, getattr(self, f"on_{node}"))
                                   for node in nodes if hasattr(self, f"on_{node}")))

        # add builtin handler mappings
        for nname in ('num', 'str', 'bytes', 'nameconstant', 'ellipsis'):
            if nname not in self.node_handlers and hasattr(self, 'on_constant'):
                self.node_handlers[nname] = self.on_constant
        for nname in ('break', 'continue'):
            if nname in self.node_handlers:
                self.node_handlers[nname] = self.on_interrupt

    def raise_exception(self, node, exc=None, msg='', expr=None, lineno=None):
        """Add an exception."""
        if expr is None:
            expr = self.expr
        if lineno is not None:
            self.lineno = lineno
        err = ExceptionHolder(node=node, exc=exc, msg=msg,
                              expr=expr, lineno=self.lineno)
        self.error.append(err)
        if exc is not None:
            raise exc(msg)

    def parse(self, text):
        """Parse statement/expression to AST representation."""
        if len(text) > self.max_statement_length:
            msg = f'length of text exceeds {self.max_statement_length:d} characters'
            self.raise_exception(None, exc=RuntimeError, expr=msg)
        self.expr = text
        try:
            out = ast.parse(text)
        except SyntaxError:
            self.raise_exception(None, exc=SyntaxError, expr=text)
        except:
            self.raise_exception(None, exc=RuntimeError, expr=text)
        return out

    def run(self, node, expr=None, lineno=None, with_raise=True):
        """Execute parsed AST representation for an expression."""
        if isinstance(node, str):
            return self.eval(node, raise_errors=with_raise)

        out = None
        if len(self.error) > 0:
            return out
        if self.retval is not None:
            return self.retval
        if isinstance(self._interrupt, (ast.Break, ast.Continue)):
            return self._interrupt
        if node is None:
            return out

        if self.max_time > 0 and (time.time() - self.start_time) > self.max_time:
            self.raise_exception(None, exc=RuntimeError,
                                 msg='execution time limit exceeded')

        if lineno is not None:
            self.lineno = lineno
        if expr is not None:
            self.expr = expr

        try:
            handler = self.node_handlers[node.__class__.__name__.lower()]
        except KeyError:
            self.raise_exception(None, exc=NotImplementedError, expr=self.expr)

        try:
            ret = handler(node)
            if isinstance(ret, enumerate):
                ret = list(ret)
            return ret
        except:
            if with_raise and self.expr is not None:
                self.raise_exception(node, expr=self.expr)

        if len(self.error) > 2:
            self._remove_duplicate_errors()
        return None

    def _remove_duplicate_errors(self):
        error = [self.error[0]]
        for err in self.error[1:]:
            lerr = error[-1]
            if err.exc != lerr.exc or err.expr != lerr.expr or err.msg != lerr.msg:
                if isinstance(err.msg, str) and len(err.msg) > 0:
                    error.append(err)
        self.error = error

    def __call__(self, expr, **kw):
        """Call class instance as function."""
        return self.eval(expr, **kw)

    def eval(self, expr, lineno=0, show_errors=True, raise_errors=False):
        """Evaluate a single statement."""
        self.lineno = lineno
        self.error = []
        self.error_msg = None
        self.start_time = time.time()
        if isinstance(expr, str):
            try:
                node = self.parse(expr)
            except Exception:
                errmsg = exc_info()[1]
                if len(self.error) > 0:
                    lerr = self.error[-1]
                    errmsg = lerr.get_error()[1]
                    if raise_errors:
                        raise lerr.exc(errmsg)
                if show_errors:
                    print(errmsg, file=self.err_writer)
                return None
        else:
            node = expr
        try:
            return self.run(node, expr=expr, lineno=lineno, with_raise=raise_errors)
        except Exception:
            if show_errors and not raise_errors:
                errmsg = exc_info()[1]
                if len(self.error) > 0:
                    errmsg = self.error[-1].get_error()[1]
                print(errmsg, file=self.err_writer)
        if raise_errors and len(self.error) > 0:
            self._remove_duplicate_errors()
            err = self.error[-1]
            raise err.exc(err.get_error()[1])
        return None

    @staticmethod
    def dump(node, **kw):
        return ast.dump(node, **kw)

    def on_expr(self, node):
        return self.run(node.value)

    def on_import(self, node):
        msg = "imports are not allowed"
        self.raise_exception(node, exc=ImportError, msg=msg)

    def on_importfrom(self, node):
        msg = "imports are not allowed"
        self.raise_exception(node, exc=ImportError, msg=msg)

    def on_pass(self, node):
        return None

    def on_return(self, node):
        if node.value is not None:
            self.retval = self.run(node.value)
        else:
            self.retval = ReturnedNone
        return

    def on_delete(self, node):
        for target in node.targets:
            name = target.id
            if name in self.symtable:
                del self.symtable[name]

    # for break and continue
    def on_interrupt(self, node):
        self._interrupt = node
        return node

    def on_break(self, node):
        return self.on_interrupt(node)

    def on_continue(self, node):
        return self.on_interrupt(node)

    def on_assert(self, node):
        if not self.run(node.test):
            msg = node.msg.value if node.msg else ""
            self.raise_exception(node, exc=AssertionError, msg=msg)
        return True

    def on_list(self, node):
        return [self.run(e) for e in node.elts]

    def on_tuple(self, node):
        return tuple(self.on_list(node))

    def on_set(self, node):
        return set([self.run(k) for k in node.elts])

    def on_dict(self, node):
        return {self.run(k): self.run(v) for k, v in
                zip(node.keys, node.values)}

    def on_constant(self, node):
        return node.value

    def on_joinedstr(self, node):
        return ''.join([self.run(k) for k in node.values])

    def on_formattedvalue(self, node):
        val = self.run(node.value)
        fstring_converters = {115: str, 114: repr, 97: ascii}
        if node.conversion in fstring_converters:
            val = fstring_converters[node.conversion](val)
        fmt = '{__fstring__}'
        if node.format_spec is not None:
            fmt = f'{{__fstring__:{self.run(node.format_spec)}}}'
        return fmt.format(__fstring__=val)

    def _getsym(self, node):
        val = self.symtable.get(node.id, Empty)
        if isinstance(val, Empty):
            msg = f"name '{node.id}' is not defined"
            self.raise_exception(node, exc=NameError, msg=msg)
        return val

    def on_name(self, node):
        ctx = node.ctx.__class__
        if ctx in (ast.Param, ast.Del):
            return str(node.id)
        return self._getsym(node)

    def node_assign(self, node, val):
        if node.__class__ == ast.Name:
            sym = node.id
            if sym in self.readonly_symbols:
                self.raise_exception(node, exc=NameError,
                                     msg=f"'{sym}' is read-only")
            self.symtable[sym] = val
        elif node.__class__ == ast.Attribute:
            if node.ctx.__class__ == ast.Store:
                rval = self.run(node.value)
                setattr(rval, node.attr, val)
        elif node.__class__ == ast.Subscript:
            self.run(node.value)[self.run(node.slice)] = val
        elif node.__class__ in (ast.Tuple, ast.List):
            if len(val) == len(node.elts):
                for telem, tval in zip(node.elts, val):
                    self.node_assign(telem, tval)
            else:
                raise ValueError('too many values to unpack')

    def on_attribute(self, node):
        """Extract attribute."""
        ctx = node.ctx.__class__
        if ctx == ast.Store:
            msg = "attribute for storage: shouldn't be here!"
            self.raise_exception(node, exc=RuntimeError, msg=msg)

        sym = self.run(node.value)
        if ctx == ast.Del:
            return delattr(sym, node.attr)

        unsafe = (node.attr in BLOCKED_ATTRS or
                 (node.attr.startswith('__') and node.attr.endswith('__')))
        if not unsafe:
            for dtype, attrlist in BLOCKED_ATTRS_TYPES.items():
                unsafe = isinstance(sym, dtype) and node.attr in attrlist
                if unsafe:
                    break
        if unsafe:
            msg = f"no safe attribute '{node.attr}' for {repr(sym)}"
            self.raise_exception(node, exc=AttributeError, msg=msg)
        else:
            try:
                return getattr(sym, node.attr)
            except AttributeError:
                pass

    def on_assign(self, node):
        val = self.run(node.value)
        for tnode in node.targets:
            self.node_assign(tnode, val)

    def on_augassign(self, node):
        return self.on_assign(ast.Assign(targets=[node.target],
                                         value=ast.BinOp(left=node.target,
                                                         op=node.op,
                                                         right=node.value)))

    def on_slice(self, node):
        return slice(self.run(node.lower),
                     self.run(node.upper),
                     self.run(node.step))

    def on_extslice(self, node):
        return tuple([self.run(n) for n in node.dims])

    def on_index(self, node):
        return self.run(node.value)

    def on_subscript(self, node):
        val = self.run(node.value)
        nslice = self.run(node.slice)
        ctx = node.ctx.__class__
        if ctx in (ast.Load, ast.Store):
            return val[nslice]
        msg = "subscript with unknown context"
        self.raise_exception(node, msg=msg)

    def on_unaryop(self, node):
        return op2func(node.op)(self.run(node.operand))

    def on_binop(self, node):
        left = self.run(node.left)
        right = self.run(node.right)
        func = op2func(node.op)
        if func is None:
            msg = f"unsupported binary operator '{node.op.__class__.__name__}'"
            self.raise_exception(node, msg=msg)
        return func(left, right)

    def on_boolop(self, node):
        val = self.run(node.values[0])
        is_and = ast.And == node.op.__class__
        if (is_and and val) or (not is_and and not val):
            for n in node.values[1:]:
                val = op2func(node.op)(val, self.run(n))
                if (is_and and not val) or (not is_and and val):
                    break
        return val

    def on_compare(self, node):
        left = self.run(node.left)
        for oper, comp in zip(node.ops, node.comparators):
            right = self.run(comp)
            if not op2func(oper)(left, right):
                return False
            left = right
        return True

    def on_print(self, node):
        if self.writer is not None:
            for val in [self.run(n) for n in node.values]:
                self.writer.write(str(val))
            if node.nl:
                self.writer.write('\n')

    def on_repr(self, node):
        return repr(self.run(node.value))

    def on_module(self, node):
        out = None
        for tnode in node.body:
            out = self.run(tnode)
        return out

    def on_expression(self, node):
        return self.on_module(node)

    def on_if(self, node):
        block = node.body
        if not self.run(node.test):
            block = node.orelse
        for tnode in block:
            self.run(tnode)

    def on_ifexp(self, node):
        expr = node.orelse
        if self.run(node.test):
            expr = node.body
        return self.run(expr)

    def on_while(self, node):
        while self.run(node.test):
            self._interrupt = None
            for tnode in node.body:
                self.run(tnode)
                if self._interrupt is not None:
                    break
            if isinstance(self._interrupt, ast.Break):
                break
        self._interrupt = None

    def on_for(self, node):
        for val in self.run(node.iter):
            self.node_assign(node.target, val)
            self._interrupt = None
            for tnode in node.body:
                self.run(tnode)
                if self._interrupt is not None:
                    break
            if isinstance(self._interrupt, ast.Break):
                break
        self._interrupt = None

    def on_with(self, node):
        ctx_managers = []
        for item in node.items:
            ctx = self.run(item.context_expr)
            ctx_managers.append(ctx)
            if item.optional_vars is not None:
                self.node_assign(item.optional_vars, ctx.__enter__())
            else:
                ctx.__enter__()
        for bnode in node.body:
            self.run(bnode)
        for ctx in reversed(ctx_managers):
            ctx.__exit__(None, None, None)

    def on_listcomp(self, node):
        out = []
        for generator in node.generators:
            for val in self.run(generator.iter):
                self.node_assign(generator.target, val)
                add = True
                for cond in generator.ifs:
                    if not self.run(cond):
                        add = False
                        break
                if add:
                    out.append(self.run(node.elt))
        return out

    def on_setcomp(self, node):
        out = set()
        for generator in node.generators:
            for val in self.run(generator.iter):
                self.node_assign(generator.target, val)
                add = True
                for cond in generator.ifs:
                    if not self.run(cond):
                        add = False
                        break
                if add:
                    out.add(self.run(node.elt))
        return out

    def on_dictcomp(self, node):
        out = {}
        for generator in node.generators:
            for val in self.run(generator.iter):
                self.node_assign(generator.target, val)
                add = True
                for cond in generator.ifs:
                    if not self.run(cond):
                        add = False
                        break
                if add:
                    out[self.run(node.key)] = self.run(node.value)
        return out

    def on_excepthandler(self, node):
        return (self.run(node.type), node.name, node.body)

    def on_try(self, node):
        for tnode in node.body:
            try:
                self.run(tnode)
            except:
                for hnd_node in node.handlers:
                    hnd = self.on_excepthandler(hnd_node)
                    if hnd[0] is not None:
                        for tline in hnd[2]:
                            self.run(tline)

        if hasattr(node, 'finalbody'):
            for tnode in node.finalbody:
                self.run(tnode)

    def on_raise(self, node):
        exc = self.run(node.exc)
        msg = ' '.join(self.run(node.exc).args)
        self.raise_exception(None, exc=exc.__class__, msg=msg)

    def on_call(self, node):
        func = self.run(node.func)
        if func is None:
            msg = "'NoneType' is not callable"
            self.raise_exception(node, exc=TypeError, msg=msg)

        args = [self.run(targ) for targ in node.args]

        keywords = {}
        for key in node.keywords:
            if key.arg is None:
                keywords.update(self.run(key.value))
            elif key.arg is not None:
                keywords[key.arg] = self.run(key.value)

        try:
            return func(*args, **keywords)
        except:
            msg = f"error calling {getattr(func, '__name__', repr(func))}"
            self.raise_exception(node, exc=TypeError, msg=msg)

    def on_arg(self, node):
        return node.arg

    def on_functiondef(self, node):
        """Define user functions."""
        if node.decorator_list:
            raise Warning("decorated functions not supported!")
        kwargs = []

        if (not check_symbol_name(node.name) or
                node.name in self.readonly_symbols):
            errmsg = f"invalid function name (reserved word?) {node.name}"
            self.raise_exception(node, exc=NameError, msg=errmsg)

        offset = len(node.args.args) - len(node.args.defaults)
        for idef, defnode in enumerate(node.args.defaults):
            defval = self.run(defnode)
            keyval = self.run(node.args.args[idef+offset])
            kwargs.append((keyval, defval))

        args = [tnode.arg for tnode in node.args.args[:offset]]
        doc = None
        nb0 = node.body[0]
        if isinstance(nb0, ast.Expr) and isinstance(nb0.value, ast.Constant):
            doc = nb0.value
        varkws = node.args.kwarg
        vararg = node.args.vararg
        if isinstance(vararg, ast.arg):
            vararg = vararg.arg
        if isinstance(varkws, ast.arg):
            varkws = varkws.arg
        self.symtable[node.name] = UserFunction(node.name, self, doc=doc,
                                                 lineno=self.lineno,
                                                 body=node.body,
                                                 args=args, kwargs=kwargs,
                                                 vararg=vararg, varkws=varkws)
        if node.name in self.no_deepcopy:
            self.no_deepcopy.remove(node.name)
