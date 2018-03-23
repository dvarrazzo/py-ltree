# python ltree setup module

import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


test_requirements = [
    'tox',
    'django',
    'psycopg2-binary',
    'pytest'
]

setup(
    name="ltree",
    version="0.0.3",
    author="Daniele Varrazzo",
    author_email="daniele.varrazzo@gmail.com",
    description="Python wrapper for the PostgreSQL ltree data type",
    license="BSD",
    keywords="ltree tree database",
    url="https://github.com/dvarrazzo/py-ltree",
    packages=['ltree'],
    install_requires=[
        'six'
    ],
    tests_require=test_requirements,
    extras_require={
        'test': test_requirements,
    },
    long_description=read('README.rst'),
    classifiers=[l.strip() for l in """
        Development Status :: 3 - Alpha
        Programming Language :: Python :: 2.7
        Programming Language :: Python :: 3
        Programming Language :: Python :: 3.5
        Programming Language :: Python :: 3.6
        Intended Audience :: Developers
        License :: OSI Approved :: BSD License
        Topic :: Database
        """.splitlines() if l and not l.isspace()],
)
