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

Karar `kisitli_uygulanabilir` olmak için tabanların birlikte en az mevcut değerin **0.8**'i kadar olması gerekir (eşik skor 45).

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

## Okuma

- **Kararı zarar teorisi tabanı (0,70) belirliyor.** Yalnız onu sıfırlamak skoru 47,7 → 39,4 yapar ve kararı `dusuk_uygulanabilirlik`e çevirir. Eşik, zarar tabanının yaklaşık %50–75'i arasındadır.
- **Üretim tabanı (0,25) kararı değiştirmiyor:** sıfırlamak skoru 47,7 → 47,1 yapar; karar aynı kalır. Önceki yorumdaki 'asıl sorun 0,25' vurgusu yanlıştı.
- **Finans tabanı hiç bağlayıcı değil:** otomatik hesap (0,230) tabandan (0,22) büyük.
- **Eleştirel:** (1) Tabansız uç da 'doğru' değil: otomatik hesaptaki tavanlar (zarar için 0,08 × yatırım geliri gibi) de atanmış yüzdeler. (2) Zarar tabanının gerekçesi kodda ve veride yok; otomatik hesaptan yaklaşık 5,5 kat büyük. (3) Karar, tek bir elle yazılmış sayının (0,70) ±%25–50 bandında dönüyor; bu yüzden skor 47,7 bir ölçüm değil, bir kabuldür.
