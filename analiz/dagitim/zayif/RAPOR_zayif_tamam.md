# RAPOR_zayif_tamam (2026-10-23)

Ön kayıt: `ON_KAYIT_zayif.md`. Sapma: `SAPMA_zayif.md`. Hesap: `z.py`. Bu tur EVDS/EVDS3 kullanmadı. Haber rakamı hükme girmedi. "Rant" bulgu sözcüğü değildir. Nedensel cümle yalnız ön kayıtlı S2 karşı-olgusu içindir; faiz ve büyüme satırları aktör sıralamasına yazılmadı.

## S1 ne değişti [HESAP]

Paylas2 S1'de yalnız 2019–21 aktarımı vardı: 1,78+0,86+0,48 = 3,12 GSYH puanı [VERİ]. Bu turda nakit yıl kavramıyla okunan Hazine payı (temettünün Hazine kısmı + Hazine'ye ödenen ihtiyat; deprem bağışı hariç) bütün yıllarda duruyor. 2024 ve 2025 özkaynak ve nakit akışta temettü ile ihtiyat aktarımı tire olduğu için 0 [VERİ], boşluk sıfırla doldurulmadı.

| Yıl | Milyar TL | GSYH puanı | Etiket |
|---|---:|---:|---|
| 2014 | 3,36 | 0,16 | [VERİ] kâr dağıtım, GK 17.04.2014 |
| 2015 | 5,80 | 0,25 | [VERİ] kâr dağıtım, GK 09.04.2015 |
| 2016 | 9,30 | 0,35 | [VERİ] kâr dağıtım, GK 11.04.2016 |
| 2017 | 6,41 | 0,20 | [VERİ] 2018 özkaynak |
| 2018 | 12,36 | 0,32 | [VERİ] 2018 özkaynak |
| 2019 | 78,29 | 1,78 | [VERİ] paylas2 ile aynı |
| 2020 | 44,46 | 0,86 | [VERİ] paylas2 ile aynı |
| 2021 | 35,78 | 0,48 | [VERİ] paylas2 ile aynı |
| 2022 | 54,34 | 0,35 | [VERİ] 2023 özkaynak |
| 2023 | 40,04 | 0,15 | [VERİ] özkaynak; 30 milyar TL bağış hariç |
| 2024 | 0 | 0 | [VERİ] tire |
| 2025 | 0 | 0 | [VERİ] tire |
| Toplam |  | 4,92 | [HESAP] |

GSYH: World Bank `NY.GDP.MKTP.CN`, 8 Ekim 2026 güncellemesi [VERİ]. 2019–21 formülü paylas2'deki 3,12 puanı yeniden üretti [HESAP].

Ek aktarım 1,79 puandır (4,918−3,125) [HESAP]. Her iki senaryoda TCMB'den Hazine'ye kayar. Orta düzey S1, GSYH puanı [HESAP]:

| Aktör | Paylas2 S1 | Bu tur S1 |
|---|---:|---:|
| Hane alt | +0,13 | +0,13 |
| Hane orta | +0,45 | +0,45 |
| Hane üst | +9,74 | +9,74 |
| KOBİ | −1,92 | −1,92 |
| Büyük firma | −4,90 | −4,90 |
| Banka | −1,08 | −1,08 |
| Hazine | −3,78 | −1,99 |
| TCMB | −1,65 | −3,44 |
| Yurt dışı+artık | +3,00 | +3,00 |

Sıfır toplam korunur (sapma 0,001 puan, eski tablodaki yuvarlama ile aynı) [HESAP]. Hane, firma, banka ve yurt dışı bu kalemden kaymadı. S1'de TCMB, Hazine'den daha büyük kayba geçti. En büyük S1 kaybı büyük firmada (−4,90), en büyük kazanç üst hane grubunda (+9,74) duruyor.

## S1−S2 ne değişti [HESAP; S2 VARSAYIM]

Orta ve yüksek κ'da Hazine ve TCMB'nin S1−S2'si değişmedi: ek aktarım, bu iki düzeyde S2'deki görünür sermaye ihtiyacını aynı miktarda artırmadı. Düşük düzeyde görünür sermaye 5,63'ten 5,96'ya çıktı; Hazine'nin erteleme getirisi 5,28'den 5,61'e, TCMB'nin kaybı −10,07'den −10,40'a kaydı.

Orta düzey S1−S2 (düşük / yüksek parantezde, değişenler):

| Aktör | Düşük | Orta | Yüksek |
|---|---:|---:|---:|
| Hane alt | +0,21 | −0,26 | −0,66 |
| Hane orta | +0,44 | −0,57 | −1,43 |
| Hane üst | +2,20 | −3,61 | −9,25 |
| KOBİ | +1,34 | +4,58 | +7,79 |
| Büyük firma | +2,36 | +9,55 | +16,69 |
| Banka | −1,18 | −1,18 | −1,18 |
| Hazine | +5,61 | +8,89 | +14,80 |
| TCMB | −10,40 | −11,19 | −15,02 |
| Yurt dışı+artık | −0,59 | −6,20 | −11,75 |

Gizli maliyet 8,46'dan 8,87'ye çıktı [HESAP]. Görünür TCMB sermayesi düşük / orta / yüksek: 5,96 / 2,75 / 2,21. Ek kur (log, kümülatif): ≈0 / 0,41 / 0,82.

C1 üst20 her düzeyde kazanır: tutmadı (yalnız düşükte +). C2 TCMB en büyük kaybeden: tuttu. C3 gizli > görünür: tuttu (8,87 > 5,96 / 2,75 / 2,21). C4 büyük firma orta düzeyde en büyük kazanan: tuttu, sınırda (9,55 ve Hazine 8,89). C5 alt40 mutlak fark < 0,5: kırılgan (yüksekte 0,66). Sıralama paylas2 ile aynı kaldı. Bu bir genel denge değildir.

## Zayıf noktalar

### Z1 Banka kârı, NIM, KKM komisyonu — kısmi

Net kâr 2014–2025, 12 yıl, BDDK Aralık bülteni, yuvarlak milyar TL [VERİ]. 2014 düzeyine göre 2015–25 farklarının toplamı +3,75 GSYH puanı [HESAP]. Bu bir bağlamdır; karşı taraf yazılmadığı için S1 banka satırı −1,08'de kaldı.

Resmî "net faiz marjı" ifadesi 12 bültenin metninde yok [DOĞRULANMADI]. TBB 2024'teki tek yıl marj, sekiz yıl eşiğini tutmaz. Net faiz geliri bültenden veya faiz geliri−giderinden yazıldı [VERİ/HESAP]; 2014 düzeyine göre fark toplamı +2,99 GSYH puanı [HESAP, VEKİL]. Bu, hane ve kamu faizini de içerir.

KKM banka komisyonu, TCMB kur farkı giderinden ayrı bir satır olarak yok [DOĞRULANMADI]. Bölünmedi.

C_Z1 kapanmadı: net kâr var, NIM ve komisyon yok, S1 banka kaymadı.

### Z2 TCMB→Hazine — kapandı

2014–2025 nakit yıllarının hepsi okundu. 2024–25 dağıtım yok [VERİ]. Ayrıntı yukarıdaki tablo ve SAPMA 1. S1 Hazine −3,78'den −1,99'a, TCMB −1,65'ten −3,44'e geldi [HESAP].

### Z3 Firma ölçeği — anahtar kapandı, S1 bölüşümü değişmedi

Aynı tanım (net kambiyo, NACE 41–43 ve 68 hariç, GENEL hariç), 2009–2023 paneli: büyük firma kümülatif zarar payı 0,6898 [HESAP]. Eski anahtar 0,690. Fark 0,02 puan, eşik 5 puan. S1 KOBİ/büyük bölüşümü değişmedi.

2024 büyük payı 0,80, 2025 büyük payı 0,82, iki yıl birlikte 0,81 [HESAP, VERİ panel]. 2023 iki panelde tutmadığı için bu pay S1'e eklenmedi (SAPMA 3). BDDK KOBİ kredisi 2024–25'te sahiplik grubuna göredir, para birimine göre değildir; net döviz pozisyonunun yerine konmadı [DOĞRULANMADI].

### Z4 Servet anahtarı — açık

Gelir beşlisine göre mevduat, altın, konut veya net servet dağıtan birincil tablo bulunamadı. GYKA gelir dağılımıdır, konut sahipliği kullanım biçimidir; ikisi servet anahtarı sayılmadı. Anahtar uydurulmadı. Hane S1 duruyor.

### Z5 Yurt dışı artığı 3,75 — açık, köprü yazıldı

Orta düzey model D − doğrudan UYP = 3,00 − (−0,75) = 3,75 GSYH puanı [HESAP]. Kanal dökümü, paylas tablosundaki D satırı [HESAP]:

| Parça | Puan | UYP'de var mı |
|---|---:|---|
| k1_D | −0,63 | hayır |
| k2_D | +5,70 | kur kanalı; UYP ile aynı değil |
| k5_D | −0,25 | hayır |
| k7_D | −3,96 | hayır (banka altını karşı tarafı) |
| k8_D | +2,23 | hayır (swap karşı tarafı) |
| D3 banka | −0,10 | hayır |
| Doğrudan UYP | −0,75 | evet |

UYP dışı parçaların toplamı −2,70 [HESAP]. Bunlar düşülünce kalan k2_D − UYP = +6,45 [HESAP]. 1,0 puan eşiğinin üstünde. Z5 kapanmadı. Ana tabloda B=0 duruyor; "karşı taraf yurt içi banka olsaydı" satırı S1'in yerine geçmedi.

USD'de stok−akım (fiyat+diğer+yöntem), 2014–25 toplamı GSYH'nin +36,2 puanı [HESAP]. Bunun içinde doğrudan yatırım yükümlülüğü −7,6, portföy hisse yükümlülüğü −2,1 [HESAP]. Bu USD kavramı TL UYP'ye eklenmedi. Altın fiyatı ayrılmadı.

### Z6 Faiz ve büyüme duyarlılığı — kapandı, aktör satırı kaymadı

Üç κ duruyor. Eklenenler [VARSAYIM katsayı, HESAP], kümülatif log puan, orta düzey (ek kur 0,41, ek enflasyon 0,12):

| φ | Δi | Δr | yatırım tepkisi −0,45·Δr |
|---:|---:|---:|---:|
| 0,3 | +0,04 | −0,09 | +0,04 |
| 1,0 | +0,12 | 0 | 0 |
| 1,5 | +0,18 | +0,06 | −0,03 |

Büyüme, aktöre yazılmadan: γ=0,1 için Δg −0,04; γ=0,3 için −0,12. Yüksek düzey kabaca bunun iki katıdır. İki büyüme satırı toplanmadı. TL stok olmadığı için aktör S1−S2'si bu kanaldan değişmedi. Bu bir genel denge çözümü değildir.

### Z7 önceki açıklar

- Z7a Hane altını: yeni stok yok [DOĞRULANMADI]. Akım, açılış stoku olmadan stok kazancına çevrilmedi. Eski 2.200–3.739 ton aralığı ve 311 milyar dolarlık 2024Ç3 kutusu durur.
- Z7b Oturulan konut: imputasyon kirası ve konut stoku bu turda birincil tablodan okunmadı [DOĞRULANMADI]. NET'e girmedi.
- Z7c KKM gelir grubu: tablo yok [DOĞRULANMADI]. Mevduat diliminden pay türetilmedi. %90 yüksek tutarlı anahtar [İKİNCİL] olarak durur.
- Z7d Göç ve eğitim: uluslararası göç bülteninde bulunan ayrımlar yaş ve vatandaşlıktır. Yükseköğretim beyin göçü metodolojisi vardır; kişi sayısı × eğitim payını en az üç yıl için okunabilir birincil tablo bu turda inmedi. İmzalı indirme bağlantısı ve haber oranı hükme girmedi [DOĞRULANMADI].
- Z7e Reel emekli aylığı: SGK yaşlılık aylığı ortalaması sekiz yıl okunmadı [DOĞRULANMADI]. OECD sosyal harcama payı bunun yerine konmadı.
- Z7f Asgari ücret civarı: kazancı asgari ücretin 1,2 katının altında olan ücretli payı bulunamadı [DOĞRULANMADI]. Asgari/ortalama oranından pay türetilmedi.
- Z7g Yurt içi banka faizi: firmaların bankalara faizi ayrı satır değil. Sektör net faizinin 2014'e göre +2,99 puanlık farkı [VEKİL, HESAP] 1,24 kalanından düşülmedi.

## Kapanış

| Kod | Sonuç |
|---|---|
| C_Z1 | Kısmi. Net kâr 12 yıl. NIM ve KKM komisyonu açık. S1 banka aynı. |
| C_Z2 | Kapandı. 2014–25 nakit aktarım okundu. S1 Hazine ve TCMB kaydı. |
| C_Z3 | Anahtar kapandı (0,690, eşik altı). 2024–25 payı ölçüldü, S1'e yazılmadı. |
| C_Z4 | Açık. Servet anahtarı yok, uydurulmadı. |
| C_Z5 | Açık. Köprü sonrası kalan 6,45 puan. |
| C_Z6 | Kapandı. φ ve γ tabloda. Büyüme ve faiz aktöre yazılmadı. |
| C_Z7 | Yedi alt kalem de açık. |

Dosyalar: `tcmb_hazine_aktarim.csv`, `tablo_zayif_S1S2.csv`, `ozet_S1eksiS2_zayif.csv`, `firma_kambiyo_olcek.csv`, `kopru_yurtdisi.csv`, `uyp_stok_akim.csv`, `banka_bddk.csv`, `s2_faiz_buyume.csv`, `zayif_S1S2.png`, `firma_kambiyo_pay.png`.

Kaynaklar: TCMB bağımsız denetim raporları (yasal özkaynak ve kâr dağıtım), TCMB sektör bilançosu panel zip (2009–2023 ve 2023–2025), BDDK Türk bankacılık sektörü aylık bülteni Aralık 2014–2025, TCMB UYP Tablo 3 ve ödemeler dengesi Tablo 4 (paketteki `uyp.txt`, `bop.txt`), World Bank WDI GSYH. Büyük zip ve PDF git'e konmadı; türetilmiş CSV kondu.
