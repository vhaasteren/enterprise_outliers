#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, Extension
from Cython.Build import cythonize
import os
import numpy
import platform

# Cross-platform OpenMP flags with environment overrides


def get_openmp_flags():
    no_openmp = os.getenv("NO_OPENMP", "0") == "1"
    runtime = os.getenv("OPENMP_RUNTIME", "").lower().strip()
    is_darwin = platform.system() == "Darwin"

    compile_args = ["-O2", "-fno-wrapv"]
    link_args = []

    if no_openmp:
        return compile_args, link_args

    if is_darwin:
        # Apple clang needs the preprocessor hint
        # and typically links against libomp
        compile_args += ["-Xpreprocessor", "-fopenmp"]
        if runtime in ("iomp5", "libiomp5"):
            link_args += ["-liomp5"]
        elif runtime in ("gomp", "libgomp"):
            link_args += ["-lgomp"]
        else:
            # default for macOS is LLVM's libomp
            link_args += ["-lomp"]
    else:
        # GCC/Clang on Linux: prefer -fopenmp for compile and link
        compile_args += ["-fopenmp"]
        if runtime in ("iomp5", "libiomp5"):
            link_args += ["-liomp5"]
        elif runtime in ("omp", "libomp"):
            link_args += ["-lomp"]
        elif runtime in ("gomp", "libgomp"):
            link_args += ["-lgomp"]
        else:
            # Let the compiler/toolchain select the correct runtime
            link_args += ["-fopenmp"]

    return compile_args, link_args


requirements = [
    "numpy>=1.16.3",
    "scipy>=1.2.0",
    "Cython>=0.28.5",
    "scikit-sparse>=0.4.5",
    "enterprise-pulsar>=3.1.0",
    "pint-pulsar>=0.8.3",
    "matplotlib>=3.2.0",
    "numdifftools>=0.9.0"
]

test_requirements = [
    "pytest",
]

# Resolve OpenMP flags based on platform and environment
extra_compile_args, extra_link_args = get_openmp_flags()

ext_modules = [
    Extension(
        "enterprise_outliers.jitterext",
        ["./enterprise_outliers/jitterext.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=["-O2"],
    ),
    Extension(
        "enterprise_outliers.choleskyext_omp",
        ["./enterprise_outliers/choleskyext_omp.pyx"],
        include_dirs=[numpy.get_include()],
        extra_link_args=extra_link_args,
        extra_compile_args=extra_compile_args,
    ),
]

# Extract version


def get_version():
    with open("enterprise_outliers/__init__.py", encoding="utf-8") as f:
        for line in f.readlines():
            if "__version__" in line:
                return line.split('"')[1]


setup(
    name="enterprise_outliers",
    version=get_version(),
    description="Outlier analysis",
    classifiers=[
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="gravitational-wave, black-hole binary, pulsar-timing arrays",
    url="https://github.com/nanograv/enterprise_outliers",
    author=(
        "Stephen R. Taylor, Paul T. Baker, Jeffrey S. Hazboun, "
        "Sarah Vigeland"
    ),
    author_email="srtaylor@caltech.edu",
    license="MIT",
    packages=[
        "enterprise_outliers",
    ],

    ext_modules=cythonize(ext_modules),
    test_suite="tests",
    tests_require=test_requirements,
    install_requires=requirements,
    include_package_data=True,
    zip_safe=False,
)
