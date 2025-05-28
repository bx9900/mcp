#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions
# and limitations under the License.
#

"""Serverless MCP Server implementation."""

import argparse
import boto3
import os
import sys

# Import all model classes
from awslabs.aws_serverless_mcp_server.models import (
    ConfigureDomainRequest,
    DeployServerlessAppHelpRequest,
    DeployWebAppRequest,
    GetIaCGuidanceRequest,
    GetLambdaEventSchemasRequest,
    GetLambdaGuidanceRequest,
    GetMetricsRequest,
    GetServerlessTemplatesRequest,
    SamBuildRequest,
    SamDeployRequest,
    SamInitRequest,
    SamLocalInvokeRequest,
    SamLogsRequest,
    UpdateFrontendRequest,
    WebappDeploymentHelpRequest,
)
from awslabs.aws_serverless_mcp_server.resources.deployment_details import (
    handle_deployment_details,
)
from awslabs.aws_serverless_mcp_server.resources.deployment_list import handle_deployments_list
from awslabs.aws_serverless_mcp_server.resources.template_details import handle_template_details
from awslabs.aws_serverless_mcp_server.resources.template_list import handle_template_list
from awslabs.aws_serverless_mcp_server.tools.guidance.deploy_serverless_app_help import (
    ApplicationType,
    deploy_serverless_app_help,
)
from awslabs.aws_serverless_mcp_server.tools.guidance.get_iac_guidance import get_iac_guidance
from awslabs.aws_serverless_mcp_server.tools.guidance.get_lambda_event_schemas import (
    get_lambda_event_schemas,
)
from awslabs.aws_serverless_mcp_server.tools.guidance.get_lambda_guidance import (
    get_lambda_guidance,
)
from awslabs.aws_serverless_mcp_server.tools.guidance.get_serverless_templates import (
    get_serverless_templates,
)

# Import all implementation modules
from awslabs.aws_serverless_mcp_server.tools.sam import (
    handle_sam_build,
    handle_sam_deploy,
    handle_sam_init,
    handle_sam_local_invoke,
    handle_sam_logs,
)
from awslabs.aws_serverless_mcp_server.tools.schemas.describe_schema import describe_schema_impl
from awslabs.aws_serverless_mcp_server.tools.schemas.list_registries import list_registries_impl
from awslabs.aws_serverless_mcp_server.tools.schemas.search_schema import search_schema_impl
from awslabs.aws_serverless_mcp_server.tools.webapps.configure_domain import configure_domain
from awslabs.aws_serverless_mcp_server.tools.webapps.deploy_webapp import deploy_webapp
from awslabs.aws_serverless_mcp_server.tools.webapps.get_metrics import get_metrics
from awslabs.aws_serverless_mcp_server.tools.webapps.update_webapp_frontend import (
    update_webapp_frontend,
)
from awslabs.aws_serverless_mcp_server.tools.webapps.webapp_deployment_help import (
    webapp_deployment_help,
)
from awslabs.aws_serverless_mcp_server.utils.logger import logger
from mcp.server.fastmcp import Context, FastMCP
from pydantic import Field
from typing import Any, Dict, Optional


AWS_PROFILE = os.environ.get('AWS_PROFILE', 'default')
logger.info(f'AWS_PROFILE: {AWS_PROFILE}')

AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
logger.info(f'AWS_REGION: {AWS_REGION}')

# Initialize boto3 client
schemas_client = boto3.client('schemas', region_name=AWS_REGION)


allow_sensitive_data_access = False
allow_write = False

mcp = FastMCP(
    'awslabs.aws-serverless-mcp-server',
    instructions="""AWS Serverless MCP

    This is an Model Context Protocl (MCP) server that guides AI coding assistants through building
    and deploying serverless applications on AWS by providing comprehensive knowledge of serverless patterns,
    best practices, and AWS services. This server guides coding assistants through the entire application development
    lifecycle, from initial design to deployment.

    ## Features
    1. Serverless Application Lifecycle
    - Intialize, build, and deploy Serverless Application Model (SAM) applications with SAM CLI
    - Test Lambda functions locally and remotely
    2. Web Application Deployment & Management
    - Deploy fullstack, frontend, and backend web applications onto AWS Serverless using Lambda Web Adapter.
    - Update frontend assets and optionally invaliate CloudFront caches
    - Create custom domain names, including certificate and DNS setup.
    3. Observability
    - Retrieve and logs and metrics of serverless resources
    4. Guidance, Templates, and Deployment Help
    - Provides guidance on AWS Lambda use-cases, selecting an IaC framework, and deployment process onto AWS Serverless
    - Provides sample SAM templates for different serverless application types from [Serverless Land](https://serverlessland.com/)
    - Provides schema types for different Lambda event sources and runtimes

    ## Prerequisites
    1. Have an AWS account
    2. Configure AWS CLI with your credentials and profile. Set AWS_PROFILE environment variable if not using default
    3. Set AWS_REGION environment variable if not using default
    4. Install AWS CLI and SAM CLI
    """,
    dependencies=['pydantic', 'boto3'],
)


# Template resources
@mcp.resource(
    'template://list',
    description="""List of SAM deployment templates that can be used with the deploy_webapp_tool.
                Includes frontend, backend, and fullstack templates. """,
)
def template_list() -> Dict[str, Any]:
    """Retrieves a list of all available deployment templates.

    Returns:
        Dict[str, Any]: A dictionary containing the list of available templates.
    """
    return handle_template_list()


@mcp.resource(
    'template://{template_name}',
    description="""Returns details of a deployment template including compatible frameworks,
                template schema, and example usage of the template""",
)
def template_details(template_name: str) -> Dict[str, Any]:
    """Retrieves detailed information about a specific deployment template.

    Args:
        template_name (str): The name of the template to retrieve details for.

    Returns:
        Dict[str, Any]: A dictionary containing the template details.
    """
    return handle_template_details(template_name)


# Deployment resources
@mcp.resource(
    'deployment://list', description='Lists CloudFormation deployments managed by this MCP server.'
)
async def deployment_list() -> Dict[str, Any]:
    """Asynchronously retrieves a list of all AWS deployments managed by the MCP server.

    Returns:
        Dict[str, Any]: A dictionary containing the list of deployments.
    """
    return await handle_deployments_list()


@mcp.resource(
    'deployment://{project_name}',
    description="""Returns details of a CloudFormation deployment managed by this MCP server, including
                deployment type, status, and stack outputs.""",
)
async def deployment_details(project_name: str) -> Dict[str, Any]:
    """Asynchronously retrieves detailed information about a specific deployment.

    Args:
        project_name (str): The name of the project deployment to retrieve details for.

    Returns:
        Dict[str, Any]: A dictionary containing the deployment details.
    """
    return await handle_deployment_details(project_name)


# SAM Tools
@mcp.tool(
    description="""
    Builds a serverless application using AWS SAM (Serverless Application Model) CLI.
    This command compiles your Lambda function code, creates deployment artifacts, and prepares your application for deployment.
    Before running this tool, the application should already be initialized with 'sam_init' tool.
    You should have AWS SAM CLI installed and configured in your environment.
    """
)
async def sam_build_tool(ctx: Context, request: SamBuildRequest) -> dict[str, Any]:
    """Asynchronously builds an AWS SAM project using the provided context and build request.

    Args:
        ctx (Context): The execution context, used for logging and other contextual operations.
        request (SamBuildRequest): The build request containing parameters such as the project directory.

    Returns:
        str: The output or result of the SAM build process.
    """
    await ctx.info(f'Building SAM project in {request.project_directory}')
    return await handle_sam_build(request)


@mcp.tool(
    description="""
    Initializes a serverless application using AWS SAM (Serverless Application Model) CLI.
    This tool creates a new SAM project that consists of:
    - An AWS SAM template to define your infrastructure code
    - A folder structure that organizes your application
    - Configuration for your AWS Lambda functions
    You should have AWS SAM CLI installed and configured in your environment.
    """
)
async def sam_init_tool(ctx: Context, request: SamInitRequest) -> dict[str, Any]:
    """Asynchronously initializes a new AWS SAM project with the provided configuration.

    Args:
        ctx (Context): The execution context, used for logging and other contextual operations.
        request (SamInitRequest): The initialization request containing parameters such as project name and directory.

    Returns:
        str: The output or result of the SAM initialization process.
    """
    await ctx.info(
        f"Initializing SAM project '{request.project_name}' in {request.project_directory}"
    )
    return await handle_sam_init(request)


@mcp.tool(
    description="""
    Deploys a serverless application using AWS SAM (Serverless Application Model) CLI.
    This command deploys your application to AWS CloudFormation.
    Every time an appplication is deployed, it should be built with 'sam_build' tool before.
    You should have AWS SAM CLI installed and configured in your environment.
    """
)
async def sam_deploy_tool(ctx: Context, request: SamDeployRequest) -> Dict[str, Any]:
    """Asynchronously deploys an AWS SAM project to AWS CloudFormation.

    Args:
        ctx (Context): The execution context, used for logging and other contextual operations.
        request (SamDeployRequest): The deployment request containing parameters such as application name and project directory.

    Returns:
        str: The output or result of the SAM deployment process.
    """
    if not allow_write:
        return {
            'success': False,
            'error': 'Write operations are not allowed. Set --allow-write flag to true to enable write operations.',
        }
    await ctx.info(
        f"Deploying SAM application '{request.application_name}' from {request.project_directory}"
    )
    return await handle_sam_deploy(request)


@mcp.tool(
    description="""
        Fetches CloudWatch logs that are generated by resources in a SAM application. Use this tool
        to help debug invocation failures and find root causes."""
)
async def sam_logs_tool(ctx: Context, request: SamLogsRequest) -> Dict[str, Any]:
    """Asynchronously fetches CloudWatch logs for resources in a SAM application.

    Args:
        ctx (Context): The execution context, used for logging and other contextual operations.
        request (SamLogsRequest): The logs request containing parameters such as resource name and stack name.

    Returns:
        Dict[str, Any]: A dictionary containing the logs and related information.
    """
    if not allow_sensitive_data_access:
        return {
            'success': False,
            'error': 'Sensitive data access is not allowed. Set --allow-sensitive-data flag to true to access logs.',
        }
    await ctx.info(f"Fetching logs for resource '{request.resource_name}'")
    response = await handle_sam_logs(request)
    return response


@mcp.tool(
    description="""
    Locally invokes a Lambda function using AWS SAM CLI.
    This command runs your Lambda function locally in a Docker container that simulates the AWS Lambda environment.
    You can use this tool to test your Lambda functions before deploying them to AWS. Docker must be installed and running in your environment.
    """
)
async def sam_local_invoke_tool(ctx: Context, request: SamLocalInvokeRequest) -> Dict[str, Any]:
    """Asynchronously invokes an AWS SAM local resource for testing purposes.

    Args:
        ctx (Context): The execution context, used for logging and other contextual operations.
        request (SamLocalInvokeRequest): The request object containing details about the resource to invoke and the project directory.

    Returns:
        Dict[str, Any]: The response from the local invocation of the specified SAM resource.
    """
    await ctx.info(
        f"Locally invoking resource '{request.resource_name}' in {request.project_directory}"
    )
    response = await handle_sam_local_invoke(request)
    return response


# Guidance Tools
@mcp.tool(
    description="""
    Use this tool to determine if AWS Lambda is suitable platform to deploy an application.
    Returns a comprehensive guide on when to choose AWS Lambda as a deployment platform.
    It includes scenarios when to use and not use Lambda, advantages and disadvantages,
    decision criteria, and specific guidance for various use cases.
    """
)
async def get_lambda_guidance_tool(
    ctx: Context, request: GetLambdaGuidanceRequest
) -> Dict[str, Any]:
    """Asynchronously retrieves Lambda guidance based on the provided use case request.

    Args:
        ctx (Context): The context object, used for logging and request context.
        request (GetLambdaGuidanceRequest): The request object containing the use case for which guidance is needed.

    Returns:
        Dict[str, Any]: A dictionary containing the Lambda guidance response.
    """
    await ctx.info(f'Getting Lambda guidance for {request.use_case}')
    response = await get_lambda_guidance(request)
    return response


@mcp.tool(
    description="""
    Returns guidance on selecting an infrastructure as code (IaC) platform to deploy Serverless application to AWS.
    Choices include AWS SAM, CDK, and CloudFormation. Use this tool to decide which IaC tool to use for your Lambda deployments
    based on your specific use case and requirements.
    """
)
async def get_iac_guidance_tool(ctx: Context, request: GetIaCGuidanceRequest) -> Dict[str, Any]:
    """Asynchronously retrieves guidance on selecting an Infrastructure as Code (IaC) platform.

    Args:
        ctx (Context): The execution context, used for logging and other contextual operations.
        request (GetIaCGuidanceRequest): The request object containing parameters such as the IaC tool.

    Returns:
        Dict[str, Any]: A dictionary containing the IaC guidance information.
    """
    await ctx.info(
        f'Getting IaC guidance for {request.iac_tool if request.iac_tool else "all tools"}'
    )
    response = await get_iac_guidance(request)
    return response


@mcp.tool(
    description="""
    Returns AWS Lambda event schemas for different event sources (e.g. s3, sns, apigw) and programming languages.  Each Lambda event source defines its own schema and language-specific types, which should be used in
    the Lambda function handler to correctly parse the event data. If you cannot find a schema for your event source, you can directly parse
    the event data as a JSON object. For EventBridge events,
    you must use the list_registries, search_schema, and describe_schema tools to access the schema registry directly, get schema definitions,
    and generate code processing logic.
    """
)
async def get_lambda_event_schemas_tool(
    ctx: Context, request: GetLambdaEventSchemasRequest
) -> Dict[str, Any]:
    """Asynchronously retrieves AWS Lambda event schemas for different event sources and programming languages.

    Args:
        ctx (Context): The execution context, used for logging and other contextual operations.
        request (GetLambdaEventSchemasRequest): The request object containing the event source and runtime.

    Returns:
        Dict[str, Any]: A dictionary containing the Lambda event schemas.
    """
    await ctx.info(f'Getting Lambda event schemas for {request.event_source} in {request.runtime}')
    response = await get_lambda_event_schemas(request)
    return response


@mcp.tool(
    description="""
    Deploy web applications to AWS Serverless, including Lambda as compute, DynamoDB as databases, API GW, ACM Certificates, and Route 53 DNS records.
    This tool uses the Lambda Web Adapter framework so that applications can be written in a standard web framework like Express or Next.js can be easily
    deployed to Lambda. You do not need to use integrate the code with any adapter framework when using this tool.
    """
)
async def deploy_webapp_tool(ctx: Context, request: DeployWebAppRequest) -> Dict[str, Any]:
    """Asynchronously deploys a web application to AWS Serverless infrastructure.

    Args:
        ctx (Context): The execution context, used for logging and other contextual operations.
        request (DeployWebAppRequest): The deployment request containing parameters such as project name and root directory.

    Returns:
        Dict[str, Any]: A dictionary containing the deployment results and information.
    """
    if not allow_write:
        return {
            'success': False,
            'error': 'Write operations are not allowed. Set --allow-write flag to true to enable write operations.',
        }
    await ctx.info(
        f"Deploying web application '{request.project_name}' from {request.project_root}"
    )
    response = await deploy_webapp(request)
    return response


@mcp.tool(
    description="""
    Get help information about using the deploy_webapp_tool to perform web application deployments.
    If deployment_type is provided, returns help information for that deployment type.
    Otherwise, returns a list of deployments and general help information.
    """
)
async def webapp_deployment_help_tool(
    ctx: Context, request: WebappDeploymentHelpRequest
) -> Dict[str, Any]:
    """Asynchronously retrieves help information about web application deployments.

    Args:
        ctx (Context): The execution context, used for logging and other contextual operations.
        request (WebappDeploymentHelpRequest): The request object containing the deployment type.

    Returns:
        Dict[str, Any]: A dictionary containing the deployment help information.
    """
    await ctx.info(f'Getting deployment help for {request.deployment_type}')
    response = await webapp_deployment_help(request)
    return response


@mcp.tool(
    description="""
    Retrieves CloudWatch metrics from a deployed web application. Use this tool get metrics
    on error rates, latency, concurrency, etc.
    """
)
async def get_metrics_tool(ctx: Context, request: GetMetricsRequest) -> Dict[str, Any]:
    """Asynchronously retrieves CloudWatch metrics for a deployed web application.

    Args:
        ctx (Context): The execution context, used for logging and other contextual operations.
        request (GetMetricsRequest): The request object containing parameters such as project name and time range.

    Returns:
        Dict[str, Any]: A dictionary containing the metrics data.
    """
    await ctx.info(f'Getting metrics for project {request.project_name}')
    response = await get_metrics(request)
    return response


@mcp.tool(
    description="""
    Update the frontend assets of a deployed web application.
    This tool uploads new frontend assets to S3 and optionally invalidates the CloudFront cache.
    """
)
async def update_webapp_frontend_tool(
    ctx: Context, request: UpdateFrontendRequest
) -> Dict[str, Any]:
    """Asynchronously updates the frontend assets of a deployed web application.

    Args:
        ctx (Context): The execution context, used for logging and other contextual operations.
        request (UpdateFrontendRequest): The request object containing parameters such as project name and assets path.

    Returns:
        Dict[str, Any]: A dictionary containing the update results.
    """
    await ctx.info(f'Updating frontend for project {request.project_name}')
    response = await update_webapp_frontend(request)
    return response


@mcp.tool(
    description="""
    Configures a custom domain for a deployed web application on AWS Serverless.
    This tool sets up Route 53 DNS records, ACM certificates, and CloudFront custom domain mappings as needed.
    Use this tool after deploying your web application to associate it with your own domain name.
    """
)
async def configure_domain_tool(ctx: Context, request: ConfigureDomainRequest) -> Dict[str, Any]:
    """Asynchronously configures a custom domain for a deployed web application.

    Args:
        ctx (Context): The execution context, used for logging and other contextual operations.
        request (ConfigureDomainRequest): The request object containing parameters such as project name and domain name.

    Returns:
        Dict[str, Any]: A dictionary containing the domain configuration results.
    """
    return await configure_domain(request)


@mcp.tool(
    description="""
    Provides instructions on how to deploy a serverless application to AWS Lambda.
    Deploying a Lambda application requires generating IaC templates, building the code, packaging
    the code, selecting a deployment tool, and executing the deployment commands. For deploying
    web applications specifically, use the deploy_webapp tool.
    """
)
async def deploy_serverless_app_help_tool(
    ctx: Context, request: DeployServerlessAppHelpRequest
) -> Dict[str, Any]:
    """Asynchronously provides instructions on how to deploy a serverless application to AWS Lambda.

    Args:
        ctx (Context): The execution context, used for logging and other contextual operations.
        request (DeployServerlessAppHelpRequest): The request object containing the application type.

    Returns:
        Dict[str, Any]: A dictionary containing the deployment help information.
    """
    # Map the string literal to the enum value
    app_type_map = {
        'event_driven': ApplicationType.EVENT_DRIVEN,
        'backend': ApplicationType.BACKEND,
        'fullstack': ApplicationType.FULLSTACK,
    }

    await ctx.info(f'Getting deployment help for {request.application_type} application')
    response = await deploy_serverless_app_help(app_type_map[request.application_type])
    return response


@mcp.tool(
    description="""
    Returns example SAM templates from the Serverless Land GitHub repo. Use this tool to get
    examples for building serverless applications with AWS Lambda and best practices of serverless architecture.
    """
)
async def get_serverless_templates_tool(
    ctx: Context, request: GetServerlessTemplatesRequest
) -> Dict[str, Any]:
    """Asynchronously retrieves example SAM templates from the Serverless Land GitHub repository.

    Args:
        ctx (Context): The execution context, used for logging and other contextual operations.
        request (GetServerlessTemplatesRequest): The request object containing parameters such as template type and runtime.

    Returns:
        Dict[str, Any]: A dictionary containing the serverless templates.
    """
    await ctx.info(
        f'Getting serverless templates for {request.template_type if request.template_type else "all types"} and {request.runtime if request.runtime else "all runtimes"}'
    )
    response = await get_serverless_templates(request)
    return response


@mcp.tool()
async def list_registries(
    ctx: Context,
    registry_name_prefix: Optional[str] = Field(
        default=None,
        description='Specifying this limits the results to only those registry names that start with the specified prefix. For EventBridge events, use aws.events registry directly instead of searching.',
    ),
    scope: Optional[str] = Field(
        default=None,
        description="""Can be set to Local or AWS to limit responses to your custom registries, or the ones provided by AWS.
        LOCAL: The registry is created in your account.
        AWS: The registry is created by AWS.

        For EventBridge events, use aws.events registry which is an AWS-managed registry containing all AWS service event schemas.""",
    ),
    limit: Optional[int] = Field(
        default=None,
        description='Maximum number of results to return. If you specify 0, the operation returns up to 10 results.',
        ge=0,
        le=100,
    ),
    next_token: Optional[str] = Field(
        default=None, description='Next token returned by the previous operation.'
    ),
) -> Dict:
    """Lists the registries in your account.

    REQUIREMENTS:
    - For AWS service events, you MUST use the aws.events registry directly
    - For custom schemas, you MAY use LOCAL scope to manage your own registries
    - When searching AWS service events, you SHOULD use the AWS scope

    USAGE PATTERNS:
    1. Finding AWS Service Event Schemas:
    - Use aws.events registry directly instead of searching
    - Filter by AWS scope to see only AWS-provided schemas

    2. Managing Custom Schemas:
    - Use LOCAL scope to view your custom registries
    - Apply registry_name_prefix to find specific registry groups
    """
    return await list_registries_impl(
        schemas_client,
        registry_name_prefix=registry_name_prefix,
        scope=scope,
        limit=limit,
        next_token=next_token,
    )


@mcp.tool()
async def search_schema(
    ctx: Context,
    keywords: str = Field(
        description='Keywords to search for. Prefix service names with "aws." for better results (e.g., "aws.s3" for S3 events, "aws.ec2" for EC2 events).'
    ),
    registry_name: str = Field(
        description='For AWS service events, use "aws.events" to search the EventBridge schema registry.'
    ),
    limit: Optional[int] = Field(
        default=None,
        description='Maximum number of results to return. If you specify 0, the operation returns up to 10 results.',
        ge=0,
        le=100,
    ),
    next_token: Optional[str] = Field(
        default=None, description='Next token returned by the previous operation.'
    ),
) -> Dict:
    """Search for schemas in a registry using keywords.

    REQUIREMENTS:
    - You MUST use this tool to find schemas for AWS service events
    - You MUST search in the "aws.events" registry for AWS service events
    - You MUST use this tool when implementing Lambda functions that consume events from EventBridge
    - You SHOULD prefix search keywords with "aws." for optimal results (e.g., "aws.s3", "aws.ec2")
    - You MAY filter results using additional keywords for specific event types

    USE CASES:

    1. Lambda Function Development with EventBridge:
    - CRITICAL: Required for Lambda functions consuming events from EventBridge
    - Search for event schemas your function needs to process
    - Example: "aws.s3" for S3 events, "aws.dynamodb" for DynamoDB streams
    - Use results with describe_schema to get complete event structure

    2. EventBridge Rule Creation:
    - Find schemas to create properly structured event patterns
    - Example: "aws.ec2" for EC2 instance state changes
    - Ensure exact field names and types in rule patterns

    IMPLEMENTATION FLOW:
    1. Search aws.events registry for service schemas
    2. Note relevant schema names from results
    3. Use describe_schema to get complete definitions
    4. Implement handlers using exact schema structure
    """
    return await search_schema_impl(
        schemas_client,
        keywords=keywords,
        registry_name=registry_name,
        limit=limit,
        next_token=next_token,
    )


@mcp.tool()
async def describe_schema(
    ctx: Context,
    registry_name: str = Field(
        description='For AWS service events, use "aws.events" to access the EventBridge schema registry.'
    ),
    schema_name: str = Field(
        description='The name of the schema to retrieve (e.g., "aws.s3@ObjectCreated" for S3 events).'
    ),
    schema_version: Optional[str] = Field(
        default=None,
        description='Version number of the schema. For AWS service events, use latest version (default) to ensure up-to-date event handling.',
    ),
) -> Dict:
    """Retrieve the schema definition for the specified schema version.

    REQUIREMENTS:
    - You MUST use this tool to get complete schema definitions before implementing handlers
    - You MUST use this tool when implementing Lambda functions that consume events from EventBridge
    - You MUST use the returned schema structure for type-safe event handling
    - You SHOULD use the latest schema version unless specifically required otherwise
    - You MUST validate all required fields defined in the schema

    USE CASES:

    1. Lambda Function Handlers with EventBridge:
    You MUST:
    - CRITICAL: Required for Lambda functions consuming events from EventBridge
    - Implement handlers using the exact event structure
    - Validate all required fields defined in schema
    - Handle optional fields appropriately
    - Ensure type safety for EventBridge-sourced events

    You SHOULD:
    - Generate strongly typed code based on schema
    - Implement error handling for missing fields
    - Document any assumptions about structure

    2. EventBridge Rules:
    You MUST:
    - Create patterns that exactly match schema
    - Use correct field names and value types
    - Include all required fields in patterns

    You SHOULD:
    - Test patterns against sample events
    - Document pattern matching logic
    - Consider schema versions in design

    The schema content provides complete event structure with all fields and types, ensuring correct event handling.
    """
    return await describe_schema_impl(
        schemas_client,
        registry_name=registry_name,
        schema_name=schema_name,
        schema_version=schema_version,
    )


def main() -> int:
    """Entry point for the AWS Serverless MCP server.

    This function is called when the `awslabs.aws-serverless-mcp-server` command is run.
    It starts the MCP server and handles command-line arguments.

    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    parser = argparse.ArgumentParser(description='AWS Serverless MCP Server')
    parser.add_argument('--log-level', help='Log level (info, debug, error)')
    parser.add_argument('--log-output', help='Absolute file path where logs are written')
    parser.add_argument(
        '--allow-write', action='store_true', help='Enables MCP tools that make write operations'
    )
    parser.add_argument(
        '--allow-sensitive-data-access',
        action='store_true',
        help='Returns sensitive data from tools (e.g. logs, environment variables)',
    )

    args = parser.parse_args()

    global allow_sensitive_data_access
    global allow_write
    allow_sensitive_data_access = True if args.allow_sensitive_data_access else False
    allow_write = True if args.allow_write else False

    if args.log_level:
        from awslabs.aws_serverless_mcp_server.utils.logger import set_log_level

        set_log_level(level=args.log_level)
    if args.log_output:
        from awslabs.aws_serverless_mcp_server.utils.logger import set_log_directory

        set_log_directory(directory=args.log_output)

    try:
        mcp.run()
        return 0
    except Exception as e:
        logger.error(f'Error starting AWS Serverless MCP server: {e}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
