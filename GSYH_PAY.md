# Yürütme maliyeti, yıl bazında GSYH payı

Çalıştır: `python3 gsyh_pay.py`. Çıktı: `gsyh_pay.csv`. Her yılın maliyeti o yılın GSYH'sine bölünür (yüzde).

**Payda varsayımdır.** Repoda GSYH yalnız 2023-2025 (ölçüm). 2026 sonrası: önceki yıl × (1+TÜFE) × (1+reel %3). TÜFE, `bes_yil_senaryo.csv` senaryo alt/üst ortası; 2029-2030 için senaryo yok, 2028-2031 arası doğrusal. Reel büyüme repoda yok, benim varsayımım.

| Yıl | GSYH (mlr TL, varsayım yolu) | Düşük | Orta | Yüksek |
|---|---|---|---|---|
| 2026 | 84,425 | 0.0 mlr TL = %0.000 | 0.0 mlr TL = %0.000 | 0.0 mlr TL = %0.000 |
| 2027 | 103,375 | 0.0 mlr TL = %0.000 | 0.0 mlr TL = %0.000 | 0.0 mlr TL = %0.000 |
| 2028 | 121,926 | 3.0 mlr TL = %0.002 | 135.9 mlr TL = %0.111 | 875.6 mlr TL = %0.718 |
| 2029 | 141,198 | 144.8 mlr TL = %0.103 | 365.4 mlr TL = %0.259 | 1,593.5 mlr TL = %1.129 |
| 2030 | 160,497 | 5.6 mlr TL = %0.003 | 242.2 mlr TL = %0.151 | 2,173.7 mlr TL = %1.354 |
| 2031 | 178,999 | 4.9 mlr TL = %0.003 | 235.1 mlr TL = %0.131 | 1,515.0 mlr TL = %0.846 |

Senaryolar: düşük = ρ %0,4, κ 0,25, en küçük prim senaryosu, adım 4.5 A alt; orta = ρ %9, κ 0,5, orta prim senaryosu, adım 4.5 A ortası; yüksek = ρ %29, κ 1,0, en büyük prim senaryosu, adım 4.5 B üst. Adım 1-2 her üçünde ρ %0,4 (stok mahsubunda yüksek ρ uygulanmaz).

Kalemler (yıl, senaryo bazında): 

- düşük 2028: adım 3 3.0
- düşük 2029: adım 3 4.8; adım 4 0.1; adım 1-2 (tek sefer, 2029 varsayım) 139.9
- düşük 2030: adım 3 4.8; adım 4 0.2; adım 4.5 0.6
- düşük 2031: adım 3 4.8; adım 4 0.1
- orta 2028: adım 3 135.9
- orta 2029: adım 3 217.4; adım 4 8.2; adım 1-2 (tek sefer, 2029 varsayım) 139.9
- orta 2030: adım 3 217.4; adım 4 21.8; adım 4.5 3.0
- orta 2031: adım 3 217.4; adım 4 17.7
- yüksek 2028: adım 3 875.6
- yüksek 2029: adım 3 1400.9; adım 4 52.7; adım 1-2 (tek sefer, 2029 varsayım) 139.9
- yüksek 2030: adım 3 1400.9; adım 4 140.4; adım 4.5 632.4
- yüksek 2031: adım 3 1400.9; adım 4 114.1

**Adım 5 (toplama girmedi).** Kira transferi (kapsama %50) 2026 fiyatıyla ve yılı belirsiz; yürütme maliyeti düşük/orta/yüksek = 0.5 / 23.8 / 116.2 mlr TL/yıl = GSYH 2026'nın %0.001 / %0.028 / %0.138'i.

**Sınırlar.** Adım 3 ve 4 maliyeti, ρ ile çarpılmış akıştır; ρ dayanağı zayıf (BES_ADIM_MALIYET.md). Üç senaryo tutarlı bir tahmin değil, bant uçlarıdır. Payda yolu tahmin değil; reel büyüme ve 2029-2030 TÜFE'si benim varsayımım.
