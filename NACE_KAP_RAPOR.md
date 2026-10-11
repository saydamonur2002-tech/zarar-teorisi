# NACE + KAP katman raporu

## 1. Katman tablosu

| Katman | Durum |
| --- | --- |
| Hazne (H,F,B,K,D) | duruyor — `mahsup_sektor_donem.csv` (trilyon TL/ay) |
| NACE bölüm | **test edilemez** — bölüm tablosu yok (TÜİK birincil çekilmedi) |
| KAP kenar | tutarlı tablo görülmedi (0 sayısal kenar); H-M seyrek kol <30 |

## 2. Yanlışlayıcılar

- **H-M (matris eseri):** test_edilemez. Yoğun L^m üst sınır silinen oran (2026-Q1 agregat): 42.7%. Seyrek KAP: yok (0 kenar). Seyrek karşıt yokken %42,7 yoğun üst sınır olarak durur.
- **H-N (NACE bölümleri arası silme farkı):** test_edilemez. Bölüm tablosu olmadan F/B hazne silme oranları (**%18,1 / %95,5**) bu hipotezin sınavı değil; hazne katmanının öncülü. “Firma tek tip” cümlesi NACE ister; bölüm yokken ne düşer ne tutar.
- **H-K (grup içi):** test_edilemez. Karşı taraf / grup eşleşmesi yetersiz.

## 3. NACE araması (düzeltme)

- Denenen EVDS grupları istihdam/sanayi (`bie_rsistihn`, `bie_istihsk4`, `bie_tsny2010`, …) — finansal hesap NACE bölümü değil.
- 2023–2026’da 0 satır, yalnızca o grupların o pencerede boş olduğunu gösterir; NACE’nin var/yok kanıtı değil.
- KAP `abcdCode` sektör/NACE değildir (doğru).
- Asıl kapı: **TÜİK birincil dosya** — bu turda çekilmedi.

## 4. KAP tarama

- Benzersiz bildirim (aylık pencereler): 12000. Başlıkta “ilişkili taraf”: 26.
- `byCriteria` yanıtı **2000/tavan**; tavan kesilmiş aylarda ilişkili taraf metni dışarıda kalmış olabilir.
- HTML gövdede sayı çıkmayan satır → kenar yazılmadı (sentetik doldurma yok). Sonuç: **tutarlı tablo görülmedi**, “bildirim yok” değil.

## 5. Dosyalar

- `nace_bolum_donem.csv`, `kap_kenar.csv`, `mahsup_yogun_seyrek.csv`
- `nace_kap_arama_gunlugu.jsonl`, `kap_universe_kilit.json`

## 6. Sınır ve sonraki risk

D haznesi NACE tablosuna katılmadı. Tahsilat iddiası yok. Olası FR ek PDF/XBRL kenar açarsa önce **grup içi pay**; ilişkili taraf çoğunlukla holding kolu. Seyrek silme oradan düşerse H-M sahte “tutulur”. H-K ayrışmazsa NACE eklemek %42’yi açıklamaz; grup içi bakiyeyi sektörmüş gibi gösterebilir.

Tekrar: `python3 nace_kap_katman.py`
