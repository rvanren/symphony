from typing import List
from antlr4.error.ErrorListener import ErrorListener  # type: ignore

from symphony_model_checker.exception import ErrorToken
from symphony_model_checker.parser.SymphonyParser import SymphonyParser

class SymphonyLexerErrorListener(ErrorListener):
    def __init__(self, filename: str):
        super().__init__()
        self.filename = filename
        self.errors: List[ErrorToken] = []

    def syntaxError(self, recognizer, offending_symbol, line, column, msg, e):
        lexeme = str(offending_symbol.text) if offending_symbol and hasattr(offending_symbol, 'text') else ""
        self.errors.append(ErrorToken(
            filename=self.filename,
            lexeme=lexeme,
            message=str(msg) + " syntax error",
            line=line,
            column=column + 1,
            is_eof_error=False
        ))

class SymphonyParserErrorListener(ErrorListener):
    def __init__(self, filename: str):
        super().__init__()
        self.filename = filename
        self.errors: List[ErrorToken] = []

    def syntaxError(self, recognizer, offending_symbol, line, column, msg, e):
        lexeme = offending_symbol.text
        line = line
        column = column + 1

        if offending_symbol.type == SymphonyParser.INDENT:
            self.errors.append(ErrorToken(
                filename=self.filename,
                lexeme=lexeme,
                message="Indentation error",
                line=line,
                column=column,
                is_eof_error=False
            ))
            return
        
        if offending_symbol.type == SymphonyParser.DEDENT:
            self.errors.append(ErrorToken(
                filename=self.filename,
                lexeme=lexeme,
                message="Unexpected dedent. May be caused by indentation error.",
                line=line,
                column=column,
                is_eof_error=False
            ))
            return

        if isinstance(msg, str):
            if msg.startswith("no viable alternative at input"):
                msg = f"Unexpected token {lexeme}"
            elif msg.startswith("extraneous input"):
                msg = f"Extraneous input {lexeme}. May be caused by another error."
            elif msg.startswith("mismatched input"):
                msg = f"Unexpected token {lexeme}"

        self.errors.append(ErrorToken(
            filename=self.filename,
            lexeme=lexeme,
            message=str(msg),
            line=line,
            column=column,
            is_eof_error=False
        ))
