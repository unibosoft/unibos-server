# 🎯 UNIBOS TEMEL KURALLAR - HER ZAMAN BURADAN BAŞLA

> **⚠️ KRİTİK:** Bu dosya ana dizinde olduğu için Claude'un her oturumda görmesi ZORUNLU.
> Bu dosya değiştirildiğinde, referans ettiği tüm dosyalar da kontrol edilmeli.

---

## 📜 Meta-Kural: Kuralların Kuralları

### Kural #0: Recursive Self-Validation
```
1. Bu dosya değiştiğinde → tüm alt kurallar kontrol edilmeli
2. Alt kurallar değiştiğinde → bu dosya güncellenmeli
3. Script'ler değiştiğinde → kurallar güncellenmeli
4. Kurallar değiştiğinde → script'ler güncellenmeli
```

### Kural #1: Hiçbir Zaman Manuel İşlem Yapma
```
❌ ASLA: rsync, git commit, deployment manuel komutları
✅ HER ZAMAN: Script'leri kullan
```

### Kural #2: Script'ler Self-Documenting Olmalı
```
Her script:
- Başlığında amacını açıklamalı
- Kritik kuralları içermeli
- Bu dosyaya referans vermeli
```

### Kural #3: Değişiklikler Atomik Olmalı
```
Eğer:
  - Kural değişirse → Script + Dokümantasyon birlikte güncellenmeli
  - Script değişirse → Kurallar + Testler birlikte güncellenmeli
```

---

## 🔗 Kural Hiyerarşisi ve Erişim

```
RULES.md (bu dosya - ANA DİZİN)
    ↓
    ├─→ VERSIONING_WORKFLOW.md (hızlı referans)
    ├─→ docs/development/VERSIONING_RULES.md (detaylı kurallar)
    ├─→ .archiveignore (arşiv hariç tutma kuralları)
    ├─→ .rsyncignore (rsync hariç tutma kuralları)
    └─→ .gitignore (git hariç tutma kuralları)
```

**Erişim Protokolü:**
1. **İlk önce RULES.md oku** (bu dosya - genel çerçeve)
2. **Sonra ilgili detay dosyasına git** (spesifik kurallar)
3. **Son olarak script'i kullan** (hiçbir zaman manuel işlem yapma)

---

## 📋 Kural Kategorileri

### 1. VERSİYONLAMA KURALLARI

**Kritik Kural:** ARŞİVLENEN = BİTMİŞ VERSİYON (yeni versiyon değil!)

**Workflow:**
```bash
# DOĞRU SIRA (ASLA DEĞIŞMEZ):
Mevcut versiyondaki geliştirmeler tamamlandı (örn. v531)
  ↓
1. DATABASE BACKUP oluştur (mevcut versiyon için)
  ↓
2. ARŞİV oluştur (mevcut v531'i arşivle - henüz v532'ye GEÇMEDİN!)
  ↓
3. GIT COMMIT (mevcut v531 final)
  ↓
4. GIT TAG + BRANCH oluştur (mevcut v531)
  ↓
5. GITHUB'A PUSH (tag + branch)
  ↓
6. DEPLOY (rocksteady'ye v531 gönder)
  ↓
7. ŞİMDİ YENİ VERSİYONA GEÇ (VERSION.json'u v532 yap)
  ↓
8. Yeni versiyon değişikliğini commit et ("chore: bump version to v532")
  ↓
9. Artık v532'desin, yeni geliştirmelere başla!
```

**Script:** `./tools/scripts/unibos_version.sh`
**Detaylar:** `docs/development/VERSIONING_RULES.md`
**Hızlı Ref:** `VERSIONING_WORKFLOW.md`

**Validation Kontrolü:**
- [ ] Script başlığında workflow sırası var mı?
- [ ] `create_archive(current_version)` ÖNCE `update_version_json(next_version)` SONRA mı?
- [ ] Git tag VE branch oluşuyor mu?
- [ ] Database backup arşivden ÖNCE mi?

---

### 2. ARŞİVLEME KURALLARI

**Kritik Kural:** Arşivler temiz olmalı (venv, node_modules, build artifacts HARİÇ)

**Beklenen Boyutlar:**
- v510-v525: 30-70MB (early monorepo)
- v526-v527: 80-90MB (full features)
- v528+: 30-40MB (cleaned structure)

**Anomali Tespiti:**
- < 20MB → Kod eksik olabilir
- > 100MB → Build artifacts veya SQL dumps dahil
- > 500MB → Flutter build hariç tutulmamış (KRİTİK HATA!)

**Exclude Dosyaları:**
- `.archiveignore` → Arşivlerden hariç tutulanlar
- `.rsyncignore` → rsync işlemlerinden hariç tutulanlar

**Validation Kontrolü:**
- [ ] `.archiveignore` venv/ içeriyor mu?
- [ ] `.archiveignore` node_modules/ içeriyor mu?
- [ ] `.archiveignore` */build/ içeriyor mu?
- [ ] `.archiveignore` *.sql içeriyor mu?
- [ ] Script `--exclude-from=.archiveignore` kullanıyor mu?

---

### 3. DATABASE BACKUP KURALLARI

**Kritik Kural:** Database backup'lar arşivlerden AYRI saklanır

**Lokasyon:** `archive/database_backups/`
**Retention:** Son 3 backup tutulur
**Format:** `unibos_vXXX_YYYYMMDD_HHMM.sql`

**Workflow:**
1. Backup oluştur (versiyonlamadan ÖNCE)
2. `archive/database_backups/` dizinine kaydet
3. Eski backup'ları sil (son 3 hariç)
4. `.gitignore` ile git'ten hariç tut

**Script:** `./tools/scripts/backup_database.sh`
**Verify:** `./tools/scripts/verify_database_backup.sh`

**Validation Kontrolü:**
- [ ] `archive/database_backups/` .gitignore'da mı?
- [ ] Versiyonlama script'i backup'ı önce mi çağırıyor?
- [ ] Backup rotation (son 3) çalışıyor mu?

---

### 4. DEPLOYMENT KURALLARI

**Kritik Kural:** Deployment ARŞİVLENMİŞ versiyonu deploy eder (yeni değil!)

**Hedef:** rocksteady production server
**Script:** `./tools/scripts/rocksteady_deploy.sh`

**Workflow:**
1. Arşiv tamamlandı
2. Tag + branch oluşturuldu
3. GitHub'a push edildi
4. **ŞİMDİ** deploy et (arşivlenen versiyonu)

**Validation Kontrolü:**
- [ ] Deploy script Daphne ve Gunicorn'u destekliyor mu?
- [ ] Nginx reload stratejisi minimal downtime sağlıyor mu?
- [ ] Deploy ARŞİVLEMEDEN SONRA mı yapılıyor?

---

### 5. GIT İŞLEM KURALLARI

**Kritik Kural:** Her versiyon için hem TAG hem BRANCH oluştur

**Tag Formatı:** `v531`, `v532`, ... (semver değil, sequential)
**Branch Formatı:** `v531`, `v532`, ... (tag ile aynı)

**Workflow:**
```bash
git checkout main
git add -A
git commit -m "v531: Deployment infrastructure improvements"
git checkout -b v531           # Branch oluştur
git push origin v531           # Branch push et
git checkout main              # Main'e dön
git push origin main           # Main push et
git tag v531                   # Tag oluştur
git push origin --tags         # Tag push et
```

**Validation Kontrolü:**
- [ ] `git_operations()` fonksiyonu branch oluşturuyor mu?
- [ ] Branch VE tag GitHub'a push ediliyor mu?
- [ ] Tag ve branch adları aynı mı?

---

### 6. SCRIPT BAKIMI KURALLARI

**Kritik Kural:** Script'ler değiştiğinde kurallar da güncellenmeli

**Script Listesi:**
- `tools/scripts/unibos_version.sh` → Versiyonlama master script
- `tools/scripts/backup_database.sh` → Database backup
- `tools/scripts/verify_database_backup.sh` → Backup doğrulama
- `tools/scripts/rocksteady_deploy.sh` → Production deployment

**Güncelleme Protokolü:**
1. Script değişti mi? → `RULES.md` kontrol et
2. Kural değişti mi? → Script'i güncelle
3. İkisi de değişti mi? → Atomik commit (birlikte)

**Validation Kontrolü:**
- [ ] Her script başlığında amacı yazıyor mu?
- [ ] Her script kritik kuralları içeriyor mu?
- [ ] Her script `RULES.md` veya detay dosyasına referans veriyor mu?

---

### 7. DOKÜMANTASYON KURALLARI

**Kritik Kural:** Dokümantasyon kodu yansıtmalı, kod dokümantasyonu

**Dokümantasyon Hiyerarşisi:**
```
RULES.md (bu dosya)
  ↓
VERSIONING_WORKFLOW.md (hızlı referans)
  ↓
docs/development/
  ├── VERSIONING_RULES.md (detaylı versioning)
  ├── DEVELOPMENT_LOG.md (geliştirme günlüğü)
  └── [diğer geliştirici dokümanları]
```

**Güncelleme Tetikleyicileri:**
- Script değişti → Dokümantasyon güncelle
- Kural değişti → Örnekler güncelle
- Workflow değişti → Tüm seviyeler güncelle (RULES.md, VERSIONING_WORKFLOW.md, VERSIONING_RULES.md)

**Validation Kontrolü:**
- [ ] Her kural değişikliği 3 dosyada da yansıtıldı mı?
- [ ] Script header'ları güncel mi?
- [ ] Örnekler gerçek kullanımı yansıtıyor mu?

---

## ✅ Validation Checklist (Claude için)

Her işlem öncesi bu checklist'i çalıştır:

### Versiyonlama İşlemi Öncesi:
- [ ] `RULES.md` okudum
- [ ] `VERSIONING_RULES.md` detaylarını kontrol ettim
- [ ] Script'in doğru workflow sırasını kullandığını doğruladım
- [ ] `.archiveignore` güncel mi kontrol ettim
- [ ] Database backup script'i mevcut mu kontrol ettim

### Script Değişikliği Öncesi:
- [ ] Değişiklik hangi kuralı etkiliyor tespit ettim
- [ ] Etkilenen tüm kural dosyalarını listeledim
- [ ] Atomik commit planı hazırladım (script + kurallar birlikte)
- [ ] Validation kontrollerini güncelleyeceğim

### Kural Değişikliği Öncesi:
- [ ] Hangi script'lerin etkileneceğini tespit ettim
- [ ] Tüm seviyelerde güncelleme gerekiyor mu kontrol ettim
- [ ] Örnekleri güncelleme listesine ekledim
- [ ] Commit mesajında "BREAKING CHANGE" gerekiyor mu değerlendirdim

---

## 🔄 Recursive Update Protocol

**Tetikleyici:** Herhangi bir kural veya script değişikliği

**Algoritma:**
```python
def update_rules_and_scripts(change):
    if change.type == "RULE":
        affected_scripts = find_scripts_using_rule(change.rule)
        affected_docs = find_docs_referencing_rule(change.rule)

        update_all(affected_scripts)
        update_all(affected_docs)
        validate_consistency()

    elif change.type == "SCRIPT":
        affected_rules = find_rules_enforced_by_script(change.script)

        update_all(affected_rules)
        validate_consistency()

    commit_atomic([change, affected_scripts, affected_rules, affected_docs])
```

---

## 📞 Claude İçin Talimatlar

### Her Oturumda:
1. **İlk iş `RULES.md` oku** (bu dosya)
2. **Görev için ilgili detay dosyasını oku**
3. **Script'i kullan, manuel komut çalıştırma**

### Versiyonlama Yapılacaksa:
1. `RULES.md` → Genel çerçeve
2. `VERSIONING_WORKFLOW.md` → Hızlı workflow
3. `docs/development/VERSIONING_RULES.md` → Detaylı kurallar
4. `./tools/scripts/unibos_version.sh` → Script'i çalıştır

### Script Güncellenecekse:
1. `RULES.md` → Meta kurallar
2. İlgili detay dosyası → Spesifik kurallar
3. Script'i güncelle
4. Tüm referansları güncelle
5. Atomik commit (hepsi birlikte)

### Kural Eklenecek/Değiştirilecekse:
1. Bu dosyayı güncelle (RULES.md)
2. İlgili detay dosyasını güncelle
3. Etkilenen script'leri güncelle
4. Validation checklist'e ekle
5. Atomik commit (hepsi birlikte)

---

## 🚨 Kritik Hatalar ve Önleme

### HATA: Arşiv Boyutu Anormali
**Neden:** `.archiveignore` güncel değil
**Önlem:** Her Flutter/Node/Python dependency değişikliğinde `.archiveignore` kontrol et

### HATA: Boş Versiyon Arşivlendi
**Neden:** VERSION.json ÖNCE güncellendi, SONRA arşiv oluşturuldu
**Önlem:** Script workflow sırasını her commit'te validate et

### HATA: Tag/Branch Push Edilmedi
**Neden:** `git_operations()` eksik veya hatalı
**Önlem:** Her versiyonlamada GitHub'ı kontrol et

### HATA: Database Backup Eksik
**Neden:** Versiyonlama script'i backup'ı çağırmıyor
**Önlem:** `archive/database_backups/` dizinini her versiyonda kontrol et

---

## 📊 İstatistikler ve Metrikler

### Script Health:
- [ ] `unibos_version.sh` son 30 günde güncellenmiş mi?
- [ ] Tüm script'ler executable mi? (`chmod +x`)
- [ ] Script header'ları bu dosyaya referans veriyor mu?

### Kural Health:
- [ ] `RULES.md` son 60 günde gözden geçirilmiş mi?
- [ ] Tüm validation checklist'ler geçiyor mu?
- [ ] Kural çelişkileri var mı?

### Arşiv Health:
- [ ] Son 5 arşiv boyut ortalaması beklenen aralıkta mı?
- [ ] `.archiveignore` son 30 günde güncellenmiş mi?
- [ ] Database backup rotation çalışıyor mu?

---

**Son Güncelleme:** 2025-11-09
**Güncelleme Nedeni:** Script workflow hatası düzeltmesi, recursive kurallar eklenmesi
**Sonraki Gözden Geçirme:** 2025-12-09 (30 gün sonra)

**Versiyon:** 1.0
**Changelog:**
- v1.0 (2025-11-09): İlk oluşturma - Recursive self-validation kuralları
