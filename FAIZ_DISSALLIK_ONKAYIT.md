# Ön kayıt — faiz dışsallığı

Yazıldı: 2026-10-16, tepki fonksiyonu katsayıları görülmeden. Yön, eşik, bant genişliği ve dönem sınırları sonra değiştirilmez.

Bu sohbette aynı kamuya açık serilerin bir kısmı daha önce çekildi. Bu dosya, bu turdaki katsayılardan önce yazıldı.

## Denklem

Aylık:

faiz_t = a + b1·(enflasyon sapması)_t + b2·(üretim açığı)_t + b3·(kur değişimi)_t + b4·(kredi büyümesi)_t + b5·faiz_(t-1) + hata

OLS. Newey–West, Bartlett çekirdeği. Bant genişliği floor(4·(n/100)^(2/9)), en az 1. Karar: iki yönlü %5, |t| > 1,96.

Dışsallık: b1, b3 veya b4’ten biri bu eşiği geçerse o tahmin içseldir. Üçü de geçmezse dışsaldır. n < 36 ise tahmin yok, katsayı yazılmaz, etiket belirlenemiyor.

Kırılma denklemi aynı artı dört kukla. Kukla, düzey kaymasıdır; eğim etkileşimi yoktur. Bir kuklanın |t| değeri 1,96’yı aşarsa kırılma vardır. Kırılma varken seri etiketi tam örneklemden verilmez.

## Seriler

Çekilme, betiğin çalıştığı gün. Uç uca ekleme yok. Eksik ay doldurulmaz.

| Rol | Kod | Not |
| --- | --- | --- |
| Fonlama maliyeti | `TP.APIFON4` | Aylık ortalama. Katalogda 2011-01…2026-10 |
| Gecelik | `TP.PY.P06.ON` | Aylık ortalama. Piyasa gecelik ağırlıklı basit faiz. Katalogda 2006-01…2026-10 |
| Politika faizi | yok | Bir haftalık repo ihale faizi bu katalog taramasında yok. Elle kodlanmaz |
| TÜFE | `TP.TUKFIY2025.GENEL` | 12 aylık yüzde değişim. Arşivle birleştirilmez |
| Çekirdek B | `TP.FE.OKTG03` | Arşiv. Denklemde yok. Katalogda 2006-01…2025-12 |
| Çekirdek C | `TP.FE.OKTG04` | Arşiv. Denklemde yok. Katalogda 2006-01…2025-12 |
| Üretim | `TP.TSANAYMT2021.BCD` | Mevsim ve takvim etkisinden arındırılmış sanayi üretimi. Katalogda 2010-01…2026-08 |
| Kur | `TP.DK.USD.A.YTL` | Aylık son |
| Kredi | `TP.KREDI.L001` | Toplam kredi hacmi, arşiv. Katalogda 2006-01…2025-01. Sektörel BDDK tablosu değildir |
| Beklenti | `TP.PKAUO.S01.E.U` | 12 ay sonrası yıllık TÜFE beklentisi. Reel faiz için |

Enflasyon sapması: 12 aylık TÜFE eksi o yılın resmi yıl sonu nokta hedefi. Hedef, 2026-10-16’da indirilen TCMB “Inflation Targets” sayfasıdır. Tabloda 2012’den 2028’e kadar hedef 5’tir. Örnek bu yıllardaysa sapma = enflasyon − 5. Belirsizlik bandı (±2) sapmanın tanımı değildir.

Üretim açığı: log sanayi üretiminin Hodrick–Prescott çevrimi, λ = 14400, tam örnek, iki yönlü. Yüzde puan için 100 ile çarpılır. Filtre, örneğin geleceğini kullanır.

Kur değişimi: 100·Δlog(USD), aylık.

Kredi büyümesi: toplam kredi stokunun 12 aylık yüzde değişimi, nominal.

## Kırılma takvimi

Kuklalar:

- 2018-08 … 2018-12
- 2020-03 … 2020-06
- 2021-09 … 2022-12
- 2023-06 … örnek sonu

Dönemler, bu pencerelerin başlangıcında kesilir:

1. Örnek başı … 2018-07
2. 2018-08 … 2020-02
3. 2020-03 … 2021-08
4. 2021-09 … 2023-05
5. 2023-06 … örnek sonu

Gözlem ayı pencerededir. faiz_(t−1) bir önceki pencerede olabilir. n < 36 olan dönemde katsayı yok.

Seri etiketi:

- Kırılma yok ve tam örneklem n ≥ 36: tam örneklemin etiketi.
- Kırılma var: tahmin edilen bir dönem içselse seri içseldir. Tahmin edilen dönemlerin hepsi dışsal fakat bir dönem n < 36 ise seri belirlenemiyor. Tahmin edilen dönem yoksa belirlenemiyor.

## Reel faiz

reel_t = faiz_t − `TP.PKAUO.S01.E.U`. Boş ay doğrusal olarak, son gözlemle veya ortalama ile doldurulmaz. O ay reel seriden düşer. Kaç ayın boş kaldığı yazılır. Reel faiz tepki fonksiyonuna konmaz. Ayrı bir dışsallık etiketi almaz.

## Tanım değişikliği

Politika faizi serisi olmadığı için onun tanım takvimi yazılmaz. AOFM’nin kanal bileşeninin (haftalık repo, gecelik, geç likidite) değiştiği günler bu turda tek tek doğrulanmadı. Gecelik serisi, TCMB borç alma kotasyonu `TP.PY.P01.ON` ve borç verme kotasyonu `TP.PY.P02.ON` değildir. Bu iki kotasyon regresyona girmez. Kırılma tarihleri yukarıdaki dört penceredir. Onlara ek tarih uydurulmaz.

## Uygulanmayacak öneri

PPK metinlerinden elle kodlanmış anlatısal şok bu turda kurulmaz. Kurulursa ayrı bir ön kayıt ister.
