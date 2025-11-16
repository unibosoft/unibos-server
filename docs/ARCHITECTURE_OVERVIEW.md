# UNIBOS 4-Tier Architecture Overview

Visual overview of the complete UNIBOS CLI/TUI architecture.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        UNIBOS ECOSYSTEM                             │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   unibos-dev    │  │ unibos-manager  │  │ unibos-server   │  │     unibos      │
│  (Developer)    │  │   (Manager)     │  │    (Server)     │  │    (Client)     │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │                    │
         ├─ Development       ├─ Remote Mgmt       ├─ Production        ├─ End User
         ├─ Local Mac/Linux   ├─ Any Machine       ├─ rocksteady.fun    ├─ Raspberry Pi
         └─ Module Dev        └─ Control Panel     └─ Ubuntu Server     └─ User Devices

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              COMMON BASE (BaseTUI)                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│  • 3-Section Layout (Header, Sidebar, Content, Footer)                         │
│  • Keyboard Navigation (↑↓←→ Enter ESC Q)                                       │
│  • MenuSection / MenuItem Structure                                             │
│  • Action Handler Registry                                                      │
│  • ANSI Color Support (256 colors)                                              │
│  • Double Buffering (flicker-free)                                              │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Profile Comparison

| Feature | unibos-dev | unibos-manager | unibos-server | unibos |
|---------|------------|----------------|---------------|--------|
| **User** | Developer | Administrator | Server Admin | End User |
| **Location** | Dev Machine | Any Machine | rocksteady.fun | User Device |
| **Purpose** | Development | Remote Control | Server Ops | App Launcher |
| **Sections** | Modules, Tools, Dev Tools | Targets, Ops, Monitor | Services, Ops, Monitor | Modules, System, Info |
| **CLI Commands** | 20+ | Future | 6 | 5 |
| **Primary Use** | Build & Deploy | Manage Remote | Maintain Server | Use Apps |

## TUI Structure Comparison

### unibos-dev
```
┌─────────────────────────────────────┐
│ Header: unibos-dev v0.534.0         │
├───────────────┬─────────────────────┤
│ 📦 modules    │ → Content Area      │
│   • recaria   │                     │
│   • movies    │   Selected item     │
│   • music     │   details and       │
│   • ...       │   actions           │
│               │                     │
│ 🔧 tools      │                     │
│   • scrolls   │                     │
│   • guard     │                     │
│   • ...       │                     │
│               │                     │
│ 🛠️ dev tools  │                     │
│   • ai        │                     │
│   • database  │                     │
│   • ...       │                     │
├───────────────┴─────────────────────┤
│ Footer: ↑↓ Move | Enter | ESC | Q  │
└─────────────────────────────────────┘
```

### unibos-manager
```
┌─────────────────────────────────────┐
│ Header: unibos-manager v0.534.0     │
├───────────────┬─────────────────────┤
│ 🎯 targets    │ → Content Area      │
│   • rocksteady│                     │
│   • local dev │   Target info       │
│   • list      │   and operations    │
│               │                     │
│ ⚙️ operations │                     │
│   • deploy    │                     │
│   • restart   │                     │
│   • ...       │                     │
│               │                     │
│ 📊 monitoring │                     │
│   • status    │                     │
│   • health    │                     │
│   • ...       │                     │
├───────────────┴─────────────────────┤
│ Footer: Current: rocksteady         │
└─────────────────────────────────────┘
```

### unibos-server
```
┌─────────────────────────────────────┐
│ Header: unibos-server v0.534.0      │
├───────────────┬─────────────────────┤
│ ⚙️ services   │ → Content Area      │
│   • django    │                     │
│   • postgres  │   Service status    │
│   • nginx     │   and controls      │
│   • workers   │                     │
│               │                     │
│ 🛠️ operations │                     │
│   • logs      │                     │
│   • restart   │                     │
│   • backup    │                     │
│   • ...       │                     │
│               │                     │
│ 📊 monitoring │                     │
│   • system    │                     │
│   • health    │                     │
│   • ...       │                     │
├───────────────┴─────────────────────┤
│ Footer: rocksteady.fun              │
└─────────────────────────────────────┘
```

### unibos (client)
```
┌─────────────────────────────────────┐
│ Header: unibos v0.534.0             │
├───────────────┬─────────────────────┤
│ 📦 modules    │ → Content Area      │
│   • recaria   │                     │
│   • movies    │   App launcher      │
│   • music     │   and info          │
│   • ...       │                     │
│               │                     │
│ ⚙️ system     │                     │
│   • settings  │                     │
│   • network   │                     │
│   • update    │                     │
│   • ...       │                     │
│               │                     │
│ ℹ️ info       │                     │
│   • status    │                     │
│   • help      │                     │
│   • about     │                     │
├───────────────┴─────────────────────┤
│ Footer: Local Node                  │
└─────────────────────────────────────┘
```

## Data Flow

```
Developer Workflow:
┌──────────────┐   develop    ┌──────────────┐   deploy    ┌──────────────┐
│  unibos-dev  │────────────→ │ Local Django │────────────→│unibos-server │
│              │   (modules)  │              │  (git push) │ (rocksteady) │
└──────────────┘              └──────────────┘             └──────────────┘
       ↑                                                            ↓
       │                                                            │
       └────────────────────── monitor via ────────────────────────┘
                            unibos-manager


End User Workflow:
┌──────────────┐   access     ┌──────────────┐   sync      ┌──────────────┐
│    unibos    │────────────→ │ Local Modules│────────────→│unibos-server │
│   (client)   │   (launch)   │  (P2P mesh)  │ (optional)  │ (rocksteady) │
└──────────────┘              └──────────────┘             └──────────────┘
```

## Component Hierarchy

```
pyproject.toml
└── [project.scripts]
    ├── unibos = "core.profiles.prod.main:main"
    ├── unibos-dev = "core.profiles.dev.main:main"
    ├── unibos-server = "core.profiles.server.main:main"
    └── unibos-manager = "core.profiles.manager.main:main"

core/profiles/
├── dev/
│   ├── main.py          # CLI entry (hybrid mode)
│   ├── tui.py           # UnibosDevTUI (BaseTUI)
│   ├── commands/        # CLI command implementations
│   └── ui/              # Splash screens
│
├── manager/
│   ├── main.py          # CLI entry (hybrid mode)
│   └── tui.py           # ManagerTUI (BaseTUI)
│
├── server/
│   ├── main.py          # CLI entry (hybrid mode)
│   ├── tui.py           # ServerTUI (BaseTUI)
│   └── commands/        # Future: CLI commands
│
└── prod/
    ├── main.py          # CLI entry (hybrid mode)
    └── tui.py           # ClientTUI (BaseTUI)

core/clients/tui/
├── __init__.py
├── base.py              # BaseTUI (ABC)
└── components/
    ├── __init__.py
    ├── header.py        # Header component
    ├── footer.py        # Footer component
    ├── sidebar.py       # Sidebar component
    └── content.py       # ContentArea component
```

## Usage Flow

```
User Input:
───────────────────────────────────────────────────

1. No Arguments:
   $ unibos-dev
        ↓
   main.py detects no args
        ↓
   Imports tui.py
        ↓
   Runs run_interactive()
        ↓
   TUI launches (BaseTUI)


2. With Arguments:
   $ unibos-dev status
        ↓
   main.py detects args
        ↓
   Click CLI handles command
        ↓
   Executes status_command()
        ↓
   Outputs to terminal
```

## Key Design Decisions

### 1. Hybrid Mode Pattern
- **No args** → Interactive TUI (user-friendly)
- **With args** → CLI commands (scriptable)
- Same entry point (`main.py`)
- Automatic detection via `sys.argv`

### 2. BaseTUI Inheritance
- All TUIs inherit from `BaseTUI`
- Shared rendering, navigation, input handling
- Profile-specific: `get_menu_sections()` and handlers
- Consistent look and feel across all profiles

### 3. 3-Section Structure
- **Section 1**: Primary functionality (modules, targets, services)
- **Section 2**: Operations/tools (tools, operations, system)
- **Section 3**: Info/monitoring (dev tools, monitoring, info)
- Easy mental model, consistent navigation

### 4. Action Handler Registry
```python
self.register_action('action_id', self.handle_action)
```
- Decoupled action handling
- Easy to add new actions
- Clear handler mapping

### 5. Profile-Specific Implementation
- Each profile has unique menu items
- Profile-specific handlers
- Shared base functionality
- Clean separation of concerns

## Benefits

1. **Consistency**: Same pattern across all profiles
2. **Discoverability**: TUI makes features discoverable
3. **Efficiency**: CLI for automation and scripting
4. **Flexibility**: One tool, two modes
5. **Maintainability**: Shared codebase via BaseTUI
6. **Extensibility**: Easy to add new profiles

## Future Enhancements

```
Phase 2:
- Real-time monitoring in TUI
- SSH integration in manager
- P2P discovery in client
- Module hot-reload

Phase 3:
- Web-based TUI (terminal.js)
- Mobile companion app
- Voice commands
- AI assistance

Phase 4:
- Multi-node orchestration
- Distributed deployment
- Load balancing
- Auto-scaling
```

## Success Metrics

✅ **All 4 CLIs implemented**
- unibos-dev
- unibos-manager
- unibos-server
- unibos

✅ **Consistent architecture**
- All use BaseTUI
- All have 3 sections
- All follow hybrid mode

✅ **Comprehensive testing**
- 21/21 tests passing
- All commands working
- Help and version OK

✅ **Complete documentation**
- Architecture overview
- Quick reference
- Implementation guide

## Summary

The UNIBOS 4-tier architecture provides a complete, consistent interface for all deployment scenarios:

1. **Development** (unibos-dev) - Build and deploy
2. **Management** (unibos-manager) - Remote control
3. **Server** (unibos-server) - Production operations
4. **Client** (unibos) - End user interface

All profiles share:
- Same interaction pattern (TUI/CLI hybrid)
- Same visual structure (3 sections)
- Same navigation (keyboard shortcuts)
- Same codebase (BaseTUI inheritance)

This creates a unified, intuitive experience across the entire UNIBOS ecosystem.
