# TÜİK NACE katman raporu

## 1. İndirilen / kullanılan dosya

| Kaynak | Dosya | Tablo | Yıl | NACE |
| --- | --- | --- | --- | --- |
| YSHİ (faaliyet) | Ekonomik faaliyetlere göre temel göstergeler, 2024.xls | `t2` | 2024 | Rev.2 kısım |
| Sektör Bilançoları | Ekonomik faaliyetlere göre firmaların referans yıl bilanço hesapları .xls | `t2` | 2024 | Rev.2 kısım (sütun) |

Bülten: [YSHİ 2024](https://data.tuik.gov.tr/Bulten/Index?p=Yillik-Sanayi-ve-Hizmet-Istatistikleri-2024-54051). Sektör bilanço bülteni: [https://data.tuik.gov.tr/Bulten/Index?p=Sektor-Bilancolari-2024-54080](https://data.tuik.gov.tr/Bulten/Index?p=Sektor-Bilancolari-2024-54080).

## 2. Çıktı

- `nace_tuik_agirlik.csv` (149 satır)
- `nace_bolum_donem.csv` (F hazne brüt çıkışı yalnız yabancı kaynak payıyla bölündü; `brut_cikis_sonra` ve `silinen_oran` boş)

## 3. H-N

**test_edilemez** — `silinen_oran` ve `brut_cikis_sonra` bölüm bazında boş. F hazne silmesi yapıştırılmadı. F/B hazne yüzdeleri H-N sınavı değil.

## 4. Kapsam dışı / pay uyumsuz

- Kapsam dışı (A,K,O): A
- pay_uyumsuz (ciro vs yabancı kaynak >10 puan): F, G

## 5. Arama günlüğü

`nace_tuik_arama_gunlugu.jsonl`

```bash
python3 nace_tuik_katman.py
```
