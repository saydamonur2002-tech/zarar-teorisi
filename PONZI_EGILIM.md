# Ponzi fazlası eğilimi

**Ponzi yüzdesi (bu dosyada):** `ponzi_fazlasi_pp` = servis/gelir proxy’sinin **%40 eşiğinin üstünde kalan kısmı** (puan).
Tam oran `borc_servis_orani_Ha`; band: hedge ≤%30, speculative %30–40, ponzi etiketi >%40.

Çalıştır: `python3 ponzi_egilim.py`. Kaynak: `uc_kural_senaryo.csv`, `tek_sistem_kademe.csv`.

## Senaryo özeti (2026-Q4 → 2031-Q4)

| Senaryo | Servis baş → son | Ponzi fazlası (pp) baş → son | Δ | Çeyrek eğim (pp/çeyrek) | Yön |
| --- | --- | --- | ---: | ---: | --- |
| `mevcut` | 0.473 → 0.591 | 7.3 → 19.1 | +11.8 | +0.590 | **artis** |
| `uc_kural_kilitli` | 0.474 → 0.317 | 7.4 → 0.0 | -7.4 | -0.370 | **azalis** |
| `maliyet_ucuz_revize` | 0.475 → 0.594 | 7.5 → 19.4 | +11.9 | +0.595 | **artis** |
| `kademe_mevcut_taban_proxy` | 0.473 → 0.211 | 7.3 → 0.0 | -7.3 | -0.365 | **azalis** |

## Kademe freni proxy (`kademe_mevcut_taban_proxy`)

Donuk taban (28 076 TL) + `tek_sistem_kademe` F4 itiş çarpanı → Ha stok büyümesi `%45` yıllık varsayım × çarpan. **uc_kural’a bağlı değil**; yalnız kademeli etkinin ponzi fazlasını aşağı çekme yönünü gösterir.

- Ponzi fazlası: **7.3 → 0.0 pp** (azalis, eğim -0.365 pp/çeyrek).
- 2027-Q4: servis **44.8%**, ponzi fazlası **4.8 pp**, band `ponzi`.
- 2029-Q4: servis **33.3%**, ponzi fazlası **0.0 pp**, band `speculative`.
- 2031-Q4: servis **21.1%**, ponzi fazlası **0.0 pp**, band `hedge`.

## Okuma

- **`mevcut` / `maliyet_ucuz_revize`:** ponzi fazlası **artış** (+11 pp civarı); servis ~%47 → ~%59 / ~%59.
- **`uc_kural_kilitli`:** ponzi fazlası **sıfıra iner** (2031-Q4 servis %31,8 → speculative/hedge sınırında); eğim **−0,12 pp/çeyrek** (2026–2031).
- **Kademe proxy (mevcut × birikimli itiş oranı):** ponzi fazlası mevcuta göre **daha yavaş artar** (eğim daha düşük); taban donukken tek başına sıfıra inmez — **azalış eğilimi** ancak `uc_kural_kilitli` ile gelir.

## Ne denmez

- “Ponzi yüzdesi ölçüldü” denmez; Ha ortalaması bilinmiyor (`MINSKY_GUNCEL_KARSILASTIRMA.md`).
- Kademe satırı hane borcunu otomatik düşürmez; F4 çarpanı → Ha büyüme **varsayımı**.

