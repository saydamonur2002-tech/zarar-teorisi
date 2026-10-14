# Havzalar net kaybediyorsa kim kazanıyor? ve kısa vadeli parasal akış

GSYH 2024'te sabit (büyüme yok); rezerv brüt (altın dahil), net rezerv değil; yeni borç/swap ve akışın çok yıllı ivmesi modellenmedi.

## 1. Kayıp havuzu ve kim topluyor

| Senaryo | Net kaybeden havza | Σ havza net | TR kaybı | Diğer kayıp | Havuz | Kazanç (V ile sınırlı) | Ölü ağırlık | Oran |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 30/30 | -15.25 | 25.82 | 14.38 | 40.20 | 25.40 | 14.80 | %37 |
| B | 30/30 | -25.73 | 41.76 | 24.13 | 65.89 | 40.46 | 25.43 | %39 |
| C | 30/30 | -9.90 | 17.70 | 9.37 | 27.07 | 17.05 | 10.02 | %37 |

| Senaryo | Merkez (MFİN, ABD, AB, Fransa) brüt / net | Dış rakip güçler (Çin, Rusya) brüt / net | Bölge brüt / net | Bant dışı kazananlar |
| --- | --- | --- | --- | --- |
| A | 12.41 (%45) / -5.75 | 6.79 (%25) / -3.44 | 8.18 (%30) / -10.84 | MFIN, IR, IL, SA, MK, AL, BA |
| B | 24.93 (%56) / -9.62 | 8.67 (%20) / -7.92 | 10.94 (%25) / -20.50 | IR, IL, SA, MK, AL, BA |
| C | 7.00 (%38) / -4.22 | 5.15 (%28) / -1.78 | 6.01 (%33) / -6.58 | MFIN, IR, US, IL, SA, MK, AL, BA |

## 2. Kısa vade (2027–2029): TR kayıp hızı → bölgeye parasal akış

Kapasite (mn $/yıl, 2024 GSYH sabit): cari açık ort. 32,253; brüt birincil gelir ödemesi ort. 24,250; brüt rezerv 155,549.

### Senaryo A: kayıp [24.262, 23.607, 22.952] vekil (hız [-0.655, -0.655, -0.655]/yıl); alıcılara ulaşan pay %98

| Köprü | Akış mn $ (3 yıl) | % GSYH | Cari açığa oran (yıl 1) | 3 yıl aşım | Rezerve oran | Geçerli ölçek s | Karar | Bölgeye akış | Merkeze | Dış rakip güçlere |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| bop_merkez_rant | [62817, 61121, 59425] | [4.62, 4.5, 4.37] | 1.95 | 86,605 | 0.56 | 0.513 | gecerli_rezervle (rezerv sınırda) | [18472, 17974, 17475] | [27987, 27231, 26476] | [15322, 14908, 14494] |
| mal_net_ticaret | [116104, 112969, 109835] | [8.54, 8.31, 8.08] | 3.6 | 242,149 | 1.56 | 0.278 | gecersiz | [34142, 33221, 32299] | [51727, 50331, 48934] | [28319, 27554, 26790] |
| tum_havza_rant | [130606, 127080, 123554] | [9.61, 9.35, 9.09] | 4.05 | 284,480 | 1.83 | 0.247 | gecersiz | [38407, 37370, 36333] | [58188, 56617, 55047] | [31856, 30996, 30136] |

### Senaryo B: kayıp [39.276, 38.656, 38.036] vekil (hız [-0.62, -0.62, -0.62]/yıl); alıcılara ulaşan pay %97

| Köprü | Akış mn $ (3 yıl) | % GSYH | Cari açığa oran (yıl 1) | 3 yıl aşım | Rezerve oran | Geçerli ölçek s | Karar | Bölgeye akış | Merkeze | Dış rakip güçlere |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| bop_merkez_rant | [101690, 100085, 98480] | [7.48, 7.36, 7.25] | 3.15 | 203,496 | 1.31 | 0.317 | gecersiz | [24238, 23856, 23473] | [55177, 54306, 53435] | [19213, 18910, 18607] |
| mal_net_ticaret | [187952, 184985, 182018] | [13.83, 13.61, 13.39] | 5.83 | 458,196 | 2.95 | 0.172 | gecersiz | [44799, 44092, 43385] | [101981, 100372, 98762] | [35511, 34951, 34390] |
| tum_havza_rant | [211428, 208091, 204753] | [15.56, 15.31, 15.07] | 6.56 | 527,513 | 3.39 | 0.153 | gecersiz | [50395, 49599, 48804] | [114720, 112909, 111098] | [39947, 39316, 38686] |

### Senaryo C: kayıp [16.755, 16.32, 15.884] vekil (hız [-0.436, -0.435, -0.436]/yıl); alıcılara ulaşan pay %96

| Köprü | Akış mn $ (3 yıl) | % GSYH | Cari açığa oran (yıl 1) | 3 yıl aşım | Rezerve oran | Geçerli ölçek s | Karar | Bölgeye akış | Merkeze | Dış rakip güçlere |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| bop_merkez_rant | [43381, 42254, 41126] | [3.19, 3.11, 3.03] | 1.35 | 30,002 | 0.19 | 0.743 | gecerli_rezervle | [13830, 13471, 13111] | [16086, 15669, 15250] | [11866, 11558, 11249] |
| mal_net_ticaret | [80180, 78098, 76011] | [5.9, 5.75, 5.59] | 2.49 | 137,530 | 0.88 | 0.402 | gecerli_rezervle (rezerv sınırda) | [25562, 24898, 24233] | [29732, 28960, 28186] | [21932, 21363, 20792] |
| tum_havza_rant | [90195, 87853, 85506] | [6.64, 6.46, 6.29] | 2.8 | 166,794 | 1.07 | 0.358 | gecersiz | [28755, 28008, 27260] | [33446, 32577, 31707] | [24672, 24031, 23389] |

