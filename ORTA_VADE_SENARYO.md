# Orta vade senaryosu, 2027–2029

Beş adım kendi yılında açılır. Hazine faiz faturası o yıllarda ayrı yürür. İki sütun toplanmaz.

Fatura: r 2025 kuponu (kalibrasyon). Eğim 2024-Q4 → 2026-Q2 (ölçüm). Beş adımın faiz ve kur etkisi `modellenmedi`.

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
- Kur durur ya da politika faizi iner denmez. İkisi `modellenmedi`.
- Stok yüzde 20 silindi denmez.
