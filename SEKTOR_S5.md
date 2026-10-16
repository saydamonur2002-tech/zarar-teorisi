# S5 — kayıp aktarımı

Kurallar: `SEKTOR_S5_ONKAYIT.md`. Çekim: 2026-10-16, bitiş 16-10-2026. Ham: `sektor_s5_ham.csv`.

S5 belirlenemiyor. NACE kesiminde özkaynağı aşan döviz kaybı yok. Çekilen banka stoku ve TCMB satışı kesim etiketi taşımıyor. Toplamın artması aktarım sayılmaz.

## Banka kanalı

`TP.HPBITABLO6.26`, grup `bie_hpbitablo6`, ad 1.2.1.b.YP. Finansal kesim dışı ticari kredilerin YP kısmı. Haftalık, toplulaştırma last. NACE değil.

Aynı tablodaki ticari toplam `TP.HPBITABLO6.20`, 27-03-2026 ham 15.996.455.548. Bölü 1.000.000 = 15.996,5 milyar TL. Bu, daha önce yazılan 2026-03 ticari stokuyla aynıdır. Birim bin TL'dir. YP satırı aynı tablodadır, aynı birimle okundu.

| | Tarih | Ham, bin TL | Milyar TL |
| --- | --- | --- | --- |
| İlk | 28-06-2024 | 4.157.373.035 | 4.157,4 |
| Son | 09-10-2026 | 8.948.876.050 | 8.948,9 |

Gözlem 120. Aralık 28-06-2024 … 09-10-2026. Bu artış, bir kesimin kur kaybının krediye geçtiği gözlem değildir.

## Firma tarafı

`TP.FDVY16`, grup `bie_fdvy`, ad B.a.1.1.1 döviz kredileri, yurt içi bankalar. Aylık, last. NACE değil. API yanıtında birim alanı yok. Çevrilmedi.

| | Dönem | Ham |
| --- | --- | --- |
| İlk hücre | 2002-12 | 0 |
| İlk pozitif | 2003-01 | 9.716 |
| Son | 2026-07 | 179.415 |

Gözlem 284. Sıfır hücre bir tanedir. Mevduat satırları ve `TP.FDVY37` net pozisyon çekilmedi.

## TCMB satışı

Grup `bie_dovefmud`, arşiv. İş günü, toplulaştırma sum. Boş gün sıfır yazılmadı. Para birimleri toplanmadı.

`TP.SATIM.USD`, ad Satım Tutarı (USD) (Arşiv). Dolu hücre 12. Aralık 11-07-2002 … 23-01-2014. Adın içinde milyon yazmıyor.

| Tarih | Ham |
| --- | --- |
| 11-07-2002 | 3 |
| 24-12-2002 | 9 |
| 11-05-2004 | 9 |
| 13-06-2006 | 494 |
| 23-06-2006 | 763 |
| 26-06-2006 | 848 |
| 18-10-2011 | 525 |
| 30-12-2011 | 1.865 |
| 02-01-2012 | 525 |
| 03-01-2012 | 326 |
| 04-01-2012 | 155 |
| 23-01-2014 | 3.151 |

On iki dolu hücrenin toplamı 8.673'dir. Bu, takvimdeki bütün günlerin toplamı değildir. Satış bir kesime yazılmamıştır.

`TP.SATIM.EUR`, `TP.SATIM.CHF`, `TP.SATIM.DEM` katalogda duruyor. İş günü çekiminde her birinde 9.600 satır var, dolu hücre yok. Satış sıfır diye yazılmadı.

Piyasa hacmi `TP.DF.*` çekilmedi. Alım serileri karar serisi değildir.
