# Tek sistem köprüsü

Kaynak: [https://github.com/saydamonur2002-tech/tek-sistem](https://github.com/saydamonur2002-tech/tek-sistem) `c01b60a`; tablolar `model/gercek`, `model/pasta`, metin `model/RAPOR.md`. Mahsup kodu `mahsup/mahsuplasma` ile bayt bayt aynı (önceden eklendi).

Çalıştır: `python3 tek_sistem_kopru.py`. Çıktı: `tek_sistem_kopru.csv` (mutabakat), `tek_sistem_esleme.csv` (beş adım), `tek_sistem_kopru_sonuc.json`.

Kural: katman sonuçları birbirine taşınmaz. Tek-sistem sayısı BDDK banka kredisidir; EVDS sayısı finansal hesap stokudur (tüm borç verenler, yurt dışı dahil). Fark açıklanır, kapatılmaz.

## 1. Mutabakat: kredi stoku (milyar TL, dönem sonu)

| Dönem | Kalem | Tek-sistem | EVDS | EVDS anahtar | Fark | EVDS/tek |
| --- | --- | ---: | ---: | --- | ---: | ---: |
| 2022-Q4 | Ticari stok | 6,038.0 | 7,808.6 | F_F4_yuk | 1,770.6 | 1.293 |
| 2022-Q4 | Bireysel stok | 1,530.0 | 1,613.8 | H_F4_yuk | 83.8 | 1.055 |
| 2022-Q4 | Toplam kredi stoku | 7,568.0 | 7,609.5 | B_VF4_var | 41.5 | 1.005 |
| 2022-Q4 | Toplam kredi stoku | 7,568.0 | 8,458.2 | S12_VF4_var | 890.2 | 1.118 |
| 2023-Q4 | Ticari stok | 8,962.0 | 11,920.3 | F_F4_yuk | 2,958.3 | 1.330 |
| 2023-Q4 | Bireysel stok | 2,669.0 | 2,854.4 | H_F4_yuk | 185.4 | 1.069 |
| 2023-Q4 | Toplam kredi stoku | 11,630.0 | 11,791.6 | B_VF4_var | 161.6 | 1.014 |
| 2023-Q4 | Toplam kredi stoku | 11,630.0 | 12,720.4 | S12_VF4_var | 1,090.4 | 1.094 |
| 2024-Q4 | Ticari stok | 12,094.0 | 15,891.5 | F_F4_yuk | 3,797.5 | 1.314 |
| 2024-Q4 | Bireysel stok | 3,807.0 | 4,167.9 | H_F4_yuk | 360.9 | 1.095 |
| 2024-Q4 | Toplam kredi stoku | 15,901.0 | 16,514.8 | B_VF4_var | 613.8 | 1.039 |
| 2024-Q4 | Toplam kredi stoku | 15,901.0 | 19,068.3 | S12_VF4_var | 3,167.3 | 1.199 |
| 2025-Q4 | Ticari stok | 17,302.0 | 23,519.9 | F_F4_yuk | 6,217.9 | 1.359 |
| 2025-Q4 | Bireysel stok | 5,575.0 | 6,237.4 | H_F4_yuk | 662.4 | 1.119 |
| 2025-Q4 | Toplam kredi stoku | 23,128.0 | 24,039.8 | B_VF4_var | 911.8 | 1.039 |
| 2025-Q4 | Toplam kredi stoku | 23,128.0 | 27,742.7 | S12_VF4_var | 4,614.7 | 1.200 |

EVDS 2026-Q1 (tek-sistem henüz yok): F_F4_yuk 25,339.8; H_F4_yuk 6,755.1; B_VF4_var 26,024.0; S12_VF4_var 31,213.9

Ölçüm: firma F.4 / BDDK ticari 1,29–1,36; hane F.4 / BDDK bireysel 1,06–1,12; mevduat bankaları VF.4 / BDDK toplam 1,00–1,04 (dört yıl sonu). Tanım: F.4 yükümlülüğü borç vereni ayırmaz (banka, banka dışı finansal, yurt dışı); BDDK sayısı yalnız banka kredisidir. Farkın hangi borç verene ait olduğu bu seriden ayrılmaz; ayrılmadı.

## 2. Net akış ↔ stok farkı (milyar TL)

| Yıl | Kalem | Tek-sistem net akış | EVDS Q4−Q4 stok farkı | Fark | EVDS/tek |
| --- | --- | ---: | ---: | ---: | ---: |
| 2023 | Net akis ticari | 2,924.0 | 4,111.7 | 1,187.7 | 1.406 |
| 2023 | Net akis bireysel | 1,139.0 | 1,240.6 | 101.6 | 1.089 |
| 2023 | Net akis toplam | 4,062.0 | 4,182.1 | 120.1 | 1.030 |
| 2024 | Net akis ticari | 3,132.0 | 3,971.2 | 839.2 | 1.268 |
| 2024 | Net akis bireysel | 1,138.0 | 1,313.4 | 175.4 | 1.154 |
| 2024 | Net akis toplam | 4,271.0 | 4,723.2 | 452.2 | 1.106 |
| 2025 | Net akis ticari | 5,208.0 | 7,628.4 | 2,420.4 | 1.465 |
| 2025 | Net akis bireysel | 1,768.0 | 2,069.6 | 301.6 | 1.171 |
| 2025 | Net akis toplam | 7,227.0 | 7,525.0 | 298.0 | 1.041 |

Stok farkı kur ve değerleme içerir; net akış değildir. Konsolide olmayan akış serisi bu köprüde çekilmedi.

## 3. Beş adım → katman

| Adım | Tek-sistem | Katman | Nesne | Dönem | Değer | Birim | Durum |
| ---: | --- | --- | --- | --- | ---: | --- | --- |
| 1 | Lira alacak ve borç e-fatura üzerinden eşleşir; kapalı döngü nakit dolaşmadan kapanır | `mahsup_sektor_evds.py` | sektör akış ağı, optimal_mahsup, brüt çıkış silinen oranı | 2026-Q1 | 0.4270 | oran | olculdu |
| 1 | Aynı adım, stok tarafı | `stok_silim.py` | araç-ayrı karşı bacak tavanı (üst sınır) | 2026-Q1 | 0.0728 | oran (üst sınır) | test_edilemez |
| 2 | Kalan net borç silinmez; üstten alta akış planıyla ödenir; alta inen pay ücret | `odeme_mahsup.py` | mahsup sonrası akış + şart kaldıracı; temerrüt sayısı | 2026-Q1 (sentetik 150 firma) | 0 | temerrüt sayısı | modellendi |
| 3 | Akış banka kredisiyle çevrilmez; eski stokun faizi durur | `odeme_mahsup.py` | kredi ihtiyacı brüt → şart | 2026-Q1 (sentetik 150 firma) | 0.0000 | trilyon TL/ay | modellendi |
| 3 | Aynı adım, kredi stoku ölçüsü | `tek_sistem_kopru.py` | firma F.4 kredi yükümlülüğü (EVDS) | 2026-Q1 | 25,339.8 | milyar TL | olculdu |
| 4 | Tasarruf dolar ve arsa yerine hedef primli endeksli senede gider | `tek_sistem_kopru.py` | hane vadeli mevduat (VF.2 ZP8) | 2026-Q1 | 8,322.4 | milyar TL | olculdu |
| 4 | Tasarruf dolar ve arsa yerine hedef primli endeksli senede gider | `tek_sistem_kopru.py` | firma vadeli mevduat (VF.2 ZP8) | 2026-Q1 | 4,400.1 | milyar TL | olculdu |
| 4 | Tasarruf dolar ve arsa yerine hedef primli endeksli senede gider | `tek_sistem_kopru.py` | gerçek kişi YP mevduat (HPB tablo 2) | 2026-Q1 | 6,639.4 | milyar TL (TL karşılığı) | olculdu |
| 4 | Hedef primli endeksli senet | `—` | senet ihracı, prim kaynağı, ikincil piyasa çıkışı |  |  |  | modellenmedi |
| 5 | Konut topluma açılırsa kira aynı akışın ikinci kolu | `—` | kira akışı |  |  |  | olculmedi |

Notlar:

- Adım 1 / sektör akış ağı, optimal_mahsup, brüt çıkış silinen oranı: Sektör düzeyi akış; bilateral e-fatura eşleşmesi değil. tek-sistem mahsuplasma paketi (mahsup/) aynı kod. (`mahsup_sektor_ozet.json`)
- Adım 1 / araç-ayrı karşı bacak tavanı (üst sınır): Stok silimi akış oranına eşitlenmez; tavan dağılım değildir. H-S araç ayrı silinen yokken skorlanmaz. (`stok_silim_sonuc.json`)
- Adım 2 / mahsup sonrası akış + şart kaldıracı; temerrüt sayısı: holding_odeme_orani 0.5, ucret_gecis_beta 0.3; ağ sentetik, ölçüm değil. (`odeme_mahsup_sonuc.json`)
- Adım 3 / kredi ihtiyacı brüt → şart: brüt 0.0 → şart 0.0. Faizin durması modellenmedi; tek-sistem 2025 firma finansman gideri 4.300 (RAPOR.md) bu depoda ölçülmedi. (`odeme_mahsup_sonuc.json`)
- Adım 3 / firma F.4 kredi yükümlülüğü (EVDS): tek-sistem ticari stok 2025 17.302 (BDDK) ile mutabakat tablosunda karşılaştırılır. (`tek_sistem_kopru.csv`)
- Adım 4 / hane vadeli mevduat (VF.2 ZP8): Senedin adresi olacak stok; senet ve prim mekanizması bu depoda modellenmedi. Altın ve arsa stoku burada yok. (`tek_sistem_kopru.csv`)
- Adım 4 / firma vadeli mevduat (VF.2 ZP8): Senedin adresi olacak stok; senet ve prim mekanizması bu depoda modellenmedi. Altın ve arsa stoku burada yok. (`tek_sistem_kopru.csv`)
- Adım 4 / gerçek kişi YP mevduat (HPB tablo 2): Senedin adresi olacak stok; senet ve prim mekanizması bu depoda modellenmedi. Altın ve arsa stoku burada yok. (`tek_sistem_kopru.csv`)
- Adım 4 / senet ihracı, prim kaynağı, ikincil piyasa çıkışı: Ne ödeme zinciri ne mahsup paketi bu enstrümanı içerir.
- Adım 5 / kira akışı: tek-sistem RAPOR.md de 'Bu kol ölçülmedi' der.

## 4. Tek-sistem'in kendi ölçüsü (taşınmadı, yan yana)

- Kopma payı 2025: 0.2216; hipotez 0.40 (`model/pasta/Olcum.csv`). Bu depoda kopma payı tanımı yok; eşlenmez.
- Bireysel stok 2025: 5,575.0; C2 payı 0.133 (`model/pasta/C1C2.csv`). `hane_taksit.py` kartı orana almaz; birleştirilmez.

## Ne denmez

- 'Mahsup kredi stokunu şu kadar düşürür' denmez; stok tavanı üst sınırdır, akış oranı ayrı nesnedir.
- 'Tasarruf senede gider' denmez; adres stokları ölçüldü, senet modellenmedi.
- Tek-sistem BDDK sayısı ile EVDS sayısı aynı stok değildir; biri diğerine düzeltilmez.
