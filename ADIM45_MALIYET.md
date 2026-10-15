# Adım 4.5: plasebo kontrolü ve yürütme maliyeti

Çalıştır: `python3 adim45_maliyet.py`. Çıktı: `adim45_maliyet.csv`. Adım 4.5'in tanımı `ADIM45_BIRIM.md`'dedir (yeni fiat TL, λ=1 parite, 2030-Q1..Q4); bu dosya o tanıma yalnız plasebo kontrolü ve yürütme maliyeti ekler.

## Tanım (repodan)

- Yeni lira altın ya da döviz üzerinde alacak değildir; dolara çevrilerek ödenmez. λ = 1 paritedir (varsayım). 2005'teki sıfır atma o adımda yoktur.
- TL_yeni = TL_eski · (1 + u·(λ−1)); kur_yeni = λ · kur_eski; USD stoku ve faiz oranları durur; ΣNL = 0; `silinen` boş.
- Sabit çapa: `bes_yil_senaryo.csv` içinde USD/TRY taban satırı tüm yıllarda 49,1274 (TP.DK.USD.A.YTL, 2026-10). λ=1 iken kur_yeni = 49,1274.
- Pencere: 2030-Q1..Q4, u = 0,25 / 0,50 / 0,75 / 1,0. TL para stoku (2026-Q1 ölçüm): 16,472.8 milyar TL (TCMB nakit 898.3 + yurt içi TL mevduat 15,574.5).

## Plasebo kontrolü

TL para bileşenlerinin payları, repodaki `olcek` ile çevrilmiş stoklardan hesaplanır; kur λ ile ölçeklenir, USD stoku ve faiz çarpanı 1 kalır.

| λ | max pay farkı | TL para (yeni) | kur_yeni | USD stok, faiz |
| --- | ---: | ---: | ---: | --- |
| parite (repo, λ=1) | 0.0e+00 | 1.647e+04 | 49.13 | ×1, ×1 |
| örnek: λ=0,001 | 1.1e-16 | 16.47 | 0.04913 | ×1, ×1 |
| örnek: λ=1e-6 (2005 türü) | 0.0e+00 | 0.01647 | 4.913e-05 | ×1, ×1 |

Pay farkı sıfır düzeyindedir: λ ne olursa olsun TL bileşenlerin payları aynı kalır. Bu **aritmetik gereğidir**; modelde para yanılsaması ve yuvarlama enflasyonu yoktur. λ ≠ 1 satırları repoda ölçülmedi; yalnız kimliğin λ'dan bağımsız olduğunu göstermek için örnektir.

## Yürütme maliyeti (milyar TL, tek sefer)

- **A. Basım + yazılım: 0.59 – 5.40.** Banknot basımı ≈ 10 milyon $ (2004 sıfır atma tahmini; 'ek maliyet değil' denmişti) × 49,1274 = 0.49; yazılım kurum başına 20–100 bin $, kurum sayısı 100–1.000 (varsayım): 0.10 – 4.91. Yeni birim paritede bile yeni banknot gerektiği varsayılır.
- **B. Tam yeni birim, üst referans: 189.7 – 632.4.** GSYH 2025 (63,240.5 milyar TL, `tavan_akis.csv`) × %0,3–1,0 (Avro bölgesine girenlerde bildirilen aralık, ikincil kaynak).
- **Pencereye dağılım (A üst ucu):** 2030-Q1 1.35, 2030-Q2 1.35, 2030-Q3 1.35, 2030-Q4 1.35 (Δu ile eşit, varsayım).

Fayda sıfır (plasebo), maliyet pozitif. Adım 4 ve 5 maliyetleriyle toplanmaz (bu tek sefer, öteki adımlar akış ve stok).

## Ne denmez

- 'Yeni birim bir şey değiştirmez' denmez; model değiştirmediğini varsayar, sınamaz.
- 'Geçiş maliyeti ölçüldü' denmez; A, 2004 haber tahmini ve kurum sayısı varsayımı; B ikincil aktarım.
- 'Altı sıfır atıldı' denmez (`ADIM45_BIRIM.md`): λ ölçülmedi, parite 1'dir.
- Yuvarlama, para yanılsaması ve fiyat belirleme alışkanlıkları modellenmedi.
