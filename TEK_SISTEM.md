# Tek sistem

Borç akışla ödenir, servet üretime bağlanır.

İki öneri tek sistemdir. 3 Ekim parçası kilitli lira alacağını açar. 4 Ekim parçası açılan paranın adresini söyler. Silme yok. Tasfiye yok.

Kaynak depo: [saydamonur2002-tech/tek-sistem](https://github.com/saydamonur2002-tech/tek-sistem) `c01b60a`.

Bu depodaki parçaları:

- Tam metin: [model/RAPOR.md](model/RAPOR.md)
- Ölçüm tabloları: [model/gercek/](model/gercek/), [model/pasta/](model/pasta/); açıklama [model/OKU.md](model/OKU.md)
- Mahsup modeli (adım 1-3, çalışan kod): [mahsup/](mahsup/) — tek-sistem zip ile bayt bayt aynı
- Ödeme zinciri köprüsü: `python3 odeme_mahsup.py`
- Katman köprüsü (mutabakat + beş adım eşlemesi): `python3 tek_sistem_kopru.py` → [TEK_SISTEM_KOPRU.md](TEK_SISTEM_KOPRU.md), `tek_sistem_kopru.csv`, `tek_sistem_esleme.csv`
- Beş adım sırayla, tek koşu (etiket kapılı; adım 1 stok eski/yeni tavan ayrı): `python3 bes_adim.py` → [BES_ADIM.md](BES_ADIM.md), `adim1_stok.csv` … `adim5.csv`, `bes_adim_sonuc.json` (`kosu`)
- Kapanış, tek test (son satırı test yazar): `python3 test_bes_adim.py` → `kapanis_sonuc.json`, `bes_adim_sonuc.json` `son`; kilitler `senet_kilit.txt`, `kapi_kilit.txt`

## Beş adım

1. Lira alacak ve borç e-fatura üzerinden eşleşir. Kapalı döngü nakit dolaşmadan kapanır.
2. Kalan net borç silinmez. Üstten alta akış planıyla ödenir. Alta inen pay ücret olarak yazılır.
3. Bu akış yeni banka kredisiyle çevrilmez. Eski stokun faizi, stok ödenene kadar durur.
4. Tasarruf dolar ve arsa yerine hedef primli endeksli senede gider. Çıkış, senedi başkasına satmaktır.
5. Konut topluma açılırsa kira, aynı akışın ikinci koludur. Bu kol ölçülmedi.

## Bu depoda hangi adım nerede

| Adım | Katman | Durum |
| ---: | --- | --- |
| 1 | `mahsup_sektor_evds.py` (sektör akış mahsupu), `stok_silim.py` (stok tavanı) | olculdu / test_edilemez |
| 2 | `odeme_mahsup.py` (şart kaldıracı, ücret geçişi) | modellendi, sentetik ağ |
| 3 | `odeme_mahsup.py` (kredi ihtiyacı); EVDS F.4 firma kredi stoku | modellendi / olculdu |
| 4 | EVDS hane-firma vadeli, HPB gerçek kişi YP (senedin adres stokları) | olculdu; senet modellenmedi |
| 5 | — | olculmedi |

Ayrıntı ve sayılar `TEK_SISTEM_KOPRU.md` içinde. Adım 4–5'in HEKİS'teki modeli (hekis-model 6c34a63, `hekis_model/`) `DIGER_REPO_KOPRU.md` içinde; tek-sistem etiketleri orada değişmez. Katman sonuçları birbirine taşınmaz; tek-sistem BDDK kredi sayıları ile EVDS finansal hesap stokları aynı tanım değildir, fark açıklanır, kapatılmaz.

## Sınır

Kart borcunu, döviz sözleşmesini ve Hazine faizini kapatmaz. Enflasyonda tavan birkaç puandır. 20 vaadi verilmez.
