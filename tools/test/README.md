# UNIBOS Test Suite

Test files and testing utilities for the UNIBOS platform.

## Test Files

### TUI Tests
- `test_tui.py` - Basic TUI functionality tests
- `test_tui_interactive.py` - Interactive TUI action handler tests

## Running Tests

From the project root directory:

```bash
# Run basic TUI tests
python tools/test/test_tui.py

# Run interactive TUI tests
python tools/test/test_tui_interactive.py

# Run all tests (future)
python -m pytest tools/test/
```

## Test Categories

### Unit Tests
Tests for individual components and functions.

### Integration Tests
Tests for component interactions and workflows.

### UI Tests
Tests for Terminal User Interface components.

### Performance Tests
Tests for system performance and resource usage.

## Writing Tests

When adding new tests:
1. Follow naming convention: `test_*.py`
2. Use descriptive test names
3. Add documentation
4. Group related tests together