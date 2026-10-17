# Beş adımın enflasyon köprüsü

Modelde enflasyon dışsaldır; bu hesap model dışı bir köprüdür, sonuç modele geri beslenmez.

Beş adımın denklemleri fiyat, ticari faiz ve kur üretmez. Bu dosyadaki puan o denklemlere girdi olmaz. Kriter özeti `3310adf8cd50`.

## Dışsallık

- `adim3_faiz_durma.py:10` — r_t = TP.KTF17; gözlem 2026-09'a kadar, sonrası son değer sabit. `adim3_faiz_durma.py:77` tam çeyrek yoksa son gözlemi yazar. Beş adımın çıktısı bu satırı güncellemez. Son gözlem %53,1925.
- `adim45_maliyet.py:20` — `KUR = 49.1274` sabittir. `bes_yil_senaryo.py:148-151` döviz model etkisini `modellenmedi` bırakır; senaryo ankete eşittir.
- `adim45_birim.py:8-10` — λ = 1 iken kur çarpanı λ'dır, USD stoku durur, faiz oranı durur.
- `bes_yil_senaryo.py:134-138` — 2027–2031 enflasyon model etkisi −7,62 ile 0 arası `varsayim` bandıdır. `bes_yil_senaryo.py:142-144` faiz model etkisini `modellenmedi` bırakır. `bes_yil_senaryo.py:188` bu bandın geçiş payı kapısından geldiğini, faiz ve dövizin anketle kaldığını yazar.
- `gsyh_pay.py:31-36` enflasyon senaryosunu yalnız GSYH paydasını büyütmek için okur. Adım 3'ün I_t formülü (`adim3_faiz_durma.py:9-10`) o paydayı kullanmaz.
- `adim4_adres_yonlendirme.py:46` — «kur riski kâğıda taşınır mı, karar yok». İhraç denklemi TÜFE, TP.KTF17 veya 49,1274 okumaz.

Tek yönlü bant şudur: `bes_yil_senaryo` enflasyona mantıksal bir aralık yazar ve `gsyh_pay` onu paydada kullanır. Aralık adım 3'ün faizine, adım 4.5'in kuruna ve adım 4'ün ihraçına geri dönmez.

## Örneklem ve esneklik

Yıl sonu Aralık, tek tanım, ekleme yok. Hedef 2010–2026; 2026 Aralık henüz yok, son tam yıl 2025. TÜFE `TP.FG.J0` (2003=100). M1 `TP.HPBITABLO1.2`, M2 `TP.HPBITABLO1.11`. Para örneklemi 2010–2025, n = 16. b1 1,007 (SE 0,108; 0,796 … 1,217; nokta 1,007; 0'ı içerir: hayır). b2 1,615 (SE 0,189; 1,244 … 1,985; nokta 1,615; 0'ı içerir: hayır). Belirtme katsayısı 0,893.

Kredi `TP.KREHACBS.A1`, reel = nominal / TÜFE. GSYH `TP.GSYIH20.CY.B1GQ` yıl toplamı (dört çeyrek zincirlenmiş hacim). Örneklem 2010–2025, n = 16. d -0,978 (SE 0,271; aralık -1,509 … -0,448; nokta -0,978). h 0,093 (SE 0,067; aralık -0,039 … 0,224; nokta 0,000). h büyüme puanıdır, enflasyon toplamına yazılmaz.

Kur eğimi `TP.HPBITABLO2.11` (gerçek kişi YP, milyon ABD doları) üzerinde. n = 1. Durum: tahmin_edilemedi. tek tanımda yıl sonu farkı 8'den az

Aralık 0'ı kesen katsayının nokta puanı 0 yazılır; ±1,96 standart hata aralığı durur. Para kanalında iki katsayının ortak aralığı OLS kovaryansından gelir.

Hız özdeşliği, PY sabitken ΔV/V = −ΔM2/M2. Fiyat denklemine eklenmez.

Örneklemde yıl sonu M2 daralmaz. En küçük Δlog M2 0,113, en büyük 0,506. Düşük senaryonun tepe daralması bunun tersi yöndedir. Orta, yüksek ve 13.967'lik ayak, görülmüş bir daralmanın ölçeğinde değildir. Puan, kilitli denklemin bu şoka uygulanmasıdır.

## Yıllık TÜFE puanı

Eksi, endeksin o yıl daha yavaş artmasıdır. Para puanı stokun değiştiği yıla yazılır: düşüş 2029'da (tepe), 2029-Q1 ihraçının ilk vadesi 2031'de geri gelir. 2030'da stok tepede durur, ek para puanı yoktur. χ = 0 ise 2031 geri dönüşü 2029 düşüşünü kapatır. χ = 0,5 ise kalıcı düzey kalır; bu, enflasyon oranına her yıl yeniden eklenen puan değildir.

Maliyet 2029, 2030 ve 2031'de aynı akıştır (α = 0 ve α = 1). Kredi akışı 2030'da tepe, 2031'de kalıcıdır; 2029 tam tepe yılı diye yazılmaz. Adım 4.5 her yıl 0. Kurun skorlanan ucu Δe = 0'dır. Kira bu tabloya girmez: yılı repoda yoktur.

Hücre, M1 alt/üst ile α = 0/1 köşelerinin nokta bandıdır. **Aday.** Kanallar aynı şokun parçası olabilir. İki tablo vardır: kredi hariç ve kredi dahil.

Kredi hariç:

| Yıl | düşük | orta | yüksek |
| --- | ---: | ---: | ---: |
| 2027 | 0,00 … 0,00 | 0,00 … 0,00 | 0,00 … 0,00 |
| 2028 | 0,00 … 0,00 | 0,00 … 0,00 | 0,00 … 0,00 |
| 2029 | -10,28 … -4,32 | -37,70 … -23,20 | -84,45 … -53,17 |
| 2030 | -1,91 … 0,00 | -3,82 … 0,00 | -7,64 … 0,00 |
| 2031 | 2,41 … 8,37 | 8,43 … 17,83 | 22,33 … 42,93 |

Kredi dahil:

| Yıl | düşük | orta | yüksek |
| --- | ---: | ---: | ---: |
| 2027 | 0,00 … 0,00 | 0,00 … 0,00 | 0,00 … 0,00 |
| 2028 | 0,00 … 0,00 | 0,00 … 0,00 | 0,00 … 0,00 |
| 2029 | -10,28 … -4,32 | -37,70 … -23,20 | -84,45 … -53,17 |
| 2030 | -1,54 … 0,37 | -2,43 … 1,39 | -4,84 … 2,80 |
| 2031 | 2,41 … 8,37 | 9,13 … 18,52 | 23,72 … 44,32 |

2028 skorlanan toplam 0'dır. Araç birleşik yurt içi ayak 13.967 milyar TL ayrıdır, skora girmez, M1 payı 0 sayılır (ölçülmedi): nokta -130,49 puan, aralık -160,46 … -100,52.

## Kanallar

| Senaryo | Para 2029 (M1 alt…üst) | Para 2031 geri | Maliyet α 0…1 | Kredi 2030 | Kredi 2031 | Kira (yıl yok) | Büyüme 2030 | Büyüme 2031 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| dusuk | -8,37 … -4,32 | 8,37 … 4,32 | 0,00 … -1,91 | 0,37 | 0,00 | -0,56 … -0,21 | 0,00 | 0,00 |
| orta | -33,88 … -23,20 | 17,83 … 12,25 | 0,00 … -3,82 | 1,39 | 0,69 | -1,41 … -0,54 | 0,00 | 0,00 |
| yuksek | -76,81 … -53,17 | 42,93 … 29,97 | 0,00 … -7,64 | 2,80 | 1,39 | -2,82 … -1,07 | 0,00 | 0,00 |

Para kanalının ±1,96 ortak aralığı, M1 alt 2029 noktası için: dusuk -8,37 (-10,29 … -6,44); orta -33,88 (-41,66 … -26,10); yuksek -76,81 (-94,45 … -59,17).

Para M1 alt sınırı 0'dır: çevrilen stok vadeli sayılır. Üst sınır, θ × 6.639,4'ün vadesiz YP'ye sığan kısmıdır. Maliyet paydası GSYH 2025 = 63.240,5. α = 0,5 yazılmaz. Kira ağırlığı 0,068028 (TÜİK 2025, başlık 04111). Konut grubu kullanılmaz. Kur geçişkenliği Öğünç ve Özel, TCMB Çalışma Tebliği 25/05: bir yıl 0,26, uzun dönem 0,38 ve 0,40. Büyük-şok 0,69 kullanılmaz. Veri ucu tahmin edilemediği için geçişkenlik puan üretmez.

Kredi katsayısı d negatiftir. Örneklemde yüksek enflasyon yıllarında reel kredi gerilemiştir. Daralma şoku bu yüzden eksi değil artı puan verir. Bu bir talep çarpanı değildir. Büyüme katsayısı h'nin aralığı 0'ı keser; büyüme noktası 0'dır, aralık durur.

Kredi stoku, EVDS son gözlem 2026-08: 27.020,9 milyar TL (ham / 1e6). Yüzde daralma = ikinci tur / bu stok. Akışın stoğa bölümüdür. Büyüme satırı toplamın dışındadır.

Adım 4.5: 0. **Kanıt.** λ = 1 fiyatların TL sayısını değiştirmez (`adim45_birim.py:8-10`).

## Tutarlılık

Aşağıdaki sapma adım dosyasına yazılmaz. Δπ, o yılın kredi dahil bandının en eksi köşesidir. 2031'de para stoku geri geldiği için net nokta eksi değildir; o yıla sapma yazılmaz. Fisher adayı: model r = 53,1925'i tuttuğu için nominal duran faiz I · |Δπ| / 53,1925 kadar büyük kalır. Yön: tablodaki milyar TL, enflasyonla birlikte faizin de düştüğü bir dünyaya göre şişkindir. Reel karşılık (|Δπ| / 100) / (1 + 0,2973) oranında daha büyüktür. π_taban = 29,73. Yön: reel rahatlama, nominal tablonun sabit fiyatta ima ettiğinden büyüktür.

| Senaryo | Yıl | Δπ | Nominal fazla, milyar TL | Reel rahatlama, % |
| --- | ---: | ---: | ---: | ---: |
| dusuk | 2029 | -10,28 | 233,3 | 7,92 |
| dusuk | 2030 | -1,54 | 35,0 | 1,19 |
| orta | 2029 | -37,70 | 1.712,0 | 29,06 |
| orta | 2030 | -2,43 | 110,3 | 1,87 |
| yuksek | 2029 | -84,45 | 7.669,2 | 65,09 |
| yuksek | 2030 | -4,84 | 439,2 | 3,73 |

Kur sabiti: skorlanan Δe = 0 iken TL'ye çevrilmiş YP stoğu bu kanaldan sapmaz. Veriden Δe üretilemediği için |Δe/e| kadar şişkinlik sayısı yoktur. Δe eksi olsaydı sabit 49,1274, değerlenen TL dünyasında YP'yi büyük gösterirdi.

α = 0 köşesinde maliyet 0'dır; o köşede Fisher sapması da 0'dır. Bant bu iki uçtur. Orta diye α = 0,5 konmaz. Yüksek 2029 köşesinde |Δπ| yüzde 53,19'u aşar. I · |Δπ| / r o köşede duran faizin kendisinden büyük çıkar. Formül kilitli olduğu için sayı durur; bu köşe, faizin enflasyon kadar inip pozitif kaldığı bir okumanın dışındadır.

## Halk dili

Model enflasyonu, faizi ve dolar kurunu kendisi üretmez; onları dışarıdan sabit alır. Buradaki hesap o sabitlere geri yazılmaz. Geçmişte yıl sonu M2 her yıl artmıştır. Eğim bu artışlardan gelir. Adımların M2'yi düşürmesi bu örneklemin dışındadır. Denklem yine de uygulanırsa orta senaryoda 2029'da fiyat artışı 23,20 ile 37,70 puan daha yavaştır. Bu, stokun düştüğü yılın geçişidir; her yıl süren bir oran değildir. 2031'de senetlerin bir kısmı mevduata dönünce bu puanın bir kısmı geri gelir. Durdurulan faizin fiyata geçişi ayrıdır: ortada 0 ile 3,82 puan daha yavaş, 2029-2031 boyunca her yıl. Kredi daralmasının geçmişteki izi fiyatı yavaşlatmak yönünde çıkmamıştır; büyüme puanının noktası 0'dır. Kira ayrıdır; hangi yıla denk geleceği repoda yazılı değildir. Kurun ne kadar oynayacağı bu seriyle ölçülememiştir. Skor, kurun 49,1274'te kalmasıdır.
