# Gidişat raporu (güncel EVDS verisiyle)

Veri: TCMB EVDS3 (anahtarsız), son gözlem: ödemeler dengesi ve bütçe 2026-08, rezerv 09-10-2026, TÜFE 2026-08. Ham seriler `gidisat_ham.csv`. 12 aylık kayan toplamlar mn $ (cari ve yatırım geliri) ve oran (faiz/gelir).

## 1. Dış denge

| 12 aylık | 2024-12 | 2025-06 | 2025-12 | 2026-06 | 2026-08 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Cari işlemler (mrd $) | -13.6 | -24.6 | -30.3 | -39.7 | -42.1 |

- Mal ihracatı 12a 267.2 → 275.2 mrd $ (%+3.0); ithalat 329.5 → 353.6 (%+7.3). İthalat ihracattan hızlı büyüyor.
- Yatırım geliri dengesi (net, 12a): -17.5 → -23.4 mrd $ (+34%); gider (brüt) 26.5 → 32.8 mrd $.

## 2. Rezerv

- Toplam rezerv: 05-01-2024 139.6 mrd $ → son 26 haftanın zirvesi 21-08-2026 188.4 → son 09-10-2026 171.6 mrd $. Son 4 haftada -7.1 mrd $ (-4.0%).
- Rezerv / 12 aylık cari açık: 4.1 yıl.

## 3. Faiz yükü ve enflasyon

- Merkezi yönetim faiz giderleri / gelirleri (12a): %14.6 (2024-12) → %16.9 (2025-08) → %16.0 (2025-12) → %16.7 (2026-08).
- TÜFE yıllık (2026-08): %31.5.

## 4. Hane ve kredi (kullanıcı verisi ve haber aktarımı; resmî kaynaklardan doğrulanmadı)

- Hane borcu / harcanabilir gelir %25 (TCMB Finansal Hesaplar 2026-I), borç/GSYİH %10,1, konut kredisi/GSYİH %1,1.
- BDDK haftalık bülten (2 Ekim 2026, yıllık değişim): takip oranı konut %0,21 (+5 bp), taşıt %1,32 (+72), ihtiyaç %6,33 (+140), tüketici %4,86 (+112), bireysel kart %5,35 (+129), sektör %3,09 (+77).
- Konut kredisi borçlusu (TCMB Risk Merkezi, tekil): 2,5 mn (2020) → 1,7 mn (2025-09); TBB konut bakiyesi 525 → 728 mrd TL (Haz 2025 → Haz 2026), borçlu sayısı %-8. Stres konutta değil, ihtiyaç ve kartta.

## 5. Model: güncel çapalarla duyarlılık

Yöntem: repodaki 2024 çapalarının (yatırım geliri gideri 18.841, ihracat 261.925, ithalat 344.100 mn $) EVDS ödemeler dengesi serilerindeki 12 aylık büyüme çarpanlarıyla (2024-12 → 2026-08) ölçeklendiği bir yan koşu: ihracat ×1,0688, ithalat ×1,1282; yatırım geliri gideri iki tanım için ×1,237 (brüt gider) ve ×1,343 (net denge). Tanımlar farklı kaynaklardan (TİM/Hazine ve TCMB ödemeler dengesi) geldiği için düzey değil büyüme oranı uygulandı. Resmî çapalar 2024'te bırakıldı; bu bir yeniden kalibrasyon değil duyarlılık koşusudur. Tabanlar (0,70 / 0,25 / 0,22) aynen.

| Çapa | Zarar tavanı (mn $) | Finans tavanı (mn $) | Finans gerçekleşme | TR net 10y (C) | Skor | Karar |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 2024 çapası (repo) | 1507.3 | 1884.1 | 0.2186 | -13.429 | 47.7 | kisitli_uygulanabilir |
| yatırım geliri gideri ×1,237 (brüt gider, 12a 2026-08) | 1864.5 | 2330.6 | 0.2705 | -13.38 | 48.0 | kisitli_uygulanabilir |
| yatırım geliri gideri ×1,343 (net denge, 12a 2026-08) | 2024.2 | 2530.3 | 0.2936 | -13.358 | 48.2 | kisitli_uygulanabilir |

**Okuma:** Çapalar güncellenince zarar ve finans tavanları büyür (yatırım geliri gideri arttığı için); finans gerçekleşmesi 0,219 → 0,271–0,294 yükselir çünkü otomatik oran tabanın (0,22) üstüne çıkar. Zarar gerçekleşmesi 0,665'te kalır çünkü zarar tabanı (0,70) hâlâ bağlayıcıdır. Skor 47,7 → 48,0–48,2, karar `kisitli_uygulanabilir` aynı; 45 çizgisine marj 2,7 puandan 3,0–3,2 puana çıkar. Yani güncel dış denge verisi (daha yüksek yatırım geliri gideri) modelin sonucunu zayıflatmıyor; sınırlı iyileştiriyor, ama bu iyileşme tavan hesabının mekaniğinden geliyor (gider arttıkça tavan büyür), gerçek bir iyileşme değil. Karar hâlâ zarar tabanına bağlı (eşik 0,513).

