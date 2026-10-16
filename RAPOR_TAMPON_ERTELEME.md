# Tampon ve Erteleme — ölçüm raporu

Tarih: 16 Ekim 2026. Sayı uydurulmadı. Dosyada olmayan hücre boş bırakıldı.

Harcama kapasitesi, bir hanenin eline geçen gelir ile o yıl net yeni borçlanmanın toplamıdır. Kredi, gelir değildir. Tampon, şokta diğer kesimlerin açığını kapatan taraftır. Erteleme, borcun ödenmeyip döndürülmesi ve faizin borçlunun üstünde kalmasıdır.

## 1. Kaynak tablosu

| Kolon | Kurum ve tablo | Tarih | Birim | Durum |
|---|---|---|---|---|
| D.1, B.2/B.3, D.4, D.41, D.62, D.5, D.61, D.7, P.3, P.51, B.6, B.9 | TÜİK Kurumsal Sektör Hesapları, bülten 58286 | 8 Ekim 2026 | — | **Veri yok.** Bülten metni okundu. Excel ve SDMX ekine bu ortamdan erişilemedi (indirme 403, SDMX 401). |
| dL | TCMB EVDS `TP.FINHESTNKS62014.ZP34`, F.4 yükümlülük **işlemi** | Çekim 16 Ekim 2026 | milyon TL | Dört çeyrek toplamı, S.14 |
| dA | TCMB EVDS `TP.FINHESTNKS62014.ZP23`, VF.0 varlık işlemi | aynı | milyon TL | S.14 |
| L_stok | TCMB EVDS `TP.FINHESTNKS14.ZP34`, F.4 yükümlülük **stoku** | aynı | milyon TL | Yılın 4. çeyreği |
| GSYH | TÜİK harcama yöntemi, EVDS `TP.GSYIH20.BY.B1GQ` | Çekim 16 Ekim 2026 | milyon TL | Dört çeyrek toplamı. Ekim sektör bülteni ile aynı yayım sürümü değil. |
| cari denge | — | — | — | **Veri yok.** `TP.ODANA6.Q01` birimi serinin künyesinde yazmıyor; TL sütununa konmadı. |
| deflatör | — | — | — | Veri yok |
| Beş sektör BF.9 işlem ve stok | TCMB EVDS finansal hesaplar, konsolide olmayan, gruplar `bie_finhestnks*` ve `bie_finhestnks620*` | Çekim 16 Ekim 2026 | ham veri bin TL; tablolar milyon TL | Akım = işlem. Kanıt aşağıda. |
| Azami kart faizi | TCMB, kredi kartı azami akdi faiz tabloları | 1 Kasım 2020 öncesi PDF; 1 Kasım 2020–31 Aralık 2025 PDF; 2026 sayfası 16 Ekim 2026 çekimi | aylık yüzde | Yıllık oran, 12 ayın bileşik faizidir |
| İhtiyaç kredisi akım faizi | EVDS `TP.KTF10`, dosya `faiz_ham.csv` | Dosyadaki aylar | yıllık yüzde | 12 ayın aritmetik ortalaması. Kart tavanı değildir. |
| Takip | EVDS `bie_hpbitablo6`, dosya `npl_ham.csv` | 2024-06 … 2026-09 | oran | Canlı stok + takip. Aralık 2023 bu dosyada yok. |
| TÜFE | EVDS `TP.GENENDEKS.T1` (2003=100) | Çekim 16 Ekim 2026 | Aralık/Aralık | Ücret artışı değildir. `ham/tufe_aralik.csv` |

Ham finansal hesap birimi bin TL'dir. 2026-Q1 hanehalkı F.4 stoku 6.755.140.613 bin TL, yani 6.755,1 milyar TL'dir. CSV'de akışlar milyon TL'dir (bin TL / 1.000).

Bülten 58286'nın kendi cümlesi, modele yazılmadan burada durur: 2025 GSMH 62 trilyon 288 milyar 195 milyon 804 bin TL; hanehalkı tasarruf oranı 2024'te %13,9, 2025'te %14,3. Daha eski bültendeki %11,3 bu raporda kullanılmadı. Bu başlıklar D.1 veya B.6 düzeyini vermez.

## 2. Çapalar

`python talep_capa_modeli.py veri_hanehalki.csv` çalıştı. Zorunlu gelir ve harcama kolonlarının 11 yılı da boş. Betik üç çapayı da "veri yok" diye geçti. H1 satırı basılmadı, çünkü kredi bağımlılık serisi boş. H2 ve H3 atlandı.

Akımın stok farkı olmadığı, S.14 için ölçüldü (`akim_stok_kontrol.csv`):

- F.4 kredide, 2015–2017 ve 2019–2025'te yıllık işlem toplamı ile stok farkı binde bir düzeyinde örtüşür. 2018'de örtüşmez: stok 19,3 milyar TL artarken işlem **−47,8 milyar TL**'dir. Aradaki fark yeniden değerlemedir. 2018'de kur, borç stokunu işlem olmadan şişirmiştir.
- BF.9 net finansal değerde işlem ile stok farkı her yıl ayrılır. 2021'de stok artışının yaklaşık %81'i işlem dışıdır. Akım serisi yeniden değerlemeyi içermez.

Çapa-2'nin toplam ekonomi için bir gölgesi var, hanehalkı için değil. Bülten, toplam ekonominin 2025'te GSYH'nin %1,8'i kadar net borç alan olduğunu yazar. Aynı yıl EVDS'te S.1 net borç verme işlemi GSYH'nin %3,6'sı kadar negatiftir. 2024'te bülten %0,9, EVDS %0,6. İki sayı aynı değildir. Ya yayım sürümü farklıdır ya da reel hesap ile finansal hesap arasındaki istatistiksel fark büyüktür. Hanehalkı B.9 kolonu boş olduğu için bu fark hane düzeyinde ölçülememiştir.

## 3. Testler

| Kod | Beklenti | Sonuç | Karar |
|---|---|---|---|
| H1 | Bant %20–30 reddedilir | Payda (P.3+P.51) boş. Betik H1 satırını basmadı. | **Belirlenemedi** |
| H2 | Faiz yükü kredi bağımlılığıyla artar | D.41 boş | **Belirlenemedi** |
| H3 | Hane B.9 düşünce cari denge bozulur | B.9 ve TL cari denge boş | **Belirlenemedi** |
| T1 | Şokta alt %20'nin reel tüketimi daha sert düşer | Gelir dilimi tüketim tablosu yok | **Belirlenemedi** |
| T2 | Ardışık şoklarda alt kesimin emilim payı azalır | Dilim tablosu yok | **Belirlenemedi** |
| E1 | 2023 sonu–2026: kart faizi > ücret artışı ve bireysel takip yükselir | Takip bacağı 2024-06'dan itibaren yükseldi. Aralık 2023 yok. Ücret artışı yok, `i > g_w` hesaplanamadı. | **Belirlenemedi** (takip yönü bu pencerede iddiayla uyumlu) |
| E2 | Bireysel Aşama 2 payı artar | Sektör düzeyi seri yok | **Belirlenemedi** |
| E3 | Takip, düşük borç dilimlerinde daha hızlı artar | Dilime göre takip yok | **Belirlenemedi** |

H1 hakkında ölçülen sınır, testin yerine geçmez. F.4 işlem / GSYH, 2015–2025'te %1,5 ile %4,8 arasındadır; 2018'de **−%1,3**'tür. Oranın %20'ye çıkması için hane harcamasının GSYH'nin yaklaşık beşte birinin altına düşmesi gerekir. Bu bir üst akıl yürütmesidir. P.3 ve P.51 gelmeden H1 reddedilmiş sayılmaz.

Borç stoku / GSYH: 2015'te %17,7, 2024'te %9,3, 2025'te %9,9. "Stok GSYH'nin yaklaşık %10'u" cümlesi 2024–2025'e uyar, 2015–2017'ye uymaz. Üst sınır testi stoku harcamaya böler. Harcama GSYH'den küçük olduğu için bu oran stok/GSYH'den büyüktür. 2015'te stok tek başına GSYH'nin %17,7'sidir; harcamaya bölününce %18'in üstüne çıkabilir. 2025'te stok/GSYH %9,9'dur; harcama GSYH'nin kabaca %55'i ise üst sınır %18 civarına gelir. Payda olmadan bu eşik kapanmaz.

## 4. Tampon tablosu

Net borç verme (NL), yayımlanan BF.9 işlemidir. Yeniden değerleme, yıl sonu BF.9 stokunun farkından bu işlemin çıkarılmasıdır. Servet değişimi ikisinin toplamıdır. Emilim payı, prompttaki tanımdır: bu servet değişiminin bir önceki yıla göre farkı, beş kesimin mutlak farkları toplamına bölünür. Pozitif pay, o yılki dönüşün o kesimin aleyhine olduğunu söyler.

Dış âlemde varlık işlemi eksi yükümlülük işlemi, BF.9'un ters işaretini verir. NL olarak BF.9 kullanıldı. 2021–2025'te beş kesimin NL toplamı sıfırdır. 2015–2020'de artık GSYH'nin en fazla %1,2'sidir (2020). 2021'de işlem kimliği kapanır, stok kimliği kapanmaz: beş kesimin servet değişimi toplamı **−320 milyar TL**'dir. 2023'te hem işlem hem stok kapanır.

Milyar TL. Pay, emilim payıdır.

| Yıl | Kesim | NL (işlem) | Yeniden değerleme | Servet değişimi | Emilim payı |
|---|---|---:|---:|---:|---:|
| 2018 | Hane + HHKOK | 148 | 77 | 225 | −%15,8 |
| 2018 | Firma | 180 | −296 | −116 | −%28,4 |
| 2018 | Kamu | −111 | −35 | −146 | −%4,3 |
| 2018 | Finansal kuruluşlar (S.12) | −168 | 113 | −55 | +%3,3 |
| 2018 | Dış âlem | −67 | 175 | 108 | +%48,2 |
| 2021 | Hane + HHKOK | 257 | 1.095 | 1.352 | −%24,6 |
| 2021 | Firma | −206 | −1.555 | −1.760 | +%17,7 |
| 2021 | Kamu | −65 | −64 | −129 | −%6,9 |
| 2021 | Finansal kuruluşlar | 249 | 232 | 481 | −%11,1 |
| 2021 | Dış âlem | −236 | −29 | −264 | +%39,7 |
| 2023 | Hane + HHKOK | 1.654 | 2.314 | 3.968 | −%32,8 |
| 2023 | Firma | −1.486 | −3.803 | −5.290 | −%1,3 |
| 2023 | Kamu | −624 | 540 | −83 | −%16,0 |
| 2023 | Finansal kuruluşlar | −235 | −615 | −850 | +%28,6 |
| 2023 | Dış âlem | 691 | 1.564 | 2.255 | +%21,4 |

**Birincil tampon** (işlemle açığı üstlenen, NL negatif olan):

- 2018: finansal kuruluşlar ve kamu.
- 2021: firma, kamu ve dış âlem. Finansal kuruluşlar net borç verendir.
- 2023: firma, kamu ve finansal kuruluşlar. Hanehalkı 1.654 milyar TL net borç verendir.

**Nihai tampon** (yeniden değerlemede serveti eriyen):

- Üç şok yılında da düzey olarak firma. 2018'de −296, 2021'de −1.555, 2023'te −3.803 milyar TL.
- Hanehalkı üç yılda da yeniden değerlemeden kazançlıdır: +77, +1.095, +2.314 milyar TL.

Formül ile düzey ayrışır. 2018'de formül dış âlemi öne çıkarır; o yıl servet kaybının düzeyi firmanın üstündedir. 2023'te formül finansal kuruluşlara %28,6 ve dış âleme %21,4 verir; firmanın kaybı sürmektedir ama bir önceki yıla göre hızlanmadığı için payı sıfıra yakındır. 2021 payları, stok kimliği −320 milyar TL açık verdiği için temkinle okunur.

Sektör toplamı, "alt gelir grubu tampondur" iddiasını desteklemez. Toplam hanehalkı bu üç şokta finansmanı sağlayan ve yeniden değerlemeden kazanan taraftadır. Bu, alt dilimin de kazandığı anlamına gelmez. Dilim tablosu olmadığı için o iddia açıkta kalır.

S.12 yalnız banka değildir; sigorta, fon ve merkez bankasını da içerir. 2021'de bu kesim net borç veren ve değer kazanan taraftadır. 2023'te hem net borç alan hem yeniden değerlemede kaybeden taraftadır ve formülün en yüksek payı ondadır.

## 5. Erteleme

`i`, TL kredi kartı azami **akdi** faizinin 12 aylık bileşik karşılığıdır. Borcunu kapatan kart faiz ödemez. Tavan, döndürenin karşılaştığı üst sınırdır; ödenen ortalama faiz değildir. Dilim varken alt, orta ve üst tavan ayrı yazıldı. 2024 Kasım'dan önce tek tavan vardır. `g_w` için güncel bir ücret serisi bu oturumda okunamadı. Asgari ücret, alt kesimin geliri olmadığı için hafızadan doldurulmadı. `i > g_w` hücreleri boştur.

| Yıl | Kart tavanı, bileşik, alt / orta / üst | İhtiyaç kredisi, akım ortalaması | Aralık/Aralık TÜFE | `g_w` |
|---|---:|---:|---:|---|
| 2018 | %26,6 | %26,8 | %20,3 | veri yok |
| 2019 | %26,8 | %23,9 | %11,8 | veri yok |
| 2020 | %17,2 | %15,9 | %14,6 | veri yok |
| 2021 | %25,7 | %23,5 | %36,1 | veri yok |
| 2022 | %22,7 | %30,9 | %64,3 | veri yok |
| 2023 | %28,8 | %44,7 | %64,8 | veri yok |
| 2024 | %58,8 / %61,1 / %62,6 | %72,0 | %44,4 | veri yok |
| 2025 | %51,1 / %62,8 / %72,4 | %65,7 | %30,9 | veri yok |
| 2026 | yıl tamam değil (10 ay) | 9 ay, yıl boş bırakıldı | Eylül'e kadar var, Aralık yok | veri yok |

İki rejim ayrılır. 2021, 2022 ve 2023'te kart tavanının bileşik hali Aralık/Aralık TÜFE'nin altındadır. Tavan faizle dönen borçlu, enflasyona karşı kazançlıdır. 2024 ve 2025'te tavan TÜFE'nin üstündedir. 2024'te ihtiyaç kredisi akım ortalaması %72 ile üst kart tavanının da üstündedir. Aynı hikâye iki rejime yazılamaz.

Ekim 2026 tavanı, aylık: 30 bin TL altında %3,25, 30–180 bin arasında %3,75, 180 bin üstünde %4,25. Yıl bitmediği için bileşik yıl oranı yazılmadı.

Takip, `npl_ham.csv`. Oran = takip / (canlı + takip). Tüketici serisi kartı da içerir.

| Dönem | Tüketici | Bireysel kart | Ticari ve diğer |
|---|---:|---:|---:|
| 2024-06 | %2,09 | %2,05 | %1,49 |
| 2024-12 | %2,83 | %2,91 | %1,56 |
| 2025-12 | %4,06 | %4,34 | %2,09 |
| 2026-01 | %4,28 | %4,52 | %2,19 |
| 2026-09 | %5,09 | %5,37 | %2,52 |

2024 Haziran'dan 2026 Eylül'e tüketici takip +3,0 puan, kart +3,3 puan, ticari +1,0 puandır. Bu pencerede bireysel bozulma ticari bozulmadan daha hızlıdır. Aralık 2023 bu dosyada yoktur; "%1,7'den geldi" cümlesi burada teyit edilmemiştir. E3 olmadan bu yükseliş alt dilime ait değildir. Aşama 2 kırılımı yayımlanmış bir seri olarak bulunamadı.

## 6. Sınırlar

- Hanehalkı sektörü esnafı da içerir. Ücretlinin oranı bu tabloda yoktur. HHKOK, 2023'te bloktan ayrı ve negatif bir net borç vermedir (yaklaşık −68 milyar TL). CSV'deki dL yalnız S.14 F.4 işlemidir.
- Toplam, dağılımı saklar. Sektör net borç verirken bir dilim borçlanıyor olabilir. 2018'de sektörün F.4 işlemi negatifken stok yükselmiştir; kur, borçlunun stokunu büyütmüştür.
- Bankalar S.12'nin içindedir. 2021'de kesim kanal gibi net borç verir. 2023'te formül onları emilim payının başına yazar. İki yıl aynı cümle değildir.
- Yeniden değerleme artık olduğu için ölçüm hatası taşır. 2021 stok kapanmayışı bunun büyüklüğünü gösterir: −320 milyar TL.

## 7. Kendini sorgulama

Sonuç, emilim payının tanımı değişirse tersine döner. Pay, servet değişiminin ikinci farkıdır. Firmanın kaybı 2023'te sürmesine rağmen hızlanmadığı için payı küçüktür. Tanım "o yılki yeniden değerleme kaybı" olsaydı, üç şok yılında da firma başa geçer, hanehalkı hiçbirinde tampon olmazdı. Bu ikinci okuma da alt dilimi göstermez.

2021'de dış âlemin %39,7'lik payı, kapanmayan −320 milyar TL'lik stok artığının içindedir. Artık kapanırsa o yılın sıralaması değişebilir.

`i > g_w` için asgari ücret artışı konursa E1'in faiz bacağı kapanır gibi görünür. Asgari ücret, emekli, kayıt dışı ve işsizin gelir artışı değildir. O vekil, alt kesim aleyhine de lehine de sonuç üretebilir. Bu yüzden boş bırakıldı.

TÜFE'nin ücretin yerine konması da sonucu çevirir. 2021–2023'te tavan TÜFE'nin altındadır; ücret TÜFE'nin de altındaysa borçlu ücrete karşı yine kaybeder. Ücret serisi olmadan rejim, borçlunun lehine kapanmış sayılmaz. Yalnız enflasyona karşı tavanın yeri ölçülmüştür.

H1, P.3 ve P.51 yerine GSYH konursa reddedilir, çünkü işlem GSYH'nin %5'inin altındadır. Payda küçüldükçe oran büyür. GSYH ile ret ilan etmek, testi değiştirmek olur.

## 8. Sonraki adım

1. Bülten 58286 ekindeki sektör hesabı (S.14+S.15), tek yayım sürümüyle `veri_hanehalki.csv` içine: D.1'den B.9'a kadar. Çapa-1, çapa-2, çapa-3, H1, H2 ancak o zaman çalışır.
2. Aynı bültenin TL cari dengesi ya da birimi yazılı bir ödemeler dengesi serisi. H3 için.
3. TÜİK Hanehalkı Bütçe Araştırması'nın yayımlanmış gelir dilimi tüketim tabloları, 2018, 2021, 2023. T1 ve T2.
4. Ücret: TÜİK kazanç veya saatlik işgücü maliyeti endeksi, 2018–2026. Asgari ücret ayrıca ve "alt kesim değildir" notuyla. E1'in `i > g_w` bacağı.
5. BDDK Aşama 2, bireysel. E2.
6. Kart bakiyesi dilimine (30 bin, 180 bin) göre takip. E3. Faiz dilimi yayımda var; takip dilimi bu oturumda yok.
