""" Setup file for moltopolparser package. """

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("CHANGELOG.md", "r", encoding="utf-8") as fh:
    changelog = fh.read()

setup(
    name='moltopolparser',
    version='0.0.1a3',
    author="Xinmeng Li",
    author_email="xinmeng@bocores.com",
    description="A lightweight package to parse and process molecular simulation files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xinmengbcr/MolTopolParser",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "pydantic>=2.7.2",
        "numpy>=1.26.4",
    ],
)
