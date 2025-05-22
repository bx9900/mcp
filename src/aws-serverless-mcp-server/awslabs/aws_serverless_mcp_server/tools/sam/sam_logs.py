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

"""SAM logs tool for AWS Serverless MCP Server."""

import subprocess
from typing import Dict, Any
from awslabs.aws_serverless_mcp_server.utils.process import run_command
from awslabs.aws_serverless_mcp_server.models import SamLogsRequest
from awslabs.aws_serverless_mcp_server.utils.logger import logger

async def sam_logs(request: SamLogsRequest) -> Dict[str, Any]:
    """
    Fetch logs for AWS Lambda functions deployed through AWS SAM.
    
    Args:
        request: SamLogsRequest object containing log retrieval parameters
    
    Returns:
        Dict: Log retrieval result
    """
    try:
        function_name = request.function_name
        stack_name = request.stack_name
        tail = request.tail
        filter_pattern = request.filter
        start_time = request.start_time
        end_time = request.end_time
        output = request.output
        region = request.region
        profile = request.profile
        include_triggered_logs = request.include_triggered_logs
        cw = request.cw
        resources_dir = request.resources_dir
        template_file = request.template_file
        
        # Build the command arguments
        cmd = ['sam', 'logs']
        cmd.extend(['--name', function_name])
        
        if stack_name:
            cmd.extend(['--stack-name', stack_name])
        
        if tail:
            cmd.append('--tail')
        
        if filter_pattern:
            cmd.extend(['--filter', filter_pattern])
        
        if start_time:
            cmd.extend(['--start-time', start_time])
        
        if end_time:
            cmd.extend(['--end-time', end_time])
        
        if output:
            cmd.extend(['--output', output])
        
        if region:
            cmd.extend(['--region', region])
        
        if profile:
            cmd.extend(['--profile', profile])
        
        if include_triggered_logs:
            cmd.append('--include-triggered-logs')
        
        if cw:
            cmd.append('--cw')
        
        if resources_dir:
            cmd.extend(['--resources-dir', resources_dir])
        
        if template_file:
            cmd.extend(['--template-file', template_file])
        
        # Execute the command
        logger.info(f"Executing command: {' '.join(cmd)}")
        stdout, stderr = await run_command(cmd, cwd=request.project_directory)
        return {
            "success": True,
            'message': f"Successfully fetched logs for Lambda function '{function_name}'",
            "output": stdout.decode()
        } 
    except Exception as e:
        error_message = getattr(e, 'stderr', str(e))
        logger.error(f"Error fetching logs for Lambda function: {error_message}")
        return {
            'success': False,
            'message': f"Failed to fetch logs for Lambda function: {error_message}",
            'error': str(e)
        }
