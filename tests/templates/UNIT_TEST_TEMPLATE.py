import os
import sys
import unittest

# Add project root to path
sys.path.append(os.getcwd())

# Import the module you're testing
from scripts.your_module import your_function


class TestYourModule(unittest.TestCase):
    """
    Tests for [Module Name]

    Purpose: [Brief description of what this module does]
    Coverage: [What aspects are being tested]
    """

    def setUp(self):
        """
        Setup run before EACH test method.

        Use this to:
        - Create test fixtures
        - Initialize test data
        - Set up temporary directories
        - Mock external dependencies
        """
        pass

    def tearDown(self):
        """
        Cleanup run after EACH test method.

        Use this to:
        - Delete temporary files
        - Reset state
        - Close connections
        - Clean up resources
        """
        pass

    @classmethod
    def setUpClass(cls):
        """
        Setup run ONCE before all tests in this class.

        Use this for expensive operations that can be shared:
        - Database connections
        - Loading large datasets
        - Starting test servers
        """
        pass

    @classmethod
    def tearDownClass(cls):
        """
        Cleanup run ONCE after all tests in this class.

        Use this to:
        - Close class-level resources
        - Final cleanup
        """
        pass

    # ========================================================================
    # TEST CASES
    # ========================================================================

    def test_function_with_valid_input_returns_expected_result(self):
        """
        Test that [function] with [valid input] returns [expected result].

        This tests the happy path / normal operation.
        """
        # Arrange - Set up test data
        input_data = "test_value"
        expected_output = "expected_result"

        # Act - Call the function being tested
        actual_output = your_function(input_data)

        # Assert - Verify the result
        self.assertEqual(actual_output, expected_output)

    def test_function_with_invalid_input_raises_error(self):
        """
        Test that [function] with [invalid input] raises [specific error].

        This tests error handling.
        """
        # Arrange
        invalid_input = None

        # Act & Assert
        with self.assertRaises(ValueError):
            your_function(invalid_input)

    def test_function_with_edge_case_handles_correctly(self):
        """
        Test that [function] handles [edge case] correctly.

        Edge cases: empty strings, None, very large numbers, etc.
        """
        # Arrange
        edge_case_input = ""
        expected_behavior = "default_value"

        # Act
        result = your_function(edge_case_input)

        # Assert
        self.assertEqual(result, expected_behavior)

    def test_function_with_multiple_conditions_all_pass(self):
        """
        Test that [function] meets multiple success criteria.

        Use this when you need to verify multiple aspects.
        """
        # Arrange
        test_input = "complex_input"

        # Act
        result = your_function(test_input)

        # Assert - Multiple assertions
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        self.assertIn("expected_substring", result)

    def test_function_behavior_is_consistent(self):
        """
        Test that [function] returns same result with same input (idempotency).

        Important for functions that should be deterministic.
        """
        # Arrange
        test_input = "consistent_input"

        # Act
        result1 = your_function(test_input)
        result2 = your_function(test_input)

        # Assert
        self.assertEqual(result1, result2)

    # ========================================================================
    # HELPER METHODS (if needed)
    # ========================================================================

    def _create_test_fixture(self):
        """Helper method to create common test data."""
        return {"key": "value"}

    def _assert_valid_output(self, output):
        """Helper method for common assertions."""
        self.assertIsNotNone(output)
        self.assertIsInstance(output, dict)


# ========================================================================
# BEST PRACTICES DEMONSTRATED IN THIS TEMPLATE
# ========================================================================
#
# 1. Descriptive Test Names: test_[function]_[scenario]_[expected_result]
# 2. AAA Pattern: Arrange, Act, Assert (clearly separated)
# 3. One Assertion Per Test: Makes failures easier to diagnose
# 4. Docstrings: Every test explains what it's testing
# 5. setUp/tearDown: Proper resource management
# 6. Helper Methods: Reduce duplication (prefix with _)
# 7. Edge Cases: Test boundaries, empty values, None, etc.
# 8. Error Handling: Test that errors are raised when expected
#
# ========================================================================


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)


# ========================================================================
# COMMON ASSERTION METHODS
# ========================================================================
#
# self.assertEqual(a, b)           # a == b
# self.assertNotEqual(a, b)        # a != b
# self.assertTrue(x)               # bool(x) is True
# self.assertFalse(x)              # bool(x) is False
# self.assertIs(a, b)              # a is b
# self.assertIsNot(a, b)           # a is not b
# self.assertIsNone(x)             # x is None
# self.assertIsNotNone(x)          # x is not None
# self.assertIn(a, b)              # a in b
# self.assertNotIn(a, b)           # a not in b
# self.assertIsInstance(a, b)      # isinstance(a, b)
# self.assertNotIsInstance(a, b)   # not isinstance(a, b)
# self.assertGreater(a, b)         # a > b
# self.assertGreaterEqual(a, b)    # a >= b
# self.assertLess(a, b)            # a < b
# self.assertLessEqual(a, b)       # a <= b
# self.assertAlmostEqual(a, b)     # round(a-b, 7) == 0
# self.assertRaises(exc, func, args)  # func(*args) raises exc
#
# ========================================================================
