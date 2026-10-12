# Faz 3 — Adım 3: faiz tahakkukunun durması kuralı (SFC transfer)

Çalıştır: `python3 adim3_faiz_durma.py`. Çıktı: `adim3_faiz_durma.csv`, `adim3_faiz_durma_sonuc.json`.

`adim3.csv` yazılmaz; oradaki 'Faizin durması modellenmedi' ve H-A3 kilidi durur. Kural burada, ayrı dosyada.

## Kural

- `D_t = κ·u2_t·S₀; I_t = ψ·(r_t/4)·D_t; F NL += I_t, ödeyen hazne NL −= I_t; ΣNL = 0`
- S₀ = 25,339.8 milyar (F F.4, 2026-Q1, `olculdu`). r_t = TP.KTF17 ticari kredi faizi; son gözlem 2026-09: 53.19%; sonrası sabit (varsayım).
- ψ = 3,143.4 / (0.6038 × 14,527.5) = **0.3584** (`olcum_turevi`). Sektör Bilançoları kapsamı (bilanço veren firmalar) ve döviz kredisi karışımı; EVDS F.4 tüm firmalar. Oran, eşitlik değil.
- κ ∈ [0.25, 0.5, 1.0] varsayım; u2 K2 penceresi 2028-Q1..2028-Q4 doğrusal (tek_sistem_kademe.py).
- SFC: F'nin ödemediği faiz B′'nin almadığı faizdir; ΣNL değişmez. B′ yerine K′ üstlenirse sütun değişir, toplam değişmez. İkisi toplanmaz.

## Yıllık duran faiz (etkin, milyar TL) ve 2024 finansman giderine oranı

| κ | 2027 | 2028 | 2029 | 2030 | 2031 |
| --- | --- | --- | --- | --- | --- |
| 0.25 | 0.0 (0.00×) | 754.8 (0.24×) | 1,207.7 (0.38×) | 1,207.7 (0.38×) | 1,207.7 (0.38×) |
| 0.5 | 0.0 (0.00×) | 1,509.6 (0.48×) | 2,415.4 (0.77×) | 2,415.4 (0.77×) | 2,415.4 (0.77×) |
| 1.0 | 0.0 (0.00×) | 3,019.3 (0.96×) | 4,830.8 (1.54×) | 4,830.8 (1.54×) | 4,830.8 (1.54×) |

## Ne denmez

- 'Faiz durdu, firma rahatladı' denmez; κ varsayım, r_t ileri sabit, ψ 2024 kapsamından.
- Yıllık duran faiz 2024 finansman giderine eşitlenmez; oran karşılaştırma içindir.
- Bu sayılar `adim3.csv`'ye, `uc_kural_senaryo.csv`'ye taşınmaz.
