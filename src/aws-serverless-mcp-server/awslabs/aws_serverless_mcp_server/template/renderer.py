"""
Template Renderer

Handles rendering of templates for CloudFormation/SAM deployments.
"""

from awslabs.aws_serverless_mcp_server.utils.logger import logger
import pybars
from .registry import DeploymentTypes, get_template_for_deployment
from awslabs.aws_serverless_mcp_server.models import DeployWebAppRequest

def get_helpers():
    """
    Get Handlebars helpers

    Returns:
        dict: Dictionary of helper functions
    """
    # Helper to check if two values are equal
    def if_equals(this, options, arg1, arg2):
        if arg1 == arg2:
            return options['fn'](this)
        else:
            return options['inverse'](this)

    # Helper to check if a value exists
    def if_exists(this, options, value):
        if value is not None and value != '':
            return options['fn'](this)
        else:
            return options['inverse'](this)

    # Helper to iterate over object properties
    def each_in_object(this, options, obj):
        result = ''
        if obj is not None:  # Check if obj is None before calling items()
            for key, value in obj.items():
                result += options['fn']({'key': key, 'value': value})
        return result

    # Helper for CloudFormation intrinsic functions
    def cf(this, options, fn_name, *args):
        if fn_name == 'Ref':
            return f'{{ "Ref": "{args[0]}" }}'
        elif fn_name == 'GetAtt':
            return f'{{ "Fn::GetAtt": ["{args[0]}", "{args[1]}"] }}'
        elif fn_name == 'Sub':
            return f'{{ "Fn::Sub": "{args[0]}" }}'
        else:
            return f'{{ "Fn::{fn_name}": {args} }}'

    # Return the helpers as a dictionary
    return {
        'ifEquals': if_equals,
        'ifExists': if_exists,
        'eachInObject': each_in_object,
        'cf': cf
    }


async def render_template(request: DeployWebAppRequest) -> str:
    """
    Render a template with the given parameters

    Args:
        params: Deployment parameters

    Returns:
        str: Rendered template as a string

    Raises:
        Exception: If template rendering fails
    """
    # Create a Handlebars compiler
    compiler = pybars.Compiler()

    # Get Handlebars helpers
    helpers = get_helpers()

    # Determine the deployment type
    deployment_type = DeploymentTypes(request.deployment_type.lower())

    # Get the appropriate framework
    framework = None
    if deployment_type == DeploymentTypes.BACKEND and request.backend_configuration.framework:
        framework = request.backend_configuration.framework
    elif deployment_type == DeploymentTypes.FRONTEND and request.frontend_configuration.framework:
        framework = request.frontend_configuration.framework
    elif deployment_type == DeploymentTypes.FULLSTACK:
        # For fullstack, we might use a combined framework name
        backend_framework = request.backend_configuration.framework
        frontend_framework = request.frontend_configuration.framework
        if backend_framework and frontend_framework:
            framework = f"{backend_framework}-{frontend_framework}"

    # Get the template for this deployment
    template = await get_template_for_deployment(deployment_type, framework)
    logger.debug(f"Using template: {template.name} at {template.path}")

    try:
        # Read the template file
        with open(template.path, 'r') as f:
            template_content = f.read()

        # Create a description for the template
        description = f"{request.project_name} - {deployment_type.value} deployment"

        # Compile the template
        compiled_template = compiler.compile(template_content)

        # Add description to params
        params_dict = request.dict() if hasattr(request, "dict") else vars(request)
        params_with_description = {**params_dict, 'description': description}
        logger.info(f"params: {params_with_description}")

        # Render the template with parameters and helpers
        rendered_template = compiled_template(params_with_description, helpers=helpers)

        logger.debug('Template rendered successfully')
        return rendered_template
    except Exception as error:
        logger.error(f"Error rendering template: {error}")
        raise Exception(f"Failed to render template: {str(error)}")
