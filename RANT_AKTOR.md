# Aktör bazlı rant kanalı direnci

**Senaryo; ölçüm değil.** Lobi bağımsız muhasebe proxy.

F referans (ölçüm, senaryo değil): finansman/faaliyet kârı **0.839** (3143.4/3746.2 milyar TL, 2024).

## Revize vs sert — H ve F (2031-Q4)

| Senaryo | Aktör | Rant kayıp | Rant direnci % | Amorti önce | Amorti sonra | Δ puan |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| uc_kural_kilitli | H | 113.8 | 2.12 | 9.99 | 9.19 | 0.8 |
| uc_kural_kilitli | F | 170.33 | 0.88 | 27.85 | 27.37 | 0.48 |
| uc_kural_kilitli | B | 119.23 | 1.49 | 74.07 | 73.78 | 0.29 |
| uc_kural_kilitli | K | 17.03 | 0.29 | 13.1 | 13.06 | 0.04 |
| maliyet_ucuz_revize | H | 289.98 | 22.64 | 9.99 | 7.91 | 2.08 |
| maliyet_ucuz_revize | F | 74.81 | 1.03 | 27.85 | 27.64 | 0.21 |
| maliyet_ucuz_revize | B | 52.37 | 0.66 | 74.07 | 73.95 | 0.12 |
| maliyet_ucuz_revize | K | 86.23 | 1.65 | 13.1 | 12.91 | 0.19 |

## Toplam ağırlıklı rant direnci

- **mevcut**: 0.0%
- **uc_kural_kilitli**: 1.44%
- **maliyet_ucuz_revize**: 9.66%

## Duyarlılık (revize, H)

Ho varlık payı %70–90 ve kira elastikiyeti 0,8–1,2: toplam rant direnci ~%7,7–%12,6; H ~%17,8–%29,9. `rant_aktor_duyarlik.csv`.

Payda: `max(|ΔNFP|, yıllık rant × ufuk_yil)`. Sert senaryoda H |ΔNFP| büyük → rant direnci düşük; revize kira kaybı baskın → H direnci yüksek.

## Ne denmez

- Ekonomik rantın tam ölçümü değildir; 0,84 yalnız F finansman/faaliyet referansıdır.
- K′ harcama ölçeği (8000 milyar TL/yıl) VARSAYIM; faiz payı %13,1 bütçe ham toplamından ölçülüdür.
