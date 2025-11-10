#!/bin/bash
# UNIBOS v448 launcher script

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🦄 unibos v448 - unicorn bodrum operating system"
echo "==============================================="
echo "📁 Working directory: $SCRIPT_DIR"

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "📌 Python version: $python_version"

# Check for virtual environment in parent directory first
if [ -d "../venv" ]; then
    echo "🔧 Using existing virtual environment..."
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source ../venv/Scripts/activate
    else
        source ../venv/bin/activate
    fi
elif [ -d "venv" ]; then
    echo "🔧 Using local virtual environment..."
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
else
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
fi

# Install dependencies - check if pip exists first
echo "📥 Checking dependencies..."
if [ -f "venv/bin/pip" ]; then
    venv/bin/pip install -q --upgrade pip
    venv/bin/pip install -q flask flask-cors requests beautifulsoup4 python-dotenv wcwidth 2>/dev/null || echo "⚠️  Some packages may not install"
elif [ -f "venv/Scripts/pip.exe" ]; then
    venv/Scripts/pip.exe install -q --upgrade pip
    venv/Scripts/pip.exe install -q flask flask-cors requests beautifulsoup4 python-dotenv wcwidth 2>/dev/null || echo "⚠️  Some packages may not install"
else
    echo "⚠️  pip not found in virtual environment, checking system packages..."
fi

# UNIBOS doesn't need database configuration
# Projects handle their own databases

# Run main program
echo ""
echo "🎮 Starting unibos..."
echo "===================="

# Check for debug mode
if [ "$UNIBOS_DEBUG" = "true" ]; then
    echo "🐛 Debug mode enabled - logs will be written to /tmp/unibos_debug.log"
fi

# Add error checking
echo "🚦 Launching main program..."
python3 main.py || {
    echo "❌ Program exited with error code: $?"
    echo "💡 Try running with UNIBOS_DEBUG=true for more details"
    exit 1
}

# Deactivate virtual environment
deactivate 2>/dev/null || true