import os
import os.path
from pathlib import Path
import pathlib
import sys
from typing import List, NamedTuple

import setuptools
import distutils.errors
from setuptools import Extension
from setuptools.command.build_ext import build_ext


# Checks the version number of package in the same way as pip.
def read(rel_path: str) -> str:
    here = os.path.abspath(os.path.dirname(__file__))
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    with open(os.path.join(here, rel_path), encoding='utf-8') as fp:
        return fp.read()

def get_version(rel_path: str) -> str:
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")

PACKAGE_NAME = 'symphony'
PROJECT_DIR_NAME = 'symphony_model_checker'

python_version = sys.version_info[:2]
if python_version < (3, 8):
    print("{} requires Python version 3.8 or later".format(PACKAGE_NAME))
    print("(Version {}.{} detected)".format(*python_version))
    sys.exit(1)

PACKAGE_VERSION = get_version(f"{PROJECT_DIR_NAME}/__init__.py")

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


class CompilerArgs(NamedTuple):
    name: str
    compile_args: List[str]
    linker_args: List[str]


EXTRA_COMPILE_ARGS = ["-pthread", "-m64", "-O3", "-DNDEBUG", "-fPIC"] # the -fPIC flag is required to create a shared object file.

# Extra link args used by gcc in Linux.
# Tested flags with cc and clang
EXTRA_LINK_ARGS = ['-pthread', '-shared', '-Wl,-O1', '-Wl,-Bsymbolic-functions', '-Wl,-Bsymbolic-functions', '-Wl,-z,relro', '-g', '-fwrapv', '-O2', '-Wl,-Bsymbolic-functions',
                   '-Wl,-z,relro', '-g', '-fwrapv', '-O2', '-g', '-fstack-protector-strong', '-Wformat', '-Werror=format-security', '-Wdate-time', '-D_FORTIFY_SOURCE=2']

compiler_and_args = [
    CompilerArgs(
        "gcc",
        EXTRA_COMPILE_ARGS,
        EXTRA_LINK_ARGS
    ),
    CompilerArgs(
        "cc",
        EXTRA_COMPILE_ARGS,
        EXTRA_LINK_ARGS
    ),
    CompilerArgs(
        "clang",
        EXTRA_COMPILE_ARGS,
        EXTRA_LINK_ARGS
    )
]

class BuildExtCommand(build_ext):
    def build_extension(self, ext) -> None:
        try:
            # Try to build the extension with the default OS build tools.
            super().build_extension(ext)
            return
        except (distutils.errors.DistutilsPlatformError, distutils.errors.CompileError) as e:
            print(e)
            print("Encountered error when building by default configurations")
            print("Building with backup configurations")

        encountered_error = None
        for c in compiler_and_args:
            ext.extra_compile_args = c.compile_args
            ext.extra_link_args = c.linker_args
            name = c.name
            self.compiler.set_executable("linker_so", name)
            self.compiler.set_executable("compiler_so", name)
            self.compiler.set_executable("compiler_cxx", name)
            try:
                super().build_extension(ext)
                return
            except distutils.errors.CompileError as e:
                encountered_error = e

        if encountered_error is not None:
            raise encountered_error


CHARM_PKG_PATH = pathlib.Path(PROJECT_DIR_NAME) / "charm"
def get_c_extension_src():
    sources = []
    base_dir = CHARM_PKG_PATH
    D = [base_dir, base_dir / "python_ext"]
    for d in D:
        sources.extend([str(f) for f in d.glob('*.c')])
    return sources

def get_c_extension_include_dirs():
    return [
        str(CHARM_PKG_PATH),
        str(CHARM_PKG_PATH / 'python_ext'),
    ]


module = Extension(
    f"{PROJECT_DIR_NAME}.charm",
    sources=get_c_extension_src(),
    include_dirs=get_c_extension_include_dirs(),
    extra_compile_args=[],
    extra_link_args=[]
    # extra_link_args=
    #     ["-lnuma"] if sys.platform.lower().startswith("linux") else []
)

setuptools.setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    author="Anonymous",
    author_email="anonymous@anonymous.com",
    description="Symphony Programming Language",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    install_requires=[
        'antlr-denter>=1.3.1',
        'antlr4-python3-runtime==4.9.3',
        'automata-lib',
        'pydot',
        'requests',
    ],
    license="BSD",
    url="https://symphony.ANONYMIZED.IO",
    include_package_data=True,
    package_data={
        PACKAGE_NAME: [
            "modules/*.hny",
            "charm/*.h",
            "charm/*.c",
            "charm/python_ext/ext.c",
            "symphony/charm.js",
            "symphony/charm.css",
        ]
    },
    entry_points={
        'console_scripts': [
            'symphony=symphony_model_checker.main:main'
        ]
    },
    python_requires=">=3.8",
    ext_modules=[module],
    cmdclass={
        "build_ext": BuildExtCommand
    }
)
