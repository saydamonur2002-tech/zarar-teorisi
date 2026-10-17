# Senet bacağı taslağı (17.10.2026)

Karar cümleleri durur. `YAPILABILIRLIK.md` zinciri «kırılgan / koşullu yapılabilir» olarak kalır. `senet_kilit.txt` ve `adim4.csv` senet satırı `modellenmedi` kalır. Bu klasör o kilidin dışındaki taslaktır: sayılar `python3 analiz/senet/yaz.py` ile yeniden yazılır. Etiket: **kanıt** depodaki ölçüm ya da kilitli formülün bu girdilerle ürettiği sayıdır; **aday** ölçek, kur ayrımı, eşleşme vekili veya takvimdir.

Koşu: λ* = 1,0357 (beş çeyreklik çapın ortancası, kanıt), β tavan 0,0439, kur δ = %19,29. F.4 2026-Q1 `s0 = 25.339,7608`, `yp = 0,544366`. Değerleme artışı `s0·yp·δ = 2.660,8843` milyar TL (kanıt, formül).

## Lider ve üst %10

Lider, ödeme zincirinde en yüksek mevduatlı sentetik düğümdür (`ODEME_ZINCIRI.md:350`). `LIDER_MEVDUAT.md` yürütme kasasıdır; bu düğüm değildir.

Kod: `N_FIRMA = 150`, üst onda adedi `round(0,10·150) = 15`, hedef paylar `(0,10, 0,40, 0,70)` (`odeme_dagilim.py:72-74`, aday). Firma VF.2 2026-Q1 **8.593,5447** milyar TL (kanıt, `tek_sistem_kopru_ham.csv`). Hedef payın nominali aday: 859,4 / 3.437,4 / 6.015,5.

`ODEME_ZINCIRI.md:528` ve `:536`: dağıtım mahsup blokesini kapatmaz; «üst %10'un tamamı gerekir» elenmedi. Bu bir kalıcılık testidir, kilit eşiği değildir. On firma ya da lider düğümü, mahsup kilidinin anahtarı olarak yazılmamıştır.

## Eşik ve emme tavanı

Adres stoku, `rev_adim4_sonuc.json` (kanıt):

| Taban | Milyar TL |
| --- | ---: |
| Önerilen `A_ön` = hane vadeli + firma vadeli | 12.722,5 |
| Üç satır `A_üç` (gerçek kişi YP 6.639,4 dahil) | 19.361,9 |
| Çift sayım bandının üstü | 19.076,6 |

DİBS 2026-03-27 piyasa 10.339,8 (kanıt). Elinde tutan: H = S14+S11 = **589,3686**. Genişletilmiş S14+S11+S1234+S128+S129 = **2.322,3191**. Kredi katsayısı bandı 0,08–0,787 (aday; eş-hareket, nedensellik değil).

Bu defterleri yıllık akış tavanı saymak adaydır. H, ne %10 ne %30 dilimini alır. Geniş defter %10 yıllık dilimi alır (1.272,25 ve 1.936,19), %30 dilimini almaz. Piyasa her iki yıllık dilimi alır.

## Kanal yok — metin

`model/RAPOR.md:9`: «Yeni para gerekmiyor, sıra kilitli.» Mahsup kapalı lira döngüsünü nakit dolaşmadan kapatır (`RAPOR.md:21`, `TEK_SISTEM.md:5`, `TEK_SISTEM.md:26`).

`RAPOR.md:15-17` ve `:24`: artan servet dolara, altına, vadeliye, fona, arsaya gitmez; hedef primli senet üretimi finanse eder. Prim, hedefin tasarrufundan ya da ikame edilen ithalatın lira karşılığından gelir. Çıkış, senedi satmaktır (`RAPOR.md:47`).

`TEK_SISTEM.md:44` ve `TEK_SISTEM_KADEME.md:3`: katman sonuçları birbirine taşınmaz. `YAPILABILIRLIK.md:61`: Adım 4, 4.5 ve 5 için şok kanalı yoktur.

Kodda `kagit_patikasi` (`adim4_adres_yonlendirme.py:50-68`) mevduat→kâğıt takasını, düz primi ve `0,08` kredi daralmasını yazar. Endeks bacağı «hesaplanmadi». Üretim tesisi ve «prim havadan gelmez» bu fonksiyonda yoktur. %10 taban, metindeki kilidi açan nakit kanalı değildir. Eksik olan, açılan paranın üretim finansmanı ve gerçekleşen tasarruftan primidir.

## Kademeli %10

`M_t = 0,10 · A` her yıl, on yıl. Kalanın %10'u değildir.

| Adres | Yıllık | Çeyrek | Süre | H | Geniş | Piyasa |
| --- | ---: | ---: | ---: | --- | --- | --- |
| `A_ön` | 1.272,25 | 318,06 | 10 yıl | almaz | alır | alır |
| `A_üç` | 1.936,19 | 484,05 | 10 yıl | almaz | alır | alır |

Tam ağ, rant kapısı: çeyrek dilim aracı üretimi kapatır, çekilen **46,7747**, banka kalanı **336,5804**. Seyrek çeyrek 3/30 kapanır (`patika.csv`). Yıl 1 atıl K′, açık bir kez varsayımı (aday): `A_ön` 1.225,48 = 2026 GSYH 84.425'in %1,45'i; kredi bandı 98–964. Sonraki yıllarda atıl, yıllık akışın tamamıdır (açık yeniden doğmaz varsayımı, aday). Çeyrek istatistiği her yıl taze ağda tekrar eder.

## Fungible bacak

Hasıla mahsup sonrası nakde eklenir; sıra BANKA'ya da harcayabilir (`bacak.py`). Aday ölçek: stok `F=θA`, akım `F=θA/4`.

Tam ağ, δ=%19,29, bütçe 0: temerrüt 7, köprü 443,87, kilitli 10, batık 6.

| Kural | Köprüyü sıfırlayan `F*` | Kilit etiketini sıfırlayan `F*` |
| --- | ---: | ---: |
| Açığa orantılı | 443,87 | yok (`acik\|kilit` boş) |
| Borca orantılı | 5.362,42 | 15.649,24 |

`θ=0,10` stok, `A_ön` (1.272,25), açığa orantılı: tam ağda temerrüt 0 ve köprü 0; kilitli etiket 15'e çıkar (brüt teşhis, nakit batığı kilitliye taşır). Borca orantılı aynı bütçe: temerrüt 5, köprü 278,24, kilitli 11. Seyrek, açığa orantılı köprü: 19/30 tohumda sonlu `F*` yok; kapananların ortancası 2.256,89. Brüt kilit etiketi θ ızgarasının içinde sıfırlanmaz. Bu sonuç, metnin «yeni para gerekmiyor» cümlesine göre fazla nakit ister (aday başarı ölçütü).

Prim örneği `τ=0`: Π=0, ΣNL=0. `τ=1` ve `R=0`: Π=0. Havadan kupon ΣNL'yi 0 tutar, «Prim havadan gelmez» sınırını tutmaz.

## Rant kapısı

Koşullar `rant.py` başlığında. Ölçülen vekil: aracı borçlunun ticari ve ücret açığı, kendi nakdinden sonra. BANKA ve holding alacaklısına pay yok. Firma tavanı kendi açığı. Yoğunlaşma tavanı `1/n` aday. e-fatura eşleşmesi ve Sayıştay ödenmeyen emir repoda yok (`VADELI_KALICILIK.md`); sıkı okuma uygun pay **0**. Aşağıdaki sayılar yerçekimi ağı vekilidir (aday).

Tam ağ, bütçe 0: aracı kalan 14,09. Geniş bütçede çekilen **46,7747**, aracı 0, banka **336,5804**. `θ*_stok` = 46,7747 / 12.722,5 = **0,0037**. Yoğunlaşma tavanı çekileni 13,16'da keser, aracı kalan 3,68; sonlu `F*` yok.

Seyrek aracı `F*`: ortanca **2.453,4** (45,34–5.661,94, 30/30 sonlu) → `θ*_stok` = 0,193. Yoğunlaşma: 29/30 sonlu değil. Tüm ticari+ücret (holding borçlusu dahil) 18/30'da kapanmaz.

`θ=0,10` stok `A_ön`: tam ağ üretimi kapanır, atıl 1.225,48, fungible kayış (BANKA'ya giden) 192,50 halkada 0'a iner. Seyrek akım dilimi 318,06: aracı kapanan 3/30, ortanca aracı kalan 1.562,71.

## %30 / yıl

`M_t = 0,30·A` üç yıl, dördüncü yıl kalan `0,10·A`. Süre 3,33 yıl.

| Adres | Yıl 1–3 | Yıl 4 | Çeyrek (tam yıl) | H | Geniş | Piyasa |
| --- | ---: | ---: | ---: | --- | --- | --- |
| `A_ön` | 3.816,75 | 1.272,25 | 954,19 | almaz | almaz | alır |
| `A_üç` | 5.808,57 | 1.936,19 | 1.452,14 | almaz | almaz | alır |

Tam ağ çeyreği yine 46,7747 çeker. Seyrek çeyrek: `A_ön` 7/30, `A_üç` 9/30. Yıl akışı tek bütçe sayılırsa (`fx_durdur_sonuc.json`, açık bir kez, aday): `A_ön` 29/30, `A_üç` 30/30. Holding borçlusunun ticari kalanı bu kapıya girmez.

Yıl 1 atıl, tam ağ, 2026 GSYH: `A_ön` 3.769,98 = %4,47, kredi bandı 302–2.967. `A_üç` 5.761,80 = %6,82, band 461–4.535. Seyrek ortanca yıl akışında çekilen 2.453,78; `A_ön` atıl ortanca 1.364,47.

Tasarım stok kuponu (yıl sonu birikmiş × π) ödenmez. `A_ön`, π=0,02: 76,34 / 152,67 / 229,01 / 254,45. π=0,05 dördüncü yıl 636,13. Ödenen Π=0.

## Prim ve ithalat tavanı

Gerçekleşen R ölçülmedi. `kagit_patikasi` endeks bacağı hesaplanmadı; `hekis_model/data/SENET.md:9` fiziki endeks sabiti 1,00 (başka nesne, eşitlenmez). Formül `Π = τ·min(πM, R)` → τ=0 → **Π=0**. ∂(temerrüt, köprü)/∂Π = 0.

Tavan, gerçekleşen ikame değil. Ticaret Bakanlığı, *Ekonomik Görünüm Aralık 2025*, BEC milyon USD. Derleyen TÜİK; kullanılan satır bakanlık PDF'idir: https://ticaret.gov.tr/data/5e18288613b8761dccd355ce/Ekonomik%20Görünüm%202025%20Aralık.pdf

| | 2024 | 2025 |
| --- | ---: | ---: |
| Ara mal | 238.253 | 250.228 |
| Sermaye | 50.633 | 54.892 |
| Tüketim | 54.469 | 59.237 |
| Toplam | 344.010 | 365.524 |
| Fası 27 enerji | 65.590 | 62.590 |

Kur, `faiz_kur_ham` aylık ortalama (aday): 2024 **32,7802** (n=12), 2025 **39,4264** (n=12). Milyar TL, 2025: ara 9.865,59, enerji 2.467,70, ara−enerji **7.397,89**, ara+sermaye 12.029,78. Ara maldan tüm fası 27'yi düşürmek örtüşme kimliği değildir (aday). Sermaye malı RAPOR'daki «ara mal» cümlesinin dışındadır.

Yıllık ihraç kuponu / 2025 dar tavan:

| θ | Adres | π=0,02 | π=0,05 |
| --- | --- | ---: | ---: |
| 0,10 | `A_ön` | 25,45 (%0,34) | 63,61 (%0,86) |
| 0,10 | `A_üç` | 38,72 (%0,52) | 96,81 (%1,31) |
| 0,30 | `A_ön` | 76,34 (%1,03) | 190,84 (%2,58) |
| 0,30 | `A_üç` | 116,17 (%1,57) | 290,43 (%3,93) |

En büyük tasarım kuponu dar tavanın %3,93'ü. Bu payın ikame edildiği ölçülmedi. ΣNL, τ=0 iken 0. τ=1 ve R kuponu karşılıyorsa yalnız kupon kadar yazılır: NL_H = +Π, NL_D = −Π. K′ primi R'siz öderse toplam yine 0 kalır; «Prim havadan gelmez» bozulur.

## Döviz stok artışını durdurma

`RAPOR.md:44`: «Döviz sözleşmesini silmez. Ticari stokun yaklaşık üçte biri yabancı paradır. Kur şişmesi yerinde kalır.» `RAPOR.md:11` amaç döviz borçlanmasını kısmaktır; bu akış kısıtıdır. `DOVIZ_EGILIM.md:23` kilitli senaryo korunmasız stoku %0 tavan ve geri al ile 120 milyar USD'de tutar (senaryo, `fx_unhedged_buyume_mevcut=0,06` varsayım → 121,8×0,06 = 7,31 milyar USD/yıl). `DOVIZ_EGILIM.md:29-30`: brüt dış borç ile korunmasız hane/firma stoku aynı satır değildir.

Dondurma yeni YP birikimini keser. Mevcut `yp` değerlenmeye devam eder. Artış **2.660,8843**, baz ile aynı.

| | Tam ağ | Yoğunluk 0,25 (30 tohum) |
| --- | ---: | --- |
| Artış | 2.660,88 | 2.660,88 |
| Temerrüt | 7 | 8–15, ortanca 13 |
| Köprü | 443,87 | 472,84–8.250,86, ortanca 4.810,19 |
| Kilitli / batık | 10 / 6 | ortanca adet 7 / 11 |

Rant kapısı `F*` değişmez: tam ağ 46,77, seyrek ortanca 2.453,4. Banka kalanı 336,58.

Durdurulan akış, üç nesne:

| Nesne | Pencere | Miktar | TL | Etiket |
| --- | --- | ---: | ---: | --- |
| Gerçek kişi YP `TP.HPBITABLO2.7` | 2024-Q4 → 2025-Q4 | +40,64 milyar USD | miktar 1.730,54; kur 787,13 | stok kanıt; kur ayrımı aday |
| Aynı seri | 2025-Q4 → 2026-Q1 | +7,55 milyar USD | miktar 332,66 | tek çeyrek |
| Yurt içi YP `.6` | yalnız o çeyrek | +5,40 milyar USD | miktar 238,02 | tüzel miktar −2,15 |
| Brüt dış borç | 2024-Q4 461,2 → 2025-Q4 522,7 | +61,5 milyar USD | açılış kuruyla 2.166 | ayrı stok, yuvarlak türev |
| Özel dış borç | 253,0 → 299,5 | +46,5 milyar USD | 1.638 | aynı |

6.639,4'lük stok `A_üç` içindedir; üstüne eklenmez. Eklenen, 2025 miktar hızıdır (aday: sürer).

Yıl 1 ihraç + bu akış: `A_ön` **5.547,29**, `A_üç` **7.539,11**. H almaz. Geniş defter yalnız FX akışını alır (1.730,54 < 2.322,32), yığılmış dilimi almaz. Piyasa her ikisini alır (0,54 ve 0,73).

Tam ağ atıl / 2026 GSYH: FX tek başına 1.683,76 = %1,99 (band 135–1.325); `A_ön`+%FX 5.500,51 = %6,52 (band 440–4.329); `A_üç`+%FX 7.492,33 = %8,87 (band 599–5.896). Seyrek: FX akışı 9/30 kapatır, aracı ortanca kalan 334,78, atıl ortanca 0. `A_ön` yıl-1 29/30; FX eklenince yine 29/30 (tavan `F*` 5.661,94). `A_üç` yıl-1 30/30.

Adım 2 yazılı koşulu (`YAPILABILIRLIK.md:9`, `:22`) bu taslakta açılmaz: mevcut maruziyet korunmuş sayılmaz (artış durur), kur yükümlülüğü karşılanmış sayılmaz (banka kalanı 336,58; köprü 443,87), yoğunluk 0,25 yoğun ağ değildir, köprü yeniden boyutlanmaz. Dondurulmuş cümle durur.

SFC: yeni akış FX mevduat yerine eşit TL kâğıt ya da TL mevduattır; ek net finansal pozisyon 0. Mevcut kur değerlemesi bazdaki artıştır. Prim 0.

## Dosyalar

| Dosya | İş |
| --- | --- |
| `yaz.py` | Aşağıdakileri sırayla koşar |
| `olcek.py` / `olcek_sonuc.json` | Lider ölçeği ve emme tavanı |
| `bacak.py` / `bacak_sonuc.json` | Fungible üretim tesisi |
| `rant.py` / `rant_sonuc.json` | Rant kapısı |
| `patika.py` / `patika_sonuc.json` / `patika.csv` | %10 ve %30 yıllık kademe |
| `prim_tavan.py` / `prim_tavan_sonuc.json` / `prim_tavan.csv` | İthalat tavanı, ödenen prim 0 |
| `fx_durdur.py` / `fx_durdur_sonuc.json` / `fx_durdur.csv` | Stok dondurma |
| `test_cikti.py` | Başlık kilitleri; modeli yeniden koşmaz |
