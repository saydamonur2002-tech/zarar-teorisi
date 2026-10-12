# Faz 4 — Adım 4: adres stoklarını ihraç / prim / çıkış ile bağlama (band)

Çalıştır: `python3 adim4_adres_yonlendirme.py`. Çıktı: `adim4_adres_yonlendirme.csv`, `adim4_adres_yonlendirme_sonuc.json`.

`adim4.csv` senet satırı `modellenmedi` kalır; `senet_kilit.txt` dokunulmaz. Burada kilidin dışında, üç ölçülmüş adres stoku üzerinde band kurulur: hiçbir sayı o satıra taşınmaz.

## Adresler (ölçüm)

| nesne | hazne | milyar TL | dönem |
| --- | --- | --- | --- |
| hane vadeli mevduat (VF.2 ZP8) | H | 8,322.4 | 2026-Q1 |
| firma vadeli mevduat (VF.2 ZP8) | F | 4,400.1 | 2026-Q1 |
| gerçek kişi YP mevduat (HPB tablo 2) | H | 6,639.4 | 2026-Q1 |
| TOPLAM | | 19,361.9 | |

## Kural (varsayım)

- İhraç_t = θ · 19,361.9 · Δu3_t; u3 K3 penceresi 2029-Q1..2029-Q4. θ ∈ [0.1, 0.25, 0.5].
- Vade 8 çeyrek; vadede (1−χ) mevduata döner, χ yenilenir; χ ∈ [0.0, 0.5].
- Prim π ∈ [0.02, 0.05] yıllık, stok üzerinden. Endeks (hedef) bacağı hesaplanmadı: hedef patikası depoda yok.
- İhraççı K′ (varsayım). SFC: tutucu VF.2↓ VF.3↑ (NFP 0); B′ F.2↓ rezerv↓ (0); K′ F.3↑ TCMB hesabı↑ (0); prim K′→tutucu transfer (ΣNL 0).
- Kredi itişi: B′ mevduat kaybı × 0.08 (tek_sistem_kademe sabiti) yıllık kredi daralması.

## Senaryo özeti (milyar TL)

| θ | χ | π | toplam ihraç | toplam çıkış | tepe stok | son stok 2031-Q4 | prim 2030 | prim 2031 | prim/duran faiz κ=0,5 (2031) | kredi itki azalt (tepe, yıllık) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.1 | 0.0 | 0.02 | 1,936.0 | 1,936.0 | 1,936.2 | -0.0 | 38.8 | 24.2 | 0.01 | 154.9 |
| 0.1 | 0.0 | 0.05 | 1,936.0 | 1,936.0 | 1,936.2 | -0.0 | 96.8 | 60.6 | 0.025 | 154.9 |
| 0.1 | 0.5 | 0.02 | 1,936.0 | 968.0 | 1,936.2 | 968.1 | 38.8 | 31.6 | 0.013 | 154.9 |
| 0.1 | 0.5 | 0.05 | 1,936.0 | 968.0 | 1,936.2 | 968.1 | 96.8 | 78.7 | 0.033 | 154.9 |
| 0.25 | 0.0 | 0.02 | 4,840.4 | 4,840.4 | 4,840.5 | 0.0 | 96.8 | 60.6 | 0.025 | 387.2 |
| 0.25 | 0.0 | 0.05 | 4,840.4 | 4,840.4 | 4,840.5 | 0.0 | 242.0 | 151.3 | 0.063 | 387.2 |
| 0.25 | 0.5 | 0.02 | 4,840.4 | 2,420.4 | 4,840.5 | 2,420.2 | 96.8 | 78.7 | 0.033 | 387.2 |
| 0.25 | 0.5 | 0.05 | 4,840.4 | 2,420.4 | 4,840.5 | 2,420.2 | 242.0 | 196.6 | 0.081 | 387.2 |
| 0.5 | 0.0 | 0.02 | 9,680.8 | 9,680.8 | 9,681.0 | 0.0 | 193.6 | 121.0 | 0.05 | 774.5 |
| 0.5 | 0.0 | 0.05 | 9,680.8 | 9,680.8 | 9,681.0 | 0.0 | 484.0 | 302.6 | 0.125 | 774.5 |
| 0.5 | 0.5 | 0.02 | 9,680.8 | 4,840.4 | 9,681.0 | 4,840.5 | 193.6 | 157.4 | 0.065 | 774.5 |
| 0.5 | 0.5 | 0.05 | 9,680.8 | 4,840.4 | 9,681.0 | 4,840.5 | 484.0 | 393.3 | 0.163 | 774.5 |

## Ne denmez

- 'Senet modellendi' denmez; `adim4.csv` satırı `modellenmedi`, kilit duruyor. Burası band: θ, χ, π, vade, ihraççı varsayım.
- HEKİS senedi (TÜFE endeksli, reel kupon 0) ile eşitlenmez; endeks bacağı burada hesaplanmadı.
- Prim / duran faiz oranı karşılaştırmadır; Faz 3 κ varsayımına bağlıdır, iki sayı toplanmaz.
