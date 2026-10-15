# Beş adımın maliyeti ve yürütme maliyeti, adım adım

Çalıştır: `python3 bes_adim_maliyet.py`. Çıktı: `bes_adim_maliyet.csv`. Yeni model değil: adım 4 ve 5'in kendi koşularındaki bantların okunması. Tüm sayılar varsayım bandı; ölçüm değil.

Yürütme maliyeti = tespit + tahsil + idari maliyet. **Hiçbir adımda modellenmedi** (`hekis_model/PILOT.md`: 'tespit, tahsil ve idari maliyet modelde yok'). Repodaki tek referans pilot eşiğindeki %25 pay (bedel/sübvansiyon ≥ 1,25; karar).

## Adım 1: stok

- **maliyet**: `yok`. Adım 1 stok; maliyet satırı yok.
- **yürütme**: `modellenmedi`. Tespit, tahsil, idari maliyet modelde yok.

## Adım 2: temerrüt ve ücret

- **maliyet**: `yok`. Temerrüt 0, parametre; maliyet satırı yok.
- **yürütme**: `modellenmedi`.

## Adım 3: faiz durma

- **maliyet**: `yok`. Kredi ihtiyacı 0; faizin durması modellenmedi.
- **yürütme**: `modellenmedi`.

## Adım 4: adres yönlendirme (senet)

- **maliyet: prim toplamı 2029-2031**: 77.5 – 1058.9 milyar TL (`band_varsayim`). 12 senaryo; orta (θ 0,25 χ 0,5 π 0,05) 529.4. Endeks bacağı hesaplanmadı: alt sınır olabilir.
- **maliyet: kredi daralması (tepe, yıllık)**: 154.9 – 774.5 milyar TL/yıl (`band_varsayim`). Orta 387.2. Banka mevduat kaybı × 0,08.
- **yürütme**: `modellenmedi`. İhraççı K′ varsayım. Prim sübvansiyon olmadığı için pilot payı uygulanmaz.

## Adım 5: kira

- **maliyet: Ho→Ha transferi, kapsama %20**: 51.6 – 160.2 milyar TL/yıl (`band_varsayim`). H içi aktarım; H toplam NL 0.
- **maliyet: Ho→Ha transferi, kapsama %50**: 129.1 – 400.6 milyar TL/yıl (`band_varsayim`).
- **maliyet: Ho→Ha transferi, kapsama %100**: 258.2 – 801.1 milyar TL/yıl (`band_varsayim`).
- **yürütme**: `modellenmedi`. Tespit, tahsil, idari maliyet modelde yok.
- **yürütme: ima edilen ödenek (pilot payı %25 × transfer %20-100)**: 12.9 – 200.3 milyar TL/yıl (`varsayim_pay`). Maliyet tahmini değil; yürütme için ayrılabilecek pay. Gerçek maliyet: tespit/tahsil/idari verisi yok.

## Ne denmez

- 'Yürütme maliyeti hesaplandı' denmez; satırlar `modellenmedi`. Yalnız adım 5'te pilot payına dayanan bir ödenek var (`varsayim_pay`).
- Adım 4 ve 5 maliyetleri toplanmaz: biri prim ve kredi daralması, öteki hane içi aktarım.
- Bantlar güven aralığı değil; varsayım aralığının uçları.
