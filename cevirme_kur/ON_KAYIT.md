# Ön kayıt — dış borç çevirme oranı kur baskısını öncelemeli mi?

Yazım zamanı (UTC): 2026-10-20T12:56:49Z

Bu dosya, çevirme oranı, EMP ve kontrol serileri indirilmeden ve her türlü Granger, yerel izdüşüm, kayan pencere ve epizot sayımından önce yazıldı. Eşikler skor görüldükten sonra değiştirilmez. Uygulama ayrılırsa satır SAPMA diye işaretlenir.

Kullanıcının kutu testi (2/3 epizotta zaman uyumu, 2021 Ekim banka %42 / firma %66, 2023 Nisan firma %44, yanlış alarm Kasım 2022 ve Eylül 2018, yıllık test iki yönde de anlamsız, hüküm BELİRSİZ) bu yazım anında çalışma ağacında `rapor.md`, `ON_KAYIT.md` veya `epizot.csv` olarak yoktu. O sayılar hedefin içine konmaz. Eşik, o aylara uysun diye seçilmez.

## Hüküm

Hipotez [aday]: bankaların ve diğer sektörlerin dış borç çevirme oranındaki düşüş, kur piyasası baskısını en az bir ay öncelemelidir.

Hüküm ancak aşağıdakilerin hepsi tutarsa **Ayakta** yazılır. Bu, karşı-olgusuz bir zaman sırası ve regresyon muhasebesidir. “Çevirme düşünce kur baskısı oluştu” cümlesi kurulmaz.

1. Epizot: kilitli üç pencereden en az ikisinde, baskı ayından 1, 2 veya 3 ay önce alarm vardır.
2. Granger: Holm sonrası, aynı sektörde çevirme EMP’yi Granger anlamda öncelemelidir, gecikme katsayılarının toplamı negatiftir, Holm p < 0,05.
3. Yerel izdüşüm: aynı sektörde, 1, 2 veya 3 ay ufkundan en az birinde katsayı negatiftir ve Holm p < 0,05.
4. Kayan pencere: aynı sektörde tutan pencere / kurulan pencere ≥ 0,60.
5. Ters yön: aynı sektörde EMP → çevirme Granger testi Holm sonrası anlamlı değildir (p ≥ 0,05).

Biri tutmazsa Ayakta yazılmaz. İşaret tam örneklemde Holm sonrası anlamlı ve pozitifse (yüksek çevirme, yüksek baskı) **Yanlışlandı**. Veri yoksa veya çubuklar dağılmışsa **Belirsiz**. Seri yoksa DOĞRULANMADI; sıfır yazılmaz.

Ters yön ayrıca raporlanır. Ters yön anlamlı, düz yön anlamsızsa düz hipotez Yanlışlandı sayılır. İkisi de anlamlıysa Belirsiz.

## Çevirme oranı

Kaynak, ödemeler dengesi ayrıntılı sunum, aylık, milyon ABD doları.

Bankalar, uzun vade:

- Kullanım: `TP.ODEAYRSUNUM6.Q169`
- Geri ödeme: `TP.ODEAYRSUNUM6.Q170`
- Net uzun vade: `TP.ODEAYRSUNUM6.Q168`
- Kısa vade, yalnız net: `TP.ODEAYRSUNUM6.Q167`
- Bankalar krediler net yükümlülük: `TP.ODEAYRSUNUM6.Q166`

Diğer sektörler (finansal olmayan firma diye daraltılamaz; yayımlı satır diğer sektörlerdir):

- Kullanım: `TP.ODEAYRSUNUM6.Q182`
- Geri ödeme: `TP.ODEAYRSUNUM6.Q183`
- Net uzun vade: `TP.ODEAYRSUNUM6.Q181`
- Kısa vade, yalnız net: `TP.ODEAYRSUNUM6.Q180`
- Diğer sektörler net yükümlülük: `TP.ODEAYRSUNUM6.Q179`

İşaret, katsayıdan önce kimlikle kurulur. Bütün aylarda bakılır.

- Uzun vade: `Q168 = Q169 + Q170` veya `Q168 = Q169 − Q170`. Hangisi mutlak hatayı en çok 1 milyon dolarda tutarsa o kullanılır. İkisi de tutmazsa uzun vade oranı DOĞRULANMADI.
- Kısa vade: `Q166 = Q167 + Q168` ve `Q179 = Q180 + Q181` en çok 1 milyon dolar sapmayla tutarsa, kısa vade net yükümlülük oluşumudur. Pozitif = net borçlanma. Tutmazsa kısa vade DOĞRULANMADI, birleşik oran kurulmaz.

Geri ödeme paydada pozitif tutar olur. Seri negatif saklanmışsa mutlak değer alınır. Kullanım, kimliğin çizdiği işaretle pozitif tutara çevrilir. Payda ≤ 0 ise o ay eksiktir, sıfır yazılmaz.

Uzun vade oranı, 12 ay:

`100 × toplam(kullanım, 12 ay) / toplam(geri ödeme, 12 ay)`

3 ay aynı formül, pencere 3. Aylık ham oran da yazılır, hükme girmez. Hükümdeki oran 12 aydır. 3 ay aynı kurallarla ayrıca sayılır, Holm ailesine girmez, Ayakta hükmünü değiştirmez.

Birleşik oran, kullanıcının “uzun vade kullanım/geri ödeme artı kısa vade net akım” cümlesidir [HESAP]:

- Pay = uzun vade kullanımı + kısa vade netinin pozitif kısmı
- Payda = uzun vade geri ödemesi + kısa vade netinin negatif kısmının mutlak değeri
- 12 aylık toplamlar üzerinden 100 × pay / payda

Kısa vade kimliği tutmazsa birleşik oran DOĞRULANMADI. O zaman tam hipotez Ayakta olamaz. Uzun vade oranı yine hesaplanır ve “eksik hipotez” diye yazılır.

Yayımlı `TP.ODEROLL.K1` (bankalar) ve `TP.ODEROLL.K2` (diğer sektörler) kontrol serisidir, hükmün yerine geçmez. Örtüşmede medyan mutlak fark 5 puandan küçükse, hesaplanan oranın başlamadığı 2008 sonrası aylar yayımlı oranla uzatılabilir; bu satır SAPMA-ek diye yazılır. Fark büyükse eklenmez.

Örnek: 2008-01’den 2026’nın son dolu ayına. Eksik ay doldurulmaz. 12 aylık oran, ilk 11 akım ayından sonra başlar.

## EMP

Çeyreklik EMP, PR #38 `emp_bosluk/ON_KAYIT.md` ile aynıdır. Bu dalda o dosya yoksa formül buraya kopyalanmıştır, değiştirilmemiştir.

- Örnek: 2016-Q2–2025-Q4. 2026 çeyreği yok.
- E: TCMB USD/TRY döviz satış kuru. Çeyrek, aylık ortalama satışın (`TP.DK.USD.S.YTL`) üç ay ortalamasıdır. Günlük kurların ortalaması değildir. Bu, PR #38’deki SAPMA-kur’dur.
- R: çeyrek sonu brüt resmi rezerv varlıkları, `TP.REZVARPD.K1`, milyon dolar. Swap hariç net konmaz.
- e = 100 × ln(E_t / E_{t−1}), r = 100 × (R_t − R_{t−1}) / R_{t−1}
- s_e, s_r: bu iki dizinin 2016-Q2–2025-Q4 örneklem standart sapması, payda n−1
- EMP = e − (s_e / s_r) × r
- Pozitif EMP, değer kaybı yönünde baskıdır. 2021-Q4 negatifse işaret çevrilmez.

Aylık test için aynı formül aya uygulanır. SAPMA-frekans. Hipotez ay önderliği istediği için Granger ve epizot aylık EMP üzerindedir. Çeyreklik seri yalnız mutabakat içindir, Granger’a girmez.

Aylık E, `TP.DK.USD.S.YTL` ay ortalamasıdır. Aylık R, ay sonu `TP.REZVARPD.K1`’dir. s_e ve s_r, aylık e ve r’nin 2008-01–2026 son dolu ay örnekleminden, EMP’nin kurulduğu aylardan, payda n−1 ile hesaplanır. Ağırlık [HESAP], yapısal değildir.

## Mutabakat (hüküm çubuğu değil)

Üç sayı yan yana yazılır. Biri 55’e çekilmez.

1. Bu formülle 2021-Q4 çeyreklik EMP. PR #38’de bu tanım 32,51 ve ağırlık 0,787 vermişti. Bu turda fark 0,1 puandan büyükse SAPMA-emp yazılır, eski sayı silinmez.
2. Kullanıcının 55’i. Formülü bu yazımda yok. Ölçeklenmez. Ayrıca, aynı rezerv ve aynı ağırlık kuralıyla, kur ayağı çeyrek sonu ayının satış kuru yapılarak bir varyant daha yazılır. O da 55 değilse, 55 DOĞRULANMADI kalır.
3. FRED ağırlığı 0,539. FRED’den ABD doları başına ulusal para, aylık `CCUSSP02TRM650N`, ve altın hariç rezerv `TRESEGTRM052N` indirilir. Aynı çeyrek formülüyle ağırlık hesaplanır, 0,539 ile karşılaştırılır. İndirme olmazsa FRED ağırlığı DOĞRULANMADI. Ayrıca bizim e ve r üzerine, yeniden tahmin edilmeden, ağırlık 0,539 konur. Bu sütun [VEKİL], “kullanıcının söylediği ağırlık”dır, FRED tahmini diye yazılmaz.

## Epizot ve alarm

Baskı pencereleri, çevirme görülmeden kilitli:

- 2018: 2018-07, 2018-08, 2018-09
- 2021: 2021-09, 2021-10, 2021-11, 2021-12
- 2023: 2023-05, 2023-06

Baskı ayı, pencere içinde aylık EMP’si en yüksek olan aydır. Eşitlikte erken ay alınır.

Alarm, 12 aylık birleşik oran için, bir sektörde:

- oran < 100, ve
- oran, üç ay önceki kendi değerinden en az 15 puan düşüktür.

Öncülük: baskı ayının 1, 2 veya 3 ay öncesinde o sektörde alarm varsa, o sektör epizotu önden tutmuştur. Baskı ayının kendisi öncülük sayılmaz.

Epizot tutması: banka veya diğer sektör tutmuşsa. Üçten en az ikisi gerekir.

Yanlış alarm: bir ayda banka veya diğer sektör alarm verir, ve o ay hiçbir epizot penceresinde değildir, baskı ayının önceki üç ayında da değildir. Aylar tekleştirilir. İsabet = tutan epizot sayısı / (tutan epizot sayısı + yanlış alarm ayı sayısı). Bu oran hükme ek eşik değildir. Sayılır ve yazılır.

3 aylık oran için aynı alarm kuralı ayrıca sayılır, hükmü değiştirmez.

## Granger, yerel izdüşüm, Holm

Aylık. Liste bazında silme. n < 48 ise o test DOĞRULANMADI.

Kontroller, çağdaş değil, 1–3 gecikme: politika faizi farkı, CDS farkı, DXY’nin 100 × log farkı, ABD 2 yıl faizinin farkı.

- Politika faizi: `TP.BISPOLFAIZ.TUR`, ay sonu veya ayın yayımlı değeri, yüzde puan. Seri yoksa veya 2008’i kapsamazsa `TP.APIFON4` iş günü ortalamasının ay ortalaması, SAPMA-faiz.
- CDS: haftalık yayımlı resmi TCMB serisi yoksa, önceki turdaki öğrenci derlemesi haftalık Türkiye 5 yıl CDS, ayın son cuması, [VEKİL]. Dosya değiştirilmez.
- DXY: FRED `DTWEXBGS`, aylık ortalama, geniş nominal dolar. İndirme olmazsa DOĞRULANMADI, kontrol düşürülmez, kontrollü test DOĞRULANMADI.
- ABD faizi: FRED `DGS2`, aylık ortalama. İndirme olmazsa CDS dosyasındaki US10Y [VEKİL], SAPMA-abd, ve bu düşüş yazılır. O düşüş, kontrollü testi ayakta tutmaya yetmez: SAPMA-abd olursa ABD kontrolü vekildir, test yine yapılır, etiket [VEKİL] olur.

EMP denklemi:

EMP_t = sabit + EMP’nin 3 gecikmesi + çevirmenin 3 gecikmesi + kontrollerin 3’er gecikmesi + hata

Granger: çevirmenin üç gecikme katsayısı birlikte sıfır. Wald, Newey-West, Bartlett, bant 3. p, ki-kare, serbestlik 3. Doğru işaret: üç katsayının toplamı negatiftir.

Yerel izdüşüm, ufuk h = 1, 2, 3:

EMP_t = sabit + d × çevirme_{t−h} + EMP’nin 3 gecikmesi + kontrollerin 3’er gecikmesi + hata

d’nin standart hatası aynı Newey-West. p, iki taraflı Student-t, serbestlik n − parametre sayısı. Doğru işaret d < 0.

Ters Granger: çevirme denkleminde EMP’nin üç gecikmesi birlikte sıfır. Aynı HAC. İşaret bu çubukta aranmaz. Yalnız anlamlılık.

Holm ailesi, 10 test, eşit:

1. Banka, çevirme → EMP
2. Diğer sektör, çevirme → EMP
3. Banka, EMP → çevirme
4. Diğer sektör, EMP → çevirme
5–7. Banka, yerel izdüşüm h = 1, 2, 3
8–10. Diğer sektör, yerel izdüşüm h = 1, 2, 3

Holm: p’ler küçükten büyüğe. Sırada j (1’den başlar), m = 10, ayarlı p_j = min(1, max_{i≤j} (m−i+1) × p_i). Ayarlı p < 0,05 anlamlıdır. Aile skor görüldükten sonra daraltılmaz.

## Kayan pencere

60 ay, adım 1. Pencerede aynı kontrollü Granger. Pencere, katsayı toplamı negatif ve Wald p < 0,05 ise tutar. Holm pencere içine uygulanmaz. Kurulan pencere 8’den azsa kayan test DOĞRULANMADI, geçmiş sayılmaz. Tekil pencere tutmaz, paydadan düşmez.

## Veri yolu

`EVDS_API_KEY` ortam değişkeni kullanılacak, değeri yazılmayacak, kopyalanmayacak, hata metninden silinecek. Bu yazım anında değişken ortamda yoktu. Anahtarlı `evds2` çağrısı ancak değişken doluysa yapılır.

Değişken yoksa seriler `evds3.tcmb.gov.tr/igmevdsms-dis` üzerinden alınabilir. Bu uç birincil yol değildir. Kullanılırsa raporda seri seri yazılır. İç portlet yok. Sertifika doğrulaması atlanmaz. TÜİK 403, Binance 451, Investing 403 aşılmaz.

FRED csv herkese açık adresten, anahtarsız, sertifika açık. Olmazsa uydurulmaz.

## Etiket

VERİ kaynak tablosu. VEKİL başka kapsam veya derleme. HESAP bu dosyadaki formül. TAHMİN açık varsayım. DOĞRULANMADI bulunamayan. Kanıt, Ayakta hükmünün tuttuğu çubuktur. Aday, tutmayan veya henüz karşı-olgusuz olandır. Ayakta olsa bile karşı-olgu yoktur. Bu nedenle Ayakta, “neden budur” diye okunmaz.
