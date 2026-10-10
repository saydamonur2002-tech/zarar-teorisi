# Ödeme zinciri, tur 9: mahsup + FX şoku

Stoklar ölçülmüş (TCMB 2026-Q1). Kenar varsayım. Girdi-çıktı ve limit serisi yok.

## Hüküm

Kontrol şoksuz kalıcılık 0.00, reel 0.000. Mahsup sonrası kalıcılık farkı pratik eşik veya p eşiğini geçmedi; 'bloke kısalır' iddiası bu turda desteklenmedi. Mahsup reel kayıp veya küçük fazlada anlamlı iyileşme gösterdi; 'kapatmaz' iddiası zayıfladı.

## Varsayımlar

150 firma. TCMB 2026-Q1 toplamları sabit. Monte Carlo 50, tohum 20274010+s. FX çevrilemez (fx_sok, hat ×0,30). Valf eşiği 0.25, π aylık 0.0225 (Ocak 2026 TÜFE). Mahsup: optimal_mahsup (net pozisyon korunur). Şok mahsup sonrası aynı dinamik kural.

Kontrol şoksuz: kalıcılık 0.00, reel 0.000.

Mahsup kalıcılığı kısaltır (destek): False. Mahsup reel/zayıf halkayı kapatmaz (elenmedi): False.

## Hücre × kol (ortalama)

| Hücre | Kol | Brüt önce | Brüt sonra | Silinen % | Kalıcılık | Reel | Küçük yavaş | Fazla medyan | P(fazla≥0,05) | Temerrüt | Kilitli | Batık |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| esit | yok | 3.09 | 3.09 | 0.0 | 0.00 | 0.454 | 0.000 | 0.022 | 0.00 | 0.0 | 0.0 | 0.0 |
| esit | mahsup | 3.09 | 2.07 | 33.0 | 0.00 | 0.000 | 0.000 | nan | nan | 0.0 | 0.0 | 0.0 |
| ms70 | yok | 3.09 | 3.09 | 0.0 | 2.66 | 0.394 | 0.099 | 0.046 | 0.06 | 18.6 | 2.6 | 16.0 |
| ms70 | mahsup | 3.09 | 1.83 | 40.8 | 14.22 | 0.000 | 0.000 | nan | nan | 15.3 | 0.0 | 15.3 |
| msa70 | yok | 3.09 | 3.09 | 0.0 | 2.68 | 0.383 | 0.000 | 0.050 | 0.52 | 18.6 | 1.8 | 16.9 |
| msa70 | mahsup | 3.09 | 1.92 | 37.7 | 3.64 | 0.296 | 0.000 | 0.014 | 0.06 | 15.0 | 0.0 | 15.0 |

## Mahsup − mahsupsuz (Wilcoxon eşli)

- **esit**: Δkal medyan 0.00, p = 1; Δreel 0.454, p = 7.687e-13; Δfazla 0.000.
- **ms70**: Δkal medyan -13.00, p = 1; Δreel 0.395, p = 8.882e-16; Δfazla 0.000.
- **msa70**: Δkal medyan -1.00, p = 1; Δreel 0.091, p = 4.202e-08; Δfazla 0.034.

Tekrar: `python3 odeme_zinciri.py`.

Dosyalar: `odeme_kons9_hucre.csv`, `odeme_kons9.png`, `odeme_kons9_sonuc.json`.


<!-- ONCEKI -->

# Ödeme zinciri, tur 8: zayıf halka ve lider-ayna

Stoklar ölçülmüş (TCMB 2026-Q1). Kenar ve dağılım varsayım. Çekilmemiş limit ve girdi-çıktı yok.

## Hüküm

Kontrol: şoksuz reel 0.000, eşit FX çevrilemez reel 0.454 (sapma 0.000). Zayıf halka: üç hücrede de medyan fazla 0,05’in altında ve küçük–büyük yavaş farkı anlamlı değil. Sistematik aktarım iddiası elendi. Lider-ayna: yalnızca servis+alacak sıfırlanınca kalıcılık değişmiyor (p = 1); mevduat da dağıtılınca kalıcılık düşüyor (baz−tam medyan 0.50, p = 5.22e-06). Lider mevduatı sonucu taşır; servis/alacak lider payı tek başına değil.

## Varsayımlar

150 firma alt düğümü. TCMB 2026-Q1 toplamları sabit. Monte Carlo 50, tohum 20273010+s. Lider = en büyük mevduatlı firma. Lider sıfır: kütlesi kalan N−1 firmaya eşit dağıtılır.

Kontrol şoksuz: kalıcılık 0.00, reel 0.000. Eşit pay FX çevrilemez reel 0.454 (hedef 0,454, sapma 0.000).

Spearman (Tur 7 ızgarası, FX çevrilemez): servis–küçük yavaş 0.741, mevduat–reel 0.843.

Zayıf halka elendi mi: True. Lider elendi mi: False.

## Zayıf halka

| Hücre | FX | Kalıcılık | Reel | Fazla medyan | P(fazla≥0,05) | Yavaş fark medyan | Ödenmeyen küçük pay |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| esit | çevrilebilir | 0.00 | 0.000 | nan | nan | 0.000 | nan |
| esit | çevrilemez | 0.00 | 0.454 | 0.022 | 0.00 | 0.000 | nan |
| ms70 | çevrilebilir | 12.84 | 0.000 | nan | nan | 0.000 | 0.000 |
| ms70 | çevrilemez | 2.66 | 0.395 | 0.045 | 0.04 | 0.083 | 0.000 |
| msa70 | çevrilebilir | 12.86 | 0.000 | nan | nan | 0.000 | 0.000 |
| msa70 | çevrilemez | 2.62 | 0.398 | 0.048 | 0.42 | 0.000 | 0.000 |

## Lider-ayna (FX çevrilemez)

| Kol | Kalıcılık | Küçük yavaş medyan | Fazla medyan |
| --- | ---: | ---: | ---: |
| baz | 2.62 | 0.000 | 0.048 |
| rol_sifir | 2.62 | 0.000 | 0.048 |
| tam_sifir | 1.42 | 0.000 | 0.051 |

Baz − rol sıfır: kalıcılık fark medyan 0.00, p = 1. Yavaş fark 0.000, p = 1.

Baz − tam sıfır: kalıcılık fark medyan 0.50, p = 5.218e-06. Yavaş fark 0.000, p = 1.

Tekrar: `python3 odeme_zinciri.py`.

Dosyalar: `odeme_kons8_hucre.csv`, `odeme_kons8.png`, `odeme_kons8_sonuc.json`.


<!-- ONCEKI -->

# Ödeme zinciri, konsantrasyon (servis / alacak / çizgi)

Stoklar ölçülmüş (TCMB 2026-Q1). Kenar ve firma içi dağılım varsayım. Çekilmemiş limit serisi ve girdi-çıktı tablosu yok.

## Hüküm

Mevduat×servis (FX çevrilemez): mevduat hedefi–küçük yavaş Spearman 0.503 (p = 0.168), servis hedefi–küçük yavaş 0.741 (p = 0.0224), mevduat–reel kayıp 0.843 (p = 0.00429). Mevduat 0,70 servis eşit: sistemik kalıcılık 0.00, yerel 0.00, küçük yavaş 0.000 — önceki tur tekrarı. Mevduat ve servis birlikte 0,70: FX çevrilebilirken kalıcılık 10.44, FX çevrilemezken 1.92, reel kayıp 0.595. Servis de konsantre olunca agregatın gizlediği sistemik bloke çıkıyor; yalnızca mevduat konsantre servis eşitken çıkmıyor. Alacak üst %10 payı arttıkça küçük firmaların alacak payı düşüyor (Spearman -1.00). Reel kayıp fazlası medyan 0.033; 5 puan eşiği aşılmadı. Zayıf halka: küçük reel kayıp payı alacak konsantrasyonunda da 5 puanı aşmıyor. Çizgi (mev 0,70, servis eşit, FX çevrilebilir): herkes yavaş 0.000, üst %10 0.170 (yerel bloke 0.12), alt yarı 0.000. Sistemik kalıcılık 0.

## Varsayımlar

150 firma alt düğümü. TCMB 2026-Q1 toplamları sabit. Kenar paylaşım kuralı önceki turla aynı. Girdi-çıktı ve çekilmemiş limit yok. Monte Carlo 50, tohum 20272010+s. Sistemik bloke sayacı değişmedi (%25 sikintili pay). Yerel bloke: alt yarı firmada o periyotta yavaş oranı ortalaması ≥ 0,40.

Test 1 (3×3 mevduat×servis, FX çevrilemez): mevduat hedefi ile küçük yavaşlık Spearman 0.503 (p = 0.1677); servis hedefi ile küçük yavaşlık 0.741 (p = 0.02237); mevduat hedefi ile reel kayıp 0.843 (p = 0.00429).

Mevduat 0,70 servis eşit: kalıcılık 0.00, yerel 0.00, yavaş 0.000. Mev=srv=0,70: FX çevrilebilir kalıcılık 10.44, FX çevrilemez 1.92, reel 0.595.

Alacak konsantrasyonu (FX çevrilemez, servis eşit): alacak hedefi ile küçük alacak payı Spearman -1.000; reel kayıp fazlası medyan 0.033 (5 puan eşiği aşılmadı).

Alacak 0,70, servis konsantre: küçük alacak payı 0.458; servis eşitken 0.458.

Çizgi (mevduat 0,70, servis eşit, FX çevrilebilir): herkes / üst %10 / alt yarı — sistemik 0.00 / 0.00 / 0.00; yerel 0.00 / 0.12 / 0.00; küçük yavaş 0.000 / 0.170 / 0.000.

## Test 1 — mevduat × servis (ortalama)

| Mev %10 | Srv %10 | FX | Kalıcılık | Yerel | Küçük yavaş | Reel |
| ---: | ---: | --- | ---: | ---: | ---: | ---: |
| 0.10 | 0.10 | çevrilebilir | 0.00 | 0.00 | 0.000 | 0.000 |
| 0.10 | 0.10 | çevrilemez | 0.00 | 0.00 | 0.000 | 0.454 |
| 0.10 | 0.40 | çevrilebilir | 0.00 | 0.00 | 0.008 | 0.000 |
| 0.10 | 0.40 | çevrilemez | 0.00 | 0.00 | 0.001 | 0.458 |
| 0.10 | 0.70 | çevrilebilir | 0.00 | 0.00 | 0.018 | 0.000 |
| 0.10 | 0.70 | çevrilemez | 0.00 | 0.00 | 0.003 | 0.528 |
| 0.40 | 0.10 | çevrilebilir | 0.00 | 0.00 | 0.000 | 0.000 |
| 0.40 | 0.10 | çevrilemez | 0.00 | 0.00 | 0.000 | 0.490 |
| 0.40 | 0.40 | çevrilebilir | 0.00 | 0.00 | 0.029 | 0.000 |
| 0.40 | 0.40 | çevrilemez | 0.00 | 0.00 | 0.003 | 0.507 |
| 0.40 | 0.70 | çevrilebilir | 1.26 | 0.00 | 0.037 | 0.000 |
| 0.40 | 0.70 | çevrilemez | 0.36 | 0.00 | 0.005 | 0.552 |
| 0.70 | 0.10 | çevrilebilir | 0.00 | 0.12 | 0.170 | 0.000 |
| 0.70 | 0.10 | çevrilemez | 0.00 | 0.00 | 0.000 | 0.558 |
| 0.70 | 0.40 | çevrilebilir | 0.00 | 0.00 | 0.143 | 0.000 |
| 0.70 | 0.40 | çevrilemez | 0.00 | 0.00 | 0.014 | 0.571 |
| 0.70 | 0.70 | çevrilebilir | 10.44 | 0.00 | 0.096 | 0.000 |
| 0.70 | 0.70 | çevrilemez | 1.92 | 0.00 | 0.012 | 0.595 |

## Test 2 — alacak

| Alac %10 | Servis | FX | Kalıcılık | Yerel | Küçük yavaş | Reel | Küçük alacak payı |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 0.10 | konsantre | çevrilebilir | 0.00 | 0.12 | 0.170 | 0.000 | 0.500 |
| 0.10 | konsantre | çevrilemez | 0.00 | 0.00 | 0.000 | 0.558 | 0.500 |
| 0.10 | eşit | çevrilebilir | 0.00 | 0.12 | 0.170 | 0.000 | 0.500 |
| 0.10 | eşit | çevrilemez | 0.00 | 0.00 | 0.000 | 0.558 | 0.500 |
| 0.40 | konsantre | çevrilebilir | 0.00 | 0.00 | 0.156 | 0.000 | 0.481 |
| 0.40 | konsantre | çevrilemez | 0.00 | 0.00 | 0.077 | 0.511 | 0.481 |
| 0.40 | eşit | çevrilebilir | 0.00 | 2.46 | 0.224 | 0.000 | 0.481 |
| 0.40 | eşit | çevrilemez | 0.00 | 0.00 | 0.030 | 0.554 | 0.481 |
| 0.70 | konsantre | çevrilebilir | 13.76 | 0.00 | 0.105 | 0.000 | 0.458 |
| 0.70 | konsantre | çevrilemez | 2.66 | 0.00 | 0.076 | 0.379 | 0.458 |
| 0.70 | eşit | çevrilebilir | 0.96 | 12.42 | 0.290 | 0.000 | 0.458 |
| 0.70 | eşit | çevrilemez | 0.00 | 0.00 | 0.039 | 0.548 | 0.458 |

## Test 3 — çizgi kime açık (FX çevrilebilir)

| Çizgi | Kalıcılık | Yerel | Küçük yavaş | Reel |
| --- | ---: | ---: | ---: | ---: |
| herkes | 0.00 | 0.00 | 0.000 | 0.000 |
| ust10 | 0.00 | 0.12 | 0.170 | 0.000 |
| alt_yarim | 0.00 | 0.00 | 0.000 | 0.000 |

Tekrar: `python3 odeme_zinciri.py`.

Dosyalar: `odeme_kons7_hucre.csv`, `odeme_kons7.png`, `odeme_kons7_sonuc.json`.


<!-- ONCEKI -->

# Ödeme zinciri, dağılım stresi

Stoklar TCMB finansal hesapları, 2026-Q1. Kenar ve firma içi dağılım varsayımdır. Çekilmemiş limit ve girdi-çıktı tablosu yoktur. Sayılar firma faturası ölçümü değildir.

## Hüküm

Eşit paylaşım agregatı tekrarlıyor: kalıcılık 0, döviz çevrilemezken reel kayıp önceki bantta. Sistemik bloke periyot artmıyor ve FX çevrilebilirken reel kayıp artmıyor. Küçük firmaların yavaş ödeme payı 0.177 artıyor (p = 3.772e-10). Agregat sayaç bunu bloke periyot olarak görmüyor. Yerel yavaşlık gizli kalıyor. Aynı yerel fark, bir aylık çizgi herkese açıkken sıfır, çizgi en küçük yarıya kapalıyken geri geliyor. Ölçülmüş aylık enflasyon, yüksek konsantrasyonda reel FX kaybını ve kalıcılığı eşiğin üstünde kapatmıyor. Küçük firmaların reel kayıp payı defter payını 5 puan aşmıyor. Zayıf halka bu kanalda da zayıf.

## Ne ölçülmüş, ne varsayım

Stoklar TCMB 2026-Q1. Firma haznesi 150 alt düğüme bölündü. Toplam mevduat, kredi stoku ve aylık servis korunuyor. Kenar, yükümlülüğün alacaklı varlık payına bölünmesidir. Girdi-çıktı tablosu yok. Çekilmemiş limit seride yok.

Üst yüzde 10 mevduat payı 0,10, 0,40 ve 0,70. Birincil streste borç servisi ve alacak eşit. Kontrolde ikisi de mevduat payını izliyor. Yan kolda bir aylık servis kadar çizgi, en küçük p0 firmaya kapalı. Bu çizgi ölçülmedi.

TÜFE 2025-01–2026-01: yıllık 0.306, aylık π = 0.0225. Monte Carlo 50. Tohum 20261010+9000.

Eşit paylaşım, FX çevrilemez, valf kapalı: kalıcılık 0.00, reel kayıp 0.454. Agregat hedef 0,454. Sapma 0.000.

Yüksek konsantrasyon, eşit servis, çizgi yok, FX yok: kalıcılık farkı 0.00 (p = 1), reel fark 0.000 (p = 1), küçük firma yavaşlık farkı 0.177 (p = 3.772e-10).

Aynı hücre, FX çevrilemez: kalıcılık 0.00, reel kayıp 0.558. Valf açık: kalıcılık 0.00, reel 0.558, kısalma 0.00 (p = 1), reel düşüş 0.000.

Küçük firma reel payı 0.080, defter payı 0.047, fazla medyan 0.033.

Eşleşen kontrol, yüksek konsantrasyon, FX çevrilemez: kalıcılık 0.00, reel kayıp 0.454, fazla medyan 0.004.

Varsayılmış bir aylık çizgi, yüksek konsantrasyon, p0 = 0,50 eksi p0 = 0: kalıcılık farkı 0.00 (p = 1), yavaşlık farkı 0.177 (p = 3.772e-10).

## Hücreler, valf kapalı

| Üst %10 | Servis | Çizgi | p0 | FX | Kalıcılık | Reel | Küçük yavaşlık | Fazla |
| ---: | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| 0.10 | eşit | 0 | 0.00 | çevrilebilir | 0.00 | 0.000 | 0.000 | — |
| 0.10 | eşit | 0 | 0.00 | çevrilemez | 0.00 | 0.454 | 0.000 | 0.022 |
| 0.40 | eşit | 0 | 0.00 | çevrilebilir | 0.00 | 0.000 | 0.000 | — |
| 0.40 | eşit | 0 | 0.00 | çevrilemez | 0.00 | 0.490 | 0.000 | 0.035 |
| 0.70 | eşit | 0 | 0.00 | çevrilebilir | 0.00 | 0.000 | 0.177 | — |
| 0.70 | eşit | 0 | 0.00 | çevrilemez | 0.00 | 0.558 | 0.000 | 0.033 |
| 0.10 | eşleşen | 0 | 0.00 | çevrilebilir | 0.00 | 0.000 | 0.000 | — |
| 0.10 | eşleşen | 0 | 0.00 | çevrilemez | 0.00 | 0.454 | 0.000 | 0.022 |
| 0.40 | eşleşen | 0 | 0.00 | çevrilebilir | 0.00 | 0.000 | 0.000 | — |
| 0.40 | eşleşen | 0 | 0.00 | çevrilemez | 0.00 | 0.454 | 0.000 | 0.010 |
| 0.70 | eşleşen | 0 | 0.00 | çevrilebilir | 0.00 | 0.000 | 0.000 | — |
| 0.70 | eşleşen | 0 | 0.00 | çevrilemez | 0.00 | 0.454 | 0.000 | 0.004 |
| 0.70 | eşit | 1 | 0.00 | çevrilebilir | 0.00 | 0.000 | 0.000 | — |
| 0.70 | eşit | 1 | 0.00 | çevrilemez | 0.00 | 0.558 | 0.000 | 0.033 |
| 0.70 | eşit | 1 | 0.50 | çevrilebilir | 0.00 | 0.000 | 0.177 | — |
| 0.70 | eşit | 1 | 0.50 | çevrilemez | 0.00 | 0.558 | 0.000 | 0.033 |

Tekrar: `python3 odeme_zinciri.py`.

Dosyalar: `odeme_dagilim_hucre.csv`, `odeme_dagilim.png`, `odeme_dagilim_sonuc.json`.


<!-- ONCEKI -->

# Ödeme zinciri, ölçülmüş stoklar

Stoklar TCMB finansal hesapları, 2026-Q1, milyar TL biriminden trilyona çevrildi. Kenar ölçülmüş fatura değildir: yükümlülük, alacaklı varlık payına bölünür. Vade ve valf eşiği varsayımdır. Çekilmemiş limit yoktur.

## Hüküm

Şoksuz patika bloke üretmiyor. Firma mevduatının ölçülmüş en büyük çeyreklik düşüşü kalıcılığı 0 periyotta bırakıyor. Döviz kredisinin çevrilmediği patikada kalıcılık 0, reel kayıp 0.454. Valf açıkken 0 ve 0.454. π aylık 0.0225. Valf periyodu 0: zincir bloke olmayınca valf açılmıyor, erime 0. FX çevirmeme şokunda valf kalıcılığı 2 periyottan az değiştiriyor ve reel kaybı 5 puandan az düşürüyor. Ölçülmüş aylık enflasyon bu kısıtı kapatmıyor. Kenar, finansal hesap stokunun orantılı karşı taraf dağılımıdır; firma faturası değildir. Aynı ağda firma mevduatını × 0,30 kesmek, ölçülmüş düşüş değildir: kalıcılık 0.

## Ne ölçülmüş, ne varsayım

Dönem 2026-Q1. Birim trilyon TL. Firma mevduatı 8.59, firma kredi yükümlülüğü 25.34, diğer yükümlülük 6.41.

Kredi döviz payı (değerleme regresyonu, F yükümlülük) 0.596. Mevduat döviz payı 0.580. FX mevduat / FX kredi stoku = 0.330. Firma mevduatının en büyük çeyreklik düşüşü -0.079. Firma aylık servis 1.67; mevduat bunun 5.1 katı.

TÜFE 2025-01–2026-01: yıllık 0.306, aylık π = 0.0225. Kaynak EVDS TP.FG.J0.

Kısa kredi 12 ay, uzun kredi 60 ay, diğer hesap 12 ay servis edilir. Bu vade ölçülmedi. Çekilmemiş banka limiti seride yok, çizgi sıfır. Valf eşiği 0,25 model kuralıdır. Girdi-çıktı ithal katsayısı yok. Reel kısıt, firmanın döviz kredisini çevirememesidir.

Karşı taraf matrisi `Lm`: borçlunun yükümlülüğü, alacaklıların varlık payına bölünür. Bu, depodaki kendi uyarısıyla ölçülmüş bir fatura ağı değildir.

## Tek patika

Monte Carlo yok. Matris tek. Kısalma eşiği 2 bloke periyot, reel kayıp eşiği 0,05. p-değeri yok. `asiri` satırı ölçülmüş düşüş değildir: önceki turlardaki × 0,30 likidite kesimi, bu stoklara uygulanır.

| Patika | Valf | Bloke | Reel kayıp | Erime | Valf periyodu |
| --- | --- | ---: | ---: | ---: | ---: |
| soksuz | kapalı | 0 | 0.000 | 0.000 | 0 |
| soksuz | açık | 0 | 0.000 | 0.000 | 0 |
| mevduat | kapalı | 0 | 0.000 | 0.000 | 0 |
| mevduat | açık | 0 | 0.000 | 0.000 | 0 |
| fx | kapalı | 0 | 0.454 | 0.000 | 0 |
| fx | açık | 0 | 0.454 | 0.000 | 0 |
| iki | kapalı | 0 | 0.454 | 0.000 | 0 |
| iki | açık | 0 | 0.454 | 0.000 | 0 |
| asiri | kapalı | 0 | 0.000 | 0.000 | 0 |
| asiri | açık | 0 | 0.000 | 0.000 | 0 |

FX çevirmemede hane, alacaklı olarak reel kaybın 0.021 kadarını taşır. Hane defter payı 0.028.

Tekrar: `python3 odeme_zinciri.py`.

Dosyalar: `odeme_gercek.png`, `odeme_gercek_sonuc.json`.


<!-- ONCEKI -->

# Ödeme zinciri, tur 5: reel kısıt

Sentetik ağ ve sentetik ithal payları. TCMB finansal hesaplarına, KAP bildirimlerine veya bu depodaki stok-akış matrislerine kalibre edilmedi. Sayılar ölçüm değildir.

## Hüküm

Reel kısıt yokken kötü köşede kalıcılık uzun ve valf onu pratik eşiğin üstünde kısaltmıyor. TL+FX şokunda valf ne kalıcılığı ne reel kaybı pratik eşiğin üstünde kısaltıyor. Enflasyon siliminin reel tıkanma için gerekli olduğu desteklenmiyor. Reel katmanın kalıcılığı uzattığı iddia bu eşikte kapanmadı. Ne valf ne FX iadesi ne ithal ikamesi kalıcılığı pratik eşiğin üstünde düşürüyor. Küçük alacaklının reel kayıp payı defter payını 5 puan aşmıyor. Zayıf halka bu kanalda da zayıf. FX hattını iade etmek reel fatura kaybını en az 5 puan düşürür. İthal payını sıfırlamak reel fatura kaybını en az 5 puan düşürür. TL+FX şoku, TL-yalnız köşeye göre kalıcılığı kısaltıyor. Teslimat düşünce TL yükümlülüğü de küçülüyor. Reel fatura kaybı bu kısalmanın içinde değil, ayrı hesapta duruyor.

## Kural

İthal payları sentetiktir. Normal FX hattı firmanın kendi bir aylık ithal gereksinimidir. FX şokunda şoklanan firmaların hattı × 0,30. TL tahsilatı FX’e dönmez. Valf yalnız TL alacağını eritir; FX hizmetini ve ithal gereksinimini eritmez. Kur geçişkenliği birincilde 0. Üretim, FX kapsamı ile gelen yerli teslimatın minimumudur. Tahsil gerçekleşen faturaya göredir. Reel kayıp bloke sayacına yazılmaz.

Şoksuz, kısıt yok: kalıcılık 0.00. Şoksuz, kısıt var: kalıcılık 0.00, reel kayıp oranı 0.0000.

## C şoku, kötü köşe

TL yalnız, valf kapalı / açık: 17.46 / 17.46. Kısalma 0.00, p = 1.

TL+FX, valf kapalı / açık: 8.12 / 8.12. Kısalma 0.00, p = 1.

Reel kayıp oranı, TL yalnız 0.0000, TL+FX kapalı 0.3783, valf açık 0.3783. Fark (kapalı − açık) 0.0000.

FX açığı, TL+FX kapalı 0.164. Nominal erime oranı, valf açık 0.0761.

FX hattı iade: kalıcılık 18.34, reel kayıp 0.0000, kapalı FX’e göre kısalma -10.22, p = 1.

İthal ikamesi (pay 0): kalıcılık 17.46, reel kayıp 0.0000, kısalma -9.34, p = 1.

Kur geçişkenliği 1, valf açık: kalıcılık 8.12, reel kayıp 0.3783. Birincil hükme girmez.

Kapasite × 0,70, FX şoku yok, valf kapalı: kalıcılık 10.24, reel kayıp 0.1718. Birincil hükme girmez.

Küçük alacaklının reel kayıp payı 0.403, defter payı 0.401, fazla medyan 0.001.

İyi köşe, TL+FX, valf kapalı / açık: kalıcılık 0.00 / 0.00, reel kayıp 0.3783 / 0.3783, valf periyodu 0.00.

## Şoklar, kötü köşe

| Şok | TL kapalı | TL açık | FX kapalı | FX açık | FX reel | İade |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| yumusak | 8.76 | 8.76 | 6.74 | 6.74 | 0.334 | 9.62 |
| c | 17.46 | 17.46 | 8.12 | 8.12 | 0.378 | 18.34 |
| sert | 20.38 | 20.38 | 11.12 | 11.06 | 0.424 | 20.74 |

## FX hattı ayı, C, kötü köşe, TL+FX

| Ay | Valf | Kalıcılık | Reel kayıp | FX açığı |
| ---: | --- | ---: | ---: | ---: |
| 0.50 | kapalı | 0.00 | 0.689 | 0.582 |
| 0.50 | açık | 0.00 | 0.689 | 0.582 |
| 1.00 | kapalı | 8.12 | 0.378 | 0.164 |
| 1.00 | açık | 8.12 | 0.378 | 0.164 |
| 2.00 | kapalı | 11.66 | 0.216 | 0.094 |
| 2.00 | açık | 11.66 | 0.216 | 0.094 |

## Hangi hipotez hangi koşulda

Reel kısıt yokken kötü köşede kalıcılık uzun ve valf onu pratik eşiğin üstünde kısaltmıyor. TL+FX şokunda valf ne kalıcılığı ne reel kaybı pratik eşiğin üstünde kısaltıyor. Enflasyon siliminin reel tıkanma için gerekli olduğu desteklenmiyor. Reel katmanın kalıcılığı uzattığı iddia bu eşikte kapanmadı. Ne valf ne FX iadesi ne ithal ikamesi kalıcılığı pratik eşiğin üstünde düşürüyor. Küçük alacaklının reel kayıp payı defter payını 5 puan aşmıyor. Zayıf halka bu kanalda da zayıf. FX hattını iade etmek reel fatura kaybını en az 5 puan düşürür. İthal payını sıfırlamak reel fatura kaybını en az 5 puan düşürür. TL+FX şoku, TL-yalnız köşeye göre kalıcılığı kısaltıyor. Teslimat düşünce TL yükümlülüğü de küçülüyor. Reel fatura kaybı bu kısalmanın içinde değil, ayrı hesapta duruyor.

## Varsayımlar

Tohum 20261010. Limit çekimi 20268010. Monte Carlo 50. 204 firma, 17 sektör. Banka tavanı tur 3 dağılımı. Valf eşiği 0,25, π = 0,30.

İthal payı sektör sırasında: 0,12, 0,28, 0,22, 0,35, 0,55, 0,48, 0,50, 0,52, 0,45, 0,18, 0,15, 0,08, 0,30, 0,20, 0,05, 0,06, 0,08. FX hizmeti 0,05 × ithal payı × sözleşme satışı. Üç Leontief turu. Kapasite birincilde 1.

Tekrar: `python3 odeme_zinciri.py`.

Dosyalar: `odeme_reel_hucre.csv`, `odeme_reel.png`, `odeme_reel_sonuc.json`.


<!-- ONCEKI -->

# Ödeme zinciri, tur 4: enflasyon kanalı

Sentetik ağ. TCMB finansal hesaplarına, KAP bildirimlerine veya bu depodaki stok-akış matrislerine kalibre edilmedi. Sayılar ölçüm değildir.

## Hüküm

Sistem valfi kötü köşede reel yükü alacaklıya yazıyor; zincir içi küçük pay 5 puan büyümüyor. Kalıcılığı pratik eşiğin üstünde kısaltmıyor: bloke periyot sayısı yerinde kalıyor. Banka çarpanı 4 iken valf açılmıyor. Küçük alacaklı erimeyi defter payıyla taşıyor. Yerel erken silme, birincil kuralın dışında, kötü köşede kalıcılığı sıfırlıyor. Yüksek gecikmede kısalma yok. Banka kapalıyken α = 0 ve α = 0,15 olan iki hücrede kısalma eşiği geçiliyor. Kalibrasyon kapanmadı.

## Kural

Valf, bir önceki periyodun şiddeti ve ödenmeyen stok / aylık fatura ikisi de eşiği geçince açılır. Açılınca nakit yükümlülük 1/(1+π) olur. Erime = yükümlülük × π/(1+π); alacaklının reel kaybı, borçlunun rahatlaması. Erime ödenmeyen tutara yazılmaz. Tahsil, erimeden sonraki yükümlülüğe göredir. Birincil ayar: eşik 0,25, π = 0,30. Kilit orta, kötü köşe α = 0,60 ve banka 0, iyi köşe α = 0 ve banka 4.

İkinci aşama kapanmadı. `hekis_enflasyon.py` yıllık TÜFE’yi `hekis-model-main/data/istanbul_2026.json` içinden okur; dosya bu ortamda yok. Sektör makro çalışma kitabı da yok. Kanalın cebiri o dosyadaki formülle aynı: reel değişim = −alacak × π / (1+π). Izgaradaki π ölçülmüş enflasyon değildir.

Şoksuz, kanal kapalı: kalıcılık 0.00. Şoksuz, birincil valf: kalıcılık 0.00, erime oranı 0.0000. Şoksuz, yerel tercih: kalıcılık 0.00, erime oranı 0.0000.

## C şoku, birincil valf

Kötü köşe kapalı / açık: 17.46 / 17.46. Kısalma ortalama 0.00, medyan 0.00, tek yanlı p = 1.

Kötü köşe, birincil valf. Ortalama yeni tahsil kapalı 0.41, açık 0.57. Hacim eşiğinin altında kalan periyot 16.08 ve 16.06. Kilit payı eşiğinin üstünde kalan periyot 17.46 ve 17.46. Bloke sayımı bu ikisinin birleşimidir. Ortalama tahsil yükselir, 0,70 eşiğinin altında kalır. Hacim sayacı ve kilit sayacı kısalmaz.

Birincil kötü köşe α = 0,60 kısalmaz. Aynı eşik ve π ile banka 0'da iki hücre pratik eşiği geçer: kilit 0,99 / süre 8 ve α = 0, kısalma ortalama 3,58, medyan 3, p = 3,53e-8; kilit orta ve α = 0,15, kısalma ortalama 2,98, medyan 3, p = 3,72e-7.

İyi köşe kapalı / açık: 0.00 / 0.00. Baz kapalı / açık: 0.58 / 0.58.

Kötü köşede ortalama enflasyon periyodu 15.66, iyi köşede 0.00.

Erime / (V0 × T), kötü 0.3538, iyi 0.0000. Küçük alacaklının erime payı 0.401, defter payı 0.401, fazla medyan 0.001.

Küçük alacaklının ödenmeyen payı, açık − kapalı medyan 0.0042, n = 50, tek yanlı p = 2.417e-05.

Küçük borçluya düşen erime payı 0.386. Büyük alacaklının erime payı 0.369.

Yerel tercih, C, kötü köşe: kalıcılık 0.00, kapalıya göre kısalma 17.46, p = 4.759e-10, erime oranı 0.0383. İyi köşe kalıcılık 0.00, enflasyon periyodu 0.00. Birincil hükme girmez.

FX yan deneyi, kötü köşe, geçişkenlik 1: kalıcılık 17.46, kısalma 0.00, erime oranı 0.2549. Birincil hükme girmez.

## Şoklar, kötü köşe, birincil valf

| Şok | Şiddet | Kapalı | Açık | Kısalma | p | Valf periyodu | Erime oranı | Valf |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| yumusak | 0.90 | 8.76 | 8.76 | 0.00 | 1 | 7.30 | 0.1522 | hayır |
| c | 2.10 | 17.46 | 17.46 | 0.00 | 1 | 15.66 | 0.3538 | hayır |
| sert | 3.20 | 20.38 | 20.38 | 0.00 | 1 | 18.52 | 0.4110 | hayır |

## Eşik × şiddet, C şoku, kötü köşe

| Eşik | π | Kapalı | Açık | Kısalma | Erime | Valf periyodu | Valf |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0.50 | 0.10 | 17.46 | 17.46 | 0.00 | 0.2628 | 14.98 | hayır |
| 0.50 | 0.30 | 17.46 | 17.46 | 0.00 | 0.3668 | 14.98 | hayır |
| 0.50 | 0.60 | 17.46 | 17.46 | 0.00 | 0.3112 | 11.70 | hayır |
| 0.25 | 0.10 | 17.46 | 17.46 | 0.00 | 0.2617 | 15.66 | hayır |
| 0.25 | 0.30 | 17.46 | 17.46 | 0.00 | 0.3538 | 15.66 | hayır |
| 0.25 | 0.60 | 17.46 | 17.14 | 0.32 | 0.2805 | 11.52 | hayır |
| 0.10 | 0.10 | 17.46 | 17.46 | 0.00 | 0.2606 | 16.10 | hayır |
| 0.10 | 0.30 | 17.46 | 17.46 | 0.00 | 0.3412 | 16.10 | hayır |
| 0.10 | 0.60 | 17.46 | 15.68 | 1.78 | 0.2627 | 11.30 | hayır |

## Hangi hipotez hangi koşulda

Kötü köşede, C şokunda enflasyon kanalı kalıcılığı pratik eşiğin üstünde kısaltmıyor. Valf işlemiyor. Aynı hücrede reel erime belirgin ve zincir içi küçük alacaklı payı 5 puan büyümüyor. Yük borçludan alacaklıya enflasyonla geçmiş olabilir. Hiyerarşi duruyor. İyi köşede valf neredeyse açılmıyor ve kalıcılık kısa. Kötü köşede valf açılıyor. Yumuşak şokta enflasyon periyodu sert şoktan az. Küçük alacaklının erime payı defter payını 5 puan aşmıyor. Zayıf halka bu kanalda da zayıf.

## Varsayımlar

Tohum 20261010. Monte Carlo 50. Ufuk 24. Ağ tur 2 ile aynı sentetik çizim, basamak banka erişimi. Şok tamponu U(0,95, 1,40), ek şok firmaların %8’i × 0,45. Yumuşak: 2 sektör × 0,55. C: 3 sektör × 0,30. Sert: 4 sektör × 0,20.

Izgara: kilit, α ve banka indeks {0, 2, 4}; eşik {0,50, 0,25, 0,10}; π {0,10, 0,30, 0,60}.

Yerel tercih birincil teste girmez. FX yan deneyi de girmez: büyük borçluda pay 0,40, ortada 0,20, küçükte 0,05; geçişkenlik 1. Bu paylar ölçüm değildir.

Tekrar: `python3 odeme_zinciri.py`.

Dosyalar: `odeme_enf_hucre.csv`, `odeme_enf_sok.csv`, `odeme_enf.png`, `odeme_enf_sonuc.json`.


<!-- ONCEKI -->

# Ödeme zinciri, tur 3: heterojen limit

Sentetik ağ ve varsayılmış limit dağılımı. TCMB finansal hesaplarına, KAP bildirimlerine veya bu depodaki stok-akış matrislerine kalibre edilmedi. Sayılar ölçüm değildir. KAP tabanlı ağ bu turda yok.

## Hüküm

Heterojen limitte parametre kolu C şokunda açık kalıyor, tam banka baskınlığı kırılıyor. Çarpan 4, sıfır çizgisi olan firmalar dururken her hücreyi sıfıra yapıştırmıyor. Tur 2'deki tam baskınlık, herkese pozitif basamak limiti verilmesine bağlıydı. Seçim kuralı sistem kalıcılığını uzatmıyor. KAP ağı bu turda yok.

## Limit varsayımı

KAP ağı eklenmedi. Depoda firma düzeyinde KAP kenarı yok; finansal hesap matrisi kimden kime ödeme ağı değil.

Birim tavan A × (aylık borç + 0,25 × boyut). A, sınıf içinde: küçük P(0)=0,50 ve değilse LogNormal(ln 0,35; 0,60); orta P(0)=0,25 ve LogNormal(ln 0,80; 0,50); büyük P(0)=0,05 ve LogNormal(ln 1,50; 0,45). Tavan 6,0'da kırpılır. Hücre çarpanı bunu çarpar. Sıfır erişim her çarpanda sıfır kalır. Çekim tohumu 20261010+7000+koşu, hücreler arası eşli. Bu dağılım ölçüm değildir.

Gerçekleşen erişim. Küçük: sıfır payı 0.50, pozitiflerin medyan erişimi 0.36. Orta: sıfır payı 0.27, pozitiflerin medyan erişimi 0.81. Büyük: sıfır payı 0.04, pozitiflerin medyan erişimi 1.48.

Şoksuz, basamak, çarpan 1: ortalama kalıcılık 0.00. Şoksuz, dağılım, çarpan 1: 0.00. Şoksuz, dağılım, seçim açık: 0.00.

## C şoku

Basamak iyi / baz / kötü / seçim: 0.00 / 0.53 / 17.17 / 0.00.

Dağılım iyi / baz / kötü / seçim: 0.00 / 0.60 / 17.17 / 0.00.

Dağılım, kötü − iyi: ortalama 17.17, medyan 18.00, tek yanlı p = 9.953e-12.

Çarpan 4, 25 hücrenin en yüksek ortalaması 8.75. Çarpan 0, en yüksek hücre ortalaması 20.30. Çarpan 4'te ortalama aralık 8.75; çarpan 0'da 20.30.

Çarpan 4'te ortalaması 1 ve üstü olan hücreler: eşik 0.99 / süre 8, α 0.60, ortalama 8.75; eşik 0.95 / süre 5, α 0.60, ortalama 6.27; eşik 0.99 / süre 8, α 0.30, ortalama 5.67; eşik 0.99 / süre 8, α 0.15, ortalama 2.40; eşik 0.95 / süre 5, α 0.30, ortalama 2.28; eşik 0.85 / süre 3, α 0.60, ortalama 1.60. α = 0 iken çarpan 4, kilit ne olursa olsun ortalama 0.

Permütasyon: hücre ortalamalarının aralığı 20.30, p = 0.001.

Çarpan 0'da kötü köşe, basamak 17.17, dağılım 17.17. Çarpan sıfır her iki kuralda da tavanı siler.

Seçim açık ile baz arasında pratik uzama yok.

Seçim − baz, dağılım: ortalama fark -0.60, medyan 0.00, uzama p = 0.9997.

Küçük alacaklı payı, seçim − baz: medyan fark -0.0007, n = 60, tek yanlı p = 0.2286. Kötü − baz medyan farkı -0.023. Hücre medyanları 0.37–0.43.

Dağılım, kötü köşede sektör yavaşlığı 10.9–16.4. Seçimde 2.6–18.2. Bazda en yavaş üç: Perakende 5.3, Diğer hizmet 4.9, Toptan 2.6.

Firma sırası, dağılım, C şoku: kötü ile baz Spearman -0.107 (p = 0.129); seçim ile baz Spearman -0.354 (p = 2.05e-07).

## Şok taraması, dağılım

Dağılımda parametre kolu taranan pencerenin en yumuşak ucunda da açık: 1 sektör, kalan likidite 0.70, kötü−iyi ortalama 5.93. Anlamlı şok 20 / 20. Yirmi karşılaştırma ham p ile duruyor. Pencerenin içinde kapanış yok. Adlandırılan şoklar: yumusak: iyi 0.00, baz 0.00, kötü 8.48, seçim 0.00; c: iyi 0.00, baz 0.60, kötü 17.17, seçim 0.00; sert: iyi 0.00, baz 3.63, kötü 20.42, seçim 0.00.

| Sektör | Kalan | Şiddet | İyi | Baz | Kötü | Seçim | Kötü−iyi | p | Kol |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 0.70 | 0.30 | 0.00 | 0.00 | 5.93 | 0.00 | 5.93 | 1.1e-09 | evet |
| 1 | 0.55 | 0.45 | 0.00 | 0.00 | 6.93 | 0.00 | 6.93 | 3.59e-10 | evet |
| 1 | 0.40 | 0.60 | 0.00 | 0.00 | 8.38 | 0.00 | 8.38 | 3.61e-10 | evet |
| 2 | 0.70 | 0.60 | 0.00 | 0.00 | 5.17 | 0.00 | 5.17 | 1.15e-07 | evet |
| 1 | 0.30 | 0.70 | 0.00 | 0.00 | 10.02 | 0.00 | 10.02 | 1.65e-10 | evet |
| 1 | 0.20 | 0.80 | 0.00 | 0.02 | 11.17 | 0.00 | 11.17 | 1.11e-10 | evet |
| 2 | 0.55 | 0.90 | 0.00 | 0.00 | 8.48 | 0.00 | 8.48 | 1.64e-09 | evet |
| 3 | 0.70 | 0.90 | 0.00 | 0.00 | 7.88 | 0.00 | 7.88 | 1.53e-09 | evet |
| 2 | 0.40 | 1.20 | 0.00 | 0.00 | 12.13 | 0.00 | 12.13 | 1.63e-10 | evet |
| 4 | 0.70 | 1.20 | 0.00 | 0.00 | 8.78 | 0.00 | 8.78 | 3.5e-10 | evet |
| 3 | 0.55 | 1.35 | 0.00 | 0.00 | 11.58 | 0.00 | 11.58 | 7.44e-11 | evet |
| 2 | 0.30 | 1.40 | 0.00 | 0.00 | 13.98 | 0.00 | 13.98 | 1.07e-10 | evet |
| 2 | 0.20 | 1.60 | 0.00 | 0.13 | 15.87 | 0.00 | 15.87 | 2.14e-11 | evet |
| 3 | 0.40 | 1.80 | 0.00 | 0.12 | 15.52 | 0.00 | 15.52 | 1.53e-11 | evet |
| 4 | 0.55 | 1.80 | 0.00 | 0.00 | 14.20 | 0.00 | 14.20 | 1.02e-11 | evet |
| 3 | 0.30 | 2.10 | 0.00 | 0.60 | 17.17 | 0.00 | 17.17 | 9.95e-12 | evet |
| 4 | 0.40 | 2.40 | 0.00 | 0.23 | 17.88 | 0.00 | 17.88 | 5.92e-12 | evet |
| 3 | 0.20 | 2.40 | 0.00 | 1.60 | 18.93 | 0.00 | 18.93 | 5.89e-12 | evet |
| 4 | 0.30 | 2.80 | 0.00 | 1.48 | 19.62 | 0.00 | 19.62 | 4.83e-12 | evet |
| 4 | 0.20 | 3.20 | 0.00 | 3.63 | 20.42 | 0.00 | 20.42 | 4.22e-12 | evet |

## Hangi hipotez hangi koşulda

Parametre kolu heterojen limitte de açık: C şokunda kötü köşe iyiden pratik eşiğin üstünde uzun. Tam baskınlık kırıldı. Çarpan 4, herkese pozitif basamak verildiği tur 2'deki gibi bütün hücreleri sıfıra yapıştırmıyor. Sıfır çizgi kitlesi, yüksek çarpanın sistemi tek başına kapatmasını engelliyor. Seçim kuralı kendi tavanını 4 kata çıkarıyor ama sıfır çizgiyi doldurmuyor. Bu, bazdan daha uzun bir sistem tıkanması ve daha büyük bir küçük-alacaklı payını birlikte üretmedi. “Bedel zayıf halkaya akar” dağılımda da zayıf kaldı. Sıkı parametre ve seçim, küçük alacaklı payını 5 puan büyütmüyor.

## Varsayımlar

Tohum 20261010. Limit çekimi 20268010+koşu. Monte Carlo 60. Ufuk 24 periyot. 204 firma, 17 sektör. Ağ tur 2 ile aynı sentetik çizim.

Seçim, firmanın kendi birim tavanını 4 katına çıkarır. Sıfır çizgiyi doldurmaz. α = 0, kilit eşiği 0,50, süre 1.

Bloke periyot ve pratik uzama tur 2 ile aynı: yeni fatura tahsili < 0,70 veya sıkıntılı düğüm payı ≥ 0,25; uzama medyan ≥ 2, ya da ortalama ≥ 2 ve koşuların en az dörtte biri.

Tekrar: `python3 odeme_zinciri.py`. Tur 2 tabloları `odeme_hucre.csv` ve `odeme_sok_esik.csv` içinde durur.

Dosyalar: `odeme_limit_hucre.csv`, `odeme_limit_sok.csv`, `odeme_limit_kosu.csv`, `odeme_limit.png`, `odeme_limit_maliyet.png`, `odeme_limit_sonuc.json`.


<!-- TUR2 -->

# Ödeme zinciri, tur 2: şok eşiği ve yerel seçim

Sentetik ağ. TCMB finansal hesaplarına, KAP bildirimlerine veya bu depodaki stok-akış matrislerine kalibre edilmedi. Sayılar ölçüm değildir.

## Hüküm

C benzeri şokta parametre-bağımsız hipotez elendi; dağıtık faillik parametreye bağlı kaldı. Banka çarpanı 4 olan 25 hücrenin hepsinde ortalama kalıcılık 0.00; çarpan 0 iken en yüksek hücre ortalaması 20.30. Kilit ve gecikme banka kapalıyken ikincil. Yerel seçim kuralı sistem kalıcılığını uzatmıyor ve küçük alacaklı payını 5 puan büyütmüyor. “Bedel zayıf halkaya akar” zayıf kaldı. Bu tamponda parametre kolu en yumuşak taranan şokta da açık; pencere içinde kapanış yok, süre farkı şiddetle büyüyor.

## Şok eşiği

Bu tamponda parametre kolu taranan pencerenin en yumuşak ucunda da açık: 1 sektör, kalan likidite 0.70, şiddet 0.30, kötü−iyi ortalama 5.93. Anlamlı şok 20 / 20. Pencerenin içinde kapanış yok; süre farkı şiddetle birlikte büyüyor. Yirmi karşılaştırma ham p ile duruyor. Asıl parametre testi C şokunun tek kontrastı ve ızgara permütasyonu. Önceki koşuda kolu kapatan kalın tampon (Aday A) bu taramada yok. Adlandırılan şoklar: yumusak: iyi 0.00, baz 0.00, kötü 8.48, seçim 0.00, kol anlamlı; c: iyi 0.00, baz 0.53, kötü 17.17, seçim 0.00, kol anlamlı; sert: iyi 0.00, baz 4.23, kötü 20.42, seçim 0.00, kol anlamlı.

Kötü ve iyi köşe seçim kapalı: kötü α = 0,60 ve banka 0; iyi α = 0 ve banka 4; ikisinde de kilit orta (0,85 / 3 periyot). Seçim açık sütunu aynı şokta yerel kural.

| Sektör | Kalan likidite | Şiddet | İyi | Baz | Kötü | Seçim açık | Kötü−iyi ortalama | p | Kol anlamlı |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 0.70 | 0.30 | 0.00 | 0.00 | 5.93 | 0.00 | 5.93 | 1.1e-09 | evet |
| 1 | 0.55 | 0.45 | 0.00 | 0.00 | 6.93 | 0.00 | 6.93 | 3.59e-10 | evet |
| 1 | 0.40 | 0.60 | 0.00 | 0.00 | 8.38 | 0.00 | 8.38 | 3.61e-10 | evet |
| 2 | 0.70 | 0.60 | 0.00 | 0.00 | 5.17 | 0.00 | 5.17 | 1.15e-07 | evet |
| 1 | 0.30 | 0.70 | 0.00 | 0.00 | 10.02 | 0.00 | 10.02 | 1.65e-10 | evet |
| 1 | 0.20 | 0.80 | 0.00 | 0.03 | 11.17 | 0.00 | 11.17 | 1.11e-10 | evet |
| 2 | 0.55 | 0.90 | 0.00 | 0.00 | 8.48 | 0.00 | 8.48 | 1.64e-09 | evet |
| 3 | 0.70 | 0.90 | 0.00 | 0.00 | 7.88 | 0.00 | 7.88 | 1.53e-09 | evet |
| 2 | 0.40 | 1.20 | 0.00 | 0.00 | 12.13 | 0.00 | 12.13 | 1.63e-10 | evet |
| 4 | 0.70 | 1.20 | 0.00 | 0.00 | 8.78 | 0.00 | 8.78 | 3.5e-10 | evet |
| 3 | 0.55 | 1.35 | 0.00 | 0.00 | 11.58 | 0.00 | 11.58 | 7.44e-11 | evet |
| 2 | 0.30 | 1.40 | 0.00 | 0.00 | 13.98 | 0.00 | 13.98 | 1.07e-10 | evet |
| 2 | 0.20 | 1.60 | 0.00 | 0.48 | 15.87 | 0.00 | 15.87 | 2.14e-11 | evet |
| 3 | 0.40 | 1.80 | 0.00 | 0.03 | 15.52 | 0.00 | 15.52 | 1.53e-11 | evet |
| 4 | 0.55 | 1.80 | 0.00 | 0.00 | 14.20 | 0.00 | 14.20 | 1.02e-11 | evet |
| 3 | 0.30 | 2.10 | 0.00 | 0.53 | 17.17 | 0.00 | 17.17 | 9.95e-12 | evet |
| 4 | 0.40 | 2.40 | 0.00 | 0.18 | 17.88 | 0.00 | 17.88 | 5.92e-12 | evet |
| 3 | 0.20 | 2.40 | 0.00 | 2.13 | 18.93 | 0.00 | 18.93 | 5.89e-12 | evet |
| 4 | 0.30 | 2.80 | 0.00 | 1.03 | 19.62 | 0.00 | 19.62 | 4.83e-12 | evet |
| 4 | 0.20 | 3.20 | 0.00 | 4.23 | 20.42 | 0.00 | 20.42 | 4.22e-12 | evet |

## C şoku, parametre ızgarası (seçim kapalı)

İyi köşe: ortalama 0.00, medyan 0.0, P(≥4) = 0.00.

Baz: ortalama 0.53, medyan 0.0, P(≥4) = 0.05.

Kötü köşe: ortalama 17.17, medyan 18.0, P(≥4) = 0.97.

Seçim açık: ortalama 0.00, medyan 0.0, P(≥4) = 0.00.

Kötü − iyi: ortalama 17.17, medyan 18.00, tek yanlı p = 9.953e-12, KS = 0.983 (p = 9.047e-54).

Banka çarpanı 4 olan 25 hücrenin en yüksek ortalaması 0.00. Banka 0'ın en yüksek ortalaması 20.30. Banka 0'da kilit ve gecikme uçları arasındaki ortalama aralık 20.30; banka 4'te 0.00.

Global permütasyon: hücre ortalamalarının aralığı 20.30, p = 0.001.

## Yerel seçim

Seçim açık ile baz arasında pratik uzama yok ve küçük pay sistematik artmıyor. “Toplam tıkanma uzar” iddiası desteklenmedi.

Seçim açık − baz (aynı C şoku): ortalama fark -0.53, medyan 0.00, uzama yönü p = 0.999, kısalma yönü p = 0.001016.

Küçük alacaklı payı, seçim − baz: medyan fark -0.0016654797013226919, n = 60, tek yanlı p = 0.5352. Izgarada tanımlı payların aralığı 0.33–0.47.

Yavaşlık (küçük − büyük), C şoku: baz 1.23, kötü -1.02, seçim 1.16.

Ortalama yavaş periyot, küçük / büyük: baz 1.52 / 0.29, seçim 7.40 / 6.24, kötü 13.67 / 14.69. Yavaşlık, sistem bloke eşiğinden ayrıdır: firma ödeme oranı 0,70 altında kalabilir, toplam tahsil yine de eşiğin üstünde durabilir.

Kötü köşede sektör yavaşlığı 10.9–16.4 periyot. Seçim açıkken 2.6–15.4. Bazda en yavaş üç sektör: Perakende 5.8, Diğer hizmet 5.5, Toptan 1.5.

Firma sırası, C şoku: kötü ile baz Spearman -0.051 (p = 0.471); kötü ile seçim Spearman -0.213 (p = 0.00226); seçim ile baz Spearman -0.125 (p = 0.0747).

## Hangi hipotez hangi koşulda

Parametre-bağımsız hipotez, C benzeri şokta (3 sektör, likidite × 0,30) elendi. Aynı ağ ve aynı şok çarpanlarında kilit, gecikme ve banka kalıcılık dağılımını değiştiriyor. Banka limiti baskın parametre olarak kaldı. Çarpan 4 olan 25 hücrenin hepsinde ortalama kalıcılık 0.00. Çarpan 0 iken en yüksek hücre ortalaması 20.30. Kilit ve gecikme, banka kapalıyken ikincil kol; banka açıkken kalıcılığı oynatmıyor. “Bedel zayıf halkaya akar” zayıf kaldı. Küçük alacaklının payı hücre medyanlarında 0.33–0.47. Kötü köşe eksi baz medyan farkı -0.035. Seçim kuralı bu payı 5 puan büyütmüyor. Sıkı parametre payı küçük alacaklı lehine sistematik artırmıyor. Yerel seçim iddiası desteklenmedi. Kural, kısa vadeli nakdi ve limiti koruyacak şekilde gevşek kilit, sıfır gecikme cezası ve geniş ama idareli çekiş. Bu, C şokunda baz parametreden daha uzun bir tıkanma ve daha büyük bir küçük-alacaklı payı birlikte üretmedi.

## Varsayımlar

Tohum 20261010. Monte Carlo 60. Ufuk 24 periyot, dönem içi 4 tur. 204 firma, 17 sektör, kenar sayısı 1205, yoğunluk 0.0291, yönsüz kümelenme 0.095.

Tampon bütün taramada U(0,95, 1,40). Ek şok: diğer firmaların %8'i × 0,45. Dış akım her periyot sonunda sözleşmedeki (borç − alacak); kaçan tahsilatı koymaz. Büyük düğüm üst çeyrek, erişim 1; küçük alt yarı, erişim 0,20.

Seçim kapalı: hücredeki kilit, α ve banka çarpanı; firma borcu kapatmak için limiti kullanır.

Seçim açık: tavan çarpan 4 (erişim payı durur); çekiş yalnız nakit borcun %50'sinin altındaysa o çubuğa kadar; α = 0; kendi kilidi eşik 0,50 ve süre 1. Nakit borcu karşılıyorsa tam ödeme.

Bloke periyot: yeni fatura tahsili < 0,70 veya sıkıntılı düğüm payı ≥ 0,25. Olay: kalıcılık ≥ 4. Pratik uzama: medyan ≥ 2 periyot, ya da ortalama ≥ 2 ve koşuların en az dörtte biri.

Şoksuz, seçim kapalı: kalıcılık 0. Şoksuz, seçim açık: kalıcılık 0.

Konveks yan deney (hükme girmez), C şoku, banka 0, α = 0,30: doğrusal ortalama 15.40, γ = 1,8 ortalama 16.57.

Tekrar: `python3 odeme_zinciri.py`.

Dosyalar: `odeme_hucre.csv`, `odeme_sok_esik.csv`, `odeme_kosu.csv`, `odeme_sektor.csv`, `odeme_firma_sira.csv`, `odeme_kalicilik.png`, `odeme_maliyet.png`, `odeme_sonuc.json`.
