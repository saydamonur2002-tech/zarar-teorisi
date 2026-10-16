# Ön kayıt — dış borçta sahip ve ödeyen

Yazıldı: 2026-10-16, stok ve akım değerleri çekilmeden. Eşikler değişmez.

## Kaynaklar, bu turda seri listesinden okundu

Brüt dış borç, TCMB, milyon ABD doları. Birim, Dış Borç Metaveri belgesinde “tüm değişkenler milyon ABD doları” diye yazıyor. Belge 12 Mart 2026. Kısa vade, aynı belgede orijinal vadesi bir yıla kadar olandır. Vadeye kalan süre değildir.

Ödemeler dengesi ayrıntılı sunum, BPM6, milyon ABD doları. Birim, Ödemeler Dengesi Metaveri belgesinde yazıyor. Finans hesabı net işlem taşır. Uzun vadeli kredide kullanım ve geri ödeme ayrı satırdır. Kısa vadeli kredide bu ayrım yoktur.

Kısa vadeli dış borç istatistiği, KVDB metaverisi, milyon ABD doları. Kısa vade yine orijinal vadedir. Grup adı “kalan vadeye göre” diye durur. Metaveri adı kısa vadeli dış borçtur. Karar, metaverideki orijinal vade tanımındadır.

UYP stok tablosunda işlem, değerleme ve diğer hacim satırı yok. Katalogda bu üçlüyü veren ayrı bir grup da yok.

## Karar

S1. Kamu payı, SDDS genel hükümet `TP.BRUTDBSDDS.G2` bölü SDDS toplam `TP.BRUTDBSDDS.G1`. Kamu dışı pay, bir eksi bu orandır. Eşik yüzde 50’dir. Kamu dışı pay bunun üstündeyse S1 desteklenir. Karar dönemi, toplamın son yayımlanan çeyreğidir.

Toplam, genel hükümet + merkez bankası + bankalar + diğer sektörler + doğrudan yatırım borç ilişkisi ile yüzde 1’den fazla ayrılırsa pay yazılmaz. Borçlu tablosundaki genel hükümet ile SDDS genel hükümet, toplamın yüzde 1’inden fazla ayrılırsa S1 belirlenemiyor olur. Borçlu tablosundaki “kamu” satırı genel hükümet değildir. Kamu bankasını ve KİT’i de taşır. S1 paydasına girmez. Yanında raporlanır.

S2. Kısa vadeli brüt geri ödeme ve kısa vadeli brüt yeni kullanım yayımda yok. Kısa vadeli satır nettir. Uzun vadeli kredi kullanımı onun yerine konmaz. Çevirme oranı onun yerine konmaz. S2 belirlenemiyor kalır. Oran 1 eşiği durur, uygulanmaz.

S3. Ödeme payı, brüt dış borcun tamamını kapsayan bir geri ödeme ister. Uzun vadeli kredi anaparası bu bütün değildir. Yüzde 10 puan eşiği bu dar akıma uygulanmaz. S3 belirlenemiyor kalır.

S4. Kur kırılımı sektörde yoksa sektör şoku yazılmaz. Toplamda TL satırı varsa döviz payı, bir eksi TL bölü toplamdır. Bileşenler toplamdan yüzde 1’den fazla saparsa pay yazılmaz. Borç/GSYH şoku yazılmaz. Metaveri, stoku referans paritesiyle dolara çevirir ve paritenin seri kodunu vermez. Kod verilmeden kur seçilmez.

## Özdeşlik

Stok değişimi = işlem + değerleme + diğer hacim. Üç sağ kalem aynı sektörde yayımlı değilse artık yazılmaz. Yüzde 5 eşiği, kurulmamış bir artığa uygulanmaz. Stok farkı geri ödeme sayılmaz.

## Akışın yazılacağı yer

Uzun vadeli kredi anaparasında kullanım ve geri ödeme gözlenen satırdır. Tahmin diye yazılmaz. Kısa vade, borç senedi, mevduat ve ticari kredi için brüt geri ödeme satırı yoksa o hücre belirlenemiyor kalır. İşaretler aynı yönde değilse oran yazılmaz. Bu oran S2 değildir.

Sahip ile ödeyen tablosu, akımın tam takvim yılı ile aynı yılın dördüncü çeyrek stokunu yan yana koyar. Son çeyrek yıl sonu değilse S1 son çeyrekte kalır. Tablo, tam yılın stokunu kullanır.

Hata ve noksan, sektör ödemesi değildir. Aynı tam yılın toplamı not edilir.
