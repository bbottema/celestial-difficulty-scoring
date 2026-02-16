"""
Pytest configuration for NightGuide tests.

This file automatically configures the Python path for all tests.
"""
import sys
from pathlib import Path

# Add src directory to Python path so tests can import app modules
project_root = Path(__file__).parent.parent
src_path = project_root / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Add tests/unit to path for test_helpers
test_unit_path = Path(__file__).parent / 'unit'
if str(test_unit_path) not in sys.path:
    sys.path.insert(0, str(test_unit_path))
