# Tekstil ve giyim: üç değişken ölçülebildi mi?

Sektör düzeyinde bir sonuç çıkmaması, "fark yok" bulgusu değildir. Ölçüm kurulamadığında etiket **belirlenemiyor**dur.

İş Yatırım listesi tekstil ile giyimi ayırmaz; üç alt sektörün ikisinde eşleşmiş firma sayısı 8'in altındadır, üçüncüsü iplik ile hazır giyimi aynı kovada tutar, bu yüzden iki sektör arasında marj farkı ölçülmedi. Finansman satırı 2016 ve 2022'de birden kapanan firma 4'tür; açık yararlanmayan firma yoktur; ithalat yoğunluğu, yurt içi üretim tutarı olmadığı için hesaplanmadı. En büyük belirsizlik, sektör sınıfının KAP faaliyet kodu değil İş Yatırım alt sektörü olması ve 2022 ham satışının, aynı yılın orijinal KAP satışından 30 firmanın 28'inde yüzde 1'den fazla sapmasıdır (medyan mutlak fark yüzde 48).

## Kapsam

Dönem 2016-2023. 2023 ham sütunu TMS 29 cari yıl olarak işaretlenir; bu turda her firmanın 2023 KAP yüzü yeniden okunmadı. 2022 ham sütunu, bu evrende orijinal 2022 bildiriminin satışına yakın değildir. Dipnot kırılımı, indirilen 2016 ve 2022 yıllık raporlarının kendi cari sütunundadır.

Sınıf kaynağı: `marj_sirket_liste.csv`, İş Yatırım alt sektörü, liste tarihi 16 Ekim 2026. Ana sektör alanı bu üç alt sektörü "Tekstil ve giyim" diye birleştirir; tablolar birleştirilmez. KAP sektör kodu bu turda alınamadı (denenen şirket kartı uçları 404 döndü). Adında "Holding" geçen üç firma (ARSAN, DERHL, RALYH) satıcı listesinde `grup=faaliyet`tir; holding yasağı nedeniyle çıkarım kümesinden ayrı tutulur, silinmez. BLCYT unvanı "Bilici Yatırım"dır, Holding değildir, çıkarım kümesinde kalır.

Çok sektörlü işaret, iki türlüdür. Ad okuması (ikinci bir sicil değil): AKSA, BAYRK, ISSEN, KOPOL, KORDS, MEGAP, SASA. Dipnotta görülen ikinci faaliyet: SKTAS 2022 notu, süt sığırcılığı kredisi faiz indirimi ve çiğ süt destekleme primini yazar. Bu, firmanın Tekstil Entegre sınıfını değiştirmez.

| Alt sektör | n firma | Dipnotu okunan (en az bir yıl) | İki yıl metin | İki yıl kırılım kapandı | Holding adlı | Ad okumasıyla çok sektörlü |
|---|---:|---:|---:|---:|---:|---:|
| Deri Giyim | 4 | 4 | 2 | 0 | 1 | 0 |
| Endüstriyel Tekstil | 4 | 3 | 3 | 1 | 0 | 4 |
| Tekstil Entegre | 28 | 25 | 15 | 3 | 2 | 3 |
| Toplam | 36 | 32 | 20 | 4 | 3 | 7 |

Okunan, PDF metni 500 baytı aşan 2016 veya 2022 yıllık raporudur. 2017-2021 ve 2023 metinleri indirilmedi; o firma-yıllar bilinmeyendir. SOHOE için pykap anlık görüntüsünde şirket kimliği yoktur. Kısa PDF (metin çıkmadı): ARSAN 2016, DAGI 2022, KOTON 2016, RODRG 2022, SKTAS 2016. Yıllık bildirim, sorgu penceresinde (yıl+1, 1 Ocak-30 Eylül) bulunamayanlar tabloda `yillik_bildirim_yok`dur; bu, firmanın o yıl var olmadığı anlamına gelmez.

## 1. Faaliyet dışı kâr

Etiket: yüz marjı **hesaplandı**. Dipnot kırılımının sektör medyanı **belirlenemiyor**. Dört firmanın kırılımı **doğrudan gözlendi** (not satırları, yüz toplamına yüzde 1 içinde kapandı).

Çekirdek = (brüt kâr + pazarlama + genel yönetim + Ar-Ge) / satış. Pazarlama, genel yönetim ve Ar-Ge ham dosyada negatiftir. Faaliyet kârı, diğer faaliyet gelir ve giderini de içerir. Vergi öncesi, yatırım ve finansman satırlarını da içerir. Ham net finansman = (finansman geliri + finansman gideri) / satış. Değişim, puan cinsinden, aynı firmada sonraki marj eksi önceki marj, sonra bu farkların medyanıdır. Düzey ve değişim aynı firmalardadır. Medyanlar toplanıp vergi öncesi medyanı gibi sunulmaz.

### Yüz, 2016-2023, holding adlılar dışında

2023 sütunu TMS 29 cari yıldır. Bu eşleşme her firma için KAP 2023 yüzüyle kapatılmadı.

Tekstil Entegre, n=18. Bu sınıf tekstil ile giyimi ayırmaz. n≥8 olduğu için dağılım yazılır; giyimle karşılaştırma değildir.

| Kalem | 2016 medyan (p25–p75) | 2023 medyan (p25–p75) | Değişim medyanı, puan (p25–p75) |
|---|---|---|---|
| Çekirdek | 2,32 (−5,64; 9,16) | 9,90 (1,56; 17,12) | +2,21 (−6,43; 12,30) |
| Faaliyet | 5,23 (−4,98; 12,47) | 14,55 (7,23; 22,14) | +9,29 (0,67; 14,71) |
| Vergi öncesi | 0,81 (−12,56; 5,26) | 12,18 (5,46; 34,63) | +14,59 (5,01; 43,66) |
| Ham net finansman | −11,33 (−17,77; −4,19) | −2,16 (−12,49; 8,64) | +13,00 (2,08; 17,81) |

Endüstriyel Tekstil ve Deri Giyim için n<8. Karşılaştırma yok. Eşleşmiş firmaların 2016-2023 ham değişimi, puan:

| Kod | Alt sektör | Not | Çekirdek | Vergi öncesi | Ham net finansman |
|---|---|---|---:|---:|---:|
| DERIM | Deri Giyim | | +3,67 | −0,90 | +2,38 |
| DESA | Deri Giyim | | +28,17 | +34,75 | +5,04 |
| DERHL | Deri Giyim | holding adlı; çift var, çıkarım dışı | +1,24 | +2,84 | +4,14 |
| ENSRI | Deri Giyim | 2016 satışı yok | — | — | — |
| AKSA | Endüstriyel | ad okuması, elyaf | −4,14 | +0,33 | +3,58 |
| KORDS | Endüstriyel | ad okuması, kord bezi | −7,31 | −10,21 | −2,61 |
| SASA | Endüstriyel | ad okuması, polyester | +4,22 | −13,07 | −10,11 |
| KOPOL | Endüstriyel | 2016 ve 2022 yıllık bildirimi yok | — | — | — |

Bu sekiz satır bir sektör medyanı değildir.

2016-2022 ham penceresi ayrıca hesaplandı ve ana tablo yapılmadı. Otuz firmada 2022 ham satışı, orijinal KAP 2022 satışının yüzde 1 komşuluğunda yalnız 2 firmada kalır. Medyan mutlak fark yüzde 48'dir. Önceki turlarda bu sapma, 2023 raporunun TMS 29 karşılaştırmalı sütunuyla ilişkilendirilmişti. Bu turda 2023 PDF'i indirilmediği için o özdeşlik bu 30 firmada yeniden kapanmadı. Dipnot hesabı ham 2022'yi kullanmaz; kendi bildirimlerinin hasılatını kullanır.

### Dipnot kırılımı

Kural: yüzdeki finansman geliri ve gideri, dipnotta "finansman/finansal gelir veya gider" başlığı ile toplam satırı arasında kur, faiz ve diğer diye ayrılır. Toplam, hedefin yüzde 1'inden fazla saparsa firma-yıl medyana girmez. Gider bloğunun toplamı negatifse bloğun işareti çevrilir; net = gelir − gider. İki yılda da iki tarafı kapananlar: BOSSA, HATEK, RALYH, SASA. RALYH holding adlıdır. SASA Endüstriyel Tekstil'dedir. Tekstil Entegre içinde holding olmayan ve iki yılı da kapanan firma BOSSA ve HATEK'tir. n=2. Sektör medyanı yazılmaz.

Dört firmanın orijinal bildirimde net marj değişimi, 2016'dan 2022'ye, puan:

| Kod | Kur | Faiz | Diğer | Üçünün toplamı (bu firmanın net finansmanı) | Vergi öncesi |
|---|---:|---:|---:|---:|---:|
| BOSSA | +4,42 | −5,45 | 0,00 | −1,03 | +31,24 |
| HATEK | +0,78 | −3,87 | −0,43 | −3,53 | +0,70 |
| RALYH | −6,32 | −1,65 | −0,44 | −8,42 | +67,85 |
| SASA | −7,90 | −5,67 | −1,84 | −15,41 | −13,15 |

Dağılım kontrolü, n=4, sektör sonucu değil. Medyan, çift sayıda gözlemde ortadaki iki değerin ortalamasıdır. Kur medyanı −2,77; faiz −4,66; diğer −0,44. Üç medyanın toplamı −7,87. Net finansman değişiminin medyanı −5,97. Vergi öncesi değişimin medyanı +15,97. Üç medyanın toplamı ile vergi öncesi medyanının farkı 23,84 puandır. Bu fark bir kalan kalem değildir; medyanlar toplanmaz. Dört firmanın ortalamaları toplanır: kur, faiz ve diğer ortalamalarının toplamı −7,10, net finansman değişiminin ortalamasına eşittir. Ortalama ile medyan aynı şey değildir. Vergi öncesi medyanını RALYH (+67,85) ve BOSSA (+31,24) yukarı çeker.

Ayrışmayan firma-yıllar ve nedeni aşağıdadır. `başlık yok`, aynı pencerede finansman başlığı bulunamadı demektir; dipnotta kırılım olmadığı anlamına gelmez. `yüz tutarı yok`, XBRL'de finansman geliri boş demektir. `kapanmadı`, satırlar toplandı ama yüze yüzde 1 içinde oturmadı. `toplam satırı yok`, yüz tutarı dipnotta bulunamadı. `pdf kısa`, dosyadan metin çıkmadı.

| Kod | 2016 | 2022 |
|---|---|---|
| AKSA | başlık yok | kapandı |
| ARSAN | pdf kısa | kapandı |
| ARTMS | yıllık bildirim yok | yıllık bildirim yok |
| ATEKS | gider başlık yok | gider başlık yok |
| BAYRK | yıllık bildirim yok | gelir yüz tutarı yok |
| BLCYT | gider kapanmadı | kapandı |
| BOSSA | kapandı | kapandı |
| BRKO | kapandı | gelir başlık yok |
| BRMEN | kapandı | gelir yüz tutarı yok |
| DAGI | gider başlık yok | pdf kısa |
| DERHL | yıllık bildirim yok | kapandı |
| DERIM | gelir yüz tutarı yok | kapandı |
| DESA | gelir yüz tutarı yok; gider kapanmadı | gelir başlık yok |
| DIRIT | kapandı | gelir başlık yok |
| ENSRI | yıllık bildirim yok | gelir yüz tutarı yok |
| HATEK | kapandı | kapandı |
| ISSEN | yıllık bildirim yok | kapandı |
| KOPOL | yıllık bildirim yok | yıllık bildirim yok |
| KORDS | gelir yüz tutarı yok | gider kapanmadı |
| KOTON | pdf kısa | yıllık bildirim yok |
| KRTEK | gelir yüz tutarı yok | gelir yüz tutarı yok; gider kapanmadı |
| LUKSK | toplam satırı yok | gelir kapanmadı |
| MAVI | yıllık bildirim yok | kapandı |
| MEGAP | gelir yüz tutarı yok; gider başlık yok | kapandı |
| MNDRS | toplam satırı yok | gider kapanmadı |
| RALYH | kapandı | kapandı |
| RODRG | toplam satırı yok | pdf kısa |
| RUBNS | yıllık bildirim yok | kapandı |
| SASA | kapandı | kapandı |
| SKTAS | pdf kısa | kapandı |
| SNPAM | gelir yüz tutarı yok; gider kapanmadı | gider kapanmadı |
| SOHOE | kimlik yok | kimlik yok |
| SONME | gelir yüz tutarı yok | kapandı |
| SUNTK | yıllık bildirim yok | kapandı |
| SUWEN | yıllık bildirim yok | kapandı |
| YUNSA | gelir yüz tutarı yok; gider başlık yok | kapandı |

Yöntem notu: başlıktaki dipnot numarası ve "31 Ocak 2023" gibi tarihler tutar sayılmasın diye ayrıştırıcı bu turda daraltıldı. TUPRS 2022 kontrolü duruyor: gelir kur 4.561.528 ve faiz 1.625.365, gider kur 8.486.100, faiz 3.046.458, diğer 750.763, fark 0. MAVI 2022 gelir ve gider notları da fark 0 ile kapandı. Kapanış toleransı hedefin yüzde 1'idir. YUNSA'da dipnot cümlesi bir sonraki tutar satırının etiketine yapışır; tutar, yüz toplamına oturduğu için sınıf kur ve faiz olarak kaldı. Bu, etiket metninin temiz olduğu anlamına gelmez.

## 2. Teşvik mimarisi

Etiket: okunan metinde sınıf **doğrudan gözlendi**. Sektör içi marj farkı **belirlenemiyor**. İlişki kurulmadı; nedensel etki hiç kurulmadı.

Yararlanan: aynı metinde yatırım teşvik belgesi cümlesi (alındı, sahip, sayılı, tarihli ve benzeri) veya tutarlı teşvik/destek geliri satırı. Yararlanmayan: "yatırım teşvik belgesi bulunmamakta" veya "devlet teşvik ve yardımları bulunmamakta", ya da teşvik geliri satırı açık tire. Bilinmeyen: metin yok, politika cümlesi var ama belge veya tutar yok, ya da metin okunamadı. Bilinmeyen, yararlanmayan yapılmadı. Bir yıl yararlanmayan, diğer yıl bilinmeyen ise firma yararlanmayan sayılmadı.

Firma rolü, yalnız 2016 ve 2022 metinlerinden:

| Alt sektör | Yararlanan | Yararlanmayan (iki yıl da açık yok) | Karışık (bir yıl açık yok) | Bilinmeyen |
|---|---:|---:|---:|---:|
| Deri Giyim (n=4, okunan 4) | 1 | 0 | 0 | 3 |
| Endüstriyel Tekstil (n=4, okunan 3) | 2 | 0 | 0 | 2 |
| Tekstil Entegre (n=28, okunan 25) | 12 | 0 | 1 | 15 |

Hiçbir alt sektörde yararlanan ve yararlanmayan sayısı birlikte 8'e ulaşmaz. Karşılaştırma yapılmadı. Tanımlayıcı sayı budur.

Açık yok cümlesi bir firma-yılda bulundu. SNPAM 2016: "Şirket'in dönem sonları itibariyle devlet teşvik ve yardımları bulunmamaktadır." SNPAM 2022 metni politika dilinde, yararlanmayan değil. Firma rolü karışıktır. Bu tek cümle kontrol grubu yapılmadı.

Yararlanan firma-yıllarda, teşvik sözcüğü ile aynı satırda görülen muhasebe bağı. Komşu sütun sayılmadı. Belge cümlesi muhasebe satırı söylemiyorsa "satır belirlenemiyor"dır; bu bir ekonomik kalem değildir.

| Kod | Yıl | Kanıt | Aynı satırda görülen bağ |
|---|---|---|---|
| ATEKS | 2016 | gelir satırı | diğer faaliyet geliri; satırı belirlenemeyen cümle |
| BAYRK | 2022 | gelir satırı | personel (SGK teşvik geliri) |
| BOSSA | 2016 | gelir satırı | diğer faaliyet geliri |
| BOSSA | 2022 | belge | diğer faaliyet geliri; vergi (kurumlar vergisi indirimi cümlesi) |
| BRKO | 2016 | gelir satırı | personel |
| DIRIT | 2016 | gelir satırı | personel; diğer faaliyet geliri |
| ENSRI | 2022 | gelir satırı | diğer faaliyet geliri |
| HATEK | 2022 | gelir satırı | diğer faaliyet geliri |
| KORDS | 2016 ve 2022 | gelir satırı | diğer faaliyet geliri |
| MAVI | 2022 | gelir satırı | diğer faaliyet geliri. Satır "Covid 19 teşvik geliri" ve "kira destek gelirleri"dir; yatırım teşvik belgesi bu metinde belge sınıfına girmedi |
| MNDRS | 2016 ve 2022 | gelir satırı | personel (SGK, 5510) ve diğer faaliyet geliri |
| RUBNS | 2022 | gelir satırı | diğer faaliyet geliri |
| SASA | 2016 | belge | satır belirlenemedi. 2022 metni yararlanan değil |
| SKTAS | 2022 | belge | finansman (süt sığırcılığı kredisi faiz indirimi); diğer faaliyet geliri. Süt primi tekstil teşviki değildir |
| SUNTK | 2022 | belge | personel, vergi, diğer faaliyet geliri |
| YUNSA | 2016 ve 2022 | gelir satırı | diğer faaliyet geliri |

Deri Giyim'de yararlanan tek firma ENSRI'dir. Endüstriyel'de KORDS ve SASA. Bu sayılarla marj farkı yazılmaz.

Yöntem notu: "teşvik geliri" ticari bir indirim de olabilir. MAVI'de kira desteği ile Covid teşvik geliri aynı sınıfa girdi; ikisi de devlet yatırım teşviki diye okunmadı, gelir satırı diye okundu. Kıdem, kiralama ve sendika teşviki elendi. IAS 12'deki "kullanılmayan teşvik tutarları" kalıbı, yararlanan sayılmadı.

## 3. İthalat

Etiket: fasıl ithalatı, ihracatı, ithalat/ihracat ve dönen altılı kodların BEC değer payı **hesaplandı**. İthalat yoğunluğu **belirlenemiyor**. 2022-2023'te 61-62 ithalatının bir parçası dönen altılı kodda yoktur; o parça sınıflanmadı. Firma marjı ile sektör ithalatı arasındaki bağ **belirlenemiyor**.

Firma ithalatı yoktur. Dolaylı ithalat gözlenmiş gibi yazılmadı. Fasıl satırında miktar 0'dır. Altılı satırların 12.552'sinde miktar dolu, 48'inde 0'dır. Birim kodu kayda yazılmadı; miktarlar toplanmadı. Ayrım değerledir. Kaynak: UN Comtrade önizleme uç noktası, raporlayan Türkiye (792), partner dünya, gümrük kodu C00, sınıflama HS, akış ithalat ve ihracat, alan `primaryValue` (ithalatta CIF, ihracatta FOB), ABD doları. Fasıl satırlarının her birinde `isReported=false` ve `isAggregate=true` döndü. Fasıl satırı altılı kodların toplamı olduğu için `isAggregate` beklenen bir işarettir. `isReported` bayrağının bu önizlemede neden hep yanlış olduğu bu turda çözülmedi. TÜİK sorgu ekranı indirilmedi. Seri, TÜİK bülten toplamıyla satır satır eşitlenmedi. Bu, TÜİK sayısının yerine konmuş bir indirme değildir.

Yurt içi üretim tutarı (tekstil ve giyim, TL veya dolar, 2016-2023) bu çalışmada yok. İthalat / (yurt içi üretim + ithalat − ihracat) hesaplanmadı.

Fasıl grupları firma sektörü değildir. 50-60 iplik, elyaf ve mensucat fasıllarıdır; 61-62 giyim eşyasıdır; 63 hazır eşya ve paçavrayı da içerir, iki gruba katılmadı. Değerler milyon ABD doları, bir ondalık.

| Yıl | 50-60 ithalat | 50-60 ihracat | 50-60 ith/ihr | 61-62 ithalat | 61-62 ihracat | 61-62 ith/ihr | 63 ithalat | 63 ihracat | 63 ith/ihr |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2016 | 8.382,2 | 9.546,2 | 0,878 | 2.230,8 | 15.229,4 | 0,146 | 252,2 | 2.250,0 | 0,112 |
| 2017 | 9.661,7 | 10.021,7 | 0,964 | 2.028,6 | 15.349,7 | 0,132 | 261,3 | 2.300,3 | 0,114 |
| 2018 | 8.984,6 | 10.574,2 | 0,850 | 1.876,8 | 15.900,4 | 0,118 | 215,1 | 2.144,5 | 0,100 |
| 2019 | 8.853,2 | 10.395,0 | 0,852 | 1.531,8 | 16.070,9 | 0,095 | 181,6 | 2.113,6 | 0,086 |
| 2020 | 7.551,3 | 9.820,8 | 0,769 | 1.293,0 | 14.988,3 | 0,086 | 220,6 | 2.521,5 | 0,088 |
| 2021 | 9.744,4 | 13.266,5 | 0,735 | 1.500,4 | 18.294,0 | 0,082 | 237,9 | 2.894,7 | 0,082 |
| 2022 | 12.483,4 | 13.026,3 | 0,958 | 2.375,2 | 19.464,3 | 0,122 | 239,0 | 2.765,2 | 0,086 |
| 2023 | 9.015,5 | 12.266,7 | 0,735 | 2.956,7 | 18.314,9 | 0,161 | 258,4 | 2.288,1 | 0,113 |

2016'dan 2023'e ithalat değişimi, iki dolar değerinin oranı, miktar değil: 50-60 yüzde +7,6; 61-62 yüzde +32,5; 63 yüzde +2,4. Yol düz değildir. 50-60 ithalatı 2022'de 12.483 milyon dolara çıkar, 2023'te 9.016'ya iner. 61-62 ithalatı 2020'de 1.293'e iner, sonra yükselir.

### BEC

Altılı kodlar, HS 2017-BEC konkordansındaki 803 koddur. 2016-2023 ve iki akışta 12.600 satır döndü. Ara mal = BEC 21 ve 22. Tüketim = 61, 62 ve 63. Sermaye parçası = 42, ara malın içine katılmadı. 611780 birden fazla BEC koduna düşer; tek sınıfa yazılmadı. Paylar fasıl grubunun dolar toplamına bölünür. "Dönen altılı kodda yok" bir BEC sınıfı değildir; istenen listede olmayıp fasıl toplamında duran tutardır.

İthalat, fasıl grubunun yüzdesi:

| Yıl | 50-60 ara mal | 50-60 tüketim | 50-60 yok | 61-62 tüketim | 61-62 yok | 63 ara mal | 63 tüketim |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2016 | 95,8 | 0,8 | 2,5 | 99,8 | 0,0 | 19,8 | 80,2 |
| 2017 | 98,6 | 0,7 | 0,0 | 99,8 | 0,0 | 25,8 | 74,2 |
| 2018 | 98,4 | 0,8 | 0,0 | 99,8 | 0,0 | 26,7 | 73,3 |
| 2019 | 98,4 | 0,7 | 0,0 | 99,8 | 0,0 | 29,2 | 70,8 |
| 2020 | 98,3 | 0,7 | 0,0 | 99,8 | 0,0 | 21,7 | 78,3 |
| 2021 | 98,4 | 0,7 | 0,0 | 99,8 | 0,0 | 25,2 | 74,8 |
| 2022 | 98,5 | 0,4 | 0,3 | 82,5 | 17,3 | 37,2 | 62,8 |
| 2023 | 97,7 | 0,7 | 0,4 | 83,3 | 16,5 | 29,5 | 70,5 |

50-60 ithalatında sermaye parçası payı yüzde 0,8 ile 1,2 arasındadır; tabloda ayrı sütun açılmadı, ara malın içine de konmadı. 61-62 ithalatında ara mal payı, dönen kodlarda 0'dır. Çoklu kod 611780, 61-62 ithalatının yüzde 0,2'sidir. 2017-2021'de altılı toplam fasıl toplamına oturur. Açık, 2022 ve 2023'te 61-62 ithalatında fasılın yüzde 17,3 ve 16,5'idir. Bu yıllar HS 2022'ye geçişle aynı döneme denk gelir. 2017 konkordansında olmayan kod istenmemiş olabilir. Eksik tutar tüketim malı diye tamamlanmadı. 2022'de 61-62 ithalatının tüketim payı, eksik yok sayılırsa yüzde 99,8'dir; fasıl toplamına bölününce yüzde 82,5'tir. İkisi de yazıldı; ikincisi eksik kodu bir sınıfa koymaz.

İhracatta 2023: 50-60'ın yüzde 71,3'ü ara mal, yüzde 21,7'si tüketim, yüzde 6,6'sı dönen altılı kodda yok. 61-62'nin yüzde 97,9'u tüketim, yüzde 2,1'i yok. 63'ün yüzde 19,2'si ara mal, yüzde 80,8'i tüketim. 2016 ihracatında 50-60'ın yüzde 74,6'sı ara mal, yüzde 22,3'ü tüketim, yüzde 2,8'i yok. 50-60 ihracatı, ithalatı gibi neredeyse tek sınıftan değildir.

Yöntem notu: fasıl toplamı, altılı kod konkordansı olmadan ara mal ve tüketim malı diye bölünemez. 57. fasıl halı ağırlıklıdır ve tek BEC kodu taşımaz; 61 ve 62 içinde hem yarı dayanıklı hem dayanıksız tüketim kodu vardır. Bir faslın tamamına tek BEC etiketi yapıştırmak yanlış olur. Konkordans, HS 2017'den BEC'e, `insongkim/concordance` deposundaki dönüşüm tablosudur. Tekstil fasıllarında görülen kodlar BEC Rev.4 ile örtüşür: 21 ve 22 ara mal, 61-63 tüketim, 42 sermaye malı parçası. Bu tablonun UNCTAD'ın kendi yayımladığı dosyanın birebir kopyası olduğu doğrulanmadı. Birden fazla BEC'e düşen kod, tek sınıfa zorlanmaz.

## 4. Öngörüler

| Öngörü | Sonuç | Olumlu kanıt | Olumsuz kanıt | Belirsizlik |
|---|---|---|---|---|
| H1. Vergi öncesi artış faaliyet dışındansa çekirdek medyanı yatay kalır ve finansman satırı pozitiftir | belirlenemiyor | Sektör kırılımı yok. Tekstil Entegre yüzünde (n=18, karma sınıf, 2023 TMS 29) vergi öncesi değişim medyanı +14,59, ham net finansman +13,00. Bu, finansman satırının pozitif yönde değiştiğini yüz düzeyinde gösterir; kur ve faiz değildir | Aynı 18 firmada çekirdek değişim medyanı +2,21, yatay değil (p25 −6,43, p75 +12,30). İki yılı da kapanan dört firmada net finansman değişimi eksi: −1,03, −3,53, −8,42, −15,41. Bu dört firma H1'in pozitif finansman parçasıyla aynı yönde değil ve sektör değil | Ham finansman, KAP finansman gideriyle özdeş değil. 2023 TMS 29 ile 2016'nın orijinal tablosu aynı ölçekte değil. Dört firmanın vergi öncesi medyanı ile üç kalem medyanının toplamı arasında 23,84 puan vardır; bu kalan kalem yapılmadı |
| H2. Teşvik alan ile almayanın çekirdek marj değişimi farklıysa ve teşvik öncesi fark yoksa ilişki olabilir | belirlenemiyor | Okunan metinde 15 firma en az bir yılda yararlanan diye sınıflandı. Satır bağı, çoğu gelir satırında diğer faaliyet geliri; MNDRS ve BAYRK'te personel; SUNTK ve BOSSA'da vergi cümlesi; SKTAS'ta finansman | Açık yararlanmayan firma yok. SNPAM yalnız 2016'da "yardım yoktur" der, 2022 bilinmeyendir. Teşvik öncesi düzey farkı, kontrol grubu olmadığı için bakılamaz. Seçilim de etki de ayırt edilemedi | Bilinmeyen 20 firma yararlanmayan sayılmadı. 2017-2021 ve 2023 okunmadı. Belge tarihi yok; 2016-2019 teşvik öncesi dönem değildir. Açıklama yapan firma, açıklama yapmayandan farklı olabilir |
| H3. Sektör ithalat artışı ile çekirdek marj arasında sektör içinde tutarlı bir ters ilişki | belirlenemiyor | İki fasıl grubunun ithalat yolu aynı değil: 50-60 sekiz yılda yüzde +7,6 ve 2022'de tepe; 61-62 yüzde +32,5 ve 2020'de dip. Bu, tek bir ithalat şoku olmadığına dair fasıl düzeyinde bir gözlemdir | Firma sektörü tekstil ve giyim diye ayrılmadığı için "sektör içinde tutarlı" diye bakılacak iki marj serisi yok. Korelasyon hesaplanmadı. "Tutarsız" da denmedi; o da bir kıyas olurdu | İki sektör ve sekiz yıl nedensel kanıt olmazdı. Burada iki sektör hiç kurulamadı. Firma ithalatı ve yurt içi üretim yok. Dolar değeri miktar değildir |

## 5. Veri eksikleri

| Eksik | Kapattığı soru |
|---|---|
| Dipnot kırılımı, iki yılda 32 firmada tam değil | Faaliyet dışı kârın kur, faiz ve diğerden geldiği sektör medyanıyla söylenemez. H1 kapanmaz |
| Teşvik belge listesi (bakanlık aylık listesi bu turda indirilmedi) ve açık yararlanmayan firma | Teşvik alan ile almayanın marj farkı kurulamaz. H2 kapanmaz. Bilinmeyeni yararlanmayan saymak bu eksiği kapatmaz |
| KAP sektör kodu ve çok sektörlü firmanın NACE ayrımı | Tekstil ile giyim ayrı raporlanamaz. Ad okuması sınıf yerine geçmez |
| Firma ithalatı ve girdi fiyatı | "İthalat yok" veya "ithal girdi marjı bastı" firma düzeyinde test edilemez |
| Yurt içi üretim tutarı | İthalat yoğunluğu hesaplanamaz |
| TÜİK fasıl tablosunun bu seriye eşitlenmesi | Comtrade önizlemesi TÜİK sayısı diye kullanılamaz |
| 2023 dipnotu ve 2017-2021 dipnotu | Teşvik firma-yıl paneli iki yıldır. 2023 marjı TMS 29 diye işaretlenir, yüzü firma firma kapanmaz |
| Ham 2022'nin TMS 29 karşılaştırmalı sütun olduğunun bu evrende yeniden kapanması | 2016-2022 ham değişimi, orijinal 2016 ile enflasyon sonrası 2022'yi karıştırıyor olabilir. Yüzde 48'lik satış farkı bunu düşündürür, kanıtlamaz |

## 6. Eleştiriler

Firma sayısı küçüktür. Deri Giyim 4, Endüstriyel Tekstil 4, iki yılı kapanan kırılım 4, açık yararlanmayan 0'dır. n=2 için medyan, iki firmanın ortasıdır ve sektör cümlesi kurulmaz. Tekstil Entegre'de yüz değişimi n=18'e çıkar; bu, örneklemin soruyu taşıdığı anlamına gelmez, çünkü kovada iplik, kumaş, hazır giyim ve ad okumasıyla köpük vardır.

Sınıf yanlıdır. Kaynak İş Yatırım alt sektörüdür, KAP faaliyet kodu değildir. ARSAN, DERHL ve RALYH holding adlı olduğu halde faaliyet grubundadır; onları çıkarmak unvan okumasıdır, sicil değildir. SASA, KORDS, MEGAP ve BAYRK için çok sektör işareti de unvan okumasıdır. SKTAS'ta sütçülük dipnotta yazılıdır; firma yine Tekstil Entegre satırında kalır. Hazır giyim adları (MAVI, KOTON, DAGI, SOHOE, SUWEN) ayrı bir giyim sektörü yapılmadı. Yapılsaydı, ikinci kaynak olmadan sınıf uydurulmuş olurdu.

Sektör ithalatını firma marjına taşımak için gerekçe yoktur. Firmanın ithal ettiği mal, fasıl 50-60 toplamı değildir. Giyim firması kumaş ithal edebilir; bu 61-62 ithalatında görünmez. 50-60 ile 61-62'nin dolar yolu farklıdır. Aynı karma firma medyanını iki sepete birden bağlamak, iki sektör varmış gibi bir kıyas üretir. Üretilmedi. Fasıl toplamında miktar 0'dır. Altılı satırda miktar çoğu zaman doludur; birim kaydedilmediği için bu miktarlar toplanmadı. Değer artışı bu yüzden fiyat mı miktar mı diye ayrılmadı. Yoğunluk, üretim paydası olmadığı için hiç yazılmadı.

Ek: ayrıştırıcı, başlık penceresinde kapanmayan notu "kırılım yok" diye okumaz; "bu kuralla kapanmadı" diye okur. Yüzde 1 toleransı küçük bir artık satırı yutar. Teşvik gelir satırı devlet yardımı olmayabilir. İki yıllık metin, çok yıllık teşvik belgesinin süresini göstermez.
