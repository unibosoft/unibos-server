#!/bin/bash
# UNIBOS v460 Root Launcher

echo "🚀 launching unibos v460..."

# Ensure we're in the right directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Start web core restart in background (non-blocking)
(
    if [ -f "backend/start_backend.sh" ]; then
        ./backend/start_backend.sh restart > /dev/null 2>&1
        
        # Wait for backend to be ready
        sleep 3
    
        # Check if backend started successfully
        if [ -f "backend/.backend.pid" ]; then
            PID=$(cat "backend/.backend.pid" 2>/dev/null)
            if ps -p "$PID" > /dev/null 2>&1; then
                # Open web UI in browser silently
                if command -v open > /dev/null 2>&1; then
                    # macOS
                    open "http://localhost:8000" 2>/dev/null
                elif command -v xdg-open > /dev/null 2>&1; then
                    # Linux
                    xdg-open "http://localhost:8000" 2>/dev/null &
                elif command -v wslview > /dev/null 2>&1; then
                    # WSL
                    wslview "http://localhost:8000" 2>/dev/null &
                fi
            fi
        fi
    fi
) &  # Run entire web core startup in background

# Continue with CLI immediately
echo ""

# Set environment variable to prevent package installation prompts
export UNIBOS_CLI_MODE=1

# Use Python directly with the main venv
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "../venv" ]; then
    source ../venv/bin/activate
fi

# Run from src directory
cd src 2>/dev/null || true
exec python3 main.py