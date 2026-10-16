# Ön kayıt — net dış varlık, net altın ve TL–DTH artığı

Yazıldı: 2026-10-16, katsayıdan önce. Eşik ve ikame yasağı sonra değiştirilmez.

Bu adım bitmeden katsayı yazılmaz. Kodu doğrulanmayan seri kullanılmaz. Yerine vekil konmaz.

## Tanımlar

Prim değil, artık. TL–DTH artığı: aynı vadede TL mevduat faizi eksi DTH faizi, eksi beklenen kur değişimi. Beklenen kur değişimi, PKA 12 ay sonrası dolar kurunun spot kura göre farkıdır. Vade, iki faiz de “3 aya kadar” ise 3 aydır. DTH faizi, döviz tevdiatın tamamını anlatan tek resmi seri yoksa kurulmaz. ABD doları mevduat faizi onun yerine yazılmaz.

Dolarizasyon payı: altın dahil DTH bölü toplam mevduat. Altın mevduatı gram ise miktar, TL karşılığı ise değer. Gram serisi yoksa gram yazılmaz. TL değeri ons fiyatına bölünerek grama çevrilmez.

Net dış varlık: swap düzeltmeli net döviz rezervi. Brüt rezerv kullanılmaz. Swap yükümlülüğü ve zorunlu karşılık, yayımlanmış ayrı kalem olarak yoksa NDV kurulmaz. Analitik bilançodaki yabancı aktif eksi yabancı pasif bu tanım değildir ve yerine konmaz.

Net altın miktarı: brüt TCMB altın stoku eksi altın swap yükümlülüğü, ton. Milyon dolar cinsinden altın, miktar değildir.

Altın fiyat etkisi, miktardan ayrı bir kontroldür. Ons fiyatı serisi yoksa bu kontrol kurulmaz ve fiyat ile miktar tek değişkende toplanmaz.

Net iç varlık: repo, tahvil stoku ve KKM yükümlülüğünün birlikte sterilizasyon ölçüsüdür. Yalnız açık piyasa işlemi ya da yalnız KKM stoku bu ölçü değildir.

## Yöntem

Aylık yerel projeksiyon. Her ufuk ayrı denklem. Karar ufku h = 1 aydır. Gecikme 1’dir, bilgi kriteriyle seçilmez. Newey–West, Bartlett, bant floor(4·(n/100)^(2/9)), en az 1. Karar bandı %95. n < 36 ise tahmin yok, katsayı yok.

H1. NDV değişiminin katsayısı negatif ve bant sıfırın altındaysa destek. Sterilizasyon kontrolü durur.

H2. Net altın miktarı değişimi, fiyat etkisi dururken negatif ve bant sıfırın altındaysa destek.

H3. NİV katsayısı pozitif ve H1 ile H2’nin mutlak değerleri NİV’siz tahmine göre küçülürse sterilizasyon vardır. Küçülmezse sterilizasyon etkisi yoktur diye yazılır. NİV yoksa H3 belirlenemiyor.

H4. Fiyat etkisi artığı açıklıyor ve miktar katsayıları anlamsızsa kanal kur beklentisidir. O zaman H1 ve H2 çürüdü yazılır. Bu sınama yapılamazsa H1 ve H2 çürüdü diye işaretlenmez.

H5. Artık yükselince altın dahil dolarizasyon payı azalır. Katsayı negatif ve bant sıfırın altındaysa destek.

H6. NDV ve net altın azalışı ile artışı ayrı katsayıdır. Tek doğrusal katsayı H6’nın yerine yazılmaz.

Kontroller her tahminde: PKA 12 ay dolar beklentisi, 24 ay enflasyon beklentisi, KKM kuklası, dört kırılma kuklası, altın fiyat etkisi.

KKM kuklasının başlangıç ve bitiş ayı, ancak bu turda indirilen tebliğ metninden yazılır. İlan haberinden ve bellekten tarih konmaz. Tebliğ inmezse kukla kurulmaz.

Kırılma pencereleri: 2018-08…2018-12, 2020-03…2020-06, 2021-09…2022-12, 2023-06…örnek sonu.

VIF 5’in üstündeyse ortak tahmin belirlenemiyor olur ve katsayılar ayrı ayrı verilir. Seriler regresyona giremiyorsa VIF hesaplanmaz.

Granger yalnız yön içindir ve bu turda, artık kurulamazsa çalıştırılmaz. Nedensellik diye yazılmaz.

Kontrolsüz ve kontrollü sütun, ancak ikisi de n ≥ 36 ise yan yana durur. İşaret değişirse başlıkta yazılır.
