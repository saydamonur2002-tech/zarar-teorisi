# Ön kayıt — konkordato mekanizmaları

Yazım zamanı: veri çekilmeden önce. Bu dosya kilitlidir. Eşikler, atama sırası ve çürütme koşulları sonradan değiştirilmez. Veri bir eşiği uygulanamaz kılarsa eşik gevşetilmez; o test o firma için tutmaz ve mekanizma ateşlemez.

Kapsam yılı: KAP duyurusu 1 Ocak 2022 – 25 Ekim 2026. Yalnız Borsa İstanbul’da işlem gören (veya ilan tarihinde görüp sonra borsadan çıkan) ortaklıklar. Banka, sigorta, finansal kiralama, faktoring ve aracı kurumlar örneklem dışı: faaliyet kârı, ticari alacak ve finansman gideri satırları bu kurumlarda aynı anlama gelmez. Listeye girerlerse “dışlandı” diye yazılır, analize sokulmaz.

## Zaman penceresi

- t0: KAP’taki ilk “konkordato başvurusu”, “geçici mühlet” veya “kesin mühlet” duyurusunun tarihi. Yalnızca “borç yapılandırma”, “iflas” veya “iflas erteleme” (konkordato kelimesi yoksa) t0 sayılmaz.
- t−1: t0’dan önce bitmiş son mali yıl. t−2 ve t−3 ondan önceki iki mali yıl.
- t−1 mali yıl sonu ile t0 arasında 18 aydan uzun boşluk varsa veri bayat sayılır; firma “belirsiz” kalır, eşik gevşetilmez.
- Çeyrek dönem, eksik yılı doldurmak için kullanılmaz.

## Ortak tanımlar

- Faaliyet kârı: kâr veya zarar tablosundaki “Esas faaliyet kârı/zararı”. Zarar negatiftir.
- Finansman gideri: aynı tablodaki “Finansman giderleri” satırının mutlak değeri. Finansman gelirinden netlenmez. Yalnızca net finansman gideri varsa A tutmaz; satır [DOĞRULANMADI] kalır.
- FAVÖK ve net borç/FAVÖK yalnızca betimlenir. Atama tetikleyicisi değildir.
- Faiz karşılama oranı (atanan tanım): faaliyet kârı / finansman gideri. Finansman gideri sıfır veya eksikse oran tanımsızdır, A tutmaz.
- Ticari alacak devir süresi (gün) = (ortalama ticari alacak / hasılat) × 365. Ortalama = (dönem başı + dönem sonu) / 2. Dönem başı yoksa B tutmaz; kapanış bakiyesiyle ikame edilmez.
- Hasılat: “Hasılat” satırı. Yoksa net satışlar.
- Net döviz pozisyonu: yabancı para pozisyon dipnotundaki (YP varlıklar − YP yükümlülükler). Açık pozisyon negatiftir. Dipnot yoksa C tutmaz.
- Kur farkı zararı: finansman gideri dökümünde ayrı gösterilen net kur farkı gideri. Ayrı satır yoksa C’nin ikinci bacağı tutmaz. “Finansman giderinin içindedir” diye tahmin edilmez.
- Kısa vadeli borç oranı = kısa vadeli yükümlülükler / toplam yükümlülükler. Atama tetikleyicisi değildir.
- Banka kredisi, finansal borç dipnotundaki banka kredileridir. Ticari borç, finansal durum tablosundaki ticari borçlardır. İkisi birbirinin yerine konmaz.

## TMS 29

- 31 Aralık 2023 ve sonrası biten yıllık hesap dönemlerinde TMS 29 uygulanmış tablolar enflasyon muhasebelidir. 2023 tablosunun yeniden düzenlenmiş 2022 karşılaştırması varsa o sütun kullanılır ve [TMS29-düzeltilmiş] yazılır.
- Yeniden düzenlenmiş köprü yoksa 2022 öncesi nominal TL ile 2023 sonrası düzeltilmiş TL seviye olarak birbirine bağlanmaz.
- A ve C aynı sütunun içindeki oranlardır; tek yıl içinde TMS 29 pay ve paydayı birlikte etkilediği için kullanılabilir.
- B’nin 45 gün ve 8 puan testleri iki yılı karşılaştırır. İki yıl farklı muhasebe esasına oturuyorsa ve TMS 29 köprüsü yoksa B tutmaz.

## A — Faiz yükü

A, hem t−2 hem t−1 için faaliyet kârı < finansman gideri ise ateşler (oran < 1). İki yıldan biri eksikse, gider sıfırsa veya yalnızca net finansman satırı varsa A ateşlemez.

## B — Tahsilat zinciri

B ancak üçü birden varsa ateşler:

1. Devir süresi(t−1) − devir süresi(t−3) ≥ 45 gün. t−3 yoksa B ateşlemez.
2. (Ticari alacak / hasılat)(t−1) − (Ticari alacak / hasılat)(t−3) ≥ 0,08.
3. Hasılat(t−1) > 0,50 × hasılat(t−3), aynı muhasebe esasında. Satış yarıdan fazla düşmüşse oran artışı payda çöküşü olabilir; B ateşlemez, “satış çöküşü” diye not düşülür.

## C — Döviz uyumsuzluğu

C ancak iki bacak birden tutarsa ateşler.

Bacak 1, t−1:

- Özkaynak > 0 ise net döviz pozisyonu / özkaynak ≤ −0,40.
- Özkaynak ≤ 0 ise oran tanımsızdır. Bu durumda net pozisyon negatif ve |net pozisyon| / toplam varlık ≥ 0,15 ise bacak 1 tutulmuş sayılır. Hangi bent kullanıldığı yazılır.

Bacak 2, t−1, ayrı kur farkı satırı varsa:

- Vergi öncesi kâr < 0 ise net kur farkı zararı ≥ 0,25 × |vergi öncesi zarar|, veya
- Faaliyet kârı > 0 ise net kur farkı zararı ≥ faaliyet kârı.

İkisi de yoksa (faaliyet kârı ≤ 0 ve vergi öncesi kâr ≥ 0) bacak 2 tutmaz.

## D — Stratejik / fırsatçı kullanım

Dört bayrak:

1. Temettü: t−2 veya t−1’de nakit kâr payı, ve aynı yıl faaliyet kârı < finansman gideri veya net zarar.
2. İlişkili taraf: t−1’de ticari olmayan ilişkili taraf alacağı veya borcu > toplam varlığın %15’i.
3. İlandan önceki 24 ayda KAP metninde ilişkili tarafa varlık satışı, devir veya grup içi borç yapılandırması.
4. İlandan sonra mahkeme gerekçesinde kötüniyet, muvazaa veya alacaklıdan mal kaçırma. Yalnızca “proje reddedildi” veya “iflasa geçti” bu bayrak değildir; gerekçe metni gerekir.

Kötüniyet bayrağı (4) tek başına D atar; A, B veya C ateşlese bile. Bu, mahkeme bulgusunun operasyonel eşiği ezdiği tek istisnadır.

Bayrak 4 yoksa D ancak şu halde ateşler: 1–3 arasından en az iki bayrak var ve A, B, C’den en fazla biri ateşlemiş. İki veya üç operasyonel mekanizma ateşlemişse D kazanamaz; firma zaten belirsizdir.

## Tek mekanizma ataması

Sırayla, ilk uyan kuralda dur:

1. Bayrak 4 varsa → D.
2. A, B, C’den tam biri ateşlemişse → o harf. Bayrak 4 dışındaki D işaretleri bunu değiştirmez.
3. A, B, C’den hiçbiri ateşlememiş ve D’nin iki bayrak kuralı tutmuşsa → D.
4. Geri kalan her şey → belirsiz. Buna iki veya üç operasyonel mekanizmanın birden ateşlemesi, hiçbirinin ateşlememesi ve eşiği hesaplatmayan eksik veri girer.

Belirsiz, “veri yok” ile aynı değildir. Notta ikisi ayrılır: “eşikler tutulmadı” ve “veri eşiği hesaplatmadı”.

## Kontrol grubu

Her konkordato firmasına bir kontrol:

- Aynı KAP sektörü.
- Halka açık, 2020–2026 arasında konkordato, iflas veya iflas erteleme duyurusu yok. Borç yapılandırması duyurusu olan firma kontrol olamaz.
- t−1 toplam varlıkları, incelenen firmanın t−1 toplam varlıklarının 0,50 ile 2,00 katı arasında.
- Bu aralıkta aday yoksa 0,33–3,00 katına gevşetilir ve “ölçek gevşek” yazılır. Yine yoksa aynı sektörde varlıkça en yakın firma alınır, “ölçek gevşek” kalır.
- Kârlılığa göre eşleştirme yapılmaz.
- Kontrolün penceresi, eşleştiği firmanın t−1 takvim yılıdır. Aynı eşikler uygulanır.
- Kontrol bulunamazsa o firma için mekanizma cümlesi kurulmaz; yalnız “atanamadı” denir.

## Ne mekanizma iddiasını çürütür

Bir harf, konkordato firmalarını kontrollerden ayırt ediyor sayılmazsa o mekanizmanın “konkordatonun nedeni” olduğu iddiası düşer. Ayırt etme kuralı, dondurulmuş halde:

- İncelenen firmalarda o harfin ateşleme oranı, kontrollerdeki ateşleme oranından en az 20 puan yüksek olacak.
- Ve o harfe atanan konkordato firması sayısı en az 3 olacak.

Ateşleme oranı, atama oranı değildir. A ateşleyip belirsizde kalan firma, A’nın ateşleme oranına girer; atama tablosuna girmez.

Aşağıdaki sonuçlardan biri çıkarsa ilgili cümlede “yanılmışım” yazılır:

- A’nın ateşleme farkı 20 puanın altındaysa: faiz yükü sağlam halka açık firmada da yaygın olabilir; konkordatoyu ayırt etmez. Yanılmışım.
- B’nin ateşleme farkı 20 puanın altındaysa: alacak süresi sektörün ortak derdi olabilir. Yanılmışım.
- C’nin ateşleme farkı 20 puanın altındaysa: döviz açığı konkordato firmasına özgü değildir. Yanılmışım.
- D’ye atanan firma 3’ün altındaysa veya kontrollerde de iki D bayrağı aynı sıklıktaysa: fırsatçı kullanım bu listeden genellenemez. Yanılmışım.
- Modal kategori belirsizse, ya da hiçbir harf 20 puan ve en az 3 atama şartını birlikte tutmuyorsa: tek baskın kanal hikâyesi tutmamıştır. Üç mekanizmadan birinin tipik konkordato nedeni olacağını bekliyordum. Yanılmışım.

Küçük örneklemde anlamlılık iddiası yok. Yalnızca sayım ve desen.

## Kaynak önceliği

- Duyuru ve mali tablo için önce KAP (kap.org.tr) PDF’i. Bu [VERİ].
- KAP’tan satır okunup burada oranlandıysa [HESAP].
- İş Yatırım, Fintables, şirket sitesi veya basın, KAP ile doğrulanmadan [İKİNCİL]. KAP ile çelişirse KAP geçerli.
- Bulunamayan satır “bulamadım”. Tahmin “tahmin” ve atamaya girmez. Doğrulanamayan [DOĞRULANMADI].

## Bu dosyadan sonra yasak

Eşik, atama sırası, kontrol aralığı ve çürütme puanı değiştirilmez. Yeni bir atama tetikleyicisi eklenmez. Net borç/FAVÖK, kısa vadeli borç oranı ve FAVÖK seviyesi sonradan “asıl neden” diye kullanılmaz.
