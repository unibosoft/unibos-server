# UNIBOS TUI Framework Documentation

## Overview

The UNIBOS TUI (Terminal User Interface) framework provides a shared infrastructure for all three CLI profiles (dev, server, prod) with a consistent v527-style interface and modern enhancements.

## Architecture

### Directory Structure

```
core/clients/
├── cli/framework/        # Legacy framework (being phased out)
│   ├── ui/              # UI components (colors, terminal, input, etc.)
│   └── interactive.py   # Base interactive mode
├── tui/                 # New shared TUI framework
│   ├── base.py          # BaseTUI class for all profiles
│   └── components/      # Reusable UI components
│       ├── header.py    # Header component
│       ├── footer.py    # Footer component
│       ├── sidebar.py   # Multi-section sidebar
│       ├── content.py   # Content area
│       ├── statusbar.py # Status bar
│       ├── menu.py      # Menu structures
│       └── actions.py   # Action handlers

core/profiles/
├── dev/
│   ├── interactive.py   # Legacy interactive mode
│   └── tui.py          # Enhanced dev TUI
├── server/
│   ├── interactive.py   # Legacy interactive mode
│   └── tui.py          # Enhanced server TUI (TODO)
└── prod/
    ├── interactive.py   # Legacy interactive mode
    └── tui.py          # Enhanced prod TUI (TODO)
```

## Key Features

### 1. V527-Style Visual Design

- **Orange-themed UI**: Consistent with UNIBOS branding
- **Lowercase text**: All UI text is lowercase (v527 convention)
- **Single-line header**: Orange background with breadcrumbs
- **Multi-section sidebar**: Organized menu sections with icons
- **Rich content area**: Detailed descriptions and metadata
- **Informative footer**: Navigation hints and system status

### 2. Shared Infrastructure

All three profiles share:
- Common UI components (header, footer, sidebar, content)
- Consistent navigation patterns (arrow keys, tab, enter, esc)
- Unified color scheme and styling
- Base action handlers and utilities
- Terminal handling and input management

### 3. Profile-Specific Features

Each profile extends BaseTUI with unique:
- Menu sections and items
- Action handlers for profile-specific commands
- Custom configuration (location, title, etc.)
- Specialized functionality

## Implementation Guide

### Creating a New TUI

```python
from core.clients.tui import BaseTUI
from core.clients.tui.components import MenuSection
from core.clients.cli.framework.ui import MenuItem

class MyProfileTUI(BaseTUI):
    def get_profile_name(self) -> str:
        return "my-profile"

    def get_menu_sections(self) -> List[MenuSection]:
        return [
            MenuSection(
                id='section1',
                label='my section',
                icon='🔧',
                items=[
                    MenuItem(
                        id='action1',
                        label='my action',
                        icon='▶️',
                        description='Action description',
                        enabled=True
                    ),
                ]
            ),
        ]

    def __init__(self):
        config = TUIConfig(
            title="my-app",
            version="v1.0.0",
            location="my location"
        )
        super().__init__(config)
        self.register_action('action1', self.handle_action1)

    def handle_action1(self, item):
        # Implementation
        return True
```

### Registering Actions

```python
# In __init__ or register_handlers method
self.register_action('action_id', self.handle_action)

# Handler method
def handle_action(self, item):
    result = self.execute_command(['command', 'args'])
    self.show_command_output(result)
    return True  # Continue TUI loop
```

### Using Action Handlers

```python
from core.clients.tui.components.actions import (
    CommandActionHandler,
    DjangoActionHandler,
    GitActionHandler
)

# Simple command execution
self.register_action('git_status',
    CommandActionHandler(self, ['git', 'status']).handle)

# Django management command
self.register_action('migrate',
    DjangoActionHandler(self, 'migrate').handle)
```

## Navigation

### Keyboard Shortcuts

- **↑/↓**: Navigate items within section
- **←/→**: Navigate between sections
- **Tab**: Switch sections (cycle)
- **Enter**: Select/execute item
- **ESC**: Back/cancel
- **Q**: Quit application
- **0-9**: Quick select item by number

### Menu States

- **Normal**: Full sidebar visible, content shows selected item
- **Submenu**: Sidebar dimmed, focused on submenu
- **Action**: Executing command, showing output

## Configuration

### TUIConfig Options

```python
@dataclass
class TUIConfig:
    title: str = "unibos"              # Application title
    version: str = "v0.534.0"          # Version string
    location: str = "bitez, bodrum"    # Location for footer
    sidebar_width: int = 30            # Sidebar width in chars
    show_splash: bool = True           # Show splash screen
    quick_splash: bool = False         # Quick splash (no delay)
    enable_animations: bool = True     # Enable animations
    lowercase_ui: bool = True          # V527 lowercase style
    show_breadcrumbs: bool = True      # Show navigation breadcrumbs
    show_time: bool = True             # Show time in header
    show_hostname: bool = True         # Show hostname in footer
    show_status_led: bool = True       # Show online/offline LED
```

## Components

### Header Component

- Displays title, version, breadcrumbs
- Orange background (v527 style)
- Shows current time and username
- Window control decorations

### Footer Component

- Navigation hints (context-aware)
- System information (hostname, location)
- Current date and time
- Online/offline status with LED indicator

### Sidebar Component

- Multiple sections with headers
- Icon support for sections and items
- Selection highlighting (orange background)
- Number shortcuts (0-9) for quick selection
- Dimming for inactive sections

### Content Area

- Title and separator line
- Multi-line descriptions with wrapping
- Special formatting for patterns (✓, ✗, →, etc.)
- Metadata display support
- Scroll indicators for long content

## Error Handling

### Terminal Compatibility

The framework handles various terminal environments:
- TTY detection for proper terminal support
- Fallback for non-terminal environments
- Error handling for termios operations
- Cross-platform support (Unix/Linux/macOS/Windows)

### Common Issues and Solutions

1. **"Operation not supported by device"**
   - Fixed with improved terminal detection
   - Fallback to simple input when needed

2. **Import errors**
   - Ensure PYTHONPATH includes project root
   - Check module structure and __init__ files

3. **Command failures**
   - All commands wrapped in try/except
   - Clear error messages shown to user
   - Non-fatal errors allow TUI to continue

## Testing

### Manual Testing

```bash
# Test TUI directly
unibos-dev  # No arguments launches TUI

# Test with debug mode
UNIBOS_DEBUG=true unibos-dev

# Test specific commands
unibos-dev status
unibos-dev dev run
```

### Unit Testing

```python
# Test menu structure
def test_menu_sections():
    tui = UnibosDevTUI()
    sections = tui.get_menu_sections()
    assert len(sections) == 4
    assert sections[0].id == 'dev'

# Test action handlers
def test_git_status_handler():
    tui = UnibosDevTUI()
    item = MenuItem(id='git_status', label='git status')
    result = tui.handle_git_status(item)
    assert result == True
```

## Migration from Legacy

### For Existing Interactive Modes

1. Keep existing interactive.py for backward compatibility
2. Create new tui.py with enhanced implementation
3. Update interactive.py to try enhanced TUI first:

```python
def run_interactive():
    try:
        from .tui import run_interactive as run_enhanced_tui
        run_enhanced_tui()
    except ImportError:
        # Fallback to legacy
        interactive = ProfileInteractive()
        interactive.run()
```

## Future Enhancements

### Planned Features

1. **Async Operations**: Background tasks with progress indication
2. **Themes**: User-selectable color schemes
3. **Plugins**: Dynamic menu item registration
4. **Notifications**: System tray integration
5. **Mouse Support**: Click navigation in terminals that support it
6. **Rich Media**: Images and charts in content area
7. **Search**: Fuzzy finder for menu items
8. **History**: Command history and replay

### P2P Integration

When P2P features are implemented:
- Node discovery in sidebar
- Peer status in footer
- P2P operations in menu
- Real-time sync indicators

## Best Practices

1. **Keep handlers simple**: Complex logic in separate functions
2. **Show feedback**: Always indicate what's happening
3. **Handle errors gracefully**: Don't crash the TUI
4. **Be consistent**: Follow v527 visual conventions
5. **Document actions**: Clear descriptions for each menu item
6. **Test thoroughly**: Each action should be tested
7. **Cache expensive operations**: Use TUI cache for slow operations

## Contributing

When adding new TUI features:

1. Extend shared components when possible
2. Follow v527 design language
3. Ensure cross-profile compatibility
4. Add comprehensive error handling
5. Update this documentation
6. Test on multiple terminals

## References

- Original v527 implementation: `docs/development/cli_v527_reference.md`
- UI components: `core/clients/cli/framework/ui/`
- Color scheme: Based on v527 ANSI codes
- Design philosophy: Simple, consistent, informative