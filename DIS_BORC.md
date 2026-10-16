# Dış borçta sahip ve ödeyen

Kurallar: `DIS_BORC_ONKAYIT.md`. Çekim: 2026-10-16. Ham: `dis_borc_sahip_ham.csv`.

2026-Q2’de brüt dış borcun yüzde 81,9’u genel hükümetin dışındadır. En büyük iki sahip diğer sektörler ve bankalardır. Kısa vadeli brüt geri ödeme yayımlı olmadığı için ödeme kaynağı belirlenemiyor. En büyük belirsizlik, stok değişiminin işlem, değerleme ve diğer hacim diye ayrılmamasıdır.

## Veri doğrulama

Birim, TCMB Dış Borç Metaveri, 12 Mart 2026: tüm değişkenler milyon ABD doları. Ödemeler dengesi metaverisi aynı birimi yazar. KVDB metaverisi de milyon ABD dolarıdır. Brüt dış borçtaki kısa vade, Dış Borç Metaveri’de orijinal vadesi bir yıla kadar olandır. KVDB sözlüğü de “kısa vade”yi orijinal vade diye tanımlar. Aynı belgenin IV. bölümü ikinci bir stok tanımlar: kalan vadeye göre kısa vadeli dış borç. Temmuz 2026 bülteni, Tablo 5 dipnotunda bunu “orijinal vadesine bakılmaksızın vadesine bir yıl ve daha kısa kalan dış borç” diye yazar.

| Kalem | Kod | Birim | İlk | Son | Kırılım | Durum |
| --- | --- | --- | --- | --- | --- | --- |
| SDDS toplam | `TP.BRUTDBSDDS.G1` | milyon USD | 2005-Q4 | 2026-Q2 | sektör | doğrulandı, n=83 |
| Genel hükümet | `TP.BRUTDBSDDS.G2` | milyon USD | 2005-Q4 | 2026-Q2 | sektör | doğrulandı |
| TCMB | `TP.BRUTDBSDDS.G16` | milyon USD | 2005-Q4 | 2026-Q2 | sektör | doğrulandı |
| Bankalar | `TP.BRUTDBSDDS.G30` | milyon USD | 2005-Q4 | 2026-Q2 | sektör | doğrulandı |
| Diğer sektörler | `TP.BRUTDBSDDS.G43` | milyon USD | 2005-Q4 | 2026-Q2 | sektör | firma ve hane ayrılmıyor |
| Doğrudan yatırım borç ilişkisi | `TP.BRUTDBSDDS.G56` | milyon USD | 2005-Q4 | 2026-Q2 | ayrı satır | doğrulandı |
| Borçlu tablosu, kısa vade | `TP.BRUTDBORCLU.G19` | milyon USD | 1989-Q4 | 2026-Q2 | orijinal vade | çeyrek brüt dış borç |
| Döviz dağılımı | `TP.BRUTDBDOVKOMP.G1`–`G7` | milyon USD | 2000-Q4 | 2026-Q2 | para birimi, sektör yok | doğrulandı, n=103 |
| Uzun vadeli kredi kullanımı ve geri ödemesi | `TP.ODEAYRSUNUM6.Q164` ve kardeşleri | milyon USD | 1989-12 | 2026-08 | sektör, brüt | yalnız uzun vadeli kredi |
| Kısa vadeli kredi | `TP.ODEAYRSUNUM6.Q162` ve kardeşleri | milyon USD | 1989-12 | 2026-08 | sektör, net | brüt geri ödeme yok |
| Net hata ve noksan | `TP.ODEAYRSUNUM6.Q210` | milyon USD | 1989-12 | 2026-08 | sektör yok | doğrulandı |
| KVDB, orijinal vade toplam | `TP.KVDB19` | milyon USD | 1989-12 | 2026-07 | Tablo 1 | bültenle aynı hücre |
| KVDB, kalan vade toplam | `TP.KALANVADE.K20` | milyon USD | 2011-07 | 2026-07 | Tablo 5 | 2026-07 hücresi 248.128 |
| Değerleme, diğer hacim | yok | — | — | — | — | katalogda yok |

Ortak tam yıl, SDDS yıl sonu ile uzun vadeli kredi akımı için 2006–2025’tir. S1’i bağlayan seri SDDS’tir. 2005-Q4’te başlar.

2026-Q2’de beş SDDS parçası toplamı, toplamın kendisine eşittir. Fark 0. Borçlu tablosundaki genel hükümet de 97.683’tür. İki tablo ayrılmıyor. Kamu bankası 77.551 ile özel banka 107.686, SDDS banka satırı 185.237’yi verir.

## Stok, 2026-Q2

Tablo: Brüt Dış Borç, tüm sektörler, enstrüman dağılımı. Milyon ABD doları.

| Sektör | Stok | Pay | Orijinal kısa vade |
| --- | --- | --- | --- |
| Genel hükümet | 97.683 | 18,1% | 790 |
| TCMB | 23.094 | 4,3% | 23.094 |
| Bankalar | 185.237 | 34,4% | 74.877 |
| Diğer sektörler | 212.561 | 39,4% | 70.213 |
| Doğrudan yatırım, ortak borç | 20.381 | 3,8% | satır yok |
| Toplam | 538.956 | 100% | |

Borçlu tablosundaki orijinal kısa vade 170.722’dir. Toplamın yüzde 31,7’si. SDDS sektör kısa vadelerinin toplamı 168.974’tür. Aradaki 1.748 milyon, toplamın yüzde 0,3’üdür. TCMB’nin toplam satırı ile kısa vade satırı bu çeyrekte aynı sayıdır.

Borçlu tablosundaki geniş kamu 197.910’dur. Pay yüzde 36,7. Bu satır genel hükümet, kamu bankası ve KİT’i birlikte taşır. S1’in payı değildir.

Kur kırılımı, aynı çeyrek, döviz dağılımı tablosu. Bileşenler toplama uyar. TL 66.007 milyon ABD doları, pay yüzde 12,2. Döviz payı yüzde 87,8’dir. Bunun 263.369’u USD, 155.238’i EUR, 3.941’i JPY, 7.367’si SDR, 43.033’ü diğerdir. Sektöre göre döviz kırılımı yoktur.

Yıl sonu payları, aynı SDDS tablosu:

| Yıl sonu | Toplam | Genel hükümet | Bankalar | Diğer | TCMB | Ortak borç | Orijinal kısa | Döviz |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2018-Q4 | 412.049 | 21,5% | 39,3% | 34,4% | 1,4% | 3,4% | 22,5% | 93,8% |
| 2019-Q4 | 398.506 | 22,4% | 37,7% | 34,6% | 2,1% | 3,1% | 24,0% | 94,5% |
| 2020-Q4 | 390.820 | 20,9% | 36,5% | 34,3% | 5,5% | 2,8% | 28,5% | 92,7% |
| 2021-Q4 | 378.522 | 19,4% | 33,1% | 37,8% | 6,9% | 2,7% | 31,3% | 95,5% |
| 2022-Q4 | 388.639 | 16,6% | 31,9% | 40,0% | 8,4% | 3,1% | 38,2% | 95,0% |
| 2023-Q4 | 432.551 | 17,5% | 31,6% | 37,2% | 10,7% | 2,9% | 40,5% | 94,2% |
| 2024-Q4 | 461.237 | 19,7% | 33,8% | 35,8% | 7,5% | 3,2% | 37,5% | 86,9% |
| 2025-Q4 | 522.732 | 18,9% | 34,5% | 38,1% | 4,8% | 3,7% | 32,0% | 88,0% |

## Akış, 2025

Ödemeler dengesi ayrıntılı sunum, milyon ABD doları. Uzun vadeli kredi anaparası brüt satırdır. Tahmin değildir. 2025’te on iki ay doludur. 2026 Ağustos’ta biter, yıl tam değildir.

Kısa vade, borç senedi, mevduat ve ticari kredide brüt geri ödeme satırı yoktur. O hücreler belirlenemiyor.

| Sektör | Uzun vadeli kredi kullanımı | Uzun vadeli kredi geri ödemesi |
| --- | --- | --- |
| Genel hükümet | 4.421 | 2.406 |
| TCMB | 0 | 0 |
| Bankalar | 53.196 | 31.019 |
| Diğer sektörler | 40.132 | 19.372 |

IMF kullanım ve geri ödeme satırları, genel hükümet ve TCMB için 2025’te 0’dır. Banka uzun vade net satırı `TP.ODEAYRSUNUM6.Q168` 2025 toplamı 22.177’dir. Bu, kullanım eksi geri ödemeye eşittir. İki brüt satır da artı yazılmıştır.

Kısa vadeli kredi 2025’te tek nettir. Bankalar −7.475, diğer sektörler 2.307, genel hükümet 0, TCMB 0. Bu net, brüt geri ödeme değildir.

## Özdeşlik

Değerleme ve diğer hacim serisi katalogda yoktur. Artık yazılmadı. Yüzde 5 eşiği uygulanmadı. Stok farkı geri ödeme sayılmadı.

Net hata ve noksan, 2025 toplamı −5.902 milyon ABD dolarıdır. Sektör ödemesi değildir.

## Hangi kısa vade

İki yayımlanmış stok vardır. Biri orijinal vadedir. Öteki kalan vadedir.

Orijinal vade, borçlu tablosundaki `TP.BRUTDBORCLU.G19` ve KVDB Tablo 1’deki `TP.KVDB19`’dur. 2026-06’da `TP.KVDB19` 170.597’dir. Bülten Tablo 1, 2026 Ç2 toplamı da 170.597’dir. TCMB 23.094, genel hükümet 790, bankalar 74.604, diğer sektörler 72.109. Alt kalemler de aynı sayıdır. 2026-Q2’de G19 170.722’dir. Aylık toplamdan farkı 125 milyon ABD dolarıdır. 125’in kalem dökümü yayımlı bir mutabakat satırında yoktur. İki hücre birleştirilmedi.

Kalan vade, `TP.KALANVADE.K20`’dir. Grup adı “Kalan Vadeye Göre Borç”tır. İngilizce grup adı “Debt Stock on a Remaining Maturity Basis”tir. 2026-07’de seri 248.128’dir. Bültenin Tablo 5 toplamı da 248.128’dir. Merkez Bankası, genel hükümet, banka kredisi, mevduat satırları, diğer sektörler ve alt kalemler aynı sayıdır. Tablo 6, `TP.KALVADBG.K18` ile aynı toplamı verir.

2026-06’da kalan vade toplamı 238.910, orijinal vade aylık toplamı 170.597’dir. Fark 68.313’tür. Bu fark, aynı aydaki dört satır farkının toplamıdır. Genel hükümet 11.062 − 790 = 10.272. Banka kredileri 44.013 − 7.977 = 36.036. Ticari krediler 64.313 − 63.565 = 748. Diğer krediler 29.801 − 8.544 = 21.257. Döviz tevdiat hesabı, banka mevduatı, TL mevduat ve prefinansman iki tabloda da aynı sayıdır. Yöntem, genel hükümet hücresini gelecek bir yılın borç projeksiyonu diye yazar. Banka kredisi, ticari kredi ve diğer kredi satırına, vadesine bir yıldan az kalmış uzun vadeli kısmın eklendiğini yazar. 68.313, ayrı bir “uzun vade artığı” satırı olarak yayımlı değildir. Dört satır farkının toplamıdır.

G19 ile K20 arasındaki 68.188, bu 68.313’ten çeyrek–ay farkı olan 125’in çıkarılmasıdır. K20, G19’un yerine konmadı.

Aynı ikili, yıl sonlarında da durur. 2024-12 orijinal aylık 172.988, çeyrek 173.015, kalan vade 221.287. 2025-12 orijinal aylık 167.367, çeyrek 167.462, kalan vade 230.461.

S2 değişmedi. İki stok da geri ödeme akımı değildir. Kısa vadeli brüt kullanım ve brüt geri ödeme hâlâ yoktur. Ön kayıt, sözlükteki orijinal vade cümlesini `TP.KALANVADE` grubuna uygulamıştı. Tablo 5 eşlemesi bu okumayı düzeltir. Eşikler ve S1–S4 durur.

## S1–S4

| | Kriter | Hesap | Sonuç |
| --- | --- | --- | --- |
| S1 | Kamu dışı pay > %50 | 1 − 97.683 / 538.956 = %81,9, 2026-Q2 | destekleniyor |
| S2 | Kısa vade yeni borç / geri ödeme > 1 | Brüt kısa vade geri ödemesi yok | belirlenemiyor |
| S3 | Borç payı − ödeme payı > 10 puan | Toplam geri ödeme yok | belirlenemiyor |
| S4 | %10 kur şokunda borç/GSYH | Sektör dövizi yok. Parite kodu metaveride yok | belirlenemiyor |

Toplam döviz payı yüzde 87,8’dir. Bu bir borç/GSYH şoku değildir.

## Sahip ve ödeyen, 2025-Q4 stok, 2025 akımı

Ödeme payı, brüt dış borcun tamamı için yazılmadı.

| Sektör | Borç payı | Ödeme payı | Fark |
| --- | --- | --- | --- |
| Genel hükümet | 18,9% | belirlenemiyor | yazılmadı |
| TCMB | 4,8% | belirlenemiyor | yazılmadı |
| Bankalar | 34,5% | belirlenemiyor | yazılmadı |
| Diğer sektörler | 38,1% | belirlenemiyor | yazılmadı |
| Ortak borç | 3,7% | belirlenemiyor | yazılmadı |

Yalnız uzun vadeli kredi anaparası, 2025. Bu dar akımdır. S3 buna uygulanmadı. Paylar, dört sektörün geri ödeme toplamı 52.797 üzerindedir.

| Sektör | Borç payı | Bu akımdaki pay | |
| --- | --- | --- | --- |
| Genel hükümet | 18,9% | 4,56% | 2.406 |
| TCMB | 4,8% | 0 | 0 |
| Bankalar | 34,5% | 58,75% | 31.019 |
| Diğer sektörler | 38,1% | 36,69% | 19.372 |

Bankanın bu dar akımdaki payı, borç payının üstündedir. Genel hükümetinki altındadır. Borç senedi, mevduat, kısa vade ve ticari kredi bu hesapta yoktur. Fark, borcun devri diye okunmaz.

## Eksik kırılım

Sektör dövizi olmadığı için kur riskinin kimde olduğu kapanır. Kalan vadeye göre stok yayımlıdır; bu stok geri ödeme değildir ve S2’yi kapatmaz. Kısa vadede brüt kullanım ve brüt ödeme ayrılmadığı için S2 kapanır. Değerleme satırı olmadığı için stoktan geri ödeme çıkarmak kapanır. Diğer sektörün içinde firma ve hane ayrılmaz.

Yıl sonu stok çeyrektir. Çeyrek içinde gelip giden kur, Aralık veya Haziran bakiyesinde durmaz. Döviz cinsi stok zaten dolarla yazılır. TL’nin çeyrek içi sıçraması, dolar stokunun döviz dilimini oynatmaz. TL dilimi yüzde 12,2’dir. Onun dolar karşılığı çeyrek sonu paritesine bağlıdır.

## Monografi

Türkiye’nin dış borcu 2026’nın ikinci çeyreğinde 539 milyar ABD dolarıdır. Bunun beşte birinden azı genel hükümettedir. Kalan, şirketler ve bankalar ile merkez bankası ve ortaklara olan borç arasında durur. En büyük dilim, firma ile haneyi ayırmayan “diğer sektörler” satırıdır. Borcun yaklaşık onda dokuzu döviz cinsidir. Kim hangi ay anaparayı ödedi, bu stoktan okunmaz. Görünen ödeme, yalnız uzun vadeli kredinin anaparasıdır. Kısa borç, tahvil ve mevduatın geri ödemesi ayrı satırda yoktur. Bu yüzden “borcu tutan, borcu ödüyor” cümlesi bu veriyle kurulamaz.

## Eleştiriler

Uzun vadeli kredi anaparası, 2025 geri ödemesinin yüzde 59’unu bankaya yazar. Bankanın stok payı yüzde 34’tür. Bu kayma, eksik enstrümanın sonucudur. Tahvilini ödeyen genel hükümet bu satırda görünmez. Yöntem değişirse ödeyen değişir. Onun için bu pay S3’e konmadı.

Stok, çeyrek sonunun dolar bakiyesidir. Martta açılıp Haziranda kapanan bir kur sıçraması bu bakiyede yoktur. Yıl içi akış aylıktır. İkisi aynı takvimi tutmaz.

Sınıflama, borçlunun sektörüdür. Garantörün sektörü değildir. Hazinenin kefil olduğu özel borç, genel hükümette durmaz. Kamu bankasının borcu, SDDS’te bankadadır. Borçlu tablosunda kamudadır. Ortaklara olan borç, diğer sektörden çıkarılıp ayrı satıra konur. İştirak üzerinden borçlanan firmanın yükü, faaliyet sektöründe görünmeyebilir.
