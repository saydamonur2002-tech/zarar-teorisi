# Net dış varlık, net altın ve TL–DTH artığı

Çekilme: 2026-10-16. Kurallar: `NDV_ALTIN_ONKAYIT.md`. Betik: `ndv_altin.py`. Kayıt: `ndv_altin_sonuc.json`.

Katsayı yazılmadı. Ortak örnek kurulmadı. En kısa belirleyici, hiç çekilemeyen seridir.

## 1. Üç cümle

H1’den H6’ya kadar her hipotez belirlenemiyor. Hiçbiri desteklenmedi ve hiçbiri çürüdü diye işaretlenmedi. En zayıf halka TL–DTH artığıdır: döviz tevdiat faizinin tek serisi yok, swap düzeltmeli net dış varlık da yok, bu yüzden kanalın ilk gözlemi oluşmadı.

Artık, aynı vadeli TL mevduat faizinden döviz tevdiat faizini ve beklenen kur değişimini düşünce kalan farktır. Beklenen kur değişimi, anketin 12 ay sonraki dolar kurunun bugünkü kura göre farkıdır.

## 2. Veri doğrulama

| Nesne | Kod | Başlangıç | n | Durum |
| --- | --- | --- | --- | --- |
| Brüt rezerv, milyon ABD doları | `TP.AB.TOPLAM` | 2002-01 | 298 | doğrulandı. Net dış varlık değildir |
| Altın, milyon ABD doları | `TP.AB.C1` | 2002-01 | 298 | doğrulandı. Ton miktarı değildir |
| Döviz rezervi, milyon ABD doları | `TP.AB.C2` | 2002-01 | 298 | doğrulandı. Net değildir |
| Yabancı aktif | `TP.AB.A02` | 2002-01 | 298 | doğrulandı. Swap düzeltmeli NDV değildir |
| Yabancı pasif toplamı | `TP.AB.A10` | 2002-01 | 298 | doğrulandı |
| Zorunlu karşılık, bloke | `TP.AB.A19` | 2002-01 | 298 | doğrulandı. NDV formülüne sokulmadı |
| Açık piyasa işlemi | `TP.AB.A24` | 2002-01 | 298 | doğrulandı. Net iç varlık değildir |
| TL mevduat faizi, 3 aya kadar, akım | `TP.TRY.MT02` | 2002-01 | 298 | doğrulandı |
| ABD doları mevduat faizi, 3 aya kadar, akım | `TP.USD.MT02` | 2002-01 | 298 | doğrulandı. DTH sepeti değildir |
| PKA 12 ay dolar kuru | `TP.PKAUO.S05.C.U` | 2013-01 | 166 | doğrulandı. Takvimle aynı sayıda ay |
| PKA 24 ay enflasyon | `TP.PKAUO.S01.F.U` | 2013-01 | 166 | doğrulandı |
| USD/TRY alış | `TP.DK.USD.A.YTL` | 2002-01 | 298 | doğrulandı |
| Toplam mevduat, yeni tablo | `TP.HPBITABLO2.1` | 2024-06 | 29 | doğrulandı. Eşik altı |
| TL mevduat, yeni tablo | `TP.HPBITABLO2.3` | 2024-06 | 29 | doğrulandı. Eşik altı |
| YP mevduat, yeni tablo | `TP.HPBITABLO2.6` | 2024-06 | 29 | doğrulandı. Eşik altı |
| Kıymetli maden, dolar karşılığı, yeni tablo | `TP.HPBITABLO4.7` | 2024-06 | 29 | doğrulandı. Gram değildir. Eşik altı |
| TL mevduat, arşiv | `TP.MEVDUAT.I001` | 2012-12 | 146 | doğrulandı. Yeni tabloyla eklenmedi |
| YP mevduat, arşiv | `TP.MEVDUAT.I067` | 2012-12 | 146 | doğrulandı. Yeni tabloyla eklenmedi |
| Kıymetli maden, arşiv | `TP.MEVDUAT.I0981` | 2012-12 | 146 | doğrulandı. Gram değildir |
| Toplam mevduat, arşiv | `TP.MEVDUAT.I114` | 2012-12 | 146 | doğrulandı |
| TL KKM stoku | `TP.KKM.K4` | 2021-12 | 56 | doğrulandı. Tek başına net iç varlık değildir |
| Swap yükümlülüğü | yok | — | 0 | bulunamadı |
| Altın swapı, ton | yok | — | 0 | bulunamadı |
| Ons altın fiyatı | yok | — | 0 | bulunamadı |
| Altın mevduatı, gram | yok | — | 0 | bulunamadı |
| DTH faizi, tek sepet | yok | — | 0 | bulunamadı |
| Swap düzeltmeli net dış varlık | yok | — | 0 | bulunamadı |
| Net iç varlık, repo + tahvil + KKM | yok | — | 0 | bulunamadı |

Swap düzeltmesi yapılmadı. Yabancı aktif ve yabancı pasif yayımlandı. Ayrı bir swap stoku yok. Brüt rezerv net dış varlığın yerine konmadı. Zorunlu karşılık blokesi ayrı duruyor ve bir formüle girmedi. Altın miktarı ile fiyatı ayrılmadı, çünkü ton ve ons serisi yok. Milyon dolar altın stoku ikisinin karışımıdır ve kullanılmadı.

KKM tebliği bu turda inmedi. 21 Aralık 2021 sayısında açılan madde özel tüketim vergisi tebliğidir. Başlangıç ve bitiş ayı oradan yazılmadı.

## 3. Ön kayıt tablosu

| Hipotez | Kriter | n | Sonuç | Katsayı | %95 aralık | Olumlu kanıt | Olumsuz kanıt |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | NDV değişimi artığı azaltır, bant sıfırın altında | kurulmadı | belirlenemiyor | yazılmadı | yazılmadı | Yabancı aktif ve pasif ayrı duruyor | Swap stoku yok. Artık yok |
| H2 | Net altın miktarı, fiyat dururken artığı azaltır | kurulmadı | belirlenemiyor | yazılmadı | yazılmadı | Altının dolar değeri 298 ay duruyor | Ton ve ons yok. Miktar ayrılmadı |
| H3 | NİV, H1 ve H2’yi küçültür | kurulmadı | belirlenemiyor | yazılmadı | yazılmadı | Açık piyasa ve KKM stoku ayrı ayrı duruyor | Üç parçalı NİV yok |
| H4 | Fiyat açıklar, miktar anlamsızsa H1 ve H2 çürür | kurulmadı | belirlenemiyor | yazılmadı | yazılmadı | Kural, sınama olmadan çürütme yazmayı kapattı | Fiyat serisi yok |
| H5 | Artık artınca dolarizasyon payı azalır | kurulmadı | belirlenemiyor | yazılmadı | yazılmadı | Arşiv mevduat 146 ay | Artık yok. Yeni tablo n = 29 |
| H6 | Artış ve azalış ayrı katsayı | kurulmadı | belirlenemiyor | yazılmadı | yazılmadı | Ayrı katsayı kuralı yazıldı | NDV ve net altın serisi yok |

İşaret değişimi yoktur. İki sütun da yoktur.

## 4. Kontrol duyarlılığı

Kontrollü tahmin yok. Kontrolsüz tahmin yok.

| Kontrol | Durum |
| --- | --- |
| PKA 12 ay dolar | Seri duruyor, 2013-01…2026-10, n = 166. Artık kurulmadığı için farka girmedi |
| 24 ay enflasyon beklentisi | Duruyor, n = 166 |
| KKM kuklası | Tebliğ inmedi. Kukla yok |
| Kırılma kuklaları | Takvim yazıldı. Örnek yok |
| Altın fiyat etkisi | Ons serisi yok |

## 5. Eşdoğrusallık

Korelasyon matrisi ve VIF hesaplanmadı. Ortak tahmin yoktur. VIF eşiği 5, ön kayıtta duruyor ve uygulanmadı.

## 6. Asimetri

Yükseliş ve düşüş için ayrı katsayı yazılmadı. Tek doğrusal katsayı da yazılmadı.

## 7. Veri eksikleri

Swap stoku ve altın swap tonu H1, H2, H3 ve H6’yı kapatır. DTH faiz sepeti artığı kapatır. Artık, H1’den H5’e kadar her denklemin sol veya sağ yanıdır. Ons fiyatı H2 ve H4’ü kapatır. Altın gramı, altın payının miktar satırını kapatır. Üç parçalı net iç varlık H3’ü kapatır. Yeni mevduat tablosu 29 aydır. Eşik 36’dır. Arşiv 146 aydır ve yeni tabloyla birleştirilmedi.

Dış kaynaklı rezerv ile iç kaynaklı altın mevduatı aynı kanal diye yazılmadı. İkisi de ölçülemedi.

## 8. Monografi

Net dış varlık (merkez bankasının döviz ve altın varlığından, swap dahil yükümlülükleri düşünce kalan stok) bu turda kurulamadı. Brüt rezerv onun yerine konmadı. Net altın miktarı (fiyatın şişirmediği, ton cinsinden stok) de kurulamadı. Eldeki altın kalemi milyon dolardır. O kalem fiyat ile miktarı birlikte taşır. TL–DTH artığı (TL mevduat faizinden döviz mevduat faizini ve beklenen kur değişimini düşünce kalan fark) kurulamadı, çünkü döviz tevdiatın tek faiz serisi yok. ABD doları mevduat faizi duruyor ve sepetin yerine yazılmadı. Sonuç zayıftır. Altı hipotez de belirlenemiyor. Para kanalı ile kur beklentisi kanalı bu veride ayrılmadı.

## 9. Eleştiriler

Altın mevduatı, hane ve firmanın bankadaki altınıdır. Merkez bankasının dışarıdan altın alması başka bir stoktur. Birincisi içerideki mevduatın biçim değiştirmesidir. İkincisi dış varlıktır. Gram serisi olmadığı için birincisinin miktarı yazılamadı. Dolar karşılığı, fiyat yükselişini miktar artışı gibi gösterir. İki kanal bu turda ayrı raporlanamadı. Birleştirilmedi.

Swap düzeltmesi, yayımlanmış bir swap kalemi olsaydı bile o kalemin hangi kurdan ve hangi vadeden tutulduğuna bağlı olurdu. Bu turda o kalem yok. Yabancı pasifin içinden swapı göz kararı ayırmak, net dış varlığı olduğundan büyük ya da küçük bırakır. O ayırma yapılmadı. Brüt rezervi netmiş gibi kullanmak swapı hiç düşmemek olurdu. O da yapılmadı.

PKA 12 ay dolar serisi 2013-01’den 2026-10’a deliksiz duruyor. Yine de bir ayda bir kez açıklanan, 12 ay sonraki kur düzeyidir. Mevduat faizi 3 aya kadardır. 12 aylık kur beklentisini 3 aylık faiz farkından çıkarmak, ufukları yapıştırır. Artık kurulsaydı bu yapıştırma artıkın içine girerdi. Kurulmadı.
