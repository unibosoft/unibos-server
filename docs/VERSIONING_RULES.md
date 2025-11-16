# UNIBOS Versioning Rules

## Version Format
```
v0.XXX.Y
```
- `v0` - Major version (always v0 during development)
- `XXX` - Minor version (increments with each release)
- `Y` - Patch version (for hotfixes only)

## Build Number Format
```
YYYYMMDD_HHMM
```
- `YYYY` - Year (4 digits)
- `MM` - Month (2 digits, 01-12)
- `DD` - Day (2 digits, 01-31)
- `HH` - Hour (2 digits, 00-23)
- `MM` - Minutes (2 digits, 00-59)

### Example
- Version: `v0.534.0`
- Build: `20251116_0550`
- Means: Version 534, created on November 16, 2025 at 05:50 AM

## Version Creation Process

### 1. Update VERSION.json
When creating a new version, update the `VERSION.json` file with:
```json
{
  "version": "v0.535.0",
  "build": "20251116_0550",
  "build_number": "20251116_0550",
  "release_date": "2025-11-16 05:50:00 +0300",
  "author": "berk hatırlı",
  "location": "bitez, bodrum"
}
```

### 2. Generate Build Number
Use the current timestamp when creating the version:
```bash
date '+%Y%m%d_%H%M'
```

### 3. Important Files to Update
- `/VERSION.json` - Main version file
- `/core/clients/tui/base.py` - TUI version display
- `/core/system/web_ui/backend/context_processors.py` - Web UI version display

## Version Management Commands

### Check Current Version
```bash
cat VERSION.json | jq '.version, .build'
```

### Create New Version Archive
```bash
# Generate timestamp
BUILD=$(date '+%Y%m%d_%H%M')

# Update VERSION.json
jq --arg build "$BUILD" '.build = $build | .build_number = $build' VERSION.json > tmp.json && mv tmp.json VERSION.json

# Create archive
./archive.sh
```

## Rules and Best Practices

### 1. Build Number Generation
- **ALWAYS** use the current date and time when creating a new version
- **NEVER** reuse old build numbers
- **NEVER** use simple incremental numbers (like 534, 535)
- Build number represents the exact moment of version creation

### 2. Version Increments
- Increment minor version (XXX) for new features or significant changes
- Keep patch version at 0 unless creating a hotfix
- Never skip version numbers

### 3. Consistency
- Build number must be consistent across all files
- Use the same format everywhere (YYYYMMDD_HHMM)
- Update all relevant files when changing version

### 4. Documentation
- Always update changelog in VERSION.json
- Include features, improvements, and fixes
- Use clear, concise descriptions

## Display Formats

### TUI Display
```
unibos v0.534.0
build: 20251116_0550
```

### Web UI Display
```
v0.534.0 (build 20251116_0550)
```

### CLI Display
```
UNIBOS v0.534.0
Build: 20251116_0550
Location: bitez, bodrum
```

## Historical Context
Earlier versions (v527-v533) used this timestamp format for build numbers. This practice ensures:
- Unique identification of each build
- Clear chronological ordering
- Precise tracking of when versions were created
- No ambiguity about version age

## Implementation in Code

### Python Example
```python
from datetime import datetime

def get_build_number():
    """Generate build number in UNIBOS format"""
    return datetime.now().strftime('%Y%m%d_%H%M')

def format_version_display(version, build):
    """Format version for display"""
    return f"{version} (build {build})"
```

### Reading Version in Python
```python
import json
from pathlib import Path

def get_version_info():
    """Read version information from VERSION.json"""
    version_file = Path(__file__).parent / 'VERSION.json'
    with open(version_file, 'r') as f:
        data = json.load(f)
    return {
        'version': data.get('version', 'v0.534.0'),
        'build': data.get('build', datetime.now().strftime('%Y%m%d_%H%M'))
    }
```

## Migration from Old Format
If you encounter old build numbers like "534" or "build_534":
1. Generate a new timestamp-based build number
2. Update all references to use the new format
3. Ensure consistency across TUI, Web UI, and CLI

---
*Last Updated: November 16, 2025*
*Author: Berk Hatırlı*