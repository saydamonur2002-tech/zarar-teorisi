# Ön kayıt — seçim ekonomisi

Yazım zamanı (UTC): 2026-10-20T13:35:47Z

Bu dosya, seçim pencereleri, plasebo ve regresyon hesaplanmadan önce yazıldı. Katalogdaki seri adları bilinir. Eşikler skor görüldükten sonra değiştirilmez. Ayrılış SAPMA diye yazılır.

Ekli kutu testi (FRED EMP, ağırlık 0,568; OECD gecelik faiz; H1 BELİRSİZ, H2 YANLIŞLANDI, faiz artışı p 0,022 / Holm 0,088 aday, H3 uymuyor) girdi değildir. O p değerleri hedef yapılmaz.

Kutu dosyası plaseboyu 1000 tekrar diye yazar. Bu görev 2000 tekrar ister. SAPMA-plasebo: tekrar sayısı 2000’dir. Yüzde 90 ve p 0,05 eşikleri kaymaz.

## Olaylar

Ay, seçimin yapıldığı takvim ayıdır. İkinci tur aynı aydaysa yeni olay açılmaz.

| Tür | Ay |
| --- | --- |
| Genel | 2002-11, 2007-07, 2011-06, 2015-06, 2015-11, 2018-06, 2023-05 |
| Yerel | 2004-03, 2009-03, 2014-03, 2019-03, 2024-03 |
| Referandum | 2010-09, 2017-04 |

H1 ve H2 çubuğu yalnız genel seçimlerdedir. Yedi genel seçim vardır. Üçte iki, en az 5/7 demektir. Verisi olan genel seçim 6’dan azsa o gösterge için çubuk DOĞRULANMADI.

Yerel ve referandum tabloda durur, 5/7 paydasına girmez.

2015 Haziran ve Kasım arası beş aydır. Gerçek takvim böyle kalır. Plasebo takvimleri olaylar arasında en az 12 ay bırakır. Bu, kutu kaydındaki kuraldır. SAPMA-2015: plasebo, gerçek 2015 çiftinden daha seyrektir. Eşik kaymaz.

## Pencereler

Seçim ayı 0’dır. Öncesi [−6, −1]. Sonrası [+1, +6]. Olay incelemesi [−12, +12], ay ay ortalama. Seçim ayı iki pencerenin dışındadır.

Taban: hiçbir kilitli olayın (genel, yerel, referandum) ±12 ayı içinde olmayan aylar.

## EMP

Birincil aylık EMP, PR #38 formülünün aya uygulanmasıdır. SAPMA-frekans. Çeyreklik seri olay testine girmez. Mutabakat için ayrıca kurulur.

- E: `TP.DK.USD.S.YTL`, ayın ortalama döviz satış kuru.
- R: `TP.REZVARPD.K1`, ay sonu brüt resmi rezerv varlıkları, milyon dolar. Swap hariç net, birincil EMP’nin rezerv bacağı değildir.
- e = 100 × ln(E_t / E_{t−1})
- r = 100 × (R_t − R_{t−1}) / R_{t−1}
- s_e, s_r: 2002-01’den son dolu aya, EMP’si kurulan ayların örneklem standart sapması, payda n−1.
- EMP = e − (s_e / s_r) × r
- Pozitif EMP, değer kaybı yönünde baskıdır.

Ay sonu varyantı: E, o ayın son iş günündeki TCMB döviz satış kurudur (`tcmb.gov.tr/kurlar`). R aynı brüt rezervdir. Ağırlık bu e ve r’den yeniden hesaplanır. H2’nin hükmü birincil EMP’dedir. Ay sonu varyantının havuzlu sonrası−taban işareti birincilin tersi ise H2 Belirsiz kalır.

Mutabakat, hüküm değildir. Çeyreklik PR #38 tanımı (üç aylık ortalama kur, aynı brüt rezerv, 2016-Q2–2025-Q4 ağırlığı) 2021-Q4 için yazılır. Kutu ağırlığı 0,568, bizim e ve r üzerine dayatılır [VEKİL]. 55’e ölçeklenmez.

## Diğer göstergeler

Gevşeme yönü parantezde.

1. Politika faizi, `TP.BISPOLFAIZ.TUR`, aylık fark, puan (negatif = gevşeme). Bu, 1 haftalık repo politika faizidir.
2. Etkin fonlama, `TP.APIFON4` iş günü değerlerinin ay ortalaması, aylık fark, puan (negatif = gevşeme). Koridorun içindeki etkin faizdir.
3. Koridorun taban ve tavanı (gecelik borçlanma ve borç verme) yayımlı aylık seri olarak bulunursa eklenir. Bulunamazsa DOĞRULANMADI, uydurulmaz.
4. Brüt rezerv yüzde değişimi, r (negatif = satış).
5. Swap hariç net rezerv. Aday tanım: analitik bilanço dış varlıklar `TP.AB.A02` eksi toplam döviz yükümlülükleri `TP.AB.A10`. Birim TL ise ayın ortalama dolar satışına bölünür, SAPMA-birim. Swap stoku `TP.SWAPTEKTAR.TOTALSTOKALIMYONLU` milyon dolarsa, swap hariç net = bu net − swap stoku. Birimler aynı para birimine inmezse çıkarma yapılmaz, swap hariç net DOĞRULANMADI. Yüzde değişim (negatif = gevşeme).
6. Arka kapı satış vekili, milyon dolar [HESAP]: −Δ(brüt rezerv) + Δ(swap stoku). Pozitif = brüt rezervdeki düşüş swap çözülmesinden fazla, ya da swap artışı rezervi doldurmuş. Swap serisi yoksa bu vekil DOĞRULANMADI.
7. Faiz hariç bütçe gideri `TP.KB.GID002`. Reel 12 aylık yüzde değişim (pozitif = gevşeme). Reel = nominal / `TP.GENENDEKS.T1` (TÜFE, 2003=100).
8. Cari transferler `TP.KB.GID026`, aynı reel 12 aylık değişim.
9. Personel giderleri `TP.KB.GID003`, aynı.
10. Kredi: `TP.KREHACBS.A1` toplam yurt içi kredi hacmi, 12 aylık nominal yüzde değişim (pozitif = gevşeme).

Bütçe serisi yıl içinde birikiyorsa (ocak düşük, aralık yüksek, ocakta sıfırlanma), ayın akımı yıl içi farktır. Ocak, düzeyin kendisidir. Bu kontrol, seçim istatistiğinden önce yapılır. Birikimli değilse düzey, aylık akım sayılır.

Asgari ücret, emekli maaşı ve memur zammı: ancak bu turda indirilen resmi bir takvim varsa ay ay 0/1 serisi kurulur [VERİ]. Hafızadan tarih yazılmaz. Takvim yoksa DOĞRULANMADI.

KGF: aylık resmi kullanım veya stok bulunursa kredi göstergesinin yanında raporlanır. Yoksa DOĞRULANMADI, sıfır yazılmaz.

EPDK veya BOTAŞ yönetilen enerji fiyatı: aylık değişim serisi inmezse DOĞRULANMADI.

Eksik gösterge Holm ailesinden düşer. Düşüş, p değeri görülmeden, yalnız boş seri yüzünden yapılır.

## H1 — seçim öncesi gevşeme

Her gösterge için, her genel seçimde, öncesi pencerenin ortalaması alınır.

Plasebo: 2000 takvim. Çekirdek 20261020. Her takvimde 7 ay, aralarında en az 12 ay, göstergenin örneklemi içinde. Bir takvim tutmazsa yeniden çekilir. 2000 başarılı takvim yoksa o gösterge DOĞRULANMADI.

Bir seçim, o göstergenin gevşeme yönünde, plasebo olaylarının yüzde 90’ından daha gevşekse “uç”tur. Gösterge, uç genel seçim sayısı / verisi olan genel seçim ≥ 2/3 ise seçim çubuğunu tutar.

Havuz: genel seçimlerin öncesi pencerelerindeki ayların ortalaması eksi taban ortalaması. Tek taraflı plasebo p = (1 + gevşeme yönünde en az bu kadar uç olan plasebo sayısı) / (1 + 2000).

Holm, havuz p’leri üzerindedir. Aile, verisi olan H1 göstergeleridir. Ayarlı p < 0,05 ise havuz çubuğu tutar.

Bir gösterge iki çubuğu da tutarsa o kol desteklenir (kanıt değil, adayın eşiği; karşı-olgu yok).

H1’in bütün hükmü:

- Bir kol iki çubuğu da tutarsa ve kontrollü rakip diye bir şart H1’e konmamışsa, o kol için eşik tutmuş yazılır. H1’in kendisi, para veya rezerv veya maliye kollarından en az biri tutmuşsa ve hiçbiri “ölçülmedi” diye açık değilse Ayakta yazılmaz gene de: Ayakta, karşı-olgu olmadığı için kullanılmaz. Eşik tutan kol “eşik tuttu, aday” diye yazılır.
- Kutudaki dil: maliye ölçülmeden H1 Belirsiz kalmıştı. Burada da ölçülmeyen kol varsa ve hiçbir ölçülen kol iki çubuğu birden tutmuyorsa H1 **Belirsiz**.
- Bütün ölçülen kollar seçim çubuğunu tutmuyorsa ve hepsi ölçülmüşse H1 **Yanlışlandı**.
- Havuz işareti gevşemenin tersi ve Holm sonrası p < 0,05 ise o kol Yanlışlandı.

## H2 — seçim sonrası baskı

Birincil EMP. Sonrası pencere ortalaması eksi taban. Doğru işaret pozitiftir.

Çubuklar: havuz farkı pozitif ve tek taraflı plasebo p < 0,05, Holm sonrası; genel seçimlerin en az 5/7’sinde sonrası ortalama, tabanın üstündedir.

Holm ailesi H2 için iki testtir: EMP sonrası havuzu, politika faizi sonrası havuzu (faiz artışı, pozitif fark). Fonlama faizi üçüncü test olarak aynı aileye girer. Aile skordan önce üçe sabittir. Seri yoksa o test düşer, aile küçülür, bu düşüş p’den önce yazılır.

Rakip: aylık regresyon

EMP_t = sabit + b × Sonrası_t + DXY değişimi + ABD 2 yıl faiz değişimi + VIX değişimi + hata

Sonrası_t, genel seçimin [+1, +6] ayında 1’dir. Kontroller çağdaştır. Newey-West, Bartlett, bant 3. b’nin p’si iki taraflıdır.

DXY = FRED `DTWEXBGS`. ABD 2 yıl = FRED `DGS2`. VIX = FRED `VIXCLS`. Üçü de aylık. İnmezse kontrollü test DOĞRULANMADI. Başka siteden vekil konmaz.

H2 hükmü:

- Havuz doğru işaretli, Holm p < 0,05, en az 5/7 pozitif, ay sonu varyantı aynı işaretli ve kontrollü b pozitif ve p < 0,05 ise eşik tuttu. Karşı-olgu olmadığı için bu “neden seçimdir” değildir. Etiket aday kalır, kanıt yazılmaz.
- Kontrollü b anlamsızlaşırsa veya kontrol inmezse, havuz tutsa bile H2 **Belirsiz**.
- Havuz işareti negatifse H2 **Yanlışlandı**. Bu, kutudaki yanlışlama kapısıdır.
- Ay sonu varyantı ters işaretliyse H2 **Belirsiz**.

Sonrası faiz artışı ayrı satırdır. Holm p < 0,05 ve fark pozitifse eşik tuttu (aday). Holm p ≥ 0,05 ise aday, eşik tutmadı.

## H3 — 2021-Q4, 2023 seçiminin uzun ısınması mı

2023-05’ten 2021-10, 2021-11, 2021-12 ayları 19, 18 ve 17 ay öncedir. Pencere [−20, −17] değildir tek başına. H3 penceresi 2021-10..2021-12 diye kilitlenir. Diğer genel seçimlerde aynı uzaklık [−20, −18] ayıdır.

Politika faizi farkı ve EMP için:

- 2021-Q4 ortalaması, diğer genel seçimlerin [−6, −1] ortalamalarının kendi ortalamasından en fazla bir standart sapma uzaktaysa “büyüklük benzer”.
- Diğer genel seçimlerin en az yarısında [−20, −18] ortalaması, gevşeme yönünde ve 2021-Q4 gevşemesinin en az yarısı kadarsa “başka seçimlerde de var”.
- İkisi birden olursa “uyar”. Biri yoksa “seçim takvimiyle açıklanamaz” (aday). Veri yoksa DOĞRULANMADI.

SAPMA-ytl. Ay sonu kur, `tcmb.gov.tr/kurlar` XML’indedir. 2005-01’den önceki günler eski liradır (örnek: 2002-11-29 satış 1.542.744). Aylık ortalama satış kuru aynı aylarda yeni lira birimindedir (2002-11 ortalama 1,61). Ay sonu kur, 2005-01’den önce 1.000.000’a bölünür. Eşik kaymadı. Bu satır, seçim penceresi ve plasebo hesabından önce yazıldı.

## Veri yolu

`EVDS_API_KEY` bu yazımda ortamda yoktur. Değeri okunmaz, yazılmaz. Anahtarlı uç ancak değişken doluysa kullanılır.

Değişken yoksa seri `evds3.tcmb.gov.tr/igmevdsms-dis` üzerinden alınabilir. Bu uç birincil yol değildir. Kullanılırsa raporda yazılır. Sertifika doğrulaması atlanmaz. TÜİK 403, Binance 451, Investing 403 ve FRED zaman aşımı aşılmaz.

## Etiket

VERİ kaynak tablo. VEKİL başka kapsam veya dayatılan ağırlık. HESAP bu dosyadaki formül. TAHMİN açık varsayım. DOĞRULANMADI bulunamayan. Eşik tutması kanıt değildir. Karşı-olgu yok.
