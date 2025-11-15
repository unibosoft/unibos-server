"""
UNIBOS Deployment Management
Deployment tools for server and node installations
"""

from pathlib import Path

__all__ = ['get_deployment_type', 'DeploymentType']


class DeploymentType:
    """Deployment type constants"""
    DEV = 'dev'
    SERVER = 'server'
    NODE = 'node'


def get_deployment_type() -> str:
    """
    Detect current deployment type from environment

    Returns:
        str: One of 'dev', 'server', 'node'
    """
    import os

    # Check environment variable first
    if 'UNIBOS_DEPLOYMENT' in os.environ:
        return os.environ['UNIBOS_DEPLOYMENT']

    # Check settings module
    django_settings = os.environ.get('DJANGO_SETTINGS_MODULE', '')
    if 'server' in django_settings:
        return DeploymentType.SERVER
    elif 'node' in django_settings:
        return DeploymentType.NODE
    elif 'development' in django_settings or 'dev' in django_settings:
        return DeploymentType.DEV

    # Default to dev
    return DeploymentType.DEV
