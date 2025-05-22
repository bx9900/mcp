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

"""Get logs tool for AWS Serverless MCP Server."""

import os
import boto3
import json
import datetime
from typing import Dict, Any
from awslabs.aws_serverless_mcp_server.models import GetLogsRequest
from awslabs.aws_serverless_mcp_server.utils.logger import logger

async def get_logs(request: GetLogsRequest) -> Dict[str, Any]:
    """
    Get logs from a deployed web application.
    
    Args:
        request: GetLogsRequest object containing log retrieval parameters
    
    Returns:
        Dict: Log retrieval result
    """
    try:
        project_name = request.project_name
        region = request.region or os.environ.get('AWS_REGION', 'us-east-1')
        
        logger.info(f"Getting logs for project {project_name}")
        
        # Initialize AWS clients
        session = boto3.Session(region_name=region) if region else boto3.Session
        logs_client = session.client('logs')
        
        # Determine the log group name
        log_group_name = request.log_group_name
        
        # If no specific log group name is provided, construct one based on project name
        if not log_group_name:
            # Default log group pattern for web applications
            log_group_name = f"/aws/lambda/{project_name}"
            logger.info(f"No log group name provided, using default: {log_group_name}")
        
        # Prepare parameters for filtering log events
        filter_params = {
            'logGroupName': log_group_name,
            'limit': request.limit or 100
        }
        
        # Add optional parameters if provided
        if request.filter_pattern:
            filter_params['filterPattern'] = request.filter_pattern
        
        if request.start_time:
            try:
                start_time = datetime.datetime.fromisoformat(request.start_time.replace('Z', '+00:00'))
                filter_params['startTime'] = int(start_time.timestamp() * 1000)
            except ValueError:
                logger.warning(f"Invalid start_time format: {request.start_time}")
        
        if request.end_time:
            try:
                end_time = datetime.datetime.fromisoformat(request.end_time.replace('Z', '+00:00'))
                filter_params['endTime'] = int(end_time.timestamp() * 1000)
            except ValueError:
                logger.warning(f"Invalid end_time format: {request.end_time}")
        
        logger.debug(f"Retrieving logs with filter_params: {json.dumps(filter_params)}")
        
        # Execute the FilterLogEvents command
        logs_response = logs_client.filter_log_events(**filter_params)
        
        # Transform the log events into a more user-friendly format
        logs = []
        for event in logs_response.get('events', []):
            # Try to parse the message as JSON if possible
            level = "INFO"
            message = event.get('message', '')
            
            try:
                parsed_message = json.loads(message)
                # Extract log level if available in the parsed message
                if isinstance(parsed_message, dict) and 'level' in parsed_message:
                    level = parsed_message['level']
            except json.JSONDecodeError:
                # If not JSON, use the raw message
                # Try to infer log level from the message content
                lower_message = message.lower()
                if 'error' in lower_message:
                    level = "ERROR"
                elif 'warn' in lower_message:
                    level = "WARN"
                elif 'debug' in lower_message:
                    level = "DEBUG"
            
            logs.append({
                'timestamp': datetime.datetime.fromtimestamp(
                    event.get('timestamp', 0) / 1000, 
                    datetime.timezone.utc
                ).isoformat(),
                'message': message,
                'level': level,
                'eventId': event.get('eventId', '')
            })
        
        return {
            'success': True,
            'logGroupName': log_group_name,
            'logs': logs,
            'nextToken': logs_response.get('nextToken')
        }
    except Exception as e:
        logger.error(f"Error in get_logs: {str(e)}")
        return {
            'success': False,
            'message': f"Failed to retrieve logs: {str(e)}",
            'error': str(e)
        }
