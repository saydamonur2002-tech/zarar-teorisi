# EVDS kod ve birim doğrulaması

Doğrulama çekimidir. Katsayı yok. Eksik kod, tanım veya birim için **doğrulanmadı** yazıldı. Kod uydurulmadı.

Çekim: EVDS3 `POST https://evds3.tcmb.gov.tr/igmevdsms-dis/fe`, anahtarsız. `frequency=5` (bu uçta aylık), `aggregationTypes=last`, `groupSeperator=false`, `01-01-1950`–`30-09-2026`. Dönüş 921 ay (`1950-01`…`2026-09`). Seri adları `serieList` (`type=json`). Boş ay, ilk dolu ay ile son dolu ay arasında değeri olmayan aydır. Haftalık ve iş günü serilerinde ay hücresi, ayın son gözlemidir. `TP.DK.USD.A.YTL`, `TP.MK.LON.YTL` ve iki faiz kodunun varsayılan toplulaştırması `avg`; bu çekimde `last` kullanıldı.

2003’ten önce başlayan seriler tabloda ayrıca yazıldı.

## Tablo

| kod | tam ad | birim | başlangıç | son | n | boş ay | kapsam | durum |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TP.AB.C1 | Altın (Milyon ABD Doları) | Milyon ABD Doları. Kaynak seri adı; EN adı `Gold (Million USD)`. `bie_abres2` metaveri bağlantısı yok. Başka birim veren sayfa bulunamadı. | 1987-12 (2003 öncesi) | 2026-09 | 466 | 0 | TCMB brüt altın rezervi. Grup haftalık (Cuma). Net değil. | doğrulandı |
| TP.AB.C2 | Döviz (Milyon ABD Doları) | Milyon ABD Doları. Aynı kaynak. EN adı `Foreign Exchange (Million USD)`. | 1987-12 (2003 öncesi) | 2026-09 | 466 | 0 | TCMB brüt döviz. Haftalık (Cuma). Swap düşülmüş net rezerv değil. | doğrulandı |
| TP.AB.A02 | A.1 DIŞ VARLIKLAR | Bin TL. AB Metaveri 2025, son güncelleme 18.02.2026: parasal büyüklük Bin TL. Tablo adı: Merkez Bankası Analitik Bilanço (Bin TL) (İş Günü). | 1980-12 (2003 öncesi) | 2026-09 | 506 | 44 | TCMB analitik bilanço dış varlıklar: altın, efektif, yurtdışı banka dövizi ve diğer döviz alacakları. İş günü. Net döviz varlığı değil. | doğrulandı |
| TP.AB.A10 | P.1 TOPLAM DÖVİZ YÜKÜMLÜLÜKLERİ | Bin TL. Aynı metaveri. | 1980-12 (2003 öncesi) | 2026-09 | 506 | 44 | TCMB döviz finansman kaynakları. İş günü. Swap düşülmüş net rezerv değil. | doğrulandı |
| TP.REZVARPD.K11 | 1.1.4.1.(Saf) Milyon Troy Ons | Seri adı: milyon troy ons. EN adı: `Volume in Millions of Fine Troy Ounces`. URL metaveri 18/12/2025: tüm değişkenler milyon ABD doları. | 2000-08 (2003 öncesi) | 2026-09 | 314 | 0 | Uluslararası rezervler ve döviz likiditesi. Sektör: TCMB ve merkezi yönetim. Altın kalemi, TCMB’ye ait bar ve külçe; menkul kıymet ve altın piyasa fiyatıyla. Bu satır miktar. Net ton değil. | çelişkili |
| TP.SWAPTEKTAR.TOTALSTOKALIMYONLU | 19.TOPLAM - STOK (Alım Yönlü) | doğrulanmadı. Adında birim yok. Grup metaveri bağlantısı yok. Koddaki `USDTUTAR` birim cümlesi değil. | 2021-01 | 2026-09 | 69 | 0 | TCMB taraflı swap, alım yönlü toplam stok. İş günü. Ton değil. | doğrulanmadı |
| TP.SWAPTEKTAR.SWAPASTOKUSDTUTAR | 6.TCMB TL Karşılığı Altın Swap Piyasası – Stok | doğrulanmadı. Aynı gerekçe. | 2021-01 | 2026-09 | 69 | 0 | TL karşılığı altın swap piyasası stoku. İş günü. Ons veya ton değil. | doğrulanmadı |
| TP.MK.LON.YTL | 1 Ons Altın Londra Satış Fiyatı (ABD Doları/Ons) | ABD Doları/Ons. Kaynak seri adı. Kodun `YTL` eki birim değil. | 1973-12 (2003 öncesi) | 2026-05 | 586 | 44 | Ankara Kuyumcular ve Saatçiler Odası, serbest piyasa, aylık. TCMB bilançosu değil. | doğrulandı |
| TP.DK.USD.A.YTL | (USD) ABD Doları (Döviz Alış) | 1 ABD doları karşılığı Türk lirası, döviz alış. Kaynak: Gösterge Niteliğindeki Kurlar, 2 Ocak 2015 yöntem cümlesi. | 1950-01 (2003 öncesi) | 2026-09 | 921 | 0 | TCMB gösterge döviz alış. Günlük; ay = ayın son gözlemi. Birim cümlesi 2 Ocak 2015 yöntemine aittir. 1950–2014 için aynı sayfada ayrı birim cümlesi yok. Ham `SERIE_NAME` çift boşlukludur. | doğrulandı |
| TP.KM.F19 | 6. DÖVİZ TEVDİAT HESAPLARI | Bin TL. APB metaveri 29/11/2024: DDKKM ve TL KKM hariç tüm değişkenler Bin TL. | 1986-01 (2003 öncesi) | 2026-08 | 488 | 0 | Mevduat bankaları, tür tablosu. Yurtiçi şubeler; yurtiçi sektörler ve yerleşik olmayanlar. Yalnız yerleşik diye yazılmadı. | doğrulandı |
| TP.KM.F22 | 7.KIYMETLİ MADEN DEPO HESAPLARI (YP) | Bin TL. Aynı APB cümlesi. EN etiket `PRECIOUS STONES`. | 1986-01 (2003 öncesi) | 2026-08 | 488 | 0 | Kıymetli maden depo hesapları. Yalnız altın değil. Gram değil. (YP) hesabın TL karşılığı. | doğrulandı |
| TP.KM.F35 | 9. TOPLAM | Bin TL. Aynı APB cümlesi. | 1986-01 (2003 öncesi) | 2026-08 | 488 | 0 | Tür tablosunun toplamı. DTH (F19), kıymetli maden (F22) ve bankalararası (F25) bu toplamın kalemleri. | doğrulandı |
| TP.MT210AGS.TRY.MT04 | 1 Yıla Kadar Vadeli (TL Mevduat, Stok,%) | Yüzde. Kaynak seri adı. | 2000-06 (2003 öncesi) | 2026-08 | 315 | 0 | Mevduat bankaları, stok faiz, 1 yıla kadar TL mevduat. Tam 12 ay vade değil. | doğrulandı |
| TP.MT210AGS.USD.MT04 | 1 Yıla Kadar Vadeli (ABD doları Mevduat, Stok, %) | Yüzde. Kaynak seri adı. | 2000-06 (2003 öncesi) | 2026-08 | 315 | 0 | Mevduat bankaları, ABD doları mevduat stok faizi. DTH sepeti değil. | doğrulandı |
| konu: net altın, ton | — | — | — | — | — | — | Taranan rezerv, analitik bilanço, swap ve altın gruplarında bu adda seri yok. K11 ton değil. | bulunamadı |
| konu: swap düşülmüş net döviz rezervi | — | — | — | — | — | — | Bu adda seri yok. C2, A02, A10 ve swap stokları ayrı kalemdir; farkları bu kodun yerine yazılmadı. | bulunamadı |
| konu: altın mevduatı, gram | — | — | — | — | — | — | Yayımlanmış gram stok kodu yok. Haftalık metaveri, parite hesabında bankaların altını gram bildirdiğini yazar; bu bir stok serisi değildir. HPBITABLO4 satırları ABD doları karşılığıdır. | bulunamadı |
| TP.KM.G46 | 3.ALTIN DEPO HESAPLARI (YP) | Bin TL. Aynı APB cümlesi. EN adı `3.GOLD DEPOSIT ACCOUNTS (FX)`. | 1986-01 (2003 öncesi) | 2026-08 | 488 | 0 | Mevduat bankaları, vade tablosu, altın depo hesaplarının TL karşılığı. Gram değil. | doğrulandı |
| TP.KM.G01 | 1.TL MEVDUAT | Bin TL. Aynı APB cümlesi. EN adı `1.TRY DEPOSITS`. | 1986-01 (2003 öncesi) | 2026-08 | 488 | 0 | Mevduat bankaları, vade tablosu TL mevduat. Bankalararası ayrı kalemdir (G43, TL+YP). DTH ayrı kalemdir (G49). | doğrulandı |
| TP.HPBITABLO3.1 | 1.TOPLAM TL MEVDUAT | Bin TL. Haftalık para ve banka metaverisi: Türk Lirası Mevduatlar, Bin TL. Metaveri Eylül 2026. | 2024-06 | 2026-09 | 28 | 0 | Bankacılık sektörü TL mevduatı, yurt içi şubeler. Haftalık (Cuma). Metaveri, diğer verilerin 28 Haziran 2024’te başladığını yazar. G01 ile aynı stok değildir. | doğrulandı |

## Üç cümle

Bilanço dış varlık ve döviz yükümlülüğü (A02, A10; Bin TL; 1985-01’den 2026-09’a boşluksuz), brüt altın ve döviz (C1, C2; milyon ABD doları; 1987-12’den, n=466) ve TL mevduat stoku (TP.KM.G01; Bin TL; 1986-01’den, n=488) çekildi.

Swap ile düzeltilmiş net döviz rezervi, net altın tonu ve altın mevduatının gram stoku bulunamadı; altın depo hesaplarının TL karşılığı TP.KM.G46 olarak var (Bin TL, n=488), swap stokları 2021-01’de başlar ve birimleri doğrulanmadı.

En büyük belirsizlik K11 birimidir: URL metaverisi (18/12/2025) bütün değişkenleri milyon ABD doları sayar, seri adı milyon troy onstur; 2026-05 çekiminde K11=23,466 ve Londra ons fiyatı 4.591,85 ABD doları, çarpım 107.752,35 milyon ABD doları, aynı ay C1=105.991,9605 milyon ABD dolarıdır.

## Çekim notları

A02 ve A10 boş 44 ay, 1981–1984’ün Aralık dışı aylarıdır. Bu dört yıl yalnız Aralık doludur (1981-12, 1982-12, 1983-12, 1984-12). 1985-01’den 2026-09’a boş ay yoktur. Metaveri zaman kapsamı: 1980–1984 yıllık, 1985–1989 aylık, 15.09.1989’dan itibaren günlük.

Londra ons boş 44 ay, 1974–1977’nin Aralık dışı aylarıdır. Aylık dizi 1978-01’de başlar. Son dolu ay 2026-05’tir.

APB metaverisi iki başlangıç cümlesi taşır: veriler Ağustos 1986’dan başlar; karşılaştırılabilir seriler Ocak 1986’dan başlar. F19, F22, F35, G01 ve G46 çekimi 1986-01’de başlar, 2026-08’de biter.

K11 ile aynı tablodaki TP.REZVARPD.K10 adı `1.1.4.Altın (Altın Mevduatlarını ve Eğer Uygunsa Altın Swaplarını İçeren)`dir. 2026-05 K10=105.992; 2026-09 K10=107.093, C1=109.640,4329. İki satır her ay eşit değildir. K10 bu tablonun istenen kodu değildir; K11 çelişkisini ayırmak için okundu.

2026-05 altın swap stoku 0, toplam alım yönlü swap stoku 3.650’dir. Bu düzeyler birim kanıtı sayılmadı.

`TP.DK.USD.A.YTL` ham adı `(USD)  ABD  Doları  (Döviz  Alış)` şeklindedir. Tabloda çift boşluklar tek boşluğa indirildi.

## Kaynak sayfaları

- Analitik bilanço: `https://tcmb.gov.tr/wps/wcm/connect/02ba6315-cbb8-4344-9d0d-b529fe778ef0/AB+Metaveri_2025.pdf` (18.02.2026).
- Uluslararası rezervler: `http://www.tcmb.gov.tr/wps/wcm/connect/d0ccd8ae-089b-4d21-ab39-569c0425cbeb/URLMetaveri.pdf` (18/12/2025).
- Aylık para ve banka: `http://www.tcmb.gov.tr/wps/wcm/connect/f3ad1a37-6d59-4a0b-b0d7-09b51cd7a73f/MetaveriAPBI2018.pdf` (29/11/2024). `bie_kmmbtmv` ve `bie_kmmbgmv` bu dosyaya bağlıdır.
- Haftalık para ve banka: `https://www.tcmb.gov.tr/wps/wcm/connect/af2e86c3-6410-45ce-9eb6-1770e459b528/Metaveri.pdf` (Eylül 2026).
- Gösterge kur: `https://www.tcmb.gov.tr/wps/wcm/connect/tr/tcmb+tr/main+menu/temel+faaliyetler/doviz+efektif/doviz+ve+efektif+piyasalari/gosterge+niteligindeki+kurlar`.
