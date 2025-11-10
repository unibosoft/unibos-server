#!/bin/bash
# UNIBOS v525 Root Launcher

echo "🚀 launching unibos v525..."

# Ensure we're in the right directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Start web core in background (non-blocking)
(
    # Check if backend is already running
    if [ -f "platform/runtime/web/backend/.backend.pid" ]; then
        PID=$(cat "platform/runtime/web/backend/.backend.pid" 2>/dev/null)
        if ps -p "$PID" > /dev/null 2>&1; then
            # Backend already running, just open browser
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
        else
            # Backend not running, start it
            if [ -f "platform/runtime/web/backend/start_backend.sh" ]; then
                ./platform/runtime/web/backend/start_backend.sh start > /dev/null 2>&1
                
                # Wait for backend to be ready
                sleep 3
                
                # Open browser
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
    else
        # No PID file, start backend
        if [ -f "platform/runtime/web/backend/start_backend.sh" ]; then
            ./platform/runtime/web/backend/start_backend.sh start > /dev/null 2>&1
            
            # Wait for backend to be ready
            sleep 3
            
            # Open browser
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