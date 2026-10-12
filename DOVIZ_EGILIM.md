# Döviz stoku eğilimi

İki ayrı nesne: **ölçüm** = TCMB brüt dış borç stoku (USD); **senaryo** = `D_korunmasiz_usd_mr` (korunmasız / hedge dışı proxy, milyar USD). Aynı satır değildir.

Çalıştır: `python3 doviz_egilim.py`.

## Ölçüm — brüt dış borç toplam (EVDS)

- **2023-Q4 → 2026-Q2:** 432.6 → **539.0 milyar USD** (Δ **+106.4**, eğim **+10.64 mr USD/çeyrek**, **artis**).
- Özel sektör payı 2023-Q4 → 2026-Q2: 2023-Q4 **%55.1** → 2026-Q2 **%59.0**

## Senaryo — korunmasız döviz stoku (`uc_kural_senaryo`)

| Senaryo | 2026-Q4 → 2031-Q4 (mr USD) | Δ | Çeyrek eğim | Yön |
| --- | --- | ---: | ---: | --- |
| `mevcut` | 121.8 → 162.9 | +41.1 | +2.06 | **artis** |
| `uc_kural_kilitli` | 120.0 → 120.0 | +0.0 | +0.00 | **sabit** |
| `maliyet_ucuz_revize` | 120.0 → 120.0 | +0.0 | +0.00 | **sabit** |

### Okuma

- **`mevcut`:** `fx_unhedged_buyume_mevcut` ≈ **%6/yıl** → stok **121.8 → 162.9 mr USD** (artış eğilimi).
- **`uc_kural_kilitli` / `maliyet_ucuz_revize`:** segment tavanı **%0** + geri bildirim (stok artarsa **önceki çeyreğe geri al**) → **120.0 mr USD** bandında **sabit**.
- **Kademe takvimi** (`tek_sistem_kademe`) döviz stokuna **doğrudan bağlı değil**; dolay etki yalnızca üç kural senaryosu üzerinden.
- **Gerçek kişi YP mevduat** (adım 4): 2026-Q1 **6 639 milyar TL** karşılığı — **zaman serisi yok**; eğilim tabloya girilmedi.

## Ne denmez

- Brüt dış borç = korunmasız hane/firma stoku denmez.
- Senaryo 120 mr USD = EVDS 539 mr USD toplam dış borç değildir (farklı tanım).

