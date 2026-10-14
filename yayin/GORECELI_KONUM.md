# Göreceli konum, direnç alternatifi ve kırılma oranı

Yerel iç elit katmanı modelde yok; ülke düzeyi. Elit sorusu ölçülmez, ancak mutlak/göreceli ayrımı ülke düzeyinde verilir.

## 1. Göreceli konum: herkes batarken en geç batan

### Senaryo A
- Net kaybeden aktör: 28 · kaybeden medyan net -0.444
- Σ kaybeden net -22.76 · Σ diğer kazanan net +3.49 · MFIN net +4.66 (kaybedenlerin |toplamının| 0.205 katı)
- Mutlak olarak bant dışı kaybeden: RS, TN, TJ, KG, AM, TM, AZ, GE, DZ, UZ, KZ, UA, LY, MA, SO, SY, LB, FR, GCC, IQ, AE, EU
- Göreceli kazanan (kayıp medyanından ayırt edilebilir iyi): CY, EG, BG, RS

| En geç batan | Net | Medyana göre | Ortak bant | Ayırt edilebilir | Mutlak sınıf |
| --- | ---: | ---: | ---: | --- | --- |
| CY | -0.099 | +0.345 | 0.284 | evet | bant_ici |
| EG | -0.103 | +0.341 | 0.299 | evet | bant_ici |
| BG | -0.121 | +0.323 | 0.284 | evet | bant_ici |
| RS | -0.148 | +0.296 | 0.212 | evet | kaybeden |
| TN | -0.238 | +0.206 | 0.284 | hayır | kaybeden |
- En çok batan: EU -3.08, CN -2.56, AE -2.31

### Senaryo B
- Net kaybeden aktör: 28 · kaybeden medyan net -0.802
- Σ kaybeden net -44.17 · Σ diğer kazanan net +3.65 · MFIN net +9.07 (kaybedenlerin |toplamının| 0.205 katı)
- Mutlak olarak bant dışı kaybeden: CY, BG, RS, TN, TJ, KG, AM, TM, AZ, GE, DZ, UZ, KZ, UA, MA, LY, SO, SY, LB, GCC, IQ
- Göreceli kazanan (kayıp medyanından ayırt edilebilir iyi): CY, EG, BG, RS, TN, TJ, KG, AZ

| En geç batan | Net | Medyana göre | Ortak bant | Ayırt edilebilir | Mutlak sınıf |
| --- | ---: | ---: | ---: | --- | --- |
| CY | -0.258 | +0.544 | 0.322 | evet | kaybeden |
| EG | -0.279 | +0.523 | 0.370 | evet | bant_ici |
| BG | -0.323 | +0.479 | 0.322 | evet | kaybeden |
| RS | -0.358 | +0.444 | 0.242 | evet | kaybeden |
| TN | -0.404 | +0.398 | 0.322 | evet | kaybeden |
- En çok batan: CN -6.14, EU -6.02, AE -4.72

### Senaryo C
- Net kaybeden aktör: 28 · kaybeden medyan net -0.290
- Σ kaybeden net -13.69 · Σ diğer kazanan net +2.67 · MFIN net +2.30 (kaybedenlerin |toplamının| 0.168 katı)
- Mutlak olarak bant dışı kaybeden: RS, TN, TJ, KG, AM, TM, AZ, GE, DZ, UZ, KZ, UA, LY, MA, SO, LB, SY, FR, GCC, AE, IQ, EU
- Göreceli kazanan (kayıp medyanından ayırt edilebilir iyi): CY, EG, BG, RS

| En geç batan | Net | Medyana göre | Ortak bant | Ayırt edilebilir | Mutlak sınıf |
| --- | ---: | ---: | ---: | --- | --- |
| CY | -0.046 | +0.244 | 0.202 | evet | bant_ici |
| EG | -0.050 | +0.240 | 0.206 | evet | bant_ici |
| BG | -0.051 | +0.239 | 0.202 | evet | bant_ici |
| RS | -0.065 | +0.225 | 0.153 | evet | kaybeden |
| TN | -0.155 | +0.135 | 0.202 | hayır | kaybeden |
- En çok batan: EU -1.85, IQ -1.36, AE -1.33

## 2. Seçenek 1: alternatif direnç (rant kaybı − net kazanç)

Ana tanım 6 aktör (bileşen 0.25), alternatif 4 aktör (bileşen 0.5). Skor 47.7 → 50.7 (yalnız tanı).

| Aktör | Rant kaybı mn $ | Net kazanç mn $ | Ana | Alternatif |
| --- | ---: | ---: | --- | --- |
| EU | 3,114 | -9,943 | evet | evet |
| US | 2,778 | 2,762 | evet | — |
| CN | 2,629 | -6,998 | evet | evet |
| RU | 2,324 | -5,103 | evet | evet |
| IR | 1,400 | 5,125 | evet | — |
| AE | 1,105 | -7,165 | evet | evet |
| IL | 979 | 1,949 | — | — |
| SA | 657 | 1,803 | — | — |
| EG | 506 | -269 | — | — |
| FR | 389 | -3,499 | — | — |
| GR | 379 | -1,265 | — | — |
| AZ | 217 | -1,233 | — | — |
| RS | 43 | -350 | — | — |

## 3. Seçenek 2: gerçek kayıp için kırılma oranı

Kayıp/kazanç oranı r. r_net_sıfır: net 0'a ininceye kadar katlanılabilir oran; r_bant: kazanan sınıfını koruyan üst oran. Referans oranlar Mısır/İran/İsrail kayıplarından.

| Senaryo | Aktör | Kazanç | Maliyet | r_net_sıfır | r_bant | Uygulanan oran |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| A | CN | 3.44 | 0.48 | 0.86 | -0.26 | 1.60 |
| A | RU | 3.35 | 0.47 | 0.86 | -0.15 | 1.42 |
| A | US | 2.65 | 0.37 | 0.86 | 0.44 | 0.63 |
| A | EU | 1.07 | 0.15 | 0.86 | -1.56 | 3.74 |
| B | CN | 4.37 | 0.36 | 0.92 | -1.06 | 2.32 |
| B | RU | 4.29 | 0.35 | 0.92 | -0.80 | 2.00 |
| B | US | 3.62 | 0.30 | 0.92 | 0.20 | 0.86 |
| B | EU | 1.37 | 0.11 | 0.92 | -3.54 | 5.32 |
| C | CN | 2.63 | 0.50 | 0.81 | 0.03 | 1.30 |
| C | RU | 2.53 | 0.48 | 0.81 | 0.06 | 1.19 |
| C | US | 1.92 | 0.37 | 0.81 | 0.51 | 0.54 |
| C | EU | 0.81 | 0.15 | 0.81 | -0.73 | 3.08 |

## 4. Kayıplar doğruysa: sistem kilidi mi, aktör becerisizliği mi?

| Senaryo | Σ net (tüm aktörler) | Σ pozitif | Σ negatif |
| --- | ---: | ---: | ---: |
| A | -39.53 | +8.15 | -47.68 |
| B | -71.34 | +12.72 | -84.06 |
| C | -25.91 | +4.96 | -30.88 |

Büyük aktörlerin net'i (maliyetli, kayıp vekilli):

| Aktör | A | B | C | En iyi |
| --- | ---: | ---: | ---: | --- |
| TR | -24.92 | -39.90 | -17.19 | C |
| MFIN | +4.66 | +9.07 | +2.30 | B |
| CN | -2.56 | -6.14 | -1.30 | C |
| RU | -1.87 | -4.63 | -0.95 | C |
| US | +0.60 | +0.21 | +0.51 | A |
| EU | -3.08 | -6.02 | -1.85 | C |
| AE | -2.31 | -4.72 | -1.33 | C |
| SA | +0.44 | +0.45 | +0.34 | B |
| FR | -1.08 | -2.13 | -0.65 | C |
| GR | -0.41 | -0.88 | -0.23 | C |
| IR | +1.35 | +1.83 | +0.95 | B |
| IL | +0.52 | +0.70 | +0.36 | B |
| EG | -0.10 | -0.28 | -0.05 | C |

Tüm büyük aktörlerin birlikte en iyi olduğu senaryo: yok.
%2 olasılıklı, tanımsız bir olayın TR net'i üzerindeki etkisi en fazla ≈ +0.45 (olay en kötü senaryoya çevirse bile).

Net toplamı kapalı sistemde sıfır olmaz: kazançlar V'den, kayıplar vekil ve maliyet ayrı kaynaktan; toplam, ölü ağırlık/dışlanan kaybın işareti.
