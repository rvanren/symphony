# Generated from Symphony.g4 by ANTLR 4.9.3
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .SymphonyParser import SymphonyParser
else:
    from SymphonyParser import SymphonyParser

# This class defines a complete generic visitor for a parse tree produced by SymphonyParser.

class SymphonyVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by SymphonyParser#program.
    def visitProgram(self, ctx:SymphonyParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#import_stmt.
    def visitImport_stmt(self, ctx:SymphonyParser.Import_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#import_name.
    def visitImport_name(self, ctx:SymphonyParser.Import_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#import_from.
    def visitImport_from(self, ctx:SymphonyParser.Import_fromContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#import_names_seq.
    def visitImport_names_seq(self, ctx:SymphonyParser.Import_names_seqContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#tuple_bound.
    def visitTuple_bound(self, ctx:SymphonyParser.Tuple_boundContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#bound.
    def visitBound(self, ctx:SymphonyParser.BoundContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#arith_op.
    def visitArith_op(self, ctx:SymphonyParser.Arith_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#unary_op.
    def visitUnary_op(self, ctx:SymphonyParser.Unary_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#int.
    def visitInt(self, ctx:SymphonyParser.IntContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#bool.
    def visitBool(self, ctx:SymphonyParser.BoolContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#atom.
    def visitAtom(self, ctx:SymphonyParser.AtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#name.
    def visitName(self, ctx:SymphonyParser.NameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#str.
    def visitStr(self, ctx:SymphonyParser.StrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#none.
    def visitNone(self, ctx:SymphonyParser.NoneContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#set_rule_1.
    def visitSet_rule_1(self, ctx:SymphonyParser.Set_rule_1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#empty_dict.
    def visitEmpty_dict(self, ctx:SymphonyParser.Empty_dictContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#paren_tuple.
    def visitParen_tuple(self, ctx:SymphonyParser.Paren_tupleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#bracket_tuple.
    def visitBracket_tuple(self, ctx:SymphonyParser.Bracket_tupleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#lambda_expr.
    def visitLambda_expr(self, ctx:SymphonyParser.Lambda_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#set_rule.
    def visitSet_rule(self, ctx:SymphonyParser.Set_ruleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#iter_parse.
    def visitIter_parse(self, ctx:SymphonyParser.Iter_parseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#for_parse.
    def visitFor_parse(self, ctx:SymphonyParser.For_parseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#where_parse.
    def visitWhere_parse(self, ctx:SymphonyParser.Where_parseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#tuple_rule.
    def visitTuple_rule(self, ctx:SymphonyParser.Tuple_ruleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#nary_expr.
    def visitNary_expr(self, ctx:SymphonyParser.Nary_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#expr_rule.
    def visitExpr_rule(self, ctx:SymphonyParser.Expr_ruleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#application.
    def visitApplication(self, ctx:SymphonyParser.ApplicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#expr.
    def visitExpr(self, ctx:SymphonyParser.ExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#assign_op.
    def visitAssign_op(self, ctx:SymphonyParser.Assign_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#aug_assign_op.
    def visitAug_assign_op(self, ctx:SymphonyParser.Aug_assign_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#expr_stmt.
    def visitExpr_stmt(self, ctx:SymphonyParser.Expr_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#assign_stmt.
    def visitAssign_stmt(self, ctx:SymphonyParser.Assign_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#aug_assign_stmt.
    def visitAug_assign_stmt(self, ctx:SymphonyParser.Aug_assign_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#const_assign_stmt.
    def visitConst_assign_stmt(self, ctx:SymphonyParser.Const_assign_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#assert_stmt.
    def visitAssert_stmt(self, ctx:SymphonyParser.Assert_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#await_stmt.
    def visitAwait_stmt(self, ctx:SymphonyParser.Await_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#var_stmt.
    def visitVar_stmt(self, ctx:SymphonyParser.Var_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#trap_stmt.
    def visitTrap_stmt(self, ctx:SymphonyParser.Trap_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#pass_stmt.
    def visitPass_stmt(self, ctx:SymphonyParser.Pass_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#finally_stmt.
    def visitFinally_stmt(self, ctx:SymphonyParser.Finally_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#invariant_stmt.
    def visitInvariant_stmt(self, ctx:SymphonyParser.Invariant_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#del_stmt.
    def visitDel_stmt(self, ctx:SymphonyParser.Del_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#spawn_stmt.
    def visitSpawn_stmt(self, ctx:SymphonyParser.Spawn_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#go_stmt.
    def visitGo_stmt(self, ctx:SymphonyParser.Go_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#print_stmt.
    def visitPrint_stmt(self, ctx:SymphonyParser.Print_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#sequential_stmt.
    def visitSequential_stmt(self, ctx:SymphonyParser.Sequential_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#global_stmt.
    def visitGlobal_stmt(self, ctx:SymphonyParser.Global_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#builtin_stmt.
    def visitBuiltin_stmt(self, ctx:SymphonyParser.Builtin_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#sequential_names_seq.
    def visitSequential_names_seq(self, ctx:SymphonyParser.Sequential_names_seqContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#atomic_block.
    def visitAtomic_block(self, ctx:SymphonyParser.Atomic_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#for_block.
    def visitFor_block(self, ctx:SymphonyParser.For_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#let_decl.
    def visitLet_decl(self, ctx:SymphonyParser.Let_declContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#when_decl.
    def visitWhen_decl(self, ctx:SymphonyParser.When_declContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#let_when_decl.
    def visitLet_when_decl(self, ctx:SymphonyParser.Let_when_declContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#let_when_block.
    def visitLet_when_block(self, ctx:SymphonyParser.Let_when_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#opt_returns.
    def visitOpt_returns(self, ctx:SymphonyParser.Opt_returnsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#method_decl.
    def visitMethod_decl(self, ctx:SymphonyParser.Method_declContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#while_block.
    def visitWhile_block(self, ctx:SymphonyParser.While_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#elif_block.
    def visitElif_block(self, ctx:SymphonyParser.Elif_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#else_block.
    def visitElse_block(self, ctx:SymphonyParser.Else_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#if_block.
    def visitIf_block(self, ctx:SymphonyParser.If_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#block_stmts.
    def visitBlock_stmts(self, ctx:SymphonyParser.Block_stmtsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#block.
    def visitBlock(self, ctx:SymphonyParser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#normal_block.
    def visitNormal_block(self, ctx:SymphonyParser.Normal_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#simple_stmt.
    def visitSimple_stmt(self, ctx:SymphonyParser.Simple_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#compound_stmt.
    def visitCompound_stmt(self, ctx:SymphonyParser.Compound_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#one_line_stmt.
    def visitOne_line_stmt(self, ctx:SymphonyParser.One_line_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#label.
    def visitLabel(self, ctx:SymphonyParser.LabelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SymphonyParser#stmt.
    def visitStmt(self, ctx:SymphonyParser.StmtContext):
        return self.visitChildren(ctx)



del SymphonyParser