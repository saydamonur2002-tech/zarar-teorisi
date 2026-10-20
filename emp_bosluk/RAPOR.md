# EMP kaynak boşlukları

Kilit: `ON_KAYIT.md`, 2026-10-20T11:02:19Z. Eşikler skor görüldükten sonra değiştirilmedi. Bu metin doğrusal uydurmanın muhasebesidir [HESAP]. Karşı-olgu kurulmadı. Faiz kararının, seçimin veya firma hedge talebinin baskıyı ürettiği yazılmaz.

Bağlamdaki 55 puan ve 27–34 puanlık kalıntı girdi yapılmadı. Çalışma ağacında o ayrıştırmanın dosyası yoktu. Aşağıdaki EMP, kilitli formülden üretilir.

## Hüküm

| Test | Hüküm |
| --- | --- |
| VADE, vadesi 1 yıl içinde gelen firma döviz borcunun stok artışı | Yanlışlandı. Katsayı −0,70 [HESAP]. Shapley payı %3,0. |
| POZ, net döviz pozisyonu açığının büyümesi | Yanlışlandı. Katsayı −0,13 [HESAP]. Shapley payı %11,5. |
| CDS, 5 yıl Türkiye CDS farkı | Ana kaynak değil. Katsayı +0,045 [HESAP], pay %28,8 (eşik %30). 2021-Q4 kalıntısının %8,2’si. |
| BEK, 12 ay sonraki USD/TRY beklentisinin log farkı | Ana kaynak değil. Katsayı +0,71 ve pay %47,7 [HESAP]. Kayan pencere DOĞRULANMADI (aşağıda). 2021-Q4 kalıntısının %72,6’sını taban uydurmasına ekler. |
| SWAP, offshore TL faizi | DOĞRULANMADI. Yayımlı offshore faiz veya yurt dışı−yurt içi fark yok. Hacim Shapley’e konmadı. |
| Çevirme (rollover) oranı | DOĞRULANMADI. Aylık veya çeyreklik zaman serisi bulunamadı. |
| 2021-Q4 “akım değil, fiyat / beklenti” okuması | BELİRSİZ. Üç koşuldan fiyat-önce tutmuyor. |
| 2021, fiyat ile tahvil satışı, C2 | Aynı hafta. Fiyat-önce değil, akım-önce değil. |
| 2018-Q3, C2 | DOĞRULANMADI. Haftalık yurt dışı DİBS stoku 11 Eylül 2020’de başlar. |
| 2023 seçim penceresi, C2 | Akım-önce. Pencere sonu tahvil satışı 0,36 milyar dolar [HESAP]. |
| 2021 olay günleri, yalnız fiyat, C1 | Beş günden dördü “fiyat pencerede önde”. Bu, akımla karşılaştırma değildir. |

Ana kaynak üç çubuğu birlikte ister: Shapley payı ≥ %30, katsayı pozitif, kayan pencerelerin ≥ %60’ı. Kayan pencerede kurulan sayı 8’in altındaysa o test geçmiş sayılmaz. Burada kurulan pencere 6’dır. Dört aday için de kayan test DOĞRULANMADI.

BEK’te altı pencereden beşi pay ve işaret eşiğini tuttu. Bu sayım, kilit gereği hükme yazılmaz.

VADE ve POZ’un işareti, “vadesi gelen borç veya açık büyüyünce baskı artar” yönünün tersinedir. Bu, 21 çeyreklik kısmi regresyonun işaretidir. Bir karşı-olgu değildir.

## 2021-Q4 ayrıştırması

Örneklemin kur ve rezerv bacakları, 2016-Q2–2025-Q4, 39 çeyrek [HESAP]:

- Kur log farkının standart sapması s_e = 8,04.
- Brüt rezerv yüzde farkının standart sapması s_r = 10,22.
- Ağırlık s_e / s_r = 0,787. Yapısal parametre değildir.

2021-Q4 [HESAP], kur ayağı TCMB aylık ortalama döviz satışının çeyrek ortalaması (SAPMA-kur):

- E = 11,08 TL.
- e = 100 × ln(E_t / E_{t−1}) = 25,97.
- Çeyrek sonu resmi rezerv varlıkları R = 111.181 milyon dolar [VERİ].
- r = −8,31.
- EMP = 25,97 − 0,787 × (−8,31) = 32,51.

SAPMA-taban. Kilitli EMP 32,51 puandır. Bağlamdaki 55 yeniden üretilmedi. Kalıntı da 27–34 değil, 7,61 puandır. Ölçek 55’e çekilmedi.

Taban model, 2020-Q4–2025-Q4, n = 21 [HESAP]. R² = 0,417. 2021-Q4 uydurması 24,89. Kalıntı b = 32,51 − 24,89 = 7,61. |b| ≥ 1 olduğu için %50 eşiği uygulanır.

2021-Q4’te adayların kendi X değerleri:

| Aday | X | Birim | Etiket |
| --- | --- | --- | --- |
| NHN | 6,93 | milyar dolar, kayıtsız çıkış | VERİ → HESAP |
| TAHVIL | 3,27 | milyar dolar, yurt dışı DİBS stok düşüşü | VERİ → HESAP |
| DOLAR | 8,61 | döviz tevdiat / toplam mevduat, puan | VERİ → HESAP |
| KACIS | 0,92 | milyar dolar, diğer sektörlerin mevduat varlık edinimi | VERİ → HESAP |
| ALTIN | −0,72 | milyar dolar, net ithalat eksi (çeyrek net ihracat) | VERİ → HESAP |
| TICARI | −4,01 | milyar dolar, ölçülmüş ticari kredi yükümlülüğü net girişi | VERİ → HESAP |
| VADE | 4,55 | milyar dolar, 1 yıla kalan vadeli stok artışı | VERİ → HESAP |
| POZ | −2,52 | milyar dolar, açık daralması X’i eksi yapar | VERİ → HESAP |
| CDS | 152,4 | puan, çeyrek sonu fark | VEKİL → HESAP |
| BEK | 25,55 | 12 ay sonraki kur beklentisinin log farkı × 100 | VERİ → HESAP |

Adayın katkısı, taban artı aday uydurması eksi taban uydurmasıdır. Ters yönün açıklanan payı 0’dır.

| Aday | Katsayı | Shapley | Uydurma farkı | \|fark\| / \|b\| | Kalıntı |
| --- | --- | --- | --- | --- | --- |
| VADE | −0,70 | %3,0 | −0,35 | 0 | kapanmadı, ters yön |
| POZ | −0,13 | %11,5 | −0,26 | 0 | kapanmadı, ters yön |
| CDS | +0,045 | %28,8 | +0,62 | %8,2 | eşiğin altında |
| BEK | +0,71 | %47,7 | +5,53 | %72,6 | yarısı kapandı |

Dört aday birlikte girince R² = 0,815 [HESAP]. Bu model eşiği değiştirmez. Birlikteyken paylar: BEK %37,8, CDS %22,2, POZ %5,0, VADE %1,1. POZ’un katsayısı birlikte modelde +0,22’ye döner. Hüküm, adayın tek başına girdiği modeldedir. POZ orada eksidir.

Taban modelin kendi Shapley payları, 2020-Q4–2025-Q4 üzerinde, yeniden skor değildir: TAHVIL %61,1, DOLAR %19,9, TICARI %7,6, NHN %6,4, ALTIN %3,2, KACIS %1,8 [HESAP]. 2016-2019 için tutarlı haftalık DİBS serisi olmadığı için bu paylar “2016-2025’te ölçülmüş akım ana kaynak değildir” cümlesinin yerine geçmez.

Üçlü okuma. VADE ve POZ kalıntının yarısını kapatmıyor. BEK kapatıyor, CDS kapatmıyor. Fiyat-önce testi 2021 kümesi için fiyat-önce demiyor. Üçü birden tutmadığı için “2021-Q4 akım değil, fiyat / beklenti sıçramasıdır” okuması BELİRSİZ kalır. BEK’in kalıntıyı kapatması bu okumayı tek başına desteklemez.

## Fiyat önce, akım önce

C2, haftalık yurt dışı yerleşik DİBS stokunun düşüşünü satış sayar. Değer kaybı, ardışık cuma günleri arasında 100 × ln. İkisi de kendi pencere sonu toplamının yarısına ilk kez hangi haftada ulaşıyorsa o hafta kaydedilir. Biri pencere sonunda pozitif değilse yön yok. Aynı hafta, fiyat-önce değildir.

2021-09-01–2022-01-15 [HESAP]. Yirmi hafta. Pencere sonu birikimli değer kaybı 47,78. Pencere sonu birikimli tahvil satışı 3,79 milyar dolar. İkisi de kendi yarısına 19 Kasım 2021 haftasında ulaşır. Sonuç: aynı hafta.

Patika monoton değildir. Birikimli değer kaybı 17 Aralık haftasında 66,81’e çıkar, 24 Aralık haftasında 33,67’ye iner, 14 Ocak 2022’de 47,78’de biter. Tahvil satışı 17 Aralık’ta 3,94 milyar dolara çıkar, 24 Aralık’ta 3,12’ye iner. 22 Ekim’de değer kaybı kendi son toplamının %28’inde, tahvil satışı %37’sindeydi. Yarı çizgisinden önce satışın kendi payı daha ilerideydi. Bu cümle zaman sırasıdır. Faiz indiriminin baskıyı ürettiği yazılmaz.

Günlük satış kuru, 20 Aralık 2021’de 17,50, 21 Aralık’ta 13,05, 23 Aralık’ta 11,47’dir [VERİ]. 24 Aralık’taki birikimli gerileme bu üç güne denk gelir.

2018-07-01–2018-09-30. Haftalık stok yok. C2 DOĞRULANMADI. Aylık arşiv bu pencerenin yerine konmadı.

2023-04-01–2023-06-30 [HESAP]. Pencere sonu değer kaybı 29,88. Pencere sonu tahvil satışı 0,36 milyar dolar. Satış, kendi yarısına 5 Mayıs haftasında ulaşır. Değer kaybı, kendi yarısına 9 Haziran haftasında ulaşır. Sonuç: akım-önce. 19 Mayıs haftasında birikimli satış 0,29’dan 0,12 milyar dolara düşer. Hüküm, ilk yarıya ulaşma haftasına göredir. 0,36 milyar dolarlık son toplam, 2021 penceresindeki 3,79’un yanındadır. Küçük bir stok farkı “önce” sayılmıştır. Bu, seçimin kuru hareket ettirdiği iddiası değildir.

C1, yalnız fiyattır. Önceki beş işlem gününün log farkı toplamı pozitif ve sonraki beş işlem gününün toplamından büyükse o gün “fiyat pencerede önde”dır. 2021’in beş gününden dördü bu koşulu tutar: 23 Eylül, 21 Ekim, 16 Aralık, 20 Aralık. 18 Kasım tutmaz (önce 0,061, sonra 0,193) [HESAP].

23 Eylül’de önceki toplam 0,0244, sonraki 0,0238’dir. Fark küçüktür. Koşul yine de tutar. 16 ve 20 Aralık’ın sonraki pencereleri negatiftir: 16 Aralık penceresi 20 Aralık’taki 17,50’yi ve 21 Aralık’taki 13,05’i birlikte içerir. “Pencerede önde”, sonraki net hareketin daha küçük olmasıdır. Karar gününden sonra kurun hiç oynamadığı anlamına gelmez.

2023 seçim günleri pazardır (SAPMA-secim). 14 Mayıs: önceki 0,0046, sonraki 0,0122. 28 Mayıs: önceki 0,0096, sonraki 0,0438 [HESAP]. İkisi de “fiyat pencerede önde” değildir. C1, C2’nin yerine geçmez. 2023 C2 hükmü akım-öncedir.

## Veri ve kapsam

Sertifika doğrulaması açıktı. `ssl` varsayılan bağlamı kullanıldı. `-k` yok. Günlük kur `https://www.tcmb.gov.tr/kurlar/YYYYMM/DDMMYYYY.xml` adresinden, ForexSelling, USD. 328 iş günü denendi, 308 kur geldi, 20 gün HTTP 404 (tatil). Investing.com 403 aşılmadı. TÜİK ve Binance çağrılmadı. EVDS anahtarı okunmadı.

`evds3.tcmb.gov.tr/igmevdsms-dis` birincil yol değildir. Şu seriler bu uç noktadan alındı ve bu cümleyle yazılır: aylık kur, resmi rezerv, net hata noksan, firma döviz pozisyonu, mevduat, kur beklentisi, ödemeler dengesi alt kalemleri, haftalık yurt dışı menkul kıymet, arşiv DİBS, swap stoku ve ihale faizi. İstatistik sayfasındaki `FKDFDVY2026-07.zip` ve `kv.zip` 2026 anlık tablolarıdır. 2016-2025 paneli bu dosyalarda yoktur.

Kimlikler, katsayıdan bağımsız, tuttu:

- Parasal olmayan altın: ihracat − ithalat = net kalem, bütün aylarda fark 0 [VERİ]. X_ALTIN = −net ihracat.
- Ticari krediler: net = varlık edinimi − yükümlülük oluşumu, fark 0 [VERİ]. X_TICARI = −yükümlülük oluşumu. Kapsam bütün sektörlerdir, yalnız finansal olmayan firma değildir.
- Efektif ve mevduat: diğer sektörler + bankalar = net varlık edinimi, fark 0 [VERİ]. X_KACIS, diğer sektörler satırıdır. Bankaların yabancı para varlık edinimi ayrıca durur, kullanılmadı.
- Net döviz pozisyonu = varlık − yükümlülük, aylık fark en çok 1 milyon dolar [VERİ]. X_POZ = −Δ(net).

VADE stoku = yurt dışından sağlanan kısa vadeli kredi + uzun vadeli dış kredinin 1 yıldan az kalan kısmı + kısa vadeli ithalat borcu + uzun vadeli ithalat borcunun 1 yıldan az kalan kısmı [VERİ]. Yurt içinden kullanılan döviz kredisi bu toplama girmez. X, bu stokun çeyrek farkıdır. Nakit olarak ödenen servis veya gerçekleşen hedge hacmi değildir. Uzun vadeli borcun kalan vadesinin 1 yılın altına inmesi de artı yazar.

TAHVIL, grup adı “Yurt Dışı Yerleşikler Menkul Kıymet Portföyü”, satır “1.1.2. DİBS (Kesin Alım)”, yurt içi piyasa, milyon dolar, haftalık cuma [VERİ]. Eurotahvil satırı bu X’in içinde değildir. Arşiv “Yurt Dışı Elinde Tutanlar” ile ay sonu farkının ortancası %25,7’dir. 2021-Q1 ve 2021-Q2 çeyrek farklarının işareti iki seride uyuşmaz. Eklenmedi (SAPMA-tahvil-ek). İlk TAHVIL farkı 2020-Q4’tür. Ortak örneklem bu yüzden 21 çeyrektir.

CDS, `AliAltintas64/Empirical-Analysis-of-Turkeys-Sovereign-CDS-Spreads` deposundaki `cds-thesis-replication/data/Turkiye_CDS_Veriseti.csv` dosyasıdır [VEKİL]. Haftalık cuma, 2010-01-01–2025-12-26, 835 satır, eksik hafta yok. Dosyada negatif değer yok. 2021-03-26 değeri 451,335’tir. Derleyicinin README’si, o haftaki negatifi bu sayıyla değiştirdiğini yazar. Bu çalışmada dosya değiştirilmedi. 2021-Q4 farkı 24 Eylül 410,6 ile 31 Aralık 562,975 arasındadır. Mart düzeltmesi bu farkın içinde değildir. 2021-Q1 sonu olduğu için 2021-Q2 farkının tabanındadır.

Kur beklentisi, Piyasa Katılımcıları Anketi uygun ortalaması, 12 ay sonrası bankalararası USD/TRY [VERİ]. Çeyrek değeri üç ayın ortalamasıdır, sonra 100 × ln.

Swap. BIST swap stoku yan sütundur: 2021-09 sonunda 9.542 milyon dolar, 2021-12 sonunda 3.807 milyon dolar [VERİ]. 2023-05 ve 2023-06 stoku 0. İşaret konmadığı için Shapley’e girmedi. `TP.FXSWAP05` TCMB döviz karşılığı TL swap ihalesinin TL faizidir. 2018-01–2025-12 arasında 15 ay doludur. Offshore zımni TL faizi değildir. X_SWAP kurulmadı.

Çevirme oranı. Katalogda rollover veya çevirme zaman serisi yok. `kv.zip` Ağustos 2026 kalan vade anlığıdır. DOĞRULANMADI.

NHN ile ticari kredi X’inin korelasyonu, 39 çeyrekte 0,05 [HESAP]. NHN ile TAHVIL, 21 çeyrekte −0,00 [HESAP]. Bağlamdaki 0,33–0,36 ve 0,46 bu hesapta çıkmadı. O katsayılar girdi yapılmadı.

## Zayıf noktalar

1. Kilitli EMP 32,51’dir. Bağlamdaki 55 ve 27–34 bu dosyada yoktur. Aynı nesne oldukları gösterilemez.
2. Tutarlı tahvil stoku 2020-Q4’te başlar. Taban, aday ve kayan test 21 çeyrektir. 2016-Q2–2020-Q3 tahvil akımı hükme girmez. Kayan pencere 6 olduğu için %60 çubuğu hiçbir adayda geçmiş sayılmaz. BEK’in payı ve işareti tutsa da ana kaynak yazılmaz.
3. Yirmi bir gözlemde taban altı, adayla yedi, birlikte modelde on açıklayıcı vardır. POZ’un işareti tek başına girince eksi, dördü birlikte girince artıdır. Paylar bu örnekleme bağlıdır.
4. 2021-Q4’te spot log farkı 25,97, beklenti log farkı 25,55’tir. Anket aynı çeyreğin kurunu görür. BEK’in kalıntıyı %72,6 kapatması, beklentinin fiyattan önce geldiğini ayırmaz.
5. C2 yarı çizgisi, pencere sonu toplama göredir. 2021 patikası 17 Aralık’ta tepe yapıp 21 Aralık’tan sonra geri gelir. Aynı hafta hükmü bu tanımdadır.
6. 2023’te akım-önce, 0,36 milyar dolarlık satış toplamına göredir. Satış Mayıs ortasında geri gelir. Büyük bir çıkışın fiyatı öncelediği bu sayıdan çıkmaz.
7. C1 pencereleri örtüşür. 16 Aralık’ın sonraki beş günü, 20 Aralık’ı içerir. Beş gün bağımsız beş deney değildir. 23 Eylül’ün iki toplamı birbirine yakındır.
8. VADE nakit servis değildir. Çevirme oranı bulunamadığı için “borç çevrilemedi” cümlesi kurulamaz.
9. TICARI ve KACIS, firma hedge tablosundan daha geniştir.
10. CDS resmi bir TCMB veya Hazine serisi değildir. Bir gözlem derleyicinin düzeltmesini taşır.
11. Ağırlık, brüt resmi rezerv varlıkların örneklem standart sapmasındadır. Swap hariç net rezerv EMP’ye konmadı.
12. Hiçbir test karşı-olgulu değildir. Uydurma farkı, “aday olmasaydı EMP şu olurdu” diye okunmaz.
