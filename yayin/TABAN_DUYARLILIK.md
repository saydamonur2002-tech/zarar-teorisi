# Gerçekleşme tabanı duyarlılığı (`taban_duyarlilik.py`)

Gerçekleşme = min(1, max(taban, otomatik)) × politika katsayısı (0,95). Otomatik = katman USD tavanı ÷ beklenen iyileşme (USD). Tabanlar `gerceklik_capa.json` içinde elle yazılmış değerlerdir; `gerceklik_capa_senkron.py` yalnız USD çapalarını günceller, tabanlara dokunmaz. Her satır, tabanları ölçeklenmiş halde tüm zincirin (`run_all`) kararlı duruma kadar yeniden koşusudur.

Mevcut tabanlar: zarar teorisi 0.7, üretim 0.25, finans 0.22, yaşam maliyeti 0.28 (yaşam maliyeti bu taramada sabit).

## Üç taban birlikte ölçeklenince

| Taban çarpanı | Zarar gerçekleşme | Üretim gerçekleşme | Finans gerçekleşme | TR net 10y (C) | Skor | Karar |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0.0 | 0.1206 | 0.1843 | 0.2186 | -16.039 | 38.8 | dusuk_uygulanabilirlik |
| 0.1 | 0.1206 | 0.1843 | 0.2186 | -16.039 | 38.8 | dusuk_uygulanabilirlik |
| 0.2 | 0.133 | 0.1843 | 0.2186 | -15.982 | 39.0 | dusuk_uygulanabilirlik |
| 0.3 | 0.1995 | 0.1843 | 0.2186 | -15.677 | 40.0 | dusuk_uygulanabilirlik |
| 0.4 | 0.266 | 0.1843 | 0.2186 | -15.372 | 41.1 | dusuk_uygulanabilirlik |
| 0.5 | 0.3325 | 0.1843 | 0.2186 | -15.067 | 42.1 | dusuk_uygulanabilirlik |
| 0.6 | 0.399 | 0.1843 | 0.2186 | -14.762 | 43.0 | dusuk_uygulanabilirlik |
| 0.7 | 0.4655 | 0.1843 | 0.2186 | -14.457 | 44.1 | dusuk_uygulanabilirlik |
| 0.8 | 0.532 | 0.19 | 0.2186 | -14.14 | 45.1 | kisitli_uygulanabilir |
| 0.9 | 0.5985 | 0.2138 | 0.2186 | -13.785 | 46.4 | kisitli_uygulanabilir |
| 1.0 | 0.665 | 0.2375 | 0.2186 | -13.429 | 47.7 | kisitli_uygulanabilir |

Üç taban birlikte ölçeklenince karar `kisitli_uygulanabilir` olmak için çarpan en az **0.8** olmalı (0,1 adımlı tarama; skor 45'e yaklaşık 0,79 civarında iniyor, bu ölçekte ayrıca koşulmadı).

## Tabanlar tek tek ölçeklenince

| Katman | Taban çarpanı | Gerçekleşme (o katman) | TR net 10y (C) | Skor | Karar |
| --- | ---: | ---: | ---: | ---: | --- |
| zarar_teorisi | 0.0 | 0.1206 | -15.926 | 39.4 | dusuk_uygulanabilirlik |
| zarar_teorisi | 0.25 | 0.1663 | -15.716 | 40.1 | dusuk_uygulanabilirlik |
| zarar_teorisi | 0.5 | 0.3325 | -14.954 | 42.6 | dusuk_uygulanabilirlik |
| zarar_teorisi | 0.75 | 0.4988 | -14.191 | 45.1 | kisitli_uygulanabilir |
| uretim_ic_akis | 0.0 | 0.1843 | -13.542 | 47.1 | kisitli_uygulanabilir |
| uretim_ic_akis | 0.25 | 0.1843 | -13.542 | 47.1 | kisitli_uygulanabilir |
| uretim_ic_akis | 0.5 | 0.1843 | -13.542 | 47.1 | kisitli_uygulanabilir |
| uretim_ic_akis | 0.75 | 0.1843 | -13.542 | 47.1 | kisitli_uygulanabilir |
| finans_katman | 0.0 | 0.2186 | -13.429 | 47.7 | kisitli_uygulanabilir |
| finans_katman | 0.25 | 0.2186 | -13.429 | 47.7 | kisitli_uygulanabilir |
| finans_katman | 0.5 | 0.2186 | -13.429 | 47.7 | kisitli_uygulanabilir |
| finans_katman | 0.75 | 0.2186 | -13.429 | 47.7 | kisitli_uygulanabilir |

## Zarar teorisi tabanı: eşik çevresinde ince tarama (mutlak taban değeri)

| Zarar tabanı | Uygulanan zarar oranı | Skor | Karar |
| ---: | ---: | ---: | --- |
| 0.5 | 0.475 | 44.8 | dusuk_uygulanabilirlik |
| 0.51 | 0.4845 | 44.9 | dusuk_uygulanabilirlik |
| 0.513 | 0.4874 | 45.0 | kisitli_uygulanabilir |
| 0.52 | 0.494 | 45.0 | kisitli_uygulanabilir |
| 0.53 | 0.5035 | 45.2 | kisitli_uygulanabilir |

Karar, zarar tabanı **0.513** ve üstündeyken duruyor (0,51'de skor 44,9 ile düşüyor). 0,513 / 0,70 = %73; marj (0,70 − 0,513) / 0,70 = **%27**. 0,70'i 0,513'ün altına çekmek skoru 45'in altına indirir.

## Okuma

- **Kararı zarar teorisi tabanı (0,70) belirliyor.** Yalnız onu sıfırlamak skoru 47,7 → 39,4 yapar ve kararı `dusuk_uygulanabilirlik`e çevirir; eşik 0,513'tür.
- **Üretim tabanı (0,25) kararı değiştirmiyor:** sıfırlamak skoru 47,7 → 47,1 yapar; karar aynı kalır.
- **Finans tabanı hiç bağlayıcı değil:** otomatik hesap (0,230) tabandan (0,22) büyük.
- **Eleştirel:** (1) Tabansız uç da 'doğru' değil: otomatik hesaptaki tavanlar (zarar için 0,08 × yatırım geliri gibi) de atanmış yüzdeler. (2) Zarar tabanının gerekçesi kodda ve veride yok; otomatik hesaptan yaklaşık 5,5 kat büyük. (3) 47,7, 45 çizgisinin 2,7 puan üstünde ve bu fark tek atanmış sayıya (0,70) bağlı; marjı %27. Skor bir ölçüm değil, bir kabuldür.
