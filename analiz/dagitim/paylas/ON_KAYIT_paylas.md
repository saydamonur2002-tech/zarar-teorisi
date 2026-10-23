# ON_KAYIT_paylas — hesaptan ÖNCE yazıldı (2026-10-23 17:44 TSİ)
Amaç: 2014–25 kümülatif, %GSYH reel, + = kazanç. İki senaryo:
S1 GERÇEK (erteleme) = eksik/tablo_aktor_kanal_tam.csv NET (VH hariç) kanalları: k1 TL erime, k2 kur, k3 KKM, k5 senyoraj, k7 banka altını, k8 swap.
S2 KARŞI-OLGU (dondur/tanı) [VARSAYIM, statik muhasebe, davranış değişmez]:
 a) KKM yok → k3=0 (aktarım hiç olmaz).
 b) Negatif reel faizle erime yok (piyasa reel faizi ≥0) → k1=0.
 c) Kur zararları sahibinde kalır → k2 aynen (kur yolu aynı varsayılır; en zayıf varsayım).
 d) Senyoraj, altın, swap aynen.
 e) TCMB'nin S2'de negatif çıkan yılları Hazine bütçesinden sermaye ile kapatılır (TCMB o yıl 0, Hazine −aynı tutar).
Aktörler: hane alt40/orta40/üst20 (hane3 ANA anahtarları, kanal bazında); firma KOBİ (MIKRO+KUCUK+ORTA) / BÜYÜK, TCMB sektör bilançoları (GELTAB/BILANCO, GENEL hariç, 2014–23; 2024–25 için 2023 payı [VARSAYIM]): k2 → net kambiyo zararı payı, k1 → mali borç payı, k3 → hazır değerler payı [VEKİL]; banka tek; kamu = Hazine + TCMB, bütçe satırlarıyla.
Ölçütler:
P1 S2'de üst20, S1'e göre kaybeder (S2−S1 < 0) → tuttu/tutmadı.
P2 S1'de KOBİ aktif başına kaybı büyükten fazla (|KOBİ/aktif payı| > |BÜYÜK/aktif payı|, ikisi de negatifse).
P3 S2 görünür bütçe maliyeti (TCMB sermaye + KKM'siz Hazine farkı) < S1 gizli maliyet (Hazine KKM + TCMB negatif yıllar + k1 ile hanelerden alınan) → "erteleme daha pahalı ama görünmez" adayı.
P4 S2−S1 farkının işareti: erteleme kazananı = S1−S2 > 0 olan aktör(ler); en büyük kazanan üst20 değilse P1 ile birlikte raporlanır.
Nedensel iddia yok; S2 bir muhasebe karşı-olgusudur, gerçekleşebilir bir politika simülasyonu değil.
