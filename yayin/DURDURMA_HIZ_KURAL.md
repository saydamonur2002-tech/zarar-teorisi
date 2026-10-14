# Durdurma hızını belirleyen ölçülebilir kurallar

Beş halka katmandır, kullanılmadı; zarar aktarımı stok-akışta (akış = sabit kayıp + boşalma·(1−d)). Kapasite tavanı gözlenen katman gerçekleşme oranlarından; 'tüm katmanlar en iyi katman kadar hızlı' iyimser üst sınırdır. Kurallar yön ve gerek/yeter karşılaştırması verir, tahmin vermez.

Tek durum d; hız sabiti b = 0.02439 (m = 1 kalibre C yolunu üretir; RMSE 0.0096).

## R1 Finansman gereği: rezerv 10 yıl dayansın diye gereken hız çarpanı m*

bop_merkez_rant: 1.0, mal_net_ticaret: 4.74, tum_havza_rant: 5.99

## R2 Gözlenen kapasite (katman gerçekleşme oranlarından)

Katman oranları: zarar_teorisi 0.665, uretim_ic_akis 0.2375, finans_katman 0.2186; ortalama 0.3737.
Kapasite çarpanı: en_kotu_katman 0.585, ortalama 1.0, en_iyi_katman 1.78

## R3 Mali alan: faiz/gelir 0.167 (2026-08); kapasite (1 − faiz/gelir) ile ölçeklenir

| Senaryo | m kapasite | faiz/gelir son yıl | mali alan çarpanı | d(son) | Rezerv tükenme (BoP / mal / rant) |
| --- | ---: | ---: | ---: | ---: | --- |
| en_kotu_katman__faiz_sabit | 0.585 | 0.1666 | 1.0 | 0.1339 | — / 2030 / 2029 |
| ortalama__faiz_sabit | 1.0 | 0.1666 | 1.0 | 0.2188 | — / 2030 / 2029 |
| en_iyi_katman__faiz_sabit | 1.78 | 0.1666 | 1.0 | 0.3584 | — / 2030 / 2029 |
| en_kotu_katman__faiz_veri_egimi | 0.585 | 0.3185 | 0.818 | 0.1212 | — / 2030 / 2029 |
| ortalama__faiz_veri_egimi | 1.0 | 0.3185 | 0.818 | 0.199 | — / 2030 / 2029 |
| en_iyi_katman__faiz_veri_egimi | 1.78 | 0.3185 | 0.818 | 0.3286 | — / 2030 / 2029 |

## Sonuç

Rezervin dayanması için gereken hız (mal köprüsü) m* = 4.74, rant köprüsü m* = 5.99; gözlenen en iyi katman hızı m = 1.78. Ölçülebilir kurallarla 4–5 kat hızı destekleyen bir koşul yok: açık, kapasite ile gereğin farkıdır.
Dışarıda bırakılan kurallar (dönüt, güven, tampon süresi, ücret–kredi bağı, başarı tanımı) ölçülemediği için bu sonuca girmez; açılırlarsa hız artabilir, ama büyüklüğü bu verilerle söylenemez.

