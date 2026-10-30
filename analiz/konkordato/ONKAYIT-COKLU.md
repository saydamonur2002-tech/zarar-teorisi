# Ön kayıt — çoklu etiket (ikinci tur)

Yazım: yeni veri çekilmeden önce. Bu dosya kilitlidir. `ONKAYIT.md` duruyor; o turun tek-mekanizma kuralı burada geçerli değildir. Eşikler, VE/VEYA mantığı ve çürütme paydası sonradan değişmez. Satır yoksa etiket VERİ YOK olur. VERİ YOK, hayır değildir. Eşik, veri gelsin diye gevşetilmez.

Pencere: KAP duyurusu 1 Ocak 2022 – 25 Ekim 2026. Birincil grup: duyuru tarihinde Borsa İstanbul’da işlem gören ortaklık. Banka, sigorta, finansal kiralama, faktoring ve aracı kurum dışarıda; listeye düşerse “dışlandı” yazılır, paydaya girmez.

İkincil grup, ancak halka açık olmadığı hâlde gelir tablosu ve bilançosu kamuya açıksa (ilan.gov.tr, ticaret sicili, konkordatotakip) ele alınır. Satırları birincil grupla aynı değilse ateşleme paydasına girmez. Kapsamı ve eksiği raporda ayrı yazılır.

## Zaman

- t0: KAP’taki ilk konkordato başvurusu, geçici mühlet veya kesin mühlet tarihi. Kelime yoksa yapılandırma veya düz iflas t0 sayılmaz.
- t−1: t0’dan önce bitmiş son mali yıl. t−2 ve t−3 ondan önceki iki yıl.
- t−1 yıl sonu ile t0 arasında 18 aydan uzun boşluk varsa o firmanın tüm etiketleri VERİ YOK. Yıl, çeyrekle doldurulmaz.

## Ortak satırlar

- Faaliyet kârı: esas faaliyet kârı/zararı. Net parasal pozisyon kazancı bu satırın içinde değildir. A ve A0 bu satırı kullanır. Parasal kazanç dahil edilmiş faaliyet kârı ayrıca yazılır ve etiketi değiştirmez.
- Finansman gideri: kâr veya zarar tablosundaki finansman giderleri satırının mutlak değeri. Dipnotta faiz, kur farkı ve diğer ayrılır. Ayrılmıyorsa “ayrılamadı” yazılır. A, ayrılmış faizi değil bu satırı kullanır. Faiz-only oran betimlemedir, tetik değildir.
- FAVÖK = esas faaliyet kârı + nakit akışındaki amortisman ve itfa. Amortisman yoksa FAVÖK bulamadım. Net borç/FAVÖK betimlemedir, tetik değildir.
- Net parasal pozisyon kazancı kendi satırıdır. Yoksa “bulamadım”. TMS 29, 31 Aralık 2023 ve sonrası yıllık tablolarda vardır. KAP özeti, yılın kendi cari sütunudur; sonraki raporun yeniden düzenlediği önceki yıl, o yılın yerine konmaz. Aynı sütunun içindeki oran kullanılır. İki yılın TL seviyesi, köprü yoksa bağlanmaz. Boyutsuz oran (devir günü, faaliyet/gider) her yıl kendi sütununda kurulursa TMS 29 kırılması oranı bozmaz.
- Net döviz pozisyonu: döviz pozisyonu dipnotundaki net yabancı para varlık/(yükümlülük). Dipnot yoksa C’nin birinci bacağı VERİ YOK. Özet satıcı serisi dipnot yerine geçmez.
- Kur farkı zararı: dipnottaki net kambiyo (zarar eksi kâr). Yalnız brüt zarar varsa onu kullan ve “netlenemedi” yaz. Satır yoksa ikinci bacak VERİ YOK.
- Ticari alacak: kısa ve uzun vade, şüpheli karşılık düşülmüş bilanço toplamı. İlişkili taraf payı ayrıca yazılır, B’nin tetiği değildir.
- Alacak devir süresi (gün) = ((dönem başı + dönem sonu) / 2) / hasılat × 365. Dönem başı, aynı satın alma gücündeki açılış veya karşılaştırmalı kapanıştır. Başka fiyat düzeyindeki önceki kapanış, dönem başı sayılmaz. Hasılat ≤ 0 ise o yılın günü VERİ YOK.
- Kısa vadeli borç: kısa vadeli yükümlülükler. Dönen varlık: dönen varlıklar. Nakit: nakit ve nakit benzerleri. Kısa vadeli finansal borç: kısa vadeli borçlanmalar. Ticari borç bunun yerine konmaz.
- Nakit akışındaki kredi kullanımı ve geri ödemesi betimlemedir. E’yi tek başına tetiklemez.

## Etiket mantığı

Her mekanizma için ayrı hücre: evet, hayır veya VERİ YOK. Bir firma birden fazla evet taşıyabilir. Tek baskın neden yok.

VE kuralı: iki bacak da evet ise evet. Biri hayır ise sonuç hayır, diğer bacak VERİ YOK olsa bile. Biri evet, diğeri VERİ YOK ise sonuç VERİ YOK. İkisi de VERİ YOK ise VERİ YOK.

VEYA kuralı: biri evet ise evet. İkisi de hayır ise hayır. Biri hayır, diğeri VERİ YOK ve evet yoksa sonuç VERİ YOK.

## A — Faiz yükü

A ancak t−2 ve t−1 için ikisi birden varsa ateşler: faaliyet kârı > 0 ve faaliyet kârı / finansman gideri < 1. Finansman gideri sıfır veya eksikse o yıl VERİ YOK ve A VERİ YOK olur. Yıllardan birinde faaliyet kârı ≤ 0 ise A hayırdır. İki yıl da artı ve en az bir yılda oran ≥ 1 ise A hayırdır.

## A0 — Faaliyet zararı

A0, t−1 faaliyet kârı < 0 ise ateşler. t−1 ≥ 0 ise hayır. t−1 yoksa VERİ YOK. t−2’nin işareti yazılır, tek başına A0 yakmaz. A ve A0 aynı firmada birlikte evet olamaz: A, t−1 faaliyet kârının artı olmasını ister.

## B — Tahsilat zinciri

B, devir süresi(t−1) / devir süresi(t−3) − 1 > 0,30 ise ateşler. t−3 günü yoksa, dönem başı yoksa veya iki yıl farklı fiyat düzeyinde seviye olarak bağlanmışsa B VERİ YOK. Oran uzamamışsa veya kısalmışsa hayır. t−3 günü sıfırsa VERİ YOK.

## C — Döviz uyumsuzluğu

t−1, VEYA kuralı.

- Bacak 1: özkaynak > 0 ve net döviz pozisyonu / özkaynak < −0,40. Özkaynak ≤ 0 ise bacak VERİ YOK. Yerine aktif oranı konmaz.
- Bacak 2: vergi öncesi kâr < 0 ve net kur farkı zararı ≥ 0,25 × |vergi öncesi zarar|. Vergi öncesi kâr ≥ 0 ise bacak hayır. Kur satırı yoksa VERİ YOK.

## E — Likidite / refinansman

t−1, VE kuralı.

- Bacak 1: kısa vadeli yükümlülükler / dönen varlıklar > 1. Dönen varlık ≤ 0 ise VERİ YOK.
- Bacak 2: nakit ve nakit benzerleri / kısa vadeli finansal borç < 0,30. Kısa vadeli finansal borç = 0 ise bacak hayır. Satır yoksa VERİ YOK.

## D — Stratejik / fırsatçı

Dört bayrak. Tutar ve aktife oran yazılır.

1. t−2 veya t−1’de nakit kâr payı > 0 ve aynı yıl net kâr < 0 veya faaliyet kârı < 0.
2. t−1 ticari olmayan ilişkili taraf alacağı veya borcu / toplam aktif > 0,15.
3. t0’dan önceki 24 ayda ilişkili tarafa varlık satışı ve bedel / t−1 aktif > 0,05. Satış var, bedel yoksa bu bayrak VERİ YOK.
4. İlan sonrası mahkeme gerekçesinde kötüniyet, muvazaa veya alacaklıdan mal kaçırma. Yalnız ret veya iflasa geçiş bu bayrak değildir.

D, VEYA ile kurulur: bayrak 4 evet ise D evet. Değilse D1–D3 arasında en az iki evet varsa D evet. Bayrak 4 hayır ve D1–D3 içinde ikiden az evet var ve kalanlar hayır ise D hayır. Eksik bayrak, iki eve ulaşmayı hâlâ mümkün kılıyorsa D VERİ YOK.

## Kontrol

Her birincil firmaya en az iki kontrol.

- Aynı KAP sektörü. Sektör alanı okunamazsa aynı iş kolu yazılır ve “resmî sektör kodu yok” denir.
- t−1 toplam aktifi, incelenen firmanın 0,50 ile 2,00 katı. Bant gevşetilmez.
- 1 Ocak 2020 – 25 Ekim 2026 arasında konkordato, iflas veya iflas erteleme duyurusu yok.
- Kâra, faiz oranına ve nakde bakılarak seçim yapılmaz.
- Bantta ikiden fazla aday varsa |ln(aktif_kontrol / aktif_firma)| en küçük iki firma alınır.
- Kontrolün t−1’i, eşleştiği firmanın t−1 takvim yılıdır. Aynı eşikler.
- İki kontrol bulunamazsa o firma için “ayırt eder” denmez.
- Ayırt etme hesabında kontrolün de o mekanizma için etiketi evet veya hayır olmalıdır. Kontrol VERİ YOK ise o kontrol, o mekanizmanın farkına girmez.

## Çürütme

Mekanizma X için atanabilen firma, etiketi evet veya hayır olan firmadır. VERİ YOK paydaya girmez ve X’i çürütmez.

X çürümüş sayılır, eğer atanabilen birincil firmalarda evet oranı yüzde 20’nin altındaysa, ya da kontrol ateşleme oranı hesaplanabiliyor ve (birincil oran − kontrol oranı) 20 puandan küçükse.

Kontrol oranı hesaplanamıyorsa ikinci bent “test edilemedi”dir, tek başına çürütme değildir. Bu durumda “ayırt edicidir” denmez. Birinci bent durur.

Evet sayısı bir veya iki ise kategori oranı bulgu diye anlatılmaz. O firma veya iki firma hikâye edilir. Yüzde yine çürütme başlığında aritmetik olarak yazılır. Anlamlılık iddiası yok.

İkincil grup bu paydalara girmez.

## Kaynak sırası

KAP finansal raporu ve dipnotu [VERİ]. KAP özetindeki cari sütun, dipnotla çelişmiyorsa [VERİ]. Burada bölünen oran [HESAP]. Haber ve veri satıcısı, KAP satırıyla doğrulanmadan [İKİNCİL]. KAP cari sütunuyla tutmayan satıcı serisi [DOĞRULANMADI] ve ateşlemez. Bulunamayan satır “bulamadım”, etiket VERİ YOK.

## Bu dosyadan sonra yasak

Eşik, VE/VEYA, kontrol bandı, iki kontrol şartı ve yüzde 20 paydası değişmez. Parasal kazanç, faiz-only oran, net borç/FAVÖK ve nakit akış işareti sonradan tetik yapılmaz.
