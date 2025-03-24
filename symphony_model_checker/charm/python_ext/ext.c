
#include "Python.h"

int exec_model_checker(int argc, char** argv);

static PyObject* run_model_checker(PyObject *self, PyObject *args) {
    Py_ssize_t tupleSize = PyTuple_Size(args);
    Py_ssize_t argc = tupleSize + 1;
    char **argv = malloc(argc * sizeof(char *));
    argv[0] = "charm";
    for (Py_ssize_t i = 0; i < tupleSize; ++i) {
        PyObject *a = PyTuple_GetItem(args, i);
        char *s;
        if (!PyArg_Parse(a, "s", &s)) {
            return NULL;
        }
        argv[i + 1] = s;
    }
    PyObject *r = PyLong_FromLong(exec_model_checker(argc, argv));
    free(argv);
    return r;
}

static char module_docstring[] =
    "This module provides an interface for running the Symphony model checker.";
static char run_model_checker_sub_docstring[] =
    "Perform model check.";

static PyMethodDef module_methods[] = {
    {"run_model_checker", run_model_checker, METH_VARARGS, run_model_checker_sub_docstring},
    {NULL, NULL, 0, NULL}
};

static PyModuleDef mod_def = {
    PyModuleDef_HEAD_INIT,
    "charm",
    module_docstring,
    -1,
    module_methods,
};

PyObject* PyInit_charm(void)
{
    return PyModule_Create(&mod_def);
};
// Redefined in the rest of charm.c
#undef _GNU_SOURCE
