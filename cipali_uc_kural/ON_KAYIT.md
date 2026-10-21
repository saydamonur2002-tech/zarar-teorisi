# Ön kayıt — çıpalı üç kural

Yazım zamanı (UTC): 2026-10-21T07:01:45Z

Bu dosya, beklenti denkleminin katsayıları hesaplanmadan ve senaryo koşulmadan yazıldı. Eşikler skor görüldükten sonra kaymaz. Uygulama ayrılırsa satır SAPMA diye işaretlenir; eşik o satırla değişmez.

0,37 ve 0,71 bu dosyanın girdisi değildir. Geriye bakışlı katsayı bu turda yeniden tahmin edilir. O iki sayı rapora “hedef” diye yazılmaz.

## Soru

Çıpa, 24 ay enflasyon beklentisinin hedefe bağlılığıdır. Soru: bu bağlılık geri gelirse kilitli üç kural senaryoda çalışır mı?

Üç kural `uc_kural_senaryo.py` içindeki kilitli senaryodur: (1) ücret tabanı, (2) kredi tavanı, (3) geri alma. Bu dosya o üçünün 2031-Q4 çıktısını yeniden yazmaz. `SENARYOLAR` üçlüsü durur. Çıpalı koşu ayrı dizindedir.

## Ne üzerine kurulduğu

`uc_kural_senaryo.py` içinde faiz kuralı ve rezerv stoku yoktur. Senaryo enflasyonu tek sayıdadır (`tufe_yol`). Bu tur o dosyayı sessizce genişletmez.

Faiz / kur katmanı, depodaki denklem biçimidir, o dosyaların yazılı katsayısı değildir:

- Faiz: `adim_faiz_tepki.py` biçimi, beklenti terimi eklenmiş. Katsayı bu turda rejim rejim tahmin edilir. `adim_faiz_tepki.json` okunmaz.
- Kur: `faiz_kur_kalibre.py` biçimi, gecikmeli faiz. Katsayı bu turda rejim rejim tahmin edilir. `faiz_kur_kalibre.json` okunmaz.
- Rezerv / müdahale: brüt rezerv stoku ve satış başına değer kaybı. `kur_mudahale_c` dalındaki c sayısı (ve “3,11”) girdi değildir. O dal birleştirilmez. c bu turda aşağıdaki vekille yeniden kurulur; kurulamazsa rezerv hükmü BELİRSİZ kalır, sıfır yazılmaz.

## Veri

Yalnız birincil satır. Haber rakamı yok. EVDS anahtarı okunmaz, yazdırılmaz. Çekiş EVDS3 herkese açık uçtur: `https://evds3.tcmb.gov.tr/igmevdsms-dis` POST, anahtarsız. Sertifika doğrulaması açık kalır.

Katalog adları bu yazımdan önce bakıldı; katsayı bakılmadı.

| Nesne | Kod | Katalog adı |
| --- | --- | --- |
| 24 ay beklenti | TP.PKAUO.S01.F.U | 24 Ay Sonrasının Yıllık TÜFE Beklentisi (% Değişim) |
| Fonlama faizi | TP.APIFON4 | TCMB Ağırlıklı Ortalama Fonlama Maliyeti |
| Kur | TP.DK.USD.S.YTL | ABD doları döviz satış |
| TÜFE arşiv | TP.FG.J0 | Genel tüketici endeksi (arşiv) |
| TÜFE 2025 baz | TP.TUKFIY2025.GENEL | Genel endeks |
| Brüt rezerv | TP.AB.TOPLAM | Toplam, milyon ABD doları |

Faiz araması, skor öncesi: `bie_ppkfaiz`, `bie_faizorani`, `bie_pyfaiz` boş döndü. Bir haftalık repo bu üç grupta yok. Koşuda ayrıca TCMB’nin yayımladığı faiz tablosu bir kez denenir. Tablo inip ay sonu bir hafta repo oranını verirse hüküm faizi odur, APIFON4 hüküm faizi olmaz. Tablo inmezse hüküm faizi APIFON4’tür ve etiket [VEKİL] kalır; SAPMA-faiz yazılır, eşik kaymaz.

Hedef: her ay 5. Koşuda TCMB’nin nokta hedef belgesi bir kez denenir. Belge bir yılda 5’ten farklı nokta hedef gösterirse o yılın hedefi belgedeki sayıdır, SAPMA-hedef yazılır, eşik kaymaz. Belge inmezse bütün aylar 5 kalır ve etiket [DOĞRULANMADI]. Belirsizlik bandı (±2) hedef değildir.

Örnek ayı, serinin kendisi belirler. Son ay 2026-10’u aşmaz. Eksik ay doldurulmaz. Çeyrek, üç ayı da varsa kurulur.

Geçmiş enflasyon, yüzde: π_t = 100 × (P_t / P_{t−12} − 1). P, t ve t−12 ikisi de TP.FG.J0’da varsa odur. Değilse ikisi de TP.TUKFIY2025.GENEL’de varsa odur. İkisi birden yıllık yüzde verirse ve mutlak fark 0,30 puandan büyükse 2025 bazındaki yüzde kullanılır, aylar SAPMA-endeks’e yazılır. Fark 0,30’un içindeyse arşiv yüzdesi durur. Ortalama alınmaz.

Kur şoku, birincil: g12_t = 100 × ln(USD_t / USD_{t−12}), USD aylık satış. Satış serisi yoksa alış TP.DK.USD.A.YTL ve SAPMA-kur; eşik kaymaz.

## Rejimler

Skor öncesi kilitli. Yeni rejim eklenmez. 2014–2015 ayrı rejim değildir.

| Kod | Ay |
| --- | --- |
| R2013 | 2013-01 .. 2013-12 |
| R1617 | 2016-01 .. 2017-12 |
| R1823 | 2018-01 .. 2023-12 |
| R2426 | 2024-01 .. örnekteki son ay |

Açıklayıcı, senaryo parametresi değil: Y2018 = 2018-01 .. 2018-12. Geriye bakışlı katsayının 2013’ten 2018’e yeniden tahmini bu iki penceredir (R2013 ve Y2018). Senaryo (a)–(d) Y2018 katsayısını kullanmaz.

Bir rejimde n < 10 veya bir regresörün varyansı sıfırsa o katsayı BELİRSİZ. Yerine başka rejimin katsayısı konmaz.

## Beklenti denklemi

Aylık, rejim içi, serbest terimsiz:

e_t − π_t = w × (h_t − π_t) + φ × g12_t + ε_t

e, 24 ay beklentisidir. h hedeftir. w çıpa ağırlığıdır. Geriye bakışlı katsayı 1 − w’dir. w [0, 1] aralığına kırpılmaz; ham katsayı yazılır ve senaryo (b) ham w’yi kullanır.

Bu kısıt, hedefin rejim içinde sabit olduğu durumda da w’yi ayırır. Serbest terimli ve hedefin ayrı katsayılı OLS ayrıca yazılır, hükmün w’si değildir: hedef sabitken sabit terim ile hedef katsayısı ayrılmaz.

φ, kur duyarlılığıdır. Birincil kur şoku g12’dir.

## Geçiş

Aylık, rejim içi:

π1_t = α + λ × g1_t + ε_t

π1_t = 100 × ln(P_t / P_{t−1}). g1_t = 100 × ln(USD_t / USD_{t−1}). λ aynı ayın kurdan fiyata geçiş oranıdır. Gecikmeli kur, duyarlılıktır, hükmün λ’sı değildir.

2024–25 çöküş tanımı, skor öncesi: λ’nın 2024-01..2025-12 penceresindeki nokta tahmini, R2013 noktasının yarısından küçüktür ve bu pencerenin Newey-West %95 üst ucu R2013 noktasının altındadır. 2026 bu tanımın penceresine girmez. Tanım tutmazsa kaldırılacak çöküş yoktur; o hüküm BELİRSİZ.

## Faiz kuralı

Aylık, rejim içi:

i_t = α + ρ × i_{t−1} + βπ × π_{t−1} + βe × (e_{t−1} − h_{t−1}) + ε_t

βe sıfırdan ayrı çıkmasa da terim denklemde kalır. Skor görünce terim düşürülmez. i, yukarıdaki faiz sırasının seçtiği seridir.

## Kur kuralı

Aylık, rejim içi:

g1_t = αg + βi × i_{t−1} + ε_t

## Rezerv vekili

Çeyrek, 2018-Q1 .. 2025-Q4. 2026 örneğe girmez. Eksik çeyrek doldurulmaz.

R, milyar dolar: TP.AB.TOPLAM / 1000. Bu brüttür, altın dahildir, swap düşülmemiştir.

S_t = max(0, −(R_t − R_{t−1})). Brüt rezerv düşüşüdür, yayımlanmış müdahale satışı değildir. Etiket [VEKİL].

g_t = α + θ × S_t + γ × i_{t−1} + ε_t

g, çeyrek satış ortalamasının 100 × ln farkıdır. i, çeyrek ortalamasıdır.

c = −1 / θ yalnız θ < 0 ve Newey-West %95 aralığı sıfırın dışındaysa. Değilse c yok, “sınırlı değil”. Aralık sıfırın dışında ve θ negatifse se(c) = se(θ) / θ², aralık c ± 1,96 se(c). Bu bir neden aralığı değildir.

## Standart hata ve aralık

Birincil standart hata Newey-West, Bartlett. Gecikme n < 24 ise 2, değilse 4. %95 uç = nokta ± 1,96 × se.

Bootstrap, çiftler, rejim satırı iadesiz değil iadeli. B = 1000. Tohum 20261021, `numpy` Generator. Yüzdelik 2,5 ve 97,5. Akış sırası kilitli: beklenti R2013, R1617, R1823, R2426, Y2018; sonra geçiş aynı beş pencere (Y2018 geçişe girer, senaryoya girmez); sonra faiz dört rejim; sonra kur dört rejim; sonra rezerv tek denklem. Duyarlılık regresyonu bu akışa girmez; onda yalnız Newey-West vardır.

“Aralık sıfırı dışlar” hükmü Newey-West’tedir. Bootstrap ayrı yazılır. İkisi ayrılırsa eşik kaymaz, ayrım zayıf nokta diye durur.

Bütün katsayılar [TAHMİN]. Senaryo çıktısı ölçüm değildir.

## Senaryo

Ufuk 2026-Q4 .. 2031-Q4, 21 çeyrek. Stok-akış başlangıcı `uc_kural_senaryo._init_state`. Üç kuralın tavan, servis eşiği (0,30 / 0,40), üretken pay eşiği (0,35, iki çeyrek, tüketici tavanı −2 puan) ve korunmasız stok geri alması aynı koddur.

Adım sırası, her çeyrek:

1. e24 = w × h + (1 − w) × π_yıllık,gecikme + φ × g12,gecikme. h = 5 (belge SAPMA’sı yoksa).
2. Faiz. Sabit varyant: i, son gözlemde donuk, rezerv satışı yok. Tepkili varyant: i = α + ρ × i_önceki + βπ × π_yıllık,gecikme + βe × (e24_önceki − h).
3. g_ham = 3 × (αg + βi × i_çeyreğe_giren). Kur, çeyreğe giren faize bakar; aynı çeyreğin yeni faizine bakmaz.
4. Tepkili varyant ve c varsa: S = min(R, c × max(g_ham, 0)), R := R − S, g = g_ham − S / c. c yoksa S = 0, g = g_ham, rezerv satırı BELİRSİZ.
5. π_çeyrek = 3 × α_geçiş + λ × g. Birim: yüzde, çeyreklik log farkla aynı ölçek.
6. Ücret, yalnız kilitli yol: net taban × (1 + e24 / 400). 2027’den itibaren Q1 ve Q3’te kama tablosunun yarısı eklenir (`KAMA_YARIMYIL`). Kapsama 2027-Q4’te 0,73’ün veya 2029-Q4’te 0,80’in altındaysa kama_ek +1, kilitli koddaki gibi. Yaşam maliyeti × (1 + π_çeyrek / 100). Mevcut yol tabanı dondurur, yaşam maliyeti aynı π ile yürür.
7. Kredi. Kilitli büyüme = yıllık enflasyon + kilitli puan. Yıllık enflasyon, bu çeyrek dahil son dört çeyreğin bileşkesidir. Mevcut yol, dosyadaki mevcut büyüme oranlarını kullanır. Geri alma aynı fonksiyondur.

Sayı patlaması: bir çeyrekte yıllık enflasyonun mutlak değeri 500 puanı aşarsa veya rezerv eksiye zorlanırsa (satış stoktan büyük ve c ile bölme tanımsız) o koşu `sayı_patladı`dır. Sarmal var sayılır, ücret kuralı kalır. Patlama susturulup yola yapıştırılmaz.

Başlangıç gecikmeleri, senaryodan önceki son gözlemdir: yıllık TÜFE, g12, e24, i, R, USD.

### Koşular

Katsayı paketi:

| Kod | Ne |
| --- | --- |
| (a) | R2426 noktaları. Güncel çıpasız paket |
| (b) | R2013 noktaları. 2013 paketi |
| (c1) | R1617 |
| (c2) | R1823 |
| (d) | k = 0 .. 20 için doğrusal: R2426 + (R2013 − R2426) × k / 20. w, φ, λ, geçiş sabiti, faiz katsayıları ve kur katsayıları birlikte kayar |

Her paket × {sabit faiz, tepkili faiz/rezerv} × {mevcut, kilitli}.

Izgara, yalnız w: 0, 0,25, 0,50, 0,75, 1. Diğer katsayılar R2426 noktasında kalır. Izgara, (a)–(d)’ye skor görününce yeni w eklemez. (b)’nin ham w’si ızgara eşiği değildir.

## Ölçüt

Kapsama_0, ilk adımdan önceki net taban / yaşam maliyetidir.

K1 geçer: 2031-Q4 kapsaması ≥ kapsama_0 − 0,02 ve kapsama, iki çeyrek üst üste kapsama_0 × 0,95’in altında kalmaz.

K2 geçer: kilitli yolda tüketici stoku (teminatsız + kart), aynı paket ve aynı faiz varyantının mevcut yoluna göre en az 4 çeyrekte çeyreklik büyümesi 0,5 puandan fazla düşüktür.

K3 tetik: tüketici tavan eki azalır veya korunmasız stok bir önceki çeyreğe geri alınır. Tetik sayısı ≥ 1 ise K3 geçti. Tetik 0 ve öncül de 0 ise K3 sınanmadı. Öncül var, tetik yoksa K3 kaldı.

Üçü birlikte geçer: K1 geçti ve K2 geçti ve K3 geçti. Biri sınanmadı, hiçbiri kalmadıysa birlikte BELİRSİZ. Biri kaldıysa birlikte kaldı.

H-C1. “Çıpa geri gelince üç kural çalışır.”

- Ayakta: ızgarada w ≥ 0,50 olan en az bir düzey, sabit ve tepkili varyantların ikisinde de üçü birlikte geçer. Eşik, bu düzeylerin en küçüğüdür.
- Yanlışlandı: K3 en az bir ızgara hücresinde puanlanır (geçti veya kaldı) ve w ≥ 0,50 olan hiçbir düzey iki varyantta birden üçü birlikte geçirmez.
- BELİRSİZ: K3 bütün ızgarada sınanmadı, ya da hüküm faiz/beklenti/TÜFE/kur serisi yok, ya da bir varyantın katsayısı BELİRSİZ olduğu için o varyant koşulamadı.

w ≥ 0,50 çubuğu “geri gelme”dir. Yalnız w = 0 veya 0,25 geçerse çıpa geri gelince çalışıyor denmez; geçen küme raporda durur, eşik “yok” yazılır, hüküm Yanlışlandı (K3 puanlandıysa) veya BELİRSİZ (K3 puanlanmadıysa).

H-Sarmal. Sarmal: dört çeyrek üst üste yıllıklandırılmış enflasyon katı artar ve 2031-Q4 yıllık enflasyonu, senaryo öncesi son gözlem yıllık enflasyonunun 5 puan üstündedir. Yıllıklandırılmış çeyrek = 100 × ((1 + π_çeyrek / 100)^4 − 1).

- Ayakta: (a) kilitli, iki faiz varyantında da sarmal var; (b) kilitli, iki varyantta da sarmal yok.
- Yanlışlandı: (a) kilitli en az bir varyantta sarmal var ve (b) kilitli de en az bir varyantta sarmal var.
- BELİRSİZ: (a) kilitli iki varyantta da sarmal yok, ya da (a) veya (b) koşulamadı.

H-Rezerv. Tükenme: R bir çeyrekte 0’a iner.

- Ayakta: c kuruldu, (a) tepkili kilitli tükenir, (b) tepkili kilitli tükenmez.
- Yanlışlandı: c kuruldu ve (b) tepkili kilitli de tükenir.
- BELİRSİZ: c yok, ya da (a) tepkili kilitli tükenmez.

H-Gecis. Çöküş tanımı yukarıdadır.

- Ayakta: tanım tutar ve şu kontrastta fark vardır. Kontrast, R2426 paketinde yalnız λ ve geçiş sabitini 2024-01..2025-12 tahminine karşı R2013 tahminine değiştirir; w ve diğer katsayılar R2426’dadır. Kilitli tepkili yolda 2024–25 λ’sı K1’i kalır veya sarmal üretir, R2013 λ’sı aynı yolu K1’de geçirir ve sarmal üretmez.
- Yanlışlandı: tanım tutar ve kontrast R2013 λ’sında da K1 kalır veya sarmal durur.
- BELİRSİZ: tanım tutmaz veya iki λ’dan biri yok.

Ücret ayağı, H-C1’in eşiği değildir. Raporda ayrı durur: K1’in iki varyantta birden geçtiği en küçük ızgara w’si. Adı “üç kural eşiği” değildir.

## Duyarlılık

Hükmü değiştirmez.

- Geçmiş enflasyon 6 ay (π_t = 100 × (P_t / P_{t−6} − 1) × 2, yıllıklandırılmış). w yeniden tahmin edilir.
- Kur şoku 3 ay: g3 = 100 × ln(USD_t / USD_{t−3}). φ yeniden tahmin edilir.
- Geçişte g1 yerine g1_{t−1}. λ yeniden tahmin edilir.
- Dört köşe: φ ve λ, Newey-West uçlarında, ızgara × iki faiz, yalnız kilitli. Ücret ayağının eşiği köşeler arasında kayarsa zayıf nokta diye yazılır.
- Faiz denklemi βe = 0 iken tepkili (a) ve (b). Birincil hüküm βe’li denklemdedir.

## Etiket

[VERİ] katalog satırı. [VEKİL] brüt rezerv düşüşü veya fonlama faizinin repo yerine durması. [HESAP] bu dosyadaki formül. [TAHMİN] rejim katsayısı ve senaryo yolu. [DOĞRULANMADI] inmeyen belge veya seri. Senaryo cümlesi “çıpa şunu yaptı” diye kurulmaz. Cümle: kilitli çubuk bu yolda tuttu veya tutmadı.

## SAPMA

Hesaptan önce kayıtlı sapma yok.
