# Anomali düzeltmeleri ve oturum sınamaları

2026-10-17. Kod düzeltmesi Balkan (ve aynı boşluktaki Azerbaycan refah payı) sürdürme maliyetidir. Diğer üç anomali ve dört oturum sınaması tanı olarak durur; ana skor 47.7 ve E[TR net 10y] −23.117 bu sayıları okumaz.

**Etiket.** **Kanıt:** dosyadaki formülün yeniden hesabı veya dosyadaki ölçülmüş satır. **Aday:** yıl uyumsuz köprü, yeniden kurulumun kendi defter tanımı, ya da φ=1’in ticaret dışı kanalı dışarıda bırakması.

**Commit.** `a1fec7d3ca2f3f4d3310bcfafe7caffd4cad37bc` (`cursor/phi-referans-duyarlilik-d2fe`). PR #33 birleştirilmedi.

**Test.** `simulate` düzeltmesi `1c0407c5fd99bea57e4cd59e9711a1b662708546`. Depo pytest: 130 geçti (kök 30, `hekis_model` ve `mahsup` 100). Etki paketi (`yayin/etki-cephesi-model.zip`, `_incoming` çalışma kopyasına bağlanarak): 78 geçti. `test_simulate_toplami_korur` bu daldaki Balkan commit’inden ve `main`’den önce de düşüyordu: `akis_model.py` ile `L_v2_2026-Q1.csv` / `G_v2_2026-Q1.csv` bu işten önce `main` ile aynıydı. Kök neden kayan nokta birikimi değil. `mat()` satırı 1’e böler; CSV 4 ondalığa yuvarlanınca F satırı 0,9999 kalır. 1e9 şokun ilk adımı tam 100 000 düşer, sonraki adımlar sapmayı 104 894’e taşır (tolerans 1e5). `simulate` yuvarlama artığı 5e-4 içindeyse payları yeniden 1’e oranlar. Bilinçli eksik satır (L_cift, toplam ≈0,83) ölçeklenmez. Düzeltmeden sonra aynı şokta sapma en çok 5e-7. Testin toleransı değiştirilmedi. Zip `_incoming` taşımaz; bağ olmadan aynı test dosyayı bulamaz.

## 1. ABD sınıfı

**Kanıt.** C’de defter: kazanç 1.518, çekim 0.307, φ medyan 3.095, kayıp 0.949, maliyet 0.288, net 0.281, tam bant 0.512. Sınıf bant içi (`net − bant < 0` ve `net + bant > 0`). Aynı satır φ=1 iken (kayıp = çekim): net 0.923, φ yayılımı hariç bant 0.200, sınıf kazanan. Bu, «ticaret-only +0.92±0.20» satırıdır (`PHI_REFERANS_DUYARLILIK.md` φ=1 tablosu, C ABD +0.923 ± 0.200).

| Kalem | A | B | C |
| --- | ---: | ---: | ---: |
| Çekim | 0.456 | 0.751 | 0.307 |
| φ min / med / maks | 1.463 / 3.244 / 5.641 | 1.451 / 3.376 / 7.098 | 1.441 / 3.095 / 4.511 |
| φ=1 net (φ bandı yok) | +1.289 ± 0.220 kazanan | +1.770 ± 0.190 kazanan | +0.923 ± 0.200 kazanan |
| φ medyan nokta net | +0.266 | −0.013 | +0.281 |
| Tam bant | 0.977 | 2.128 | 0.512 |
| Ana sınıf | bant içi | bant içi | bant içi |

Sınıfı kim çeviriyor:

- **A ve C.** Medyan φ noktayı düşürür (C’de 0.923 → 0.281, fark = çekim × (φ−1) = 0.643) ama nokta pozitif kalır. φ yayılımı hariç bantla (C 0.200) hâlâ kazanan (0.281 − 0.200 = 0.081). Tam bant (kayıp belirsizliği 0.471) noktayı yutar. Sınıfı çeviren kalem φ bandıdır, çekimin kendisi değildir.
- **B.** Medyan φ noktayı sıfırın altına alır (+1.770 → −0.013). Kazananlıktan çıkaran kalem φ düzeyidir. Bant, kaybeden etiketini de engeller.

φ, kaybı modelli IR, IL, EG’de model kaybının çekime oranıdır (`projeksiyon.py:709-726`). ABD’nin havza kaybı 0, kapsamı `bilinmiyor` (`test_kaybi_bilinmeyenler_referans_oranla_modellendi`). ABD havzası yok. ABD’ye özgü φ bu vekilde tanımlı değildir: ölçülmüş bir ABD kaybı aynı birimde durmuyor. Bağımsız kalibrasyon o kaydı gerektirir; uydurulmadı.

**Tutarlı tanım.** Ana defter çekim × φ olarak kalır. φ=1 alt sınırdır: ticaret kanalı, ticaret dışı çarpan dışarıda. Ana defterde ABD kazanan denmez.

## 2. Boşluk dolum: hangi tablo

İki koşu aynı tavanı kullanır (bölgesel ihracat / 4785.41). **Kanıt:** `dis_ticaret_gsyh_2023.json` toplamları IR 29746.6, IL 3696.4, EG 15498.7 → 6.216, 0.772, 3.239. TR model ortakları 79690.3 → 16.653 (Comtrade reporter 792, akış X, 2023, HS TOTAL).

Fark iki tanımda.

**Mevcut kazanç tavandan düşer.** Oda = max(0, tavan − kendi P − kendi tam havzasının girişi). C’de oda/V: TR 95.7, IR 26.8, EG 15.3, IL 2.3. Yeniden kurulum T = min(tavan, V) yazar, mevcut kazancı düşmez. C payları 35.7, 18.6, 4.4 bu brüt tavandır (oda değil, tavan/V). TR’de mevcut 0 olduğu için iki pay aynıdır.

**TR C net.** Yayın kaybı −17.191. Brüt iade 16.653 eklenirse −0.538 (yeniden kurulum). Havza girişi çekilince TR’nin Doğu Akdeniz kefalet 0.55, gaz 0.32 ve Karadeniz 0.35 payı da geri alınır: −0.1455. Net iyileşme 16.507, TR net **−0.684**. **Kanıt:** `ulke_havza_pay.json` payları × C `rakip_ikame_gelen` × (2.989 / 3.711). Yeniden kurulumun −0.538’i bu payı ikinci kez TR lehine bırakır.

Tutarlı tablo mevcut-kazanç tanımıdır. Sistem sütunu MFİN oranını sabit tutar (oran serbest bırakılırsa vekil kayıp kazançla ölçeklenir; bu artefakt ayrıdır).

| | A pay | A TR net | A sistem (oran sabit) | B pay | B sistem | C pay | C TR net | C sistem |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| IR | 16.4 | −24.917 | −50.742 | 8.8 | −89.300 | 26.8 | −17.191 | −33.065 |
| IL | 1.0 | −24.917 | −50.695 | 0.2 | −89.284 | 2.3 | −17.191 | −32.971 |
| EG | 9.4 | −24.917 | −50.718 | 4.7 | −89.289 | 15.3 | −17.191 | −33.016 |
| TR | 65.6 | −8.264 | −48.548 | 41.2 | −87.996 | 95.7 | −0.684 | −30.295 |

Taban sistem (düzeltme öncesi) A −50.694, B −89.283, C −32.964. Ölü ağırlık dolumda değişmez (C 13.406 → 13.407, yuvarlama). Rant taşınmadı. Karar skoru bu tabloyu okumaz.

Yeniden kurulumun ön-kayıtlı Ö3’ü (K2a’da TR Δsistem A −0.199, B −0.090) o kurulumun kendi defterine aittir: `g` = net refah + havza kaybı, MFİN oran serbest. **Aday.** Tutarlı tanımın tablosu bu değildir.

## 3. Balkan sürdürme maliyeti

**Kanıt, hata.** Oran κ·pol, birleşik satırda kazancı > 0 olan aktöre yazılır (`projeksiyon.py:671-682`). Balkan beşlisinin birleşik kazancı 0 (`dis_kazanc_vekili` 0), oran yok. Defter kazancı AB satırından %68 bölünür (`uluslararasi_stok_akis_capa.json` `eu_satir_balkan_kanal_pay`, aktörler RS BA BG AL MK). Eski defter bu paya maliyet 0 yazıyordu. AB yalnız kalan %32’sinden ücretleniyordu.

**Düzeltme.** `refah_dis_entegrasyon.py:38-44` ve `:212-215`. Oranı olmayan ve kazancı > 0 olan TR dışı satır, senaryodaki tek oranı (birleşikte yazılı κ·pol) alır. AB’nin kalan payı kendi oranıyla durur; ön-bölünme tabanı ikinci kez yazılmaz.

Azerbaycan Balkan listesinde değildir. C’de defter kazancı refah 0.020, birleşik kazanç 0. Aynı boşluk onu da ücretler: C maliyet 0.004. Sınıf kaybeden kalır.

| | Oran | RS | BA | BG | AL | MK | AZ | Sistem önce → sonra |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| A | 0.14 | 0.049 | 0.053 | 0.053 | 0.053 | 0.053 | 0.005 | −50.694 → −50.96 |
| B | 0.082 | 0.036 | 0.038 | 0.038 | 0.038 | 0.038 | 0.006 | −89.283 → −89.477 |
| C | 0.19 | 0.053 | 0.056 | 0.056 | 0.056 | 0.056 | 0.004 | −32.964 → −33.245 |

Sistem farkı yeni maliyetlerin toplamıdır (A 0.266, B 0.194, C 0.281). AB, ABD, Suudi, İran, İsrail neti değişmez. C’de Suudi kazanan kalır (0.212 ± 0.142). ABD bant içi kalır.

Kısmi bant tabanı (tam kapsam medyanı) C’de 0.143. Bu tabanla C Bulgaristan −0.105 ± 0.143 bant içiyken −0.161 ± 0.143 kaybedene iner. Diğer büyük aktörlerin sınıfı durur. `bant_sinama.py:150-158` kırılma payı p* artık (1 − κ·pol) ile bölünür. C’de AL p*(net=0) 0.488, BG 1.134; taban p 0.68 hâlâ AL’nin üstünde, BG’nin altında.

Test `test_dis_aktor_surdurme_maliyeti` beş Balkan satırında maliyet = oran × defter kazancı diye kilitler.

## 4. İran gelir ödemesi

**Kanıt.** İran `kapsam_disi` (`bolge_birincil_gelir_odemesi.json:134-138`). Verisiz ülke dış bağlama tavanına girmez (`olu_agirlik_ayrisma.py:34`, `:47`). İran’ın defter kazancı bu seriden gelmez: matris × boşluk, sonra refah (`projeksiyon.py:520-527`, `refah_dis_entegrasyon.py:143-159`). C net 0.744 = kazanç 1.260 − havza kaybı 0.277 − maliyet 0.239. Gelir ödemesi bu özdeşlikte yok. Kapsam dışı olmak defter netini şişirmez.

Dış bağlama zararı (vekil, BoP köprüsüyle mn $): A 0.660 / 1709, B 1.131 / 2928, C 0.390 / 1010. Akran ödeme/GSYH (**aday**, ödeme yılı 2025, GSYH 2023): IQ 0.0131, TR 0.0304, EG 0.0491, IL 0.0665. Tavan = oran × İran GSYH 457510.5. En düşük tavan (IQ) 5991 mn $. İran zararı bunu yalnız B’de rant köprüsünde (6088) 98 mn $ aşar, 0.018 vekil. f üç hanede değişmez (B rant 0.771). Diğer senaryo ve köprülerde tavan bağlanmaz.

## 5. Boşluk dolum yanlılık testi

Ön-kayıt (yeniden kurulum, sonuçtan önce): H0 «TR üstünlüğü yanlılık ürünü». Ö1 dolum payında, Ö2 Δsistemde, Ö3 iade kalkınca (K2a) TR Δsistem ≤ 0.

| Ölçüt | Sonuç | Etiket |
| --- | --- | --- |
| Ö1 | TR 10 tarafsız varyantın 9’unda 1.; K6 eşit tavanda berabere | kurulumun kendi sayısı |
| Ö2 | 30 hücrenin 20’sinde TR 1.; çoğunluğu kaybettiği 2 varyant (K1b, K2a) | kurulumun kendi sayısı |
| Ö3 | K2a A −0.199, B −0.090 ≤ 0 | kurulumun kendi sayısı; **aday** tanım |

Ö3 o kurulumda tuttu. Bölüm 2’nin tutarlı tablosunda yabancı adayın oran-sabit Δsistem’i ≤ 0 (sistem iyileşmez); TR’ninki pozitif (C +2.669) ve havza payı geri alındığı için −0.684’te durur. Ölü ağırlık ikisinde de yerinde kalır.

## 6. Ölü ağırlık geri kazanım sınırı

**Kanıt.** `OLU_AGIRLIK_AYRISMA.json`. D = A 20.217, B 34.041, C 13.406. f_max = max(BoP, rant) = 0.957 / 0.860 / 1.000. Geri kazanılabilir üst = ölçüm boşluğu + f_max × belirsiz. Kalan yıkım tabanı = gerçek yıkım + (1−f_max) × belirsiz.

| | D | Üst (geri) | Yıkım tabanı |
| --- | ---: | ---: | ---: |
| A | 20.217 | 12.997 | 7.220 |
| B | 34.041 | 21.716 | 12.325 |
| C | 13.406 | 7.970 | 5.436 |

Tavan kesişimi min(ticaret, üst): IR her senaryoda 6.216 (ticaret bağlar), IL 0.772, EG 3.239, TR A 12.997, B 16.653, C 7.970. Bu tutar kazanç yazılmadan kayıp havuzundan düşülürse TR net A −11.920, B −23.243, C −9.221. Kalan D A 7.220, B 17.388, C 5.436. Sistem (düzeltme öncesi taban + bu düşüm) −37.697 / −72.630 / −24.994. Balkan maliyeti bu özdeşliğe girmez; düzeltme sonrası tabana aynı düşüm eklenirse sistem 0.266 / 0.194 / 0.281 daha düşüktür.

Ülkenin kendi dış bağlaması (ticaret tavanı bağlanmadan, BoP): IR 0.660 / 1.131 / 0.390, IL 0.201 / 0.427 / 0.101, EG 0.771 / 1.428 / 0.440. TR satırı kodda yok (TR atlanır).

## 7. Tampon sızıntı

**Yanlışlama, sonuçtan önce.** «Sızıntı oyunu sürdürür» iddiası şu ise bozulur: s ∈ {0, 1, 2, 5, 10}% içinde kaybı > 0 olan hiçbir aktör net ≥ 0 olmaz, ya da bunu sağlayacak s tamponu 1 yıldan kısa sürede bitirir.

**Kanıt.** Rezerv 2024 brüt, altın dahil: 155548682878.2 USD = 155548.683 mn (`tr_bagimsiz_olcek.json`, `TUR.toplam_rezerv_usd`). Köprüler `gerceklik_realizasyon.json`: BoP 2589.12, mal 4785.41, rant 5383.14 mn USD / vekil. Kayıp havuzu = muhasebe kaybı + havza girişi + TR iç refah (krediler sökülünce). Çekimli havuz buna dış-veri kaybını ekler.

Herkesin kaybı aynı anda kapanır ancak akış = havuz iken. s* = havuz × köprü / rezerv. %10 BoP akışı 6.008 vekil = 15554.9 mn USD/yıl.

| Havuz | A BoP s* / yıl | B | C | %10 BoP kapsama A/B/C |
| --- | --- | --- | --- | --- |
| Havza (çekim yok) | 77.4% / 1.29 | 127.1% / 0.79 | 52.1% / 1.92 | 12.9 / 7.9 / 19.2 |
| Çekimli | 122.6% / 0.82 | 204.4% / 0.49 | 81.0% / 1.23 | 8.2 / 4.9 / 12.3 |

Mal ve rant köprülerinde s* daha yüksektir (C çekimli mal 149.8%, rant 168.5%). Izgaranın hiçbir noktasında kaybı olan aktör net ≥ 0 olmaz. Bunu sağlayacak s* ya %50’nin üstündedir ya da (B havza BoP 0.79 yıl, bütün çekimli köprüler) tamponu 1 yıldan kısa sürede bitirir. **İddia bozuldu.**

Sabit akışta tükenme: %1 → 100 yıl, %2 → 50, %5 → 20, %10 → 10. Stok bitince telafi durur, yıllık net eski kayba döner.

## 8. Kazanç–maliyet

**Yanlışlama, sonuçtan önce.** «Kazananlar maliyeti sıfırlıyor, net kazanç yok» iddiası şu ise bozulur: makul κ ∈ [0.1, 1] ve pol ∈ [0.25, 1] içinde net − bant > 0 kalan aktör vardır. Tersi, aralığın her noktasında kazanan kalmamasıdır.

**Hüküm: belirsiz.** Model noktası κ=0.2’de kazanan vardır (İran üç senaryoda; C’de Suudi). κ=1 ve pol=1’de nokta net kazanan bırakmaz; kalan bant içi MFİN bandı ve C İsrail’dir. Aralığın altı iddiayı bozar, üstü tutar. Bölgesel askeri dilim ölçülmedi; ulusal milis harcaması (WB MS.MIL.XPND.CD, 2024 ABD 1 004 901 mn USD, Suudi 80 331) defter maliyetinin yerine yazılmaz.

κ* = (net + maliyet) / (pol × kazanç), nokta neti sıfırlayan κ. Bantlı eşik daha düşüktür.

| | A net ± bant, κ* | B | C |
| --- | --- | --- | --- |
| ABD | +0.266 ± 0.977, 0.387 | −0.013 ± 2.128, 0.188 | +0.281 ± 0.512, 0.395 |
| Suudi | +0.244 ± 0.252, 0.715 | +0.203 ± 0.502, 0.778 | +0.212 ± 0.142, 0.623 |
| İran | +1.004 ± 0.240, 1.068 | +1.306 ± 0.235, 1.677 | +0.744 ± 0.207, 0.821 |
| İsrail | +0.296 ± 0.178, 0.889 | +0.350 ± 0.205, 1.137 | +0.219 ± 0.126, 0.745 |

C Suudi, model bandının tepesi κ=0.35’te bant içine düşer (κ*_bant 0.340). B İran κ=1 ve pol=0.41’de nokta net +0.599 ile kazanan kalır; pol=1’de kalmaz.

Balkan payına maliyet yazılınca κ* değişmez (G = net + maliyet aynı kalır). Değişen, κ=0.2 noktasının yeri: C BA net 0.033, kendi bantı 0.035, bant içi. AL 0.068 ve MK 0.072 kendi bantlarında (0.035) hâlâ kazanan; kısmi bant tabanı 0.143 onları bant içine alır. Düzeltme öncesi bu üçlünün kendi bantı 0 idi ve nokta kazanan sayılıyordu.

## Değişen dosyalar

Paket `yayin/etki-cephesi-model.zip`:

- Kod: `etki_cephesi/refah_dis_entegrasyon.py`, `etki_cephesi/bant_sinama.py`, `tests/test_etki_cephesi_sfc_revize.py`
- Defter: `DIS_ULKE_REFAH.json`, `DIS_ULKE_REFAH_{A,B,C}.json`, `DIS_ULKE_REFAH_GENIS.json`, `DIS_ULKE_REFAH_GENIS_{A,B,C}.json`
- Türev: `GORECELI_KONUM.json`, `GORECELI_KONUM.md`, `BANT_SINAMA.json`, `BANT_SINAMA.md`, `BOLGE_STOK_AKIS.json`, `BOLGE_STOK_AKIS.md`, `TR_OLCEK_SINAMA.json`, `TR_OLCEK_SINAMA.md`, `HAVZA_KAZANAN_KISA_VADE.json`, `HAVZA_KAZANAN_KISA_VADE.md`, `IKAME_CIFT_SAYIM.json`, `IKAME_CIFT_SAYIM.md`, `SENARYO_RAPOR_{A,B,C}.md`, `SENARYO_KARSILASTIRMA.md`
- Not: `data/etki_cephesi/gozlem/duyarlilik/anomali_2026_10_17.json` (ana model okumaz)

Depo: `yayin/ANOMALI_DUZELTMELERI.md`, `yayin/README.md` (bir dizin satırı), `yayin/PHI_REFERANS_DUYARLILIK.md` (taban cümlesi), yukarıdaki raporların `yayin/` kopyaları, `data/etki_cephesi/gozlem/duyarlilik/anomali_2026_10_17.json`.

Projeksiyon, karar skoru, φ dökümleri ve ölü ağırlık kovaları durur. Stok-akış kurum matrisi (`ULUSLARARASI_STOK_AKIS.json`, IMF/WB) yeniden yazılmadı: sürdürme o matrise girmez.
