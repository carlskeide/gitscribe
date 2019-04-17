# coding: utf-8
from setuptools import setup, find_packages

setup(
    name='GitScribe',
    version='1.1.0',

    description='Automated Release Notes distribution.',
    url='https://github.com/carlskeide/gitscribe/',
    author='Carl Skeide',

    packages=find_packages(),

    install_requires=[
        "flask",
        "flask",
        "requests",
        "markdown"
    ],
    extras_require={
        'test': [
            'pytest',
            'pytest-cov',
            'flake8'
        ],
    }
)
