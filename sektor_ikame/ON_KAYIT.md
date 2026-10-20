# Ön kayıt — sektör ikamesi ve kur baskısı

Yazım zamanı (UTC): 2026-10-20T14:39:31Z

Bu dosya, sektör paneli, RCA, teşvik ve EMP regresyonu hesaplanmadan önce yazıldı. Eşikler skor görüldükten sonra değiştirilmez. Ayrılış SAPMA diye yazılır.

Soru: Yurt içi arz varken ithal girdi veya makine kullanmak, kur baskısının genel sürücüsü müdür ve 2021-Q4’ün nedeni midir? Gaziantep’te üretilen bir malın yurt içinde satılıp aynı malın Adana’dan ithal edilmesi motivasyondur. Tek bir firma veya il çifti bu dosyada kanıt yapılmaz.

Karşı-olgu yok. Eşik tutması “neden budur” cümlesi değildir. Kanıt yazılmaz.

## EMP

Tanım, `emp_bosluk` ön kaydıyla aynıdır. Örnek 2016-Q2–2025-Q4. 2026 yok.

E, `TP.DK.USD.S.YTL` aylık ortalama satış kurunun çeyrek içi aritmetik ortalaması. R, `TP.REZVARPD.K1` çeyrek sonu brüt resmi rezerv. e = 100 × ln(E_t / E_{t−1}). r = 100 × (R_t − R_{t−1}) / R_{t−1}. s_e ve s_r, n−1. EMP = e − (s_e / s_r) × r. Pozitif, değer kaybı yönünde baskıdır. 2021-Q4 yeniden hesaplanır. 32,50’ye ölçeklenmez.

Ay sonu varyantı: E, çeyreğin son ayının ortalama satış kurudur. R aynı brüttür. Ağırlık bu e ve r’den yeniden hesaplanır. Bildirilen 54,7 hedef değildir. Ters işaret çıkarsa çevirilmez.

Aylık EMP, aynı formülün aya uygulanmasıdır. SAPMA-frekans. Aylık test, çeyreklik hükmü değiştirmez. İki frekans ters işaret verirse o aday Belirsiz.

## Adaylar

Üç kilitli nesne ve bir vekil. Vekil, kilitli nesnenin yerine konmaz.

1. **Bağımlılık.** OECD TiVA 2025, ölçü `EXGR_FVA`, birim `PT_EXGR`, Türkiye, karşı taraf dünya, yıllık. Bu, ihracatın yabancı katma değer payıdır. İmalat dilimleri, veri kısıtındaki C ile başlayan faaliyetlerdir. Hepsi iki haneli NACE değildir (örnek C10T12, C13T15). Bu gruplama SAPMA-sektor diye yazılır, iki haneli sanılıp geçilmez. Endeks, dilim paylarının ihracat içindeki ağırlığıyla ortalamasıdır. Ağırlık aynı tablodaki ihracat payıdır. Yoksa eşit ağırlık yazılmaz. Seri inmezse bu aday DOĞRULANMADI. Yıla bölünüp çeyreğe yayılmaz.

2. **İkame edilebilir ithalat.** HS satırında Türkiye’nin RCA’sı 1’in üstündeyse o satırda yurt dışı piyasada arz gücü vardır. RCA = (Türkiye’nin o satır ihracatı / Türkiye toplam ihracatı) / (dünya o satır ihracatı / dünya toplam ihracatı). Taban penceresi 2017–2019 ortalamasıdır. Bu pencerede RCA > 1 olan satırlar kilitlenir. Sonraki yıllar kümeyi yeniden seçmez. İkame payı, bu satırların ithalatı / toplam mal ithalatı. Birim değer, aynı satırda ithalat birim değeri / ihracat birim değeri. Birim değer = değer / net kilogram, net kilo sıfırsa satır düşer. Birim değer Shapley’e girmez. Tanımlayıcıdır.

   Dünya ihracatı, Comtrade’de tek bir “dünya” muhabiri boş dönerse, önceden yazılı muhabir kümesinin ihracat toplamı kullanılır [VEKİL]. Küme: 36, 56, 76, 124, 156, 203, 251, 276, 344, 360, 381, 392, 410, 458, 484, 528, 616, 643, 682, 699, 702, 704, 724, 764, 784, 792, 826, 842. Bu kümenin toplam mal ihracatı, Dünya Bankası dünya mal ihracatının yüzde 70’inin altındaysa RCA adayı DOĞRULANMADI. Yüzde 70 ve üstündeyse vekil diye kalır, kilitli dünya RCA’sı diye yazılmaz.

   HS6 inmezse HS4. HS4 de inmezse HS2. İnce ayrım SAPMA-hs. Çeyreğe yayılmaz. Yıllık seri, 2021-Q4’ün içindeki ayları önden haber veremez.

3. **Teşvikli ithal makine.** Sanayi ve Teknoloji Bakanlığı yatırım teşvik belgelerinde ithal makine-teçhizat, sektör ve yıl. X, ithal makine tutarıdır. Pay (ithal / ithal+yerli) tanımlayıcıdır, Shapley’deki X tutardır. Sayfa açılmaz veya tablo inmezse DOĞRULANMADI. Hafızadan yıl yazılmaz. Yıllık belge, 2021-Q4’ü önden haber veremez.

4. **Vekil endeks, ISIC.** `TP.ITHISICREV4` ve `TP.IHRISICREV4`, imalat 10–33, aylık. Yurt içi üretim değeri inmezse “aynı malın yurt içi arzı” ölçülmez. Vekilde arz izi, aynı ISIC’te ihracatın pozitif olmasıdır [VEKİL]. Bu, Gaziantep-Adana mal eşlemesi değildir.

   Bölüm s, ay t: yoğunluk m_s = ithalat / (ithalat + ihracat). İhracat sıfırsa bölüm o ayda vekile girmez. Endeks = sum m_s × (ithalat_s / imalat ithalatı). Yüksek endeks, ihracatı da olan bölümlerde ithalatın ağır basmasıdır. TiVA payı değildir.

   İkame vekili, ayrı satır: 2017–2019’da ihracatı ithalatından büyük olan imalat bölümlerinin sonraki ithalatı / toplam ithalat. Bu RCA değildir. H1’in kilitli ikame nesnesi tutulmazsa bu satır hükmü kurmaz.

## Sürücü çubuğu

Doğru işaret pozitiftir. Yüksek aday, sonraki EMP’yi yükseltir.

Çeyrek denklem, aday aylık veya çeyreklikse:

EMP_t = sabit + b × X_{t−1} + politika faizi_t + CDS farkı_t + DXY değişimi_t + hata

Faiz, `TP.BISPOLFAIZ.TUR` çeyrek ortalaması, düzey. CDS, çeyrek sonu farkı. DXY, çeyrek log fark × 100. Newey-West, Bartlett, bant 2. Tek taraflı p, b > 0.

Shapley, R²’nin sıralama ortalamasıdır. Pay = φ_X / R². R² ≤ 0 ise pay yazılmaz.

Aday çubuğu tutar, beşi birden olursa:

1. b > 0.
2. Shapley payı ≥ %30.
3. Kayan 16 çeyrek, adım 1. Pencerelerin ≥ %60’ında (1) ve (2) birlikte. Kurulan pencere 8’den azsa kayan test DOĞRULANMADI, geçmiş sayılmaz.
4. Ters yön aynı çubuğu tutmaz. Ters denklem: X_t = sabit + b × EMP_{t−1} + aynı kontroller. Ters de (1)–(3) tutarsa öncülük tek yönlü değildir.
5. Holm. Aile, verisi olup regresyona giren adayların tek taraflı p’leridir. Aile, p görülmeden, boş seriler düştükten sonra sabittir. Ayarlı p < 0,05.

Biri tutmazsa o aday sürücü değildir. b ≤ 0 ise o aday için yön yanlışlanır.

Yıllık aday çeyrek denkleme girmez. Yıllık denklemde EMP, yıl içindeki çeyrek EMP ortalamasıdır. Gecikme bir yıldır. Kayan pencere 8 yıldır. 8 pencere yoksa kayan test DOĞRULANMADI. Yıllık aday, 2021 yılının kendi Q4’ünü önden haber vermiş sayılmaz.

Aylık robustness: aynı formül, bant 3, kayan 36 ay. Çeyreklik hükmü değiştirmez.

Kontrol inmezse o kontrol düşer. Bu düşüş katsayıdan önce yazılır. Üç kontrolden ikisi yoksa kontrollü test DOĞRULANMADI. Kontrolsüz denklem ayrıca yazılır, hükmü kurmaz.

## 2021-Q4

Bu bir neden testi değildir. Karşı-olgu yoktur.

Adayın 2021-Q4 muhasebesi ancak şu dört birlikteyse “eşik tuttu” yazılır:

1. Çeyreklik adayda X_2021-Q3, 2016-Q2–2019-Q4 ortancasının üstündedir. Yıllık adayda bu madde DOĞRULANMADI.
2. b × X_{t−1}, 2021-Q4 EMP’sinin en az %30’u ve pozitiftir. EMP 2021-Q4 sıfıra yakınsa (mutlak değer 1 puandan küçükse) bu madde uygulanmaz.
3. Kur tabanı: 2021-Q4 mal ithalat ödemelerinde, “bağımlı” bölümlerin payı ≥ %30 ve 2017–2019 ortalama payının en az 5 puan üstündedir. Bağımlı bölüm, 2017–2019’da imalat bölümleri arasında ithalat/(ithalat+ihracat) ortancasının üstünde olan ve ihracatı pozitif olan bölümdür. Enerji ve imalat dışı ayrı yazılır. Bu, ithalat faturasının paylaşımıdır [HESAP]. 32,50 puanın paylaşımı diye yazılmaz.
4. Aday, sürücü çubuğunun beşini de tutar.

Dördü birden tutsa da cümle “eşik tuttu, aday”dır. “2021-Q4’ün nedeni budur” yazılmaz.

## Hüküm

H1, genel sürücü.

- Kilitli nesnelerden biri beş çubuğu da tutarsa H1 **Ayakta**. Bu kelime “eşikler tuttu” demektir. Kanıt değildir.
- Ölçülen her kilitli adayda b ≤ 0 ve çeyrek sayısı ≥ 16 ise H1 **Yanlışlandı**.
- Kilitli nesneler inmez, yalnız vekil ölçülürse H1 **Belirsiz**. Vekil kendi çubuğunu tutsa da H1 Ayakta olmaz.
- Diğer haller **Belirsiz**.

H2, 2021-Q4.

- Dört muhasebe maddesi tutarsa **Ayakta** yazılır ve hemen altında neden cümlesinin kurulmadığı belirtilir.
- Katkı ters işaretliyse veya kur tabanında bağımlı pay 2017–2019’un altında kalırsa ve veri varsa **Yanlışlandı**.
- Veri yoksa veya maddeler bölünmüşse **Belirsiz**.

SAPMA, katsayıdan önce. OECD TiVA sorgusu 500 döndü. TiVA adayı DOĞRULANMADI. Bakanlık teşvik adresi reddedildi. Teşvik adayı DOĞRULANMADI. FRED dolar endeksi zaman aşımına uğradı. DXY kontrolü düşer. ISIC serisi 2013-01’de başlar, 2008’de değil. Comtrade dünya muhabiri boştur. 2018’de kümeden inen 25 muhabirin mal ihracatı, Dünya Bankası dünya mal ihracatının %72,8’idir. 124, 699 ve 764 bu turda 429 verdi. Ölçülen pay %70’in üstündedir. RCA, bu kümenin HS2 fasıl ihracatıyla kurulur [VEKİL]. HS4 sayfaları 429’a takıldığı için inmez. SAPMA-hs. Eşik kaymadı.

## Veri yolu

`EVDS_API_KEY` bu yazımda yoktur. Okunmaz. Anahtarlı uç ancak değişken doluysa kullanılır. Değişken yoksa `evds3.tcmb.gov.tr/igmevdsms-dis` kullanılabilir. Kullanılırsa raporda yazılır. Sertifika doğrulaması atlanmaz. TÜİK 403, bakanlık reddi ve FRED zaman aşımı aşılmaz.

## Etiket

VERİ kaynak tablo. VEKİL başka kapsam. HESAP bu dosyadaki formül. TAHMİN açık varsayım. DOĞRULANMADI bulunamayan. Sıfır yazılmaz.
