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
"""Tests for the update_frontend module."""

import pytest
import os
from unittest.mock import patch, MagicMock, mock_open
from awslabs.aws_serverless_mcp_server.models import UpdateFrontendRequest
from awslabs.aws_serverless_mcp_server.tools.webapps.update_frontend import (
    update_frontend, get_all_files, upload_file_to_s3, sync_directory_to_s3
)


class TestUpdateFrontend:
    """Tests for the update_frontend module."""

    @pytest.mark.asyncio
    async def test_get_all_files(self):
        """Test the get_all_files function."""
        # Mock os.listdir and os.path.isdir
        mock_file_structure = {
            '/tmp/test-assets': ['file1.txt', 'file2.js', 'subdir'],
            '/tmp/test-assets/subdir': ['file3.css', 'file4.html']
        }
        
        def mock_listdir(path):
            return mock_file_structure.get(path, [])
        
        def mock_isdir(path):
            base_dir = os.path.dirname(path)
            file_name = os.path.basename(path)
            return file_name in mock_file_structure.get(base_dir, []) and file_name in mock_file_structure
        
        with patch('os.listdir', side_effect=mock_listdir), \
             patch('os.path.isdir', side_effect=mock_isdir):
            
            # Call the function
            files = await get_all_files('/tmp/test-assets')
            
            # Verify the result
            assert len(files) == 4
            assert '/tmp/test-assets/file1.txt' in files
            assert '/tmp/test-assets/file2.js' in files
            assert '/tmp/test-assets/subdir/file3.css' in files
            assert '/tmp/test-assets/subdir/file4.html' in files

    @pytest.mark.asyncio
    async def test_upload_file_to_s3(self):
        """Test the upload_file_to_s3 function."""
        # Mock S3 client
        mock_s3_client = MagicMock()
        
        # Mock file open
        mock_file_content = b'test file content'
        
        with patch('builtins.open', mock_open(read_data=mock_file_content)), \
             patch('mimetypes.guess_type', return_value=('text/plain', None)):
            
            # Call the function
            await upload_file_to_s3(
                mock_s3_client,
                '/tmp/test-assets/file1.txt',
                'test-bucket',
                '/tmp/test-assets'
            )
            
            # Verify S3 client was called with the correct parameters
            mock_s3_client.put_object.assert_called_once_with(
                Bucket='test-bucket',
                Key='file1.txt',
                Body=mock_file_content,
                ContentType='text/plain'
            )

    @pytest.mark.asyncio
    async def test_sync_directory_to_s3(self):
        """Test the sync_directory_to_s3 function."""
        # Mock S3 client
        mock_s3_client = MagicMock()
        
        # Mock S3 list_objects_v2 response
        mock_s3_client.list_objects_v2.return_value = {
            'Contents': [
                {'Key': 'file1.txt'},
                {'Key': 'file2.js'},
                {'Key': 'old-file.txt'}  # This file should be deleted
            ],
            'IsTruncated': False
        }
        
        # Mock get_all_files
        mock_files = [
            '/tmp/test-assets/file1.txt',
            '/tmp/test-assets/file2.js',
            '/tmp/test-assets/new-file.css'  # This file should be uploaded
        ]
        
        with patch('awslabs.aws_serverless_mcp_server.tools.webapps.update_frontend.get_all_files', return_value=mock_files), \
             patch('awslabs.aws_serverless_mcp_server.tools.webapps.update_frontend.upload_file_to_s3') as mock_upload:
            
            # Call the function
            await sync_directory_to_s3(mock_s3_client, '/tmp/test-assets', 'test-bucket')
            
            # Verify upload_file_to_s3 was called for each file
            assert mock_upload.call_count == 3
            
            # Verify delete_object was called for the old file
            mock_s3_client.delete_object.assert_called_once_with(
                Bucket='test-bucket',
                Key='old-file.txt'
            )

    @pytest.mark.asyncio
    async def test_update_frontend_success(self):
        """Test successful frontend update."""
        # Create a mock request
        request = UpdateFrontendRequest(
            project_name="test-project",
            project_root="/tmp/test-project",
            built_assets_path="/tmp/test-project/build"
        )
        
        # Mock boto3 session and clients
        mock_session = MagicMock()
        mock_cfn_client = MagicMock()
        mock_s3_client = MagicMock()
        mock_cloudfront_client = MagicMock()
        
        mock_session.client.side_effect = lambda service: {
            'cloudformation': mock_cfn_client,
            's3': mock_s3_client,
            'cloudfront': mock_cloudfront_client
        }[service]
        
        # Mock CloudFormation describe_stacks response
        mock_cfn_client.describe_stacks.return_value = {
            'Stacks': [
                {
                    'Outputs': [
                        {
                            'OutputKey': 'WebsiteBucket',
                            'OutputValue': 'test-bucket'
                        },
                        {
                            'OutputKey': 'CloudFrontDistributionId',
                            'OutputValue': 'ABCDEF12345'
                        }
                    ]
                }
            ]
        }
        
        with patch('boto3.Session', return_value=mock_session), \
             patch('os.path.exists', return_value=True), \
             patch('awslabs.aws_serverless_mcp_server.tools.webapps.update_frontend.sync_directory_to_s3') as mock_sync:
            
            # Call the function
            result = await update_frontend(request)
            
            # Verify the result
            assert result["status"] == "success"
            assert "Frontend assets updated successfully" in result["message"]
            
            # Verify sync_directory_to_s3 was called with the correct parameters
            mock_sync.assert_called_once_with(mock_s3_client, "/tmp/test-project/build", "test-bucket")
            
            # Verify CloudFront invalidation was created
            mock_cloudfront_client.create_invalidation.assert_called_once()
            args, kwargs = mock_cloudfront_client.create_invalidation.call_args
            assert kwargs["DistributionId"] == "ABCDEF12345"
            assert kwargs["InvalidationBatch"]["Paths"]["Items"] == ["/*"]

    @pytest.mark.asyncio
    async def test_update_frontend_no_cloudfront(self):
        """Test frontend update without CloudFront distribution."""
        # Create a mock request
        request = UpdateFrontendRequest(
            project_name="test-project",
            project_root="/tmp/test-project",
            built_assets_path="/tmp/test-project/build"
        )
        
        # Mock boto3 session and clients
        mock_session = MagicMock()
        mock_cfn_client = MagicMock()
        mock_s3_client = MagicMock()
        
        mock_session.client.side_effect = lambda service: {
            'cloudformation': mock_cfn_client,
            's3': mock_s3_client,
            'cloudfront': MagicMock()
        }[service]
        
        # Mock CloudFormation describe_stacks response without CloudFront output
        mock_cfn_client.describe_stacks.return_value = {
            'Stacks': [
                {
                    'Outputs': [
                        {
                            'OutputKey': 'WebsiteBucket',
                            'OutputValue': 'test-bucket'
                        }
                    ]
                }
            ]
        }
        
        with patch('boto3.Session', return_value=mock_session), \
             patch('os.path.exists', return_value=True), \
             patch('awslabs.aws_serverless_mcp_server.tools.webapps.update_frontend.sync_directory_to_s3') as mock_sync:
            
            # Call the function
            result = await update_frontend(request)
            
            # Verify the result
            assert result["status"] == "success"
            assert "Frontend assets updated successfully" in result["message"]
            
            # Verify sync_directory_to_s3 was called with the correct parameters
            mock_sync.assert_called_once_with(mock_s3_client, "/tmp/test-project/build", "test-bucket")
            
            # Verify content includes message about no CloudFront distribution
            assert any("No CloudFront distribution found" in content["text"] for content in result["content"])

    @pytest.mark.asyncio
    async def test_update_frontend_assets_not_found(self):
        """Test frontend update with assets path not found."""
        # Create a mock request
        request = UpdateFrontendRequest(
            project_name="test-project",
            project_root="/tmp/test-project",
            built_assets_path="/tmp/test-project/build"
        )
        
        with patch('os.path.exists', return_value=False):
            # Call the function
            result = await update_frontend(request)
            
            # Verify the result
            assert result["status"] == "error"
            assert "Built assets path not found" in result["message"]

    @pytest.mark.asyncio
    async def test_update_frontend_stack_not_found(self):
        """Test frontend update with CloudFormation stack not found."""
        # Create a mock request
        request = UpdateFrontendRequest(
            project_name="test-project",
            project_root="/tmp/test-project",
            built_assets_path="/tmp/test-project/build"
        )
        
        # Mock boto3 session and clients
        mock_session = MagicMock()
        mock_cfn_client = MagicMock()
        
        mock_session.client.side_effect = lambda service: {
            'cloudformation': mock_cfn_client,
            's3': MagicMock(),
            'cloudfront': MagicMock()
        }[service]
        
        # Mock CloudFormation describe_stacks to raise an exception
        mock_cfn_client.describe_stacks.side_effect = Exception("Stack does not exist")
        
        with patch('boto3.Session', return_value=mock_session), \
             patch('os.path.exists', return_value=True):
            
            # Call the function
            result = await update_frontend(request)
            
            # Verify the result
            assert result["status"] == "error"
            assert "Failed to update frontend assets" in result["message"]

    @pytest.mark.asyncio
    async def test_update_frontend_no_bucket_output(self):
        """Test frontend update with no WebsiteBucket output in CloudFormation stack."""
        # Create a mock request
        request = UpdateFrontendRequest(
            project_name="test-project",
            project_root="/tmp/test-project",
            built_assets_path="/tmp/test-project/build"
        )
        
        # Mock boto3 session and clients
        mock_session = MagicMock()
        mock_cfn_client = MagicMock()
        
        mock_session.client.side_effect = lambda service: {
            'cloudformation': mock_cfn_client,
            's3': MagicMock(),
            'cloudfront': MagicMock()
        }[service]
        
        # Mock CloudFormation describe_stacks response without WebsiteBucket output
        mock_cfn_client.describe_stacks.return_value = {
            'Stacks': [
                {
                    'Outputs': [
                        {
                            'OutputKey': 'ApiEndpoint',
                            'OutputValue': 'https://api.example.com'
                        }
                    ]
                }
            ]
        }
        
        with patch('boto3.Session', return_value=mock_session), \
             patch('os.path.exists', return_value=True):
            
            # Call the function
            result = await update_frontend(request)
            
            # Verify the result
            assert result["status"] == "error"
            assert "Could not find WebsiteBucket output" in result["message"]
