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

"""Serverless MCP Server implementation"""

import argparse
from awslabs.aws_serverless_mcp_server.utils.logger import logger
import sys
from mcp.server.fastmcp import Context, FastMCP
from typing import Dict, Any

from awslabs.aws_serverless_mcp_server.utils.logger import logger
from awslabs.aws_serverless_mcp_server.resources.template_details import handle_template_details
from awslabs.aws_serverless_mcp_server.resources.deployment_details import handle_deployment_details
from awslabs.aws_serverless_mcp_server.resources.deployment_list import handle_deployments_list
from awslabs.aws_serverless_mcp_server.resources.template_list import handle_template_list

# Import all implementation modules
from awslabs.aws_serverless_mcp_server.tools.sam import (
    sam_build, sam_init, sam_deploy, sam_local_invoke, sam_logs, sam_pipeline
)
from awslabs.aws_serverless_mcp_server.tools.webapps.deploy_webapp import deploy_webapp
from awslabs.aws_serverless_mcp_server.tools.webapps.get_metrics import get_metrics
from awslabs.aws_serverless_mcp_server.tools.webapps.update_webapp_frontend import update_webapp_frontend
from awslabs.aws_serverless_mcp_server.tools.webapps.webapp_deployment_help import webapp_deployment_help
from awslabs.aws_serverless_mcp_server.tools.guidance.get_iac_guidance import get_iac_guidance
from awslabs.aws_serverless_mcp_server.tools.guidance.get_lambda_event_schemas import get_lambda_event_schemas
from awslabs.aws_serverless_mcp_server.tools.guidance.get_lambda_guidance import get_lambda_guidance
from awslabs.aws_serverless_mcp_server.tools.guidance.get_serverless_templates import get_serverless_templates
from awslabs.aws_serverless_mcp_server.tools.guidance.deploy_serverless_app_help import deploy_serverless_app_help, ApplicationType

# Import all model classes
from awslabs.aws_serverless_mcp_server.models import (
    DeployServerlessAppHelpRequest, SamBuildRequest, SamInitRequest, SamDeployRequest, SamLogsRequest, SamPipelineRequest,
    GetIaCGuidanceRequest, GetLambdaEventSchemasRequest, GetLambdaGuidanceRequest,
    GetServerlessTemplatesRequest, DeployWebAppRequest, GetMetricsRequest, UpdateFrontendRequest,
    SamLocalInvokeRequest, WebappDeploymentHelpRequest
)

allow_sensitive_data_access = False
allow_write = False

mcp = FastMCP(
    'awslabs.aws-serverless-mcp-server',
    instructions="""AWS Serverless MCP
    
    Use Serverless MCP server to deploy applications onto AWS Serverless. This server implements
    a set of tools and resources that can be used to deploy and test serverless applications.

    ## Features
    - Deploy existing web applications (fullstack, frontend, and backend) onto AWS Serverless.
    - Intialize, build, and deploy serverless applications with Serverless Application Model (SAM) CLI
    - View and logs and metrics of serverless resources
    - Get guidance on AWS Lambda use-cases, selecting an IaC framework, and deploying onto AWS Serverless
    - Get sample SAM templates of serverless applications from Serverless Land
    - Get event source schema types for Lambda runtimes

    ## Prerequisites
    1. Have an AWS account
    2. Configure AWS CLI with your credentials and profile. Set AWS_PROFILE environment variable if not using default
    3. Set AWS_REGION environment variable if not using default
    4. Install AWS CLI and SAM CLI
    """,
    dependencies=['pydantic', 'boto3'],
)

# Template resources
@mcp.resource("template://list",
              description="""List of deployment templates that can be used with the deploy_webapp tool.
                Includes frontend, backend, and fullstack templates. """)
def template_list() -> Dict[str, Any]:
    """List of available deployment templates."""
    return handle_template_list()

@mcp.resource("template://{template_name}",
              description="""Returns details of a deployment template including compatible frameworks,
                template schema, and example usage of the template""")
def template_details(template_name: str) -> Dict[str, Any]:
    """Details of a deployment template."""
    return handle_template_details(template_name)

# Deployment resources
@mcp.resource("deployment://list",
              description="Lists CloudFormation deployments managed by this MCP server.")
async def deployment_list() -> Dict[str, Any]:
    """List of all AWS deployments managed by the MCP server."""
    return await handle_deployments_list()

@mcp.resource("deployment://{project_name}",
              description="""Returns details of a CloudFormation deployment managed by this MCP server, including
                deployment type, status, and stack outputs.""")
async def deployment_details(project_name: str) -> Dict[str, Any]:
    """Get details about a specific deployment."""
    return await handle_deployment_details(project_name)

# SAM Tools
@mcp.tool(description="""
    Builds a serverless application using AWS SAM (Serverless Application Model) CLI.
    This command compiles your Lambda functions, creates deployment artifacts, and prepares your application for deployment.
    Before running this tool, the application should already be initialized with 'sam_init' tool.
    You should have AWS SAM CLI installed and configured in your environment.
    """)
async def sam_build_tool(
    ctx: Context,
    request: SamBuildRequest
) -> str:

    await ctx.info(f"Building SAM project in {request.project_directory}")
    await sam_build(request)
    return f"SAM build completed successfully for project in {request.project_directory}"

@mcp.tool(description= """
    Initializes a serverless application using AWS SAM (Serverless Application Model) CLI.
    This tool creates a new SAM project that consists of:
    - An AWS SAM template to define your infrastructure code
    - A folder structure that organizes your application
    - Configuration for your AWS Lambda functions
    You should have AWS SAM CLI installed and configured in your environment.
    """)
async def sam_init_tool(
    ctx: Context,
    request: SamInitRequest
) -> str:
    await ctx.info(f"Initializing SAM project '{request.project_name}' in {request.project_directory}")
    await sam_init(request)
    return f"SAM initialization completed successfully for project '{request.project_name}' in {request.project_directory}"

@mcp.tool(description="""
    Deploys a serverless application using AWS SAM (Serverless Application Model) CLI.
    This command deploys your application to AWS CloudFormation.
    Every time an appplication is deployed, it should be built with 'sam_build' tool before.
    You should have AWS SAM CLI installed and configured in your environment.
    """)
async def sam_deploy_tool(
    ctx: Context,
    request: SamDeployRequest
) -> str:
    if not allow_write:
        return {
            "success": False,
            "error": "Write operations are not allowed. Set --allow-write flag to true to enable write operations."
        }
    await ctx.info(f"Deploying SAM application '{request.application_name}' from {request.project_directory}")
    await sam_deploy(request)
    return f"SAM deployment completed successfully for application '{request.application_name}'"

@mcp.tool(description="""
        Fetches CloudWatch logs that are generated by resources in a SAM application. Use this tool
        to help debug invocation failures and find root causes.""")
async def sam_logs_tool(
    ctx: Context,
    request: SamLogsRequest
) -> Dict[str, Any]:
    if not allow_sensitive_data_access:
        return {
            "success": False,
            "error": "Sensitive data access is not allowed. Set --allow-sensitive-data flag to true to access logs."
        }
    await ctx.info(f"Fetching logs for Lambda function '{request.function_name}' in {request.project_directory}")
    response = await sam_logs(request)
    return response

@mcp.tool(description="""
    Locally invokes a Lambda function using AWS SAM CLI.
    This command runs your Lambda function locally in a Docker container that simulates the AWS Lambda environment.
    You can use this tool to test your Lambda functions before deploying them to AWS. Docker must be installed and running in your environment.
    """)
async def sam_local_invoke_tool(
    ctx: Context,
    request: SamLocalInvokeRequest
) -> Dict[str, Any]:
    await ctx.info(f"Locally invoking Lambda function '{request.function_name}' in {request.project_directory}")
    response = await sam_local_invoke(request)
    return response

@mcp.tool(description="""
    Sets up CI/CD pipeline configuration for AWS SAM applications.
    This tool bootstraps the necessary resources for CI/CD pipelines and generates configuration files.
    It supports multiple CI/CD providers including GitHub Actions, GitLab CI/CD, Bitbucket Pipelines, and Jenkins.
    Use this tool to automate the deployment of your serverless applications.
    """)
async def sam_pipeline_tool(
    ctx: Context,
    request: SamPipelineRequest
) -> Dict[str, Any]:
    await ctx.info(f"Setting up CI/CD pipeline for SAM project in {request.project_directory} using {request.cicd_provider}")
    response = await sam_pipeline(request)
    return response

# Guidance Tools
@mcp.tool(description="""
    Use this tool to determine if AWS Lambda is suitable platform to deploy an application.
    Returns a comprehensive guide on when to choose AWS Lambda as a deployment platform.
    It includes scenarios when to use and not use Lambda, advantages and disadvantages,
    decision criteria, and specific guidance for various use cases.
    """)
async def get_lambda_guidance_tool(
    ctx: Context,
    request: GetLambdaGuidanceRequest
) -> Dict[str, Any]:
    await ctx.info(f"Getting Lambda guidance for {request.use_case}")
    response = await get_lambda_guidance(request)
    return response

@mcp.tool(description="""
    Returns guidance on selecting an infrastructure as code (IaC) platform to deploy Serverless application to AWS.
    Choices include AWS SAM, CDK, and CloudFormation. Use this tool to decide which IaC tool to use for your Lambda deployments
    based on your specific use case and requirements.
    """)
async def get_iac_guidance_tool(
    ctx: Context,
    request: GetIaCGuidanceRequest
) -> Dict[str, Any]:
    await ctx.info(f"Getting IaC guidance for {request.iac_tool if request.iac_tool else 'all tools'}")
    response = await get_iac_guidance(request)
    return response

@mcp.tool(description="""
    Returns AWS Lambda event schemas for different event sources (e.g. s3, sns, apigw) and programming languages. Each Lambda event source
    defines its own schema and language-specific types, which should be used in the Lambda function handler to correctly parse the event data.
    If you cannot find a schema for your event source, you can directly parse the event data as a JSON object.
    """)
async def get_lambda_event_schemas_tool(
    ctx: Context,
    request: GetLambdaEventSchemasRequest
) -> Dict[str, Any]:
    
    await ctx.info(f"Getting Lambda event schemas for {request.event_source} in {request.runtime}")
    response = await get_lambda_event_schemas(request)
    return response

@mcp.tool(description="""
    Deploy web applications to AWS Serverless, including Lambda as compute, DynamoDB as databases, API GW, ACM Certificates, and Route 53 DNS records.
    This tool uses the Lambda Web Adapter framework so that applications can be written in a standard web framework like Express or Next.js can be easily
    deployed to Lambda. You do not need to use integrate the code with any adapter framework when using this tool.
    """)
async def deploy_webapp_tool(
    ctx: Context,
    request: DeployWebAppRequest
) -> Dict[str, Any]:
    if not allow_write:
        return {
            "success": False,
            "error": "Write operations are not allowed. Set --allow-write flag to true to enable write operations."
        }
    await ctx.info(f"Deploying web application '{request.project_name}' from {request.project_root}")
    response = await deploy_webapp(request)
    return response

@mcp.tool(description="""
    Get help information about using the deploy_webapp tool to perform web application deployments.
    If deployment_type is provided, returns help information for that deployment type.
    Otherwise, returns a list of deployments and general help information.
    """)
async def webapp_deployment_help_tool(
    ctx: Context,
    request: WebappDeploymentHelpRequest
) -> Dict[str, Any]:
    await ctx.info(f"Getting deployment help for {request.deployment_type}")
    response = await webapp_deployment_help(request)
    return response

@mcp.tool(description= """
    Retrieves CloudWatch metrics from a deployed web application. Use this tool get metrics
    on error rates, latency, concurrency, etc.
    """)
async def get_metrics_tool(
    ctx: Context,
    request: GetMetricsRequest
) -> Dict[str, Any]:
    await ctx.info(f"Getting metrics for project {request.project_name}")
    response = await get_metrics(request)
    return response

@mcp.tool(description="""
    Update the frontend of a deployed web application.
    This tool uploads new frontend assets to S3 and optionally invalidates the CloudFront cache.
    """)
async def update_webapp_frontend_tool(
    ctx: Context,
    request: UpdateFrontendRequest
) -> Dict[str, Any]:
    await ctx.info(f"Updating frontend for project {request.project_name}")
    response = await update_webapp_frontend(request)
    return response

@mcp.tool(description= """
    Provides instructions on how to deploy a serverless application to AWS Lambda.
    Deploying a Lambda application requires generating IaC templates, building the code, packaging
    the code, selecting a deployment tool, and executing the deployment commands. For deploying
    web applications specifically, use the deploy_webapp tool.
    """)
async def deploy_serverless_app_help_tool(
    ctx: Context,
    request: DeployServerlessAppHelpRequest
) -> Dict[str, Any]:
    # Map the string literal to the enum value
    app_type_map = {
        "event_driven": ApplicationType.EVENT_DRIVEN,
        "backend": ApplicationType.BACKEND,
        "fullstack": ApplicationType.FULLSTACK
    }
    
    await ctx.info(f"Getting deployment help for {request.application_type} application")
    response = await deploy_serverless_app_help(app_type_map[request.application_type])
    return response

@mcp.tool(description="""
    Returns example SAM templates from the Serverless Land GitHub repo. Use this tool to get
    examples for building serverless applications with AWS Lambda and best practices of serverless architecture.
    """)
async def get_serverless_templates_tool(
    ctx: Context,
    request: GetServerlessTemplatesRequest
) -> Dict[str, Any]:
    await ctx.info(f"Getting serverless templates for {request.template_type if request.template_type else 'all types'} and {request.runtime if request.runtime else 'all runtimes'}")
    response = await get_serverless_templates(request)
    return response

def main() -> int:
    """Entry point for the AWS Serverless MCP server.
    
    This function is called when the `awslabs.aws-serverless-mcp-server` command is run.
    It starts the MCP server and handles command-line arguments.
    
    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    parser = argparse.ArgumentParser(description="AWS Serverless MCP Server")
    parser.add_argument("--log-level",  help="Log level (info, debug, error)")
    parser.add_argument("--log-output", help="Absolute file path where logs are written")
    parser.add_argument("--allow-write", action='store_true', help="Enables MCP tools that make write operations")
    parser.add_argument("--allow-sensitive-data-access", action='store_true', help="Returns sensitive data from tools (e.g. logs, environment variables)")
    
    args = parser.parse_args()
    
    global allow_sensitive_data_access
    global allow_write
    allow_sensitive_data_access = True if args.allow_sensitive_data_access else False
    allow_write = True if args.allow_write else False

    if args.log_level:
        logger.set_log_level(level=args.log_level)
    if args.log_output:
        logger.set_log_directory(directory=args.log_output)
    
    try:
        mcp.run()
        return 0
    except Exception as e:
        logger.error(f"Error starting AWS Serverless MCP server: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
