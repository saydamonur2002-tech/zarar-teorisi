# Göreceli konum, direnç alternatifi ve kırılma oranı

Yerel iç elit katmanı modelde yok; ülke düzeyi. Elit sorusu ölçülmez, ancak mutlak/göreceli ayrımı ülke düzeyinde verilir.

## 1. Göreceli konum: herkes batarken en geç batan

### Senaryo A
- Net kaybeden aktör: 28 · kaybeden medyan net -0.444
- Σ kaybeden net -28.40 · Σ diğer kazanan net +3.72 · MFIN net +4.66 (kaybedenlerin |toplamının| 0.164 katı)
- Mutlak olarak bant dışı kaybeden: RS, TN, TJ, KG, AM, TM, AZ, GE, DZ, UZ, KZ, UA, LY, MA, SO, SY, LB, FR, GCC, AE, IQ, EU
- Göreceli kazanan (kayıp medyanından ayırt edilebilir iyi): CY, EG, BG, RS

| En geç batan | Net | Medyana göre | Ortak bant | Ayırt edilebilir | Mutlak sınıf |
| --- | ---: | ---: | ---: | --- | --- |
| CY | -0.099 | +0.345 | 0.284 | evet | bant_ici |
| EG | -0.103 | +0.341 | 0.299 | evet | bant_ici |
| BG | -0.121 | +0.323 | 0.284 | evet | bant_ici |
| RS | -0.148 | +0.296 | 0.212 | evet | kaybeden |
| TN | -0.238 | +0.206 | 0.284 | hayır | kaybeden |
- En çok batan: EU -10.29, IQ -2.04, CN -2.02

### Senaryo B
- Net kaybeden aktör: 28 · kaybeden medyan net -0.750
- Σ kaybeden net -51.43 · Σ diğer kazanan net +4.32 · MFIN net +9.07 (kaybedenlerin |toplamının| 0.176 katı)
- Mutlak olarak bant dışı kaybeden: CY, BG, RS, TN, TJ, KG, AM, TM, AZ, GE, DZ, UZ, KZ, UA, MA, LY, SO, SY, LB, GCC, IQ, EU
- Göreceli kazanan (kayıp medyanından ayırt edilebilir iyi): CY, EG, BG, RS, TN

| En geç batan | Net | Medyana göre | Ortak bant | Ayırt edilebilir | Mutlak sınıf |
| --- | ---: | ---: | ---: | --- | --- |
| CY | -0.258 | +0.492 | 0.322 | evet | kaybeden |
| EG | -0.279 | +0.471 | 0.370 | evet | bant_ici |
| BG | -0.323 | +0.427 | 0.322 | evet | kaybeden |
| RS | -0.358 | +0.392 | 0.242 | evet | kaybeden |
| TN | -0.404 | +0.346 | 0.322 | evet | kaybeden |
- En çok batan: EU -17.83, CN -4.56, AE -3.73

### Senaryo C
- Net kaybeden aktör: 28 · kaybeden medyan net -0.290
- Σ kaybeden net -17.66 · Σ diğer kazanan net +2.78 · MFIN net +2.30 (kaybedenlerin |toplamının| 0.13 katı)
- Mutlak olarak bant dışı kaybeden: RS, TN, TJ, KG, AM, TM, AZ, GE, DZ, UZ, KZ, UA, LY, MA, SO, LB, SY, FR, GCC, AE, IQ, EU
- Göreceli kazanan (kayıp medyanından ayırt edilebilir iyi): CY, EG, BG, RS

| En geç batan | Net | Medyana göre | Ortak bant | Ayırt edilebilir | Mutlak sınıf |
| --- | ---: | ---: | ---: | --- | --- |
| CY | -0.046 | +0.244 | 0.202 | evet | bant_ici |
| EG | -0.050 | +0.240 | 0.206 | evet | bant_ici |
| BG | -0.051 | +0.239 | 0.202 | evet | bant_ici |
| RS | -0.065 | +0.225 | 0.153 | evet | kaybeden |
| TN | -0.155 | +0.135 | 0.202 | hayır | kaybeden |
- En çok batan: EU -6.56, IQ -1.36, AE -1.17

## 2. Seçenek 1: alternatif direnç (rant kaybı − net kazanç)

Ana tanım 6 aktör (bileşen 0.25), alternatif 4 aktör (bileşen 0.5). Skor 47.7 → 50.7 (yalnız tanı).

| Aktör | Rant kaybı mn $ | Net kazanç mn $ | Ana | Alternatif |
| --- | ---: | ---: | --- | --- |
| EU | 3,114 | -35,319 | evet | evet |
| US | 2,778 | 3,278 | evet | — |
| CN | 2,629 | -5,620 | evet | evet |
| RU | 2,324 | -3,946 | evet | evet |
| IR | 1,400 | 5,125 | evet | — |
| AE | 1,105 | -6,293 | evet | evet |
| IL | 979 | 1,949 | — | — |
| SA | 657 | 1,884 | — | — |
| EG | 506 | -269 | — | — |
| FR | 389 | -3,084 | — | — |
| GR | 379 | -1,098 | — | — |
| AZ | 217 | -1,233 | — | — |
| RS | 43 | -350 | — | — |

## 3. Seçenek 2: gerçek kayıp için kırılma oranı

Kayıp/kazanç oranı r. r_net_sıfır: net 0'a ininceye kadar katlanılabilir oran; r_bant: kazanan sınıfını koruyan üst oran. Referans oranlar Mısır/İran/İsrail kayıplarından.

| Senaryo | Aktör | Kazanç | Maliyet | r_net_sıfır | r_bant | Uygulanan oran |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| A | CN | 3.44 | 0.48 | 0.86 | -0.16 | 1.45 |
| A | RU | 3.35 | 0.47 | 0.86 | -0.08 | 1.28 |
| A | US | 2.65 | 0.37 | 0.86 | 0.49 | 0.56 |
| A | EU | 1.07 | 0.15 | 0.86 | -5.89 | 10.48 |
| B | CN | 4.37 | 0.36 | 0.92 | -0.77 | 1.96 |
| B | RU | 4.29 | 0.35 | 0.92 | -0.56 | 1.70 |
| B | US | 3.62 | 0.30 | 0.92 | 0.33 | 0.70 |
| B | EU | 1.37 | 0.11 | 0.92 | -10.75 | 13.95 |
| C | CN | 2.63 | 0.50 | 0.81 | 0.07 | 1.21 |
| C | RU | 2.53 | 0.48 | 0.81 | 0.10 | 1.10 |
| C | US | 1.92 | 0.37 | 0.81 | 0.53 | 0.49 |
| C | EU | 0.81 | 0.15 | 0.81 | -3.60 | 8.87 |

## 4. Kayıplar doğruysa: sistem kilidi mi, aktör becerisizliği mi?

| Senaryo | Σ net (tüm aktörler) | Σ pozitif | Σ negatif |
| --- | ---: | ---: | ---: |
| A | -44.94 | +8.38 | -53.32 |
| B | -77.94 | +13.39 | -91.32 |
| C | -29.77 | +5.08 | -34.85 |

Büyük aktörlerin net'i (maliyetli, kayıp vekilli):

| Aktör | A | B | C | En iyi |
| --- | ---: | ---: | ---: | --- |
| TR | -24.92 | -39.90 | -17.19 | C |
| MFIN | +4.66 | +9.07 | +2.30 | B |
| CN | -2.02 | -4.56 | -1.04 | C |
| RU | -1.42 | -3.36 | -0.73 | C |
| US | +0.80 | +0.79 | +0.61 | A |
| EU | -10.29 | -17.83 | -6.56 | C |
| AE | -1.96 | -3.73 | -1.17 | C |
| SA | +0.47 | +0.54 | +0.35 | B |
| FR | -0.91 | -1.66 | -0.57 | C |
| GR | -0.34 | -0.66 | -0.20 | C |
| IR | +1.35 | +1.83 | +0.95 | B |
| IL | +0.52 | +0.70 | +0.36 | B |
| EG | -0.10 | -0.28 | -0.05 | C |

Tüm büyük aktörlerin birlikte en iyi olduğu senaryo: yok.
%2 olasılıklı, tanımsız bir olayın TR net'i üzerindeki etkisi en fazla ≈ +0.45 (olay en kötü senaryoya çevirse bile).

Net toplamı kapalı sistemde sıfır olmaz: kazançlar V'den, kayıplar vekil ve maliyet ayrı kaynaktan; toplam, ölü ağırlık/dışlanan kaybın işareti.
