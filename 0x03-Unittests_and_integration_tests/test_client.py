#!/usr/bin/env python3
"""
Unit tests for the GithubOrgClient class from the client module.

This module tests the retrieval of organization metadata using mocked requests.
"""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized
from parameterized import parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD
import requests


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


@parameterized_class([
    {
        "org_payload": org_payload,
        "repos_payload": repos_payload,
        "expected_repos": expected_repos,
        "apache2_repos": apache2_repos
    }
    for org_payload, repos_payload,
    expected_repos, apache2_repos in TEST_PAYLOAD
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration test class for GithubOrgClient.

    Only external requests (requests.get) are mocked using fixtures.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up class-level patching of requests.get using fixture side_effects.
        """
        cls.get_patcher = patch("requests.get")

        # Start patching
        cls.mock_get = cls.get_patcher.start()

        # Create a side effect for requests.get
        def side_effect(url: str):
            """
            Side effect function to return the appropriate mocked response.
            """

            if url == GithubOrgClient.ORG_URL.format(org="google"):
                return MockResponse(cls.org_payload)
            elif url == cls.org_payload.get("repos_url"):
                return MockResponse(cls.repos_payload)
            return MockResponse(None)

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls) -> None:
        """Stop the patcher."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """
        Test that public_repos returns all expected repository names
        based on the fixture payload.
        """

        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """
        Test that public_repos returns only repositories matching
        the apache-2.0 license key from the fixture payload.
        """

        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )


class MockResponse:
    """Simple mock for requests.Response with a json() method."""

    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload
