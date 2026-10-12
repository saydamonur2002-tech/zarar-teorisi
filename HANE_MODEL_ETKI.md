# Hane etkisi — model çerçevesi

Ölçüm ile senaryo aynı tabloda **eşitlenmez**. Ha = asgari ücretli proxy (`uc_kural` servis oranı); Hm/Ho = `hane_alt` (2026-Q1 panel). Çift kayıt: **borçlu defterinde borç nominal kalır**.

Çalıştır: `python3 hane_model_etki.py`.

## 2031-Q4 senaryo karşılaştırması (hane kanalları)

| Kanal | `mevcut` | `uc_kural_kilitli` | `maliyet_ucuz_revize` |
| --- | --- | --- | --- |
| Net taban (TL/ay) | 28,076.0 | 63,415.0 | 34,384.0 |
| Kapsama | 0.574 | 0.854 | 0.861 |
| Ha servis/gelir | 0.591 (ponzi) | 0.318 (speculative) | 0.586 (ponzi) |
| Ponzi fazlası (pp) | 19.100 | 0.000 | 18.600 |
| NFP_H (milyar TL) | 26,182.2 | 31,553.6 | 26,941.2 |
| Korunmasız USD stok (mr) | 162.9 | 120.0 | 120.0 |
| Limit dondur (H kart/tüketici) | 0 | 1 | 1 |

## Eğilim (2026-Q4 → 2031-Q4, senaryo)

| Senaryo | Taban Δ | Servis Δ | Ponzi fazlası Δ (pp) | NFP_H Δ |
| --- | ---: | ---: | ---: | ---: |
| `mevcut` | +0 TL | +0.118 | +11.8 | +4581.8 |
| `uc_kural_kilitli` | +35339 TL | -0.157 | -7.5 | +9947.3 |
| `maliyet_ucuz_revize` | +6308 TL | +0.111 | +11.1 | +5334.9 |

## Alt hazne (2026-Q1, varsayım — `hane_alt`)

- **Ha:** NFP **−1,63 trilyon TL** (borç > varlık payı); taşıma kapasitesi **~0,92 trilyon TL** (%30 taksit/gelir, 36 ay, faiz ~%63).
- **Hm / Ho:** pozitif NFP; borç yükü modelde Ha’da yoğunlaştırılır (`D_A_BASE` %40).
- Gözlenen stres: takipteki tüketici **~0,37 trilyon TL**; geniş tanım üst band **~2,47 trilyon TL**.
- İma edilen Ha borç payı üst sınırı (stres): **%17–44**; taban %40 **üst banda yakın**.

## Ölçüm çelişkisi (modele girmez ama hane okuması)

- **`hane_taksit` (2024):** kart hariç taksit/gelir **~%4,0** — düşük görünür.
- **`uc_kural` Ha proxy (2026):** servis/gelir **~%47** — agregat, kart dahil varsayım, sabit taban.
- **EVDS 13 ay (2026-09):** kart **+45,9%**, tüketici **+43,3%** stok büyümesi → `mevcut` senaryoda servis **artış eğilimi**.

## Tek sistem kademeleri (hane)

- **K1 mahsup:** doğrudan hane defteri yok; dolay **F itiş freni** → `kademe_mevcut_taban_proxy` ponzi fazlası **mevcuta göre daha yavaş** (bkz. `PONZI_EGILIM.md`).
- **K2 stok tavan:** firma kimden-kime; **hane stokuna yazılmaz**.
- **K3 mevduat adresi:** tasarruf yönlendirme; hane **YP/vadeli stok** ölçümü tek nokta, dağıtım modellenmedi.

## Döviz (hane)

- **`mevcut`:** korunmasız USD stok **121,8 → 162,9 mr USD** (senaryo; kur/kanallar kabaca `R_H`).
- **Kilitli/revize:** **120 mr USD** tavan; hane reel kur şoku proxy’si **sınırlı**.
- Brüt dış borç **ölçümde artıyor** (`DOVIZ_EGILIM.md`) — hane FX mevduatı ayrı nesne.

## Ne denmez

- “Kademe hane borcunu sildi” denmez.
- “NFP_H milyar = hane geliri” denmez (birim ve kapsam farklı).
- Ponzi etiketi = resmi temerrüt oranı değildir.

