# Adım 4.5: yeni para birimine geçiş (plasebo)

Çalıştır: `python3 adim45_para_birimi.py`. Çıktı: `adim45.csv`. Adım 4 ile 5 arasında; adım 4 çıktısını okur, adım 5 girdisine dokunmaz.

## Plasebo ne demek

Tüm TL değerleri sabit bir oranla (örnek: 1 yeni birim = 1.000 eski TL) yeni birime çevrilir; gerçek bir şey değişmez. Modelde bunun karşılığı: oranlar aynı kalır, parasal kalemler yalnız ölçek alır. Adım 1-5 çıktılarından beş oran çevirmeden önce ve sonra hesaplandı; en büyük fark 1.1e-16 (kayan nokta düzeyi). Bu denklik **aritmetik gereğidir**: modelde para yanılsaması, yuvarlama enflasyonu veya fiyat belirleme alışkanlığı yok, dolayısıyla etki tanım gereği sıfırdır. Gerçekte bu terimler vardır ve yeni para birimi plasebo olmayabilir; model bunu ölçmez.

| Oran | Çevirmeden önce | Sonra |
| --- | ---: | ---: |
| ortak/brüt (adım 1) | 0.258188 | 0.258188 |
| silinen/kredi ihtiyacı (adım 2) | 1.753272 | 1.753272 |
| duran faiz/S0 (adım 3) | 0.095328 | 0.095328 |
| prim/adres (adım 4) | 0.027342 | 0.027342 |
| HEKİS/piyasa kira (adım 5) | 0.859845 | 0.859845 |

## Tek gerçek terim: yürütme maliyeti (milyar TL, tek sefer)

- **A. Sıfır atma (YTL 2005 türü):** 0.39 – 3.62. Banknot basımı ≈ 10 milyon $ (2004 tahmini, Hürriyet; 'ek maliyet değil' denmişti) = 0.33 milyar TL (kur 32,87); yazılım kurum başına 20–100 bin $ (TCMB Başkan Yardımcısı aktarımı), kurum sayısı N bilinmiyor, 100–1.000 varsayım: 0.07 – 3.29 milyar TL.
- **B. Yeni para birimi (euro türü tam değişim):** GSYH'nin %0,3–1,0'ı = 133.8 – 445.9 milyar TL (GSYH 2024: 44.587,2 milyar TL). Avro bölgesine girenlerde ortalama %0,3–0,5, Litvanya %0,5–0,7, Hırvatistan %0,5–1 (bir Bulgaristan analizinde aktarılan, ikincil kaynak, doğrulanmadı). Birleşik Krallık için kampanya kaynaklı %4,4 kullanılmadı.

Fayda sıfır (plasebo), maliyet pozitif: net etki = −maliyet. Adım 4 ve 5 ile toplanmaz (tek seferlik; öteki adımlar akış ve stok).

## Ne denmez

- 'Yeni para birimi bir şey değiştirmez' denmez; model değiştirmediğini varsayar, sınamaz.
- 'Geçiş maliyeti ölçüldü' denmez; A rejimi 2004 tahmini ve kurum sayısı varsayımı, B rejimi başka ülkelerin ikincil aktarımı.
- Yuvarlama, para yanılsaması ve fiyat belirleme alışkanlıkları modellenmedi; gerçek plasebo ihlali bu kanallardan gelir.
