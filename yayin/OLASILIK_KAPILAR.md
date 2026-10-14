# P(C) — kapılarla yeniden kurulum

**Etiket:** `olasilik_olculmedi_kapi_iskeleti`

- Prior: tekdüze {'A': 0.3333, 'B': 0.3333, 'C': 0.3333} (eski el ataması {'A': 0.22, 'B': 0.18, 'C': 0.6} dayanaksızdı).
- Bugünkü P: **{'A': 0.333, 'B': 0.333, 'C': 0.333}**. ölçüm başlamadı: P(C) = prior (1/3). 0,60 hiçbir ölçüme dayanmıyordu.
- Karar eşiği (skor 62): P(C) ≥ **0.561**.

## Kapılar

| Kapı | Kaynak | Olabilirlik | Durum |
| --- | --- | --- | --- |
| K1 merkez sızıntı sürüklenmesi | EVDS TP.ODEAYRSUNUM6.Q76/Q5 | turetilmis | olcum_bekliyor |
| K2 dış kısıt (borç çevirme ≥ %100: bankalar ve diğer sektörler) | EVDS bie_oderoll TP.ODEROLL.K1, K2 (12 ay ort.) | varsayim | olcum_bekliyor |
| K3 etki erozyonu (bölge ihracat payı) | TİM; EVDS ülke grubu serisi katalogda yok | turetilmis (etki_erosyon_carpani) ama σ ölçülemez | veri_yok |
| K4 bağ kullanımı | — | tanımsız | olculmedi |

## K2 dış kısıt

- Tarihçe: 12 aylık ort. çevirme ≥ %100 olan pencerelerin payı **0.534** (232 pencere). Bu A için taban oran p0.
- Son: {'donem': '2026-08', 'K1_bankalar': 109.8, 'K2_diger': 175.0, 'acik': True}
- Varsayım (tek parametre): p_C = p0 + δ, p_B = p0 − δ, δ = 0.1.

| Açık sayısı (3 kontrol noktasından) | P(A) | P(B) | P(C) | Eşiği geçer | Karar bandı |
| ---: | ---: | ---: | ---: | --- | --- |
| 0/3 | 0.305 | 0.547 | 0.148 | hayır | kisitli_uygulanabilir (skor 57.3, bant dışı kırpıldı) |
| 1/3 | 0.341 | 0.409 | 0.25 | hayır | kisitli_uygulanabilir (skor 57.3, bant dışı kırpıldı) |
| 2/3 | 0.344 | 0.276 | 0.38 | hayır | kisitli_uygulanabilir (skor 59.1) |
| 3/3 | 0.312 | 0.167 | 0.521 | hayır | kisitli_uygulanabilir (skor 60.9) |

### δ duyarlılığı (P(C): hiç açık yok → hepsi açık)

| δ | tekdüze prior | eski el ataması prior |
| ---: | --- | --- |
| 0.0 | 0.333 → 0.333 | 0.6 → 0.6 |
| 0.05 | 0.232 → 0.428 | 0.479 → 0.689 |
| 0.1 | 0.148 → 0.521 | 0.349 → 0.76 |
| 0.15 | 0.086 → 0.605 | 0.227 → 0.815 |
| 0.2 | 0.045 → 0.676 | 0.13 → 0.855 |

## Sonuç

K2 üç kontrol noktasında da açık çıksa P(C) = 0.521; karar eşiği 0.561. Tek kapı eşiği geçirmez: C'yi 'uygulanabilir' yapacak kanıt yok; karar P(C) varsayımıyla değil, kapı kümesiyle verilmeli.

## Ne denmez

- 'P(C) = 1/3' bir ölçüm değildir; bilgi yokluğudur. Ölçüm 2027-12'den itibaren başlar.
- K2 olabilirliği varsayımdır (δ). Tablo bunun ne kadar oynattığını gösterir, doğrulamaz.
- K3 ve K4 veri gelene kadar olasılığa girmez; sıfır değil, bilinmiyor.
