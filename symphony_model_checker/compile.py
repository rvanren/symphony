from antlr4 import InputStream, FileStream, CommonTokenStream # type: ignore

from symphony_model_checker.exception import SymphonyCompilerError, SymphonyCompilerErrorCollection
from symphony_model_checker.symphony.ast import AST, BlockAST

import symphony_model_checker.symphony.symphony as legacy_symphony
from symphony_model_checker.symphony.symphony import Scope, Code, State
from symphony_model_checker.symphony.ops import FrameOp, ReturnOp
from symphony_model_checker.symphony.value import AddressValue, ContextValue
from symphony_model_checker.parser.antlr_rule_visitor import SymphonyVisitorImpl
from symphony_model_checker.parser.SymphonyParser import SymphonyParser
from symphony_model_checker.parser.SymphonyErrorListener import SymphonyLexerErrorListener, SymphonyParserErrorListener
from symphony_model_checker.parser.SymphonyLexer import SymphonyLexer

import os

from typing import List, Optional, Tuple

def _build_input_stream(**kwargs) -> InputStream:
    try:
        filename = kwargs.get('filename', None)
        str_value = kwargs.get('str_value', None)
        if filename is not None:
            return FileStream(filename, 'utf-8')
        elif str_value is not None:
            return InputStream(str_value)
    except UnicodeDecodeError as e:
        lexeme = str(e.args[1][e.start:e.end]) # e.args[0] is the encoding name, and e.args[1] contains the bytes being parsed.
        raise SymphonyCompilerError(
            message=e.reason,
            filename=filename,
            line=1,
            column=1,
            lexeme=lexeme
        )
    raise ValueError("Cannot build input stream without a source")


def _build_parser(progam_input: InputStream, lexer_error_listener=None, parser_error_listener=None):
    lexer = SymphonyLexer(progam_input)
    stream = CommonTokenStream(lexer)
    parser = SymphonyParser(stream)

    lexer.removeErrorListeners()
    parser.removeErrorListeners()
    if lexer_error_listener:
        lexer.addErrorListener(lexer_error_listener)
    if parser_error_listener:
        parser.addErrorListener(parser_error_listener)

    return parser


def _load_string(string, scope: Scope, code: Code, filename="<string-code>"):
    legacy_symphony.namestack.append(filename)
    ast = _parse_string(string, filename)
    for mod in ast.getImports():
        _do_import(scope, code, mod)

    # method names and label names get a temporary value
    # they are filled in with their actual values after compilation
    # TODO.  Look for duplicates?
    for (token, lb) in ast.getLabels():
        (lexeme, file, line, column) = token
        if scope.find(token):
            raise SymphonyCompilerError(
                message="Duplicate label %s (defined before in line %d)" % (lexeme, scope.names[lexeme][1][2]),
                filename=file,
                line=line,
                column=column,
                lexeme=lexeme
            )
        scope.names[lexeme] = ("constant", (lb, file, line, column))

    ast.compile(scope, code, None)
    legacy_symphony.namestack.pop()


def _load_file(filename: str, scope: Scope, code: Code, init: bool):
    if filename in legacy_symphony.files:
        return
    legacy_symphony.namestack.append(filename)
    with open(filename, "r", encoding='utf-8') as f:
        legacy_symphony.files[filename] = f.read().split("\n")

    ast = _parse(filename)
    if ast is None:
        raise SymphonyCompilerError(
            message="Unknown error: unable to parse Symphony file",
            filename=filename
        )

    _, _, line1, column1 = ast.token
    lexeme2, _, line2, column2 = ast.endtoken
    # Hack: some external software sometimes adds the lexeme 'newLine' in there
    if lexeme2 != 'newLine' or column2 != 1:
        column2 += len(lexeme2) - 1
    if init:
        code.append(FrameOp(("__init__", None, None, None), []), ast.token, ast.endtoken, stmt=(line1, column1, line2, column2))

    for mod in ast.getImports():
        _do_import(scope, code, mod)

    # method names and label names get a temporary value
    # they are filled in with their actual values after compilation
    # TODO.  Look for duplicates?
    for (token, lb) in ast.getLabels():
        (lexeme, file, line, column) = token
        if scope.find(token):
            raise SymphonyCompilerError(
                message="Duplicate label %s" % lexeme,
                filename=file,
                line=line,
                column=column,
                lexeme=lexeme
            )
        scope.names[lexeme] = ("constant", (lb, file, line, column))

    ast.compile(scope, code, None)
    if init:
        # print("TOKEN", ast.token, "END", ast.endtoken)
        _, file, line, column = ast.token
        code.append(ReturnOp(("result", file, line, column), AddressValue(None, [])), ast.endtoken, ast.endtoken, stmt=(line2, column2, line2, column2))  # to terminate "__init__" process
    legacy_symphony.namestack.pop()


def _do_import(scope: Scope, code: Code, module: Tuple[str, Optional[str], Optional[int], Optional[int]]):
    (lexeme, file, line, column) = module
    code.modpush(lexeme)
    # assert lexeme not in scope.names        # TODO
    if lexeme not in legacy_symphony.imported:
        # module name replacement with -m flag
        modname = legacy_symphony.modules.get(lexeme, lexeme)

        # create a new scope
        scope2 = Scope(None)
        scope2.prefix = lexeme
        scope2.labels = scope.labels
        scope2.inherit = True

        found = False
        install_path = os.path.dirname(os.path.realpath(__file__))
        for directory in [os.path.dirname(legacy_symphony.namestack[-1]), os.path.join(install_path, "modules"), "."]:
            filename = os.path.join(directory, modname + ".hny")
            if os.path.exists(filename):
                scope2.file = filename
                _load_file(filename, scope2, code, False)
                found = True
                break
        if not found:
            raise SymphonyCompilerError(
                filename=file,
                lexeme=modname,
                message="Can't import module %s from %s" % (
                    modname, legacy_symphony.namestack),
                line=line,
                column=column
            )
        legacy_symphony.imported[lexeme] = scope2

    scope.names[lexeme] = ("module", legacy_symphony.imported[lexeme])
    code.modpop()

def _parse_constant(name: str, value: str):
    filename = "<constant argument>"
    _input = _build_input_stream(str_value=value)
    parser = _build_parser(_input)
    visitor = SymphonyVisitorImpl(filename)

    tree = parser.expr()
    ast = visitor.visit(tree)

    scope = Scope(None)
    code = Code()
    code.modpush("__const__")
    ast.compile(scope, code, None)
    state = State(code, scope.labels)
    ctx = ContextValue(("__arg__", None, None, None), 0,
                       legacy_symphony.emptytuple, legacy_symphony.emptytuple)
    ctx.atomic = 1
    while ctx.pc != len(code.labeled_ops):
        code.labeled_ops[ctx.pc].op.eval(state, ctx)
    legacy_symphony.constants[name] = ctx.pop()


def _parse_string(string: str, filename: str = "<string-code>") -> BlockAST:
    _input = _build_input_stream(str_value=string)
    parser = _build_parser(_input)
    visitor = SymphonyVisitorImpl(filename)

    tree = parser.program()
    return visitor.visit(tree)


def _parse(filename: str) -> BlockAST:
    _input = _build_input_stream(filename=filename)
    error_listener = SymphonyParserErrorListener(filename)
    lexer_error_listener = SymphonyLexerErrorListener(filename)
    parser = _build_parser(
        _input,
        lexer_error_listener=lexer_error_listener,
        parser_error_listener=error_listener
    )

    tree = parser.program()
    if error_listener.errors or lexer_error_listener.errors:
        raise SymphonyCompilerErrorCollection(
            lexer_error_listener.errors + error_listener.errors
        )

    visitor = SymphonyVisitorImpl(filename)
    try:
        return visitor.visit(tree)
    except SymphonyCompilerError as e:
        raise SymphonyCompilerErrorCollection([e.token])


def parse(filename: str) -> AST:
    return _parse(filename)


def parse_string(string: str) -> AST:
    return _parse_string(string)


def do_compile(fname: str, consts: List[str], mods: List[str], interface: Optional[str]):
    for c in consts:
        try:
            i = c.index("=")
            _parse_constant(c[0:i], c[i + 1:])
        except (IndexError, ValueError):
            raise SymphonyCompilerError(
                message="Usage: -c C=V to define a constant"
            )

    for m in mods:
        try:
            i = m.index("=")
            legacy_symphony.modules[m[0:i]] = m[i + 1:]
        except (IndexError, ValueError):
            raise SymphonyCompilerError(
                message="Usage: -m module=version to specify a module version"
            )

    scope = Scope(None)
    scope.file = str(fname)
    scope.inherit = True
    code = Code()
    code.modpush("__main__")
    _load_file(str(fname), scope, code, True)

    unused_constant_def = legacy_symphony.constants.keys() - legacy_symphony.used_constants
    unused_module_def = legacy_symphony.modules.keys() - legacy_symphony.imported.keys()
    if len(unused_constant_def) > 0:
        raise SymphonyCompilerError(
            message="The following constants were defined from the command line but not used: " + ', '.join(unused_constant_def),
            filename=fname,
            line=0,
            column=0,
            lexeme="",
        )
    if len(unused_module_def) > 0:
        raise SymphonyCompilerError(
            message="The following modules were defined from the command line but not used: " + ', '.join(unused_module_def),
            filename=fname,
            line=0,
            column=0,
            lexeme="",
        )

    # Analyze liveness of variables
    newcode = code.liveness()

    newcode.link()
    legacy_symphony.optimize(newcode)
    return newcode, scope
