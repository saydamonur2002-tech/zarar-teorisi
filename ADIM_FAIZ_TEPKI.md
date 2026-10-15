# Beş adımın faiz düğmesi

Soru: K1 ve K3 kredi freni politika faizini kaydırır mı, o kayma kuru ve Hazine faturasını değiştirir mi?

Zincir: kredi temposu / 2025 GSYH oranı → geçiş LR → enflasyon puanı → AOFM tepkisi → faiz-kur denklemi.
K2 bu zincire girmez. Kapı doldurulmaz. LR nokta tahmini `tahmin_ols` dir.

## Tepki

- Ana pencere 2018-Q1 → 2024-Q4, n=28. ρ **1.000** (se 0.063), β **0.032** (se 0.054). R² 0.870. Uzun dönem türetilmedi, ρ bire yapışık.
- β sıfırın içindedir: se β'dan büyüktür. Ana yolda beş adım AOFM'yi kaydırmaz sayılır; çeyrek katsayısı yine de uygulanır.
- 2023-Q3 → 2024-Q4 rejimi, n=6. ρ 0.537 (se 0.063), β 0.291 (se 0.163). Durağan hali **0.63**: bir puan enflasyon, AOFM'yi 0.63 puan kaydırır.

Tek adım sınavı, ölçülen gecikmeyle:

| Çeyrek | Rejim tahmini | Ölçülen | Fark |
| --- | ---: | ---: | ---: |
| 2025-Q1 | 46.37 | 45.20 | +1.17 |
| 2025-Q2 | 41.81 | 47.41 | -5.60 |
| 2025-Q3 | 41.94 | 43.29 | -1.35 |
| 2025-Q4 | 38.90 | 39.45 | -0.55 |
| 2026-Q1 | 36.36 | 38.18 | -1.82 |
| 2026-Q2 | 35.51 | 40.00 | -4.49 |
| 2026-Q3 | 36.88 | 38.72 | -1.84 |

## Yıl, puan

| Yıl | Kredi puanı, GSYH | Enflasyon puanı | AOFM, ana β | AOFM, 2023 rejimi |
| --- | ---: | ---: | ---: | ---: |
| 2027 | 2.03 | -1.91 | -0.06 | -1.20 |
| 2028 | 3.25 | -3.06 | -0.10 | -1.92 |
| 2029 | 4.79 | -4.49 | -0.14 | -2.83 |

2025 itiş 4820.9 milyar, GSYH payı 7.62. LR 0.94. GSYH yolu yok; oran sabit. Geçiş aynı yıla yazıldı.

## Ne denmez

- Beş adım faizi ölçülmüş biçimde indirdi denmez. Ana β sıfırdan ayrı değildir.
- 2023 rejimi 2025 sınavını tuttu denmez. 2025-Q2 farkı tabloda durur.
- K1 ile K3 Hazine faizine eklendi denmez. İkisi yalnız kredi girdisinde durur.
- Kapı doldu denmez. LR kapıya yazılmadı.
