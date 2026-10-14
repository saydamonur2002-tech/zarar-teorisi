# Orta vade senaryosu, 2027–2029

Beş adım kendi yılında açılır. Hazine faiz faturası o yıllarda ayrı yürür. İki sütun toplanmaz.

Fatura: r 2025 kuponu (kalibrasyon). Eğim 2024-Q4 → 2026-Q2 (ölçüm). Faiz → kur bağı kalibre edildi. Beş adımın faiz düğmesi ayrıca kalibre edildi: ana pencerede β sıfırdan ayrı değil.

## Hazine faturası, milyar TL

| Yıl | Mevcut tempo | Özel USD akışı 0 | Haziran 2026 stoku donuk | İç stok yıl sonu | Özel USD yıl sonu | Kur model yıl sonu |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026 | 2744 | 2744 | 2598 | 10365 | 340 | 49.7 |
| 2027 | 3513 | 3513 | 2625 | 13068 | 383 | 59.7 |
| 2028 | 4328 | 4328 | 2625 | 15770 | 426 | 71.7 |
| 2029 | 5172 | 5172 | 2625 | 18473 | 470 | 86.1 |

2026 modeli 2744. Ödenek 2.742. Özel USD akışını sıfırlamak 2027 farkını **+0.0**, 2028 farkını **+0.0**, 2029 farkını **+0.0** bırakır.

2029 mevcut tempo **5172**. Bunun içi 3954, dışı 664, diğer 554. İç stok yıl sonu 18473 milyar TL.

2026’nın donuk sütunu 2.598’dir: ilk yarı ölçülmüş stok, ikinci yarı Haziran stoku. 2027’den itibaren yılın tamamı Haziran 2026 stokundadır: 2.625.

Kur sütunu ölçülmüş çeyrek ortalamasının bileşik eğimidir. 2026-Q4 ve sonrası gerçekleşmiş kur değildir. 2027-Q4 model düzeyi 59,7; aynı yılın anketi 58,60. 2028 ve 2029 anketi yoktur. 71,7 ve 86,1 eğimin uzamasıdır.

Ağustos 2026 iç stok ölçümü 9.545. Eğimin Haziran’dan düz çizgisi Ağustos’ta 9.464 eder. Düzey çizgiye yakındır. İki aylık tempo çeyreğe çekilirse +797 milyar TL olur; senaryo eğimi +676’da kalır.

## Faiz → kur, aynı fatura

Denklem: g = 13.41 − 0.187 · AOFM gecikmesi. Pencere 2021-Q1 → 2024-Q4. Sınav 2026-Q2 kuru 47.06 verir; ölçülen 45.37; sapma +3.7%.

İç stok ve kamu USD eğimde kalır. Değişen, dış faizin kurudur. İç kupon durur.

| Yıl | Eğim kuru, fatura | Faiz 37’de kalır | Anket faizi | Kur, faiz 37 | Kur, anket |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2026 | 2744 | 2747 | 2747 | 50.8 | 50.8 |
| 2027 | 3513 | 3542 | 3551 | 65.8 | 68.2 |
| 2028 | 4328 | 4409 | 4466 | 85.2 | 96.5 |
| 2029 | 5172 | 5338 | 5517 | 110.5 | 139.4 |

2029’da faiz 37’de kalırsa fatura **5338** (dış 829). Anket faiziyle **5517** (dış 1008). Eğim kurundaki fatura 5172.

Anket faizi 2026 yıl sonu 35,07, 2027 yıl sonu 27,16, 2028 yıl sonu 22,43. 2029 anketi yoktur; faiz 22,43’te durur. Katsayı negatif olduğu için faiz inince çeyrek değer kaybı büyür. 2027-Q4 anket kuru 58,60’tır. Aynı çeyrekte bu denklem, anket faiziyle 68.2 üretir.

## Beş adımın faiz düğmesi

Ana tepki 2018-Q1 → 2024-Q4: β 0.032, se 0.054. Sıfırdan ayrı değil. 2029 faturası bu yolda **5339**. Faiz 37 sütunu 5338. Fark **+1.3**.

2023-Q3 → 2024-Q4 rejimi, n=6. Durağan hal 0.63. K1 ve K3, 2029’da enflasyonu yıl ortalamasında -4.5 puan kaydırır; AOFM **-2.83** puan. Kur yıl sonu 114.8. Fatura **5364** (dış 856).

| Yıl | Fatura, ana β | Fatura, 2023 rejimi | Kur, 2023 rejimi |
| --- | ---: | ---: | ---: |
| 2027 | 3542 | 3543 | 66.1 |
| 2028 | 4410 | 4418 | 86.9 |
| 2029 | 5339 | 5364 | 114.8 |

Rejim sınavında 2025-Q2 tahmini ölçülenin 5,6 puan altındadır. Bu sütun o rejimin durağan halidir.

## Beş adım, aynı yıllar

| Yıl | Açık adım | Adımın kendi sayısı | Birim | Etiket |
| --- | --- | ---: | --- | --- |
| 2026 | hiçbiri | 0 | — | ölçüm |
| 2027 | 1 akış ve 2, K1 | 2058 | milyar TL/yıl, yıl sonu itiş temposu | senaryo takvimi |
| 2028 | 1 stok tavanı, K2; adım 3 | 755 | milyar TL/yıl, duran firma faizi, κ=0,25 | varsayım |
| 2029 | 4, K3 | 36–91 | milyar TL, prim, θ=0,25 | band varsayım |
| 2027–2029 | 5 | — | kira satırı | ölçülmedi |

2027 yıl sonu K1 itiş temposu 2058. Yıl içinde biriken F.4 farkı 1286. Bu, stoktan silinen tutar değildir. `silinen` boş kalır. Akış satırı 0,427 `baska_nesne` olarak durur.

2028 yıl sonu K2 brüt üst sınır 14623. Adım 3’ün duran faizi 755. Bunu banka yazar. Hazine faiz satırından düşülmez. ΣNL = 0. K1 aynı yılda açık kalır; itiş temposu 2.058,5.

2029 prim bandı 36–91. Aynı yıl adım 3 tam yıldır: duran faiz 1208. Prim ile duran faiz toplanmaz. İhraççı varsayımı K′. Senet satırı `modellenmedi` kalır. Adım 5’in orta vadede penceresi yoktur. Ho→Ha bandı (yüzde 20 kapsama, 52–160) bu tabloya yazılmaz.

## Ne denmez

- Beş adım Hazine faturasını 2029’da sabitledi denmez. Mevcut tempo faturası yürür.
- Özel dış borç akışı durunca fatura değişir denmez. Üç yılda da fark 0,0.
- Adım 3’ün 1.208’i 2029 Hazine faizinden düşülür denmez. Ödeyen bankadır.
- Prim, duran faiz ve Hazine kuponu toplanır denmez.
- Beş adım faizi ölçülmüş biçimde indirdi denmez. Ana β sıfırdan ayrı değildir. 2023 rejimi n=6’dır.
- Anket faizi inince kur yavaşlar denmez. Kalibre edilen katsayı negatiftir: faiz inince değer kaybı artar.
- Stok yüzde 20 silindi denmez.
