# Odak: İsrail, İran, Mısır

Bu bölüm modeli değiştirmez. Sayılar `olustur.py` ile mevcut dosyalardan okunur. Havza satırı olmayan yer null kalır.

Yenilemek, repo kökünden: `python3 etki_cephesi/odak_israil_iran_misir/olustur.py`.

Havza payı, `havza_kayip.json` ile aynı kuraldır: mutlak net bölü otuz havzanın net toplamının mutlak değeri, yüzde, iki ondalık. Toplam net A −15,247, B −25,727, C −9,899.

## İran

Üç havza. Ülke toplamı bu üç netin toplamıdır. Aktör kodu IR. Aktör defterindeki `havza_net`, üç havzanın toplamına eşittir.

|  | A net | A pay | B net | B pay | C net | C pay |
| --- | --- | --- | --- | --- | --- | --- |
| İran — Körfez/güney | -0.159 | 1.04 | -0.251 | 0.98 | -0.105 | 1.06 |
| İran — Doğu/Orta Asya kapısı | -0.156 | 1.02 | -0.27 | 1.05 | -0.1 | 1.01 |
| İran — Irak/Suriye hattı | -0.102 | 0.67 | -0.153 | 0.59 | -0.072 | 0.73 |
| ülke toplamı | -0.417 | 2.73 | -0.674 | 2.62 | -0.277 | 2.8 |

## Mısır

Tek havza: `misir`, Kuzey Afrika — Mısır (Nil). Ülke toplamı bu satırdır. Aktör kodu EG. Aktör defterindeki `havza_net` bu havza satırından farklıdır; iki kaynak yan yana durur, biri diğerine çekilmedi.

|  | A net | A pay | B net | B pay | C net | C pay |
| --- | --- | --- | --- | --- | --- | --- |
| Kuzey Afrika — Mısır (Nil) | -0.331 | 2.17 | -0.527 | 2.05 | -0.223 | 2.25 |
| ülke toplamı | -0.331 | 2.17 | -0.527 | 2.05 | -0.223 | 2.25 |

## İsrail

İsrail havza_kayip.json otuz havzasında ve geri_kalan.json aktörlerinde yok. Kendi havza neti ve ülke toplamı null. Aktör IL PROJEKSIYON.json içinde var; başka havzaların pay katsayılarında da geçer. O katsayılar net değildir.

Kendi havza neti: null. Ülke toplamı: null.

Bulunan İsrail sayıları aktör defterindedir (kod IL), 2023 dış ticaret gözleminde ve başka havzalara yazılmış pay katsayılarındadır. Katsayı, o havzanın neti değildir.

`ulke_havza_pay.json` içindeki İsrail payı:

| Havza | ulke_havza_pay |
| --- | --- |
| dogu_akdeniz_gaz | 0.28 |
| dogu_akdeniz_kefalet | 0.15 |

`dis_aktör_pay.json` içindeki İsrail payı. Aynı havza adı iki dosyada ayrı katsayı taşır.

| Havza | dis_aktör_pay |
| --- | --- |
| dogu_akdeniz_gaz | 0.24 |
| dogu_akdeniz_kefalet | 0.2 |
| dogu_akdeniz | 0.22 |
| misir | 0.15 |

## Aktör defteri

Kaynak: `PROJEKSIYON.json` `aktör_birlesik`. Birim vekil.

| Ülke | Senaryo | havza_net | dış kazanç | net, maliyet düşülmüş | durum |
| --- | --- | --- | --- | --- | --- |
| İran | A | -0.417 | 1.438 | 0.82 | dis_kazanc |
| İran | B | -0.674 | 1.715 | 0.9 | dis_kazanc |
| İran | C | -0.277 | 1.139 | 0.646 | dis_kazanc |
| Mısır | A | -0.505 | 0.271 | -0.272 | havza_kayip |
| Mısır | B | -0.891 | 0.353 | -0.567 | havza_kayip |
| Mısır | C | -0.316 | 0.201 | -0.153 | havza_kayip |
| İsrail | A | -0.232 | 0.527 | 0.221 | dis_kazanc |
| İsrail | B | -0.487 | 0.71 | 0.165 | dis_kazanc |
| İsrail | C | -0.124 | 0.38 | 0.184 | dis_kazanc |

## Gözlem, 2023

Kaynak, güncel model zipindeki `data/etki_cephesi/gozlem/dis_ticaret_gsyh_2023.json`. İhracat ortak ülke vektörü `odak_ulkeler.json` içindedir. GSYH milyon dolar.

| Ülke | kalibrasyon aktörü | GSYH mn $ | ihracat ortağı |
| --- | --- | --- | --- |
| İran | evet | 457510.5 | 30 |
| Mısır | evet | 395926.1 | 31 |
| İsrail | evet | 513393.4 | 18 |

## Sistem ve pay katsayısı

Rol ve refah endeksi `dis_ulke_sistemi.json` içindedir. Pay katsayıları `ulke_havza_pay.json`, `dis_aktör_pay.json` ve `ulkeler_bolge.json` içindedir. Üçü de zip girdisidir. Ayrıntı `odak_ulkeler.json`.

| Ülke | rol | refah endeksi | kendi havzası |
| --- | --- | --- | --- |
| İran | bolge_guc | 0.48 | var |
| Mısır | tampon | 0.44 | var |
| İsrail | bolge_guc | 0.82 | yok |

## Okunmayan yan kayıt

Bu dosyalarda IR, IL ve EG sayıları vardır. Dosyaların kendi notu ana modelin onları okumadığını söyler. Bölüm o sayıları kopyalamaz.

- `data/etki_cephesi/gozlem/duyarlilik/phi_kosu1_rs_az.json`
- `data/etki_cephesi/gozlem/duyarlilik/phi_kosu3_phi1_uye.json`
- `data/etki_cephesi/gozlem/duyarlilik/anomali_2026_10_17.json`

`geri_kalan.json` aktörlerinde İran, Mısır ve İsrail yoktur.
