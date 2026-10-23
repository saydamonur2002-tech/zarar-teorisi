# Zararın Muhasebesi

Altı kesimli stok–akım modeli (SFC) ve Tek Sistem paketinin bu kaldıraçlara çevrilmiş hali. Birim: stok trilyon TL veya milyar dolar; akım çeyreklik trilyon TL.

```bash
python3 zararin_muhasebesi/build_page.py
python3 zararin_muhasebesi/test_sfc_muhasebe.py
```

Katsayı kararları `KATSAYI.md`. Koşu öncesi eşikler `ON_KAYIT.md`. Sapma `SAPMA.md`.

Adres stoku `adim4.csv` üzerinden okunur. `TS_NPL_COEF = 0,5` ve atalet `ρ = 0,59` repodaki ölçümle aynı nesne olmadığı için durur. Banka açılış artığı `BANKA_OZKAYNAK_TN = 4,65` adlı sabittir; Temmuz 2026 iddiası **[DOĞRULANMADI]**.

S4z ve S5z, zombi kanalı kapalı yapısal kopyadır. Bu kopya model içi karşı-olgudur; Türkiye için nedensel tahmin değildir.
