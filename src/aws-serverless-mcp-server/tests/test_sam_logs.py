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
"""Tests for the sam_logs module."""

import os
import pytest
import subprocess
import tempfile
from awslabs.aws_serverless_mcp_server.models import SamLogsRequest
from awslabs.aws_serverless_mcp_server.tools.sam.sam_logs import handle_sam_logs
from unittest.mock import MagicMock, patch


class TestSamLogs:
    """Tests for the sam_logs function."""

    @pytest.mark.asyncio
    async def test_sam_logs_success(self):
        """Test successful SAM logs retrieval."""
        # Create a mock request
        request = SamLogsRequest(
            resource_name='test-function',
            project_directory=os.path.join(tempfile.gettempdir(), 'test-project'),
        )

        # Mock the subprocess.run function
        mock_result = MagicMock()
        mock_result.stdout = b'2023-05-21 12:00:00 INFO Lambda function logs'
        mock_result.stderr = b''

        with patch(
            'awslabs.aws_serverless_mcp_server.tools.sam.sam_logs.run_command',
            return_value=(mock_result.stdout, mock_result.stderr),
        ) as mock_run:
            # Call the function
            result = await handle_sam_logs(request)

            # Verify the result
            assert result['success'] is True
            assert 'Successfully fetched logs for resource' in result['message']
            assert result['output'] == '2023-05-21 12:00:00 INFO Lambda function logs'

            # Verify run_command was called with the correct arguments
            mock_run.assert_called_once()
            args, kwargs = mock_run.call_args
            cmd = args[0]

            # Check required parameters
            assert 'sam' in cmd
            assert 'logs' in cmd
            assert '--name' in cmd
            assert 'test-function' in cmd

    @pytest.mark.asyncio
    async def test_sam_logs_with_optional_params(self):
        """Test SAM logs retrieval with optional parameters."""
        # Create a mock request with optional parameters
        request = SamLogsRequest(
            resource_name='test-function',
            project_directory=os.path.join(tempfile.gettempdir(), 'test-project'),
            stack_name='test-stack',
            tail=True,
            filter='ERROR',
            start_time='2023-05-21 00:00:00',
            end_time='2023-05-21 23:59:59',
            output='json',
            region='us-west-2',
            profile='default',
            include_triggered_logs=True,
            cw=True,
            resources_dir=os.path.join(tempfile.gettempdir(), 'resources'),
            template_file='template.yaml',
        )

        # Mock the subprocess.run function
        mock_result = MagicMock()
        mock_result.stdout = (
            b'{"timestamp": "2023-05-21 12:00:00", "message": "Lambda function logs"}'
        )
        mock_result.stderr = b''

        with patch(
            'awslabs.aws_serverless_mcp_server.tools.sam.sam_logs.run_command',
            return_value=(mock_result.stdout, mock_result.stderr),
        ) as mock_run:
            # Call the function
            result = await handle_sam_logs(request)

            # Verify the result
            assert result['success'] is True

            # Verify run_command was called with the correct arguments
            mock_run.assert_called_once()
            args, kwargs = mock_run.call_args
            cmd = args[0]

            # Check optional parameters
            assert '--stack-name' in cmd
            assert 'test-stack' in cmd
            assert '--start-time' in cmd
            assert '2023-05-21 00:00:00' in cmd
            assert '--end-time' in cmd
            assert '2023-05-21 23:59:59' in cmd
            assert '--region' in cmd
            assert 'us-west-2' in cmd
            assert '--profile' in cmd
            assert 'default' in cmd

    @pytest.mark.asyncio
    async def test_sam_logs_failure(self):
        """Test SAM logs retrieval failure."""
        # Create a mock request
        request = SamLogsRequest(
            resource_name='test-function',
            project_directory=os.path.join(tempfile.gettempdir(), 'test-project'),
        )

        # Mock the subprocess.run function to raise an exception
        error_message = b'Command failed with exit code 1'
        with patch(
            'awslabs.aws_serverless_mcp_server.tools.sam.sam_logs.run_command',
            side_effect=subprocess.CalledProcessError(1, 'sam logs', stderr=error_message),
        ):
            # Call the function
            result = await handle_sam_logs(request)

            # Verify the result
            assert result['success'] is False
            assert 'Failed to fetch logs for resource' in result['message']
            assert 'Command failed with exit code 1' in result['message']

    @pytest.mark.asyncio
    async def test_sam_logs_general_exception(self):
        """Test SAM logs retrieval with a general exception."""
        # Create a mock request
        request = SamLogsRequest(
            resource_name='test-function',
            project_directory=os.path.join(tempfile.gettempdir(), 'test-project'),
        )

        # Mock the subprocess.run function to raise a general exception
        error_message = 'Some unexpected error'
        with patch(
            'awslabs.aws_serverless_mcp_server.tools.sam.sam_logs.run_command',
            side_effect=Exception(error_message),
        ):
            # Call the function
            result = await handle_sam_logs(request)

            # Verify the result
            assert result['success'] is False
            assert 'Failed to fetch logs for resource' in result['message']
            assert error_message in result['message']
