"""Pytest configuration and fixtures."""

import sys
from pathlib import Path

# Add src to Python path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
