# UNIBOS v533+ - Yapılacaklar Listesi

**Oluşturulma:** 2025-11-13
**Güncelleme:** 2025-11-13
**Durum:** Aktif

> **Not:** Tamamlanan görevler arşivlenir. Bu dosya sadece aktif görevleri içerir.

---

## ✅ TAMAMLANDI: CLI Tool (2025-11-13)

### 1.1 Eski CLI'yı Analiz Et ve Adapte Et ✅
- [x] Eski main.py'yi bul (`archive/versions/unibos_v533_20251110_1400/apps/cli/src/main.py`)
- [x] Splash screen ve logo'yu analiz et
- [x] Modül yapısını incele (version_manager, setup_manager, git_manager)
- [x] Dependencies'i belirle (Click, terminal UI libs)

### 1.2 Modern CLI Yapısını Oluştur ✅
- [x] `core/cli/main.py` - Ana entry point (splash + command router)
- [x] `core/cli/ui/` - UI components
  - [x] `splash.py` - Animated splash screen with UNIBOS ASCII logo
  - [x] `colors.py` - ANSI color definitions (256 colors + RGB)
  - [x] `layout.py` - Terminal layout utilities (cursor, boxes, centering)
  - [x] `__init__.py` - Package initialization
- [x] `core/cli/commands/` - Command modules
  - [x] `__init__.py`
  - [x] `deploy.py` - Deployment commands
  - [x] `dev.py` - Development commands
  - [x] `db.py` - Database commands
  - [x] `status.py` - Health check commands

### 1.3 Deployment Entegrasyonu ✅
- [x] `core/cli/commands/deploy.py`:
  - [x] `unibos deploy rocksteady` → calls `core/deployment/rocksteady_deploy.sh`
  - [x] `unibos deploy rocksteady --quick` → quick sync mode
  - [x] `unibos deploy rocksteady --check-only` → pre-flight check
  - [x] `unibos deploy local` → placeholder for local deployment
  - [x] `unibos deploy raspberry <target>` → placeholder for Pi deployment
  - [x] `unibos deploy check` → health check integration

### 1.4 Development Commands ✅
- [x] `core/cli/commands/dev.py`:
  - [x] `unibos dev run` → Django dev server (with --port, --host options)
  - [x] `unibos dev shell` → Django shell
  - [x] `unibos dev test` → runs tests
  - [x] `unibos dev migrate` → runs migrations
  - [x] `unibos dev makemigrations` → creates migrations
  - [x] `unibos dev logs` → view/tail logs

### 1.5 Database Commands ✅
- [x] `core/cli/commands/db.py`:
  - [x] `unibos db backup` → calls `tools/scripts/backup_database.sh`
  - [x] `unibos db backup --verify` → backup + verification
  - [x] `unibos db restore <file>` → placeholder for restore
  - [x] `unibos db migrate` → runs migrations
  - [x] `unibos db status` → showmigrations

### 1.6 Setup ve Installation ✅
- [x] `setup.py` - Python package setup (updated entry point)
- [x] `core/__init__.py` - Package structure fix
- [x] Entry point: `console_scripts = ['unibos = core.cli.main:main']`
- [x] Test: `pip install -e .` works
- [x] Test: `unibos` command available globally
- [x] Test: All commands verified (status, deploy, dev, db)

**Result:** CLI tool fully functional! Global `unibos` command available with splash screen, comprehensive commands, and script integration.

---

## ✅ TAMAMLANDI: Module Path Migration (2025-11-13)

**Result:** ✅ No code migration needed! Module FileFields already correct, only Django settings fix required.

### 2.1 Audit Current State ✅
- [x] Analyzed all 13 modules for FileField usage
- [x] Found only 3 modules with FileFields (documents, music, personal_inflation)
- [x] All FileField paths already correctly structured
- [x] Documented in [MODULE_PATH_MIGRATION_ANALYSIS.md](docs/development/MODULE_PATH_MIGRATION_ANALYSIS.md)

### 2.2 FileField Status (13 modules analyzed) ✅
**Modules with FileFields (3/13):**
- [x] **documents** - ✅ Correct (`documents/uploads/`, `documents/thumbnails/`)
- [x] **music** - ✅ Correct (`music/artwork/`, `music/playlists/`)
- [x] **personal_inflation** - ✅ Correct (`wimm/receipts/`)

**Modules without FileFields (10/13):**
- [x] birlikteyiz, cctv, currencies, movies, recaria, restopos, solitaire, store, wimm, wims

### 2.3 Django Settings Fix ✅
**Problem:** MEDIA_ROOT was `data/shared/media` instead of `data/modules`

**Files Updated:**
- [x] [core/web/unibos_backend/settings/base.py](core/web/unibos_backend/settings/base.py:287) → `MEDIA_ROOT = data/modules`
- [x] [core/web/unibos_backend/settings/emergency.py](core/web/unibos_backend/settings/emergency.py:135) → `MEDIA_ROOT = data/modules`
- [x] [core/web/unibos_backend/settings/dev_simple.py](core/web/unibos_backend/settings/dev_simple.py:56) → `MEDIA_ROOT = data/modules`

### 2.4 No Migration Script Needed ✅
- [x] No code changes required (FileField paths already correct)
- [x] No data to migrate (fresh v533 setup, no old files)
- [x] Directory structure verified (`data/modules/` with all subdirs exist)
- [x] Zero risk - configuration change only

**Path Example:**
```python
# FileField: documents/uploads/receipts/2025/11/invoice.pdf
# MEDIA_ROOT: /data/modules/
# Final: /data/modules/documents/uploads/receipts/2025/11/invoice.pdf ✅
```

---

## 🎯 ÖNCELIK 3: Production Cleanup (1 gün)

### 3.1 Local Cleanup
- [ ] Remove Flutter build artifacts (if any)
- [ ] Clean large log files (>10MB)
- [ ] Remove database backups from code directory
- [ ] Verify .gitignore is comprehensive

### 3.2 Remote Cleanup (Rocksteady)
- [ ] Already done: Flutter build removed (-1.6GB)
- [ ] Check for other bloat
- [ ] Verify data/ structure

### 3.3 Archive Optimization
- [ ] Review archive sizes
- [ ] Ensure .archiveignore is comprehensive
- [ ] Document archive retention policy

---

## 🎯 ÖNCELIK 4: Documentation Updates

### 4.1 CLI Documentation
- [ ] Create `core/cli/README.md`
- [ ] Document all commands with examples
- [ ] Add troubleshooting section

### 4.2 Deployment Documentation
- [ ] Update `core/deployment/README.md` with CLI commands
- [ ] Add screenshots/examples
- [ ] Document common issues

### 4.3 Development Guide
- [ ] Update developer onboarding docs
- [ ] Document new CLI usage
- [ ] Update architecture diagrams

---

## 📋 İLERİ TARİHLİ GÖREVLER (Phase 3-5)

### Platform Infrastructure (Week 3)
- [ ] Task Distribution System
  - [ ] `core/platform/orchestration/`
  - [ ] Celery task queue
  - [ ] Worker registry
  - [ ] Health monitoring

- [ ] Connection Routing
  - [ ] `core/platform/routing/`
  - [ ] Local-first policy
  - [ ] Performance-based routing
  - [ ] Load balancing

- [ ] Offline Mode
  - [ ] `core/platform/offline/`
  - [ ] Offline detection
  - [ ] Sync queue
  - [ ] Conflict resolution (CRDT)

### Production Deployments (Week 4)
- [ ] Local Production (`/Users/berkhatirli/Applications/unibos/`)
- [ ] Rocksteady VPS (already done, but needs CLI integration)
- [ ] Raspberry Pi edge device

### Testing & Documentation (Week 5)
- [ ] Unit tests for all modules
- [ ] Integration tests
- [ ] Deployment tests
- [ ] Performance tests
- [ ] Security audit
- [ ] User acceptance testing
- [ ] Final documentation
- [ ] v533 release tag

---

## 📌 KURALLAR

### TODO Dosyası Yönetimi
1. **Ana dizinde sadece bu dosya** (`TODO.md`)
2. **Tamamlanan görevler** → `archive/planning/completed/`
3. **Eski roadmap'ler** → `archive/planning/`
4. **Her hafta güncelleme**: Completed → Archive, New → TODO
5. **Atomik commits**: TODO + ilgili code/docs birlikte

### Commit Kuralı
```bash
# Todo'yu güncelle + ilgili değişiklikleri yap
git add TODO.md core/cli/main.py core/cli/ui/splash.py
git commit -m "feat(cli): implement splash screen with logo

- Created splash.py with animated unibos logo
- Updated TODO.md to mark task complete
- Refs: TODO.md section 1.2"
```

---

## 📅 Haftalık Gözden Geçirme

**Her Pazartesi:**
1. Completed tasks → `archive/planning/completed/YYYY-MM-DD.md`
2. Update priorities
3. Add new tasks if needed
4. Review blockers

**Her Cuma:**
1. Weekly progress summary
2. Next week planning
3. Risk assessment

---

**Son Güncelleme:** 2025-11-13
**Sonraki Gözden Geçirme:** 2025-11-18 (Pazartesi)
