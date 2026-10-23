# ON_KAYIT — karsi_olgu (veri çekilmeden önce yazıldı, 2026-10-23 TSİ)
H: Zarar birikimi, maliyeti üst gelir/sermayenin taşımamasından kaynaklanır.
Rakipler: R1 dış şok (kur değer kaybı, ABD faizi, emtia); R2 para politikası (negatif reel faiz, KKM benzeri); R3 kurumsal/muhasebe (kayıt dışı yükümlülük, KÖİ).
Epizodlar (t0): TUR 2018, ARG 2018, BRA 2015, EGY 2016, EGY 2022, ZAF 2015, IDN 2013, IDN 2018, MEX 2015, CHL 2019, COL 2015, HUN 2008.
Pencere: t0-2..t0-1 (öncesi) vs t0..t0+3 (sonrası).
Şok: kur değer kaybı (LCU/USD, t0-1→t0+1, %) [HESAP], ABD 10y faiz değişimi ortak, emtia: ÖLÇÜLMEDİ (yoksa).
Yük vekili Y (üste yük): Δ(üst %10 gelir payı) ≤0 ve Δ(dolaylı vergi payı) ≤0 → "üste paylaştıran". Sürekli skor: −Δtop10 − Δdolaylı.
Sonuç S: enflasyon (sonrası ort.), Δ faiz gideri/gelir, NPL değişimi, toparlanma = kişi başı GSYH şok öncesi düzeye dönüş yılı.
R2 vekili: sonrası ort. reel faiz (WB). R3: ölçülemez ise ÖLÇÜLMEDİ.
Testler: (a) şok terciline göre eşleştirip Y-iyi vs Y-kötü sonuç sıralaması; (b) S~şok+R2 sonra +Y: R² artışı, kısmi korelasyon (n≈12, yorum sınırlı); (c) sentetik kontrol: n küçük, veri yetersizse YAPILMADI.
Yanlışlama: şok/R2 sabitken Y ile S ilişkisi işaret olarak H'ye ters ya da R² artışı <0.05 → H desteklenmez. Destek: kısmi korelasyon H yönünde |r|≥0.5 ve R² artışı ≥0.15 ve (a)'da tutarlı. Arası Belirsiz.
Nedensellik yok; ters nedensellik (kötü sonuç dağılımı bozar) not edilecek.

## SAPMA-1 (2026-10-23 22:40 TSİ, ilk sonuç "Belirsiz" görüldükten SONRA eklendi)
Drive'dan wdi_wid_birlesik_panel_dolu.csv (WID emek_payi, ust10_gelir_payi; ISO2) alındı. Değişiklik: Y2 = −ΔWID_üst10 + ΔWID_emek_payı − Δdolaylı (puan; pencere aynı). Kalite bayrağı ≤1 olan yıllar hariç tutulan ikinci duyarlılık koşusu. Eşikler ve karar kuralı DEĞİŞMEDİ. Sonuç görüldükten sonra eklendiği için doğrulayıcı değil, keşifsel sayılır.
