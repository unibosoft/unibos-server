"""
Birlikteyiz Django App Configuration
Emergency mesh network and earthquake monitoring

UNIBOS Module Integration

Background Services:
- Earthquake data fetch scheduler (every 5 minutes)
- EMSC WebSocket real-time listener
"""

from django.apps import AppConfig
from pathlib import Path
import sys
import os
import threading
import time
import logging
import asyncio

logger = logging.getLogger(__name__)

# Global flags to prevent multiple instances
_scheduler_started = False
_emsc_started = False
_scheduler_lock = threading.Lock()
_emsc_lock = threading.Lock()


class BirlikteyizConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.birlikteyiz.backend'
    label = 'birlikteyiz'
    verbose_name = 'Birlikteyiz - Emergency Network'

    def ready(self):
        """
        Initialize UNIBOS module and register signals
        """
        # Add shared SDK to Python path
        self._add_sdk_to_path()

        # Initialize UNIBOS module
        self._initialize_module()

        # Import and register signals
        from . import signals  # noqa

        # Start earthquake data fetch scheduler
        # Only start in main process (not in manage.py commands like migrate)
        self._start_earthquake_scheduler()

        # Start EMSC WebSocket listener for real-time data
        self._start_emsc_listener()

    def _add_sdk_to_path(self):
        """Add UNIBOS SDK to Python path if not already there"""
        try:
            # Get project root (from modules/birlikteyiz/backend -> go up 3 levels)
            module_dir = Path(__file__).resolve().parent.parent.parent.parent
            sdk_path = module_dir / 'platform' / 'sdk' / 'python'

            if sdk_path.exists() and str(sdk_path) not in sys.path:
                sys.path.insert(0, str(sdk_path))
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not add SDK to path: {e}")

    def _initialize_module(self):
        """Initialize UNIBOS module wrapper"""
        try:
            from unibos_sdk import UnibosModule

            # Initialize module
            self.unibos_module = UnibosModule('birlikteyiz')

            # Log initialization
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"✓ Initialized UNIBOS module: birlikteyiz v{self.unibos_module.manifest.get('version')}")

            # Ensure storage paths exist
            self.unibos_module.get_storage_path('uploads/')
            self.unibos_module.get_cache_path()
            self.unibos_module.get_logs_path()

        except ImportError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"UNIBOS SDK not available, running in legacy mode: {e}")

    def _start_earthquake_scheduler(self):
        """
        Start background scheduler for earthquake data fetching.

        This runs every 5 minutes to fetch earthquake data from all configured sources.
        Uses a daemon thread so it doesn't block server shutdown.

        Only starts when:
        - Running as a web server (RUN_MAIN is set by runserver/uvicorn reloader)
        - Not already started (singleton pattern)
        """
        global _scheduler_started

        # Check if we should start the scheduler
        # RUN_MAIN is set by Django's autoreload, we only want to run in the main process
        # For uvicorn/gunicorn, we check if this is the main thread
        is_main_process = os.environ.get('RUN_MAIN') == 'true' or \
                          'uvicorn' in sys.argv[0] or \
                          'gunicorn' in sys.argv[0]

        # Skip for management commands like migrate, makemigrations, shell, etc.
        is_management_command = any(cmd in sys.argv for cmd in [
            'migrate', 'makemigrations', 'shell', 'dbshell', 'collectstatic',
            'createsuperuser', 'check', 'test', 'flush', 'loaddata', 'dumpdata'
        ])

        if is_management_command:
            return

        with _scheduler_lock:
            if _scheduler_started:
                return
            _scheduler_started = True

        # Start the scheduler thread
        scheduler_thread = threading.Thread(
            target=self._earthquake_fetch_loop,
            name='birlikteyiz-earthquake-scheduler',
            daemon=True  # Daemon thread - will be killed when main process exits
        )
        scheduler_thread.start()
        logger.info("🌍 Birlikteyiz earthquake data scheduler started (every 5 minutes)")

    def _earthquake_fetch_loop(self):
        """
        Background loop that fetches earthquake data every 5 minutes.

        Runs indefinitely until the server is stopped.
        Handles errors gracefully to prevent the loop from crashing.
        """
        from django.core.management import call_command
        from django.utils import timezone

        # Wait 30 seconds before first fetch (let server fully start)
        time.sleep(30)

        # Initial fetch
        logger.info("🌍 Running initial earthquake data fetch...")
        try:
            call_command('fetch_earthquakes')
            logger.info("✅ Initial earthquake data fetch completed")
        except Exception as e:
            logger.error(f"❌ Initial earthquake fetch failed: {e}")

        # Fetch every 5 minutes (300 seconds)
        fetch_interval = 300

        while True:
            try:
                time.sleep(fetch_interval)

                logger.info(f"🌍 Scheduled earthquake data fetch at {timezone.now()}")
                call_command('fetch_earthquakes')
                logger.info("✅ Scheduled earthquake data fetch completed")

            except Exception as e:
                logger.error(f"❌ Scheduled earthquake fetch failed: {e}")
                # Continue loop even if fetch fails

    def _start_emsc_listener(self):
        """
        Start EMSC WebSocket listener for real-time earthquake data.

        EMSC (European-Mediterranean Seismological Centre) provides real-time
        earthquake data via WebSocket. This runs in a separate thread with its
        own asyncio event loop.

        Only starts when:
        - Running as a web server
        - Not already started (singleton pattern)
        """
        global _emsc_started

        # Skip for management commands
        is_management_command = any(cmd in sys.argv for cmd in [
            'migrate', 'makemigrations', 'shell', 'dbshell', 'collectstatic',
            'createsuperuser', 'check', 'test', 'flush', 'loaddata', 'dumpdata',
            'emsc_listener', 'fetch_earthquakes'  # Skip if running these commands directly
        ])

        if is_management_command:
            return

        with _emsc_lock:
            if _emsc_started:
                return
            _emsc_started = True

        # Start the EMSC listener in a separate thread
        emsc_thread = threading.Thread(
            target=self._emsc_listener_thread,
            name='birlikteyiz-emsc-websocket',
            daemon=True
        )
        emsc_thread.start()
        logger.info("🌐 EMSC WebSocket listener thread started")

    def _emsc_listener_thread(self):
        """
        Thread function that runs the EMSC WebSocket listener.

        Creates a new asyncio event loop for this thread and runs the
        WebSocket client in it.
        """
        # Wait for server to fully start
        time.sleep(45)

        logger.info("🌐 Starting EMSC WebSocket connection...")

        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            from .services.emsc_websocket_client import EMSCWebSocketClient

            client = EMSCWebSocketClient()

            # Run the client
            loop.run_until_complete(client.start())

        except Exception as e:
            logger.error(f"❌ EMSC WebSocket listener error: {e}")
        finally:
            loop.close()
