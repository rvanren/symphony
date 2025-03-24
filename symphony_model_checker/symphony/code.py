from typing import Set
from symphony_model_checker.symphony.ops import *

class Labeled_Op:
    def __init__(self, module: Optional[str], op: Op, start, stop, stmt, labels):
        self.module = module    # module
        self.op = op            # operation
        self.start = start      # first token
        self.stop = stop        # last token
        self.stmt = stmt
        self.labels = labels
        self.live_in: Set[str] = set()
        self.live_out: Set[str] = set()

class Code:
    def __init__(self, parent=None):
        self.labeled_ops: List[Labeled_Op] = []
        self.endlabels = set()
        self.modstack = []      # module stack
        self.curModule = None
        self.curFile = None
        self.curLine = 0
        self.parent = parent

    def modpush(self, module):
        self.modstack.append(self.curModule)
        self.curModule = module

    def modpop(self):
        self.curModule = self.modstack.pop()

    def location(self, file, line: int):
        self.curFile = file
        self.curLine = line

    def append(self, op: Op, start, stop, labels=set(), stmt=None):
        assert len(start) == 4
        assert len(stop) == 4
        assert self.curModule is not None
        self.labeled_ops.append(Labeled_Op(self.curModule, op, start, stop, stmt, labels | self.endlabels))
        self.endlabels = set()

    def nextLabel(self, endlabel):
        self.endlabels.add(endlabel)

    # This method inserts DelVar operations as soon as a variable is no
    # longer live
    def liveness(self):
        # First figure out what the labels point to and initialize
        # the nodes
        map = {}
        lop_predecessors: Dict[int, Set[int]] = {}
        for pc in range(len(self.labeled_ops)):
            lop = self.labeled_ops[pc]
            lop_predecessors[pc] = set()
            lop.live_in = set()
            lop.live_out = set()
            for label in lop.labels:
                assert label not in map, label
                map[label] = pc
        # Compute the predecessors of each node
        for pc in range(len(self.labeled_ops)):
            lop = self.labeled_ops[pc]
            if isinstance(lop.op, JumpOp):
                assert isinstance(lop.op.pc, LabelValue)
                op_pc = map[lop.op.pc]
                succ = self.labeled_ops[op_pc]
                lop_predecessors[op_pc] |= {pc}
            elif isinstance(lop.op, JumpCondOp):
                assert pc < len(self.labeled_ops) - 1
                assert isinstance(lop.op.pc, LabelValue)
                op_pc = map[lop.op.pc]
                succ = self.labeled_ops[op_pc]
                lop_predecessors[op_pc] |= {pc}
                lop_predecessors[pc + 1] |= {pc}
            elif pc < len(self.labeled_ops) - 1 and not isinstance(lop.op, ReturnOp):
                lop_predecessors[pc + 1] |= {pc}
        # Live variable analysis
        change = True
        while change:
            change = False
            for pc in range(len(self.labeled_ops)):
                lop = self.labeled_ops[pc]
                if pc == len(self.labeled_ops) - 1:
                    live_out = set()
                elif isinstance(lop.op, JumpOp):
                    assert isinstance(lop.op.pc, LabelValue)
                    succ = self.labeled_ops[map[lop.op.pc]]
                    live_out = succ.live_in
                else:
                    live_out = self.labeled_ops[pc + 1].live_in
                    if isinstance(lop.op, JumpCondOp):
                        assert isinstance(lop.op.pc, LabelValue)
                        succ = self.labeled_ops[map[lop.op.pc]]
                        live_out = live_out | succ.live_in
                live_in = lop.op.use() | (live_out - lop.op.define())
                if not change and (live_in != lop.live_in or live_out != lop.live_out):
                    change = True
                lop.live_in = live_in
                lop.live_out = live_out
        # Create new code with DelVars inserted
        newcode = Code()
        for lop_pc, lop in enumerate(self.labeled_ops):
            # print(lop.op, lop.live_in, lop.live_out)

            # If a variable is live on output of any predecessor but not
            # live on input, delete it first
            pre_del = set()
            for pred in lop_predecessors[lop_pc]:
                plop = self.labeled_ops[pred]
                live_out = plop.live_out | plop.op.define()
                pre_del |= live_out - lop.live_in

            labels = lop.labels
            newcode.curModule = lop.module

            # If an atomic inc operation, put the delvar inside the atomic section
            if isinstance(lop.op, AtomicIncOp):
                newcode.append(lop.op, lop.start, lop.stop, labels=labels, stmt=lop.stmt)
                labels = set()

            for d in sorted(pre_del - { 'this' }):
                newcode.append(DelVarOp((d, None, None, None)), lop.start, lop.stop, labels=labels, stmt=lop.stmt)
                labels = set()

            if not isinstance(lop.op, AtomicIncOp):
                newcode.append(lop.op, lop.start, lop.stop, labels=labels, stmt=lop.stmt)

            # If a variable is defined or live on input but not live on output,
            # immediately delete afterward
            # TODO.  Can optimize StoreVar by replacing it with Pop
            # post_del = (lop.op.define() | lop.live_in) - lop.live_out
            post_del = lop.live_in - lop.live_out
            for d in sorted(post_del - { 'this' }):
                newcode.append(DelVarOp((d, None, None, None)), lop.start, lop.stop, stmt=lop.stmt)

        return newcode

    def link(self):
        map = {}
        for pc in range(len(self.labeled_ops)):
            lop = self.labeled_ops[pc]
            for label in lop.labels:
                assert label not in map, label
                map[label] = PcValue(pc)
        for lop in self.labeled_ops:
            lop.op.substitute(map)
