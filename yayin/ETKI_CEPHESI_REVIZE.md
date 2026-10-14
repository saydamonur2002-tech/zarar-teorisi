# Etki cephesi modeli: revize sonucu

Kaynak: `zarar-teorisi` dalı `cursor/odeme-zinciri-kalicilik-f01a`, `yayin/etki-cephesi-model.zip`.
Doğrulama: yama temiz zip çıkarımına uygulandı, `run_all.py` tek komutla kararlı duruma vardı (özet `5a66f0878458f83e`, temiz kurulumda 3 geçiş),
**53 test geçti** (27 mevcut + 26 yeni; bir mevcut testin işareti güncellendi). Orijinal pipeline zip'teki raporları birebir yeniden üretiyor
(fark yalnız CRLF/LF ve bir Windows yol ayracı).

## Düzeltilen hatalar

| # | Hata | Düzeltme |
|---|---|---|
| 1 | `stok_silim_tavan` (0,2582, üst sınır, başka nesne) gerçekleşmiş silinme gibi uygulanıyordu: F.4 25.339,8 → 18.797,1 | Baz yol sabit, silinen ölçülmedi. 0 / 0,10 / 0,20 varsayım bandı. 0,2582 yalnız tutarlılık kontrolü |
| 2 | λ = 0,7181 = 1 − 0,0728/0,2582 (iki üst sınırın oranı) `simulate`'e λ diye gidiyordu | λ açık senaryo parametresi, varsayılan 0,5, bant 0,25/0,5/0,75 |
| 3 | Karşı bacağı tanımsız "refah" darbeleri SFC'ye girip tüm sektörleri artıya çekiyordu (Σ = +0,586 tr TL) | `dissal` işareti: SFC dışında raporlanır, kapanış farkı ilan edilir |
| 4 | 2026-Q1 matrisi 2024 ortalama kuruyla (32,87) çevriliyordu | Matris dönemi kuru (2026-Q1 = 44,38) |
| 5 | Finans katmanı işaret dönüşü ölçüm gibi yayınlanıyordu | "varsayım çarpanlı ham" etiketi |
| 6 | Uygulanabilirlik özeti sabit metindi ("10 yılda TR net iyileşir") | Özet sayıdan türetilir; beklenen karışımda iyileşme yoksa engel olarak yazılır |
| 7 | Pipeline kendi çıktısını girdi okuyor: yamalı sürümde tek koşu ara durum bırakıyordu | `run_all.py` kararlı duruma kadar geçer (en çok 5), `RUN_ALL_KARARLILIK.json` yazar |
| 8 | **D'nin çift muamelesi:** dış rant F'ye "zarar" yazılıp L ile D'ye kayıp yayılıyordu (D −0,223) ve ayrıca "D kârı" G ile yerli sektörlere dağıtılıyordu (D'de kalmıyordu) | Rant **F→D transferi**: F −A, D +A, doğrudan NFP, toplam sıfır. Ödeyen F, transfer payı %100 (kullanıcı kararı): 22.550 mn $ × 44,38 = 1,001 tr TL; kapsam dışı rant yok. `bolge_stok_akis` TR net = H+F+B+K (eski formül D'yi 0,45 ile ayrıca düşüyordu) |
| 9 | Olasılık atamasının sonuca bağımlılığı görünmüyordu | `OLASILIK_DUYARLILIK` raporu (aşağıda); `degerlendir()` isteğe bağlı `olasilik` parametresi aldı, varsayılan davranış aynı |

## Önce / sonra (kararlı durum)

| Çıktı | Önce | Sonra |
|---|---|---|
| SFC entegre etki H/F/B/K/D (tr TL) | 0,119 / 0,153 / 0,088 / 0,117 / 0,109 (Σ +0,586) | **0 / −1,001 / 0 / 0 / +1,001 (Σ 0)** |
| SFC kapanış | beyan yok | **kapanış_ok = True** (Σ darbe 0) |
| Senaryo başına D'ye giden rant A / B / C (tr TL) | −0,134 / −0,540 / +0,109 (eski işaret: D kayıp taşıyordu) | **1,886 / 3,482 / 1,001** (C en az, B en çok kaçırır) |
| Bölge: TR sfc_net | +0,223 | −1,001 |
| Dışsal enjeksiyon (SFC dışı) | SFC'nin içindeydi | +0,892 tr TL, ayrı raporlanıyor |
| F.4 stok, 2036 | 18.797,1 mr TL | 25.339,8 (baz); bant 22.805,8 / 20.271,8 |
| Finans katmanı TR net (vekil) | +0,241 (sıfır yılı 2035) | **−0,489** (2037) |
| Zarar-çözüm katmanı TR net | −11,112 | −13,113 |
| Beklenen TR 10 yıl | −16,666 | −18,186 |
| Uygulanabilirlik skoru / C / beklenen | 66,4 / 71,3 / 57,3 | **62,7** / 67,1 / 54,5 |
| Senaryo skorları A / B / C | 51,0 / 50,3 / 79,7 | 50,1 / 49,4 / 73,0 |
| C yolu TR net, 10. yıl (taban → son) | −17,19 → −11,80 | −17,19 → −13,10 |
| Beklenen karışımın iyileşmesi | +0,087 skor (özet "iyileşir" diyordu) | −1,00 vekil: iyileşme yok, engel olarak yazıldı |
| Lm × rant, kur | 32,87 | 44,38; kapanış_ok = False (Σ x = +0,178) |

Not: bu tablo P(C)=0,60 ile. P(C) kapılara bağlanınca skor 58,8 (finans kalibre yola da bağlıyken) ve karar `kisitli_uygulanabilir` (aşağıda).
| 10 | C'nin gerçekleşmesini ölçen bir ölçüt yoktu | `c_dinamik_olcut.py`: sıralı Bayes, EVDS merkez sızıntı oranı; güç analizi (aşağıda) |

## C olasılığı duyarlılığı (yeni rapor)
`olasilik_duyarlilik.py` → `reports/etki_cephesi/OLASILIK_DUYARLILIK.{json,md}`. P(C) 0,30–0,80, kalan A:B taban oranla bölünür (taban artık 1:1).
**Yeni olasılık üretmez.** Tablo kapılara bağlanmış taban (A=B) ve finans katmanı kalibre yola bağlıyken; kapı sonuçlarının karara çevrilmesi de aynı raporda.

| P(C) | P(A) | P(B) | E[TR net 10y, yaşam dahil] | E[GSYH %] | E[iyileşme] | Skor | Karar |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0.30 | 0.350 | 0.350 | -23.455 | 6.524 | -6.26 | 58.2 | kisitli_uygulanabilir |
| 0.35 | 0.325 | 0.325 | -22.687 | 6.31 | -5.50 | 59.1 | kisitli_uygulanabilir |
| 0.40 | 0.300 | 0.300 | -21.92 | 6.096 | -4.73 | 60.0 | kisitli_uygulanabilir |
| 0.45 | 0.275 | 0.275 | -21.152 | 5.882 | -3.96 | 60.9 | kisitli_uygulanabilir |
| 0.50 | 0.250 | 0.250 | -20.384 | 5.668 | -3.19 | 61.8 | kisitli_uygulanabilir |
| 0.55 | 0.225 | 0.225 | -19.616 | 5.453 | -2.43 | 62.7 | uygulanabilir_kosullu |
| 0.60 | 0.200 | 0.200 | -18.848 | 5.239 | -1.66 | 63.6 | uygulanabilir_kosullu |
| 0.65 | 0.175 | 0.175 | -18.081 | 5.025 | -0.89 | 64.5 | uygulanabilir_kosullu |
| 0.70 | 0.150 | 0.150 | -17.313 | 4.811 | -0.12 | 65.4 | uygulanabilir_kosullu |
| 0.75 | 0.125 | 0.125 | -16.545 | 4.597 | +0.65 | 67.5 | uygulanabilir_kosullu |
| 0.80 | 0.100 | 0.100 | -15.777 | 4.383 | +1.41 | 69.7 | uygulanabilir_kosullu |

- Karar eşiği (skor 62) geçişi P(C) ≈ **0,51** (finans kalibre yola bağlanmadan önce 0,56). Kapılardan bugünkü P(C) = 0,33, yani eşiğin altında.
- Beklenen karışımda iyileşme ancak P(C) ≳ 0,71'de başlıyor.
- E[TR net 10 yıl] aralığı −23,46 … −15,78.

## C için dinamik ölçüt (yeni rapor)
`c_dinamik_olcut.py` → `C_DINAMIK_OLCUT.{json,md}`. Gösterge: merkez sızıntı oranı = 12 ay yatırım geliri gideri / 12 ay mal ihracatı (EVDS, `data/etki_cephesi/gozlem/`). Senaryo sürüklenmesi `ln(merkez_sizinti_carpan)/10` (A 0, B +1,4 %/yıl, C −1,05 %/yıl): varsayımdır.
- Ölçüm baz yıldan sonra başlar (ilk güncelleme 2027-12 verisi): **şimdi güncelleme yok, posterior = prior**. Eksik ay güncellemez.
- **Güç analizi:** yıllık σ = 0,177, C ile A/B arasındaki sürüklenme farkı 0,0105–0,0245. SPRT %95 için **307 (C vs B) ve 1.660 (C vs A) yıl** gerekir; 4000 koşulu Monte Carlo'da 10 yıl sonra gerçek senaryo C de olsa B de olsa E[P(C)] ≈ 0,58–0,61. Gösterge P(C)'yi **doğrulayamaz**.
- **Çapa uyumsuzluğu:** kalibrasyonda 2024 yatırım geliri gideri 18.841 mn $; EVDS 26.483 (×1,41; 2023 = 18.793). `gerceklik_capa.json` değiştirilmedi.
- **Karşı-olgusal trend yok:** oran 2023 sonu 0,075 → 2025 sonu 0,120 (×1,61); senaryoların iki yıllık sürüklenmesi en çok ±0,028.

## Ana pipeline P(C)'ye bağlandı, döngü kırıldı
Önceki durum: ana pipeline `senaryolar.json` içindeki elle atanmış 0,22 / 0,18 / 0,60'ı kullanıyordu. Şimdi `etki_cephesi/_olasilik.py` olasılığı verir.
- **Döngü neden yok:** `_olasilik.py` saf hesaptır; pipeline raporu (`reports/`) okumaz. Yalnız `senaryolar.json` (senaryo parametreleri), `finans_katman_kopru.json` ve EVDS gözlem CSV'lerini okur. Karar eşiği ve skor bağlantısı (rapor okumak gerektirir) ayrı yerde: `olasilik_duyarlilik.py`, tek yönlü. Test: `_olasilik.py` kaynağında `reports` geçmiyor.
- `senaryolar.json`: `olasilik_vekili` → `olasilik_vekili_eski_el_atamasi` (eski değer yalnız karşılaştırma). 9 modül `_olasilik.vekil()` okur. `c_dinamik_olcut` prior'u tekdüze.
- **`en_olasi` → `referans_senaryo`** (`senaryolar.json`, `PROJEKSIYON.json`, `akis_olcum`, `projeksiyon`, `uzun_vade_esik`, README): "en olası" bir olasılık iddiasıydı; C yalnız referans rapor senaryosu. Raporlardaki "(en olası)" etiketleri "(referans)" oldu. Eski anahtar yok; bir test hiçbir raporda "en olası" kalmadığını denetler.
- **Bayat rapor bulundu:** `UZUN_VADE_ESIK` `run_all` dışında kalmıştı, zip'teki eski sayıları taşıyordu (C 2026: −18,015; 2036 orta yol: −11,341). Revize sayılarla (−17,70; −13,11) yenilendi ve `run_all` adımlarına eklendi.
- Gözlem gelince (2027-12'den itibaren) `vekil()` kendiliğinden hareket eder; el ile bir şey yazılmaz.

| Çıktı | P(C)=0,60 (eski) | P(C)=1/3 (kapılar, gözlem yok) |
|---|---|---|
| Uygulanabilirlik skoru | 62,7 | **58,8** |
| Karar | uygulanabilir_kosullu | **kisitli_uygulanabilir** |
| Skor C-senaryosu / beklenen A·B·C | 67,1 / 54,5 | 63,7 / 49,7 |
| Senaryo skorları A / B / C | 50,1 / 49,4 / 73,0 | 52,4 / 52,4 / 69,6 |
| E[TR net 10 yıl] (yaşam dahil) | −18,19 | **−22,94** |
| Beklenen karışımın iyileşmesi | −1,00 | **−5,75** (iyileşme yok) |
| C yolu TR net 10. yıl | −17,19 → −13,10 | −17,19 → −12,67 (olasılığa bağlı değil; değişim finans bağlamasından, aşağıda) |
| Finans katmanı beklenen TR net (ham) | − | −12,99 |

Okuma: C yolunun kendi sonucu iyileşir; olasılık ona dokunmaz. Değişen, C'ye verilen ağırlıktır. Ağırlık düşünce karışım kötüleşiyor ve karar eşiğin altına iniyor. 62,7 sonucu elle atanmış 0,60'a yaslanıyordu.

## P(C) ölçülebilir kapılarla yeniden kuruldu (yeni rapor)
`olasilik_kapilar.py` → `OLASILIK_KAPILAR.{json,md}` (saf hesap `_olasilik.py`). Eski 0,22 / 0,18 / 0,60 elle atanmıştı, dayanağı yoktu.
- **Prior tekdüze (1/3).** Ölçüm baz yıldan (2026) sonra başlar; şimdi güncelleme yok → **bugünkü P(C) = 0,333**. Bu ölçüm değil, bilgi yokluğudur.
- **K1 merkez sızıntı sürüklenmesi:** olabilirlik `senaryolar.json`'dan türetilir; ayırt gücü yok (307 yıl).
- **K2 dış kısıt (EVDS `bie_oderoll`, bankalar ve diğer sektörler 12 ay ort. çevirme ≥ %100):** kontrol noktaları 2027-12, 2029-12, 2031-12. Taban oran p0 = tarihçede "açık" pencere payı = **0,534** (232 pencere; bugün açık: K1 109,8, K2 175,0). Olabilirlik **varsayım**: p_A = p0, p_B = p0 − δ, p_C = p0 + δ, δ = 0,10 (tek parametre, duyarlılığı raporda).
- **K3 etki erozyonu** (bölge ihracat payı): EVDS'de seri yok, TİM verisi depoda yok → kapalı. **K4 bağ kullanımı:** gözlenebilir seri yok → kapalı. İkisi de olasılığa girmez: bilinmiyor sıfır değildir.

| Açık | P(A) | P(B) | P(C) | Skor | Karar | Eşiği geçer |
| ---: | ---: | ---: | ---: | ---: | --- | --- |
| 0/3 | 0.305 | 0.547 | 0.148 | 55.4 | kisitli_uygulanabilir | hayır |
| 1/3 | 0.341 | 0.409 | 0.25 | 57.3 | kisitli_uygulanabilir | hayır |
| 2/3 | 0.344 | 0.276 | 0.38 | 59.6 | kisitli_uygulanabilir | hayır |
| 3/3 | 0.312 | 0.167 | 0.521 | 62.1 | uygulanabilir_kosullu | evet |

- **Sonuç:** tek ölçülebilir kapı en iyi ihtimalle P(C) = 0,52 verir. Karar eşiği finans kalibre yola bağlanmadan önce 0,56'ydı (3/3 açıkta bile skor 61,3, geçmezdi); bağlandıktan sonra 0,51: 3/3 açık **skor 62,1 ile eşiği 0,1 puan farkla geçer**. Yani sonuç kapı verisinden çok finans bağlamasının varsayımlarına duyarlı; kenar durumu.
- δ duyarlılığı: δ = 0,20 ile 3/3 açık → 0,68; δ = 0 ile kapı hiçbir şey söylemez. Eski el ataması prior kullanılırsa sonuç prior'a yaslanır (0,35 … 0,76): tabloyu prior belirler, kapı değil.

## A, B, C için eşit ayrıntı (yeni)
Önceki durum: A ve B için ülke/aktör md'si vardı ama `AKIS_OLCUM`, `ZARAR_COZUM` md'si ve ayrıntılı bölümler yalnız referans senaryo C'dendi; `PROJEKSIYON.md` C'yi başa alıp ayrıca "Referans" bloğuyla öne çıkarıyordu.
- `senaryo_rapor.py` → `SENARYO_RAPOR_{A,B,C}.md` (9 bölüm, aynı alanlar, aynı sıra) ve `SENARYO_KARSILASTIRMA.md` (yan yana). Bir test üç raporun alan listesinin aynı olduğunu denetler.
- `AKIS_OLCUM_{A,B,C}.{json,md}`, `ZARAR_COZUM_{A,B,C}.md` eklendi. `AKIS_OLCUM.*` yalnız alt modüllerin tek-girdi dosyası olarak kaldı.
- `PROJEKSIYON.md`: referans bloğu kalktı, senaryolar A, B, C sırasında, üçü için aynı özet tablo.
- **Düzeltme:** bu bölümün ilk sürümü "üretim iç akışı ve finans katmanı A/B için C tabanından ölçekleniyor" diyordu. Kodu okuyunca doğrusu şuydu: üretim katmanı her senaryonun **kendi** zarar-çözüm tabanını kullanıyordu ama **aynı** çarpanları uyguluyordu (A, B de C ile aynı oranda iyileşiyordu). C'ye göre ek ölçekleme yalnız finans katmanındaydı ve merkez sızıntı çarpanını ikinci kez uyguluyordu (projeksiyonda zaten uygulanmıştı: çift sayım). F.4 stok yolu ise gerçekten senaryodan bağımsız.

## A ve B için üretim ve finans katmanı ayrı kuruldu
- **Üretim katmanı:** g_u = bağ kullanımı(senaryo) / bağ kullanımı(C): A 0,423, B 0,269, C 1. Üretime bağlama, bağ kullanılmıyorsa daralır. Etkin çarpan = 1 − g_u (1 − çarpan); rant artı değer payı ve iç akış kazanımları da g_u ile ölçeklenir.
- **Finans katmanı:** g_f = politika gerçekleşmesi(senaryo) / (C), politika = clip(1,05 − etki erozyonu + diplomatik esneklik, 0,25, 1): A 0,737, B 0,432, C 1. Finans halka ek çarpanları, MFIN kenar çarpanı, yatırım geliri iç tutma, TDS rahatı ve kredi kesintisi g_f ile ölçeklenir. Çift sayan eski C-göreli ölçekleme kaldırıldı.
- Farklı sürücüler: üretim katmanı bağ kullanımına, finans katmanı dış koşula bağlı. İkisi de `senaryolar.json` parametrelerinden türetildi; çarpanların kendisi ortak ve atanmış, doğrusal ölçekleme **varsayım**. Kapatma: kopru dosyalarında `senaryo_gerceklesme.aktif=false` (g=1).
- **C'nin sayıları bayt bayt aynı** (g_C = 1).

| TR net (vekil) | Önce A | Sonra A | Önce B | Sonra B | C |
|---|---:|---:|---:|---:|---:|
| Üretim iç akışı | −6,34 | **−13,32** | −10,10 | **−24,82** | −4,38 |
| Finans katmanı | −2,25 | **−7,33** | −7,12 | **−31,15** (ters çevrilmiş; çevrilmeseydi −18,49) | −0,49 |
| Kalibre son (gerçeklik) | −16,31 | −17,62 | −32,19 | −38,31 | −11,21 |

- Katman yığını: zarar çözümü ≤ üretim; finans ≥ üretim, yalnız B'de (ters çevrilmiş) finans < üretim (test). Sıfır yılı (aynı eğimin devamı varsayımı): A 2065, B 2087 (önce 2044), C 2044.
- **Karara etkisi küçük (finans kalibre yola bağlanmadan önce):** skor 57,9 ve karar aynı; E[TR net 10 yıl] −22,18 → −22,50.

## B'nin finans katmanı araçsallaşma yönünde ters çevrildi
- **Kural:** `bag_modu` içinde baskın mod araçsal ise (yalnız B: 0,54) finans katmanı ters çevrilir. A baskın modu atıl, C kullanım: çevrilmez. Etkin g_f = −güç · g_f, güç = 1 (B: +0,432 → **−0,432**).
- **Ne olur:** `etkin_carpan = 1 − g(1 − çarpan)` olduğu için g < 0 iken azaltım çarpanları artırım çarpanına döner (halka ek çarpanları, MFIN kenar), iç tutma, TDS rahatı ve kredi kesintisi kazanımı kayba döner. Finans geri kazanım B'de pozitif yerine **−2,81**. Anlam: finans kanalları TR lehine kısalmaz, dış çıkar ağının aracına döner.
- **B finans TR net:** −18,49 (çevrilmemiş) → **−31,15**; üretim katmanı −24,82'den de kötü. Boşalma 34,5, sıfır yılı yok (net yükselmiyor). B kalibre son −33,88 → −38,31; GSYH vekili %9,43 → %10,66.
- **Duyarlılık (varsayım):** çevrilmemiş −18,49 · güç 0 (finans etkisiz) −24,82 · güç 0,5 −27,99 · güç 1 (tam ayna) −31,15. Ayna simetri ve güç = 1 **varsayım**; `finans_katman_kopru.json` `ters_cevirme` (aktif/güç) ile ayarlanır.
- **Bu aşamada karara etkisi yoktu** (skor 57,9): finans fazı kalibre yolda sıralı koşulduğu için 10. yıl satırına ulaşmıyordu. Sebep etiket değil faz takvimiydi; sonraki bölümde bağlandı.

## Finans katmanı kalibre yola bağlandı
- **Neden girmiyordu:** kalibre yol fazları sıralı koşuyordu (zarar 7 y → üretim 12 y → finans 10 y). 10 yıllık başlık 10. satıra bakar: 7 yıl zarar + 3 yıl üretim. Finans fazı yolun 20. yılından sonra başlıyordu, yani başlık sonuçlarına hiç girmiyordu. Ayrıca sıralı yolda her faz geçişinde bir yıl eksikti (2033 → 2035).
- **Yeni mod `uretimle_es_zamanli`** (`finans_katman_kopru.json` `kalibre_yola_baglama`): zarar fazı 7 yıl aynen; ondan sonra finans, üretim ÜSTÜ bir katman olduğundan üretimle aynı anda başlar ve kendi olgunluğunda (10 y) yükselir. Yol yıllık kesintisiz. `mod: "sirali"` eski davranış. Faz takvimi **varsayımdır**.
- **İkinci düzeltme (benim önceki adımımın hatası):** kalibre yol r_u ve r_f'yi senaryo politikasıyla (pol_s) çarpıyordu; katmanlar artık kendi g_u, g_f'lerini taşıdığı için bu ikinci kez uygulamaydı. Katmanlarda pol_s yerine C'nin pol'ü (sabit) kullanılıyor, C'nin son değerleri değişmiyor.
- **Ters çevrilmiş finansın gerçekleşmesi:** `_gerceklesme` yalnız iyileşme için tavan koyar; negatif delta (B) için 1,0 döner, yani zarar tavansız gerçekleşir (B r_f = 0,95, A 0,21, C 0,22). Gerekçe: araçsallaşma kazanım gerçekleşmesine bağlı olmayan bir zarar; **varsayım**.

| Yapılandırma | Skor | E[TR net 10y] | 10y TR net A / B / C | Son (kalibre) A / B / C |
|---|---:|---:|---|---|
| 1) bağlama kapalı (sıralı, pol_s) | 57,9 | −22,50 | −19,49 / −35,05 / −12,96 | −17,62 / −38,31 / −11,21 |
| 2) yalnız pol çift sayımı düzeltildi (sıralı) | 57,9 | −22,36 | −19,36 / −34,76 / −12,96 | −16,65 / −41,94 / −11,21 |
| 3) **varsayılan:** finans eşzamanlı | **58,8** | **−22,94** | **−18,84 / −37,29 / −12,71** | −16,65 / −41,94 / −11,21 |

- Karar `kisitli_uygulanabilir` kaldı. Skor C'nin finans kazanımıyla arttı (63,7), beklenen karışım B'nin zararıyla kötüleşti (−22,94; iyileşme Δ −5,75).
- B kalibre GSYH vekili (son değer) %11,67 (bağlamadan önce %10,66). Etki B'nin finans katmanında: 10. yılda A +0,6, C +0,25 iyileşirken B −2,2 kötüleşti.
- **Karar eşiği P(C) 0,56 → 0,51** (yukarıdaki bölümler güncel); kapı 3/3 açıkta skor 62,1.
- Hâlâ varsayım: faz takvimi, ayna simetri + güç=1, zarar tavansız gerçekleşme, katman çarpanları (atanmış). `FINANS_KATMAN` etiketi "varsayım çarpanlı ham"; uyarı metni "kalibre yola bağlı, ham değer kalibre değildir" diye güncellendi.

## Düzeltilmeyen / açık
- Ödeyenin yalnız F olması kullanıcı kararıdır; rantın bir kısmını H veya kamu ödüyorsa transfer F'ye fazla yazılır.
- `bolge_stok_akis`, `lm_rant_sektor` darbeleri sıfır toplamlı değil: yalnız ilan edildi.
- λ ve κ ölçülmüş değil. Sonuçlar senaryo bandıdır. Senaryo olasılıkları (0,22 / 0,18 / 0,60) ölçülmüş değil.
- USD akışları 2024 çapasından, matris 2026-Q1: yalnız kur düzeltildi.
- `_incoming/zarar-teorisi-main` bu pakette yok; `zarar-teorisi` reposunun `main` kopyası oraya konmalı.

## Uygulama
```
cd etki-cephesi-model; patch -p1 < etki-cephesi-revize.patch
python etki_cephesi/run_all.py     # kararlı duruma kadar geçer
python -m pytest tests -q
```
Yama kaynak, veri ve test dosyalarını içerir. Raporlar ve `data/etki_cephesi/kalibre/*.json` pipeline ürünüdür.
`etki-cephesi-model-revize.zip` aynı sonucu hazır (raporlar yenilenmiş) içerir.
