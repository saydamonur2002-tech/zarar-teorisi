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
