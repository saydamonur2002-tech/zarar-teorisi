# Kalan vade stokunun Temmuz artışı

Kurallar: `KALAN_VADE_ARTIS_ONKAYIT.md`. Çekim: 2026-10-16. Ham: `kalan_vade_artis_ham.csv`.

2026-06’dan 2026-07’ye kalan vade stoku 9.218 milyon ABD doları arttı. Bu artış ölçüldü. Yeni borçlanma, geri ödeme, vade geçişi, değerleme ve diğer hacmin payı ölçülmedi. Beş bileşen de belirlenemiyor olduğu için hangisinin en büyük parça olduğu sıralanamaz. En sağlam hücre, stokun kendisidir: `TP.KALANVADE.K20`, 2026-06’da 238.910, 2026-07’de 248.128. Aynı ayın orijinal vade stoku, `TP.KVDB19`, 6.552 arttı. 9.218’in 6.552’si bu komşu stokun artışıyla aynı sayıdır. Kalan 2.666 yalnız kalan vade tablosundadır. Bu yakınlık, bileşenin adı değildir.

## Veri doğrulama

Birim, API kaydında yok. KVDB metaverisi, ödemeler dengesi metaverisi ve Dış Borç Metaveri (12 Mart 2026) milyon ABD doları yazar. TL serisi bu hesaba girmedi.

`TP.KALANVADE.K20` aylıktır. İlk ay 2011-07, son ay 2026-07, gözlem 181. Bu, aralıksız 181 aydır. Aylık değişim yorumunun 12 ay şartı sağlanır. Stok, yükümlülüktür. Akım değildir.

| Kalem | Kod | Birim | İlk | Son | n | Durum |
| --- | --- | --- | --- | --- | --- | --- |
| Kalan vade toplamı | `TP.KALANVADE.K20` | milyon USD | 2011-07 | 2026-07 | 181 | doğrulandı |
| Brüt dış borç, döviz toplamı | `TP.BRUTDBDOVKOMP.G1` | milyon USD | 2000-Q4 | 2026-Q2 | 103 | doğrulandı, K20 değil |
| Aynı tablo, USD | `TP.BRUTDBDOVKOMP.G2` | milyon USD | aynı grup | 2026-Q2 | — | K20’nin paritesi değil |
| Aynı tablo, EUR, JPY, SDR, diğer | `G3`, `G4`, `G5`, `G7` | milyon USD | aynı grup | — | — | adları seri listesinde |
| Aynı tablo, TL | `TP.BRUTDBDOVKOMP.G6` | milyon USD | aynı grup | 2026-Q2 | — | brüt dış borcun TL dilimi |
| Aynı tabloda orijinal kısa vade | `TP.BRUTDBDOVKOMP.G8` | milyon USD | aynı grup | 2026-Q2 | — | 2026-Q2 = 170.722 |
| KVDB döviz toplamı | `TP.KVADEDOVKOMP.USDTOPLAM` | milyon USD | 2005-Q1 | 2026-Q2 | 86 | orijinal vade toplamına eşit |
| Kısa vade brüt kullanım ve brüt geri ödeme | yok | — | — | — | — | kod yok |
| Kısa vade net satırlar | `TP.ODEAYRSUNUM6.Q145`, `Q162`, `Q167`, `Q175`, `Q180`, `Q189` | milyon USD | aylık | — | — | net; S3’e girmedi |
| Uzun vadeli kredi kullanımı ve geri ödemesi | `Q164`–`Q165`, `Q169`–`Q170`, `Q177`–`Q178`, `Q182`–`Q183` | milyon USD | 1989-12, yalnız `Q169` | 2026-08 | 419, yalnız `Q169` | sekiz satır 2026-06…08’de dolu; vade geçişi değil |
| Vade geçişi, anapara takvimi | yok | — | — | — | — | kod yok |
| Değerleme, diğer hacim | yok | — | — | — | — | UYP’de ve katalogda yok |

`TP.BRUTDBDOVKOMP.G1`–`G7`, brüt dış borcun döviz dağılımıdır. Son dönem 2026-Q2’dir. 2026-07 hücresi yoktur. 2026-Q2 toplamı 538.956’dır. Bu, kalan vade stoku değildir. Payı, K20’nin değerlemesine konmadı. Parite kodu bu stokun metaverisinde yazılı değildir. Parite seçilmedi.

`TP.KVADEDOVKOMP.USDTOPLAM`, 2024-Q1’den 2026-Q2’ye kadar her çeyrek sonunda `TP.KVDB19` ile aynı sayıdır. 2026-Q2’de ikisi de 170.597’dir. Aynı ayda K20 238.910’dur. Bu döviz tablosu orijinal vade stokunundur. Kalan vade stokunun döviz tablosu değildir. Aylık frekansla 2026-07 de gelmez.

Kısa vade satırlarının altında kullanım ve geri ödeme çocuğu yoktur. Uzun vade satırlarının altında vardır. 2026-06, 2026-07 ve 2026-08’de sekiz uzun vade satırı da doludur. 2026-07, milyon ABD doları: TCMB kullanım 0, geri ödeme 0; bankalar 4.385 ve 3.199; genel hükümet 215 ve 282; diğer sektörler 3.248 ve 1.592. Bu, uzun vadeli kredinin anapara akımıdır. O ay vadesi bir yılın altına inen borç değildir. Bileşen tablosuna yazılmadı.

Katalogda vade geçişi, diğer hacim, anapara takvimi ve amortisman grubu yoktur. “Değerleme” adını taşıyan tek grup konut kirasıdır (`bie_bk`). Dış borç değerlemesi değildir.

## Aylık stok

Milyon ABD doları. Seri `TP.KALANVADE.K20`.

| Ay | Stok | ΔStok |
| --- | ---: | ---: |
| 2025-08 | 226.520 | 3.231 |
| 2025-09 | 224.803 | −1.717 |
| 2025-10 | 225.966 | 1.163 |
| 2025-11 | 223.998 | −1.968 |
| 2025-12 | 230.461 | 6.463 |
| 2026-01 | 239.028 | 8.567 |
| 2026-02 | 239.158 | 130 |
| 2026-03 | 237.058 | −2.100 |
| 2026-04 | 242.046 | 4.988 |
| 2026-05 | 242.011 | −35 |
| 2026-06 | 238.910 | −3.101 |
| 2026-07 | 248.128 | 9.218 |

Karar ayı 2026-07’dir. ΔStok = 248.128 − 238.910 = 9.218.

## Bileşenler, 2026-07

| Bileşen | Değer | Etiket | Veri |
| --- | --- | --- | --- |
| Yeni kısa vadeli borçlanma | belirlenemiyor | belirlenemiyor | brüt kullanım satırı yok |
| Kısa vadeli geri ödeme | belirlenemiyor | belirlenemiyor | brüt geri ödeme satırı yok |
| Vade geçişi | belirlenemiyor | belirlenemiyor | anapara takvimi yok |
| Değerleme | belirlenemiyor | belirlenemiyor | K20’nin döviz tablosu ve parite kodu yok |
| Diğer hacim | belirlenemiyor | belirlenemiyor | satır yok |

Aynı beş etiket, tablodaki diğer on bir ay için de geçerlidir. Eksik bileşen sıfır yazılmadı. `TP.BRUTDBORCLU.G19` bu tabloda kullanılmadı.

## Özdeşlik artığı

Artık yazılmadı. Sağ taraftaki beş bileşen ölçülmeden ΔStok eksi toplam bileşen kurulamaz. Eksik bileşeni sıfır saymak, artığı 9.218 ve payı yüzde 100 yapardı. Bu, ön kaydın yasakladığı işlemdir. Yüzde 5 eşiği uygulanmadı.

## S1–S4

| | Kriter | Hesap | Sonuç |
| --- | --- | --- | --- |
| S1 | Vade geçişi / ΔStok > %50 | Vade geçişi yok | belirlenemiyor |
| S2 | Dolar dışı pay × parite değişimi > ΔStok’un %10’u | K20’nin döviz payı ve parite kodu yok | belirlenemiyor |
| S3 | Brüt borçlanma / brüt geri ödeme > 1 | İki brüt satır da yok. Net satır kullanılmadı | belirlenemiyor |
| S4 | Diğer hacim ve artık > \|ΔStok\|’un %5’i | Artık kurulmadı | belirlenemiyor |

Stok artışı borçlanma diye yorumlanmadı. Yenileme diye de yorumlanmadı.

## Veri eksikleri

Kalan vade stokunun kendi döviz kompozisyonu, 2026-06 ve 2026-07. Bu gelirse değerleme, miktar değişiminden ayrılabilir. S2 ancak o zaman hesaplanır. Parite kodu da metaveride adlandırılmalıdır.

Kredi bazında anapara takvimi. Hangi uzun vadeli borcun kalan vadesinin o ay bir yılın altına indiği. Bu gelirse S1 hesaplanır. Uzun vadeli kredi kullanımı ve geri ödemesi bu takvimin yerine konmaz.

Kısa vadeli brüt kullanım ve brüt geri ödeme, bu stokla aynı kapsamda. Bu ikisi gelirse S3 hesaplanır. Net finansal hesap satırı yetmez.

Bu stok için değerleme ve diğer hacim satırı. İkisi de gelirse artık yazılır ve S4 uygulanır.

## Hangi veriye yakın

Stok, bir tarihteki bakiyedir. Artış, dört ayrı yoldan gelebilir: yeni kısa vadeli borç, vade geçişi, parite değerlemesi, geri ödemenin beklenenden az olması. Dördüncüsü bakiyeyi yerinde tutar. 9.218’lik bir artışı tek başına üretmez. İlk üçü ayrı satır ister. O satırlar yoktur. S1–S4 durur.

9.218, kendi tablosunun satır toplamıdır. Milyon ABD doları, 2026-07 eksi 2026-06.

| Kalem | Kalan vade | Orijinal vade | Yalnız kalan vadede |
| --- | ---: | ---: | ---: |
| TCMB | 49 | 49 | 0 |
| Genel hükümet | 2.337 | 639 | 1.698 |
| Bankalar | 3.951 | 3.242 | 709 |
| Banka kredileri | 2.580 | 1.871 | 709 |
| Döviz tevdiat | 230 | 230 | 0 |
| Banka mevduatı | 1.285 | 1.285 | 0 |
| TL mevduat | −144 | −144 | 0 |
| Diğer sektörler | 2.881 | 2.622 | 259 |
| Ticari krediler | 1.514 | 1.501 | 13 |
| Diğer krediler | 1.367 | 1.121 | 246 |
| Toplam | 9.218 | 6.552 | 2.666 |

Toplam, TCMB, genel hükümet, bankalar ve diğer sektörlerin toplamıdır. Kredi ve mevduat satırları bankanın içindedir. Ticari kredi ve diğer kredi, diğer sektörün içindedir.

Orijinal vade, `TP.KVDB19` ve alt satırlarıdır. 2026-06’da 170.597, 2026-07’de 177.149. Mevduat satırları iki tabloda da aynı farkı verir. Bu dilim, kalan vade tablosuna sonradan eklenen uzun vade parçası değildir. İki stokta birden duran bir bakiye değişimidir. İçinde yeni borç, ödeme ve parite hâlâ ayrılmamıştır.

Yalnız kalan vade tablosunda duran 2.666’nın 1.698’i genel hükümet satırındadır. Yöntem, bu satırı gelecek bir yılın borç projeksiyonu diye yazar. Ayrı bir vade geçişi akımı değildir. Banka kredisindeki 709 ve diğer kredideki 246 da aynı durumdadır: iki stokun farkının değişimidir, takvim satırı değildir.

Uzun vadeli kredi kullanımı, 2026-07, dört sektörün toplamı 7.848’dir. 9.218’e uzaklığı 1.370’tir. Sayı, orijinal vade stokunun 6.552’sinden daha yakındır. Kavram yakından uzaktır. Bu, uzun vadeli kredinin o ay çekilen anaparasıdır. Bir yılın içine yeni giren borç değildir. Kısa vadeli net satırlar, 2026-07: `Q145` 3, `Q162` 0, `Q167` 570, `Q175` 0, `Q180` 272, `Q189` 1.483. En büyüğü ticari kredinin netidir, 1.483. Hiçbiri 9.218 değildir. Bu altı satırın yan yana toplamı yayımlanmış bir toplam değildir. Nettir. S3’e girmedi.

Yakın veri, aynı ailenin öbür stokudur: orijinal vadeye göre kısa vadeli dış borç, aynı ay, 6.552. Artışın mekanizması bu komşuluktan okunmaz.

## Monografi

Bir yıl içinde ödenmesi gereken dış borç, Haziran 2026’da 238,9 milyar dolardı. Temmuzda 248,1 milyar dolara çıktı. Artış 9,2 milyar dolardır. Bu, o ay yapılan bir ödeme değildir. Borcun o tarihteki bakiyesidir. Bakiyenin neden büyüdüğü bu veriye yazılmamıştır. Yeni borç alınmış olabilir. Eski bir borcun vadesi bir yılın içine girmiş olabilir. Bir kısmı ödenmiş olabilir. Euro ya da lira cinsinden borcun dolar karşılığı oynamış olabilir. Bu beş ihtimalin tutarı ayrı satırda yoktur. Onun için Temmuz artışı yeni borçlanma diye okunamaz.

## Eleştiriler

Vade geçişi, kimse yeni borç almasa da bu stoku büyütür. Vadesine on üç ay kalmış bir kredi, bir ay sonra on iki aya iner ve stoğa girer. Stok artışı, o ay kasaya giren parayı göstermez.

Değerleme ile yeni borçlanma aynı ayda bir arada durabilir. Euro borcun dolar karşılığı değişir, aynı hafta yeni bir kredi de çekilir. İkisi de dolar stokunu oynatır. Ayrılmadan yazılan toplam, ikisinden birine bağlanamaz. Brüt dış borcun TL dilimi bu ayrımı vermez. O dilim başka stoktur ve Temmuz hücresi yoktur.

Kalan vade tanımı, yenilenen borcun bir kısmını görmez. Bir yılın içindeki borç kapanıp yerine vadesi bir yıldan uzun yeni borç açılırsa stok düşer. Yükümlülük sürmüştür. Tersi de olur. Kısa borç aynı pencerenin içinde yenilenirse stok yerinde durur. Yenilemenin brüt tutarı stoktan okunmaz.
