# AWS Serverless MCP Server

## Overview

This MCP server enables AI assistants to build and deploy applications onto AWS Serverless using Serverless Application Model (SAM). It implements a set of tools and resources that can be used to interact with serverless services.

## Features
- Deploy existing web applications (fullstack, frontend, and backend) onto AWS Serverless using Lambda Web Adapter.
- Intialize, build, and deploy Serverless Application Model (SAM) applications with SAM CLI
- Access and logs and metrics of serverless resources
- Build CI/CD piplines to automate deployments
- Get guidance on AWS Lambda use-cases, selecting an IaC framework, and deployment process onto AWS Serverless
- Get sample SAM templates of serverless applications from Serverless Land
- Get schema types for different Lambda event sources and runtimes

## Prerequisites
- Have an AWS account with [credentials configured](https://docs.aws.amazon.com/cli/v1/userguide/cli-configure-files.html)
- Install uv from [Astral](https://docs.astral.sh/uv/getting-started/installation/) or the [GitHub README](https://github.com/astral-sh/uv#installation)
- Install Python 3.10 or newer using uv python install 3.10 (or a more recent version)
- Install [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- Install [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

## Installation

To use this MCP server with an AWS CLI profile, add the following to your MCP configuration:
```json
{
  "mcpServers": {
    "awslabs.aws-serverless-mcp": {
      "command": "uvx",
      "args": [
        "awslabs.aws_serverless_mcp_server@latest"
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
          "AWS_SECRET_ACCESS_KEY": "your-temporary-secret-key",
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

### Arguments
To enable write operations and logs access, you must explicitly arguments in the MCP configuration. By default these operations are disabled.
--allow-write: Enables write operations (sam_deploy and deploy_webapp tools)
--allow-sensitive-data: Enables tools that return logs for AWS resources (sam_logs tool)

```json
{
  "mcpServers": {
    "awslabs.aws-serverless-mcp": {
      "command": "uvx",
      "args": [
        "awslabs.aws_serverless_mcp_server@latest"
        "--allow-write",
        "allow-sensitive-data"
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
- `resource_id`: ID of the resource to build (builds a single resource)
- `template_file`: Path to the template file (defaults to template.yaml)
- `base_dir`: Resolve relative paths to function's source code with respect to this folder
- `build_dir`: Path to a folder where the built artifacts will be stored
- `cache_dir`: Path to a folder where the built artifacts will be cached
- `cached`: Use cached build artifacts if available
- `use_container`: Use a container to build the function
- `no_use_container`: Run build in local machine instead of Docker container
- `container_env_vars`: Environment variables to pass to the container
- `container_env_var_file`: Path to a JSON file containing container environment variables
- `skip_pull_image`: Skip pulling the latest Docker image for the runtime
- `build_method`: Build method to use
- `build_in_source`: Build your project directly in the source folder
- `no_build_in_source`: Do not build your project directly in the source folder
- `beta_features`: Allow beta features
- `no_beta_features`: Deny beta features
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
- `no_confirm_changeset`: Don't prompt for confirmation before deploying the changeset
- `config_file`: Path to the SAM configuration file
- `config_env`: Environment name specifying default parameter values in the configuration file
- `no_execute_changeset`: Don't execute the changeset (preview only)
- `fail_on_empty_changeset`: Fail the deployment if the changeset is empty
- `force_upload`: Force upload artifacts even if they exist in the S3 bucket
- `use_json`: Use JSON for output
- `metadata`: Metadata to include with the stack
- `notification_arns`: SNS topic ARNs to notify about stack events
- `tags`: Tags to apply to the stack
- `resolve_s3`: Automatically create an S3 bucket for deployment artifacts
- `disable_rollback`: Disable rollback on deployment failure
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

### sam_pipeline_tool

Sets up CI/CD pipeline configuration for AWS SAM applications.

**Parameters:**
- `project_directory` (required): Absolute path to directory containing the SAM project
- `cicd_provider` (required): CI/CD provider to use (e.g., github-actions, gitlab-ci, bitbucket-pipelines, jenkins)
- `bucket`: S3 bucket to store artifacts
- `bootstrap_ecr`: Whether to bootstrap ECR repository
- `bitbucket_repo_uuid`: Bitbucket repository UUID
- `cloudformation_execution_role`: IAM role for CloudFormation execution
- `confirm_changes`: Whether to confirm changes before deployment
- `config_env`: Environment name specifying default parameter values in the configuration file
- `config_file`: Path to the SAM configuration file
- `create_image_repository`: Whether to create an ECR repository
- `debug`: Turn on debug logging
- `deployment_branch`: Git branch for deployments
- `github_org`: GitHub organization name
- `gitlab_group`: GitLab group name
- `gitlab_project`: GitLab project name
- `git_provider`: Git provider (e.g., github, gitlab, bitbucket)
- `image_repository`: ECR repository URI
- `interactive`: Whether to run in interactive mode
- `oidc_client_id`: OIDC client ID
- `oidc_provider`: OIDC provider
- `oidc_provider_url`: OIDC provider URL
- `output_dir`: Directory to output generated files
- `parameter_overrides`: CloudFormation parameter overrides
- `permissions_provider`: Permissions provider (e.g., iam, oidc)
- `pipeline_execution_role`: IAM role for pipeline execution
- `pipeline_user`: IAM user for pipeline execution
- `profile`: AWS profile to use
- `region`: AWS region to deploy to
- `save_params`: Whether to save parameters to the SAM configuration file
- `stage`: Deployment stage

### sam_local_invoke_tool

Locally invokes a Lambda function using AWS SAM CLI. The Lambda runtime environment is emulated locally in a Docker container.

**Parameters:**
- `project_directory` (required): Absolute path to directory containing the SAM project
- `function_name` (required): Name of the Lambda function to invoke locally
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
- `skip_pull_image`: Skip pulling the latest Docker image for the runtime
- `debug_args`: Additional arguments to pass to the debugger
- `debugger_path`: Path to the debugger to use
- `warm_containers`: Warm containers strategy
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

## Example Usage

### Creating a Lambda Function with SAM

Example user prompt:

```
I want to create a new AWS Lambda function using SAM. Can you help me create a Python hello-world application called "my-sam-app" in the "/path/to/project" directory? After creating it, please build and deploy it with the necessary IAM capabilities. I don't need to review the changeset before deployment.
```

This prompt would trigger the AI assistant to:
1. Initialize a new SAM project with the hello-world template
2. Build the SAM application
3. Deploy the application with CAPABILITY_IAM permissions

### Deploying a Web Application

Example user prompt:

```
I need to deploy a Node.js backend web application to AWS Lambda. The project is called "my-web-app" and is located at "/path/to/project". The built artifacts are in "/path/to/artifacts". The app runs on port 3000 and needs 512MB of memory with a 30-second timeout. Can you deploy this for me?
```

This prompt would trigger the AI assistant to use the deploy_webapp_tool to deploy the backend application with the specified configuration.

### Individual SAM Tool Examples

#### SAM Initialize

Example user prompt:

```
Can you initialize a new SAM project for me? I want to create a Python application called "weather-api" using the "hello-world" template. Please set it up in my "/projects/aws-lambda" directory and use pip as the dependency manager.
```

#### SAM Build

Example user prompt:

```
I need to build my SAM application located in "/projects/aws-lambda/weather-api". Can you build it for me? I'd like to use a container for the build process and cache the build artifacts for faster builds in the future.
```

#### SAM Deploy

Example user prompt:

```
Please deploy my SAM application called "weather-api" from the "/projects/aws-lambda/weather-api" directory. I need to include IAM capabilities and I don't want to be prompted to confirm the changeset. Also, please use the "us-west-2" region for deployment.
```

#### SAM Local Invoke

Example user prompt:

```
I want to test my Lambda function locally before deploying it. Can you invoke the "GetWeatherFunction" from my SAM project in "/projects/aws-lambda/weather-api"? Here's the test event data: {"city": "Seattle", "country": "USA"}
```

#### SAM Pipeline

Example user prompt:

```
I need to set up a CI/CD pipeline for my SAM application in "/projects/aws-lambda/weather-api". Can you configure a GitHub Actions pipeline for me? I want to deploy from the "main" branch to the "us-west-2" region. Please create the necessary IAM roles and resources for the pipeline.
```

#### SAM Logs

Example user prompt:

```
I need to debug an issue with my Lambda function in the "weather-api" stack. Can you fetch the CloudWatch logs for the "GetWeatherFunction" resource? I only want to see error messages from the last hour, and please format the output as JSON.
```

#### Retrieving Web Application Logs

Example user prompt:

```
Can you show me the logs for my "weather-api" application that I deployed? I'm particularly interested in logs from the last 30 minutes, and I only need to see errors related to API requests. Please limit the results to 100 log entries.
```

This prompt would trigger the AI assistant to use the get_logs_tool to retrieve filtered logs from the deployed application.

### Additional Tool Examples

#### Lambda Guidance

Example user prompt:

```
I'm building a REST API that needs to process requests with low latency. Would AWS Lambda be a good choice for this? I'm planning to use Python 3.9 and would like to understand the pros and cons of using Lambda for this use case.
```

#### IaC Guidance

Example user prompt:

```
I need to deploy a serverless application to AWS that includes Lambda functions, API Gateway, and DynamoDB. Which Infrastructure as Code tool would be best for this? I'm familiar with both Python and JavaScript.
```

#### Lambda Event Schemas

Example user prompt:

```
I'm writing a Lambda function in Node.js that will be triggered by S3 events. Can you show me what the event object structure looks like so I know how to parse it in my code?
```

#### Configure Custom Domain

Example user prompt:

```
I've deployed my web application "my-portfolio" to AWS and now I want to use my custom domain "example.com" for it. I already have an ACM certificate with ARN "arn:aws:acm:us-east-1:123456789012:certificate/abcd1234" and my Route 53 hosted zone ID is "Z1234ABCD5678EF". Can you help me set this up?
```

#### Deployment Help

Example user prompt:

```
I'm trying to deploy a fullstack application to AWS but I'm not sure how to structure it. Can you provide guidance on the best practices for deploying fullstack applications with serverless technologies?
```

#### Application Metrics

Example user prompt:

```
Can you show me the performance metrics for my "user-auth-service" application? I'd like to see the error rate, latency, and invocation count for the past 24 hours.
```

#### Update Frontend

Example user prompt:

```
I've made changes to the frontend of my "customer-portal" application. The updated files are in "/projects/customer-portal/build". Can you update the deployed frontend and invalidate the CloudFront cache so users see the changes immediately?
```

#### Serverless App Deployment Help

Example user prompt:

```
I want to create an event-driven application that processes data from an S3 bucket. Can you guide me through the process of deploying this type of serverless application to AWS?
```

#### Serverless Templates

Example user prompt:

```
I need examples of well-architected serverless applications. Can you show me some API templates for Python that I can use as a reference for my project?
```

## Links

- [Homepage](https://awslabs.github.io/mcp/)
- [Documentation](https://awslabs.github.io/mcp/servers/aws-serverless-mcp-server/)
- [Source Code](https://github.com/awslabs/mcp.git)
- [Bug Tracker](https://github.com/awslabs/mcp/issues)
- [Changelog](https://github.com/awslabs/mcp/blob/main/src/aws-serverless-mcp-server/CHANGELOG.md)

## License

Apache-2.0
