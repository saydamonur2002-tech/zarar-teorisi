# H1–H7 sınaması

Çekilme: 2026-10-16. Kurallar: `ZINCIR_ONKAYIT.md`. Betik: `zincir_h1h7.py`. Ham: `zincir_h1h7_ham.csv`. Karar dosyası: `zincir_h1h7_sonuc.json`.

Kurallar sonuçtan sonra değiştirilmedi. Kilitli BDDK stok ve mevduat serileri 2024-06'da başlıyor. Bu, katsayı görülmeden bilinmiyordu. Seri değiştirilmedi. Karar, kilitli seride kaldı.

## 1. Üç cümle

Merkezi iddia olan %20–30 kredi ikame bandı bu turda türetilmedi; açık kaldı. H1'den H7'ye kadar her halka belirlenemiyor: kilitli sektörel kredi ve mevduat stokları 2024-06'da başladığı için 9 aylık yerel projeksiyon 4 gözleme, Granger 13 gözleme iniyor; kilitli alt sınır 36'dır. Zincirin en zayıf yeri tek bir çürümüş halka değildir; sınanmış halka yoktur. Ölçülen tek uyuşmazlık firma stok-akışındadır: 2014-Q4–2026-Q1, 46 çeyrekte işlem akımı, F.4 stok farkının medyan %61'idir.

## 2. Hipotez tablosu

Şok her yerde `TP.APIFON4`, TCMB ağırlıklı ortalama fonlama maliyeti, aylık ortalama, yüzde puan farkı. Bir haftalık repo ihale faizi serisi bu çekimde yok. Çekilme 2026-10-16. AOFM 2013-01…2026-10, n=166. 2018-08: %18,30. 2023-06: %9,32. 2026-10: %37,00.

Karar bandı %95. n<36 ise katsayı yazılmaz.

| Halka | Ön kayıt yön ve eşik | Sonuç | Katsayı, %95 bant | Olumlu kanıt | Olumsuz kanıt |
| --- | --- | --- | --- | --- | --- |
| H1 | AOFM farkının reel 12 aylık kredi büyümesine katsayısı h=9'da negatif; bant sıfırın altında. Üç sektörden en az ikisi. Gecikme 3; gecikme 6 işaret çevirirse belirlenemiyor. | belirlenemiyor | yazılmadı. Ticari h=9, n=4 | AOFM ve TÜFE (`TP.TUKFIY2025.GENEL`, 2013-01…2026-09, n=165) duruyor | `TP.HPBITABLO6.20` ticari, `.11` ihtiyaç, `.3` konut 2024-06'da başlıyor, n=29 |
| H2 | Borç/GSYH stoktur. Aynı stokun büyümesi özdeşliktir, nedensel destek sayılmaz. Ayrı akım, h=0, bant sıfırın üstünde, n≥36 | belirlenemiyor | yazılmadı. Akım regresyonu n=7 | Firma işlem akımı `TP.FINHESTNKS62011.ZP34` 2013-Q4…2026-Q1, n=47 | BDDK paydası 9 çeyrek. n=7 < 36 |
| H3 | Granger, gecikme 3, p<0,05. Kredi mevduatı öngörür, tersi öngörmezse en fazla "sınırlı". İki yön birden anlamlıysa belirlenemiyor | belirlenemiyor | yazılmadı. TL, YP TL karşılığı ve YP milyon dolar, n=13 | Parite arındırılmış mevduat değişimi `TP.HPBITABLO5.1` 2014-02…2026-10, n=153 | Kredi büyümesi 2024-06 stoğundan türediği için ortak örnek 36'nın altında |
| H4 | Parite arındırılmış YP değişimi, kredi büyümesi, kur farkı ve PKA 12 ay dolar beklentisi dururken bant sıfırın üstünde. Değilse çürüyor. Örnek yetmezse belirlenemiyor | belirlenemiyor | yazılmadı. Kontrollü n=16 | `TP.PKAUO.S05.C.U` ve `TP.DK.USD.A.YTL` uzun | Kredi serisi kısa. n=16 < 36. TL payı karar çıktısı yapılmadı |
| H5 | Konut fiyatı 12 aylık büyüme, h=3, AOFM kontrolüyken bant sıfırın üstünde | belirlenemiyor | yazılmadı. n=10 | `TP.KFE.TR` 2013-01…2026-09, n=165 | Toplam kredi `TP.HPBITABLO6.1` 2024-06'da başlıyor |
| H6 | İlan ayı, ancak resmî metin inince. Tepe, ilan ±9 ayda `TP.HPBITABLO6.1` nominal 12 aylık büyümesinin en yükseği. Seri başlangıcı ilan tarihi sayılmaz | belirlenemiyor | yazılmadı | `TP.KKM.K1` 2021-12…2026-07, n=56. Bu, serinin ilk ayıdır | Tebliğ metni indirilmedi. Kilitli kredi serisi 2021 penceresinde yok |
| H7 | LKO asgari %100. KV dış borç/brüt rezerv > 1 analitik. YP pozisyonda yönetmelik inmezse oran yok. Swaplı net rezerv serisiz hesaplanmaz | belirlenemiyor | yazılmadı | Brüt rezerv `TP.AB.TOPLAM` duruyor | Dört göstergeden üçü ölçülmedi. İhlal ilan edilmedi |

## 3. Rakip açıklamalar

| Rakip | Ayırt edici öngörü | Sonuç |
| --- | --- | --- |
| Küresel likidite | AOFM katsayısı, VIX veya Fed faizi girince sıfıra iner | belirlenemiyor. Bu kaynaklarda seri çekilmedi |
| Kur şoku, 2018 ve 2021–22 | Kuklalı ve kuklasız h=9 katsayısı ayrışır | belirlenemiyor. İki belirtim de n=4. Ayrışma yazılmadı |
| Maliye, kamu borçlanması | Genel yönetim F.4/GSYH, özel kredi büyümesiyle birlikte hareket eder | belirlenemiyor. Nesne `TP.FINHESTNKS13.ZP34`, 2026-Q1 ham 1.736.061.645,57 bin TL, yani 1.736,1 milyar TL. Hazine iç borç stoku bu seri değildir |
| Reel gelir | Hacim GSYH kredi büyümesini alır, AOFM katsayısı düşer | belirlenemiyor. Zincirlenmiş hacim serisi yok. Vekil kurulmadı |

## 4. Stok-akış

Birim: EVDS finansal hesap ham değeri bin TL'dir. 2026-Q1 firma F.4 ham 25.339.760.798,22. Milyar TL'ye bölüm 25.339,8. Depodaki 2026-Q1 köprü sayısıyla aynıdır.

Uzun örnek, yalnız finansal hesap, 2014-Q4…2026-Q1, 46 çeyrek:

| Nesne | Seri, stok | Seri, işlem | Medyan işlem / stok farkı | Aynı işaret |
| --- | --- | --- | --- | --- |
| Firma, finansal olmayan | `TP.FINHESTNKS11.ZP34` | `TP.FINHESTNKS62011.ZP34` | 0,611 | 39/46 |
| Hane | `TP.FINHESTNKS14.ZP34` | `TP.FINHESTNKS62014.ZP34` | 0,9995 | — |

Firma dağılımının 10. ve 90. yüzdeliği −0,38 ve 1,29'dur. Medyan mutlak fark, stok farkının 0,50'sidir. Stok farkı işlem artı değerlemedir. Firmada değerleme payı büyüktür. Hanede stok farkı işlemin üstüne oturur.

Kısa kesit, BDDK ticari (`TP.HPBITABLO6.20`) ile firma F.4, 2024-Q3…2026-Q1, n=7. Medyan BDDK çeyrek farkı / F.4 çeyrek farkı 0,62. Medyan işlem / F.4 farkı 0,70. n=7 bir karar örneği değildir. İki stok aynı nesne değildir: BDDK banka kredisi, F.4 tüm borç verenler, konsolide olmayan. 2026-03 BDDK ticari 15.996,5 milyar TL; F.4 25.339,8 milyar TL.

Borç/GSYH, 2026-Q1 civarı dört çeyrek GSYH 67.768,5 milyar TL (`TP.GSYIH20.BY.B1GQ`). BDDK ticari / bu GSYH medyanı 0,24 (n=9). Konut stoku 2026-03: 740,0 milyar TL, oran 0,011. Ön kayıttaki 0,05–5 bandı konutu işaretler. Bölme bin TL / bin TL'dir; bant, konut oranının küçük olduğunu söyler. Bu oran bir karar sayısı değildir.

## 5. Bilinen zayıflıklar

| Zayıflık | Bu tur |
| --- | --- |
| Banka bilançosu yok | Kapanmadı. H3'e "destekleniyor" yolu ön kayıtta kapalıydı. Örnek de yetmedi |
| Kredi ile gelir karışıklığı | Kapanmadı. H2'ye nedensel etiket verilmedi. Özdeşlik regresyonu karar sayılmadı |
| Birim tutarsızlığı | F.4 birimi bu turda köprüyle tuttu. Zincirin katsayıları yazılmadığı için o denklemdeki birim bu turda yeniden kurulmadı |
| İki yıl etiketi | Kapanmadı. Bu tur o etiketlere dokunmadı |
| %20–30 kredi ikame bandı | Kapanmadı. Türetilmedi |

## 6. Veri eksikleri

| Eksik | Kapattığı halka |
| --- | --- |
| `TP.HPBITABLO6` sektörel stok, başlangıç 2024-06 | H1, H3, H4, H5, H6'nın kredi penceresi |
| `TP.HPBITABLO2` TL ve YP stok, başlangıç 2024-06 | H3, H4'ün kredi ile ortak örneği |
| Bir haftalık repo ihale faizi | H1'in şoku AOFM'de kaldı |
| Hacim GSYH | Reel gelir rakibi |
| Kısa vadeli dış borç, LKO, banka YP net pozisyonu, swap stoku | H7 |
| KKM tebliğ metni | H6 |
| VIX, EMBI, Fed faizi | Küresel likidite rakibi |
| Hazine iç borç stoku | Maliye rakibinin doğru nesnesi |

## 7. Monografi paragrafı

Bu turda yerel projeksiyon (bir şokun birkaç ay sonraki etkisini, her ufuk için ayrı denklemle ölçen yöntem) kurulamadı: sektörel kredi stoku 2024 ortasında başladığı için dokuzuncu aydaki denklem dört gözleme düştü ve önceden yazılan otuz altı gözlem eşiğinin altında kaldı. Granger sınaması (bir serinin kendi geçmişine, diğer serinin geçmişini eklemenin öngörüyü artırıp artırmadığı) aynı nedenle yazılmadı. Firma tarafında stok-akış özdeşliği (stoktaki değişim, işlem ile değerlemenin toplamıdır) 46 çeyrekte tutmuyor: işlem akımı, stok farkının medyan yüzde 61'i. Hane tarafında aynı oran medyan 1,00. Bulgu zayıf bir nedensellik iddiası değildir. Zincirin yedi halkası da belirlenemiyor. Yüzde 20–30 kredi ikame bandı bu sayılardan çıkmıyor.

## 8. Üç eleştiri

KKM ters nedensellik bu turda sınanamadı. Serinin ilk ayı 2021-12'dir; bu bir tebliğ tarihi değildir. Kilitli kredi serisi o pencerede yoktur. Tedbirin kredi zirvesinden önce mi sonra mı geldiği yazılamadı. Tepki ile sebep ayrılmadı.

Gecikme seçimi sonucu belirlemedi. Gecikme 3 ve gecikme 6, n=4 yüzünden aynı kapıdan döndü. Otuz altı gözlem eşiği, gecikmeden önce karar verdi. Eşik aylık örnek için yazılmıştı ve çeyreklik H2'ye de uygulandı. Çeyrekte otuz altı gözlem dokuz yıldır. BDDK ile ortak çeyrek 7'dir. Bu, H2'yi neredeyse yapısal olarak belirlenemiyor yapar. Eşik sonuçtan sonra indirilmedi.

Zincir uzadıkça birleşik güven düşer, ama burada düşecek bir güven yoktur. Yedi halka da boştur. Boş halkaların çarpımı bir olasılık değildir. Tek bir korelasyonla zincir kurulmaz. Bu turda o korelasyon da yazılmadı.
