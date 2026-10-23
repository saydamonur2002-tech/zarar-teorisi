# RAPOR_borc — varlık/ücretten borca kayış (2015-25 kümülatif, % GSYH)
Ön kayıt: ON_KAYIT_borc.md; sapma: SAPMA_borc.md. Kod b.py; tablo_borc.csv, yil_borc.csv, borc.png.
## Tablo (ANA anahtar)
| Aktör | A ücret net | A ücret brüt | A finans | A net top | B nominal | B reel | B/A nominal | B/A reel |
|---|---|---|---|---|---|---|---|---|
| Alt40 | −1,67 | −3,67 | −0,92 | −2,60 | 4,32 | 1,00 | 1,67 | 0,38 |
| Orta40 | −3,58 | −7,84 | −1,78 | −5,36 | 10,27 | 2,37 | 1,92 | 0,44 |
| Üst20 | −4,77 | −10,45 | −2,35 | −7,12 | 14,67 | 3,39 | 2,06 | 0,48 |
| Hane toplam | −10,03 | −21,95 | −5,05 | −15,08 | 29,26 | 6,76 | 1,94 | 0,45 |
| Firma | (+10,03 kazanç) | | −10,58 kur | −10,58 | 141,5 | 47,3 | 13,4 | 4,5 |
Ücret: AMECO ALCD0 [VERİ]; finans: hane3 k1+k5 [HESAP]; borç: finansal hesaplar F.4 [VERİ, EVDS3 anahtarsız uç, 2026-10-07]; anahtarlar [VEKİL]; B reel, B/A [HESAP].
Hane borcu/GSYH stok 18,5 (2014) → 9,9 (2025) [HESAP]. 2022: ücret payı −10,4 puan, reel yeni borç ≈0.
BDDK 2019-25 bireysel net yeni borcun %90,6'sı ihtiyaç+taşıt+kart, %9,4 konut [VERİ/HESAP].
## Kriterler
K1 alt40 B/A > üst20: ANA 1,67<2,06 TUTMADI; K_tüketim duyarlılığında 2,42>1,54 tutuyor → anahtara bağlı, TUTMADI.
K2 yeni borcun >%50'si tüketim: %90,6 TUTTU (2019-25, yalnız banka).
K3 ücret payı düşüşü ↔ tüketici kredi reel büyümesi: corr = −0,17 (n=6) TUTMADI.
K4 firma B > |A_kur|: TUTTU (nominal 141,5; reel 47,3) [aday; nominal akım döviz borcunun kur değerlemesini içerir].
## Hüküm [aday]
Ücret kaybının yalnız ~%45'i (reel) borçla ikame edildi; reel hane borç stoku yarıya indi. "Kaybolan ücret borçla kapatıldı" genel olarak tutmuyor; yeni borç ise ağırlıkla tüketim. Nedensellik iddiası yok.
## Zayıf noktalar
Grup anahtarları gelir/tüketim akımı + ikincil yaygınlık (2021 TÜİK yaşam memnuniyeti, dergipark aktarımı; gelir dilimi ≈ beşte bir VARSAYIM). AMECO 2025 tahmin içerebilir. Ücret payı düşüşü tüm hanelere gelir payıyla dağıtıldı (ücretli olmayanlar dahil). Firma kur kaybı ile F.4 değerlemesi çift sayım riski. Hazine dahil edilmedi.
