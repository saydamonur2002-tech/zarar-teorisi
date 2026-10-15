# Beş adımın maliyeti ve yürütme maliyeti, adım adım

Çalıştır: `python3 bes_adim_maliyet.py`. Çıktı: `bes_adim_maliyet.csv`. Maliyet satırları adım 4 ve 5'in kendi koşularındaki bantlardan; yürütme satırları `yurutme_maliyet.py` modelinden. Tüm sayılar varsayım bandı; ölçüm değil.

Yürütme maliyeti = tespit + tahsil + idari maliyet. Model (`yurutme_maliyet.py`): yürütme = program akışı × ρ. Program akışı: adım 1'de ortak stok, adım 2'de mahsupla silinen, adım 3'te yıllık duran faiz, adım 4'te prim toplamı, adım 5'te Ho→Ha transferi; adım 1 (ortak stok) ve 2 (mahsupla silinen) için stok, yalnız alt ρ ile üst sınır; adım 3 (duran faiz) için yıllık akış. ρ bandı varsayım: %0,4 / %9 / %25 (pilot payı) / %29; alt, orta ve üst uçlar Grosh'a atfedilen hedefleme idaresi aralığı (ikincil kaynak, doğrulanmadı), %25 `hekis_model` pilot payı (karar). Bileşenlere (tespit/tahsil/idari) ayrılmadı: yalnız toplam.

## Adım 1: stok

- **maliyet**: `yok`. Adım 1 stok; maliyet satırı yok.
- **yürütme ρ=0.4% (üst sınır): ortak stok 20,363.4 × ρ**: 81.5 – 81.5 milyar TL (tek sefer) (`modellendi_ust_sinir`). Silinen tutar boş: ortak stok silinebilecek en çok. ρ ≥ %9 uygulanmaz: 1,833-5,905 milyar TL gerçekçi değil.

## Adım 2: temerrüt ve ücret

- **maliyet**: `yok`. Temerrüt 0, parametre; maliyet satırı yok.
- **yürütme ρ=0.4% (üst sınır): silinen 14,602.3 × ρ**: 58.4 – 58.4 milyar TL (tek sefer) (`modellendi_ust_sinir`). Mahsupla silinen (Faz 2 düğümlü ağ; kenarlar varsayım, üst sınır). ρ ≥ %9 uygulanmaz: 1,314-4,235 milyar TL gerçekçi değil.

## Adım 3: faiz durma

- **maliyet**: `yok`. Kredi ihtiyacı 0; faizin durması modellenmedi.
- **yürütme ρ=0.4% (alt), κ=0.25: duran faiz 1,207.6 × ρ**: 4.8 – 4.8 milyar TL/yıl (2029) (`modellendi_band`). κ varsayım; r_t ileri sabit (Faz 3).
- **yürütme ρ=9% (orta), κ=0.25: duran faiz 1,207.6 × ρ**: 108.7 – 108.7 milyar TL/yıl (2029) (`modellendi_band`).
- **yürütme ρ=25% (pilot payı), κ=0.25: duran faiz 1,207.6 × ρ**: 301.9 – 301.9 milyar TL/yıl (2029) (`modellendi_band`).
- **yürütme ρ=29% (üst), κ=0.25: duran faiz 1,207.6 × ρ**: 350.2 – 350.2 milyar TL/yıl (2029) (`modellendi_band`).
- **yürütme ρ=0.4% (alt), κ=0.5: duran faiz 2,415.6 × ρ**: 9.7 – 9.7 milyar TL/yıl (2029) (`modellendi_band`).
- **yürütme ρ=9% (orta), κ=0.5: duran faiz 2,415.6 × ρ**: 217.4 – 217.4 milyar TL/yıl (2029) (`modellendi_band`).
- **yürütme ρ=25% (pilot payı), κ=0.5: duran faiz 2,415.6 × ρ**: 603.9 – 603.9 milyar TL/yıl (2029) (`modellendi_band`).
- **yürütme ρ=29% (üst), κ=0.5: duran faiz 2,415.6 × ρ**: 700.5 – 700.5 milyar TL/yıl (2029) (`modellendi_band`).
- **yürütme ρ=0.4% (alt), κ=1.0: duran faiz 4,830.8 × ρ**: 19.3 – 19.3 milyar TL/yıl (2029) (`modellendi_band`).
- **yürütme ρ=9% (orta), κ=1.0: duran faiz 4,830.8 × ρ**: 434.8 – 434.8 milyar TL/yıl (2029) (`modellendi_band`).
- **yürütme ρ=25% (pilot payı), κ=1.0: duran faiz 4,830.8 × ρ**: 1207.7 – 1207.7 milyar TL/yıl (2029) (`modellendi_band`).
- **yürütme ρ=29% (üst), κ=1.0: duran faiz 4,830.8 × ρ**: 1400.9 – 1400.9 milyar TL/yıl (2029) (`modellendi_band`).

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

- 'Yürütme maliyeti ölçüldü' denmez; ρ bandı varsayım, program akışı bant. Adım 1 ve 2 stok mahsubu: yalnız alt ρ, üst sınır; bu oran stok temizliği için bile iyimser olabilir.
- ρ'nun dayanağı ikincil kaynak (Grosh'a atfedilen %0,4-29); adım 4'te (mevduat senedi) daha da zayıf.
- Adım 4 ve 5 maliyetleri toplanmaz: biri prim ve kredi daralması, öteki hane içi aktarım.
- Bantlar güven aralığı değil; varsayım aralığının uçları.
