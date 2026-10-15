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

Üç taban birlikte ölçeklenince karar `kisitli_uygulanabilir` olmak için çarpan en az **0.8** olmalı (0,1 adımlı tarama; ince tarama aşağıda).

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

## Üç taban birlikte: eşik çevresinde ince tarama

| Çarpan (mevcut değerin yüzdesi) | Zarar | Üretim | Finans | Skor | Karar |
| ---: | ---: | ---: | ---: | ---: | --- |
| %70 | 0.49 | 0.175 | 0.154 | 44.1 | dusuk_uygulanabilirlik |
| %71 | 0.497 | 0.1775 | 0.1562 | 44.2 | dusuk_uygulanabilirlik |
| %72 | 0.504 | 0.18 | 0.1584 | 44.3 | dusuk_uygulanabilirlik |
| %73 | 0.511 | 0.1825 | 0.1606 | 44.4 | dusuk_uygulanabilirlik |
| %74 | 0.518 | 0.185 | 0.1628 | 44.5 | dusuk_uygulanabilirlik |
| %75 | 0.525 | 0.1875 | 0.165 | 44.5 | dusuk_uygulanabilirlik |
| %76 | 0.532 | 0.19 | 0.1672 | 44.7 | dusuk_uygulanabilirlik |
| %77 | 0.539 | 0.1925 | 0.1694 | 44.8 | dusuk_uygulanabilirlik |
| %78 | 0.546 | 0.195 | 0.1716 | 44.9 | dusuk_uygulanabilirlik |
| %79 | 0.553 | 0.1975 | 0.1738 | 45.0 | kisitli_uygulanabilir |
| %80 | 0.56 | 0.2 | 0.176 | 45.1 | kisitli_uygulanabilir |

Üç taban birlikte ölçeklenince karar, çarpan **0.79** (yani %79) ve üstündeyken duruyor; marj **%21**. Yalnız zarar tabanı için eşik %73 (marj %27); üretim ve finans tabanı tek başına kararı hiçbir noktada değiştirmiyor. Birlikte düşürünce eşik yükselir (daha dar marj), çünkü üretim tabanı (otomatik 0,194'ün üstünde olduğu sürece bağlayıcı) skoru birkaç onda puan aşağı çeker.

## Bu sayılar neyi temsil ediyor?

- **Katman yığını:** TR net kaybı, C yolundan başlayıp üç adımda iyileşir: zarar çözümü (C → C_zarar_cozum), üretim iç akışı, finans katmanı. Modelin her adım için hesapladığı iyileşme (Δ): zarar 4,587 vekil (≈ 11.876 mn $), üretim 8,491 (≈ 21.984 mn $), finans 3,162 (≈ 8.187 mn $); 1 vekil ≈ 2.589,12 mn $.
- **Gerçekleşme oranı:** Her adımın Δ'sinin TR net'e gerçekten yansıyan payı. TR net(10y) = C + Δ_zarar·r_z + Δ_üretim·r_ü + Δ_finans·r_f. Yani "model bu kadar iyileşme hesapladı, politikanın bunun yüzde kaçı gerçekleşir" varsayımı.
- **Otomatik oran:** Katmanın 10 yıllık USD iyileşme tavanı ÷ Δ (USD). Tavanlar: zarar 1.507 mn $ (yatırım geliri giderinin %8'i), üretim 4.264 mn $ (Drive modeli, orta reform net iyileşme), finans 1.884 mn $ (yatırım geliri giderinin %10'u). Sonuç: zarar 0,127, üretim 0,194, finans 0,230. Bu, "mümkün olan en çok bu kadar kazanılır" tavanından türeyen orandır.
- **Taban:** Otomatik oran ne derse desin gerçekleşmenin en az bu orana çıkacağı **varsayımı** (`max(taban, otomatik)`). Zarar 0,70 = zarar çözümü adımının en az %70'i, üretim 0,25 = en az %25'i, finans 0,22 = en az %22'si gerçekleşir. Son uygulanan oran bunun ×0,95 (politika katsayısı) halidir: 0,665 / 0,2375 / 0,2186.
- **Dolayısıyla:** Taban bir "uygulama başarısı alt sınırı" varsayımıdır; ölçülmüş bir değer değil ve nereden geldiği kayıtlı değil. Zarar tabanı, otomatik tavandan türeyen orandan yaklaşık 5,5 kat büyüktür; yani model zarar adımının tavanın izin verdiğinden çok daha fazlasının gerçekleşeceğini varsayıyor.
- **Eşiklerin anlamı:** Skor 45'in altına inince karar `kisitli_uygulanabilir`'den `dusuk_uygulanabilirlik`'e düşer. Zarar tabanı 0,70'ten 0,513'e (%73) inerse ya da üç taban birlikte %79'a inerse bu olur. Yani bu uygulama-başarısı varsayımlarının yaklaşık beşte biri kadar iyimser olması kararı bozar.

## Okuma

- **Kararı zarar teorisi tabanı (0,70) belirliyor.** Yalnız onu sıfırlamak skoru 47,7 → 39,4 yapar ve kararı `dusuk_uygulanabilirlik`e çevirir; eşik 0,513'tür.
- **Üç taban birlikte eşik %79, tek başına zarar tabanı eşiği %73.**
- **Üretim tabanı (0,25) kararı değiştirmiyor:** sıfırlamak skoru 47,7 → 47,1 yapar; karar aynı kalır.
- **Finans tabanı hiç bağlayıcı değil:** otomatik hesap (0,230) tabandan (0,22) büyük.
- **Eleştirel:** (1) Tabansız uç da 'doğru' değil: otomatik hesaptaki tavanlar (zarar için 0,08 × yatırım geliri gibi) de atanmış yüzdeler. (2) Zarar tabanının gerekçesi kodda ve veride yok; otomatik hesaptan yaklaşık 5,5 kat büyük. (3) 47,7, 45 çizgisinin 2,7 puan üstünde ve bu fark tek atanmış sayıya (0,70) bağlı; marjı %27. Skor bir ölçüm değil, bir kabuldür.
