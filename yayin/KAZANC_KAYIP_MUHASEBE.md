# Kazanç–kayıp muhasebesi

**Etiket:** `kanal_kaldirildi_normalize`. Bir boşluğun dağıtımı V'yi (TR boşalması + pasif katkısı) aşmamalı. Eskiden kanal, matris, ikame, merkez aynı V'den beslenir ve dışlamazdı (A %184, B %218, C %170). `kanal` kaldırıldı; kalan üç kanal V'ye normalize edilir.

## Boşluk V ve kazanç kanalları (kanal kaldırıldı, normalize edildi)

| Senaryo | V (boşluk) | matris | ikame | merkez | Σ kazanç | Σ/V | ham Σ/V (normalizasyondan önce) | katsayı |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 25.397 | 12.156 | 0.0 | 7.825 | 19.981 | 0.787 | 0.924 | 0.8513 |
| B | 40.462 | 14.312 | 0.0 | 17.539 | 31.851 | 0.787 | 1.257 | 0.6265 |
| C | 17.398 | 9.746 | 0.0 | 3.918 | 13.664 | 0.785 | 0.785 | 1.0 |

## Merkez finans (MFIN) ayrı pay: kazanç, kayıp, maliyet

MFIN'in kazancı açık sızıntı kenarlarından ölçülür; kaybı modelde yoktur, referans oranla (İran, İsrail, Mısır) **vekil** atanır (`≈`); sürdürme maliyeti diğer dış aktörlerle aynı formüldür.

| Senaryo | V payı: MFIN | V payı: ülke aktörleri | dağıtılmayan | MFIN kazanç | kayıp vekili (± belirsizlik) | sürdürme maliyeti | MFIN net |
| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| A | 0.308 | 0.479 | 0.213 | 7.825 | ≈3.445 (±6.156) | 1.096 | ≈3.284 |
| B | 0.433 | 0.354 | 0.213 | 17.539 | ≈12.03 (±18.688) | 1.438 | ≈4.071 |
| C | 0.225 | 0.56 | 0.215 | 3.918 | ≈1.279 (±2.603) | 0.744 | ≈1.895 |

## Kayıp tarafı ve fark

| Senaryo | TR kayıp | TR dışı kayıp | Σ kayıp | Σ kazanç − Σ kayıp | Σ kazanç − V |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | 25.822 | 14.376 | 40.198 | -20.217 | -5.416 |
| B | 41.76 | 24.132 | 65.892 | -34.041 | -8.611 |
| C | 17.7 | 9.37 | 27.07 | -13.406 | -3.734 |

## Bulgu

- **A:** normalize edildi: ham toplam V'nin %92'i, katsayı 0.8513; Σ kazanç ≠ Σ kayıp (kayıp bölge net etkisi; özdeşlik Σ kazanç ≤ V).
- **B:** normalize edildi: ham toplam V'nin %126'i, katsayı 0.6265; Σ kazanç ≠ Σ kayıp (kayıp bölge net etkisi; özdeşlik Σ kazanç ≤ V).
- **C:** Σ kazanç ≠ Σ kayıp (kayıp bölge net etkisi; özdeşlik Σ kazanç ≤ V).

## Kapsam (neyin modellenmediği)

| Senaryo | Aktör | Kazanç tam / kısmi / yok | Kayıp modellendi / bilinmiyor | Net tam / kısmi |
| --- | ---: | --- | --- | --- |
| A | 37 | 14 / 21 / 1 | 28 / 9 | 6 / 31 |
| B | 37 | 14 / 21 / 1 | 28 / 9 | 6 / 31 |
| C | 37 | 14 / 21 / 1 | 28 / 9 | 6 / 31 |

Evren dışı (modelde hiç yok, kazanç/kayıp **bilinmiyor**; derleme, tam liste değil): Katar, Kuveyt, Umman, Ürdün, Hindistan, Japonya, Güney Kore, Birleşik Krallık, Almanya (AB yalnız Balkan vekil), İtalya.

## Not

Σ kazanç ≤ V artık sağlanır. Σ kazanç = Σ kayıp sağlanmaz ve hedeflenmedi: kayıp tarafı bölge net etkisidir, kazanç ise TR boşalmasının (V) dağıtımıdır.
