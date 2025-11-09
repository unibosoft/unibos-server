# 🎯 UNIBOS KURALLAR - CLAUDE İÇİN YÖNLENDME DOSYASI

> **⚠️ KRİTİK:** Bu dosya ana dizindedir, Claude her oturumda MUTLAKA görecektir.
> **AMAÇ:** Claude'u doğru kural dosyalarına yönlendirmek, detay vermek DEĞİL!

---

## 🚨 EN ÖNEMLİ 3 KURAL

### 1️⃣ HİÇBİR ZAMAN MANUEL İŞLEM YAPMA
```
❌ ASLA: rsync, git commit, deployment manuel komutları
✅ HER ZAMAN: Script'leri kullan (tools/scripts/)
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
```

---

## 📂 KURAL DOSYALARI - BURAYA GIT!

### Versiyonlama Yapacaksan:
1. **[VERSIONING_WORKFLOW.md](VERSIONING_WORKFLOW.md)** ← Hızlı workflow özeti
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
1. **[docs/development/VERSIONING_RULES.md](docs/development/VERSIONING_RULES.md)** ← Deployment kuralları
2. **Script:** `./tools/scripts/rocksteady_deploy.sh`

---

## 🔗 DOSYA HİYERARŞİSİ

```
RULES.md (bu dosya - YÖNLENDME)
    ↓
VERSIONING_WORKFLOW.md (hızlı referans)
    ↓
docs/development/
    ├── VERSIONING_RULES.md (DETAYLI KURALLAR - BURAYA GIT!)
    ├── DEVELOPMENT_LOG.md
    └── [diğer dokümanlar]
    ↓
tools/scripts/
    ├── unibos_version.sh (versioning master script)
    ├── backup_database.sh
    ├── verify_database_backup.sh
    └── rocksteady_deploy.sh
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

## 📝 Son Güncelleme

**Tarih:** 2025-11-09
**Neden:** Script workflow hatası düzeltmesi, yönlendirici kural sistemi
**Sonraki Gözden Geçirme:** Her major script değişikliğinde

---

**Not:** Detaylı kurallar, örnekler, validation checklist'ler vb. için yukarıdaki linkleri takip et. Bu dosya sadece yönlendirme amaçlıdır.
