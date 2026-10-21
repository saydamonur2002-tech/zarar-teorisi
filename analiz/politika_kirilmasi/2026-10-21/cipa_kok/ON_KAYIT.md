# ON_KAYIT — Çıpa kökü (K1–K5)
Yazıldı 2026-10-21 ~12:55 TSİ, yeni veri çekilmeden önce. EVDS3 anahtarsız web (BEYAN); EVDS_API_KEY okunmaz. Haber yok; seçim tarihleri yalnız takvim [İKİNCİL-tarih]. Önceki çıktılar (cipa_sebep, cipa_tarihi) yeniden kullanılır. Nedensellik yok.
Bağımlı: g = 24 ay sonrası TÜFE beklentisi (PPA) − 5 (yoksa 12 ay). Eşik tarihi "kopuş" = 2016-11.
## K1 Sicil/öğrenme
Yıl sonu TÜFE − hedef (TCMB hedef belgeleri), 2006–2018: ardışık kaçırma sayısı N_t, kümülatif sapma C_t. Sabit kazanç g: Δb12_t(12 ay) = g·(π_t − b12_{t−12}) 36 aylık kayan pencere.
YANLIŞLAMA: (i) C_t 2012–2016 arasında artmıyorsa (eğim ≤0) VEYA (ii) yıllık g_t ile C_{t−1} korelasyonu <0,3 VEYA (iii) kazanç g 2016 öncesi pencerede 2006–12 penceresinden yüksek değilse.
## K2 Tepki fonksiyonu
i_t = c + φπ·(b12_t) + φy·gap_t + φe·Δ12 kur + e, 48 aylık kayan pencere, i = politika/ON faizi (2006–10), APIFON4 (2010+). gap = sanayi üretimi log − HP trend [VEKİL].
YANLIŞLAMA: φπ'nin 1'in altına ilk inişi 2016-11'den SONRA ise VEYA 2006–2010 pencereleri de <1 ise (ilke hiç sağlanmamış → "zayıflama" yok, K2 "zayıflama" düşer; "hiç güçlü olmadı" ayrı not).
## K3 Mali baskınlık
K2 denklemine FDD/gelir (cipa_sebep X4) ve seçim öncesi 6 ay kuklası eklenir (2010–2018). YANLIŞLAMA: ikisi de |t|<2 (HAC) → düşer. S4 sonucu (BELİRSİZ) aynen taşınır.
## K4 İletişim
TCMB Enflasyon Raporu yıl sonu ara hedef/tahmin (birincil) vs %5; beklenti b24 %5'e mi TCMB tahminine mi daha yakın (ortalama mutlak uzaklık). YANLIŞLAMA: b24 %5'e daha yakın VEYA TCMB tahmini %5'ten ≤0,5 puan sapıyor. Tahmin belgeleri yoksa [DOĞRULANMADI].
## K5 Dış baskı: resmi kaynaklı olay listesi yoksa [DOĞRULANMADI], ölçülmez.
## Karşı olgu (emsal): Brezilya Focus 12 ay beklenti farkı ve BCB hedef sicili; hedefi kaçıran emsalde fark büyüdü mü. MX/ZA yoksa [DOĞRULANMADI].
## Zaman sırası: her K için eşik ilk geçiş tarihi; Granger (12 gecikme sınır) Holm düzeltmeli; placebo: eşik tarihi rastgele kaydırma.
## SAPMALAR
- S1: EVDS3'te PPA beklentileri yalnız 2013+ (eski kodlar 500) → K1 kazanç testi (iii) 2006–12 ile kıyaslanamadı; K2'de π = gerçekleşen yıllık TÜFE [VEKİL] (beklenti yerine).
- S2: K2 faiz serisi 2006–10 TCMB BPP O/N teklif (TP.PY.P02.ON), 2011+ APIFON4; sanayi üretimi kaba ay ortalamasıyla arındırılıp HP (λ=129600).
- S3: Granger/yerel projeksiyon/Holm/placebo bu turda koşulmadı (yıllık n=6; cipa_sebep sonuçları taşındı).
- S4: Brezilya hedefi 4,5 (2006–18) [İKİNCİL]; BCB sayfası JS, birincil açılmadı. MX/ZA [DOĞRULANMADI].
- S5: K3 seçim kuklası takvimi [İKİNCİL-tarih].
