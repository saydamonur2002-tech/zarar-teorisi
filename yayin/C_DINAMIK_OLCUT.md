# C senaryosu: dinamik ölçüt

**Etiket: olasilik_olculmedi_dinamik_olcut.** merkez_sizinti_orani = 12a yatırım geliri gideri / 12a mal ihracatı (EVDS ödemeler dengesi)

- Varsayım: Senaryo sürüklenmesi d_s = ln(merkez_sizinti_carpan_s)/T (T=10 yıl); karşı-olgusal trend = baz yıl öncesi Ara→Ara ortalaması.
- Prior (A/B/C): {'A': 0.22, 'B': 0.18, 'C': 0.6} → **posterior: {'A': 0.22, 'B': 0.18, 'C': 0.6}**; güncelleme: yok (olcum_baslamadi: bilinmiyor sifir degildir).
- Ölçüm penceresi: baz 2026, ilk güncelleme 2027-12 verisi; son gözlem ayı 2026-08.
- Karşı-olgusal trend: μ = +0.045/yıl, σ = 0.177 (n=10).
- Senaryo sürüklenmesi (yıllık log): {'A': 0.0, 'B': 0.014, 'C': -0.0105}.

## Güç analizi: bu gösterge C'yi ayırt edebilir mi?

| Çift | Fark (yıllık log) | SPRT %95 için gerekli yıl |
| --- | ---: | ---: |
| C vs A | 0.0105 | 1,660 |
| C vs B | 0.0245 | 307 |
| A vs B | 0.014 | 943 |

**Ayırt edebilir (≤ 10 yıl): False.** C için en kısa ayrım 307 yıl.

Monte Carlo (4000 koşu, 10 yıl, gerçek senaryo → P(C) son):

| Gerçek senaryo | E[P(C)] | p10–p90 | P(P(C)>0,8) | P(P(C)<0,4) |
| --- | ---: | --- | ---: | ---: |
| A | 0.595 | 0.501–0.683 | 0.0 | 0.005 |
| B | 0.578 | 0.48–0.669 | 0.0 | 0.011 |
| C | 0.609 | 0.518–0.697 | 0.0 | 0.004 |

- Karar eşiği P(C) ≈ 0.561; posterior − eşik = 0.039.

## Model uyarıları (gözlemden)

- **Karşı-olgusal trend yok:** r(2023 sonu) 0.0749 → r(2025 sonu) 0.1204 (×1.607); senaryoların iki yıllık sürüklenmesi en çok ±0.028. Hiçbir senaryo bu hareketi taşımıyor.
- **Çapa uyumsuzluğu:** kalibrasyon 2024 yatırım geliri gideri = 18,841 mn $; EVDS aynı yıl 26,483 (×1.406), bir önceki yıl 18,793. Uyumsuz: True.

## Diğer kapı adayları

| Kapı | Kaynak | Durum |
| --- | --- | --- |
| merkez_sizinti_surukleme | EVDS TP.ODEAYRSUNUM6.Q76 / Q5 | olculebilir |
| dis_kisit (borç çevirme oranı) | EVDS bie_oderoll (TP.ODEROLL.K1-K4) | veri_var_esleme_yok |
| etki_erozyonu (bölge ihracat payı) | TİM / bolge_havza_ticaret.json (EVDS dışı) | kaynak_dis |
| bag_modu_kullanim | — | olculmedi |
