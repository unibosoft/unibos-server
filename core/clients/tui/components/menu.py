"""
UNIBOS TUI Menu Components
Menu sections and items for TUI
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Callable

from core.clients.cli.framework.ui import MenuItem


@dataclass
class MenuSection:
    """
    Menu section containing items

    Attributes:
        id: Unique section identifier
        label: Display label for section
        icon: Optional icon/emoji for section
        items: List of menu items in this section
        metadata: Optional metadata dict
    """
    id: str
    label: str
    icon: str = ""
    items: List[MenuItem] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_item(self, item: MenuItem):
        """Add item to section"""
        self.items.append(item)

    def get_item(self, item_id: str) -> Optional[MenuItem]:
        """Get item by ID"""
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for compatibility"""
        return {
            'id': self.id,
            'label': self.label,
            'icon': self.icon,
            'items': self.items,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MenuSection':
        """Create from dict"""
        return cls(
            id=data.get('id', ''),
            label=data.get('label', ''),
            icon=data.get('icon', ''),
            items=data.get('items', []),
            metadata=data.get('metadata', {})
        )