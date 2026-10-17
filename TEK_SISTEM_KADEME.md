# Tek sistem — sıralı kademeli üç pencere

Senaryo takvimi; ölçüm değil. Katman sonuçları birbirine taşınmaz.

Çalıştır: `python3 tek_sistem_kademe.py`. Dönem: `2026-Q4` … `2031-Q4`.

## Pencereler (ayrık, sıralı)

| Kademe | Kod | Başlangıç | Bitiş | Katman | Referans |
| ---: | --- | --- | --- | --- | --- |
| 1 | `K1_mahsup` | 2027-Q1 | 2027-Q4 | mahsup_sektor_evds.py; odeme_mahsup.py | sektor_brut_silinen_oran = 0.421 oran |
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

## Kademeli etkin → borca etkisi (proxy)

Ölçüm değil; katmanlar birleştirilmedi. **Nominal borç silinmez** (tek sistem kuralı). Etki kanalları:

| Kademe | Borç nesnesi | Mekanizma | Formül (kademe uygulama u) |
| --- | --- | --- | --- |
| K1 | Firma **yeni kredi itişi** (F.4 akım proxy) | Brüt mahsup → zinciri çeviren taze akış | `u1 × 0.421 × itiş_yıllık / 4` çeyrek; itiş=4820.9 milyar (2025) |
| K1 | **Net stok** | Mahsup net pozisyonu korur | F.4 stokunda **doğrudan düşüş yok**; yalnız itiş freni |
| K2 | **Kimden-kime brüt stok** (üst sınır) | Karşı bacak tavanı yükselir | `u2 × (yeni−eski) × brüt` = brüt fazlalık azaltılabilir tavan |
| K3 | **Yeni banka kredi itişi** (varsayım) | Mevduat adresi senede kayar | `u3 × adres × 0.08` / 4 çeyrek; pay VARSAYIM |

**F.4 stok kumul proxy** (2026-Q1 taban → çeyrek net yeni = itiş/4, 2027-Q1’den itibaren K1+K3 düşülür):

| Dönem | K1 itiş azalt (milyar/yıl) | K2 brüt üst (milyar) | K3 kredi azalt (milyar/yıl) | F4 baseline | F4 etkin | Fark |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-Q4 | 0.0 | 0.0 | 0.0 | 25339.8 | 25339.8 | 0.0 |
| 2027-Q4 | 2029.6 | 0.0 | 0.0 | 30160.6 | 28892.2 | 1268.4 |
| 2029-Q4 | 2029.6 | 14622.6 | 1549.0 | 39802.2 | 33506.6 | 6295.6 |
| 2031-Q4 | 2029.6 | 14622.6 | 1549.0 | 49443.8 | 35991.4 | 13452.4 |

Tam kademe (2031-Q4): yıllık itiş freni ≈ **2029.6 milyar TL** (≈ %42.1 itiş); K2 brüt üst sınır **14622.6 milyar**; K3 kredi itişi freni **1549.0 milyar/yıl** (varsayım). F.4 kumul fark **13452.4 milyar** — yalnız itiş proxy; kur/değerleme yok.

Hane borcu (`uc_kural_senaryo`) bu takvime **bağlı değil**. Çift kayıtta borçlu defteri nominal kalır.

## Ne denmez

- “Üçü aynı defterde eşzamanlı entegre edildi” denmez; yalnız takvim.
- “Mevduat dağıtımı modellendi” denmez; K3 etkin adres **milyar TL bandı**, senet `modellenmedi`.
- Stok **silinen** tutarı bu takvimden türetilmez (`silinen` boş).

Depo referansı: firma mahsup oranı `0.32959478056952846`; yeni stok tavan `0.2582`.

