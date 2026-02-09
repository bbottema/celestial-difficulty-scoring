#!/usr/bin/env python
"""
Test runner for celestial observability scoring tests.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py unit               # Run only unit tests
    python run_tests.py advanced           # Run only advanced tests
    python run_tests.py -v                 # Verbose output
"""
import sys
import os
import unittest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def run_tests(test_type='all', verbosity=2):
    """Run the test suite."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    if test_type in ('all', 'unit'):
        print("Loading unit tests...")
        from tests.scoring import test_observability_unit_tests
        from tests.scoring import test_magnitude_constants
        unit_tests1 = loader.loadTestsFromModule(test_observability_unit_tests)
        unit_tests2 = loader.loadTestsFromModule(test_magnitude_constants)
        suite.addTests(unit_tests1)
        suite.addTests(unit_tests2)
        print(f"  Added {unit_tests1.countTestCases() + unit_tests2.countTestCases()} unit tests")

    if test_type in ('all', 'advanced'):
        print("Loading advanced tests...")
        from tests.scoring import test_advanced_scenarios
        advanced_tests = loader.loadTestsFromModule(test_advanced_scenarios)
        suite.addTests(advanced_tests)
        print(f"  Added {advanced_tests.countTestCases()} advanced tests")

    print(f"\nRunning {suite.countTestCases()} total tests...\n")
    print("=" * 70)

    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print(f"\nTests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    if result.wasSuccessful():
        print("\n[PASS] ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n[FAIL] {len(result.failures) + len(result.errors)} TESTS FAILED")
        return 1


if __name__ == '__main__':
    test_type = 'all'
    verbosity = 2

    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ('unit', 'advanced'):
            test_type = arg
        elif arg == '-v':
            verbosity = 2
        elif arg == '-vv':
            verbosity = 3
        else:
            print(__doc__)
            sys.exit(1)

    exit_code = run_tests(test_type, verbosity)
    sys.exit(exit_code)
