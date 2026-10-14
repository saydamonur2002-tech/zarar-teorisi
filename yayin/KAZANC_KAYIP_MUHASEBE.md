# Kazanç–kayıp muhasebesi

**Etiket:** `kanal_kaldirildi_normalize`. Bir boşluğun dağıtımı V'yi (TR boşalması + pasif katkısı) aşmamalı. Eskiden kanal, matris, ikame, merkez aynı V'den beslenir ve dışlamazdı (A %184, B %218, C %170). `kanal` kaldırıldı; kalan üç kanal V'ye normalize edilir.

## Boşluk V ve kazanç kanalları (kanal kaldırıldı, normalize edildi)

| Senaryo | V (boşluk) | matris | ikame | merkez | Σ kazanç | Σ/V | ham Σ/V (normalizasyondan önce) | katsayı |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 25.397 | 12.764 | 4.414 | 8.218 | 25.396 | 1.0 | 1.119 | 0.8941 |
| B | 40.462 | 15.747 | 5.419 | 19.296 | 40.462 | 1.0 | 1.451 | 0.6892 |
| C | 17.398 | 9.746 | 3.384 | 3.918 | 17.048 | 0.98 | 0.98 | 1.0 |

## Kayıp tarafı ve fark

| Senaryo | TR kayıp | TR dışı kayıp | Σ kayıp | Σ kazanç − Σ kayıp | Σ kazanç − V |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | 25.822 | 14.376 | 40.198 | -14.802 | -0.001 |
| B | 41.76 | 24.132 | 65.892 | -25.43 | 0.0 |
| C | 17.7 | 9.37 | 27.07 | -10.022 | -0.35 |

## Bulgu

- **A:** normalize edildi: ham toplam V'nin %112'i, katsayı 0.8941; Σ kazanç ≠ Σ kayıp (kayıp bölge net etkisi; özdeşlik Σ kazanç ≤ V).
- **B:** normalize edildi: ham toplam V'nin %145'i, katsayı 0.6892; Σ kazanç ≠ Σ kayıp (kayıp bölge net etkisi; özdeşlik Σ kazanç ≤ V).
- **C:** Σ kazanç ≠ Σ kayıp (kayıp bölge net etkisi; özdeşlik Σ kazanç ≤ V).

## Kapsam (neyin modellenmediği)

| Senaryo | Aktör | Kazanç tam / kısmi / yok | Kayıp modellendi / bilinmiyor | Net tam / kısmi |
| --- | ---: | --- | --- | --- |
| A | 37 | 14 / 21 / 1 | 28 / 8 | 6 / 30 |
| B | 37 | 14 / 21 / 1 | 28 / 8 | 6 / 30 |
| C | 37 | 14 / 21 / 1 | 28 / 8 | 6 / 30 |

Evren dışı (modelde hiç yok, kazanç/kayıp **bilinmiyor**; derleme, tam liste değil): Katar, Kuveyt, Umman, Ürdün, Hindistan, Japonya, Güney Kore, Birleşik Krallık, Almanya (AB yalnız Balkan vekil), İtalya.

## Not

Σ kazanç ≤ V artık sağlanır. Σ kazanç = Σ kayıp sağlanmaz ve hedeflenmedi: kayıp tarafı bölge net etkisidir, kazanç ise TR boşalmasının (V) dağıtımıdır.
