# AWS Serverless MCP Server

## Overview

This is an Model Context Protocl (MCP) server that guides AI coding assistants through building and deploying serverless applications on AWS by providing comprehensive knowledge of serverless patterns, best practices, and AWS services. This server guides coding assistants through the entire application development lifecycle, from initial design to deployment.

The MCP server is an intelligent development companion designed to support every stage of building serverless applications.
* Architecture Guidance: Helps evaluate design choices and select optimal serverless patterns based on application needs. Offers recommendations on event sources, function boundaries, and service integrations.
* AI-Powered Development: Provides rich context about serverless environments, enabling the generation of structured, best-practice-aligned code. Suggests effective use of AWS services for event processing, data persistence, and service communication.
* Operational Best Practices: Ensures alignment with AWS architectural principles. Guides implementation of security controls, performance tuning, cost optimization, and monitoring.

With AWS Serverless MCP, developers can build reliable, efficient, and production-ready serverless applications with confidence.

## Features
The set of tools provided by the Serverless MCP server can be broken down into four categories:

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
  - Provides schema registry management and discovery for AWS EventBridge events
  - Enables type-safe Lambda function development with complete event schemas

## Prerequisites
- Have an AWS account with [credentials configured](https://docs.aws.amazon.com/cli/v1/userguide/cli-configure-files.html)
- Install uv from [Astral](https://docs.astral.sh/uv/getting-started/installation/) or the [GitHub README](https://github.com/astral-sh/uv#installation)
- Install Python 3.10 or newer using uv python install 3.10 (or a more recent version)
- Install [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- Install [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

## Installation

You can download the AWS Serverless MCP Server from GitHub. To get started using your favorite code assistant with MCP support, like Q Developer, Cursor or Cline.

Add the following code to your MCP client configuration. The Serverless MCP server uses the default AWS profile by default. You only need to set the AWS_PROFILE if you want to use a different profile. Adjust the region and log level as necessary.
```json
{
  "mcpServers": {
    "awslabs.aws-serverless-mcp": {
      "command": "uvx",
      "args": [
        "awslabs.aws_serverless_mcp_server@latest",
        "--allow-write", // Enables write operations
        "--allow-sensitive-data-access" // Enables tools that return logs for AWS resources
      ],
      "env": {
          "AWS_PROFILE": "your-aws-profile",
          "AWS_REGION": "us-east-1",
          "FASTMCP_LOG_LEVEL": "ERROR"
        },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### Using Temporary Credentials
```json
{
  "mcpServers": {
    "awslabs.aws-serverless-mcp-server": {
        "command": "uvx",
        "args": ["awslabs.aws-serverless-mcp-server@latest"],
        "env": {
          "AWS_ACCESS_KEY_ID": "your-temporary-access-key",
          "AWS_SECRET_ACCESS_KEY": "your-temporary-secret-key", # pragma: allowlist secret
          "AWS_SESSION_TOKEN": "your-session-token",
          "AWS_REGION": "us-east-1",
          "FASTMCP_LOG_LEVEL": "ERROR"
        },
        "disabled": false,
        "autoApprove": []
    }
  }
}
```

## Server Configuration Options
### `--allow-write`
Enables write access mode, which allows mutating operations. By default, the server runs in read-only mode, which restricts operations to only perform read actions, preventing any changes to AWS resources.

Mutating operations:
* sam_deploy_tool: Deploys a SAM application into AWS Cloud using CloudFormation
* deploy_webapp: Generates SAM template and deploys a web application into AWS CloudFormation. Creates public resources, including Route 53 DNS records, and CloudFront distributions


### `--allow-sensitive-data-access`
Enables access to sensitive data such as logs. By default, the server restricts access to sensitive data.

Operations returning sensitive data:
* sam_logs_tool: Returns Lambda function logs and API Gateway logs

## Local Development

To make changes to this MCP locally and run it:

1. Clone this repository:
   ```bash
   git clone https://github.com/awslabs/mcp.git
   cd mcp/src/aws-serverless-mcp-server
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Configure AWS credentials:
   - Ensure you have AWS credentials configured in `~/.aws/credentials` or set the appropriate environment variables.
   - You can also set the AWS_PROFILE and AWS_REGION environment variables.

4. Run the server:
   ```bash
   python -m awslabs.aws_serverless_mcp_server.server
   ```

5. To use this MCP server with AI clients, add the following to your MCP configuration:
```json
{
  "mcpServers": {
    "awslabs.aws-serverless-mcp-server": {
        "command": "mcp/src/aws-serverless-mcp-server/bin/awslabs.aws-serverless-mcp-server/",
        "env": {
          "AWS_PROFILE": "your-aws-profile",
          "AWS_REGION": "us-east-1",
          "FASTMCP_LOG_LEVEL": "ERROR"
        },
        "disabled": false,
        "autoApprove": []
    }
  }
}
```

## Environment Variables

By default, the default AWS profile is used. However, the server can be configured through environment variables in the MCP configuration:

- `AWS_PROFILE`: AWS CLI profile to use for credentials
- `AWS_REGION`: AWS region to use (default: us-east-1)
- `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`: Explicit AWS credentials (alternative to AWS_PROFILE)
- `AWS_SESSION_TOKEN`: Session token for temporary credentials (used with AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY)
- `FASTMCP_LOG_LEVEL`: Logging level (ERROR, WARNING, INFO, DEBUG)

## Available Resources

The server provides the following resources:

### Template Resources
- `template://list`: List of available deployment templates.
- `template://{template_name}`: Details of a specific deployment template.

### Deployment Resources
- `deployment://list`: List of all AWS deployments managed by the MCP server.
- `deployment://{project_name}`: Details about a specific deployment.

## Available Tools

The server exposes deployment capabilities as tools:

### sam_init_tool

Initializes a serverless application using AWS SAM (Serverless Application Model) CLI.

**Parameters:**
- `project_name` (required): Name of the SAM project to create
- `runtime` (required): Runtime environment for the Lambda function
- `project_directory` (required): Absolute path to directory where the SAM application will be initialized
- `dependency_manager` (required): Dependency manager for the Lambda function
- `architecture`: Architecture for the Lambda function
- `package_type`: Package type for the Lambda function
- `application_template`: Template for the SAM application, e.g., hello-world, quick-start, etc.
- `application_insights`: Activate Amazon CloudWatch Application Insights monitoring
- `no_application_insights`: Deactivate Amazon CloudWatch Application Insights monitoring
- `base_image`: Base image for the application when package type is Image
- `config_env`: Environment name specifying default parameter values in the configuration file
- `config_file`: Path to configuration file containing default parameter values
- `debug`: Turn on debug logging
- `extra_content`: Override custom parameters in the template's cookiecutter.json
- `location`: Template or application location (Git, HTTP/HTTPS, zip file path)
- `save_params`: Save parameters to the SAM configuration file
- `tracing`: Activate AWS X-Ray tracing for Lambda functions
- `no_tracing`: Deactivate AWS X-Ray tracing for Lambda functions

### sam_build_tool

Builds a serverless application using AWS SAM (Serverless Application Model) CLI.

**Parameters:**
- `project_directory` (required): Absolute path to directory containing the SAM project
- `template_file`: Path to the template file (defaults to template.yaml)
- `base_dir`: Resolve relative paths to function's source code with respect to this folder
- `build_dir`: Path to a folder where the built artifacts will be stored
- `use_container`: Use a container to build the function
- `no_use_container`: Run build in local machine instead of Docker container
- `container_env_vars`: Environment variables to pass to the container
- `container_env_var_file`: Path to a JSON file containing container environment variables
- `build_image`: URI of the container image to pull for the build
- `debug`: Turn on debug logging

### sam_deploy_tool

Deploys a serverless application using AWS SAM (Serverless Application Model) CLI using CloudFormation.

**Parameters:**
- `application_name` (required): Name of the application to be deployed
- `project_directory` (required): Absolute path to directory containing the SAM project
- `template_file`: Path to the template file (defaults to template.yaml)
- `s3_bucket`: S3 bucket to deploy artifacts to
- `s3_prefix`: S3 prefix for the artifacts
- `region`: AWS region to deploy to
- `profile`: AWS profile to use
- `parameter_overrides`: CloudFormation parameter overrides encoded as key-value pairs
- `capabilities`: IAM capabilities required for the deployment
- `config_file`: Path to the SAM configuration file
- `config_env`: Environment name specifying default parameter values in the configuration file
- `use_json`: Use JSON for output
- `metadata`: Metadata to include with the stack
- `notification_arns`: SNS topic ARNs to notify about stack events
- `tags`: Tags to apply to the stack
- `resolve_s3`: Automatically create an S3 bucket for deployment artifacts
- `debug`: Turn on debug logging

### sam_logs_tool

Fetches CloudWatch logs that are generated by resources in a SAM application. Use this tool to help debug invocation failures and find root causes.

**Parameters:**
- `resource_name`: Name of the resource to fetch logs for (logical ID in CloudFormation/SAM template)
- `stack_name`: Name of the CloudFormation stack
- `filter`: Filter logs by pattern
- `start_time`: Fetch logs starting from this time (format: YYYY-MM-DD HH:MM:SS)
- `end_time`: Fetch logs up until this time (format: YYYY-MM-DD HH:MM:SS)
- `output`: Output format (text or json)
- `region`: AWS region to use
- `profile`: AWS profile to use
- `include_triggered_logs`: Include logs from explicitly triggered Lambda functions
- `cw`: Use AWS CloudWatch to fetch logs
- `resources_dir`: Directory containing resources to fetch logs for
- `template_file`: Absolute path to the SAM template file

### sam_local_invoke_tool

Locally invokes a Lambda function using AWS SAM CLI. The Lambda runtime environment is emulated locally in a Docker container.

**Parameters:**
- `project_directory` (required): Absolute path to directory containing the SAM project
- `resource_name` (required): Name of the Lambda function to invoke locally
- `template_file`: Path to the SAM template file (defaults to template.yaml)
- `event_file`: Path to a JSON file containing event data
- `event_data`: JSON string containing event data (alternative to event_file)
- `environment_variables`: Environment variables to pass to the function
- `debug_port`: Port for debugging
- `docker_network`: Docker network to run the Lambda function in
- `container_env_vars`: Environment variables to pass to the container
- `parameter`: Override parameters from the template file
- `log_file`: Path to a file where the function logs will be written
- `layer_cache_basedir`: Directory where the layers will be cached
- `region`: AWS region to use
- `profile`: AWS profile to use

### get_iac_guidance_tool

Returns guidance on selecting an infrastructure as code (IaC) platform to deploy Serverless application to AWS.

**Parameters:**
- `iac_tool`: IaC tool to use (CloudFormation, SAM, CDK, Terraform)
- `include_examples`: Whether to include examples

### get_lambda_event_schemas_tool

Returns AWS Lambda event schemas for different event sources and runtimes.

**Parameters:**
- `event_source` (required): Event source (e.g., S3, DynamoDB, API Gateway)
- `runtime` (required): Runtime for the schema references (e.g., go, nodejs, python, java)

### get_lambda_guidance_tool

Returns guidance on when to choose AWS Lambda as a deployment platform.

**Parameters:**
- `use_case` (required): Description of the use case
- `include_examples`: Whether to include examples

### deploy_webapp_tool

Deploy web applications to AWS, including Lambda as compute, DynamoDB as database, API GW, ACM certificate, and Route 53 DNS records. This tool uses the Lambda Web Adapter framework so that applications written in a standard web framework like Express or Next.js can be easily deployed to Lambda. You do not need to use any additional adapter framework when using this tool.

**Parameters:**
- `deployment_type` (required): Type of deployment (backend, frontend, fullstack)
- `project_name` (required): Project name
- `project_root` (required): Absolute path to the project root directory
- `region`: AWS region
- `backend_configuration`: Backend configuration
- `frontend_configuration`: Frontend configuration

### configure_domain_tool

Configure a custom domain for a deployed web application and associates it with a CloudFront distribution.

**Parameters:**
- `project_name` (required): Project name
- `domain_name` (required): Custom domain name
- `certificate_arn` (required): ACM certificate ARN
- `hosted_zone_id`: Route 53 hosted zone ID
- `create_route53_record`: Whether to create a Route 53 record
- `region`: AWS region to use

### deployment_help_tool

Get help information about deployments that can be done by the deploy_webapp tool.

**Parameters:**
- `deployment_type` (required): Type of deployment (backend, frontend, fullstack)

### get_metrics_tool

Get metrics from a deployed web application.

**Parameters:**
- `project_name` (required): Project name
- `metric_names` (required): List of metric names to retrieve
- `start_time`: Start time for metrics (ISO format)
- `end_time`: End time for metrics (ISO format)
- `period`: Period for metrics in seconds
- `statistics`: Statistics to retrieve
- `region`: AWS region to use

### update_frontend_tool

Update the frontend of a deployed web application.

**Parameters:**
- `project_name` (required): Project name
- `project_root` (required): Project root
- `built_assets_path` (required): Path to pre-built frontend assets
- `invalidate_cache`: Whether to invalidate the CloudFront cache
- `region`: AWS region to use

### deploy_serverless_app_help_tool

Provides instructions on how to deploy a serverless application to AWS Lambda.

**Parameters:**
- `application_type` (required): Type of application to deploy (event_driven, backend, fullstack)

### get_serverless_templates_tool

Returns example SAM templates from the Serverless Land GitHub repo.

**Parameters:**
- `template_type` (required): Template type (e.g., API, ETL, Web)
- `runtime`: Lambda runtime (e.g., nodejs18.x, python3.9)

### Schema Tools

#### list_registries_tool

Lists the registries in your account.

**Parameters:**
- `registry_name_prefix`: Limits results to registries starting with this prefix
- `scope`: Filter by registry scope (LOCAL or AWS)
- `limit`: Maximum number of results to return (1-100)
- `next_token`: Pagination token for subsequent requests

#### search_schema_tool

Search for schemas in a registry using keywords.

**Parameters:**
- `keywords` (required): Keywords to search for (prefix with "aws." for service events)
- `registry_name` (required): Registry to search in (use "aws.events" for AWS service events)
- `limit`: Maximum number of results (1-100)
- `next_token`: Pagination token

#### describe_schema_tool

Retrieve complete schema definition for specified schema version.

**Parameters:**
- `registry_name` (required): Registry containing the schema
- `schema_name` (required): Name of schema to retrieve
- `schema_version`: Version number of schema (latest by default)

## Example Usage

### Creating a Lambda Function with SAM

Example user prompt:

```
I want to build a simple backend for a todo app using Python and deploy it to the cloud with AWS Serverless. Can you help me create a new project called my-todo-app. It should include basic functionality to add and list todos. Once it's set up, please build and deploy it with all the necessary permissions. I don’t need to review the changeset before deployment.
```

This prompt would trigger the AI assistant to:
1. Initialize a new SAM project using a template.
2. Make modifications to code and infra for a todo app.
3. Build the SAM application
4. Deploy the application with CAPABILITY_IAM permissions

### Deploying a Web Application

Example user prompt:

```
I have a full-stack web app built with Node.js called my-web-app, and I want to deploy it to the cloud using AWS. Everything’s ready — both frontend and backend. Can you set it up and deploy it with AWS Lambda so it's live and works smoothly?
```

This prompt would trigger the AI assistant to use the deploy_webapp_tool to deploy the full stack application with the specified configuration.

### Working with EventBridge Schemas

Example user prompt:

```
I need to create a Lambda function that processes autoscaling events. Can you help me find the right event schema and implement type-safe event handling?
```

This prompt would trigger the AI assistant to:
1. Search for autoscaling event schemas in aws.events registry using search_schema_tool
2. Retrieve complete schema definition using describe_schema_tool
3. Generate type-safe handler code based on schema structure
4. Implement validation for required fields

## Security Features
1. **AWS Authentication**: Uses AWS credentials from the environment for secure authentication
2. **TLS Verification**: Enforces TLS verification for all AWS API calls
3. **Resource Tagging**: Tags all created resources for traceability
4. **Least Privilege**: Uses IAM roles with appropriate permissions for CloudFormation templates

## Security Considerations

### Production Use Cases
The AWS Serverless MCP Server can be used for production environments with proper security controls in place. For production use cases, consider the following:

* **Read-Only Mode by Default**: The server runs in read-only mode by default, which is safer for production environments. Only explicitly enable write access when necessary.

### Role Scoping Recommendations
To follow security best practices:

1. **Create dedicated IAM roles** to be used by the AWS Serverless MCP Server with the principle of least privilege
2. **Use separate roles** for read-only and write operations
3. **Implement resource tagging** to limit actions to resources created by the server
4. **Enable AWS CloudTrail** to audit all API calls made by the server
5. **Regularly review** the permissions granted to the server's IAM role
6. **Use IAM Access Analyzer** to identify unused permissions that can be removed

### Sensitive Information Handling
**IMPORTANT**: Do not pass secrets or sensitive information via allowed input mechanisms:

- Do not include secrets or credentials in CloudFormation templates
- Do not pass sensitive information directly in the prompt to the model

## Links

- [Homepage](https://awslabs.github.io/mcp/)
- [Documentation](https://awslabs.github.io/mcp/servers/aws-serverless-mcp-server/)
- [Source Code](https://github.com/awslabs/mcp.git)
- [Bug Tracker](https://github.com/awslabs/mcp/issues)
- [Changelog](https://github.com/awslabs/mcp/blob/main/src/aws-serverless-mcp-server/CHANGELOG.md)

## License

Apache-2.0
