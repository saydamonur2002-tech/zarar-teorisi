# P(C) — kapılarla yeniden kurulum

**Etiket:** `olasilik_olculmedi_kapi_iskeleti`

- Prior: tekdüze {'A': 0.3333, 'B': 0.3333, 'C': 0.3333} (eski el ataması {'A': 0.22, 'B': 0.18, 'C': 0.6} dayanaksızdı).
- Bugünkü P: **{'A': 0.333, 'B': 0.333, 'C': 0.333}**. ölçüm başlamadı: P(C) = prior (1/3). 0,60 hiçbir ölçüme dayanmıyordu.

## Kapılar

| Kapı | Kaynak | Olabilirlik | Durum |
| --- | --- | --- | --- |
| K1 merkez sızıntı sürüklenmesi | EVDS TP.ODEAYRSUNUM6.Q76/Q5 | gecmisten (kayan 5 yillik log-egim ceyrekleri) | olcum_bekliyor |
| K2 dış kısıt (borç çevirme ≥ %100: bankalar ve diğer sektörler) | EVDS bie_oderoll TP.ODEROLL.K1, K2 (12 ay ort.) | gecmisten (n kucuk, ortusen pencereler) | olcum_bekliyor |
| K3 etki erozyonu (bölge ihracat payı) | TİM; EVDS ülke grubu serisi katalogda yok | turetilmis (etki_erosyon_carpani) ama σ ölçülemez | veri_yok |
| K4 bağ kullanımı | — | tanımsız | olculmedi |

## K2 dış kısıt

- Tarihçe: 12 aylık ort. çevirme ≥ %100 olan pencerelerin payı **0.534** (232 pencere). Bu A için taban oran p0.
- Son: {'donem': '2026-08', 'K1_bankalar': 109.8, 'K2_diger': 175.0, 'acik': True}
- Olabilirlik **geçmişten**: P(açık | rejim) = {'A': 0.2, 'B': 0.75, 'C': 0.5}, geçmiş sayım (açık, toplam) = {'A': [0, 3], 'B': [2, 2], 'C': [1, 2]}. Rejim = kayan 5 yıllık eğimin çeyreği (C ≤ q25, B ≥ q75, A arası). n = 7 örtüşen pencere (etkin ~2 bağımsız): çok zayıf. λ = 0.0 (λ=1: kapı bilgi taşımaz).

| Açık sayısı (3 kontrol noktasından) | P(A) | P(B) | P(C) |
| ---: | ---: | ---: | ---: |
| 0/3 | 0.785 | 0.024 | 0.192 |
| 1/3 | 0.427 | 0.156 | 0.417 |
| 2/3 | 0.108 | 0.472 | 0.42 |
| 3/3 | 0.014 | 0.76 | 0.225 |

### λ duyarlılığı (geçmişe ağırlık; P(C): hiç açık yok → hepsi açık)

| λ | tekdüze prior | eski el ataması prior |
| ---: | --- | --- |
| 0.0 | 0.192 → 0.225 | 0.394 → 0.491 |
| 0.25 | 0.231 → 0.267 | 0.454 → 0.545 |
| 0.5 | 0.274 → 0.305 | 0.514 → 0.586 |
| 0.75 | 0.312 → 0.33 | 0.567 → 0.606 |
| 1.0 | 0.333 → 0.333 | 0.6 → 0.6 |

## Karar bağlantısı

Kapı sonuçlarının uygulanabilirlik kararına çevrilmesi `OLASILIK_DUYARLILIK.md` içinde ('Kapı sonuçları').

## Ne denmez

- 'P(C) = 1/3' bir ölçüm değildir; bilgi yokluğudur. Ölçüm 2027-12'den itibaren başlar.
- K2 olabilirliği 7 örtüşen geçmiş pencereden gelir; çok gürültülü. λ tablosu geçmişe verilen ağırlığın etkisini gösterir.
- K3 ve K4 veri gelene kadar olasılığa girmez; sıfır değil, bilinmiyor.
