# Ön kayıt — yatırım teşvik sistemi çıpanın sebebi mi?

Kayıt anı: 2026-10-21T05:02:52Z. Bu saatten sonra eşik, pencere ve hüküm kuralı değişmez. Değişirse aynı dosyaya SAPMA satırı düşer; eski eşik silinmez. Bu satırdan önce teşvik kararı tarihi aranmadı, kur getirisi, beklenti farkı ve dış ticaret payı hesaplanmadı.

Soru: teşvik rejimi değişiklikleri, kilitli kırılma tarihlerine denk gelip Türkiye'ye özgü kur ve beklenti sıçraması üretti mi; teşvikli ithal makine yapısal döviz talebiyle çıpanın sürmesini açıklıyor mu; faiz/kâr payı desteği ve Hazine/KGF kredisi parasal aktarımı zayıflattı mı. Ayakta, ölçütün tuttuğu anlamına gelir. Ölçüt tutsa da karşı-olgusal, teşvik metnini aynı gündeki diğer haberden ayırmıyorsa sebep cümlesi yazılmaz. Karşı-olgusal burada yalnızca BRL, MXN ve ZAR'a göre Türkiye'ye özgü kur farkıdır.

## Kilitli kırılmalar

Bunlar yeniden tahmin edilmez. Bai-Perron yok.

- Erken uyarı: Kasım 2016.
- Kalıcı kopuş: Temmuz 2018. Yüzde 90 aralık Mayıs–Eylül 2018.
- Kısmi dönüş: Ağustos 2019.
- En büyük kırılma: Aralık 2021.
- Toparlanma: Kasım 2023'ten sonra. 12–13 puanda takılma iddiası ölçülür, doğru kabul edilmez.

## Çıpa

g = 24 ay sonrası TÜFE beklentisi, uygun ortalama, eksi yüzde 5 hedef. Seri: TP.PKAUO.S01.F.U. Aylık gözlem ay etiketidir; bülten günü kayması bu seride aranmaz.

Kur ayağı: TL'nin BRL, MXN ve ZAR'a göre aynı penceredeki farkı. Beklentinin kura duyarlılığı H-T2'de ayrıca tarif edilir; H-T1 eşiğine girmez.

## Karar listesi (hesaptan önce kapanır)

Liste, getiriyi görmeden ve pencereye düşüp düşmediğine bakmadan kapanır. Pencereye düşen bir metin sonradan eklenmez; düşmeyen bir metin listeden çıkarılmaz.

Kaynak sırası:

1. mevzuat.gov.tr üzerinde 2012/3305 sayılı Bakanlar Kurulu kararının birleşik metnindeki değişiklik dipnotları. Dipnottaki her değiştiren karar numarası listeye girer.
2. Proje bazlı teşvik: aynı sitede veya Resmi Gazete'de bu kararın dayanağı olan metin. Kullanıcıdaki "2016 proje bazlı / süper teşvik" adayı bu aramayla doğrulanır; numara uydurulmaz.
3. HIT-30: ancak Resmi Gazete kararı ise listeye girer. Strateji kitapçığı, sunum ve haber [İKİNCİL] ve hüküm dışıdır.
4. 2025 veya 2026: birleşik metnin 2025–2026 değişiklikleri ve Resmi Gazete'de teşvik rejimini değiştiren yeni bir karar. Bulunamazsa "yok" yazılır; arama yapılmadı denmez.

Eşleşme tarihi, kararın içindeki imza tarihi değil, Resmi Gazete sayı tarihidir. İkisi de tabloda durur. Yürürlük tarihi ikinci bir eşleşme hakkı vermez.

Metin okunamazsa o kalem [DOĞRULANMADI], eşleşme sayılmaz. Sertifika doğrulaması kapatılmaz, engel sayfası aşılmaz.

## Pencereler

Sayı tarihi bu aralığın içindeyse karar pencerededir.

- W1 erken uyarı: 2016-10-01 … 2016-12-31
- W2 kalıcı kopuş aralığı: 2018-05-01 … 2018-09-30
- W3 kısmi dönüş: 2019-07-01 … 2019-09-30
- W4 en büyük kırılma: 2021-11-01 … 2022-01-31
- W5 takılma başlangıcı: 2023-10-01 … 2023-12-31

2012/3305'in kendi yayını, FX örneklemi 2016'da başladığı için kur testi dışında kalır. Zaman çizelgesinde durur. Örneklem, pencereye sığdırmak için 2012'ye uzatılmaz.

## Kur ölçütü

Kaynak: TCMB kurlar XML, bülten günü. Adres `https://www.tcmb.gov.tr/kurlar/YYYYMM/DDMMYYYY.xml`. USD ForexSelling. EVDS gün etiketi olay günü değildir: EVDS'te t günü, bir önceki iş gününün 15:30 bültenidir. Eşler aynı takvim gününde Fed H.10 ile eşlenir.

Getiri: 100 × ln(E_t / E_{t−1}). Pozitif, doların yerel para cinsinden artmasıdır. Eş kuru kaynakta dolar başına yerel para değilse, yerel para başına dolara çevrilir.

Türkiye'ye özgü gün-0 = TRY getirisi eksi BRL, MXN, ZAR getirilerinin eşit ağırlıklı ortalaması. Gün, TRY ile birlikte en az iki eşin her iki ucu varsa girer. İkişten az eş varsa pencere boştur; boş pencere geçmez ve kalmaz.

Gün-0: sayı tarihi bülten günüyse o gün, değilse sonraki TCMB bülteni.

CAR ±1 ve CAR ±3, gün-0'ın etrafındaki bülten günlerinde Türkiye'ye özgü günlük getirilerin toplamıdır. Gün, aynı eş kuralıyla girer; boş uç doldurulmaz. CAR sağlamlıktır. Gün-0 kalırsa CAR onu geçirmez. Gün-0 boşsa CAR yerine konmaz.

Örneklem: 2016-01-04'ten, indirme anında alınan son bültene kadar.

Plasebo evrenin tamamıdır; 2000 çekiliş yoktur. İki havuz:

- Havuz Yıl: gün-0 ile aynı takvim yılındaki diğer bülten günleri. Teşvik gün-0'larının her biri ve etrafındaki ±5 bülten günü çıkarılır.
- Havuz Dışı: 2016'dan son bültene kadar, olay yılı, 2018 ve 2021 dışındaki bülten günleri. Aynı ±5 çıkarımı.

Tek taraflı p = (1 + havuzda gözlenen kadar veya daha büyük olan gün sayısı) / (1 + N). Hipotez TL'ye özgü değer kaybıdır; değerlenme lehine sayılmaz.

Kur ayağı geçer, ancak üçü birden:

- p_yıl ≤ 0,10
- gözlenen ≥ havuz Yıl'ın 90. yüzdeliği
- Holm düzeltmeli p ≤ 0,10

Holm ailesi, FX örnekleminde gün-0'ı hesaplanan bütün liste kararlarıdır; yalnızca pencereye düşenler değil. p_dışı > 0,10 ise kur ayağı belirsiz kalır; yıl içi uç bir gün, sakin yıllarda uç değilse geçmez. N < 100 ise p hüküm kurmaz; o günün kur ayağı belirsizdir.

Sağlamlık, hüküm değil: eş kümesine INR eklemek; H.10 gününü +1 ve −1 kaydırmak. İşaret üçünde de aynı kalmazsa o gün belirsizdir.

## Beklenti ölçütü

Δg, sayı tarihinin takvim ayındaki g eksi bir önceki aydır. Taban: 2013-01 … 2016-09 aylık Δg. Seri daha geç başlarsa, 2016-09'da biten en uzun stretch; 24 aydan kısaysa beklenti ayağı belirsizdir, eşik kaydırılmaz.

Geçer: Δg > 0 ve (1 + tabanda gözlenen kadar veya daha büyük Δg sayısı) / (1 + N_taban) ≤ 0,10.

## Ayrışma

S aynı Resmi Gazete sayısında şunlardan biri varsa karar ayrışmaz, S kümesine girmez:

- TCMB başkanı ataması veya görevden alınması
- TCMB'nin kuruluş veya görev kararnamesi (3 sayılı CBK ve onu değiştiren metin)
- Teşvik istisnası olmayan, genel kurumlar vergisi, genel KDV veya ÖTV oranını değiştiren karar

Teşvik aracının kendisi (gümrük muafiyeti, KDV istisnası, vergi indirimi, faiz desteği) karıştırıcı değildir. Aynı sayı okunamazsa karar S'ye girmez.

## H-T1 hükmü

- Liste kurulamazsa: BELİRSİZ.
- Pencereye düşen karar yoksa: Yanlışlandı. Denk gelme yoktur. Pencere dışı günlerin kuru sonradan eşleşme açmaz.
- Pencereye düşenlerin hepsi ayrışmıyorsa: BELİRSİZ.
- Ayrışan en az bir karar var ve hiçbiri hem kur hem beklenti ayağını geçmiyorsa: Yanlışlandı.
- Ayrışan en az biri her iki ayağı da geçerse: Ayakta. Cümle şudur: o yayım günü, kilitli pencerede, aynı sayıdaki kurum karışığından ayrı, Türkiye'ye özgü değer kaybı ve beklenti sıçraması ölçütü tuttu. Teşvik sisteminin çıpanın sebebi olduğu yazılmaz.

## H-T2 — teşvikli ithal makine

Birincil seri, teşvik belgesine bağlı ithal makine tutarı veya yatırım teşvik belgesi kapsamındaki gümrük vergisi muafiyeti / KDV istisnasıdır. Adresler: Sanayi ve Teknoloji Bakanlığı teşvik belgesi istatistiği; HMB vergi harcaması. Her adres bir kez, sertifika açık, denenir. Engel sayfası [DOĞRULANMADI]. HS84 toplam ithalatı, birim değer ve ihracat/ithalat oranı [VEKİL]'dir; tek başına Ayakta yapmaz. Önceki makine kalitesi oranları bu turun kanıtı değildir.

Takılma bandı, aynı g serisinden: 2023-11'den son aya kadar min ≥ 10, max ≤ 16 ve max − min ≤ 4. Tutmazsa H-T2'nin "12–13'te takılma" cümlesi düşer.

Ayakta, dördü birden:

- Birincil seri en az 2015–2023'ü kapsar.
- Teşvikli ithal makinenin toplam makine ithalatına oranı, 2013–2015 ortalamasından (seri daha geç başlarsa 2016 öncesi ilk üç yıl) son üç yıl ortalamasına en az 10 puan çıkar.
- Bu artış varken takılma bandı tutar.
- Payda HS84 ise payda [VEKİL] diye işaretlenir; pay birincil kaldığı sürece hüküm kurulabilir. Pay da yoksa BELİRSİZ.

Yanlışlandı: birincil seri vardır ve pay artışı 5 puandan küçüktür veya pay düşer. Artış 5 ile 10 puan arasındaysa BELİRSİZ. Birincil seri yoksa BELİRSİZ; vekil tablo hükmü değiştirmez.

Duyarlılık, hüküm dışı [HESAP]: 24 aylık kayan regresyonda Δg, aylık USD satış log getirisine (bülten günlerinin ay ortalaması) karşı. 2014-01…2016-09, 2018-10…2021-11 ve 2023-11…son ay için ortalama eğim raporlanır. Eğim büyüse de makine serisi yoksa H-T2 Ayakta olmaz.

## H-T3 — aktarım

Birincil seri teşvik faiz veya kâr payı desteği, ya da teşvikle bağlı Hazine/KGF kredisi veya kefaletidir. Adı teşvik olmayan genel Hazine kefaleti [VEKİL]'dir ve Ayakta yapmaz. Politika faizi, bir hafta vadeli repo ihale faiz oranının aylık serisidir; EVDS kodu sonuçta yazılır, uydurulmaz. Aylık seri kullanılır; günlük EVDS etiketi gün-0 yapmaz.

Büyük şok: ay sonu politika faizinde |Δi| ≥ 1,0 puan. Tepki: Δg_{t+1}. Üç aylık tepki sağlamlıktır, ikinci hüküm değildir.

Yüksek teşvik payı, ancak seri aylık veya üç aylıksa tanımdır: gecikmeli çeyreğin payı örneklem ortancasının üstündeyse 1. Yıllık seri aylara yayılmaz; o durumda regresyon kurulmaz, H-T3 BELİRSİZ kalır, yıllık düzey yalnızca tarif edilir.

Regresyon, |Δi| ≥ 1 olan aylarda: Δg_{t+1} = a + b·Δi_t + c·(Δi_t × Yüksek_{t−1}). Büyük şok ayı 12'den azsa kurulmaz; BELİRSİZ.

Plasebo: Yüksek göstergesi 3 aylık bloklar halinde 2000 kez karılır. Tohum 20261021. p = (1 + c_perm ≥ c_gözlenen sayısı) / 2001. Tek taraflı, c'nin büyük olması lehine.

Ayakta: seri aylık veya üç aylık ve teşvike bağlıdır; b < 0; c > 0 ve |c| ≥ 0,5|b|; plasebo p ≤ 0,10. Ülke eşi olmadığı için "aktarımı teşvik zayıflattı" sebep cümlesi yine yazılmaz. Ayakta, etkileşim ölçütünün tuttuğu anlamına gelir.

Yanlışlandı: regresyon kuruldu ve b ≥ 0 veya c ≤ 0 veya |c| < 0,5|b| veya p > 0,10. Seri yoksa, seri yıllıksa veya şok ayı 12'den azsa: BELİRSİZ.

## Etiket ve kanıt

[VERİ] birincil indirme. [VEKİL] teşvikli makine veya teşvikli kredi yerine geçen toplam. [HESAP] ön kayıtlı formül. [TAHMİN] regresyon katsayısı. [DOĞRULANMADI] okunamayan adres veya metin. [İKİNCİL] haber ve manşet; hüküm dışı. Kanıt, hükme giren ölçüttür. Diğer rakam adaydır.

EVDS_API_KEY okunmaz. Günlük kur ve aylık beklenti EVDS3 `igmevdsms-dis` ile alınırsa raporda yazılır.

## Hükümden önce yapılmayacaklar

Eşik, pencere veya aile, sonuca bakılarak değiştirilmez. Boş eş günü doldurulmaz. Engel sayfası ikinci bir aynadan alınmaz. Karşı-olgusal yokken sebep fiili yazılmaz.
