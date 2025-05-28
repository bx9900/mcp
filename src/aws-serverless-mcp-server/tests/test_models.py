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
"""Tests for the models module."""

import pytest
from awslabs.aws_serverless_mcp_server.models import (
    GetIaCGuidanceRequest,
    GetLambdaEventSchemasRequest,
    GetLambdaGuidanceRequest,
    SamBuildRequest,
    SamDeployRequest,
    SamInitRequest,
)
from pydantic import ValidationError


class TestSamBuildRequest:
    """Tests for the SamBuildRequest model."""

    def test_sam_build_request_required_fields(self):
        """Test SamBuildRequest with required fields."""
        request = SamBuildRequest(project_directory='/tmp/test-project')
        assert request.project_directory == '/tmp/test-project'
        assert request.template_file is None
        assert request.use_container is False

    def test_sam_build_request_all_fields(self):
        """Test SamBuildRequest with all fields."""
        request = SamBuildRequest(
            project_directory='/tmp/test-project',
            resource_id='MyFunction',
            template_file='template.yaml',
            base_dir='/tmp',
            build_dir='/tmp/build',
            use_container=True,
            no_use_container=False,
            container_env_vars={'NODE_ENV': 'production'},
            container_env_var_file='env.json',
            build_image='amazon/aws-sam-cli-build-image-nodejs18.x',
            debug=True,
        )
        assert request.project_directory == '/tmp/test-project'
        assert request.template_file == 'template.yaml'
        assert request.base_dir == '/tmp'
        assert request.build_dir == '/tmp/build'
        assert request.use_container is True
        assert request.no_use_container is False
        assert request.container_env_vars == {'NODE_ENV': 'production'}
        assert request.container_env_var_file == 'env.json'
        assert request.build_image == 'amazon/aws-sam-cli-build-image-nodejs18.x'
        assert request.debug is True

    def test_sam_build_request_missing_required_fields(self):
        """Test SamBuildRequest with missing required fields."""
        with pytest.raises(ValidationError):
            SamBuildRequest()


class TestSamInitRequest:
    """Tests for the SamInitRequest model."""

    def test_sam_init_request_required_fields(self):
        """Test SamInitRequest with required fields."""
        request = SamInitRequest(
            project_name='test-project',
            runtime='nodejs18.x',
            project_directory='/tmp/test-project',
            dependency_manager='npm',
        )
        assert request.project_name == 'test-project'
        assert request.runtime == 'nodejs18.x'
        assert request.project_directory == '/tmp/test-project'
        assert request.dependency_manager == 'npm'
        assert request.architecture == 'x86_64'
        assert request.package_type == 'Zip'
        assert request.application_template == 'hello-world'

    def test_sam_init_request_all_fields(self):
        """Test SamInitRequest with all fields."""
        request = SamInitRequest(
            project_name='test-project',
            runtime='nodejs18.x',
            project_directory='/tmp/test-project',
            dependency_manager='npm',
            architecture='arm64',
            package_type='Image',
            application_template='quick-start',
            application_insights=True,
            no_application_insights=False,
            base_image='amazon/nodejs18.x-base',
            config_env='dev',
            config_file='samconfig.toml',
            debug=True,
            extra_content='{"key": "value"}',
            location='https://github.com/aws/aws-sam-cli-app-templates',
            save_params=True,
            tracing=True,
            no_tracing=False,
        )
        assert request.project_name == 'test-project'
        assert request.runtime == 'nodejs18.x'
        assert request.project_directory == '/tmp/test-project'
        assert request.dependency_manager == 'npm'
        assert request.architecture == 'arm64'
        assert request.package_type == 'Image'
        assert request.application_template == 'quick-start'
        assert request.application_insights is True
        assert request.no_application_insights is False
        assert request.base_image == 'amazon/nodejs18.x-base'
        assert request.config_env == 'dev'
        assert request.config_file == 'samconfig.toml'
        assert request.debug is True
        assert request.extra_content == '{"key": "value"}'
        assert request.location == 'https://github.com/aws/aws-sam-cli-app-templates'
        assert request.save_params is True
        assert request.tracing is True
        assert request.no_tracing is False

    def test_sam_init_request_missing_required_fields(self):
        """Test SamInitRequest with missing required fields."""
        with pytest.raises(ValidationError):
            SamInitRequest(project_name='test-project', runtime='nodejs18.x')


class TestSamDeployRequest:
    """Tests for the SamDeployRequest model."""

    def test_sam_deploy_request_required_fields(self):
        """Test SamDeployRequest with required fields."""
        request = SamDeployRequest(
            application_name='test-app', project_directory='/tmp/test-project'
        )
        assert request.application_name == 'test-app'
        assert request.project_directory == '/tmp/test-project'
        assert request.template_file is None
        assert request.s3_bucket is None
        assert request.capabilities == ['CAPABILITY_IAM']

    def test_sam_deploy_request_all_fields(self):
        """Test SamDeployRequest with all fields."""
        request = SamDeployRequest(
            application_name='test-app',
            project_directory='/tmp/test-project',
            template_file='template.yaml',
            s3_bucket='my-bucket',
            s3_prefix='my-prefix',
            region='us-west-2',
            profile='default',
            parameter_overrides='ParameterKey=Key,ParameterValue=Value',
            capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM'],
            config_file='samconfig.toml',
            config_env='dev',
            metadata={'key': 'value'},
            tags={'key': 'value'},
            resolve_s3=True,
            debug=True,
        )
        assert request.application_name == 'test-app'
        assert request.project_directory == '/tmp/test-project'
        assert request.template_file == 'template.yaml'
        assert request.s3_bucket == 'my-bucket'
        assert request.s3_prefix == 'my-prefix'
        assert request.region == 'us-west-2'
        assert request.profile == 'default'
        assert request.parameter_overrides == 'ParameterKey=Key,ParameterValue=Value'
        assert request.capabilities == ['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']
        assert request.config_file == 'samconfig.toml'
        assert request.config_env == 'dev'
        assert request.metadata == {'key': 'value'}
        assert request.tags == {'key': 'value'}
        assert request.resolve_s3 is True
        assert request.debug is True


class TestGetIaCGuidanceRequest:
    """Tests for the GetIaCGuidanceRequest model."""

    def test_get_iac_guidance_request_required_fields(self):
        """Test GetIaCGuidanceRequest with required fields."""
        request = GetIaCGuidanceRequest()
        assert request.iac_tool == 'CloudFormation'
        assert request.include_examples is True

    def test_get_iac_guidance_request_all_fields(self):
        """Test GetIaCGuidanceRequest with all fields."""
        request = GetIaCGuidanceRequest(
            iac_tool='SAM',
            include_examples=False,
        )
        assert request.iac_tool == 'SAM'
        assert request.include_examples is False

    def test_get_iac_guidance_request_invalid_iac_tool(self):
        """Test GetIaCGuidanceRequest with invalid iac_tool."""
        with pytest.raises(ValidationError):
            GetIaCGuidanceRequest(resource_type='Lambda', iac_tool='Invalid')


class TestGetLambdaEventSchemasRequest:
    """Tests for the GetLambdaEventSchemasRequest model."""

    def test_get_lambda_event_schemas_request_required_fields(self):
        """Test GetLambdaEventSchemasRequest with required fields."""
        request = GetLambdaEventSchemasRequest(event_source='S3', runtime='nodejs')
        assert request.event_source == 'S3'
        assert request.runtime == 'nodejs'

    def test_get_lambda_event_schemas_request_missing_required_fields(self):
        """Test GetLambdaEventSchemasRequest with missing required fields."""
        with pytest.raises(ValidationError):
            GetLambdaEventSchemasRequest(event_source='S3')


class TestGetLambdaGuidanceRequest:
    """Tests for the GetLambdaGuidanceRequest model."""

    def test_get_lambda_guidance_request_required_fields(self):
        """Test GetLambdaGuidanceRequest with required fields."""
        request = GetLambdaGuidanceRequest(use_case='Serverless API')
        assert request.use_case == 'Serverless API'

    def test_get_lambda_guidance_request_all_fields(self):
        """Test GetLambdaGuidanceRequest with all fields."""
        request = GetLambdaGuidanceRequest(
            use_case='Serverless API',
            include_examples=False,
        )
        assert request.use_case == 'Serverless API'
        assert request.include_examples is False
