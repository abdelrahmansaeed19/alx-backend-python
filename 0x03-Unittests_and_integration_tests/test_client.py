#!/usr/bin/env python3
"""
Unit tests for the GithubOrgClient class from the client module.

This module tests the retrieval of organization metadata using mocked requests.
"""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """
    Unit tests for the GithubOrgClient.org method.

    Verification of org property fetches the correct data from the GitHub API.
    """

    @parameterized.expand([
        ("google", {"login": "google", "id": 1}),
        ("abc", {"login": "abc", "id": 2}),
    ])
    @patch("client.get_json")
    def test_org(self, org_name: str, expected_payload: dict, mock_get_json):
        """
        Test that GithubOrgClient.org returns the correct value
        and get_json is called once with the expected URL.
        """
        mock_get_json.return_value = expected_payload
        client = GithubOrgClient(org_name)
        result = client.org

        self.assertEqual(result, expected_payload)
        mock_get_json.assert_called_once_with
        (f"https://api.github.com/orgs/{org_name}")

    def test_public_repos_url(self) -> None:
        """
        Test that the _public_repos_url property returns the expected URL
        based on the mocked org data.
        """
        payload = {"repos_url": "https://api.github.com/orgs/test-org/repos"}

        with patch.object(GithubOrgClient, "org", call=PropertyMock) as m_org:
            m_org.return_value = payload
            client = GithubOrgClient("test-org")
            self.assertEqual(client._public_repos_url, payload["repos_url"])

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json) -> None:
        """
        Unit-test GithubOrgClient.public_repos.

        Mocks get_json and _public_repos_url to return controlled data.
        Verifies that the result is as expected and both mocks are called once.
        """
        test_payload = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"},
        ]
        mock_get_json.return_value = test_payload

        with patch.object(GithubOrgClient, "_public_repos_url",
                          new_callable=PropertyMock) as mock_url:
            mock_url.return_value = "https://fake-url.com/orgs/test/repos"
            client = GithubOrgClient("test")
            result = client.public_repos()

            self.assertEqual(result, ["repo1", "repo2", "repo3"])
            mock_get_json.assert_called_once_with
            ("https://fake-url.com/orgs/test/repos")
            mock_url.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo: dict, license_key: str, expected: bool):
        """
        Unit-test for GithubOrgClient.has_license.
        Ensures that:
            the method correctly identifies if a repo has the given license.
        """
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)
