# Tek sistem — sıralı kademeli üç pencere

Senaryo takvimi; ölçüm değil. Katman sonuçları birbirine taşınmaz.

Çalıştır: `python3 tek_sistem_kademe.py`. Dönem: `2026-Q4` … `2031-Q4`.

## Pencereler (ayrık, sıralı)

| Kademe | Kod | Başlangıç | Bitiş | Katman | Referans |
| ---: | --- | --- | --- | --- | --- |
| 1 | `K1_mahsup` | 2027-Q1 | 2027-Q4 | mahsup_sektor_evds.py; odeme_mahsup.py | sektor_brut_silinen_oran = 0.427 oran |
| 2 | `K2_stok` | 2028-Q1 | 2028-Q4 | stok_silim.py; adim1_stok | yeni_tavan_ust_sinir = 0.2582 oran |
| 3 | `K3_mevduat` | 2029-Q1 | 2029-Q4 | adim4 (adres adayları) | adres_mevduat_toplam = 19361.9 milyar TL |

Pencere içi: uygulama oranı çeyrekte `1/n … n/n` (doğrusal kademe). Pencere sonrası: **1,0** (açık kalır).

## Örnek kilometre taşları

| Dönem | K1 | K2 | K3 | Not |
| --- | ---: | ---: | ---: | --- |
| 2026-Q4 | 0.0 | 0.0 | 0.0 | henüz hiçbiri |
| 2027-Q1 | 0.25 | 0.0 | 0.0 | K1 başlar |
| 2027-Q4 | 1.0 | 0.0 | 0.0 | K1 tam |
| 2028-Q1 | 1.0 | 0.25 | 0.0 | K2 başlar |
| 2028-Q4 | 1.0 | 1.0 | 0.0 | K2 tam |
| 2029-Q1 | 1.0 | 1.0 | 0.25 | K3 başlar |
| 2029-Q4 | 1.0 | 1.0 | 1.0 | üçü tam |
| 2031-Q4 | 1.0 | 1.0 | 1.0 | üçü açık (1,0) |

## Ne denmez

- “Üçü aynı defterde eşzamanlı entegre edildi” denmez; yalnız takvim.
- “Mevduat dağıtımı modellendi” denmez; K3 etkin adres **milyar TL bandı**, senet `modellenmedi`.
- Stok **silinen** tutarı bu takvimden türetilmez (`silinen` boş).

Depo referansı: firma mahsup oranı `0.32959478056952846`; yeni stok tavan `0.2582`.

