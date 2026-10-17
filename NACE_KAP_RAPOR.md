# NACE + KAP katman raporu

## 1. Katman tablosu

| Katman | Durum |
| --- | --- |
| Hazne (H,F,B,K,D) | duruyor — `mahsup_sektor_donem.csv` (trilyon TL/ay) |
| NACE bölüm | TÜİK YSHİ (GitHub xls) |
| KAP kenar | tutarlı tablo görülmedi (0 sayısal kenar); sayısal kenar 0 |

## 2. Yanlışlayıcılar

- **H-M:** `test_edilemez`. Yoğun L^m üst sınır (2026-Q1): 42.1. Seyrek KAP: yok. Fark (yoğun−seyrek): —. Etiket kümesi: test_edilemez | matris_eseri | hipotez_duser | ters_yon.
- **H-N:** `test_edilemez`. Bölüm silinen_oran ölçülmedi; F/B hazne farkı H-N değil. TÜİK: `NACE_TUIK_RAPOR.md`.
- **H-K:** `test_edilemez`.

## 3. NACE araması (düzeltme)

- Denenen EVDS grupları istihdam/sanayi (`bie_rsistihn`, `bie_istihsk4`, `bie_tsny2010`, …) — finansal hesap NACE bölümü değil.
- 2023–2026’da 0 satır, yalnızca o grupların o pencerede boş olduğunu gösterir; NACE’nin var/yok kanıtı değil.
- KAP `abcdCode` sektör/NACE değildir (doğru).
- TÜİK YSHİ: GitHub `Ekonomik faaliyetlere göre temel göstergeler, 2024.xls` (`python3 nace_tuik_katman.py`).
- Sektör Bilançoları xls GitHub’da yoksa yabancı kaynak payı ve F hazne bölünmesi yapılmaz.

## 4. KAP tarama

- Benzersiz bildirim (aylık pencereler): 12000. Başlıkta “ilişkili taraf”: 26.
- `byCriteria` yanıtı **2000/tavan**; tavan kesilmiş aylarda ilişkili taraf metni dışarıda kalmış olabilir.
- HTML gövdede sayı çıkmayan satır → kenar yazılmadı (sentetik doldurma yok). Sonuç: **tutarlı tablo görülmedi**, “bildirim yok” değil.

## 5. Dosyalar

- `nace_bolum_donem.csv`, `kap_kenar.csv`, `mahsup_yogun_seyrek.csv`, `nace_kap_sonuc.json`
- `nace_kap_arama_gunlugu.jsonl`, `kap_universe_kilit.json`

## 6. Sınır ve sonraki risk

D haznesi NACE tablosuna katılmadı. Tahsilat iddiası yok. Olası FR ek PDF/XBRL kenar açarsa önce **grup içi pay**; ilişkili taraf çoğunlukla holding kolu. Seyrek silme oradan düşerse H-M sahte “tutulur”. H-K ayrışmazsa NACE eklemek %42’yi açıklamaz; grup içi bakiyeyi sektörmüş gibi gösterebilir.

Tekrar: `python3 nace_kap_katman.py`
