# C senaryosu olasılığı — duyarlılık bandı

**Etiket: olasilik_olculmedi_duyarlilik_bandi.** Taban olasılık kapı iskeletinden (`_olasilik.py`); bu rapor yeni olasılık üretmez. C = p, kalan A:B taban oranla (0.333:0.333) bölünür.

| P(C) | P(A) | P(B) | E[TR net 10y, yaşam dahil] | E[GSYH %] | E[iyileşme] | Skor | Karar |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0.30 | 0.350 | 0.350 | -22.644 | 6.313 | -5.45 | 57.3 | kisitli_uygulanabilir |
| 0.35 | 0.325 | 0.325 | -21.952 | 6.122 | -4.76 | 58.2 | kisitli_uygulanabilir |
| 0.40 | 0.300 | 0.300 | -21.261 | 5.932 | -4.07 | 59.1 | kisitli_uygulanabilir |
| 0.45 | 0.275 | 0.275 | -20.569 | 5.741 | -3.38 | 60.0 | kisitli_uygulanabilir |
| 0.50 | 0.250 | 0.250 | -19.878 | 5.551 | -2.69 | 60.9 | kisitli_uygulanabilir |
| 0.55 | 0.225 | 0.225 | -19.186 | 5.36 | -2.00 | 61.8 | kisitli_uygulanabilir |
| 0.60 | 0.200 | 0.200 | -18.495 | 5.17 | -1.30 | 62.7 | uygulanabilir_kosullu |
| 0.65 | 0.175 | 0.175 | -17.803 | 4.979 | -0.61 | 63.6 | uygulanabilir_kosullu |
| 0.70 | 0.150 | 0.150 | -17.112 | 4.789 | +0.08 | 64.6 | uygulanabilir_kosullu |
| 0.75 | 0.125 | 0.125 | -16.42 | 4.598 | +0.77 | 66.8 | uygulanabilir_kosullu |
| 0.80 | 0.100 | 0.100 | -15.729 | 4.408 | +1.46 | 68.9 | uygulanabilir_kosullu |

## Kapı sonuçları (K2: 3 kontrol noktasından kaçı açık)

| Açık | P(A) | P(B) | P(C) | Skor | Karar | Eşiği geçer |
| ---: | ---: | ---: | ---: | ---: | --- | --- |
| 0/3 | 0.305 | 0.547 | 0.148 | 54.6 | kisitli_uygulanabilir | hayır |
| 1/3 | 0.341 | 0.409 | 0.25 | 56.4 | kisitli_uygulanabilir | hayır |
| 2/3 | 0.344 | 0.276 | 0.38 | 58.8 | kisitli_uygulanabilir | hayır |
| 3/3 | 0.312 | 0.167 | 0.521 | 61.3 | kisitli_uygulanabilir | hayır |

Taban (kapı iskeleti, gözlem yok): P(C) = 0.333 → skor 57.9 · kisitli_uygulanabilir (bandın dışında, ızgarada değil).


- E[TR net 10y] aralığı: **-22.644 … -15.729** (P(C) 0,30 → 0,80).
- Skor aralığı: **57.3 … 68.9**.
- Karar eşiği (skor 62) geçişi: P(C) ≈ **0.561**
- Beklenen karışımda iyileşme (Δ > 0,05) başlangıcı: P(C) ≈ **0.698**
- Taban satır ana raporla tutarlı: True.
