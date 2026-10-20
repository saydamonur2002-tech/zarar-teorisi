# Ön kayıt — Temmuz 2018 çıpa kopuşunun olay ayrıştırması

Yazım zamanı (UTC): 2026-10-20T16:03:34Z

Bu dosya, günlük kur getirisi, plasebo ve sentetik kontrol hesaplanmadan önce yazıldı. Eşikler skor görüldükten sonra değiştirilmez. Ayrılış SAPMA diye yazılır.

Ekli aylık rapor, kırılmayı 2018-07 diye tarihler. Yüzde 90 güven aralığı 2018-05 ile 2018-09’dur. Bu tarih bu turun girdisidir. Bai-Perron yeniden tahmin edilmez. “2,05’ten 6,73’e” cümlesi, bu turda yeniden üretilmeden hüküm sayısı yapılmaz.

Karşı-olgu, emsal kur farkı ve sentetik kontroldür. İkisi yoksa nedensel cümle kurulmaz. Kanıt yazılmaz.

## Olaylar

İş günü, TCMB’nin döviz satış kuru yayımladığı gündür. Takvim günü iş günü değilse gün 0, sonraki ilk iş günüdür.

Birincil takvim, skor öncesi:

| Kod | Gün 0 | Kaynak |
| --- | --- | --- |
| PPK-05 | 2018-05-23 | TCMB DUY2018-18, faiz duyurusu |
| PPK-06 | 2018-06-07 | TCMB DUY2018-23, faiz duyurusu |
| SECIM | 2018-06-25 | Seçim 24 Haziran 2018 pazar. Gün 0 sonraki iş günü |
| GAZETE | 2018-07-10 | Resmî Gazete 10 Temmuz 2018, sayı 30474. Aynı sayıda 3 sayılı Cumhurbaşkanlığı Kararnamesi (üst kademe atama usulü) ve 9 Temmuz 2018 tarihli 2018/1 sayılı atama kararı |
| PPK-07 | 2018-07-24 | TCMB DUY2018-27, faiz duyurusu |
| OFAC | 2018-08-07 | Federal Register 2018-16874, OFAC listesine ekleme. Metinde Türkiye uyruklu bir kişi vardır |
| CELIK | 2018-08-15 | Federal Register 2018-17703, çelik ithalatını ayarlayan başkanlık belgesi. Metin Türkiye’yi adlandırır |
| PPK-09 | 2018-09-13 | TCMB DUY2018-38, faiz duyurusu |

9 Temmuz ile 10 Temmuz aynı gazete gününe düşer. İkisi ayrı olay diye skorlanmaz. Küme GAZETE’dir. Kararnamenin madde metni bu yazımda PDF’ten okunamadı. “Görev süresi güvencesi kalktı” cümlesi, madde metni okunmadan hüküm gerekçesi yapılmaz.

Mayıs ve Haziran faiz duyuruları, kullanıcının altı olay listesinde yoktu. Güven aralığının içindeler ve TCMB dizininde skor öncesi görüldüler. Aileye girdiler. Gizlenmezler.

Karşılaştırma günleri, günlük testten önce aranır. Arama penceresi kilitlidir: 1–15 Temmuz 2019, 1–15 Kasım 2020, 15–25 Mart 2021. Gün, o aralıktaki Resmî Gazete dizininde “Merkez Bankası” ve atama birlikte geçiyorsa o gündür. Birden fazla gün varsa başkanı adlandıran gün alınır. Hiçbiri yoksa o karşılaştırma DOĞRULANMADI. Ayın kur istatistiğine bakılarak gün seçilmez.

## Pencereler

Günlük getiri, 100 × ln(E_t / E_{t−1}). Pozitif, doların yerel para karşısında değer kazanmasıdır.

±1 penceresi, 100 × ln(E_{+1} / E_{−2}). ±3 penceresi, 100 × ln(E_{+3} / E_{−4}). İş günü kaymasıyla. Uç gün yoksa o pencere boştur, doldurulmaz.

Kalıcılık, gün 0’dan gün +10’a, 100 × ln(E_{+10} / E_{−1}). ±3 getirisi pozitifse, bu birikim ±3 getirisinin en az yarısı ve aynı işaretliyse kalıcıdır.

## Emsal ve sentetik kontrol

Emsaller: Brezilya reali, Güney Afrika randı, Meksika pesosu, Hindistan rupisi, Endonezya rupisi. Kaynak, Fed H.10 tarihsel kurları. H.10 inmezse BIS döviz kuru. İkisi de inmezse karşı-olgu DOĞRULANMADI.

Eşit ağırlık farkı: Türkiye pencere getirisi eksi, o pencerede gözlemi olan emsallerin ortalaması. Emsal dörtten azsa pencere boştur.

Sentetik kontrol: ağırlıklar 2017-01-03 ile 2018-04-30 günlük getirilerinde, sıfırdan küçük değil, toplamı 1, hata kareleri en küçük. Donörler aynı beş emsaldir. Pencere farkı, Türkiye eksi sentetik. Eşit ağırlık ile sentetik işaretleri ters ise o olay Belirsiz.

## Çıpa ayı

g = 24 ay sonrası TÜFE beklentisi, uygun ortalama, eksi 5. Seri `TP.PKAUO.S01.F.U`. EVDS3 kullanılırsa raporda yazılır.

Mayıs–Eylül 2018 içinde Δg en büyük olan ay, çıpa ayıdır. Fark 0,10 puandan küçükse iki ay birden çıpa ayıdır. Olay, gün 0 o aydaysa çıpa ayının içindedir.

## Sürücü çubuğu

Bir 2018 olayı kur penceresinde büyüktür, dördü birden olursa:

1. ±3 eşit ağırlık farkı pozitiftir.
2. Bu fark, plasebo ±3 farklarının en az yüzde 90’ındandır. Holm sonrası tek taraflı p < 0,10.
3. Kalıcılık tutar.
4. Sentetik fark aynı işarettedir. Sentetik kurulamazsa bu madde DOĞRULANMADI ve olay Ayakta olamaz.

Plasebo: 2000 iş günü. Çekirdek 20180724. Havuz, 2016-01-04 ile 2019-12-31, kilitli olayların ±5 iş günü dışında. Tek taraflı p = (1 + en az bu kadar büyük plasebo sayısı) / (1 + 2000).

Holm ailesi, penceresi hesaplanan 2018 olaylarıdır. Karşılaştırma günleri ailede değildir. Aile, p görülmeden sabittir.

Kur sürücüsü, çubuğu tutan olayların ±3 farkı en büyük olanıdır. İkinci olay, birincinin yüzde 80’inden büyükse sürücü paylaşılır. Tek olay iddiası o zaman Belirsizdir.

Çıpa sürücüsü, kur sürücüsünün çıpa ayının içinde olmasıdır. Değilse o olay çıpayı taşımıyor diye yazılır.

## Hipotezler

H-kurum. GAZETE kümesi çıpa sürücüsüdür ve ±3 farkı, bulunan her karşılaştırma gününün ±3 farkından büyüktür (aynı yön, değer kaybı).

H-faiz. PPK-07 çıpa sürücüsüdür. 24 Temmuz kararı, metinden okunan faizdir. Anket sürprizi ayrıca tanımlanır. Sürpriz = karar faizi eksi `TP.PKAUO.S04.C.U` (ilk toplantı beklentisi), aynı ay. Anketin toplantıdan önce toplandığı birincil not yoksa sürpriz hükümden çıkar, DOĞRULANMADI. Kur penceresi durur.

H-yaptirim. OFAC veya CELIK çıpa sürücüsüdür. İkisi de çubuğu tutar ve birbirinin yüzde 80’inden büyükse yaptırım paylaşılan sürücüdür.

H-secim. SECIM çıpa sürücüsüdür.

PPK-05, PPK-06 ve PPK-09 ailede skorlanır. PPK-09’un beklenen kur işareti, büyük artışta değerlenmedir (eksi getiri). Eksi ve plasebonun en küçük yüzde 10’undaysa “artış penceresi değerlenme” diye yazılır. Bu, kopuşu taşımak değildir.

Hüküm:

- Çubukların hepsi ve hipotezin kendi şartı tutarsa **Ayakta**. Bu kelime eşik tuttu demektir. Neden cümlesi kurulmaz.
- Kur penceresi hesaplanmış ve çubuk tutmamışsa o hipotez **Yanlışlandı**.
- Karşı-olgu, anket veya karşılaştırma günü yoksa ve bu yokluk hükmü belirliyorsa **Belirsiz**.

Hiçbir 2018 olayı kur çubuğunu tutmaz ve karşı-olgu varsa, “tek olay kopuşu taşır” cümlesi Yanlışlandı. Kopuş o zaman bu pencerelerin toplamıdır, tek güne indirgenmez.

## Ölçülmeyenler

Beş yıl CDS’in birincil serisi bu yazımda yoktur. Hükme girmez. DOĞRULANMADI.

DİBS eğrisi, EVDS’de tek tek tahvil fiyatıdır. Sabit vadeli gösterge serisi yoktur. Eğri bu turda kurulmaz. DOĞRULANMADI. Uydurma getiri yazılmaz.

Medya manşeti ve haber rakamı kullanılmaz. Kullanılırsa İKİNCİL diye işaretlenir ve hükümden çıkar.

SAPMA-emsal. Katsayıdan önce. Endonezya H.10 dosyası `dat00_id` 404 verdi. Brezilya, Güney Afrika, Meksika ve Hindistan indi. Beşin dördü var. Bir emsalin tatili, Türkiye iş günüyle çakışmazsa o emsal o pencereden düşer. Pencerede en az üç emsalin iki ucu varsa eşit ağırlık kurulur. Üçün altı boştur. Eşik kaymadı.

## Veri yolu

`EVDS_API_KEY` okunmaz. Anahtar yoksa `evds3.tcmb.gov.tr/igmevdsms-dis` kullanılabilir. Kullanılırsa raporda yazılır. Günlük dolar satışı `tcmb.gov.tr/kurlar`. Sertifika doğrulaması atlanmaz. Site reddi aşılmaz.

## Etiket

VERİ kaynak metin veya tablo. VEKİL başka kapsam. HESAP bu dosyadaki formül. TAHMİN açık varsayım. DOĞRULANMADI bulunamayan. İKİNCİL haber veya derleme. Sıfır yazılmaz.

## SAPMA — skordan sonra, eşik değişmedi

Yazım: 2026-10-20T16:16:55Z. Çubuklar ve hipotez tanımları yukarıdaki metindedir. Yeniden tahmin yok.

SAPMA-plasebo. Ön kayıt paydası 1+2000 idi. Çekirdek 20180724 ile 2000 iş günü çekildi. Bunların 823’ünde ±3 eşit ağırlık farkı kurulabildi. p = (1 + en az bu kadar büyük plasebo sayısı) / (1 + 823). Bu dağılımın yüzde 90 eşiği 3,06’dır. Yüzde 90 ve Holm sonrası p < 0,10 şartı kaymadı.

SAPMA-arama. Karşılaştırma kodu, kilitli pencerelerde sayfanın tüm metninde “merkez bank” ve “atan” aradı. Bu eşleşme, döviz kuru ekinin bulunduğu günleri de tuttu. Aynı pencerelerin dizin bağlantıları yeniden okundu. Merkez Bankası başkanını adlandıran bağlantı yok. Bu günler karşılaştırma günü sayılmadı. `sonuclar.json` içindeki karşılaştırma kur sayıları hükme girmez. Sayfa düzeyi eşleşmeler, plasebo havuzundan ±5 iş günü düşmüştü. 2018 olay pencereleri bu günlere uzaktır. Havuz yeniden çekilmedi.

## Ek — 10 Temmuz çelişkisi ve görevden alma metinleri

Yazım zamanı (UTC): 2026-10-20T17:18:44Z

Bu ek, yeni kur hesabı ve yeni plasebo çekilmeden önce yazıldı. Aşağıdaki eşikler skor görüldükten sonra değiştirilmez. Ayrılış SAPMA diye yazılır. İlk turun çubukları ve H-yaptırım / H-faiz / H-seçim hükümleri bu ekle yeniden açılmaz.

### Karşılaştırılan iki sonuç

İki sayı farklı tahmindir. Biri diğerinin işaret çevrilmiş hali diye baştan kabul edilmez.

Bu dalın ilk turu, 10 Temmuz 2018 için ±3 eşit ağırlık penceresini boş bıraktı. Uç, TCMB iş günüyle 4 Temmuz 2018’dir. Fed H.10’ta o gün kur yoktur. Ham TRY ±3, 100 × ln(E_{+3} / E_{−4}) = +3,41’dir. Gün 0’ın emsal farkı yayınlanmadı. ±1 eşit ağırlık +1,74’tür. Seri, EVDS3 satış kuru `TP.DK.USD.S.YTL`. Emsal: BRL, ZAR, MXN, INR. Pozitif, doların yerel para karşısında değer kazanmasıdır.

Ekli bağımsız test şunu yazar: anormal getiri = Δlog USD/TRY − ort(Δlog BRL, MXN, ZAR). USD/TRY, TCMB kurlar XML, ForexBuying, 15:30. Emsal, FRED H.10. Plasebo, aynı takvim yılının günleri, tek yön. 10 Temmuz 2018 gün 0: +4,52, p = 0,017. 9 Temmuz ±3 birikimli: +8,70, p = 0,035. 10 Temmuz ±3 birikimli: +6,21, p = 0,078. Bu sayılar iddiadır. Bu tur yeniden üretmeden hüküm sayısı olmaz.

### Satır satır karşılaştırma

Hesap bitince dört satır yazılır. Eşik kaymaz.

1. Veri kaynağı. Aynı takvim gününde üç TRY kuru yan yana: kurlar XML ForexBuying, kurlar XML ForexSelling, eldeki EVDS3 satış serisi. Fark 0,15 puandan küçükse alış/satış ayrımı çelişkinin kaynağı değildir.
2. Tarih hizası. İstanbul 15:30, yaz saatinde New York öğleninden önce gelir (aynı takvim günü, yaklaşık altı buçuk saat). Aynı takvim günü eşlemesi, Türk sabah olayını hem 15:30 göstergeye hem o günün New York öğlen kuruna koyar. Kaydırma, robustness’tır: TRY günü sabit, emsal getirisi +1 ve −1 TCMB iş günü kayar. Düzeltilmiş gün 0, kaydırmasız eşlemedir.
3. Tatil. İlk kural durur: uçta emsal yoksa o uçtan uca pencere boştur, kur uydurulmaz. Ekli testin birikimli getirisi ayrı tahmin olarak kurulur: −3’ten +3’e TCMB iş günlerinin günlük anormal getirileri toplanır. Bir gün, o gün ve önceki günde TRY varsa ve BRL, MXN, ZAR üçlüsünden en az ikisinin iki ucu da varsa toplama girer. 4 Temmuz, emsali yoksa toplama girmez. Doldurulmaz.
4. Pencere. Gün 0 = 100 × ln(E_t / E_{t−1}), ardışık TCMB iş günleri. ±1 ve ±3 uçtan uca, ilk turdaki tanım. Birikimli ±1 ve ±3, yukarıdaki günlük toplam. Dört sayı birden yazılır. Biri diğerinin yerine geçmez.

### Hangisi doğru

Kural, skor öncesi:

- Aynı takvim günü, ForexSelling, emsal BRL+MXN+ZAR, gün 0 formülü ekli +4,52’yi 0,15 puan içinde verirse, ekli gün 0 o tahmin için doğru aritmetiktir. İlk turun boş ±3’ü bununla çelişmez: o tur gün 0 emsal farkı yayınlamadı, ±3’ü 4 Temmuz ucu boş olduğu için boş bıraktı.
- +4,52 yalnız +1 veya −1 kaydırmayla 0,15 içine girerse, fark tarih hizasındadır. Düzeltilmiş sonuç kaydırmasız olandır.
- Alış, satış ve kaydırma hiçbirinde 0,30 puan içine girmezse ekli +4,52 bu dosyalardan **DOĞRULANMADI**. Düzeltilmiş sonuç, bu turda kurlar XML satış kuruyla kurulan gündür.
- İşaret, TRY getirisi eksi emsal ortalamasıdır. Ters çıkarma yapılmaz.

Düzeltilmiş tek sonuç, 9 Temmuz ve 10 Temmuz için kaydırmasız gün 0’dır. Kurlar XML satış kuru, emsal BRL+MXN+ZAR, tatilde doldurma yok. Yanında birikimli ±3 ve ilk turun boş uçtan uca ±3’ü durur.

### Sağlamlık

Üçü de düzeltilmiş gün 0 ve birikimli ±3 için, skor öncesi kilitli:

- R-emsal. Aynı hesap, eşit ağırlık {BRL, MXN, ZAR, INR}, o günde en az üçü varsa. INR dosyası eldeki H.10’dur. Yeni indirme gerekmez.
- R-saat. Emsal +1 ve −1 iş günü kayar. Kaydırmasız gün 0’ın işareti bu ikisinden birinde ters dönerse, o günün gün 0’ı H-kurum için Belirsizdir.
- R-plasebo. Tek yön p = (1 + en az gözlenen kadar büyük gün sayısı) / (1 + N). İki havuz: 2018’in geçerli günleri; 2016, 2017 ve 2019’un geçerli günleri (2018 yok). İkisi de p < 0,10 ise büyük. Yalnız 2018 küçükse “yalnız kriz yılı havuzunda” yazılır. Havuz örneklem değildir. Tüm geçerli günler girer. Çekirdek yok.

### Ayrılma

9 Temmuz KHK 703 ile 10 Temmuz 3 sayılı kararname ve 2018/1 atama kararı, kur etkisinde ayrılır, yalnız şu üçü birden olursa: kaydırmasız gün 0’lardan biri R-plasebo’nun iki havuzunda da büyüktür, diğeri değildir, ve birincil metin iki işlemi farklı yayımlanma günlerine koyar. Gün 0 pencereleri çakışmaz. ±1 pencereleri komşu günde çakışır. ±1 ile ayrılma iddiası kurulmaz.

Metin aynı sayıda ise ayrılma yok diye yazılır. Kur büyük olsa da kabine veya Hazine ve Maliye ataması, mevzuattan ayrılmaz.

### H-kurum güncellemesi

İlk hüküm Belirsizdir. Bu ek onu yalnız şöyle taşır.

- 3 sayılı kararname md.4’ün 10 Temmuz 2018 sayfasındaki aslı okunursa, kurum cümlesi o alıntıyla yazılır. Okunamazsa o cümle DOĞRULANMADI kalır. Metin tek başına Ayakta yapmaz.
- H-kurum Ayakta olmaz. İlk turda çıpa ayı Ağustos’tur ve bu ek çıpa ayını açmaz. Temmuz kümesi çıpa sürücüsü değildir.
- Düzeltilmiş 10 Temmuz gün 0 pozitif, iki plasebo havuzunda da p < 0,10, saat kaydırmasında işaret aynı ve 9 Temmuz gün 0 büyük değilse: Temmuz kümesinin kur izi 10 Temmuz gün 0’dadır, mevzuat ile atama yine ayrılamaz, H-kurum **Belirsiz** kalır. “10 Temmuz gün 0 büyük” cümlesi yazılır.
- Düzeltilmiş gün 0 iki havuzda da büyük değilse: ekli testin “10 Temmuz gün 0 anlamlı” cümlesi bu tanımda **Yanlışlandı**. H-kurum Belirsiz kalır. Boş ±3 ilk kuralın doğru uygulanmasıdır. O boşluk, gün 0’ın sıfır olduğu anlamına gelmez.
- Saat kaydırması işareti çevirirse gün 0 Belirsizdir.

Karşı-olgu, emsal farkıdır. Emsal farkı yoksa nedensel cümle yok.

### Görevden alma metinleri

Aranacak birincil sayfa: resmigazete.gov.tr. Tarih, gazete sayısı, karar sayısı, kararın görevden alma ve atama cümleleri, dayanak hüküm. Aday günler, ekli tablodaki 6 Temmuz 2019, 7 Kasım 2020 ve 20 Mart 2021’dir. Bunlar iddiadır. Metin o günde yoksa o ayın mükerrer sayıları da bakılır: 1–15 Temmuz 2019, 1–15 Kasım 2020, 15–25 Mart 2021. Metin yoksa o karar **DOĞRULANMADI**. Kur sayısına bakılarak gün seçilmez.

Ayrıca: 10 Temmuz 2018, sayı 30474, 3 sayılı Cumhurbaşkanlığı Kararnamesi md.4’ün o sayıdaki aslı. KHK 703 öncesi 1211 sayılı Kanun md.25 birinci fıkra ve md.29’un eski metni, mevzuat.gov.tr veya o maddeleri yayımlayan Resmî Gazete. Bulunamazsa DOĞRULANMADI. Haber metni kullanılmaz.

Ekli testin görevden alma kur sayıları (+2,64, −1,94, +7,97) yeniden üretilmeden hüküm sayısı olmaz. Metin bulunursa, düzeltilmiş gün 0 formülü o gün için de kurulur. Bu, H-kurum’un Ayakta şartına girmez. İlk turda H-kurum, gazete kümesinin çıpa sürücüsü olmasını ister. Bu ek çıpa ayını açmaz.

## SAPMA — ek tur, eşik değişmedi

Yazım: 2026-10-20T18:05:00Z.

SAPMA-kapsam. Kurlar XML ilk indirme 2016–2019’du. Görevden alma gazeteleri 2020 ve 2021’dedir. Aynı satış kuru formülüyle 2020 ve 2021 bültenleri eklendi. Gün 0 tanımı ve p formülü kaymadı.

SAPMA-p. Ekli testin 10 Temmuz gün 0’ı +4,52, bu turda da +4,52’dir. Onların p’si 0,017, bu turun 2018 havuzu p’si 0,022’dir (228 geçerli gün). Fark, geçerli gün sayısındadır. İkisi de 0,10’un altındadır. Eşik kaymadı. 9 Temmuz birikimli ±3 için ekli 8,70 bu turda çıkmadı. Doldurmasız toplam 6,01’dir. 8,70 hüküm sayısı yapılmadı.

### Veri

`EVDS_API_KEY` okunmaz. Yeni TRY, kurlar XML. EVDS3 bu ekte yeniden çağrılırsa raporda yazılır. Sertifika doğrulaması atlanmaz. Site reddi aşılmaz. Reddedilirse o parça DOĞRULANMADI.
