# TMS 29: XI_29 2022 satışı hangi sütun?

Tutarlar TL'dir. `a` İş Yatırım XI_29 kalem 3C, 2022 yıllık satış, `marj_ham.csv` önbelleğidir; çekim saati dosyada yoktur. `b` 2022 yıllık KAP bildiriminin cari hasılatıdır. `c` 2023 yıllık KAP bildiriminin karşılaştırmalı 2022 hasılatıdır; birden fazla yıllık varsa tablodaki `c` ilk bildirimin önceki sütunudur. Eşitlik, TL farkı 1'in altında ya da satışa göre göreli fark 0,001'in altında demektir. Medyan, ortalama değildir. Boş kaynak doldurulmadı.

## 1. Sonuç

H1'in kaynak kısmı destekleniyor: 32 firmanın 32'sinde XI_29 2022 satışı, KAP 2023 ilk bildiriminin karşılaştırmalı 2022 satışına TL bazında eşittir; vergi öncesi kâr da 32 firmada eşittir. `c/b` medyanı 1,9220'dir, 27 firma Aralık 2023 TÜFE / 2022 ortalama TÜFE olan 1,9214'ün yüzde 5 komşuluğundadır; KORDS, BRKO'nun ilk bildirimi, DIRIT, RODRG ve DERHL bu kümenin dışındadır, katsayı tek sayı değildir. Önceki ilk 100 reel satış medyanı yüzde 279,2 ve çekirdek marj medyanı −0,98 puan, bu düzeltilmiş 2022 sütununa dayanır; aynı ilk 100'de 2022 orijinal satışla reel satış medyanı yüzde 138,1 olur, pazarlama satırı okunan 95 firmada çekirdek marj medyanı −1,40 puandan +4,04 puana döner.

## 2. Otuz iki firma

Tablo türü, gelir tablosu gövdesindeki «Finansal Tablo Niteliği» alanıdır. `bin TL` yazan kaynakta XBRL sunum birimi 1.000'dir; tablodaki tutar bu birimle çarpılmıştır.

| Firma | a XI_29 2022 | b KAP 2022 orijinal | c KAP 2023 karşılaştırmalı | b/a | c/a | Tablo türü | Kaynak |
|---|---:|---:|---:|---:|---:|---|---|
| AKSA | 34.464.528.000 | 17.454.244.000 | 34.464.528.000 | 0,5064 | 1,0000 | 2022: Konsolide; 2023: Konsolide Olmayan | a: XI_29 3C, marj_ham.csv. b: KAP 1113628, 15.02.2023, bin TL. c: KAP 1249910, 15.02.2024, bin TL |
| ARSAN | 2.047.115.117 | 1.067.150.964 | 2.047.115.117 | 0,5213 | 1,0000 | Konsolide | a: XI_29 3C, marj_ham.csv. b: KAP 1149914, 10.05.2023, TL. c: KAP 1288503, 20.05.2024, TL; son bildirim 21.05.2024 idx 1289158 c=2.047.115.117 |
| ATEKS | 1.897.909.403 | 993.154.904 | 1.897.909.403 | 0,5233 | 1,0000 | Konsolide | a: XI_29 3C, marj_ham.csv. b: KAP 1119312, 02.03.2023, TL. c: KAP 1277813, 26.04.2024, TL |
| BAYRK | 278.864.440 | 144.077.280 | 278.864.440 | 0,5167 | 1,0000 | Konsolide Olmayan | a: XI_29 3C, marj_ham.csv. b: KAP 1118459, 01.03.2023, TL. c: KAP 1273098, 16.04.2024, TL |
| BLCYT | 1.335.723.425 | 678.666.477 | 1.335.723.425 | 0,5081 | 1,0000 | Konsolide | a: XI_29 3C, marj_ham.csv. b: KAP 1120548, 06.03.2023, TL. c: KAP 1285062, 10.05.2024, TL |
| BOSSA | 5.111.475.711 | 2.614.671.126 | 5.111.475.711 | 0,5115 | 1,0000 | Konsolide Olmayan | a: XI_29 3C, marj_ham.csv. b: KAP 1116505, 23.02.2023, TL. c: KAP 1266818, 04.04.2024, TL |
| BRKO | 66.402.199 | 66.402.199 | 66.402.199 | 1,0000 | 1,0000 | Konsolide | a: XI_29 3C, marj_ham.csv. b: KAP 1132178, 05.04.2023, TL. c: KAP 1296590, 08.06.2024, TL; son bildirim 14.06.2024 idx 1299757 c=102.591.397 |
| BRMEN | 3.591.143 | 1.852.668 | 3.591.143 | 0,5159 | 1,0000 | Konsolide | a: XI_29 3C, marj_ham.csv. b: KAP 1123629, 13.03.2023, TL. c: KAP 1288255, 20.05.2024, TL |
| DAGI | 1.096.673.923 | 585.521.025 | 1.096.673.923 | 0,5339 | 1,0000 | Konsolide | a: XI_29 3C, marj_ham.csv. b: KAP 1122877, 10.03.2023, TL. c: KAP 1278014, 26.04.2024, TL |
| DERHL | 1.689.043.845 | 630.122.991 | 1.689.043.845 | 0,3731 | 1,0000 | Konsolide | a: XI_29 3C, marj_ham.csv. b: KAP 1116454, 23.02.2023, TL. c: KAP 1287122, 16.05.2024, TL |
| DERIM | 1.992.452.896 | 1.074.987.879 | 1.992.452.896 | 0,5395 | 1,0000 | Konsolide Olmayan | a: XI_29 3C, marj_ham.csv. b: KAP 1118719, 01.03.2023, TL. c: KAP 1284364, 09.05.2024, TL |
| DESA | 2.545.112.548 | 1.358.955.850 | 2.545.112.548 | 0,5339 | 1,0000 | Konsolide Olmayan | a: XI_29 3C, marj_ham.csv. b: KAP 1114575, 16.02.2023, TL. c: KAP 1262951, 27.03.2024, TL |
| DIRIT | 199.077.938 | 120.819.514 | 199.077.938 | 0,6069 | 1,0000 | Konsolide | a: XI_29 3C, marj_ham.csv. b: KAP 1164769, 03.07.2023, TL. c: KAP 1297519, 11.06.2024, TL |
| ENSRI | 363.593.388 | 189.386.442 | 363.593.388 | 0,5209 | 1,0000 | 2022: Konsolide Olmayan; 2023: Konsolide | a: XI_29 3C, marj_ham.csv. b: KAP 1116833, 24.02.2023, TL. c: KAP 1247808, 07.02.2024, TL |
| HATEK | 1.155.606.051 | 591.114.934 | 1.155.606.051 | 0,5115 | 1,0000 | Konsolide | a: XI_29 3C, marj_ham.csv. b: KAP 1124561, 14.03.2023, TL. c: KAP 1281401, 04.05.2024, TL; son bildirim 10.05.2024 idx 1285122 c=1.155.606.051 |
| ISSEN | 3.813.646.327 | 1.983.560.711 | 3.813.646.327 | 0,5201 | 1,0000 | Konsolide | a: XI_29 3C, marj_ham.csv. b: KAP 1120555, 06.03.2023, TL. c: KAP 1264001, 28.03.2024, TL |
| KORDS | 18.439.743.907 | 18.439.743.907 | 18.439.743.907 | 1,0000 | 1,0000 | Konsolide | a: XI_29 3C, marj_ham.csv. b: KAP 1116583, 24.02.2023, TL. c: KAP 1260844, 21.03.2024, TL |
| KRTEK | 2.045.035.220 | 1.049.227.801 | 2.045.035.220 | 0,5131 | 1,0000 | Konsolide Olmayan | a: XI_29 3C, marj_ham.csv. b: KAP 1117685, 28.02.2023, TL. c: KAP 1265975, 02.04.2024, TL |
| LUKSK | 455.654.261 | 235.743.341 | 455.654.261 | 0,5174 | 1,0000 | 2022 ve 25.04.2024: Konsolide; 26.04.2024: Konsolide Olmayan (hasılat aynı) | a: XI_29 3C, marj_ham.csv. b: KAP 1123582, 13.03.2023, TL. c: KAP 1277241, 25.04.2024, TL; son bildirim 26.04.2024 idx 1277859 c=455.654.261 |
| MAVI | 21.037.941.000 | 10.591.901.000 | 21.037.941.000 | 0,5035 | 1,0000 | Konsolide | a: XI_29 3C, marj_ham.csv. b: KAP 1124758, 14.03.2023, bin TL. c: KAP 1258959, 15.03.2024, bin TL |
| MEGAP | 2.950.343.226 | 1.536.660.101 | 2.950.343.226 | 0,5208 | 1,0000 | Konsolide | a: XI_29 3C, marj_ham.csv. b: KAP 1123186, 11.03.2023, TL. c: KAP 1277266, 25.04.2024, TL |
| MNDRS | 7.994.262.391 | 4.118.740.095 | 7.994.262.391 | 0,5152 | 1,0000 | Konsolide | a: XI_29 3C, marj_ham.csv. b: KAP 1120671, 06.03.2023, TL. c: KAP 1288491, 20.05.2024, TL |
| RALYH | 695.941.623 | 359.481.627 | 695.941.623 | 0,5165 | 1,0000 | Konsolide | a: XI_29 3C, marj_ham.csv. b: KAP 1121952, 08.03.2023, TL. c: KAP 1288737, 21.05.2024, TL |
| RODRG | 49.792.266 | 42.019.419 | 49.792.266 | 0,8439 | 1,0000 | Konsolide | a: XI_29 3C, marj_ham.csv. b: KAP 1131713, 04.04.2023, TL. c: KAP 1247287, 06.02.2024, TL; son bildirim 11.03.2024 idx 1257719 c=49.792.266 |
| RUBNS | 1.430.000.183 | 742.489.969 | 1.430.000.183 | 0,5192 | 1,0000 | Konsolide Olmayan | a: XI_29 3C, marj_ham.csv. b: KAP 1116416, 23.02.2023, TL. c: KAP 1274788, 18.04.2024, TL |
| SASA | 61.835.185.000 | 31.060.178.000 | 61.835.185.000 | 0,5023 | 1,0000 | Konsolide | a: XI_29 3C, marj_ham.csv. b: KAP 1125376, 16.03.2023, bin TL. c: KAP 1255158, 06.03.2024, bin TL |
| SKTAS | 1.567.355.052 | 803.660.363 | 1.567.355.052 | 0,5127 | 1,0000 | Konsolide | a: XI_29 3C, marj_ham.csv. b: KAP 1124165, 13.03.2023, TL. c: KAP 1281410, 04.05.2024, TL |
| SNPAM | 653.341.072 | 341.584.562 | 653.341.072 | 0,5228 | 1,0000 | Konsolide Olmayan | a: XI_29 3C, marj_ham.csv. b: KAP 1116763, 24.02.2023, TL. c: KAP 1284667, 10.05.2024, TL |
| SONME | 29.328.393 | 15.263.894 | 29.328.393 | 0,5204 | 1,0000 | Konsolide Olmayan | a: XI_29 3C, marj_ham.csv. b: KAP 1116776, 24.02.2023, TL. c: KAP 1284216, 09.05.2024, TL |
| SUNTK | 7.574.904.395 | 3.974.507.185 | 7.574.904.395 | 0,5247 | 1,0000 | Konsolide | a: XI_29 3C, marj_ham.csv. b: KAP 1123227, 12.03.2023, TL. c: KAP 1281321, 03.05.2024, TL |
| SUWEN | 1.757.058.244 | 940.027.301 | 1.757.058.244 | 0,5350 | 1,0000 | Konsolide | a: XI_29 3C, marj_ham.csv. b: KAP 1117969, 28.02.2023, TL. c: KAP 1276646, 24.04.2024, TL |
| YUNSA | 2.405.442.036 | 1.279.958.274 | 2.405.442.036 | 0,5321 | 1,0000 | Konsolide | a: XI_29 3C, marj_ham.csv. b: KAP 1116207, 23.02.2023, TL. c: KAP 1274798, 18.04.2024, TL |

## 3. Katsayı dağılımı

`c/b`, ilk 2023 bildirimine göredir. n=32.

| Ölçü | c/b |
|---|---:|
| Medyan | 1,9220 |
| p25 | 1,8777 |
| p75 | 1,9494 |
| En düşük | 1,0000 (BRKO ilk bildirim ve KORDS) |
| En yüksek | 2,6805 (DERHL) |
| Ortalama | 1,8604 |

Ortalama, iki adet 1,00 ve RODRG yüzünden medyanın altındadır; sonuç ölçüsü medyandır. Yüzde 5 bandının dışında beş firma vardır. Mutlak `b/a − 1` medyanı 0,4797'dir (yüzde 47,97). `b/a − 1` değeri −%50 ile −%46 arasında olan firma sayısı 27'dir; sınıra en yakın DERIM −%46,05'tir. Bandın dışı: DERHL −%62,69, DIRIT −%39,31, RODRG −%15,61, BRKO %0, KORDS %0.

Katsayı firmadan bağımsız bir sabit değildir. Kümenin içi Aralık 2023 / 2022 ortalamasına yapışıktır. Dışarıdakilerin okunan nedenleri bölüm 4 ve 5'tedir.

## 4. Hipotezler

| Hipotez | Sonuç | Olumlu kanıt | Olumsuz kanıt |
|---|---|---|---|
| H1. XI_29, 2023 karşılaştırmalı sütundur; katsayı büyük ölçüde sabittir | Desteklendi | Satışta 32/32, vergi öncesinde 32/32 TL eşitliği. Çekirdek kalem (brüt, pazarlama, genel yönetim, Ar-Ge) 29 firmada eşit. Medyan `c/b` 1,9220; 27/32, 1,9214'ün yüzde 5 içinde | Beş firmanın katsayısı bu bandın dışında. Katsayı tek sabit değil. DIRIT, RALYH ve SONME'de pazarlama satırı XBRL'de boş; çekirdek eşitliği bu üçünde belirlenemiyor |
| H2. Fark firmaya özgü yeniden düzenlemedir; bazılarında düzeltme yoktur | Zayıfladı | KORDS'ta düzeltme yok (katsayı 1). DIRIT yıl sonu katsayısını, DERHL karma bir köprüyü, BRKO ikinci bildirimi başka bir katsayıyı kullanıyor | XI_29'un kaynağı 32 firmada da ilk karşılaştırmalı sütun. Düzeltmesiz iki firma da bu sütuna eşit. Yirmi yedilik küme firmaya özgü dağınık bir yeniden düzenleme değil |
| H3. Tek sistematik ölçek yok; çekim veya birim hatası | Zayıfladı | RODRG dipnotu bir cümlede sunum birimini bin TL, bir cümlede TL yazar. Bu çelişki tek başına birim ihtimalini açık bırakır | 32/32 eşitlik bin TL kaymasıyla (1.000 kat) uyuşmaz. 27 firma aynı orana toplanır. RODRG'da XI_29, XBRL birimi 1 TL olan 49.792.266'ya eşittir; bin TL okuması bu eşitliği bozar |
| H4. Fark, konsolide ile bireysel tablonun karışmasıdır | Zayıfladı | AKSA'da 2022 başlığı Konsolide, 2023 başlığı ve PDF kapağı Konsolide Olmayan. ENSRI'de başlık Konsolide Olmayan'dan Konsolide'ye döner. LUKSK'nin 26.04.2024 bildirimi Konsolide Olmayan başlık taşır | Aynı çiftin iki tarafı da Konsolide Olmayan olan sekiz firmada (BAYRK, BOSSA, DERIM, DESA, KRTEK, RUBNS, SNPAM, SONME) oran yine 1,87–1,94 aralığındadır. AKSA ve ENSRI oranları yüzde 5 bandındadır. LUKSK'nin iki 2023 bildiriminde hasılat aynıdır. Başlık farkı, yüzde 48'lik kümeyi açıklamaz |

İlk 100'ün ayrı kontrolü, kaynak eşitliğini 32 ile sınırlamaz. `kap_tur3` önbelleğindeki 2023 önceki sütun, 99 firmanın 96'sında XI_29 2022 satışına eşittir. GSRAY'ın bu pencerede 2023 yıllığı yoktur. KRDMA, KRDMB ve KRDMD tek konsolide karşılaştırmalı tutara (54.168.492.046 TL, bildirim 1280030, 30.04.2024) bölünmüş pay sınıflarıdır; oran farkı TMS 29 katsayısı değildir. Bu önbellek 2024'ün ilk dokuz ayındaki son yıllığı alır; Ekim 2024 sonrası düzeltme bildirimi ilk 100'de ayrıca taranmadı.

## 5. TMS 29 katsayı kontrolü

EVDS `TP.GENENDEKS.T1`, 2022 ve 2023'ün on iki ayı. 2022 ortalaması 967,71; 2022 Aralık 1.128,45; 2023 ortalaması 1.488,91; 2023 Aralık 1.859,38.

| Oran | Değer | `c/b` medyanı 1,9220 ile |
|---|---:|---|
| 2022 ortalama / 2023 ortalama | 0,6499 | Uyuşmaz. Bu, düzeltme çarpanının ters yönüdür |
| 2023 ortalama / 2022 ortalama | 1,5386 | Uyuşmaz. Medyandan 0,383 düşüktür |
| 2023 Aralık / 2022 Aralık | 1,64773 | Medyandan 0,274 düşüktür. DIRIT'in `c/b` değeri ve dipnotundaki 31 Aralık 2022 katsayısı ile TL'ye kadar örtüşür: 120.819.514 × 1,64773 = 199.077.938 |
| 2023 Aralık / 2022 ortalama | 1,92142 | Medyandan 0,0006 yüksektir (medyanın yüzde 0,03'ü) |

Gelir tablosu TMS 29'da işlem tarihinden endekslenir. Tek bir Aralık/Aralık katsayısı bu yüzden teorik gelir katsayısı değildir. Medyanın 1,9214'e yakınlığı, yıl içine yayılmış satış için yaklaşık bir gözlemdir; her firmanın bu oranı kullandığı dipnotta yazılmaz.

Okunan dipnotlar:

- KORDS, 2023 bildirimi 1260844: «Şirket'in fonksiyonel para biriminin ABD Doları olması sebebiyle … TMS 29 kapsamında herhangi bir düzeltme yapmasına gerek bulunmamaktadır.» `c/b` = 1. 2022 bildirimi 1116583 aynı USD gerekçesini yazar.
- DIRIT, 1297519: dipnot 31 Aralık 2022 katsayısını 1,64773 basar ve «önemli bir sınıflama bulunmamaktadır» der. Yüzdeki satış oranı bu yıl sonu katsayısına eşittir. Aynı dipnot, gelir kalemlerinin yansıtıldıkları dönemlerin katsayısıyla endekslendiğini de söyler. Yüz ile bu cümle aynı uygulamayı tarif etmiyor; yüzdeki sayı yıl sonu katsayısıdır.
- BRKO ilk bildirim 1296590 (08.06.2024): dipnot aynı 1,64773 katsayısını ve satın alma gücü cümlesini taşır, «önemli bir sınıflama bulunmamaktadır» der. Yüzdeki karşılaştırmalı hasılat 66.402.199, yani 2022 orijinalidir. Dipnot ile yüz çelişir. XI_29 yüzü alır. İkinci bildirim 1299757 (14.06.2024): cari hasılat 45.105.636 durur, karşılaştırmalı hasılat 102.591.397 olur. 66.402.199 × 1,545 = 102.591.397. Bu, dipnotta basılan 1,64773 değildir. 1,545, 2023 Aralık / 2023 Ocak TÜFE'nin üç haneye yuvarlanmış haline eşittir; dipnot bu oranı seçtiğini yazmaz. Katsayının nedeni belirlenemiyor.
- DERHL, 1287122: 26.12.2023 ortak kontrole tabi birleşme (Soho Giyim ile Toprak Yenilenebilir Enerji) karşılaştırmalı dönemleri yeniden düzenlemiş. Dipnot 2.7, 2022 satışını tek sütunda 630.122.991'den 1.689.043.845'e taşır; sütun «düzeltmeler/sınıflamalar»dır, enflasyon ile birleşmeyi ayırmaz. Bölüm notunda yeniden düzenlenmiş 2022 Enerji satışı 526.742.286'dır. Bu satır düşülünce kalan oran 1,8446'dır; ne 1,64773 ne 1,92142. Hasılatın ne kadarının enflasyon olduğu belirlenemiyor.
- RODRG, 1247287: TMS 29 uygulanmış, basılan 2022 yıl sonu katsayısı 1,64. Gözlenen `c/b` 1,1850 bu katsayı değildir. Dipnot sunum birimini bir yerde bin TL, bir yerde TL yazar. 11.03.2024 bildirim 1257719'un PDF metni okunamadı; XBRL karşılaştırmalı hasılatı ilk bildirimle aynıdır. 1,185'in nedeni belirlenemiyor.

### Yeniden düzenleme taraması

2023 yıllık PDF'leri 37 bildirimin 36'sında metne çevrildi. «Yeniden sınıflandırılacak / sınıflandırılmayacak» diğer kapsamlı gelir satırları satış düzeltmesi sayılmadı. «Gerekli görüldüğünde yeniden sınıflandırılır» politika cümlesi, tutar vermediği için satış köprüsü sayılmadı. «TMS 29 uyarınca yeniden düzenlenmiştir» ibaresi enflasyon düzeltmesinin kendi cümlesidir.

Enflasyon dışı (ya da enflasyonla aynı sütunda karışmış) satış düzenlemesi tutarıyla okunan firma DERHL'dir. BRKO ve DIRIT, önemli bir sınıflama olmadığını yazar. KORDS, TMS 29 uygulamadığını yazar. Diğer firmalarda enflasyon dışı bir hasılat köprüsü bu taramada ayrılmadı; olmaması kanıtlanmış değildir.

2022 PDF metni kısa olduğu için o yılın dipnotu okunamayanlar: DAGI ve RODRG. Bu iki firmanın 2023 metni okundu (RODRG'nin ikinci bildirimi hariç).

## 6. Önceki sonuçlara etki

Önceki reel satış, her firmanın satışının yılın ortalama TÜFE'sine bölünmesi ve 2016–2022 büyüme oranlarının medyanıdır. TÜFE ortalamaları: 2016 = 280,85, 2022 = 967,71, oran 3,4457. Bu deflatör, 2022 nominal satışı için kuruludur. 2023 karşılaştırmalı satışı 31 Aralık 2023 satın alma gücündedir; onu 2022 ortalamasına bölmek fiyat düzeyini karıştırır ve reel büyümeyi şişirir.

| Hesap | Eski (XI_29 / düzeltilmiş 2022) | Yeni (KAP 2022 orijinal) |
|---|---|---|
| İlk 100 reel satış medyanı, 2016–2022 | %279,2 (oran 2,7918; n=100) | %138,1 (oran 1,3809; n=100) |
| Aynı hesap, Kardemir üç pay sınıfı hariç | Bu satır eski raporda ayrı yoktur | %135,0 (n=97) |
| İlk 100 çekirdek marj değişimi medyanı | −0,98 puan (n=100) | Pazarlama satırı boş: ENJSA, AKENR, MPARK, CLEBI, AYEN. Kalan 95'te düzeltilmiş sütun −1,40 puan, orijinal sütun +4,04 puan |
| 32'lik kümede 2016 satışı olanlar, reel satış medyanı | %318,9 (n=26) | %127,7 (n=26) |
| Bu 26'nın çekirdeği okunan 23'ü, çekirdek değişim medyanı | +6,52 puan | +7,65 puan |

Çekirdek, (brüt kâr + pazarlama + genel yönetim + Ar-Ge) / satıştır. Değişim, 2022 marjı eksi 2016 marjıdır; 2016 XI_29 sütunu nominaldir. İlk 100'ün −0,98 puanı, düzeltilmiş 2022 marjı ile nominal 2016 marjının farkıdır. Orijinal 2022 ile aynı 95 firmada medyanın işareti değişir: 95 firmanın 72'sinde iki sürümün farkı 1 puandan büyüktür. Tekstil 23'ünde medyan her iki sütunda da artıdır; kayma yaklaşık 1,1 puandır. İlk 100'ün işareti ile bu 23'ün işareti aynı örneklem değildir.

2022 düzeyinde, düzeltilmiş vergi öncesi marj eksi orijinal vergi öncesi marjın medyanı −7,17 puandır (n=32). 30 firmada mutlak fark 1 puandan büyüktür. Uçlar BRMEN +298,2, SONME −138,7 ve RODRG −84,8 puandır; küçük satışta oran şişer. Satış ve vergi öncesi aynı katsayıyla ölçeklenseydi marj değişmezdi. Değişmesi, düzeltmenin her satıra tek çarpan olmadığını gösterir. Bu, 2016–2022 değişim medyanı değildir.

İlk 100'ün içinde bu 32'den beş firma vardır: AKSA, KORDS, MAVI, MNDRS, SASA. Yüzde 279'un yerini 32'lik kümenin yüzde 128'i almaz.

## 7. Veri eksikleri

- 32 firmanın üç satış sütunu da okundu. Satış için «veri yok» satırı yoktur.
- Çekirdek satırı boş (pazarlama hücresinde tutar yok): DIRIT, RALYH, SONME. İlk 100'de ENJSA, AKENR, MPARK, CLEBI, AYEN. Bu sekizde çekirdek karşılaştırması yapılmadı. Ar-Ge satırı boş olup XI_29 Ar-Ge'si 0 olan 15 firmada çekirdek, Ar-Ge sıfır alınarak kuruldu; bu bir kabuldür.
- 2016 satışı olmadığı için 2016–2022 büyümesine girmeyenler: BAYRK, ENSRI, ISSEN, RUBNS, SUNTK, SUWEN.
- GSRAY, ilk 100 eşleşmesinde 2023 yıllığı yok.
- RODRG 11.03.2024 PDF metni okunamadı. DAGI ve RODRG 2022 PDF metni 500 bayttan kısadır.
- ARTMS, KOPOL ve KOTON'un sorgu penceresinde 2022 yıllığı, SOHOE'nin kayıt kimliği yoktur. Bu turun 32'sine alınmadılar; tahmin edilmediler.
- BRKO'da 1,545'in ve RODRG'da 1,185'in dipnot gerekçesi bulunamadı. DERHL'de enflasyon ile birleşmenin hasılat payı ayrılmadı.

## 8. Eleştiri

Karşılaştırmalı 2022 sütununun ayrıca yeniden düzenlenip düzenlenmediği, ancak firma bir köprü bastıysa bilinir. Yirmi yedi firmada böyle bir köprü okunmadı. Oranın 1,92'ye yakın olması, küçük bir sınıflama farkının katsayının içinde durmadığını göstermez. DERHL köprüsü enflasyonu ve ortak kontrol birleşmesini tek sütuna koyar. BRKO'nun ilk dipnotu düzeltme yaptığını söyler, yüz düzeltmemiş bir 2022 satışı gösterir. Dipnot cümlesi yüzün yerine konamaz.

32 firma, XI_29 2022 satışı ile penceredeki 2022 KAP yıllığı bulunan tekstil ve giyim adlarıdır. İlk 100'ün seçimi bu listenin içinden yapılmamıştır. Kaynak eşitliği ilk 100'ün 96'sında da görüldü; bu, 32'nin kendi kendine seçilmiş bir ölçek hatası olmadığını gösterir. Yine de 32'nin katsayı dağılımı, borsanın tamamının katsayı dağılımı diye okunamaz. İlk 100'de de `a/b` medyanı 1,895'tir (Kardemir üç sınıf hariç, n=97); CIMSA 2,43 ve ARENA dahil altı firma 1,00 uçtadır. Bu uçların dipnotu bu turda açılmadı.

Tek bir enflasyon oranı katsayıyı taşımaz. Medyan, 2023 Aralık / 2022 ortalamasına yakındır ve 2022 ortalama / 2023 ortalamasına, 2023 ortalaması / 2022 ortalamasına ve Aralık/Aralık oranına uzakdır. Aralık/Aralık yalnız DIRIT'te, dipnotun bastığı katsayıyla, TL'ye kadar tutar. KORDS bilinçli olarak 1'dir. BRKO'nun ikinci yüzü 1,545'tir. RODRG 1,185 ve DERHL 2,6805 iki resmi oranın da dışındadır. Gelir kaleminin teorik katsayısı firmanın aylık satış takvimine bağlıdır; o takvim okunmadı.

XI_29 2022 sütunu, bu 32'de ve ilk 100'ün okunan 96'sında 2023 karşılaştırmalı sütundur. Önceki marj ve reel büyüme hesapları bu sütunu 2022'nin nominal hali gibi kullanmıştır. Yüzde 279 ve −1,0 puan bu ölçümle yeniden kurulmalıdır. Orijinal 2022 ile hesaplanan yüzde 138,1 ve +4,04 puan da, 2016'nın sonraki tablolarda yeniden düzenlenip düzenlenmediği okunmadığı için kapanmış bir sonuç değildir.
