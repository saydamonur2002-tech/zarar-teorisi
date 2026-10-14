# Etki cephesi modeli: revize sonucu

Kaynak: `zarar-teorisi` dalı `cursor/odeme-zinciri-kalicilik-f01a`, `yayin/etki-cephesi-model.zip`.
Doğrulama: yama temiz zip çıkarımına uygulandı, `run_all.py` tek komutla kararlı duruma vardı (özet `59c2c071a9ada012`, temiz kurulumda 3 geçiş),
**62 test geçti** (27 mevcut + 35 yeni; bir mevcut testin işareti güncellendi). Orijinal pipeline zip'teki raporları birebir yeniden üretiyor
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

Not: bu tablo P(C)=0,60 ile. P(C) kapılara, kapılar ve katmanlar geçmişe bağlanıp `kanal` kuralı kalkınca skor 56,7 ve karar `kisitli_uygulanabilir` (aşağıda).
| 10 | C'nin gerçekleşmesini ölçen bir ölçüt yoktu | `c_dinamik_olcut.py`: sıralı Bayes, EVDS merkez sızıntı oranı; güç analizi (aşağıda) |

## C olasılığı duyarlılığı (yeni rapor)
`olasilik_duyarlilik.py` → `reports/etki_cephesi/OLASILIK_DUYARLILIK.{json,md}`. P(C) 0,30–0,80, kalan A:B taban oranla bölünür (taban 1:1). **Yeni olasılık üretmez.** Tablo, kapı ve katmanlar geçmişten kurulduktan ve `kanal` dağıtım kuralı kaldırıldıktan sonraki güncel durum:

| P(C) | P(A) | P(B) | E[TR net 10y, yaşam dahil] | E[GSYH %] | E[iyileşme] | Skor | Karar |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0.30 | 0.350 | 0.350 | -23.622 | 7.059 | -6.43 | 56.1 | kisitli_uygulanabilir |
| 0.35 | 0.325 | 0.325 | -22.846 | 6.826 | -5.66 | 57.0 | kisitli_uygulanabilir |
| 0.40 | 0.300 | 0.300 | -22.07 | 6.594 | -4.88 | 57.9 | kisitli_uygulanabilir |
| 0.45 | 0.275 | 0.275 | -21.293 | 6.361 | -4.10 | 58.8 | kisitli_uygulanabilir |
| 0.50 | 0.250 | 0.250 | -20.517 | 6.129 | -3.33 | 59.7 | kisitli_uygulanabilir |
| 0.55 | 0.225 | 0.225 | -19.741 | 5.896 | -2.55 | 60.6 | kisitli_uygulanabilir |
| 0.60 | 0.200 | 0.200 | -18.965 | 5.664 | -1.77 | 61.5 | kisitli_uygulanabilir |
| 0.65 | 0.175 | 0.175 | -18.189 | 5.431 | -1.00 | 62.4 | uygulanabilir_kosullu |
| 0.70 | 0.150 | 0.150 | -17.412 | 5.198 | -0.22 | 63.3 | uygulanabilir_kosullu |
| 0.75 | 0.125 | 0.125 | -16.636 | 4.966 | +0.55 | 65.2 | uygulanabilir_kosullu |
| 0.80 | 0.100 | 0.100 | -15.86 | 4.733 | +1.33 | 67.5 | uygulanabilir_kosullu |

- Karar eşiği (skor 62) geçişi P(C) ≈ **0,63** (kanal kaldırılmadan önce 0,52). Kapılardan bugünkü P(C) = 0,33, yani eşiğin altında.
- Beklenen karışımda iyileşme ancak P(C) ≳ 0,72'de başlıyor.
- E[TR net 10 yıl] aralığı −23,62 … −15,86.

## C için dinamik ölçüt (yeni rapor; geçmişten kurulmuş sürüklenme)
`c_dinamik_olcut.py` → `C_DINAMIK_OLCUT.{json,md}`. Gösterge: merkez sızıntı oranı r = 12 ay yatırım geliri gideri / 12 ay mal ihracatı (EVDS). **Senaryo sürüklenmesi geçmişten:** r'nin kayan 5 yıllık log-eğimleri (2015–2025, 7 pencere): A = medyan (−0,008/yıl), B = q75 (+0,057), C = q25 (−0,055). Eski: ln(atanmış çarpan)/10 ile A 0, B +0,014, C −0,0105.
- Ölçüm baz yıldan sonra başlar: şimdi güncelleme yok, posterior = prior (1/3). Eksik ay güncellemez.
- **Güç analizi (geçmiş sürüklenmeyle):** yıllık σ = 0,177 (geçmiş log değişim std'si). SPRT %95 için **C vs B 15 yıl, C vs A 82 yıl, A vs B 44 yıl** (eski atanmış sürüklenmeyle 307 / 1.660 yıl). Monte Carlo (10 yıl): gerçek C ise E[P(C)] = 0,53, gerçek A ise 0,34, gerçek B ise 0,14. C'yi B'den **ayırır**, A'dan ayıramaz.
- **Neden iyileşti:** senaryolar geçmiş rejimlerin çeyreği olarak tanımlandı; atanmış ±%10–15 geçmiş dalgalanmanın çok altındaydı. Bu bir bulgu değil, tanım sonucu: gösterge "gelecek geçmiş rejimlerden birine benzer" varsayımı altında ayırt ediyor.
- **Hâlâ geçmişin dışı:** r 2023 sonu 0,075 → 2025 sonu 0,120 (×1,61): 2025 penceresinin eğimi +0,174, B'nin q75'inin (0,057) üç katı; yani yakın dönem B rejiminin bile dışında. Hiçbir senaryo bu hareketi taşımıyor.
- **Çapa uyumsuzluğu:** kalibrasyonda 2024 yatırım geliri gideri 18.841 mn $; EVDS 26.483 (×1,41; 2023 = 18.793). `gerceklik_capa.json` değiştirilmedi.

## Ana pipeline P(C)'ye bağlandı, döngü kırıldı
Önceki durum: ana pipeline `senaryolar.json` içindeki elle atanmış 0,22 / 0,18 / 0,60'ı kullanıyordu. Şimdi `etki_cephesi/_olasilik.py` olasılığı verir.
- **Döngü neden yok:** `_olasilik.py` saf hesaptır; pipeline raporu (`reports/`) okumaz. Yalnız `senaryolar.json` (senaryo parametreleri), `finans_katman_kopru.json` ve EVDS gözlem CSV'lerini okur. Karar eşiği ve skor bağlantısı (rapor okumak gerektirir) ayrı yerde: `olasilik_duyarlilik.py`, tek yönlü. Test: `_olasilik.py` kaynağında `reports` geçmiyor.
- `senaryolar.json`: `olasilik_vekili` → `olasilik_vekili_eski_el_atamasi` (eski değer yalnız karşılaştırma). 9 modül `_olasilik.vekil()` okur. `c_dinamik_olcut` prior'u tekdüze.
- **`en_olasi` → `referans_senaryo`** (`senaryolar.json`, `PROJEKSIYON.json`, `akis_olcum`, `projeksiyon`, `uzun_vade_esik`, README): "en olası" bir olasılık iddiasıydı; C yalnız referans rapor senaryosu. Raporlardaki "(en olası)" etiketleri "(referans)" oldu. Eski anahtar yok; bir test hiçbir raporda "en olası" kalmadığını denetler.
- **Bayat rapor bulundu:** `UZUN_VADE_ESIK` `run_all` dışında kalmıştı, zip'teki eski sayıları taşıyordu (C 2026: −18,015; 2036 orta yol: −11,341). Revize sayılarla (−17,70; −13,11) yenilendi ve `run_all` adımlarına eklendi.
- Gözlem gelince (2027-12'den itibaren) `vekil()` kendiliğinden hareket eder; el ile bir şey yazılmaz.

| Çıktı | P(C)=0,60 (eski) | P(C)=1/3 (kapılar, gözlem yok) |
|---|---|---|
| Uygulanabilirlik skoru | 62,7 | **56,7** |
| Karar | uygulanabilir_kosullu | **kisitli_uygulanabilir** |
| Skor C-senaryosu / beklenen A·B·C | 67,1 / 54,5 | 61,5 / 47,7 |
| Senaryo skorları A / B / C | 50,1 / 49,4 / 73,0 | 50,3 / 50,3 / 67,3 |
| E[TR net 10 yıl] (yaşam dahil) | −18,19 | **−23,10** |
| Beklenen karışımın iyileşmesi | −1,00 | **−5,91** (iyileşme yok) |
| C yolu TR net 10. yıl | −17,19 → −13,10 | −17,19 → −12,72 (olasılığa bağlı değil; finans bağlaması ve geçmiş çarpanından) |
| Finans katmanı beklenen TR net (ham) | − | −13,70 |

Okuma: C yolunun kendi sonucu iyileşir; olasılık ona dokunmaz. Değişen, C'ye verilen ağırlıktır. Ağırlık düşünce karışım kötüleşiyor ve karar eşiğin altına iniyor. 62,7 sonucu elle atanmış 0,60'a yaslanıyordu.

## P(C) ölçülebilir kapılarla yeniden kuruldu (yeni rapor)
`olasilik_kapilar.py` → `OLASILIK_KAPILAR.{json,md}` (saf hesap `_olasilik.py`). Eski 0,22 / 0,18 / 0,60 elle atanmıştı, dayanağı yoktu.
- **Prior tekdüze (1/3).** Ölçüm baz yıldan (2026) sonra başlar; şimdi güncelleme yok → **bugünkü P(C) = 0,333**. Bu ölçüm değil, bilgi yokluğudur.
- **K1 merkez sızıntı sürüklenmesi:** olabilirlik **geçmişten** (A medyan, B q75, C q25 kayan 5 yıllık log-eğim); ayırt gücü: C için en kısa ayrım 15 yıl (SPRT %95).
- **K2 dış kısıt (EVDS `bie_oderoll`, bankalar ve diğer sektörler çevirme ≥ %100):** kontrol noktaları 2027-12, 2029-12, 2031-12. Olabilirlik **geçmişten**: P(açık | rejim); rejim = kayan 5 yıllık eğimin çeyreği. Geçmiş sayım (açık/toplam): A 0/3, B 2/2, C 1/2 → Laplace ile A 0,20, B 0,75, C 0,50. **n = 7 örtüşen pencere (etkin ~2 bağımsız): çok zayıf.** Önceki δ varsayımının işareti de tersti: geçmişte dış finansman en çok sızıntı artarken (2023–25, B benzeri rejim) açıktı.
- **K3 etki erozyonu** (bölge ihracat payı): EVDS'de seri yok → kapalı. **K4 bağ kullanımı:** gözlenebilir seri yok → kapalı. İkisi de olasılığa girmez: bilinmiyor sıfır değildir.

| Açık | P(A) | P(B) | P(C) | Skor | Karar | Eşiği geçer |
| ---: | ---: | ---: | ---: | ---: | --- | --- |
| 0/3 | 0.785 | 0.024 | 0.192 | 54.2 | kisitli_uygulanabilir | hayır |
| 1/3 | 0.427 | 0.156 | 0.417 | 58.2 | kisitli_uygulanabilir | hayır |
| 2/3 | 0.108 | 0.472 | 0.42 | 58.3 | kisitli_uygulanabilir | hayır |
| 3/3 | 0.014 | 0.76 | 0.225 | 54.8 | kisitli_uygulanabilir | hayır |

- **Sonuç:** K2 P(C)'yi monoton artırmıyor: 3/3 açıkta B öne çıkıyor (0,76), C en çok 1–2 açıkta (0,42). En iyi tek kapı P(C) = 0,42; karar eşiği şimdi 0,63; **hiçbir K2 sonucu eşiği geçirmez** (skorlar 54,2 … 58,3).
- λ duyarlılığı (geçmişe ağırlık): λ = 0 saf geçmiş, λ = 1 kapı bilgi taşımaz (0,333). Eski el ataması prior kullanılırsa sonuç prior'a yaslanır: tabloyu prior belirler, kapı değil.

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

## Salt geçmiş projeksiyonu (yeni rapor)
`gecmis_projeksiyon.py` → `GECMIS_PROJEKSIYON.{json,md}`. **Girdi yalnız EVDS gözlem CSV'si.** Senaryo parametresi, olasılık, katman çarpanı, λ/κ, faz takvimi, kalibrasyon ağırlığı, kapı iskeleti **kullanılmaz**; pipeline raporu okunmaz (test, importları ve girdi okumalarını denetler).
- Seriler: merkez sızıntı oranı r = yatırım geliri gideri / mal ihracatı ve net yatırım geliri gideri (mn $). Tam yıllar 2015–2025.
- Üç yöntem, hiçbiri seçilmedi: `duz` (son 12 ay sabit: r = 0,1191; net = 23.445 mn $), `trend5` (son 5 yıl log-doğrusal), `trendT` (tüm yıllar log-doğrusal), 95% tahmin aralığıyla.
- **Gözlem:** r 2015–2019'da 0,077 → 0,087, 2022'de 0,056'ya düştü, 2025'te **0,120**. Net: 9,3 → 21,8 mlr $.
- **Geriye test (2022'ye kadar fit, 2023–2025 tahmin):** üç yöntem de eksik tahmin etti; ortalama mutlak hata r için %36–50, net için %36–46 (`trendT` en iyi, `trend5` en kötü). 2025'te hata %−51 … −65. Rejim değişimi (2023'ten sonra r ×1,6) geçmişten öngörülemedi. 3 gözlemlik test: güç düşük, yalnız yön.
- **Ne diyor:** son 12 ay sabit tutulursa r 0,119'da kalır; `trendT` 2036'da 0,108 [0,046; 0,255]; `trend5` 2036'da 0,78 [0,08; 7,9] (anlamsız genişlikte: son 5 yıl rejim değişimini içeriyor). Geçmiş tek başına ne C'yi ne B'yi ne A'yı ayırt eder.

## Kapılar ve katmanlar geçmişten kuruldu (b seçeneği)
Senaryolar kaldı; büyüklükleri geçmişten gelir (`etki_cephesi/_gecmis.py`, saf: yalnız gözlem CSV'leri ve tam olgunluk yılı).
- **Senaryo = geçmiş rejimi:** A = medyan, B = üst çeyrek, C = alt çeyrek eğim (kayan 5 yıllık log-eğim). `merkez_sizinti_carpan = exp((d_s − d_A) · 10)`: **A 1,00, B 1,91, C 0,62** (atanmış 1,00 / 1,15 / 0,90 yerine). `senaryolar.json`: değerler `merkez_sizinti_carpan_eski_atanmis`.
- **Kapılar:** K1 ve K2 olabilirliği yukarıdaki gibi geçmişten (δ varsayımı kalktı, λ eklendi).
- **Finans katmanı:** MFIN kenar sızıntı çarpanı = geçmişten C çarpanı (0,62; atanmış 0,52 yerine). `finans_katman_kopru.json` `gecmisten_turet`.
- **Geçmişten TÜRETİLEMEYEN, atanmış kalanlar** (geçmişte gözlenebilir karşılığı olmayan kavramlar): etki erozyonu, diplomatik esneklik, bağ modu payları, halka çarpanları (zarar/üretim/finans), yatırım geliri iç tutma, TDS rahatı, kredi kesintisi, olgunluk süreleri, ters çevirme gücü, faz takvimi. Katmanların büyük kısmı bu yüzden hâlâ atanmış: **"katmanları geçmişten kur" kısmen yapıldı.**

| TR net (vekil) | Önce | Sonra |
|---|---|---|
| Merkez sızıntı Σ A / B / C (PROJEKSIYON) | 13,13 / 20,73 / 7,90 | 13,13 / **31,86** / **6,16** |
| Finans katmanı A / B / C | −7,33 / −31,15 / −0,49 | −7,71 / −32,16 / −1,23 |
| Kalibre son A / B / C | −16,65 / −41,94 / −11,21 | −16,76 / −43,28 / −11,38 |
| Skor / karar | 58,8 / kısıtlı | **58,7 / kısıtlı** |
| E[TR net 10 yıl] | −22,94 | **−23,10** |
| Karar eşiği P(C) | 0,51 | **0,52** |

- Karar değişmedi: geçmişten kurmak sonucu çok oynatmadı (skor −0,1). Merkez sızıntı çarpanı yalnız merkez sızıntı kalemini değiştiriyor; TR boşalma ve karar skorunu belirleyen kalemler değişmedi.
- Bu bölümden önceki bölümlerdeki finans ve katman sayıları atanmış çarpanlarla hesaplanmıştı (örn. "ters çevirme", "kalibre yola bağlandı" tabloları); güncel değerler yukarıdaki tablodadır, mekanizmalar aynıdır.

## Kapsam işaretleri: modellenmeyenler "bilinmiyor"
`kazanc_kayip_muhasebe.py` → `KAZANC_KAYIP_MUHASEBE.{json,md}` (ilk sürüm teşhisti; bu bölümdeki oranlar düzeltmeden öncekidir).
- **Kaynak:** `projeksiyon.py` bir korunum özdeşliği tanımlamıyordu. Dış aktör kazancı dört kanaldan geliyor ve dördü **aynı bölge kaybından** (TR boşalması V) besleniyor: `kanal` (V × aktör payı), `matris` (V × katsayı farkı), `ikame` ve `merkez` kenarları (bölge kaybı × pay × çarpan). Birbirini dışlamıyorlar.
- **Ölçüm (V = TR boşalması + 0,08 · pasif):** kanal + matris V'nin **%128'i** (aynı boşluk iki kuralla dağıtılıyor); dört kanalın toplamı V'nin A'da **%184**, B'de %218, C'de %170'i. A'da V = 25,4; Σ kazanç = 46,7 (kanal 18,3 + matris 14,3 + ikame 4,9 + merkez 9,2).
- **Kayıp tarafı ayrı bir nicelik:** TR kaybı 25,8 + TR dışı ülke kayıpları 14,4 = 40,2. Σ kazanç − Σ kayıp: A +6,5, B +22,1, C +2,5. Bu fark korunum ihlali değil, **özdeşliğin hiç tanımlı olmamasının** sonucu: kazanç V'den, kayıp bölge net etkisinden hesaplanıyor. "Kazanan kaybedenin kaybettiği kadar kazanır" modelde yok.
- **Düzeltme:** ilk sürümde yapılmadı (kullanıcı kararı bekleniyordu); sonraki bölümde uygulandı.
- **Kapsam işaretleri** (`aktör_birlesik`: `kazanc_kapsam`, `kayip_kapsam`, `net_kapsam`): kazanç kanalı hiç modellenmemişse "yok", biri modelliyse "kısmi", ikisi modelliyse "tam". Kayıp listesinde olmayan aktör için "bilinmiyor". Raporlarda sıfır yerine `—`, kısmi için `†`, net yalnız ikisi tam modelliyse yazılır. 37 aktörden **net tam yalnız 6** (İran, İsrail, Mısır, Sırbistan, Azerbaycan, Türkiye); kazancı tam modellenenler 14 (13 aktör + MFIN); kayıp bilinmeyenler 8 (Çin, Rusya, AB, ABD, BAE, Suudi Arabistan, Fransa, Yunanistan); "Körfez (vekil)" düğümünün kazancı yok.
- **Evren dışı** (modelde hiç yok; derleme): Katar, Kuveyt, Umman, Ürdün, Hindistan, Japonya, Güney Kore, Birleşik Krallık, Almanya, İtalya.
- `DIS_AKTOR_*.md` birleşik tablosu eskiden ilk 30 satırı gösteriyordu (en büyük kayıp ülkeler, Irak ve Körfez, kesiliyordu); artık tüm aktörler yazılıyor.

## Kazanç–kayıp tutarsızlığı bulundu, `kanal` kaldırıldı, normalize edildi
`kazanc_kayip_muhasebe.py` → `KAZANC_KAYIP_MUHASEBE.{json,md}`.
- **Kaynak:** dış aktör kazancı dört kanaldan geliyor ve dördü **aynı bölge kaybından** (boşluk V = TR boşalması + 0,08 · pasif) besleniyordu: `kanal` (V × aktör payı), `matris` (V × katsayı farkı), `ikame`, `merkez`. Birbirini dışlamıyorlardı: kanal + matris V'nin %128'i; dört kanalın toplamı A'da %184, B'de %218, C'de %170.
- **Düzeltme (kullanıcı kararı: kanalı kaldır + normalize):** `kanal` kuralı kaldırıldı (matris kuralıyla aynı boşluğu ikinci kez dağıtıyordu). Kalan üç kanalın (matris, ikame, merkez) toplamı V'yi aşıyorsa orantılı küçültülür, altındaysa dokunulmaz. Katsayılar: **A 0,894, B 0,689, C 1,0** (ham toplam V'nin %112 / %145 / %98'i). Artık Σ kazanç ≤ V: A 25,40 / V 25,40, B 40,46 / 40,46, C 17,05 / 17,40.
- Defterde (`DIS_ULKE_REFAH`, uluslararası stok-akış) `kanal_kazanc` yuvası artık matris kuralını taşır; stok kapanışı ve MFIN tutarlılığı korundu (`kapanis_ok` A/B/C, `mfin uyum_ok`).
- **Σ kazanç = Σ kayıp hedeflenmedi:** kayıp bölge net etkisi (A: TR 25,8 + diğer 14,4 = 40,2), kazanç ise TR boşalmasının dağıtımı (V). Aralarındaki fark artık negatif (A −14,8, B −25,4, C −10,0): kazanç kayıptan az.
- **Karara etkisi (dikkat):** skor 58,7 → **56,7**, karar `kisitli_uygulanabilir`; karar eşiği P(C) 0,52 → **0,63**; C senaryosunun kendi skoru 63,5 → 61,5. Sebep tek bir aktör: **Mısır** çevre kazananı olmaktan çıktı (net birleşik +0,50 → eşik 0,05'in altı); "halka-çevre koalisyonu" bileşeni 0,75 → 0,50. Yani karar skoru bir aktörün çift sayılmış kazancından 2 puan alıyormuş. E[TR net 10 yıl] değişmedi (−23,10).
- Kapsam işaretleri (yukarıdaki bölüm) geçerli: kazanç tam modellenenler 14, net tam 6 aktör.

## Mısır: bıçak sırtı düzeltildi, sebep ledger–projeksiyon net farkıydı
Mısır `kanal` kalkınca "çevre kazananı" olmaktan çıkmıştı (ledger neti +0,202 → +0,074; eşik 0,08). Araştırma:
- **Mısır'ın iki farklı neti vardı.** `PROJEKSIYON` (C): −0,010 (nötr). `DIS_ULKE_REFAH` defteri (C): +0,074. Fark: defter, kimliği bilinmeyen merkez sızıntısının **36 ülkeye eşit payını** (`merkez_belirsiz`, Mısır'da 0,062) kazanç olarak ekliyordu. `PROJEKSIYON` aynı payı "fayda Σ'ye eklenmez" diye hariç tutuyordu. Bilinmeyen payı herkese eşit kazanç yazmak, "bilinmiyor sıfır değildir" ilkesine de aykırı.
- **Düzeltme:** defterde `merkez_belirsiz` kazanca eklenmez; alan satırda ayrı durur ve stok-akış kenarlarında (akış kapanışı) kullanılmaya devam eder. Artık defter neti = projeksiyon neti + refah rant payı (test: EG, IR, IL, SA, AE, CN, RU, US).
- **Mısır'ın durumu:** C'de defter neti +0,012 (projeksiyon −0,010), A'da −0,037 (−0,079), B'de −0,224 (−0,320). Sınıf `rant_kanali_bosluk_taraftari`: boşluk rant kanalından 505,9 mn $ fark, ama net ≈ 0. Eşiğin (0,08) belirgin altında: artık bıçak sırtı değil, ve kazanan değil.
- **Mısır kazanan olarak "düzelmedi" ve düzelmemeli:** önceki +0,50 yalnız `kanal` çift sayımından ve eşit dağıtılan belirsiz paydan geliyordu. Hiçbir muhasebede güvenilir biçimde pozitif değil.
- Diğer aktörler: tüm kazanç satırları 0,06 azaldı (belirsiz pay), hiçbir sınıf değişmedi. Karar skoru (56,7), karar eşiği ve E[TR net] aynı; `kapanis_ok` A/B/C ve MFIN tutarlılığı korundu.

## Sınıf eşiği belirsizlik bandıyla değiştirildi
Önceki: `bolge_stok_akis._sinif_etiket` sabit ±0,08 eşiğiyle "kazanan/kaybeden/nötr" diyordu; Mısır +0,074'te bıçak sırtındaydı. Şimdi sınıf, net'in **belirsizlik bandına** göre:
- **Kural:** kazanan ⇔ net − bant > 0; kaybeden ⇔ net + bant < 0; aksi halde `belirsiz_bant_ici` (rant kanalı boşluk farkı > 400 mn $ ise `rant_kanali_bosluk_taraftari`). Eski `notr` sınıfı kalktı.
- **Bant = √(kural² + belirsiz²):** (1) dağıtım kuralı belirsizliği = |kanal kuralı − matris kuralı| (kaldırılan `kanal` kuralı yalnız TANI olarak hesaplanır, kazanca girmez; `kanal_alternatif_kazanc`); (2) kimliği bilinmeyen merkez payı (`merkez_belirsiz`, sayılmadı ama kazanç olabilir). Bağımsız sayılıp karesel toplanır. TR ve MFIN için bant 0.
- **Kısmi kapsamlı aktörlerde** kanal kuralı hiç modellenmediğinden kural belirsizliği ölçülemez; bant en az tam kapsamlı aktörlerin bant medyanı (0,143) alınır (**vekil varsayım**; aksi halde bant 0 görünür, sahte "kesin" sınıf çıkardı).
- **Çıktı:** her aktörde `net_bandi`, `net_alt_ust`, `bant_kapsami`. `BOLGE_STOK_AKIS.md` bant içi aktörleri ayrı listeler.
- **Sınıf değişimi:** Bosna-Hersek kazanandan bant içine; Bulgaristan ve Kıbrıs nötrden bant içine; Sırbistan nötrden çevre kaybedene (net −0,065, bant 0,053). Mısır bant içinde ([−0,13; +0,15]). Kazananlar: Çin, Rusya, ABD, İran, BAE, AB, Suudi Arabistan, İsrail, Fransa, Yunanistan, Arnavutluk, Kuzey Makedonya. Bantlar: Çin ±1,12, Rusya ±1,13 (kural farkı büyük), İran ±0,14, ABD ±0,09.
- **Hâlâ kenar:** Yunanistan net 0,167 / bant 0,158 (marj 0,009), Arnavutluk ve Kuzey Makedonya 0,18 / 0,143 (Balkan payları AB satırının atanmış %68'lik bölünmesinden geliyor). Bant içine girmeleri küçük bir bant değişiminde olur.
- Karar skoru (56,7), karar eşiği P(C) (0,63), E[TR net 10 yıl] ve `kapanis_ok` aynı.

## Yunanistan ve Balkanların bantla sınanması (Çin, Rusya, İran aynı sınamadan geçirildi)
`bant_sinama.py` → `BANT_SINAMA.{json,md}` (duyarlılık/dayanıklılık; başka modüle girdi olmaz). Tek atanmış parametre değişir: AB→Balkan bölünme payı p (taban 0,68; 0,34 / 0,51 / 0,85), dağıtım kuralı (matris ↔ kanal üst ucu), bilinmeyen merkez payının kazanç sayılması, kazancın tamamı ×0,5 / ×1,5, kayıp ×0,75 / ×1,25.
- **Sonuç: Yunanistan ve beş Balkan ülkesinden hiçbirinin sınıfı dayanıklı değil** (A, B, C'nin hepsinde); yalnız Kıbrıs hep bant içinde.
- **Yunanistan:** taban "çevre kazananı" (C: net 0,167, bant 0,158, marj 0,009). Dağıtım kuralı ve belirsiz pay varyantları yalnız yukarı iter; **kazanç ×0,5** ile bant içine düşer. Yani Yunanistan'ın kazananlığı atanmış aktör payına (`dis_aktör_pay`) bağlı.
- **Balkanlar kazançlarını AB satırının atanmış bölünmesinden alıyor ve neredeyse eşit pay alıyor** (kayıtlı refah endeksi olmayan BA, BG, AL, MK için eşit ağırlık): bu dört ülkenin kazancı aynı (C: 0,35); sınıfı yalnız kendi havza kaybı belirliyor. Kırılma payı p* (net = 0), C: **AL 0,33, MK 0,33, BA 0,40** (taban 0,68'in altında → kazanan tarafta), **BG 0,78, RS 0,82** (üstünde → kaybeden tarafta). "Kazanan başlar" payı (bant dışı kazanan): AL/MK 0,60, BA 0,68, yani taban p'de AL/MK marjı 0,04, BA'nın 0,001.
- **p'nin %25'lik azalması** (0,51) AL, MK ve BA'yı bant içine alıyor; %50'lik azalması (0,34) net'i sıfıra yaklaştırıyor. Balkan "kazananları" tek bir atanmış bölünme payının sonucu, ölçülmüş bir bulgu değil.
- **Sınıf kümeleri:** RS kaybeden ↔ bant içi (C'de üç sınıf), BG bant içi ↔ kaybeden; A'da BA/BG bant içi, B'de AL/MK bant içi.
- BA'da net − bant marjı 0,001: yuvarlama düzeyinde (C'de ana rapor bant içi, sınama kazanan diyor).

## Çin, Rusya, İran aynı sınamadan geçirildi (ilk sürüm; kayıp-bilinmiyor düzeltmesi sonraki bölümde)
Aynı varyantlar (kazanç ×0,5 / ×1,5, dağıtım kuralı alternatifi, belirsiz pay, kayıp ×0,75 / ×1,25); kural varyantı artık işaretli (alternatif kural kazancı artırabilir de azaltabilir de). Yeni ölçütler: `en_kotu_marj` (taban sınıfın yönünde, tüm varyantlar içinde bandı en az aşan değer) ve `kazanc_olcek_kirilma` k* (kazancın bu çarpanın altına inmesi aktörü bant dışı kazanan olmaktan çıkarır).
- **Çin, Rusya, İran A, B, C'nin hepsinde dayanıklı (YALNIZ kayıp = 0 varsayımıyla; bkz. sonraki bölüm):** her varyantta "çevre entegre kazananı". En kötü varyant her zaman kazanç ×0,5; en kötü marj: Çin 0,19 (C) – 0,49 (B), Rusya 0,14 – 0,42, İran 0,34 – 0,47.
- **k*:** Çin 0,39 – 0,43, Rusya 0,40 – 0,45, İran 0,28 – 0,33. Yani kazançlarının %55–72'si silinse de bant dışı kazanan kalırlar. Karşılaştırma: Yunanistan k* 0,89 – 0,98, Balkanlar (AL, MK) 0,90 – 0,98: kazançta %2–10'luk kayıp yeter.
- **Önemli uyarı:** bant taban değerinde tutuldu (kazanç ölçeklenince bant ölçeklenmedi), ve sınama aktör başına. Çin ve Rusya'nın kazançları aynı atanmış paylara (`dis_aktör_pay`) ve ikame varsayımlarına dayanır; bu paylar sistematik olarak şişkinse (hepsi birden), sıralama değişmez ama mutlak kazançlar küçülür. Dayanıklılık kazançların büyüklüğünden geliyor (Çin 2,6, Rusya 2,5 vs Yunanistan 0,17), ölçümün güvenilirliğinden değil.

## ABD, İsrail, BAE, Suudi Arabistan, Fransa, AB sınandı; "kaybı bilinmiyor" düzeltmesi
Aynı varyantlar; AB için bölünme payı (1 − p) ile kalan pay. Sınama sırasında **bir önceki bölümdeki bir eksiği buldum:** Çin ve Rusya (ve ABD, BAE, Suudi Arabistan, Fransa, AB, Yunanistan) için havza kaybı **modelde yok** (`kayip_kapsam: bilinmiyor`); önceki sınama bunu sessizce sıfır saymıştı. Bu "bilinmiyor sıfır değildir" ilkesine aykırıydı ve Çin/Rusya'yı olduğundan dayanıklı gösterdi.
- **Düzeltme:** kaybı bilinmeyen aktörlere iki ek varyant: kayıp = referans aktörlerin kayıp/kazanç oranının **medyanı** ve **en yükseği**. Referans: kaybı ve kazancı tam modellenmiş, AB bölünmesinden bağımsız İran, İsrail, Mısır (her üç senaryoda aynı küme; A: medyan 0,26 / maks 1,08, B: 0,38 / 1,34, C: 0,21 / 0,96; maks hep Mısır). Kırılma noktası olarak **r\*** da yazılır: bilinmeyen kayıp kazancın bu oranından küçükse aktör hâlâ bant dışı kazanan.
- **Sonuç:** kazanç, pay ve kural salınımlarına dayanıklı olanlar (kayıp-dışı varyantlarda hep kazanan): Çin, Rusya, ABD, BAE, Suudi Arabistan, AB (+ İran, kaybı modelli). **Medyan oranda** hepsi kazanan kalır. **Mısır oranında** (kayıp ≈ kazanç) hiçbiri kazanan kalmaz: bant içine, ABD için A ve B'de, BAE, Suudi Arabistan ve AB için B'de kaybedene düşer.
- **r\*** (C): Çin 0,57, Rusya 0,56, Fransa 0,43, AB 0,82, BAE 0,84, Suudi Arabistan 0,90, ABD 0,96, Yunanistan 0,05. Yani kazanan olarak kalmak için Çin'in kaybı kazancının %57'sinden azı olmalı; ABD'nin %96'sından azı. Referans medyanı 0,21–0,38.
- **Fransa kenarda** (kayıp-dışı varyantlarda bile kazanç ×0,5 ile bant içi; k\* 0,50–0,57); **İsrail** A ve C'de dayanıklı, B'de kazanç ×0,5 ile bant içine düşer (en kötü marj −0,06).
- **k\* (kazanç çarpanı):** ABD 0,04, Suudi Arabistan 0,09–0,12, BAE 0,15–0,17, AB 0,17–0,19: kazançları ana raporun %4–19'una inmeden bant dışı kazanan; bu **büyüklük** etkisi (ABD'nin kazancı 1,9–3,6, bandı 0,09–0,13), ölçüm güvenilirliği değil.
- **Genel okuma:** sınıf iddiasının gücü kayıp tarafının bilinmemesiyle sınırlı. Kayıp modellendiği tek büyük kazananda (İran) iddia sağlam; kayıp bilinmeyen sekiz kazananda iddia "kayıp küçükse" koşullu.

## Kaybı bilinmeyenler referans oranla modellendi
Önceki: kaybı modelde olmayan sekiz aktör (Çin, Rusya, ABD, AB, BAE, Suudi Arabistan, Fransa, Yunanistan) `havza_kayip = 0` ile yaşıyor, yalnız sınamada kayıp varyantı uygulanıyordu. Şimdi **ana modelde** kayıp vekili var:
- **Referans:** kaybı ve kazancı tam modellenmiş, AB bölünmesinden bağımsız İran, İsrail, Mısır'ın kayıp/kazanç oranı (`kayip_referans_orani`): A medyan 0,29 (min 0,23, maks 1,19), B 0,45 (0,29 – 1,56), C 0,22 (0,20 – 1,03). Maksimum hep Mısır.
- **Kayıp vekili** = medyan oran × aktörün kazancı (`havza_kayip_referans`); belirsizliği = (maks − min)/2 × kazanç (`kayip_referans_belirsizlik`), bant bileşeni olarak √(kural² + belirsiz pay² + kayıp belirsizliği²). `net_birlesik_referansli = kazanç − vekil kayıp`. **`havza_kayip` alanı sıfır kalır** (modelli kayıp ile vekil karıştırılmaz; stok-akış kapanışı ve toplamlar etkilenmez). Raporlarda `≈…‡` ile işaretli, kesin değil.
- **Kısmi kapsam proxy'si** (bant medyanı) yalnız kural + belirsiz pay bandını temsil eder; kayıp belirsizliği dahil edilmedi (aksi halde kayıp bandı kısmi kapsamlı aktörlere de bulaşırdı).
- **Sınıf etkisi (C):** Çin net 2,63 → **2,04** (bant ±1,57), Rusya 2,53 → 1,96 (±1,54), ABD 1,92 → 1,50 (±0,81), BAE 0,85 → 0,66, Suudi Arabistan 0,70 → 0,54, AB 0,81 → 0,63, Fransa 0,35 → 0,27: hepsi hâlâ bant dışı kazanan ama marjlar küçüldü. **Yunanistan bant içine düştü** (0,13 ± 0,17).
- **A:** Çin ve Rusya kazanan (marj ≈ 0,25, k\* ≈ 0,93: kazançlarının %7'si silinse bant içine); Fransa ve Yunanistan bant içi. **B:** kaybı modelde olmayan sekizin **hiçbiri bant dışı kazanan değil** (Çin 2,41 ± 3,25 …); B'de yalnız İran kazanan kalır, İsrail kenarda.
- Karar skoru (56,7), karar ve E[TR net] aynı; halka-çevre koalisyonu bileşeni (İran, İsrail) etkilenmedi.
- `BANT_SINAMA`: taban artık referans-kayıplı; varyantlar "bilinmeyen kayıp = 0 (yalnız modelli)" ve "en yüksek referans oran"; r\* (kayıp belirsizliği hariç diğer bant) korunur: Çin 0,57, Rusya 0,56, ABD 0,96 (C).

## Senaryoya maliyet eklendi: dış ülkelerin kaybın devamlılığı için katlandığı maliyet
`data/etki_cephesi/surdurme_maliyeti.json` (varsayım, ölçülmüş veri yok). Dış aktör, TR'nin kaybını sürdürmek için (karşı-hamleyi etkisizleştirme: diplomatik/güvenlik varlığı, finansman, lobi, yaptırım uygulama) kazancından bir kısmını harcar.
- **Formül:** maliyet = κ · pol_s · aktörün kazancı. κ = **0,20** (varsayım, bant 0,10 – 0,35); pol_s = clip(1,05 − etki erozyonu + diplomatik esneklik, 0,25, 1) = **TR'nin karşı-hamle gücü** (`stok_akis_sim` ve `finans_katman` ile aynı formül): A 0,70, B 0,41, C 0,95. TR güçlüyse kaybı sürdürmek pahalı (C), zayıfsa ucuz (B). TR ve MFIN muaf; maliyet kazancı aşamaz (oran < 1). Kazançla orantılı dağıtılır (bedava binici yok sayılır).
- **Çıktı:** `surdurme_maliyeti`, `net_birlesik_maliyetli` (projeksiyon), `net_maliyetli` (defter); bant, κ bandının yarı aralığıyla (±(0,35−0,10)/2 · pol · kazanç) genişler; sınıf maliyetli net'e göre. `SENARYO_RAPOR` bölüm 10: Σ maliyet A 2,36 / B 1,82 / C 2,38; Σ dış kazanç (TR, MFIN hariç) 19,2 / 25,2 / 14,2; maliyet/kazanç %12 / %7 / %17.
- **Sınıf etkisi (C):** Çin net 2,04 → **1,54** (bant ±1,60), Rusya 1,96 → 1,48 (±1,57): **bant içine girdiler** (`rant_kanali_bosluk_taraftari`); Fransa de bant içi. ABD 1,13 (±0,84), BAE 0,50, Suudi Arabistan 0,41, AB 0,48, İran 0,95 (±0,23), İsrail 0,36 hâlâ bant dışı kazanan. **A:** Çin ve Rusya bant içinde; ABD, BAE, Suudi Arabistan, AB kazanan. **B:** yalnız İran kazanan.
- **Karar etkisi:** skor 56,7 → **53,7**, karar `kisitli_uygulanabilir`; karar eşiği P(C) 0,63 → **0,75**; K2 sonuçları skoru 51,2 – 55,3'e indi. **Bu 3 puan dolaylı bir etki:** doğrudan maliyetin değil, `direnc_dusuk` bileşeninin (1,0 → 0,75) sonucu. Çin ve Rusya bant içine düşünce "rant kanalı boşluk taraftarı" etiketini aldılar ve direnç sayımına girdiler; bant dışı kazanan olarak bu sayıma girmiyorlardı. Yani direnç, aktörün boşluk rantından yararlanmasına değil sınıf etiketine bağlı: kazanan = direnç yok, bant içi + büyük rant farkı = direnç. Bu tutarsızlık maliyetten önce de vardı, maliyet onu görünür kıldı.
- `BANT_SINAMA`: taban artık referans-kayıplı ve maliyetli; varyantlar "sürdürme maliyeti = 0" ve "κ üst".

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
