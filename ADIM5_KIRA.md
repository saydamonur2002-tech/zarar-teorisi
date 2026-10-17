# Faz 6 — Adım 5: kira akışı bandı (satır `olculmedi` kalır)

Çalıştır: `python3 adim5_kira.py`. Çıktı: `adim5_kira_ham.csv`, `adim5_kira.csv`, `adim5_kira_aralik.csv`, `adim5_kira_sonuc.json`.

`adim5.csv` kira satırı `olculmedi`; bu dosya onu doldurmaz. Kol için hesaplanabilir band burada, her girdi etiketli.

## Ölçüm

- Birim kira TP.BK.TR 2026-Q3: **275.37 TL/m²/ay**; yıllık değişim 32.0%. Kapsam: değerlemesi yapılan konutlar.
- Yeni kiracı kira endeksi TP.YKKE.TR 2026-09: 342.91; yıllık 26.6%.

## Yol A: b × m² × N × κ × 12 (milyar TL/yıl)

| m² | κ | kiracı hane | aylık kira TL | yıllık milyar |
| --- | --- | --- | --- | --- |
| 90 | 0.25 | 6,600,000 | 24,783 | 1,962.8 |
| 90 | 0.3 | 7,920,000 | 24,783 | 2,355.4 |
| 110 | 0.25 | 6,600,000 | 30,291 | 2,399.0 |
| 110 | 0.3 | 7,920,000 | 30,291 | 2,878.8 |

- Band **[1,962.8, 2,878.8] milyar TL/yıl**. N = 26,400,000 hane (`dis_kaynak_elle`, doğrulanmadı); κ, m² varsayım.

## Yol B: depodaki proxy

- konut_stok 7,278.6 milyar (H varlık × 0,25, direnc_yuzdesi) × 0.035 = **254.8 milyar/yıl**. Yol A'nın çok altında: proxy finansal varlık payıdır, konut serveti değil. İki yol toplanmaz; A ölçüme yakın, B varsayım.

## HEKİS ile karşılaştırma

- HEKİS havuz kirası 20,000 TL/ay (`modellendi`) / piyasa 100 m² 27,537 TL/ay = **0.73**. Oran; eşitlenmez.

## Aralıklar (Adım 5)

| nesne | alt | üst | birim | etiket | not |
| --- | --- | --- | --- | --- | --- |
| birim kira (TL/m²/ay) | 275 | 275 | TL/m²/ay | `olcum` | TP.BK.TR 2026-Q3; tek nokta |
| konut alanı | 90.0 | 110 | m² | `varsayim` |  |
| aylık piyasa kirası (kiracı başına) | 24,783 | 30,291 | TL/ay | `band_varsayim` | b × m² |
| kiracı hane oranı | 0.25 | 0.3 | oran | `varsayim` | TÜİK GYKA civarı; depoda yok |
| kiracı hane sayısı | 6,600,000 | 7,920,000 | hane | `dis_kaynak_elle` | N 26,400,000 × κ |
| kira akışı yıllık (yol A) | 1,963 | 2,879 | milyar TL/yıl | `band_varsayim` | b × m² × N × κ × 12 |
| kira akışı yıllık (yol B proxy) | 255 | 255 | milyar TL/yıl | `varsayim_proxy` | A ile toplanmaz |
| HEKİS havuz kirası | 20,000 | 20,000 | TL/ay | `modellendi` | hekis-model; politika kirası |
| kiracı başına aylık fark (piyasa − HEKİS) | 4,783 | 10,291 | TL/ay | `band_varsayim` | HEKİS kirası piyasa altında kaldığı sürece |
| Ho→Ha yıllık transfer, kapsama payı 20% | 75.8 | 196 | milyar TL/yıl | `band_varsayim` | fark × kiracı hane × pay × 12; H içi dağılım, H toplam NL 0; Ho kaybı = Ha kazancı |
| Ho→Ha yıllık transfer, kapsama payı 50% | 189 | 489 | milyar TL/yıl | `band_varsayim` | fark × kiracı hane × pay × 12; H içi dağılım, H toplam NL 0; Ho kaybı = Ha kazancı |
| Ho→Ha yıllık transfer, kapsama payı 100% | 379 | 978 | milyar TL/yıl | `band_varsayim` | fark × kiracı hane × pay × 12; H içi dağılım, H toplam NL 0; Ho kaybı = Ha kazancı |

- Transfer satırları: HEKİS kirası piyasa kirasının altında kaldığı sürece kiracının (Ha) kazancı ev sahibinin (Ho) kaybıdır; H toplam NL değişmez. Kapsama payı tek sisteme giren kiracı payıdır; yüzde 20 satırı 'yüzde 20' koşusudur.
- Tüm alt/üst uçlar varsayım aralığının uçlarıdır; güven aralığı değil.

## SFC

- H içi transfer (kiracı → ev sahibi); H toplam NL 0; Ha/Ho dağılımı; F kurumsal ev sahibi payı ölçülmedi.

## Ne denmez

- 'Kira ölçüldü' denmez; satır `olculmedi`. Band: b ölçüm, geri kalanı varsayım/elle.
- 'HEKİS döngüyü kırdı' denmez; oran karşılaştırmadır.
