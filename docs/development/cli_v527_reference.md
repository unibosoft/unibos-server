# UNIBOS v527 CLI Reference

## Overview
This document serves as a reference for the v527 interactive CLI system that we're porting to v1.0.0.

## Source Information
- **Version**: v527 (2025-11-02)
- **Commit**: e053e28
- **File**: `src/main.py` (8,125 lines)
- **Extracted**: `/tmp/unibos_main_v527.py`

## Architecture

### Entry Point
- **Shell Launcher**: `unibos.sh` (from v507 commit 399c600)
  - Starts Django backend in background
  - Opens browser to localhost:8000
  - Launches Python CLI: `python3 src/main.py`

### Core Components

#### 1. Colors Class (Lines 153-183)
ANSI color codes for terminal UI:
- Foreground: RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, ORANGE
- Background: BG_GRAY, BG_ORANGE, BG_DARK, BG_CONTENT
- Styles: BOLD, DIM, RESET

#### 2. MenuState Class (Lines 186-217)
State management for navigation:
- `current_section`: 0=modules, 1=tools, 2=dev_tools
- `selected_index`: Current selection
- `in_submenu`: Submenu context
- `preview_mode`: Show documentation previews
- Caching: `sidebar_cache`, `module_docs_cache`

#### 3. Terminal UI Functions
- `clear_screen()`: Enhanced screen clearing
- `get_terminal_size()`: Terminal dimensions
- `move_cursor(x, y)`: Position cursor
- `hide_cursor()` / `show_cursor()`: Cursor visibility
- `get_spinner_frame()`: Animation frames
- `wrap_text()`: Text wrapping

#### 4. Main Loop (Line 3005)
Event-driven navigation:
- Arrow keys (↑↓←→)
- Page navigation (PgUp/PgDn)
- Enter for selection
- ESC for back
- Number keys for quick selection

### UI Layout

#### Header
- Platform icon (🪐)
- Version info
- System status indicator
- Current time (Istanbul timezone)

#### Sidebar (Left)
Three sections with navigation:
1. **Modules Section**
   - Dynamic module discovery
   - Module icons and names
   - Active/inactive states

2. **Tools Section**
   - Database setup
   - Web forge
   - Version manager
   - Git operations

3. **Dev Tools Section**
   - Development utilities
   - Testing tools
   - Debug options

#### Content Area (Right)
- Context-specific content
- Documentation previews
- Form inputs
- Action results

#### Footer
- Navigation hints
- Keyboard shortcuts
- Status messages

### Key Features

#### 1. Module System
- Dynamic module discovery from filesystem
- Module metadata (name, icon, description)
- Enable/disable functionality
- Module-specific actions

#### 2. Multi-language Support
- Translation system (`translations.py`)
- Language detection
- Runtime language switching

#### 3. Git Integration
- Status display
- Quick commit/push/pull
- Branch management
- Interactive git operations

#### 4. Version Management
- Version info display
- Build tracking
- Release management

#### 5. Web Forge
- Project scaffolding
- Template generation
- Development workflows

#### 6. Database Tools
- Setup wizards
- Migration management
- Backup/restore

### Input Handling

#### Platform-specific
- **Unix/Linux/macOS**: termios + tty
- **Windows**: msvcrt

#### Key Mapping
- `\x1b[A`: UP arrow
- `\x1b[B`: DOWN arrow
- `\x1b[C`: RIGHT arrow
- `\x1b[D`: LEFT arrow
- `\x1b[5~`: Page Up
- `\x1b[6~`: Page Down
- `\r`: Enter
- `\x1b`: ESC
- `0-9`: Quick selection

### Dependencies
From v527 main.py imports:
- `emoji_safe_slice`: Emoji handling
- `sidebar_fix`: Sidebar rendering
- `translations`: I18n support
- `currencies_enhanced`: Currency module
- `network_utils`: Network security
- `ui_architecture`: UI framework
- `cli_context_manager`: Context management
- `version_manager`: Version tracking
- `git_manager`: Git operations
- `setup_manager`: Setup wizards
- `repair_manager`: System repair

### Visual Design Elements

#### Color Scheme
- Primary: Orange (#208) - UNIBOS branding
- Secondary: Cyan - Headers and highlights
- Success: Green
- Warning: Yellow
- Error: Red
- Muted: Gray/Dim

#### Typography
- Bold for headers
- Dim for hints and secondary info
- Color-coded by context

#### Layout Principles
- Left sidebar: 30-40 chars
- Right content: Remaining width
- Header: 3 lines
- Footer: 2 lines
- Content area: Calculated dynamically

## Migration Notes

### What to Keep
1. **Visual Design**: Entire UI/UX aesthetic
2. **Navigation System**: Arrow key + keyboard shortcuts
3. **State Management**: MenuState pattern
4. **Color Scheme**: All ANSI colors
5. **Layout Structure**: Sidebar + content area

### What to Adapt
1. **Module Discovery**: Use v1.0.0 module registry
2. **CLI Separation**: Split into unibos/unibos-dev/unibos-server
3. **Import Paths**: Adjust for new structure
4. **Backend Integration**: Connect to Django via core.web

### What to Add
1. **Hybrid Mode**: Click commands + interactive mode
2. **Modern Features**: From current development
3. **New Modules**: Support for v1.0.0 modules
4. **P2P Features**: When implemented

## Implementation Strategy

### Phase 1: Core UI Components
Extract and create reusable components:
- `core/cli/ui/colors.py`: Color definitions
- `core/cli/ui/terminal.py`: Terminal utilities
- `core/cli/ui/menu.py`: Menu state and navigation
- `core/cli/ui/layout.py`: Layout engine

### Phase 2: Interactive Base
Create shared interactive mode:
- `core/cli/interactive.py`: Base interactive class
- Hybrid mode detection
- Splash screen system
- Main loop architecture

### Phase 3: CLI-specific Implementation
For each CLI (unibos, unibos-dev, unibos-server):
- Define menu items for scope
- Implement action handlers
- Connect to appropriate modules

### Phase 4: Integration
- Module registry integration
- Django backend connection
- Service management hooks
- Testing and refinement

## Reference Files
- v527 main.py: `/tmp/unibos_main_v527.py`
- v507 unibos.sh: git show 399c600:unibos.sh
- Current structure: `/Users/berkhatirli/Desktop/unibos-dev/`

## Notes
- This is the most advanced version of the interactive CLI
- 8,125 lines of battle-tested code
- Used in production from v507-v527
- Proven UX with real users
- Don't reinvent - adapt and enhance
