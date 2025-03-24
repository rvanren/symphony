from symphony_model_checker.h2py.H2PyStmtVisitor import H2PyStmtVisitor
import symphony_model_checker.symphony.ast as hast

import ast as past


def h2py(hast: hast.AST) -> past.AST:
    stmt_visitor = H2PyStmtVisitor()
    return past.Module(
        body=[
            past.ImportFrom(
                module='h2py_runtime',
                names=[past.alias(name='*')],
                level=0
            )
        ] + stmt_visitor(hast),
        type_ignores=[]
    )
