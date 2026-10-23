# ON_KAYIT_zayif — hesaptan ÖNCE (2026-10-23)

Amaç: paylas2 ve önceki RAPOR dosyalarında açık kalan yedi zayıf noktayı kapatmak. Birim, aksi yazılmadıkça 2014–2025 kümülatif reel %GSYH, artı kazanç. Sıfır toplam korunur. Nedensel cümle yalnız bu dosyada tanımlı karşı-olguda kurulur. "Rant" bulgu sözcüğü değildir. Haber rakamı hükme girmez. EVDS3 iç ucu ve EVDS API bu turda kullanılmayacak; eski dosyalardaki EVDS3 kökeni önceki beyan olarak durur, yeni sayı oradan üretilmez.

Kaynak sırası: kurumun kendi tablosu (TCMB, BDDK, TBB, TÜİK, SGK, HMB, ILO, OECD, WB, WGC, BIS). İndirme başarısız veya sayfa engelli ise o kalem [DOĞRULANMADI] yazılır; engel aşılmaz, sayı uydurulmaz.

## Z1 — Banka net kârı, net faiz marjı, KKM komisyonu

Kaynak denemesi: BDDK aylık bülten ve TBB istatistikî rapor (seçilmiş rasyolar / gelir-gider). KKM komisyonu yalnız TCMB dipnotu veya BDDK/TBB tablosunda kur farkı giderinden ayrı bir satır varsa alınır.

- Net kâr ve NIM bulunursa yan tabloya yazılır [VERİ]. Karşı taraf (mevduat sahibi, kredi borçlusu, Hazine) ayrılmadan sıfır toplamlı aktör satırına eklenmez.
- KKM komisyonu ayrılamazsa [DOĞRULANMADI]; TCMB'nin yayımladığı KKM gideri kur farkını da içerdiği için komisyon diye bölünmez.
- Ölçüt C_Z1: S1 banka satırı yalnız karşı tarafı yazılı bir kimlikle değişir. Aksi halde S1 banka önceki değerde kalır; yeni seri bağlamdır. "Kapandı" = 2014–2025 için en az 8 yıl net kâr/GSYH ve NIM birincil tablodan okunmuş, komisyon ise ya ayrılmış ya da ayrılamadığı açıkça yazılmış.

## Z2 — TCMB kâr aktarımı, 2014–2018 ve 2022–2025

Kavram, paylas2 ile aynı: TCMB yasal/IFRS finansal tablo, özkaynak değişim tablosundaki Hazine'ye aktarılan kâr (2019–21'de toplanan iki satırın karşılığı). GSYH: World Bank WDI NY.GDP.MKTP.CN (pasta/gdpcn.json ile aynı gösterge; bu turda API yeniden okunacak). Yüzde = tutar_milyar_TL × 1000 / (GSYH_TL / 1e6) × 100. 2019–21 bu formülle 1,78+0,86+0,48 vermişti; sapma olursa SAPMA'ya yazılır.

- Zarar ve "dağıtılmadı" tabloda yazılıysa tutar 0 [VERİ].
- Tablo inmezse o yıl boş kalır. Sıfırla doldurulmaz. HMB nakit "MB kâr payı" bulunursa yalnız çapraz kontrol [VERİ] ve ayrı duyarlılık sütunudur; tahakkuk kavramının yerine geçmez.
- Aktör kuralı (paylas2 D2 ile aynı): doğrulanan her yıl, her iki senaryoda TCMB'den düşülür, Hazine'ye eklenir.
- Ölçüt C_Z2: 2014–18'in tamamı ve 2022–25'in yayımlanmış yılları tahakkuk kavramıyla okunursa Z2 kapandı. Eksik yıl varsa kısmi. S1 Hazine ve TCMB bu toplam kadar kayar; diğer aktörler bu kalemden kaymaz.

## Z3 — Firma döviz pozisyonu ölçeğe göre; 2024–25 ölçek verisi

Kaynak: TCMB sektör bilançoları, paylas/p.py ile aynı kavram (net kambiyo kârı/zararı; inşaat 41–43 ve 68 hariç; GENEL hariç). BDDK KOBİ kredisinin para birimi ayrımı ayrı satırdır: kredi stoku net döviz pozisyonu değildir, k2 anahtarının yerine konmaz. Ancak [VEKİL] duyarlılık olarak, kavram farkı yazılarak gösterilebilir.

- 2024 veya 2025 sektör bilançosu yoksa son yıl yazılır, eksik yıllar [DOĞRULANMADI], pay uzatılmaz.
- Ölçüt C_Z3: büyük firma net kambiyo zararı payı, mevcut 0,690'dan 5 puandan az saparsa S1 firma bölüşümü "eşik altı, değişmedi". 5 puan ve üzeri saparsa KOBİ/büyük k2 yeniden bölünür ve S1 farkı raporlanır. Ölçek verisi 2024–25 için yoksa Z3 kısmi kalır.

## Z4 — Servet tabanlı hane anahtarı

Kabul: kurum tablosunda mevduat, altın, konut veya net servetin gelir beşlisine dağılımı. Gelir payı, tüketim payı ve konut sahipliği oranı servet anahtarı sayılmaz. Konut sahipliği bulunursa yalnız gerçekleşmemiş konut notunun bölüşümünde kullanılabilir; finansal NET anahtarı değişmez.

BDDK tutar dilimi bu turda EVDS3'ten çekilmeyecek. Bültende aynı tablo kamuya açık dosya olarak varsa kullanılabilir [VERİ]. Haber, TBMM aktarımı ve servet raporu özeti hükme girmez.

- Ölçüt C_Z4: birincil servet anahtarı yoksa Z4 açık kalır; "bulunamadı" yazılır, anahtar uydurulmaz. Varsa e_servet duyarlılığı hesaplanır. Ö1 (üst payı > %47,6) ve Ö2 (alt net < 0) bu anahtarda yeniden okunur. Ana ANA anahtar ancak kaynak finansal stoku kapsıyorsa değişir.

## Z5 — Yurt dışı artığı 3,75 puan

Başlangıç (paylas2): S1 yurt dışı+artık − UYP doğrudan = artık. UYP doğrudan tanımı eksik/e.py K9 ile aynı, mevcut yeni_kanallar_yil.csv yeniden toplanacak [HESAP].

Köprü, muhasebe, nedensel değil. İşaret: artı = yurt dışı kazancı.

1. Model D satırının kanal dökümü (k1, k2, k5, k7, k8, paylas2 banka YP düzeltmesi).
2. Doğrudan UYP reel değerleme.
3. Fark = (1) − (2).
4. Farkın içinde, D'ye yazılmış ama UYP'de olmayan kalemler ayrı satır: banka altını karşı tarafı, swap karşı tarafı, senyorajın D parçası, TL artığı. Ana tabloda B=0 varsayımı korunur. "Karşı taraf yurt içi banka olsaydı" yalnız [VARSAYIM] köprü satırıdır, S1'in yerine geçmez.
5. UYP'nin kendi içinde, USD: değerleme+diğer = ΔNIIP − finans hesabı (BPM6, bop.txt Tablo 4 ve uyp.txt Tablo 3) [HESAP]. Bu USD artığı ayrıca: (i) portföy hisse yükümlülüğü stok farkı − hisse yükümlülük akımı, (ii) doğrudan yatırım yükümlülüğü stok farkı − DY yükümlülük akımı. İkisi de "fiyat" diye adlandırılmaz; "stok−akım farkı (fiyat+diğer+yöntem)" [HESAP]. Parasal altın işlem akımı bültende ayrı değilse altın fiyatı ayrılmaz.
6. Reel TL UYP ile USD stok-akım farkının GSYH payı aynı kavram değildir; ikisi yan yana durur, biri diğerine eklenmez.

- Ölçüt C_Z5: açıklanamayan kalan ≤ 1,0 GSYH puanı ise Z5 kapandı. Üstünde ise köprü yazılır, Z5 açık kalır. Kalan, köprü satırlarının aritmetik farkıdır; yeni bir artık uydurulmaz.

## Z6 — S2 faiz ve büyüme tepkisi (duyarlılık)

Mevcut üç κ düzeyi durur (kur kuralı ψ=3,4, β ∈ {0,2; 0,3; 0,45}, kalibre_faiz/ceyrek_veri.csv). Bu tur ekler, onların yerine geçmez.

Model dosyası sfc_model.py içindeki katsayılar bu projede tahmin değildir [VARSAYIM]: φ_π=0,3, gam_r=0,45. g_r modelde 0 olduğu için ek kur, faizle geri beslenerek küçültülmez.

- Ek enflasyon π_ex,t = β · ek_kur_t (paylas2 ile aynı β).
- Ek nominal faiz Δi_t = φ · π_ex,t, φ ∈ {0,3; 1,0; 1,5}. Reel faiz farkı Δr_t = (φ−1)·π_ex,t.
- Aktör aktarımı yalnız şu stoklar kamuya açık tablodan gelirse yazılır: hane TL mevduat, firma TL kredi, Hazine TL iç borç, hepsi /GSYH. Aktarım_t = (stok_{t−1}/GSYH_t)·Δr_t. Mevduat sahibi kazanır, TL borçlu kaybeder, toplam sıfır. Banka payı 0 [VARSAYIM: mevduat ve kredi faizi aynı puan kayar]. Stok yoksa aktör satırı bu kanaldan değişmez; Δi ve Δr makro satır olarak kalır.
- k1'den geriye stok çıkarılmaz (orijinal faiz tanımı repoda yok).
- Büyüme: iki ayrı makro satır, aktöre yazılmaz. (i) Δg_t = −γ·ek_kur_t, γ ∈ {0,1; 0,3} [VARSAYIM]. (ii) yatırım tepkisi Δgk_t = −0,45·Δr_t [VARSAYIM, model gam_r]. İkisi toplanmaz.
- Ölçüt C_Z6: üç φ ve iki γ için tablo üretilmişse duyarlılık kapandı. Aktör S1−S2'si ancak stok bulunduysa faiz aktarımı kadar değişir. Büyüme satırı aktör sıralamasını değiştirmez. Bu bir genel denge değildir.

## Z7 — önceki açıklar

- Z7a Hane altını. Akım (WGC mücevher+külçe+sikke talebi) bulunursa 2014–25 toplamı [VERİ] yazılır. Açılış stoku yoksa stok kazancına çevrilmez. Mevcut 2.200–3.739 ton aralığı ve 311 mlr $ (2024Ç3, TCMB kutusu) durur. Yeni stok ancak kurum stok tahmini ise eklenir.
- Z7b Sahibinin oturduğu konut. TÜİK imputasyon kirası veya konut stoku bulunursa gerçekleşmemiş not olarak yazılır, NET'e girmez. Konut sahipliği oranı s ile kira stoku × s/(1−s) yalnız [VARSAYIM] duyarlılıktır ve ancak s birincil tablodansa. Beşli dağılım yoksa bölüştürülmez.
- Z7c KKM gelir grubu. BDDK/TCMB tablosu yoksa açık kalır. Mevduat diliminden KKM payı türetilmez. Mevcut %90 yüksek tutarlı anahtar [İKİNCİL] olarak durur, yükseltilmez.
- Z7d Göç, eğitime göre. TÜİK uluslararası göç bülteni, vatandaş göçü × eğitim. En az 3 yıl okunursa kapandı: kişi sayısı ve yükseköğretim payı [VERİ]. Parasal beşeri sermaye hesabı yok. Portal dinamik/engelli ise ILO denenecek; o da yoksa [DOĞRULANMADI].
- Z7e Ortalama reel emekli aylığı. SGK yaşlılık aylığı ortalaması, TÜİK veya WB TÜFE ile reel, 2014=100. En az 8 yıl birincil ise kapandı. OECD SOCX %GSYH bunun yerine geçmez (o harcama payıdır, aylık değildir).
- Z7f Asgari ücret civarı pay. Ön tanım: ücretliler içinde kazancı asgari ücretin 1,2 katının altında olanların payı. Bu dağılım kurum tablosunda yoksa ölçülmez. OECD asgari/ortalama oranından pay türetilmez. Oran zaten iz/'de var; tekrar hüküm yapılmaz.
- Z7g Firmaların +10,03 ücret kazancının yurt içi banka faizi. iz/ ile aynı yöntem: 2015–25, %GSYH, 2014 düzeyine göre farkların toplamı. Firmaların yurt içi bankalara faiz ödemesi birincil ise 1,24 kalanından düşülür [VERİ/HESAP]. Yalnız banka net faiz geliri (tüm sektör) bulunursa [VEKİL] bağlamdır, 1,24'ten düşülmez (hane ve kamu faizini de içerir).

## S1/S2 güncelleme kuralı

Aktör tablosunu değiştirenler: Z2 (doğrulanan aktarım), Z3 (C_Z3 eşiği aşılırsa k2 bölüşümü), Z1 (yalnız karşı taraf belli ise), Z6 (yalnız TL stok varsa faiz aktarımı). Z4, Z5, Z7 ana NET'i değiştirmez; yan tablo ve köprüdür. Her değişen sayıda etiket durur. Σ aktör = 0 kontrolü bozulursa sonuç yazılmaz, SAPMA'ya işlenir.

## Ölçüt özeti (sonuçtan önce kilitli)

| Kod | Kapandı sayılması |
|---|---|
| C_Z1 | Net kâr ve NIM ≥8 yıl birincil; komisyon ayrıldı veya ayrılamadı denildi; S1 banka ancak karşı taraf varsa kayar |
| C_Z2 | 2014–18 ve yayımlanmış 2022–25 tahakkukla okundu; S1 Hazine/TCMB kaydı |
| C_Z3 | Ölçek k2 ya eşik altı ya da yeniden bölündü; 2024–25 yoksa kısmi |
| C_Z4 | Birincil servet anahtarı yoksa açık ve uydurma yok |
| C_Z5 | Köprü sonrası açıklanamayan ≤1,0 puan |
| C_Z6 | φ ve γ tabloları var; büyüme aktöre yazılmadı |
| C_Z7 | Her alt kalem kendi cümlesine göre ayrı ayrı |
