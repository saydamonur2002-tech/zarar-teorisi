# Havzalar net kaybediyorsa kim kazanıyor? ve kısa vadeli parasal akış

GSYH 2024'te sabit (büyüme yok); rezerv brüt (altın dahil), net rezerv değil; yeni borç/swap ve akışın çok yıllı ivmesi modellenmedi.

## 1. Kayıp havuzu ve kim topluyor

| Senaryo | Net kaybeden havza | Σ havza net | TR kaybı | Diğer kayıp | Havuz | Kazanç (V ile sınırlı) | Ölü ağırlık | Oran |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 30/30 | -15.25 | 25.82 | 14.38 | 40.20 | 19.98 | 20.22 | %50 |
| B | 30/30 | -25.73 | 41.76 | 24.13 | 65.89 | 31.85 | 34.04 | %52 |
| C | 30/30 | -9.90 | 17.70 | 9.37 | 27.07 | 13.66 | 13.41 | %50 |

| Senaryo | Merkez (MFİN, ABD, AB, Fransa) brüt / net | Dış rakip güçler (Çin, Rusya) brüt / net | Bölge brüt / net | Bant dışı kazananlar |
| --- | --- | --- | --- | --- |
| A | 11.09 (%50) / -7.92 | 4.51 (%20) / -5.40 | 6.36 (%29) / -12.46 | IR, IL, MK, AL, BA |
| B | 21.86 (%61) / -15.83 | 5.72 (%16) / -10.63 | 8.35 (%23) / -22.93 | IR, IL, MK, AL |
| C | 6.41 (%43) / -5.11 | 3.53 (%24) / -3.09 | 4.85 (%33) / -7.57 | IR, IL, SA, MK, AL, BA |

## 2. Kısa vade (2027–2029): TR kayıp hızı → bölgeye parasal akış

Kapasite (mn $/yıl, 2024 GSYH sabit): cari açık ort. 32,253; brüt birincil gelir ödemesi ort. 24,250; brüt rezerv 155,549.

### Senaryo A: kayıp [24.262, 23.607, 22.952] vekil (hız [-0.655, -0.655, -0.655]/yıl); alıcılara ulaşan pay %77

| Köprü | Akış mn $ (3 yıl) | % GSYH | Cari açığa oran (yıl 1) | 3 yıl aşım | Rezerve oran | Geçerli ölçek s | Karar | Bölgeye akış | Merkeze | Dış rakip güçlere |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| bop_merkez_rant | [62817, 61121, 59425] | [4.62, 4.5, 4.37] | 1.95 | 86,605 | 0.56 | 0.513 | gecerli_rezervle (rezerv sınırda) | [14096, 13716, 13335] | [24547, 23884, 23222] | [9965, 9696, 9427] |
| mal_net_ticaret | [116104, 112969, 109835] | [8.54, 8.31, 8.08] | 3.6 | 242,149 | 1.56 | 0.278 | gecersiz | [26054, 25350, 24647] | [45370, 44145, 42920] | [18417, 17920, 17423] |
| tum_havza_rant | [130606, 127080, 123554] | [9.61, 9.35, 9.09] | 4.05 | 284,480 | 1.83 | 0.247 | gecersiz | [29308, 28517, 27726] | [51037, 49659, 48281] | [20718, 20158, 19599] |

### Senaryo B: kayıp [39.276, 38.656, 38.036] vekil (hız [-0.62, -0.62, -0.62]/yıl); alıcılara ulaşan pay %76

| Köprü | Akış mn $ (3 yıl) | % GSYH | Cari açığa oran (yıl 1) | 3 yıl aşım | Rezerve oran | Geçerli ölçek s | Karar | Bölgeye akış | Merkeze | Dış rakip güçlere |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| bop_merkez_rant | [101690, 100085, 98480] | [7.48, 7.36, 7.25] | 3.15 | 203,496 | 1.31 | 0.317 | gecersiz | [17994, 17710, 17426] | [47157, 46413, 45668] | [12332, 12137, 11943] |
| mal_net_ticaret | [187952, 184985, 182018] | [13.83, 13.61, 13.39] | 5.83 | 458,196 | 2.95 | 0.172 | gecersiz | [33258, 32733, 32208] | [87159, 85783, 84407] | [22793, 22433, 22074] |
| tum_havza_rant | [211428, 208091, 204753] | [15.56, 15.31, 15.07] | 6.56 | 527,513 | 3.39 | 0.153 | gecersiz | [37412, 36822, 36231] | [98046, 96498, 94950] | [25640, 25236, 24831] |

### Senaryo C: kayıp [16.755, 16.32, 15.884] vekil (hız [-0.436, -0.435, -0.436]/yıl); alıcılara ulaşan pay %77

| Köprü | Akış mn $ (3 yıl) | % GSYH | Cari açığa oran (yıl 1) | 3 yıl aşım | Rezerve oran | Geçerli ölçek s | Karar | Bölgeye akış | Merkeze | Dış rakip güçlere |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| bop_merkez_rant | [43381, 42254, 41126] | [3.19, 3.11, 3.03] | 1.35 | 30,002 | 0.19 | 0.743 | gecerli_rezervle | [10984, 10699, 10413] | [14501, 14124, 13747] | [8004, 7796, 7588] |
| mal_net_ticaret | [80180, 78098, 76011] | [5.9, 5.75, 5.59] | 2.49 | 137,530 | 0.88 | 0.402 | gecerli_rezervle (rezerv sınırda) | [20302, 19775, 19247] | [26801, 26105, 25408] | [14793, 14409, 14024] |
| tum_havza_rant | [90195, 87853, 85506] | [6.64, 6.46, 6.29] | 2.8 | 166,794 | 1.07 | 0.358 | gecersiz | [22838, 22245, 21651] | [30149, 29366, 28582] | [16641, 16209, 15776] |

