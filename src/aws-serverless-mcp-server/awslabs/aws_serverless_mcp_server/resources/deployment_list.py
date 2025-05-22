import json
from typing import Dict, Any
from awslabs.aws_serverless_mcp_server.utils.logger import logger
from awslabs.aws_serverless_mcp_server.utils.deployment_manager import list_stack_details

async def handle_deployments_list() -> Dict[str, Any]:
    """
    List all deployments with CloudFormation stack details and format for MCP response.
    """
    try:
        logger.info('Deployment list resource called')
        detailed_deployments = await list_stack_details()

        if not detailed_deployments:
            return {
                "contents": [],
                "metadata": {
                    "count": 0,
                    "message": "No deployments found"
                }
            }

        formatted_deployments = [
            {
                "uri": f"deployment://{deployment.get('projectName')}",
                "text": json.dumps({
                    "projectName": deployment.get('projectName'),
                    "type": deployment.get('deploymentType', 'unknown'),
                    "status": deployment.get('status', 'unknown'),
                    "lastUpdated": deployment.get('lastUpdated', '')
                })
            }
            for deployment in detailed_deployments
        ]

        return {
            "contents": formatted_deployments,
            "metadata": {
                "count": len(formatted_deployments)
            }
        }
    except Exception as error:
        logger.error(f'Error listing deployments: {error}')
        return {
            "contents": [],
            "metadata": {
                "count": 0,
                "error": f"Failed to list deployments: {str(error)}"
            }
        }
