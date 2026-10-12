# Üç kural SFC senaryosu

Stok-akış tutarlı **senaryo**; ölçüm değil. Çalıştır: `python3 uc_kural_senaryo.py`.

## Kurallar (kilitli senaryo)

1. Taban: telafi + yarıyıl reel kama; üst ücretler yalnız TÜFE (basitleştirildi).
2. Seçici kredi + DTI: segment tavanları, limit çarpanı, Ponzi bandı.
3. Geri bildirim: kapsama, alt %20 borç/gelir, üretken pay, döviz stoku.

## Varsayımlar

- Ha borç payı: `0.4` (VARSAYIM)
- Kama geçişkenliği: `1.0`
- TÜFE yolu (yıllık): `0.28`
- kart %33,4 / tüketici %13,9 DOĞRULANMADI bu depoda

## 2031-Q4 karşılaştırma (milyar TL NFP; oranlar birim dosyasında)

| Gösterge | Mevcut | Üç kural kilitli |
| --- | ---: | ---: |
| NFP_H | 26181.8 | 31553.6 |
| NFP_F | -47839.0 | -67150.8 |
| borc_servis_orani_Ha | 0.57 | 0.318 |
| uretken_zarf_payi | 0.45 | 0.569 |
| korunmasiz_doviz_stok_mr_usd | 162.9 | 120.0 |
| kapsama | 0.574 | 0.854 |
| K_butce_NL_milyar | 0.0 | -24.9 |

## Ne denmez

- Politika önerisi veya uygulama vaadi değildir.
- `simulate()` lam/kappa ampirik olarak zayıf (OKU.txt); yayılım katsayısı kısmi.
- Merkezi bütçe ≠ K′; fiscal_shock mükellef payı varsayımdır.
