#!/usr/bin/env python
"""
Test runner for integration tests (tests with external network/API dependencies).

Usage:
    python run_tests_it.py         # Run integration tests
    python run_tests_it.py -v      # Verbose output
    python run_tests_it.py -vv     # Very verbose output

Warning: These tests make real API calls and may be slow or fail if services are down.
"""
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def run_tests(verbosity=2):
    """Run integration tests (external API calls)."""
    import pytest

    args = [
        'tests/it/',
        '-v' if verbosity >= 2 else '',
        '-vv' if verbosity >= 3 else '',
        '--tb=short',
    ]

    # Filter out empty strings
    args = [arg for arg in args if arg]

    print("Running integration tests (with external API calls)...")
    print("WARNING: These tests make real network calls and may be slow.\n")
    print(f"Command: pytest {' '.join(args)}\n")
    print("=" * 70)

    exit_code = pytest.main(args)

    print("\n" + "=" * 70)
    if exit_code == 0:
        print("\n[PASS] ALL INTEGRATION TESTS PASSED!")
    else:
        print(f"\n[FAIL] Some integration tests failed (exit code: {exit_code})")

    return exit_code


if __name__ == '__main__':
    verbosity = 2

    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == '-v':
            verbosity = 2
        elif arg == '-vv':
            verbosity = 3
        elif arg in ('-h', '--help'):
            print(__doc__)
            sys.exit(0)
        else:
            print(__doc__)
            sys.exit(1)

    exit_code = run_tests(verbosity)
    sys.exit(exit_code)
