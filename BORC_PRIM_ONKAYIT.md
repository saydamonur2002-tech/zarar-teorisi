# Ön kayıt — borç düzeyi ve iç tahvil primi

Yazıldı: 2026-10-16, katsayı görülmeden. Eşik, ufuk ve ikame yasağı sonra değiştirilmez.

Prim, 10 yıllık gösterge tahvil faizi eksi TCMB ağırlıklı ortalama fonlama maliyetidir. Bu fark tek başına risk primi değildir. Beklenen faiz yolunu ve vade primini de taşır.

## Denklem

Sıklık çeyrekliktir. Borç stoku aya ara değerle geçilmez. Prim, çeyrekteki üç ayın ortalamasıdır. Üç aydan biri yoksa o çeyrek düşer. İki ayla ortalama kurulmaz.

Yöntem yerel projeksiyondur. Her ufuk ayrı denklemdir. VAR ana tahmin değildir. Gecikme 1 çeyrektir. Bilgi kriteriyle seçilmez.

Newey–West, Bartlett, bant floor(4·(n/100)^(2/9)), en az 1. Karar bandı %95: katsayı ± 1,96 standart hata. Bant sıfırı dışlıyorsa ve işaret hipotezle aynıysa desteklenir. Tersi yönde dışlıyorsa çürür. Sıfırı içerirse veya n < 36 ise belirlenemiyor. n < 36 ise katsayı yazılmaz.

Gözlem ayı değil, çeyrektir. 36 çeyrek dokuz yıldır.

Granger, gecikme 1, yalnız yön içindir. Nedensellik diye yazılmaz. Kararı yerel projeksiyon verir.

## Hipotezler

H1. Borç/GSYH’nin bir çeyrek gecikmeli düzeyi, primin 4 çeyrek (12 ay) sonraki düzeyini pozitif etkiler. Kontroller durur. Karar ufku 4’tür.

H2. Borç dinamiğinin çeyreklik artışı, primin 2 çeyrek (6 ay) sonraki düzeyini pozitif etkiler. Dinamik, düzey katsayısıyla yazılmaz.

H3. Primin çeyreklik artışı, borç/GSYH’nin 4 çeyrek sonraki değişimini pozitif etkiler. 2 çeyrek raporlanır, kararı değiştirmez.

H4. H1’in beklenen faizsiz katsayısı ile beklenen faizli katsayısı aynı işaretliyse ve ikincinin mutlak değeri birincinin en çok yarısıysa, ilişkinin büyük kısmı faiz beklentisine aittir. İşaret değişirse bu cümle kurulmaz, değişim yazılır. Beklenen faizsiz katsayının bandı sıfırı içeriyorsa küçülme kaydı düşülmez.

## Kontroller

Her tahminde: toplantı öncesi faiz beklentisi, VIX, ABD 10 yıllık tahvil getirisi, 24 ay enflasyon beklentisi, USD/TRY’nin çeyreklik log farkı, dört kırılma kuklası.

Kukla çeyrekleri: 2018-Q3 ve 2018-Q4. 2020-Q1 ve 2020-Q2. 2021-Q3…2022-Q4. 2023-Q2…örnek sonu.

Beklenen faiz: `TP.PKAUO.S04.C.U`, ilk toplantı için politika faizi beklentisi. Ay sonu repo beklentisi `TP.PKAUO.S04.A.U` onun yerine konmaz.

## Nesneler

- Tahvil faizi: adı 10 yıllık gösterge tahvil faizi olan EVDS serisi. Bu turda böyle bir seri çekilemezse prim kurulmaz. Mevduat faizi, fonlama maliyeti ve üçüncü taraf hesabı tahvil faizinin yerine geçmez.
- Fonlama: `TP.APIFON4`.
- Borç stoku: genel yönetim toplam borç stoku. Finansal hesap F.0 toplam yükümlülük (`TP.FINHESTNKS13.ZP45`) ve F.3 borçlanma senedi (`TP.FINHESTNKS13.ZP31`) bu stok değildir. Yerine konmaz.
- GSYH: `TP.GSYIH20.BY.B1GQ`. Oran, stok bölü o çeyrek dahil son dört çeyrek cari GSYH’dir. Stok yoksa oran yazılmaz.
- Dinamikteki faiz, 10 yıllık tahvil faizidir. Efektif borç faizi serisi değildir. Tahvil faizi yoksa dinamik yazılmaz. Büyüme, nominal GSYH’nin dört çeyrek önceki düzeye göre yüzde değişimidir.
- Kur: `TP.DK.USD.A.YTL`.
- Enflasyon beklentisi: `TP.PKAUO.S01.F.U`.
- VIX ve ABD 10 yıl: EVDS’de doğrulanmış seri yoksa dış kaynaktan doldurulmaz.

Eksik nesne varsa denklem kurulmaz. Katsayı yoktur. Etiket belirlenemiyor.
