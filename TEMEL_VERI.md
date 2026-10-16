# Temel veri envanteri

Üç cümle. Envanterdeki 24 bulgu satırının 13'ü sütun değişimine duyarlıdır; bunlar geçersiz sayılmadı, ölçüme bağlı diye işaretlendi. İşareti dönenler, dört satırı dolu çekirdek alt kümesi, net finansman medyanı ve SANKO'ya karşı vergi öncesi farkıdır. Temel tablo 630 hisse ve 2016–2023 için 5.040 satırdır; analiz evreni 125 firma ve 1.000 satırdır, KAP cari satış 2022'de 125/125, 2016'da 112/125, 2017–2021'de 0/625 doludur. En büyük açık 2017–2021 KAP yüzünün çekilmemiş olmasıdır: 2023 XI_29 satışı, yayımlanmış 100'de 97/100 firmada 2024 bildiriminin karşılaştırmalı sütununa eşittir, bu sütunun satın alma gücü dipnotu okunmadı.

Sayılar bu turda `marj_ham.csv`, KAP önbelleği ve EVDS'ten yeniden hesaplandı. Önceki metindeki sayı, yeniden üretilen sayıdan ayrılır. Medyan, ortalamanın yerine konmaz. İki sütundan biri doğru ilan edilmez.

## 1. Bulgu envanteri

Satış sütunu kısaltmaları: **XI** = `marj_ham.csv` XI_29 kalem 3C. **KAP cari** = yıllık bildirimin cari sütunu, pencere yıl+1 Ocak–Eylül, penceredeki son yıllık. **KAP 2022 karşılaştırmalı** = 2023 yıllık bildiriminin önceki sütunu; 2022 XI bu sütuna eşittir (önceki tur: tekstil 32/32, yayımlanmış 100'de 96/99). **KAP 2023 karşılaştırmalı** = 2024 yıllık bildiriminin önceki sütunu; 2023 XI bu sütuna eşittir (bu tur, aşağıda).

Marj değişimi, aynı firmada (sonraki marj − önceki marj) × 100, sonra bu farkların medyanıdır. Reel satış, EVDS `TP.GENENDEKS.T1` yıl ortalamasıyladır: 2016 = 280,84583333333336, 2022 = 967,7108333333334.

| # | Bulgu | Satış sütunu | Marj ve KAP satırı | Örneklem | Sütuna duyarlı | Sütun değişince |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Reel satış medyanı %279,2 (oran 2,7918; n=100; p25 2,064; p75 4,508) | 2016 XI, 2022 XI (= 2023 karşılaştırmalısı) | Satış düzeyi. Marj yok | Yayımlanmış ilk 100, KRDMA ve KRDMB dahil | Evet, ölçüme bağlı | Eşli KAP cari / KAP cari, n=94: medyan %141,3 (oran 1,4132; p25 0,721; p75 2,201). Büyüme işareti durur, medyan küçülür. Önceki metindeki %138,1 (oran 1,3809; n=100), 2016 paydası XI ve 2022 payı KAP cari olan karışık sütundur; bu turda ana ölçü değildir |
| 2 | Çekirdek değişim medyanı −0,98 puan (n=100; p25 −5,98; p75 +3,25) | 2016 XI, 2022 XI | Çekirdek = (3D + 3DA + 3DB + 3DC) / 3C. KAP: GrossProfit, MarketingExpense, AdministrativeExpense, ResearchAndDevelopmentExpense. Boş satır sıfırlanmadı | Yayımlanmış ilk 100 | Evet, ölçüme bağlı | Eşli ve dört satırı dolu n=46: XI medyan −3,21 (p25 −6,05; p75 +2,92), KAP cari +4,64 (p25 +0,94; p75 +8,78). İşaret döner. Kalan 54 firmanın KAP çekirdeği veri yok. Önceki +4,04 (n=95) bu önbellekte üretilmedi. Pazarlama dolu ve boş Ar-Ge sıfırlanırsa n=89, XI −1,40, KAP +4,39; işaret yine döner. Sıfırlama bu tabloda kullanılmadı |
| 3 | Faaliyet değişim medyanı −0,1 puan | 2016 XI, 2022 XI | 3DF / 3C. Diğer faaliyet geliri ve gideri dahil. KAP'ta bu satır çekilmedi | Yayımlanmış ilk 100 | Bilinmiyor | KAP faaliyet satırı veri yok |
| 4 | Vergi öncesi değişim medyanı +2,14 puan (n=100; p25 −3,80; p75 +12,33) | 2016 XI, 2022 XI | 3I / 3C. KAP: ProfitLossBeforeTax / Revenue | Yayımlanmış ilk 100 | Evet, ölçüme bağlı | Eşli n=94: XI +2,23 (p25 −3,11; p75 +13,59), KAP cari +6,53 (p25 +0,08; p75 +16,36). İşaret durur, medyan büyür. Kanonik eşli n=92: XI +2,14, KAP +6,23. İşaret durur |
| 5 | Net finansman değişim medyanı +2,79 puan (n=100; p25 −2,68; p75 +9,53) | 2016 XI, 2022 XI | (3HB + 3HC) / 3C. KAP: (FinanceIncome + FinanceCosts) / Revenue. Gider XI'de negatif | Yayımlanmış ilk 100 | Evet, ölçüme bağlı | Eşli n=73: XI +2,88 (p25 −2,32; p75 +9,43), KAP cari −0,08 (p25 −2,37; p75 +2,95). İşaret döner. Kanonik eşli n=71: XI +2,87, KAP −0,12. İşaret döner |
| 6 | Net diğer faaliyet değişim medyanı −0,05 puan | 2016 XI, 2022 XI | (3DD + 3DE) / 3C. KAP satırı çekilmedi | Yayımlanmış ilk 100 | Bilinmiyor | Veri yok |
| 7 | Reel beta medyanı 0,95 | XI satış ve satışların maliyeti, 2017–2022, TÜFE yıl ortalaması | Beta, marj değil. 2022 satış ucu karşılaştırmalı sütun | Yayımlanmış ilk 100 | Evet, ölçüme bağlı | KAP satış ve maliyetle yeniden hesaplanmadı. Yeni sayı veri yok |
| 8 | 2016–2023 çekirdek değişim medyanı −0,68 puan (önceki metin −0,7; n=100) | 2016 XI, 2023 XI (= 2024 karşılaştırmalısı, Kardemir pay sınıfları hariç) | Çekirdek, satır 2 ile aynı | Yayımlanmış ilk 100 | Evet, ölçüme bağlı | Eşli KAP cari, dört satır dolu, n=45: XI −1,37, KAP −0,57. İşaret durur. Tam 100'ün KAP çekirdeği veri yok. Kanonik XI n=98 medyan −0,51 |
| 9 | 2022'den 2023'e nominal satış artışı medyanı %51,0 (oran 0,5097; n=100) | XI 2022 / XI 2023. İkisi de karşılaştırmalı sütun, farklı bildirim yılları | Satış düzeyi | Yayımlanmış ilk 100 | Evet, ölçüme bağlı | KAP cari 2023 / KAP cari 2022, n=99: medyan %92,0 (oran 0,9198). Büyüme işareti durur, medyan büyür. İki oran da tek fiyat yılı değildir: XI, 2024 karşılaştırmalısını 2023 karşılaştırmalısına böler; KAP cari, 2023 yüzünü 2022 nominal yüze böler |
| 10 | Sektör medyanları (örnek: gıda çekirdek +0,6, ulaştırma +18,1) | 2016 XI, 2022 XI | Çekirdek, faaliyet, vergi öncesi, net finansman | Ana sektör, n≥5 | Evet, ölçüme bağlı | KAP ile sektör medyanı yeniden hesaplanmadı. Yeni sayı veri yok |
| 11 | Holding çekirdek değişim medyanı +12 puan (n=25) | 2016 XI, 2022 XI | Çekirdek | Holding, ana analiz dışı | Bilinmiyor | Holding KAP yüzü bu turda çekilmedi |
| 12 | TCMB imalat çekirdek artışı yaklaşık +4 puan | TCMB sektör tablosu. KAP sütunu değil | TCMB kâr tanımı, XI çekirdeği değil | TCMB imalat | Hayır | Sütun değişimi bu sayıyı taşımaz. Bu sayıyı XI −0,98 ile yan yana koyan cümle, satır 2'ye bağlıdır |
| 13 | Fiyat çarpanı medyanı %485, miktar artığı medyanı %184 | XI nominal satış, sektör Yİ-ÜFE | Satış düzeyi. İki medyanın çarpımı nominal büyümeye eşitlenmedi | Yayımlanmış ilk 100 | Evet, ölçüme bağlı | KAP satışla yeniden hesaplanmadı. Yeni sayı veri yok |
| 14 | Tekstil Entegre vergi öncesi değişim medyanı +14,59 puan (n=18; p25 +5,01; p75 +43,66) | 2016 XI, 2023 XI | 3I / 3C | Tekstil Entegre, holding adlı ARSAN, DERHL, RALYH hariç. 18 firmanın 18'inde 2023 XI satışı, 2024 karşılaştırmalı satışa eşittir | Evet, ölçüme bağlı | Eşli KAP cari n=17: XI medyan +14,70, KAP medyan +14,27. İşaret dönmez, medyan yakın kalır. MAVI'nin 2016 KAP vergi öncesi yoktur |
| 15 | Tekstil Entegre çekirdek +2,21 (n=18; p25 −6,43; p75 +12,30) | 2016 XI, 2023 XI | Çekirdek | Aynı 18 | Evet, ölçüme bağlı | Dört KAP satırı iki yılda da dolu olan n=6: XI +0,38, KAP −1,92. İşaret bu altıda döner. n<8 olduğu için sektör karşılaştırması yazılmaz. Tam 18'in KAP çekirdeği veri yok |
| 16 | Tekstil Entegre faaliyet +9,29 (n=18; p25 +0,67; p75 +14,71) | 2016 XI, 2023 XI | 3DF / 3C | Aynı 18 | Bilinmiyor | KAP faaliyet satırı çekilmedi |
| 17 | Tekstil Entegre ham net finansman +13,00 (n=18; p25 +2,08; p75 +17,81) | 2016 XI, 2023 XI | (3HB + 3HC) / 3C | Aynı 18 | Bilinmiyor | 2023 KAP finansman satırı XBRL önbelleğinde yok. 2016–2022 penceresindeki 32 firma sonucu bölüm 5'tedir |
| 18 | Yararlanan çekirdek değişim medyanı +0,90 (n=45). SANKO −1,74. Medyanlar farkı +2,64 | 2016 XI, 2023 XI | Çekirdek | Teşvik listesi `tesvik_secilim.json`, yararlanan 45, yararlanmayan SANKO | Hayır, eşli alt kümede. SANKO farkı bilinmiyor | Dört satır dolu eşli n=29: XI medyan +1,14, KAP medyan +1,14 (fark 10⁻¹⁰ altında). SANKO'nun KAP çekirdeği kurulamadı, bir satır boş. +2,64 KAP çekirdekte veri yok |
| 19 | Yararlanan vergi öncesi değişim medyanı +2,69 (n=45). SANKO −2,80. Fark +5,48 | 2016 XI, 2023 XI | 3I / 3C | Aynı liste | Evet, ölçüme bağlı | Yararlanan eşli n=43: XI +2,69, KAP cari +2,84. İşaret durur. SANKO XI −2,80, KAP cari +4,94 (2023 yüzü idx 1284683, 10.05.2024; 2023 XI = 2024 karşılaştırmalısı idx 1399549, 03.03.2025). Fark, KAP cari sütununda yaklaşık −2,10 olur. İşaret döner |
| 20 | Bilinmeyen 54 firma yararlanmayan sayılınca vergi öncesi medyanlar farkı −1,22 | 2016 XI, 2023 XI | 3I / 3C | Yararlanan 45, kontrol 55 | Evet, ölçüme bağlı | Eşli KAP cari: yararlanan n=43 medyan +2,84, kontrol n=50 medyan +4,84, fark −1,99. İşaret eksi kalır, büyüklük değişir. Eşli XI farkı −1,63'tür; önceki −1,22 eşlenmemiş n=55 XI medyanındandır (kontrol XI medyan +3,91) |
| 21 | 2016–2019 yararlanan çekirdek değişim medyanı +1,22 (n=45) | XI 2016 ve XI 2019 | Çekirdek | Yararlanan 45 | Bilinmiyor | 2017, 2018 ve 2019 KAP yüzü çekilmedi |
| 22 | Kardemir A, B ve D tek konsolide tutardır | Grup satış KAP konsolide. XI pay sınıfı ölçeğindedir | Marj, ölçeklenince aynı kalır. Satış düzeyi kalmaz | KRDMA, KRDMB, KRDMD | Hayır, marj için. Satış düzeyi ayrı ölçektir | 2024 bildirimi tek indeks: 1402671, yayım 07.03.2025. XI satış / karşılaştırmalı satış: A 0,2108, B 0,1048, D 0,6844. 2016'da D için XI/KAP cari 0,6844. Kanonik satır KRDMD'dir; A ve B analiz dışıdır, yerlerine firma eklenmedi. Kanonik reel XI medyanı %272,8 (oran 2,7277; n=98) |
| 23 | 25 firma dipnotu: net kur medyanı +0,82, net faiz −1,19, net diğer −0,14 | Özgün bildirimin kendi dipnotu, 2016 ve 2022 | Dipnot satırı, XI kalemi değil | Dipnotu iki yılda kapanan 25 | Hayır | Sayı, tek bir bildirimin dipnotundadır. XI sütunuyla yeniden kurulmaz |
| 24 | Dört firma dipnot kırılımı: BOSSA, HATEK, RALYH, SASA | Bildirimin kendi hasılatı | Dipnot toplamı yüze kapananlar | n=4, sektör medyanı yazılmadı | Hayır | Kırılım, okunan bildirimin satırıdır |

Satır 2'de ham dosya, KAP'ta boş olan Ar-Ge'yi 0 tutuyor: yayımlanmış 100'ün 2016 ve 2022 firma-yıllarında bu ikili 88 kez sayıldı. Bu yüzden XI çekirdek n=100 kuruluyor, KAP sıkı çekirdek n=46'da kalıyor.

## 2. Tanım belgesi

Ana analizde kullanılan satış, KAP yıllık bildirimin cari sütunudur. Pencere, ilgili yılın ertesi takvim yılında 1 Ocak–30 Eylül, penceredeki son yıllık bildirimdir. İlk yayımlanan bildirim ayrıca işaretlenmedi. XI_29 ayrı kolondadır (`satis_xi29`). Karşılaştırmalı sütun ayrı kolondadır (`satis_kap_karsilastirmali`). İkisi de ana satışın yerine yazılmaz.

XI_29 kaynağı `marj_ham.csv`. Liste `marj_sirket_liste.csv`, 16 Ekim 2026. Bu dosyada KAP yayım tarihi yoktur.

2022 XI_29 satışı, 2023 yıllık bildiriminin karşılaştırmalı satışıdır. Bu kimlik önceki turda tekstil 32 firmanın 32'sinde ve yayımlanmış 100'ün okunan 96'sında kuruldu. Bu tur o kimliği yeniden sınamadı; 2022 karşılaştırmalı kolon, eldeki 2023 bildiriminden dolduruldu.

2023 XI_29 satışı, 2024 yıllık bildiriminin karşılaştırmalı satışıdır. Pencere 2025-01-01 … 2025-09-30, son yıllık. Yayımlanmış 100'de satış 97 eşit, 3 fark, 0 yok. Vergi öncesi 97 eşit, 3 fark. Üç fark KRDMA, KRDMB, KRDMD'dir; üçü de idx 1402671, yayım 07.03.2025 20:28:36. Kanonik 98'de satış 97 eşit, fark yalnız KRDMD ve oran 0,6844'tür. Tekstil 32'de satış 32/32 eşittir. SANKO satış ve vergi öncesi eşittir: idx 1399549, yayım 03.03.2025 23:24:47. 2024 gelir tablosunda okunan bildirimlerin sütun sayısı 2'dir (yayımlanmış 100'de 100/100).

Kanonik 97 firmada (2024 karşılaştırmalı satış) / (2023 cari satış) oranının medyanı 1,443787714184061'dir. EVDS `TP.GENENDEKS.T1` Aralık 2024 / Aralık 2023 = 2.684,55 / 1.859,38 = 1,443787714184298. İki sayı aynıdır. 79 firma, 1,4438'in 0,01 komşuluğundadır. THYAO, EREGL, ISDMR ve ENKAI'de oran 1,00'dır. Dipnot okunmadı. Medyanın endekse eşit olması, her satırın tek çarpanla düzeltildiği anlamına gelmez.

Marj tanımları, her iki sütunda aynıdır.

| Marj | XI_29 | KAP kavramı | Boş satır |
| --- | --- | --- | --- |
| Çekirdek | (3D brüt + 3DA pazarlama + 3DB genel yönetim + 3DC Ar-Ge) / 3C | GrossProfit, MarketingExpense, AdministrativeExpense, ResearchAndDevelopmentExpense, bölü Revenue | Pazarlama veya Ar-Ge boşsa çekirdek kurulmaz. Sıfır yazılmaz. `paz_bos` ve `arge_bos` ayrıdır. Gider artı geldiyse eksiye çevrilir |
| Faaliyet | 3DF / 3C | Bu turda çekilmedi | Veri yok |
| Vergi öncesi | 3I / 3C | ProfitLossBeforeTax / Revenue | Payda veya pay yoksa veri yok |
| Net finansman | (3HB + 3HC) / 3C | (FinanceIncome + FinanceCosts) / Revenue. Yıl json'undaki tutar × birim. XBRL `ISTENEN` listesinde finansman kavramı yoktur | İki kalemden biri yoksa veri yok |

Pay sınıfı. KRDMA ve KRDMB `analiz=disi_pay_sinifi`. Kanonik kod KRDMD. Üç sınıf aynı konsolide bildirimi paylaşır. XI tutarı grup toplamı değildir. Grup satışı için KAP konsolide kolon kullanılır. Yıllar arasında XI ölçeği ile KAP ölçeği karıştırılmaz.

Tablo türü. `tablo_turu`, gelir tablosundaki "Finansal Tablo Niteliği" hücresidir. "Konsolide Olmayan" bireyseldir. Ayrıştırıcı bu turda düzeltildi; 2016 ve 2023 için yeni çekilen indeksler bu ayrıştırıcıyladır. 2022 önbelleğinin bir kısmı eski ayrıştırıcıda kalmış olabilir. Eski kayıt, "Konsolide Olmayan"ı "Konsolide" diye kesmiş olabilir. 2022 tablo türü bu turda baştan okunmadı.

Holding (`grup=holding`) ve finans dışı (`grup=finans_disi`) tabloda durur, `analiz` alanı `disi_holding` veya `disi_finans`tır. Ana medyanlara girmezler.

Eksik hücre "veri yok"dur. Tahmin yoktur.

Birim. KAP yıl json'undaki tutar, bildirimdeki birimle çarpılır (1, 1.000 veya 1.000.000 TL). 2024 dosyasındaki `rev` ve `rev_prev` bu çarpım uygulanmış TL'dir.

## 3. Kapsam

| Kolon | Evren | n | Boş | Boş oranı |
| --- | --- | --- | --- | --- |
| Satır | Liste, 630 hisse × 8 yıl | 5.040 | — | — |
| `satis_xi29` | Tüm tablo | 5.040 | 1.208 | 0,240 |
| `satis_kap_cari` | Tüm tablo | 5.040 | 4.700 | 0,933 |
| `satis_kap_karsilastirmali` | Tüm tablo | 5.040 | 4.788 | 0,950 |
| `satis_xi29` | Analiz evreni | 1.000 | 13 | 0,013 |
| `satis_kap_cari` | Analiz evreni | 1.000 | 666 | 0,666 |
| `satis_kap_karsilastirmali` | Analiz evreni | 1.000 | 752 | 0,752 |
| `cekirdek_kap` | Analiz evreni | 1.000 | 823 | 0,823 |
| `vo_kap` | Analiz evreni | 1.000 | 666 | 0,666 |
| `satis_kap_cari` | Evren, 2022 | 125 | 0 | 0 |
| `satis_kap_cari` | Evren, 2016 | 125 | 13 | 0,104 |
| `satis_kap_cari` | Evren, 2017–2021 | 625 | 625 | 1 |
| `satis_kap_karsilastirmali` | Evren, 2023 | 125 | 0 | 0 |

Analiz evreni, kanonik ilk 100 (98 hisse; KRDMA ve KRDMB düşülmüş, yerine firma konmamış) ile 32 tekstil kodunun birleşimidir. Örtüşenler tek sayılır: 125 firma × 8 yıl = 1.000 satır.

2016 XI satışı ile 2016 KAP cari satış, bu evren artı listedeki diğer çekilmiş firmalarda 112 çiftte kıyaslandı. 98 yakın (mutlak fark 1 TL altında veya göreli fark 0,001 altında), 14 aykırı:

| Kod | XI / KAP cari | Not |
| --- | --- | --- |
| SISE | 1,0175 | XI, 2017 karşılaştırmalı satışa eşit. Neden okunmadı |
| ULKER | 1,0694 | 2017 taramasında yok |
| KRDMD | 0,6844 | Pay sınıfı ölçeği |
| IZMDC | 0,9776 | |
| ZOREN | 1,0243 | |
| TAVHL | 1,0788 | |
| GOODY | 1,0050 | |
| ARENA | 0,9826 | |
| BESLR | 4,1092 | 2017 taramasında yok. Neden okunmadı |
| EGPRO | 1,0505 | |
| GSRAY | 1,1037 | |
| KARSN | 1,0354 | |
| ECILC | 0,3753 | 2017 taramasında yok. Neden okunmadı |
| DAGI | 0,9895 | |

## 4. Duyarlılık

Pencere 2016–2022. Düzeltilmiş sütun, XI_29'dur ve 2022 ucu 2023 bildiriminin karşılaştırmalı sütunudur. Orijinal sütun, iki yılın da KAP cari sütunudur. Eşli satır, iki sütunda da sayısı olan firmadır. İşaret, iki medyan da sıfırdan farklı ve ters yöndeyse döner.

Yayımlanmış ilk 100, KRDMA ve KRDMB dahil.

| Gösterge | n eşli | Orijinal, KAP cari, medyan (p25; p75) | Düzeltilmiş, XI_29, medyan (p25; p75) | İşaret döner mi |
| --- | --- | --- | --- | --- |
| Reel satış, 2016–2022 | 94 | %141,3 (72,1; 220,1) | %279,2 (206,3; 466,7) | Hayır |
| Çekirdek değişimi, dört satır dolu | 46 | +4,64 puan (0,94; 8,78) | −3,21 puan (−6,05; 2,92) | Evet |
| Çekirdek değişimi, yayımlanmış tanım | 100 XI; KAP veri yok | Veri yok | −0,98 puan (−5,98; 3,25), n=100 | Belirlenemiyor |
| Vergi öncesi değişimi | 94 | +6,53 puan (0,08; 16,36) | +2,23 puan (−3,11; 13,59) | Hayır |
| Net finansman değişimi | 73 | −0,08 puan (−2,37; 2,95) | +2,88 puan (−2,32; 9,43) | Evet |

Eşlenmemiş XI medyanları, yayımlanmış tanımdır: reel n=100 %279,2; çekirdek n=100 −0,98; vergi öncesi n=100 +2,14; net finansman n=100 +2,79. Eşli XI reel medyanı da %279,2'dir. Eşli XI çekirdek medyanı −3,21'dir, çünkü alt küme dört satırı dolu firmalardır.

Kanonik liste, n=98. Eşli reel n=92: XI %272,8, KAP %140,5, işaret dönmez. Eşli çekirdek n=46: aynı −3,21 ve +4,64, işaret döner. Eşli vergi öncesi n=92: XI +2,14, KAP +6,23, işaret dönmez. Eşli net finansman n=71: XI +2,87, KAP −0,12, işaret döner.

32 tekstil firması. Altı firmada 2016 XI satışı yoktur: BAYRK, ENSRI, ISSEN, RUBNS, SUNTK, SUWEN.

| Gösterge | n eşli | Orijinal, KAP cari | Düzeltilmiş, XI_29 | İşaret döner mi |
| --- | --- | --- | --- | --- |
| Reel satış | 24 | %116,7 (45,9; 164,0) | %313,0 (173,9; 393,7) | Hayır |
| Çekirdek, dört satır dolu | 10 | +8,58 (5,23; 20,09) | +2,31 (−3,21; 17,87) | Hayır |
| Vergi öncesi | 24 | +6,47 (−3,93; 32,11) | +4,08 (−8,81; 19,63) | Hayır |
| Net finansman | 15 | −3,53 (−7,04; 5,37) | +4,79 (−17,86; 12,49) | Evet |

Eşlenmemiş XI, 32'de reel n=26 medyan %318,9; çekirdek n=26 +6,91; vergi öncesi n=26 +5,82; net finansman n=26 +3,04. Çekirdeğin eşli XI medyanı +2,31'dir; +6,91 bu ona eşit değildir. Holding adlı ARSAN, DERHL ve RALYH düşünce eşli net finansman n=13: XI +5,89, KAP −3,53, işaret yine döner. Eşli çekirdek yine n=10'dur.

## 5. 2016 yeniden düzenleme taraması

Soru: 2016 KAP cari satışı, 2017 yıllık bildiriminin karşılaştırmalı satışına eşit mi. Örnek, 14 tekstil ve 14 büyük firmadır: AKSA, KORDS, MAVI, SASA, MNDRS, BOSSA, DERHL, DIRIT, YUNSA, SUWEN, HATEK, DESA, BLCYT, KRTEK, TUPRS, THYAO, BIMAS, AEFES, TCELL, EREGL, FROTO, SISE, ENKAI, PGSUS, CCOLA, ARCLK, TOASO, ASELS. Pencere 2018-01-01 … 2018-09-30. Okunan gelir tablolarının sütun sayısı 2'dir. 2016, bu örnekte 2018–2023 bildirimlerinin içinde bir sütun olarak aranmadı; iki sütunlu tabloda 2016 kolonu yoktur. 2023 bildirimlerinde XBRL'i okunan 94 firmanın sütun sayısı 2'dir. 2024 bildirimlerinde yayımlanmış 100'ün 100'ünde sütun sayısı 2'dir.

Satış eşit (göreli fark 0,001 altında): AKSA, KORDS, SASA, MNDRS, BOSSA, DIRIT, YUNSA, HATEK, DESA, BLCYT, KRTEK, TUPRS, THYAO (iki bildirim, ikisi de eşit), BIMAS, AEFES, TCELL, EREGL, FROTO (18.289.107.267 ve 18.289.107.000; oran 0,999999985, birim yuvarlaması), ENKAI, PGSUS, CCOLA, ARCLK, TOASO, ASELS.

Satış farklı: SISE. 2016 cari 8.421.668.181 TL, idx 591297, yayım 06.03.2017 22:58:35, birim 1, nitelik Konsolide. 2017 karşılaştırmalı 8.569.464.000 TL, idx 662893, yayım 27.02.2018 20:24:44, nitelik Konsolide, oran 1,01755. Vergi öncesi 1.174.379.806 ve 1.174.379.000; oran 0,9999993. Satış sapmasının nedeni okunmadı. Birleşme, politika veya sınıflama diye yazılmadı.

Satış eşit, vergi öncesi farklı: BOSSA. 2016 cari satış 361.200.233 TL, vergi öncesi −9.706.769 TL, idx 587340, yayım 17.02.2017 19:25:15, birim 1, nitelik Konsolide (ayrıştırıcı bu turda yeniden okudu). 2017 karşılaştırmalı satış 361.200.233 TL, vergi öncesi −48.278.654 TL, idx 668857, yayım 16.03.2018 05:18:00, nitelik Konsolide Olmayan. Tablo türü hücresi değişmiş, vergi öncesi tutarı değişmiş, satış tutarı değişmemiştir. Neden okunmadı.

Kıyas kurulamadı: MAVI. 2017 bildirimi vardır, sütun sayısı 2'dir; 2016 KAP satışı önbellekte yoktur. DERHL ve SUWEN: 2018 Ocak–Eylül penceresinde 2017 yıllık bildirimi yoktur.

Bu tarama, bölüm 3'teki 14 aykırı firmanın büyüklerini kapsamaz. BESLR (4,11) ve ECILC (0,38) örnekte yoktur.

## 6. Eleştiri

2022 karşılaştırmalı sütun, 2023 bildiriminin içindedir ve önceki turda Aralık 2023 satın alma gücüne bağlanmıştır. Onu 2022 ortalama TÜFE'sine bölüp 2016 nominal satışla kıyaslamak, iki fiyat kavramını tek reel oranda birleştirir. 2023 XI_29 bir adım daha ileridedir: bu turda 2024 bildiriminin karşılaştırmalı sütununa eşittir ve bu sütunun 2023 yüzüne oranı, medyanda Aralık 2024 TÜFE / Aralık 2023 TÜFE'ye eşittir. Gelir tablosu kalemleri teoride tek Aralık çarpanıyla düzeltilmez; dipnot okunmadığı için bu eşitlik bir kimlik olarak kaldı, bir düzeltme ispatı olarak yazılmadı. 2016–2023 XI marjı, çoğu firmada nominal 2016 ile sonraki bir karşılaştırmalı sütunu aynı farka koyar. Tekstil vergi öncesi medyanının 17 firmada dönmemesi, iki sütunun birbirinin yerine geçtiğini göstermez.

Örnek 28 firma, 2018'in ilk dokuz ayında yıllık bildirim bırakmış olanlardır. Yarısı tekstil diye seçildi. Satışın eşit çıktığı firmalar, 2016 XI ile 2016 KAP'ın ayrıldığı BESLR ve ECILC'yi içermez. Taramadaki eşitlik, o 14 aykırının nedenini taşımaz. BOSSA, satış eşit diye "yeniden düzenlenmedi" densin diye seçilseydi vergi öncesi farkı ve tablo türü değişikliği görünmezdi; satış tek başına yeterli sınama değildir.

"Orijinal" bu tabloda, yıl+1 Ocak–Eylül penceresindeki son yıllık bildirimin cari sütunudur. İlk yayım değildir ve hiç yeniden düzenlenmemiş anlamına gelmez. SISE'de 2016 cari satış, ertesi yılın karşılaştırmalı satışından %1,75 ayrılır; vergi öncesi ayrılmaz. Neden okunmadı. Pencere içindeki düzeltme bildirimi, önceki bildirimin üzerine yazılır. Önceki turda BRKO'da XI_29, ilk 2023 yüzüne eşit, sonraki düzeltme bildirimine eşit değildi. Bu tablonun "son yıllık" kuralı o ayrımı taşımaz.

Yeni bir tez kurulmadı.
