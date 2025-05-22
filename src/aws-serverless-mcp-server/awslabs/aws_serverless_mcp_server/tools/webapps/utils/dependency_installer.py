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

"""Dependency Installer for AWS Serverless MCP Server.

Handles installation of dependencies in the build artifacts directory
based on the runtime environment.
"""

import os
import shutil
import subprocess
from awslabs.aws_serverless_mcp_server.utils.logger import logger

async def install_dependencies(
    project_root: str,
    built_artifacts_path: str,
    runtime: str
) -> None:
    """
    Install dependencies in the build artifacts directory based on runtime.
    
    Args:
        project_root: Root directory of the project
        built_artifacts_path: Path to the built artifacts
        runtime: Lambda runtime (e.g., nodejs18.x, python3.9)
    
    Raises:
        Exception: If dependency installation fails
    """
    logger.info(f"Installing dependencies for runtime: {runtime} in {built_artifacts_path}")
    
    try:
        if runtime.startswith('nodejs'):
            await install_node_dependencies(project_root, built_artifacts_path)
        elif runtime.startswith('python'):
            await install_python_dependencies(project_root, built_artifacts_path)
        elif runtime.startswith('java'):
            # Java dependencies are typically bundled in the JAR/WAR file
            logger.info('Java dependencies are expected to be bundled in the artifact')
        elif runtime.startswith('dotnet'):
            # .NET dependencies are typically bundled in the published output
            logger.info('.NET dependencies are expected to be bundled in the artifact')
        elif runtime.startswith('go'):
            # Go dependencies are typically compiled into the binary
            logger.info('Go dependencies are expected to be compiled into the binary')
        elif runtime.startswith('ruby'):
            await install_ruby_dependencies(project_root, built_artifacts_path)
        else:
            logger.warning(f"Unsupported runtime: {runtime}, dependencies may need to be installed manually")
    except Exception as e:
        logger.error(f"Error installing dependencies: {str(e)}")
        raise Exception(f"Failed to install dependencies: {str(e)}")

async def install_node_dependencies(
    project_root: str,
    built_artifacts_path: str
) -> None:
    """
    Install Node.js dependencies.
    
    Args:
        project_root: Root directory of the project
        built_artifacts_path: Path to the built artifacts
    """
    # Check if package.json exists in the built artifacts path
    target_package_json_path = os.path.join(built_artifacts_path, 'package.json')
    source_package_json_path = os.path.join(project_root, 'package.json')
    
    if not os.path.exists(target_package_json_path):
        # If package.json doesn't exist in the built artifacts, check if it exists in the project root
        if os.path.exists(source_package_json_path):
            logger.info(f"Copying package.json from {source_package_json_path} to {target_package_json_path}")
            shutil.copyfile(source_package_json_path, target_package_json_path)
        else:
            logger.warning('No package.json found, skipping Node.js dependency installation')
            return
    
    # Check if package-lock.json exists and copy it if available
    source_package_lock_path = os.path.join(project_root, 'package-lock.json')
    target_package_lock_path = os.path.join(built_artifacts_path, 'package-lock.json')
    
    if os.path.exists(source_package_lock_path) and not os.path.exists(target_package_lock_path):
        logger.info('Copying package-lock.json for faster installation')
        shutil.copyfile(source_package_lock_path, target_package_lock_path)
    
    # Install production dependencies
    logger.info('Installing Node.js production dependencies')
    try:
        # Use shell=True to support complex commands with pipes and redirects
        result = subprocess.run(
            'npm install --production',
            shell=True,
            cwd=built_artifacts_path,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"npm install completed: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"npm install failed: {e.stderr}")
        raise Exception(f"Failed to install Node.js dependencies: {e.stderr}")

async def install_python_dependencies(
    project_root: str,
    built_artifacts_path: str
) -> None:
    """
    Install Python dependencies.
    
    Args:
        project_root: Root directory of the project
        built_artifacts_path: Path to the built artifacts
    """
    # Check if requirements.txt exists in the built artifacts path
    target_requirements_path = os.path.join(built_artifacts_path, 'requirements.txt')
    source_requirements_path = os.path.join(project_root, 'requirements.txt')
    
    if not os.path.exists(target_requirements_path):
        # If requirements.txt doesn't exist in the built artifacts, check if it exists in the project root
        if os.path.exists(source_requirements_path):
            logger.info(f"Copying requirements.txt from {source_requirements_path} to {target_requirements_path}")
            shutil.copyfile(source_requirements_path, target_requirements_path)
        else:
            logger.warning('No requirements.txt found, skipping Python dependency installation')
            return
    
    # Install Python dependencies to the current directory
    logger.info('Installing Python dependencies')
    try:
        # Use shell=True to support complex commands with pipes and redirects
        result = subprocess.run(
            'pip install -r requirements.txt -t .',
            shell=True,
            cwd=built_artifacts_path,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"pip install completed: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"pip install failed: {e.stderr}")
        raise Exception(f"Failed to install Python dependencies: {e.stderr}")

async def install_ruby_dependencies(
    project_root: str,
    built_artifacts_path: str
) -> None:
    """
    Install Ruby dependencies.
    
    Args:
        project_root: Root directory of the project
        built_artifacts_path: Path to the built artifacts
    """
    # Check if Gemfile exists in the built artifacts path
    target_gemfile_path = os.path.join(built_artifacts_path, 'Gemfile')
    source_gemfile_path = os.path.join(project_root, 'Gemfile')
    
    if not os.path.exists(target_gemfile_path):
        # If Gemfile doesn't exist in the built artifacts, check if it exists in the project root
        if os.path.exists(source_gemfile_path):
            logger.info(f"Copying Gemfile from {source_gemfile_path} to {target_gemfile_path}")
            shutil.copyfile(source_gemfile_path, target_gemfile_path)
            
            # Copy Gemfile.lock if it exists
            source_gemfile_lock_path = os.path.join(project_root, 'Gemfile.lock')
            target_gemfile_lock_path = os.path.join(built_artifacts_path, 'Gemfile.lock')
            
            if os.path.exists(source_gemfile_lock_path):
                shutil.copyfile(source_gemfile_lock_path, target_gemfile_lock_path)
        else:
            logger.warning('No Gemfile found, skipping Ruby dependency installation')
            return
    
    # Install Ruby dependencies to vendor/bundle
    logger.info('Installing Ruby dependencies')
    try:
        # Configure bundle to install to vendor/bundle
        result1 = subprocess.run(
            'bundle config set --local path vendor/bundle',
            shell=True,
            cwd=built_artifacts_path,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"bundle config completed: {result1.stdout}")
        
        # Install dependencies
        result2 = subprocess.run(
            'bundle install',
            shell=True,
            cwd=built_artifacts_path,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"bundle install completed: {result2.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"bundle install failed: {e.stderr}")
        raise Exception(f"Failed to install Ruby dependencies: {e.stderr}")
