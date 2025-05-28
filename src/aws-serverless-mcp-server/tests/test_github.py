# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions
# and limitations under the License.
"""Tests for the github module."""

import pytest
from unittest.mock import patch, Mock, MagicMock
import requests
from awslabs.aws_serverless_mcp_server.utils.github import (
    fetch_github_content
)


class TestGithubUtils:
    """Tests for the github utility functions."""

    @pytest.mark.asyncio
    async def test_fetch_github_content_success(self):
        """Test successful GitHub content fetch."""
        # Mock response data
        mock_content = {
            "content": "SGVsbG8sIHdvcmxkIQ==",  # Base64 encoded "Hello, world!"
            "encoding": "base64"
        }
        
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_content
        
        # Mock the httpx.AsyncClient.get method
        with patch('requests.get', new_callable=Mock) as mock_get:
            mock_get.return_value = mock_response
            
            # Call the function
            result = fetch_github_content("https://api.github.com/repos/owner/repo/contents/path/to/file.txt")
            
            # Verify the result
            assert "content" in result
            
            # Verify the API call
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_github_content_not_found(self):
        """Test GitHub content fetch with 404 response."""
        # Create a mock response for 404
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Client Error")
        
        # Mock the httpx.AsyncClient.get method
        with patch('requests.get', new_callable=Mock) as mock_get:
            mock_get.return_value = mock_response
            
            # Call the function and assert that any exception is raised
            with pytest.raises(ValueError):
                fetch_github_content("https://api.github.com/repos/owner/repo/contents/path/to/non-existent-file.txt")

    @pytest.mark.asyncio
    async def test_fetch_github_content_error(self):
        """Test GitHub content fetch with error."""
        # Mock the httpx.AsyncClient.get method to raise an exception
        with patch('requests.get', new_callable=Mock) as mock_get:
            mock_get.side_effect = requests.ConnectionError("Connection error")
            
            # Call the function and assert that a ValueError is raised
            with pytest.raises(ValueError):
                fetch_github_content("https://api.github.com/repos/owner/repo/contents/path/to/file.txt")
