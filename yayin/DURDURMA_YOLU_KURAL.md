# Durdurmanın gerçekleşme yolu (kural bazlı)

Kurallar mekanizma düzeyinde (halka/katman/kapı), aktör düzeyinde değil. Eşleştirmeler ve kapı eşikleri atanmış; hız sabiti kalibre C yoluna uydurulmuş. Cari açık ve rezerv sabit (büyüme, yeni borç yok); rezerv brüt.

Kalibrasyon: a = 0.17554, θ_z = 0.5806, kalibre yola RMSE (d) = 0.01923. Faz sınırı: 2034.

Halka ağırlıkları (C): zarar_aktarimi 0.17, uretim_bagimlilik 0.226, para_sizintisi 0.187, koordinasyon_kopuk 0.102, dis_kisit 0.315.
Halka hızları g: zarar_aktarimi 0.665, uretim_bagimlilik 0.2375, para_sizintisi 0.2186, koordinasyon_kopuk 0.3737, dis_kisit 0.3737.

| Yıl | 2027 | 2028 | 2029 | 2030 | 2031 | 2032 | 2033 | 2034 | 2035 | 2036 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| d (kalibre C yolu) | 0.025 | 0.051 | 0.076 | 0.101 | 0.127 | 0.152 | 0.177 | 0.191 | 0.205 | 0.219 |
| d (kural, m=1) | 0.027 | 0.050 | 0.072 | 0.091 | 0.108 | 0.123 | 0.137 | 0.166 | 0.193 | 0.219 |

## kalibre (m = 1.0, sıra kuralı: True)

d yolu: 0.026, 0.050, 0.072, 0.091, 0.108, 0.123, 0.137, 0.166, 0.193, 0.219
d ≥ 0,25 / 0,5 / 0,75 yılı: None / None / None; halka açılış yılları: {'uretim_bagimlilik': 2034, 'para_sizintisi': 2034, 'dis_kisit': None}; son yıl halka durma oranları: {'zarar_aktarimi': 0.711, 'uretim_bagimlilik': 0.12, 'para_sizintisi': 0.111, 'koordinasyon_kopuk': 0.493, 'dis_kisit': 0.0}
TR net yolu: -16.75, -16.35, -16.00, -15.68, -15.39, -15.14, -14.90, -14.42, -13.97, -13.54

| Köprü | Akış / cari açık (yıl 1 → 10) | Akış cariye sığar (ilk yıl) | 10 yıl aşım | Rezerv oranı | Rezerv tükenme yılı |
| --- | --- | --- | ---: | ---: | --- |
| bop_merkez_rant | 1.38 → 1.12 | — | 83,018 | 0.53 | — |
| mal_net_ticaret | 2.56 → 2.07 | — | 427,034 | 2.75 | 2030 |
| tum_havza_rant | 2.88 → 2.33 | — | 520,660 | 3.35 | 2029 |

## hiz_x2 (m = 2.0, sıra kuralı: True)

d yolu: 0.053, 0.095, 0.128, 0.155, 0.210, 0.257, 0.299, 0.336, 0.369, 0.440
d ≥ 0,25 / 0,5 / 0,75 yılı: 2032 / None / None; halka açılış yılları: {'uretim_bagimlilik': 2031, 'para_sizintisi': 2031, 'dis_kisit': 2036}; son yıl halka durma oranları: {'zarar_aktarimi': 0.93, 'uretim_bagimlilik': 0.407, 'para_sizintisi': 0.381, 'koordinasyon_kopuk': 0.755, 'dis_kisit': 0.131}
TR net yolu: -16.31, -15.61, -15.05, -14.61, -13.70, -12.90, -12.21, -11.59, -11.04, -9.87

| Köprü | Akış / cari açık (yıl 1 → 10) | Akış cariye sığar (ilk yıl) | 10 yıl aşım | Rezerv oranı | Rezerv tükenme yılı |
| --- | --- | --- | ---: | ---: | --- |
| bop_merkez_rant | 1.35 → 0.82 | 2034 | 41,774 | 0.27 | — |
| mal_net_ticaret | 2.49 → 1.51 | — | 332,018 | 2.13 | 2030 |
| tum_havza_rant | 2.8 → 1.69 | — | 413,775 | 2.66 | 2029 |

## hiz_x3 (m = 3.0, sıra kuralı: True)

d yolu: 0.080, 0.134, 0.172, 0.249, 0.312, 0.364, 0.469, 0.556, 0.628, 0.687
d ≥ 0,25 / 0,5 / 0,75 yılı: 2031 / 2034 / None; halka açılış yılları: {'uretim_bagimlilik': 2030, 'para_sizintisi': 2030, 'dis_kisit': 2033}; son yıl halka durma oranları: {'zarar_aktarimi': 0.987, 'uretim_bagimlilik': 0.608, 'para_sizintisi': 0.575, 'koordinasyon_kopuk': 0.888, 'dis_kisit': 0.584}
TR net yolu: -15.87, -14.95, -14.32, -13.04, -12.00, -11.13, -9.37, -7.92, -6.73, -5.74

| Köprü | Akış / cari açık (yıl 1 → 10) | Akış cariye sığar (ilk yıl) | 10 yıl aşım | Rezerv oranı | Rezerv tükenme yılı |
| --- | --- | --- | ---: | ---: | --- |
| bop_merkez_rant | 1.31 → 0.47 | 2031 | 26,058 | 0.17 | — |
| mal_net_ticaret | 2.42 → 0.88 | 2036 | 228,449 | 1.47 | 2030 |
| tum_havza_rant | 2.73 → 0.99 | 2036 | 293,241 | 1.89 | 2030 |

## hiz_x5 (m = 5.0, sıra kuralı: True)

d yolu: 0.133, 0.279, 0.378, 0.552, 0.673, 0.759, 0.821, 0.866, 0.899, 0.923
d ≥ 0,25 / 0,5 / 0,75 yılı: 2028 / 2030 / 2032; halka açılış yılları: {'uretim_bagimlilik': 2028, 'para_sizintisi': 2028, 'dis_kisit': 2030}; son yıl halka durma oranları: {'zarar_aktarimi': 1.0, 'uretim_bagimlilik': 0.878, 'para_sizintisi': 0.853, 'koordinasyon_kopuk': 0.981, 'dis_kisit': 0.938}
TR net yolu: -14.98, -12.54, -10.89, -8.00, -5.97, -4.54, -3.50, -2.76, -2.21, -1.80

| Köprü | Akış / cari açık (yıl 1 → 10) | Akış cariye sığar (ilk yıl) | 10 yıl aşım | Rezerv oranı | Rezerv tükenme yılı |
| --- | --- | --- | ---: | ---: | --- |
| bop_merkez_rant | 1.24 → 0.15 | 2029 | 8,833 | 0.06 | — |
| mal_net_ticaret | 2.29 → 0.27 | 2031 | 99,557 | 0.64 | — |
| tum_havza_rant | 2.57 → 0.31 | 2032 | 128,915 | 0.83 | — |

## sirasiz (m = 1.0, sıra kuralı: False)

d yolu: 0.043, 0.083, 0.119, 0.153, 0.184, 0.213, 0.240, 0.265, 0.288, 0.310
d ≥ 0,25 / 0,5 / 0,75 yılı: 2034 / None / None; halka açılış yılları: {'uretim_bagimlilik': 2027, 'para_sizintisi': 2027, 'dis_kisit': None}; son yıl halka durma oranları: {'zarar_aktarimi': 0.711, 'uretim_bagimlilik': 0.347, 'para_sizintisi': 0.324, 'koordinasyon_kopuk': 0.493, 'dis_kisit': 0.0}
TR net yolu: -16.47, -15.81, -15.20, -14.64, -14.12, -13.63, -13.19, -12.77, -12.38, -12.03

| Köprü | Akış / cari açık (yıl 1 → 10) | Akış cariye sığar (ilk yıl) | 10 yıl aşım | Rezerv oranı | Rezerv tükenme yılı |
| --- | --- | --- | ---: | ---: | --- |
| bop_merkez_rant | 1.36 → 0.99 | 2036 | 51,455 | 0.33 | — |
| mal_net_ticaret | 2.52 → 1.84 | — | 368,312 | 2.37 | 2030 |
| tum_havza_rant | 2.83 → 2.07 | — | 454,603 | 2.92 | 2029 |

## sirasiz_x3 (m = 3.0, sıra kuralı: False)

d yolu: 0.129, 0.228, 0.304, 0.365, 0.476, 0.565, 0.638, 0.698, 0.747, 0.787
d ≥ 0,25 / 0,5 / 0,75 yılı: 2029 / 2032 / 2036; halka açılış yılları: {'uretim_bagimlilik': 2027, 'para_sizintisi': 2027, 'dis_kisit': 2031}; son yıl halka durma oranları: {'zarar_aktarimi': 0.987, 'uretim_bagimlilik': 0.737, 'para_sizintisi': 0.706, 'koordinasyon_kopuk': 0.888, 'dis_kisit': 0.732}
TR net yolu: -15.04, -13.39, -12.12, -11.11, -9.26, -7.77, -6.55, -5.56, -4.75, -4.07

| Köprü | Akış / cari açık (yıl 1 → 10) | Akış cariye sığar (ilk yıl) | 10 yıl aşım | Rezerv oranı | Rezerv tükenme yılı |
| --- | --- | --- | ---: | ---: | --- |
| bop_merkez_rant | 1.24 → 0.34 | 2030 | 11,296 | 0.07 | — |
| mal_net_ticaret | 2.3 → 0.62 | 2033 | 144,736 | 0.93 | — |
| tum_havza_rant | 2.58 → 0.7 | 2034 | 191,013 | 1.23 | 2030 |

## Rezerv 10 yıl boyunca tükenmesin diye gereken hız çarpanı m* (kalibre sıra kuralıyla)

bop_merkez_rant: 1.0, mal_net_ticaret: 3.85, tum_havza_rant: 4.97

## Alternatif kural yapısı: kullanıcının 3↔2↔1 ⇒ 4 ⇒ 5 mimarisi

Halkalar 1 (üretim), 2 (koordinasyon), 3 (para sızıntısı) kendi hızlarında ilerler; 4 (zarar aktarımı) yalnız ortak ilerlemeyle (geometrik ortalama) azalır, 5 (dış kısıt) 4 yarıya inince açılır.
Kalibrasyon: a = 0.17206, kalibre yola RMSE (d) = 0.01199 (faz sıralı yapı: 0.01923).

| Yıl | 2027 | 2028 | 2029 | 2030 | 2031 | 2032 | 2033 | 2034 | 2035 | 2036 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| d (kalibre C yolu) | 0.025 | 0.051 | 0.076 | 0.101 | 0.127 | 0.152 | 0.177 | 0.191 | 0.205 | 0.219 |
| d (3↔2↔1, m=1) | 0.023 | 0.045 | 0.068 | 0.090 | 0.112 | 0.134 | 0.156 | 0.177 | 0.198 | 0.219 |

### 3↔2↔1 kalibre (m = 1.0)

d yolu: 0.023, 0.045, 0.068, 0.090, 0.112, 0.134, 0.156, 0.177, 0.198, 0.219
d ≥ 0,25 / 0,5 / 0,75 yılı: None / None / None; son yıl halka durma oranları: {'zarar_aktarimi': 0.192, 'uretim_bagimlilik': 0.341, 'para_sizintisi': 0.318, 'koordinasyon_kopuk': 0.486, 'dis_kisit': 0.0}
Rezerv tükenme yılı (BoP / mal / rant): — / 2030 / 2029

### 3↔2↔1 hiz_x2 (m = 2.0)

d yolu: 0.046, 0.091, 0.135, 0.178, 0.220, 0.261, 0.299, 0.335, 0.369, 0.400
d ≥ 0,25 / 0,5 / 0,75 yılı: 2032 / None / None; son yıl halka durma oranları: {'zarar_aktarimi': 0.545, 'uretim_bagimlilik': 0.574, 'para_sizintisi': 0.543, 'koordinasyon_kopuk': 0.748, 'dis_kisit': 0.0}
Rezerv tükenme yılı (BoP / mal / rant): — / 2030 / 2029

### 3↔2↔1 hiz_x3 (m = 3.0)

d yolu: 0.069, 0.136, 0.201, 0.263, 0.320, 0.373, 0.419, 0.520, 0.604, 0.673
d ≥ 0,25 / 0,5 / 0,75 yılı: 2030 / 2034 / None; son yıl halka durma oranları: {'zarar_aktarimi': 0.812, 'uretim_bagimlilik': 0.73, 'para_sizintisi': 0.698, 'koordinasyon_kopuk': 0.883, 'dis_kisit': 0.474}
Rezerv tükenme yılı (BoP / mal / rant): — / 2031 / 2030

### 3↔2↔1 hiz_x5 (m = 5.0)

d yolu: 0.114, 0.224, 0.326, 0.413, 0.584, 0.705, 0.790, 0.849, 0.890, 0.919
d ≥ 0,25 / 0,5 / 0,75 yılı: 2029 / 2031 / 2033; son yıl halka durma oranları: {'zarar_aktarimi': 0.988, 'uretim_bagimlilik': 0.898, 'para_sizintisi': 0.875, 'koordinasyon_kopuk': 0.979, 'dis_kisit': 0.902}
Rezerv tükenme yılı (BoP / mal / rant): — / — / 2031

3↔2↔1 mimarisiyle rezerv tükenmesin diye gereken m*: bop_merkez_rant: 1.0, mal_net_ticaret: 4.27, tum_havza_rant: 5.23
