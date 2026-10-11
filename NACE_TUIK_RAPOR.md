# TÜİK NACE katman raporu

## 1. İndirilen / kullanılan dosya

| Kaynak | Dosya | Tablo | Yıl | NACE |
| --- | --- | --- | --- | --- |
| YSHİ (faaliyet) | Ekonomik faaliyetlere göre temel göstergeler, 2024.xls | `t2` | 2024 | Rev.2 kısım |
| Sektör Bilançoları | bulunamadı (GitHub) | — | 2024 | — |

Bülten: [YSHİ 2024](https://data.tuik.gov.tr/Bulten/Index?p=Yillik-Sanayi-ve-Hizmet-Istatistikleri-2024-54051). Sektör bilanço bülteni: [https://data.tuik.gov.tr/Bulten/Index?p=Sektor-Bilancolari-2024-54080](https://data.tuik.gov.tr/Bulten/Index?p=Sektor-Bilancolari-2024-54080).

## 2. Çıktı

- `nace_tuik_agirlik.csv` (64 satır)
- `nace_bolum_donem.csv` (F hazne bölünmesi yalnız yabancı kaynak payı varsa)

## 3. H-N

**test_edilemez** — silinen_oran bölüm bazında ölçülmedi; F/B hazne yüzdeleri H-N sınavı değil.

## 4. Kapsam dışı / pay uyumsuz

- Kapsam dışı (A,K,O): (tabloda yok)
- pay_uyumsuz (ciro vs yabancı kaynak >10 puan): — (bilanço payı yok)

## 5. Arama günlüğü

`nace_tuik_arama_gunlugu.jsonl`

```bash
python3 nace_tuik_katman.py
```
