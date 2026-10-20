# Sektör ikamesi ve kur baskısı

H1, ithal girdi veya makinenin kur baskısının genel sürücüsü olması: **Belirsiz**. H2, bunun 2021-Q4’ün nedeni olması: **Yanlışlandı**.

Karşı-olgu yok. Ayakta yazılmadı. “Neden budur” cümlesi kurulmaz.

Kilit `ON_KAYIT.md`, 2026-10-20T14:39:31Z. Hesap `hesap.py`.

## Ne ölçüldü, ne ölçülmedi

Üç kilitli nesne inmedi.

İhracatın yabancı katma değer payı (OECD TiVA) sorgu 500 verdi. **DOĞRULANMADI**.

Teşvik belgesindeki ithal makine-teçhizat tablosu bakanlık adresinden inmedi. Adres reddetti. **DOĞRULANMADI**. Yıl uydurulmadı.

Dünya mal ticaretinin tek muhabiri Comtrade’de boştu. RCA, 25 ülkenin fasıl ihracatıyla kuruldu. Bu küme 2017–2019’da dünya mal ihracatının %72,8’idir [VEKİL]. Eşik %70’ti. Fasıl, HS2’dir. Başlık ve altılı mal kodu inmez. **SAPMA-hs**. Bu, Gaziantep’te üretilen tek bir malla Adana’nın aynı malı ithal etmesi değildir.

Birim değer inmez. Fasıl satırlarında net kilogram sıfır geldi. **DOĞRULANMADI**.

Dolar endeksi FRED’den inmedi. Kontrol düştü. Kalan kontroller politika faizi ve CDS’tir. CDS, yayımlı bir Hazine serisi değildir. Kamuya açık bir derleme dosyasıdır [VEKİL], 2010’dan 2025-12-26’ya.

`EVDS_API_KEY` yoktu. ISIC ticareti, kur, rezerv ve politika faizi `evds3.tcmb.gov.tr/igmevdsms-dis` üzerinden alındı. Sertifika doğrulaması açıktı. ISIC serisi 2013’te başlar.

## EMP

Çeyreklik tanım, PR #38 ile aynıdır. 2016-Q2–2025-Q4. Ağırlık 0,787. 2021-Q4 EMP **32,50** [HESAP]. Ay sonu varyantı, çeyreğin son ayının ortalama satış kuruyla, **54,74** [HESAP]. İkisi de ölçeklenmedi.

## Vekil endeks

İmalat bölümleri 10–32. Bölüm 33’ün mal ticareti serisi boştur, endekse girmez. Yoğunluk, ithalat / (ithalat + ihracat). Endeks, ihracatı olan bölümlerin yoğunluklarının ithalat payıyla ortalamasıdır [VEKİL]. TiVA payı değildir.

Çeyrek denklem, 39 çeyrek. Gecikmeli endeks, çağdaş faiz ve CDS farkı. Katsayı **+102** [HESAP]. Tek taraflı p 0,11. Shapley payı **%10**. Kayan 16 çeyreğin 24’ünden 7’si tutar, oran **%29**. Eşikler %30 ve %60’tır. İkisi de tutulmaz.

Ters yön tutmaz. Gecikmeli EMP, endeksi pozitif yönde sürmez. Katsayı eksi, kayan pencerelerin hiçbiri tutmaz. Öncülük iki yönlü değildir. Öncülük de yoktur. Tek yön “yok” demektir.

Aylık aynı endeks, katsayı **−17** [HESAP]. Pay %8. Kayan 36 ayın %37’si tutar. İşaret çeyreğin tersidir. Kilit, iki frekans ters işaret verirse adayı Belirsiz bırakır. Holm, çeyrek p 0,11 ve yıllık RCA p 0,16 üzerindedir. Ayarlı p 0,22. Eşik 0,05’tir.

2021-Q3 endeksi 0,575’tir. 2016-Q2–2019-Q4 ortancası 0,609’dur. Kriz çeyreğinin öncesi, eski ortancanın üstünde değildir. 2021-Q4 endeksi 0,558’dir.

b × X çarpımı 2021-Q4’te 58,6 puandır. EMP 32,50’dir. Çarpım, çeyreğin kendisinden büyüktür. Aynı regresyonda faiz ve CDS ters tarafa çeker. Shapley bu endekse R²’nin %10’unu verir. Çarpım, çeyreğin açıklanmış payı değildir.

## İkame edilebilir ithalat

2017–2019 ortalamasında RCA 1’in üstünde olan **48 fasıl** kilitlendi. Küme sonradan değişmedi. Listenin içinde giyim (61, 62), motorlu taşıt (87), demir-çelik (72) vardır. Mineral yakıt faslı (27) listede yoktur.

Bu fasılların ithalat payı [VEKİL]:

| Yıl | Pay |
| --- | --- |
| 2017 | %46,2 |
| 2018 | %43,3 |
| 2019 | %42,2 |
| 2020 | %48,2 |
| 2021 | %43,2 |
| 2022 | %41,6 |
| 2023 | %45,1 |
| 2024 | %44,3 |

2021, 2017–2019’un üstünde bir sıçrama değildir. 2020 daha yüksektir. Yıllık regresyon, 9 yıl, katsayı pozitif, p 0,16, Shapley **%15**. Kayan 8 yıllık pencere iki tane kurulur. Sekizin altında olduğu için kayan test geçmiş sayılmaz. Yıllık pay, 2021 yılının kendi son çeyreğini önden haber veremez.

## Kur tabanı, 2021-Q4

Bağımlı bölüm, 2017–2019’da imalat yoğunluğunun ortancasının (0,47) üstünde olan bölümdür. Bunlar 11, 12, 17, 18, 19, 20, 21, 24, 26, 28, 30. Rafine petrol (19) bu listenin içindedir.

Bu bölümlerin toplam mal ithalatındaki payı 2017–2019’da **%54,2**, 2021-Q4’te **%49,8** [HESAP]. Fark **−4,4 puan**. Eşik, payın en az 5 puan yükselmesiydi. Pay düşmüştür. Ham petrol bölümü (06) o çeyrekte seri olarak yok, sıfır yazılmadı. Rafine petrol (19) 2021-Q4 ithalatının %5,4’üdür.

Bu, faturanın paylaşımıdır. 32,50 puanın paylaşımı değildir.

## Hüküm

H1 Belirsiz. TiVA, belge teşviki ve dünya RCA’sı ölçülmedi. Ölçülen iki vekil, Shapley ve kayan pencere eşiklerini tutmaz. Aylık ve çeyreklik işaretler terstir. Vekil tutsaydı da H1 Ayakta yazılmazdı.

H2 Yanlışlandı. 2021-Q4’te bağımlı bölümlerin ithalat payı, 2017–2019’un altındadır. Endeks, krizden önceki çeyrekte eski ortancanın üstünde değildir. İkame fasıl payı 2021’de sıçramamıştır. Önceki turlarda cari denge, enerji, makine ithalatı, firma döviz pozisyonu, çevirme ve seçim de 2021-Q4’ü önden haber vermemişti. Bu tur, yurt içi arz varken ithalat hikâyesini o çeyreğin nedeni diye taşımaz.

## Zayıf noktalar

1. Fasıl, bir mal değildir. 48 fasıl, ithalatın yaklaşık yüzde 43’ünü tutar. Dar bir “yerli mal dururken ithal” kümesi değildir.
2. TiVA ve teşvik boştur. H1’in Belirsiz kalması buradandır.
3. CDS derlemedir. Dolar endeksi yoktur.
4. Bölüm yoğunluğu, aynı malın yurt içi üretimi değildir. İhracat, arzın izidir.
5. b × X çarpımının 32,50’yi aşması bir pay hesabı değildir.
6. Karşı-olgu yoktur.
