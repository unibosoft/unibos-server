# UNIBOS TUI Rebuild Analysis
## v527 vs Current Implementation - Complete Assessment

**Date**: 2025-11-16
**Analyst**: Claude Code
**Task**: Rebuild TUI to match v527 exactly with modern architecture

---

## Executive Summary

The current TUI implementation (v0.534) has good architectural foundation but differs significantly from v527's proven UI/UX. This document provides a complete analysis and rebuild plan to achieve v527 parity while maintaining modern code quality.

### Critical Finding
The current implementation has:
- **Good**: Modern architecture with BaseTUI, component separation, type hints
- **Bad**: Menu structure doesn't match v527, missing tools/dev tools sections
- **Missing**: Several v527 interaction patterns and visual behaviors

---

## Part 1: v527 Reference (Ground Truth)

### Menu Structure (from main.py lines 768-795)

#### TOOLS Section
```python
menu_state.tools = [
    ("system_scrolls", "📊 system scrolls", "forge status & info", True, handler),
    ("castle_guard", "🔒 castle guard", "fortress security", True, handler),
    ("forge_smithy", "🔧 forge smithy", "setup forge tools", True, handler),
    ("anvil_repair", "🛠️  anvil repair", "mend & fix issues", True, handler),
    ("code_forge", "📦 code forge", "version chronicles", True, handler),
    ("web_ui", "🌐 web ui", "web interface manager", True, handler),
    ("administration", "🔐 administration", "system administration", True, handler),
]
```

#### DEV TOOLS Section
```python
menu_state.dev_tools = [
    ("ai_builder", "🤖 ai builder", "ai-powered development", True, handler),
    ("database_setup", "🗄️  database setup", "postgresql installer", True, handler),
    ("public_server", "🌐 public server", "deploy to ubuntu/oracle vm", True, handler),
    ("sd_card", "💾 [translated]", "sd operations", True, None),
    ("version_manager", "📊 version manager", "archive & git tools", True, handler),
]
```

### Visual Layout (v527 exact)

```
╔════════════════════════════════════════════════════════════════╗
║ 🪐 unibos v527 › tools › web ui         user | 14:35 | [X]    ║  <- ORANGE BG
╠══════════════╦═══════════════════════════════════════════════════╣
║              ║                                                  ║
║  📦 modules  ║  CONTENT AREA                                    ║
║   0 module1  ║  Shows selected item description                ║
║   1 module2  ║  or command output                               ║
║              ║                                                  ║
║  🔧 tools    ║  Can display:                                    ║
║ > 0 item     ║  - Menu item descriptions                        ║
║   1 item     ║  - Command results                               ║
║              ║  - Interactive forms                             ║
║  🚀 dev      ║  - Status information                            ║
║   0 tool1    ║                                                  ║
║   1 tool2    ║                                                  ║
║              ║                                                  ║
╠══════════════╩═══════════════════════════════════════════════════╣
║ ↑↓ navigate | enter select | ←→ sections | tab | q | hostname ║  <- DARK BG
╚════════════════════════════════════════════════════════════════╝
```

### Key V527 Features

1. **Three-Section Sidebar**
   - Each section has header with icon + label
   - Sections: modules, tools, dev_tools
   - Orange highlight on current section
   - Quick select numbers (0-9) visible

2. **Navigation**
   - ↑/↓: Navigate within section
   - ←/→: Switch sections
   - TAB: Cycle sections forward
   - ENTER: Execute selected item
   - ESC/Q: Exit
   - 0-9: Quick select

3. **Visual Hierarchy**
   - Header: Single line, orange background, breadcrumb
   - Sidebar: Dark background, orange highlights
   - Content: Full width right panel, no border
   - Footer: Dark background, hints + system info

4. **Content Area Behavior**
   - Dims sidebar when showing detailed content
   - Scrollable output
   - Persistent display (stays until new content)
   - Syntax highlighting for certain patterns

---

## Part 2: Current Implementation Assessment

### File Structure (v0.534)
```
core/clients/tui/
├── base.py                    # BaseTUI - good foundation
├── components/
│   ├── header.py             # ✓ Works well
│   ├── footer.py             # ✓ Works well
│   ├── sidebar.py            # ⚠️  Needs fixes
│   ├── content.py            # ⚠️  Needs fixes
│   ├── menu.py               # ✓ Good structure
│   └── statusbar.py          # ? Not used in v527
└── framework/
    └── layout.py             # ? Unclear usage

core/profiles/dev/
└── tui.py                     # UnibosDevTUI - WRONG menu structure
```

### What Works Well

1. **BaseTUI Architecture** (base.py)
   - Good separation of concerns
   - Action handler registry pattern
   - Component-based rendering
   - State management with MenuState
   - Type hints and documentation

2. **Header Component** (header.py)
   - Orange background implemented correctly
   - Breadcrumb support
   - Time/username display
   - Lowercase UI support

3. **Footer Component** (footer.py)
   - Dark background
   - System status display
   - Navigation hints
   - LED status indicator

### What's Broken/Different

#### 1. Menu Structure (CRITICAL)
**Problem**: Current UnibosDevTUI has 4 sections, not matching v527's 3 sections

Current structure:
```python
sections = [
    'development',    # ❌ Not in v527
    'git & deploy',   # ❌ Not in v527
    'database',       # ❌ Not in v527
    'platform'        # ❌ Not in v527
]
```

Should be:
```python
sections = [
    'modules',        # ✓ With module discovery
    'tools',          # ✓ 7 items from v527
    'dev tools'       # ✓ 5 items from v527
]
```

#### 2. Sidebar Component Issues

**Problems**:
- Quick select numbers not visible on non-selected items
- Section highlighting not exactly like v527
- Item spacing differs from v527
- Missing proper dimming when in content mode

**v527 Sidebar Behavior**:
```python
# Each item shows:
"  2 🔧 forge smithy"  # Number visible even when not selected
#  ^-- Yellow number, visible always

# Selected item:
"> 2 🔧 forge smithy"  # Orange background, bold text
#  ^-- Selection marker
```

Current sidebar only shows numbers on selected items.

#### 3. Content Area Issues

**Problems**:
- Doesn't dim sidebar properly
- Missing scroll position indicator at top
- Content wrapping not exactly like v527
- Missing some syntax highlighting patterns

#### 4. Navigation State

**Problems**:
- Quick select (0-9) works but visual feedback wrong
- Section switching (TAB) works but animation differs
- No smooth scroll indication

#### 5. Missing Features

1. **Module Discovery**: v527 dynamically discovers modules from filesystem
2. **Translation System**: v527 has i18n support (not critical for dev)
3. **Content Area Dimming**: Sidebar should dim when showing command output
4. **Real-time Updates**: Clock in header should update (v527 had this)

---

## Part 3: V527 Tools & Dev Tools Complete Reference

### TOOLS Section - Detailed

```python
[
    # Item 0
    {
        'id': 'system_scrolls',
        'icon': '📊',
        'label': 'system scrolls',
        'description': 'forge status & info',
        'handler': 'handle_tool_system_scrolls',
        'sub_items': [
            'show forge status',
            'display version info',
            'list installed modules',
            'check system health'
        ]
    },

    # Item 1
    {
        'id': 'castle_guard',
        'icon': '🔒',
        'label': 'castle guard',
        'description': 'fortress security',
        'handler': 'handle_tool_castle_guard',
        'sub_items': [
            'change admin password',
            'manage access tokens',
            'view security logs',
            'configure firewall'
        ]
    },

    # Item 2
    {
        'id': 'forge_smithy',
        'icon': '🔧',
        'label': 'forge smithy',
        'description': 'setup forge tools',
        'handler': 'handle_tool_forge_smithy',
        'sub_items': [
            'install dependencies',
            'configure environment',
            'setup database',
            'initialize modules'
        ]
    },

    # Item 3
    {
        'id': 'anvil_repair',
        'icon': '🛠️',
        'label': 'anvil repair',
        'description': 'mend & fix issues',
        'handler': 'handle_tool_anvil_repair',
        'sub_items': [
            'fix database issues',
            'repair file permissions',
            'clean cache files',
            'reset configurations'
        ]
    },

    # Item 4
    {
        'id': 'code_forge',
        'icon': '📦',
        'label': 'code forge',
        'description': 'version chronicles',
        'handler': 'handle_tool_code_forge',
        'sub_items': [
            'view version history',
            'create new version',
            'compare versions',
            'rollback version'
        ]
    },

    # Item 5
    {
        'id': 'web_ui',
        'icon': '🌐',
        'label': 'web ui',
        'description': 'web interface manager',
        'handler': 'handle_tool_web_ui',
        'sub_items': [
            'start web server',
            'stop web server',
            'view server logs',
            'open in browser'
        ]
    },

    # Item 6
    {
        'id': 'administration',
        'icon': '🔐',
        'label': 'administration',
        'description': 'system administration',
        'handler': 'handle_tool_administration',
        'sub_items': [
            'manage users',
            'system settings',
            'backup data',
            'restore data'
        ]
    }
]
```

### DEV TOOLS Section - Detailed

```python
[
    # Item 0
    {
        'id': 'ai_builder',
        'icon': '🤖',
        'label': 'ai builder',
        'description': 'ai-powered development',
        'handler': 'handle_dev_ai_builder',
        'sub_items': [
            'chat with claude',
            'generate code',
            'review changes',
            'auto-document'
        ]
    },

    # Item 1
    {
        'id': 'database_setup',
        'icon': '🗄️',
        'label': 'database setup',
        'description': 'postgresql installer',
        'handler': 'handle_dev_database_setup',
        'sub_items': [
            'install postgresql',
            'create database',
            'run migrations',
            'seed test data'
        ]
    },

    # Item 2
    {
        'id': 'public_server',
        'icon': '🌐',
        'label': 'public server',
        'description': 'deploy to ubuntu/oracle vm',
        'handler': 'handle_dev_public_server',
        'sub_items': [
            'deploy to server',
            'check server status',
            'view remote logs',
            'ssh to server'
        ]
    },

    # Item 3
    {
        'id': 'sd_card',
        'icon': '💾',
        'label': 'sd card',
        'description': 'sd operations',
        'handler': 'handle_dev_sd_card',
        'sub_items': [
            'flash sd card',
            'backup sd card',
            'verify sd card',
            'eject sd card'
        ]
    },

    # Item 4
    {
        'id': 'version_manager',
        'icon': '📊',
        'label': 'version manager',
        'description': 'archive & git tools',
        'handler': 'handle_dev_version_manager',
        'sub_items': [
            'create archive',
            'view archives',
            'git status',
            'git commit & push'
        ]
    }
]
```

---

## Part 4: Rebuild Plan

### Phase 1: Fix Sidebar Component (PRIORITY 1)

**File**: `/Users/berkhatirli/Desktop/unibos-dev/core/clients/tui/components/sidebar.py`

**Changes**:
1. Always show quick select numbers (0-9) on all items, not just selected
2. Number color: Yellow for unselected, matches selected color when selected
3. Fix section header background to match v527 exactly
4. Add proper dimming when `in_submenu` is True

**Code Pattern**:
```python
# Always show number for items 0-9
if i < 10:
    number_color = Colors.YELLOW if not (i == selected_index and not is_dimmed) else fg
    sys.stdout.write(f"{bg}{number_color}{i}{Colors.RESET} ")
```

### Phase 2: Enhance Content Area (PRIORITY 1)

**File**: `/Users/berkhatirli/Desktop/unibos-dev/core/clients/tui/components/content.py`

**Changes**:
1. Add scroll position indicator at top when scrolled
2. Improve text wrapping to match v527
3. Add more syntax highlighting patterns
4. Support dimming sidebar when active

### Phase 3: Rebuild UnibosDevTUI Menu (PRIORITY 1)

**File**: `/Users/berkhatirli/Desktop/unibos-dev/core/profiles/dev/tui.py`

**Complete Replacement**: Change from 4 sections to 3 sections matching v527:

```python
def get_menu_sections(self) -> List[MenuSection]:
    return [
        # Section 0: MODULES
        self._get_modules_section(),

        # Section 1: TOOLS
        self._get_tools_section(),

        # Section 2: DEV TOOLS
        self._get_dev_tools_section(),
    ]

def _get_modules_section(self):
    """Dynamic module discovery like v527"""
    # Scan for modules in registry
    # Return MenuSection with discovered modules

def _get_tools_section(self):
    """V527 exact tools menu"""
    return MenuSection(
        id='tools',
        label='tools',
        icon='🔧',
        items=[
            # 7 items from v527 tools section
            MenuItem(id='system_scrolls', ...),
            MenuItem(id='castle_guard', ...),
            MenuItem(id='forge_smithy', ...),
            MenuItem(id='anvil_repair', ...),
            MenuItem(id='code_forge', ...),
            MenuItem(id='web_ui', ...),
            MenuItem(id='administration', ...),
        ]
    )

def _get_dev_tools_section(self):
    """V527 exact dev tools menu"""
    return MenuSection(
        id='dev_tools',
        label='dev tools',
        icon='🚀',
        items=[
            # 5 items from v527 dev_tools section
            MenuItem(id='ai_builder', ...),
            MenuItem(id='database_setup', ...),
            MenuItem(id='public_server', ...),
            MenuItem(id='sd_card', ...),
            MenuItem(id='version_manager', ...),
        ]
    )
```

### Phase 4: Implement Handlers (PRIORITY 2)

Map v527 functionality to new handlers:

**Tools Handlers**:
- `handle_tool_system_scrolls` → Show system status (like current platform_status)
- `handle_tool_castle_guard` → Security settings
- `handle_tool_forge_smithy` → Setup wizard
- `handle_tool_anvil_repair` → Diagnostic/repair tools
- `handle_tool_code_forge` → Version management
- `handle_tool_web_ui` → Django server management (keep current dev_run/stop)
- `handle_tool_administration` → Admin functions

**Dev Tools Handlers**:
- `handle_dev_ai_builder` → Claude integration
- `handle_dev_database_setup` → DB wizard (keep current db handlers)
- `handle_dev_public_server` → Deployment (keep current deploy_rocksteady)
- `handle_dev_sd_card` → SD card operations (new)
- `handle_dev_version_manager` → Archive & git (keep current git handlers)

### Phase 5: Add Module Discovery (PRIORITY 2)

**File**: `/Users/berkhatirli/Desktop/unibos-dev/core/profiles/dev/tui.py`

```python
def _get_modules_section(self) -> MenuSection:
    """Discover and list installed modules"""
    from core.base.registry import ModuleRegistry

    registry = ModuleRegistry()
    modules = registry.get_all_modules()

    items = []
    for module in modules:
        items.append(MenuItem(
            id=f"module_{module.id}",
            label=module.name,
            icon=module.icon or '📦',
            description=module.description,
            enabled=module.is_enabled,
            metadata={'module': module}
        ))

    return MenuSection(
        id='modules',
        label='modules',
        icon='📦',
        items=items
    )
```

### Phase 6: Enhance BaseTUI (PRIORITY 3)

**File**: `/Users/berkhatirli/Desktop/unibos-dev/core/clients/tui/base.py`

**Changes**:
1. Add real-time clock update in header (optional, low priority)
2. Improve content buffering
3. Add submenu support (for tool sub-items)
4. Better error handling

---

## Part 5: Implementation Checklist

### Must Have (v527 Parity)
- [ ] Sidebar shows numbers 0-9 on all items
- [ ] Three sections: modules, tools, dev tools
- [ ] V527 exact tool names and icons
- [ ] V527 exact dev tool names and icons
- [ ] Quick select (0-9) works
- [ ] TAB cycles sections
- [ ] Content area scrolls properly
- [ ] Lowercase UI throughout

### Should Have (Enhanced UX)
- [ ] Module discovery from registry
- [ ] Smooth section transitions
- [ ] Better error messages
- [ ] Proper process management
- [ ] Log viewing

### Nice to Have (Future)
- [ ] Real-time header clock
- [ ] Sub-menu navigation
- [ ] Translation support
- [ ] Terminal resize handling
- [ ] Color scheme options

---

## Part 6: Testing Strategy

### Unit Tests
1. Test each menu section returns correct structure
2. Test action handlers execute properly
3. Test sidebar rendering with various states
4. Test content area wrapping and scrolling

### Integration Tests
1. Test full navigation flow
2. Test quick select (0-9)
3. Test section switching
4. Test command execution

### Manual Testing
1. Visual comparison with v527 screenshot
2. Navigation feel and responsiveness
3. All keyboard shortcuts
4. Edge cases (long text, terminal resize)

---

## Part 7: Migration Path

### Step 1: Prepare
- [x] Analyze v527 structure ← WE ARE HERE
- [ ] Document all differences
- [ ] Create backup of current implementation

### Step 2: Core Components
- [ ] Fix sidebar.py
- [ ] Fix content.py
- [ ] Test components in isolation

### Step 3: Menu Rebuild
- [ ] Implement new get_menu_sections()
- [ ] Add all tool handlers
- [ ] Add all dev tool handlers
- [ ] Test navigation

### Step 4: Module System
- [ ] Implement module discovery
- [ ] Test module listing
- [ ] Test module enable/disable

### Step 5: Polish
- [ ] Fix visual discrepancies
- [ ] Optimize rendering
- [ ] Add loading states
- [ ] Error handling

### Step 6: Release
- [ ] Full testing suite
- [ ] Documentation
- [ ] Deploy to dev environment

---

## Part 8: Risk Assessment

### High Risk
1. **Breaking existing functionality**: Current TUI is being used
   - **Mitigation**: Keep old implementation as backup, feature flag

2. **Missing v527 behavior**: Subtle UX patterns we might miss
   - **Mitigation**: Direct visual comparison, user testing

### Medium Risk
1. **Module discovery**: May not work with current registry
   - **Mitigation**: Fallback to static list

2. **Handler complexity**: 12 new handlers to implement
   - **Mitigation**: Start with stubs, implement incrementally

### Low Risk
1. **Visual differences**: Colors/spacing slightly off
   - **Mitigation**: Easy to tweak with CSS-like approach

---

## Conclusion

The current TUI has solid architecture but wrong menu structure. By following this plan:

1. Fix sidebar to show numbers always
2. Rebuild menu to match v527 (3 sections, exact names)
3. Implement all 12 handlers (7 tools + 5 dev tools)
4. Add module discovery
5. Polish and test

We can achieve v527 parity while maintaining modern code quality.

**Estimated Effort**:
- Core fixes: 2-4 hours
- Menu rebuild: 4-6 hours
- Handler implementation: 6-8 hours
- Testing & polish: 2-4 hours
- **Total**: 14-22 hours

**Priority Order**:
1. Sidebar fixes (immediate visual improvement)
2. Menu structure (functional parity)
3. Tool handlers (usability)
4. Module discovery (completeness)
5. Polish (perfection)

---

**Next Step**: Implement Phase 1 (Sidebar fixes) and Phase 3 (Menu rebuild) in parallel.
