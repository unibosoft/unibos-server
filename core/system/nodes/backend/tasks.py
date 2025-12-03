"""
Celery Tasks for Node Registry

Handles periodic heartbeat monitoring and node status management.
"""

import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone
from django.conf import settings

from .models import Node, NodeStatus, NodeEvent

logger = logging.getLogger(__name__)

# Configuration
HEARTBEAT_TIMEOUT_MINUTES = getattr(settings, 'NODE_HEARTBEAT_TIMEOUT_MINUTES', 5)
STALE_THRESHOLD_MINUTES = getattr(settings, 'NODE_STALE_THRESHOLD_MINUTES', 15)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def check_node_heartbeats(self):
    """
    Check all nodes for stale heartbeats and mark them offline.

    Runs every minute via Celery Beat.
    Marks nodes as offline if no heartbeat received in HEARTBEAT_TIMEOUT_MINUTES.
    """
    try:
        timeout_threshold = timezone.now() - timedelta(minutes=HEARTBEAT_TIMEOUT_MINUTES)

        # Find nodes that should be marked offline
        stale_nodes = Node.objects.filter(
            is_active=True,
            status=NodeStatus.ONLINE,
            last_heartbeat__lt=timeout_threshold
        )

        marked_offline = 0
        for node in stale_nodes:
            node.status = NodeStatus.OFFLINE
            node.save(update_fields=['status'])

            # Log the event
            NodeEvent.objects.create(
                node=node,
                event_type='offline',
                message=f'Node {node.hostname} marked offline (no heartbeat for {HEARTBEAT_TIMEOUT_MINUTES}+ minutes)',
                extra_data={'last_heartbeat': str(node.last_heartbeat)}
            )

            logger.warning(f"Node {node.hostname} ({node.id}) marked offline - no heartbeat since {node.last_heartbeat}")
            marked_offline += 1

        # Also check for nodes that never sent a heartbeat
        never_heartbeat = Node.objects.filter(
            is_active=True,
            status=NodeStatus.ONLINE,
            last_heartbeat__isnull=True,
            registered_at__lt=timeout_threshold
        )

        for node in never_heartbeat:
            node.status = NodeStatus.OFFLINE
            node.save(update_fields=['status'])

            NodeEvent.objects.create(
                node=node,
                event_type='offline',
                message=f'Node {node.hostname} marked offline (never sent heartbeat)',
            )

            logger.warning(f"Node {node.hostname} ({node.id}) marked offline - never sent heartbeat")
            marked_offline += 1

        return {
            'status': 'success',
            'checked': Node.objects.filter(is_active=True).count(),
            'marked_offline': marked_offline
        }

    except Exception as e:
        logger.error(f"Error checking node heartbeats: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def cleanup_stale_metrics(self):
    """
    Clean up old node metrics to prevent database bloat.

    Runs daily via Celery Beat.
    Removes metrics older than 7 days by default.
    """
    from .models import NodeMetric

    try:
        retention_days = getattr(settings, 'NODE_METRICS_RETENTION_DAYS', 7)
        cutoff_date = timezone.now() - timedelta(days=retention_days)

        deleted_count, _ = NodeMetric.objects.filter(
            recorded_at__lt=cutoff_date
        ).delete()

        logger.info(f"Cleaned up {deleted_count} old node metrics (older than {retention_days} days)")

        return {
            'status': 'success',
            'deleted_metrics': deleted_count,
            'retention_days': retention_days
        }

    except Exception as e:
        logger.error(f"Error cleaning up stale metrics: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def cleanup_old_events(self):
    """
    Clean up old node events to prevent database bloat.

    Runs daily via Celery Beat.
    Removes events older than 30 days by default.
    """
    try:
        retention_days = getattr(settings, 'NODE_EVENTS_RETENTION_DAYS', 30)
        cutoff_date = timezone.now() - timedelta(days=retention_days)

        deleted_count, _ = NodeEvent.objects.filter(
            created_at__lt=cutoff_date
        ).delete()

        logger.info(f"Cleaned up {deleted_count} old node events (older than {retention_days} days)")

        return {
            'status': 'success',
            'deleted_events': deleted_count,
            'retention_days': retention_days
        }

    except Exception as e:
        logger.error(f"Error cleaning up old events: {e}")
        raise self.retry(exc=e)


@shared_task
def send_heartbeat_to_central():
    """
    Send heartbeat from this node to the central registry.

    Runs every minute via Celery Beat.
    Used when this node is not the central server.
    """
    import requests
    import psutil

    try:
        # Get central server URL from settings
        central_url = getattr(settings, 'CENTRAL_REGISTRY_URL', None)
        if not central_url:
            logger.debug("No central registry configured, skipping heartbeat")
            return {'status': 'skipped', 'reason': 'no_central_registry'}

        # Get this node's identity
        try:
            from core.base.identity import get_node_identity
            identity = get_node_identity()
            node_id = str(identity.node_id)
        except Exception as e:
            logger.warning(f"Could not get node identity: {e}")
            return {'status': 'error', 'reason': 'no_identity'}

        # Collect metrics
        metrics = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_used_mb': psutil.virtual_memory().used // (1024 * 1024),
            'disk_percent': psutil.disk_usage('/').percent,
            'disk_used_gb': psutil.disk_usage('/').used / (1024 ** 3),
        }

        # Send heartbeat
        response = requests.post(
            f"{central_url}/api/v1/nodes/{node_id}/heartbeat/",
            json=metrics,
            timeout=10
        )

        if response.status_code == 200:
            logger.debug(f"Heartbeat sent successfully to central registry")
            return {'status': 'success', 'response': response.json()}
        else:
            logger.warning(f"Heartbeat failed: {response.status_code} - {response.text}")
            return {'status': 'error', 'code': response.status_code}

    except requests.RequestException as e:
        logger.warning(f"Could not send heartbeat to central registry: {e}")
        return {'status': 'error', 'reason': str(e)}
    except Exception as e:
        logger.error(f"Unexpected error sending heartbeat: {e}")
        return {'status': 'error', 'reason': str(e)}


@shared_task
def register_with_central():
    """
    Register this node with the central registry.

    Called on startup and periodically to ensure registration.
    """
    import requests
    import psutil
    import platform
    import socket

    try:
        central_url = getattr(settings, 'CENTRAL_REGISTRY_URL', None)
        if not central_url:
            logger.debug("No central registry configured, skipping registration")
            return {'status': 'skipped', 'reason': 'no_central_registry'}

        # Get this node's identity
        try:
            from core.base.identity import get_node_identity
            identity = get_node_identity()
        except Exception as e:
            logger.warning(f"Could not get node identity: {e}")
            return {'status': 'error', 'reason': 'no_identity'}

        # Prepare registration data
        registration_data = {
            'id': str(identity.node_id),
            'hostname': socket.gethostname(),
            'node_type': identity.node_type.value if hasattr(identity.node_type, 'value') else str(identity.node_type),
            'platform': platform.system().lower(),
            'ip_address': socket.gethostbyname(socket.gethostname()),
            'port': getattr(settings, 'SERVER_PORT', 8000),
            'version': getattr(settings, 'VERSION', 'unknown'),
            'capabilities': {
                'has_gpu': identity.capabilities.has_gpu if hasattr(identity, 'capabilities') else False,
                'has_camera': identity.capabilities.has_camera if hasattr(identity, 'capabilities') else False,
                'can_run_django': True,
                'can_run_celery': True,
                'can_run_websocket': True,
                'storage_gb': psutil.disk_usage('/').total // (1024 ** 3),
                'ram_gb': psutil.virtual_memory().total // (1024 ** 3),
                'cpu_cores': psutil.cpu_count(),
            }
        }

        # Send registration
        response = requests.post(
            f"{central_url}/api/v1/nodes/register/",
            json=registration_data,
            timeout=30
        )

        if response.status_code in [200, 201]:
            logger.info(f"Successfully registered with central registry")
            return {'status': 'success', 'response': response.json()}
        else:
            logger.warning(f"Registration failed: {response.status_code} - {response.text}")
            return {'status': 'error', 'code': response.status_code}

    except requests.RequestException as e:
        logger.warning(f"Could not register with central registry: {e}")
        return {'status': 'error', 'reason': str(e)}
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        return {'status': 'error', 'reason': str(e)}
