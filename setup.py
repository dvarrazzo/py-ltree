# python ltree setup module

import os
from setuptools import setup


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name="ltree",
    version="0.1.0",
    author="Daniele Varrazzo",
    author_email="daniele.varrazzo@gmail.com",
    description="Python wrapper for the PostgreSQL ltree data type",
    license="BSD",
    keywords="ltree tree database",
    url="https://github.com/dvarrazzo/py-ltree",
    packages=["ltree"],
    install_requires=["psycopg > 3"],
    long_description=read("README.rst"),
    classifiers=[
        c.strip()
        for c in """
        Development Status :: 4 - Beta
        Programming Language :: Python :: 3.9
        Programming Language :: Python :: 3.10
        Programming Language :: Python :: 3.11
        Intended Audience :: Developers
        License :: OSI Approved :: BSD License
        Topic :: Database
        """.splitlines()
        if c and not c.isspace()
    ],
)
