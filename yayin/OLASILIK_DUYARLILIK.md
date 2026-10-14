# C senaryosu olasılığı — duyarlılık bandı

**Etiket: olasilik_olculmedi_duyarlilik_bandi.** Olasılıklar elle atanmış vekildir; bu rapor yeni olasılık üretmez. C = p, kalan A:B taban oranla (0.22:0.18) bölünür.

| P(C) | P(A) | P(B) | E[TR net 10y, yaşam dahil] | E[GSYH %] | E[iyileşme] | Skor | Karar |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0.30 | 0.385 | 0.315 | -22.102 | 6.162 | -4.91 | 57.3 | kisitli_uygulanabilir |
| 0.35 | 0.357 | 0.292 | -21.45 | 5.982 | -4.26 | 58.2 | kisitli_uygulanabilir |
| 0.40 | 0.330 | 0.270 | -20.797 | 5.803 | -3.61 | 59.1 | kisitli_uygulanabilir |
| 0.45 | 0.302 | 0.247 | -20.144 | 5.623 | -2.95 | 60.0 | kisitli_uygulanabilir |
| 0.50 | 0.275 | 0.225 | -19.491 | 5.443 | -2.30 | 60.9 | kisitli_uygulanabilir |
| 0.55 | 0.247 | 0.203 | -18.838 | 5.263 | -1.65 | 61.8 | kisitli_uygulanabilir |
| 0.60 **(taban)** | 0.220 | 0.180 | -18.186 | 5.084 | -1.00 | 62.7 | uygulanabilir_kosullu |
| 0.65 | 0.193 | 0.158 | -17.533 | 4.904 | -0.34 | 63.6 | uygulanabilir_kosullu |
| 0.70 | 0.165 | 0.135 | -16.88 | 4.724 | +0.31 | 65.0 | uygulanabilir_kosullu |
| 0.75 | 0.138 | 0.113 | -16.227 | 4.545 | +0.96 | 67.1 | uygulanabilir_kosullu |
| 0.80 | 0.110 | 0.090 | -15.574 | 4.365 | +1.62 | 69.2 | uygulanabilir_kosullu |

- E[TR net 10y] aralığı: **-22.102 … -15.574** (P(C) 0,30 → 0,80).
- Skor aralığı: **57.3 … 69.2**.
- Karar eşiği (skor 62) geçişi: P(C) ≈ **0.561**
- Beklenen karışımda iyileşme (Δ > 0,05) başlangıcı: P(C) ≈ **0.68**
- Taban satır ana raporla tutarlı: True.
