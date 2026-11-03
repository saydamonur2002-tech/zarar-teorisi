# Resmî Gazete biçimsel boşluk metni

Pencere: 1 Ocak 2018 — 15 Eylül 2026. Karşı dönem ölçülmedi.

Bu metin on iki kamu mekanizmasının Resmî Gazete’de duran biçimini ölçer. Skor, hükmün kâğıt üzerindeki tamamlığıdır. Uygulama, fiili denetim ve mali sapma bu turda yoktur. Etki yüzdesi, GSYH payı ve nedensel cümle yazılmaz. Aile medyanı bir rapor satırıdır. Model katsayısı değildir. `rg_bosluk_skor.py` satır skorunu ve bağ kimliğini girdi sayar; aile medyanını katsayı saymaz.

Kaynak sınırı: Resmî Gazete’de yayımlanmış kanun, Cumhurbaşkanlığı kararnamesi, yönetmelik, tebliğ ve Resmî Gazete’de yayımlanmış genelge. İç genelge, protokol ve teamül yok sayıldı. Kurul kararı, taslak ve kanun teklifi hüküm değildir. Hüküm bulunamazsa skor 1.00 ve tip “norm yok”dur. Yakın metin boşluğu kapatmaz.

## Ölçme

Her mekanizma tek cümledir ve dört parça taşır: kim yetkili, hangi ölçütle, hangi sürede, hangi yaptırımla. Cümle parçayı taşımazsa ölçülmez. Parça metinde boşsa katmanların hepsi 0 yazılır. Bu, “hüküm yoksa skor 1.00” kuralının parçaya indirgenmiş hâlidir. Yokluğu istikrar diye 1 saymak skoru 1.00’dan aşağı çekerdi.

Her parça için beş katman, 0 veya 1:

1. Norm var mı? Açık hüküm Resmî Gazete’de duruyor mu?
2. Belirli mi? Yetki, ölçüt, süre veya istisna metinde net mi; yoksa “ilgili kurumca belirlenir”, “kanaat”, “yeterliliğe hükmedilir” veya bir bant ile mi kaçıyor?
3. Yaptırım ve denetim o parçanın kendi metnine bağlı mı? Sayıştay, idari para, iptal, disiplin, kamu zararı veya aynı maddede yazılı iade ve izin iptali burada sayılır. Başka kanundaki genel bant, o parçanın kendi maddesinde yoksa bu katman 0 kalır ve yaptırım parçasına yazılır.
4. Kaynak veya veri yükümlülüğü yazılı mı? Bütçe kalemi, raporlama, ilan, bildirim veya denetime hazır kayıt.
5. İstikrar: aynı hüküm pencerede 0 veya 1 kez değişmişse 1, iki ve daha fazla yama varsa 0. Yönetmeliğin başka maddesinin yamalanması, dokunulmayan cümleyi istikrarsız saymaz.

Ağırlık kilitlidir: norm 0.15, belirlilik 0.20, yaptırım-denetim 0.30, kaynak-veri 0.25, istikrar 0.10. Parça puanı bu ağırlıkların toplamıdır. Mekanizma boşluğu, dört parça puanının ortalamasının birden farkıdır. İki basamağa yuvarlanır.

Aile tek etikettir. Uymayan “sınıflanmadı” bırakılır. Bu on ikisi aileye oturdu; sınıflanmayan satır yok.

Endeks üç kapıdan geçer. Norm yok satırı aile medyanına girmez. Aday sayısı 5’in altındaysa “örnek küçük” yazılır, medyan endeks olmaz. Aday sayısı 5 ve üstüyse örneklem sapması hesaplanır. Sapma 0.15 ve üstse aile heterojendir; ham medyan raporlanır, endeks yazılmaz, ortalama yazılmaz. Alt tipin n’i 5’in altındaysa o alt tip de endekslenmez. Çekirdek altı ailenin (yetki, ölçüt, kaynak, veri, denetim-yaptırım, alım) ortalaması alınmaz. Buna sistem boşluğu denmez.

Aynı Resmî Gazete maddesi birden fazla satırda durabilir. Bağ kimliği tarih, sayı ve maddedir. Raporda bir kez listelenir. Satır skorları bu yüzden birbirine eklenmez. Paylaşılan madde, satırları tek gözlem yapmaz. Her satır kendi cümlesinin skorudur.

Aralık dışı yayım, pencere başlamadan önce çıkmış ve pencerede yürürlükte duran metindir. Skoru kendiliğinden düşürmez. Satırda işaretlenir. Penceredeki yama sayısı istikrar katmanındadır.

## Elenen üç cümle

Üç cümle tarandı ve ölçülmedi.

Birincisi, 17 Mart 2020 tarihli ve 8948 sayılı Bankacılık Düzenleme ve Denetleme Kurulu kararıdır. Donuk alacak için yönetmelikteki 90 günü, 31 Aralık 2020’ye kadar 180 gün uygulatır ve metin kurum internet sitesinde yayımlanacağını yazar. Kurul kararı bu turun izinli türü değildir. 90 gün eşiğinin istikrarını da bu karar bozmaz. Yönetmelik cümlesi durur. Karar, yönetmeliğin yerine geçmez.

İkincisi, Bankaların Sermaye Yeterliliğinin Ölçülmesine ve Değerlendirilmesine İlişkin Yönetmelik taslağıdır. Kurumun görüş metnidir. Yürürlük cümlesi 1 Ocak 2026 der. Resmî Gazete’de yayımlanmış yönetmelik olarak açılmadı. Yüzde 8 tabanı bu taslaktan değil, 2005 tarihli kanundan okundu.

Üçüncüsü, 2026’da Türkiye Büyük Millet Meclisine gelen tüketici kredisi ve kredi kartı borcunun yapılandırılmasına ilişkin kanun teklifidir. Komisyondadır. Resmî Gazete’de kanun değildir. Borç sona erdirme satırını kapatmaz.

## 1. Donuk gün eşiği

Aile: ölçüt-tarife. Alt tip: sayı yazılı eşik. Skor: 0.34. Birincil tip: yaptırım. İkincil etiket: biçimsel kaçış. Endeks adayıdır. Aralık dışı yayım: 22 Haziran 2016.

Cümle: Banka, anapara veya faizi vadesinden itibaren doksan günü aşan krediyi donuk alacak sayar, yüz seksen gün ve bir yıl eşikleriyle gruplar; aykırılık, genel idari para bandına bağlıdır.

Açılan metin: 22 Haziran 2016, 29750, Kredilerin Sınıflandırılması ve Bunlar İçin Ayrılacak Karşılıklara İlişkin Usul ve Esaslar Hakkında Yönetmelik, madde 4 ve madde 5. Yaptırım bağı: 25 Şubat 2020, 31050, 7222 sayılı Kanunun 16. maddesi, 5411 sayılı Kanunun 148. maddesi.

Madde 4, bankaları kredileri gruplayarak izlemekle yükümlü kılar. Birinci grupta ödeme otuz günden fazla gecikmez. İkinci grupta tahsil, vadeden itibaren otuz günden fazla gecikir ancak doksan günü geçmez. Üçüncü grupta anapara veya faizin tahsili doksan günden fazla gecikir ancak yüz seksen günü geçmez. Dördüncü grupta gecikme yüz seksen günü geçer, bir yılı geçmez. Beşinci grupta tahsil bir yıldan fazla gecikmiştir. Madde 5, üçüncü, dördüncü ve beşinci grubu donuk alacak sayar. Tüketici kredisi, borçlu yerine kredi bazında değerlendirilebilir. Bir tüketici kredisinin donuk sayılması, aynı borçlunun diğer tüketici kredilerini kendiliğinden donuk yapmaz. Banka onları birinci grup dışında bir yere koyabilir.

Aynı madde 4, gün sayısının yanında bir kanal daha açar. Üçüncü grubun 4 numaralı bendi, makroekonomik şart veya borçluya ilişkin olumsuz gelişme nedeniyle tahsilin doksan günden fazla gecikeceğine kanaat getirilen krediyi de bu gruba yazar. Gün eşiği sayıdır. Kanaat kanalı, eşiğe varmadan sınıflandırma yoludur. Bu satırın cümlesi gün eşiğidir. Kanaat, eşiğin sayısını silmez. Eşiğin tek yol olmadığını gösterir.

24 Mayıs 2022 tarihli ve 31845 sayılı Resmî Gazete’ye kadar işlenen konsolide metinde doksan gün cümlelerinin üzerinde “değişik” işareti yoktur. İşaretler madde 6, 13, 16 ve 18’in başka fıkralarındadır. Yönetmelik pencerede altı kez yamalanmıştır: 27 Mart 2018 (30373), 15 Ağustos 2018 (30510), 18 Ekim 2018 (30569), 27 Kasım 2019 (30961), 6 Temmuz 2021 (31533), 24 Mayıs 2022 (31845). Bu yamalar doksan gün cümlesine işlemediği için istikrar 1’dir. Cümle 2016 metninde durur.

Yaptırım, sınıflandırma maddesinin içinde değildir. 7222 sayılı Kanunun 16. maddesi, 5411 sayılı Kanunun 148. maddesinin birinci fıkrasının (b) bendindeki alt tutarı elli bin, üst tutarı beş yüz bin Türk lirası yapar. “Alınan kararlara” ibaresinden sonra “ve verilen talimatlara” eklenir. Aynı fıkraya, aykırılık birden fazla işlenmişse veya cezanın uygulanmasından itibaren iki yıl içinde tekrarlanmışsa Kurulun tutarları iki katına kadar artıracağı cümlesi girer. Bent, Kanuna dayanılarak çıkarılan yönetmelik ve tebliğlere uyulmamasını kapsar. Doksan güne özel bir cezası yoktur. Tutar bir banttır.

Madde 18, ikinci gruptaki kredinin 0-30, 31-60 ve 61-90 gün diye izlenmesi için altyapı kurulmasını ve yeniden sınıflandırma değerlendirmesinin denetime hazır tutulmasını yazar. Bu, veri katmanını doldurur. Kamuoyuna hane ve firma kırılımı yayımlama yükümlülüğü değildir. O ayrı satırdır.

| Parça | Norm | Belirlilik | Yaptırım | Kaynak-veri | İstikrar | Parça puanı |
| --- | --- | --- | --- | --- | --- | --- |
| Yetki | 1 | 1 | 0 | 1 | 1 | 0.70 |
| Ölçüt | 1 | 1 | 0 | 1 | 1 | 0.70 |
| Süre | 1 | 1 | 0 | 1 | 1 | 0.70 |
| Yaptırım | 1 | 0 | 1 | 0 | 1 | 0.55 |

Dört parçanın ortalaması 0.6625’tir. Boşluk 0.34’tür. En zayıf parça yaptırımdır. Hüküm vardır. Yaptırım, gün eşiğine değil yönetmelik aykırılığının geneline bağlı bir banttır. Bu, biçimsel kaçıştır. Bilinçli düzenlememe diye kilitlenmez.

## 2. Özel karşılık tabanı

Aile: ölçüt-tarife. Alt tip: kurum veya model. Skor: 0.61. Birincil tip: süre. İkincil tipler: ölçüt, yaptırım. İkincil etiket: biçimsel kaçış ve bilinçli düzenlememe olabilir. Endeks adayıdır. Aralık dışı yayım: 22 Haziran 2016.

Cümle: TFRS 9 uygulamayan banka, üçüncü grup için en az yüzde 20, dördüncü için en az yüzde 50, beşinci için yüzde 100 özel karşılık ayırır. TFRS 9 uygulayan bankada oran, bankanın kendi modeline ve Kurulun daha yüksek karşılık istemesine kalır. Ayrılacağı süre bu maddelerde yazılı değildir. Aykırılık genel idari para bandındadır.

Açılan metin: aynı yönetmelik, 22 Haziran 2016, 29750, madde 9 ve madde 11. Yaptırım bağı yine 25 Şubat 2020, 31050, 7222 sayılı Kanunun 16. maddesidir.

Madde 9’un birinci fıkrası esası koyar. Bankalar kredileri için TFRS 9 kapsamında karşılık ayırır. Beşinci fıkra, Kurula, kredi bazında veya banka bazında bu karşılıktan daha yüksek tutar isteme yetkisi verir. Altıncı fıkra, Kurulun, bankanın başvurusu üzerine karşılıkların TFRS 9 yerine madde 10, 11, 13 ve 15’e göre ayrılmasına karar verebileceğini yazar. Sayısal taban, esas değil, Kurul kararıyla girilen istisnadır.

Madde 11, TFRS 9 uygulamayan bankalar içindir. Üçüncü grup en az yüzde 20, dördüncü grup en az yüzde 50, beşinci grup yüzde 100. Beşinci fıkra, Kurulun bu oranlardan daha yüksek özel karşılık oranı belirleyebileceğini yazar. Konsolide metinde bu yüzde cümlelerinin üzerinde “değişik” işareti yoktur. İstikrar 1’dir.

Süre parçası boştur. Madde 7, yeniden yapılandırılmış donuk alacağın ikinci gruba çıkması için en az bir yıl donuk izlenmesini şart koşar. Bu, karşılığın hangi gün ayrılacağının süresi değildir. Madde 9 ve 11, karşılık için gün, ay veya bilanço dönemi yazmaz. Parça yoksa beş katman da 0’dır.

Belgelendirme madde 18’dedir. Karşılık tutarına ilişkin değerlendirme denetime hazır tutulur. Veri katmanı bu yüzden 1’dir. Yayımlama yükümlülüğü değildir.

| Parça | Norm | Belirlilik | Yaptırım | Kaynak-veri | İstikrar | Parça puanı |
| --- | --- | --- | --- | --- | --- | --- |
| Yetki | 1 | 0 | 0 | 1 | 1 | 0.50 |
| Ölçüt | 1 | 0 | 0 | 1 | 1 | 0.50 |
| Süre | 0 | 0 | 0 | 0 | 0 | 0.00 |
| Yaptırım | 1 | 0 | 1 | 0 | 1 | 0.55 |

Ortalama 0.3875’tir. Boşluk 0.61’dir. Süre hiç yazılmamıştır. Ölçüt, esas olan rejimde sayı değildir. Yüzde 20, 50 ve 100, TFRS 9 uygulamayan bankaya ve Kurulun istisna kararına bağlıdır. Madde 9 bunu açıkça esasın dışına koyar. Bu, biçimsel kaçıştır. Aynı açıklık, sayısal tabanın bilinçli olarak esas kılınmamış olabileceğini gösterir. Bu ihtimal kanıtlanmadan boşluk diye kilitlenmez. Üçüncü ihtimal açık kalır: bilinçli düzenlememe olabilir.

## 3. SYR tabanı

Aile: ölçüt-tarife. Alt tip: sayı yazılı eşik. Skor: 0.23. Birincil tip: süre. İkincil tip: yaptırım. İkincil etiket: biçimsel kaçış. Endeks adayıdır. Aralık dışı yayım: 1 Kasım 2005.

Cümle: Banka, yüzde sekizden az olmayacak sermaye yeterliliği oranını hesaplar, tutturur ve raporlar. Kurul oranı yükseltebilir. Giderim süresi, Kurumun uygun göreceği süredir. Yetersizlikte tedbir ve idari para bandı vardır.

Açılan metin: 1 Kasım 2005, 25983 (mükerrer), 5411 sayılı Bankacılık Kanunu, madde 45, madde 67 ve madde 68. Sayı, mevzuat dizinindeki Resmî Gazete kaydıdır. Madde metni o günün mükerrer Resmî Gazete sayfasından okundu.

Madde 45, sermaye yeterliliğini, maruz kalınan riskler nedeniyle oluşabilecek zararlara karşı yeterli özkaynak bulundurulması diye tanımlar. Bankalar, Kurumun yönetmeliğinde öngörülen usule göre yüzde sekiz oranından az olmamak üzere belirlenecek oranı hesaplar, tutturur, idame ettirir ve raporlar. İkinci fıkra, Kurula, bankaların iç sistemleri ile aktif ve mali yapıları dikkate alınarak asgari oranı artırma ve banka bazında farklılaştırma yetkisi verir. Taban yazılıdır. Tabanın üstü Kuruldadır. Artırma yetkisi tabanı delmez. “Yüzde sekizden az olmamak” cümlesi belirli sayılır.

Bu satır, gözlenen bir sermaye oranını ve koruma tamponlarının toplamını ölçmez. Yüzde 8, kanundaki tabandır. Tamponlar, banka bazında yükseltilmiş oran ve içsel model bu cümlenin içinde değildir. Taslak yönetmelik elendiği için yüzde 6 ve yüzde 4,5 gibi ara oranlar bu satıra yazılmadı.

Madde 67, özkaynakların sermaye yeterliliği düzenlemelerine göre yetersiz olmasını veya bu durumun gerçekleşmek üzere bulunmasını, tedbir alınacak hâller arasına koyar. Madde 68, Kurumun, yönetim kurulundan, Kurumun uygun göreceği bir süre ve onaylayacağı bir plan içinde özkaynak artırımı dâhil tedbir istemesini yazar. Süre vardır. Uzunluğu “uygun göreceği süre”dir. Belirlilik 0’dır. Bu, biçimsel kaçıştır.

Madde 45 “raporlamak zorundadır” der. Veri katmanı yetki ve ölçüt parçalarında 1’dir. Sürenin kendisi bir rapor dönemi yazmaz. Yaptırım parçasında da rapor yükümlülüğü yoktur.

Yaptırım iki kanaldadır. Madde 67 ve 68 tedbirdir. Madde 148 banttır. Tedbirin hangisinin seçileceği ve para cezasının bant içinde nereye düşeceği metinde sabit değildir. Yaptırım parçasının belirliliği 0’dır. Madde 45’in yüzde sekiz cümlesine ve madde 67’ye bu taramada ikinci bir yama bulunmadı. 7222 sayılı Kanun madde 45’i değiştirmiyor. İstikrar 1’dir. Bu, kanunun başka maddelerinin pencerede değişmediği anlamına gelmez.

| Parça | Norm | Belirlilik | Yaptırım | Kaynak-veri | İstikrar | Parça puanı |
| --- | --- | --- | --- | --- | --- | --- |
| Yetki | 1 | 1 | 1 | 1 | 1 | 1.00 |
| Ölçüt | 1 | 1 | 1 | 1 | 1 | 1.00 |
| Süre | 1 | 0 | 1 | 0 | 1 | 0.55 |
| Yaptırım | 1 | 0 | 1 | 0 | 1 | 0.55 |

Ortalama 0.775’tir. Boşluk 0.23’tür. Taban ve raporlama yazılıdır. Açık parça, giderim süresinin Kuruma bırakılması ve yaptırımın bant ile tedbir menüsünde kalmasıdır.

## 4. Tüketici gecikme faizi

Aile: ölçüt-tarife. Alt tip: sayı yazılı eşik. Skor: 0.25. Birincil tip: veri. İkincil etiket: veri bağsız. Endeks adayıdır. Aralık dışı yayım: 22 Mayıs 2015.

Cümle: Kredi veren, belirli süreli tüketici kredisinde gecikme faizini sözleşmedeki akdi faiz oranının yüzde otuz fazlasıyla sınırlar, aşanı aynı oran üzerinden iade eder. Gün sayısı, ödemenin yapıldığı tarihe göredir. Yayımlama veya paylaşma yükümlülüğü bu maddede yoktur.

Açılan metin: 22 Mayıs 2015, 29363, Tüketici Kredisi Sözleşmeleri Yönetmeliği, madde 4, madde 2 ve madde 18.

Madde 4, belirli süreli sözleşmede gecikme faiz oranını, akdi faiz oranının yüzde otuz fazlasını geçmemek üzere belirlenen oran diye tanımlar. Belirsiz süreli sözleşmede oran “ilgili mevzuat gereği” belirlenir. Bu satırın cümlesi belirli sürelidir. Belirsiz sürenin kaçışı bu satıra yazılmaz.

Madde 2’nin üçüncü fıkrası, tüketici kredisi sayılan kredi kartı sözleşmelerine ve kredili mevduat hesabı sözleşmelerine madde 14 ila 19’un uygulanmayacağını yazar. Yüzde otuz tavanı kredi kartına bu yönetmelikle gitmez. Kart ayrı satırdır. İstisna metinde açıktır. Belirliliği düşürmez. Kapsamı daraltır.

Madde 18’in ikinci fıkrası, temerrüt veya geç ödemede akdi faizin yüzde otuz fazlasından daha yüksek gecikme faizi tahsil edilemeyeceğini yazar. Aksi halde kredi veren, fazla tahsil ettiği tutarı ve bu tutarın tahsil edildiği tarihten tüketiciye fiilen geri ödendiği tarihe kadar, akdi faizin yüzde otuz fazlası üzerinden hesaplanacak faizi ödemekle yükümlüdür. Üçüncü fıkra, gecikme faizinin geç ödenen anapara üzerinden, geç ödenen gün sayısıyla ve tüketicinin ödemeyi yaptığı tarih esas alınarak hesaplanacağını yazar. Bu süre tüketici aleyhine değiştirilemez.

İade, aynı maddede yazılı bir sonuçtur. Sayıştay veya idari para değildir. Parçanın kendi metnine bağlı bir yaptırımdır. Bu yüzden yaptırım katmanı 1’dir. 6502 sayılı Kanunun idari para maddesi bu turda Resmî Gazete sayfası olarak açılmadı. Açılmayan madde skora yazılmaz. 23 Eylül 2022 tarihli ve 31962 sayılı değişiklik, madde 4, 6, 11, 13, 24, 26 ve 32’ye gider. Madde 18’e gitmez. İstikrar 1’dir.

Dört parçada da kaynak veya veri yükümlülüğü yoktur. Boşluk buradadır.

| Parça | Norm | Belirlilik | Yaptırım | Kaynak-veri | İstikrar | Parça puanı |
| --- | --- | --- | --- | --- | --- | --- |
| Yetki | 1 | 1 | 1 | 0 | 1 | 0.75 |
| Ölçüt | 1 | 1 | 1 | 0 | 1 | 0.75 |
| Süre | 1 | 1 | 1 | 0 | 1 | 0.75 |
| Yaptırım | 1 | 1 | 1 | 0 | 1 | 0.75 |

Ortalama 0.75’tir. Boşluk 0.25’tir. Birincil tip veridir. Dört parça da durur. Eksik olan, yayımlama ve paylaşma yüküdür.

## 5. Kart gecikme faizi

Aile: ölçüt-tarife. Alt tip: kurum veya model. Skor: 0.70. Birincil tip: yaptırım. İkincil tipler: süre, ölçüt. İkincil etiket: biçimsel kaçış. Endeks adayıdır. Aralık dışı yayım yok.

Cümle: Türkiye Cumhuriyet Merkez Bankası, kredi kartında azami akdi ve gecikme faiz oranını tespit ve ilan eder. Oran, süre ve aykırılık yaptırımı bu cümlede sayıya bağlanmaz.

Açılan metin: 25 Şubat 2020, 31050, 7222 sayılı Kanunun 20. maddesi. Bu madde, 5464 sayılı Banka Kartları ve Kredi Kartları Kanununun 26. maddesinin üçüncü fıkrasını şöyle değiştirir: “Türkiye Cumhuriyet Merkez Bankası, azami akdi ve gecikme faiz oranlarını tespit ve ilan etmeye yetkilidir.”

Yetki adı yazılıdır. Merkez Bankasıdır. İlan, veri katmanını doldurur. Oran yazılmaz. Ölçüt, kuruma bırakılır. Belirlilik 0’dır. Fıkra, oranın hangi sürede ilan edileceğini ve aykırı tahsilin ne olacağını yazmaz. Süre ve yaptırım parçaları boştur. Beş katman da 0’dır. 5464 sayılı Kanunun ceza maddesi bu fıkra için ayrıca açılmadı. Açılmayan madde, boş yaptırım parçasını doldurmaz.

Pencerede bu fıkraya doğrulanan değişiklik 7222’dir. İkinci yama bu taramada yoktur. İstikrar 1’dir.

| Parça | Norm | Belirlilik | Yaptırım | Kaynak-veri | İstikrar | Parça puanı |
| --- | --- | --- | --- | --- | --- | --- |
| Yetki | 1 | 1 | 0 | 1 | 1 | 0.70 |
| Ölçüt | 1 | 0 | 0 | 1 | 1 | 0.50 |
| Süre | 0 | 0 | 0 | 0 | 0 | 0.00 |
| Yaptırım | 0 | 0 | 0 | 0 | 0 | 0.00 |

Ortalama 0.30’dur. Boşluk 0.70’tir. Yetki ve ilan vardır. Oran, süre ve yaptırım kaçmıştır. Biçimsel kaçıştır.

## 6. Asgari satış bedeli

Aile: ölçüt-tarife. Alt tip: oran hükmü yok. Skor: 1.00. Birincil tip: norm yok. İkincil etiket: bilinçli düzenlememe olabilir. Endekse girmez. Aralık dışı yayım yok.

Cümle: Kaynak kuruluş, donuk alacağı yazılı bir asgari bedel oranıyla, belirli sürede ve aykırı satış yaptırımıyla varlık yönetim şirketine satar.

Açılan metin: 14 Temmuz 2021 tarihli Resmî Gazete, Varlık Yönetim Şirketlerinin Kuruluş ve Faaliyet Esasları ile Devralınacak Alacaklara İlişkin İşlemler Hakkında Yönetmelik, madde 18. Sayfa `20210714-2.htm` gövdesinden okundu. Sayı, dizin kaydında 31541’dir. Sayfa başlığında sayı bu turda ayrıca basılı değildi.

Madde 18’in birinci fıkrası, Kurumun denetimindeki kaynak kuruluşun, borçluyu ve teminatı dikkate alarak borcun tahsil edilme yüzdesini, süresini ve gerçeğe uygun değerini de içerecek şekilde iktisadi nedenini yazılı hale getirmesi kaydıyla alacağını varlık yönetim şirketine devredebileceğini yazar. Devrin uygulama esasları yazılı belirlenir. Bu, asgari bir bedel oranı değildir. Gerçeğe uygun değer, oran tavanı veya tabanı olarak sayıya bağlanmaz. Süre ve aykırı bedelin yaptırımı da bu cümlede yoktur.

Yakın metin skoru kapatmaz. İhale usulü ayrı satırdır. İhale, fiyat tabanı koymaz. Satır norm yok kalır. Beş katmanın dördü parçada da 0’dır. Skor 1.00’dır.

Madde, devri serbest bırakıp gerekçeyi yazdırmayı seçmiş olabilir. Bu, bilinçli düzenlememe olabilir. Kanıtlanmadan kilitlenmez. Endekse girmez. Ölçüt ailesinin ham medyanını da çekmez.

## 7. Borç sona erdirme

Aile: yetki-görev. Alt tip: oran hükmü yok. Skor: 1.00. Birincil tip: norm yok. İkincil etiket: bilinçli düzenlememe olabilir. Endekse girmez. Aralık dışı yayım yok.

Cümle: İflasa tabi olmayan gerçek kişinin tüketici kredisi veya kredi kartı borcunu, alacaklı onayından bağımsız bir ölçütle, belirli sürede sona erdirmeye yetkili makam ve bu sona ermeye aykırı tahsilin yaptırımı.

Açılan metin: 15 Mart 2018, 30361, 7101 sayılı Kanun. Madde 13, 2004 sayılı İcra ve İflas Kanununun 285. maddesini değiştirir. Madde 20, 292. maddeyi değiştirir. Madde 36, 308. maddeyi değiştirir.

Madde 285, borçlarını vadesinde ödeyemeyen veya ödeyememe tehlikesi altında bulunan herhangi bir borçlunun, vade veya tenzilat için konkordato talep edebileceğini yazar. İflasa tabi olmayan borçlu için görevli mahkeme, yerleşim yerindeki asliye ticaret mahkemesidir. Konkordato, alacaklıların projesine ve mahkemenin tasdikine bağlı bir yoldur. Alacaklı onayından bağımsız bir silme yetkisi değildir.

Madde 292’nin ikinci fıkrası, iflasa tabi olmayan borçlu bakımından kesin mühlet içinde belirli hâller gerçekleşirse mahkemenin mühleti kaldırıp konkordato talebini reddedeceğini yazar. İflas açılmaz. Madde 308, konkordato tasdik edilmezse talebin reddine karar verileceğini, iflasın ancak borçlu iflasa tabi şahıslardan ise ve doğrudan doğruya iflas sebebi varsa resen açılabileceğini yazar.

19 Haziran 2021, 7327 sayılı Kanunun 6. maddesi, 308. maddeye bir fıkra ekler. Konkordato iflasla sonuçlanırsa tasfiyenin basit veya adi usule göre yapılmasını ve gerekirse adi tasfiyeyi komiserlerin yürüteceğini yazar. Silme yetkisi eklemez. Bu fıkra, satırın üç metin sınırına sığmadığı için bağ listesinde ayrıca durmaz. Hükmü değiştirmez.

Bu üç madde, iflasa tabi olmayan borçluyu görür ve iflası ona bağlamaz. Borcu sona erdirecek makamı, ölçütü, süreyi ve aykırı tahsilin yaptırımını kurmaz. Yakın metin, norm yok skorunu kapatmaz. Skor 1.00’dır. Yetki ailesinde endeks adayı 0’dır. Örnek küçüktür.

7101, bu sınıfı ayrıca yazıp iflası bağlamadığı için üçüncü ihtimal açıktır: bilinçli düzenlememe olabilir. Metin, düzenlememenin kasıt olduğunu kanıtlamaz. Kilitlenmez.

## 8. VYŞ faaliyet izni

Aile: izin-ruhsat. Alt tip: sayı yazılı eşik. Skor: 0.10. Birincil tip: ölçüt. İkincil etiket: biçimsel kaçış. Endeks adayıdır. Ailede tek satır olduğu için örnek küçüktür. Aralık dışı yayım yok.

Cümle: Kurul, nakden en az elli milyon Türk lirası sermaye ve yazılı kurucu şartlarıyla kuruluş ve faaliyet izni verir. Kuruluş izninden itibaren yüz seksen günde faaliyet izni başvurusu, izinden itibaren bir yılda faaliyete geçiş zorunludur. Aksi halde izin iptal edilir.

Açılan metin: 14 Temmuz 2021, dizin sayısı 31541, aynı varlık yönetim şirketi yönetmeliği, madde 4 ve madde 6.

Madde 4, kuruluş iznini Kurula verir. Şirket anonimdir. Ödenmiş sermaye nakden ve muvazaasız en az elli milyon Türk lirasıdır. Hisse senetleri nama yazılı ve nakit karşılığıdır. Unvanda “Varlık Yönetim Şirketi” ibaresi bulunur. Kurul, asgari sermayeyi artırmaya yetkilidir. Taban yazılıdır. Tabanın üstü Kuruldadır.

Madde 6, faaliyet izninde Kurumun şunlara bakacağını yazar: sermayenin nakden ödenip ödenmediği, planlanan faaliyeti taşıyıp taşımadığı, hizmet birimleri ile risk yönetimi, iç kontrol, muhasebe, bilgi işlem ve raporlama sistemlerinin kurulup kurulmadığı, personel kadrosunun ve görev tanımlarının yeterli olup olmadığı. Değerlendirme sonunda faaliyet konularını yürütebilecek yeterliliğe sahip bulunduğuna hükmedilen şirkete Kurul izin verir. Sermaye sayısı belirlidir. Yeterlilik hükmü değildir. Ölçüt ve yetki parçalarının belirliliği bu yüzden 0’dır. Biçimsel kaçış buradadır.

Aynı fıkranın altıncı bendi süreleri ve yaptırımı birlikte yazar. Kuruluş izninden itibaren yüz seksen gün içinde faaliyet izni için başvurulmazsa, izinden itibaren bir yıl içinde faaliyete geçilmezse veya faaliyet bir yıl kesintisiz ara verirse izin iptal edilir. Faaliyete geçiş, yedi iş günü içinde Kuruma bildirilir. Süre belirli, yaptırım iptal, veri bildirimi yazılıdır. Bu iki parçanın puanı 1.00’dır.

Pencerede bu iki maddeye doğrulanan ikinci yama bu taramada yoktur. 27 Ağustos 2025 tarihli bir ek cümle ikincil derlemede anılır. O sayfa bu turda açılmadı. Açılmayan yama, istikrarı 0 yapmaz. İstikrar 1’dir.

| Parça | Norm | Belirlilik | Yaptırım | Kaynak-veri | İstikrar | Parça puanı |
| --- | --- | --- | --- | --- | --- | --- |
| Yetki | 1 | 0 | 1 | 1 | 1 | 0.80 |
| Ölçüt | 1 | 0 | 1 | 1 | 1 | 0.80 |
| Süre | 1 | 1 | 1 | 1 | 1 | 1.00 |
| Yaptırım | 1 | 1 | 1 | 1 | 1 | 1.00 |

Ortalama 0.90’dır. Boşluk 0.10’dur. Açık parça, faaliyet izninin “yeterliliğe hükmedilir” cümlesidir.

## 9. İhale ile devir

Aile: alım-yükümlülük. Alt tip: sayı yazılı eşik. Skor: 0.34. Birincil tip: yaptırım. İkincil etiket: biçimsel kaçış. Endeks adayıdır. Ailede tek satırdır. Örnek küçüktür. Aralık dışı yayım yok.

Cümle: Kaynak kuruluş, münferit bir risk grubunu içeren alacaklar hariç, alacağını varlık yönetim şirketine yalnız ihale ile devreder. İlan en az beş iş günü, inceleme en az on iş günüdür. İhlal, bu maddede ayrı cezaya bağlanmaz.

Açılan metin: 14 Temmuz 2021, dizin sayısı 31541, madde 18. Yaptırım bağı: 25 Şubat 2020, 31050, 7222 sayılı Kanunun 16. maddesi.

Madde 18’in ikinci fıkrası, Kurumun denetimindeki kaynak kuruluşların, yalnızca münferit bir risk grubunu içeren alacaklar hariç, alacaklarını ihale usulü dışında devredemeyeceğini yazar. İstisna metindedir. Üçüncü fıkra, ihaleye davet niteliğindeki bilgilendirmenin kaynak kuruluşun internet sitesinde, ana sayfada görünecek şekilde en az beş iş günü yayımlanmasını yazar. Dördüncü fıkra, ihaleye katılacak şirketlere ihale öncesi inceleme için on iş gününden az olmamak üzere aynı süre ve aynı nitelikte bilgi verilmesini yazar. Paylaşılacak asgari liste yazılıdır: kredi türü, borçlunun kimliği, anapara, işlemiş faiz ve masraf, faiz oranı, temerrüt tarihi, teminat, yapılandırma ve hukuki süreç. Kurul, listeye ilave unsur belirleyebilir. İlave unsur yetkisi, yazılı asgari listeyi silmez. Ölçüt belirli sayılır.

Bilgi paylaşımı, 5411 sayılı Kanunun 73. maddesinin dördüncü fıkrasına uygun gizlilik sözleşmesiyle ve yalnız ihale amacıyla sınırlıdır. İhale sonrası imha edilir. Bu, veri yükümlülüğüdür.

İhlalin cezası madde 18’de yoktur. Bağ, yönetmelik aykırılığının genel idari para bandıdır. Bant belirli değildir. Yaptırım parçası 0.55’tir. Diğer üç parça 0.70’dir.

| Parça | Norm | Belirlilik | Yaptırım | Kaynak-veri | İstikrar | Parça puanı |
| --- | --- | --- | --- | --- | --- | --- |
| Yetki | 1 | 1 | 0 | 1 | 1 | 0.70 |
| Ölçüt | 1 | 1 | 0 | 1 | 1 | 0.70 |
| Süre | 1 | 1 | 0 | 1 | 1 | 0.70 |
| Yaptırım | 1 | 0 | 1 | 0 | 1 | 0.55 |

Ortalama 0.6625’tir. Boşluk 0.34’tür. İhale ve süre yazılıdır. Eksik olan, ihlale bu maddede bağlanmış ayrı yaptırımdır.

## 10. Hane-firma yayımlama

Aile: veri-rapor. Alt tip: oran hükmü yok. Skor: 1.00. Birincil tip: norm yok. Endekse girmez. Aralık dışı yayım: 22 Haziran 2016.

Cümle: Bankacılık Düzenleme ve Denetleme Kurumu, yakın izlemedeki kredinin hane ve firma kırılımını yazılı bir ölçütle, belirli sürede yayımlar. Yayımlamama yaptırıma bağlıdır.

Açılan metin: 22 Haziran 2016, 29750, sınıflandırma yönetmeliği, madde 18. Bu madde, bankanın içeride gün kovası tutmasını ve değerlendirmeyi denetime hazır bulundurmasını yazar. Kuruma veya kamuya, yakın izlemenin hane ve firma diye ayrılmış bir tablosunu belirli sürede yayımlama yükü koymaz. İç kayıt, yayımlama hükmü değildir. Yakın metin skoru kapatmaz. Skor 1.00’dır.

Veri ailesinde endeks adayı, yalnız gün kovası satırıdır. Bir aday, örnek küçüktür. Bu satır medyana girmez.

## 11. Gün kovası kaydı

Aile: veri-rapor. Alt tip: sayı yazılı eşik. Skor: 0.51. Birincil tip: süre. İkincil etiket: yaptırım bağsız. Endeks adayıdır. Aile örnek küçüktür. Aralık dışı yayım: 22 Haziran 2016.

Cümle: Banka, ikinci gruptaki krediyi 0-30, 31-60 ve 61-90 gün diye kaydeder. Üst yönetim, yakından izleme için tedbir ve politika yazar. Kurma süresi ve aykırı kaydın cezası bu fıkrada yoktur.

Açılan metin: 22 Haziran 2016, 29750, madde 18’in dördüncü fıkrası. Yaptırım bağı, fıkranın dışında, 7222 sayılı Kanunun 16. maddesidir.

Fıkra, üç kovayı sayı ile yazar. Banka altyapıyı oluşturur. Üst yönetim tedbir ve politikadan sorumludur. Kovalar belirlidir. Fıkra, altyapının hangi güne kadar kurulacağını yazmaz. Süre parçası boştur. Fıkra, aykırı kaydın cezalarını da yazmaz. Yaptırım parçası genel banttır. Belgelendirme yükümlülüğü aynı maddenin üçüncü fıkrasındadır. Veri katmanı 1’dir. Fıkranın üzerinde “değişik” işareti yoktur. İstikrar 1’dir.

| Parça | Norm | Belirlilik | Yaptırım | Kaynak-veri | İstikrar | Parça puanı |
| --- | --- | --- | --- | --- | --- | --- |
| Yetki | 1 | 1 | 0 | 1 | 1 | 0.70 |
| Ölçüt | 1 | 1 | 0 | 1 | 1 | 0.70 |
| Süre | 0 | 0 | 0 | 0 | 0 | 0.00 |
| Yaptırım | 1 | 0 | 1 | 0 | 1 | 0.55 |

Ortalama 0.4875’tir. Boşluk 0.51’dir. Kova yazılıdır. Kurma süresi yoktur. Ceza, fıkraya bağlanmamıştır.

## 12. İdari para bandı

Aile: denetim-yaptırım. Alt tip: sayı yazılı eşik. Skor: 0.35. Birincil tip: ölçüt. İkincil etiket: biçimsel kaçış. Endeks adayıdır. Ailede tek satırdır. Örnek küçüktür. Aralık dışı yayım yok.

Cümle: Kurul, Kanuna dayanılarak çıkarılan yönetmelik ve tebliğlere uyulmamasında elli bin ile beş yüz bin Türk lirası arasında idari para cezası verir. Cezanın uygulanmasından itibaren iki yıl içinde tekrarlanırsa veya karar verilinceye kadar aykırılık birden fazla işlenmişse tutarı iki kata kadar artırabilir.

Açılan metin: 25 Şubat 2020, 31050, 7222 sayılı Kanunun 16. maddesi, 5411 sayılı Kanunun 148. maddesinin birinci fıkrası.

Yetki Kuruldur. Süre, cezanın uygulanmasından itibaren iki yıldır. Bu pencere belirli yazılmıştır. Ölçüt, yönetmelik ve tebliğ aykırılığının geneli ile elli bin ve beş yüz bin arasındaki banttır. Hangi aykırılığın bandın neresine düşeceği ve iki katın işletilip işletilmeyeceği Kuruldadır. Belirlilik 0’dır. Veri yükümlülüğü bu maddede yoktur. Pencerede bu bende doğrulanan değişiklik 7222’dir. İkinci yama bu taramada yoktur. İstikrar 1’dir.

Bu satır, donuk gün, özel karşılık, ihale ve gün kovasının yaptırım parçasında yeniden kullanılır. Bağ birdir: `2020-02-25|31050|7222 m.16`. Beş satırda durur. Endekste bir kez listelenir. Beş satırın skoru birbirine eklenmez. Her satır kendi cümlesini ölçer. Ortak bant, o cümlelerin yaptırım parçasını belirli yapmaz.

| Parça | Norm | Belirlilik | Yaptırım | Kaynak-veri | İstikrar | Parça puanı |
| --- | --- | --- | --- | --- | --- | --- |
| Yetki | 1 | 1 | 1 | 0 | 1 | 0.75 |
| Ölçüt | 1 | 0 | 1 | 0 | 1 | 0.55 |
| Süre | 1 | 1 | 1 | 0 | 1 | 0.75 |
| Yaptırım | 1 | 0 | 1 | 0 | 1 | 0.55 |

Ortalama 0.65’tir. Boşluk 0.35’tir. Ceza vardır. Tutarı bir banttır. Biçimsel kaçıştır.

## Bağlar

Aynı madde birden fazla satırda duran üç bağ:

- `2016-06-22|29750|m.18` iki satırdadır: hane-firma yayımlama ve gün kovası kaydı. Birincisi bu maddede yayımlama bulamaz ve norm yok kalır. İkincisi aynı maddede gün kovasını bulur ve 0.51 olur. Aynı sayfa, iki cümleyi birden kapatmaz.
- `2020-02-25|31050|7222 m.16` beş satırdadır: donuk gün eşiği, özel karşılık tabanı, ihale ile devir, gün kovası kaydı, idari para bandı.
- `2021-07-14|31541|m.18` iki satırdadır: asgari satış bedeli ve ihale ile devir. Birincisi bedel oranı bulamaz. İkincisi ihale süresini bulur.

## Aile

Ölçüt-tarife: satır 6. Norm yok 1 (asgari satış bedeli). Endeks adayı 5. Aday skorlar 0.23, 0.25, 0.34, 0.61 ve 0.70’tir. Ham medyan 0.34’tür. Örneklem sapması 0.22’dir. Eşik 0.15’tir. Aile heterojendir. Medyan endeks değildir. Ortalama yazılmaz.

Alt tipler, norm yok hariç, örnek küçüktür. Sayı yazılı eşik üç satırdır: SYR tabanı 0.23, tüketici gecikme faizi 0.25, donuk gün eşiği 0.34. Medyan 0.25, sapma 0.06’dır. Kurum veya model iki satırdır: özel karşılık tabanı 0.61, kart gecikme faizi 0.70. Medyan 0.66, sapma 0.06’dır. İkisi de n 5’in altında olduğu için endeks değildir. Sapmaları düşüktür. Bu, ailenin kendi içindeki iki kümenin ayrı ayrı sıkı, ailenin ise dağınık olduğunu gösterir. Dağınıklık, sayı yazan eşik ile kuruma veya modele bırakılan oran arasındadır.

Yetki-görev: satır 1, norm yok 1, endeks adayı 0. Örnek küçük. Endeks yok.

İzin-ruhsat: satır 1, endeks adayı 1, ham medyan 0.10. Örnek küçük. Endeks yok.

Alım-yükümlülük: satır 1, endeks adayı 1, ham medyan 0.34. Örnek küçük. Endeks yok.

Veri-rapor: satır 2, norm yok 1, endeks adayı 1, ham medyan 0.51. Örnek küçük. Endeks yok.

Denetim-yaptırım: satır 1, endeks adayı 1, ham medyan 0.35. Örnek küçük. Endeks yok.

Kaynak-ödenek, süre-yürürlük, transfer-hak, koordinasyon, kadro-atama ve istisna-teşvik: satır 0. Örnek küçük. Endeks yok.

Çekirdek altı ailenin hiçbiri endeks koşullarını tutmaz. Yetki, kaynak, veri, denetim-yaptırım ve alım örnek küçüktür. Ölçüt heterojendir. Altısının ortalaması yazılmaz.

## Karşı dönem

Eşit uzunluktaki önceki aralık 18 Nisan 2009 — 31 Aralık 2017’dir. Bu aralık için aile medyanı ölçülmedi. Karşı dönem yok. Aralık dışı yayım, karşı dönem skoru değildir. 2005, 2015 ve 2016 metinleri, 2018-2026 penceresinde duran hüküm olarak okundu.

## Ölçülmeyen

Uygulama, fiili denetim ve mali sapma ölçülmedi. Etki yüzdesi bu turda yoktur. Bir bankanın doksan günü fiilen kaç gün tuttuğu, Kurulun banttan hangi tutarı kestiği, Merkez Bankasının ilan ettiği kart faizinin kaç olduğu ve varlık yönetim şirketine satışın anaparanın hangi payına yapıldığı bu skorların içinde değildir. İç genelge, protokol ve teamül yok sayıldı. Yoklukları skoru kapatmaz.

Model girdisi, satır skoru ve bağ kimliğidir. Aile medyanı rapor satırıdır. Katsayı değildir. Ham medyan 0.34, heterojen bir ailenin ortasındaki satırdır. On iki mekanizmanın ortak bir boşluk yüzdesi yoktur.
