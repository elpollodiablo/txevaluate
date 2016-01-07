"""A setuptools based setup module.
"""
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='txevaluate',
    version='0.1.0',
    description='A logic expression evaluator for twisted',
    long_description=long_description,
    url='https://github.com/elpollodiablo/txevaluate',
    author='Philip Poten',
    author_email='philip.poten@gmail.com',
    license='Apache',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='twisted',
    py_modules=["txevaluate"],
    install_requires=['Twisted'],
    extras_require={
    },
    package_data={
    },
    data_files=[],
    entry_points={
    },
)