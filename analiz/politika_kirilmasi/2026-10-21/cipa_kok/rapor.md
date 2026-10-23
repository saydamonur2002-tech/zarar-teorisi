# Çıpa neden göçtü? — kök testi (cipa_kok, 2026-10-21 TSİ)
Veri: TCMB "Enflasyon Hedefleri" tablosu (birincil), EVDS3 anahtarsız web (BEYAN: TP.FG.J0, TP.PKAUO.S01.E/F.U, TP.PY.P02.ON, TP.APIFON4, TP.SANAYREV4.Y1, TP.DK.USD.A.YTL), cipa_sebep/aylik.csv (X4), BCB Focus ve SGS 13522 (API), TCMB Başkan konuşması 27.10.2016 ve ER 2018-I. Kod: hesap.py → cikti.txt, k1.csv, k2_phi.csv. EVDS_API_KEY okunmadı.

**Tek cümle:** Kasım 2016'dan önce eşiği geçen ve emsal karşı olgusuyla uyumlu tek kök K2: TCMB'nin enflasyona tepkisi 2012 ortasından itibaren Taylor ilkesinin altında (2013-01–2016-10 pencerelerinin %100'ünde φπ<1). Hedefi kaçırma (K1) tek başına yetmiyor: Brezilya hedefi 7 yıl üst üste aştı (2010–16) ama sert sıkılaştırmadan sonra beklenti 2017'de hedefe döndü. Türkiye'de kaçırmalara tepki zayıf kaldı; TCMB kendi tahmininde %5'i ileri itti (K4), piyasa da %5'i değil TCMB tahminini izledi. İstatistiksel sıralama; nedensel değil.

## K1 Sicil (birincil hedef tablosu)
| Yıl | Hedef | Gerç. | Sapma | Ardışık aşım | Kümülatif | g (b24−5) |
|---|---|---|---|---|---|---|
| 2006–08 | 5/4/4 | 9,7/8,4/10,1 | +4,7/+4,4/+6,1 | 1→3 | 15,2 | – |
| 2009–10 | 7,5/6,5 | 6,5/6,4 | −1,0/−0,1 | 0 | 14,1 | – |
| 2011–12 | 5,5/5 | 10,4/6,2 | +4,9/+1,2 | 1→2 | 20,2 | – |
| 2013 | 5 | 7,4 | +2,4 | 3 | 22,6 | 1,03 |
| 2014 | 5 | 8,2 | +3,2 | 4 | 25,8 | 1,69 |
| 2015 | 5 | 8,8 | +3,8 | 5 | 29,6 | 1,67 |
| 2016 | 5 | 8,5 | +3,5 | 6 | 33,1 | 2,15 |
| 2017 | 5 | 11,92 | +6,9 | 7 | 40,0 | 2,92 |
| 2018 | 5 | 20,30 | +15,3 | 8 | 55,3 | 5,11 |
- Kümülatif sapmanın 2012–16 eğimi +3,3/yıl; corr(g_t, C_{t−1}) 2013–18 = 0,96 (n=6, iki seri de trendli).
- Öğrenme kazancı (Δ12 b12 = g·(π − b12_{t−12})): 2014-01–2016-10 g=0,33 (t 3,5) → 2016-11–2018-12 g=0,53 (t 13,1). Artış Kasım 2016'dan SONRA ölçülüyor; 2006–12 kıyası yok (S1).
- TCMB'nin kendi metni (Başkan, "2009 Yılında Para ve Kur Politikası"): hedeflerin "iki yıl üst üste aşılması … çapa olma fonksiyonunun zayıflamasına neden olmuştur"; beklentilerde "giderek artan oranda geçmiş dönem enflasyonuna ağırlık". Yani aynı mekanizma 2006–08'de bir kez yaşanmış ve hedef revizyonuyla (Haziran 2008) karşılanmış.
- **Karşı olgu, Brezilya (hedef 4,5 [İKİNCİL]):** 2010–16'da 7 ardışık aşım, kümülatif 15,8; 12 ay beklenti farkı 2015'te 1,76 → 2017'de −0,12. corr(g, C_{t−1}) = 0,09. Hedefi kaçıran emsalde çıpa kalıcı kopmadı.

## K2 Tepki fonksiyonu (48 aylık kayan pencere, i ~ π + açık + Δkur)
- φπ (pencere sonu Aralık): 2009 1,35 · 2010 0,93 · 2011 1,49 · **2012 0,19 · 2013 0,45 · 2014 0,35 · 2015 0,47 · 2016 0,43** · 2017 0,74 · 2018 1,05 · 2019 1,46.
- φπ<1 olan pencerelerin oranı: 2009-12–2012-12 %41; **2013-01–2016-10 %100**; 2016-11–2019-12 %58. 12 ay kesintisiz <1 ilk başlangıç: **2012-07**.
- Tam dönem regresyon: 2006–10 φπ 1,06 (t 2,9); 2011-01–2016-10 (çoklu araç/asimetrik koridor) φπ 0,29 (t 3,3), kur katsayısı 0,08 (t 3,2); 2011–18 0,95.
- **Belirti bağı (K2 → 2016 Ç4 fonlama):** 2011–16/10 kuralına göre tahmin edilen fonlama Eki 6,8 / Kas 7,4 / Ara 8,3 / Oca 8,7; gerçekleşen 7,8 / 7,9 / 8,3 / 8,9. Ç4 2016'daki "düşük fonlama" zayıf kuraldan sapma değil; kuralın kendisi. Kural 2016-10'da bile φπ≈0,4.

## K3 Mali baskınlık (K2 + FDD/gelir + seçim öncesi 6 ay)
- 2011-01–2016-10: FDD/gelir katsayısı −0,31 (t −2,7), seçim +0,72 (t 1,8). 2011–18: −0,36 (t −6,0), seçim +0,95 (t 2,9).
- İşaret, mali baskınlığın beklenen yönünün tersine: faiz dışı fazla küçüldükçe faiz *yükseliyor*, seçim öncesinde faiz *daha yüksek*. "Faiz mali dengeye uyacak şekilde düşük tutuldu" bu veride görülmüyor. Trendli seriler, yön sahte olabilir. S4 (mali gevşeme Kasım 2016 öncesi ilk eşik, 2016-06) beklenti kanalı olarak BELİRSİZ kalıyor.

## K4 İletişim (birincil TCMB metinleri)
- 27.10.2016: 2016 %7,5, 2017 %6,5, "%5 düzeyinde istikrar" 2018. ER 2018-I: 2018 %7,9, 2019 %6,5, %5 "orta vadede". %5'e ulaşma tarihi her seferinde 2 yıl ileri itiliyor; 2017 tahmini hedeften 1,5 puan sapmış (eşik 0,5).
- Piyasa: b24 Eki 2016 = 7,01 → TCMB 2017 tahminine uzaklık 0,51, %5'e 2,01. Oca 2018: b24 8,23; TCMB 24 ay tahmini 6,4 (uzaklık 1,8), hedef 5 (3,2). Beklenti %5'ten çok TCMB tahminine yakın, ondan da yüksek.

## Hüküm
| Kök | Ön kayıtlı yanlışlama | Gözlem | Hüküm |
|---|---|---|---|
| K1 Sicil/öğrenme | C sabit / ilişkisiz / kazanç artmadı | C yükseliyor (+3,3/yıl), corr 0,96; kazanç 0,33→0,53 ama Kasım 2016 sonrası; Brezilya karşı olgusu: kaçırma ≠ kalıcı kopuş | **AYAKTA (gerekli, yetmiyor)** |
| K2 Tepki zayıflığı | φπ<1 inişi Kasım 2016'dan sonra / 2006–10 da <1 | İlk kalıcı <1 2012-07; 2006–10 φπ 1,06 | **AYAKTA**; zaman sırasında ilk |
| K3 Mali baskınlık | Mali değişkenler anlamsız | Anlamlı ama ters işaret; seçim etkisi ters | **YANLIŞLANDI (faiz tepkisi kanalı)**; S4 beklenti kanalı BELİRSİZ |
| K4 İletişim çelişkisi | b24 %5'e yakın veya tahmin ≤0,5 sapıyor | Tahmin 1,5 puan sapıyor; b24 TCMB tahminine yakın | **AYAKTA** |
| K5 Dış baskı | Resmi olay listesi | Açılmadı | **[DOĞRULANMADI]** |
- **Zaman sırası:** K2 (2012-07) → K1 ardışık aşım 2011'den beri büyüyor (2013'te bant dışı) → S4 mali eşik 2016-06 → kopuş 2016-11 → K1 kazanç artışı ve K4 ötelemesi sonra derinleşiyor (2017–18).
- **Emsal farkı (karşı olgu):** Brezilya'yla ayrışan şey kaçırma değil, kaçırmadan sonraki tepki: Türkiye'de φπ 2013–16'da sürekli <1.
- **Belirti ↔ kök:** 2016 Ç4 fonlamanın düşük kalması → K2 kuralının doğrudan çıktısı. Kur ayrışması, DİBS çıkışı, endeks çıkarılması: K1–K4'ün öngörmediği, ayrı olaylar (önceki dosyalar); kök değil.

## Zayıflıklar
- Beklenti 2013 öncesi yok; K2 gerçekleşen enflasyonla (geriye dönük) kuruldu; ters nedensellik (faiz enflasyona tepki/enflasyon faize tepki) ayrılmadı.
- Granger, Holm, placebo bu turda koşulmadı; yıllık n=6 korelasyonları trend kaynaklı olabilir.
- Brezilya hedefi [İKİNCİL]; Meksika ve Güney Afrika yok → tek emsal.
- 2011–16 çoklu araç döneminde politika duruşu tek faizle tam ölçülmüyor (koridor, ROM, ZK).
- K5 ölçülmedi; "rant" bulgu sayılmadı.
