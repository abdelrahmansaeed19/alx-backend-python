#!/usr/bin/env python3
"""
Unit tests for the GithubOrgClient class from the client module.

This module tests the retrieval of organization metadata using mocked requests.
"""

import unittest
from unittest.mock import patch
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """
    Unit tests for the GithubOrgClient.org method.

    Verifies that the org property fetches the correct data from the GitHub API.
    """

    @parameterized.expand([
        ("google", {"login": "google", "id": 1}),
        ("abc", {"login": "abc", "id": 2}),
    ])
    @patch("client.get_json")
    def test_org(self, org_name: str, expected_payload: dict, mock_get_json) -> None:
        """
        Test that GithubOrgClient.org returns the correct value
        and get_json is called once with the expected URL.
        """
        mock_get_json.return_value = expected_payload
        client = GithubOrgClient(org_name)
        result = client.org

        self.assertEqual(result, expected_payload)
        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")
