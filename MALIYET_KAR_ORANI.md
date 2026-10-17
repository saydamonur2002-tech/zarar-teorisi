# Maliyet/kar oranı (SFC senaryo)

**Senaryo; ölçüm değil.** Kar proxy muhasebe kârı değildir.

Çalıştır: `python3 maliyet_kar_orani.py` (`uc_kural_senaryo.csv` veya otomatik `run()`).

## Ölçülen referans (senaryo değil)

| Yıl | Finansman | Faaliyet kârı | Oran |
| --- | ---: | ---: | ---: |
| 2023 | 2120.2 | 3797.9 | 0.558 |
| 2024 | 3143.4 | 3746.2 | 0.839 |

Faiz yükünün faaliyet kârını ne kadar yediği. Senaryo maliyet/kar ile **karıştırılmaz**.

## Senaryo proxy (2031-Q4)

| Senaryo | F maliyet | K′ maliyet (|küm.|) | Toplam maliyet | Kar (kapsama) | Maliyet/kar | F özel (×1000/|ΔNFP_F|) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| mevcut | 0.0 | 0.0 | 0.0 | 0.0 | None | 0.0 |
| uc_kural_kilitli | 13647.5 | 4695.2 | 18342.7 | 142.51 | 128.71 | 375.25 |
| maliyet_ucuz_revize | 834.9 | 19.0 | 853.9 | 78.53 | 10.87 | 52.69 |

## Alternatif kar proxy (isteğe bağlı)

- **mevcut**: NFP_H Δ=4581.8 milyar → maliyet/kar=0.0; Ha servis düşüş=-0.118 → maliyet/kar=None
- **uc_kural_kilitli**: NFP_H Δ=9947.3 milyar → maliyet/kar=1.84; Ha servis düşüş=0.157 → maliyet/kar=116832.48
- **maliyet_ucuz_revize**: NFP_H Δ=5335.1 milyar → maliyet/kar=0.16; Ha servis düşüş=-0.119 → maliyet/kar=None

## Duyarlılık özeti

- yaşam düşüş `0.03`: maliyet/kar=12.15, Δkapsama=0.244
- yaşam düşüş `0.04`: maliyet/kar=10.87, Δkapsama=0.287
- yaşam düşüş `0.05`: maliyet/kar=9.86, Δkapsama=0.323

## Ne denmez

- Politika vaadi değil.
- K′ ≠ tam kamu konsolidasyonu.
