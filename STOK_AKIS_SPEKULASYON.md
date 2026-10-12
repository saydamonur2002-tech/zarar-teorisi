# Stok-akış matrisi ve spekülasyona yakın aktörler

**Dönem (EVDS stok/akış):** 2026-Q1. **Ha servis proxy:** 2026-Q4 `mevcut` senaryo girişi.

## Aktör özeti (NFP = varlık − borç, trilyon TL)

| Aktor | NFP_trilyonTL | NL_ceyrek_trilyonTL | R_ceyrek_trilyonTL | spekulasyon_yakinlik_0_1 | minsky_rejim_okuma |
| --- | --- | --- | --- | --- | --- |
| H | 21.395 | 0.278 | 0.908 | 1.2 | ponzi_band |
| Ha | 21.395 | 0.278 | 0.908 | 1.2 | ponzi_band |
| F | -30.108 | -1.417 | -0.981 | 0.678 | speculative |
| K | -6.44 | -1.069 | 0.524 | 0.534 | speculative |
| D | 15.635 | 1.726 | -0.225 | 0.35 | dis_finansman |
| B | -0.481 | 0.481 | -0.227 | 0.0 | aracı_kredi_genislemesi |

## Spekülasyona en yakın (yakinlik ≥ 0,55)

| Aktor | Aktor_ad | spekulasyon_yakinlik_0_1 | minsky_rejim_okuma |
| --- | --- | --- | --- |
| H | Hane (S.14+15) | 1.2 | ponzi_band |
| Ha | Asgari ücretli proxy (Ha) | 1.2 | ponzi_band |
| F | Firmalar (S.11) | 0.678 | speculative |

## Eşikler

- Hane servis/gelir: hedge ≤ **30%**, ponzi etiketi > **40%**
- Firma: finansman/faaliyet kârı ≤0,5 hedge; 0,5–1,0 spekülatif; >1,0 ponzi baskısı
- Kamu: bütçe faiz/harcama payı >%12 spekülatif baskı (fiscal)

## Dosyalar

- `stok_akis_aktor_matrisi.csv` — aktör satırları
- `stok_akis_enstruman_matrisi_2026Q1.csv` — enstrüman × H,F,B,K,D işlem net (bin TL)
- `sfc_islem_akis_matrisi.csv` — tam zaman serisi

Çalıştır: `python3 stok_akis_spekulasyon_matrisi.py`