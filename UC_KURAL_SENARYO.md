# SFC senaryo: sert taban vs maliyet ucuzlatma revizesi

Stok-akış tutarlı **senaryo**; ölçüm değil. Çalıştır: `python3 uc_kural_senaryo.py`.

## Senaryolar

| Kod | İçerik |
| --- | --- |
| `mevcut` | Donuk nominal taban; kart/tüketici büyüme iddiası |
| `uc_kural_kilitli` | Sert taban telafisi + kama; işveren yükü F′de |
| `maliyet_ucuz_revize` | Yaşam maliyeti reel düşüş + sınırlı zam; memur K′; seçici kredi |

## Revize parametreleri (VARSAYIM)

- Yaşam maliyeti reel düşüş (yıllık): `0.04`
- Taban yarıyıl nominal artış %: `0.85`
- Kamu makas (milyar TL/çeyrek): `45.0`
- Ek kilit yaşam→limit (revize): `limit_dondur = limit_stres ∧ (yasam_dusus_oran ≥ 0.015)` (Q1/Q3 yaşam düşüş çeyreklerinde; sert/mevcut bypass).

## 2031-Q4 üçlü karşılaştırma

| Gösterge | Mevcut | Sert üç kural | Maliyet revize |
| --- | ---: | ---: | ---: |
| NFP_H | 26182.2 | 31554.1 | 26941.5 |
| NFP_F | -47839.2 | -67151.0 | -46628.0 |
| borc_servis_orani_Ha | 0.591 | 0.317 | 0.594 |
| uretken_zarf_payi | 0.45 | 0.569 | 0.569 |
| korunmasiz_doviz_stok_mr_usd | 162.9 | 120.0 | 120.0 |
| kapsama | 0.574 | 0.854 | 0.861 |
| net_taban_TL | 28076.0 | 63415.0 | 34384.0 |
| yasam_maliyeti_TL | 48885.0 | 74300 | 39943.0 |
| K_butce_NL_milyar | 0.0 | -24.6 | -2.2 |
| F_ucret_kanali_kumul_milyar | 0.0 | 13647.3 | 834.9 |

## F yükü

Sert senaryoda yaşam maliyeti yüksek kalırken taban agresif artar; işveren payı (45 TL/100) ve geniş prim indirimi F NL yükünü büyütür. Revizede reel maliyet düşüşü marjı destekler, taban zamı küçük (%4/yarıyıl + geri bildirim), işveren payı düşük, KOBİ desteği dar, memur makası K′ kanalına yazılır → kümülatif F ücret kanalı sert: 13647.3 milyar vs revize: 834.9 milyar (senaryo birimi).

## Duyarlılık (yalnız revize; yaşam reel düşüş)

- `0.03`: kapsama 0.818, NFP_F -47202.3, F ücret kanalı küm. 834.9 milyar
- `0.04`: kapsama 0.861, NFP_F -46628.0, F ücret kanalı küm. 834.9 milyar
- `0.05`: kapsama 0.897, NFP_F -46026.6, F ücret kanalı küm. 809.7 milyar

## Ne denmez

- Politika önerisi veya uygulama vaadi değildir.
- Kira/gıda/enerji kanalları ayrıştırılmadı; tek reel düşüş parametresi.
