#!/bin/bash
#
# UNIBOS Edge Node Installer
# ==========================
# Install, repair, or uninstall UNIBOS on Raspberry Pi and Linux systems
#
# Usage:
#   curl -sSL https://recaria.org/install.sh | bash              # Install
#   curl -sSL https://recaria.org/install.sh | bash -s repair    # Repair
#   curl -sSL https://recaria.org/install.sh | bash -s uninstall # Uninstall
#
# Supported Platforms:
#   - Raspberry Pi Zero 2W, Pi 3, Pi 4, Pi 5
#   - Ubuntu/Debian Linux
#
# Author: UNIBOS Team
# Version: 1.1.4
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
DIM='\033[2m'
NC='\033[0m'

# Configuration
UNIBOS_VERSION="1.1.4"
UNIBOS_REPO="https://github.com/unibosoft/unibos.git"
CENTRAL_REGISTRY_URL="https://recaria.org"
INSTALL_DIR="$HOME/unibos"
VENV_DIR="$INSTALL_DIR/core/clients/web/venv"
SERVICE_PORT=8000

# Logging
log() { echo -e "  $1"; }
log_ok() { echo -e "  ${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "  ${YELLOW}[!]${NC} $1"; }
log_err() { echo -e "  ${RED}[X]${NC} $1"; }
log_step() { echo -e "\n${CYAN}$1${NC}"; }

# =============================================================================
# BANNER
# =============================================================================

print_banner() {
    clear
    echo ""
    echo -e "${CYAN}"
    echo "  _   _ _   _ ___ ____   ___  ____  "
    echo " | | | | \ | |_ _| __ ) / _ \/ ___| "
    echo " | | | |  \| || ||  _ \| | | \___ \ "
    echo " | |_| | |\  || || |_) | |_| |___) |"
    echo "  \___/|_| \_|___|____/ \___/|____/ "
    echo -e "${NC}"
    echo -e "  ${DIM}edge node installer v${UNIBOS_VERSION}${NC}"
    echo ""
}

# =============================================================================
# SYSTEM INFO
# =============================================================================

detect_system_info() {
    # Platform detection
    PLATFORM="linux"
    PLATFORM_NAME="linux"

    if [ -f /proc/cpuinfo ]; then
        if grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null || \
           grep -q "BCM" /proc/cpuinfo 2>/dev/null; then
            PLATFORM="raspberry-pi"
            if grep -q "Zero 2" /proc/device-tree/model 2>/dev/null; then
                PLATFORM_NAME="raspberry pi zero 2w"
            elif grep -q "Pi 5" /proc/device-tree/model 2>/dev/null; then
                PLATFORM_NAME="raspberry pi 5"
            elif grep -q "Pi 4" /proc/device-tree/model 2>/dev/null; then
                PLATFORM_NAME="raspberry pi 4"
            elif grep -q "Pi 3" /proc/device-tree/model 2>/dev/null; then
                PLATFORM_NAME="raspberry pi 3"
            else
                PLATFORM_NAME="raspberry pi"
            fi
        fi
    fi

    # RAM and CPU
    RAM_MB=0
    [ -f /proc/meminfo ] && RAM_MB=$(grep MemTotal /proc/meminfo | awk '{print int($2/1024)}')
    CPU_CORES=$(nproc 2>/dev/null || echo 1)

    # UNIBOS status
    UNIBOS_INSTALLED="no"
    UNIBOS_RUNNING="no"
    INSTALLED_VERSION=""

    if [ -d "$INSTALL_DIR" ]; then
        UNIBOS_INSTALLED="yes"
        if [ -f "$INSTALL_DIR/VERSION.json" ]; then
            # Get semantic version from display.semantic field
            INSTALLED_VERSION=$(grep -o '"semantic"[[:space:]]*:[[:space:]]*"[^"]*"' "$INSTALL_DIR/VERSION.json" 2>/dev/null | head -1 | cut -d'"' -f4)
        fi
        if systemctl is-active --quiet unibos 2>/dev/null; then
            UNIBOS_RUNNING="yes"
        fi
    fi
}

print_system_info() {
    echo -e "  ${DIM}─────────────────────────────────────${NC}"
    echo -e "  ${CYAN}system${NC}"
    echo -e "    platform    : ${PLATFORM_NAME}"
    echo -e "    ram         : ${RAM_MB} mb"
    echo -e "    cpu cores   : ${CPU_CORES}"
    echo ""
    echo -e "  ${CYAN}unibos${NC}"
    if [ "$UNIBOS_INSTALLED" == "yes" ]; then
        echo -e "    installed   : ${GREEN}yes${NC} (v${INSTALLED_VERSION:-unknown})"
        if [ "$UNIBOS_RUNNING" == "yes" ]; then
            echo -e "    status      : ${GREEN}running${NC}"
        else
            echo -e "    status      : ${YELLOW}stopped${NC}"
        fi
    else
        echo -e "    installed   : ${DIM}no${NC}"
    fi
    echo -e "  ${DIM}─────────────────────────────────────${NC}"
    echo ""
}

# =============================================================================
# MODE SELECTION (Arrow Key Navigation)
# =============================================================================

# Menu options (lowercase)
MENU_OPTIONS=("install" "repair" "uninstall")
MENU_DESCRIPTIONS=("fresh installation" "fix existing installation" "remove unibos")
MENU_COLORS=("$GREEN" "$YELLOW" "$RED")

draw_menu() {
    local selected=$1

    # Move cursor up to redraw menu (3 options + 2 empty lines = 5 lines)
    if [ "$2" == "redraw" ]; then
        printf "\033[5A"  # Move up 5 lines
        printf "\033[K"   # Clear line
    fi

    echo ""
    for i in "${!MENU_OPTIONS[@]}"; do
        printf "\033[K"  # Clear line before printing
        if [ $i -eq $selected ]; then
            echo -e "   ${MENU_COLORS[$i]}▸ ${MENU_OPTIONS[$i]}${NC}  ${DIM}- ${MENU_DESCRIPTIONS[$i]}${NC}"
        else
            echo -e "     ${DIM}${MENU_OPTIONS[$i]}  - ${MENU_DESCRIPTIONS[$i]}${NC}"
        fi
    done
    echo ""
}

select_menu() {
    local selected=0
    local key

    # Default to repair if already installed
    if [ "$UNIBOS_INSTALLED" == "yes" ]; then
        selected=1
    fi

    echo -e "  ${CYAN}select action${NC}  ${DIM}(↑↓ navigate, enter select, q quit)${NC}"

    # Draw initial menu
    draw_menu $selected

    # Hide cursor
    printf "\033[?25l"

    # Trap to restore cursor on exit
    trap 'printf "\033[?25h"' EXIT

    # Read from /dev/tty to handle pipe input (curl | bash)
    exec 3</dev/tty

    while true; do
        # Read single key from tty
        IFS= read -rsn1 key <&3

        # Handle empty key (Enter pressed)
        if [ -z "$key" ]; then
            printf "\033[?25h"  # Show cursor
            exec 3<&-  # Close fd
            echo ""
            SELECTED_MODE="${MENU_OPTIONS[$selected]}"
            return 0
        fi

        case "$key" in
            $'\x1b')  # Escape sequence (arrow keys)
                read -rsn2 -t 0.1 rest <&3
                case "$rest" in
                    '[A')  # Up arrow
                        ((selected--)) || true
                        [ $selected -lt 0 ] && selected=$((${#MENU_OPTIONS[@]} - 1))
                        draw_menu $selected "redraw"
                        ;;
                    '[B')  # Down arrow
                        ((selected++)) || true
                        [ $selected -ge ${#MENU_OPTIONS[@]} ] && selected=0
                        draw_menu $selected "redraw"
                        ;;
                esac
                ;;
            'q'|'Q')  # Quit
                printf "\033[?25h"  # Show cursor
                exec 3<&-  # Close fd
                echo ""
                log "cancelled."
                exit 0
                ;;
            '1')  # Quick select
                printf "\033[?25h"
                exec 3<&-
                echo ""
                SELECTED_MODE="install"
                return 0
                ;;
            '2')
                printf "\033[?25h"
                exec 3<&-
                echo ""
                SELECTED_MODE="repair"
                return 0
                ;;
            '3')
                printf "\033[?25h"
                exec 3<&-
                echo ""
                SELECTED_MODE="uninstall"
                return 0
                ;;
        esac
    done
}

# =============================================================================
# PLATFORM DETECTION
# =============================================================================

detect_platform() {
    log_step "Detecting platform..."

    PLATFORM="linux"
    PLATFORM_DETAIL="generic"
    RAM_MB=0
    CPU_CORES=1

    # Check if Raspberry Pi
    if [ -f /proc/cpuinfo ]; then
        if grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null || \
           grep -q "BCM" /proc/cpuinfo 2>/dev/null; then
            PLATFORM="raspberry-pi"

            if grep -q "Zero 2" /proc/device-tree/model 2>/dev/null; then
                PLATFORM_DETAIL="zero2w"
            elif grep -q "Pi 5" /proc/device-tree/model 2>/dev/null; then
                PLATFORM_DETAIL="pi5"
            elif grep -q "Pi 4" /proc/device-tree/model 2>/dev/null; then
                PLATFORM_DETAIL="pi4"
            elif grep -q "Pi 3" /proc/device-tree/model 2>/dev/null; then
                PLATFORM_DETAIL="pi3"
            fi
        fi
    fi

    # Get RAM and CPU
    [ -f /proc/meminfo ] && RAM_MB=$(grep MemTotal /proc/meminfo | awk '{print int($2/1024)}')
    CPU_CORES=$(nproc 2>/dev/null || echo 1)

    # Set worker config based on platform
    case "$PLATFORM_DETAIL" in
        "zero2w"|"pi3") WORKER_COUNT=1 ;;
        "pi4") WORKER_COUNT=$((RAM_MB >= 4000 ? 3 : 2)) ;;
        "pi5") WORKER_COUNT=4 ;;
        *) WORKER_COUNT=$((CPU_CORES > 4 ? 4 : CPU_CORES)) ;;
    esac

    log_ok "$PLATFORM ($PLATFORM_DETAIL) - ${RAM_MB}MB RAM, $CPU_CORES cores"

    export PLATFORM PLATFORM_DETAIL RAM_MB CPU_CORES WORKER_COUNT
}

# =============================================================================
# PRE-FLIGHT CHECKS
# =============================================================================

check_requirements() {
    log_step "Checking requirements..."

    # Not root
    if [ "$EUID" -eq 0 ]; then
        log_err "Do not run as root! Use: curl ... | bash"
        exit 1
    fi

    # Sudo available
    if ! sudo -n true 2>/dev/null; then
        log "Sudo password required for system packages..."
        sudo -v || { log_err "Sudo required"; exit 1; }
    fi

    log_ok "Requirements OK"
}

# =============================================================================
# INSTALL FUNCTIONS
# =============================================================================

install_dependencies() {
    log_step "Installing dependencies..."

    if command -v apt-get &>/dev/null; then
        sudo apt-get update -qq
        sudo apt-get install -y -qq \
            python3 python3-pip python3-venv python3-dev \
            postgresql postgresql-contrib libpq-dev \
            redis-server git curl wget build-essential \
            avahi-daemon avahi-utils libnss-mdns \
            libffi-dev libssl-dev 2>/dev/null
    else
        log_err "Only apt-based systems supported currently"
        exit 1
    fi

    # Enable services
    sudo systemctl enable postgresql redis-server avahi-daemon 2>/dev/null || true
    sudo systemctl start postgresql redis-server avahi-daemon 2>/dev/null || true

    log_ok "Dependencies installed"
}

install_unibos() {
    log_step "Installing UNIBOS..."

    # Clone repo
    if [ -d "$INSTALL_DIR" ]; then
        log_warn "Existing installation found, updating..."
        cd "$INSTALL_DIR" && git pull origin main 2>/dev/null || true
    else
        log "Cloning repository (GitHub credentials may be required)..."
        git clone --depth 1 "$UNIBOS_REPO" "$INSTALL_DIR" || {
            log_err "Clone failed. Use GitHub PAT as password."
            exit 1
        }
    fi

    # Create venv and install
    cd "$INSTALL_DIR"
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install --upgrade pip wheel -q

    cd "$INSTALL_DIR/core/clients/web"
    "$VENV_DIR/bin/pip" install -r requirements.txt -q 2>/dev/null || \
    "$VENV_DIR/bin/pip" install django djangorestframework psycopg2-binary \
        redis celery channels daphne uvicorn django-environ django-redis \
        djangorestframework-simplejwt django-cors-headers django-filter \
        drf-spectacular django-extensions django-celery-beat channels-redis \
        django-prometheus -q

    log_ok "UNIBOS installed"
}

setup_database() {
    log_step "Setting up database..."

    DB_NAME="unibos_db"
    DB_USER="unibos_user"
    DB_PASS=$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 24)

    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';" 2>/dev/null || true
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" 2>/dev/null || true
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" 2>/dev/null || true
    sudo -u postgres psql -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;" 2>/dev/null || true

    # Save credentials
    mkdir -p "$INSTALL_DIR/data/config"
    cat > "$INSTALL_DIR/data/config/db.env" << EOF
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASS=$DB_PASS
EOF
    chmod 600 "$INSTALL_DIR/data/config/db.env"

    log_ok "Database configured"
}

setup_environment() {
    log_step "Configuring environment..."

    SECRET_KEY=$(openssl rand -base64 48 | tr -dc 'a-zA-Z0-9' | head -c 64)
    LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "127.0.0.1")
    source "$INSTALL_DIR/data/config/db.env"

    cat > "$INSTALL_DIR/.env" << EOF
# UNIBOS Edge Node Configuration
# Generated: $(date -Iseconds)

# Django Settings
DJANGO_SETTINGS_MODULE=unibos_backend.settings.edge
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=$LOCAL_IP,localhost,127.0.0.1,$(hostname),$(hostname).local

# Database
DATABASE_URL=postgres://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASS=$DB_PASS
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Node Identity
NODE_TYPE=edge
NODE_PLATFORM=$PLATFORM
NODE_PLATFORM_DETAIL=$PLATFORM_DETAIL

# Central Registry
CENTRAL_REGISTRY_URL=$CENTRAL_REGISTRY_URL

# Performance
WORKER_COUNT=$WORKER_COUNT
WORKER_TYPE=uvicorn.workers.UvicornWorker

# Modules
ENABLED_MODULES=all
EOF

    chmod 600 "$INSTALL_DIR/.env"
    ln -sf "$INSTALL_DIR/.env" "$INSTALL_DIR/core/clients/web/.env" 2>/dev/null || true

    log_ok "Environment configured"
}

setup_services() {
    log_step "Setting up services..."

    # Main service
    sudo tee /etc/systemd/system/unibos.service > /dev/null << EOF
[Unit]
Description=UNIBOS Edge Node
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$INSTALL_DIR/core/clients/web
EnvironmentFile=$INSTALL_DIR/.env
Environment="PYTHONPATH=$INSTALL_DIR:$INSTALL_DIR/core/clients/web"
Environment="UNIBOS_ROOT=$INSTALL_DIR"
ExecStart=$VENV_DIR/bin/uvicorn unibos_backend.asgi:application --host 0.0.0.0 --port $SERVICE_PORT --workers $WORKER_COUNT
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    # Celery service
    sudo tee /etc/systemd/system/unibos-celery.service > /dev/null << EOF
[Unit]
Description=UNIBOS Celery Worker
After=network.target redis.service

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$INSTALL_DIR/core/clients/web
EnvironmentFile=$INSTALL_DIR/.env
Environment="PYTHONPATH=$INSTALL_DIR:$INSTALL_DIR/core/clients/web"
Environment="UNIBOS_ROOT=$INSTALL_DIR"
ExecStart=$VENV_DIR/bin/celery -A unibos_backend worker --loglevel=info --concurrency=2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    # mDNS service
    sudo tee /etc/avahi/services/unibos.service > /dev/null << EOF
<?xml version="1.0" standalone='no'?>
<!DOCTYPE service-group SYSTEM "avahi-service.dtd">
<service-group>
  <name replace-wildcards="yes">UNIBOS on %h</name>
  <service>
    <type>_unibos._tcp</type>
    <port>$SERVICE_PORT</port>
    <txt-record>version=$UNIBOS_VERSION</txt-record>
    <txt-record>platform=$PLATFORM_DETAIL</txt-record>
  </service>
</service-group>
EOF

    sudo systemctl daemon-reload
    log_ok "Services configured"
}

run_migrations() {
    log_step "Running migrations..."

    cd "$INSTALL_DIR/core/clients/web"
    export PYTHONPATH="$INSTALL_DIR:$INSTALL_DIR/core/clients/web"
    set -a && source "$INSTALL_DIR/.env" && set +a

    "$VENV_DIR/bin/python" manage.py migrate --noinput 2>/dev/null || log_warn "Some migrations skipped"
    "$VENV_DIR/bin/python" manage.py collectstatic --noinput 2>/dev/null || log_warn "Static files skipped"

    log_ok "Migrations complete"
}

start_services() {
    log_step "Starting services..."

    sudo systemctl enable unibos unibos-celery 2>/dev/null || true
    sudo systemctl restart avahi-daemon 2>/dev/null || true
    sudo systemctl start unibos unibos-celery 2>/dev/null || true

    sleep 3

    if systemctl is-active --quiet unibos; then
        log_ok "UNIBOS is running"
    else
        log_warn "Service may still be starting..."
    fi
}

# =============================================================================
# REPAIR FUNCTIONS
# =============================================================================

repair_installation() {
    log_step "Repairing UNIBOS installation..."

    if [ ! -d "$INSTALL_DIR" ]; then
        log_err "No installation found at $INSTALL_DIR"
        log "Run install instead."
        exit 1
    fi

    # Stop services
    sudo systemctl stop unibos unibos-celery 2>/dev/null || true

    # Update code
    log "Updating code..."
    cd "$INSTALL_DIR" && git pull origin main 2>/dev/null || log_warn "Git pull failed"

    # Reinstall dependencies
    log "Reinstalling Python packages..."
    cd "$INSTALL_DIR/core/clients/web"
    "$VENV_DIR/bin/pip" install -r requirements.txt -q 2>/dev/null || true

    # Run migrations
    log "Running migrations..."
    export PYTHONPATH="$INSTALL_DIR:$INSTALL_DIR/core/clients/web"
    set -a && source "$INSTALL_DIR/.env" && set +a
    "$VENV_DIR/bin/python" manage.py migrate --noinput 2>/dev/null || true
    "$VENV_DIR/bin/python" manage.py collectstatic --noinput 2>/dev/null || true

    # Restart services
    sudo systemctl daemon-reload
    sudo systemctl start unibos unibos-celery 2>/dev/null || true

    sleep 2

    if systemctl is-active --quiet unibos; then
        log_ok "Repair complete - UNIBOS is running"
    else
        log_warn "Repair complete - check logs: journalctl -u unibos -f"
    fi
}

# =============================================================================
# UNINSTALL FUNCTIONS
# =============================================================================

uninstall_unibos() {
    log_step "uninstalling unibos..."

    echo ""
    echo -e "  ${RED}warning: this will remove:${NC}"
    echo "    - unibos installation at $INSTALL_DIR"
    echo "    - systemd services (unibos, unibos-celery)"
    echo "    - mdns service configuration"
    echo ""
    echo -e "  ${YELLOW}database and system packages will not be removed.${NC}"
    echo ""

    # Read from /dev/tty for pipe support
    echo -n "  are you sure? [y/N] "
    read -n 1 -r REPLY </dev/tty
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "cancelled."
        exit 0
    fi

    # Stop and disable services
    log "Stopping services..."
    sudo systemctl stop unibos unibos-celery 2>/dev/null || true
    sudo systemctl disable unibos unibos-celery 2>/dev/null || true

    # Remove service files
    log "Removing service files..."
    sudo rm -f /etc/systemd/system/unibos.service
    sudo rm -f /etc/systemd/system/unibos-celery.service
    sudo rm -f /etc/avahi/services/unibos.service
    sudo systemctl daemon-reload

    # Remove installation
    log "Removing installation..."
    rm -rf "$INSTALL_DIR"

    # Remove pipx installation
    pipx uninstall unibos 2>/dev/null || true
    ~/.local/bin/pipx uninstall unibos 2>/dev/null || true

    log_ok "UNIBOS uninstalled"
    echo ""
    log "To remove database: sudo -u postgres dropdb unibos_db"
    log "To remove db user:  sudo -u postgres dropuser unibos_user"
}

# =============================================================================
# SUMMARY
# =============================================================================

print_summary() {
    LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "127.0.0.1")
    NODE_NAME=$(hostname)

    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}     UNIBOS Installation Complete!         ${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo -e "  ${CYAN}Access:${NC}"
    echo -e "    http://$LOCAL_IP:$SERVICE_PORT"
    echo -e "    http://${NODE_NAME}.local:$SERVICE_PORT"
    echo ""
    echo -e "  ${CYAN}Commands:${NC}"
    echo -e "    Status:   sudo systemctl status unibos"
    echo -e "    Logs:     journalctl -u unibos -f"
    echo -e "    Restart:  sudo systemctl restart unibos"
    echo ""

    # Quick health check
    echo -n "  Health: "
    if curl -s "http://localhost:$SERVICE_PORT/health/" 2>/dev/null | grep -q "ok"; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${YELLOW}Starting...${NC}"
    fi
    echo ""
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    print_banner

    # Detect system info first
    detect_system_info
    print_system_info

    # Check for command line argument
    MODE="${1:-}"

    # If no argument, show interactive menu
    if [ -z "$MODE" ]; then
        select_menu
        MODE="$SELECTED_MODE"
    fi

    # Execute based on mode
    case "$MODE" in
        install)
            check_requirements
            detect_platform
            install_dependencies
            install_unibos
            setup_database
            setup_environment
            setup_services
            run_migrations
            start_services
            print_summary
            ;;
        repair)
            check_requirements
            detect_platform
            repair_installation
            ;;
        uninstall)
            uninstall_unibos
            ;;
        *)
            log_err "Unknown mode: $MODE"
            log "Usage: $0 [install|repair|uninstall]"
            exit 1
            ;;
    esac
}

main "$@"
