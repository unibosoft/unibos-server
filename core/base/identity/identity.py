"""
UNIBOS Instance Identity Management

Each UNIBOS instance has a unique UUID and identity that persists across restarts.
Supports node type detection, capability declaration, and platform integration.
"""
import uuid
import json
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime


class NodeType(Enum):
    """Node type classification"""
    CENTRAL = "central"      # Central server (rocksteady)
    LOCAL = "local"          # Local development instance
    EDGE = "edge"            # Edge device (Raspberry Pi)
    DESKTOP = "desktop"      # Desktop/laptop instance
    UNKNOWN = "unknown"


@dataclass
class NodeCapabilities:
    """Node capability declaration"""
    # Platform capabilities
    has_gpu: bool = False
    has_camera: bool = False
    has_gpio: bool = False
    has_lora: bool = False

    # Service capabilities
    can_run_django: bool = True
    can_run_celery: bool = True
    can_run_websocket: bool = True

    # Module capabilities
    available_modules: List[str] = None

    # Storage capabilities
    storage_gb: int = 0
    ram_gb: int = 0

    def __post_init__(self):
        if self.available_modules is None:
            self.available_modules = []


@dataclass
class NodeIdentity:
    """Complete node identity information"""
    uuid: str
    node_type: NodeType
    hostname: str
    platform: str  # "macos", "linux", "raspberry-pi", "windows"
    capabilities: NodeCapabilities
    created_at: str
    last_seen: str

    # Optional registration info
    registered_to: Optional[str] = None  # Central server URL
    registration_token: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'uuid': self.uuid,
            'node_type': self.node_type.value,
            'hostname': self.hostname,
            'platform': self.platform,
            'capabilities': asdict(self.capabilities),
            'created_at': self.created_at,
            'last_seen': self.last_seen,
            'registered_to': self.registered_to,
            'registration_token': self.registration_token,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'NodeIdentity':
        """Create from dictionary"""
        caps_data = data.get('capabilities', {})
        capabilities = NodeCapabilities(
            has_gpu=caps_data.get('has_gpu', False),
            has_camera=caps_data.get('has_camera', False),
            has_gpio=caps_data.get('has_gpio', False),
            has_lora=caps_data.get('has_lora', False),
            can_run_django=caps_data.get('can_run_django', True),
            can_run_celery=caps_data.get('can_run_celery', True),
            can_run_websocket=caps_data.get('can_run_websocket', True),
            available_modules=caps_data.get('available_modules', []),
            storage_gb=caps_data.get('storage_gb', 0),
            ram_gb=caps_data.get('ram_gb', 0),
        )

        return cls(
            uuid=data['uuid'],
            node_type=NodeType(data['node_type']),
            hostname=data['hostname'],
            platform=data['platform'],
            capabilities=capabilities,
            created_at=data['created_at'],
            last_seen=data['last_seen'],
            registered_to=data.get('registered_to'),
            registration_token=data.get('registration_token'),
        )


class InstanceIdentity:
    """
    Unique identity for this UNIBOS instance

    Provides persistent UUID, node type detection, and capability management.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize instance identity

        Args:
            data_dir: Directory to store identity data (default: data/core/)
        """
        # Set data directory
        if data_dir is None:
            # Default: PROJECT_ROOT/data/core/
            project_root = Path(__file__).parent.parent.parent
            data_dir = project_root / 'data' / 'core'

        self.data_dir = Path(data_dir)
        self.identity_file = self.data_dir / 'node.json'

        # Ensure directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load or create identity
        self.identity = self._load_or_create_identity()

    def _load_or_create_identity(self) -> NodeIdentity:
        """Load existing identity or create new one"""
        if self.identity_file.exists():
            return self._load_identity()
        else:
            return self._create_identity()

    def _load_identity(self) -> NodeIdentity:
        """Load identity from file"""
        try:
            with open(self.identity_file, 'r') as f:
                data = json.load(f)

            identity = NodeIdentity.from_dict(data)

            # Update last_seen
            identity.last_seen = datetime.now().isoformat()
            self._save_identity(identity)

            return identity
        except Exception as e:
            print(f"Warning: Failed to load identity, creating new: {e}")
            return self._create_identity()

    def _create_identity(self) -> NodeIdentity:
        """Create new node identity"""
        import socket
        from core.platform import PlatformDetector

        # Detect platform
        detector = PlatformDetector()
        platform_info = detector.detect()

        # Generate UUID
        node_uuid = str(uuid.uuid4())

        # Determine node type
        node_type = self._detect_node_type(platform_info)

        # Build capabilities
        capabilities = NodeCapabilities(
            has_gpu=platform_info.has_gpu,
            has_camera=platform_info.has_camera,
            has_gpio=platform_info.has_gpio,
            has_lora=platform_info.has_lora,
            can_run_django=True,
            can_run_celery=platform_info.device_type in ['server', 'desktop'],
            can_run_websocket=True,
            available_modules=[],  # Will be populated later
            storage_gb=int(platform_info.disk_total_gb),
            ram_gb=int(platform_info.ram_total_gb),
        )

        # Create identity
        now = datetime.now().isoformat()
        identity = NodeIdentity(
            uuid=node_uuid,
            node_type=node_type,
            hostname=socket.gethostname(),
            platform=platform_info.os_type,
            capabilities=capabilities,
            created_at=now,
            last_seen=now,
        )

        # Save to file
        self._save_identity(identity)

        return identity

    def _detect_node_type(self, platform_info) -> NodeType:
        """
        Detect node type based on platform info

        Args:
            platform_info: PlatformInfo object

        Returns:
            NodeType enum
        """
        import socket

        hostname = socket.gethostname().lower()

        # Check for rocksteady (central server)
        if hostname == 'rocksteady':
            return NodeType.CENTRAL

        # Check for Raspberry Pi (edge device)
        if platform_info.is_raspberry_pi:
            return NodeType.EDGE

        # Check for desktop/laptop
        if platform_info.device_type == 'desktop':
            return NodeType.DESKTOP

        # Development machine
        if platform_info.device_type == 'server' and hostname != 'rocksteady':
            return NodeType.LOCAL

        return NodeType.UNKNOWN

    def _save_identity(self, identity: NodeIdentity):
        """Save identity to file"""
        try:
            with open(self.identity_file, 'w') as f:
                json.dump(identity.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save identity: {e}")

    def get_uuid(self) -> str:
        """Get node UUID"""
        return self.identity.uuid

    def get_node_type(self) -> NodeType:
        """Get node type"""
        return self.identity.node_type

    def get_capabilities(self) -> NodeCapabilities:
        """Get node capabilities"""
        return self.identity.capabilities

    def update_capabilities(self, **kwargs):
        """
        Update node capabilities

        Args:
            **kwargs: Capability fields to update
        """
        for key, value in kwargs.items():
            if hasattr(self.identity.capabilities, key):
                setattr(self.identity.capabilities, key, value)

        self.identity.last_seen = datetime.now().isoformat()
        self._save_identity(self.identity)

    def register_with_central(self, central_url: str, token: Optional[str] = None):
        """
        Register this node with a central server

        Args:
            central_url: Central server URL
            token: Optional registration token
        """
        self.identity.registered_to = central_url
        self.identity.registration_token = token
        self.identity.last_seen = datetime.now().isoformat()
        self._save_identity(self.identity)

    def get_identity(self) -> NodeIdentity:
        """Get complete node identity"""
        return self.identity

    def to_dict(self) -> Dict:
        """Get identity as dictionary"""
        return self.identity.to_dict()


# Singleton instance
_instance_identity: Optional[InstanceIdentity] = None


def get_instance_identity() -> InstanceIdentity:
    """Get singleton instance identity"""
    global _instance_identity

    if _instance_identity is None:
        _instance_identity = InstanceIdentity()

    return _instance_identity
