# Hazine vadeli mevduat ve kalıcılık

Kalıcılık: ödeme emri günü → nakdin 102 hesaba geçtiği gün. Vadeli: MY VF.2 vadeli (`TP.FINHESTNKS1311.ZP8`). Borç faizi ve bankanın Hazine'ye ödediği faiz konu dışı. Akış, stok tavanı, lider mevduat bu teste girmez.

## Üç kapı

| Kapı | Durum | Not |
| --- | --- | --- |
| 1_vade_gunu | **ayrılmadı** | Merkezi yönetim vadeli mevduatın vade dilimi kırılımı (1 aya kadar / 1–3 / 3–6 / 6–12 / 12+) EVDS'de yok. Finansal hesaplar yalnız vadesiz/vadeli (ZP7/ZP8). TCMB 'dthvade' ve BDDK aylık bülten vade dilimini sektör toplamı için verir; tür × vade çaprazı yayımlanmaz. HPB tablo 3 resmî kuruluşlar vadesiz/vadeli (TL) GY kapsamıdır, MY diye kullanılmadı. |
| 2_thkh | **ayrılmadı** | THKH bakiyesi için ayrı kamu serisi yok (lider_mevduat katmanı: 6 grup kodu + 2 web sorgusu). GY–GY 352 ve MY F.2 (ZP27) aday notunda kalır; vadeli diye etiketlenmez. MY F.2 vadeli (ZP30) ölçülüdür ama ihraç tarafıdır, tutulan vadeli değildir. |
| 3_odenmeyen_emir | **bulunamadı** | Merkezi yönetim konsolide 320 Bütçe Emanetleri ve 103 Verilen Çekler ve Gönderme Emirleri bakiyesi 2025-Q2 ve Q3 için bulunamadı. Muhasebat portalı (/portal/v2 pages: genel-yonetim-mali-istatistikleri, mali-istatistikler-gfsm-2014e-uyumlu, merkezi-yonetim-alt-sektoru-mali-istatistikleri) dosya bağlantısı vermiyor; 3 sayfa + 3 arama denendi. Bulunan ama testin nesnesi olmayan: GİB Eylül 2025 kurum mizanı (103 hesabı dönem hareketi ~525 milyar, bakiye 0,11; 320 bakiye 0,05) kurum düzeyidir; Sayıştay Adana BB 2024 raporu 320 bekleme gün tablosu belediyedir. Sayıştay HMB raporunda gün sayısı yok. Gün sayısı hiçbir kaynakta MY için yayımlanmıyor. |

## Gözlenen (milyar TL, dönem sonu)

| Dönem | Vadeli | Vadesiz | Para | VF.2 | MY F.2 vadeli (ihraç) | TCMB F.2 vadeli (ihraç) | Resmî TL vadeli, banka (GY) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2024-Q4 | 782.8 | 746.8 | 0.3 | 1,529.9 | 19.4 | 354.7 | 323.8 |
| 2025-Q1 | 402.1 | 898.4 | 0.4 | 1,300.9 | 28.0 | 1,114.4 | 335.3 |
| 2025-Q2 | 561.9 | 1,318.5 | 0.5 | 1,880.9 | 30.5 | 221.7 | 358.5 |
| 2025-Q3 | 1,908.0 | 827.6 | 0.6 | 2,736.2 | 48.0 | 1,680.6 | 730.0 |
| 2025-Q4 | 2,072.2 | 725.6 | 0.5 | 2,798.3 | 58.9 | 1,756.9 | 1,057.4 |
| 2026-Q1 | 2,110.2 | 822.6 | 0.8 | 2,933.6 | 89.9 | 1,012.0 | 1,065.7 |

2025-Q2 → Q3: vadeli 561.9 → 1,908.0 (+1,346.1); vadesiz 1,318.5 → 827.6 (-490.9); VF.2 +855.3. Sıçrama girdidir, nedeni değil.

## Yanlışlayıcılar

- **H-K1:** `test_edilemez`. Vadeli arttı (+1346.1), vadesiz düştü (-490.9). Ödenmeyen emir ve gün ölçülmedi (kapı 3 bulunamadı). Vadeli artış tek başına lehte yazılmaz.
- **H-K2:** `ayri_stok`. THKH serisi yok; sıçrama THKH ile eşleştirilemedi. Kural gereği etiket ayri_stok; bu 'ayrı olduğu gösterildi' değil 'eşleşme gösterilemedi' demektir. Kalıcılık cümlesi düşer: THKH dışı vadeli, kurum ödemesini kilitlemez.
- Yan ölçüm: TCMB vadeli mevduat ihraç eder (F.2 vadeli). Q2→Q3 TCMB F.2 vadeli +1458.9, MY VF.2 vadeli +1346.1; eş hareket ölçüldü, karşı taraf eşlemesi kimden-kime'de yok, bu yüzden eşitlenmez.

## Arama günlüğü

| Nerede | Ne | Sonuç |
| --- | --- | --- |
| EVDS grup | bie_finhestnks1311 (ZP5–ZP8, ZP27–ZP30) | açıldı; vadesiz/vadeli var, vade dilimi yok |
| EVDS grup | bie_hpbitablo3 (3.9–3.11) | açıldı; resmî vadesiz/vadeli TL, GY kapsamı |
| EVDS grup | bie_mevdvade, bie_mevvade, bie_mevduatvade, bie_vademev, bie_mkvade, bie_pbvade, bie_hpbvade, bie_tlmevvade, bie_vadedag, bie_mevdagilim, bie_bddkmev, bie_bddkvade, bie_mbvade, bie_pbmv, bie_mevduatvadeli | boş (15 kod) |
| EVDS grup | bie_zorundth | açıldı; ZK'ya tabi DTH 1 ay altı/üstü, sektör toplamı |
| TCMB | dthvade.html | sektör vade dilimi, tür çaprazı yok |
| BDDK | Aylık bülten: Mevduat Türler İtibarıyla / Vade İtibarıyla | ayrı tablolar, çapraz yok |
| Muhasebat | /portal/v2 pages ×3, posts arama | GFSM sayfaları dosya vermiyor; 320/103 konsolide bakiye yok |
| GİB | Eylül 2025 Mizan_Son_Duzey.pdf | kurum düzeyi 103/320; MY değil |
| Sayıştay | HMB 2021 denetim raporu | 320/103 gün bulgusu yok |
| Sayıştay | Adana BB 2024 | 320 bekleme gün tablosu; belediye, MY değil |

Tekrar: `python3 vadeli_kalicilik.py`. Dosyalar: `vadeli_kalicilik.csv`, `vadeli_kalicilik_sonuc.json`.
