"""
Setup script for color-extractor package.
Simple setup.py for compatibility with older pip versions.
Main configuration is in pyproject.toml.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="color-extractor",
    version="1.0.0",
    packages=find_packages(),
    python_requires=">=3.7",
)
