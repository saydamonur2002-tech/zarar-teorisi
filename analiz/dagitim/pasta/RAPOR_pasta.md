# RAPOR_pasta (2014-25). Ön kayıt: ON_KAYIT_pasta.md. Sapma: K2'de makine-teçhizat için TÜİK verisi yerine TCMB sektör paneli (net defter değeri) [VEKİL] kullanıldı; S2(e) d'ye eşitlendi.
Dosyalar: p.py, k3.py, b.py, sentetik_placebo.csv, k3_sektor_test.csv, panel_makine_payi.csv, menu_alt40_uretim.csv, wb_*.csv, pasta.png
Veri: World Bank WDI API (anahtarsız, resmi) [VERİ]; TCMB sektör paneli (yerel); EVDS/EVDS3 kullanılmadı. Repoya yazılmadı.
## S1 Pasta küçüldü mü?
- K1 seviye: kişi başı reel GSYH büyümesi 2014-25 TR %3,70/yıl; emsal: BRA 0,33, CHL 1,03, COL 1,39, HUN 2,99, IDN 3,38, IND 5,04, MEX 0,43, POL 4,04, ROU 3,53, ZAF −0,64 [VERİ]. Sentetik (CHL 0,64 + IND 0,36; ön dönem RMSE 3,8 log puan = zayıf uyum) → TR 2025'te +14,4 log puan ÜSTTE. Kendi 2004-13 trendine göre +6,9 [HESAP]. Placebo: TR fark/RMSE oranı 3,8; 10 emsalin 8'i daha uç → ayırt edilemez. Karar: "seviye küçüldü" TUTMADI (en az emsal kadar büyüdü).
- Ama TR kendi geçmişinden yavaşladı: GSYH büyümesi 2004-13 %6,0 → 2014-25 %4,8.
- K2 bileşim: GSCF/GSYH TR 26,9→29,8 (emsal 23,7→22,6), DiD +3,9 puan → toplam yatırım düşmedi. Makine vekili (imalat+diğer, inşaat/emlak hariç): makine/aktif %14,6 (2014) → %11,0 (2021); makine/GSYH 22,6 → 19,4 [VEKİL]. 2023 sonrası enflasyon muhasebesi kırılması (2024: 30,4) → kullanılmadı. Bileşim inşaata kaymış olabilir [aday]; TÜİK makine-teçhizat serisi bu turda çekilmedi.
- K3 sektör: 2018 finansman gideri/satış sıçraması → 2018-20 makine payı: eğim +0,23, perm p=0,89 (n=71). Placebo 2016 p=0,85; 2021→23 p=0,72. Öncül test (2018 sıçraması → 2016-17) p=0,007: kur kaybı yaşayan sektörler ZATEN önceden makine payı düşüren sektörler → seçilim. TUTMADI.
- Hüküm: aktarım pastayı küçülttü kanıtı YOK; seviye emsale göre iyi, bileşimde makine payı düşüşü var ama firma kur kaybına bağlanamadı. Sonuç: belirsiz/olumsuz. Nedensellik iddiası yok.
## S2/S3 menü: menu_alt40_uretim.csv (havuz P=14,9 %GSYH kümülatif = hane 10,32 + TCMB 1,48 + yurt dışı/artık 3,10)
(tablolar CSV'de; özet kullanıcı mesajında)
## Zayıf noktalar
Sentetik ön-dönem uyumu kötü; WB TR GSYH 2016 revizyonu sonrası seri; makine vekili net defter değeri (amortisman/yeniden değerleme etkisi); alt-40 payı tüketim anketi (WB, 2024-25 yok, varsayım); özel tüketim/GSYH hane geliri vekili; teşvik İKİNCİL; ICOR yöntemi kaba; havuzda yurt dışı satırı güvenilmez artık içeriyor.
