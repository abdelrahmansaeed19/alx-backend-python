#!/usr/bin/env python3


"""
Unit tests for utility functions from the utils module.

This module tests:
- access_nested_map for valid and invalid key paths
- get_json for JSON fetching from URLs
- memoize decorator for caching behavior
"""

from parameterized import parameterized
import unittest
from utils import access_nested_map, get_json, memoize
from unittest.mock import patch, Mock


class TestAccessNestedMap(unittest.TestCase):
    """Unit tests for the access_nested_map function."""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):

        """
        Test that access_nested_map returns the expected result for valid paths
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), 'a'),
        ({"a": 1}, ("a", "b"), 'b'),
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_key):

        """
        Test that access_nested_map raises KeyError for invalid paths.
        """

        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        self.assertEqual(str(context.exception), f"'{expected_key}'")


class TestGetJson(unittest.TestCase):
    """Unit tests for the get_json function."""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    def test_get_json(self, test_url, test_payload):
        """
        get_json returns the expected payload and calls requests.get once.
        """

        with patch("utils.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = test_payload
            mock_get.return_value = mock_response

            result = get_json(test_url)

            mock_get.assert_called_once_with(test_url)
            self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Unit tests for the memoize decorator."""

    def test_memoize(self):
        """
        Test that the memoize decorator caches results after first computation.
        """

        class TestClass:
            """Dummy class to test memoization."""

            def a_method(self):
                """Returns a fixed integer value."""

                return 42

            @memoize
            def a_property(self):
                """Returns the result of a_method, memoized."""

                return self.a_method()
        with patch.object(TestClass, 'a_method', return_value=42) as mock:
            obj = TestClass()
            result1 = obj.a_property
            result2 = obj.a_property

            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)
            mock.assert_called_once()
