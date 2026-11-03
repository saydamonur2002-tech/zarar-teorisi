# Ön kayıt — kur müdahalesinin rezerv maliyeti, c

Yazım zamanı (UTC): 2026-10-20T09:12:13Z

Bu dosya, rezerv, kur ve kontrol serilerinin indirilmesinden ve her türlü katsayı hesabından önce yazıldı. Eşikler ve pencereler skor görüldükten sonra değiştirilmez. Uygulama ayrılırsa satır SAPMA diye işaretlenir.

`model_rr.py` bu yazım anında çalışma ağacında ve `origin/main` üzerinde yoktu. Ekli dosya diske düşmedi. Model koşusu, dosya bulunursa onun fonksiyonuyla yapılır. Bulunamazsa TÜFE yolu ve tükeniş tarihi uydurulmaz; satır DOĞRULANMADI kalır.

## c ne

c, çeyreklik kurun yukarı sapmasının 1 puanını bastırmakla beraber giden rezerv satışıdır. Birim: milyar ABD doları / puan.

Puan, 100 × log farktır. Kur E, TCMB döviz satış USD/TRY aylık ortalamasının çeyrek içi aritmetik ortalamasıdır.

g_t = 100 × ln(E_t / E_{t−1})

g pozitifse lira değer kaybetmiştir. “Yukarı sapma” bu işaretteki değer kaybıdır.

Satış S_t, milyar dolardır ve lirayı tutmak için döviz satıldığında pozitiftir. Birincil S, yayımlanmış doğrudan TCMB döviz satışı artı yayımlanmış kamu bankası döviz satışıdır. İkisi ayrı sütundur; toplam yalnız ikisi de aynı pencerede yayımlanmışsa kurulur. Biri yoksa diğeriyle doldurulmaz.

Doğrudan satış satırı yoksa vekil:

S_vekil = −(swap hariç net rezervin çeyrek farkı) − altın değerleme − cari işlemler hesabının o çeyrekteki işaretiyle rezervi otomatik artıran kısmı

Altın değerleme = ons miktarı × ons fiyat farkı. Ons veya fiyat yoksa değerleme düşülmez ve vekil kullanılmaz; o çeyrek S boş kalır.

Cari işlemler, rezervin “satış” sayılmaması için çıkarılır: cari fazla rezervi artırır, cari açık rezervi eritir ama bu erime müdahale satışı değildir. Vekil formülünde cari açık (negatif CA) rezerv düşüşünden düşülmez; yani S_vekil = max(0, −Δ net_ex_swap − altın_değerleme + min(CA, 0)). CA milyar dolar, açık negatiftir. min(CA, 0) açık kadar rezerv düşüşünü satıştan ayırır. Cari fazla satış diye yazılmaz. Bu vekil [VEKİL]’dir, birincil S’nin yerine hükmü kurmaz. Birincil S yoksa hükmün c’si bu vekille hesaplanır ve etiket VEKİL kalır.

KKM stok dönüşümü, ihracatçı döviz teslimi ve reeskont, ayrı kanaldır. Birincil S’ye eklenmez. Tutar yayımlanmışsa yan sütundur.

## Denklem

Örnek: 2018-Q1–2025-Q4, çeyrek. 2025 son çeyrek eksikse pencere son tam çeyrekte durur, doldurulmaz, SAPMA yazılır. 2026 örneğe girmez.

g_t = α + θ · S_t + γ1 · i_{t−1} + γ2 · CA_{t−1} + γ3 · ΔCDS_{t−1} + γ4 · portföy_{t−1} + γ5 · dolarizasyon_{t−1} + γ6 · g_{t−1} + ε_t

i, TCMB politika faizi (bir hafta repo; yoksa ağırlıklı ortalama fonlama). CA, cari işlemler, milyar dolar. CDS, 5 yıl Türkiye CDS’i, puan; yoksa denklemden çıkar, SAPMA-kontrol, eşik kaymaz. Portföy, yurt dışı yerleşik net portföy akımı, milyar dolar. Dolarizasyon, döviz mevduatı / toplam mevduat.

θ, 1 milyar dolar satışın g üzerindeki koşullu beraberliğidir. Satış değer kaybını bastırıyorsa θ negatiftir.

c = −1 / θ

θ’nın %95 aralığı sıfırı içerirse c’nin sonlu aralığı yazılmaz; “sınırlı değil”. Aralık sıfırın dışında ve θ negatifse delta yöntemi:

se(c) = se(θ) / θ²

%95 aralık c ± 1,96 se(c). Standart hata Newey-West, gecikme 4. Bu bir nedensellik aralığı değildir.

## İçsellik

Satış, baskı yükselince artar. Bu, θ’yı sıfıra veya pozitife iter; c’yi büyük gösterir. OLS birincil beraberliktir, karşı-olgusuz nedensellik cümlesi kurulmaz.

Araç (kilitli, skor öncesi): Z_t, aşağıdaki pencerelerde 1, dışında 0. Araç, o pencerelerin takvim/anlatı tarihi olduğu iddiasıdır; “dışsal” diye kanıtlanmış sayılmaz.

Birinci aşama F < 10 ise IV noktası birincil değildir. Birincil, aşağıdaki sıra bozulmadan seçilir.

## Birincil c’nin seçimi

1. Tam örnek OLS’te θ < 0 ve %95 aralığı sıfırın dışındaysa birincil c bu θ’dan gelir.
2. Değilse birincil c, bastırma görülen epizot oranlarının satış ağırlıklı ortalamasıdır. OLS ayrıca yazılır, “ayırt edilemedi” denir.
3. İkisi de yoksa birincil c DOĞRULANMADI. Sıfır yazılmaz. Model koşusu yapılmaz.

Epizot c’si ile regresyon c’si 2 kattan fazla ayrılırsa birincil sayı “kararsız” diye işaretlenir; eşik buna göre kaydırılmaz.

## Epizot pencereleri

Skor görmeden kilitlendi. Yeni pencere eklenmez.

| Kod | Pencere | Ne |
| --- | --- | --- |
| E1 | 2018-Q3–2018-Q4 | Ağustos 2018 ve hemen sonrası |
| E2 | 2019-Q1–2020-Q4 | Kamu bankası penceresi |
| E3 | 2021-Q4 | Aralık 2021 |
| E4 | 2023-Q1–2023-Q2 | Seçim öncesi |
| E5 | 2023-Q3–2023-Q4 | Seçim sonrası |
| E6 | 2025-Q1 | Mart 2025 |

E2 için dolaşan “yaklaşık 128 milyar dolar” rakamı, resmi satır bulunmadan S’ye yazılmaz.

## Epizot karşı-olgusu

Karşı-olgu yalnız epizot dışı çeyreklerde kurulur:

g_t = a + b1·i_{t−1} + b2·CA_{t−1} + b3·ΔCDS_{t−1} + b4·portföy_{t−1} + b5·g_{t−1} + e

Epizot çeyreğinde P_t bu denklemin uydurmasıdır. Bastırılan puan = max(0, P_t − g_t), ve ancak o çeyrekte S > 0 ise. S ≤ 0 ise o çeyrek bastırma hanesine yazılmaz.

Epizot c = (penceredeki S toplamı) / (bastırılan puan toplamı).

Payda ≤ 0 ise c tanımsızdır; “bastırmadı” yazılır, ortalamaya sıfır diye girmez.

Bu P, yapısal karşı-olgu değildir. Etiket [HESAP]. “Müdahale olmasaydı kur şöyle olurdu” cümlesi kurulmaz. Cümle: “epizot dışı beraberlikten sapma”.

## Erteleme ve birikme

Epizot bitince sonraki 4 çeyrekte fazla değer kaybı = Σ max(0, g − P).

- Bu toplam, bastırılan puanın ≥ %70’i ise pencere “erteledi”.
- < %30 ise “baskıyı o pencerede karşı-olgudan daha fazla geri getirmedi” (offset diye kısaltılır; nedensel dengeleme iddiası değildir).
- Arası “kısmi”.

Son epizotta 4 çeyrek yoksa o test boştur, doldurulmaz.

Birikme, tam örnekte:

g_t = α + θ·S_t + φ·Birikim_{t−1} + aynı kontroller + ε

Birikim, geçmiş bastırılan puanların, sonraki 4 çeyrekte geri gelen kısmı düşülmüş stokudur. φ’nin %95 aralığı sıfırın üstündeyse “bastırılan baskı sonraki değer kaybıyla beraber artıyor” yazılır. Aralık sıfırı içerirse birikme ayırt edilemedi. φ tek başına neden değildir.

## Doğrusal olmayan maliyet

θ_t etkileşimi:

g_t = α + θ0·S_t + θ1·S_t·(R_{t−1} / R_medyan) + kontroller + ε

R, swap hariç net rezervin çeyrek başı düzeyi; yoksa brüt rezerv. R_medyan, örnek medyanı, sıfırdan büyük.

H0: θ1 = 0, Newey-West. θ1 > 0 ve aralık sıfırın dışındaysa (rezerv düşünce satışın değer kaybını bastırma beraberliği zayıflıyor, çünkü θ0 negatifken pozitif etkileşim |θ|’yı küçültür) “c, rezerv düşünce yükseliyor” yazılır. Aksi halde yükseliş ayırt edilemedi.

## Yanlışlama

Izgara 1 / 3 / 10 / 30 bu turun hedefi değildir. Onların ürettiği “kurtarıldı / 2031” hükmü c’yi seçmek için kullanılmaz.

- “c ≤ 10” yanlışlanır, birincil %95 aralığın tamamı 10’un üstündeyse.
- “c ≥ 30” yanlışlanır, birincil %95 aralığın tamamı 30’un altındaysa.
- Aralık hem 10’u hem 30’u örtüyorsa ızgara hükmü BELİRSİZ.
- Aralık sınırsızsa veya birincil c yoksa BELİRSİZ.

Epizot oranı için ayrı %95 aralık yoktur. Yerine, epizot içi çeyrekleri birer birer dışarıda bırakınca c’nin en küçüğü ve en büyüğü yazılır. Bu, örnekleme aralığı diye adlandırılmaz.

## Model koşusu

Birincil c ve, varsa, %95 uçları ile `model_rr` içinde üç kural, b = 1,26 ve b = 0,42 yeniden koşulur. Çıktı: hüküm, rezervin bittiği çeyrek, TÜFE yolu. Model dosyası yoksa bu üçü DOĞRULANMADI.

Modelin kendi ızgarası (c ≤ 10 kurtarıldı, c ≈ 30 iken çöküş 2031’e kayar, rezerv 2029-Q3 biter) ancak o kod çalışınca karşılaştırılır. Kod yokken o tarihler yeniden üretilmez.

## Etiket ve yasak

VERİ kaynak tablosu. VEKİL başka kapsam veya stok farkından türetilmiş satış. HESAP bu dosyadaki formül. TAHMİN açık varsayım. DOĞRULANMADI bulunamayan; sıfır yazılmaz.

Sayı uydurulmaz. EVDS3 iç uç noktası yok. Sertifika doğrulaması atlanmaz. TÜİK 403 aşılmaz. EVDS anahtarı okunmaz.

## SAPMA (hesaptan önce, katsayı görülmeden)

SAPMA-formul. Kilitli satır `S = max(0, −ΔR − altın_değerleme + min(CA, 0))` altın fiyatı düşünce fiyat kaybını satışa ekler: değerleme = ons × fiyat farkı negatif olunca `−ΔR − değerleme` büyür. Niyet cümlesi, fiyat etkisinin satış sayılmamasıdır. Uygulanan vekil:

S = max(0, −(ΔR − değerleme) + min(CA, 0)) = max(0, −ΔR + değerleme + min(CA, 0))

Değerleme = önceki ayın ons miktarı × (aylık ortalama ons fiyatı − önceki ay). Çeyrek değerlemesi üç ayın toplamıdır. ΔR çeyrek sonu stok farkıdır. Literal kilitli işaret ayrıca sütun olarak durur, hükmün c’sine girmez. Eşik kaymadı.

SAPMA-kontrol. Türkiye 5 yıl CDS’i EVDS kataloğunda ve TCMB veri gruplarında yok. γ3 denklemden çıktı. Epizot karşı-olgusundan b3 de çıktı. Eşik kaymadı.

SAPMA-tanim. “Swap hariç net” için ön kayıt satır kodu kilitlemedi. Kullanılan satırlar, URDL aylık şablonu: R = (TP.REZVARPD.K1 + TP.DOVVARNC.K14 + TP.DOVVARNC.K23) / 1000, milyar dolar. K14 yurt içi para karşılığı forward/future net pozisyonudur (para swapının gelecekteki bacağını içerir). K23 “diğer” önceden belirlenmiş kalemdir. Bu, bütün II.1 yükümlülüklerini (zorunlu karşılık, Hazine döviz mevduatı) düşen IMF likidite neti değildir. Brüt ayrıca yazılır. Eşik kaymadı.

SAPMA-birikim. Ön kayıt, aynı değer kaybının birden fazla geçmiş bastırmadan düşülmesini yasaklayan bir sıra yazmadı. Uygulama: bastırılan puanlar kuyruğa girer; bir çeyrekteki fazla değer kaybı en eski kalan puandan düşülür (FIFO). Aynı çeyrekte bastırma ve fazla değer kaybı birlikte pozitif olamaz, çünkü biri max(0, P−g) diğeri max(0, g−P). Eşik kaymadı.
