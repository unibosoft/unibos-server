# 🎯 UNIBOS KURALLAR - CLAUDE İÇİN YÖNLENDME DOSYASI

> **⚠️ KRİTİK:** Bu dosya ana dizindedir, Claude her oturumda MUTLAKA görecektir.
> **AMAÇ:** Claude'u doğru kural dosyalarına yönlendirmek, detay vermek DEĞİL!

---

## 🚨 EN ÖNEMLİ 3 KURAL

### 1️⃣ HİÇBİR ZAMAN MANUEL İŞLEM YAPMA
```
❌ ASLA ASLA ASLA:
   • Manuel rsync komutları
   • Manuel ssh deployment komutları
   • Manuel git commit/tag/branch komutları
   • Manuel deployment işlemleri
   • Manuel arşiv oluşturma
   • Manuel version bump işlemleri
   • Manuel pip install veya dependency kurulumu (remote'da)
   • Manuel service restart komutları
   • Manuel dev→prod sync veya git push komutları

✅ HER ZAMAN HER ZAMAN HER ZAMAN:
   • ./tools/scripts/unibos_version.sh (versiyonlama için)
   • ./tools/scripts/backup_database.sh (database backup için)
   • ./core/deployment/rocksteady_deploy.sh (deployment için)
   • unibos git sync-prod (local prod sync için)
   • unibos git push-dev / push-prod (git operations için)

⚠️ BU KURAL İHLAL EDİLEMEZ - HİÇBİR İSTİSNA YOK!
⚠️ DEPLOYMENT MUTLAKA ./core/deployment/rocksteady_deploy.sh İLE YAPILMALI!
```

### 2️⃣ HER OTURUMDA KURALLARI OKU
```
1. İlk iş: RULES.md (bu dosya)
2. İkinci iş: İlgili detay dosyası
3. Son iş: Script'i çalıştır
```

### 3️⃣ DEĞIŞIKLIKLER ATOMIK OLMALI
```
Kural değişti → Script + Dokümantasyon birlikte güncelle
Script değişti → Kurallar + Dokümantasyon birlikte güncelle
TODO güncellendi → İlgili code/docs birlikte commit et
```

### 4️⃣ ANA DİZİN HEP DÜZENLİ OLMALI
```
✅ Ana dizinde SADECE:
   • README.md, RULES.md, TODO.md
   • VERSION.json
   • .gitignore, .rsyncignore, .archiveignore
   • setup.py, pyproject.toml (packaging)
   • core/, modules/, data/, docs/, tools/ (dizinler)

❌ Ana dizinde ASLA:
   • Eski TODO/ROADMAP dosyaları
   • Geçici notlar, planlar
   • Backup dosyaları
   • Test dosyaları

→ Tüm eski planlama dosyaları: archive/planning/
→ Tamamlanan TODO'lar: archive/planning/completed/
```

---

## 🎬 HER OTURUM BAŞLANGICI - ZORUNLU CHECKLIST

**⚠️ MUTLAKA YAP:** Claude, her yeni oturuma başlarken bu checklist'i takip et!

### 1️⃣ Otomatik Kontroller (İlk 30 saniye)

```bash
# A. Screenshot kontrolü
ls -la *.png Screenshot*.png 2>/dev/null
# → VARSA: SCREENSHOT_MANAGEMENT.md oku ve işle
# → YOKSA: Devam et

# B. Istanbul timezone doğrulama
TZ='Europe/Istanbul' date '+%Y-%m-%d %H:%M:%S %z'
# → "+03:00" görmeli sin - YOKSA HATA!

# C. Git status
git status --short
# → Uncommitted changes varsa: Not et, kullanıcıya bildir

# D. Current version
grep '"version"' apps/cli/src/VERSION.json | head -1
```

### 2️⃣ Detaylı Protokol (Oku ve Uygula)

- **[docs/development/CLAUDE_SESSION_PROTOCOL.md](docs/development/CLAUDE_SESSION_PROTOCOL.md)** ← Oturum protokolü (MUTLAKA OKU!)
- **[docs/development/SCREENSHOT_MANAGEMENT.md](docs/development/SCREENSHOT_MANAGEMENT.md)** ← SS varsa işle
- **[docs/development/CODE_QUALITY_STANDARDS.md](docs/development/CODE_QUALITY_STANDARDS.md)** ← Kod standartları

### 3️⃣ Kullanıcıya Karşılama (Türkçe)

```
Merhaba Berk! 👋

✅ Projeyi taradım ve hazırım.
📸 Screenshot: [VAR: dosya adı / YOK]
⏰ Istanbul: [YYYY-MM-DD HH:MM:SS +03:00]
🔧 Git status: [Clean / X files changed]
📌 Version: [vXXX]

Ne üzerinde çalışmamı istersin?
```

---

## 📂 KURAL DOSYALARI - BURAYA GIT!

### Versiyonlama Yapacaksan:
1. **[docs/development/VERSIONING_WORKFLOW.md](docs/development/VERSIONING_WORKFLOW.md)** ← Hızlı workflow özeti
2. **[docs/development/VERSIONING_RULES.md](docs/development/VERSIONING_RULES.md)** ← Detaylı kurallar
3. **Script:** `./tools/scripts/unibos_version.sh`

### Arşivleme Yapacaksan:
1. **[docs/development/VERSIONING_RULES.md](docs/development/VERSIONING_RULES.md)** ← "Archive Exclusion Rules" bölümü
2. **[.archiveignore](.archiveignore)** ← Hariç tutulan dosyalar
3. **Script:** `./tools/scripts/unibos_version.sh` (Option 5: Archive Only)

### Database Backup Yapacaksan:
1. **[docs/development/VERSIONING_RULES.md](docs/development/VERSIONING_RULES.md)** ← "Database Backup System" bölümü
2. **Script:** `./tools/scripts/backup_database.sh`
3. **Verify:** `./tools/scripts/verify_database_backup.sh`

### Deployment Yapacaksan:
1. **[core/deployment/README.md](core/deployment/README.md)** ← Deployment guide
2. **Script:** `./core/deployment/rocksteady_deploy.sh`
3. **⚠️ MUTLAKA:** Pre-flight checks yapılır, manuel komut yasak!

### Dev/Prod Workflow Yapacaksan:
1. **[docs/guides/dev-prod-workflow.md](docs/guides/dev-prod-workflow.md)** ← Detaylı workflow guide
2. **[docs/guides/git-workflow-usage.md](docs/guides/git-workflow-usage.md)** ← CLI usage guide
3. **CLI Commands:**
   - `unibos git setup` - Git remotes kurulumu
   - `unibos git push-dev` - Dev repo'ya push
   - `unibos git push-prod` - Prod repo'ya push (filtered!)
   - `unibos git sync-prod` - Local prod'a sync (filtered!)
4. **⚠️ KRITIK:**
   - Dev database: `unibos_dev` / `unibos_dev_user`
   - Prod database: `unibos_db` / `unibos_db_user`
   - `.prodignore` file defines exclusions
   - ASLA manuel rsync veya git push kullanma!

---

## 🔗 DOSYA HİYERARŞİSİ

```
RULES.md (bu dosya - YÖNLENDME)
    ↓
docs/development/
    ├── VERSIONING_WORKFLOW.md (hızlı referans)
    ├── VERSIONING_RULES.md (DETAYLI KURALLAR - BURAYA GIT!)
    ├── DEVELOPMENT_LOG.md
    └── [diğer dokümanlar]
    ↓
tools/scripts/
    ├── unibos_version.sh (versioning master script)
    ├── backup_database.sh
    └── verify_database_backup.sh
core/deployment/
    ├── rocksteady_deploy.sh (production deployment)
    └── README.md (deployment guide)
```

---

## ✅ HER İŞLEM ÖNCESİ CHECKLIST

### Versiyonlama Yapacaksan:
- [ ] `RULES.md` okudum (bu dosya)
- [ ] `VERSIONING_WORKFLOW.md` okudum (hızlı workflow)
- [ ] `docs/development/VERSIONING_RULES.md` okudum (detaylı kurallar)
- [ ] Script kullanacağım (manuel komut YOK!)

### Script Değiştireceksen:
- [ ] Hangi kuralın etkilendiğini tespit ettim
- [ ] İlgili kural dosyasını okudum
- [ ] Atomik commit yapacağım (script + kurallar birlikte)

### Kural Değiştireceksen:
- [ ] Hangi script'lerin etkileneceğini tespit ettim
- [ ] Tüm seviyeler güncellenecek (RULES.md, VERSIONING_WORKFLOW.md, VERSIONING_RULES.md)
- [ ] Atomik commit yapacağım (kurallar + scriptler birlikte)

---

## 🔄 RECURSIVE SELF-VALIDATION SYSTEM

### Kendini Koruyan Kurallar Prensibi

**Amaç**: Kuralların zamanla bozulmasını önlemek, her değişiklikte tutarlılığı sağlamak.

### Validation Matrix

| Değişiklik Yapılan | Kontrol Edilmesi Gerekenler | Güncellenmesi Gerekenler |
|-------------------|---------------------------|------------------------|
| **RULES.md** | VERSIONING_WORKFLOW.md, VERSIONING_RULES.md, CLAUDE_SESSION_PROTOCOL.md | Script header comment'leri, CLAUDE.md index |
| **TODO.md** | Tamamlanan tasklar archive'e taşınmalı | İlgili code/docs birlikte commit |
| **unibos_version.sh** | VERSIONING_RULES.md workflow bölümü | Script header, kural dökümanları |
| **VERSIONING_RULES.md** | unibos_version.sh, backup_database.sh | VERSIONING_WORKFLOW.md örnekleri |
| **.archiveignore** | .gitignore tutarlılığı | VERSIONING_RULES.md exclusion listesi |
| **.rsyncignore** | .archiveignore tutarlılığı | core/deployment/README.md exclusion listesi |
| **rocksteady_deploy.sh** | core/deployment/README.md, .rsyncignore | RULES.md deployment bölümü |
| **CLAUDE_SESSION_PROTOCOL.md** | SCREENSHOT_MANAGEMENT.md, CODE_QUALITY_STANDARDS.md | RULES.md checklist, CLAUDE.md index |
| **SCREENSHOT_MANAGEMENT.md** | CLAUDE_SESSION_PROTOCOL.md | .archiveignore screenshot path'leri |
| **CODE_QUALITY_STANDARDS.md** | CLAUDE_SESSION_PROTOCOL.md | Kod değişikliklerinde uyumluluk |
| **dev-prod-workflow.md** | .prodignore, git-workflow-usage.md | CLI commands (git.py), database credentials consistency |
| **.prodignore** | dev-prod-workflow.md, git.py | Exclusion list in documentation, rsync/git operations |
| **core/cli/commands/git.py** | .prodignore, dev-prod-workflow.md | Exclusion patterns, workflow documentation |

### Atomik Commit Kuralı

```bash
# ❌ YANLIŞ: Sadece script değişti
git add tools/scripts/unibos_version.sh
git commit -m "Updated versioning script"

# ✅ DOĞRU: Script + İlgili kurallar + Dökümanlar birlikte
git add tools/scripts/unibos_version.sh
git add docs/development/VERSIONING_RULES.md
git add VERSIONING_WORKFLOW.md
git commit -m "refactor(versioning): update workflow order

- Updated unibos_version.sh to archive before version bump
- Updated VERSIONING_RULES.md with correct workflow
- Updated VERSIONING_WORKFLOW.md examples

Refs: #recursive-validation"
```

### Self-Check Süreci

Her değişiklik sonrası kendine şu soruları sor:

1. **Kural değişti mi?**
   - Etkilenen script'ler tespit edildi mi?
   - Script header'ları güncellendi mi?
   - İlgili dökümanlar senkronize edildi mi?

2. **Script değişti mi?**
   - Script header'daki rule referansları doğru mu?
   - İlgili kural dosyaları güncellendi mi?
   - Workflow örnekleri hala geçerli mi?

3. **Değişiklik atomik mi?**
   - Tüm ilgili dosyalar aynı commit'te mi?
   - Commit mesajı ne değiştiğini açıklıyor mu?
   - Cross-reference'lar bozulmadı mı?

### Gelecek: Otomatik Validation

```bash
# TODO: tools/scripts/validate_rules.sh oluşturulacak
# Bu script otomatik olarak:
# 1. Kural dosyalarının varlığını kontrol eder
# 2. Çapraz referansları doğrular
# 3. Script header'larındaki rule linklerini validate eder
# 4. Tutarsızlıkları rapor eder
```

---

## 📝 Son Güncelleme

**Tarih:** 2025-11-13 (Updated)
**Neden:** Dev/prod workflow kuralları ve validation eklendi
**Değişiklikler:**
- ✅ Dev/prod workflow section eklendi (RULES.md)
- ✅ dev-prod-workflow.md, git-workflow-usage.md, .prodignore validation matrix'e eklendi
- ✅ CLI git commands (push-dev, push-prod, sync-prod) mandatory kullanım
- ✅ Manuel rsync/git push yasaklandı (dev→prod için)
- ✅ Database naming standardized (unibos_dev/unibos_dev_user vs unibos_db/unibos_db_user)
- ✅ .prodignore updated to exclude .archiveignore
- ✅ core/deployment/ dizini oluşturuldu (deploy/ yerine)
- ✅ rocksteady_deploy.sh version-agnostic yapıldı
- ✅ Otomatik architecture detection (core/web vs platform/*)
- ✅ Pre-flight size checks (Flutter build, logs, venv detection)
- ✅ Otomatik dependency checking ve kurulum
- ✅ core/deployment/README.md oluşturuldu (comprehensive guide)

**Bir Önceki Güncelleme:** 2025-11-09 - Claude oturum protokolü ve kod kalitesi standartları
**Sonraki Gözden Geçirme:** Her major script veya kural değişikliğinde

---

**Not:** Detaylı kurallar, örnekler, validation checklist'ler vb. için yukarıdaki linkleri takip et. Bu dosya sadece yönlendirme amaçlıdır.
