# Ön kayıt — EMP kaynak boşlukları

Yazım zamanı (UTC): 2026-10-20T11:02:19Z

Bu dosya, firma döviz pozisyonu, CDS, swap, kur beklentisi ve günlük kur serileri indirilmeden ve her türlü katsayı, Shapley ve olay penceresi hesabından önce yazıldı. Eşikler skor görüldükten sonra değiştirilmez. Uygulama ayrılırsa satır SAPMA diye işaretlenir.

Kullanıcının bildirdiği önceki ayrıştırma (NHN Shapley yaklaşık 0,37, tahvil çıkışı yaklaşık 0,26, 2021-Q4’te 55 puanın 27–34’ü açıklanmamış) bu yazım anında çalışma ağacında bir dosya olarak yoktu. O sayılar bu hesabın girdisi yapılmaz, EMP ölçeği onlara uysun diye yeniden ölçeklenmez. Test, aşağıdaki kilitli tanımdan üretilen EMP ve kalıntı üzerinde yapılır. Önceki 55 / 27–34 yalnız bağlamdır; yeniden üretilmezse SAPMA-taban yazılır, uydurulmaz.

## Eşikler (aynen)

Bir aday ölçülmüş akım “ana kaynak”tır, üçü birden tutarsa:

1. Shapley payı ≥ %30.
2. İşaret, aşağıda kilitlenen yöndedir.
3. Kayan pencerelerin ≥ %60’ında (1) ve (2) birlikte tutulur.

Biri tutmazsa o aday ana kaynak diye yazılmaz. İşaret ters ise “yanlışlandı”. Pay veya kayan pencere eşiği tutmazsa “ana kaynak değil”. Seri yoksa DOĞRULANMADI; sıfır yazılmaz.

2021-Q4 kalıntısının ≥ %50’si, adayın katkısıyla ve doğru yönde kapanırsa o aday kalıntıyı açıklamış sayılır. Ters yön katkı, açıklanan paya yazılmaz (pay 0).

## EMP

Örnek: 2016-Q2–2025-Q4, çeyrek. 2026 yok. Son çeyrek eksikse pencere son tam çeyrekte durur, doldurulmaz, SAPMA yazılır.

E, TCMB USD/TRY döviz satış kuru. Çeyrek değeri, çeyrek içindeki iş günü kurlarının aritmetik ortalamasıdır. Günlük kur yoksa aylık ortalamanın çeyrek ortalamasıdır; bu durumda SAPMA-kur.

R, çeyrek sonu brüt resmi rezerv, milyon ABD doları. Swap hariç net, EMP’nin içine konmaz; brüt, baskı tanımının rezerv bacağıdır.

e_t = 100 × ln(E_t / E_{t−1})

r_t = 100 × (R_t − R_{t−1}) / R_{t−1}

s_e ve s_r, bu iki dizinin 2016-Q2–2025-Q4 örneklem standart sapmasıdır (payda n−1). İkisi de sıfırdan büyük olmalıdır.

EMP_t = e_t − (s_e / s_r) × r_t

EMP pozitifse lira üzerinde değer kaybı yönünde baskı vardır. Ağırlık aynı örnekten hesaplanır; yapısal bir parametre değildir, etiket [HESAP]. 2021-Q4 negatif çıkarsa işaret çevrilmez.

## Adaylar ve doğru işaret

Bütün X’ler “baskıyı artıran yön” pozitif olacak biçimde kurulur. Doğru işaret, EMP regresyonunda katsayının pozitif olmasıdır. Yayın tanımı bu işareti kurmaya yetmezse o adayın işareti uydurulmaz, test DOĞRULANMADI.

| Kod | Ne | X |
| --- | --- | --- |
| NHN | Ödemeler dengesi net hata noksan | −NHN (pozitif = kayıtsız çıkış) |
| TAHVIL | Yurt dışı yerleşik devlet iç borçlanma senedi | −net alım (pozitif = satış / çıkış) |
| DOLAR | Dolarizasyon, döviz mevduatı / toplam mevduat | çeyrek farkı, puan |
| KACIS | Yurt içi yerleşiklerin yurt dışı mevduatı veya bankaların yurt dışı muhabir dövizi, hangisi yayımlıysa | artış, milyar dolar |
| ALTIN | Net altın ithalatı | pozitif = net ithalat, milyar dolar |
| TICARI | Firma ticaret kredisi, ölçülmüş | −net giriş |
| VADE | Finansal kesim dışı firmaların 1 yıla kadar kalan vadeli döviz borcu | stok artışı, milyar dolar |
| POZ | Aynı firmaların net döviz pozisyonu (varlık − yükümlülük) | −Δpozisyon (açık büyüyünce pozitif) |
| CDS | Türkiye 5 yıl CDS | çeyrek farkı, puan |
| BEK | TCMB Piyasa Katılımcıları Anketi, 12 ay sonrası USD/TRY beklentisi | beklentinin log farkı × 100 |

VADE ve POZ bu turun yeni firma adaylarıdır. CDS ve BEK, 2021-Q4 kalıntı adaylarıdır. NHN, TAHVIL, DOLAR, KACIS, ALTIN, TICARI taban kümedir; önceki turun “ölçülmüş akım ana kaynak değil” cümlesi bu dosyada yeniden skorlanmaz, yalnız kalıntıyı kurmak için yeniden hesaplanır.

Kripto ve varlık fiyatı bu tura eklenmez; önceki turda elenmişler, yeni veri boşluğu değiller.

Swap hacmi (BIST veya TCMB swap cirosu) işaretli bir baskı kaynağı yapılmaz. Hacim iki yöne de şişer. Offshore TL faizi veya yurt dışı−yurt içi TL faiz farkı yayımlıysa X_SWAP = farkın çeyrek ortalaması, doğru işaret pozitiftir (offshore TL faizi yurt içine göre yüksekse baskı adayı). Fark yayımlı değilse fiyattan tersine mühendislik yapılmaz; swap fiyat testi DOĞRULANMADI. Hacim yan sütundur, Shapley’e girmez.

## Shapley

EMP, sabit terim ve eldeki X’ler üzerine doğrusal regresyon. Shapley, R²’nin sıralama ortalamasıdır: her değişkenin marjinal R² katkısı, bütün sıralarda eşit ağırlıkla ortalanır. Pay = φ / R². R² ≤ 0 ise pay yazılmaz.

Ana kaynak hükmü, yeni adaylar (VADE, POZ, CDS, BEK, varsa SWAP) için, taban küme artı o adayın birlikte girdiği modelde verilir. Adaylar tek tek girer; bir de dördü birlikte girer, o model ayrıca yazılır, eşiği tek tek olan değiştirmez.

Kayan pencere: 16 çeyrek, adım 1. Pencerede aynı regresyon. Pencere, pay ≥ %30 ve katsayı pozitifse “tutar”. Tutan pencere sayısı / kurulan pencere sayısı ≥ 0,60 ise kayan eşik tutulur. Kurulan pencere sayısı 8’den azsa kayan test DOĞRULANMADI, geçmiş sayılmaz. Tekil pencere “tutmaz” diye sayılır, atlanır ama paydadan da düşmez.

## 2021-Q4 kalıntısı

Taban model: EMP üzerine sabit + taban küme (elde olanlar). Kalıntı b = EMP − uydurulmuş taban, 2021-Q4.

Adayın katkısı, taban artı aday modelinin 2021-Q4 uydurması eksi taban uydurmasıdır. Bu fark, b ile aynı işaretliyse ve |fark| / |b| ≥ 0,50 ise kalıntının en az yarısı kapanmış sayılır. |b| < 1 puan ise test “kalıntı yok” diye yazılır, %50 uygulanmaz.

Bu iki uydurma bir karşı-olgudur diye adlandırılmaz. Cümle: “doğrusal uydurmanın muhasebesi” [HESAP].

2021-Q4’ün “akım değil, fiyat / beklenti” okuması ancak üçü birden olursa desteklenmiş sayılır:

- VADE ve POZ, kalıntının %50’sini kapatmaz (ikisi de).
- CDS veya BEK, kalıntının ≥ %50’sini doğru yönde kapatır.
- Aşağıdaki fiyat-önce testi, 2021 kümesi için fiyat-önce der.

Biri eksikse bu okuma BELİRSİZ. VADE veya POZ kalıntının ≥ %50’sini kapatırsa “akım değil” cümlesi o ölçülmüş firma kalemi için yanlışlanır. CDS ve BEK ikisi de %50’nin altında kalır ve firma da kapatmazsa kalıntı açıklanmamış kalır; okuma desteklenmez.

## Fiyat önce, akım önce

Olay günleri, skor öncesi kilitli. Yeni gün eklenmez.

- 2021: 23 Eylül, 21 Ekim, 18 Kasım, 16 Aralık (faiz kararları), 20 Aralık (KKM).
- 2023 seçim: 14 Mayıs ve 28 Mayıs 2023.
- 2018-Q3: tek gün kilitlenmedi. O çeyrek, haftalık zaman testi için ayrı penceredir. 10 Ağustos sonradan eklenmez.

Gün 0, ilan takvim günüdür. TCMB kuru gün sonu satış kuruysa gün kaydırılmaz.

C1, yalnız fiyat. Her olay için işlem günü log farkları: önceki 5 işlem günü toplamı ile olay günü dahil sonraki 5 işlem günü toplamı. Önceki toplam pozitif ve sonraki toplamdan büyükse o olay “fiyat pencerede önde”. 2021’in beş gününün çoğunluğu böyleyse 2021 kümesi “fiyat pencerede önde”. 2023 iki günü ayrı yazılır. Bu, akımla karşılaştırma değildir.

C2, fiyat ile akım. Akım, yurt dışı yerleşik devlet tahvili stokunun haftalık farkıdır; satış pozitiftir. Haftalık stok yoksa C2 DOĞRULANMADI, aylığa indirgenmez.

Pencereler: 2021-09-01–2022-01-15; 2018-07-01–2018-09-30; 2023-04-01–2023-06-30.

Pencere sonunda birikimli değer kaybı ve birikimli tahvil satışı hesaplanır. Değer kaybı, kendi pencere sonu toplamının %50’sine, tahvil satışı kendi %50’sine varmadan ulaşırsa “fiyat-önce”. Tersiyse “akım-önce”. Biri pencere sonunda pozitif değilse o pencere “yön yok”. Bu bir zaman sırasıdır [HESAP]. “Faiz indirimi baskıyı yarattı” cümlesi kurulmaz; karşı-olgu yok.

## Veri yolu

Birincil yol, TCMB istatistik sayfasındaki yayımlanmış dosya ve `tcmb.gov.tr/kurlar` günlük kurudur. `evds3.tcmb.gov.tr/igmevdsms-dis` birincil yol değildir. Bir seri yalnız orada bulunursa kullanılabilir; kullanılan her seri raporda bu cümleyle yazılır. EVDS anahtarı okunmaz. İç portlet yok. Sertifika doğrulaması atlanmaz. TÜİK 403 ve Binance 451 aşılmaz. Sayı uydurulmaz.

Firma serisi yalnız yıllık yayımlanmışsa çeyreğe bölünmez, enterpole edilmez. O test DOĞRULANMADI.

## SAPMA (katsayıdan önce, satır eşlemesi)

SAPMA-kur. EMP’nin kur bacağı, günlük kurların çeyrek ortalaması yerine TCMB aylık ortalama satış kurunun (`TP.DK.USD.S.YTL`) çeyrek içi aritmetik ortalamasıdır. Günlük kur, olay pencerelerinde `tcmb.gov.tr/kurlar` XML’inden ayrıca okunur. Eşik kaymadı.

SAPMA-vade. “1 yıla kadar kalan vadeli döviz borcu” tek satır değildir. Stok = yurt dışından sağlanan kısa vadeli kredi (`TP.FDVY28`) + uzun vadeli dış kredinin vadeye kalanı 1 yıldan az olan kısmı (`TP.FDVY30`) + kısa vadeli ithalat borcu (`TP.FDVY33`) + uzun vadeli ithalat borcunun vadeye kalanı 1 yıldan az olan kısmı (`TP.FDVY35`). Birim milyon dolardan milyar dolara bölünür. X_VADE bu stokun çeyrek farkıdır. Eşik kaymadı.

SAPMA-tahvil. Devlet tahvili, ödemeler dengesi portföy toplamı değil, yurt dışı yerleşiklerin DİBS stokudur (`TP.MKNETHAR.M2`, milyon ABD doları, haftalık). X_TAHVIL = −Δstok / 1000. Eşik kaymadı.

SAPMA-tahvil-ek. Katsayıdan önce, arşiv `TP.DIBS12.NOMINAL.USD` (aylık, 2015-01–2021-08) ile `TP.MKNETHAR.M2` örtüştü. Ay sonu stok farkının mutlak değerinin ortancası %25,7. 2020-Q4–2021-Q2 çeyrek farklarının işareti iki seride uyuşmuyor (2021-Q1 ve 2021-Q2). Eklenmedi, biri diğerinin yerine konmadı. X_TAHVIL yalnız `TP.MKNETHAR.M2` çeyrek sonu stok farkıdır; ilk fark 2020-Q4. Taban kümenin ortak örneklemi bu nedenle 2020-Q4–2025-Q4 (21 çeyrek). Kayan 16 çeyrek pencere sayısı 6’dır. Sekizin altında olduğu için kayan test, yukarıdaki kural gereği DOĞRULANMADI sayılır ve geçmiş yazılmaz. Eşik kaymadı.

SAPMA-secim. Katsayıdan önce. 14 Mayıs 2023 ve 28 Mayıs 2023 pazardır; o günlerde TCMB satış kuru yoktur. C1’de önceki pencere, olay takvim gününden önceki 5 işlem gününün log farklarıdır. Sonraki pencere, olay gününden itibaren ilk 5 işlem gününün log farklarıdır; olay günü işlem günüyse o gün dahildir. Yeni olay günü eklenmez. Eşik kaymadı.

SAPMA-kur-esleme. C2 haftası, menkul kıymet stokunun cuma gününe oturtulur. O cuma TCMB satış kuru yayımlanmamışsa (tatil), o tarihten önceki son yayımlanmış satış kuru kullanılır. Yeni olay günü eklenmez. Eşik kaymadı.

## Etiket

VERİ kaynak tablosu. VEKİL başka kapsamdan türetilmiş. HESAP bu dosyadaki formül. TAHMİN açık varsayım. DOĞRULANMADI bulunamayan; sıfır yazılmaz.
