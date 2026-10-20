# Seçim ekonomisi

H1, seçim öncesi gevşeme: **Belirsiz**. H2, seçim sonrası kur baskısı: **Belirsiz**. Sonrası politika faizi: havuz eşiği tuttu, **aday**. H3, 2021 sonu 2023 seçiminin uzun ısınması mı: **seçim takvimiyle açıklanamaz**, aday.

Karşı-olgu yok. Eşik tutması “seçim bunu yaptı” demek değildir. Kanıt yazılmaz.

Kilit `ON_KAYIT.md`, 2026-10-20T13:35:47Z. Kutu testinin p değerleri girdi yapılmadı. Taslak hesap `hesap.py`, tablo `secim_tablo.csv`.

## Seçim seçim

Öncesi, seçimden önceki altı ayın ortalamasıdır. Sonrası, sonraki altı ayın. Faiz, aylık puan farkıdır. Rezerv, brüt resmi rezervin aylık yüzde değişimidir. EMP, aylık baskıdır. Harcama, faiz hariç bütçe giderinin reel yıllık yüzde değişimidir. Boş hücre, o pencerede seri yoktur.

| Seçim | Tür | Faiz önce | Faiz sonra | Rezerv önce | EMP önce | EMP sonra | Harcama önce |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2002-11 | Genel | −0,33 | −0,50 | 2,16 | 2,03 | −2,61 | |
| 2007-07 | Genel | 0,00 | −0,33 | 1,90 | −2,87 | −2,53 | 14,5 |
| 2011-06 | Genel | −0,12 | −0,08 | 2,49 | −0,48 | 4,08 | 9,6 |
| 2015-06 | Genel | −0,12 | 0,00 | −1,62 | 4,12 | 2,31 | 2,7 |
| 2015-11 | Genel | 0,00 | 0,00 | −0,59 | 2,15 | 0,35 | 6,9 |
| 2018-06 | Genel | 0,00 | 1,04 | −1,05 | 2,93 | 2,88 | 6,7 |
| 2023-05 | Genel | −0,33 | 5,25 | 0,36 | 0,36 | 1,50 | 15,7 |
| 2004-03 | Yerel | −1,33 | −0,33 | 2,05 | −2,54 | 1,45 | |
| 2009-03 | Yerel | −0,88 | −0,54 | −1,70 | 7,07 | −3,09 | 14,6 |
| 2014-03 | Yerel | 0,92 | −0,29 | −0,34 | 2,34 | −0,72 | 4,4 |
| 2019-03 | Yerel | 1,04 | −1,25 | 2,06 | −3,06 | 0,13 | 6,0 |
| 2024-03 | Yerel | 3,33 | 0,00 | 1,74 | 0,79 | −1,93 | 47,1 |
| 2010-09 | Referandum | 0,08 | −0,12 | 2,09 | −1,71 | −0,55 | 4,9 |
| 2017-04 | Referandum | 0,08 | 0,00 | −1,75 | 4,96 | −1,82 | 11,7 |

Sayılar [HESAP]. Yedi genel seçimin 5/7 eşiği yerel ve referanduma uygulanmaz.

## H1

Gevşeme, plasebonun yüzde 90’ından daha gevşekse uç sayılır. 2000 takvim, çekirdek 20261020 [HESAP]. Havuz p tek taraflıdır. Holm, verisi en az altı genel seçimi kapsayan göstergelerdedir.

| Gösterge | Genel seçim | Uç | Havuz fark | p | Holm | İki çubuk |
| --- | --- | --- | --- | --- | --- | --- |
| Politika faizi | 7 | 0 | −0,14 puan | 0,44 | 1,00 | yok |
| Brüt rezerv | 7 | 0 | −0,54 puan | 0,41 | 1,00 | yok |
| Faiz hariç harcama, reel | 6 | 0 | +2,2 puan | 0,34 | 1,00 | yok |
| Cari transfer, reel | 6 | 0 | +0,8 puan | 0,61 | 1,00 | yok |
| Personel, reel | 6 | 1 (2023) | +7,7 puan | 0,20 | 1,00 | yok |

Faiz ve rezervde havuz, gevşeme yönündedir: faiz biraz inmiş, rezerv artışı tabandan yavaştır. Bu fark plasebo takvimlerinde de sık görülür. Hiçbir genel seçim, faiz ya da rezervde en gevşek yüzde 10’a girmez. 2002’de faiz ayda 0,33 puan inmiştir. Bu, plasebo kuyruğu değildir.

Personelde yalnız 2023 uçtur. Reel personel gideri seçim öncesi yüzde 30 büyümüştür. Havuz p 0,20’dir. Holm eşiği tutulmaz.

Ölçülmeyen ya da altı seçime yetmeyen kollar DOĞRULANMADI: etkin fonlama (dört seçim, seri 2011’de başlar), kredi (beş seçim, seri 2007’de başlar), swap hariç net ve arka kapı satışı (swap stoku 2021’de başlar, bir genel seçim), asgari ücret ve memur zammı takvimi, KGF, EPDK/BOTAŞ fiyatı, koridorun taban ve tavanı. Bu yüzden H1 Belirsiz kalır. Ölçülen kollar da iki çubuğu tutmadığı için “eşik tuttu” denmez.

2023 öncesi kredi stoku yıllık yüzde 57 büyümüştür [HESAP]. Beş seçim olduğu için bu sayı çubuğa yazılmaz.

## H2

Birincil EMP’de sonrası eksi taban **+0,05** puandır [HESAP]. Plasebo p 0,41. Holm 0,41. Yedi seçimden dördünde sonrası, tabanın üstündedir (2011, 2015 Haziran, 2018, 2023). Beş gerekir. Eşik tutulmaz.

İşaret pozitiftir. Kutu testindeki “sonrası tabanın altında” sonucu bu tanımda çıkmaz. İşaret ters olmadığı için H2 Yanlışlandı yazılmaz.

Ay sonu kurla kurulan EMP’de havuz **+0,23** puandır, aynı işaret. p 0,44. Üç seçimde tabanın üstündedir. Ters işaret kapısı açılmaz.

Kontrol regresyonu kurulmadı. FRED dolar endeksi, ABD 2 yıl faizi ve VIX zaman aşımına uğradı. Başka siteden vekil konmadı. Kontrollü test DOĞRULANMADI. Kilit, kontrol inmezse havuz tutsa bile H2’yi Belirsiz bırakır. Havuz zaten tutmuyor. H2 Belirsiz.

Genel seçimlerin ortalama EMP yolu, ay 0 seçim ayı [HESAP]: 12 ay önce 0,70, 6 ay önce 1,87, 1 ay önce 2,09, seçim ayı 2,94, 1 ay sonra 1,56, 6 ay sonra −0,68, 12 ay sonra −1,35. Sonraki yıl, seçim ayının üstünde bir baskı sırtı değildir.

### Sonrası faiz

Politika faizinin sonrası eksi taban **+0,78** puan/aydır. p 0,016. Holm, EMP ile birlikte iki testte, **0,033**. Fark pozitiftir. Faiz satırının eşiği tutar. Etiket adaydır.

Yedi seçimden yalnız ikisinde sonrası, tabanın üstündedir: 2018 ayda +1,04 puan, 2023 ayda +5,25 puan. 2023’ün altı ayı, yüzde 8,5’ten yüzde 40’a giden artışı taşır. Diğer beş seçimde sonrası faiz tabana yapışıktır ya da inmektedir. Havuz, bu iki artışı ortalar. Her seçimden sonra faiz arttı denmez.

Fonlama faizi 2011’den önce yoktur. Sonrası çubuğu altı seçime yetmez. DOĞRULANMADI.

## H3

2021 Ekim–Aralık, 2023 Mayıs seçiminden 17–19 ay öncedir.

Politika faizi bu üç ayda ayda 1,33 puan inmiştir. Diğer genel seçimlerin seçim öncesi altı ayında ortalama iniş 0,10 puandır. Standart sapma 0,13’tür. 2021 bu dağılımın içine girmez. Aynı uzaklıkta, diğer seçimlerde bu büyüklükte bir iniş yoktur.

EMP bu üç ayda 17,6’dır. Diğer seçimlerin öncesi ortalaması 1,3, standart sapması 2,5’tir. Harcamanın reel artışı yüzde 26’dır. Diğer öncesi ortalama yüzde 8, standart sapma 4’tür. Üçü de “benzer büyüklük” değildir. H3, seçim takvimiyle açıklanamaz. Aday.

## EMP mutabakatı

Aylık birincil EMP, PR #38 formülünün aya uygulanmasıdır. Kur, ayın ortalama satış kurudur. Rezerv, brüt resmi rezervdir. 2002-01’den 2026-09’a 297 ay. Ağırlık 0,798 [HESAP].

Çeyreklik aynı tanım, 2016-Q2–2025-Q4: 2021-Q4 EMP **32,50**, ağırlık 0,787. PR #38 ile fark 0,1 puanın altındadır.

Kutu ağırlığı 0,568 bu e ve r üzerine konunca 2021-Q4 EMP 30,69 olur [VEKİL]. FRED’den ağırlık yeniden hesaplanmadı.

Ay sonu varyantının ağırlığı 0,951’dir. 2005 öncesi günlük kur eski liradır, 1.000.000’a bölündü (SAPMA-ytl).

## Rezerv ve arka kapı

Swap hariç net, tek bir yayımlı satır olarak bulunmadı. Kurulan vekil: analitik bilanço dış varlık eksi toplam döviz yükümlülüğü, dolar, eksi TCMB swap stoku. Swap stoku 2021-01’de başlar. 2021-12: brüt rezerv 111.181 milyon dolar [VERİ], formülün neti −0,9 milyar dolar, swap stoku 49,4 milyar, swap düşülünce −50,2 milyar [HESAP]. Bu, resmi “swap hariç” tablosunun kopyası diye yazılmaz. Seçim çubuğuna girmez. Arka kapı satışı da aynı nedenle DOĞRULANMADI’dır.

## Veri

`EVDS_API_KEY` yoktu. Değeri okunmadı. Şu seriler `evds3.tcmb.gov.tr/igmevdsms-dis` üzerinden alındı: ortalama dolar satışı, brüt rezerv, politika faizi, fonlama maliyeti, TÜFE, faiz hariç gider, personel, cari transfer, kredi hacmi, analitik bilanço, altın ve döviz stoku, swap stoku. Sertifika doğrulaması açıktı.

Günlük ay sonu kur `tcmb.gov.tr/kurlar` XML’idir. 297 ayın hepsi indi.

FRED üç seride zaman aşımına uğradı. Çalışma bakanlığının asgari ücret dosyası 404 verdi. KGF ve EPDK sayfaları açıldı, aylık fiyat veya kefalet serisi çıkarılmadı. Takvim hafızadan yazılmadı.

## Zayıf noktalar

1. H1’in zam, KGF ve enerji kolları boştur. Belirsiz hükmü buradan da gelir.
2. 2015’in iki seçimi beş ay arayladır. Plasebo en az 12 ay bırakır. Plasebo, gerçek takvimden daha seyrektir.
3. Sonrası faiz eşiği, 2023’ün büyük artışı ve 2018 ile tutulur. Beş seçimde bu artış yoktur.
4. Sonrası EMP farkı artı 0,05 puandır. Bu, bir sırt değildir. Kontrolsüzdür.
5. Swap hariç net, 2021’den önce kurulamaz. −50 milyar, formülün kendi sayısıdır.
6. Politika faizi serisi, 2010’dan önce 1 haftalık repo diye aynı araç değildir. Seri, TCMB’nin “politika faizi” satırıdır.
7. Harcama aralıkta şişer. Mevsim ayrımı yapılmadı.
8. Karşı-olgu yoktur.
