# OVP çapa

Stok-akışa bağlı değil. `uc_kural_senaryo` parametreleri yazılmaz.

Son yayın: 2027-2029 (2026-09-06).
Önceki yayın: 2026-2028 (2025-09-09).

Senaryodaki `tufe_yol` 0.28 duruyor. OVP program yılları ayrı yüzde-yol olarak durur.

## Çapa

| Değişken | Yıl | Değer | Kaynak |
| --- | ---: | ---: | --- |
| tufe_yil_sonu | 2023 | — | bos |
| tufe_yil_sonu | 2024 | — | bos |
| tufe_yil_sonu | 2025 | 30.89 | evds |
| tufe_yil_sonu | 2026 | 28.4 | ovp |
| tufe_yil_sonu | 2027 | 21.0 | ovp |
| tufe_yil_sonu | 2028 | 13.5 | ovp |
| tufe_yil_sonu | 2029 | 9.0 | ovp |
| gsyh_buyume | 2023 | 5.05 | evds |
| gsyh_buyume | 2024 | 3.48 | evds |
| gsyh_buyume | 2025 | 3.74 | evds |
| gsyh_buyume | 2026 | 3.3 | ovp |
| gsyh_buyume | 2027 | 4.2 | ovp |
| gsyh_buyume | 2028 | 4.6 | ovp |
| gsyh_buyume | 2029 | 5.0 | ovp |
| usd_try | 2023 | — | bos |
| usd_try | 2024 | — | bos |
| usd_try | 2025 | — | bos |
| usd_try | 2026 | — | bos |
| usd_try | 2027 | — | bos |
| usd_try | 2028 | — | bos |
| usd_try | 2029 | — | bos |

## Çapa eksi son OVP hücresi

Geçmiş yıl çapası gerçekleşen seridir. Fark, bu değer ile son yayındaki OVP hücresi arasındadır.

| Değişken | Yıl | Çapa | OVP hücresi | Fark |
| --- | ---: | ---: | ---: | ---: |
| tufe_yil_sonu | 2025 | 30.89 | 30.9 | -0.01 |
| gsyh_buyume | 2025 | 3.74 | 3.7 | 0.04 |

## Revizyon

Tablo iki OVP hücresini karşılaştırır. Çapa tablosundaki EVDS değeri buraya yazılmaz.

| Değişken | Yıl | Son | Önceki | Fark |
| --- | ---: | ---: | ---: | ---: |
| gsyh_buyume | 2024 | — | 3.3 | — |
| gsyh_buyume | 2025 | 3.7 | 3.3 | 0.4 |
| gsyh_buyume | 2026 | 3.3 | 3.8 | -0.5 |
| gsyh_buyume | 2027 | 4.2 | 4.3 | -0.1 |
| gsyh_buyume | 2028 | 4.6 | 5.0 | -0.4 |
| gsyh_buyume | 2029 | 5.0 | — | — |
| tufe_yil_sonu | 2024 | — | 44.4 | — |
| tufe_yil_sonu | 2025 | 30.9 | 28.5 | 2.4 |
| tufe_yil_sonu | 2026 | 28.4 | 16.0 | 12.4 |
| tufe_yil_sonu | 2027 | 21.0 | 9.0 | 12.0 |
| tufe_yil_sonu | 2028 | 13.5 | 8.0 | 5.5 |
| tufe_yil_sonu | 2029 | 9.0 | — | — |

## Doğrulanamayan

- usd_try: OVP Tablo 1.1 kur satırı yok
- tufe_yil_sonu 2023, 2024: bes_yil_senaryo_ham.json Aralık çifti yok (seri 2024-01'den)
