# Ön kayıt — kalan vade stokunun aylık artışı

Yazıldı: 2026-10-16. Bileşen değerleri çekilmeden. Eşikler değişmez.

## Kavram

Karar ayı, 2026-07 eksi 2026-06’dır. Stok, `TP.KALANVADE.K20`. Bu, kalan vadeye göre bir yıl ve daha kısa dış borç stokudur. Yükümlülük stokudur. Geri ödeme akımı değildir.

Orijinal vade stoku `TP.BRUTDBORCLU.G19` başka kavramdır. K20’ye eklenmez. K20’den çıkarılmaz. K20’nin paydası yapılmaz.

Özdeşlik: ΔStok = yeni kısa vadeli borçlanma − kısa vadeli geri ödeme + vade geçişi + değerleme + diğer hacim. Her bileşen ayrı yazılır. Yayımlı olmayan bileşen sıfır yazılmaz. Artık, ancak sağdaki bileşenlerin hepsi ölçülmüşse yazılır. Biri belirlenemiyorsa artık yazılmaz. Yüzde 5 eşiği, kurulmamış bir artığa uygulanmaz.

Değerleme, stokun dolar karşılığının para birimi paritesinden gelen kısmıdır. TL’nin ekonomiye etkisi diye okunmaz. Parite, bu stokun metaverisinde adı yazılı bir seri ise kullanılır. Ad yoksa parite seçilmez.

## Eşikler

S1. Vade geçişi / ΔStok > yüzde 50 ise artış, yeni borçlanma değil, mevcut borcun zamanlamasıdır. Vade geçişi hesaplanamıyorsa S1 belirlenemiyor kalır.

S2. Dolar dışı pay ile dolar paritesi değişiminin çarpımı, ΔStok’un yüzde 10’unu aşıyorsa değerleme önemlidir. Stok artışı borçlanma diye yorumlanmaz. Pay ya da parite yoksa S2 belirlenemiyor kalır.

S3. Kısa vadeli brüt borçlanma / brüt geri ödeme > 1 ise stok yeni borçlanmayla yenileniyor. Yalnız brüt akışla test edilir. Net akışla oran yazılmaz. Brüt satır yoksa S3 belirlenemiyor kalır.

S4. Diğer hacim ve artık, ΔStok’un mutlak değerinin yüzde 5’ini aşarsa bu bir veri ya da kapsam sorunudur. Bileşen yorumu yazılmaz. Artık kurulmamışsa S4 belirlenemiyor kalır.

Eşikler: yüzde 50, yüzde 10, oran 1, yüzde 5.

## Veri kapısı

Bu kapı kapanmadan bileşen hesaplanmaz.

K20’nin ilk ayı, son ayı ve gözlem sayısı seri listesinden ve çekimden okunur. Aylık değişim, en az 12 gözlem yoksa yorumlanmaz. İki uç hücre yine de yazılır.

Para birimi bileşimi, kalan vade stokunun kendi tablosu ise S2’ye girer. `TP.BRUTDBDOVKOMP.G1`–`G7` brüt dış borcun döviz dağılımıdır. Kalan vade stoku değildir. Bu pay, K20’nin değerlemesine konmaz. Kalan vade stokunun kendi döviz tablosu yoksa değerleme belirlenemiyor kalır.

Ödemeler dengesi finansal hesabında kısa ve uzun vade, sektör ve yön kırılımlı aylık seri aranır. Seri listesinde yoksa kod yok yazılır. Net satır, brüt borçlanma ve brüt geri ödeme yerine konmaz.

Uzun vadeli kredi kullanımı ve geri ödemesi, `TP.ODEAYRSUNUM6` altında seri listesinde duruyorsa gözlenen akım diye yazılır. Vade geçişi değildir. Vade geçişi, kredi bazında anapara takvimi ya da bu stok için yayımlanmış bir vade geçişi satırı ister. İkisi de yoksa vade geçişi belirlenemiyor kalır.

Birim milyon ABD doları değilse o seri bileşene girmez. TL ile dolar karıştırılmaz.

Kalem stokunun aylık farkı (genel hükümet, banka kredisi, mevduat) özdeşliğin bileşeni değildir. Yeni borçlanma, geri ödeme, vade geçişi, değerleme ya da diğer hacim diye etiketlenmez.
