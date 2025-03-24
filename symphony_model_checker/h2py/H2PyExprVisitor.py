from symphony_model_checker.h2py.H2PyEnv import H2PyEnv
from symphony_model_checker.symphony.AbstractASTVisitor import AbstractASTVisitor
from symphony_model_checker.h2py.util import *
import symphony_model_checker.h2py.h2py_runtime as h2py_runtime
import symphony_model_checker.symphony.value as hvalue
import symphony_model_checker.symphony.ast as hast

import ast as past


class H2PyExprVisitor(AbstractASTVisitor):

    def __call__(self, node: hast.AST, env: H2PyEnv = H2PyEnv()) -> past.AST:
        return node.accept_visitor(self, env)

    def visit_name(self, node: hast.NameAST, env: H2PyEnv):
        return past.Name(id=escape_name(node.name[T_TOKEN]), ctx=env.get('ctx'))

    def visit_nary(self, node: hast.NaryAST, env: H2PyEnv):
        op = node.op[T_TOKEN]

        if op == '+':
            assert len(node.args) == 2
            return past.BinOp(
                left=self(node.args[0], env.rep(ctx=past.Load())),
                op=past.Add(),
                right=self(node.args[1], env.rep(ctx=past.Load()))
            )

        elif op == '*':
            assert len(node.args) == 2
            return past.BinOp(
                left=self(node.args[0], env.rep(ctx=past.Load())),
                op=past.Mult(),
                right=self(node.args[1], env.rep(ctx=past.Load()))
            )

        elif op == '-':
            assert len(node.args) == 2
            return past.BinOp(
                left=self(node.args[0], env.rep(ctx=past.Load())),
                op=past.Sub(),
                right=self(node.args[1], env.rep(ctx=past.Load()))
            )

        elif op == 'and':
            assert len(node.args) == 2
            return past.BoolOp(
                op=past.And(),
                values=[
                    self(node.args[0], env.rep(ctx=past.Load())),
                    self(node.args[1], env.rep(ctx=past.Load()))
                ]
            )

        elif op == 'or':
            assert len(node.args) == 2
            return past.BoolOp(
                op=past.Or(),
                values=[
                    self(node.args[0], env.rep(ctx=past.Load())),
                    self(node.args[1], env.rep(ctx=past.Load()))
                ]
            )

        elif op == '=>':
            assert len(node.args) == 2
            return past.BoolOp(
                op=past.Or(),
                values=[
                    past.UnaryOp(
                        op=past.Not(),
                        operand=self(node.args[0], env.rep(ctx=past.Load()))
                    ),
                    self(node.args[1], env.rep(ctx=past.Load()))
                ]
            )

        elif op == '&':
            assert len(node.args) == 2
            return past.BinOp(
                left=self(node.args[0], env.rep(ctx=past.Load())),
                op=past.BitAnd(),
                right=self(node.args[1], env.rep(ctx=past.Load()))
            )

        elif op == '|':
            assert len(node.args) == 2
            return past.BinOp(
                left=self(node.args[0], env.rep(ctx=past.Load())),
                op=past.BitOr(),
                right=self(node.args[1], env.rep(ctx=past.Load()))
            )

        elif op == '^':
            assert len(node.args) == 2
            return past.BinOp(
                left=self(node.args[0], env.rep(ctx=past.Load())),
                op=past.BitXor(),
                right=self(node.args[1], env.rep(ctx=past.Load()))
            )

        elif op in {'//', '/'}:
            assert len(node.args) == 2
            return past.BinOp(
                left=self(node.args[0], env.rep(ctx=past.Load())),
                op=past.FloorDiv(),
                right=self(node.args[1], env.rep(ctx=past.Load()))
            )

        elif op in {'%', 'mod'}:
            assert len(node.args) == 2
            return past.BinOp(
                left=self(node.args[0], env.rep(ctx=past.Load())),
                op=past.Mod(),
                right=self(node.args[1], env.rep(ctx=past.Load()))
            )

        elif op in {'**'}:
            assert len(node.args) == 2
            return past.BinOp(
                left=self(node.args[0], env.rep(ctx=past.Load())),
                op=past.Pow(),
                right=self(node.args[1], env.rep(ctx=past.Load()))
            )

        elif op == '<<':
            assert len(node.args) == 2
            return past.BinOp(
                left=self(node.args[0], env.rep(ctx=past.Load())),
                op=past.LShift(),
                right=self(node.args[1], env.rep(ctx=past.Load()))
            )

        elif op == '>>':
            assert len(node.args) == 2
            return past.BinOp(
                left=self(node.args[0], env.rep(ctx=past.Load())),
                op=past.RShift(),
                right=self(node.args[1], env.rep(ctx=past.Load()))
            )

        elif op == 'choose':
            assert len(node.args) == 1
            return past.Call(
                func=past.Name(id='choose', ctx=env.get('ctx')),
                args=[self(node.args[0], env)],
                keywords=[]
            )

        else:
            raise NotImplementedError(op)

    def visit_cmp(self, node: hast.CmpAST, env: H2PyEnv):
        assert(len(node.ops) == 1)

        op = node.ops[0][T_TOKEN]
        if op == '==':
            return past.Compare(
                left=self(node.args[0], env.rep(ctx=past.Load())),
                ops=[past.Eq()],
                comparators=[
                    self(node.args[1], env.rep(ctx=past.Load())),
                ]
            )

        elif op == '!=':
            return past.Compare(
                left=self(node.args[0], env.rep(ctx=past.Load())),
                ops=[past.NotEq()],
                comparators=[
                    self(node.args[1], env.rep(ctx=past.Load())),
                ]
            )

        elif op == '<':
            return past.Compare(
                left=self(node.args[0], env.rep(ctx=past.Load())),
                ops=[past.Lt()],
                comparators=[
                    self(node.args[1], env.rep(ctx=past.Load())),
                ]
            )

        elif op == '<=':
            return past.Compare(
                left=self(node.args[0], env.rep(ctx=past.Load())),
                ops=[past.LtE()],
                comparators=[
                    self(node.args[1], env.rep(ctx=past.Load())),
                ]
            )

        elif op == '>':
            return past.Compare(
                left=self(node.args[0], env.rep(ctx=past.Load())),
                ops=[past.Gt()],
                comparators=[
                    self(node.args[1], env.rep(ctx=past.Load())),
                ]
            )

        elif op == '>=':
            return past.Compare(
                left=self(node.args[0], env.rep(ctx=past.Load())),
                ops=[past.GtE()],
                comparators=[
                    self(node.args[1], env.rep(ctx=past.Load())),
                ]
            )

        else:
            raise NotImplementedError(op)

    def visit_constant(self, node: hast.ConstantAST, env: H2PyEnv):
        return past.Constant(value=node.const[T_TOKEN])

    def visit_tuple(self, node: hast.TupleAST, env: H2PyEnv):
        return past.Tuple(
            elts=[self(subnode, env) for subnode in node.list],
            ctx=env.get('ctx')
        )

    def visit_dict(self, node: hast.DictAST, env: H2PyEnv):
        return past.Call(
            func=past.Name(id='H', ctx=past.Load()),
            args=[
                past.Dict(
                    keys=[self(key, env) for key, _ in node.record],
                    values=[self(value, env) for _, value in node.record]
                )
            ],
            keywords=[]
        )

    def visit_apply(self, node: hast.ApplyAST, env: H2PyEnv):
        def convert_arg(arg):
            if isinstance(arg, list):
                result = []
                for subarg in arg:
                    result += convert_arg(subarg)
                return result

            elif isinstance(arg, hast.TupleAST):
                return convert_arg(arg.list)

            else:
                assert isinstance(arg, hast.AST)
                return [self(arg, env)]

        if isinstance(node.method, hast.NameAST):
            if ( # omit empty tuple when calling function with no arguments
                isinstance(node.arg, hast.ConstantAST) 
                and isinstance(node.arg.const[T_TOKEN], hvalue.ListValue)
                and len(node.arg.const[T_TOKEN]) == 0
            ):
                return past.Call(
                    func=past.Name(id=node.method.name[T_TOKEN], ctx=past.Load()),
                    args=[],
                    keywords=[]
                )

            else:
                return past.Call(
                    func=past.Name(id=node.method.name[T_TOKEN], ctx=past.Load()),
                    args=convert_arg(node.arg),
                    keywords=[]
                )

        elif isinstance(node.method, hast.PointerAST):
            return past.Call(
                func=self(node.method, env),
                args=convert_arg(node.arg),
                keywords=[]
            )

        else:
            raise NotImplementedError(node)

    def visit_pointer(self, node: hast.PointerAST, env: H2PyEnv):
        return past.Call(
            func=past.Attribute(
                value=self(node.expr, env.rep(ctx=past.Load())),
                attr='get'
            ),
            args=[],
            keywords=[]
        )

    def visit_address(self, node: hast.AddressAST, env: H2PyEnv):
        def convert_addr_lv(lv):
            if isinstance(lv, hast.NameAST):
                # ?lv
                return past.Constant(value=lv.name[T_TOKEN])

            elif isinstance(lv, hast.ApplyAST):
                # ?(lv.method)[lv.arg]
                return past.Tuple(elts=[convert_addr_lv(lv.method), self(lv.arg, env.rep(ctx=past.Load()))])

            elif isinstance(lv, hast.PointerAST):
                # ?(!lv.expr)
                #
                # lv.expr must evaluate to an HAddr already, so we directly
                # translate that

                return self(lv.expr, env.rep(ctx=past.Load()))

            else:
                raise NotImplementedError(f'Unable to convert addr lv {lv}')

        return past.Call(
            func=past.Name(id='HAddr', ctx=past.Load()),
            args=[convert_addr_lv(node.lv)],
            keywords=[]
        )
