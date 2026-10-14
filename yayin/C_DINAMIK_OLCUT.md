# C senaryosu: dinamik ölçüt

**Etiket: olasilik_olculmedi_dinamik_olcut.** merkez_sizinti_orani = 12a yatırım geliri gideri / 12a mal ihracatı (EVDS ödemeler dengesi)

- Varsayım: Senaryo sürüklenmesi geçmişten: A = medyan, B = q75, C = q25 (r'nin kayan 5 yıllık log-eğimleri, 2015–2025); gözlem g ~ N(d_s, σ), σ = yıllık log değişimin geçmiş std'si. Senaryo = geçmiş rejimleri varsayımı.
- Prior (A/B/C): {'A': 0.3333, 'B': 0.3333, 'C': 0.3333} → **posterior: {'A': 0.3333, 'B': 0.3333, 'C': 0.3333}**; güncelleme: yok (olcum_baslamadi: bilinmiyor sifir degildir).
- Ölçüm penceresi: baz 2026, ilk güncelleme 2027-12 verisi; son gözlem ayı 2026-08.
- Karşı-olgusal trend: μ = +0.000/yıl, σ = 0.177 (n=10).
- Senaryo sürüklenmesi (yıllık log): {'A': -0.0076, 'B': 0.0571, 'C': -0.055}.

## Güç analizi: bu gösterge C'yi ayırt edebilir mi?

| Çift | Fark (yıllık log) | SPRT %95 için gerekli yıl |
| --- | ---: | ---: |
| C vs A | 0.0474 | 82 |
| C vs B | 0.1121 | 15 |
| A vs B | 0.0647 | 44 |

**Ayırt edebilir (≤ 10 yıl): False.** C için en kısa ayrım 15 yıl.

Monte Carlo (4000 koşu, 10 yıl, gerçek senaryo → P(C) son):

| Gerçek senaryo | E[P(C)] | p10–p90 | P(P(C)>0,8) | P(P(C)<0,4) |
| --- | ---: | --- | ---: | ---: |
| A | 0.338 | 0.067–0.645 | 0.018 | 0.624 |
| B | 0.137 | 0.009–0.352 | 0.0 | 0.929 |
| C | 0.526 | 0.213–0.806 | 0.108 | 0.299 |

- Karar eşiği P(C) ≈ None; posterior − eşik = None.

## Model uyarıları (gözlemden)

- **Karşı-olgusal trend yok:** r(2023 sonu) 0.0749 → r(2025 sonu) 0.1204 (×1.607); senaryoların iki yıllık sürüklenmesi en çok ±0.114. Hiçbir senaryo bu hareketi taşımıyor.
- **Çapa uyumsuzluğu:** kalibrasyon 2024 yatırım geliri gideri = 18,841 mn $; EVDS aynı yıl 26,483 (×1.406), bir önceki yıl 18,793. Uyumsuz: True.

## Diğer kapı adayları

| Kapı | Kaynak | Durum |
| --- | --- | --- |
| merkez_sizinti_surukleme | EVDS TP.ODEAYRSUNUM6.Q76 / Q5 | olculebilir |
| dis_kisit (borç çevirme oranı) | EVDS bie_oderoll (TP.ODEROLL.K1-K4) | veri_var_esleme_yok |
| etki_erozyonu (bölge ihracat payı) | TİM / bolge_havza_ticaret.json (EVDS dışı) | kaynak_dis |
| bag_modu_kullanim | — | olculmedi |
