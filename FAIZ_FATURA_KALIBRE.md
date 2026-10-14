# Faiz faturası kalibrasyonu

Soru: özel dış borç akışı durursa 2026 faiz ödeneği sabit kalır mı?

Kimlik: iç faiz = r_ic × iç stok. Dış faiz = r_dis × (kamu brüt dış borç USD × kur). Diğer = r_diger × iç stok. r, 2025 yılından çözülür.

## Kalibrasyon

- İç stok 2026-06: **9013.9 milyar TL** (`TP.KB.A09`, çeyrek sonu). SBB Haziran iç stok 9.010,5. Fark 3.4.
- 2025 EVDS faiz toplamı **2054.4 milyar TL**. SBB gerçekleşmesi 2054.4. Fark 0.0.
- 2025 kuponu: iç **%22.65**, dış **%3.31** (kamu USD × kur üzerinden), diğer **%3.18**.
- 2024 kuponu 2025 stokuna uygulanınca fatura **2058** çıkar. Ölçülen 2054. Sapma **0.2%**. İç kupon %21.4'ten %22.6'e çıkmış, dış ve diğer kupon gerilemiş, toplam kapanmıştır.
- 2026 ilk yarı ölçüm **1464**. Düz yarıyıl kuponu **1285** verir. Sapma **-12.2%**. 2025'te ilk yarı yılın %54'ünü taşımıştı. Yıl toplamı bu mevsimle ayrı tutulur.

## Eğim, 2024-Q4 → 2026-Q2

- İç stok **+675.7 milyar TL/çeyrek**.
- Kamu brüt dış borç **+4.06 milyar USD/çeyrek**. Özel **+10.83**. TCMB **-1.93**.
- Kur çarpanı **çeyrek başına %4.68** (çeyrek ortalaması USD/TRY).
- Uzun pencere 2023-Q4 → 2026-Q2 özel eğim +7.97 milyar USD/çeyrek. İleri hesap son tempoyu kullanır.

## 2027 faturası, milyar TL

| Yol | İç | Dış | Diğer | Toplam | 2026 ödeneğine fark |
| --- | ---: | ---: | ---: | ---: | ---: |
| Mevcut tempo | 2730 | 400 | 383 | **3513** | +771 |
| Aktarım durdu (özel USD akışı 0) | 2730 | 400 | 383 | **3513** | +771 |
| Kamu USD ve kur donuk, iç stok yürür | 2730 | 298 | 383 | **3410** | +669 |
| İç stok, kamu USD ve kur donuk | 2041 | 298 | 286 | **2625** | -116 |

2026 modeli, mevcut tempoda **2744**. Ödenek 2742. Mevsimle şişirilmiş ilk yarı (2025 payı) **2707**.

Aktarımın durması ile mevcut tempo arasındaki fark **+0.0 milyar TL**. Özel USD stoku faturaya girmez. Faturaya giren dış stok kamu brüt dış borcudur.

Donuk Haziran 2026 stokundan 2027 mevcut yola fark **+888**. Tek tek açılınca iç stok **+785**, kur **+68**, kamu USD **+27**. Üçü birlikte +881 eder. Kalan, üçünün aynı anda yürümesindendir.

## Ne denmez

- İlk yarı sapması yıl sapmasıdır denmez. 2026 model yılı ödeneğin üstündedir, fark 2 milyar TL mertebesindedir.
- Özel dış borç durunca Hazine faizi sabitlenir denmez. İki yolun toplamı aynıdır.
- Beş adım kuru veya politika faizini indirdi denmez. Kur eğimi ölçülmüş çeyrek ortalamasıdır. Faiz model etkisi `modellenmedi`.
- Kamu brüt dış borç = merkezi yönetim dış borcu (Haziran 2026: 128,2 milyar USD) denmez. Bütçe dış faizi, kamu stokunun üstünden kalibre edildi.
