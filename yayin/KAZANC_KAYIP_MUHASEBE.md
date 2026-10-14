# Kazanç–kayıp muhasebesi

**Etiket:** `teshis_model_degismedi`. Bir boşluğun dağıtımı V'yi (TR boşalması + pasif katkısı) aşmamalı; kanal, matris, ikame, merkez aynı V'den beslenir ve dışlamaz.

## Boşluk V ve kazanç kanalları

| Senaryo | V (boşluk) | kanal | matris | ikame | merkez | Σ kazanç | Σ/V | (kanal+matris)/V |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 25.397 | 18.324 | 14.276 | 4.939 | 9.192 | 46.731 | 1.84 | 1.284 |
| B | 40.462 | 29.32 | 22.848 | 7.863 | 27.997 | 88.028 | 2.176 | 1.289 |
| C | 17.398 | 12.519 | 9.746 | 3.384 | 3.918 | 29.567 | 1.699 | 1.28 |

## Kayıp tarafı ve fark

| Senaryo | TR kayıp | TR dışı kayıp | Σ kayıp | Σ kazanç − Σ kayıp | Σ kazanç − V |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | 25.822 | 14.376 | 40.198 | 6.533 | 21.334 |
| B | 41.76 | 24.132 | 65.892 | 22.136 | 47.566 |
| C | 17.7 | 9.37 | 27.07 | 2.497 | 12.169 |

## Bulgu

- **A:** kanal + matris V'yi aşıyor: aynı boşluk iki kuralla dağıtılıyor; toplam kazanç V'yi aşıyor; toplam kazanç ≠ toplam kayıp (özdeşlik tanımsız).
- **B:** kanal + matris V'yi aşıyor: aynı boşluk iki kuralla dağıtılıyor; toplam kazanç V'yi aşıyor; toplam kazanç ≠ toplam kayıp (özdeşlik tanımsız).
- **C:** kanal + matris V'yi aşıyor: aynı boşluk iki kuralla dağıtılıyor; toplam kazanç V'yi aşıyor; toplam kazanç ≠ toplam kayıp (özdeşlik tanımsız).

## Kapsam (neyin modellenmediği)

| Senaryo | Aktör | Kazanç tam / kısmi / yok | Kayıp modellendi / bilinmiyor | Net tam / kısmi |
| --- | ---: | --- | --- | --- |
| A | 37 | 14 / 21 / 1 | 28 / 8 | 6 / 30 |
| B | 37 | 14 / 21 / 1 | 28 / 8 | 6 / 30 |
| C | 37 | 14 / 21 / 1 | 28 / 8 | 6 / 30 |

Evren dışı (modelde hiç yok, kazanç/kayıp **bilinmiyor**; derleme, tam liste değil): Katar, Kuveyt, Umman, Ürdün, Hindistan, Japonya, Güney Kore, Birleşik Krallık, Almanya (AB yalnız Balkan vekil), İtalya.

## Not

Bu rapor tutarsızlığın KAYNAĞINI ölçer; düzeltmez. Düzeltme için bir dağıtım kuralı seçilmeli (kanal veya matris) ya da payların toplamı 1'e normalize edilmeli.
