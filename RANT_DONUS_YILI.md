# Eski gelir düzeyine dönüş yılı (rant kanalı)

**Senaryo; ölçüm değil.** Payda: ücret/kapsama/yasam tasarrufu (H), faaliyet+zarf (F), faaliyet (B), vergi/transfer (K) — hepsi VARSAYIM reel büyüme ile.

| Senaryo | Aktör | Rant kayıp | Rant direnci % | Amorti Δ | **Dönüş yılı** | Rant dışı artış (milyar/yıl) |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| mevcut | H | 0.0 | 0.0 | 0.0 | **0** | 73.85 |
| mevcut | F | 0.0 | 0.0 | 0.0 | **0** | 187.31 |
| mevcut | B | 0.0 | 0.0 | 0.0 | **0** | 16.79 |
| mevcut | K | 0.0 | 0.0 | 0.0 | **0** | 136.94 |
| mevcut | TOPLAM | | 0.0 | | | |
| uc_kural_kilitli | H | 113.8 | 2.12 | 0.8 | **0.53** | 216.36 |
| uc_kural_kilitli | F | 170.33 | 0.88 | 0.48 | **0.51** | 335.47 |
| uc_kural_kilitli | B | 119.23 | 1.49 | 0.29 | **7.1** | 16.79 |
| uc_kural_kilitli | K | 17.03 | 0.29 | 0.04 | **0.02** | 1075.98 |
| uc_kural_kilitli | TOPLAM | | 1.44 | | | |
| maliyet_ucuz_revize | H | 289.98 | 22.64 | 2.08 | **1.84** | 157.89 |
| maliyet_ucuz_revize | F | 74.81 | 1.03 | 0.21 | **0.22** | 335.47 |
| maliyet_ucuz_revize | B | 52.37 | 0.66 | 0.12 | **3.12** | 16.79 |
| maliyet_ucuz_revize | K | 86.23 | 1.5 | 0.18 | **0.61** | 140.74 |
| maliyet_ucuz_revize | TOPLAM | | 9.65 | | | |

## Revize vs sert (H)

Revize kira kaybı büyük, ücret/kapsama kazancı sınırlı → **H dönüş yılı en uzun**. Sert H rantı korunduğu için kayıp düşük → dönüş kısa veya 0.

Duyarlılık: tüm aktörlerde rant dışı reel büyüme %2 / %3 / %5 → `rant_donus_yili_duyarlik.csv`.

## Ne denmez

- Kira arzı artmazsa H gerçek süresi daha uzun olabilir.
- Dönüş yılı ölçülen gelir geri kazanım süresi değildir.
