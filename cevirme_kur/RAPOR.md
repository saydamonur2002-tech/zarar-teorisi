# Çevirme oranı kur baskısını öncelemeli mi?

Hüküm: **Belirsiz**. Hipotez aday olarak kalır. Ayakta yazılmaz. Yanlışlandı da yazılmaz. Karşı-olgu yok. “Çevirme düşünce baskı oluştu” denmez.

Kilit `ON_KAYIT.md`, 2026-10-20T12:56:49Z. Eşikler skor görüldükten sonra değiştirilmedi. Kutu testinin `rapor.md`, `ON_KAYIT.md` ve `epizot.csv` dosyaları bu çalışmada yoktu. Oradaki %42, %66 ve %44 hedef yapılmadı.

## Ne çıktı

On iki aylık birleşik çevirme oranı, üç epizotun hiçbirinde baskı ayından 1–3 ay önce alarm vermedi. Tutan epizot 0 / 3 [HESAP]. Ayakta’nın ilk çubuğu tutmaz.

Granger, yerel izdüşüm, kayan pencere ve ters yön kurulmadı. Kontroldeki dolar endeksi (FRED `DTWEXBGS`) üç denemede zaman aşımına uğradı. Ön kayıt, bu indirme olmazsa kontrollü testi DOĞRULANMADI bırakır. Kontrol düşürülmedi. İşaret testi de yapılmadı. Bu yüzden “ters işaretle yanlışlandı” denemez.

Yanlış alarm 18 ay [HESAP]. İsabet 0 / (0 + 18) = 0. Bu oran ek bir eşik değildir.

Üç aylık oran, aynı alarm kuralıyla 2018 ve 2021’de bankada önden tutar, 2023’te tutmaz. Bu 2 / 3’tür [HESAP]. Ön kayıt üç aylık oranı hükmün dışına koyar. Ayakta’yı değiştirmez.

## Epizotlar

Baskı ayı, kilitli pencerenin içinde aylık EMP’si en yüksek aydır.

| Epizot | Baskı ayı | Aylık EMP | Önceki üç ay, banka 12 ay | Diğer sektör 12 ay | Alarm |
| --- | --- | --- | --- | --- | --- |
| 2018 | 2018-08 | 27,7 | 109, 107, 108 | 140, 140, 143 | yok |
| 2021 | 2021-12 | 33,8 | 95, 94, 90 | 124, 122, 125 | yok |
| 2023 | 2023-05 | 13,7 | 83, 83, 83 | 155, 140, 140 | yok |

Sayılar yuvarlanmıştır [HESAP]. Oranlar yüzde. Hepsi 15 puanlık düşüş koşulunun dışındadır. Banka 2021 ve 2023’te %100’ün altındadır. Düşüş yoktur. Diğer sektör üç pencerede de %100’ün üstündedir.

2018’de banka oranı baskıdan sonra düşer. Ağustos 99, Eylül 83 [HESAP]. Eylül alarmdır. Baskı ağustostadır. Düşüş, baskıyı izler. Eylül epizot penceresinin içinde olduğu için yanlış alarm sayılmaz. Ekim, kasım ve aralık 2018 yanlış alarmdır.

Kasım 2022, kutu testinde yanlış alarm diye anılmıştı. Burada banka 12 aylık oran 77’dir, %100’ün altındadır. Ağustosa göre düşüş 2,8 puandır. 15 puan koşulu tutmaz. Alarm yazılmaz [HESAP].

Yanlış alarm ayları: 2009’un martından kasımına, 2016-05, 2018-10, 2018-11, 2018-12, 2019-06, 2019-07, 2019-12, 2023-08, 2023-10. On sekiz ay.

Üç aylık yan sayım, banka: 2018 Mayıs ve Temmuz, 2021 Eylül ve Ekim alarmdır. 2021 Eylül’de üç aylık banka oranı 65, Ekim’de 56’dır [HESAP]. 2023’ün önceki üç ayında alarm yoktur. Bu, kutu testindeki Ekim %42 / %66 ve Nisan %44 ile aynı sayılar değildir.

## Çevirme oranı nasıl kuruldu

Ödemeler dengesi, 2006-01–2026-08, milyon dolar [VERİ]. Kimlik bütün aylarda sıfır hatayla tutar.

Uzun vade neti = kullanım − geri ödeme. İkisi de pozitif saklanmıştır. Kısa vade, net yükümlülüktür. Pozitif kısa vade, net borçlanmadır. Bankalar: kısa vade `Q167`, kullanım `Q169`, geri ödeme `Q170`. Diğer sektörler: `Q180`, `Q182`, `Q183`.

On iki aylık uzun vade oranı, on iki ayın kullanımı bölü on iki ayın geri ödemesidir. Birleşik oran, kısa vadeyi de katar: pozitif kısa vade paya, negatif kısa vade paydaya eklenir [HESAP]. Hüküm bu birleşik 12 aylık orandadır.

Diğer sektör, yalnız finansal olmayan firma değildir. Hane ve banka dışı kesimler de bu satırdadır. Daraltılmadı.

Yayımlı `TP.ODEROLL.K1` ve `K2` ile medyan mutlak fark, 2008’den sonra, bankada 29 puan, diğer sektörde 10 puandır [HESAP]. Beş puan eşiğinin üstündedir. Seriler eklenmedi. Ekim 2021’de yayımlı oran banka 96, diğer sektör 131’dir [VERİ]. Hesaplanan birleşik oran 94 ve 122’dir. Kutu testinin %42 ve %66’sı bu iki satırda da yoktur. Nisan 2023’te yayımlı diğer sektör 96, hesaplanan 140’tır. %44 yoktur.

## EMP mutabakatı

Çeyreklik tanım, PR #38 ile aynıdır. Kur, üç aylık ortalama satış kurudur. Rezerv, brüt resmi rezerv varlıklarıdır. 2016-Q2–2025-Q4.

2021-Q4 [HESAP]:

- Kur log farkı e = 25,97
- Rezerv yüzde farkı r = −8,31
- Ağırlık s_e / s_r = 0,787
- EMP = 32,50

PR #38’de aynı tanım 32,51 ve 0,787 idi. Fark 0,1 puanın altındadır. SAPMA-emp yazılmaz.

Çeyreğin son ayının satış kuruyla kurulan varyant, aynı rezerv ve kendi ağırlığıyla, 2021-Q4’te **54,74** verir [HESAP]. e = 46,33, ağırlık 1,01. Bildirilen 55 ile fark 0,26 puandır. O formülün dosyası burada yok. 55 birebir doğrulanmış değildir. Ölçeklenmedi.

FRED ağırlığı 0,539 indirilemedi. DOĞRULANMADI. Kullanıcının söylediği 0,539, bizim e ve r üzerine konunca 2021-Q4 EMP 30,45 olur [VEKİL]. Bu, FRED’den tahmin edilmiş ağırlık değildir.

Aylık EMP, aynı formülün aya uygulanmasıdır (SAPMA-frekans). 2008-01–2026-09, 225 ay. Ağırlık 0,755 [HESAP]. Epizot bu aylık seridedir. 2021 Aralık aylık EMP 33,8, çeyreklik 32,50 ile aynı büyüklüktedir.

## Neden Granger yok

`EVDS_API_KEY` bu ortamda yoktu. Değeri aranmadı, yazılmadı. Seriler `evds3.tcmb.gov.tr/igmevdsms-dis` uç noktasından alındı. Bu uç birincil yol değildir. Kullanılan seriler: kredi kullanım ve geri ödemeleri, kısa vade neti, yayımlı çevirme oranları, dolar satış kuru, resmi rezerv, politika faizi `TP.BISPOLFAIZ.TUR`. Sertifika doğrulaması açıktı.

FRED `DTWEXBGS`, `DGS2`, `CCUSSP02TRM650N` ve `TRESEGTRM052N` zaman aşımına uğradı. Anahtarsız FRED API 400 döndü. Başka siteden dolar endeksi konmadı. CDS dosyası indirildi [VEKİL], regresyona girmedi. Politika faizi indirildi, regresyona girmedi.

Kontrollü test olmadığı için Holm, kayan %60 ve ters yön DOĞRULANMADI’dır.

## Zayıf noktalar

1. Hüküm, on iki aylık alarmın sıfır epizot tutmasına ve eksik kontrole dayanır. İşaret görülmedi.
2. Alarm, oranın %100 altında olması ve üç ayda 15 puan düşmesidir. Uzun süre düşük kalan bir oran, düşüş yoksa alarm sayılmaz. 2021’de banka oranı zaten %90–95’tir.
3. Üç aylık oran iki epizotta tutar. Hükme yazılmaz. İki pencere aynı hikâyeyi anlatmaz.
4. Diğer sektör, firma diye dar değildir.
5. Yayımlı çevirme oranı ile hesaplanan oran bankada 29 puan ayrılır. Kutu testinin yüzdeleri ikisinde de yoktur.
6. 55, son ay kuru varyantına 0,26 puan uzaklıktadır. Aynı sayı diye yazılmaz.
7. Aylık ağırlık 0,755, çeyreklik ağırlık 0,787’dir. İkisi de örneklem sapmasıdır.
8. Karşı-olgu yoktur. Zaman sırası, neden değildir.
