# Faz 5 — Geçiş payı kapısı: band daraltma (OLS + Newey-West)

Çalıştır: `python3 gecis_payi_band.py`. Çıktı: `gecis_payi_ham.csv`, `gecis_payi_band.csv`, `gecis_payi_band_sonuc.json`.

`tavan_akis.csv` gecis/tavan boş kalır; kapı kilitli. Burada üretilen sayı ekonometrik tahmindir (`tahmin_ols`): birincil ölçüm değil, kapıya taşınmaz; bes_yil bandını daraltmak için ayrı satırda durur.

## Model

- π_t = 400·Δlog TÜFE; kredi_t = 100·F.4 akım/GSYH (çeyrek); kur_t = 100·Δlog USD/TRY.
- π_t = α + mevsim + Σ_{k=0..2} b_k kredi_{t−k} + c_0 kur_t + c_1 kur_{t−1} + ρ π_{t−1} + ε; LR = Σb/(1−ρ); NW(4) se; delta yöntemi.
- Band = CI95 ∩ [0,1]. Yorum: 1 puan GSYH kredi akımı → LR puan yıllık TÜFE.

## Tahminler

| spesifikasyon | örneklem | n | R² | Σb | ρ | LR | se | CI95 | band95 ∩ [0,1] | band68 ∩ [0,1] | bes_yil puan (68) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tam örneklem (2015-Q3+), dinamik | 2015-Q3..2025-Q4 | 42 | 0.75 | 0.5152 | 0.4513 | 0.9389 | 0.7418 | [-0.5151, 2.3929] | [0.0, 1.0] | [0.1971, 1.0] | [-7.62, -1.5] |
| tam örneklem (2015-Q3+), statik | 2015-Q3..2025-Q4 | 42 | 0.627 | 0.8077 |  | 0.8077 | 0.604 | [-0.3762, 1.9916] | [0.0, 1.0] | [0.2037, 1.0] | [-7.62, -1.55] |
| tam örneklem, k=0..1, dinamik (az parametre) | 2015-Q3..2025-Q4 | 42 | 0.743 | 0.2256 | 0.4662 | 0.4226 | 0.6132 | [-0.7793, 1.6244] | [0.0, 1.0] | [0.0, 1.0] | [-7.62, -0.0] |
| 2018+ (kur şokları), dinamik | 2018-Q1..2025-Q4 | 32 | 0.765 | 0.9111 | 0.3653 | 1.4355 | 0.8149 | [-0.1616, 3.0326] | [0.0, 1.0] | [0.6206, 1.0] | [-7.62, -4.73] |
| 2021+ (yüksek enflasyon), dinamik | 2021-Q1..2025-Q4 | 20 | 0.896 | 1.2231 | 0.0351 | 1.2676 | 0.7626 | [-0.227, 2.7623] | [0.0, 1.0] | [0.5051, 1.0] | [-7.62, -3.85] |

- RAPOR 'üçte biri' (0.333) varsayımı ana CI95 içinde mi: **evet**.
- bes_yil enflasyon bandı: mevcut [−7.62, 0] → daraltılmış **[-7.62, -0.0]** puan (95, ana tahmin); 68 bandı **[-7.62, -1.5]** puan. `bes_yil_senaryo` dosyaları yazılmadı.
- Sonuç: tek sayıya inmez. Nokta tahmin LR 0.94 (tam geçişe yakın) ama se 0.74; 95 bandı [0,1]'i daraltmaz, 68 bandı alt ucu 0'dan kaldırır. Kredi katsayıları her spesifikasyonda pozitif; kesinlik yok.

## Sınırlar

- Kredi akımı içsel (enflasyon krediyi de etkiler); OLS geçiş payı nedensel değil. Kur ve gecikmeli π kontrol; araç değişken yok.
- Örneklem rejim değiştiriyor (2018 kur şoku, 2021+ yüksek enflasyon); alt örneklem satırları bunun için.
- F.4 akımı 2015-Q1 öncesi yıllık (Q4'e yazılı), çeyrek yok; TP.FG.J0 (2003=100) 2026'da bitiyor → örneklem 2015-Q3..2025-Q4.
- Band tek sayıya inmez; se bunu söyler. Daralan band kapıya yazılmaz; kapı birincil ölçüm ister.
