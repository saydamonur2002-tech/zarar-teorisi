# Ön kayıt — H1–H7 zinciri

Yazıldı: 2026-10-16, tahminlerden önce. Bu dosyadaki yön, eşik, gecikme ve karar kuralı sonuç görüldükten sonra değiştirilmez. Bir yazılım hatası düzelirse ayrı not düşülür; karar kuralı o notla değişmez.

Bu tur, modelin merkezi iddiası olan %20–30 kredi ikame bandını tahmin etmez. O bant bu tasarımda türetilmez. Turun ilk bulgusu bu eksiktir; zincir onu kapatmaz.

Önceden maruz kalma: aynı kamuya açık serilerin bir kısmı bu depoda ve bu sohbette daha önce kullanıldı. Kriterler bu turdaki katsayılardan önce yazıldı. Kör bir ön kayıt değildir.

## Veri

Çekilme, betiğin çalıştığı gün. Kaynağı yazılamayan sayı kullanılmaz. Eksik seri tahminle doldurulmaz. İki endeks uç uca eklenmez.

- Şok: `TP.APIFON4`, TCMB ağırlıklı ortalama fonlama maliyeti, aylık ortalama, yüzde puan farkı. İlan edilen bir haftalık repo ihale faizi bu turda EVDS serisi olarak bulunamadı. AOFM onun yerine konup "politika faizi" diye adlandırılmaz. Şokun adı AOFM'dir.
- Fiyat: `TP.TUKFIY2025.GENEL`. Arşiv `TP.FG.J0` ile birleştirilmez.
- Kur: `TP.DK.USD.A.YTL`, aylık son.
- Kredi stoku, BDDK, aylık son (EVDS toplulaştırma: last): ticari `TP.HPBITABLO6.20`; konut `TP.HPBITABLO6.3`; ihtiyaç `TP.HPBITABLO6.11`. Geniş tüketici `TP.HPBITABLO6.2` konutu içerir; karar serisi değildir, yalnız not edilir.
- Mevduat: yurt içi TL `TP.HPBITABLO2.3`; yurt içi YP, TL karşılığı `TP.HPBITABLO2.6`; YP milyon USD `TP.HPBITABLO2.10`; parite etkisinden arındırılmış değişim `TP.HPBITABLO5.1`.
- Konut fiyatı: `TP.KFE.TR`. Arşiv `TP.HKFE01` ile birleştirilmez.
- Kur beklentisi: `TP.PKAUO.S05.C.U`, 12 ay sonrası ABD doları.
- GSYH: `TP.GSYIH20.BY.B1GQ`, cari, harcama, çeyreklik. Resmî zincirlenmiş hacim serisi bulunamazsa reel gelir vekili kurulmaz; rakip R4 belirlenemiyor kalır.
- Kamu kredisi, ayrı nesne: finansal hesap `TP.FINHESTNKS13.ZP34` (genel yönetim F.4, konsolide olmayan). Hazine iç borç stoku değildir.
- Firma kredisi, ayrı nesne: `TP.FINHESTNKS11.ZP34` ve işlem akımı `TP.FINHESTNKS62011.ZP34`. Hane işlem akımı `TP.FINHESTNKS62014.ZP34` bulunursa kullanılır.
- Brüt rezerv: `TP.AB.TOPLAM`. Swap düşülmüş net rezerv, seri yoksa hesaplanmaz.
- KKM: `TP.KKM.K1`, `TP.KKM.K4`.

Örnek: serilerin ortak başladığı aydan, 2026'da gelen son aya. Ufukta kullanılabilir gözlem 36'nın altındaysa o halka belirlenemiyor.

## Yöntem (kilitli)

Yerel projeksiyon (Jordà). VAR ana tahmin değildir. Gecikme 3 aydır; bilgi kriteriyle seçilmez. Duyarlılık gecikmesi 6 aydır ve yalnız şu işi yapar: birincil katsayının işareti gecikme 6'da tersine dönerse karar belirlenemiyor olur.

Newey–West, bant genişliği h+1. Karar bandı %95. Bant sıfırı içeriyorsa destekleniyor ya da çürüyor denmez.

Kırılma kuklaları, şok tarihine yapışık, örnek bölünmesi değil:

- 2018-08 … 2018-12
- 2020-03 … 2020-06
- 2021-09 … 2022-12
- 2023-06 … örnek sonu

Kontroller çağdaş değil, 1–3 gecikme: şok, bağımlı değişken, aylık log kur farkı, 12 aylık TÜFE enflasyonu. Kur ve enflasyonun çağdaş değeri konmaz.

## Karar

H1. Bağımlı: reel 12 aylık kredi stok büyümesi, `(S_t/P_t)/(S_{t-12}/P_{t-12})−1`. Birincil ufuk h=9. H6 ve h=12 raporlanır, kararı değiştirmez. Beklenen işaret: AOFM farkının katsayısı negatif. Sektör kendi kararını alır. H1 bütünü, üç sektörden en az ikisi destekleniyorsa destekleniyor; biri destekleniyorsa bütün belirlenemiyor.

H2. Borç/GSYH stok oranıdır: çeyrek sonu BDDK stoku / o çeyrek dahil son dört çeyrek cari GSYH. Aynı stokun büyümesini bu oranın farkına koymak özdeşliktir; nedensel destek sayılmaz, karar belirlenemiyor. Nedensel sınama yalnız ayrı bir işlem akımı serisi varsa yapılır: oranın farkı, akım/GSYH üzerine, nominal GSYH büyümesi kontrol edilerek, h=0, %95 bandı sıfırın üstünde. Kamu F.4 bu regresyona girmez; yanında raporlanır.

H3. Granger, gecikme 3, eşik p<0,05, TL ve YP ayrı. Kredi büyümesi mevduat büyümesini öngörür ve tersi öngörmezse sonuç "sınırlı"dır. Banka bilançosu olmadığı için H3 "destekleniyor" etiketini alamaz. İki yön de anlamlıysa belirlenemiyor. Yalnız ters yön anlamlıysa çürüyor. Korelasyon karar değildir.

H4. Karar çıktısı, parite etkisinden arındırılmış YP mevduat değişimidir (`TP.HPBITABLO5.1`). TL karşılığı pay, kur değerlemesi karıştığı için karar çıktısı değildir. Kredi büyümesinin katsayısı, aylık log kur farkı ve PKA 12 ay dolar beklentisinin gerçekleşen kura göre farkı eklendikten sonra %95 bandıyla sıfırın üstündeyse destekleniyor. Bant sıfırı içeriyor ya da işaret negatife dönüyorsa çürüyor. PKA örtüşmesi yoksa belirlenemiyor.

H5. Toplam yurt içi kredi `TP.HPBITABLO6.1`, reel 12 aylık büyüme. Konut fiyatının 12 aylık büyümesi, h=3, AOFM farkı ve üç gecikmesi kontrol altındayken %95 bandıyla pozitifse destekleniyor. Değilse, işaret pozitif ve bant sıfırı içeriyorsa belirlenemiyor; bant sıfırın altındaysa çürüyor. −6…+6 korelasyon gecikmesi raporlanır, karar değildir.

H6. Tarih, ancak resmî metin bu turda erişilirse kullanılır. Bellekten tarih yazılmaz. Kural: ilan ayı, ilandan 9 ay önce ve 9 ay sonraki pencerede `TP.HPBITABLO6.1` nominal 12 aylık büyümesinin en yüksek olduğu ayla karşılaştırılır. Tepe ilandan önceyse tepki. Sonraysa öncü. Aynı aysa belirlenemiyor. Gözlenen büyüme "eşik" diye raporlanır; %20 gibi bir tetik bu turda konmaz. Tebliğ bulunamazsa H6 belirlenemiyor. Serinin ilk gözlemi tebliğ tarihi sayılmaz.

H7. Eşikler bu turda yazılır. Seri yoksa ihlal ilan edilmez.

- Likidite karşılama oranı: asgari %100. Seri EVDS kataloğunda yoksa ölçülmez.
- Kısa vadeli dış borç / brüt rezerv > 1: analitik eşik, resmî tetik değil. Seri yoksa ölçülmez.
- Banka döviz net genel pozisyonu: yönetmelik maddesi bu turda dosyaya inmezse %20 rakamı kullanılmaz.
- Swap düşülmüş net rezerv < 0: seri yoksa hesaplanmaz.

Likidite sorunu, ancak ölçülen bir gösterge kendi eşiğini aşarsa yazılır.

## Rakipler

- Küresel likidite: izin verilen kaynaklarda seri yoksa belirlenemiyor. Dış kaynaktan doldurulmaz.
- Kur şoku: H1 birincil katsayısı, 2018 ve 2021–22 kuklaları çıkarıldığında ve dururken ayrı raporlanır. Karar, kuklalı temel belirtimdir.
- Maliye: genel yönetim F.4/GSYH farkı, özel kredi büyümesinin yanında. Nesne Hazine borç stoku değilse öyle yazılır.
- Reel gelir: resmî hacim GSYH yoksa rakip belirlenemiyor.
