# Çıpalı üç kural

Ön kayıt `cipali_uc_kural/ON_KAYIT.md` içinde 2026-10-21T07:01:45Z kilitlendi. Katsayılar ondan sonra hesaplandı. Eşikler kaydırılmadı.

Bu metin senaryo çubuklarının tutup tutmadığını yazar. Çıpa bir sonucu doğurdu denmez. Katsayılar [TAHMİN]. Koşu ölçüm değildir.

Veri çekimi EVDS3 herkese açık uçtur (`https://evds3.tcmb.gov.tr/igmevdsms-dis`), anahtarsız. EVDS anahtarı okunmadı.

## Hüküm

- H-C1, çıpa geri gelince üç kural: **BELİRSİZ**. Eşik çıpa düzeyi: **yok**.
- H-Sarmal: **BELİRSİZ**.
- H-Rezerv: **BELİRSİZ**.
- H-Gecis, 2024–25 geçiş çöküşü: **BELİRSİZ**.
- Ücret ayağı (üç kural eşiği değildir): iki varyantta birden K1’in geçtiği en küçük ızgara w = **0,00**. Geçen küme: 0,00.

## Beklenti [TAHMİN]

Denklem serbest terimsiz: e − π = w (h − π) + φ g12. Geriye bakış 1 − w. 0,37 ve 0,71 girdi değildir.

| Pencere | n | w | 1 − w | φ | w Newey-West %95 |
| --- | ---: | ---: | ---: | ---: | --- |
| R2013 | 12 | 0,679 | 0,321 | 0,031 | [0,586; 0,772] |
| R1617 | 24 | 0,577 | 0,423 | 0,027 | [0,439; 0,715] |
| R1823 | 72 | 0,783 | 0,217 | 0,056 | [0,707; 0,860] |
| R2426 | 33 | 0,684 | 0,316 | 0,014 | [0,536; 0,832] |
| Y2018 | 12 | 0,400 | 0,600 | -0,069 | [0,289; 0,510] |

Çiftler bootstrap, tohum 20261021, B = 1000, yüzdelik 2,5–97,5.

| Pencere | w bootstrap | φ bootstrap |
| --- | --- | --- |
| R2013 | [0,588; 0,766] | [0,003; 0,054] |
| R1617 | [0,438; 0,747] | [-0,014; 0,082] |
| R1823 | [0,738; 0,829] | [0,024; 0,090] |
| R2426 | [0,545; 0,816] | [-0,187; 0,269] |
| Y2018 | [0,262; 0,531] | [-0,131; -0,018] |

Hedef her ay 5. Yıl yılı nokta hedef belgesi inip farklı bir sayı vermedi: [DOĞRULANMADI].
Hüküm faizi: VEKIL TP.APIFON4 (ağırlıklı ortalama fonlama). Bir hafta repo tablosu hüküm serisi olmadı.

## Geçiş [TAHMİN]

π1 = α + λ g1. λ aynı ayın kurdan fiyata oranıdır.

| Pencere | n | λ | Newey-West %95 |
| --- | ---: | ---: | --- |
| R2013 | 12 | -0,160 | [-0,363; 0,043] |
| R1617 | 24 | 0,160 | [0,119; 0,200] |
| R1823 | 72 | 0,214 | [0,107; 0,321] |
| R2426 | 33 | 0,409 | [-0,220; 1,038] |
| Y2018 | 12 | 0,131 | [0,057; 0,205] |

2024-01..2025-12 çöküş tanımı: **tutmaz**. λ = 0,503. Tanım, bu λ’nın 2013 noktasının yarısından küçük olmasını ve %95 üst ucunun 2013 noktasının altında kalmasını ister. Tutmayınca kaldırılacak çöküş yoktur.

λ bootstrap: R2013 [-0,441; 0,181]; R2426 [-0,271; 1,117].

## Rezerv vekili

θ = 0,5170, c = —. sınırlı değil. S, brüt rezerv düşüşüdür [VEKİL], yayımlanmış satış değildir.

## Koşular

Kilitli yol. Birlikte: K1 ücret, K2 tavan, K3 geri alma tetiki.

| Paket | Faiz | K1 | K2 | K3 | Birlikte | Sarmal | Enflasyon 2031 | Kapsama 2031 |
| --- | --- | --- | --- | --- | --- | --- | ---: | ---: |
| (a) R2426 çıpasız | sabit | kaldi | gecti | sinanmadi | kaldi | yok | 36,0 | 0,288 |
| (a) R2426 çıpasız | tepkili | kaldi | gecti | sinanmadi | kaldi | yok | 35,7 | 0,289 |
| (b) R2013 | sabit | kaldi | gecti | sinanmadi | kaldi | yok | 36,6 | 0,232 |
| (b) R2013 | tepkili | kaldi | gecti | sinanmadi | kaldi | yok | 12,5 | 0,386 |
| (c1) R1617 | sabit | gecti | gecti | sinanmadi | belirsiz | yok | -14,6 | 1,135 |
| (c1) R1617 | tepkili | gecti | gecti | sinanmadi | belirsiz | yok | 31,6 | 0,647 |
| (c2) R1823 | sabit | kaldi | gecti | sinanmadi | kaldi | yok | 22,1 | 0,371 |
| (c2) R1823 | tepkili | kaldi | gecti | sinanmadi | kaldi | yok | 32,0 | 0,326 |
| (d) kademeli | sabit | kaldi | gecti | sinanmadi | kaldi | yok | 28,8 | 0,421 |
| (d) kademeli | tepkili | kaldi | gecti | sinanmadi | kaldi | yok | 13,0 | 0,476 |

K3 tetik sayısı tablodaki kilitli yolların toplamında 0. Tüketici tavanı dondurması her yolun 21 çeyreğinde açık. Dondurma, alt dilim borç varsayımı eşik üstünde kaldığı için açıktır; çıpa ağırlığı bu sayacı değiştirmez. K3 öncülü oluşmadığı için sınanmadı.

## Izgara

Diğer katsayılar R2426 noktasında. Yalnız w değişir.

| w | Sabit birlikte | Tepkili birlikte | K1 sabit | K1 tepkili |
| ---: | --- | --- | --- | --- |
| 0,00 | belirsiz | belirsiz | gecti | gecti |
| 0,25 | kaldi | belirsiz | kaldi | gecti |
| 0,50 | kaldi | kaldi | kaldi | kaldi |
| 0,75 | kaldi | kaldi | kaldi | kaldi |
| 1,00 | kaldi | kaldi | kaldi | kaldi |

K1 iki varyantta birden yalnız tabloda geçtiği w düzeylerinde tutulur. w yükseldikçe ücret kuralı kalır: taban hedefe yakınsamış beklentiyi izler, yaşam maliyeti gerçekleşen enflasyonla yürür. Bu en küçük w, çıpa geri gelince üç kuralın açıldığı eşik değildir. O eşik H-C1’dedir ve kurulamadı.

## Duyarlılık

Hükmü değiştirmez. [TAHMİN].

| Pencere | 6 ay enflasyonda w | 3 ay kurda φ | gecikmeli λ |
| --- | ---: | ---: | ---: |
| R2013 | 0,859 | -0,008 | 0,075 |
| R1617 | 1,038 | 0,016 | 0,081 |
| R1823 | 0,886 | 0,057 | 0,314 |
| R2426 | 0,517 | 1,119 | 0,294 |
| Y2018 | 0,662 | -0,037 | — |

## Zayıf noktalar

- `uc_kural_senaryo.py` içinde faiz kuralı ve rezerv stoku yoktu. Bu koşu o iki katmanı ayrı kurdu; kilitli üç senaryonun 2031 tablosu yeniden yazılmadı.
- Ücret kuralı PATIKA tablosunu ezmez. Taban, beklentiyle yürür. Bu, kilitli dosyanın kendi 2031 kapsama sayısının aynısı değildir.
- K3, üretken pay ve korunmasız stok öncülü yolun içinde oluşmazsa sınanmadı kalır. Mekanik tavan (alt20 başlangıcı 2,8) K2’yi çıpadan bağımsız bağlayabilir; ölçüm yine de mevcut yolla farktır.
- Faiz TP.APIFON4’tür [VEKİL]. Bir hafta repo ile aynı şey diye okunmaz.
- Rezerv satışı brüt stok düşüşünden gelen c’dir [VEKİL]. c yoksa rezerv hükmü BELİRSİZ.
- Hedef 5, yıl belgesi inmeden [DOĞRULANMADI].
- Senaryo 2026-Q4’ten 2031-Q4’e kadardır. Patlama (yıllık enflasyonun mutlak değeri 500’ü aşarsa) sarmal ve ücret kalır diye yazılır; yol yapıştırılmaz.
- R1617 kur denklemi 2016–17 fonlama aralığında kuruldu. Sabit faiz yolu onu 2026 fonlama düzeyine taşır; (c1) sabit yolda 2031 enflasyonu eksiye yazar. Bu ölçüm değildir.
- φ ve λ Newey-West uçlarında ücret ayağının geçen en küçük w kümesi: 0,00, yok, 0,00, 0,00. Bu küme hükmü değiştirmez.
- βe = 0 duyarlılığı, tepkili kilitli: (a) K1 kaldi, sarmal var; (b) K1 gecti, sarmal yok. Birincil hüküm βe’li denklemdedir.

## Ne denmez

- Çıpa enflasyonu indirdi veya üç kuralı işletti denmez. Çubuk senaryo yolunda tutuldu veya tutulmadı.
- 0,37 ve 0,71 bu turda yeniden bulunan katsayı diye yazılmaz.
- Fonlama maliyeti bir hafta repo diye yazılmaz.
- Brüt rezerv düşüşü müdahale satışı diye yazılmaz.
