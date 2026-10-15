# Adım 4.5 — TL'den yeni fiat TL'ye geçiş

Çalıştır: `python3 adim45_birim.py`. Çıktı: `adim45_birim.csv`, `adim45_birim.json`.

Yeni lira altın ya da döviz üzerinde alacak değildir. Dolara çevrilerek ödenmez. λ = 1 paritedir; bu bir varsayımdır. Sayılar durur. Başka bir λ bütün TL stoklarını, TL akışlarını ve kuru aynı çarpanla ölçekler. USD stoku ve faiz oranı durur. Ölçülmüş bir sıfır atma yoktur.

Takvim 2030-Q1 .. 2030-Q4, senaryo takvimi. K3 bundan önce kapanır. Adım 5'in penceresi yoktur. Üç kademe penceresine dördüncü pencere eklenmez.

## Stok, 2026-Q1 ölçümü (milyar TL)

| Nesne | Eski | Yeni, λ=1 | Fark | Etiket |
| --- | ---: | ---: | ---: | --- |
| TCMB nakit yükümlülüğü | 898.3 | 898.3 | 0 | ölçüm |
| Yurt içi TL mevduat | 15,574.5 | 15,574.5 | 0 | ölçüm |
| — gerçek kişi TL | 8,037.5 | 8,037.5 | 0 | ölçüm |
| — ticari TL | 3,993.3 | 3,993.3 | 0 | ölçüm |
| — resmî TL | 1,455.9 | 1,455.9 | 0 | ölçüm |
| — HHKAOK TL | 331.6 | 331.6 | 0 | ölçüm |
| — banka dışı finansal TL | 1,756.2 | 1,756.2 | 0 | ölçüm |
| **Toplam** | **16,472.8** | **16,472.8** | **0** | ölçüm |

Banka kasasındaki para 356.3 bu nakit yükümlülüğünün içindedir. İkinci kez eklenmez.

## Girmeyenler

| Nesne | TL karşılığı | λ=1 sonrası | |
| --- | ---: | ---: | --- |
| Yurt içi YP | 10,026.3 | 10,026.3 | USD stok durur |
| Gerçek kişi YP | 6,639.4 | 6,639.4 | fiat TL stokuna girmez |
| Tüzel YP | 3,386.9 | 3,386.9 | USD stok durur |
| Kâğıt stoku, θ=0,25, 2030-Q4 | 4,840.5 | 4,840.5 | ayrı kat, paraya eklenmez |

H VF.2 (15.356,8) toplama yazılmaz. YP'nin TL karşılığını da tutar. HPB yurt içi TL ile aynı çevre değildir.

## Kimlik

- TL_yeni = TL_eski · (1 + u·(λ−1)). 2030-Q4'te u=1, TL_yeni = λ · TL_eski.
- kur_yeni = λ · kur_eski. Bu dosya 2030 kur düzeyi tahmin etmez.
- USD stok ×1. r_ic, r_dis, r_diger ve AOFM ×1.
- İki taraf da ölçeklenir. NFP farkı 0. ΣNL = 0. silinen boş.
- TL cinsinden oran, payda da TL ise durur. GSYH patikası bu dosyada kurulmaz.

## Ne denmez

- Altı sıfır atıldı denmez. λ ölçülmedi. Parite 1'dir.
- Borç silindi denmez. `silinen` boş kalır.
- YP mevduat yeni TL'ye çevrildi denmez.
- Kâğıt stoku para stokuna eklendi denmez.
- Geçiş Hazine faiz faturasını indirdi denmez. λ=1 iken fatura farkı 0'dır.
- Senet satırı doldu denmez. `adim4.csv` ve kilit durur.
