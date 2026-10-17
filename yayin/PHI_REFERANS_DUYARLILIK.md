# φ referans duyarlılığı

Üç salt-okunur koşu, 2026-10-17. Model kodu, `yayin/etki-cephesi-model.zip` ve mevcut rapor çıktıları duruyor. Sayılar vekil. Ham döküm: `data/etki_cephesi/gozlem/duyarlilik/` — ana model bu klasörü okumaz (`projeksiyon._dis_veri` yalnız `gozlem/dis_ticaret_gsyh_2023.json`).

**Etiket.** **Kanıt:** dosyadaki formülün yeniden hesabı veya API satırının dosyayla örtüşmesi. **Aday:** partnersiz ihracat, ayna veri, ya da ticaret dışı kanalın φ=1 ile dışarıda kalması.

## Formül

φ, kaybı modelli referans aktörde model kaybının ham çekime oranıdır. Çekim = Σ_j (ihracat_ij / GSYH_j) · L_j (`etki_cephesi/projeksiyon.py:698-703`, paket `yayin/etki-cephesi-model.zip`). Kalibrasyon listesi JSON `kalibrasyon_aktorleri`. Filtre: kayıp > 0 ve çekim > 0 (`:714-718`). Kod medyanı sıralı listenin `len//2` indeksidir (`:726`); iki ortanın ortası değildir. n=2 iken üst değer seçilir.

Ayrı nesne: `REFERANS_ORAN = ("IR","IL","EG")` (`:637`). MFİN kayıp vekili, kazancı > 0 olan bu aktörlerin kayıp/kazanç oranının medyanı × MFİN kazancıdır (`:800-809`). Kazancı 0 olan aktör bu orana girmez.

Sınıf: net − bant > 0 kazanan, net + bant < 0 kaybeden, aksi halde bant içi; bant içinde rant farkı > 400 mn $ ise ham etiket `rant_kanali_bosluk_taraftari` (`bolge_stok_akis.py:65-77`). Sistem toplamı defter `net_maliyetli` toplamıdır (`goreceli_konum.py:147-155`). Karar skoru ve E[TR net] bu φ’yi okumaz (`senaryo_uygulanabilirlik.py:100-105`; `SENARYO_UYGULANABILIRLIK.json:2` ve `:48`).

Taban (3 aktör, kanıt — bu φ koşusunun yayımlı sistemi): A −50.694, B −89.283, C −32.964. Halka çevre IR, IL. Skor 47.7. E[TR net 10y] −23.117. Bu mutlak sistem, Balkan sürdürme düzeltmesinden öncedir. Düzeltme sonrası sistem A −50.96, B −89.477, C −33.245 (`ANOMALI_DUZELTMELERI.md`). φ farkları aynı kalır: maliyet κ·pol’dür, φ’ye bağlı değildir.

| | A φ min / med / maks | B | C |
| --- | --- | --- | --- |
| IR, EG, IL | 1.463 / 3.244 / 5.641 | 1.451 / 3.376 / 7.098 | 1.441 / 3.095 / 4.511 |

Medyan Mısır. Sıra IR < EG < IL.

## 1. Sırbistan ve Azerbaycan φ’ye giremiyor

İkisi de net-tam (kazanç kapsamı tam, kayıp modellendi) ve Balkan pay listesinde RS var, AZ yok (`uluslararasi_stok_akis_capa.json:17`). İhracat bloğu yok (`dis_ticaret_gsyh_2023.json` anahtarları: AE, CN, EG, EU, FR, GR, IL, IR, RU, SA, US). Projeksiyon kazancı ikisinde de 0. Filtre çekim > 0 istediği için φ kümesine giremezler. Oran filtresi kazanç > 0 istediği için MFİN oranına da giremezler.

**Kanıt.** Beşli küme (IR, IL, EG, RS, AZ) tabanla özdeş: aynı φ, aynı net, aynı sistem.

### Mısır düşünce

Kalibrasyon IR+IL. n=2, kod medyanı indeks 1 = İsrail = φ_maks. Nokta kayıp sıçrar.

| | A | B | C |
| --- | ---: | ---: | ---: |
| φ min / med / maks | 1.463 / 5.641 / 5.641 | 1.451 / 7.098 / 7.098 | 1.441 / 4.511 / 4.511 |
| Sistem toplamı | −70.728 | −140.451 | −40.921 |
| Taban sistem | −50.694 | −89.283 | −32.964 |

| Aktör | A net ± bant | B | C |
| --- | --- | --- | --- |
| CN | −6.590 ± 3.488 kaybeden | −15.267 ± 7.339 kaybeden | −3.092 ± 1.944 kaybeden |
| RU | −5.663 ± 3.098 kaybeden | −12.867 ± 6.307 kaybeden | −2.725 ± 1.790 kaybeden |
| US | −0.827 ± 0.977 bant içi | −2.807 ± 2.128 kaybeden | −0.153 ± 0.512 bant içi |
| AB | −18.750 ± 7.223 kaybeden | −39.133 ± 15.961 kaybeden | −9.967 ± 3.585 kaybeden |
| AE | −4.311 ± 1.896 kaybeden | −9.598 ± 4.235 kaybeden | −2.127 ± 0.935 kaybeden |
| SA | −0.005 ± 0.252 bant içi | −0.440 ± 0.502 bant içi | +0.113 ± 0.142 bant içi |
| FR | −1.980 ± 0.891 kaybeden | −4.284 ± 1.910 kaybeden | −1.015 ± 0.468 kaybeden |
| GR | −0.820 ± 0.431 kaybeden | −1.878 ± 0.907 kaybeden | −0.402 ± 0.231 kaybeden |

Tavana göre Çin ve Rusya kaybedene iner. C’de SA kazanan iken bant içine düşer.

Aynı koşuda Mısır `REFERANS_ORAN` dışına da alınırsa MFİN nokta kaybı değişmez (üçlüde de kod medyanı zaten İsrail’in oranıydı). Bant daralır. Net − bant > 0 olduğu için sınıf bant içinden kazanana döner.

| MFİN | A taban | A, Mısır oran dışı | B taban | B, Mısır oran dışı | C taban | C, Mısır oran dışı |
| --- | --- | --- | --- | --- | --- | --- |
| Kayıp vekili | 3.443 | 3.443 | 12.032 | 12.032 | 1.277 | 1.277 |
| Net | +3.286 | +3.286 | +4.069 | +4.069 | +1.897 | +1.897 |
| Bant | 6.192 | 0.902 | 18.710 | 2.722 | 2.645 | 0.493 |
| Sınıf | bant içi | kazanan | bant içi | kazanan | bant içi | kazanan |

### φ = 1, kayıtlı vektör

`_PHI_SABIT` (`projeksiyon.py:706`, `:719-720`). Kayıtlı AB vektörü (25 üyenin toplamı, BG ve CY hedefleri yazılmamış). Çin→Kırgızistan, ihracat/GSYH = 1.30 olduğu için hub kuralıyla düşülür. MFİN oranı tabanda kalır.

| | A | B | C |
| --- | ---: | ---: | ---: |
| Sistem | −31.940 | −56.628 | −21.198 |

| Aktör | A kayıp / net ± bant | B | C |
| --- | --- | --- | --- |
| CN | 1.533 / +0.527 ± 1.378 bant içi | 2.541 / +0.225 ± 1.552 bant içi | 1.025 / +0.505 ± 1.142 bant içi |
| RU | 1.326 / +0.490 ± 1.388 bant içi | 2.163 / +0.321 ± 1.581 bant içi | 0.899 / +0.430 ± 1.142 bant içi |
| US | 0.456 / +1.289 ± 0.220 kazanan | 0.751 / +1.770 ± 0.191 kazanan | 0.307 / +0.923 ± 0.200 kazanan |
| AB | 3.456 / −2.710 ± 0.209 kaybeden | 5.653 / −4.661 ± 0.219 kaybeden | 2.333 / −1.776 ± 0.168 kaybeden |
| AE | 0.902 / −0.123 ± 0.200 bant içi | 1.498 / −0.462 ± 0.205 kaybeden | 0.600 / −0.020 ± 0.160 bant içi |
| SA | 0.104 / +0.478 ± 0.127 kazanan | 0.173 / +0.613 ± 0.117 kazanan | 0.070 / +0.357 ± 0.093 kazanan |
| FR | 0.408 / −0.088 ± 0.261 bant içi | 0.668 / −0.212 ± 0.302 bant içi | 0.275 / −0.047 ± 0.200 bant içi |
| GR | 0.172 / −0.021 ± 0.237 bant içi | 0.301 / −0.045 ± 0.318 bant içi | 0.110 / −0.017 ± 0.158 bant içi |
| MFİN | +3.286 ± 6.192 bant içi | +4.069 ± 18.710 bant içi | +1.897 ± 2.645 bant içi |

ABD ve SA üç senaryoda da kazanan. AB kaybeden kalır. Sistem negatif kalır, tabandan daha az negatiftir.

## 2. Irak dördüncü, Tunus beşinci referans

Aday ölçütü: modellenmiş kendi kaybı, AB Balkan listesinde olmamak, IR/IL/EG’den ayrı bir yapı. Pozitif kazançlı ve bu ölçüte uyan dördüncü aktör yok. Kazancı > 0 ve kaybı modelli olanlar yalnız IR, IL, EG, UA (C 0.026, kısmi), CY (C 0.074, AB içi ortak). Irak C kaybı 1.360, kazanç 0, `makro_ceper: korfez` (`bolgeler.json:6-7`). Tunus C kaybı 0.155, kazanç 0. GCC vekili tek raporlayıcı yapılmadı: üyeleri SA ve AE zaten φ’nin hedefi. Ürdün’ün havza kaybı satırı yok.

Kazanç 0 olduğu için ikisi yalnız φ’ye girer, MFİN oranına girmez (`:804`). MFİN satırı tabanla aynı kalır.

### Veri

Comtrade önizleme, yıllık 2023, HS TOTAL:

`https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=368&period=2023&cmdCode=TOTAL&flowCode=X&partner2Code=0&customsCode=C00&motCode=0&maxRecords=500`

Irak kendi ihracatı: dünya 105 725.7 mn USD, partner kodu 899 (Areas nes) 101 332.4 mn USD, pay %95.8. Türkiye satırı 18 400 USD. Bu payda çekime konmadı.

Ana seri: satırı olan ortakta kendi X’i; satırı olmayanda o ortağın Irak’tan ithalatı (flowCode M, CIF, `partnerCode=368`). TR raporlandığı için ayna 1 498.2 mn yazılmadı. Ayna dolduranlar: AM, AZ, BG, BH, GE, RS, TN, UA, UZ. Satırı hiç olmayanlar: DZ, IL, KG, LY, SO, TJ, TM.

Tunus kendi X’i, reporter 788: dünya 20 039.7 mn USD, 160 ortak (önizleme tavanı 500). IL ve KG satırı yok. TR 211.5 mn.

Ortak GSYH: `https://api.worldbank.org/v2/country/…/indicator/NY.GDP.MKTP.CD?date=2023&format=json`. 35 ortak dosyayla 0.1 mn USD’ye kadar aynı. Suriye 2023 boş; 2022 = 23 737.6, dosyadaki SY ile aynı (`date=2022`).

Mısır→Türkiye kontrolü (kanıt): API 3 643 855 576 USD = dosyadaki 3643.9.

C’de Irak çekimi 0.00916. Büyük parçalar Lübnan 0.00432 ve Sırbistan 0.00411. Türkiye katkısı 0.

| | A φ | B φ | C φ |
| --- | ---: | ---: | ---: |
| IR | 1.463 | 1.451 | 1.441 |
| EG | 3.244 | 3.376 | 3.095 |
| IL | 5.641 | 7.098 | 4.511 |
| IQ | 136.796 | 123.856 | 148.552 |
| TN (5’li) | 12.582 | 12.705 | 12.365 |

Dört sayıda kod medyanı indeks 2 = İsrail. Tunus, İsrail ile Irak arasında kaldığı için beşli sette de min, medyan ve maks değişmez (C: 1.441 / 4.511 / 148.552). Nokta kayıp, Mısır’sız koşuyla aynıdır çünkü medyan yine İsrail’dir. Sistem de aynı: A −70.728, B −140.451, C −40.921.

Bant ise Irak’ın φ_maks’ından açılır. Sekiz dış aktörün üç senaryoda da sınıfı bant içidir. C’den bir kesit (A ve B aynı sınıfta, bant daha geniş):

| Aktör | C kayıp | C net ± bant | A net ± bant | B net ± bant |
| --- | ---: | --- | --- | --- |
| CN | 4.622 | −3.092 ± 75.377 | −6.590 ± 103.776 | −15.267 ± 155.499 |
| RU | 4.054 | −2.725 ± 66.116 | −5.663 ± 89.732 | −12.867 ± 132.377 |
| US | 1.383 | −0.153 ± 22.561 | −0.827 ± 30.849 | −2.807 ± 45.944 |
| AB | 10.524 | −9.967 ± 171.616 | −18.750 ± 233.875 | −39.133 ± 345.987 |
| AE | 2.707 | −2.127 ± 44.142 | −4.311 ± 61.062 | −9.598 ± 91.696 |
| SA | 0.314 | +0.113 ± 5.114 | −0.005 ± 7.045 | −0.440 ± 10.570 |
| FR | 1.243 | −1.015 ± 20.264 | −1.980 ± 27.591 | −4.284 ± 40.876 |
| GR | 0.495 | −0.402 ± 8.066 | −0.820 ± 11.651 | −1.878 ± 18.404 |
| MFİN | 1.277 | +1.897 ± 2.645 | +3.286 ± 6.192 | +4.069 ± 18.710 |

**Aday.** Irak φ’si ticaret-dışı çarpan gibi okunamaz. Paydanın %95.8’i partnersiz.

**Ayna duyarlılığı.** Bütün ortaklar CIF ayna olsaydı (TR 1 498.2 mn dahil) C’de Irak φ’si 48.318 olurdu. Medyan yine İsrail, sistem yine −40.921, C’de Çin noktası yine −3.092. Yalnız bant daralır (Çin C ±24.043). 899 hâlâ payda dışındadır.

## 3. Aktör başına φ = 1, AB ve GCC ayrık

Paylaşılan φ yok. Kayıp_i = çekim_i. Bu, ticaret dışı kanalı dışarıda bırakan alt sınırdır. Bant yalnız ölçülebilir parçalar: kural, belirsiz merkez payı, κ (`refah_dis_entegrasyon.py:184-207`; `surdurme_maliyeti.json` κ = 0.2, bant 0.1–0.35). φ bandı yok.

### Ayrım ve kazanç

AB 25 üye: AT BE BG CY CZ DE DK EE ES FI HR HU IE IT LT LU LV MT NL PL PT RO SE SI SK. Fransa ve Yunanistan ayrı, eski dosyadaki gibi. `dis_aktör_pay.json:3` üye devlet içermez. Balkan kuralı AB kazancının bir dilimini RS, BA, BG, AL, MK’ya taşır (`refah_dis_entegrasyon.py:54-89`); bu üye payı değildir. Üye neti **bilinmiyor**. Yeniden kurulan AB neti = mevcut AB defter kazancı − Σ üye çekimi − AB maliyeti.

GCC: SA, AE, QA, KW, BH, OM (`bolge_birincil_gelir_odemesi.json` ve `bolgeler.json:8`). QA, KW, BH, OM pay tablosunda yok; netleri bilinmiyor ve sistem toplamına konmadı. SA ve AE’nin kazancı kendi satırlarındadır.

### Veri ve Areas nes

Her raporlayıcı, 2023, flowCode X, HS TOTAL, aynı Comtrade önizleme ucu, `reporterCode` = M49. Rusya reporter 643 boş döndü; kayıtlı ayna duruyor (eksik: SY, LY, DZ, SO, TM). **Aday:** ayna, CIF/FOB farkı.

| Aktör | Dünya mn USD | Areas nes | Etiket |
| --- | ---: | ---: | --- |
| SA | 320 018 | %77.3 | payda dışı, kayıp alt sınır |
| AE | 570 245 | %50.3 | aynı |
| KW | 83 980 | %92.9 | aynı |
| OM | 59 041 | %60.9 | aynı |
| IR | 104 487 | %12.5 | raporda, çekime dağıtılmadı |
| CY | 5 132 | %10.6 | raporda |
| QA, BH, AB üyeleri, CN, US, FR, TR, AZ, RS | — | ≤ %3 | adlı ortaklar |

Çin→Kırgızistan (1.30 × GSYH) çekimden düşüldü. Düşülen parça: A 0.355, B 0.600, C 0.233. **Kanıt:** dosyadaki hub notu bu çifti örnek verir.

Mısır→Türkiye ve IR/IL/EG/CN/US/AE/SA çekimleri dosyayla aynı. Fransa ve Yunanistan farkı yalnız BG ve CY hedefleri. Onlar model ortağı; bu koşuda duruyorlar.

C’de 25’li toplam 2.459. Bunun 0.126’sı BG ve CY hedefleri. O ikisi düşünce kalan 2.333, kayıtlı AB vektörünün C çekimiyle aynı (**kanıt**).

GSYH yine dosyadaki Dünya Bankası 2023 (Suriye 2022), yukarıdaki uçla doğrulanmış hali.

### AB üyeleri, yalnız kayıp

| Üye | A | B | C |
| --- | ---: | ---: | ---: |
| DE | 1.034 | 1.683 | 0.701 |
| IT | 0.582 | 0.965 | 0.389 |
| ES | 0.316 | 0.517 | 0.213 |
| NL | 0.267 | 0.437 | 0.180 |
| PL | 0.220 | 0.356 | 0.149 |
| BE | 0.168 | 0.276 | 0.113 |
| RO | 0.142 | 0.230 | 0.096 |
| CZ | 0.130 | 0.211 | 0.088 |
| HU | 0.124 | 0.199 | 0.084 |
| BG | 0.106 | 0.173 | 0.072 |
| AT | 0.090 | 0.146 | 0.061 |
| SE | 0.065 | 0.106 | 0.044 |
| HR | 0.054 | 0.087 | 0.037 |
| SK | 0.054 | 0.088 | 0.037 |
| SI | 0.048 | 0.078 | 0.033 |
| DK | 0.043 | 0.072 | 0.028 |
| FI | 0.040 | 0.065 | 0.027 |
| LT | 0.036 | 0.060 | 0.024 |
| PT | 0.035 | 0.057 | 0.023 |
| IE | 0.030 | 0.049 | 0.020 |
| CY | 0.029 | 0.054 | 0.018 |
| LV | 0.012 | 0.020 | 0.008 |
| EE | 0.012 | 0.019 | 0.008 |
| LU | 0.006 | 0.010 | 0.004 |
| MT | 0.003 | 0.006 | 0.002 |
| **25 toplam** | **3.646** | **5.964** | **2.459** |

| AB yeniden | A | B | C |
| --- | ---: | ---: | ---: |
| Kazanç (defter) | 0.868 | 1.081 | 0.688 |
| Kayıp φ=1 | 3.646 | 5.964 | 2.459 |
| Net ± bant | −2.900 ± 0.209 kaybeden | −4.972 ± 0.218 kaybeden | −1.902 ± 0.167 kaybeden |
| Kayıtlı vektör φ=1 (bölüm 1) | −2.710 ± 0.209 | −4.661 ± 0.219 | −1.776 ± 0.168 |

### GCC ve diğer aktörler

| | A kayıp | B | C | C net ± bant | Sınıf |
| --- | ---: | ---: | ---: | --- | --- |
| SA | 0.104 | 0.173 | 0.070 | +0.357 ± 0.093 | kazanan |
| AE | 0.902 | 1.498 | 0.600 | −0.020 ± 0.160 | bant içi |
| QA | 0.016 | 0.026 | 0.010 | bilinmiyor | bilinmiyor |
| KW | 0.006 | 0.010 | 0.004 | bilinmiyor | bilinmiyor |
| BH | 0.014 | 0.022 | 0.009 | bilinmiyor | bilinmiyor |
| OM | 0.027 | 0.045 | 0.018 | bilinmiyor | bilinmiyor |

SA A/B: +0.478 ± 0.128 kazanan, +0.613 ± 0.117 kazanan. AE A/B: −0.123 ± 0.200 bant içi, −0.462 ± 0.205 kaybeden. SA ve AE kayıpları nes dışı bırakıldığı için ticaret içinde de alt sınırdır (**aday**).

| | A net ± bant | B | C |
| --- | --- | --- | --- |
| CN | +0.527 ± 1.379 bant içi | +0.225 ± 1.552 bant içi | +0.505 ± 1.142 bant içi |
| RU | +0.490 ± 1.388 bant içi | +0.321 ± 1.581 bant içi | +0.430 ± 1.141 bant içi |
| US | +1.289 ± 0.220 kazanan | +1.770 ± 0.190 kazanan | +0.923 ± 0.200 kazanan |
| FR | −0.098 ± 0.262 bant içi | −0.228 ± 0.302 bant içi | −0.054 ± 0.200 bant içi |
| GR | −0.061 ± 0.238 bant içi | −0.118 ± 0.318 bant içi | −0.041 ± 0.158 bant içi |
| MFİN | +3.286 ± 6.192 bant içi | +4.069 ± 18.710 bant içi | +1.897 ± 2.645 bant içi |

MFİN hâlâ IR/IL/EG vekili. C kazanç 3.918, vekil kayıp 1.277. Bant o oranın kendi aralığıdır.

### Net-tam altı: model kaybı ve yalnız ticaret

Sistem havza kaybını tutar. Ticaret sütunu, aynı kazançtan yalnız çekim düşülürse çıkan karşılaştırmadır. Kazanç uydurulmadı. RS defter kazancı AB’den Balkan aktarımıdır; projeksiyon kazancı 0.

| | C model | C ticaret | oran | C model net | A ticaret | B ticaret |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| IR | 0.277 | 0.192 | 1.44 | +0.744 | 0.285 | 0.464 |
| IL | 0.124 | 0.028 | 4.51 | +0.219 | 0.041 | 0.069 |
| EG | 0.316 | 0.102 | 3.09 | −0.135 | 0.156 | 0.264 |
| RS | 0.392 | 0.046 | 8.70 | −0.115 | 0.067 | 0.109 |
| AZ | 0.249 | 0.094 | 2.66 | −0.229 | 0.137 | 0.223 |
| TR | 17.700 | 0.328 | 54.0 | −17.191 | 0.514 | 0.888 |

**Kanıt.** IR, IL, EG oranları bölüm 1’deki φ ile aynıdır (C 1.441, 4.511, 3.095). TR model kaybı 17.70, ticaret kanalı 0.33: havza kaybının neredeyse tamamı ticaret çekiminin dışındadır.

### Sistem

KG düşülmüş, AB = 25 üye toplamı, FR/GR ayrı, QA/KW/BH/OM sistem dışında.

| | 3’lü φ | φ=1, 25 üye | Fark |
| --- | ---: | ---: | ---: |
| A | −50.694 | −32.180 | +18.514 |
| B | −89.283 | −57.027 | +32.256 |
| C | −32.964 | −21.354 | +11.610 |

Yuvarlak: A −32.18, B −57.03, C −21.35. Bölüm 1’deki φ=1 sisteminden (A −31.940, B −56.628, C −21.198) fark, BG/CY hedeflerinin ve FR/GR’nin bu hedeflere ihracatının ekidir.

## Sonuç

**Dayanıklı (kanıt, φ=1 alt sınırında her iki kurulumda da).** AB kaybeden. ABD ve SA kazanan. Sistem toplamı negatif kalır (en az negatif hali C −21.35). Karar skoru 47.7 ve E[TR net 10y] −23.117 üç koşuda da değişmez: halka çevre IR ve IL model netiyle durur, direnç rant farkı eşiğindendir, E[TR] 10 yıllık TR yoludur.

**Kırılgan.** Çin ve Rusya’nın sınıfı φ’ye bağlıdır. Üçlü medyanda ve φ=1’de bant içi (φ=1’de nokta pozitif). Medyan İsrail’e kayınca, bant da İsrail’de kalıyorsa (Mısır düşülünce) kaybeden olurlar. Irak dördüncü nokta olunca nokta kayıp aynıdır (medyan yine İsrail) ama φ_maks ≈ 137–149 bandı açtığı için sınıf yine bant içine döner. MFİN’in nokta neti üçlü oranla aynı kalır; sınıfı, Mısır oran kümesindeyken bant içi, Mısır düşünce (bant 6.192 → 0.902, 18.710 → 2.722, 2.645 → 0.493) kazanandır.

**Aday, kalibrasyon olarak kullanılmadı.** Irak ve Körfez nes payları (Irak %95.8, Kuveyt %92.9, Suudi Arabistan %77.3, Umman %60.9, BAE %50.3) adlı ortak çekimini ticaretin alt sınırı yapar. Rusya aynadır. φ=1 ticaret dışı kanalı ölçmez.
