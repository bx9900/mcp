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
"""Tests for the AWS Lambda MCP Server."""

import pytest
from unittest.mock import patch, AsyncMock
from awslabs.aws_serverless_mcp_server.server import (
    sam_build_tool, sam_init_tool, sam_deploy_tool, get_iac_guidance_tool
)
import awslabs.aws_serverless_mcp_server.server
from awslabs.aws_serverless_mcp_server.models import (GetIaCGuidanceRequest, SamDeployRequest, SamBuildRequest, SamInitRequest)


class MockContext:
    """Mock context for testing."""

    async def info(self, message):
        """Mock info method."""
        pass

    async def error(self, message):
        """Mock error method."""
        pass


class TestSamBuildTool:
    """Tests for the sam_build_tool function."""

    @pytest.mark.asyncio
    async def test_sam_build_tool(self):
        """Test the sam_build_tool function."""
        ctx = MockContext()
        
        # Mock the sam_build function
        with patch('awslabs.aws_serverless_mcp_server.server.sam_build', new_callable=AsyncMock) as mock_sam_build:
            mock_sam_build.return_value = {"success": True, "message": "Build successful"}
            
            # Call the function
            result = await sam_build_tool(
                ctx,
                SamBuildRequest(
                    project_directory="/tmp/test-project"))
            
            # Verify the result
            assert result["message"] == "Build successful"
            
            # Verify sam_build was called with the correct arguments
            mock_sam_build.assert_called_once()
            args = mock_sam_build.call_args[0][0]
            assert args.project_directory == "/tmp/test-project"


class TestSamInitTool:
    """Tests for the sam_init_tool function."""

    @pytest.mark.asyncio
    async def test_sam_init_tool(self):
        """Test the sam_init_tool function."""
        ctx = MockContext()
        
        # Mock the sam_init function
        with patch('awslabs.aws_serverless_mcp_server.server.sam_init', new_callable=AsyncMock) as mock_sam_init:
            mock_sam_init.return_value = {"success": True, "message": "Initialization successful"}
            
            # Call the function
            result = await sam_init_tool(
                ctx,
                SamInitRequest(project_name="test-project", runtime="nodejs18.x", project_directory="/tmp/test-project", dependency_manager="npm")
            )
            
            # Verify the result
            assert result["message"] == "Initialization successful"
            
            # Verify sam_init was called with the correct arguments
            mock_sam_init.assert_called_once()
            args = mock_sam_init.call_args[0][0]
            assert args.project_name == "test-project"
            assert args.runtime == "nodejs18.x"
            assert args.project_directory == "/tmp/test-project"
            assert args.dependency_manager == "npm"


class TestSamDeployTool:
    """Tests for the sam_deploy_tool function."""

    @pytest.mark.asyncio
    async def test_sam_deploy_tool(self):
        """Test the sam_deploy_tool function."""
        ctx = MockContext()
        
        # Mock the sam_deploy function
        with patch('awslabs.aws_serverless_mcp_server.server.sam_deploy', new_callable=AsyncMock) as mock_sam_deploy:
            mock_sam_deploy.return_value = {"success": True, "message": "Deployment successful"}
            # Set a global variable for test
            awslabs.aws_serverless_mcp_server.server.allow_write = True
            # Call the function
            result = await sam_deploy_tool(
                ctx,
                SamDeployRequest(application_name="test-app", project_directory="/tmp/test-project")
            )
            
            # Verify the result
            assert result["message"] == "Deployment successful"
            
            # Verify sam_deploy was called with the correct arguments
            mock_sam_deploy.assert_called_once()
            args = mock_sam_deploy.call_args[0][0]
            assert args.application_name == "test-app"
            assert args.project_directory == "/tmp/test-project"


class TestGetIaCGuidanceTool:
    """Tests for the get_iac_guidance_tool function."""

    @pytest.mark.asyncio
    async def test_get_iac_guidance_tool(self):
        """Test the get_iac_guidance_tool function."""
        ctx = MockContext()
        
        # Call the function
        result = await get_iac_guidance_tool(
            ctx,
            GetIaCGuidanceRequest(iac_tool="SAM", include_examples=True)
        )
        
        # Verify the result
        assert "title" in result
        assert result["title"] == "Using AWS Infrastructure as Code (IaC) Tools for Serverless Deployments"
