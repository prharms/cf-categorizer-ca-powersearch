#!/usr/bin/env python3
"""
Test runner for the Campaign Finance Categorization Tool.
Runs all tests and provides coverage information.
"""

import unittest
import sys
import os
from typing import List

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def discover_and_run_tests(test_dir: str = None, pattern: str = 'test_*.py') -> unittest.TestResult:
    """
    Discover and run all tests in the specified directory.
    
    Args:
        test_dir: Directory to search for tests (default: current directory)
        pattern: Pattern to match test files (default: 'test_*.py')
    
    Returns:
        Test results
    """
    if test_dir is None:
        test_dir = os.path.dirname(__file__)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern=pattern)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    return result


def print_test_summary(result: unittest.TestResult) -> None:
    """Print a summary of test results."""
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    
    print(f"Total tests run: {total_tests}")
    print(f"Successes: {total_tests - failures - errors - skipped}")
    print(f"Failures: {failures}")
    print(f"Errors: {errors}")
    print(f"Skipped: {skipped}")
    
    if failures > 0:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if errors > 0:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    success_rate = ((total_tests - failures - errors) / total_tests * 100) if total_tests > 0 else 0
    print(f"\nSuccess rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 ALL TESTS PASSED! 🎉")
    elif success_rate >= 80:
        print("✅ Most tests passed, but some issues need attention.")
    else:
        print("❌ Many tests failed. Review and fix issues.")


def main():
    """Main entry point for the test runner."""
    print("Campaign Finance Categorization Tool - Test Suite")
    print("="*70)
    
    # Check if we're in the right directory
    if not os.path.exists('tests'):
        print("Error: Run this script from the project root directory")
        sys.exit(1)
    
    # Run tests
    result = discover_and_run_tests()
    
    # Print summary
    print_test_summary(result)
    
    # Exit with appropriate code
    if result.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main() 