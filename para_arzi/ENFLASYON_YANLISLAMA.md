# Enflasyon etkisi — yanlışlama ölçütleri

Bu dosya hesap çalışmadan yazıldı. `enflasyon_etki.py` sayıyı ancak bu kurallarla üretir. Ölçüt değişirse json'daki `kriter_sha256` tutmaz.

Köprü, beş adımın denklemlerine yazılmaz. `adim3_faiz_durma.py`, `adim45_maliyet.py` ve `bes_yil_senaryo.py` bu dosyayı okumaz.

## Dışsallık (kod)

Beş adımın fiyat, faiz ve kur çıktısı yoktur.

- TÜFE tabanı `bes_yil_senaryo.py` içinde EVDS son gözlemidir ve her yıl aynı sayı olarak yazılır. 2027–2031 için enflasyon «model etkisi» −7,62 ile 0 arası mantıksal bir banttır (`varsayim`); faiz ve dövizin model etkisi `modellenmedi`dir. Bu bant adım 3'ün `r_t` satırına, adım 4.5'in kur sabitine ve adım 4'ün ihraçına geri yazılmaz.
- Ticari faiz: `adim3_faiz_durma.py` tam çeyrek yoksa son TP.KTF17 gözlemini sabitler. Beş adımın hiçbir çıktısı bu seriyi güncellemez.
- Kur: `adim45_maliyet.py` içinde `KUR = 49.1274` sabittir. `bes_yil_senaryo.csv` tabanı 2026–2031 boyunca aynı sayıdır. Beş adımın çıktısı bu sabiti değiştirmez.
- `gsyh_pay.py` enflasyon senaryosunu yalnız GSYH paydasını büyütmek için okur. O payda adım 3'ün `I_t` formülüne girmez.

**Yanlışlama.** Adım 3, 4, 4.5 veya 5'in kodu TÜFE, TP.KTF17 veya 49,1274'ü kendi çıktısından yeniden yazıyorsa «dışsal» denmez. Bu köprünün json'u o dosyalara girdi olursa «geri beslenmez» denmez.

## Ortak

Etki, yıllık TÜFE'ye puan olarak yazılır. Eksi, endeksin daha yavaş artmasıdır. Her kanal ayrıdır. Toplam, kanalların aritmetik toplamıdır ve **aday**dır: kanallar aynı mevduat şokunun parçaları olabilir, toplam üst zarftır. Para kanalı ile kredi kanalı aynı şoktan gelir; ikisi birden toplanmış toplamın yanında, kredi hariç toplam da yazılır.

Senaryo kilidi, PR #34 `m2_etki.json` ile aynıdır:

| Senaryo | Adım 4 kalıcı M2 | Adım 4 tepe M2 | κ (adım 3) | Kira kapsaması | Kredi, kalıcı / tepe (milyar TL/yıl) |
| --- | ---: | ---: | ---: | ---: | ---: |
| düşük | 0 | 1.272,25 | 0,25 | 0,20 | 0 / 101,78 |
| orta | 2.384,575 | 4.769,15 | 0,50 | 0,50 | 190,766 / 381,532 |
| yüksek | 4.769,15 artı birleşik ayak 13.967 (aday) | 9.538,3 artı aynı ayak | 1,00 | 1,00 | 381,532 / 763,064 |

Yüksek senaryoda birleşik ayak ayrı satırda durur. Skorlanan toplam, ayaksız yüksek satırdır. Ayaklı sayı üst zarf diye işaretlenir.

Zaman:

- Adım 1–2'nin M2 ayağı skorlanan kuralda 0'dır. Birleşik ayak 2028 (K2 penceresi) ve adaydır.
- Adım 4 (para, kur, kredi) ihraç 2029, tepe 2030-Q4'e kadar, vade 8 çeyrek. χ = 0 ise 2031 sonunda kalıcı 0. χ = 0,5 ise 2031'den kalan stok kalıcıdır.
- Adım 3 tam yıl 2029–2031 (`adim3_faiz_durma_sonuc.json`); 2028 kısmi.
- Adım 4.5 2030, etki 0.
- Adım 5'in yılı repoda yok (`gsyh_pay.py`). Yıl uydurulmaz; akış, kapsama durduğu sürece yıllıktır.

## 1. Para

M2 düşüşünün vadeli kısmı ile M1 ayrılır.

- M1 = dolaşım + vadesiz TL + vadesiz YP (`m2_etki.json`, 27-03-2026). Vadeli TL + vadeli YP, M2 − M1'dir.
- Adım 4'ün adresi vadeli mevduat ve gerçek kişi YP'dir. Vadeli kısım M1'i değiştirmez. YP'nin vadesiz payı ölçülmediği için M1 etkisi için alt sınır 0'dır (tamamı vadeli sayılır). Üst sınır, gerçek kişi YP satırının θ katının M1'deki vadesiz YP'ye sığdığı kadardır. Sığmayan kısım vadeliye yazılır.
- Hız: PY sabitken vadeli çıkış M2'yi küçültür, V = PY/M2 aynı oranda büyür. Bu özdeşliktir, fiyat tahmini değildir. Fiyat denklemine eklenmez.

Esneklik, EVDS yıllık farklardan, uydurulmaz. Örneklem, TÜFE ile M1 ve M2'nin ortak yıllarıdır; 2010–2026 hedeflenir, tanımlar eklenerek uzatılmaz, ortak pencere neyse o yazılır. Aralık: yıl sonu.

  Δlog TÜFE_t = a + b1·Δlog M1_t + b2·Δlog(M2/M1)_t + u_t

OLS, başka kontrol yok. b1 ve b2 **aday**dır (indirgenmiş biçim, nedensellik değil).

Fiyat puanı = 100 · (b1·Δlog M1 + b2·Δlog(M2/M1)). Δlog M1 alt senaryoda 0. b1 veya b2'nin tahmin aralığı 0'ı içerirse o katsayının fiyat puanı 0 yazılır ve aralık ayrıca durur. Aralık, katsayının ±1,96 standart hatasıdır. İki katsayının birlikte ürettiği puan aralığı, OLS kovaryansından delta yöntemiyle ayrıca yazılır; bu aralık noktanın yerine geçmez. Standart hata hesaplanamazsa (n < 8) kanal «tahmin edilemedi» diye boş kalır, sayı uydurulmaz.

## 2. Kur

Kurun kendisi modelde `modellenmedi`. Alt sınır Δe = 0: `adim4` «kur riski kâğıda taşınır mı, karar yok» der; risk kâğıtta kalırsa döviz talebi düşmez.

Üst sınır ancak veriden: yıllık Δlog(USD/TRY) üzerinde gerçek kişi YP mevduatının (USD) yıllık Δlog'unun OLS eğimi β, 2010–2026 ortak penceresi, tek tanım. β **aday**. Şok eksidir: mevduat azalır. Δe/e = β · log(1 − θ · YP_adres / YP_stok). YP_adres = 6.639,4 milyar TL. YP_stok, aynı gerçek kişi YP satırının 2026-03 gözlemidir; adresle aynıysa oran θ olur. Kur 49,1274, TL stokunu dolara çeviren gözlemdir. Eğim 0'ı içerirse üst sınır da 0 yazılır. Yıl sonu farkı 8'den azsa üst sınır «tahmin edilemedi» kalır; arşiv tanımı eklenerek pencere uzatılmaz.

Geçişkenlik **kanıt**, yayın: Öğünç ve Özel, TCMB Çalışma Tebliği 25/05, Nisan 2025. Ilımlı şok, Model 1, bir yıl %26; model ortalaması uzun dönem %38–40. Bu deney çeyreklik %20 kur şoku değildir; %69 büyük-şok bandı kullanılmaz. TÜFE puanı = 100 · (Δe/e) · geçiş. Bir yıl 0,26, uzun dönem 0,38 ve 0,40. 100, oranı yüzde puana çevirir. Eksi kur (TL değerlenmesi) eksi puandır.

## 3. Maliyet

I, 2029 etkin duran faizdir: κ = 0,25 / 0,5 / 1 için 1.207,6 / 2.415,6 / 4.830,8 milyar TL/yıl (`BES_ADIM_MALIYET.md`). Payda GSYH 2025 = 63.240,5 milyar TL (`tavan_akis.csv`). 2029 GSYH'si ölçülmedi; payda kaydırılmaz.

Puan bandı = −100 · (I / GSYH) · α, α ∈ {0, 1}. 100, GSYH payını yüzde puana çevirir; para, kira ve kredi formülleri aynı birimi yazar. α = 0 ve α = 1 mantıksal uçtur (`bes_yil_senaryo` geçiş bandı ile aynı tür). Orta diye 0,5 yazılmaz. Senaryo tablosunda maliyet kanalı bu bandın iki ucudur. Yön: faiz maliyeti düşünce fiyatlar, geçiş varsa, daha yavaş artar. 2029–2031 akıştır; 2031'de de sürer çünkü `r_t` sabit ve stok kapanmaz.

## 4. Kira

Ağırlık **kanıt**: TÜİK TÜFE metodoloji belgesi, 2025 sepeti, temel başlık 04111 Gerçek kira, 6,8028. Konut grubu (15,2156) kullanılmaz.

Piyasa kirası 24.783–30.291 TL/ay, fark 4.783–10.291 (`BES_ADIM_MALIYET.md`). Yüzde düşüş = fark / piyasa. Alt: 4.783/30.291. Üst: 10.291/24.783. Kapsama 0,20 / 0,50 / 1,00 **aday**.

Puan = −100 · 0,068028 · kapsama · (fark/piyasa). Yıl repoda yok. Akış, kapsama açıkken yıllık; kalıcı bir stok değildir.

## 5. Kredi

Orta senaryo bandı, PR #34 ikinci turudur: kalıcı 190,766, tepe 381,532 milyar TL/yıl. Kullanıcının 191–382 yuvarlaması yerine json yazılır.

Esneklik, aynı ortak yıllık pencerede, uydurulmaz:

  Δlog TÜFE_t = c + d · Δlog(reel kredi)_t + u_t
  Δlog GSYH_t = g + h · Δlog(reel kredi)_t + u_t

Reel kredi = nominal kredi / TÜFE. d ve h **aday**. Kredi stoku EVDS banka kredisi, 2026'ya en yakın gözlem. Yüzde daralma = (ikinci tur) / stok. Bu bir akışın stoğa bölümüdür; stoktan silinen kredi değildir. **Aday** ölçek.

Enflasyon puanı = 100 · d · Δlog(reel kredi). Büyüme puanı ayrı satırdır, enflasyon toplamına eklenmez: 100 · h · aynı Δlog. d veya h'nin aralığı 0'ı içerirse nokta 0, aralık durur.

## 6. Adım 4.5

λ = 1 iken fiyatların TL sayısı değişmez (`adim45_birim.py`). TÜFE mal sepetidir, birim adının yeniden yazılması değildir. Doğrudan puan 0. **Kanıt.** **Yanlışlama:** λ = 1 iken kod TL fiyatını değiştiriyorsa 0 yazılmaz.

## Tutarlılık (geri besleme yok)

Hesap bittikten sonra, bulunan toplam puan Δπ (eksi) ile şu sapma yazılır. Formül şimdi kilitlidir:

- Nominal adım 3: Fisher **aday** varsayımıyla r, Δπ kadar iner. Model r = 53,1925'i tuttuğu için nominal duran faizi I · |Δπ| / 53,1925 kadar büyük bırakır. Yön: tablodaki milyar TL, enflasyonla birlikte faizin de düştüğü bir dünyaya göre şişkindir.
- Reel değer: nominal I sabitken fiyat düzeyi π_taban = 29,73 (2026-09, `bes_yil_senaryo.csv`) yerine π_taban + Δπ ile büyürse, bir yıllık reel karşılık yaklaşık (|Δπ| / 100) / (1 + 0,2973) oranında daha büyüktür. Δπ yüzde puandır; 100'e bölünmesi sonucu oran yapar. Yön: reel rahatlama, nominal tablonun sabit fiyatta ima ettiğinden büyüktür.
- Kur sabiti: Δe = 0 ise TL'ye çevrilmiş YP stoğu sapmaz. Δe ≠ 0 ise YP'nin TL karşılığı |Δe/e| oranında şişkindir. Yön: sabit 49,1274, değerlenen TL dünyasında YP'yi büyük gösterir.

Bu üç satır adım dosyalarına yazılmaz.
