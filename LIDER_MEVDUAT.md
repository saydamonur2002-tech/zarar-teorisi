# Lider mevduat katmanı

Yürütme rolünün tuttuğu nakit. Kişi, hane, firma mevduatı değildir. Akış yüzdesi ve stok tavanı bu kata taşınmaz.

## Parça tablosu (2026-Q1, milyar TL)

| Parça | Durum | Stok | Seri | Not |
| --- | --- | ---: | --- | --- |
| THKH | ayrılmadı |  | `` | ayrılmadı; 4749 m.12 ve CB Kararı 17 (RG 8.8.2018/30500) kapsam tanımlar, stok serisi yok. Aday: GY mevduat yükümlülüğü 360.8 (tamamı S.1311 ihraçlı, EVDS ZP27); kimden-kime GY–GY 352 (2026-Q1). THKH diye etiketli değil, lider sütununa geçmez. |
| resmi_mevduat | bulundu | 2,933.6 | `TP.FINHESTNKS1311.ZP5` | Merkezi yönetim (S.1311) VF.2 para ve mevduat, konsolide olmayan stok; TCMB+banka, TL+YP; vadesiz 822.6 + vadeli 2110.2. GY'den ayrı seri: GY 3398.8 = MY + yerel 274.6 + SGK 190.6. |
| merkez_banka | bulundu | 1,192.0 | `TP.BL0661.A + TP.BL0821.A` | TCMB bilançosu P3111 nakit (Hazine, genel ve özel bütçeli idareler): TL 574.8 + YP 617.2. P311 toplam 1346.5 = nakit + altın 154.5 (altın F.1, mevduat değil). Hazine tek başına ayrılmadı; THKH bu kalemin içinde olabilir, seri ayırmaz. |
| banka | ayrılmadı |  | `TP.HPBITABLO3.9` | ayrılmadı; HPB tablo 3 'Resmî kuruluşlar' TL 1455.9 GY kapsamıdır (yerel yönetim ve SGK dahil), merkezi yönetim bacağı ayrılmaz; YP resmî serisi yok. |

## Dönemler

| Dönem | MY VF.2 | TCMB P3111 nakit | TCMB P3112 altın | Banka resmî TL (GY) | GY VF.2 | Hane VF.2 | MY/hane % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2024-Q4 | 1,529.9 | 820.5 | 180.6 | 610.8 | 1,906.4 | 10,805.4 | 14.2 |
| 2025-Q1 | 1,300.9 | 550.5 | 155.0 | 520.5 | 1,577.2 | 12,437.3 | 10.5 |
| 2025-Q2 | 1,880.9 | 921.0 | 189.6 | 730.0 | 2,367.0 | 13,035.9 | 14.4 |
| 2025-Q3 | 2,736.2 | 1,413.4 | 230.0 | 1,148.0 | 3,112.8 | 13,916.9 | 19.7 |
| 2025-Q4 | 2,798.3 | 1,103.6 | 268.8 | 1,515.4 | 3,478.0 | 14,559.9 | 19.2 |
| 2026-Q1 | 2,933.6 | 1,192.0 | 154.5 | 1,455.9 | 3,398.8 | 15,356.8 | 19.1 |
| 2026-Q2 |  | 1,071.6 | 139.9 | 1,566.3 |  |  |  |
| 2026-Q3 |  | 1,115.7 | 153.3 | 1,546.1 |  |  |  |

## Yanlışlayıcılar

- **H-L:** `ayri` (buyuk). Merkezi yönetim VF.2 2,933.6 < GY VF.2 3,398.8; ayrı EVDS serisi (S.1311). Hane VF.2 15,356.8; MY/hane = %19.1; TCMB P3111 nakit/hane = %7.8. Büyüklük kontrol kanıtı değildir.
- **H-L2:** `silinen_bos`. Lider parçasının ters bacağı yok: TCMB ve bankalar GY'de mevduat tutmaz; GY mevduat yükümlülüğü (360.8) tamamı S.1311 ihraçlı ve kimden-kime GY–GY 352 kendi içidir. Skora girmez. Tavan yazılmaz.
- **THKH:** ayrılmadı. Dayanak 4749 m.12; CB Kararı 17 (RG 8.8.2018/30500). Stok serisi yok; haberden tutar doldurulmadı.

## Sınır

- GY toplamı yan sütundur, lider değildir. Resmî kuruluşlar (banka) GY kapsamıdır.
- TCMB P311 = P3111 nakit + P3112 altın; merkez_banka satırı yalnız nakittir. Finansal hesaplarda altın F.1'dir, VF.2'ye girmez.
- Hane 15.357 ve firma stokları lider sütununa girmez. Stok silimi tavanı ve akış %42,7 bu dosyada yok.

## Arama günlüğü

| Grup | Sonuç | Not |
| --- | --- | --- |
| `bie_finhestnks1311` | açıldı | Merkezi yönetim (S.1311) konsolide olmayan stok; VF.2, F.2 |
| `bie_finhestnks1313 / 1314` | açıldı | Yerel yönetim, SGK; GY toplamı kontrolü |
| `bie_finhestnks13` | açıldı | GY toplamı (yan sütun) |
| `bie_finhestnks14` | açıldı | Hane VF.2 (yüzde 10 eşiği) |
| `bie_mbblnca` | açıldı | TCMB bilançosu aylık; P311 = P3111 nakit + P3112 altın, TL/YP. Yıl sonu yıllık bilançoyla birebir (2024: 1.001,1; 2025: 1.372,4) |
| `bie_abanlbil` | açıldı, kullanılmadı | Analitik bilanço 'Kamu Mevduatı' TL; 'Kamu ve Diğer Döviz Mevduatı' karışık |
| `bie_hpbitablo3` | açıldı | Resmî kuruluşlar TL; GY kapsamı, MY ayrılmaz |
| `bie_hpbitablo2/4/8` | açıldı, boş | YP veya toplam mevduatta resmî ayrımı yok |
| `bie_mevduat` | açıldı, kullanılmadı | Arşiv seri; banka grubu bazında resmî kuruluşlar |
| `bie_finhestnks1312 / 71311 / 61311` | boş | Kimden-kime MY alt sektörü yok |
| `bie_hznakit, bie_hazine, bie_hazinenakit, bie_nakitdenge, bie_kamufin, bie_hzborc` | boş | THKH / Hazine nakit rezervi stok serisi EVDS'de bulunamadı |
| `web: HMB nakit gerçekleşmeleri` | akım | Aylık nakit dengesi akımdır; THKH bakiyesi yayımlanmıyor (2 sorgu denendi) |

Tekrar: `python3 lider_mevduat.py`. Dosyalar: `lider_mevduat.csv`, `lider_mevduat_sonuc.json`.
