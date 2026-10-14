# C senaryosu olasılığı — duyarlılık bandı

**Etiket: olasilik_olculmedi_duyarlilik_bandi.** Taban olasılık kapı iskeletinden (`_olasilik.py`); bu rapor yeni olasılık üretmez. C = p, kalan A:B taban oranla (0.333:0.333) bölünür.

| P(C) | P(A) | P(B) | E[TR net 10y, yaşam dahil] | E[GSYH %] | E[iyileşme] | Skor | Karar |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0.30 | 0.350 | 0.350 | -23.455 | 6.524 | -6.26 | 58.2 | kisitli_uygulanabilir |
| 0.35 | 0.325 | 0.325 | -22.687 | 6.31 | -5.50 | 59.1 | kisitli_uygulanabilir |
| 0.40 | 0.300 | 0.300 | -21.92 | 6.096 | -4.73 | 60.0 | kisitli_uygulanabilir |
| 0.45 | 0.275 | 0.275 | -21.152 | 5.882 | -3.96 | 60.9 | kisitli_uygulanabilir |
| 0.50 | 0.250 | 0.250 | -20.384 | 5.668 | -3.19 | 61.8 | kisitli_uygulanabilir |
| 0.55 | 0.225 | 0.225 | -19.616 | 5.453 | -2.43 | 62.7 | uygulanabilir_kosullu |
| 0.60 | 0.200 | 0.200 | -18.848 | 5.239 | -1.66 | 63.6 | uygulanabilir_kosullu |
| 0.65 | 0.175 | 0.175 | -18.081 | 5.025 | -0.89 | 64.5 | uygulanabilir_kosullu |
| 0.70 | 0.150 | 0.150 | -17.313 | 4.811 | -0.12 | 65.4 | uygulanabilir_kosullu |
| 0.75 | 0.125 | 0.125 | -16.545 | 4.597 | +0.65 | 67.5 | uygulanabilir_kosullu |
| 0.80 | 0.100 | 0.100 | -15.777 | 4.383 | +1.41 | 69.7 | uygulanabilir_kosullu |

## Kapı sonuçları (K2: 3 kontrol noktasından kaçı açık)

| Açık | P(A) | P(B) | P(C) | Skor | Karar | Eşiği geçer |
| ---: | ---: | ---: | ---: | ---: | --- | --- |
| 0/3 | 0.305 | 0.547 | 0.148 | 55.4 | kisitli_uygulanabilir | hayır |
| 1/3 | 0.341 | 0.409 | 0.25 | 57.3 | kisitli_uygulanabilir | hayır |
| 2/3 | 0.344 | 0.276 | 0.38 | 59.6 | kisitli_uygulanabilir | hayır |
| 3/3 | 0.312 | 0.167 | 0.521 | 62.1 | uygulanabilir_kosullu | evet |

Taban (kapı iskeleti, gözlem yok): P(C) = 0.333 → skor 58.8 · kisitli_uygulanabilir (bandın dışında, ızgarada değil).


- E[TR net 10y] aralığı: **-23.455 … -15.777** (P(C) 0,30 → 0,80).
- Skor aralığı: **58.2 … 69.7**.
- Karar eşiği (skor 62) geçişi: P(C) ≈ **0.511**
- Beklenen karışımda iyileşme (Δ > 0,05) başlangıcı: P(C) ≈ **0.711**
- Taban satır ana raporla tutarlı: True.
