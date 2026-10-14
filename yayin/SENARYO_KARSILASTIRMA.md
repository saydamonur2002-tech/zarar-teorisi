# Senaryo karşılaştırması (A | B | C)

Aynı alanlar, aynı sıra. Her sütun ilgili `SENARYO_RAPOR_{X}.md` ile birebir.

## 1. Tanım (senaryo parametreleri)

| Alan | A | B | C |
| --- | ---: | ---: | ---: |
| Ad | Atıl bağ — pasif tutum | Araçsallaşma + donmuş enigma | Katmanlı oyun inşası — kısmi kullanım |
| Olasılık (kapı iskeleti, gözlem yokken tekdüze) | 0.333 | 0.333 | 0.333 |
| Etki erozyonu çarpanı | 0.35 | 0.58 | 0.22 |
| TR diplomatik esneklik | 0 | -0.06 | 0.12 |
| Merkez sızıntı çarpanı (geçmişten, A=1) | 1 | 1.909 | 0.622 |
| Merkez sızıntı çarpanı (eski, atanmış) | 1 | 1.15 | 0.9 |
| Bağ modu kullanım / atıl / araçsal | 0.22 / 0.5 / 0.28 | 0.14 / 0.32 / 0.54 | 0.52 / 0.26 / 0.22 |

## 2. Projeksiyon (10 yıl vekil)

| Alan | A | B | C |
| --- | ---: | ---: | ---: |
| TR yarıçevre boşalma | 24.952 | 40.166 | 17.172 |
| Merkez finans sızıntı Σ | 13.133 | 31.862 | 6.157 |
| MFIN kenar Σ | 9.192 | 27.997 | 3.918 |
| Tüm havza rant Σ | 1.984 | 4.083 | 1.12 |
| Merkez + rant Σ | 15.117 | 35.945 | 7.277 |
| Pasif boşluk Σ | 5.566 | 3.695 | 2.823 |
| Araçsallaşma Σ | 1.946 | 3.891 | 1.491 |
| Temsil zedesi Σ | 2.688 | 3.186 | 1.626 |
| Dış mimari Σ | 3.608 | 3.642 | 2.072 |
| İç dinamik tıkanma | 0.642 | 0.789 | 0.334 |

## 3. Akış ölçümü (USD köprüsü, mn $)

| Alan | A | B | C |
| --- | ---: | ---: | ---: |
| MFIN kenar | 11,456.4 | 14,675.0 | 10,144.2 |
| Belirsiz merkez | 4,911.8 | 2,025.9 | 5,797 |
| Merkez toplam | 16,368.3 | 16,700.8 | 15,941.2 |
| Rant toplam | 2,472.7 | 2,140.2 | 2,899.8 |

## 4. Zarar çözümü (beş adım varsayımı)

| Alan | A | B | C |
| --- | ---: | ---: | ---: |
| TR net ham | -25.822 | -41.76 | -17.7 |
| TR net çözüm sonrası | -19.137 | -30.961 | -13.113 |
| TR net farkı | 6.685 | 10.799 | 4.587 |
| TR boşalma ham → sonrası | 24.952 → 21.247 | 40.166 → 34.201 | 17.172 → 14.622 |

## 5. Üretim iç akışı ve finans katmanı

| Alan | A | B | C |
| --- | ---: | ---: | ---: |
| Üretim iç akış TR net | -13.32 | -24.82 | -4.383 |
| Üretim: sıfır yılı tahmini | 2065 | 2087 | 2044 |
| Finans katmanı TR net | -7.707 | -32.16 | -1.23 |
| Finans: sıfır üstü takvim yılı | 2050 | — | 2040 |
| Üretime bağlanma gerçekleşmesi g_u (bağ kullanımı / C) | 0.423 | 0.269 | 1 |
| Finans dış koşul gerçekleşmesi g_f (politika / C; < 0: ters çevrilmiş) | 0.737 | -0.432 | 1 |
| Finans ters çevrildi (araçsallaşma) | hayır | evet | hayır |
| Finans TR net: çevrilmemiş olsaydı (varsayım bandı üstü) | — | -17.48 | — |
| Finans etiketi | varsayim_carpanli_ham | varsayim_carpanli_ham | varsayim_carpanli_ham |

## 6. Stok-akış (SFC, tr TL)

| Alan | A | B | C |
| --- | ---: | ---: | ---: |
| Matris dönemi / kur | 2026-Q1 / 44.38 | 2026-Q1 / 44.38 | 2026-Q1 / 44.38 |
| H | 0 | 0 | 0 |
| F | -1.886 | -3.482 | -1.001 |
| B | 0 | 0 | 0 |
| K | 0 | 0 | 0 |
| D | 1.886 | 3.482 | 1.001 |
| Kapanış (Σ=0) | evet | evet | evet |
| F.4 stok 2036, baz (mr TL) | 25,339.8 | 25,339.8 | 25,339.8 |
| F.4 stok 2036, silme %20 varsayımı | 20,271.8 | 20,271.8 | 20,271.8 |

## 7. Gerçeklik kalibrasyonu

| Alan | A | B | C |
| --- | ---: | ---: | ---: |
| TR net son (kalibre) | -16.755 | -43.277 | -11.377 |
| GSYH % | 5.009 | 12.938 | 3.401 |
| TR net 10. yıl yolu | -19.355 | -37.975 | -13.415 |
| Yol modu (finans üretimle eşzamanlı mı) | uretimle_es_zamanli | uretimle_es_zamanli | uretimle_es_zamanli |
| Finans kalibre gerçekleşme r_f (tersse harm: tavan yok) | 0.209 | 0.95 | 0.219 |
| Gerçekleşme: zarar / üretim / finans | 0.49 / 0.237 / 0.209 | 0.287 / 0.237 / 0.95 | 0.665 / 0.237 / 0.219 |

## 8. Dış rant parasal akışı

| Alan | A | B | C |
| --- | ---: | ---: | ---: |
| Boşluk rantı toplam (vekil) | 7.895 | 14.574 | 4.189 |
| Refah dış toplam (vekil) | 1.984 | 4.084 | 1.12 |
| Refah TR iç toplam (vekil) | 0.905 | 1.864 | 0.509 |
| Boşluk rantı (mn $) | 42,499.9 | 78,453.9 | 22,550.0 |
| Refah dış (mn $) | 10,680.1 | 21,984.7 | 6,029.1 |

## 9. Uluslararası stok-akış

| Alan | A | B | C |
| --- | ---: | ---: | ---: |
| Kapanış tamam | evet | evet | evet |
| Havza net stok (mn $) | 59,935.9 | 112,206.2 | 40,831.1 |
| Havza kayıp brüt kenar (mn $) | 216,391.5 | 354,705.8 | 145,721.8 |
| Merkez sızıntı (mn $) | 51,935.9 | 111,361.1 | 25,430.5 |
| Kanal ikame (mn $) | 92,477.1 | 113,950.3 | 70,696.7 |

## 10. Dış aktörlerin kaybın devamlılığı için maliyeti (varsayım)

| Alan | A | B | C |
| --- | ---: | ---: | ---: |
| Maliyet katsayısı κ × TR karşı-hamle gücü pol | 0.2 × 0.7 | 0.2 × 0.41 | 0.2 × 0.95 |
| Σ sürdürme maliyeti (TR, MFIN hariç) | 2.36 | 1.824 | 2.375 |
| Σ dış kazanç (TR, MFIN hariç) | 19.165 | 25.249 | 14.248 |
| Maliyet / kazanç | 0.123 | 0.072 | 0.167 |
| Kazançtan maliyet düşülünce Σ dış net | 16.805 | 23.425 | 11.873 |

## 11. Merkez finans (MFIN) ayrı pay (kayıp = referans vekil)

| Alan | A | B | C |
| --- | ---: | ---: | ---: |
| MFIN kazancı (sızıntı kenarları, normalize) | 8.218 | 19.296 | 3.918 |
| MFIN kaybı (referans-oran vekil, ±belirsizlik) | ≈2.41 (±3.941) | ≈8.637 (±12.217) | ≈0.874 (±1.634) |
| MFIN sürdürme maliyeti | 1.151 | 1.582 | 0.744 |
| MFIN net (kayıp ve maliyet düşülmüş) | 4.657 | 9.077 | 2.3 |
| MFIN payı / boşluk V | 0.324 | 0.477 | 0.225 |

## Not

**Yapısal sınır (A, B, C için aynı):** üretim ve finans katmanları senaryoya özgü gerçekleşmeyle kurulur: g_u = bağ kullanımı / C'ninki (üretime bağlama kanalı), g_f = politika gerçekleşmesi / C'ninki (dış koşul: erozyon, diplomatik esneklik). Etkin çarpan = 1 − g (1 − çarpan); C'de g = 1. Çarpanların kendisi (halka düzeltmesi, MFIN, TDS, iç tutma) tüm senaryolarda ortak ve atanmıştır; g türetilmiştir ama doğrusal ölçekleme varsayımdır. Baskın modu araçsal olan senaryoda (B) finans katmanı ters çevrilir (g_f < 0, ayna simetri, güç 1: varsayım; duyarlılık finans raporunda). F.4 stok yolu (bölüm 6) beş adımın kredi itişinden gelir ve senaryodan bağımsızdır; üç sütunda aynı olması senaryo farkı değil model yapısıdır. Finans katmanı kalibre yola bağlıdır (üretimle eşzamanlı yükselir); çarpanları atanmıştır. Olasılık ölçülmemiştir (gözlem yokken tekdüze); bu rapor senaryolar arasında sıra kurmaz.
