# Beş adımın maliyeti ve yürütme maliyeti, adım adım

Çalıştır: `python3 bes_adim_maliyet.py`. Çıktı: `bes_adim_maliyet.csv`. Maliyet satırları adım 4 ve 5'in kendi koşularındaki bantlardan; yürütme satırları `yurutme_maliyet.py` modelinden. Tüm sayılar varsayım bandı; ölçüm değil.

Yürütme maliyeti = tespit + tahsil + idari maliyet. Model (`yurutme_maliyet.py`): yürütme = program akışı × ρ. Program akışı: adım 5'te Ho→Ha transferi, adım 4'te prim toplamı; adım 1-3'te yürütülen akış yok (0, kurgu). ρ bandı varsayım: %0,4 / %9 / %25 (pilot payı) / %29; alt, orta ve üst uçlar Grosh'a atfedilen hedefleme idaresi aralığı (ikincil kaynak, doğrulanmadı), %25 `hekis_model` pilot payı (karar). Bileşenlere (tespit/tahsil/idari) ayrılmadı: yalnız toplam.

## Adım 1: stok

- **maliyet**: `yok`. Adım 1 stok; maliyet satırı yok.
- **yürütme**: 0 – 0 milyar TL (`akis_yok`). Yürütülen akış yok: 0 kurgu gereği (maliyet yok demek değil).

## Adım 2: temerrüt ve ücret

- **maliyet**: `yok`. Temerrüt 0, parametre; maliyet satırı yok.
- **yürütme**: 0 – 0 milyar TL (`akis_yok`). Yürütülen akış yok: 0 kurgu gereği.

## Adım 3: faiz durma

- **maliyet**: `yok`. Kredi ihtiyacı 0; faizin durması modellenmedi.
- **yürütme**: 0 – 0 milyar TL (`akis_yok`). Yürütülen akış yok: 0 kurgu gereği.

## Adım 4: adres yönlendirme (senet)

- **maliyet: prim toplamı 2029-2031**: 77.5 – 1058.9 milyar TL (`band_varsayim`). 12 senaryo; orta (θ 0,25 χ 0,5 π 0,05) 529.4. Endeks bacağı hesaplanmadı: alt sınır olabilir.
- **maliyet: kredi daralması (tepe, yıllık)**: 154.9 – 774.5 milyar TL/yıl (`band_varsayim`). Orta 387.2. Banka mevduat kaybı × 0,08.
- **yürütme ρ=0.4% (alt)**: 0.3 – 4.2 milyar TL (2029-31) (`modellendi_band`). Prim toplamı × ρ. ρ dayanağı zayıf: hedeflenmiş transfer idaresi aralığı senet ihracına taşındı.
- **yürütme ρ=9% (orta)**: 7.0 – 95.3 milyar TL (2029-31) (`modellendi_band`). Orta senaryo prim 529.4 × ρ = 47.6.
- **yürütme ρ=25% (pilot payı)**: 19.4 – 264.7 milyar TL (2029-31) (`modellendi_band`). hekis_model pilot SAFETY=1,25 (karar).
- **yürütme ρ=29% (üst)**: 22.5 – 307.1 milyar TL (2029-31) (`modellendi_band`).

## Adım 5: kira

- **maliyet: Ho→Ha transferi, kapsama %20**: 51.6 – 160.2 milyar TL/yıl (`band_varsayim`). H içi aktarım; H toplam NL 0.
- **maliyet: Ho→Ha transferi, kapsama %50**: 129.1 – 400.6 milyar TL/yıl (`band_varsayim`).
- **maliyet: Ho→Ha transferi, kapsama %100**: 258.2 – 801.1 milyar TL/yıl (`band_varsayim`).
- **yürütme ρ=0.4% (alt), kapsama %20**: 0.2 – 0.6 milyar TL/yıl (`modellendi_band`). Transfer × ρ.
- **yürütme ρ=9% (orta), kapsama %20**: 4.6 – 14.4 milyar TL/yıl (`modellendi_band`).
- **yürütme ρ=25% (pilot payı), kapsama %20**: 12.9 – 40.0 milyar TL/yıl (`modellendi_band`).
- **yürütme ρ=29% (üst), kapsama %20**: 15.0 – 46.5 milyar TL/yıl (`modellendi_band`).
- **yürütme ρ=0.4% (alt), kapsama %50**: 0.5 – 1.6 milyar TL/yıl (`modellendi_band`).
- **yürütme ρ=9% (orta), kapsama %50**: 11.6 – 36.1 milyar TL/yıl (`modellendi_band`).
- **yürütme ρ=25% (pilot payı), kapsama %50**: 32.3 – 100.2 milyar TL/yıl (`modellendi_band`).
- **yürütme ρ=29% (üst), kapsama %50**: 37.4 – 116.2 milyar TL/yıl (`modellendi_band`).
- **yürütme ρ=0.4% (alt), kapsama %100**: 1.0 – 3.2 milyar TL/yıl (`modellendi_band`).
- **yürütme ρ=9% (orta), kapsama %100**: 23.2 – 72.1 milyar TL/yıl (`modellendi_band`).
- **yürütme ρ=25% (pilot payı), kapsama %100**: 64.5 – 200.3 milyar TL/yıl (`modellendi_band`).
- **yürütme ρ=29% (üst), kapsama %100**: 74.9 – 232.3 milyar TL/yıl (`modellendi_band`).

## Ne denmez

- 'Yürütme maliyeti ölçüldü' denmez; ρ bandı varsayım, program akışı bant. Adım 1-3'te 0, 'maliyet yok' değil 'yürütülen akış yok'.
- ρ'nun dayanağı ikincil kaynak (Grosh'a atfedilen %0,4-29); adım 4'te (mevduat senedi) daha da zayıf.
- Adım 4 ve 5 maliyetleri toplanmaz: biri prim ve kredi daralması, öteki hane içi aktarım.
- Bantlar güven aralığı değil; varsayım aralığının uçları.
