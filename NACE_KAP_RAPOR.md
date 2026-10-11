# NACE + KAP katman raporu

## 1. Katman tablosu

| Katman | Durum |
| --- | --- |
| Hazne (H,F,B,K,D) | duruyor — `mahsup_sektor_donem.csv` |
| NACE bölüm | **bulunamadı** — EVDS NACE/istihdam serileri 2023–2026 boş |
| KAP kenar | 0 kenar — **test edilemez** (<30) |

## 2. Yanlışlayıcılar

- **H-M (matris eseri):** test_edilemez. Yoğun silinen oran (2026-Q1 hazne agregat): 42.7%. Seyrek KAP: nan% (0 kenar).
- **H-N (yük yeri):** tutmuyor. F silinen oran 18.1%, B 95.5%.
- **H-K (grup içi):** test_edilemez. Grup içi pay ayrıştırması yapılmadı (karşı taraf eşleşmesi yetersiz).

## 3. Dosyalar

- `nace_bolum_donem.csv`, `kap_kenar.csv`, `mahsup_yogun_seyrek.csv`
- `nace_kap_arama_gunlugu.jsonl`, `kap_universe_kilit.json`

## 4. Sınır

KAP evreni kilit dosyasında. XU100 listesi bulunamadı. D haznesi NACE tablosuna katılmadı. Alıntılar ≤15 kelime. Brüt üst sınır dili: mahsup sonrası agregat brüt servis akışı düşer; tahsilat iddiası yok.

Tekrar: `python3 nace_kap_katman.py`
