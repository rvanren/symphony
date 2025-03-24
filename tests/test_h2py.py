import unittest

from symphony_model_checker.symphony.DumpASTVisitor import DumpASTVisitor
from symphony_model_checker.h2py.h2py import h2py
from symphony_model_checker.compile import parse_string
import ast as past


class TestH2PyProgram(unittest.TestCase):

    def assert_h2py(self, symphony_code: str, python_code: str):
        dump_ast = DumpASTVisitor()
        symphony_ast = parse_string(symphony_code)

        try:
            python_ast = h2py(symphony_ast)

        except Exception as error:
            self.fail(f"""
Error while calling H2PyASTVisitor: {error}

Dump Symphony AST: {dump_ast(symphony_ast)}
""")

        try:
            unparsed = past.unparse(python_ast)

        except Exception as error:
            self.fail(f"""
Error while unparsing Python AST: {error}

Dump Symphony AST: {dump_ast(symphony_ast)}

Dumped Parsed Python AST: {past.dump(python_ast, indent=2)}

Expected Python AST: {past.dump(past.parse(python_code), indent=2)}
""")

        self.assertEqual(python_code.strip(), unparsed.strip(), f"""
Dump Symphony AST: {dump_ast(symphony_ast)}

Dumped Parsed Python AST: {past.dump(python_ast, indent=2)}

Expected Python AST: {past.dump(past.parse(python_code), indent=2)}
""")

    def assert_h2py_files(self, symphony_path: str, python_path: str):
        with open(symphony_path) as symphony_file:
            with open(python_path) as python_file:
                self.assert_h2py(symphony_file.read(), python_file.read())

    def test_print(self):
        self.assert_h2py_files(
            'tests/resources/h2py/print.hny',
            'tests/resources/h2py/print.py'
        )

    def test_func_1(self):
        self.assert_h2py_files(
            'tests/resources/h2py/func_1.hny',
            'tests/resources/h2py/func_1.py',
        )

    def test_binops(self):
        self.assert_h2py_files(
            'tests/resources/h2py/binops.hny',
            'tests/resources/h2py/binops.py',
        )

    def test_dict_assign(self):
        self.assert_h2py_files(
            'tests/resources/h2py/dict_assign.hny',
            'tests/resources/h2py/dict_assign.py',
        )

    def test_imports(self):
        self.assert_h2py_files(
            'tests/resources/h2py/imports.hny',
            'tests/resources/h2py/imports.py',
        )

    def test_local_assign_assert(self):
        self.assert_h2py_files(
            'tests/resources/h2py/local_assign_assert.hny',
            'tests/resources/h2py/local_assign_assert.py',
        )

    def test_local_assign(self):
        self.assert_h2py_files(
            'tests/resources/h2py/local_assign.hny',
            'tests/resources/h2py/local_assign.py',
        )

    def test_ptr_assign_1(self):
        self.assert_h2py_files(
            'tests/resources/h2py/ptr_assign_1.hny',
            'tests/resources/h2py/ptr_assign_1.py',
        )

    def test_ptr_assign_2(self):
        self.assert_h2py_files(
            'tests/resources/h2py/ptr_assign_2.hny',
            'tests/resources/h2py/ptr_assign_2.py',
        )

    def test_tuple_assign(self):
        self.assert_h2py_files(
            'tests/resources/h2py/tuple_assign.hny',
            'tests/resources/h2py/tuple_assign.py',
        )

    def test_h2py_name_conflict(self):
        self.assert_h2py_files(
            'tests/resources/h2py/h2py_name_conflict.hny',
            'tests/resources/h2py/h2py_name_conflict.py',
        )

    @unittest.skip('''
    h2py_name_conflict_2.py is not semantically equivalent to 
    h2py_name_conflict_2.hny because, in renaming 'H' to '_H', this conflicts 
    with the existing _H name.
    ''')
    def test_h2py_name_conflict_2(self):
        self.assert_h2py_files(
            'tests/resources/h2py/h2py_name_conflict_2.hny',
            'tests/resources/h2py/h2py_name_conflict_2.py',
        )

    def test_addr_1(self):
        self.assert_h2py_files(
            'tests/resources/h2py/addr_1.hny',
            'tests/resources/h2py/addr_1.py',
        )

    def test_if_1(self):
        self.assert_h2py_files(
            'tests/resources/h2py/if_1.hny',
            'tests/resources/h2py/if_1.py',
        )

    def test_if_else(self):
        self.assert_h2py_files(
            'tests/resources/h2py/if_else.hny',
            'tests/resources/h2py/if_else.py',
        )

    def test_if_elif_else(self):
        self.assert_h2py_files(
            'tests/resources/h2py/if_elif_else.hny',
            'tests/resources/h2py/if_elif_else.py',
        )

    def test_var_1(self):
        self.assert_h2py_files(
            'tests/resources/h2py/var_1.hny',
            'tests/resources/h2py/var_1.py',
        )

    def test_while_1(self):
        self.assert_h2py_files(
            'tests/resources/h2py/while_1.hny',
            'tests/resources/h2py/while_1.py',
        )

    def test_var_2(self):
        self.assert_h2py_files(
            'tests/resources/h2py/var_2.hny',
            'tests/resources/h2py/var_2.py',
        )
    
    def test_choose_1(self):
        self.assert_h2py_files(
            'tests/resources/h2py/choose_1.hny',
            'tests/resources/h2py/choose_1.py',
        )

    def test_ptr_assign_3(self):
        self.assert_h2py_files(
            'tests/resources/h2py/ptr_assign_3.hny',
            'tests/resources/h2py/ptr_assign_3.py',
        )

    def test_ptr_assign_4(self):
        self.assert_h2py_files(
            'tests/resources/h2py/ptr_assign_4.hny',
            'tests/resources/h2py/ptr_assign_4.py',
        )

    def test_addr_2(self):
        self.assert_h2py_files(
            'tests/resources/h2py/addr_2.hny',
            'tests/resources/h2py/addr_2.py',
        )

    def test_ptr_apply_1(self):
        self.assert_h2py_files(
            'tests/resources/h2py/ptr_apply_1.hny',
            'tests/resources/h2py/ptr_apply_1.py',
        )

    def test_addr_3(self):
        self.assert_h2py_files(
            'tests/resources/h2py/addr_3.hny',
            'tests/resources/h2py/addr_3.py',
        )

    def test_apply_1(self):
        self.assert_h2py_files(
            'tests/resources/h2py/apply_1.hny',
            'tests/resources/h2py/apply_1.py',
        )


if __name__ == '__main__':
    unittest.main()
