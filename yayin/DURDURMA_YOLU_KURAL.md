# Durdurmanın gerçekleşme yolu (kural bazlı)

Kurallar mekanizma düzeyinde (halka/katman/kapı), aktör düzeyinde değil. Eşleştirmeler ve kapı eşikleri atanmış; hız sabiti kalibre C yoluna uydurulmuş. Cari açık ve rezerv sabit (büyüme, yeni borç yok); rezerv brüt.

Kalibrasyon: a = 0.17641, θ_z = 0.5825, kalibre yola RMSE (d) = 0.01893. Faz sınırı: 2034.

Halka ağırlıkları (C): zarar_aktarimi 0.17, uretim_bagimlilik 0.226, para_sizintisi 0.187, koordinasyon_kopuk 0.102, dis_kisit 0.315.
Halka hızları g: zarar_aktarimi 0.665, uretim_bagimlilik 0.2375, para_sizintisi 0.2193, koordinasyon_kopuk 0.3739, dis_kisit 0.3739.

| Yıl | 2027 | 2028 | 2029 | 2030 | 2031 | 2032 | 2033 | 2034 | 2035 | 2036 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| d (kalibre C yolu) | 0.025 | 0.051 | 0.076 | 0.101 | 0.127 | 0.152 | 0.177 | 0.191 | 0.206 | 0.220 |
| d (kural, m=1) | 0.027 | 0.051 | 0.072 | 0.091 | 0.108 | 0.124 | 0.138 | 0.167 | 0.194 | 0.220 |

## kalibre (m = 1.0, sıra kuralı: True)

d yolu: 0.027, 0.051, 0.072, 0.091, 0.108, 0.124, 0.138, 0.167, 0.194, 0.220
d ≥ 0,25 / 0,5 / 0,75 yılı: None / None / None; halka açılış yılları: {'uretim_bagimlilik': 2034, 'para_sizintisi': 2034, 'dis_kisit': None}; son yıl halka durma oranları: {'zarar_aktarimi': 0.713, 'uretim_bagimlilik': 0.121, 'para_sizintisi': 0.112, 'koordinasyon_kopuk': 0.495, 'dis_kisit': 0.0}
TR net yolu: -16.75, -16.35, -15.99, -15.67, -15.39, -15.13, -14.90, -14.41, -13.96, -13.53

| Köprü | Akış / cari açık (yıl 1 → 10) | Akış cariye sığar (ilk yıl) | 10 yıl aşım | Rezerv oranı | Rezerv tükenme yılı |
| --- | --- | --- | ---: | ---: | --- |
| bop_merkez_rant | 1.38 → 1.12 | — | 82,810 | 0.53 | — |
| mal_net_ticaret | 2.56 → 2.07 | — | 426,650 | 2.74 | 2030 |
| tum_havza_rant | 2.88 → 2.32 | — | 520,228 | 3.34 | 2029 |

## hiz_x2 (m = 2.0, sıra kuralı: True)

d yolu: 0.053, 0.096, 0.129, 0.156, 0.210, 0.258, 0.300, 0.337, 0.370, 0.441
d ≥ 0,25 / 0,5 / 0,75 yılı: 2032 / None / None; halka açılış yılları: {'uretim_bagimlilik': 2031, 'para_sizintisi': 2031, 'dis_kisit': 2036}; son yıl halka durma oranları: {'zarar_aktarimi': 0.931, 'uretim_bagimlilik': 0.409, 'para_sizintisi': 0.383, 'koordinasyon_kopuk': 0.757, 'dis_kisit': 0.132}
TR net yolu: -16.30, -15.60, -15.04, -14.60, -13.69, -12.89, -12.19, -11.57, -11.02, -9.84

| Köprü | Akış / cari açık (yıl 1 → 10) | Akış cariye sığar (ilk yıl) | 10 yıl aşım | Rezerv oranı | Rezerv tükenme yılı |
| --- | --- | --- | ---: | ---: | --- |
| bop_merkez_rant | 1.35 → 0.81 | 2034 | 41,575 | 0.27 | — |
| mal_net_ticaret | 2.49 → 1.5 | — | 331,340 | 2.13 | 2030 |
| tum_havza_rant | 2.8 → 1.69 | — | 413,013 | 2.66 | 2029 |

## hiz_x3 (m = 3.0, sıra kuralı: True)

d yolu: 0.080, 0.135, 0.173, 0.250, 0.313, 0.365, 0.471, 0.558, 0.630, 0.689
d ≥ 0,25 / 0,5 / 0,75 yılı: 2031 / 2034 / None; halka açılış yılları: {'uretim_bagimlilik': 2030, 'para_sizintisi': 2030, 'dis_kisit': 2033}; son yıl halka durma oranları: {'zarar_aktarimi': 0.987, 'uretim_bagimlilik': 0.609, 'para_sizintisi': 0.578, 'koordinasyon_kopuk': 0.89, 'dis_kisit': 0.586}
TR net yolu: -15.86, -14.94, -14.31, -13.03, -11.98, -11.11, -9.34, -7.89, -6.70, -5.71

| Köprü | Akış / cari açık (yıl 1 → 10) | Akış cariye sığar (ilk yıl) | 10 yıl aşım | Rezerv oranı | Rezerv tükenme yılı |
| --- | --- | --- | ---: | ---: | --- |
| bop_merkez_rant | 1.31 → 0.47 | 2031 | 25,951 | 0.17 | — |
| mal_net_ticaret | 2.42 → 0.87 | 2036 | 227,631 | 1.46 | 2030 |
| tum_havza_rant | 2.73 → 0.98 | 2036 | 292,321 | 1.88 | 2030 |

## hiz_x5 (m = 5.0, sıra kuralı: True)

d yolu: 0.133, 0.281, 0.379, 0.553, 0.675, 0.761, 0.823, 0.868, 0.901, 0.925
d ≥ 0,25 / 0,5 / 0,75 yılı: 2028 / 2030 / 2032; halka açılış yılları: {'uretim_bagimlilik': 2028, 'para_sizintisi': 2028, 'dis_kisit': 2030}; son yıl halka durma oranları: {'zarar_aktarimi': 1.0, 'uretim_bagimlilik': 0.879, 'para_sizintisi': 0.856, 'koordinasyon_kopuk': 0.982, 'dis_kisit': 0.939}
TR net yolu: -14.97, -12.52, -10.87, -7.97, -5.94, -4.50, -3.47, -2.73, -2.18, -1.78

| Köprü | Akış / cari açık (yıl 1 → 10) | Akış cariye sığar (ilk yıl) | 10 yıl aşım | Rezerv oranı | Rezerv tükenme yılı |
| --- | --- | --- | ---: | ---: | --- |
| bop_merkez_rant | 1.24 → 0.15 | 2029 | 8,750 | 0.06 | — |
| mal_net_ticaret | 2.29 → 0.27 | 2031 | 99,133 | 0.64 | — |
| tum_havza_rant | 2.57 → 0.3 | 2032 | 128,242 | 0.82 | — |

## sirasiz (m = 1.0, sıra kuralı: False)

d yolu: 0.043, 0.083, 0.120, 0.154, 0.185, 0.214, 0.241, 0.266, 0.290, 0.311
d ≥ 0,25 / 0,5 / 0,75 yılı: 2034 / None / None; halka açılış yılları: {'uretim_bagimlilik': 2027, 'para_sizintisi': 2027, 'dis_kisit': None}; son yıl halka durma oranları: {'zarar_aktarimi': 0.713, 'uretim_bagimlilik': 0.348, 'para_sizintisi': 0.326, 'koordinasyon_kopuk': 0.495, 'dis_kisit': 0.0}
TR net yolu: -16.47, -15.80, -15.19, -14.62, -14.10, -13.62, -13.17, -12.75, -12.37, -12.00

| Köprü | Akış / cari açık (yıl 1 → 10) | Akış cariye sığar (ilk yıl) | 10 yıl aşım | Rezerv oranı | Rezerv tükenme yılı |
| --- | --- | --- | ---: | ---: | --- |
| bop_merkez_rant | 1.36 → 0.99 | 2036 | 51,127 | 0.33 | — |
| mal_net_ticaret | 2.52 → 1.83 | — | 367,602 | 2.36 | 2030 |
| tum_havza_rant | 2.83 → 2.06 | — | 453,804 | 2.92 | 2029 |

## sirasiz_x3 (m = 3.0, sıra kuralı: False)

d yolu: 0.130, 0.229, 0.306, 0.366, 0.478, 0.567, 0.640, 0.700, 0.749, 0.789
d ≥ 0,25 / 0,5 / 0,75 yılı: 2029 / 2032 / 2036; halka açılış yılları: {'uretim_bagimlilik': 2027, 'para_sizintisi': 2027, 'dis_kisit': 2031}; son yıl halka durma oranları: {'zarar_aktarimi': 0.987, 'uretim_bagimlilik': 0.739, 'para_sizintisi': 0.709, 'koordinasyon_kopuk': 0.89, 'dis_kisit': 0.734}
TR net yolu: -15.02, -13.37, -12.09, -11.08, -9.23, -7.74, -6.52, -5.53, -4.71, -4.04

| Köprü | Akış / cari açık (yıl 1 → 10) | Akış cariye sığar (ilk yıl) | 10 yıl aşım | Rezerv oranı | Rezerv tükenme yılı |
| --- | --- | --- | ---: | ---: | --- |
| bop_merkez_rant | 1.24 → 0.33 | 2029 | 11,180 | 0.07 | — |
| mal_net_ticaret | 2.29 → 0.62 | 2033 | 144,050 | 0.93 | — |
| tum_havza_rant | 2.58 → 0.69 | 2034 | 190,050 | 1.22 | 2030 |

## Rezerv 10 yıl boyunca tükenmesin diye gereken hız çarpanı m* (kalibre sıra kuralıyla)

bop_merkez_rant: 1.0, mal_net_ticaret: 3.83, tum_havza_rant: 4.97
