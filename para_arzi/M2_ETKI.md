# Beş adımın M2 etkisi

Kurallar `M2_YANLISLAMA.md` dosyasında kilitlendi; bu sayılar ondan sonra üretildi. Kriter özeti `86b007ac48ec`.

## M2 düzeyi

**Kanıt.** TCMB EVDS3, grup `bie_hpbitablo1` (Para Arzı), hafta 27-03-2026. Ham birim bin TL; milyar TL = ham / 1e6. Birim çapası: 2026-03 `TP.KM.E041 + TP.KB.FON033` = 8037.0898 milyar TL, repodaki 8.037,1 ile örtüşür (fark -0.0102).

| Kalem | milyar TL | M2 payı |
| --- | ---: | ---: |
| Dolaşımdaki para | 879,8 | %3,49 |
| Vadesiz TL | 2.282,2 | %9,06 |
| Vadeli TL | 12.127,6 | %48,13 |
| **M2 TL kısmı** | **15.289,6** | %60,68 |
| Vadesiz YP | 7.144,1 | %28,35 |
| Vadeli YP | 2.762,7 | %10,96 |
| **M2 YP kısmı** | **9.906,8** | %39,32 |
| **M2** | **25.196,4** | %100 |
| M3 menkul (3.3) | 124,6 | M2 dışı |
| M3 | 27.699,7 | |

M2 = TL kısmı + YP kısmı, sapma 0,05 milyar TL altında. M3 = M2 + repo + para piyasası fonu + ihraç edilen menkul. Menkul satırı M2 toplamına girmez.

## 16.472,8 ile M2

**Kanıt.** TL para stoku 16.472,8 = emisyon 898.3 + tablo 3 yurt içi TL mevduat 15574.5 (`adim45_birim.py`: «M1 değildir»). Aynı çeyreğin M2'si 25.196,4 milyar TL'dir. Fark 8.723,6 milyar TL. Eşitlik iddiası düşer.

Farkın yazılabilen kanalları, ölçülmüş ayrıntı uydurulmadan:

- M2'nin YP kısmı 9.906,8 milyar TL'dir; 16.472,8 YP içermez. YP tek başına farkı aşar (9.906,8 > 8.723,6): TL tarafları da aynı stok değildir.
- 898,3 emisyondur, banka kasasını içerir. M2 dolaşımdaki parayı kullanır (879,8, haftalık). İki nakit ölçümü aynı an ve aynı tanımdır denmez.
- Tablo 3 TL mevduatı 15.574,5; M2'nin TL mevduatı (vadesiz + vadeli) 14.409,8. Kapsamlar ayrı yayımlanır.

## Senet

**Kanıt.** M2 bileşenleri dolaşımdaki para, vadesiz mevduat (TL ve YP) ve vadeli mevduat (TL ve YP). İhraç edilen menkul M3'ün 3.3 satırıdır, M2 toplamının içinde değildir. Bu hafta o satır 124,6 milyar TL. Repodaki 27.03.2026 DİBS stoku 10339.8 milyar TL. Menkul satırı DİBS stoğu değildir. Hazine kâğıdı da banka kâğıdı da M2 toplananı değildir. Adım 4 SFC'si zaten VF.2'yi düşürüp VF.3'ü artırır. YP mevduat M2'nin içindedir; senede çıkan YP mevduat da M2'den çıkar.

## Adım 1–2

| | Araç ayrı | Araç birleşik |
| --- | ---: | ---: |
| Mahsup 0,421, mevduat ayağı | 0 | 0 |
| Mahsup, M2 | 0 (**kanıt**) | 0 (**kanıt**) |
| Stok silimi, mevduat ayağı yurt içi | 0 | 13.967,0 |
| Stok silimi, mevduat ayağı yurt dışı | 0 | 4.033,0 |
| Stok silimi, M2 | 0 (**kanıt**) | 13.967,0 (**aday**) |

**Kanıt.** Mahsup, net pozisyonu sabit tutan bir akış oranıdır; mevduat stoku çıktısı yoktur. Araç ayrıda silinen 0; H–PFK ve F–PFK mevduat karşı bacağı yapısal 0'dır. Birleşik üç çiftin silineni 18.000,0 (F–PFK 7.195, H–PFK 6.772, PFK–ROW 4.033). İlk iki çiftte küçük bacak mevduattır: yurt içi mevduat ayağı 7.195 + 6.772. PFK–ROW'da alacaklı PFK, borçlu ROW: 4.033 yurt dışı mevduat varlığıdır, Türkiye M2'sine yazılmaz. Yurt içi ayağın M2'ye birebir inmesi adaydır: PFK bankadan ayrılmamıştır, metin kısmi çifttir, H-S bu sütunu skorlamaz.

## Adım 3, 4.5, 5

| Adım | Doğrudan M2 | Etiket |
| --- | ---: | --- |
| 3 faiz durması | 0 | **kanıt** (anapara ve mevduat stoku düşmez; faiz akışının mevduata oranı ölçülmedi, dolaylı tutar yok) |
| 4.5 yeni birim, λ = 1 | 0 | **kanıt** (TL_yeni = TL_eski) |
| 5 kira, Ho → Ha | 0 | **kanıt** (iki hane arasında aktarım) |

## Adım 4 ve senaryolar

Adresin M2'ye giren ayrı stoku 12.722,5 ile 19.076,6 arasındadır (**kanıt**, örtüşme aritmetiği). θ × bu stokun M2'den çıkması **aday**dır: VF.2 ZP8 ile HPB mevduatı aynı çevre diye ölçülmedi. Tepe = θ × adres. Kalıcı = χ × tepe. İkinci tur = 0,08 × eldeki stok, milyar TL/yıl, **aday**; stok toplamına eklenmez.

| Senaryo | θ | χ | Adres | Adım 1–2 | Adım 4 tepe | Adım 4 tepe / M2 | Kalıcı | Başlık stok | Başlık / M2 | 2. tur tepe /yıl | 2. tur kalıcı /yıl |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| dusuk | 0.1 | 0.0 | 12.722,5 | ayri | 1.272,2 | %5,05 | 0,0 | 0,0 | %0,00 | 101,8 | 0,0 |
| orta | 0.25 | 0.5 | 19.076,6 | ayri | 4.769,1 | %18,93 | 2.384,6 | 2.384,6 | %9,46 | 381,5 | 190,8 |
| yuksek | 0.5 | 0.5 | 19.076,6 | birlesik | 9.538,3 | %37,86 | 4.769,1 | 18.736,2 | %74,36 | 763,1 | 381,5 |

Başlık = adım 1–2 M2 + adım 4 kalıcı + adım 3/4.5/5 (0). Tepe başlığa girmez: senet eldeyken görülen düşüştür, vade sonunda χ payı kalır. Düşükte χ = 0 olduğu için kalıcı birinci tur 0'dır; senet vadesinde mevduata döner. Yüksek başlığın 13.967,0 milyar TL'si araç birleşik yurt içi ayaktır ve adaydır. Bu aday çıkarılırsa yüksek başlık 4.769,1 milyar TL, %18,93 olur. Aday silim dururken senet tepedeyse toplam 23.505,3 milyar TL, %93,29 olur; bu başlık değildir.

Adım adım, başlık stokunun içinde (milyar TL):

| Adım | düşük | orta | yüksek |
| --- | ---: | ---: | ---: |
| 1–2 mahsup ve stok | 0,0 | 0,0 | 13.967,0 |
| 3 | 0,0 | 0,0 | 0,0 |
| 4 kalıcı | 0,0 | 2.384,6 | 4.769,1 |
| 4.5 | 0,0 | 0,0 | 0,0 |
| 5 | 0,0 | 0,0 | 0,0 |
| Başlık | 0,0 | 2.384,6 | 18.736,2 |
| Başlık / M2 | %0,00 | %9,46 | %74,36 |

İkinci tur bu tabloda yoktur. Düşük senaryoda tepe ikinci tur 101,8 milyar TL/yıldır ve vade sonunda 0'a iner. Ortada tepe 381,5, kalıcı 190,8. Yüksekte tepe 763,1, kalıcı 381,5.
