#!/bin/bash

# UNIBOS Backend Startup Script
# DevOps Security Enhanced Version

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="${SCRIPT_DIR}/venv"
PYTHON_BIN="${VENV_PATH}/bin/python"
PID_FILE="${SCRIPT_DIR}/.backend.pid"
LOG_FILE="${SCRIPT_DIR}/server.log"
PORT=8000

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if backend is running
check_backend() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0  # Running
        else
            rm -f "$PID_FILE"
            return 1  # Not running
        fi
    fi
    return 1  # Not running
}

# Function to stop backend
stop_backend() {
    if check_backend; then
        PID=$(cat "$PID_FILE")
        echo -e "${YELLOW}Stopping backend (PID: $PID)...${NC}"
        kill "$PID" 2>/dev/null
        sleep 2
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${YELLOW}Force stopping...${NC}"
            kill -9 "$PID" 2>/dev/null
        fi
        rm -f "$PID_FILE"
        echo -e "${GREEN}Backend stopped${NC}"
    else
        echo -e "${YELLOW}Backend is not running${NC}"
    fi
}

# Function to start backend
start_backend() {
    if check_backend; then
        PID=$(cat "$PID_FILE")
        echo -e "${YELLOW}Backend is already running (PID: $PID)${NC}"
        return 0
    fi
    
    # Check if port is in use
    if lsof -i :$PORT > /dev/null 2>&1; then
        echo -e "${RED}Port $PORT is already in use!${NC}"
        echo "Checking what's using the port..."
        lsof -i :$PORT
        return 1
    fi
    
    # Activate virtual environment and start server
    echo -e "${GREEN}Starting backend on port $PORT...${NC}"
    
    # Rotate log file if it's too large (>10MB)
    if [ -f "$LOG_FILE" ] && [ $(stat -f%z "$LOG_FILE" 2>/dev/null || stat --format=%s "$LOG_FILE" 2>/dev/null || echo 0) -gt 10485760 ]; then
        mv "$LOG_FILE" "${LOG_FILE}.$(date +%Y%m%d_%H%M%S)"
        echo "Log file rotated"
    fi
    
    # Start Django with development settings
    cd "$SCRIPT_DIR"
    export SECRET_KEY='dev-secret-key-for-testing'
    nohup "$PYTHON_BIN" manage.py runserver --settings=unibos_backend.settings.development 0.0.0.0:$PORT >> "$LOG_FILE" 2>&1 &
    PID=$!
    echo $PID > "$PID_FILE"
    
    # Wait a moment and check if it started successfully
    sleep 3
    if check_backend; then
        echo -e "${GREEN}✓ Backend started successfully (PID: $PID)${NC}"
        echo -e "${GREEN}✓ Web UI: http://localhost:$PORT${NC}"
        echo -e "${GREEN}✓ API Status: http://localhost:$PORT/api/status/${NC}"
        
        # Check API status
        if curl -s http://localhost:$PORT/api/status/ > /dev/null 2>&1; then
            echo -e "${GREEN}✓ API is responding${NC}"
        else
            echo -e "${YELLOW}⚠ API may still be initializing...${NC}"
        fi
    else
        echo -e "${RED}✗ Failed to start backend${NC}"
        echo "Check the log file: $LOG_FILE"
        tail -20 "$LOG_FILE"
        return 1
    fi
}

# Function to restart backend
restart_backend() {
    echo -e "${YELLOW}Restarting backend...${NC}"
    stop_backend
    sleep 2
    start_backend
}

# Function to show status
status_backend() {
    if check_backend; then
        PID=$(cat "$PID_FILE")
        echo -e "${GREEN}✓ Backend is running (PID: $PID)${NC}"
        
        # Check API health
        if curl -s http://localhost:$PORT/api/status/ > /dev/null 2>&1; then
            echo -e "${GREEN}✓ API is healthy${NC}"
            curl -s http://localhost:$PORT/api/status/ | python -m json.tool 2>/dev/null || curl -s http://localhost:$PORT/api/status/
        else
            echo -e "${YELLOW}⚠ API is not responding${NC}"
        fi
        
        # Show memory usage
        if command -v ps > /dev/null; then
            echo -e "\n${YELLOW}Memory Usage:${NC}"
            ps aux | grep -E "PID|$PID" | grep -v grep
        fi
    else
        echo -e "${RED}✗ Backend is not running${NC}"
    fi
}

# Function to tail logs
tail_logs() {
    echo -e "${YELLOW}Tailing server logs (Ctrl+C to stop)...${NC}"
    tail -f "$LOG_FILE"
}

# Main script logic
case "${1:-}" in
    start)
        start_backend
        ;;
    stop)
        stop_backend
        ;;
    restart)
        restart_backend
        ;;
    status)
        status_backend
        ;;
    logs)
        tail_logs
        ;;
    *)
        echo "UNIBOS Backend Control Script"
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start    - Start the backend server"
        echo "  stop     - Stop the backend server"
        echo "  restart  - Restart the backend server"
        echo "  status   - Check backend status"
        echo "  logs     - Tail server logs"
        exit 1
        ;;
esac

exit 0