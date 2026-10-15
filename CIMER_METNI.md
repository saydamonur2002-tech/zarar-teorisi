# CİMER başvuru metni: beş adımlı borç çözümü politika önerisi

**Konu:** Hane halkı, firma ve banka bilançolarındaki karşılıklı borç yükünün beş adımda ele alınmasına dair politika önerisi

**Muhatap:** Hazine ve Maliye Bakanlığı, Türkiye Cumhuriyet Merkez Bankası, Bankacılık Düzenleme ve Denetleme Kurumu (BDDK) ve ilgili diğer kurumlar

**Başvuran:** [Ad Soyad] · [İletişim]

---

## 1. Başvurunun amacı ve kısa özeti

Sayın yetkili,

Bu başvuruyla, Türkiye'deki hane halkı, firma ve banka bilançolarında biriken borç yükünü azaltmaya yönelik, sırayla uygulanabilecek beş adımlık bir politika önerisi sunuyorum. Öneri bir kanun taslağı ya da hukuki görüş değildir. Kamuya açık verilerle kurulmuş bir hesaplama modelinin sonuçlarına dayanan, kurumlarınızca incelenmesini istediğim bir fikirdir.

Öneri şu beş adımdan oluşuyor:

1. Sektörler arasında karşılıklı duran borç ve alacak stokunun kayıt düzeyinde mahsup edilmesi.
2. Firma ve hane düğümlerinden oluşan borç ağında çok taraflı mahsup yapılması.
3. Seçilen borç stokunda faiz işlemesinin durdurulması.
4. Vadeli ve yabancı para mevduat sahiplerine, adresi önceden belirlenmiş senet verilmesi.
5. Piyasa kirası ile havuz kirası arasındaki farkın ev sahibinden kiracıya aktarılması.

Bunlara ek olarak, 4. ile 5. adım arasına yerleştirilen, mevcut Türk lirasından yeni bir Türk lirasına geçişi öngören isteğe bağlı bir "4.5. adım" da inceledim. Modelim bu adımın borç yükünü azaltmadığını, yalnızca maliyet getirdiğini gösteriyor. Bunu aşağıda ayrıca açıklıyorum.

Başvurunun en önemli yanı şudur: sunduğum bütün tutarlar tahmin ya da resmî hesap değildir. Her biri, açıkça belirttiğim varsayımlara bağlı bir bant değeridir. Bazı girdiler ölçülmüş resmî verilerdir. Bazıları ise benim koyduğum varsayımlardır ve kurumlarınızın mikro verisiyle doğrulanması gerekir. Metin boyunca bu ayrımı yapmaya çalıştım.

## 2. Sorunun tanımı: karşılıklı borç zinciri

Bir ekonomide borç, tek yönlü bir ilişki değildir. Bir firmanın bankaya borcu vardır, aynı firmanın başka bir firmadan alacağı vardır. O firmanın alacaklısı da başka birine borçludur. Hane halkı hem borçlu hem de mevduat sahibidir. Banka hem alacaklı hem borçludur. Bu ağda herkes birinin alacaklısı, bir başkasının borçlusudur.

Bu yapının önemli bir sonucu var: borçların bir kısmı, kâğıt üzerinde bir karşılığı olan alacaklarla zaten dengelenir. Yani bazı borçlar aynı anda hem birinin yükü hem başkasının varlığıdır. Eğer bu karşılıklı kısım doğrudan mahsup edilebilirse, ekonomiye yeni para basmadan, yalnızca kayıtları sadeleştirerek bir miktar borç ortadan kalkar. Bunu mahsuplaşma (netleştirme) olarak biliyoruz. Mahsuplaşma bilinen bir yöntemdir. Ancak sistematik ve ülke ölçeğinde, sektörleri ve firmaları bir arada gören bir mahsup mekanizması hakkında kamuya açık bir çalışma bulmak zordur. Bu öneri, o boşluğu doldurmaya yönelik bir ilk denemedir.

Bu sorunun neden önemli olduğunu da söylemeliyim. Borç yükünün yüksek olduğu bir ortamda faiz ödemeleri gelirin büyük bir bölümünü alır. Hane halkı tüketimi kısar, firma yatırımı erteler, banka yeni kredi vermekte zorlanır. Borç çözümü yalnızca borçlunun değil, alacaklının ve bankanın da sorunudur. Çünkü ödenemeyen borç, alacaklı tarafta tahsil edilemeyen alacak demektir.

Güncel makro görünüm de bu çerçevenin önemini artırıyor. 12 aylık cari açık 2026 Ağustos itibarıyla yaklaşık 42,1 milyar dolar. Merkez Bankası rezervi 2 Ekim 2026'da 167,4 milyar dolar. Bu rezerv, 21 Ağustos'taki 188,4 milyar dolarlık zirvenin altındadır. Bu rakamlar tek başına kriz göstergesi değildir. Ama dış finansman ihtiyacı sürerken iç borç yükünün de ağır olduğu bir ortamda, yeni para ya da yeni borç yaratmayan çözümlerin değerlendirilmesinin faydalı olacağını düşünüyorum.

## 3. Çalışmanın dayanağı ve sınırları

Önerinin arkasındaki hesaplamalar, açık bir depoda (github.com/saydamonur2002-tech/zarar-teorisi) yayımlanmış kodla yapıldı. Kullanılan ana veri kaynakları şunlar:

- TCMB EVDS: finansal hesaplar, kredi faizleri, konut kira serileri, döviz kuru ve GSYH.
- Sektör Bilançoları: 2024 verisi; firma kısımlarının (17 NACE grubu) ve hane halkının bilançoları.

Modelin üç türlü girdisi var ve bunları birbirinden ayırmak önemli:

1. **Ölçüm:** Resmî bir kaynaktan doğrudan alınmış değer. Örneğin firmaların toplam kredi yükümlülüğü ve GSYH.
2. **Varsayım:** Verisi olmadığı için benim seçtiğim parametre. Örneğin hangi borçlunun hangi alacaklıya borçlu olduğunu gösteren kenar dağılımı, ya da kaç hanenin kira ödediğine dair oran.
3. **Karar:** Bir tasarım tercihi. Örneğin havuz kirası olarak 20.000 TL/ay seçilmesi.

Bu ayrımı yapmamın nedeni dürüstlüktür. Bir hesabın kesin göründüğünü, ama arkasında gevşek bir varsayım olduğunu saklamak, hem sizi yanıltır hem de önerinin güvenilirliğini zedeler. Bu yüzden aşağıda her adımın hangi kısmının ölçüm, hangisinin varsayım olduğunu belirttim.

Tüm tutarlar milyar Türk lirası cinsindendir ve cari fiyatlıdır. Bir de önemli bir sınırı baştan söylemeliyim: bu model, davranışsal tepkileri (insanların ve kurumların yeni kurallara nasıl uyum sağlayacağını) sınırlı biçimde içeriyor. Yani sonuçlar, "kurallar bugün aniden uygulansa ne olurdu" sorusuna bir yaklaşıklıktır, "kesin ne olacak" sorusuna bir cevap değildir.

## 4. Adım 1: Sektörler arası ortak stokun mahsubu

**Ne öneriyorum?** Sektör çiftleri arasında hem borç hem alacak olarak görünen tutarın, yani "ortak stokun", kayıt düzeyinde mahsup edilmesi. Örneğin A sektörünün B sektörüne olan borcu ile B sektörünün A sektörüne olan borcunun küçük olanı kadarı, iki taraftan da düşülür.

**Model ne buluyor?** Altı sektör çiftinin her birinde iki yönlü bacak ayrı ayrı alınır. Bir yön için veri yoksa, EVDS'teki konsolide olmayan aynı araç tutarı üst sınır olarak kullanılır. Çift düzeyinde ortak stok iki yönün küçüğüdür. Sonuç: ortak stok yaklaşık 20.363 milyar TL. Brüt toplam ise yaklaşık 78.870 milyar TL.

**Bu sayıyı nasıl okumalı?** Bu, silinebilecek en çok tutardır, gerçekte silinecek tutar değildir. Çünkü kimin kime borçlu olduğunu gösteren kimden-kime tablosu kamuya açık değildir. Bu yüzden 20.363 milyar TL bir tavan, bir üst sınırdır. Gerçek mahsup, kurumların elindeki mikro veriyle yapılırsa daha düşük çıkacaktır.

**Uygulama maliyeti.** Bu adımın yürütme maliyeti, yani tespit, tahsil ve idare giderleri, modelde en düşük oran (%0,4) kullanıldığında yaklaşık 81,5 milyar TL tek seferlik. Daha yüksek oranlar bu adım için gerçekçi olmayan tutarlar verdiği için kullanmadım. Bunun nedeni, stok mahsubunun yeni bir ödeme akışı yaratmaması, yalnızca mevcut kayıtların karşılıklı düşülmesidir.

**Talep.** Bu adımın tek başına bile en az riskli olduğunu düşünüyorum, çünkü yeni para ya da yeni borç yaratmıyor. Kurumlarınızın elindeki kimden-kime verisiyle gerçek mahsup edilebilir tutarın hesaplanmasını rica ediyorum.

## 5. Adım 2: Ağ üzerinden çok taraflı mahsup

**Ne öneriyorum?** Adım 1 yalnızca sektör çiftleri arasında mahsup yapar. Adım 2, firmaları ve haneleri tek bir ağda birleştirir. Böylece üç ya da daha fazla taraflı döngüler de mahsup edilir. Örneğin A, B'ye; B, C'ye; C de A'ya borçluysa, bu döngüdeki en küçük borç kadarı üç tarafta birden düşülür. İki taraflı mahsuplaşmanın göremediği bir sadeleşme budur.

**Model ne buluyor?** Ağ, Sektör Bilançoları 2024'ten gelen 17 NACE firma grubundan, 17 hane düğümünden ve bir dış düğümden oluşuyor. Toplam 322 kenarı var. Bu ağda mahsupla silinen borç yaklaşık 14.602 milyar TL. Bu, ağdaki borcun yaklaşık %88,5'ine karşılık geliyor.

**Bu sayıya dikkat.** Bu sonuç, öneri içindeki en az sağlam rakamdır ve bunu açıkça söylüyorum. Düğümler ölçüme dayanır, ama kenarların, yani kimin kime ne kadar borçlu olduğunun dağılımı bir çekim ve RAS (matris dengeleme) varsayımıdır. Gerçek ağ farklı olabilir. Bu yüzden %88,5'i bir tavan, bir "en çok bu kadar" değeri olarak okumak gerekir. Gerçek oran bundan düşük olabilir, hatta önemli ölçüde düşük olabilir. Bu rakamı kurumlarınızın mikro verisiyle sınamadan politika kararına temel yapmanın doğru olmayacağını düşünüyorum.

**Uygulama maliyeti.** Adım 1 ile aynı gerekçeyle yalnızca en düşük oran uygulandığında yaklaşık 58,4 milyar TL, tek seferlik.

**Talep.** Bu adımın pilot olarak, gönüllü ve küçük bir örneklemle denenmesini öneriyorum. Pilot sonucu, gerçek ağın model ağına ne kadar benzediğini gösterecektir.

## 6. Adım 3: Faizin durdurulması

**Ne öneriyorum?** Mahsuptan sonra kalan borç stokunun belirli bir payında, faiz işlemesinin belirli bir süre durdurulması. Faiz durduğunda borçlu, anapara dışında bir yük taşımaz. Alacaklı da faiz geliri kaybeder. Bu yüzden bu adımın bedelini kimin ödeyeceği önemli bir sorudur ve aşağıda ele alıyorum.

**Model ne buluyor?** Faiz durmasının büyüklüğü şu formülle hesaplanıyor: durdurulan stok, firmaların kredi yükümlülüğü (2026 ilk çeyrek itibarıyla yaklaşık 25.340 milyar TL, ölçüm) ile bir kapsam payının çarpımıdır. Faiz oranı, ticari kredi faizinin son gözlemidir (2026 Eylül'de yaklaşık %53,2, sonrası sabit tutuldu, bu bir varsayımdır). Sektör Bilançoları ile EVDS arasındaki kapsam farkını yakalayan bir düzeltme katsayısı da var (yaklaşık 0,358).

Kapsam payı için üç değer denendi: %25, %50 ve %100. Bunlar varsayımdır, ölçüm değildir. 2029 yılı için durmuş yıllık faiz tutarı sırasıyla yaklaşık 1.208, 2.416 ve 4.831 milyar TL'dir.

**Kim öder?** Faizin durması bir kayıp yaratır. Bu kayıp ya borç verenin (banka, firma) ya da kamunun üzerine düşer. Modelde kaybı tek bir taraf öder (bankalar ya da firmalar kesimi), iki taraf birden değil. Yani bu adım zararı yok etmez, yalnızca başka bir tarafa kaydırır. Bu nedenle adımın tasarımında, kaybın kime yükleneceğinin açıkça belirlenmesi şarttır. Bu kararı vermek benim işim değil, kurumlarınızındır.

**Uygulama maliyeti.** Faiz durması yıllık bir akıştır, dolayısıyla yürütme maliyeti de yıllıktır. Yürütme oranı %0,4 olduğunda 2029'da yıllık 4,8 ile 19,3 milyar TL arasındadır. Oran %9'a çıkarsa 108,7 ile 434,8 milyar TL. Oran %29'a çıkarsa 350,2 ile 1.400,9 milyar TL. Bu, beş adım içinde yürütme maliyeti en yüksek olabilecek kalemdir.

**Talep.** Faiz durmasının hangi borçlara, hangi süreyle ve kimin hesabına uygulanacağının net kurallara bağlanmasını rica ediyorum. Bu adım ancak kaybın kime düşeceği belli olduğunda anlamlıdır.

## 7. Adım 4: Adres yönlendirmeli senet

**Ne öneriyorum?** Mevduat sahiplerine, vadeli mevduat ve yabancı para mevduatı karşılığında, devletçe belirlenmiş bir adrese yönlendirilen bir senet verilmesi. Buradaki fikir, mevduatın bir kısmının bankadan çekilip bu senede dönüştürülmesidir. Böylece hem mevduat sahibinin alacağı korunur hem de banka sisteminin üzerindeki baskı yönetilir.

**Model ne buluyor?** Senede dönüştürülebilecek üç ölçülmüş stok var:

- Hane vadeli mevduatı: yaklaşık 8.322 milyar TL
- Firma vadeli mevduatı: yaklaşık 4.400 milyar TL
- Gerçek kişi yabancı para mevduatı: yaklaşık 6.639 milyar TL

Toplam yaklaşık 19.362 milyar TL (2026 ilk çeyrek, ölçüm). Bunun ne kadarının senede dönüşeceği ise üç varsayıma bağlı: dönüşüm payı (%10, %25 ya da %50), yenileme oranı (sıfır ya da %50) ve prim (%2 ya da %5). Bu 12 senaryoda 2029-2031 dönemindeki toplam prim maliyeti yaklaşık 77,5 ile 1.058,9 milyar TL arasındadır. Orta senaryoda bu 529,4 milyar TL.

**Bankalar için sonuç.** Bankalar mevduat kaybedeceği için kredi vermeleri de daralır. Modelde bu daralma yılda yaklaşık 155 ile 775 milyar TL arasında. Orta senaryoda 387 milyar TL. Bu, krediye bağımlı hane ve firmalar için bir bedeldir ve karar verilirken mutlaka tartılmalıdır.

**Bilinen eksik.** Senedin endekse bağlı bir bacağı olabilir (enflasyona ya da dövize bağlı getiri). Bunu hesaplamadım. Bu yüzden prim maliyeti gerçekte yukarıdaki tutarlardan yüksek olabilir. Yani sayılar bir alt sınır olabilir.

**Uygulama maliyeti.** Prim toplamının bir oranı olarak hesaplandığında yürütme maliyeti 2029-2031 toplamında %0,4 oranıyla 0,3 ile 4,2 milyar TL, %9 oranıyla 7 ile 95 milyar TL, %29 oranıyla 22,5 ile 307 milyar TL arasındadır. Bu adımda kullandığım yürütme oranının dayanağı özellikle zayıftır. Çünkü hedefli transfer programlarının idare giderleri hakkında bildirilen aralığı, bir mevduat senedi ihracına taşıdım. Bu eşleştirme tartışmalıdır.

**Talep.** Bu adım, beş adım içinde en çok bankacılık sistemine dokunan adımdır. Uygulanmadan önce BDDK ve Merkez Bankası tarafından, kredi daralmasının etkisi dahil, ayrı bir etki analizinden geçirilmesini rica ediyorum.

## 8. Adım 4.5: Yeni Türk lirasına geçiş (isteğe bağlı)

**Ne inceledim?** Mevcut Türk lirasının, 1'e 1 pariteyle yeni bir Türk lirasına çevrilmesi. Çalışmama göre geçiş 2030 yılı içinde, dört çeyrekte kademeli olarak yapılabilir (yüzde 25, 50, 75 ve 100 oranında). Yeni lira, altın ya da dövize bağlı bir alacak değildir, yani bir dolar ya da altın hakkı vermez. Kur olarak sabit bir çapa kullanılıyor (bir dolar karşılığı yaklaşık 49,13 TL).

**Sonuç: fayda yok.** Bu adımın modeldeki adı "plasebo". Çünkü parite 1 olduğunda ya da başka bir oran seçildiğinde bile, hanelerin, firmaların ve bankaların net pozisyonu değişmez. Mevcut TL para stoku yaklaşık 16.473 milyar TL ve yeni birime geçtiğinde de aynı gerçek değeri taşır. Kimse daha zengin ya da daha fakir olmaz, borçlar da hafiflemez. Sıfır atmak ya da birimi küçültmek, borç yükünü azaltmaz.

**Maliyeti var.** Sade bir geçiş (banknot basımı ve kurumların yazılım uyumu) yaklaşık 0,6 ile 5,4 milyar TL tek seferlik. Tam yeni bir birim kurulursa, GSYH'nin %0,3 ile %1'i kadar, yani yaklaşık 190 ile 632 milyar TL. Bu ikinci tutar, ikincil kaynaklara dayanan bir üst referanstır.

**Benim değerlendirmem.** Bu adımı öneriye dahil etmemin nedeni, bu konunun kamuoyunda sıkça gündeme gelmesi ve sonucunun açıkça gösterilmesi gerektiğini düşünmemdir. Modelime göre bu adım borç sorununu çözmez. Kendi kanaatim, bu adımın öncelikli olmaması gerektiğidir. Beş adımın geri kalanı bu adım olmadan da çalışır. Kurumlarınız bu adımı başka gerekçelerle (örneğin ödeme sistemi yenileme) değerlendirmek isterse, bunu borç çözümünden ayrı bir proje olarak ele almalıdır.

## 9. Adım 5: Kira farkının havuzlanması

**Ne öneriyorum?** Piyasa kirası ile belirlenmiş bir havuz kirası arasındaki farkın, ev sahibinden kiracıya aktarılması. Böylece kira yükü ağır olan hanelerin yükü hafifler.

**Model ne buluyor?** Girdilerin bir kısmı ölçüm, bir kısmı varsayım:

- Birim kira: metrekare başına ayda yaklaşık 258,45 TL (EVDS konut birim kira serisi, 2026 ikinci çeyrek, ölçüm).
- Konut büyüklüğü 90 ile 110 metrekare, kiracı hane oranı %25 ile %30, toplam hane sayısı yaklaşık 26,4 milyon (varsayım ya da dış kaynak).
- Piyasa kirası aylık yaklaşık 23.260 ile 28.430 TL.
- Havuz kirası aylık 20.000 TL (modelin kararı, bir tasarım tercihi).
- Aradaki fark aylık 3.260 ile 8.430 TL.

Kapsama payına göre yıllık transfer şu aralıklardadır: %20 kapsamda 51,6 ile 160,2 milyar TL, %50 kapsamda 129,1 ile 400,6 milyar TL, %100 kapsamda 258,2 ile 801,1 milyar TL.

**Önemli ayrım.** Bu transfer bir hane içi aktarımdır. Ev sahibi de bir hanedir, kiracı da. Yani toplam hane halkı düzeyinde net etki sıfırdır, para bir haneden diğerine geçer. Bu adımın faydası kaynak yaratması değil, dağılımı değiştirmesidir. Bu nedenle adımı savunurken "kamuya maliyeti yok" demek doğru olmaz. Doğrusu, "kamuya net maliyeti yok, ama bir hane grubundan diğerine kaynak aktarır" demektir. Bunun hakkaniyet açısından tartışılması gerekir.

**Uygulama maliyeti.** %50 kapsamda ve orta yürütme oranında (%9) yıllık yaklaşık 23,8 milyar TL. Oran %29 ise yaklaşık 116 milyar TL.

**Talep.** Bu adım için ev sahiplerinin ve kiracıların davranışının (örneğin ev sahiplerinin evi satması ya da kiraya vermekten çekilmesi) ayrıca incelenmesini rica ediyorum. Modelim bu tepkileri içermiyor ve bu önemli bir eksiktir.

## 10. Beş adımın toplam yürütme maliyeti

Her adımın tek tek yürütme maliyetini yukarıda verdim. Toplamları yıl bazında, ilgili yılın GSYH'sine bölerek de hesapladım. Bunun için 2026 sonrasına ait bir GSYH yolu kurmam gerekti. Bu yol bir varsayımdır: önceki yıl GSYH'si çarpı enflasyon çarpı yüzde 3 reel büyüme. Resmî bir tahmin değildir.

Sonuçlar üç senaryoda şöyledir (adım 5 hariç):

- **Düşük senaryo** (en düşük yürütme oranı): yıllık GSYH'nin binde 1'inin altı. 2029'da, adım 1 ve 2'nin tek seferlik maliyeti bu yıla konduğu için, yaklaşık %0,10.
- **Orta senaryo:** yıllık GSYH'nin yaklaşık %0,11 ile %0,26'sı, yani binde 1 ile binde 3 arası.
- **Yüksek senaryo** (en yüksek yürütme oranı, en büyük faiz durması, tam yeni birim): yıllık %0,72 ile %1,35. Zirve 2030'da, yaklaşık %1,35. Bunun büyük kısmı adım 3'ün faiz kalemi ve adım 4.5'in tam yeni birim seçeneğinden gelir.

Bu rakamları okurken üç şeye dikkat edilmesini rica ediyorum. Birincisi, yürütme oranlarının (yüzde 0,4, 9 ve 29) dayanağı zayıf. Üst ve alt uçlar ikincil bir kaynakta bildirilen hedefleme idaresi aralığından geliyor, ben bunu doğrulayamadım. Bir de %25'lik bir değer var ki o benim kendi pilot çalışmamdan gelen bir karardır. İkincisi, üç senaryo birbirinden bağımsız tahminler değil, bandın uçlarıdır. Gerçekte bütün parametrelerin aynı anda en kötü değerde olması beklenmez. Üçüncüsü, GSYH yolu varsayımdır, 2029 ve 2030 için enflasyon senaryosu da yoktur. Bu yüzden bu oranlar kesin değil, büyüklük mertebesi verir.

Bunlardan çıkardığım ana sonuç şu: orta senaryoda uygulamanın idare yükü, GSYH'nin binde birkaçı mertebesindedir. Bu yönetilebilir görünüyor. Ama yüksek senaryoda yüzde bir civarına çıkabiliyor ve bu ciddi bir yük olurdu. Aradaki farkı belirleyen ana etken adım 3'ün kapsamı ve idare giderlerinin oranıdır. Bu ikisini kurumlarınızın gerçek verisi daha iyi belirleyebilir.

## 11. Riskler ve olası itirazlar

Bu öneriye yöneltilebilecek itirazları önceden düşündüm ve bazılarını açıkça kabul ediyorum.

**"Bu, borçların silinmesi demek, ahlaki risk yaratır."** Haklı bir itiraz. Borç silineceği beklentisi, gelecekte insanların daha rahat borçlanmasına yol açabilir. Bu yüzden öneriyi tek seferlik, açık kurallara bağlı ve yeni borçlanmayı sınırlayan düzenlemelerle birlikte düşünmek gerekir. Benim modelim bu davranışsal etkiyi içermiyor.

**"Alacaklıların kaybı ne olacak?"** Adım 3 ve adım 4'te bir kayıp var ve bu kaybı birinin üstlenmesi gerekiyor. Bunu yok saymıyorum. Önerinin en zor yanı budur ve bu kararı vermek benim yetkimde değil.

**"Hukuki dayanağı var mı?"** Bu başvuru, adımların hangi kanuna ya da düzenlemeye dayanacağını söylemiyor ve söyleyemez. Mahsup, borç silme, faiz durdurma ve senet ihracının hukuki çerçevesinin kurumlarınızca ayrıca değerlendirilmesi gerekir. Bu metin yalnızca iktisadi büyüklükleri ortaya koyuyor.

**"Modelin varsayımları gerçeği yansıtıyor mu?"** Tam olarak değil. Özellikle adım 2'deki ağ yapısı, adım 5'teki kiracı oranları ve yürütme maliyeti oranları varsayıma dayalı. Bu varsayımların mikro veriyle doğrulanması, önerinin ciddiye alınabilmesi için gereklidir.

**"Neden bu adımların sırası böyle?"** Sıra, riskin ve geri döndürülebilirliğin artışına göre seçildi. Adım 1 ve 2 yeni para ya da borç yaratmayan, kayıt düzeyinde işlemlerdir ve en az riskli olanlardır. Adım 3 ve 4 gerçek kayıpları dağıtır. Adım 5 hanelerin kendi arasında bir dağılım değişikliğidir. İstenirse adımlar birbirinden bağımsız olarak da uygulanabilir.

## 12. Taleplerim

Bu başvuruyla kurumlarınızdan şunları rica ediyorum:

1. Önerinin Hazine ve Maliye Bakanlığı, Merkez Bankası ve BDDK tarafından birlikte değerlendirilmesi.
2. Adım 1'in, yani sektörler arası ortak stok mahsubunun, kurumların elindeki kimden-kime verisiyle gerçek tutarının hesaplanması. Bu, benim 20.363 milyar TL'lik üst sınırımın gerçekte ne kadar olduğunu gösterecektir.
3. Adım 1 ve 2'nin, yalnızca kayıt düzeyinde ve gönüllülük esasıyla, küçük bir örneklemde pilot olarak denenmesi.
4. Modelde "varsayım" olarak etiketlenmiş girdilerin (borç ağındaki kenar dağılımı, kapsama payları, kiracı oranları, yürütme oranları) kurumların mikro verisiyle doğrulanması ya da düzeltilmesi.
5. Adım 3 ve adım 4 için, kaybın kime yükleneceğine dair ayrı bir etki analizi yapılması.
6. Önerinin hukuki uygulanabilirliği hakkında kurumsal bir görüş bildirilmesi.

Çalışmanın bütün kodu, girdileri ve tabloları açık depoda yer alıyor (github.com/saydamonur2002-tech/zarar-teorisi). İsteyen herkes rakamları yeniden üretebilir, varsayımları değiştirip sonucu kendisi görebilir. Eleştiriye açığım. Bir varsayımın yanlış olduğunu gösteren olursa, modeli buna göre güncellerim.

Konuyu değerlendirdiğiniz için teşekkür ederim.

Saygılarımla,

[Ad Soyad]
[Tarih]
