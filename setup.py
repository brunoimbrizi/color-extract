"""
Setup script for color-extract package.
Simple setup.py for compatibility with older pip versions.
Main configuration is in pyproject.toml.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="color-extract",
    version="0.0.2",
    packages=find_packages(),
    python_requires=">=3.7",
)
