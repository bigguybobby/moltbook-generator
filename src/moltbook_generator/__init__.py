"""
MoltBook Listing Generator

A tool to generate MoltBook format listings from GitHub repositories.
Parses project metadata, extracts information, and generates optimized
descriptions using AI.
"""

__version__ = "0.1.0"
__author__ = "MoltBook Team"

from .generator import MoltBookGenerator
from .parsers import RepoParser
from .templates import MoltBookTemplate

__all__ = ["MoltBookGenerator", "RepoParser", "MoltBookTemplate"]
