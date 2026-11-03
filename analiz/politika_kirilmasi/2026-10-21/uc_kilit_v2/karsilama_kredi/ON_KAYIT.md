# ON_KAYIT — Karşılama oranı ve hanehalkı kredisi
Yazıldı 2026-10-21 ~15:10 TSİ, hesaptan önce. Yorum (parent): asgari ücret tabanı "aynı" varsayılır; karşılama = net asgari ücret / yaşam maliyeti (PR #44 K1, başlangıç 0,574 = 28.075,50 / 48.885). EVDS3 anahtarsız web ön yüzü (BEYAN); anahtar isteyen uç yok; EVDS_API_KEY okunmaz. Nedensellik yok.
## Seriler
- Net AÜ: ucret_kopus/asgari_ucret.csv (RG tarih/sayı) + 2026 PR ASGARI 28.075,50.
- Yaşam maliyeti: PR'da yalnız tek nokta (2026-09, 48.885, TÜRK-İŞ, PR notu "doğrulanmalı") → geriye TÜFE ile taşınır: Y_t = 48.885·P_t/P_2026-09 [VEKİL; reel yaşam sepeti sabit varsayımı]. Karşılama_t = net_t / Y_t.
- Kredi: TP.HPBITABLO6.2 (tüketici kredileri) + TP.HPBITABLO6.16 (bireysel kredi kartı), bin TL, ay sonu (PR'ın kullandığı kodlar). Net akım = Δstok; reel = TÜFE ile 2026-09 fiyatına.
- Açık (kişi başı, aylık) = Y_t − net_t. Asgari ücretli sayısı resmî kaynakta yok → toplam açık yerine "kapsanan kişi eşdeğeri" N* = net kredi akımı / kişi başı açık [HESAP]; finansman oranı ancak N varsayımıyla — N senaryosu: yalnız duyarlılık [DOĞRULANMADI].
## Testler
- Dönem ortalamaları: 2016–17, 2018–20, 2021–23, 2024–26.
- Korelasyon: Δkarşılama (12 ay) ile reel kredi akımı büyümesi, gecikme 0..12; AYAKTA ("karşılama düşünce kredi artar"): en az bir gecikmede ρ<−0,3 ve |t|>2 (HAC). YANLIŞLANDI: tüm gecikmelerde ρ≥0.
- Eşik: reel net akım/ kişi başı açık (N*) serisinde Binseg (ruptures, min 6 ay) ve kırılma tarihlerindeki karşılama düzeyi.
- Kredi tavanı kuklası: resmî tarih bulunamazsa [DOĞRULANMADI], koşulmaz.
- Senaryo duyarlılığı (tek ek): kosu_v4 mantığı, K2 açık (PR) vs K2 kapalı (kilitli yolda tüketici stoku mevcut yol büyümesinde) — K1 değişimi raporlanır; K1 tanımı kredi içermediği için değişmezse "K1 krediye duyarsız (model gereği)" yazılır.
## SAPMALAR (hesap sonrası)
- SK1: EVDS'de TP.HPBITABLO6.2/6.16 yalnız 2024-06'dan var; 2016–2023 kredi akımı bulunamadı → o dönemlerde finansman oranı [DOĞRULANMADI]. Eski BDDK/EVDS kodları doğrulanmadığı için denenmedi.
- SK2: Asgari ücretli sayısı resmî kaynaktan yok → toplam açık ve finansman oranı hesaplanmadı; yerine N* (kredi akımının kapatabileceği kişi-açık eşdeğeri) [HESAP].
- SK3: Kredi tavanı kuklası resmî tarih doğrulanmadığı için koşulmadı [DOĞRULANMADI].
- SK4: Gecikme 2'deki negatif korelasyon (−0,61) Ocak asgari ücret zammından iki ay sonra (Mart) düşük kredi akımıyla çakışıyor (2025-03, 2026-03) → mevsim/takvim artefaktı adayı; hüküm ön kayıta göre AYAKTA yazılır ama "kırılgan" etiketiyle.
- SK5: Binseg N* serisinde kırılma bulmadı (n=27) → eşik yok.
- SK6: K2 duyarlılığı PR calistir'e monkeypatch (yalnız bu betikte): kilitli yolda tüketici/kart büyümesi mevcut oranlara, limit_dondur=False.

## EK v2 (2026-10-21 ~15:45 TSİ, hesaptan ÖNCE)
A) Uzun kredi serisi: sıra BDDK (FinTurk/aylık/haftalık bülten) → EVDS eski kodlar (anahtarsız ön yüz). Doğrulama: 2024-06..örtüşen aylarda |fark|/stok ≤ %1 → aynı tanım; değilse kopukluk yazılır, seri zincirlenmez (yalnız akım oranı ile ayrı rapor). Testler v1 ölçütleriyle uzun seride yeniden: korelasyon (gecikme 0..12; ayrıca Ocak/Mart takvim kuklası kontrollü), Binseg (min 6 ay). Kredi tavanı tarihleri yalnız TCMB/BDDK resmî metinden; yoksa [DOĞRULANMADI]. Asgari ücretli sayısı SGK resmî; yoksa [DOĞRULANMADI].
B) kosu_v5.py (PR kopyası değişmez, calistir kaynağına inspect ile ek): her çeyrek açık_q = (yaşam − taban)·3; net kredi = κ·açık (κ ızgara {0; 0,25; 0,5}; A'dan tahmin varsa eklenir); K2 açıkken kredi büyümesi PR kilitli tavanıyla sınırlanır (net kredi ≤ tavan büyümesi × stok). Kredi→enflasyon: π_q += μ·(net kredi / yaşam·3 ölçekli) — μ ızgara {0; 0,05; 0,1} [TAHMİN] (veriden tahmin yalnız uzun seri bulunursa). Borç stoku B: B_{t+1} = B_t·(1+r/400) + net kredi; servis = r/400·B + B/16 (4 yıl vade varsayımı [VARSAYIM]); r = EVDS tüketici kredisi faizi son değer (bulunamazsa PR APIFON4 + 0 [VEKİL]). Etkin karşılama = (taban − servis/3)/yaşam. K1-etkin: K1 kuralı etkin karşılamayla. Izgara: w{0;0,5;1} × α_geçiş{1,951;0} × λ{0,16;0,409} × κ × μ × K2{açık;kapalı} × faiz{sabit;tepkili}. Hüküm: "K2→K1 görünür" = aynı hücrede K2 açık/kapalı K1-etkin sonucu farklı olan hücre ≥1.
## SAPMALAR v2 (hesap sonrası)
- SV1: BDDK Aylık Bülten Tablo 4 (Tüketici Kredileri, sektör, TL, milyon TL) sayfanın kendi herkese açık AJAX ucu (BasitRaporGetir, anahtarsız) ile 2015-12..2026-08 çekildi; 2026-09 henüz yok. Tek kaynak → zincirleme gerekmedi.
- SV2: v1 hatası: EVDS TP.HPBITABLO6.2 ≈ BDDK satır 12 (tüketici + kart toplamı; fark %1,2), 6.16 ≈ kart (fark %2). v1'de 6.2+6.16 toplanmıştı → kart çift sayıldı, v1 akım/N* ~%50 şişkindi. EVDS–BDDK farkı %1 eşiğini aşıyor → EVDS serisi bırakıldı, BDDK kullanıldı.
- SV3: Kredi tavanı tarihleri resmî metinden çıkarılmadı [DOĞRULANMADI]; SGK asgari ücretli sayısı alınmadı [DOĞRULANMADI] → N* ile kalındı.
- SV4: κ veriden pozitif tahmin edilemedi (akım/stok, açık payıyla NEGATİF ilişkili: −0,080, t −3,7) → ızgara. μ ızgara [TAHMİN].
- SV5: Faiz r = TP.KTF10 2026-10 = 62,12 (kod adı resmî olarak doğrulanmadı) [VEKİL]. Borç dinamiği B_{t+1} = B_t + kredi − B_t/16 (faiz servis içinde ödenir); ON_KAYIT'taki B·(1+r/400) yerine — anapara+faiz servisi etkin karşılamaya girer.
- SV6: K2 açıkken, PR'ın limit_dondur bayrağı açık olduğu çeyreklerde kilitli yolda net kredi = 0; değilse tavan oranı f = max(0, 1−8/π_yıllık).
