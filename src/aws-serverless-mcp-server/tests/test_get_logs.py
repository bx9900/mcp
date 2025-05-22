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
"""Tests for the get_logs module."""

import pytest
import datetime
import json
from unittest.mock import patch, MagicMock
from awslabs.aws_serverless_mcp_server.models import GetLogsRequest
from awslabs.aws_serverless_mcp_server.tools.webapps.get_logs import get_logs


class TestGetLogs:
    """Tests for the get_logs function."""

    @pytest.mark.asyncio
    async def test_get_logs_success(self):
        """Test successful logs retrieval."""
        # Create a mock request
        request = GetLogsRequest(
            project_name="test-project"
        )

        # Mock the boto3 session and CloudWatch Logs client
        mock_session = MagicMock()
        mock_logs_client = MagicMock()
        mock_session.client.return_value = mock_logs_client

        # Mock the CloudWatch Logs filter_log_events response
        timestamp = int(datetime.datetime.now().timestamp() * 1000)
        mock_logs_client.filter_log_events.return_value = {
            'events': [
                {
                    'timestamp': timestamp,
                    'message': 'This is a log message',
                    'eventId': '12345'
                },
                {
                    'timestamp': timestamp + 1000,
                    'message': 'This is an error message',
                    'eventId': '12346'
                },
                {
                    'timestamp': timestamp + 2000,
                    'message': json.dumps({
                        'level': 'DEBUG',
                        'message': 'This is a JSON log message'
                    }),
                    'eventId': '12347'
                }
            ],
            'nextToken': 'next-token'
        }

        with patch('boto3.Session', return_value=mock_session):
            # Call the function
            result = await get_logs(request)

            # Verify the result
            assert result["success"] is True
            assert result["logGroupName"] == "/aws/lambda/test-project"
            assert result["nextToken"] == "next-token"
            assert len(result["logs"]) == 3
            
            # Check the log entries
            assert result["logs"][0]["level"] == "INFO"
            assert result["logs"][0]["message"] == "This is a log message"
            assert result["logs"][0]["eventId"] == "12345"
            
            assert result["logs"][1]["level"] == "ERROR"
            assert result["logs"][1]["message"] == "This is an error message"
            
            assert result["logs"][2]["level"] == "DEBUG"
            assert json.loads(result["logs"][2]["message"])["message"] == "This is a JSON log message"

            # Verify boto3 session was created with the correct parameters
            mock_session.client.assert_called_once_with('logs')
            
            # Verify filter_log_events was called with the correct parameters
            mock_logs_client.filter_log_events.assert_called_once()
            args, kwargs = mock_logs_client.filter_log_events.call_args
            assert kwargs["logGroupName"] == "/aws/lambda/test-project"
            assert kwargs["limit"] == 100

    @pytest.mark.asyncio
    async def test_get_logs_with_custom_log_group(self):
        """Test logs retrieval with custom log group name."""
        # Create a mock request with custom log group
        request = GetLogsRequest(
            project_name="test-project",
            log_group_name="/custom/log/group"
        )

        # Mock the boto3 session and CloudWatch Logs client
        mock_session = MagicMock()
        mock_logs_client = MagicMock()
        mock_session.client.return_value = mock_logs_client

        # Mock the CloudWatch Logs filter_log_events response
        mock_logs_client.filter_log_events.return_value = {
            'events': [],
            'nextToken': None
        }

        with patch('boto3.Session', return_value=mock_session):
            # Call the function
            result = await get_logs(request)

            # Verify the result
            assert result["success"] is True
            assert result["logGroupName"] == "/custom/log/group"
            
            # Verify filter_log_events was called with the correct parameters
            mock_logs_client.filter_log_events.assert_called_once()
            args, kwargs = mock_logs_client.filter_log_events.call_args
            assert kwargs["logGroupName"] == "/custom/log/group"

    @pytest.mark.asyncio
    async def test_get_logs_with_optional_params(self):
        """Test logs retrieval with optional parameters."""
        # Create a mock request with optional parameters
        request = GetLogsRequest(
            project_name="test-project",
            start_time="2023-05-20T00:00:00Z",
            end_time="2023-05-21T23:59:59Z",
            limit=50,
            filter_pattern="ERROR",
            region="us-west-2"
        )

        # Mock the boto3 session and CloudWatch Logs client
        mock_session = MagicMock()
        mock_logs_client = MagicMock()
        mock_session.client.return_value = mock_logs_client

        # Mock the CloudWatch Logs filter_log_events response
        mock_logs_client.filter_log_events.return_value = {
            'events': [],
            'nextToken': None
        }

        with patch('boto3.Session', return_value=mock_session):
            # Call the function
            result = await get_logs(request)

            # Verify the result
            assert result["success"] is True

            # Verify boto3 session was created with the correct parameters
            mock_session.client.assert_called_once_with('logs')
            
            # Verify filter_log_events was called with the correct parameters
            mock_logs_client.filter_log_events.assert_called_once()
            args, kwargs = mock_logs_client.filter_log_events.call_args
            
            # Check that optional parameters were included
            assert kwargs["limit"] == 50
            assert kwargs["filterPattern"] == "ERROR"
            assert "startTime" in kwargs
            assert "endTime" in kwargs
            
            # Check that start_time and end_time were converted to milliseconds since epoch
            start_dt = datetime.datetime.fromisoformat("2023-05-20T00:00:00+00:00")
            end_dt = datetime.datetime.fromisoformat("2023-05-21T23:59:59+00:00")
            assert kwargs["startTime"] == int(start_dt.timestamp() * 1000)
            assert kwargs["endTime"] == int(end_dt.timestamp() * 1000)

    @pytest.mark.asyncio
    async def test_get_logs_invalid_time_format(self):
        """Test logs retrieval with invalid time format."""
        # Create a mock request with invalid time formats
        request = GetLogsRequest(
            project_name="test-project",
            start_time="invalid-start-time",
            end_time="invalid-end-time"
        )

        # Mock the boto3 session and CloudWatch Logs client
        mock_session = MagicMock()
        mock_logs_client = MagicMock()
        mock_session.client.return_value = mock_logs_client

        # Mock the CloudWatch Logs filter_log_events response
        mock_logs_client.filter_log_events.return_value = {
            'events': [],
            'nextToken': None
        }

        with patch('boto3.Session', return_value=mock_session), \
             patch('awslabs.aws_serverless_mcp_server.utils.logger.logger.warning') as mock_logger:
            # Call the function
            result = await get_logs(request)

            # Verify the result
            assert result["success"] is True
            
            # Verify that warnings were logged for invalid time formats
            mock_logger.assert_any_call("Invalid start_time format: invalid-start-time")
            mock_logger.assert_any_call("Invalid end_time format: invalid-end-time")
            
            # Verify filter_log_events was called without start_time and end_time
            mock_logs_client.filter_log_events.assert_called_once()
            args, kwargs = mock_logs_client.filter_log_events.call_args
            assert "startTime" not in kwargs
            assert "endTime" not in kwargs

    @pytest.mark.asyncio
    async def test_get_logs_boto3_exception(self):
        """Test logs retrieval with boto3 exception."""
        # Create a mock request
        request = GetLogsRequest(
            project_name="test-project"
        )

        # Mock the boto3 session and CloudWatch Logs client
        mock_session = MagicMock()
        mock_logs_client = MagicMock()
        mock_session.client.return_value = mock_logs_client

        # Mock the CloudWatch Logs filter_log_events to raise an exception
        error_message = "An error occurred (ResourceNotFoundException) when calling the FilterLogEvents operation"
        mock_logs_client.filter_log_events.side_effect = Exception(error_message)

        with patch('boto3.Session', return_value=mock_session):
            # Call the function
            result = await get_logs(request)

            # Verify the result
            assert result["success"] is False
            assert "Failed to retrieve logs" in result["message"]
            assert error_message in result["error"]
