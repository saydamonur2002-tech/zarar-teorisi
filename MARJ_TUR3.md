# Tur 3: dipnot, örneklem, çıkış, beta, TCMB kalanı

Pencere 2016–2022. Sıralama 2023 yıllık satışı. Banka, sigorta ve diğer finans aracıları dışarıda. Tam panel: 2016–2023 satışı pozitif 265 faaliyet firması. İlk 100 eşiği 7,63 milyar TL. Firma değişimi = (2022 marjı − 2016 marjı) × 100. Çekirdek = (brüt + pazarlama + genel yönetim + Ar-Ge) / satış. Medyanlar toplanmaz. Eksik satır doldurulmaz.

Baştaki açıklanamayan kalan: TCMB imalat (NACE C) faaliyet kârı / net satış, 2016’dan 2022’ye **+4,08 puan** yükselir. Bu artışın kambiyo katkısı **0 puandır**. Kimlik şöyledir: brüt marj **+1,31** + faaliyet gider oranının düşmesi **+2,76** (pazarlama +1,18, genel yönetim +1,52, Ar-Ge +0,05) = +4,08. Kimlik kalanı **0** (10⁻⁷ puanın altında). Net kambiyo / satış **+0,33 puan** değişir ve F satırındadır; faaliyet kârı F’den önceki satırdır, dolayısıyla bu +0,33 faaliyet kârının içine girmez. KAP tarafında, aşağıda tanımlanan imalat-benzeri hayatta kalanların çekirdek marjı toplam/toplam **+0,44 puan** değişir (n = 188, iki yılda da 188). 4,08 − 0,44 = **3,64 puan**. Bu çıkarma bir kalem kimliği değildir. Tezin açıklanamayan kısmı bu 3,64 puandır: TCMB toplamının içi kapanıyor, KAP ile TCMB arasındaki işaret ve büyüklük farkı kapanmıyor.

## Üç cümle

En güçlü bulgu: TCMB’deki +4,08 puanın kambiyo payı sıfırdır ve kimlik kalanı sıfırdır; KAP imalat-benzeri panelin çekirdek toplamı +0,44 puandır, aradaki 3,64 puan kalemlere dağıtılamaz. Aynı pencerede net finansman medyanı ilk 100’de +2,79, küçük hayatta kalanlarda −2,68 puandır; eksi işaret, 2016 çekirdeği yüksek küçük firmalarda toplanır (−7,80, n = 71).

En büyük belirsizlik: +2,14 puanlık vergi öncesi medyanı, satış ve vergi öncesinin 96/99 firmada TMS 29 karşılaştırmalısı olduğu bir sütundandır; `3HC` bu karşılaştırmalı finansman gideriyle 12/98 firmada örtüşür. Dipnotu iki yılda da kapanan 25 firmada net kur medyanı +0,82, net faiz −1,19, net diğer −0,14’tür; üç medyanın toplamı −0,51, aynı 25’in özgün vergi öncesi medyanı +3,87’dir.

Sonraki adım: `3HC`’nin hangi XBRL kalemine bağlandığını satır satır eşlemek ve başlığı bulunamayan dipnotları elden okumak. Çıkış dosyasında açıklaması boş olan 23 firmanın birleşme mi olduğu bu dosyayla belirlenemez.

## 1. Finansman satırının ayrıştırılması

Etiket: dipnotu kapanan firmalar için **hesaplandı**. +2,14 puanın kur / faiz / diğer dağılımı için **belirlenemiyor**.

Kaynak, ilk 100’ün KAP yıllık finansal raporu: 2016 ve 2022 özgün bildirimlerinin PDF dipnotu. Yüz toplamı aynı bildirimin XBRL `FinanceIncome` / `FinanceCosts` tutarıdır. Dipnot satırları bu toplama yüzde 1 içinde kapanmazsa firma o yıl ayrıştırılmış sayılmaz. Gider dipnotu bazen parantezle (negatif), bazen pozitif yazılır. Blok toplamı negatifse kalemlerin işareti birlikte çevrilir; kapalı toplam korunur. Satır satır mutlak değer aynı 25 firmada aynı medyanı verdi (karışık işaretli blok sayısı 3). Sınıf: kur farkı veya kambiyo → kur; faiz, katılım, kâr payı, reeskont, iskonto ve kiralama+finansman → faiz; kalan → diğer. Parasal kazanç ayrı bir sınıf olarak geçmedi.

İki yılda da gelir ve gider dipnotu kapanan firma **25 / 100**. Kodlar: AKENR, ASUZU, AYES, BIMAS, CMENT, DGNMO, DYOBY, ECILC, EGPRO, GOLTS, HEKTS, INDES, JANTS, KAREL, PETKM, PGSUS, PNSUT, SARKY, TKFEN, TUPRS, ULUUN, VAKKO, VESBE, VESTL, ZOREN.

Bu 25, özgün bildirim, puan:

| Kalem | n | p25 | Medyan | p75 | Ortalama |
| --- | ---: | ---: | ---: | ---: | ---: |
| Net kur | 25 | −0,43 | +0,82 | +2,07 | +1,033 |
| Net faiz | 25 | −1,95 | −1,19 | +0,82 | −0,268 |
| Net diğer | 25 | −0,97 | −0,14 | +0,20 | −0,279 |
| Üç kalemin toplamı | 25 |  | −0,51 |  | +0,486 |
| Yüz net finansman | 25 | −2,35 | −0,32 | +2,95 | +0,486 |
| Vergi öncesi (XBRL) | 25 | +1,24 | +3,87 | +15,18 | +16,503 |

Üç medyanın toplamı (−0,51) yüz finansman medyanından (−0,32) **0,19 puan** uzaktır. Üç ortalamanın toplamı (+0,486) yüz finansman ortalamasına kapanır (fark 0,0002 puan). Aynı üç ortalama, vergi öncesi ortalamasına kapanmaz: fark **16,0 puan**. Bu ortalama tek firmaya bağlıdır: ECILC’nin özgün vergi öncesi marjı 2016’da %14,0, 2022’de %250,1’dir (satış 1,83 milyar TL, vergi öncesi 4,58 milyar TL, birim bin TL). Medyan +3,87 bu firmanın kuyruğu değildir.

Tek taraf kapalıyken kalem / satış değişimi (eksik sınıf 0 yazıldı; medyan 0, satırın hiç olmadığı firmaları da içerir):

| Kalem | n | p25 | Medyan | p75 |
| --- | ---: | ---: | ---: | ---: |
| Kur geliri | 29 | −1,03 | +0,02 | +1,06 |
| Faiz geliri | 29 | −0,16 | 0,00 | +0,21 |
| Diğer gelir | 29 | −0,12 | 0,00 | +0,22 |
| Kur gideri | 27 | −1,52 | −0,33 | +0,55 |
| Faiz gideri | 27 | −0,21 | +0,45 | +1,91 |
| Diğer gider | 27 | −0,02 | +0,02 | +0,89 |

Gider satırında eksi değişim, giderin satışa oranının düştüğünü söyler.

+2,14 puanın dağılımı. Bu sayı, ilk 100’ün İş Yatırım vergi öncesi medyanıdır ve 2022 ucu karşılaştırmalı sütundur. 25 firmanın dipnotu özgün bildirimdedir ve örneklem 100 değildir. Bu iki nesne birbirine bölünemez. Aynı 25’in kendi vergi öncesi medyanı (+3,87) ile üç kalem medyanının toplamı (−0,51) arasındaki fark **+4,38 puandır**. Bu 4,38, medyanlar toplanamadığı için bir “kalan kalem” değildir. Çekirdek, diğer faaliyet ve yatırım bu 25’in dipnot hesabında yoktur.

Özgün XBRL, ilk 100, 2016’dan 2022’ye: vergi öncesi medyan **+6,53** (n = 94; p25 +0,08; p75 +16,36). Karşılaştırmalı 2022 eksi özgün 2016: vergi öncesi medyan **+2,16** (n = 93). Özgün 2022 marjı eksi karşılaştırmalı 2022 marjı: vergi öncesi medyan **+2,59** puan (n = 99; p25 0; p75 +6,07). Net finansman için aynı farkın medyanı **0,00** (n = 86). Yani restatement vergi öncesi marjı kaydırıyor; yüz net finansman marjının medyan farkı sıfır. KAP yüz net finansman değişiminin medyanı özgün seride **−0,08** (n = 73), karşılaştırmalı 2022 ucunda **−0,09** (n = 73). İş Yatırım net finansman medyanı **+2,79** (n = 100) bu iki KAP medyanının aynısı değildir.

İş Yatırım 2022 sütununun KAP ile örtüşmesi (göreli fark %1’in altı):

| Kalem | Özgün 2022 | 2023 karşılaştırmalısı |
| --- | ---: | ---: |
| Satış | 12 / 100 | 96 / 99 |
| Vergi öncesi | 12 / 100 | 96 / 99 |
| Finansal gelir | 9 / 87 | 86 / 89 |
| Finansal gider | 10 / 99 | 12 / 98 |

Örtüşmeyen üç satış kodu KRDMA, KRDMB, KRDMD’dir; karşılaştırmalı sütun grup toplamıdır. 2016’da satış 80/94, vergi öncesi 82/94, finansal gider 76/94 örtüşür. Canlı İş Yatırım sorgusunda AEFES `3HC` 2022 sütunu +3,72 milyar TL’dir; KAP karşılaştırmalı finansman gideri −13,86 milyar TL, özgün 2022 gideri −7,57 milyar TL’dir. Üçü de ayrı sayıdır. `3HC` medyanı bu turda KAP finansman gideri gibi okunamaz.

Ayrıştırılamayan **75** firma. Engel, yıl ve taraf çiftinin durumudur. 23 firmada 2022 iki taraf da kapandı, 2016 kapanmadı; değişim medyanına girmediler.

| Engel | Firma |
| --- | --- |
| 2016 ve 2022 başlık yok | AKSA, AKSEN, ARCLK, ASELS, BANVT, CCOLA, CLEBI, DARDL, INGRM, OTKAR, SANKO, SASA, TATGD, TOASO, TTKOM, TTRAK, ULKER, YATAS |
| Yalnız 2016 başlık yok (2022 kapandı) | AEFES, BEYAZ, CIMSA, ISDMR, KRDMA, KRDMB, KRDMD, TCELL, THYAO |
| 2016 yüz toplamı yok, gider PDF metni yok; 2022 de yok | ALCAR, ARENA, BIZIM, DEVA, KARSN, MPARK, SELEC, TBORG |
| Yalnız 2016 yüz toplamı ve PDF metni yok | AYEN, BTCIM, CRFSA, GUBRF, KORDS, MNDTR |
| 2016 yüz/PDF yok, 2022 başlık yok | BESLR, BRISA, DOAS, KENT, TAVHL, TKNSA |
| 2016 toplam satırı yok (2022 kapandı) | BRSAN, EREGL, IZMDC, MNDRS |
| Yalnız 2022 başlık yok | AYGAZ, FROTO, NUHCM |
| 2016 bildirim listede yok; 2022 yüz/PDF yok | SOKM, TRENJ, TRMET |
| 2016 bildirim yok, 2022 başlık yok | MAVI |
| 2016 bildirim yok, 2022 yüz toplamı yok | TRALT |
| 2016 bildirim yok, 2022 gider kapanmadı | ENJSA |
| İki yıl da kapanmadı | SISE |
| 2016 toplam satırı yok, 2022 başlık yok | TUKAS |
| 2016 gider kapanmadı | GOODY, ODAS |
| Tek taraf veya karışık | AKCNS, BASCM, BUCIM, DOKTA, ENKAI, GSRAY, MGROS, OYAKC, PRKAB, RYSAS, TMSN |

Başlık yok, metinde “finansman geliri/gideri” veya “finansal geliri/gideri” başlığı ile yüz toplamı aynı pencerede bulunamadı demektir. Tahmin edilmedi.

## 2. Büyük ve küçük firmalar

Etiket: **hesaplandı**. Taban, İş Yatırım dosyasıdır. 2022 satış ve vergi öncesi karşılaştırmalı sütundur. Net finansman `3HB + 3HC`’dir ve bölüm 1’deki KAP finansman gideri değildir. Ortalamalar bu bölümde yok: küçük kümenin çekirdek değişim ortalaması +835 puandır ve tek firmaya bağlıdır (PRKME, +137.973 puan).

İlk 100. Eşik 7,63 milyar TL. Eksik satır 0.

| Kalem | n | p25 | Medyan | p75 |
| --- | ---: | ---: | ---: | ---: |
| Çekirdek | 100 | −5,98 | −0,98 | +3,25 |
| Faaliyet (`3DF`) | 100 | −5,69 | −0,14 | +3,24 |
| Vergi öncesi | 100 | −3,80 | +2,14 | +12,33 |
| Net finansman | 100 | −2,68 | +2,79 | +9,53 |

Küçük hayatta kalanlar. Aynı panelin eşiğin altı, n = 165. Eksik satır 0. İlk 100 ile birleştirilmedi.

| Kalem | n | p25 | Medyan | p75 |
| --- | ---: | ---: | ---: | ---: |
| Çekirdek | 165 | −9,20 | +1,78 | +14,12 |
| Faaliyet (`3DF`) | 165 | −7,02 | +4,15 | +16,11 |
| Vergi öncesi | 165 | −11,20 | +0,67 | +21,30 |
| Net finansman | 165 | −14,53 | −2,68 | +10,16 |

İşaret dönüşü. Net finansman medyanı büyükte artı, küçükte eksidir. 2023 satışının beş dilimi (her biri n = 53):

| Dilim | Satış aralığı (milyar TL) | Çekirdek medyan | Faaliyet medyan | Vergi öncesi medyan | Net finansman medyan |
| --- | --- | ---: | ---: | ---: | ---: |
| Q1 | 0,01–0,47 | +8,25 | +9,83 | +13,36 | −2,68 |
| Q2 | 0,48–2,15 | +4,33 | +6,19 | +0,54 | −4,58 |
| Q3 | 2,16–6,39 | +0,41 | +0,14 | −2,54 | −0,50 |
| Q4 | 6,96–27,3 | −1,89 | −0,94 | +2,13 | +2,87 |
| Q5 | 27,6–991 | −0,18 | +0,38 | +2,16 | +1,62 |

İşaret, Q3 ile Q4 arasında, kabaca 6–7 milyar TL satışta artıya döner. En eksi medyan en küçük dilimde değildir; Q2’dedir (−4,58).

2016 çekirdek medyanı %6,82. İlk 100 ile çapraz:

| Hücre | n | Çekirdek | Faaliyet | Vergi öncesi | Net finansman |
| --- | ---: | ---: | ---: | ---: | ---: |
| Büyük, 2016 çekirdek yüksek | 62 | −3,21 | −1,72 | +0,85 | +2,98 |
| Büyük, 2016 çekirdek düşük | 38 | +1,37 | +1,16 | +2,88 | +1,42 |
| Küçük, 2016 çekirdek yüksek | 71 | −5,26 | −2,90 | −6,23 | −7,80 |
| Küçük, 2016 çekirdek düşük | 94 | +8,34 | +9,47 | +6,98 | +0,35 |

Eksi finansman medyanı “bütün küçükler” değildir. Küçük ve 2016 çekirdeği yüksek olan 71 firmadadır. Büyük firmanın iki yarısı da artıdır.

|Çekirdek değişiminin| medyanı 8,22 puan. Bu eşiğin üstü ve altı, büyükte finansman medyanını eksiye çevirmez (+0,80 ve +2,87), küçükte artıya çevirmez (−3,13 ve −2,27). İşaret, değişimin büyüklüğüyle değil satış dilimi ve 2016 çekirdek düzeyiyle birlikte gider.

Kardemir üç pay senedi (KRDMA, KRDMB, KRDMD) ilk 100’ün içindedir. A ve B düşülüp yerleri doldurulmazsa n = 98 olur; çekirdek medyanı −0,65, vergi öncesi +2,01, net finansman +2,17. İşaret durur, finansman medyanı 0,6 puan küçülür.

## 3. Çıkan firmalar

Etiket: çıkış tarihi ve dosyadaki açıklama için **doğrudan gözlendi**. Marj ve nakit oranları için **hesaplandı**. Konkordato ve açıklaması boş çıkışın hukuki nedeni için **belirlenemiyor**.

Kaynak, Borsa İstanbul işlem sırası kapanan şirketler dosyası, çıkış tarihi 2016-01-01 ile 2023-12-31. Anahtar kelimeyle faaliyet 38, holding 14, finans 6, fon 9. “YATIRIM” geçen ve holding sayılan, bu yüzden ölçülmeyen üç ad: BOYP (Beymen, 2019-12-25), MEMSA (2020-11-27), EGCEY (2020-10-30). Dosyanın tamamında “konkordato” geçen satır **0**’dır. Bu, konkordato olmadığı anlamına gelmez; dosya onu yazmıyor.

İş Yatırım XI_29’dan en az bir yıl marjı gelen **31**. Hiçbir yılda marjı olmayan **7** aşağıda, veri yok listesindedir. 2016 marjı ölçülen **22 / 31**. 2017–2021 arasında son tam yılı olan **18**. Son tam yılı 2022 olan **0**. 2016’da çıkanların son tam yılı çoğu zaman 2015’tir; bu, istenen 2017–2021 aralığının dışındadır.

Kâr ile nakit: son tam yılda vergi öncesi marjı artı ve faaliyet nakit akışı / kısa vadeli yükümlülük eksi olan firma, her ikisi de dolu olanlar arasında **0**’dır. Koşul 18 firmada hesaplandı, 13 firmada nakit veya vergi öncesi eksik olduğu için **belirlenemiyor**. NTTUR’da vergi öncesi marj +%13,9 iken faaliyet kârı / |finansal gider| −0,76’dır; nakit akışı satırı yoktur. Bu, kâr tanımı ile nakit akışının ayrışması değil, vergi öncesi ile faaliyet kârının ayrışmasıdır.

Oranların medyanı yazılmadı. ATPET net borç / FAVÖK −296, NTTUR +69, MRTGG faaliyet / |finansal gider| −147’dir. BAKAN’ın 2016 vergi öncesi marjı −%166.730’dur; satışa göre ölçek bozuktur ve tabloda “ölçek” diye bırakıldı. ADANA, ADBGR ve ADNAC aynı vergi öncesi marjı (%22,4) ve aynı faaliyet / |finansal gider| (1,76) paylaşır; nakit / kısa vadeli yükümlülük 1,25, 0,89 ve 0,12’dir. Üç pay senedi, tek ihraççı. Çimento kümesinin 2020-05-21 çıkışında dosya açıklaması boştur; birleşme denmedi.

Marjlar düzeydir, değişim değildir. nakit = faaliyet nakit akışı / kısa vadeli yükümlülük. nb = (finansal borç − nakit) / (faaliyet kârı + |amortisman|). kap = faaliyet kârı / |`3HC`|; saf faiz karşılama değildir, çünkü `3HC` faizden ibaret değildir.

| Kod | Çıkış | Son tam yıl | Önceki | Çekirdek 2016 | Vergi öncesi 2016 | Son nakit | Son nb | Son kap | Dosya nedeni |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| PLASP | 2016-04-14 | 2015 | yok | yok | yok | yok | −0,57 | −3,38 | açıklama boş |
| MRTGG | 2016-05-18 | 2015 | yok | yok | yok | yok | −2,29 | −146,87 | açıklama boş |
| VIAGO | 2016-07-27 | 2015 | yok | yok | yok | yok | 1,55 | 5,60 | açıklama boş |
| TARAF | 2016-07-28 | 2015 | yok | yok | yok | yok | 0,75 | 4,76 | açıklama boş |
| UYUM | 2016-11-03 | 2015 | yok | yok | yok | yok | 0,09 | 1,04 | açıklama boş |
| HZNDR | 2016-11-07 | 2015 | yok | yok | yok | yok | −0,10 | 4,08 | açıklama boş |
| FENIS | 2016-12-01 | 2015 | yok | yok | yok | yok | −7,33 | −0,17 | açıklama boş |
| KRATL | 2017-02-07 | 2015 | yok | yok | yok | yok | 4,40 | 0,58 | açıklama boş |
| BAKAN | 2017-03-07 | 2016 | 2015 | ölçek | ölçek | yok | −0,85 | −12,33 | açıklama boş |
| NTTUR | 2017-10-19 | 2016 | 2015 | −%23,4 | +%13,9 | yok | 69,43 | −0,76 | Net Holding’e devir |
| PIMAS | 2017-12-29 | 2016 | 2015 | −%1,5 | %0,0 | 0,30 | −7,22 | −0,07 | Ege Profil’e devir |
| ASCEL | 2018-02-19 | 2016 | 2015 | +%3,2 | −%5,4 | 0,22 | 7,22 | 0,37 | açıklama boş |
| ESEMS | 2018-04-17 | 2017 | 2016 | −%4,3 | −%10,2 | 0,08 | −0,48 | −6,62 | açıklama boş |
| DMISH | 2018-05-02 | 2015 | yok | yok | yok | yok | −2,63 | −0,76 | açıklama boş |
| KIPA | 2018-08-31 | 2017 | 2016 | −%3,5 | −%10,4 | −0,02 | −6,12 | −1,37 | Migros’a devir |
| ANELT | 2018-12-03 | 2017 | 2016 | −%1987 | −%3167 | −0,10 | −12,21 | 0,60 | açıklama boş |
| DGZTE | 2019-02-20 | 2017 | 2016 | +%9,1 | +%53,1 | 0,62 | −3,38 | yok | açıklama boş |
| BMEKS | 2019-03-12 | 2018 | 2017 | −%5,7 | −%12,6 | −0,03 | −2,25 | −1,82 | açıklama boş |
| ATPET | 2019-03-21 | 2017 | 2016 | −%7,5 | −%4,7 | −0,22 | −295,65 | −0,17 | açıklama boş |
| IZOCM | 2019-10-02 | 2018 | 2017 | +%8,1 | +%6,8 | 0,26 | 0,63 | 2,11 | açıklama boş |
| ADANA | 2020-05-21 | 2019 | 2018 | +%23,2 | +%39,8 | 1,25 | −0,70 | 1,76 | açıklama boş |
| ADBGR | 2020-05-21 | 2019 | 2018 | +%23,2 | +%39,8 | 0,89 | −0,98 | 1,76 | açıklama boş |
| ADNAC | 2020-05-21 | 2019 | 2018 | +%23,2 | +%39,8 | 0,12 | −7,07 | 1,76 | açıklama boş |
| ASLAN | 2020-05-21 | 2019 | 2018 | +%26,4 | +%22,3 | 0,36 | 5,46 | 0,58 | açıklama boş |
| BOLUC | 2020-05-21 | 2019 | 2018 | +%31,2 | +%29,5 | 0,50 | 4,32 | 0,32 | açıklama boş |
| UNYEC | 2020-05-21 | 2019 | 2018 | +%24,6 | +%29,3 | 1,29 | 0,00 | 2,70 | açıklama boş |
| ANACM | 2020-09-30 | 2019 | 2018 | +%5,2 | +%27,3 | 0,25 | 2,36 | 1,45 | Şişecam’a devir |
| DENCM | 2020-09-30 | 2019 | 2018 | −%18,4 | −%19,2 | 0,39 | −1,28 | 0,37 | Şişecam’a devir |
| SODA | 2020-09-30 | 2019 | 2018 | +%20,1 | +%31,2 | 0,45 | −0,54 | 1,43 | Şişecam’a devir |
| TRKCM | 2020-09-30 | 2019 | 2018 | +%7,4 | +%20,0 | 0,30 | 1,87 | 0,81 | Şişecam’a devir |
| OLMK | 2022-10-20 | 2021 | 2020 | −%1,8 | −%2,9 | 0,00 | 0,48 | 9,95 | Mondi Turkey’e devir |

OLMK’nın çıkış öncesi son iki yılında vergi öncesi marj −%1,1’den +%9,4’e gelir; nakit / kısa vadeli yükümlülük −0,16’dan +0,00’a, net borç / FAVÖK 6,10’dan 0,48’e gelir. Kâr artı, nakit sıfıra yakındır. Ayrışma iddiası için eşik konmadı; iki seri de yazıldı.

Veri yok. İş Yatırım’da hiçbir yılda marj satırı yok. Sessizce düşürülmedi.

| Kod | Çıkış | Dosyadaki ifade |
| --- | --- | --- |
| KILER | 2016-01-04 | Carrefoursa tarafından devir alınmıştır |
| BOYNR | 2016-03-07 | açıklama boş |
| ARBUL | 2016-03-24 | açıklama boş |
| GEDIZ | 2016-12-01 | açıklama boş |
| AKPAZ | 2018-05-02 | açıklama boş |
| PMVR3 | 2020-03-17 | açıklama boş |
| OZBAL | 2022-01-12 | Erciyas Çelik Boru ile devrolunmak suretiyle birleşmiştir |

## 4. Beta eşiği

Etiket: **hesaplandı**. Beta, 2017–2022’de Δlog(satış / deflatör) üzerine Δlog(|satışların maliyeti| / deflatör) regresyonudur. En az beş nokta. İthalat geçişkenliği değildir. 2022 satış ucu, 96/99 firmada TMS 29 karşılaştırmalısıdır; maliyet satırı bu turda XBRL ile tek tek doğrulanmadı. Son Δlog, karşılaştırmalı 2022 ile önceki yılın sütununu karıştırıyor olabilir.

TÜFE, ilk 100, n = 100. Medyan beta 0,954. Sınıfın içindeki çekirdek, İş Yatırım çekirdek değişiminin medyanıdır.

| Eşik | Pay | n | Sınıf içi çekirdek medyan |
| --- | ---: | ---: | ---: |
| ≥ 0,5 | %100 | 100 | −0,98 |
| ≥ 0,7 | %93 | 93 | −0,18 |
| ≥ 0,8 | %87 | 87 | +0,21 |
| ≥ 0,9 | %75 | 75 | +0,78 |
| ≥ 1,0 | %30 | 30 | +1,67 |

Pay, 0,9 ile 1,0 arasında 75’ten 30’a iner. Sınıf içi çekirdek medyanının işareti 0,7 ile 0,8 arasında eksiden artıya döner. Eşik sonucu değiştirir; değiştiği yer tek bir nokta değildir.

Sektör ÜFE’si 41 firmada eşleşti. Medyan ÜFE betası 0,935. Aynı 41 firmada TÜFE betasının medyanı 0,933’tür. ÜFE eksi TÜFE farkının medyanı **−0,003**. Medyan beta deflatörle yer değiştirmez.

Aynı 41 firma, iki deflatör:

| Eşik | TÜFE payı (n) | TÜFE sınıf içi çekirdek | ÜFE payı (n) | ÜFE sınıf içi çekirdek |
| --- | ---: | ---: | ---: | ---: |
| ≥ 0,5 | %100 (41) | +1,85 | %100 (41) | +1,85 |
| ≥ 0,7 | %97,6 (40) | +1,55 | %97,6 (40) | +1,55 |
| ≥ 0,8 | %90,2 (37) | +2,06 | %85,4 (35) | +2,18 |
| ≥ 0,9 | %75,6 (31) | +2,57 | %63,4 (26) | +2,19 |
| ≥ 1,0 | %24,4 (10) | +4,56 | %22,0 (9) | +6,94 |

0,5 ve 0,7’de iki deflatör aynı firmaları seçer. Fark 0,9 eşiğinde açılır: pay 12 puan, sınıf içi çekirdek medyanı 0,4 puan. Bu 41’in kendi çekirdek medyanı, eşik 0,5’te bile +1,85’tir. Tam örneklemin −0,98’i ile karşılaştırılamaz; küme başkadır.

ÜFE’si olmayan 59 firma: 37’sinde sektör haritası vardı, EVDS seri adı bulunamadı, imalat ÜFE yedeği bu turda uygulanmadı. 22’sinde harita yok (ticaret, hizmet, ulaştırma ve benzeri). Ana sektör sayımı: mineral 13, ticaret 11, kimya 10, ana metal 7, ulaştırma 6, dayanıklı 4, hizmet 3, inşaat 2, makine 2, kağıt 1.

## 5. Kaynak uyumsuzluğu

Etiket: TCMB satırları için **doğrudan gözlendi**. KAP toplamı için **hesaplandı**. 3,64 puanın kalem dağılımı için **belirlenemiyor**.

TCMB tekdüzen, NACE C, gelir tablosu dosyası sayfa t7. Faaliyet kârı, F’den önceki satırdır. F’nin içinde kambiyo kârı, kambiyo zararı, faiz geliri, temettü ve enflasyon düzeltmesi vardır. “F’nin içinde olduğu için faaliyet kârına dahildir” cümlesi bu dosyada yanlıştır.

2016 net satış 1.235.363.064; 2022 net satış 10.289.457.866 (bin TL). Marjlar orandır, düzey karşılaştırması yapılmadı.

| Kalem | 2016 marj | 2022 marj | Değişim (puan) | Faaliyet kârına giren |
| --- | ---: | ---: | ---: | ---: |
| Brüt satış kârı | %17,26 | %18,58 | +1,31 | +1,31 |
| Ar-Ge / satış |  |  | −0,05 | +0,05 |
| Pazarlama / satış |  |  | −1,18 | +1,18 |
| Genel yönetim / satış |  |  | −1,52 | +1,52 |
| Faaliyet kârı | %7,68 | %11,76 | +4,08 | +4,08 |
| Kambiyo kârı / satış |  |  | +3,17 | 0 |
| Kambiyo zararı / satış |  |  | +2,83 | 0 |
| Net kambiyo / satış | −%0,12 | +%0,21 | +0,33 | 0 |
| Faiz geliri / satış (F içinde) |  |  | +0,14 | 0 |
| Finansman gideri / satış (H) |  |  | +0,19 | 0 |

Kimlik kalanı 0. Kambiyonun +4,08 içindeki payı 0. Açıklanamayan TCMB-içi kalan **0**.

KAP alt kümesi bu turda şöyle kesildi: tam panelde ana sektörü gıda, mineral, makine, kimya, tekstil, dayanıklı tüketim, kağıt, ana metal veya otomotiv olanlar. Enerji, madencilik, inşaat, hizmet, ulaştırma, ticaret ve “diğer” dışarıda. Bu, resmi NACE C kodu değildir; İş Yatırım ana sektör etiketidir.

| KAP ölçüsü | n | Çekirdek | Faaliyet `3DF` | Vergi öncesi |
| --- | ---: | ---: | ---: | ---: |
| İmalat-benzeri panel, medyan | 188 | +0,46 | +0,95 | +1,45 |
| İmalat-benzeri panel, toplam/toplam | 188 | +0,44 | −0,36 | +1,68 |
| İlk 100 içinden imalat-benzeri, medyan | 69 | −0,99 | −1,23 | +1,80 |
| İlk 100 içinden imalat-benzeri, toplam/toplam | 69 | +0,33 | −0,54 | +1,62 |

Toplam/toplam, TCMB’nin “payların toplamı / satışların toplamı” hesabına daha yakındır. Yine de +0,44, +4,08’in yanında kalır. Medyan ile toplam arasındaki KAP içi fark küçüktür (+0,46’ya karşı +0,44). Boşluk, medyan seçiminden gelmiyor.

TCMB firma sayısı, temel göstergeler t5: imalat toplamı 2016’da 110.002, 2022’de 166.074. Büyük sınıf 3.601 ve 4.197. Gelir tablosu dosyası büyüklüğe göre bölünmemiştir. KAP 188 firma, borsada kalmış ve sekiz yıl satışı dolu olanlardır. 3,64 puanın ne kadarı evren, ne kadarı kâr tanımı (TCMB faaliyet kârı çekirdeğe yakındır; KAP `3DF` diğer faaliyet gelirini de taşır), ne kadarı 2022 karşılaştırmalı sütun, bu çıkarmayla ayrılmaz.

## 6. 2016 satışı boş olanlar

Etiket: sayım için **doğrudan gözlendi**. Halka arz tarihi için **belirlenemiyor**.

Önceki turdaki 213 bu dosyada çıkmadı. Faaliyet listesinde 469 kod vardır. 2016 satışı boş veya pozitif olmayan **203**. Pozitif olan 266. Her faaliyet kodunun 2016 satırı dosyada vardır; boşluk, satırın hiç olmaması değil, satışın boş veya sıfır olmasıdır.

İlk pozitif satış yılı, serinin bu dosyada başladığı yıldır. Halka arz tarihi değildir. Geç halka arz ile veri boşluğu bu alanla ayrılamadı.

| İlk pozitif yıl | Firma sayısı |
| --- | ---: |
| 2017 | 9 |
| 2018 | 54 |
| 2019 | 33 |
| 2020 | 36 |
| 2021 | 35 |
| 2022 | 12 |
| 2023 | 19 |
| Hiç pozitif satış yok | 5 |

Ana sektör: gıda 31, enerji 25, hizmet 24, makine 24, kimya 22, mineral 17, ulaştırma 11, tekstil 10, ana metal 10, ticaret 8, kağıt 6, diğer 5, inşaat 3, dayanıklı 3, madencilik 3, otomotiv 1. Boşluk tek sektörde toplanmıyor. Gıda, enerji, hizmet, makine ve kimya birlikte 126 / 203’tür.

2023 satışı ilk 100 eşiğinin üstünde olan **55** kod bu boşluğun içindedir: AHGAZ, ALFAS, ARASE, ARMGD, ASTOR, AYDEM, AZTEK, BALSU, BASGZ, BIENY, BOBET, CANTE, CATES, CWENE, EBEBK, EKDMR, EKIM, EKSUN, ENERY, ERCB, EUPWR, GENIL, GESAN, GLRMK, GOKNR, HOROZ, IZENR, KARCL, KAYSE, KCAER, KIMMR, KLSER, KLYPV, KMPUR, KOCMT, KOTON, KRVGD, LILAK, MEGMT, MOBTL, MOGAN, MOPAS, OBAMS, OFSYM, PENTA, QUAGR, SARAE, SMRTG, SSAAT, SUNTK, TABGD, VEYAS, YEOTK, YIGIT, YYLGD. Bunların 2016 satışı olmadığı için 2016–2022 değişim paneline girmediler. Panel, geç gelen büyük firmaları dışarıda bırakır.

## A, B, C

| Açıklama | Bu tur | Gerekçe |
| --- | --- | --- |
| A dolaylı ithalat | Belirlenemedi | İthalat miktarı ve firma girdi fiyatı bu turda yoktur; iddia test edilmedi. |
| B fiyatlama gücü | Zayıfladı | “Geçiş yüksek” payı eşikle %100’den %30’a iner; sınıf içi çekirdek medyanının işareti 0,7 ile 0,8 arasında döner. Aynı 41 firmada ÜFE ve TÜFE medyan betası 0,003 puan ayrıdır; pay farkı 0,9 eşiğinde açılır. |
| C finansman / muhasebe | Zayıfladı | Dipnotu kapanan 25 firmada net finansman medyanı −0,32, net faiz −1,19, net kur +0,82’dir ve üçü vergi öncesi medyanı +3,87’yi toplamaz. `3HC` medyanı +2,79, KAP finansman gideriyle 12/98 firmada örtüşür. TMS 29, vergi öncesi değişim medyanını özgün bildirime göre 2,59 puan aşağı çeker. |

## Veri eksikleri

| Eksik veri | Kapattığı soru |
| --- | --- |
| `3HC` ile XBRL finansman giderinin satır satır eşlemesi | İş Yatırım net finansman medyanının finansman gideri olup olmadığı |
| 75 firmada kapanmayan dipnot | +2,14 puanın kur, faiz ve diğer arasında dağılımı |
| Özgün 2022 satışların maliyeti (beta için) | Betanın son noktasının restatement ile şişip şişmediği |
| 59 firmada sektör ÜFE serisi | ÜFE betasını ilk 100’ün tamamına yaymak |
| Çıkış dosyasında boş açıklama (ölçülen 31’in 23’ü) ve konkordato alanı | Çıkışın birleşme mi, iflas mı, konkordato mu olduğu |
| 7 çıkmış firmada hiç XI_29 satırı; 9 ölçülende 2016 sütunu yok | Çıkanların 2016 marjı ve 2017–2021 nakit tablosu |
| Faaliyet nakit akışı, 31’in 11’inde son yılda yok | Kâr ile nakit akışının ayrışıp ayrışmadığı |
| 2016 satışının boş olmasının halka arz tarihi mi, veri boşluğu mu olduğu | 203 firmanın neden panel dışında kaldığı |
| Brüt, pazarlama, genel yönetim ve Ar-Ge satırlarının XBRL ile eşlemesi | Çekirdek medyanının da karşılaştırmalı sütun olup olmadığı. Satış ve vergi öncesi eşlendi; bu dört satır eşlenmedi |
| Firma ithalat miktarı ve girdi fiyatı | Dolaylı ithalat. Bu turda test edilmedi |

## Eleştiri

Dipnot tutarlılığı zayıf. 100 firmanın 25’inde iki yıl ve iki taraf kapanıyor. En sık engel başlığın bulunamamasıdır (18 firmada her iki yıl). Kapanan notta “faiz” sınıfı banka faizini, kiralama faizini ve kıdem tazminatı faizini aynı kovaya koyar. Üç blokta işaretler karışıktır; bu 25’te medyanı değiştirmedi, başka bir örneklemde değiştirebilir. ECILC’nin %250 vergi öncesi marjı kapanan kümenin ortalamasını tek başına taşır. Medyan bu kuyruktan korunur; ortalama korunmaz.

0,8 eşiği veriden çıkmış bir sınır değildir. Pay 0,5’te %100, 0,8’de %87, 1,0’da %30’dur. Sınıf içi çekirdek medyanı 0,7’de hâlâ eksidir (−0,18), 0,8’de artıdır (+0,21). Eşiği 0,1 oynatmak sonucu değiştirir. ÜFE, medyan betayı 0,003 puan oynatır ve 0,9 eşiğindeki payı 12 puan düşürür. “Geçiş yüksek” etiketi eşiğin ve deflatörün seçimidir.

2023 yılını pencerenin dışında bırakmak TMS 29’u dışarıda bırakmadı. İş Yatırım 2022 satış ve vergi öncesi, 96/99 firmada 2023 raporunun karşılaştırmalı sütunudur. Özgün bildirimde vergi öncesi değişim medyanı +6,53 (n = 94), karşılaştırmalı uçta +2,16’dır (n = 93). Pencere 2023’ü kesince restatement 2022 ucunun içinde kalır. Çekirdek paydası da bu satış sütunudur. Payın (brüt ve faaliyet giderleri) aynı sütunla örtüşüp örtüşmediği bu turda satır satır doğrulanmadı.

Bunların yanında: ilk 100 üç Kardemir pay senedini ayrı firma sayar; çıkan çimento kümesi üç pay senedini aynı kârla yazar; Beymen adındaki “yatırım” kelimesi yüzünden faaliyet çıkış listesine girmedi; küçük kümenin ortalaması PRKME’dir.

Bu analiz, faaliyet dışı kârın yapısal bir olgu mu yoksa örneklem ve ölçüm etkisi mi olduğunu ayıramıyor. TCMB kimliği kapanıyor ve kambiyo orada sıfırdır. KAP’ta finansman medyanının işareti örneklemle dönüyor, dipnot alt kümesinde finansman medyanı eksiye yaklaşıyor, `3HC` ise KAP finansman gideriyle çoğu firmada örtüşmüyor. “Fark yok” denemez. Fark ölçülemiyor: aynı kâr tanımının, aynı restatement’ın ve aynı firmanın iki kaynakta yan yana durduğu bir artık elde değil.
