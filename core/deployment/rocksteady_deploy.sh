#!/bin/bash
#
# UNIBOS Rocksteady Deployment Script
# Version-agnostic automated deployment with intelligent checks
#
# Usage: ./rocksteady_deploy.sh [action]
# Actions: deploy, check, install-deps, install-ocr, help
#

set -e  # Exit on error

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - Auto-detected from repository structure
REMOTE_HOST="rocksteady"
REMOTE_USER="ubuntu"
REMOTE_DIR="/home/ubuntu/unibos"
# Navigate up two levels from core/deployment to get repository root
LOCAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Auto-detect current version from VERSION.json if exists
CURRENT_VERSION="unknown"
if [ -f "$LOCAL_DIR/VERSION.json" ]; then
    CURRENT_VERSION=$(grep -o '"version": *"[^"]*"' "$LOCAL_DIR/VERSION.json" | cut -d'"' -f4 || echo "unknown")
fi

# Auto-detect architecture (detect core/web vs platform/runtime/web/backend)
if [ -d "$LOCAL_DIR/core/web" ]; then
    BACKEND_PATH="core/web"
    VENV_PATH="$REMOTE_DIR/core/web/venv"
    MANAGE_PY_PATH="$REMOTE_DIR/core/web"
elif [ -d "$LOCAL_DIR/platform/runtime/web/backend" ]; then
    BACKEND_PATH="platform/runtime/web/backend"
    VENV_PATH="$REMOTE_DIR/platform/runtime/web/backend/venv"
    MANAGE_PY_PATH="$REMOTE_DIR/platform/runtime/web/backend"
else
    echo -e "${RED}Error: Cannot detect backend structure${NC}"
    exit 1
fi

# Print functions
print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}\n"
}

print_step() {
    echo -e "${BLUE}▶${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check local repository size before transfer
check_local_size() {
    print_header "Pre-Flight Size Check"

    print_step "Detected architecture: $BACKEND_PATH"
    print_step "Deploying version: $CURRENT_VERSION"
    print_step "Analyzing local repository size..."

    # Check total size
    total_size=$(du -sh "$LOCAL_DIR" 2>/dev/null | cut -f1)
    print_step "Total repository size: $total_size"

    # Check for large directories that shouldn't be deployed
    print_step "Checking for deployment blockers..."

    local has_issues=0

    # Check Flutter build directories (any mobile/build or */build pattern)
    flutter_builds=$(find "$LOCAL_DIR" -type d -name "build" -path "*/mobile/*" 2>/dev/null)
    if [ ! -z "$flutter_builds" ]; then
        echo "$flutter_builds" | while read build_dir; do
            if [ -d "$build_dir" ]; then
                build_size=$(du -sh "$build_dir" 2>/dev/null | cut -f1)
                print_error "Flutter build directory found: $build_size"
                print_warning "  Location: ${build_dir#$LOCAL_DIR/}"
                has_issues=1
            fi
        done
    fi

    # Check for Python venv in local directory (architecture-aware)
    if [ -d "$LOCAL_DIR/$BACKEND_PATH/venv" ]; then
        venv_size=$(du -sh "$LOCAL_DIR/$BACKEND_PATH/venv" 2>/dev/null | cut -f1)
        print_warning "Local venv found: $venv_size (will be excluded)"
    fi

    # Check for large log files (architecture-aware)
    large_logs=$(find "$LOCAL_DIR/$BACKEND_PATH" -name "*.log" -size +10M 2>/dev/null)
    if [ ! -z "$large_logs" ]; then
        print_warning "Large log files found:"
        echo "$large_logs" | while read log; do
            log_size=$(du -sh "$log" | cut -f1)
            print_warning "  - $(basename $log): $log_size"
        done
        has_issues=1
    fi

    # Check for database backups (architecture-aware)
    db_backups=$(find "$LOCAL_DIR/$BACKEND_PATH" -name "*.backup_*" -o -name "db.sqlite3" 2>/dev/null)
    if [ ! -z "$db_backups" ]; then
        print_warning "Database files found (will be excluded):"
        echo "$db_backups" | while read db; do
            db_size=$(du -sh "$db" 2>/dev/null | cut -f1)
            print_warning "  - $(basename $db): $db_size"
        done
    fi

    # Calculate expected transfer size (excluding common patterns)
    print_step "Calculating expected transfer size..."
    expected_size=$(rsync -an --stats \
        --exclude='venv/' \
        --exclude='*.log' \
        --exclude='*.backup_*' \
        --exclude='db.sqlite3*' \
        --exclude='build/' \
        --exclude='__pycache__/' \
        --exclude='.DS_Store' \
        --exclude='archive/' \
        --exclude='data/' \
        --exclude='data_db/' \
        "$LOCAL_DIR/" | grep "Total file size" | awk '{print $4, $5}')

    print_success "Expected transfer size: $expected_size"

    if [ $has_issues -eq 1 ]; then
        print_error "⚠ Issues found that may affect deployment"
        echo ""
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "Deployment cancelled"
            exit 1
        fi
    fi

    print_success "Pre-flight check passed"
    return 0
}

# Sync files using rsync with proper exclusions
sync_files() {
    print_header "Syncing Files to Rocksteady"

    print_step "Using .rsyncignore for exclusion patterns..."

    if [ ! -f "$LOCAL_DIR/.rsyncignore" ]; then
        print_error ".rsyncignore file not found!"
        return 1
    fi

    # Perform sync
    print_step "Starting rsync..."
    if rsync -avz --progress \
        --exclude-from="$LOCAL_DIR/.rsyncignore" \
        "$LOCAL_DIR/" \
        "$REMOTE_HOST:$REMOTE_DIR/"; then
        print_success "Files synced successfully"
        return 0
    else
        print_error "File sync failed"
        return 1
    fi
}

# Check and install Python dependencies
check_and_install_deps() {
    print_header "Checking Python Dependencies"

    local requirements_file="$1"
    local deps_type="$2"

    print_step "Checking $deps_type dependencies on remote..."

    # Create a Python script to check installed packages
    ssh "$REMOTE_HOST" "cat > /tmp/check_deps.py << 'PYTHON_EOF'
import sys
import subprocess

def check_package(package_line):
    if not package_line.strip() or package_line.startswith('#'):
        return None

    # Parse package==version
    if '==' in package_line:
        package, version = package_line.split('==')
        package = package.strip()
        version = version.strip()
    else:
        package = package_line.strip()
        version = None

    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'show', package],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            # Package is installed, check version if specified
            if version:
                installed_version = None
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        installed_version = line.split(':', 1)[1].strip()
                        break

                if installed_version == version:
                    return ('ok', package, version)
                else:
                    return ('wrong_version', package, version, installed_version)
            return ('ok', package, None)
        else:
            return ('missing', package, version)
    except Exception as e:
        return ('error', package, str(e))

# Read requirements from stdin
missing = []
wrong_version = []
errors = []

for line in sys.stdin:
    result = check_package(line)
    if result:
        status = result[0]
        if status == 'missing':
            missing.append(result[1:])
        elif status == 'wrong_version':
            wrong_version.append(result[1:])
        elif status == 'error':
            errors.append(result[1:])

# Output results
if missing:
    print('MISSING:')
    for pkg, ver in missing:
        if ver:
            print(f'{pkg}=={ver}')
        else:
            print(pkg)

if wrong_version:
    print('WRONG_VERSION:')
    for pkg, expected, installed in wrong_version:
        print(f'{pkg}: expected {expected}, installed {installed}')

if errors:
    print('ERRORS:')
    for pkg, err in errors:
        print(f'{pkg}: {err}')

if not missing and not wrong_version and not errors:
    print('ALL_OK')
PYTHON_EOF
"

    # Run the check
    local check_result=$(ssh "$REMOTE_HOST" "cd $REMOTE_DIR/core/web && source $VENV_PATH/bin/activate && cat $requirements_file | $VENV_PATH/bin/python3 /tmp/check_deps.py")

    if echo "$check_result" | grep -q "ALL_OK"; then
        print_success "All $deps_type dependencies are installed"
        return 0
    else
        print_warning "Some $deps_type dependencies need installation:"
        echo "$check_result"
        echo ""

        print_step "Installing missing dependencies..."
        if ssh "$REMOTE_HOST" "cd $REMOTE_DIR/core/web && source $VENV_PATH/bin/activate && pip install -r $requirements_file"; then
            print_success "$deps_type dependencies installed"
            return 0
        else
            print_error "Failed to install $deps_type dependencies"
            return 1
        fi
    fi
}

# Check and install OCR/ML dependencies
install_ocr_deps() {
    print_header "Installing OCR/ML Dependencies"

    print_step "Checking system OCR packages..."

    ssh "$REMOTE_HOST" << 'REMOTE_SCRIPT'
    # Check and install system packages
    missing_packages=""

    if ! dpkg -l | grep -q tesseract-ocr; then
        missing_packages="$missing_packages tesseract-ocr"
    fi

    if ! dpkg -l | grep -q poppler-utils; then
        missing_packages="$missing_packages poppler-utils"
    fi

    if ! dpkg -l | grep -q libgl1; then
        missing_packages="$missing_packages libgl1"
    fi

    if ! dpkg -l | grep -q libglib2.0-0; then
        missing_packages="$missing_packages libglib2.0-0"
    fi

    if [ ! -z "$missing_packages" ]; then
        echo "Installing system packages: $missing_packages"
        sudo apt-get update -qq
        sudo apt-get install -y $missing_packages
    else
        echo "All system OCR packages are installed"
    fi
REMOTE_SCRIPT

    print_success "System OCR packages ready"

    # Check Python OCR packages
    print_step "Checking Python OCR packages..."

    local ocr_packages="pytesseract opencv-python numpy paddleocr paddlepaddle torch torchvision transformers easyocr surya-ocr"

    local missing_ocr=$(ssh "$REMOTE_HOST" "cd $REMOTE_DIR/core/web && source $VENV_PATH/bin/activate && python3 -c \"
import sys
missing = []
for pkg in '$ocr_packages'.split():
    try:
        __import__(pkg.replace('-', '_'))
    except ImportError:
        missing.append(pkg)
if missing:
    print(' '.join(missing))
\"")

    if [ -z "$missing_ocr" ]; then
        print_success "All Python OCR packages are installed"
        return 0
    else
        print_warning "Missing OCR packages: $missing_ocr"
        print_step "Installing from requirements.txt..."

        ssh "$REMOTE_HOST" "cd $REMOTE_DIR/core/web && source $VENV_PATH/bin/activate && pip install pytesseract opencv-python numpy paddleocr paddlepaddle==2.6.2 torch==2.6.0 torchvision==0.21.0 transformers easyocr surya-ocr"

        print_success "OCR dependencies installed"
    fi
}

# Run database migrations
run_migrations() {
    print_header "Running Database Migrations"

    print_step "Checking for pending migrations..."

    local pending=$(ssh "$REMOTE_HOST" "cd $REMOTE_DIR/core/web && PYTHONPATH=$REMOTE_DIR/core/web:$REMOTE_DIR DJANGO_SETTINGS_MODULE=unibos_backend.settings.production $VENV_PATH/bin/python3 manage.py showmigrations --plan 2>/dev/null | grep '\[ \]' | wc -l")

    if [ "$pending" -eq "0" ]; then
        print_success "No pending migrations"
        return 0
    else
        print_step "Found $pending pending migrations, applying..."

        if ssh "$REMOTE_HOST" "cd $REMOTE_DIR/core/web && PYTHONPATH=$REMOTE_DIR/core/web:$REMOTE_DIR DJANGO_SETTINGS_MODULE=unibos_backend.settings.production $VENV_PATH/bin/python3 manage.py migrate"; then
            print_success "Migrations applied successfully"
            return 0
        else
            print_error "Migration failed"
            return 1
        fi
    fi
}

# Restart services
restart_services() {
    print_header "Restarting Services"

    print_step "Restarting gunicorn..."
    ssh "$REMOTE_HOST" "sudo systemctl restart gunicorn"
    sleep 2

    local gunicorn_status=$(ssh "$REMOTE_HOST" "systemctl is-active gunicorn")
    if [ "$gunicorn_status" = "active" ]; then
        print_success "Gunicorn is running"
    else
        print_error "Gunicorn failed to start"
        return 1
    fi

    print_step "Restarting nginx..."
    ssh "$REMOTE_HOST" "sudo systemctl restart nginx"

    local nginx_status=$(ssh "$REMOTE_HOST" "systemctl is-active nginx")
    if [ "$nginx_status" = "active" ]; then
        print_success "Nginx is running"
    else
        print_error "Nginx failed to start"
        return 1
    fi

    return 0
}

# Health check
health_check() {
    print_header "Health Check"

    print_step "Testing HTTP endpoint..."

    local http_code=$(ssh "$REMOTE_HOST" "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/")

    if [ "$http_code" = "302" ] || [ "$http_code" = "200" ]; then
        print_success "Server is responding (HTTP $http_code)"
    else
        print_error "Server returned HTTP $http_code"
        return 1
    fi

    print_step "Testing module endpoints..."
    local module_code=$(ssh "$REMOTE_HOST" "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/module/birlikteyiz/")

    if [ "$module_code" = "302" ] || [ "$module_code" = "200" ]; then
        print_success "Modules are accessible (HTTP $module_code)"
    else
        print_warning "Module check returned HTTP $module_code"
    fi

    return 0
}

# Full deployment
full_deploy() {
    print_header "Starting UNIBOS Deployment"

    # Pre-flight checks
    check_local_size || exit 1

    # Sync files
    sync_files || exit 1

    # Check dependencies
    check_and_install_deps "$REMOTE_DIR/core/web/requirements.txt" "core" || exit 1

    # Check uvicorn (required for gunicorn workers)
    print_step "Ensuring uvicorn is installed..."
    ssh "$REMOTE_HOST" "cd $REMOTE_DIR/core/web && source $VENV_PATH/bin/activate && pip install 'uvicorn[standard]'" || exit 1

    # Run migrations
    run_migrations || exit 1

    # Restart services
    restart_services || exit 1

    # Health check
    health_check || exit 1

    print_header "Deployment Complete"
    print_success "UNIBOS is now running on Rocksteady!"
}

# Show help
show_help() {
    cat << EOF
UNIBOS Rocksteady Deployment Script

Usage: $0 [action]

Actions:
  deploy          Full deployment with all checks (default)
  check           Run health checks only
  install-deps    Check and install Python dependencies
  install-ocr     Install OCR/ML dependencies
  sync            Sync files only
  migrate         Run database migrations only
  restart         Restart services only
  help            Show this help

Examples:
  $0                    # Full deployment
  $0 check              # Health check only
  $0 install-ocr        # Install OCR dependencies

Features:
  ✓ Pre-flight size checks
  ✓ Automatic dependency detection and installation
  ✓ Smart rsync with exclusion patterns
  ✓ Database migration management
  ✓ Service restart and verification
  ✓ Comprehensive health checks

EOF
}

# Main
ACTION="${1:-deploy}"

case "$ACTION" in
    deploy)
        full_deploy
        ;;
    check)
        health_check
        ;;
    install-deps)
        check_and_install_deps "$REMOTE_DIR/core/web/requirements.txt" "core"
        ;;
    install-ocr)
        install_ocr_deps
        ;;
    sync)
        check_local_size && sync_files
        ;;
    migrate)
        run_migrations
        ;;
    restart)
        restart_services
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown action: $ACTION"
        show_help
        exit 1
        ;;
esac
