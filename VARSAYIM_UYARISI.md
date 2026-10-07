# Varsayım uyarısı

Bu depo kapalı bir muhasebe iskeleti ve kalibrasyondur. Aşağıdaki sayılar ölçülmüş gerçek gibi okunursa model olduğundan sert görünür. Kaynak not: `OKU.txt` (7 Ekim 2026 çekimi).

İki sınıf var. **Varsayım:** modele elle konmuş pay, eşik veya faiz. **Doğrulanmadı:** iddia duruyor ama belgeyle kapanmadı. İkisi de sonuç satırına girdi diye yazılmaz.

## Elle konmuş varsayımlar

**Hane alt bölünmesi ölçüm değildir.** H = Ha (asgari ücretli) + Hm (memur) + Ho (diğer). Varlık/mevduat payı Ha %5, Hm %15, Ho %80; bu da ölçüm değil. Borç payında iki katman var, karıştırılmamalı.

İlk kullanıcı varsayımı %70'di. `OKU.txt` satır 101 hâlâ bunu taban diye yazıyor ve Ha netini −3,95 trilyon TL veriyor (varlık 1,46, borç 5,40, kişi başı ~789 bin TL, yıllık gelirin 2,3 katı). Bu sayı %70 duyarlılık satırının sayısıdır, çalışan taban değildir.

Çalışan taban `hane_alt.py` içinde `D_A_BASE = 0.40`. Yorum satırı bunu açıkça söylüyor: ilk varsayım %70'ti, gözlenen stresle uyumlu aralığın üstündeydi, taban %40'a indirildi. 2026-Q1'de bu payla Ha neti −1,63 trilyon TL (varlık 1,46, borç 3,09); kişi başı 451 bin TL, yıllık gelirin 1,34 katı; ödenemez kısım 2,16 trilyon; tanınırsa lambda_B = 0,16. %70 hâlâ duyarlılık tablosunda duruyor: orada lambda_B = 0,59.

Çapraz kontrol: gözlenen hane stresinden (takipteki 0,37 trilyon TL ile yakın izlemenin hane payı 2,47 trilyon TL) ima edilen Ha borç payının üst sınırı %17–44. %40 bu bandın üst kenarı, %70 bandın dışında. %70 ancak çok gelirli haneler, borcu borçla çevirme ya da gizli temerrüt ile tutulur. "Yük stoku" bu üçüncünün adı; ölçüm değil.

**VYS hane payı da taban.** `vys_kanali.py` hane payını %40 ile çalıştırır. Olumlu ölçütü şuydu: model hatasız ve %40, gözlenen stresin ima ettiği %17–44 aralığının içinde, üst sınıra yakın. Yakın izlemenin %80'i hane varsayımıyla geçer; orta stresle %27'yi aşar. VYS'nin devraldığı portföyde bireysel pay ~%80 varsayımıyla hane yükünün ~%25'i (106 milyar TL) banka raporlamasının dışında kalır. Satılan havuzların karşılık düzeyi bilinmiyor; satış bankaya zarar mı kâr mı yazar belirsiz. Hane borcu her iki durumda da nominal kalır.

**Mükellef–hazne ayrımı varsayımdır.** Merkezi yönetim sınıflaması kapanıyor (alt kalemler üst kalemi %0,0 sapmayla veriyor). Kimin ödediği kapanmıyor: gelir/mülkiyet/tüketim vergisi H'ye, kurumlar ve dış ticaret F'ye, damga-harç-diğer yarı yarı yazıldı. Son 4 çeyrek vergi yükü bu ayrımla H %57, F %43; harcama alıcısı H %44, F %35, B %13, D %8. Bütçe dengesi ile K′ net işlem akışının seviye korelasyonu 0,63, fark korelasyonu −0,15. Yani merkezi yönetim, SGK + yerel yönetim + TCMB'yi içeren K′'yi temsil etmiyor.

**Gecikme faizi ve tahsilat en zayıf varsayım.** Çift kayıtta gecikme faizi %63,2 (ihtiyaç faizi), ömür boyu tahsilat %16,5 (20 çeyrek), kısmi ödeme yok. Birikmiş faiz bu üçüne bağlı. Yasal sınır ve kısmi ödeme doğrulanmadı. Banka tarafı hafif, borçlu tarafı büyük çıkmasının nedeni büyük ölçüde budur.

**Sermaye eşiği önceki girdi.** SYR %16,5 yeniden doğrulanmadı; asgari %12 varsayım. Serbest sermaye 1.236 milyar TL bu eşiğe bağlı. Eşik kayarsa lambda_B ve "serbest sermayeyi aşan kısım" kayar. Dağıtım sözleşmesel varsayımdır; kimden kime yazıldığı gözlenen bir akış değildir.

## Doğrulanmadı, modele girdi değil

- 2010–2020 D uyumsuzluğu (D'nin %2–12'si) bütünüyle parasal altın ve SDR'de; 2021'den sonra 0, U haznesinde. Nedeni (karşılıksız parasal altın mı, sınıflama değişikliği mi) doğrulanmadı. Eski "%0,001" ifadesi yanlıştı.
- D'nin büyük kur dönemlerindeki değerleme kazancı sistematik az tahmin ediliyor (2025-Q4: gözlenen 1,92, tahmin 0,99–1,12 trilyon TL). Aday açıklama: hisse/FDI ve YP-TL bileşimi enstrüman içinde yok. Doğrulanmadı.
- Bireysel iflas borcu silmez deniyor; doğrulanmadı. Temerrüt bu yüzden sıfır toplamlı transfer sayılmıyor, sistem net kayıp yazılıyor. Hukuk kapanmadan bu satır sonuç değildir.
- Brüt dış borçta kur payı %75, D'nin net finansal pozisyonunda değerleme payı %28. Farklı nesneler: net pozisyon varlıkları da içerir. Yurt dışı varlıkların kurla değerlenmesi doğrulanmadı.
- Eylül "Bilanço Rotasyonu" raporu 2026-Q2'de EVDS ile birebir (221/318/539) ama önceki yıllarda Kamu+TCMB EVDS'den 46–53 milyar USD yüksek. Raporda kamu azalır, EVDS'te kamu ve özel birlikte artar. Kaynak dosyası doğrulanmalı; rotasyon cümlesi EVDS'te görünmüyor.
- TGA satış rakamları (2024: 40,7; 2026 Ocak–Mayıs 42,7; Nisan–Haziran 25,7 milyar TL) haber/FIR derlemesi. Resmi seriyle doğrulanmadı.

## Matris ne kanıtlamaz

Geriye dönük test (45 çeyrek, altın/SDR hariç): orantılı Lm R² = 0,868; basit varlık-payı kıyası 0,862. Matris, kuruluş varsayımının ötesinde bilgi eklemiyor. Döviz ağırlıklı dağıtım daha kötü (0,565). Bilateral D kısıtı iyileştirmedi (0,856). L ve Lm kapalı muhasebe; kimden kime aktığı ölçülmüş bir ağ değil.

Stok-akış kimliği ayrıdır ve 2021'den beri işlem akışlarında kapanır: NFP_t = NFP_{t−1} + NL_t + R_t. Kapanma, yukarıdaki payların doğru olduğu anlamına gelmez.
