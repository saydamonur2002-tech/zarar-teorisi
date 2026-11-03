# Kur müdahalesinin rezerv maliyeti

Ön kayıt `ON_KAYIT.md` içinde 2026-10-20T09:12:13Z kilitlendi. Katsayılar ondan sonra hesaplandı. Eşikler kaydırılmadı. Ayrılan yerler o dosyada SAPMA diye durur.

## Hüküm

Birincil c = 3,11 milyar dolar / puan [VEKİL], kaynak: bastırma görülen epizotların satış ağırlıklı ortalaması. Bu sayı yalnız 2019-Q1–2020-Q4 penceresinden gelir. %95 aralık: sınırlı değil. Aralık olmadığı için “c ≤ 10” ve “c ≥ 30” yanlışlanamaz.

Izgara hükmü: BELİRSİZ. “c ≤ 10” yanlışlandı: hayır. “c ≥ 30” yanlışlandı: hayır. Aralık hem 10’u hem 30’u örtüyorsa veya aralık yoksa ön kayıt BELİRSİZ der.

`model_rr.py` çalışma ağacında yok (DOĞRULANMADI). b = 1,26 ve b = 0,42 için üç kural koşusu yapılmadı. Hüküm, rezervin bittiği çeyrek ve TÜFE yolu her iki b için de [DOĞRULANMADI]. 2029-Q3 ve 2031 tarihleri bu dosyada üretilmedi.

Bu c, koşullu beraberliktir. Satış baskı yükselince arttığı için OLS, θ’yı sıfıra veya pozitife iter ve c’yi büyük gösterebilir. Karşı-olgusuz nedensellik cümlesi yok. Epizot P’si “epizot dışı beraberlikten sapma”dır [HESAP]; “müdahale olmasaydı kur şöyle olurdu” denmez.

## Veri

Kur E, TCMB USD/TRY döviz satış kurunun aylık ortalamasının çeyrek içi aritmetik ortalamasıdır [VERİ] `TP.DK.USD.S.YTL`. g = 100 × ln(E_t / E_{t−1}) [HESAP].

Politika faizi, BIS derlemesi Türkiye merkez bankası politika faizi aylık düzeyinin çeyrek ortalamasıdır [VERİ] `TP.BISPOLFAIZ.TUR`. Bir hafta repo bu seridedir. Ağırlıklı ortalama fonlama (`TP.APIFON4`) panelde durur, denkleme girmez.

Cari işlemler [VERİ] `TP.ODANA6.Q01`, milyon dolardan milyar dolara bölündü, çeyrek toplamı. Portföy, yurt dışı yerleşik tarafı [VERİ] `TP.ODANA6.Q17` (portföy net yükümlülük oluşumu). Pozitif değer, şablonun “yükümlülük oluşumu” işaretidir. Dolarizasyon [VERİ] `TP.KM.G49` / `TP.KM.G57` (döviz tevdiat / mevduat toplamı, bin TL, oran birimsiz).

CDS serisi bulunamadı [DOĞRULANMADI]. γ3 ve epizot denklemindeki b3 çıktı (SAPMA-kontrol).

Swap hariç net [HESAP], milyar dolar: (resmi rezerv `TP.REZVARPD.K1` + forward/swap net `TP.DOVVARNC.K14` + diğer `TP.DOVVARNC.K23`) / 1000. Ons [VERİ] `TP.REZVARPD.K11` milyon troy ons. Ons fiyatı [VERİ] `TP.MK.LON.YTL` ABD doları/ons. Değerleme = önceki ayın ons × fiyat farkı [HESAP].

Altın stoku / (ons × fiyat) oranı, gözlem olduğu her ayda 0,96 ile 1,06 arasında kaldı (n = 120) [HESAP]. 1’den uzaklık, Londra satış fiyatı ile TCMB’nin altın değerleme fiyatının aynı olmamasından gelebilir.

Birincil S kurulamadı. Doğrudan TCMB satışı yayımlı; kamu bankası (arka kapı) satışı çeyrek çeyrek yayımlı değil [DOĞRULANMADI]. Ön kayıt, ikisi birden yoksa toplamı kurmaz ve eksiği diğeriyle doldurmaz. Dolaşan “yaklaşık 128 milyar dolar” rakamı S’ye yazılmadı. Hükmün satış serisi vekildir [VEKİL], SAPMA-formul işaret düzeltmesiyle.

Yayımlanmış TCMB satışı ayrı sütundur [VERİ]: aylık PDF’te KİT’lere satış + doğrudan müdahale satışı + satım ihalesi. 2018–2025’te satım ihalesi sütunu boştu; dolu olanlar KİT satışı ve, yalnız Aralık 2021 ile Mart 2025’te, doğrudan müdahaledir. PDF: TCMB “Monthly Buying and Selling Amounts”, milyon ABD doları. Aralık 2021 müdahalesi 7,278 milyar, Mart 2025 müdahalesi 1,134 milyar; aynı iki tutar “Doğrudan döviz müdahaleleri” listesinde de durur.

Yan kanal, S’ye eklenmedi. İhracat reeskontu [VERİ] aynı PDF’in alım sütunu ve stok `TP.RKDRK01`. KKM stoku [VERİ] `TP.KKM.K1` milyar dolar; dönüşümün döviz satış tutarı ayrı yayımlanmadığı için akıma çevrilmedi [DOĞRULANMADI]. İhracatçı döviz teslim zorunluluğunun tutarı ayrı seri olarak bulunamadı [DOĞRULANMADI].

EVDS çağrısı `https://evds3.tcmb.gov.tr/igmevdsms-dis/fe` POST, anahtarsız, `groupSeperator` false. İç uç nokta kullanılmadı. Sertifika atlanmadı. TÜİK’e gidilmedi.

Cari işlemler yıllık toplamı, milyar dolar [VERİ, çeyreklerin toplamı]: 2018: -14,6 (çeyrek sayısı 4), 2019: 15,0 (çeyrek sayısı 4), 2020: -31,0 (çeyrek sayısı 4), 2021: -7,1 (çeyrek sayısı 4), 2022: -46,7 (çeyrek sayısı 4), 2023: -41,8 (çeyrek sayısı 4), 2024: -13,6 (çeyrek sayısı 4), 2025: -30,3 (çeyrek sayısı 4).

## Yöntem

Örnek 2018-Q1–2025-Q4. 2026 yok. Eksik çeyrek doldurulmadı. Denklem, CDS’siz:

g_t = α + θ S_t + γ1 i_{t−1} + γ2 CA_{t−1} + γ4 portföy_{t−1} + γ5 dolarizasyon_{t−1} + γ6 g_{t−1} + ε

S, vekil satış, milyar dolar. Newey-West gecikme 4. c = −1/θ. θ’nın %95 aralığı sıfırı içerirse veya θ negatif değilse c’nin sonlu aralığı yazılmaz. Aralık sıfırın dışında ve θ negatifse se(c) = se(θ) / θ², aralık c ± 1,96 se(c).

Vekil: S = max(0, −ΔR + altın değerlemesi + min(CA, 0)). Literal kilitli işaret (−ΔR − değerleme) panelde `s_literal` diye durur, hükme girmez (SAPMA-formul).

Epizot karşı-olgusu yalnız epizot dışı çeyreklerde, CDS’siz ve dolarizasyonsuz kurulur. Bastırılan puan = max(0, P − g) ve ancak S > 0 ise. Epizot c = S toplamı / bastırılan puan. Payda ≤ 0 ise “bastırmadı”, ortalamaya girmez. Sonraki 4 çeyrekteki fazla değer kaybı Σ max(0, g − P). ≥ %70 erteledi, < %30 geri gelmedi, arası kısmi. 4 çeyrek yoksa test boş.

Araç Z, kilitli epizot pencerelerinde 1. Birinci aşama F, Newey-West t istatistiğinin karesidir. F < 10 ise IV birincil değildir.

## Epizotlar

| Kod | Pencere | S, milyar $ [VEKİL] | Bastırılan puan [HESAP] | c | Çeyrek dışarıda min–max | Sonraki 4 çeyrek |
| --- | --- | --- | --- | --- | --- | --- |
| E1 | 2018-Q3–2018-Q4 | 18,69 | 0,00 | bastırmadı | yok | sınıflanmadı; fazla 5,62 puan |
| E2 | 2019-Q1–2020-Q4 | 69,60 | 22,39 | 3,11 | 2,01 – 5,26 | erteledi; fazla 22,75 puan |
| E3 | 2021-Q4–2021-Q4 | 4,87 | 0,00 | bastırmadı | yok | sınıflanmadı; fazla 11,42 puan |
| E4 | 2023-Q1–2023-Q2 | 2,21 | 0,00 | bastırmadı | yok | sınıflanmadı; fazla 23,06 puan |
| E5 | 2023-Q3–2023-Q4 | 0,45 | 0,00 | bastırmadı | yok | sınıflanmadı; fazla 7,71 puan |
| E6 | 2025-Q1–2025-Q1 | 0,00 | 0,00 | satış yok | yok | 4 çeyrek yok |

Min–max, örnekleme anlamında %95 aralık değildir. Epizot dışı regresyonun gözlem sayısı ve R² raporun sayı ekinde.

Bastırma görülen epizotların satış ağırlıklı c’si: 3,11 [VEKİL] [HESAP]. Bu ortalama tek epizottan gelir: E2. Diğer pencereler paydada sıfır kaldığı için ortalamaya girmedi.

E2’nin payı, penceredeki bütün vekil satıştır; g’nin P’nin üstünde kaldığı çeyrekler de paydadır. Bastırmayan ama satışı olan çeyrekler: 2019-Q2 satışı 6,34, 2020-Q2 satışı 24,67 [HESAP]. Bastıran çeyrekler: 2019-Q1, 2020-Q1, 2020-Q3.

E2’den sonraki dört çeyrek [HESAP]:

| Çeyrek | g | P | fazla = max(0, g−P) |
| --- | --- | --- | --- |
| 2021-Q1 | -6,58 | 2,65 | 0,00 |
| 2021-Q2 | 12,73 | 8,07 | 4,66 |
| 2021-Q3 | 2,00 | 7,40 | 0,00 |
| 2021-Q4 | 25,97 | 7,88 | 18,09 |

Toplam fazla 22,75 puan, bastırılan 22,39 puanın yanında ön kaydın %70 eşiğine göre “erteledi” diye yazılır. 2021-Q4’ün fazlası 18,09 puandır. Bu, “baskı kalıcı olarak dengelendi” cümlesi değildir. P yapısal karşı-olgu değildir.

Aynı P ile, yayımlanmış TCMB satışı (KİT + müdahale + ihale) [VERİ] epizot oranı ayrıca şöyledir. Bu sütun hükmün c’si değildir. Payda 0,05 puandan küçükse c yazılmaz. Küçük c, az yayımlanmış satışın büyük bir P−g farkına bölünmesidir; o fark satışa bağlanmaz.

| Kod | S, milyar $ [VERİ] | Bastırılan puan | c |
| --- | --- | --- | --- |
| E1 | 2,67 | 11,59 | 0,23 |
| E2 | 12,44 | 46,44 | 0,27 |
| E3 | 13,12 | 0,00 | bastırmadı |
| E4 | 0,00 | 0,00 | satış yok |
| E5 | 0,00 | 0,00 | satış yok |
| E6 | 1,13 | 0,00 | bastırmadı |

Aralık 2021 doğrudan müdahalesi 7,278 milyar dolar ve o çeyreğin KİT satışıyla birlikte S = 13,12’dir [VERİ]. g = 25,97, P = 7,88; değer kaybı epizot dışı uyumun üstünde kaldı, bastırılan puan 0. Mart 2025 müdahalesi 1,134 milyar dolardır [VERİ]. O çeyrekte g ve P ikisi de 4,80; bastırılan puan 0’a yapışıktır, c üretilmedi.

Kilitli pencere dışında 2024-Q1 vekil satışı 19,38 milyar dolardır [VEKİL]; yayımlanmış TCMB satışı o çeyrekte 0,00. Yeni epizot eklenmedi.

## Havuz regresyonu

n = 32, R² = 0,18. İlk çeyrek 2018-Q1, son 2025-Q4.

θ = 0,2279, Newey-West se = 0,1585, %95 [-0,08, 0,54].
θ pozitif ve aralık sıfırı içeriyor. Bastırma beraberliği ayırt edilemedi. Pozitif işaret, ön kayıttaki içsellikle uyumludur: satış, değer kaybı yüksekken artınca θ yukarı itilir. Bu, “satış değer kaybını artırdı” iddiası değildir.

Diğer katsayılar (gecikmeli kontroller), aynı Newey-West:

| Katsayı | Nokta | se | %95 |
| --- | --- | --- | --- |
| sabit | 21,4792 | 13,4303 | [-4,84, 47,80] |
| S | 0,2279 | 0,1585 | [-0,08, 0,54] |
| faiz_gecikme | -0,1721 | 0,1138 | [-0,40, 0,05] |
| ca_gecikme | -0,0873 | 0,2145 | [-0,51, 0,33] |
| portfoy_gecikme | -0,3157 | 0,3662 | [-1,03, 0,40] |
| dolarizasyon_gecikme | -29,5450 | 26,4895 | [-81,46, 22,37] |
| g_gecikme | 0,0596 | 0,1319 | [-0,20, 0,32] |

Birinci aşama: n = 32, Z katsayısı = 4,4016, F = 3,49. F < 10 ise IV birincil değildir. Bu turda IV birincil değil.

## Yayımlanmış TCMB satışı (hüküm değil)

S = KİT satışı + doğrudan müdahale + satım ihalesi [VERİ]. n = 32, θ = 1,7011, se = 0,1992.
θ pozitif ve aralık sıfırın dışında. Yayımlanmış satış ile çeyreklik değer kaybı aynı yönde beraber hareket ediyor. Karşı-olgu yok; bu bir neden cümlesi değildir. c yazılmadı.

## Birikme ve rezerv düzeyi

φ = -0,0262, se = 0,2496, %95 [-0,52, 0,46]. birikme ayırt edilemedi. φ tek başına neden değildir. n = 31.

R medyanı = 64,84 milyar dolar. θ0 = -0,3224, θ1 = 0,4636, θ1 %95 [-0,35, 1,28]. yükseliş ayırt edilemedi.

## Zayıf noktalar

- Birincil c tek pencereden gelir ve o pencere “erteledi” diye sınıflanmıştır. Sonraki fazla değer kaybının büyük parçası 2021-Q4’tedir. Kalıcı dengeleme diye okunmaz.
- Epizot c’sinin payı, bastırmayan çeyreklerin satışını da içerir. Bu, kilitli oran kuralıdır ve c’yi, yalnız bastıran çeyrekler alınsaydı çıkacak orandan büyük tutar.
- Vekil satış, swap hariç netin düşüşünden cari açık ve altın fiyatı ayrıldıktan sonra kalan artı kısımdır. Brüt rezerv artmadan forward/swap açığı büyürse bu düşüş vekile girer. Kamu bankasının kendi bilançosundan sattığı döviz, TCMB’nin bu ölçülen stokunu o çeyrekte düşürmediyse vekile girmez. 69,60 milyar dolar, dolaşan 128 milyar dolarlık iddianın karşılığı değildir.
- Epizot dışı örnek 16 çeyrektir. P’nin faiz katsayısı bu kısa örnekte pozitiftir. P yapısal değildir.
- İçsellik durur. Anlatı aracı epizot takvimidir; dışsallık kanıtlanmadı. Birinci aşama F eşiğin altında kaldı, IV birincil yazılmadı.
- Newey-West gecikme 4, çeyrek sayısı 32 iken standart hatalar geniştir. Havuz θ’sının aralığı sıfırı içerir ve işaret pozitiftir; havuzdan sonlu c çıkmaz. Izgara BELİRSİZ’dir çünkü birincil c’nin örnekleme aralığı yoktur. Çeyrek dışarıda bırakma aralığı %95 diye kullanılmadı. Eşik kaydırılmadı.
- `model_rr.py` repoda ve çalışma ağacında yoktu. b = 1,26 ve b = 0,42 koşusu, tükeniş çeyreği ve TÜFE yolu üretilmedi.
- Kamu bankası satışının resmi çeyreklik satırı bulunamadı. Sayıştay düzenlilik raporları ve TBMM soru önergesi bu tutarı bir zaman serisi olarak vermiyor. 128 milyar dolar S’ye yazılmadı.

## Sayı eki

Çeyrek panel `ceyrek_panel.csv`. Ham EVDS `ham/evds_aylik.json`. Aylık TCMB satış `ham/tcmb_satis_aylik.json`. Makine özeti `sonuclar.json`.
Epizot dışı n = 16, R² = 0,33. Katsayı sırası: sabit, faiz, cari, portföy, g gecikmesi. Noktalar: 7,7937, 0,0217, 0,0637, -0,6852, -0,0136.
