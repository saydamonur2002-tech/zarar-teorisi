# Etki cephesi modeli: revize sonucu

Kaynak: `zarar-teorisi` dalı `cursor/odeme-zinciri-kalicilik-f01a`, `yayin/etki-cephesi-model.zip`.
Doğrulama: yama temiz zip çıkarımına uygulandı, `run_all.py` tek komutla kararlı duruma vardı (özet `9a97b1331fac8996`),
**47 test geçti** (27 mevcut + 20 yeni; bir mevcut testin işareti güncellendi). Orijinal pipeline zip'teki raporları birebir yeniden üretiyor
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

Not: karar hâlâ `uygulanabilir_kosullu`, ama skor eşiğin (62) yalnız 0,7 üstünde.
| 10 | C'nin gerçekleşmesini ölçen bir ölçüt yoktu | `c_dinamik_olcut.py`: sıralı Bayes, EVDS merkez sızıntı oranı; güç analizi (aşağıda) |

## C olasılığı duyarlılığı (yeni rapor)
`olasilik_duyarlilik.py` → `reports/etki_cephesi/OLASILIK_DUYARLILIK.{json,md}`. P(C) 0,30–0,80, kalan A:B taban oranla (0,22:0,18) bölünür.
**Yeni olasılık üretmez**; olasılıklar (A 0,22 / B 0,18 / C 0,60) elle atanmış vekildir.

| P(C) | P(A) | P(B) | E[TR net 10y, yaşam dahil] | E[GSYH %] | E[iyileşme] | Skor | Karar |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0.30 | 0.385 | 0.315 | -22.102 | 6.162 | -4.91 | 57.3 | kisitli_uygulanabilir |
| 0.35 | 0.357 | 0.292 | -21.45 | 5.982 | -4.26 | 58.2 | kisitli_uygulanabilir |
| 0.40 | 0.330 | 0.270 | -20.797 | 5.803 | -3.61 | 59.1 | kisitli_uygulanabilir |
| 0.45 | 0.302 | 0.247 | -20.144 | 5.623 | -2.95 | 60.0 | kisitli_uygulanabilir |
| 0.50 | 0.275 | 0.225 | -19.491 | 5.443 | -2.30 | 60.9 | kisitli_uygulanabilir |
| 0.55 | 0.247 | 0.203 | -18.838 | 5.263 | -1.65 | 61.8 | kisitli_uygulanabilir |
| 0.60 **(taban)** | 0.220 | 0.180 | -18.186 | 5.084 | -1.00 | 62.7 | uygulanabilir_kosullu |
| 0.65 | 0.193 | 0.158 | -17.533 | 4.904 | -0.34 | 63.6 | uygulanabilir_kosullu |
| 0.70 | 0.165 | 0.135 | -16.88 | 4.724 | +0.31 | 65.0 | uygulanabilir_kosullu |
| 0.75 | 0.138 | 0.113 | -16.227 | 4.545 | +0.96 | 67.1 | uygulanabilir_kosullu |
| 0.80 | 0.110 | 0.090 | -15.574 | 4.365 | +1.62 | 69.2 | uygulanabilir_kosullu |

- Karar eşiği (skor 62) geçişi P(C) ≈ 0,56; taban 0,60, yani eşiğe yakın.
- Beklenen karışımda iyileşme ancak P(C) ≳ 0,68'de başlıyor; tabanda yok (Δ −1,00).
- E[TR net 10 yıl] aralığı −22,10 … −15,57.
- Taban satır ana raporla birebir tutuyor; mevcut raporlar yeni parametreden etkilenmedi.

## C için dinamik ölçüt (yeni rapor)
`c_dinamik_olcut.py` → `C_DINAMIK_OLCUT.{json,md}`. Gösterge: merkez sızıntı oranı = 12 ay yatırım geliri gideri / 12 ay mal ihracatı (EVDS, `data/etki_cephesi/gozlem/`). Senaryo sürüklenmesi `ln(merkez_sizinti_carpan)/10` (A 0, B +1,4 %/yıl, C −1,05 %/yıl): varsayımdır.
- Ölçüm baz yıldan sonra başlar (ilk güncelleme 2027-12 verisi): **şimdi güncelleme yok, posterior = prior**. Eksik ay güncellemez.
- **Güç analizi:** yıllık σ = 0,177, C ile A/B arasındaki sürüklenme farkı 0,0105–0,0245. SPRT %95 için **307 (C vs B) ve 1.660 (C vs A) yıl** gerekir; 4000 koşulu Monte Carlo'da 10 yıl sonra gerçek senaryo C de olsa B de olsa E[P(C)] ≈ 0,58–0,61. Gösterge P(C)'yi **doğrulayamaz**.
- **Çapa uyumsuzluğu:** kalibrasyonda 2024 yatırım geliri gideri 18.841 mn $; EVDS 26.483 (×1,41; 2023 = 18.793). `gerceklik_capa.json` değiştirilmedi.
- **Karşı-olgusal trend yok:** oran 2023 sonu 0,075 → 2025 sonu 0,120 (×1,61); senaryoların iki yıllık sürüklenmesi en çok ±0,028.

## P(C) ölçülebilir kapılarla yeniden kuruldu (yeni rapor)
`olasilik_kapilar.py` → `OLASILIK_KAPILAR.{json,md}`. Eski 0,22 / 0,18 / 0,60 elle atanmıştı, dayanağı yoktu. Yeni kurulum:
- **Prior tekdüze (1/3).** Bilgi yoksa ağırlık yok. Ölçüm baz yıldan (2026) sonra başlar; şimdi güncelleme yok → **bugünkü P(C) = 0,333**. Bu ölçüm değil, bilgi yokluğudur.
- **K1 merkez sızıntı sürüklenmesi:** olabilirlik `senaryolar.json`'dan türetilir; ayırt gücü yok (307 yıl).
- **K2 dış kısıt (EVDS `bie_oderoll`, bankalar ve diğer sektörler 12 ay ort. çevirme ≥ %100):** kontrol noktaları 2027-12, 2029-12, 2031-12. Taban oran p0 = tarihçede "açık" pencere payı = **0,534** (232 pencere; bugün açık: K1 109,8, K2 175,0). Olabilirlik **varsayım**: p_A = p0, p_B = p0 − δ, p_C = p0 + δ, δ = 0,10 (tek parametre, duyarlılığı raporda).
- **K3 etki erozyonu** (bölge ihracat payı): EVDS'de seri yok, TİM verisi depoda yok → kapalı. **K4 bağ kullanımı:** gözlenebilir seri yok → kapalı. İkisi de olasılığa girmez: bilinmiyor sıfır değildir.

| K2'de 3 kontrol noktasından açık sayısı | P(A) | P(B) | P(C) | Eşiği (0,561) geçer |
| ---: | ---: | ---: | ---: | --- |
| 0 | 0,305 | 0,547 | 0,148 | hayır |
| 1 | 0,341 | 0,409 | 0,250 | hayır |
| 2 | 0,344 | 0,276 | 0,380 | hayır |
| 3 | 0,312 | 0,167 | 0,521 | hayır |

- **Sonuç:** tek ölçülebilir kapı en iyi ihtimalle P(C) = 0,52 verir; karar eşiği 0,56. Yani bugün eldeki gözlenebilir kanıtla C "uygulanabilir_koşullu" yapılamaz. P(C)=1/3 noktasında duyarlılık bandı `kisitli_uygulanabilir` der (skor ≈ 57–58); ana rapor hâlâ eski 0,60 ile 62,7 / `uygulanabilir_kosullu` gösteriyor.
- δ duyarlılığı: δ = 0,20 ile 3/3 açık → 0,68; δ = 0 ile kapı hiçbir şey söylemez. Eski el ataması prior kullanılırsa sonuç prior'a yaslanır (0,35 … 0,76): tabloyu prior belirler, kapı değil.
- Ana pipeline'ın `olasilik_vekili` değeri **değiştirilmedi** (başlık sayıları kayardı); yeni P(C)'ye bağlamak ayrı karardır.

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
