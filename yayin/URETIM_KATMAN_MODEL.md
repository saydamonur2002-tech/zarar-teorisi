# Üretim katmanı modeli (Drive) ve sisteme bağlanışı

Tipoloji katsayıları ölçülmemiştir (belgede VARSAYIM). İhracat kaybı penaltı sabitleri belge hücrelerinden alındı. Üretim katmanı gerçekleşmesi, tavan/ihtiyaç oranı tabanın altında kaldığı için tabanla belirlenir.

## Kaynak belgeler

- **81 İl Sızıntı Matrisi Analizi** (2026-08-31, `1WSI8f3jqplxSQ6TGOklvA46FN4lVXMyPAa4qE_68GlY`): tipoloji katsayıları, cari açık stres testi, revizyon (adreslenebilir taban, ihracat esnekliği)
- **Zarar_Teorisi_Tek_Cekirdek_Dort_Dugum_Tam_Rapor** (2026-08-31, `1kyycqD5RedYe3UT8wJDTQInyGE8Wul71BXZMA1vxa84`): 81 il simülasyonundaki ithalat gereği senaryoları (286,1 / 231,0 / 193,1 mn TL); düğüm numaralaması ve 3↔2↔1 mimarisi sisteme bağlanmadı
- **Görsellerdeki Üretim Borç Harcama Modelinin Teknik İncelemesi** (2026-07-02, `1UfxS1v5YWw3LuWrC1R6KvvH7qVExYnBx`): HC ≤ Y* + FX − DS kısıtı, iç/dış borç servisi ayrımı (sayısal parametre yok; kavramsal)
- **Türkiye Ekonomisi Model Analizi Raporu** (2026-07-05, `1LPVm6thF8tliPvYUMmj0D6d3trNxVIcFFMMPEVDRgdU`): Y*, D, HC stok-akış çerçevesi (sayısal katman parametresi yok; senaryo anlatısı)

## 1. Belge sayıları parametrelerden yeniden üretildi

| Büyüklük | Belge | Yeniden hesap |
| --- | ---: | ---: |
| Adreslenebilir ara malı tabanı (mrd $) | 198.11 | 198.109 |
| Brüt ithalat tasarrufu, orta_reform (mrd $) | 12.86 | 12.86 |
| Brüt ithalat tasarrufu, guclu_reform (mrd $) | 34.74 | 34.738 |
| Revize net iyileşme, koordinasyon (mrd $) | -2.886 | -2.886 |
| Revize net iyileşme, orta_reform (mrd $) | 4.265 | 4.264 |
| Revize net iyileşme, guclu_reform (mrd $) | 11.621 | 11.621 |
| Cari açık kapanma oranı, koordinasyon | -0.074 | -0.074 |
| Cari açık kapanma oranı, orta_reform | 0.11 | 0.11 |
| Cari açık kapanma oranı, guclu_reform | 0.299 | 0.299 |

## 2. İhracat esnekliği ε duyarlılığı: revize net iyileşme (mrd $/yıl)

| ε | koordinasyon | orta reform | güçlü reform |
| ---: | ---: | ---: | ---: |
| 0.0 | 0.0 | 7.15 | 19.316 |
| 0.15 | -1.443 | 5.707 | 15.468 |
| 0.3 | -2.886 | 4.264 | 11.621 |
| 0.5 | -4.81 | 2.34 | 6.491 |
| 0.75 | -7.215 | -0.065 | 0.078 |
| 1.0 | -9.62 | -2.47 | -6.334 |

Kritik eşik ε ≈ 0.75: orta ve güçlü reform nötr/negatif.

## 3. Sisteme iki bağ

- Üretim bağımlılığı halkası (C): 3.933 vekil ≈ 18,821 mn $ (mal ticareti köprüsü).
- **Halka çarpanı:** eski atanmış 0.68; modelden koordinasyon 1.1533, orta reform **0.7734** (kullanılan), güçlü reform 0.3826.
- **İyileşme tavanı (mn $/yıl):** eski 2,054.4; modelden koordinasyon 0.0, orta reform **4,264.5** (kullanılan), güçlü reform 11,620.6.

## 4. Üretim katmanı gerçekleşmesini ne belirliyor?

Üretim katmanının adımı 8.493 vekil ≈ 21,988 mn $ (BoP köprüsü). Tavan/ihtiyaç oranı: eski 0.0934, modelden **0.1939**; atanmış taban 0.25. Uygulanan gerçekleşme 0.2375: belirleyici **taban (atanmış)**.
