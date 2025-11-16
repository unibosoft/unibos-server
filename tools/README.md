# UNIBOS Tools Directory

This directory contains development tools, testing utilities, and deployment scripts for the UNIBOS platform.

## Directory Structure

```
tools/
├── deployment/     # Deployment scripts and utilities
├── test/          # Test files and testing utilities
└── scripts/       # Various utility scripts
```

## Subdirectories

### /deployment
Contains deployment-related scripts and configurations:
- Deployment automation scripts
- Server configuration templates
- CI/CD pipeline configurations

### /test
Contains test files and testing utilities:
- TUI tests
- Unit tests
- Integration tests
- Performance tests

### /scripts
Contains various utility scripts:
- Development helpers
- Build scripts
- Maintenance utilities

## Usage

All tools should be run from the project root directory:

```bash
# Run a test
python tools/test/test_tui.py

# Run a deployment script
bash tools/deployment/deploy.sh
```

## Contributing

When adding new tools:
1. Place them in the appropriate subdirectory
2. Add documentation
3. Update this README if necessary