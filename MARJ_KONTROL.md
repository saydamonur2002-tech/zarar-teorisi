# Kontrol turu: finansman, hayatta kalma, pay sınıfı, eşik, TMS 29

Bu notun 2022 sütunu özgün 2022 bildirimi değildir. Satış ve vergi öncesi, ölçülen 99 firmanın 96’sında 2023 TMS 29 karşılaştırmalısıyla örtüşür. Finansal gider satırı (`3HC`) aynı karşılaştırmalı finansman gideriyle 98 firmanın 12’sinde örtüşür. Dipnot kırılımı, çıkan firma listesi ve bu örtüşmenin hesabı `MARJ_TUR3.md` içindedir. Aşağıdaki “kur farkı ayrılamadı” cümlesi, dipnotu kapanan 25 firma için artık geçerli değildir.

Kaynaklar bu turda yeniden okundu. Önceki turdaki sayılar iddia kabul edildi; aşağıya yalnız yeniden hesaplananlar yazıldı.

Hesap: firma değişimi = (2022 marjı − 2016 marjı) × 100. Sonra bu firma değişimlerinin medyanı, p25–p75 aralığı ve ortalaması. Çekirdek = (brüt kâr + pazarlama + genel yönetim + Ar-Ge) / satış. Bu tanım diğer faaliyet gelirini dışarıda bırakır. Faaliyet = XI_29 `3DF` / satış; bu satır diğer faaliyet gelir ve giderini içerir. Vergi öncesi = `3I` / satış. Net diğer = (`3DD` + `3DE`) / satış. Net finansman = (`3HB` + `3HC`) / satış. Net yatırım = (`3HA` + `3HAA`) / satış. Artık = vergi öncesi değişimi − (çekirdek + net diğer + net yatırım + net finansman). `3HAC` (özkaynak yöntemi) ve `3HCA` (vergi öncesi diğer) `marj_ham.csv` içinde yoktur; artığın içinde kalırlar.

Örneklem: İş Yatırım listesi, 16 Ekim 2026. Sıralama 2023 yıllık satış (`3C`). Banka, sigorta ve diğer finans aracıları dışarıda. Tam panel (2016–2023 satışı pozitif) 265 faaliyet firması. İlk 100’ün 2023 satış eşiği 7,63 milyar TL. Pencere 2016–2022. TÜFE, EVDS `TP.GENENDEKS.T1` aylık ortalaması: 2016 = 280,85; 2022 = 967,71.

## Üç cümle

En güçlü bulgu: ilk 100’de vergi öncesi marjın ortalaması 2016’dan 2022’ye +3,28 puandır ve bu ortalama, çekirdek −0,79 + net diğer faaliyet +0,30 + net yatırım +2,18 + net finansman +1,59 + artık −0,01 olarak kapanır; net yatırım ortalaması beş firmanın kuyruğudur (ECILC, TRALT, TRENJ, TRMET, ALCAR) ve onlar düşünce yatırım ortalaması −0,01 olur. Medyanlar toplanmaz: vergi öncesi medyan +2,14 puan (p25 −3,80; p75 +12,33), net finansman medyanı +2,79, çekirdek medyanı −0,98, net diğer medyanı −0,05’tir.

En büyük belirsizlik: `3HB` yüz tablosunda tek satırdır; kur farkı, faiz ve parasal kazanç 100 firmanın hiçbirinde ayrılamadı. Borsadan çıkan 18 firmanın 2022 tablosu bu kaynakta yoktur; çıkışın değişim medyanına etkisi belirlenemiyor. Hâlâ listede olup ilk 100 dışında kalanlarda net finansman değişiminin medyanı eksiye döner.

Sonraki adım: KAP dipnotundan `3HB` kırılımı (kur farkı, faiz, diğer, net parasal pozisyon kazancı) ve çıkan firmaların 2022 tabloları.

## 1. Finansman kırılımı

Etiket: yüz satırları için **hesaplandı**. Kur farkı / faiz / diğer ayrımı için **belirlenemiyor**.

Bulgu. “+2,1 puanın 2,8’i finansmandır” cümlesi bu dağılımda kurulamaz. Medyanların toplamı +1,92 puandır (çekirdek −0,98 + net diğer −0,05 + yatırım +0,16 + finansman +2,79 + artık 0,00). Vergi öncesi medyan +2,14 puandır. Ortalama kimliği kapanır:

| Kalem | Ortalama (puan) | Medyan | p25 | p75 |
| --- | ---: | ---: | ---: | ---: |
| Çekirdek | −0,79 | −0,98 | −5,98 | +3,25 |
| Net diğer faaliyet | +0,30 | −0,05 | −1,39 | +1,14 |
| Net yatırım | +2,18 | +0,16 | −0,14 | +0,77 |
| Net finansman | +1,59 | +2,79 | −2,68 | +9,53 |
| Artık | −0,01 | 0,00 | 0,00 | +0,04 |
| Vergi öncesi | +3,28 | +2,14 | −3,80 | +12,33 |

Ortalamada net finansman, vergi öncesi ortalamanın yaklaşık yarısıdır (+1,59 / +3,28). Kalan ortalama artışın büyük parçası net yatırımdır. Bu ortalama, beş firmanın 2016–2022 net yatırım marjı değişiminden gelir: ECILC +119,3, TRALT +29,5, TRENJ +27,1, TRMET +27,0, ALCAR +16,6 puan. Bu beş düşünce kalan 95 firmanın yatırım ortalaması −0,01 puandır. Aynı listenin alt ucu ENKAI −19,5, KARSN −13,5, AYEN −11,6’dır. Net diğer faaliyet, medyanda vergi öncesi artışı taşımaz.

İşaret: 100 firmanın 74’ünde net finansman değişimi ile vergi öncesi değişimi aynı işarettedir. Net finansman değişimi 63 firmada, vergi öncesi değişimi 61 firmada artıdır. Çekirdek değişimi 53 firmada gerilemiştir.

Artık mutlak değeri 1 puanı aşan 11 firma: DOAS, VESTL, AYGAZ, TKFEN, OYAKC, OTKAR, AKSA, TAVHL, NUHCM, CLEBI, ECILC. Bunlarda özkaynak yöntemi veya `3HCA` yüzdeki kimliği bozar. Medyan artık sıfırdır.

Kur farkı, faiz ve diğer. Bu turda EREGL’nin XI_29 şablonu yeniden çekildi: 147 satır. Finansal gelir tek kalemdir, `3HB` “(Esas Faaliyet Dışı) Finansal Gelirler”. Finansal gider tek kalemdir, `3HC`. “Net parasal pozisyon kazançları/kayıpları” satırı yoktur. `4BEA` parasal net yabancı para pozisyonudur; bu bir stoktur, TMS 29 kâr-zarar kalemi değildir. Finans sektörüne ait `3CAC` faiz satırı EREGL’de sıfırdır. `marj_ham.csv` bütün firmalar için `fin_gelir` ve `fin_gider`i tek sütunda tutar. Dipnot PDF’i okunmadı.

Ayrıştırılamayan firmalar: ilk 100’ün tamamı. Neden: yüz şablonunda `3HB` alt kalemsizdir; dipnot bu veri setinde yoktur. Firma firma dipnot tutarlılığı denetlenmedi. Bir firma kur farkını `3DD` diğer faaliyet gelirine yazmış olabilir; o tutar net diğer faaliyetin içindedir ve o kalemin medyan değişimi −0,05 puandır. Bu, hiçbir firmada kur farkının `3DD` içinde olmadığı anlamına gelmez.

## 2. Hayatta kalma yanlılığı

Etiket: 2016 düzeyi için **hesaplandı**. Çıkan firmaların 2016–2022 değişimi için **belirlenemiyor**.

Borsa İstanbul “İşlem sırası kapanan şirketler” dosyasında kapanma tarihi 2016-01-01 ile 2023-12-31 arasında olan 67 satır vardır. İsim kuralı (Türkçe İ katlanmış): faaliyet 38, holding 14, finans 6, fon 9. “YATIRIM” sözcüğü holdinge atar. Bu kural Beymen’i (BOYP, “Beymen Perakende ve Tekstil Yatırımları”) holdinge koyar; 2016 marjı çekilmedi. VIA GMYO (VIAGO) “GAYRİMENKUL” içermediği için faaliyete düştü; 2016 satışı boş olduğu için ölçüme girmedi.

Faaliyet satırlarından Adana A ve B (ADANA, ADBGR) aynı şirketin pay sınıfı olduğu için atıldı; ADNAC kaldı. İş Yatırım XI_29’dan 2016 ve 2022 istendi. Kullanılabilir 2016 marjı olan 18 firma var. `|çekirdek| > %100` veya `|vergi öncesi| > %200` olan ANELT ve BAKAN ölçek dışı bırakıldı. 2016 satışı boş olanlar: OZBAL, PMVR3, DMISH, AKPAZ, KRATL, FENIS, GEDIZ, HZNDR, UYUM, TARAF, VIAGO, MRTGG, PLASP, ARBUL, BOYNR, KILER.

2016 düzeyi, satışa oran:

| Grup | n | Çekirdek medyan | Çekirdek p25–p75 | Vergi öncesi medyan | Vergi öncesi p25–p75 |
| --- | ---: | ---: | --- | ---: | --- |
| Çıkan, ölçülebilen | 18 | %4,2 | −%4,1; +%17,4 | %10,4 | −%5,2; +%28,8 |
| İlk 100 | 100 | %8,3 | +%3,8; +%13,3 | %4,0 | −%1,2; +%10,1 |

Çekirdekte çıkanların 2016 medyanı, ilk 100’ün yaklaşık 4 puan altındadır. Vergi öncesinde çıkanların medyanı yaklaşık 6 puan üstündedir. Bu vergi öncesi fark, aynı gün kapanan iki işleme duyarlıdır. Çimento dördü (ADNAC, ASLAN, BOLUC, UNYEC; 2020-05-21) tek gözleme, cam dördü (SODA, TRKCM, DENCM, ANACM; Şişecam ile 2020-09-30) tek gözleme indirilince 12 gözlem kalır. Çekirdek medyanı −%1,7’ye iner; ilk 100 ile fark büyür. Vergi öncesi medyanı −%1,5’e iner; “çıkanların vergi öncesi marjı daha yüksekti” cümlesi bu birleştirmede durmaz. Çekirdek farkının yönü durur.

18 firmanın hiçbirinde 2022 satışı ve kârı bu çekimde dolu değildir (`delist_degisim_olan` boştur). OLMK 2022-10-20’de devrolunmuştur; 2022 sütunu yine boştur. Çıkanların 2016–2022 marj değişimi bu veriyle belirlenemiyor. Düzeltilmiş bir değişim medyanı yazılmadı.

Ayrı kanal: 16 Ekim 2026’da hâlâ listede olan, faaliyet grubunda, 2016 satışı pozitif, ilk 100’de olmayan firmalar. Bu, delist etkisi değildir; 2023 satışına göre küçük kalan hayatta kalanlardır.

| Ölçü | n | Medyan | p25 | p75 |
| --- | ---: | ---: | ---: | ---: |
| 2016 çekirdek, `|marj| ≤ 1` | 163 | %5,2 | −%2,5 | +%12,8 |
| 2016–2022 çekirdek değişimi, süzgeçsiz | 166 | +1,95 puan | −9,2 | +14,2 |
| Aynı değişim, `|2016 çekirdek| ≤ 1` ve `|değişim| ≤ 100` puan | 159 | +2,13 | −8,3 | +13,9 |
| Aynı süzgeç, vergi öncesi değişimi | 159 | +1,13 | −8,9 | +21,3 |
| Aynı süzgeç, net finansman değişimi | 159 | −2,27 | −13,0 | +10,0 |

Süzgeçsiz ortalamalar kullanılmadı: çekirdek değişiminin ortalaması bir firmanın (PRKME, 2016 çekirdeği −%1379) ölçeğinden +830 puana çıkar. Medyan okunur.

Yön. İlk 100’de çekirdek değişim medyanı −0,98 puandır. Listenin dışında kalan hayatta kalanlarda +2,13 puandır. İşaret tersine döner. Net finansman medyanı ilk 100’de +2,79, dışarıda −2,27 puandır; işaret yine tersine döner. Vergi öncesi medyan dışarıda da artıdır (+1,13), ilk 100’deki +2,14’ten küçüktür. Bu, 2023’te büyük olan hayatta kalanların seçimidir. Delist’in değişim medyanını ne kadar kaydıracağı belirlenemiyor.

## 3. Pay sınıfı birleştirme

Etiket: **hesaplandı**.

Ada göre `(A)/(B)/(C)/(D)` eki ve sekiz yılda satış oranı max/min < 1,005 taraması yapıldı. Faaliyet panelinde adı pay sınıfı olan tek grup Kardemir’dir: KRDMD, KRDMA, KRDMB. Satış oranı her yıl sabittir (D/A = 3,247; D/B = 6,531). Vergi öncesi / satış her yıl üç sınıfta aynıdır. A ve B, 2023 satış sıralamasında D’nin kopyasıdır.

MZHLD ile EPLAS’ın satış oranı yaklaşık 1,00’dır; vergi öncesi marjları aynı değildir (2021’de −%12,7 ve −%9,3). Pay sınıfı sayılmadı. EREGL / ISDMR satış oranı yıllar arasında 1,67 ile 2,06 arasındadır; marjlar aynı değildir. Konsolidasyon örtüşmesidir, birleştirilmedi. Bu örtüşmenin medyana etkisi ayrı ölçülmedi.

A ve B düşünce n = 98. Medyanlar (puan): çekirdek −0,65 (p25 −6,05; p75 +3,31), faaliyet +0,17, vergi öncesi +2,01 (p25 −4,37; p75 +11,81), net finansman +2,17. İlk 100’e göre çekirdek medyanı −0,98’den −0,65’e, finansman medyanı +2,79’dan +2,17’ye gelir. İşaretler durur.

Kota yeniden 100 tekil ihraççıya doldurulunca girenler FENER (hizmet) ve DGATE (ticaret). Çekirdek ve vergi öncesi medyanları n = 98 ile aynı kalır: −0,65 ve +2,01.

Sektör. A ve B ikisi de ana metaldir. n ≥ 8 olan beş sektörün medyanı birleştirmeden önce ve sonra aynıdır, çünkü düşen hisse o sektörlerde yoktur. Ana metal 7’den 5’e iner. Her iki n de 8’in altındadır; sektör sonucu yazılmadı. Ölçüm notu, sektör sonucu değildir: üç kez sayılan Kardemir, birleştirme öncesi ana metal vergi öncesi medyanını +13,5 puanda tutuyordu; A ve B düşünce bu medyan +0,9 puana iner ve n = 5 olduğu için sektör bulgusu sayılmaz.

DGATE ticarete eklenirse (n = 12) çekirdek medyanı +0,21’den +0,50’ye, vergi öncesi medyanı +2,68’den +2,55’e gelir. İkisi de n = 11’in p25–p75 aralığının içindedir. FENER hizmettedir; hizmet n = 4 olur, sektör sonucu yazılmaz.

## 4. Eşik duyarlılığı

Etiket: **hesaplandı**.

Beta, 2017–2022’de TÜFE ile arındırılmış satışın log farkının, `|satışların maliyeti|` log farkı üzerine OLS eğimidir. En az beş nokta. Bu, ithalat geçiş katsayısı değildir. İlk 100, n = 100: medyan 0,954; p25 0,898; p75 1,014; en düşük 0,554 (DEVA); en yüksek 1,803 (PGSUS). “Geçiş yüksek” burada beta ≥ eşik diye kodlandı. “Beta eşiğin altında ve çekirdek değişimi > +3 puan” hücresi ayrıca sayıldı.

| Eşik | Beta ≥ eşik | Eşiğin altında ve çekirdek > +3 puan |
| ---: | ---: | ---: |
| 0,5 | %100 (100/100) | 0 |
| 0,7 | %93 | 1 |
| 0,8 | %87 | 1 |
| 0,9 | %75 | 3 |
| 1,0 | %30 | 14 |

“Geçiş yüksek” payı eşiğe duyarlıdır: 0,5 ile 1,0 arasında 100’den 30’a iner. Medyan beta 0,95 bu eşiğin dışında, dağılımın yeridir; eşiğe duyarsız olan odur. 0,5’in altında firma yoktur. “Düşük beta ve yükselen çekirdek” hücresi 0,5 eşiğinde boştur; eşik 1,0’a çıkınca 14 firma girer. O hücrenin boşluğu 0,5 kuralına bağlıdır.

KRDMA ve KRDMB aynı betayı (0,617) üç kez sayar. İkisi düşünce n = 98’de paylar %100, %95, %89, %77 ve %31 olur. Duyarlılık aynı yerde durur.

## 5. TMS 29

Etiket: firma bayrağı için **belirlenemiyor**. 2022–2023 nominal satış artışı **hesaplandı**; bu artış TMS 29 uygulamasının ölçüsü değildir.

XI_29 yüzünde “enflasyona göre düzeltilmiştir” başlığı veya net parasal pozisyon kâr/zarar satırı yoktur. EREGL şablonu bu turda bunu gösterdi. Diğer 99 firmanın dipnotu okunmadı. Fonksiyonel para birimi TL olmayan istisnalar bu şablondan seçilemez. 2023 tablosunun firma bazında enflasyon düzeltmeli olup olmadığı bu veriyle belirlenemiyor.

2023 / 2022 yıllık ortalama TÜFE = 1.488,91 / 967,71 = 1,539 (%53,9). İlk 100’ün nominal satış artışının medyanı %51,0’dır (p25 %28,6; p75 %71,5). TMS 29 uygulansaydı 2023 ve karşılaştırmalı 2022 aynı satın alma gücünde olurdu; uygulanmasaydı ikisi nominal kalırdı. Ortanca büyümenin TÜFE’ye yakın olması bu iki durumu ayırmaz. 2022 ile 2023 arasındaki marj kıyasının güveni bu yüzden düşüktür. Birincil pencere 2016–2022 olarak bırakıldı. 2023’ü ayıran bir düzeltme köprüsü (raporlanan 2022 ile yeniden düzenlenmiş 2022) bu sette yoktur.

## 6. Kaynak uyumsuzluğu

Etiket: sayımlar ve satır tanımları **doğrudan gözlendi**. KAP imalat-benzeri alt kümenin marj değişimi **hesaplandı**. Boşluğun nedeni **belirlenemiyor**.

TCMB/TÜİK tekdüzen gelir tablosu, NACE Rev.2 bölüm C, sayfa t7. Değerler bin TL’dir; oranlar bundan etkilenmez. “Faaliyet karı veya zararı” satırı, F diğer olağan gelirden öncedir. F’nin içinde temettü, faiz, kambiyo kârları ve enflasyon düzeltmesi kârı vardır. “Dönem kar veya zararı” İngilizce karşılığı vergi öncesidir.

| TCMB C | 2016 | 2022 | Fark |
| --- | ---: | ---: | ---: |
| Faaliyet kârı / net satış | %7,68 | %11,76 | +4,08 puan |
| (Faaliyet + F − G) / net satış | %8,68 | %13,17 | +4,49 puan |
| Dönem kârı (vergi öncesi) / net satış | %4,46 | %9,06 | +4,60 puan |
| Net kambiyo / net satış | −0,12 puan | +0,21 puan | +0,33 puan |
| Kambiyo kârı / F | %74,4 | %82,2 | |
| Faiz geliri / F | %6,0 | %5,5 | |
| Net enflasyon düzeltmesi / satış | ~0 | −0,02 puan | |

KAP tarafı, ilk 100’den KRDMA ve KRDMB düşülmüş, ana sektörü gıda, kimya, otomotiv, ana metal, mineral, tekstil, dayanıklı tüketim, kâğıt veya makine olan 67 firma. Çekirdek değişim medyanı −0,97 puan (p25 −5,40; p75 +3,10). Faaliyet değişim medyanı −0,94 puandır. İşaret, TCMB C faaliyet kârı / satışın +4,08 puanlık artışıyla terstir.

Dört aday, her biri kendi kanıtıyla:

Holding ağırlığı. Olumlu kanıt: KAP örneklemi holdingleri faaliyet 100’ünden ayırır; TCMB C onları ayırmaz. Olumsuz kanıt ve sınır: gelir tablosu holding kırılımı vermez, firma düzeyi TCMB yoktur. Holdinglerin C içindeki satış payı bu veriyle belirlenemiyor. Ağırlık hipotezi ne doğrulandı ne elendi.

Muhasebe tanımı. Olumlu kanıt: aynı “faaliyet kârı” adı iki ayrı nesnedir. XI_29 `3DF` diğer faaliyet gelirini içerir. TCMB faaliyet kârı F’den öncedir; F kambiyo ve faizi taşır. Olumsuz kanıt: kıyas, adları hizalayarak da yapıldı. KAP çekirdeği diğer faaliyet gelirini dışlar; TCMB faaliyet kârı da F’yi dışlar. İkisi de kur ve faizi, o kalemler F veya `3HB` içindeyse, dışarıda bırakır. Bu hizalamadan sonra KAP medyanı geriler, TCMB oranı yükselir. TCMB net kambiyo satışa oranla +0,33 puan oynar; faaliyet kârı satırının +4,08 puanlık artışı F’nin dışındadır. Tanım farkı gerçektir ve bu boşluğu kapatmaz. Tekdüzen ile TFRS’nin faaliyet satırının içindeki karşılık, iskonto ve indirim farkı ayrıca ölçülmedi.

Örneklem kapsamı. Olumlu kanıt: TCMB C firma sayısı 2016’da 110.002, 2022’de 166.074’tür. Büyük ölçek 3.601’den 4.197’ye çıkar (temel göstergeler, t5, satır “Büyük”). KAP ölçüsü, 16 Ekim 2026’da duran ve 2023 satışı en büyük 100 faaliyet firmasıdır. Olumsuz kanıt: gelir tablosu ölçek sınıflarına bölünmemiştir. Büyük firmaların marjının küçüklerden farklı olup olmadığı bu dosyayla belirlenemiyor. Soru 2, listelenen küçüklerde çekirdek değişim medyanının artı olduğunu gösterir; bu, TCMB’nin yükselişiyle aynı işarettedir ve ilk 100 ile ters işarettedir. Bu bir bileşim ipucudur. TCMB’nin yükselişini ölçek bileşimine bağlamak için ölçek kırılımlı gelir tablosu gerekir; o tablo burada yoktur.

Sektör sınıflaması. Olumlu kanıt: TCMB ölçüsü bölüm C’nin tamamıdır. KAP “imalat-benzeri” küme, İş Yatırım ana sektörünün elle gruplanmasıdır ve NACE iki haneli ayrım değildir. Olumsuz kanıt: bu elle kümede de çekirdek medyanı −0,97 puandır. Boşluk, ana metal veya tek bir küçük sektörün ortalamayı çekmesiyle kapanmaz. C’nin içinde hangi alt bölümün marjının yükseldiği t7’de yoktur. Alt bölüm bileşimi belirlenemiyor.

Dört adaydan hiçbiri, diğerleri elenerek kabul edilmedi. Boşluğun yönü ölçülüdür. Nedeni bu veriyle belirlenemiyor.

## 7. Küçük örneklemli sektörler

Etiket: **hesaplandı**. Yazım kuralı: n < 8 ise sektör sonucu yok.

Birleştirme sonrası n < 8, sonuç yazılmayanlar: ana metal 5, dayanıklı tüketim 6, enerji 7, hizmet 3, kâğıt 1, madencilik 2, makine 3, tekstil 5, ulaştırma 6, inşaat 2. Gerekçe: medyan, bu sayılarda bir iki firmanın yer değiştirmesiyle oynar. Ana metaldeki pay sınıfı etkisi soru 3’te ölçüm notu olarak durur; sektör bulgusu değildir.

n ≥ 8. Sayılar 2016–2022 firma değişiminin puanıdır. Sıra p25 / medyan / p75.

| Ana sektör | n | Çekirdek | Faaliyet | Vergi öncesi | Net finansman |
| --- | ---: | --- | --- | --- | --- |
| Gıda ve içecek | 12 | −8,0 / +0,6 / +2,6 | −6,2 / +0,3 / +2,2 | −6,1 / +5,8 / +12,4 | −0,7 / +3,0 / +9,8 |
| Kimya | 10 | −9,3 / −2,8 / +2,9 | −6,2 / −1,9 / +2,0 | −1,8 / +2,0 / +3,2 | −4,5 / −1,0 / +5,8 |
| Mineral ürünler | 13 | −6,1 / −0,3 / +3,7 | −7,2 / −4,6 / +0,8 | −9,4 / −0,1 / +1,5 | −2,3 / −0,1 / +4,3 |
| Otomotiv | 12 | −3,0 / +2,0 / +3,7 | −5,3 / +1,1 / +5,4 | +0,6 / +4,5 / +8,8 | +0,6 / +5,3 / +9,2 |
| Ticaret | 11 | −1,8 / +0,2 / +1,1 | −0,9 / +0,3 / +2,7 | −0,2 / +2,7 / +10,3 | −1,0 / +5,4 / +11,8 |

Bu beş sektörde çekirdek medyanı −2,8 ile +2,0 puan arasındadır. Vergi öncesi medyanı mineralde −0,1, gıdada +5,8 puandır. Aralıklar medyanın iki yanında geniştir: gıdada vergi öncesi p25 −6,1, p75 +12,4’tür. Tek medyan bu dağılımı temsil etmez. Kimyada net finansman medyanı eksi, vergi öncesi medyanı artıdır; finansmanla vergi öncesi her sektörde aynı yönde değildir.

## A, B ve C bu turdan sonra

Bu tur ithalatı ve yerel tedariki test etmez. Beta, satış ile maliyetin eşhareketidir.

| Açıklama | Bu tur | Dayanak |
| --- | --- | --- |
| A. Dolaylı ithalat | Belirlenemedi | İthalat miktarı, girdi menşei ve yerel tedarik ölçülmedi. Beta eşiği soru 4’te duyarlıdır; bu, A’nın lehinde veya aleyhinde bir gözlem değildir |
| B. Fiyatlama gücü | Zayıfladı (0,5 kuralında); eşiğe bağlı parça duyarlı | Çekirdek medyanı −0,98 puandır. Beta < 0,5 ve çekirdek > +3 puan hücresi boştur. Eşik 1,0 olunca aynı hücreye 14 firma girer. B, medyan firmanın tarifi olarak zayıftır; “düşük beta”nın tanımı sonucu değiştirir |
| C. Muhasebe / finansman | Diğer faaliyet geliri zayıfladı. Finansman satırı ilk 100’de işaret olarak duruyor. Alt kalem ve örneklem nedeniyle yapısal diye belirlenemedi | Net diğer medyan −0,05. Ortalama kimliğinde finansman +1,59, yatırım kuyruğu +2,18. Medyanlar toplanamaz. Kur, faiz ve parasal kazanç ayrı değil. İlk 100 dışında finansman medyanı −2,27 puandır |

## Veri eksikleri

| Eksik veri | Kapatacağı soru |
| --- | --- |
| KAP dipnotunda finansal gelirin kur farkı, faiz ve diğer kırılımı; net parasal pozisyon kazancı | Soru 1 ve C’nin alt kalemleri |
| Çıkan firmaların 2017–2022 tabloları (İş Yatırım 2022 sütunu 18 firmada boş) | Soru 2’nin değişim yarısı |
| İsim kuralının yanlış kovasına düşen BOYP için ayrı sınıf ve 2016 marjı | Soru 2’nin 18 firma medyanının kenarı |
| TCMB gelir tablosunun ölçek ve holding kırılımı, ya da firma düzeyi | Soru 6, holding ağırlığı ve büyük/küçük marj |
| NACE iki haneli (bölüm içi) gelir tablosu | Soru 6, imalat içi bileşim |
| Firma bazında TMS 29 bayrağı ve 2022 raporlanan / 2022 yeniden düzenlenmiş köprü | Soru 5 |
| EREGL konsolidesi ile ISDMR’nin örtüşmesini ayıran konsolidasyon düzeltmesi | Soru 3’ün kenarı; medyan etkisi ölçülmedi |

## Eleştiriler

Dipnot tutarlılığı. Finansman ayrımı yüz satırına dayanır. EREGL şablonu `3HB`’nin tek satır olduğunu gösterir. Diğer 99 firmanın aynı ekonomik kalemi aynı satıra yazdığı denetlenmedi. Kur farkı bir firmada `3DD`, diğerinde `3HB` olabilir. Net diğer medyanının yerinde kalması, `3DD` içinde kur farkı olmadığı anlamına gelmez. Artık mutlak değeri 1 puanı aşan 11 firmada yüz kimliği zaten kapanmaz. Beş firmanın yatırım kuyruğu ortalama hikâyesini taşır; bu beşin yatırım gelirinin varlık satışı mı kur farkı mı olduğu dipnotsuz bilinemez.

Eşik keyfiliği. 0,8 önceki turun eşiğidir. “Yüksek geçiş” payı 0,5’te %100, 0,8’de %87, 1,0’da %30’dur. Dağılımın duran parçası medyan 0,95’tir. Beta, TÜFE ile arındırılmış satış ve maliyetin eğimidir; sektör ÜFE’si ile yeniden tahmin edilmedi. Kardemir üç kez sayılınca 0,8 payı %87, iki kopya düşünce %89 olur. Eşik cümlesi, medyan cümlesinden daha kırılgandır.

Dönem seçimi. 2016 ve 2022 iki uçtur; aradaki patika (2018 kur sıçraması, 2021–2022) firma medyanına ayrı yazılmadı. 2023, TMS 29 yılı olduğu için ana pencereden çıkarıldı. Bu, bilinen bir kırılmayı karıştırmaktan kaçınır ve aynı anda 2023’ü sessizce düşürür. Firma bazında düzeltme bayrağı olmadığı için 2022–2023 marj farkı yorumlanmadı. Sıralama yılı da 2023 satışıdır. Bu seçim, soru 2’de çekirdek ve finansman değişiminin işaretini, listenin dışındaki hayatta kalanlara göre ters çevirir. Pencereyi veya sıralama yılını değiştirmek sonucu değiştiriyor; tek pencere yapısal bir olgu gibi okunamaz.

## Kapanış

Bu analizin hiçbir sonucu “ithalat yok” tezini kanıtlamaz veya çürütmez. İthalat miktarı ve yerel tedarik ölçülmedi.

Asıl soru, faaliyet dışı kârın yapısal bir olgu mu yoksa ölçüm ve örneklem etkisi mi olduğudur. Bu sette ikisi ayrışmıyor. İlk 100’ün içinde net diğer faaliyet medyanda artmaz; vergi öncesi medyan ile net finansman medyanı aynı işarettedir; ortalamada finansman, vergi öncesi ortalamanın yaklaşık yarısıdır ve kalan ortalama bir yatırım kuyruğudur. Aynı finansman medyanı, 2023 satışına göre küçük kalan hayatta kalanlarda eksiye döner. Kur, faiz ve parasal kazanç ayrılmamıştır. Çıkan firmaların değişimi gözlenmemiştir. 2023 TMS 29 etkisi firma bazında ayrılmamıştır. Faaliyet dışı kâr bu örneklemde vardır; yapısal mı, büyük ve hayatta kalan firmaların ölçümü mü, bu veriyle belirlenemiyor.
