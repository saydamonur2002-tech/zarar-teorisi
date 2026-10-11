# Enflasyon tavanı, işlem akımı

Çalıştır: `python3 tavan_akis.py`. Çıktı: `tavan_akis.csv`, `tavan_akis_sonuc.json`.

Tanım: tavan = kredi itişinin fiyata geçen parçası. İtiş = firma F.4 **işlem akımı** (dört çeyrek toplamı), stok farkı değil. Geçiş payı ölçülmeden yazılmaz; 1/3 kullanılmaz. Adım 1 etiketi ve stok tavanı bu dosyaya girmez.

## 1. Üç yıl: itiş (akım) ve stok farkı ayrı (milyar TL; oranlar yüzde GSYH)

| Yıl | F.4 işlem akımı | Stok farkı Q4−Q4 | GSYH (cari) | Oran akım | Oran stok | Geçiş | Tavan | Durum |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2023 | 1,829.5 | 4,111.7 | 27,091.5 | 6.75 | 15.18 |  |  | itis_olculdu; gecis_bulunamadi; tavan_bos |
| 2024 | 3,039.3 | 3,971.2 | 44,676.0 | 6.80 | 8.89 |  |  | itis_olculdu; gecis_bulunamadi; tavan_bos |
| 2025 | 4,820.9 | 7,628.4 | 63,240.5 | 7.62 | 12.06 |  |  | itis_olculdu; gecis_bulunamadi; tavan_bos |

Seriler: akım `TP.FINHESTNKS62011.ZP34` (konsolide olmayan, işlem, sum), stok `TP.FINHESTNKS11.ZP34` (konsolide olmayan, last), GSYH `TP.GSYIH20.BY.B1GQ` (harcama, cari, 4 çeyrek). Stok farkı kur ve değerleme içerir; akım sütunuyla eşitlenmez. Buradaki stok farkı EVDS firma F.4'tür (tüm borç verenler); RAPOR'un 5.208'i BDDK ticari stok farkıdır (yalnız banka) — ikisi de stok farkı, ikisi de akım değil.

## 2. Geçiş payı: birincil arama

| Nerede | Ne | Sonuç |
| --- | --- | --- |
| EVDS katalog (evds_katalog_gruplar.json, 680 grup) | 'çıktı açığı' / 'cikti acigi' | 0 grup; TCMB çıktı açığı Enflasyon Raporu grafiğidir, EVDS serisi yok |
| EVDS katalog | 'geçiş' / 'geçişkenlik' (kredi→fiyat) | 0 grup; kur geçişkenliği serisi de yok |
| EVDS katalog | fiyat: TÜFE (bie_tukfiy2025), Yİ-ÜFE (bie_tufe1yi), H-ÜFE (bie_hufe) | endeks var; kredi itişinin fiyata geçen payı değil, katsayı değil |
| EVDS katalog | beklenti/anket: Piyasa Katılımcıları, Sektörel, Hanehalkı; KKO; Banka Kredileri Eğilim | var; geçiş payı vermez |
| Depo | odeme_enf_sonuc.json, odeme_enf.py | sentetik ağ; 'Sayılar ölçüm değildir' (dosya uyarısı); kullanılmaz |
| Depo | OKU.txt 'gecis' | TGA geçiş hızı; fiyat geçişi değil |
| tek-sistem RAPOR.md | 'Fiyata üçte biri geçse' | varsayım cümlesi, kaynak yok; `varsayim`, tavan diye durmaz |

Sonuç: geçiş payı **bulunamadı**, 7 arama denendi. Geçiş sütunu boş; tavan sütunu boş.

## 3. Yanlışlayıcılar

- **H-T** (stok farkı tavanı şişirir): `siser`. 2025 oran_stok 12.06 vs oran_akim 7.62 (yüzde GSYH); fark 4.44 puan. RAPOR'un yüzde 8,3'ü stok farkıyla kurulmuştur.
- **H-T2** (tavan kurulur): `test_edilemez`. geçiş payı birincil bulunamadı; tavan boş; 2,5 puan lehte yazılmaz

## 4. Referans notu (sonuç sütununa geçmez)

tek-sistem RAPOR.md (c01b60a): ticari net akış 5,208 / milli gelir 63,021 = yüzde 8.3; 'fiyata üçte biri geçse' yaklaşık 2.5 puan. 5.208 stok farkıdır (`TEK_SISTEM_KOPRU.md` 9/9). 'Üçte biri' `varsayim`; tavan diye durmaz.

## Ne denmez

- 'Enflasyon 2,5 puan iner' denmez. İtiş şu, geçiş ölçülmedi, tavan boş.
- Stok farkı akım diye kullanılmaz.
- Oran akım, oran stokun yerine 'doğru tavan' diye de yazılmaz; geçiş olmadan ikisi de tavan değildir.
