# C senaryosu olasılığı — duyarlılık bandı

**Etiket: olasilik_olculmedi_duyarlilik_bandi.** Taban olasılık kapı iskeletinden (`_olasilik.py`); bu rapor yeni olasılık üretmez. C = p, kalan A:B taban oranla (0.333:0.333) bölünür.

| P(C) | P(A) | P(B) | E[TR net 10y, yaşam dahil] | E[GSYH %] | E[iyileşme] | Skor | Karar |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0.30 | 0.350 | 0.350 | -23.622 | 7.059 | -6.43 | 53.1 | kisitli_uygulanabilir |
| 0.35 | 0.325 | 0.325 | -22.846 | 6.826 | -5.66 | 54.0 | kisitli_uygulanabilir |
| 0.40 | 0.300 | 0.300 | -22.07 | 6.594 | -4.88 | 54.9 | kisitli_uygulanabilir |
| 0.45 | 0.275 | 0.275 | -21.293 | 6.361 | -4.10 | 55.8 | kisitli_uygulanabilir |
| 0.50 | 0.250 | 0.250 | -20.517 | 6.129 | -3.33 | 56.7 | kisitli_uygulanabilir |
| 0.55 | 0.225 | 0.225 | -19.741 | 5.896 | -2.55 | 57.6 | kisitli_uygulanabilir |
| 0.60 | 0.200 | 0.200 | -18.965 | 5.664 | -1.77 | 58.5 | kisitli_uygulanabilir |
| 0.65 | 0.175 | 0.175 | -18.189 | 5.431 | -1.00 | 59.4 | kisitli_uygulanabilir |
| 0.70 | 0.150 | 0.150 | -17.412 | 5.198 | -0.22 | 60.3 | kisitli_uygulanabilir |
| 0.75 | 0.125 | 0.125 | -16.636 | 4.966 | +0.55 | 62.2 | uygulanabilir_kosullu |
| 0.80 | 0.100 | 0.100 | -15.86 | 4.733 | +1.33 | 64.5 | uygulanabilir_kosullu |

## Kapı sonuçları (K2: 3 kontrol noktasından kaçı açık)

| Açık | P(A) | P(B) | P(C) | Skor | Karar | Eşiği geçer |
| ---: | ---: | ---: | ---: | ---: | --- | --- |
| 0/3 | 0.785 | 0.024 | 0.192 | 51.2 | kisitli_uygulanabilir | hayır |
| 1/3 | 0.427 | 0.156 | 0.417 | 55.2 | kisitli_uygulanabilir | hayır |
| 2/3 | 0.108 | 0.472 | 0.42 | 55.3 | kisitli_uygulanabilir | hayır |
| 3/3 | 0.014 | 0.76 | 0.225 | 51.8 | kisitli_uygulanabilir | hayır |

Taban (kapı iskeleti, gözlem yok): P(C) = 0.333 → skor 53.7 · kisitli_uygulanabilir (bandın dışında, ızgarada değil).


- E[TR net 10y] aralığı: **-23.622 … -15.86** (P(C) 0,30 → 0,80).
- Skor aralığı: **53.1 … 64.5**.
- Karar eşiği (skor 62) geçişi: P(C) ≈ **0.745**
- Beklenen karışımda iyileşme (Δ > 0,05) başlangıcı: P(C) ≈ **0.718**
- Taban satır ana raporla tutarlı: True.
