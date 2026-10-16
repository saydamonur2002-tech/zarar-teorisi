# Dilim, motiv ve sızıntı

Şoku izleyen yılda dış borç stoku ile kısa vadeli pay birlikte artmadı. 2019'da stok, 2017'deki 460.245 milyon ABD dolarından 398.506'ya indi. 2022'de stok, 2020'deki 390.820'den 388.639'a indi; kısa pay yükseldi, stok yükselmedi. 2024'te stok 2022'nin üstüne çıktı, kısa pay %38,2'den %37,5'e geriledi. Kurun Aralık'tan Aralık'a %57 yükseldiği 2023'te yerleşik hanehalkının döviz tevdiat payı %42,2'den %31,1'e düştü. K2 ve K3, önceden yazılmış beklentiyi tutmadı. Dilim ve motiv testleri belirlenemedi: yayımlanmış dilim tablosu ve kurtarma takvimi klasörde yok. Belirlenemedi bir sonuçtur. Henüz bakılmamış bir iddia, destek sayılmaz.

Kısa vade, borcun baştan bir yıl içinde ödenecek diye kayda geçmesidir. Döviz tevdiat payı, bankadaki döviz hesabının TL mevduatla birlikte ne kadar yer tuttuğudur.

Çekim 16 Ekim 2026. Dış borç serisi, 12 Mart 2026 yöntem değişikliğinden sonradır: elde tutanın yerleşikliği ve piyasa değeri. Birim, TCMB metaverisinde milyon ABD dolarıdır (`ham/tcmb_dis_borc_metaveri.pdf`). `SONUC_stok_akis_tampon_2026-10.md`, `sektor_B9_tuik.csv`, `makro.csv` ve dilim ekleri klasörde yoktu. `veri_hanehalki.csv` içinde gelir ve harcama sütunları boştur.

## 1. Kaynak

| Gösterge | Kurum | Tablo | Sürüm | Birim |
|---|---|---|---|---|
| Brüt dış borç stoku | TCMB | EVDS `TP.BRUTDBORCLU.G1`, Q4 | 16 Ekim 2026 | milyon ABD doları |
| Kısa vade payı | TCMB | `G19 / G1` | aynı | pay. Kısa vade, orijinal vadesi 1 yıla kadar |
| Dış âlem B.9 | TCMB | S.2 BF.9 akımı, `tampon_yillik.csv` | 16 Ekim 2026 finansal hesap | milyon TL. Pay, EVDS GSYH'ye bölünür |
| USD alış | TCMB | `TP.DK.USD.A.YTL`, Aralık son iş günü | 16 Ekim 2026 | TL |
| Hane TL, döviz tevdiat, kıymetli maden | TCMB | `TP.KM.E040`, `E050`, `E056`, Aralık, mevduat bankaları | 16 Ekim 2026 | EVDS ham. Seri listesinde birim alanı yok. Pay birimsizdir |
| Ticari kredi TL / YP | TCMB | `TP.HPBITABLO6.21`, `.26` | 2024'ten önce gözlem yok | şok yıllarında boş |
| KKM | TCMB | `TP.KKM.K1`, `K2`, `K4` | seri adındaki birim | milyar ABD doları ve milyar TL |
| Yapılandırılmış kredi | BDDK / TCMB | katalogda ayrı seri yok | | veri yok |
| Mülk geliri, borç yükü, tüketim dilimi | TÜİK | GYKA ve HBA %20 tabloları | Ekim 2026 eki klasörde yok | veri yok |
| Mevduat tutar dilimi | TBB / BDDK | | | veri yok |
| Kurtarma tarihi | Resmî Gazete, BDDK | | | veri yok |
| Takip oranı | TCMB | `takip_aylik.csv` | gözlem 2024-06'da başlıyor | oran |

Ayrıntı `kaynak_tablo.csv` içindedir.

## 2. Dağılım

`dilim.csv` yıl × dilim × gösterge ızgarasıdır. 2018–2025, beş dilim, dört gösterge, ham ve düzeltilmiş: 328 satır. Değer sütununun tamamı boştur.

| | Mülk geliri | Faiz yükü | Borç yükü (çok yük) | Tüketim |
|---|---|---|---|---|
| Alt %20 … üst %20, 2018–2025 | veri yok | veri yok | veri yok | veri yok |
| Aynı hücre, ulusal hesaba bağlanmış | veri yok | veri yok | | |

Mevduat tutar dilimi de boştur. O satırın dilim kodu `hesap_dilimi`dir. Hesap dilimi hane dilimi değildir. Tablo gelseydi bile "alt %20 şunu aldı" denmeyecekti.

## 3. Motiv

| Test | Beklenti (sonuç görülmeden yazılı) | Sonuç | Karar |
|---|---|---|---|
| M1 | Kurtarma yılında üst ve orta kesimin kaybı alt kesime kayar | Kurtarma yılı okunmadı. Dilim kaybı yok | Belirlenemedi |
| M2 | Aynı şokta, farklı politika rejiminde dağılım benzer kalır | Dağılım tablosu yok. Rejim karşılaştırması kurulamadı | Belirlenemedi |
| M3 | Takip ve yapılandırma ile reel kaybın zamanı arasında gecikme vardır | Takip serisi 2024-06'da başlar. 2018, 2021 ve 2023'ün takip oranı bu dosyada yok. Gecikme için ortak yıl yok | Belirlenemedi |

`motiv_takvim.csv` iki tür satır taşır. Kart azami faizinin bileşik yıllık tavanı 2018–2025 için `erteleme_yillik.csv`den gelir; bu bir faiz tavanıdır, kamu sermayesi veya yapılandırma kararı değildir, M1'e konmadı. Kamu sermayesi ve yapılandırma yasası satırları boştur. Tarih ezberden yazılmadı.

M1 ile M2 arasındaki karar bir rejim karşılaştırmasıdır. Niyet okunmadı. Karşılaştırma yapılamadığı için iki iddia da açıkta kaldı.

## 4. Kanal

Üç kanalın "borç vadesi içindeki payı" boş bırakıldı. Yapılandırılmış kredi stoku yok. Dış borç stoku, döviz mevduat payı ve olmayan bir stok, tek bir borcun yüzdeleriymiş gibi toplanmadı.

Şok yılları bu depoda daha önce ilan edilen yıllardır: 2018, 2021, 2023. Şok öncesi, önceki yılın aralık sonudur. Şok sonrası, sonraki yılın aralık sonudur. 2023 için bir yıl daha (2025) ayrıca durur.

Döviz payı, `E050 / (E040 + E050)`dir. Kıymetli maden (`E056`) ikinci sütunda paydaya girer. İkisi de mevduat bankasındaki yerleşik hanehalkıdır.

| Şok | Pencere | Yıl | K1 yapılandırma | K2 stok, milyon USD | K2 kısa pay | K2 dış âlem B.9 / GSYH | K3 döviz tevdiat payı | K3 tevdiat + maden | K3 ticari TL payı | USD alış |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 2018 | öncesi | 2017 | veri yok | 460.245 | %23,8 | %5,9 | %37,8 | %39,1 | veri yok | 3,81 |
| 2018 | şok | 2018 | veri yok | 412.049 | %22,5 | −%1,8 | %41,7 | %43,3 | veri yok | 5,26 |
| 2018 | sonrası | 2019 | veri yok | 398.506 | %24,0 | −%1,4 | %46,2 | %48,7 | veri yok | 5,94 |
| 2021 | öncesi | 2020 | veri yok | 390.820 | %28,5 | %1,9 | %50,2 | %56,0 | veri yok | 7,34 |
| 2021 | şok | 2021 | veri yok | 378.522 | %31,3 | −%3,2 | %59,7 | %64,2 | veri yok | 12,98 |
| 2021 | sonrası | 2022 | veri yok | 388.639 | %38,2 | −%1,6 | %42,2 | %47,9 | veri yok | 18,70 |
| 2023 | öncesi | 2022 | veri yok | 388.639 | %38,2 | −%1,6 | %42,2 | %47,9 | veri yok | 18,70 |
| 2023 | şok | 2023 | veri yok | 432.551 | %40,5 | %2,5 | %31,1 | %37,7 | veri yok | 29,40 |
| 2023 | sonrası | 2024 | veri yok | 461.237 | %37,5 | %0,6 | %25,0 | %33,7 | %51,4 | 35,22 |
| 2023 | ikinci yıl | 2025 | veri yok | 522.732 | %32,0 | %3,6 | %25,4 | %41,5 | %50,4 | 42,86 |

B.9 akımdır. Pozitif işaret, o yıl dış âlemin Türkiye'ye net borç verdiği anlamına gelir. Bu, stoktaki alacaklı pozisyonunun kendisi değildir.

| Test | Beklenti | Ölçülen | Karar |
|---|---|---|---|
| K1 | Şoku izleyen yıllarda yurt içi yapılandırma stoku artar | Stok yok | Belirlenemedi |
| K2 | Şoku izleyen yıllarda dış borç stoku ve kısa vadeli pay birlikte artar | 2019'da stok düştü, kısa pay 2017'ye göre 0,2 puan yükseldi. 2022'de kısa pay yükseldi, stok 2020'nin altında kaldı. 2024'te stok yükseldi, kısa pay geriledi. 2023'ün kendi yılında ikisi birden yükseldi; izleyen iki yılda kısa pay geriledi | Desteklenmedi |
| K3 | Kur şokunda döviz mevduatı payı artar; TL borç payı düşer | USD alış 2018'de %38, 2021'de %77, 2023'te %57 yükseldi. Döviz tevdiat payı 2018 ve 2021'de yükseldi, 2023'te düştü. Maden eklenince yön aynı kaldı. Ticari TL payı şok yıllarında yok; 2024–2025'te %51,4'ten %50,4'e indi, bu pencere şok testi değildir | Desteklenmedi. TL borç bacağı belirlenemedi |

K2'nin "dış âlem net alacaklı pozisyonu büyür" cümlesi stok pozisyonudur. Eldeki B.9 akımdır. Akım 2018 ve 2021'de negatife döndü, 2023'te GSYH'nin %2,5'i kadar pozitif oldu. Akım, stok iddiasının yerine konmadı.

## 5. D1 ve D2

| Test | Beklenti | Ham | Düzeltilmiş | Karar |
|---|---|---|---|---|
| D1 | Net faiz ve mülk gelirinin çoğu üst %20'dedir | veri yok | veri yok | Belirlenemedi |
| D2 | Faiz yükü ve tüketim kesintisi alt %20'dedir | veri yok | veri yok | Belirlenemedi |

Düzeltme kuralı duruyor: dilim payı, ulusal hesaptaki faiz ve kira toplamına uygulanacak, ham ve düzeltilmiş yan yana yazılacaktı. Dilim payı yok, `veri_hanehalki.csv` içinde D.4 boş. Çarpım yapılmadı.

## 6. Sınırlar

Anket, üst kesimin faiz ve kira gelirini eksik yazar. Bu eksik, teorinin aleyhine bir ölçüm hatasıdır. Düzeltme için gereken iki sayıdan ikisi de yok.

Mevduat tutar dilimi ile hane gelir dilimi aynı sıra değildir. Biri hesabın büyüklüğüne, öteki hanenin gelirine bakar.

Döviz tevdiat, ölçüm raporundaki kural gereği enflasyondan korunmuş sayılır ve TL mevduatla tek bir "reel mevduat"ta birleştirilmedi. Kıymetli maden de TL sayılmadı; ayrı bir pay olarak duruyor.

Kur korumalı mevduat (KKM) döviz tevdiatın içinde değildir. Aralık 2023'te dövizden dönen KKM'nin gerçek kişi tutarı 59,0 milyar ABD doları, TL KKM toplamı 282,5 milyar TL'dir. TL KKM'nin hane kırılımı seride yoktur. Aralık 2025'te gerçek kişi dövizden dönen KKM 0,2 milyar ABD doları, TL KKM 0'dır. KKM, döviz payına eklenmedi.

Ticari kredinin TL/YP ayrımı EVDS'de 2024'ten önce gelmiyor. Tüketici kredisinde bu ayrım tabloda yok.

Motiv kararı nedensellik değildir. Kurtarma yılı ile dilim kaybı aynı tabloda olmadığı için M1 ve M2'den biri seçilmedi.

## 7. Kendini sorgulama

Karar, şu üç tanıma bağlıdır. Tanım değişirse sonuç değişir.

Şok sonrası, sonraki yıl sonunun önceki yıl sonuyla karşılaştırılmasıdır. 2023'ün kendi yılına bakılırsa stok ve kısa pay birlikte yükselir (388.639'dan 432.551'e, %38,2'den %40,5'e). Metin "izleyen yıllar" dediği için karar 2024 ve 2025'e bakıyor; orada kısa pay geriliyor. Karşılaştırma şok yılının kendisine çekilirse 2023 için K2'nin stok ve kısa pay bacağı tutar, 2018 ve 2021 yine tutmaz.

Kısa vade, metaverideki orijinal vadedir. Kalan vade ayrı bir tablodur ve bu teste girmedi. Kalan vade payı 2024–2025'te yükselirse, K2'nin bu rapordaki kararı o tanıma taşınamaz.

Döviz payının paydasına kıymetli maden eklenince 2018 ve 2021'de yükseliş, 2023'te düşüş durur. Bu varsayım K3'ü çevirmez. KKM'nin döviz sayılması 2023'ü çevirebilir: o yıl korumalı stok büyüktür, mevduat serisinin birimi metadata'da yazmadığı için ekleme yapılmadı. 2025'te KKM kapanmışken döviz tevdiat payı %25,4'tür; 2021'deki %59,7'nin altındadır. KKM'nin bitmesi, payı 2021 düzeyine geri getirmemiştir.

## 8. Sonraki adım

Aynı testler duracak. Eksik olan dört tablo gelince `dilim.csv` doldurulacak: GYKA'da gelir türünün %20 payı, HBA'da dilim tüketimi, GYKA'da "çok yük" oranı, TBB/BDDK mevduat tutar dilimi. Ulusal hesap faiz ve kira toplamı aynı sürüme bağlanacak; ham ve düzeltilmiş yan yana yazılacak. Yapılandırılmış kredi stoku ve Resmî Gazete'den okunmuş kurtarma yılları gelince K1, M1 ve M2 aynı beklentiyle yeniden çalıştırılacak. Takip serisi 2023'ün aralığına uzamazsa M3 belirlenemedi kalacak.
