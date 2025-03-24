from typing import Any, Union
from antlr4.Token import CommonToken  # type: ignore

from symphony_model_checker.parser.SymphonyVisitor import SymphonyVisitor
from symphony_model_checker.parser.SymphonyParser import SymphonyParser
from symphony_model_checker.symphony.ast import *

class SymphonyVisitorImpl(SymphonyVisitor):

    def __init__(self, file: str):
        assert isinstance(file, str)
        self.file = file
        self.associative_operators = { "+", "*", "|", "&", "^", "and", "or" }

    def get_token(self, tkn: Union[CommonToken, tuple], value: Any) -> tuple:
        if isinstance(tkn, CommonToken):
            line = tkn.line
            col = tkn.column + 1
        else:
            line = tkn[2]
            col = tkn[3]

        assert isinstance(col, int)
        assert isinstance(line, int)

        return value, self.file, line, col

    # Visit a parse tree produced by SymphonyParser#import_stmt.
    def visitImport_stmt(self, ctx: SymphonyParser.Import_stmtContext):
        if ctx.import_from():
            return self.visit(ctx.import_from())
        elif ctx.import_name():
            return self.visit(ctx.import_name())
        tkn = self.get_token(ctx.start, ctx.start.text)
        raise SymphonyCompilerError(
            message="Failed to parse import",
            filename=self.file,
            line=tkn[2],
            column=tkn[3],
            lexeme=tkn[0]
        )

    # Visit a parse tree produced by SymphonyParser#import_name.
    def visitImport_name(self, ctx: SymphonyParser.Import_nameContext):
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return ImportAST(endtoken, tkn, False, self.visit(ctx.import_names_seq()))

    # Visit a parse tree produced by SymphonyParser#import_from.
    def visitImport_from(self, ctx: SymphonyParser.Import_fromContext):
        dotted_name = self.get_token(ctx.NAME().symbol, str(ctx.NAME()))
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        if ctx.STAR():
            return FromAST(endtoken, tkn, False, dotted_name, [])
        names = self.visit(ctx.import_names_seq())
        return FromAST(endtoken, tkn, False, dotted_name, names)
    
    def visitImport_names_seq(self, ctx: SymphonyParser.Import_names_seqContext):
        return [self.get_token(d.symbol, str(d)) for d in ctx.NAME()]
    
    def visitSequential_names_seq(self, ctx: SymphonyParser.Sequential_names_seqContext):
        return [self.get_token(d.symbol, str(d)) for d in ctx.NAME()]

    # Visit a parse tree produced by SymphonyParser#program.
    def visitProgram(self, ctx: SymphonyParser.ProgramContext):
        stmts = [s for stmt in ctx.stmt() for s in self.visit(stmt) if s is not None]
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        if len(stmts) == 0:
            raise SymphonyCompilerError(
                message="Empty program",
                filename=self.file,
                line=tkn[2],
                column=tkn[3],
                lexeme=tkn[0]
            )
        return BlockAST(endtoken, tkn, False, stmts, endtoken)

    # Visit a parse tree produced by SymphonyParser#tuple_bound.
    def visitTuple_bound(self, ctx:SymphonyParser.Tuple_boundContext):
        if ctx.bound() is not None:
            return self.visit(ctx.bound())
        if ctx.NAME():
            name = ctx.NAME()
            return self.get_token(name.symbol, str(name))
        return []

    # Visit a parse tree produced by SymphonyParser#bound.
    def visitBound(self, ctx: SymphonyParser.BoundContext):
        bv = [self.visit(t) for t in ctx.tuple_bound()]
        if len(bv) == 1:
            return bv[0]
        return bv

    # Visit a parse tree produced by SymphonyParser#unary_op.
    def visitUnary_op(self, ctx: SymphonyParser.Unary_opContext):
        return self.get_token(ctx.start, ctx.getText())

    # Visit a parse tree produced by SymphonyParser#int.
    def visitInt(self, ctx: SymphonyParser.IntContext):
        txt = ctx.getText()
        tkn = self.get_token(ctx.start, int(txt, 0))
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return ConstantAST(endtoken, tkn)

    # Visit a parse tree produced by SymphonyParser#bool.
    def visitBool(self, ctx: SymphonyParser.BoolContext):
        txt = ctx.getText()
        tkn = self.get_token(ctx.start, txt == 'True')
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return ConstantAST(endtoken, tkn)

    # Visit a parse tree produced by SymphonyParser#atom.
    def visitAtom(self, ctx: SymphonyParser.AtomContext):
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        lexeme = ctx.getText()
        if lexeme.startswith("0x"):
            v = chr(int(lexeme, 16))
            tkn = self.get_token(ctx.start, v)
            return ConstantAST(endtoken, tkn)
        else:
            tkn = self.get_token(ctx.start, lexeme[1:])
            return ConstantAST(endtoken, tkn)

    # Visit a parse tree produced by SymphonyParser#name.
    def visitName(self, ctx: SymphonyParser.NameContext):
        tkn = self.get_token(ctx.start, ctx.getText())
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return NameAST(endtoken, tkn)

    # Visit a parse tree produced by SymphonyParser#str.
    def visitStr(self, ctx: SymphonyParser.StrContext):
        value = ctx.getText()
        if value.startswith("'''") and value.endswith("'''"):
            s = value[3:-3]
        elif value.startswith('"""') and value.endswith('"""'):
            s = value[3:-3]
        elif value.startswith("'") and value.endswith("'"):
            s = value[1:-1]
        elif value.startswith('"') and value.endswith('"'):
            s = value[1:-1]
        else:
            tkn = self.get_token(ctx.start, value)
            raise SymphonyCompilerError(
                message="Unable to parse string",
                filename=self.file,
                line=tkn[2],
                column=tkn[3],
                lexeme=tkn[0]
            )
        tkn = self.get_token(ctx.start, s)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return ConstantAST(endtoken, tkn)

    def visitPrint_stmt(self, ctx: SymphonyParser.Print_stmtContext):
        cond = self.visit(ctx.expr())
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return PrintAST(endtoken, tkn, False, cond)

    # Visit a parse tree produced by SymphonyParser#none.
    def visitNone(self, ctx: SymphonyParser.NoneContext):
        tkn = self.get_token(ctx.start, AddressValue(None, []))
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return ConstantAST(endtoken, tkn)

    # Visit a parse tree produced by SymphonyParser#address.
    # def visitAddress(self, ctx: SymphonyParser.AddressContext):
    #     expr = self.visit(ctx.expr_rule())
    #     tkn = self.get_token(ctx.start, ctx.start.text)
    #     endtoken = self.get_token(ctx.stop, ctx.stop.text)
    #     return AddressAST(endtoken, tkn, expr)

    # Visit a parse tree produced by SymphonyParser#assign_op.
    def visitAssign_op(self, ctx: SymphonyParser.Assign_opContext):
        return self.get_token(ctx.start, ctx.getText())

    # Visit a parse tree produced by SymphonyParser#aug_assign_op.
    def visitAug_assign_op(self, ctx: SymphonyParser.Aug_assign_opContext):
        return self.get_token(ctx.start, ctx.getText())

    # Visit a parse tree produced by SymphonyParser#expr_stmt.
    def visitExpr_stmt(self, ctx: SymphonyParser.Expr_stmtContext):
        e = self.visit(ctx.expr_rule())
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return CallAST(endtoken, tkn, False, e)

    # Visit a parse tree produced by SymphonyParser#assign_stmt.
    def visitAssign_stmt(self, ctx: SymphonyParser.Assign_stmtContext):
        ops = [self.visit(e) for e in ctx.assign_op()]
        expr = [self.visit(e) for e in ctx.tuple_rule()]
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return AssignmentAST(endtoken, tkn, expr[:-1], expr[-1], ops, False)

    # Visit a parse tree produced by SymphonyParser#aug_assign_stmt.
    def visitAug_assign_stmt(self, ctx: SymphonyParser.Aug_assign_stmtContext):
        op = self.visit(ctx.aug_assign_op())
        expressions = [self.visit(e) for e in ctx.tuple_rule()]
        lhs = expressions[0]
        rhs = expressions[1]
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return AuxAssignmentAST(endtoken, tkn, lhs, rhs, op, False)

    # Visit a parse tree produced by SymphonyParser#const_assign_stmt.
    def visitConst_assign_stmt(self, ctx: SymphonyParser.Const_assign_stmtContext):
        lvalues = self.visit(ctx.bound())
        value = self.visit(ctx.expr())
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return ConstAST(endtoken, tkn, False, lvalues, value)

    # Visit a parse tree produced by SymphonyParser#assert_stmt.
    def visitAssert_stmt(self, ctx: SymphonyParser.Assert_stmtContext):
        assertion = self.visit(ctx.expr(0))
        msg = self.visit(ctx.expr(1)) if ctx.expr(1) is not None else None
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return AssertAST(endtoken, tkn, False, assertion, msg)

    # Visit a parse tree produced by SymphonyParser#await_stmt.
    def visitAwait_stmt(self, ctx: SymphonyParser.Await_stmtContext):
        cond = self.visit(ctx.expr())
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return LetWhenAST(endtoken, tkn, False, [('cond', cond, tkn, endtoken)], PassAST(endtoken, tkn, False))

    # Visit a parse tree produced by SymphonyParser#trap_stmt.
    def visitTrap_stmt(self, ctx: SymphonyParser.Trap_stmtContext):
        func = self.visit(ctx.expr())
        # if not isinstance(func, ApplyAST):
        #     tkn = self.get_token(func.token, func.token[0])
        #     raise SymphonyCompilerError(
        #         message="Expected a method call but found something else.",
        #         filename=self.file,
        #         line=tkn[2],
        #         column=tkn[3],
        #         lexeme=tkn[0]
        #     )
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return TrapAST(endtoken, tkn, False, func)

    # Visit a parse tree produced by SymphonyParser#pass_stmt.
    def visitPass_stmt(self, ctx: SymphonyParser.Pass_stmtContext):
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return PassAST(endtoken, tkn, False)

    # Visit a parse tree produced by SymphonyParser#Finally_stmt.
    def visitFinally_stmt(self, ctx: SymphonyParser.Finally_stmtContext):
        cond = self.visit(ctx.expr())
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return FinallyAST(endtoken, cond, tkn, False)

    # Visit a parse tree produced by SymphonyParser#invariant_stmt.
    def visitInvariant_stmt(self, ctx: SymphonyParser.Invariant_stmtContext):
        cond = self.visit(ctx.expr())
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return InvariantAST(endtoken, cond, tkn, False)

    # Visit a parse tree produced by SymphonyParser#del_stmt.
    def visitDel_stmt(self, ctx: SymphonyParser.Del_stmtContext):
        e = self.visit(ctx.expr())
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return DelAST(endtoken, tkn, False, e)

    def visitSimple_stmt(self, ctx: SymphonyParser.Simple_stmtContext):
        if ctx.ATOMICALLY():
            a = self.visit(ctx.children[-1])
            assert isinstance(a, AST)
            atom = ctx.ATOMICALLY()
            a.atomically = self.get_token(atom.getSymbol(), atom.getText())
            return a
        return super().visitSimple_stmt(ctx)

    def visitCompound_stmt(self, ctx: SymphonyParser.Compound_stmtContext):
        if ctx.ATOMICALLY():
            a = self.visit(ctx.children[-1])
            assert isinstance(a, AST)
            atom = ctx.ATOMICALLY()
            a.atomically = self.get_token(atom.getSymbol(), atom.getText())
            return a
        return super().visitCompound_stmt(ctx)

    # Visit a parse tree produced by SymphonyParser#spawn_stmt.
    def visitSpawn_stmt(self, ctx: SymphonyParser.Spawn_stmtContext):
        is_eternal = ctx.ETERNAL() is not None
        target = self.visit(ctx.expr())
        # if not isinstance(target, ApplyAST):
        #     tkn = self.get_token(target.token, target.token[0])
        #     raise SymphonyCompilerError(
        #         message="Expected a method call but found something else.",
        #         filename=self.file,
        #         line=tkn[2],
        #         column=tkn[3],
        #         lexeme=tkn[0]
        #     )
        # method, arg = target.method, target.arg
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        # return SpawnAST(endtoken, tkn, False, method, arg, None, is_eternal)
        return SpawnAST(endtoken, tkn, False, target, None, is_eternal)

    # Visit a parse tree produced by SymphonyParser#go_stmt.
    def visitGo_stmt(self, ctx: SymphonyParser.Go_stmtContext):
        target = self.visit(ctx.expr(0))
        args = self.visit(ctx.expr(1))
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return GoAST(endtoken, tkn, False, target, args)

    # Visit a parse tree produced by SymphonyParser#sequential_stmt.
    def visitSequential_stmt(self, ctx: SymphonyParser.Sequential_stmtContext):
        expr = self.visit(ctx.sequential_names_seq())
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return SequentialAST(endtoken, tkn, False, expr)

    # Visit a parse tree produced by SymphonyParser#global_stmt.
    def visitGlobal_stmt(self, ctx: SymphonyParser.Global_stmtContext):
        expr = [self.visit(e) for e in ctx.expr()]
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return GlobalAST(endtoken, tkn, False, expr)

    # Visit a parse tree produced by SymphonyParser#builtin_stmt.
    def visitBuiltin_stmt(self, ctx: SymphonyParser.Builtin_stmtContext):
        name = str(ctx.NAME())
        nametkn = self.get_token(ctx.NAME().symbol, name)
        value = str(ctx.STRING())[1:-1]     # remove quotes
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return BuiltinAST(endtoken, tkn, NameAST(nametkn, nametkn), value)

    # Visit a parse tree produced by SymphonyParser#atomic_block.
    def visitAtomic_block(self, ctx: SymphonyParser.Atomic_blockContext):
        stmts = self.visit(ctx.block())
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        atom = ctx.ATOMICALLY()
        atoken = self.get_token(atom.getSymbol(), atom.getText())
        colon = ctx.COLON()
        ctoken = self.get_token(colon.getSymbol(), colon.getText())
        return AtomicAST(endtoken, tkn, atoken, stmts, ctoken)

    # Visit a parse tree produced by SymphonyParser#for_block.
    def visitFor_block(self, ctx: SymphonyParser.For_blockContext):
        iterables = self.visit(ctx.iter_parse())
        stmts = self.visit(ctx.block())
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return ForAST(endtoken, iterables, stmts, tkn, False)

    # Visit a parse tree produced by SymphonyParser#let_decl.
    def visitLet_decl(self, ctx: SymphonyParser.Let_declContext):
        lvalues = self.visit(ctx.bound())
        values = self.visit(ctx.tuple_rule())
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        op = self.visit(ctx.assign_op())
        return "var", lvalues, values, tkn, endtoken, op

    # Visit a parse tree produced by SymphonyParser#when_decl.
    def visitWhen_decl(self, ctx:SymphonyParser.When_declContext):
        expr = self.visit(ctx.expr())
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        if ctx.EXISTS() is not None:
            bv = self.visit(ctx.bound())
            return 'exists', bv, expr, tkn, endtoken
        else:
            return 'cond', expr, tkn, endtoken

    # Visit a parse tree produced by SymphonyParser#let_when_decl.
    def visitLet_when_decl(self, ctx:SymphonyParser.Let_when_declContext):
        decl = []
        if ctx.when_decl() is not None:
            decl.append(self.visit(ctx.when_decl()))
        elif ctx.let_decl() is not None:
            decl.append(self.visit(ctx.let_decl()))
        else:
            tkn = self.get_token(ctx.start, ctx.start.text)
            raise SymphonyCompilerError(
                message="Unexpected declaration in let/when block declaration.",
                filename=self.file,
                line=tkn[2],
                column=tkn[3],
                lexeme=tkn[0]
            )
        if ctx.let_when_decl() is not None:
            decl.extend(self.visit(ctx.let_when_decl()))
        return decl

    # Visit a parse tree produced by SymphonyParser#let_when_block.
    def visitLet_when_block(self, ctx:SymphonyParser.Let_when_blockContext):
        vars_and_conds = self.visit(ctx.let_when_decl())
        stmts = self.visit(ctx.block())
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        if all(vac[0] == 'var' for vac in vars_and_conds):
            vars = [vac[1:] for vac in vars_and_conds if vac[0] == 'var']
            return LetAST(endtoken, tkn, False, vars, stmts)
        else:
            return LetWhenAST(endtoken, tkn, False, vars_and_conds, stmts)

    # Visit a parse tree produced by SymphonyParser#opt_returns.
    def visitOpt_returns(self, ctx: SymphonyParser.Opt_returnsContext):
        return ctx.NAME()

    # Visit a parse tree produced by SymphonyParser#method_decl.
    def visitMethod_decl(self, ctx: SymphonyParser.Method_declContext):
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        value = str(ctx.NAME())
        method_name = self.get_token(ctx.NAME().symbol, value)
        args = self.visit(ctx.bound()) if ctx.bound() else []
        if ctx.opt_returns() is None:
            result_name = None
        else:
            ors = self.visit(ctx.opt_returns())
            result_name = self.get_token(ors.symbol, str(ors))
        body = self.visit(ctx.block())
        colon = ctx.COLON()
        ctoken = self.get_token(colon.getSymbol(), colon.getText())
        ast = MethodAST(endtoken, tkn, False, method_name, args, result_name, body, ctoken)
        return ast

    # Visit a parse tree produced by SymphonyParser#while_block.
    def visitWhile_block(self, ctx: SymphonyParser.While_blockContext):
        cond = self.visit(ctx.expr())
        stmts = self.visit(ctx.block())
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        colon = ctx.COLON()
        ctoken = self.get_token(colon.getSymbol(), colon.getText())
        return WhileAST(endtoken, tkn, False, cond, stmts, ctoken)

    # Visit a parse tree produced by SymphonyParser#if_block.
    def visitIf_block(self, ctx: SymphonyParser.If_blockContext):
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        colon = ctx.COLON()
        ctoken = self.get_token(colon.getSymbol(), colon.getText())
        cond = self.visit(ctx.expr())
        if_block = self.visit(ctx.block())
        alts = [(cond, if_block, tkn, endtoken, ctoken)]
        else_block = None
        if ctx.elif_block() is not None:
            for c in ctx.elif_block():
                alts.append(self.visit(c))
        if ctx.else_block() is not None:
            else_block = self.visit(ctx.else_block())
        return IfAST(endtoken, tkn, False, alts, else_block)

    # Visit a parse tree produced by SymphonyParser#elif_block.
    def visitElif_block(self, ctx: SymphonyParser.Elif_blockContext):
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        colon = ctx.COLON()
        ctoken = self.get_token(colon.getSymbol(), colon.getText())
        cond = self.visit(ctx.expr())
        stmts = self.visit(ctx.block())
        return cond, stmts, tkn, endtoken, ctoken

    # Visit a parse tree produced by SymphonyParser#else_block.
    def visitElse_block(self, ctx: SymphonyParser.Else_blockContext):
        return self.visit(ctx.block())

    # Visit a parse tree produced by SymphonyParser#var_stmt.
    def visitVar_stmt(self, ctx:SymphonyParser.Var_stmtContext):
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        lv = self.visit(ctx.bound())
        e = self.visit(ctx.tuple_rule())
        return VarAST(endtoken, tkn, False, [(lv, e)])

    # Visit a parse tree produced by SymphonyParser#normal_block.
    def visitNormal_block(self, ctx: SymphonyParser.Normal_blockContext):
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        if ctx.block() is not None:
            return self.visit(ctx.block())
        elif ctx.block_stmts() is not None:
            stmts = self.visit(ctx.block_stmts())
            return BlockAST(endtoken, tkn, False, stmts, endtoken)
        raise SymphonyCompilerError(
            message="Unexpected block structure.",
            filename=self.file,
            line=tkn[2],
            column=tkn[3],
            lexeme=tkn[0]
        )

    # Visit a parse tree produced by SymphonyParser#block_stmts.
    def visitBlock_stmts(self, ctx: SymphonyParser.Block_stmtsContext):
        block = [s for stmt in ctx.stmt() for s in self.visit(stmt)]
        return [s for s in block if s is not None]

    # Visit a parse tree produced by SymphonyParser#label.
    def visitLabel(self, ctx: SymphonyParser.LabelContext):
        names = [self.get_token(n.symbol, str(n)) for n in ctx.NAME()]
        return names

    # Visit a parse tree produced by SymphonyParser#stmt.
    def visitStmt(self, ctx: SymphonyParser.StmtContext):
        labels = []
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        if ctx.label() is not None:
            labels = self.visit(ctx.label())
        if ctx.one_line_stmt() is not None:
            stmt = self.visit(ctx.one_line_stmt())
        elif ctx.compound_stmt() is not None:
            stmt = self.visit(ctx.compound_stmt())
        elif ctx.import_stmt() is not None:
            stmt = self.visit(ctx.import_stmt())
        elif ctx.normal_block() is not None:
            stmt = self.visit(ctx.normal_block())
        else:
            return []

        assert stmt is not None
        if isinstance(stmt, AST):
            stmt_block = [LocationAST(endtoken, tkn, stmt, self.file, tkn[2])]
        elif isinstance(stmt, list):
            stmt_block = [LocationAST(endtoken, tkn, s, self.file, tkn[2]) for s in stmt]
        if ctx.COLON() or labels:
            if ctx.COLON():
                colon = ctx.COLON()
                ctoken = self.get_token(colon.getSymbol(), colon.getText())
                block = BlockAST(endtoken, tkn, False, stmt_block, ctoken)
            else:
                block = BlockAST(endtoken, tkn, False, stmt_block, endtoken)
            if labels:
                return [LocationAST(endtoken, tkn, LabelStatAST(endtoken, tkn, labels, block), self.file, tkn[2])]
            else:
                return [block]
        return stmt_block

    def visitBlock(self, ctx: SymphonyParser.BlockContext):
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        if ctx.normal_block():
            return self.visit(ctx.normal_block())
        elif ctx.one_line_stmt():
            return BlockAST(endtoken, tkn, False, self.visit(ctx.one_line_stmt()), endtoken)
        raise SymphonyCompilerError(
            message="Unable to parse block",
            filename=self.file,
            line=tkn[2],
            column=tkn[3],
            lexeme=tkn[0]
        )

    # Visit a parse tree produced by SymphonyParser#one_line_stmt.
    def visitOne_line_stmt(self, ctx: SymphonyParser.One_line_stmtContext):
        stmts = [self.visit(ctx.simple_stmt())]
        if ctx.one_line_stmt():
            stmts.extend(self.visit(ctx.one_line_stmt()))
        return stmts

    # Visit a parse tree produced by SymphonyParser#arith_op.
    def visitArith_op(self, ctx:SymphonyParser.Arith_opContext):
        return self.get_token(ctx.start, ctx.getText())

    # Visit a parse tree produced by SymphonyParser#set_rule_1.
    def visitSet_rule_1(self, ctx: SymphonyParser.Set_rule_1Context):
        if ctx.set_rule():
            return self.visit(ctx.set_rule())
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return SetAST(endtoken, self.get_token(ctx.start, ctx.start.text), [])

    # Visit a parse tree produced by SymphonyParser#empty_dict.
    def visitEmpty_dict(self, ctx: SymphonyParser.Empty_dictContext):
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return DictAST(endtoken, self.get_token(ctx.start, ctx.start.text), [])

    # Visit a parse tree produced by SymphonyParser#paren_tuple.
    def visitParen_tuple(self, ctx: SymphonyParser.Paren_tupleContext):
        if ctx.tuple_rule():
            return self.visit(ctx.tuple_rule())
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return ConstantAST(endtoken, (emptytuple, self.file, tkn[2], tkn[3]))

    # Visit a parse tree produced by SymphonyParser#brack_tuple.
    def visitBracket_tuple(self, ctx: SymphonyParser.Bracket_tupleContext):
        if ctx.tuple_rule():
            return self.visit(ctx.tuple_rule())
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return ConstantAST(endtoken, (emptytuple, self.file, tkn[2], tkn[3]))

    def visitLambda_expr(self, ctx: SymphonyParser.Lambda_exprContext):
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        args = self.visit(ctx.bound()) if ctx.bound() is not None else []
        body = self.visit(ctx.nary_expr())
        return LambdaAST(endtoken, args, body, tkn, False)

    # Visit a parse tree produced by SymphonyParser#set_rule.
    def visitSet_rule(self, ctx: SymphonyParser.Set_ruleContext):
        values = [self.visit(e) for e in ctx.nary_expr()]
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        if ctx.COLON():
            if ctx.iter_parse():
                k, v = values[0], values[1]
                comp = self.visit(ctx.iter_parse())
                return DictComprehensionAST(endtoken, k, v, comp, tkn)
            k = values[::2]
            v = values[1::2]
            return DictAST(endtoken, tkn, list(zip(k, v)))
        if ctx.iter_parse():
            comp = self.visit(ctx.iter_parse())
            return SetComprehensionAST(endtoken, values[0], comp, tkn)
        if ctx.RANGE():
            return RangeAST(endtoken, values[0], values[1], tkn)
        if ctx.COMMA():
            return SetAST(endtoken, tkn, values)
        return SetAST(endtoken, tkn, [values[0]])

    # Visit a parse tree produced by SymphonyParser#iter_parse.
    def visitIter_parse(self, ctx: SymphonyParser.Iter_parseContext):
        v = [self.visit(e) for e in ctx.children]
        return [x for x in v if x is not None]

    # Visit a parse tree produced by SymphonyParser#for_parse.
    def visitFor_parse(self, ctx: SymphonyParser.For_parseContext):
        l1 = self.visit(ctx.bound(0))
        l2 = self.visit(ctx.bound(1)) if ctx.bound(1) else None
        expr = self.visit(ctx.nary_expr())
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        if l2 is not None:
            return "for", (l2, l1, expr, tkn, endtoken)
        else:
            return "for", (l1, None, expr, tkn, endtoken)

    # Visit a parse tree produced by SymphonyParser#where_parse.
    def visitWhere_parse(self, ctx: SymphonyParser.Where_parseContext):
        expr = self.visit(ctx.nary_expr())
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        return "where", (expr, tkn, endtoken)

    # Visit a parse tree produced by SymphonyParser#tuple_rule.
    def visitTuple_rule(self, ctx: SymphonyParser.Tuple_ruleContext):
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        values = [self.visit(e) for e in ctx.nary_expr()]
        if ctx.iter_parse():
            iterators = self.visit(ctx.iter_parse())
            return ListComprehensionAST(endtoken, values[0], iterators, tkn)
        comma_count = len(ctx.COMMA())
        if len(values) == 1 and comma_count != 1:
            return values[0]
        return TupleAST(endtoken, values, tkn)

    def factor_expr(self, ops, exprs):
        if len(ops) == 0:
            return exprs[0]
        if len(ops) == 1:
            return NaryAST(exprs[1].endtoken, exprs[0].token, ops[0], exprs)
        found = False
        for o in ops:
            if o[0] in { '/', '//', '%', 'mod' }:
                if found:
                    token = ops[0]
                    raise SymphonyCompilerError(
                        message="Expression too complicated: use parentheses",
                        filename=self.file,
                        line=token[2],
                        column=token[3],
                        lexeme=token[0]
                    )
                found = True
            else:
                assert o[0] == '*'
        return NaryAST(exprs[-1].endtoken, exprs[0].token, ops[-1],
            [ NaryAST(exprs[-2].endtoken, exprs[0].token, ops[0], exprs[:-1]), exprs[-1] ])

    def simple_expr(self, ops, exprs):
        simple_ops = [ o for o in ops if o[0] in { '+', '-' } ]
        if len(simple_ops) == 0:
            return self.factor_expr(ops, exprs)
        sub_ops = []
        sub_exprs = [ exprs[0] ]
        sub_asts = []
        for i in range(len(ops)):
            if ops[i] in simple_ops:
                sub_asts.append(self.factor_expr(sub_ops, sub_exprs))
                sub_ops = []
                sub_exprs = [ exprs[i+1] ]
            else:
                sub_ops.append(ops[i])
                sub_exprs.append(exprs[i+1])
        sub_asts.append(self.factor_expr(sub_ops, sub_exprs))
        ast = sub_asts[0]
        for i in range(len(simple_ops)):
            ast = NaryAST(sub_asts[i+1].endtoken, sub_asts[0].token, simple_ops[i], [ ast, sub_asts[i+1] ])
        return ast

    def arith_expr(self, ops, exprs):
        assert len(ops) + 1 == len(exprs)
        if len(ops) == 0:
            return exprs[0]
        if len(ops) == 1:
            return NaryAST(exprs[1].endtoken, exprs[0].token, ops[0], exprs)

        # See if all are the same associative operator
        if ops[0][0] in self.associative_operators and all(o[0] == ops[0][0] for o in ops):
            return NaryAST(exprs[-1].endtoken, exprs[0].token, ops[0], exprs)

        # See if it's a simple arithmetic expression
        if all(o[0] in { '+', '-', '*', '/', '//', '%', 'mod' } for o in ops):
            return self.simple_expr(ops, exprs)

        token = ops[0]
        raise SymphonyCompilerError(
            message="Expression too complicated: use parentheses",
            filename=self.file,
            line=token[2],
            column=token[3],
            lexeme=token[0]
        )

    def cmp_expr(self, ops, exprs):
        assert len(ops) + 1 == len(exprs)
        if len(ops) == 0:
            return exprs[0]
        cmp_ops = [ o for o in ops if o[0] in { '==', '!=', '<', '<=', '>', '>=' } ]
        if len(cmp_ops) == 0:
            return self.arith_expr(ops, exprs)
        sub_ops = []
        sub_exprs = [ exprs[0] ]
        sub_asts = []
        for i in range(len(ops)):
            if ops[i] in cmp_ops:
                sub_asts.append(self.arith_expr(sub_ops, sub_exprs))
                sub_ops = []
                sub_exprs = [ exprs[i+1] ]
            else:
                sub_ops.append(ops[i])
                sub_exprs.append(exprs[i+1])
        sub_asts.append(self.arith_expr(sub_ops, sub_exprs))
        return CmpAST(sub_asts[-1].endtoken, sub_asts[0].token, cmp_ops, sub_asts)

    def bool_expr_helper(self, ops, exprs, operator):
        op = None
        sub_ops = []
        sub_exprs = [ exprs[0] ]
        sub_asts = []
        for i in range(len(ops)):
            if ops[i][0] == operator:
                if op == None:
                    op = ops[i]
                sub_asts.append(self.cmp_expr(sub_ops, sub_exprs))
                sub_ops = []
                sub_exprs = [ exprs[i+1] ]
            else:
                sub_ops.append(ops[i])
                sub_exprs.append(exprs[i+1])
        sub_asts.append(self.cmp_expr(sub_ops, sub_exprs))
        return NaryAST(sub_asts[-1].endtoken, sub_asts[0].token, op, sub_asts)

    def bool_expr(self, ops, exprs):
        assert len(ops) > 0
        assert len(ops) + 1 == len(exprs)
        bool_ops = [ o[0] for o in ops if o[0] in { 'or', 'and', '=>', '==', '=' } ]
        if 'or' in bool_ops:
            if len(set(bool_ops)) > 1:
                token = ops[0]
                raise SymphonyCompilerError(
                    message="Boolean expression too complicated: use parentheses",
                    filename=self.file,
                    line=token[2],
                    column=token[3],
                    lexeme=token[0]
                )
            return self.bool_expr_helper(ops, exprs, 'or')
        if 'and' in bool_ops:
            if len(set(bool_ops)) > 1:
                token = ops[0]
                raise SymphonyCompilerError(
                    message="Boolean expression too complicated: use parentheses",
                    filename=self.file,
                    line=token[2],
                    column=token[3],
                    lexeme=token[0]
                )
            return self.bool_expr_helper(ops, exprs, 'and')
        if '=>' in bool_ops:
            if len(bool_ops) > 1:
                token = ops[0]
                raise SymphonyCompilerError(
                    message="Boolean imply expression too complicated: use parentheses",
                    filename=self.file,
                    line=token[2],
                    column=token[3],
                    lexeme=token[0]
                )
            return self.bool_expr_helper(ops, exprs, '=>')
        return self.cmp_expr(ops, exprs)

    # Visit a parse tree produced by SymphonyParser#nary_expr.
    def visitNary_expr(self, ctx: SymphonyParser.Nary_exprContext):
        expressions = [self.visit(e) for e in ctx.expr_rule()]
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        if ctx.arith_op():
            ops = [self.visit(o) for o in ctx.arith_op()]
            return self.bool_expr(ops, expressions)
        if ctx.IF():
            condition = self.visit(ctx.nary_expr())
            expressions.insert(1, condition)
            op_token = self.get_token(ctx.IF().symbol, str(ctx.IF()))
            return NaryAST(endtoken, tkn, op_token, expressions)
        if ctx.IN():
            in_token = self.get_token(ctx.IN().symbol, str(ctx.IN()))
            ast = NaryAST(endtoken, tkn, in_token, expressions)
            if ctx.NOT():
                not_token = self.get_token(ctx.NOT().symbol, str(ctx.NOT()))
                return NaryAST(endtoken, tkn, not_token, [ast])
            return ast
        assert len(expressions) == 1
        return expressions[0]

    # Visit a parse tree produced by SymphonyParser#expr_rule.
    def visitExpr_rule(self, ctx:SymphonyParser.Expr_ruleContext):
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        if ctx.SETINTLEVEL():
            expr = self.visit(ctx.expr_rule())
            return SetIntLevelAST(endtoken, tkn, expr)
        if ctx.SAVE():
            expr = self.visit(ctx.expr_rule())
            return SaveAST(endtoken, tkn, expr)
        if ctx.STOP():
            expr = self.visit(ctx.expr_rule())
            return StopAST(endtoken, tkn, expr)
        if ctx.unary_op():
            op = self.visit(ctx.unary_op())
            if op[0] == '!':
                expr = self.visit(ctx.expr_rule())
                return PointerAST(endtoken, expr, tkn)
            elif op[0] == '?':
                expr = self.visit(ctx.expr_rule())
                return AddressAST(endtoken, expr, tkn)
            else:
                expr = self.visit(ctx.expr_rule())
                return NaryAST(endtoken, tkn, op, [expr])
        if ctx.application():
            return self.visit(ctx.application())
        raise SymphonyCompilerError(
            message="Invalid expression",
            filename=self.file,
            line=tkn[2],
            column=tkn[3],
            lexeme=tkn[0]
        )

    # Visit a parse tree produced by SymphonyParser#application.
    def visitApplication(self, ctx:SymphonyParser.ApplicationContext):
        tkn = self.get_token(ctx.start, ctx.start.text)
        endtoken = self.get_token(ctx.stop, ctx.stop.text)
        if ctx.ARROWID():
            p = self.visit(ctx.application())
            name = self.get_token(ctx.ARROWID().symbol, str(ctx.ARROWID()))
            (lexeme, file, line, col) = name
            lexeme = lexeme[2:]
            col += 2
            while lexeme[0] == ' ':
                lexeme = lexeme[1:]
                col += 1
            return ApplyAST(endtoken, PointerAST(endtoken, p, tkn), ConstantAST(endtoken, (lexeme, file, line, col)), tkn)
        elif ctx.application():
            f = self.visit(ctx.application())
            return ApplyAST(endtoken, f, self.visit(ctx.basic_expr()), tkn)
        else:
            return self.visit(ctx.basic_expr())
