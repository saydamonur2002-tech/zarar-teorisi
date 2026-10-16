# Net dış varlık, altın ve TL–DTH artığı

H1'den H6'ya kadar altı hipotez de belirlenemiyor. Hiçbiri desteklenmedi; hiçbiri çürütülmedi, çünkü çürütme bir katsayı ve bir güven aralığı ister, bu turda katsayı yazılmadı. En zayıf halka, saf zorunlu karşılık stoku ile altın swapının ton cinsinden miktarının EVDS'te ayrı kodla durmamasıdır: para kanalı (H1–H4 ve H6) bu iki eksikte, dolarizasyon payı (H5) ise altın mevduatının gram ve TL kodu olmadığı için kapanır.

Teknik kısaltmalar ilk geçtiklerinde açılır. DTH, döviz tevdiat hesabıdır; bankadaki döviz mevduatını anlatır. NDV, net dış varlıktır; merkez bankasının döviz alacağından döviz borcu düşünce kalan tutardır. Artık, TL mevduat faizi ile DTH faizi arasındaki farktan, piyasanın beklediği kur değişimi çıkınca kalan getiridir. Yerel projeksiyon, her vade için ayrı yazılan denklemdir. Newey–West, hatalar zaman içinde birbirine bağlıyken kullanılan standart hatadır. Granger testi, bir serinin geçmişinin diğerini öngörüp öngörmediğine bakar; nedensellik değildir. VIF, değişkenlerin birbirini ne kadar tekrarladığının ölçüsüdür. Sterilizasyon, döviz alınınca oluşan TL likiditenin repo ya da tahville geri çekilmesidir. KKM, kur korumalı mevduattır.

Çekme: EVDS3, `frequency=5` (aylık), `aggregation=last`, pencere 2003-01 … 2026-09. Kayıt `ndv_dogrulama.json`. Regresyon çalıştırılmadı. Eşik 36'dır ve sonuca göre değiştirilmedi. Brüt döviz rezervi NDV diye kullanılmadı. Kıymetli maden depo hesabı altın mevduatı diye kullanılmadı.

## 1. Veri doğrulama

| Seri | Kod | Başlangıç | Bitiş | n | Durum |
| --- | --- | --- | --- | --- | --- |
| Swap ve zorunlu karşılık düşülmüş net döviz rezervi | kod yok | — | — | — | bulunamadı |
| Brüt döviz rezervi, milyon ABD doları | TP.AB.C2 | 2003-01 | 2026-09 | 285 | doğrulandı; NDV yerine konmadı |
| Brüt altın, milyon ABD doları | TP.AB.C1 | 2003-01 | 2026-09 | 285 | doğrulandı; miktar değil |
| Analitik bilanço dış varlıklar | TP.AB.A02 | 2003-01 | 2026-09 | 285 | doğrulandı; altın dahil |
| Toplam döviz yükümlülükleri | TP.AB.A10 | 2003-01 | 2026-09 | 285 | doğrulandı; ZK ayrılmaz |
| Bankalar döviz mevduatı | TP.AB.A14 | 2003-01 | 2026-09 | 285 | doğrulandı; ZK ile serbest mevduat birlikte |
| Zorunlu karşılıklar bloke hesabı | TP.AB.A19 | 2003-01 | 2026-09 | 285 | doğrulandı; TL bloke, döviz ZK stoku değil |
| Açık piyasa işlemleri | TP.AB.A24 | 2003-01 | 2026-09 | 285 | doğrulandı; NİV'nin tamamı değil |
| Menkul kıymetler | TP.AB.A051 | 2003-01 | 2026-09 | 285 | doğrulandı; NİV'nin tamamı değil |
| Resmi altın, milyon troy ons | TP.REZVARPD.K11 | 2003-01 | 2026-09 | 285 | doğrulandı; brüt miktar, net değil |
| Altın, mevduat ve swap dahil | TP.REZVARPD.K10 | 2003-01 | 2026-09 | 285 | doğrulandı; miktar değil |
| Forward, future ve swap açık pozisyonu | TP.DOVVARNC.K15 | 2003-01 | 2026-09 | 285 | doğrulandı; saf swap stoku değil |
| TCMB swap stoku, alım yönlü | TP.SWAPTEKTAR.TOTALSTOKALIMYONLU | 2021-01 | 2026-09 | 69 | doğrulandı |
| TL karşılığı altın swap stoku, ABD doları | TP.SWAPTEKTAR.SWAPASTOKUSDTUTAR | 2021-01 | 2026-09 | 69 | doğrulandı; ton değil |
| Döviz tevdiat hesapları | TP.KM.F19 | 2003-01 | 2026-08 | 284 | doğrulandı; mevduat bankaları, yerleşik ayrımı yok |
| Kıymetli maden depo hesapları | TP.KM.F22 | 2003-01 | 2026-08 | 284 | doğrulandı; altın kodu değil, vekil yapılmadı |
| Toplam mevduat, mevduat bankaları | TP.KM.F35 | 2003-01 | 2026-08 | 284 | doğrulandı |
| Bankalararası mevduat | TP.KM.F25 | 2003-01 | 2026-08 | 284 | doğrulandı |
| Yurt içi yerleşik TL mevduat | TP.HPBITABLO3.2 | 2024-06 | 2026-09 | 28 | doğrulandı; n<36 |
| Yurt içi yerleşik YP mevduat | TP.HPBITABLO4.2 | 2024-06 | 2026-09 | 28 | doğrulandı; n<36 |
| Gerçek kişi kıymetli maden, ABD doları | TP.HPBITABLO4.7 | 2024-06 | 2026-09 | 28 | doğrulandı; gram değil, n<36 |
| Tüzel kişi kıymetli maden, ABD doları | TP.HPBITABLO4.12 | 2024-06 | 2026-09 | 28 | doğrulandı; gram değil, n<36 |
| TL mevduat faizi, 1 yıla kadar, stok | TP.MT210AGS.TRY.MT04 | 2003-01 | 2026-08 | 284 | doğrulandı |
| ABD doları mevduat faizi, 1 yıla kadar, stok | TP.MT210AGS.USD.MT04 | 2003-01 | 2026-08 | 284 | doğrulandı; DTH sepeti değil |
| PKA 12 ay sonrası dolar kuru, TL | TP.PKAUO.S05.C.U | 2013-01 | 2026-09 | 165 | doğrulandı |
| PKA 24 ay sonrası TÜFE, % | TP.PKAUO.S01.F.U | 2013-01 | 2026-09 | 165 | doğrulandı |
| ABD doları alış | TP.DK.USD.A.YTL | 2003-01 | 2026-09 | 285 | doğrulandı |
| Londra ons altın, ABD doları/ons | TP.MK.LON.YTL | 2003-01 | 2026-05 | 281 | doğrulandı |
| TL KKM stoku, milyar TL | TP.KKM.K4 | 2021-12 | 2026-07 | 56 | doğrulandı; banka stoku, TCMB yükümlülüğü değil |
| Altın mevduatı, gram | kod yok | — | — | — | bulunamadı |
| Altın mevduatı, TL | kod yok | — | — | — | bulunamadı |
| Net altın, ton | kod yok | — | — | — | bulunamadı |
| NİV (repo + tahvil + KKM yükümlülüğü) | kod yok | — | — | — | bulunamadı |

Ortak örneklem kurulamadı. Artığın parçaları içinde en kısa doğrulanan seri PKA'dır: 2013-01 başlangıç, 2026-09 bitiş, n=165, ay atlaması yok. Londra ons 2026-05'te biter. Yurt içi yerleşik mevduat n=28 ile eşiğin altındadır. TCMB'nin kendi swap stok tablosu 2021-01'de başlar, n=69. Bu uzunluklar bir regresyon örneklemi değildir; eksik tanımlar yüzünden denklem kurulmadı.

Swap düzeltmesi kurulmadı. Yayımlanmış ve doğrulanan parçalar şunlardır: brüt döviz `TP.AB.C2`; Uluslararası Rezervler ve Döviz Likiditesi tablosunda forward, future ve para swapının gelecekteki bacağını içeren açık pozisyon `TP.DOVVARNC.K15`; 2021-01'den itibaren TCMB taraflı swap stokları `TP.SWAPTEKTAR`. Saf zorunlu karşılık stoku bu parçaların arasında yoktur. `TP.AB.A19` TL bloke hesaptır. `TP.AB.A14` bankaların TCMB'deki döviz mevduatıdır ve zorunlu karşılık ile serbest mevduatı ayırmaz.

## 2. Ön kayıt

Yöntem, sonuç görülmeden kilitlendi ve çalıştırılmadı. Aylık yerel projeksiyon. Ufuklar 0, 1, 3, 6 ve 12 ay. Karar ufku 3. aydır. Gecikme 3'tür. Newey–West gecikmesi `floor(4*(T/100)^(2/9))` formülüdür, veriye bakılarak seçilmez. Güven aralığı, serbestlik derecesi n−k olan t dağılımının %95 eşiğidir. Gözlem 36'nın altındaysa katsayı yazılmaz. Granger yalnızca yön içindir. Kontrolsüz ve kontrollü yan yana duracaktı; katsayının işareti değişirse başlıkta yazılacaktı. VIF 5'in üstündeyse ortak tahmin belirlenemiyor sayılacak, katsayılar ayrı denklemlerde verilecekti.

Artık, kilitli tanıma göre şöyle kurulacaktı: 1 yıla kadar vadeli TL stok faizi eksi aynı vadeli ABD doları stok faizi eksi PKA 12 ay sonrası dolar düzeyinin spot kura göre yüzde değişimi. Tam 12 aylık mevduat faizi kodu yoktur; kova "1 yıla kadar"dır. Bu tanım da tahmin edilmedi, çünkü H1–H5'in bağımlı ya da bağımsız değişkeni eksik kaldı.

KKM kuklası, ilan tarihine göre değil tebliğ tarihine göre kilitlendi. Başlangıç: 21 Aralık 2021, Resmî Gazete 31696 mükerrer, Tebliğ 2021/14; kukla ayı 2021-12. Yeni açılışın bitişi: 23 Ağustos 2025, Tebliğ 2025/20, Resmî Gazete 32995, "23/8/2025 tarihinden itibaren hesap açılmaz"; kuklanın son açık ayı 2025-07. Tebliğ 2026/1, 24 Ocak 2026'da 2021/14'ü yürürlükten kaldırır. Bu tarih stokun bittiği ay diye kullanılmadı. Kukla regresyona girmedi.

Kırılma kuklaları kilitlendi: 2018'in tüm ayları, 2020'in tüm ayları, 2021-01…2022-12, 2023'ün tüm ayları. Regresyona girmediler.

| Hipotez | Kriter | n | Sonuç | Katsayı | %95 aralık | Olumlu kanıt | Olumsuz kanıt |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1. NDV artınca artık azalır | Katsayı negatif, aralık sıfırı dışlar | regresyon yok | belirlenemiyor | yazılmadı | yazılmadı | `TP.DOVVARNC.K15` 2003-01'den beri var, n=285 | Saf ZK stoku yok. Brüt `TP.AB.C2` NDV yapılmadı |
| H2. Net altın miktarı artınca, fiyat kontrolüyle artık azalır | Aynı | regresyon yok | belirlenemiyor | yazılmadı | yazılmadı | Brüt ons `TP.REZVARPD.K11` n=285 | Altın swapının ton kodu yok. Dolar stoku tona çevrilmedi |
| H3. NİV, H1 ve H2'yi küçültür | NİV katsayısı pozitif ve H1–H2 mutlak değeri küçülür. Küçülmezse sterilizasyon etkisi yoktur | regresyon yok | belirlenemiyor | yazılmadı | yazılmadı | APİ `TP.AB.A24` ve tahvil `TP.AB.A051` ayrı ayrı var | Üç parçalı NİV kodu yok. H1 ve H2 katsayısı olmadığı için küçülme sınanamadı |
| H4. Fiyat etkiler, miktar anlamsızsa kanal kur beklentisidir; o zaman H1 ve H2 çürüdü sayılır | Fiyat katsayısı anlamlı, miktar katsayıları anlamsız | regresyon yok | belirlenemiyor | yazılmadı | yazılmadı | Londra ons `TP.MK.LON.YTL` ve kur `TP.DK.USD.A.YTL` var | Miktar katsayısı yok. H1 ve H2 çürütülmedi |
| H5. Artık artınca altın dahil dolarizasyon payı azalır | Katsayı negatif, aralık sıfırı dışlar | regresyon yok | belirlenemiyor | yazılmadı | yazılmadı | DTH `TP.KM.F19` ve faizler var. PKA n=165 | Altın mevduatının gram ve TL kodu yok. Kıymetli maden vekil yapılmadı. Yurt içi yerleşik tablo n=28 |
| H6. NDV ve net altın artışları ile azalışları ayrı katsayıdır | Katsayılar farklıysa ayrıca yazılır; tek doğrusal katsayı yazılmaz | regresyon yok | belirlenemiyor | yazılmadı | yazılmadı | Swap stok tablosu artış ve azalışı ayırmaya yetecek uzunlukta değildir (n=69) ve zaten net altın değildir | İki miktar serisi kurulamadı |

## 3. Kontrol duyarlılığı

Kontrol listesi kilitliydi: PKA 12 ay dolar beklentisi, 24 ay enflasyon beklentisi, KKM kuklası, 2018 / 2020 / 2021–2022 / 2023 kırılmaları, altın fiyat etkisi (ons fiyatı çarpı kur, miktardan ayrı).

| Denklem | n | Katsayı | Aralık | İşaret kontrolsüzden döndü mü |
| --- | --- | --- | --- | --- |
| H1–H6 kontrolsüz | yazılmadı | yazılmadı | yazılmadı | belirlenemiyor |
| H1–H6 kontrollü | yazılmadı | yazılmadı | yazılmadı | belirlenemiyor |

Kontroller eklendikçe eşiğin altına düşüldüğü için bir katsayı silinmedi. Katsayı, tanım kurulamadığı için hiç yazılmadı. Yurt içi yerleşik mevduatta n=28, eşik 36'nın altındadır; bu seri tek başına da denkleme girmez.

## 4. Eşdoğrusallık

NDV, net altın miktarı ve NİV kurulamadığı için bu üçlünün korelasyon matrisi ve VIF'i yazılmadı. Ortak tahmin de ayrı tahmin de yoktur. VIF eşiği 5, sonuca göre değiştirilmedi.

Doğrulanan parçaların yan yana durması bir regresyon değildir. Brüt döviz, brüt ons ve açık piyasa işlemleri aynı aylarda uzun bir pencere paylaşır (2003-01 … 2026-05 içinde Londra ons da vardır). Bu birlikte hareket, nedensellik diye yazılmadı.

## 5. Asimetri

H6, NDV azalışı ile artışı ve net altın azalışı ile artışı için ayrı katsayı ister. İki seri de yok. Yükseliş ve düşüş katsayısı yazılmadı. Tek doğrusal katsayı da yazılmadı.

## 6. Veri eksikleri

| Eksik | Kapattığı hipotez |
| --- | --- |
| Saf zorunlu karşılık stoku | H1. H1 olmayınca H3'ün "katsayı küçüldü mü" sınaması ve H4'ün miktar bacağı da kapanır. H6'nın NDV bacağı kapanır |
| Altın swapı, ton veya ons | H2. Aynı zincirle H3, H4 ve H6'nın altın bacağı |
| Altın mevduatı gram ve TL | H5. Dolarizasyon payının altın dahil tanımı kurulamaz |
| Yurt içi yerleşik ayrımı, n=28 | H5 için yerleşiklik şartı. Eşik aşılmadığı için bu tablo denkleme konmadı |
| NİV'yi tek kodda toplayan repo + tahvil + KKM yükümlülüğü | H3. `TP.KKM.K4` bankadaki KKM stokudur |
| 2013 öncesi PKA, bu kodda yok | Artık 2013-01'den önce yazılamazdı. Arşiv grubu `bie_urbeka` ayrı frekanstadır ve eklenmedi |

## 7. Monografi paragrafı

Merkez bankasının döviz ve altın alımları, TL mevduatı döviz mevduatından daha cazip hale getiriyor mu, ve bu cazip getiri insanları dövizden TL'ye döndürüyor mu? Bu iki soru bu veriyle cevaplanamadı. Döviz rezervinden swap borcunu ve zorunlu karşılığı düşülmüş net tutarın zorunlu karşılık parçası yayımlanmış bir stok kodu olarak durmuyor. Altının ton cinsinden net stoku da durmuyor: eldeki ons serisi brüt, swapın miktarı ise yok. Bankadaki altın mevduatının gramı ve TL tutarı da ayrı bir kod değil; tabloda kıymetli maden depo hesabı var ve o satır altın diye kullanılmadı. Bu yüzden ne rezervin getiri artığına etkisi ne de artığın dolarizasyon payına etkisi ölçüldü. Sonuç zayıftır: hipotezler çürütülmedi, desteklenmedi, belirlenemiyor olarak kaldı.

## 8. Eleştiri

Altın mevduatı, yurt içindeki bir dönüşümdür. Kişinin kasadaki altını bankaya yatırması, yurt dışından rezerv girişi değildir; bankanın TL cinsinden bir yükümlülüğü ve kıymetli maden varlığı artar. TCMB'nin brüt ons stoku (`TP.REZVARPD.K11`) resmi rezervdir. Bu iki hareket aynı kanala yazılırsa, içerideki portföy kayması dış rezerv artışı gibi okunur. Bu turda ikisi birleştirilmedi. Gram ve TL altın mevduatı olmadığı için iç kanal ayrıca da ölçülemedi. Ölçülememesi, kanalın sıfır olduğu anlamına gelmez.

Swap düzeltmesini yayımlanmış kalemlerle zorlamak yanlı bir NDV üretir. `TP.DOVVARNC.K15` yalnız bankayla yapılan döviz swapı değildir; forward, future ve swapın gelecekteki bacağını aynı açık pozisyonda toplar. `TP.SWAPTEKTAR` stokları 2021-01'de başlar ve ABD doları cinsindendir; altın swapı da dolar stokudur, ton değildir. `TP.AB.A14` zorunlu karşılığı serbest döviz mevduatından ayırmaz. Bu üç kalem brüt dövizden düşülürse çıkan sayı, istenen NDV'ye göre hem fazla hem eksik kalem taşır. Katsayı yazılsaydı bu karışım, rezerv etkisinin büyüklüğünü ve işaretini kaydırabilirdi. Kaydırma yapılmadı; yanlılık, kurulmayan denklemin gerekçesi olarak duruyor.

PKA beklentisi ayın her günü yoktur. `TP.PKAUO.S05.C.U` 2013-01 ile 2026-09 arasında 165 aydır ve bu pencerede ay boşluğu yoktur; her nokta anketin uygun ortalamasıdır, günlerin ortalaması değildir. Mevduat faizi ise ayın stok faizidir. Anket günü ay sonundan uzaksa, beklenen kur değişimi ile faiz aynı anı anlatmaz. Artık bu farkı yutar. 2013 öncesi arşiv 15 günlüktir ve bu koda eklenmedi. Artık tahmin edilseydi, anketin seyrekliği Newey–West standart hatasını da yerel projeksiyon katsayısını da etkilerdi: seyrek anket, artıkta ölçme hatası bırakır, katsayı sıfıra doğru küçülür. Bu turda artık regresyonu yazılmadığı için bu küçülme bir sayı değildir.
