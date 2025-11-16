# UNIBOS v535 Development Roadmap

**Creation Date:** 2025-11-13
**Last Update:** 2025-11-16 (Comprehensive merge: TODO + v527/v530-v533 analysis)
**Current Phase:** Phase 0.5 - Critical Fixes & Production Parity
**Target Release:** February 1, 2026 (12-week timeline)
**Alternative Fast Track:** 4 weeks for Minimum Viable v535

---

## EXECUTIVE SUMMARY

This roadmap integrates:
1. **Current TODO.md** - Active development tasks and three-tier CLI architecture
2. **v527 Analysis** - TUI/CLI design patterns (ghost key fixes, performance optimizations)
3. **v530-v533 Analysis** - Production infrastructure gaps and advanced features
4. **v533 Production** - Live Rocksteady server deployment insights

### Critical Path:
```
Phase 0.5 (Week 1-2): Infrastructure → Phase 1 (Week 3-4): CLI & Platform
→ Phase 2 (Week 5-6): Modules → Phase 3 (Week 7-8): P2P → Phase 4+ (Week 9-12): Polish
```

### Current Architecture Decisions:
- ✅ **Four-tier CLI:** unibos (production), unibos-dev (developer), unibos-server (server admin), unibos-manager (remote management)
- ✅ **Simplified CLI:** Direct command access (e.g., `unibos-dev run` instead of `unibos-dev dev run`)
- ✅ **Tech Stack:** psutil, JSON metadata, Hybrid P2P (mDNS + REST + WebSocket)
- ✅ **Profile-based:** dev/server/prod/manager configurations
- ✅ **Modern modular architecture:** Distributed modules system (superior to v532 monolith)

### Critical Issues Discovered:
- 🚨 **WebSocket/Channels ENTIRELY MISSING** - All real-time features non-functional
- 🚨 **Celery NOT RUNNING** - Even in production! 10 scheduled tasks broken
- 🚨 **Middleware Stack Incomplete** - Missing 10 critical security/monitoring middleware
- 🚨 **TUI Bugs from v527 Loss** - Ghost keypresses, navigation jumps, flicker

### Feature Parity Status:
- **Archive v532:** 100% (reference implementation)
- **Current v534:** ~35% (significant gap)
- **Target v535:** 80%+ (achievable in 12 weeks)

---

## 🚨 PHASE 0.5: Critical Fixes & Production Parity (URGENT - Week 1-2)

**Goal:** Restore critical infrastructure lost between v527/v532 and current v534
**Duration:** 2 weeks
**Priority:** CRITICAL - Must complete before continuing Phase 1

### 0.5.1 TUI/CLI Bug Fixes (v527 Patterns) 🔴 CRITICAL

**Problem:** Ghost keypresses, navigation jumps 2-3 items, sidebar flicker
**Root Cause:** Lost v527 optimizations during monorepo restructure
**Impact:** TUI unusable for daily operations

#### Triple-Flush Input Buffer (Priority 0 - Fix This Week)

```python
# v527 Pattern - Add to core/clients/tui/base.py
def clear_input_buffer(self):
    """v527 critical fix: Triple-flush eliminates ghost keypresses"""
    try:
        import termios
        for _ in range(3):
            termios.tcflush(sys.stdin, termios.TCIFLUSH)
            termios.tcflush(sys.stdin, termios.TCIOFLUSH)
            time.sleep(0.01)
    except:
        pass
```

- [ ] **Add clear_input_buffer() method**
  - **File:** `core/clients/tui/base.py`
  - **Why:** Eliminates 90% of navigation bugs
  - **From:** v527/src/submenu_handler.py
  - **Effort:** 30 minutes
  - **Priority:** 🔴 CRITICAL

- [ ] **Call before/after submenu entry/exit**
  - **Files:** `core/profiles/dev/tui.py`, all action handlers
  - **Why:** Prevents buffered keystrokes from previous context
  - **Effort:** 2 hours
  - **Code Example:**
    ```python
    def handle_menu_item_select(self, item):
        self.clear_input_buffer()  # BEFORE action
        # ... execute action ...
        self.clear_input_buffer()  # AFTER action
    ```

#### Debouncing Pattern (Priority 0)

```python
# v527 Pattern - Add to main event loop
self.last_keypress_time = 0
self.min_keypress_interval = 0.05  # 50ms

while self.running:
    key = self.get_key()
    if not key:
        continue

    # v527 debouncing
    current_time = time.time()
    if current_time - self.last_keypress_time < self.min_keypress_interval:
        self.clear_input_buffer()
        continue
    self.last_keypress_time = current_time

    # ... handle key ...
```

- [ ] **Implement 50ms debouncing threshold**
  - **File:** `core/clients/tui/base.py` - run() method
  - **Why:** Smooth, responsive navigation without lag
  - **From:** v527/src/main.py lines 3206-3216
  - **Effort:** 1 hour
  - **Priority:** 🔴 CRITICAL

#### Selective Sidebar Redraw (Priority 1 - 10x Performance)

- [ ] **Implement fast sidebar update (2 lines instead of 30+)**
  - **File:** `core/clients/tui/components/sidebar.py`
  - **Why:** Current full redraw: 50ms, v527 selective: 5ms (10x faster)
  - **From:** v527/src/sidebar_fix.py
  - **Effort:** 3 hours
  - **Impact:** No flicker, 60fps smoothness
  - **Priority:** 🟠 HIGH
  - **Code Pattern:**
    ```python
    def update_selection_fast(self, old_index, new_index):
        """Only redraw 2 lines: previous + current"""
        # Clear previous highlight
        # Draw current highlight
        # No full sidebar redraw needed
    ```

#### Emoji-Safe String Handling (Priority 1)

- [ ] **Copy emoji_safe_slice.py module from v527**
  - **Source:** `archive/versions/.../unibos_v527_.../src/emoji_safe_slice.py`
  - **Destination:** `core/clients/tui/utils/emoji_safe_slice.py`
  - **Why:** Emoji breaks sidebar alignment (🦄 counts as 2 chars)
  - **Effort:** 30 minutes
  - **Priority:** 🟠 HIGH
  - **Usage:**
    ```python
    from core.clients.tui.utils.emoji_safe_slice import emoji_safe_slice
    safe_name = emoji_safe_slice(item.name, 22)  # Perfect fit
    ```

#### UX Enhancements (Priority 2)

- [ ] **Breadcrumb navigation in header**
  - **File:** `core/clients/tui/components/header.py`
  - **Why:** Users don't know current location
  - **From:** v527/src/main.py - get_navigation_breadcrumb()
  - **Effort:** 2 hours
  - **Display:** `🦄 unibos v534  ›  tools › version manager`
  - **Priority:** 🟢 MEDIUM

- [ ] **Terminal resize detection**
  - **File:** `core/clients/tui/base.py` - main loop
  - **Why:** Broken layout on window resize
  - **From:** v527/src/main.py lines 3177-3184
  - **Effort:** 1 hour
  - **Priority:** 🟢 MEDIUM

- [ ] **Copy submenu_handler.py for standardization**
  - **Source:** `archive/versions/.../unibos_v527_.../src/submenu_handler.py`
  - **Destination:** `core/clients/tui/framework/submenu.py`
  - **Why:** Consistent submenu entry/exit across all actions
  - **Effort:** 2 hours
  - **Priority:** 🟠 HIGH

**Phase 0.5.1 Success Metrics:**
- ✅ No ghost keypresses
- ✅ <10ms navigation response time
- ✅ No sidebar flicker
- ✅ Breadcrumb always visible in submenus
- ✅ Works correctly on terminal resize

---

### 0.5.2 WebSocket/ASGI Infrastructure 🔴 CRITICAL

**Status:** ENTIRELY MISSING in v534
**Impact:** All real-time features non-functional (currency rates, alerts, earthquake updates)
**From:** v532 analysis + v533 production
**Effort:** 3-4 days

#### Step 1: Install Dependencies

```bash
pip install channels==4.0.0
pip install channels-redis==4.1.0
pip install uvicorn[standard]==0.25.0
```

- [ ] **Install Channels and dependencies**
  - **Why:** Enable WebSocket support in Django
  - **Priority:** 🔴 CRITICAL
  - **Effort:** 10 minutes

#### Step 2: Configure ASGI Application

- [ ] **Update settings/base.py**
  - **Add:** `INSTALLED_APPS += ['channels']`
  - **Add:** `ASGI_APPLICATION = 'unibos_backend.asgi.application'`
  - **Add Channel Layers config:**
    ```python
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': ['redis://localhost:6379/0'],
                'capacity': 1500,
                'expiry': 10,
            },
        },
    }
    ```
  - **File:** `core/clients/web/unibos_backend/settings/base.py`
  - **Effort:** 30 minutes

- [ ] **Create/Update ASGI app**
  - **File:** `core/clients/web/unibos_backend/asgi.py`
  - **Source:** v532 asgi.py
  - **Add:** ProtocolTypeRouter with WebSocket support
  - **Code:**
    ```python
    from channels.routing import ProtocolTypeRouter, URLRouter
    from channels.auth import AuthMiddlewareStack

    application = ProtocolTypeRouter({
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter([
                # Module routes added here
            ])
        ),
    })
    ```
  - **Effort:** 1 hour

#### Step 3: Update Gunicorn Configuration

- [ ] **Change worker class to UvicornWorker**
  - **File:** `core/clients/web/gunicorn.conf.py`
  - **Change:** `worker_class = "uvicorn.workers.UvicornWorker"`
  - **Why:** Required for WebSocket support
  - **From:** v533 production config
  - **Effort:** 5 minutes

#### Step 4: Implement First WebSocket Consumer (Currencies)

- [ ] **Copy CurrencyRatesConsumer from v532**
  - **Source:** `archive/.../v532/.../apps/currencies/consumers.py` (20,778 bytes)
  - **Destination:** `modules/currencies/backend/consumers.py`
  - **Update imports:** `from apps.` → `from modules.currencies.backend.`
  - **Effort:** 2 hours
  - **Features:**
    - Real-time exchange rate updates
    - Subscription model (per currency pair)
    - Periodic updates (every 10 seconds)
    - JWT authentication
    - 20,778 bytes of production-tested code

- [ ] **Create routing configuration**
  - **File:** `modules/currencies/backend/routing.py`
  - **Add WebSocket URL patterns:**
    ```python
    from django.urls import path
    from . import consumers

    websocket_urlpatterns = [
        path('ws/currencies/rates/', consumers.CurrencyRatesConsumer.as_asgi()),
        path('ws/currencies/portfolio/', consumers.PortfolioConsumer.as_asgi()),
        path('ws/currencies/alerts/', consumers.CurrencyAlertsConsumer.as_asgi()),
    ]
    ```
  - **Effort:** 30 minutes

- [ ] **Update main ASGI routing**
  - **File:** `core/clients/web/unibos_backend/asgi.py`
  - **Import:** Module WebSocket routes
  - **Effort:** 15 minutes

#### Step 5: Testing

- [ ] **Test WebSocket connection**
  - **Command:** `gunicorn unibos_backend.asgi:application --bind 0.0.0.0:8000 --worker-class uvicorn.workers.UvicornWorker`
  - **Verify:** ASGI/HTTP in logs
  - **Test:** Connect via JavaScript WebSocket client
  - **Effort:** 1 hour

- [ ] **Test real-time currency updates**
  - **Test:** Subscribe to USD/TRY pair
  - **Verify:** Receive updates every 10 seconds
  - **Effort:** 30 minutes

**Phase 0.5.2 Deliverables:**
- ✅ Channels installed and configured
- ✅ ASGI application working
- ✅ Gunicorn using UvicornWorker
- ✅ At least 1 WebSocket consumer operational (currencies)
- ✅ Real-time updates tested and working

---

### 0.5.3 Celery Task Queue Deployment 🔴 CRITICAL

**Status:** NOT RUNNING even in production v533!
**Impact:** No background tasks executing (currency updates, earthquake data, alerts, cleanup)
**Scheduled Tasks:** 10 tasks defined but never run
**From:** v532 task definitions + v533 deployment needs
**Effort:** 2 days

#### Step 1: Create Systemd Services

- [ ] **Create celery-worker.service**
  - **File:** `/etc/systemd/system/celery-worker.service` (production)
  - **Template:**
    ```ini
    [Unit]
    Description=UNIBOS Celery Worker
    After=network.target redis.service postgresql.service

    [Service]
    Type=forking
    User=ubuntu
    Group=ubuntu
    WorkingDirectory=/home/ubuntu/unibos/core/clients/web
    Environment="PYTHONPATH=/home/ubuntu/unibos"
    Environment="DJANGO_SETTINGS_MODULE=unibos_backend.settings.production"
    ExecStart=/home/ubuntu/unibos/venv/bin/celery -A unibos_backend worker \
              --loglevel=info \
              --logfile=/home/ubuntu/unibos/logs/celery-worker.log \
              --pidfile=/home/ubuntu/unibos/run/celery-worker.pid \
              --detach

    ExecStop=/home/ubuntu/unibos/venv/bin/celery -A unibos_backend control shutdown
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```
  - **Effort:** 30 minutes
  - **Priority:** 🔴 CRITICAL

- [ ] **Create celerybeat.service**
  - **File:** `/etc/systemd/system/celerybeat.service` (production)
  - **Template:** Similar to worker but with `beat` command
  - **Effort:** 30 minutes
  - **Priority:** 🔴 CRITICAL

- [ ] **For local dev: Create launchd plist (macOS)**
  - **File:** `~/Library/LaunchAgents/com.unibos.celery-worker.plist`
  - **Effort:** 1 hour
  - **Priority:** 🟠 HIGH

#### Step 2: Copy Task Files from v532

- [ ] **Copy currencies tasks**
  - **Source:** `archive/.../v532/.../apps/currencies/tasks.py` (22,635 bytes)
  - **Destination:** `modules/currencies/backend/tasks.py`
  - **Tasks included:**
    - `update_exchange_rates` (every 30 min)
    - `import_firebase_rates_incremental` (every 5 min)
    - `check_currency_alerts` (every 5 min)
    - `calculate_portfolio_performance` (every 15 min)
    - `cleanup_old_bank_rates` (daily)
    - `generate_market_data` (hourly)
  - **Effort:** 2 hours
  - **Priority:** 🔴 CRITICAL

- [ ] **Copy birlikteyiz tasks**
  - **Source:** `archive/.../v532/.../apps/birlikteyiz/tasks.py`
  - **Destination:** `modules/birlikteyiz/backend/tasks.py`
  - **Tasks included:**
    - `fetch_earthquakes` (every 5 min)
  - **Effort:** 1 hour

- [ ] **Copy personal_inflation tasks**
  - **Source:** `archive/.../v532/.../apps/personal_inflation/tasks.py`
  - **Destination:** `modules/personal_inflation/backend/tasks.py`
  - **Tasks included:**
    - `calculate_inflation_rates` (daily)
  - **Effort:** 1 hour

- [ ] **Copy authentication tasks**
  - **Task:** `cleanup_expired_tokens` (daily)
  - **Effort:** 30 minutes

#### Step 3: Configure Celery Beat Schedule

- [ ] **Add CELERY_BEAT_SCHEDULE to settings/base.py**
  - **From:** v532 settings
  - **Code:**
    ```python
    from datetime import timedelta

    CELERY_BEAT_SCHEDULE = {
        'update-currency-rates': {
            'task': 'modules.currencies.backend.tasks.update_exchange_rates',
            'schedule': timedelta(minutes=30),
        },
        'import-firebase-rates-incremental': {
            'task': 'modules.currencies.backend.tasks.import_firebase_rates_incremental',
            'schedule': timedelta(minutes=5),
        },
        # ... (10 total tasks)
    }
    ```
  - **Effort:** 1 hour

#### Step 4: Deployment & Testing

- [ ] **Enable and start services (production)**
  - **Commands:**
    ```bash
    sudo systemctl enable celery-worker.service
    sudo systemctl enable celerybeat.service
    sudo systemctl start celery-worker.service
    sudo systemctl start celerybeat.service
    ```
  - **Effort:** 15 minutes

- [ ] **Verify tasks execute**
  - **Check logs:** `/home/ubuntu/unibos/logs/celery-worker.log`
  - **Monitor:** Task execution times
  - **Test:** Currency rates update
  - **Test:** Earthquake data fetch
  - **Effort:** 1 hour

**Phase 0.5.3 Deliverables:**
- ✅ celery-worker.service running
- ✅ celerybeat.service running
- ✅ All 10 scheduled tasks executing
- ✅ Currency rates updating every 30 min
- ✅ Earthquake data fetching every 5 min
- ✅ Alerts checking every 5 min
- ✅ Daily cleanup tasks running

---

### 0.5.4 Middleware Stack Implementation 🔴 CRITICAL

**Status:** 10 critical middleware missing
**Impact:** Security vulnerabilities, no monitoring, no rate limiting
**Current:** 10 basic Django middleware
**Target:** 20-item production-grade stack
**From:** v532 middleware.py (8,178 bytes) + middleware_activity.py (3,559 bytes)
**Effort:** 2 days

#### Step 1: Copy Middleware Files

- [ ] **Copy middleware.py from v532**
  - **Source:** `archive/.../v532/.../apps/common/middleware.py` (8,178 bytes)
  - **Destination:** `core/system/common/backend/middleware.py`
  - **Contains:**
    - SecurityHeadersMiddleware (CSP, X-Content-Type-Options, etc.)
    - RequestLoggingMiddleware (structured logging with timing)
    - RateLimitMiddleware (smart rate limiting with exemptions)
  - **Effort:** 30 minutes

- [ ] **Copy middleware_activity.py from v532**
  - **Source:** `archive/.../v532/.../apps/common/middleware_activity.py` (3,559 bytes)
  - **Destination:** `core/system/common/backend/middleware_activity.py`
  - **Contains:**
    - UserActivityMiddleware (user activity monitoring)
    - APIActivityMiddleware (API usage statistics)
  - **Effort:** 30 minutes

- [ ] **Update imports for v535 structure**
  - **Change:** `from apps.` → `from core.system.` or `from modules.`
  - **Test:** All imports resolve correctly
  - **Effort:** 1 hour

#### Step 2: Install Missing Dependencies

```bash
pip install django-prometheus==2.3.1
pip install whitenoise==6.6.0
pip install sentry-sdk==1.39.1
```

- [ ] **Install monitoring and serving packages**
  - **Effort:** 10 minutes

#### Step 3: Update MIDDLEWARE in settings/base.py

- [ ] **Add all 20 middleware items in correct order**
  - **File:** `core/clients/web/unibos_backend/settings/base.py`
  - **Order matters!** Entry point → Django core → Custom → Exit point
  - **Configuration:**
    ```python
    MIDDLEWARE = [
        # 1. Prometheus monitoring (entry point)
        'django_prometheus.middleware.PrometheusBeforeMiddleware',

        # 2-10. Django core middleware
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'corsheaders.middleware.CorsMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',

        # 11-19. Custom UNIBOS middleware
        'core.system.common.backend.middleware.SecurityHeadersMiddleware',
        'core.system.common.backend.middleware.RequestLoggingMiddleware',
        'core.system.common.backend.middleware.RateLimitMiddleware',
        'core.system.common.backend.middleware_activity.UserActivityMiddleware',
        'core.system.common.backend.middleware_activity.APIActivityMiddleware',
        # Add more as needed

        # 20. Prometheus monitoring (exit point)
        'django_prometheus.middleware.PrometheusAfterMiddleware',
    ]
    ```
  - **Effort:** 1 hour

#### Step 4: Configure Redis for Rate Limiting

- [ ] **Ensure Redis configured with connection pooling**
  - **Already in Phase 0.5.5** (Redis enhancement)
  - **Verify:** RateLimitMiddleware can access Redis
  - **Effort:** 30 minutes

#### Step 5: Testing

- [ ] **Test SecurityHeadersMiddleware**
  - **Check headers:** X-Content-Type-Options, X-Frame-Options, CSP
  - **Tool:** `curl -I https://localhost:8000/`
  - **Effort:** 30 minutes

- [ ] **Test RateLimitMiddleware**
  - **Test:** Make 1001 requests rapidly
  - **Verify:** 429 response after limit
  - **Check:** Different limits for authenticated vs anonymous
  - **Effort:** 1 hour

- [ ] **Test RequestLoggingMiddleware**
  - **Check logs:** Structured logging with request/response times
  - **Verify:** IP address, user agent, timing headers
  - **Effort:** 30 minutes

- [ ] **Monitor performance impact**
  - **Before:** Baseline response time
  - **After:** Measure overhead (should be <5ms)
  - **Effort:** 30 minutes

**Phase 0.5.4 Deliverables:**
- ✅ All 20 middleware active
- ✅ Security headers on all responses
- ✅ Rate limiting protecting API
- ✅ Request logging with timing
- ✅ Activity tracking operational
- ✅ Prometheus metrics exposed
- ✅ Performance overhead <5ms

---

### 0.5.5 Redis Configuration Enhancement 🟠 HIGH

**Status:** Basic configuration, missing optimizations
**Gap:** No compression, no pooling, database sessions (slow)
**From:** v532/v533 production config
**Impact:** 30-50% memory savings, faster sessions, connection exhaustion prevention
**Effort:** 2 hours

#### Update CACHES Configuration

- [ ] **Add advanced Redis configuration to settings/base.py**
  - **File:** `core/clients/web/unibos_backend/settings/base.py`
  - **Replace current CACHES with:**
    ```python
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 50,        # Connection pooling
                    'retry_on_timeout': True,     # Resilience
                },
                'SOCKET_CONNECT_TIMEOUT': 5,
                'SOCKET_TIMEOUT': 5,
                'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',  # Saves memory
                'IGNORE_EXCEPTIONS': True,        # Don't crash on Redis failure
            },
            'KEY_PREFIX': 'unibos',
            'TIMEOUT': 300,
        }
    }

    # Use Redis for sessions (not database)
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
    SESSION_COOKIE_AGE = 1209600  # 2 weeks
    ```
  - **Why:** 30-50% memory reduction, graceful degradation, faster sessions
  - **Effort:** 30 minutes

#### Install Django-Redis Compressor

```bash
pip install django-redis==5.4.0
```

- [ ] **Install django-redis with zlib support**
  - **Effort:** 5 minutes

#### Testing

- [ ] **Verify compression working**
  - **Check:** Redis memory usage before/after
  - **Tool:** `redis-cli INFO memory`
  - **Expected:** 30-50% reduction
  - **Effort:** 30 minutes

- [ ] **Test failover behavior**
  - **Stop Redis:** `sudo systemctl stop redis`
  - **Verify:** Django still works (IGNORE_EXCEPTIONS)
  - **Check logs:** Warning logged but no crash
  - **Restart Redis:** `sudo systemctl start redis`
  - **Effort:** 30 minutes

- [ ] **Test session performance**
  - **Before:** Database session queries
  - **After:** No DB queries for sessions
  - **Measure:** Response time improvement
  - **Effort:** 30 minutes

**Phase 0.5.5 Deliverables:**
- ✅ Redis compression enabled (30-50% memory savings)
- ✅ Connection pooling (max 50 connections)
- ✅ Sessions in Redis (not database)
- ✅ Graceful degradation if Redis fails
- ✅ Channels backend using Redis

---

### 0.5.6 PYTHONPATH & Settings Consolidation 🟠 HIGH

**Status:** Inconsistent path resolution
**Issue:** v533 production uses different depth than v534 local
**Impact:** Import errors when deploying v534 to production
**From:** v533 production analysis
**Effort:** 1 day

#### Analyze Path Resolution Differences

- [ ] **Document current path structures**
  - **v533 Production:**
    - `PYTHONPATH=/home/ubuntu/unibos/core/web:/home/ubuntu/unibos`
    - Settings path: `parent.parent.parent.parent.parent` (5 levels)
  - **v534 Local:**
    - `PYTHONPATH=/Users/berkhatirli/Desktop/unibos-dev`
    - Settings path: Different due to `clients/` layer
  - **Document:** Path resolution for imports
  - **Effort:** 2 hours

#### Standardize Settings Files

- [ ] **Compare v532 base.py with current base.py**
  - **v532:** 19,892 bytes
  - **Current:** Smaller, missing configurations
  - **Copy from v532:**
    ```bash
    scp rocksteady:/home/ubuntu/unibos.old.../settings/base.py /tmp/v532_base.py
    ```
  - **Merge:** Middleware, INSTALLED_APPS, CACHES, DATABASES configs
  - **Effort:** 4 hours

- [ ] **Update production.py settings**
  - **Add from v532:**
    - `CSRF_TRUSTED_ORIGINS = ['https://recaria.org', 'https://www.recaria.org']`
    - Email backend configuration (mail.recaria.org)
    - Security settings for production
    - Sentry DSN configuration
  - **Effort:** 2 hours

- [ ] **Standardize PYTHONPATH across environments**
  - **Create:** `.env.example` with clear PYTHONPATH documentation
  - **Update:** All systemd service files
  - **Update:** gunicorn.conf.py if needed
  - **Test:** All imports work in all environments
  - **Effort:** 2 hours

#### Testing

- [ ] **Test Django server startup**
  - **Command:** `python manage.py check`
  - **Command:** `python manage.py check --deploy`
  - **Verify:** All checks pass
  - **Effort:** 30 minutes

- [ ] **Test all module imports**
  - **Script:** Import each module's models, views, serializers
  - **Verify:** No ImportError
  - **Effort:** 1 hour

**Phase 0.5.6 Deliverables:**
- ✅ PYTHONPATH standardized across all environments
- ✅ Settings files consolidated with v532 production settings
- ✅ Django server starts cleanly
- ✅ All modules import successfully
- ✅ Deployment to production works without import errors

---

### 0.5.7 Archive Protection System ✅ COMPLETED

- [x] **Create:** `docs/ARCHIVE_PROTECTION_RULES.md`
- [x] **Create:** `tools/archive_daily_check.sh`
- [ ] **CRITICAL ISSUE:** Archive in `.gitignore`
  - [ ] Decision: Keep in git or external backup?
  - [ ] If git: Remove from .gitignore
  - [ ] If external: Setup robust backup system
  - [ ] Document decision in ARCHIVE_PROTECTION_RULES.md
- [ ] **Setup:** Daily archive verification
  - [ ] Add to cron or launchd
  - [ ] Alert on anomalies
  - [ ] Automated backup to external storage

---

### 0.5.8 Dependencies Installation 🟢 MEDIUM

**From:** v532 package analysis
**Missing packages:** 11 critical packages + OCR stack

#### Install Missing Core Packages

```bash
pip install django-cachalot==2.6.1      # Automatic query caching
pip install django-crontab==0.7.1       # Cron job scheduling (alternative to Celery Beat)
pip install marshmallow==3.20.2         # Advanced serialization
pip install sentry-sdk==1.39.1          # Error tracking
pip install user-agents==2.2.0          # User agent parsing
pip install python-decouple==3.8        # Settings management
pip install django-prometheus==2.3.1    # Monitoring metrics
pip install whitenoise==6.6.0           # Static file serving
pip install drf-spectacular==0.27.0     # API documentation
```

- [ ] **Install all missing packages**
  - **Priority:** HIGH for production
  - **Effort:** 30 minutes

#### OCR Stack (Optional - for Documents module)

```bash
# Advanced OCR engines (v532 has 11 engines)
pip install paddleocr==3.3.1
pip install paddlepaddle==2.6.2         # ARM64 support
pip install torch==2.6.0
pip install torchvision==0.21.0
pip install transformers==4.57.1
pip install easyocr==1.7.2
pip install surya-ocr==0.9.0
pip install python-doctr[torch]==0.9.0
```

- [ ] **Install OCR packages (when working on Documents module)**
  - **Priority:** MEDIUM
  - **Effort:** 1 hour (large downloads)
  - **Note:** Defer to Phase 2 if needed

---

## PHASE 0.5 COMPLETION CRITERIA

**Target Completion:** 2025-11-30 (2 weeks from now)

**Must Have (Minimum Viable):**
- ✅ TUI triple-flush and debouncing implemented (no ghost keys)
- ✅ WebSocket/Channels working for at least 1 module (currencies)
- ✅ Celery worker and beat running with all 10 tasks
- ✅ 20-item middleware stack active
- ✅ Redis optimized with compression
- ✅ Django server starts cleanly with production settings

**Should Have:**
- ✅ Fast sidebar redraw implemented
- ✅ Breadcrumb navigation in TUI
- ✅ emoji_safe_slice module integrated
- ✅ PYTHONPATH standardized
- ✅ Settings files consolidated

**Nice to Have:**
- Terminal resize detection
- Submenu handler standardization
- OCR stack installed

**Success Metrics:**
- Zero ghost keypresses in TUI
- WebSocket real-time updates <1s latency
- All 10 Celery tasks executing on schedule
- Middleware overhead <5ms
- Redis memory usage reduced by 30-50%

---

## 📋 PHASE 1: CLI Separation & Platform Foundation

### ✅ 1.1 CLI Restructuring (COMPLETED - 2025-11-15)

- [x] Renamed `core/cli/` → `core/cli_dev/`
- [x] Created `core/cli/` (Production CLI)
- [x] Created `core/cli_server/` (Server CLI)
- [x] Setup files for all three CLIs
- [x] Testing completed

**Results:**
- 3 separate CLIs successfully created
- Security model applied (dev/server CLIs don't go to production)
- All CLIs tested and working
- Documentation: `docs/development/cli/three-tier-architecture.md`

---

### ✅ 1.2 Platform Detection Foundation (COMPLETED - 2025-11-15)

- [x] Created `core/platform/detector.py`
- [x] CLI integration for both unibos and unibos-dev
- [x] Platform detection working

**Results:**
- Platform detection system successfully created
- psutil integration with detailed system info
- Raspberry Pi special detection working
- `platform` command active in both CLIs

---

### 1.3 Service Management & Node Identity 🔄 IN PROGRESS

**Goal:** Per-platform service management and unique node identity
**Duration:** 1 week
**Priority:** HIGH

#### Service Manager Implementation

- [ ] **Create:** `core/platform/service_manager.py`
  - [ ] Abstraction layer for service management
  - [ ] systemd support (Linux/Raspberry Pi)
  - [ ] launchd support (macOS)
  - [ ] Windows Services support (Windows)
  - [ ] Supervisor fallback
  - **Effort:** 1 week
  - **Priority:** 🟠 HIGH

- [ ] **CLI Integration:**
  - [ ] `unibos service start` → Start all UNIBOS services
  - [ ] `unibos service stop` → Stop all services
  - [ ] `unibos service status` → Show service status
  - [ ] `unibos-server service restart` → Restart services on server
  - **Effort:** 2 days

#### Node Identity & Persistence

- [ ] **Extend:** `core/instance/identity.py`
  - [ ] UUID persistence (save to `data/core/node.uuid`)
  - [ ] Node type detection (central, local, edge)
  - [ ] Platform integration (use PlatformInfo)
  - [ ] Capability declaration (modules, hardware, services)
  - [ ] Registration method (register with central server)
  - **Effort:** 3 days

- [ ] **Create:** Django app `core/system/nodes/`
  - [ ] Models: `Node`, `NodeCapability`, `NodeStatus`
  - [ ] API: `/api/nodes/register`, `/api/nodes/list`, `/api/nodes/<uuid>/`
  - [ ] Admin interface
  - [ ] WebSocket for real-time status updates
  - **Effort:** 1 week

- [ ] **CLI Commands:**
  - [ ] `unibos node info` → Show this node's identity
  - [ ] `unibos node register <central-url>` → Register with central
  - [ ] `unibos node peers` → List known peers
  - [ ] `unibos-server nodes list` → List all registered nodes (central only)

---

## 📋 PHASE 2: Module System Enhancement (Week 5-6)

### 2.1 Module Metadata (JSON)

**Goal:** Standardize module metadata and dynamic loading
**Duration:** 1 week

- [ ] **Create template:** `module.json` schema
  ```json
  {
    "name": "string",
    "version": "semver",
    "description": "string",
    "author": "string",
    "license": "string",
    "category": "emergency|finance|media|iot|game",
    "dependencies": {
      "core": ">=version",
      "modules": ["module_name"]
    },
    "capabilities": {
      "requires_lora": false,
      "requires_gps": false,
      "requires_camera": false,
      "offline_capable": true,
      "p2p_enabled": false
    },
    "platforms": ["linux", "macos", "windows", "raspberry_pi"],
    "entry_points": {
      "backend": "modules.name.backend",
      "cli": "modules.name.cli",
      "mobile": "modules.name.mobile"
    }
  }
  ```

- [ ] **Add to all 13 modules:**
  - [ ] birlikteyiz/module.json
  - [ ] cctv/module.json
  - [ ] currencies/module.json
  - [ ] documents/module.json
  - [ ] movies/module.json
  - [ ] music/module.json
  - [ ] personal_inflation/module.json
  - [ ] recaria/module.json (MMORPG game, Ultima Online inspired)
  - [ ] restopos/module.json
  - [ ] solitaire/module.json
  - [ ] store/module.json
  - [ ] wimm/module.json
  - [ ] wims/module.json

- [ ] **Create:** `core/system/modules/registry.py`
  - [ ] Auto-discovery (scan `modules/*/module.json`)
  - [ ] Dependency resolution
  - [ ] Platform compatibility check
  - [ ] Capability matching
  - [ ] Dynamic INSTALLED_APPS generation

- [ ] **CLI Commands:**
  - [ ] `unibos module list` → List all modules
  - [ ] `unibos module info <name>` → Show module details
  - [ ] `unibos module enable <name>` → Enable module
  - [ ] `unibos module disable <name>` → Disable module
  - [ ] `unibos-dev module create <name>` → Create new module template

---

### 2.2 Critical Module Features (from v532 analysis)

#### Currencies Module WebSocket Consumers

- [ ] **Implement PortfolioConsumer**
  - **Source:** v532 consumers.py
  - **Features:**
    - Real-time portfolio value tracking
    - Ownership verification
    - Automatic updates (every 30 seconds)
    - Holdings with profit/loss calculation
  - **Effort:** 1 day

- [ ] **Implement CurrencyAlertsConsumer**
  - **Source:** v532 consumers.py
  - **Features:**
    - Price alert notifications
    - Alert creation/deletion via WebSocket
    - Triggered by Celery tasks
    - User-specific rooms
  - **Effort:** 1 day

#### Documents Module - Multi-OCR Engine Support

- [ ] **Copy ocr_service.py from v532**
  - **Source:** `archive/.../v532/.../apps/documents/ocr_service.py` (55,651 bytes!)
  - **Destination:** `modules/documents/backend/ocr_service.py`
  - **Features:**
    - 11 OCR engines (Tesseract, PaddleOCR, TrOCR, Donut, etc.)
    - Quality-based routing
    - Confidence scoring
    - Batch processing (50-100 documents)
  - **Effort:** 2 days

- [ ] **Add confidence tracking to Document model**
  - **Fields:** `ocr_engine`, `confidence_score`
  - **Migration:** Create and run
  - **Effort:** 2 hours

- [ ] **Implement receipt parsing for Turkish stores**
  - **Source:** v532 parsers/receipt_parser.py
  - **Integration:** With personal_inflation module
  - **Effort:** 1 day

#### Birlikteyiz Module - Real-Time Features

- [ ] **EMSC WebSocket integration**
  - **Source:** v532 has systemd service for EMSC WebSocket
  - **Features:** Real-time earthquake alerts from EMSC
  - **Effort:** 2 days

- [ ] **Enhanced interactive map**
  - **Features:** Leaflet.js with clustering, source filtering
  - **Effort:** 1 day

---

### 2.3 Service Layer Architecture (from v532 pattern)

**Goal:** Extract business logic from views into service layer
**Benefits:** Testability, reusability, separation of concerns
**From:** v532 services.py pattern
**Effort:** 1 week across all modules

#### Create Service Layer Template

```python
# modules/{module}/backend/services.py

class {Module}Service:
    """Encapsulates all {module}-related business logic"""

    def __init__(self):
        self.external_service = ExternalAPIService()
        self.cache_manager = CacheManager()

    def get_data(self, filters: Dict) -> List:
        """Business logic with caching"""
        # 1. Check cache
        # 2. Query database
        # 3. Cache result
        # 4. Return
        pass

    def create_item(self, user, data: Dict) -> Model:
        """Create with validation"""
        # 1. Validate
        # 2. Create
        # 3. Invalidate cache
        # 4. Trigger async tasks
        # 5. Return
        pass
```

- [ ] **Create CurrencyService**
  - **Source:** v532 currencies/services.py (22,240 bytes)
  - **Effort:** 1 day

- [ ] **Create DocumentService**
  - **Features:** OCR orchestration, AI enhancement
  - **Effort:** 1 day

- [ ] **Create service layer for other modules as needed**
  - **Effort:** 3 days

---

## 📋 PHASE 3: P2P Network Foundation (Week 7-8)

**Goal:** Implement Hybrid P2P approach (mDNS + REST + WebSocket + WebRTC future)
**Architecture:** Local discovery + Central registry + Real-time messaging

### 3.1 Local Network Discovery (mDNS/Zeroconf)

- [ ] **Install:** `pip install zeroconf`

- [ ] **Create:** `core/p2p/discovery.py`
  - [ ] `NodeDiscovery` class
  - [ ] Advertise this node (`_unibos._tcp.local.`)
  - [ ] Scan for other nodes
  - [ ] Callback handlers (on_service_added, on_service_removed)
  - [ ] Maintain peer list
  - **Effort:** 2 days

- [ ] **CLI Commands:**
  - [ ] `unibos network scan` → Scan local network for nodes
  - [ ] `unibos network advertise` → Start advertising this node

- [ ] **Test:**
  - [ ] Test with 2 nodes on same WiFi
  - [ ] Verify auto-discovery works
  - [ ] Verify peer list updates

---

### 3.2 Central Registry (REST API)

**Already defined in Phase 1.3 Node Identity**

- [ ] **API Endpoints:**
  - [ ] POST `/api/nodes/register` → Register node
  - [ ] GET `/api/nodes/list` → List all nodes
  - [ ] GET `/api/nodes/<uuid>/` → Node details
  - [ ] PUT `/api/nodes/<uuid>/heartbeat` → Update last_seen
  - [ ] DELETE `/api/nodes/<uuid>/` → Unregister

- [ ] **Heartbeat System:**
  - [ ] Celery beat task (every 60s)
  - [ ] Send heartbeat to central server
  - [ ] Mark nodes offline if no heartbeat >5min

---

### 3.3 Real-Time Communication (WebSocket)

- [ ] **Create:** `core/p2p/consumers.py`
  - [ ] WebSocket consumer for node-to-node messaging
  - [ ] Routing: `/ws/p2p/<node_uuid>/`
  - [ ] Message types: ping, data, command, status
  - **Effort:** 2 days

- [ ] **Node-to-Node Communication:**
  - [ ] Direct connection (if local network)
  - [ ] Relay via central (if internet only)
  - **Effort:** 1 day

**Message Format:**
```json
{
  "type": "ping",
  "from": "node-uuid-123",
  "to": "node-uuid-456",
  "timestamp": "2025-11-15T12:00:00Z"
}
```

---

### 3.4 WebRTC (Future - Phase 4+)

**Deferred to later phase**

- [ ] Research `aiortc` library
- [ ] STUN/TURN server setup
- [ ] Signaling server (via Rocksteady)
- [ ] Use case: Remote CCTV streaming

---

## 📋 PHASE 4: Deployment & Production Features (Week 9-10)

### 4.1 Environment-Specific Settings

- [ ] **Create:** `core/clients/web/unibos_backend/settings/targets/`
  - [ ] `raspberry_pi.py` → Lightweight, edge device
  - [ ] `central_server.py` → Full features, orchestrator
  - [ ] `local_desktop.py` → User-selected modules

**Example raspberry_pi.py:**
```python
from ..base import *

DEBUG = False
ALLOWED_HOSTS = ['*']  # Local network

# Minimal modules
ENABLED_MODULES = ['birlikteyiz', 'cctv', 'wimm']

# Hardware-specific
BIRLIKTEYIZ_LORA_ENABLED = True
CCTV_CAMERA_DEVICE = '/dev/video0'

# Performance
DATABASES['default']['CONN_MAX_AGE'] = 0
CELERY_WORKER_CONCURRENCY = 2
```

---

### 4.2 Administration Module (from v532) 🔴 CRITICAL for Enterprise

**Status:** ENTIRELY MISSING in v534
**From:** v532 has complete implementation (15+ files)
**Effort:** 1 week

- [ ] **Copy entire administration module from v532**
  - **Source:** `archive/.../v532/.../apps/administration/`
  - **Destination:** `core/system/administration/`
  - **Effort:** 1 day

- [ ] **Database Models:**
  - [ ] Role (8 system roles: Super Admin, Admin, Manager, etc.)
  - [ ] Department (IT, HR, Finance, Operations)
  - [ ] AuditLog (complete action tracking)
  - [ ] SystemSetting (configurable parameters)
  - [ ] PermissionGroup

- [ ] **Run migrations and create defaults**
  - [ ] Create 8 default roles
  - [ ] Create department structure
  - [ ] Setup admin interface
  - **Effort:** 1 day

- [ ] **Test RBAC permissions**
  - [ ] User assignment to roles
  - [ ] Permission enforcement
  - [ ] Audit logging
  - **Effort:** 1 day

---

### 4.3 Advanced Security Features (from v532)

- [ ] **Copy authentication validators from v532**
  - **Source:** v532 authentication/validators.py
  - **Features:**
    - Uppercase/lowercase/digit/special char requirements
    - Common pattern detection (12345, qwerty)
    - Sequential character detection
    - User-specific checks (no username in password)
  - **Effort:** 1 hour

- [ ] **Implement custom exception handler**
  - **Source:** v532 common/exceptions.py
  - **Features:** Structured error responses with logging
  - **Effort:** 1 hour

- [ ] **Configure Sentry error tracking**
  - **Install:** `sentry-sdk==1.39.1`
  - **Configure:** In settings/production.py
  - **Effort:** 30 minutes

---

### 4.4 Deployment Implementations

- [ ] **Local Production Deployment:**
  - [ ] `unibos-dev deploy local` command
  - [ ] Target: `/Users/berkhatirli/Applications/unibos/`
  - [ ] Use rsync with `.prodignore`
  - [ ] Setup launchd service (macOS)
  - **Effort:** 2 days

- [ ] **Raspberry Pi Deployment:**
  - [ ] `unibos-dev deploy raspberry <ip>` command
  - [ ] SSH deployment
  - [ ] Platform-specific setup script
  - [ ] systemd service installation
  - **Effort:** 3 days

- [ ] **Rocksteady Deployment Enhancement:**
  - [ ] Already works, integrate with CLI
  - [ ] Add rollback support
  - [ ] Health checks post-deployment
  - **Effort:** 1 day

---

## 📋 PHASE 5: Raspberry Pi Hardware Integration (Week 11-12)

### 5.1 Birlikteyiz - LoRa Mesh Network

**Priority:** HIGH (Emergency network proof-of-concept)

- [ ] **Hardware:**
  - [ ] LoRa module (SX1276/SX1278, 868MHz EU)
  - [ ] GPS module (NEO-6M)
  - [ ] Test on Raspberry Pi Zero 2 W

- [ ] **Software:**
  - [ ] Python LoRa library (pyLoRa or CircuitPython)
  - [ ] GPS library (gpsd)
  - [ ] Mesh protocol implementation
  - [ ] Message relay algorithm
  - [ ] Deduplication logic

- [ ] **Integration:**
  - [ ] `modules/birlikteyiz/backend/lora_gateway.py`
  - [ ] Celery task for message processing
  - [ ] WebSocket for real-time updates

- [ ] **Test:**
  - [ ] 2-node mesh test (send message A→B)
  - [ ] 3-node relay test (A→B→C)
  - [ ] Offline queue test

---

### 5.2 CCTV - Camera Monitoring

- [ ] **Hardware:**
  - [ ] USB camera or Pi Camera Module
  - [ ] Test on Raspberry Pi 4

- [ ] **Software:**
  - [ ] OpenCV for camera access
  - [ ] Motion detection
  - [ ] Video recording (H.264)
  - [ ] Thumbnail generation

- [ ] **Integration:**
  - [ ] `modules/cctv/backend/camera_manager.py`
  - [ ] Stream via WebSocket (for live view)
  - [ ] Future: WebRTC for remote access

---

## 📋 PHASE 6+: Future Enhancements

### Offline Mode & Sync
- [ ] Offline detection
- [ ] Operation queue
- [ ] CRDT-based conflict resolution
- [ ] Sync engine

### Module Marketplace
- [ ] Module package format (.zip with module.json)
- [ ] Installation mechanism
- [ ] Marketplace server
- [ ] Security scanning

### Multi-Platform Installers
- [ ] macOS: .dmg or Homebrew formula
- [ ] Linux: .deb and .rpm packages
- [ ] Windows: .exe installer
- [ ] Raspberry Pi: Custom OS image

---

## 📊 IMPLEMENTATION GUIDES

### Code Pattern: Advanced Celery Task (from v532)

```python
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def import_firebase_rates_incremental(self):
    """Production-grade import with all best practices"""

    # 1. Create import log for tracking
    import_log = BankRateImportLog.objects.create(
        import_type='scheduled',
        source_url=FIREBASE_URL,
        status='in_progress'
    )

    try:
        # 2. Fetch data with timeout
        response = requests.get(FIREBASE_URL, timeout=30)
        response.raise_for_status()
        data = response.json()

        # 3. Get existing IDs in ONE query (performance)
        existing_ids = set(BankExchangeRate.objects.values_list('entry_id', flat=True))

        # 4. Bulk insert with statistics tracking
        batch = []
        batch_size = 100
        stats = {'total': 0, 'new': 0, 'updated': 0, 'failed': 0}

        for entry_id, entry_data in data.items():
            if self._validate_entry(entry_data):
                batch.append(self._process_entry(entry_id, entry_data))
                stats['new'] += 1

            if len(batch) >= batch_size:
                with transaction.atomic():
                    BankExchangeRate.objects.bulk_create(batch, batch_size=50)
                batch = []

        # 5. Update import log with statistics
        import_log.status = 'completed'
        import_log.new_entries = stats['new']
        import_log.completed_at = timezone.now()
        import_log.save()

        # 6. Cache invalidation on new data
        if stats['new'] > 0:
            cache.delete('bank_rates:latest')
            cache.delete_pattern('bank_rates:chart:*')

            # 7. Notify via WebSocket
            notify_new_bank_rates.delay(stats['new'])

        return {'status': 'success', 'stats': stats}

    except Exception as e:
        import_log.status = 'failed'
        import_log.error_message = str(e)
        import_log.save()
        raise self.retry(exc=e)
```

**Key Lessons:**
1. Always track import statistics
2. Use bulk operations for performance
3. Implement incremental updates
4. Add proper error handling
5. Invalidate caches on data changes
6. Notify users of updates via WebSocket

---

### Code Pattern: WebSocket Consumer (from v532)

```python
class CurrencyRatesConsumer(AsyncJsonWebsocketConsumer):
    """Production-ready WebSocket with subscription model"""

    async def connect(self):
        # 1. Authentication
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        # 2. Join room
        self.room_group_name = "currency_rates"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # 3. Accept connection
        await self.accept()

        # 4. Send initial data
        await self.send_initial_rates()

        # 5. Start periodic updates
        self.update_task = asyncio.create_task(
            self.periodic_rate_update()
        )

    async def periodic_rate_update(self):
        """Send updates every 10 seconds"""
        while True:
            try:
                await asyncio.sleep(10)

                subscriptions = self.scope.get('subscriptions', set())
                updates = {}

                for pair in subscriptions:
                    rate = await self.get_currency_pair_rate(pair)
                    if rate:
                        updates[pair] = rate

                if updates:
                    await self.send_json({
                        'type': 'rate_updates',
                        'data': updates,
                        'timestamp': timezone.now().isoformat()
                    })
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Update error: {e}")
                await asyncio.sleep(30)

    @database_sync_to_async
    def get_currency_pair_rate(self, pair):
        """Fetch rate from database with caching"""
        cache_key = f'rate_{pair}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        # ... fetch from database, cache, return ...
```

**Key Lessons:**
1. Always authenticate WebSocket connections
2. Use subscription model (don't send everything)
3. Implement periodic updates with asyncio
4. Cache database queries
5. Graceful error handling
6. Clean up on disconnect

---

### Code Pattern: Query Optimization (from v532)

```python
# 1. Prefetch related objects
portfolios = Portfolio.objects.prefetch_related(
    'holdings__currency',
    'holdings__currency__exchange_rates'
).select_related('user')

# 2. Annotate for aggregations
holdings = PortfolioHolding.objects.annotate(
    current_value=F('amount') * F('currency__latest_rate')
)

# 3. Values for lightweight queries
rates_summary = ExchangeRate.objects.values(
    'base_currency__code'
).annotate(
    avg_rate=Avg('rate'),
    count=Count('id')
)

# 4. Bulk operations
ExchangeRate.objects.bulk_create(batch, batch_size=100)
ExchangeRate.objects.bulk_update(rates, fields=['rate'], batch_size=100)
```

---

## 📅 WEEKLY MILESTONES

### Week 1-2: Phase 0.5 - Critical Infrastructure
- ✅ TUI bug fixes (ghost keys, debouncing, fast sidebar)
- ✅ WebSocket/Channels operational
- ✅ Celery deployed and running
- ✅ Middleware stack complete
- ✅ Redis optimized

### Week 3-4: Phase 1 Completion - CLI & Platform
- ✅ Service management (systemd/launchd)
- ✅ Node identity and registration
- ✅ Platform-specific configurations

### Week 5-6: Phase 2 - Module Enhancement
- ✅ Module metadata (JSON)
- ✅ Currencies module WebSocket consumers
- ✅ Documents multi-OCR
- ✅ Service layer architecture

### Week 7-8: Phase 3 - P2P Foundation
- ✅ mDNS local discovery
- ✅ Central registry API
- ✅ Node-to-node WebSocket messaging

### Week 9-10: Phase 4 - Production Features
- ✅ Administration module
- ✅ Advanced security
- ✅ Deployment automation

### Week 11-12: Phase 5 - Hardware & Polish
- ✅ Raspberry Pi LoRa mesh
- ✅ CCTV camera integration
- ✅ Documentation and testing

---

## 📌 RULES & CONVENTIONS

### TODO Management
1. **Main directory has only this file** (`TODO.md`)
2. **During updates:**
   - Completed tasks → `✅` mark and move to "COMPLETED" section
   - Abandoned tasks → Delete or archive with "ABANDONED" note
   - Changed priorities → Re-order
   - New details → Add to relevant section
3. **Completed phases** → `archive/planning/completed/phase-N.md`
4. **Weekly review:** Completed tasks archived, new tasks added
5. **Atomic commits:** TODO + related code/docs committed together

### Commit Convention
```bash
git add TODO.md modules/currencies/backend/consumers.py
git commit -m "feat(currencies): implement WebSocket real-time rates

- Added CurrencyRatesConsumer from v532
- Updated TODO.md Phase 0.5.2 progress
- Supports subscription model for currency pairs

Refs: TODO.md Phase 0.5.2"
```

### Todo Review Checklist
- [ ] Completed tasks marked?
- [ ] Abandoned tasks deleted/noted?
- [ ] New tasks added?
- [ ] Priorities updated?
- [ ] Dates correct?
- [ ] Links/refs complete?
- [ ] Sections organized?

---

## 📅 WEEKLY REVIEW SCHEDULE

**Every Monday:**
1. Archive last week's completed tasks
2. Set this week's priorities
3. Identify blockers

**Every Friday:**
1. Weekly progress summary
2. Next week planning
3. Risk assessment

---

## 📊 CURRENT STATUS

**Completed Phases:**
- ✅ Phase 0: CLI Tool (2025-11-13)
- ✅ Phase 0: Module Path Migration (2025-11-13)
- ✅ Phase 1.1: CLI Restructuring (2025-11-15)
- ✅ Phase 1.2: Platform Detection (2025-11-15)

**Active Phase:**
- 🔄 Phase 0.5: Critical Fixes & Production Parity (started 2025-11-16)

**Next Phases:**
- 📋 Phase 1.3: Service Management & Node Identity
- 📋 Phase 2: Module System Enhancement
- 📋 Phase 3: P2P Network Foundation

---

## 🎯 DECISIONS & NOTES

### Architecture Decisions (2025-11-15)
- ✅ **Three-tier CLI:** unibos, unibos-dev, unibos-server
- ✅ **psutil:** Platform detection and monitoring
- ✅ **JSON metadata:** For module.json (not YAML)
- ✅ **Hybrid P2P:** mDNS + REST + WebSocket + WebRTC (future)

### Critical Findings from Archive Analysis (2025-11-16)
- 🚨 **WebSocket ENTIRELY MISSING:** Must implement immediately
- 🚨 **Celery NOT RUNNING:** Even in production! Critical gap
- 🚨 **v527 TUI patterns LOST:** Ghost key bug, flicker, navigation issues
- ✅ **v535 architecture BETTER:** Profile-based, modular design superior to v532 monolith
- ⚠️ **Feature gap ~65%:** But achievable in 12 weeks

### Module Corrections (2025-11-15)
- ✅ **Recaria:** MMORPG game project (Ultima Online inspired), not yet started

### Platform Priorities (2025-11-15)
- 🔴 **Phase 1:** Raspberry Pi + Birlikteyiz (LoRa mesh) - Emergency network PoC
- 🟡 **Phase 2:** CCTV camera monitoring
- 🟢 **Phase 3:** Full home server (all modules)

---

## APPENDIX A: FILE LOCATIONS (v527/v532 Archive)

### Critical Files to Copy from v527 (TUI Patterns)

```
archive/versions/old_pattern_v001_v533/unibos_v527_20251102_0644/src/

Essential (copy these):
├── emoji_safe_slice.py (119 lines) → core/clients/tui/utils/
└── submenu_handler.py (133 lines) → core/clients/tui/framework/

Reference (study patterns):
├── sidebar_fix.py (268 lines) - Fast sidebar update pattern
├── main.py (8,125 lines) - Main event loop patterns
└── administration_menu.py - Specialized menu template
```

### Critical Files to Copy from v532 (Backend Features)

```
archive/versions/old_pattern_v001_v533/unibos_v532_20251109_1435/

High Priority (Week 1-2):
├── apps/common/middleware.py (8,178 bytes) → core/system/common/backend/
├── apps/common/middleware_activity.py (3,559 bytes) → core/system/common/backend/
├── apps/common/exceptions.py → core/system/common/backend/
├── unibos_backend/settings/base.py (19,892 bytes) - for comparison
├── unibos_backend/asgi.py → core/clients/web/unibos_backend/
└── gunicorn.conf.py → core/clients/web/

Medium Priority (Week 3-4):
├── apps/currencies/consumers.py (20,778 bytes) → modules/currencies/backend/
├── apps/currencies/tasks.py (22,635 bytes) → modules/currencies/backend/
├── apps/currencies/services.py (22,240 bytes) → modules/currencies/backend/
├── apps/documents/ocr_service.py (55,651 bytes) → modules/documents/backend/
└── apps/birlikteyiz/consumers.py → modules/birlikteyiz/backend/

Lower Priority (Week 5+):
└── apps/administration/ (entire module) → core/system/administration/
```

---

## APPENDIX B: MIGRATION COMMANDS

### Copy Files from Archive

```bash
# TUI patterns from v527
cp archive/versions/.../unibos_v527_20251102_0644/src/emoji_safe_slice.py \
   core/clients/tui/utils/

cp archive/versions/.../unibos_v527_20251102_0644/src/submenu_handler.py \
   core/clients/tui/framework/

# Middleware from v532
cp archive/versions/.../unibos_v532_20251109_1435/apps/common/middleware*.py \
   core/system/common/backend/

# WebSocket consumers from v532
cp archive/versions/.../unibos_v532_20251109_1435/apps/currencies/consumers.py \
   modules/currencies/backend/

# Celery tasks from v532
cp archive/versions/.../unibos_v532_20251109_1435/apps/currencies/tasks.py \
   modules/currencies/backend/
```

### Update Imports in Copied Files

```bash
# Update import paths for v535 structure
sed -i 's/from apps\./from core.system./g' core/system/common/backend/middleware.py
sed -i 's/from apps\./from modules./g' modules/currencies/backend/consumers.py
```

### Deploy to Production (Rocksteady)

```bash
# From local dev
./tools/deployment/deploy_to_rocksteady.sh

# On Rocksteady
cd /home/ubuntu/unibos/core/clients/web
python manage.py migrate --no-input
python manage.py collectstatic --no-input
sudo systemctl restart gunicorn
sudo systemctl restart celery-worker
sudo systemctl restart celerybeat

# Health check
curl https://recaria.org/health/
```

---

## APPENDIX C: TECHNOLOGY STACK

### Core Dependencies (Current + Missing)

| Package | Version | Status | Priority |
|---------|---------|--------|----------|
| **Django** | 5.1+ | ✅ Present | - |
| **Django REST Framework** | Latest | ✅ Present | - |
| **Channels** | 4.0.0 | ❌ Missing | 🔴 CRITICAL |
| **Channels-Redis** | 4.1.0 | ❌ Missing | 🔴 CRITICAL |
| **Celery** | 5.3+ | ✅ Present | - |
| **Redis** | 7.0+ | ✅ Present | - |
| **django-redis** | 5.4.0 | ⚠️ Basic | 🟠 HIGH |
| **Uvicorn** | 0.25.0 | ❌ Missing | 🔴 CRITICAL |
| **psutil** | 5.9+ | ✅ Present | - |
| **Zeroconf** | 0.80+ | ❌ Missing | 🟠 HIGH |
| **django-cachalot** | 2.6.1 | ❌ Missing | 🟠 HIGH |
| **sentry-sdk** | 1.39.1 | ❌ Missing | 🟠 HIGH |
| **whitenoise** | 6.6.0 | ❌ Missing | 🟠 HIGH |
| **django-prometheus** | 2.3.1 | ❌ Missing | 🟢 MEDIUM |
| **drf-spectacular** | 0.27.0 | ❌ Missing | 🟢 MEDIUM |

### OCR Stack (Optional - Documents Module)

| Package | Version | Status | Priority |
|---------|---------|--------|----------|
| **Tesseract** | Latest | ✅ Present | - |
| **PaddleOCR** | 3.3.1 | ❌ Missing | 🟠 HIGH |
| **PaddlePaddle** | 2.6.2 | ❌ Missing | 🟠 HIGH |
| **PyTorch** | 2.6.0 | ❌ Missing | 🟠 HIGH |
| **Transformers** | 4.57.1 | ❌ Missing | 🟢 MEDIUM |
| **EasyOCR** | 1.7.2 | ❌ Missing | 🟢 MEDIUM |
| **Surya-OCR** | 0.9.0 | ❌ Missing | 🟢 LOW |

---

## APPENDIX D: RESOURCE ESTIMATES

### Time Estimates by Phase

| Phase | Duration | Developer Effort | Complexity |
|-------|----------|-----------------|------------|
| **Phase 0.5** | 2 weeks | Full-time | HIGH |
| **Phase 1.3** | 1 week | Full-time | MEDIUM |
| **Phase 2** | 2 weeks | Full-time | HIGH |
| **Phase 3** | 2 weeks | Full-time | MEDIUM |
| **Phase 4** | 2 weeks | Full-time | MEDIUM |
| **Phase 5** | 2 weeks | Full-time | HIGH (hardware) |
| **Phase 6+** | Ongoing | Part-time | VARIES |

**Total for v535 MVP (80% parity):** 12 weeks
**Fast Track (60% parity):** 4 weeks

---

**Last Update:** 2025-11-16
**Next Review:** 2025-11-18 (Monday)
**Active Work:** Phase 0.5 - Critical Infrastructure
**Target Release:** February 1, 2026 (v535 with 80% feature parity)
**Alternative:** December 14, 2025 (MVP with 60% parity)
