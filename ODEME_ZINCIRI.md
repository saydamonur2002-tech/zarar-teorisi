# Ödeme zinciri kalıcılığı

Sentetik ağ. TCMB sektör verisine, finansal hesaplara veya bu depodaki L/G matrislerine kalibre edilmedi. Sayılar ölçüm değildir.

## Hüküm

Dağıtık faillik bu simülasyonda **desteklendi**.

Orta kilitte düşük banka ve yüksek gecikme maliyeti, yüksek banka ve düşük gecikmeye göre kalıcılığı pratik eşikle uzatıyor.

Birincil kontrast (kötü köşe − iyi köşe, aynı 80 şok): ortalama fark 16.77 periyot, medyan fark 18.00, tek yanlı Wilcoxon p = 6.98e-15, iki yanlı p = 1.396e-14. KS istatistiği 0.975, p = 1.654e-64.

Küçük alacaklının ödenmeyen payı, iyi köşede tanımsız: o köşe ödenmeyen tutar bırakmıyor (n = 0). Sıkıntılı hücrelerde pay medyan 0.40, aralık 0.34–0.43. Bileşim parametreyle kaymıyor; değişen, ödenmeyen tutarın büyüklüğü.

Global etiket permütasyonu: hücre ortalamalarının aralığı 20.19 periyot, p = 0.001 (999 karıştırma).

## Ne sabit, ne değişti

204 firma, 17 sektör, sektör başına 12 firma. Kenar sayısı 1205, yoğunluk 0.0291, yönsüz ortalama kümelenme 0.095, ortalama çıkış derecesi 5.91, giriş gücü Gini 0.390, PageRank Gini 0.615. Büyük düğüm 51, küçük düğüm 102.

Bu ölçüler parametre ızgarasında yeniden çekilmedi. Aynı şok çarpanları 80 tohumda her hücreye uygulandı. Değişenler: kilit eşiği ve süresi [(0.5, 1), (0.7, 2), (0.85, 3), (0.95, 5), (0.99, 8)], gecikme α [0.0, 0.05, 0.15, 0.3, 0.6], banka çarpanı [0.0, 0.5, 1.0, 2.0, 4.0]. Her periyot sonunda likiditeye sözleşmedeki (borç − alacak) eklenir; herkes tam öderse stok yerinde kalır. Bu dış akım kaçırılan tahsilatı yerine koymaz.

Seçilen şok/tampon adayı C: likidite tamponu U(0.95, 1.4), 3 sektörde likidite × 0.3, diğer firmaların 8% kadarı × 0.45. İç bölge kuralını (şoksuz kalıcılık 0, baz ortalama 2–16, standart sapma en az 1) hiçbir aday tutmadı. Yedek kural, şoksuz tıkanmayanlar arasından baz ortalaması 8'e en yakın adayı seçti. Köşe farkına bakılmadı. Kalibrasyon tablosu `odeme_sonuc.json` içindedir.

Şok büyüklüğü kontrolü (aynı ağ, aynı üç köşe, hükme girmez): aday A: iyi 0.00, baz 0.00, kötü 0.00; aday B: iyi 0.00, baz 0.00, kötü 9.47

Şoksuz baz parametre: kalıcılık 0, ortalama yeni fatura tahsil oranı 1.000.

## Kalıcılık

İyi köşe (kilit orta, α = 0.0, banka = 4.0): ortalama 0.00, medyan 0.0, P(kalıcılık ≥ 4) = 0.00.

Baz (orta, orta, orta): ortalama 0.44, medyan 0.0, P = 0.04.

Kötü köşe (kilit orta, α = 0.6, banka = 0.0): ortalama 16.77, medyan 18.0, P = 0.95.

Parametreler her koşuda ızgaradan rastgele çekilince: ortalama 3.79, medyan 0.0. Baz ile KS p = 0.01809.

Kilit süresi (diğerleri orta): 1: ortalama 0.00, medyan 0.0, P(≥4) 0.00; 2: ortalama 0.00, medyan 0.0, P(≥4) 0.00; 3: ortalama 0.44, medyan 0.0, P(≥4) 0.04; 5: ortalama 6.04, medyan 6.0, P(≥4) 0.55; 8: ortalama 10.97, medyan 12.0, P(≥4) 0.90

Gecikme α (diğerleri orta): 0: ortalama 0.00, medyan 0.0, P(≥4) 0.00; 0.05: ortalama 0.00, medyan 0.0, P(≥4) 0.00; 0.15: ortalama 0.44, medyan 0.0, P(≥4) 0.04; 0.3: ortalama 3.11, medyan 0.0, P(≥4) 0.41; 0.6: ortalama 5.31, medyan 3.0, P(≥4) 0.47

Banka çarpanı (diğerleri orta): 0: ortalama 12.39, medyan 14.0, P(≥4) 0.85; 0.5: ortalama 4.67, medyan 4.0, P(≥4) 0.54; 1: ortalama 0.44, medyan 0.0, P(≥4) 0.04; 2: ortalama 0.00, medyan 0.0, P(≥4) 0.00; 4: ortalama 0.00, medyan 0.0, P(≥4) 0.00

Eğimler (tohum içi doğrusal eğim, öngörülen yöne tek yanlı Wilcoxon): kilit medyan eğim 3.250, aralık 12.00, p = 5.605e-14, destek = True. Gecikme medyan eğim 4.893, aralık 3.00, p = 8.041e-09, destek = True. Banka medyan eğim -2.500, aralık 14.00, p = 1.758e-13, destek = True.

Ayrı KS, orta diğer parametrelerde: kilit ucu p = 9.588e-43 (ortalama fark 10.97); banka 0 eksi banka 4 p = 1.575e-36 (ortalama fark 12.39); gecikme ucu p = 8.489e-11 (ortalama fark 5.31).

## Kim yavaşlıyor, maliyet nereye gidiyor

Yavaşlık, firmanın kilitli olduğu veya ödeme oranının 0.70 altında kaldığı periyot sayısıdır. Kötü köşede sektör ortalamaları 10.3–16.1 periyot; tıkanma birkaç sektörde kalmıyor. Baz köşede yavaşlık daha toplu: Perakende 5.4, Diğer hizmet 5.0, Toptan 1.3.

Büyük borçlunun ödeyemediği tutarın küçük alacaklıya düşen payı, kötü köşede medyan 0.432. Bu pay ile küçük−büyük yavaşlık farkının Spearman korelasyonu 0.569 (p = 3.77e-08). Aktarım oranı, aynı kötü köşe içinde kimin daha yavaşladığını öngörüyor. Parametre değişince ödenmeyen tutarın küçük payı neredeyse yerinde kalıyor.

Gün kayması: kötü ve baz: Spearman -0.095 (p = 0.175), ilk onda bir kesişim 0.00. kötü ve iyi: Bir köşede yavaşlık sabit; sıra tanımsız.

Maliyet şekli yan deneydir, hükme girmez. Ortalama kalıcılık: {"alpha_0": {"banka_0": 1.175, "banka_4": 0.0}, "dogrusal_0_30": {"banka_0": 14.9625, "banka_4": 0.0}, "konveks_gamma_1_8_alpha_0_30": {"banka_0": 16.0875, "banka_4": 0.0}}.

## Hangi hipotez elendi

Parametre-bağımsız hipotez, seçilen şokta elendi. Aynı ağ ve aynı şok çarpanlarıyla kilit, gecikme ve banka kalıcılık dağılımını değiştiriyor. Banka çarpanı 4 olan 25 hücrenin hepsinde ortalama kalıcılık 0.00. En yumuşak kilitte (eşik 0.50, süre 1) en yüksek hücre ortalaması 0.14. İkisi de sistemik tıkanmayı kapatıyor. Gecikme, banka kapalıyken süreyi uzatıyor; banka açıkken etkisi küçülüyor.

Maliyetin büyük düğümden küçük tedarikçiye kaydığı biçimi desteklenmedi. Sıkıntı olan hücrelerde küçük alacaklının payı dar bir bantta. Kötü köşede büyük firmalar küçüklerden daha yavaş (yavaşlık farkı tabloda, banka 0 ve yüksek α). Ara banka limitinde küçükler daha yavaş. Aktarım oranı bu farkı koşular arasında öngörüyor; parametre onu sistematik olarak büyütmüyor.

Yumuşak şok (aday A) üç köşede de kalıcılık üretmiyor. O şokta parametre kolu gereksiz, hipotez elenir. Aday B'nin kötü köşesi uzuyor, iyi köşesi uzamıyor: eşik, şok büyüklüğünde. Seçilen aday C bu eşiğin üstünde. Sonuç şok protokolüne bağlıdır; her şokta parametre bağımlılığı iddia edilmez.

Eleme kuralı kodda: 125 hücrenin ortalamaları tohum içinde karıştırılınca gözlenen aralık çıkmıyor (p > 0.05), köşe farkı iki yanlı Wilcoxon ile ayrılmıyor ve maliyet payı en az 5 puan kaymıyorsa parametre-bağımsız hipotez kalır. Destek için kötü köşe iyiden en az 2 periyot uzun ve tek yanlı p < 0.05 olmalıydı. Bu koşu destek eşiğini geçti. Maliyet payı kayması geçmedi; hüküm kalıcılık kontrastına dayanır.

## Dosyalar

`odeme_hucre.csv` hücre özeti, `odeme_kosu.csv` 10.000 koşu, `odeme_sektor.csv` sektör yavaşlığı, `odeme_firma_sira.csv` firma sırası, `odeme_kalicilik.png`, `odeme_maliyet.png`, `odeme_sonuc.json`.

Tekrar: `python3 odeme_zinciri.py`. Ağ tohumu 20261010.
