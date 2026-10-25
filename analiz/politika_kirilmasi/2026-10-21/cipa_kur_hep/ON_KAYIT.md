# ON_KAYIT — "Başından beri çıpa yoktu, hep kura bağlıydı" iddiasının yanlışlanması
Yazıldı 2026-10-21 ~13:00 TSİ, hesaptan önce. Veri: cipa_kok/ham (EVDS3 anahtarsız web ön yüzü, BEYAN; EVDS_API_KEY okunmaz), Brezilya BCB SGS API. Nedensellik iddiası yok; haber sayısı yok.
## Model (kayan pencere, aylık)
b_t − π̄_t = w·(H_t − π̄_t) + λ·Δkur_t + c + e   (b = 24 ay [yoksa 12 ay] TÜFE beklentisi, H = hedef, π̄ = son 12 ay yıllık TÜFE, Δkur = USDTRY 3 aylık log değişim %, EVDS kur bir ay geriye değil gün kayması aylık ortalamada ihmal edilebilir; yine de ay sonu değil ay ortalaması kullanılır). Sabitli ve sabitsiz. HAC (Newey-West, 6 gecikme) %95 GA. Pencere 36 ay.
## Ölçütler
- AYAKTA: 2016 öncesi pencerelerde λ, 2017+ ortalama λ'nın GA'sı içinde VE w GA'sı 0'ı içeriyor.
- YANLIŞLANDI: 2016 öncesi pencerelerin çoğunda λ'nın üst GA sınırı 2017+ nokta tahmininin altında VE w alt GA sınırı > 0.
- Diğer durumlar: BELİRSİZ.
- Kırılma: Bai-Perron (ruptures, BIC) λ_t ve w_t serilerinde; ayrıca beklenti-kur geçişi (b'nin Δkur'a basit regresyonu) kayan.
- Emsal: Brezilya Focus 12 ay beklentisi aynı denklem (H=4,5 [İKİNCİL]); BRL/USD.
## SAPMALAR (hesap sonrası)
- S1: PPA beklentileri EVDS3'te yalnız 2013-01+ (TP.BEK.S01.A.U dahil). 2006–2012 pencereleri TR için KOŞULAMADI; "2016 öncesi" = 2013-01..2016-10.
- S2: EVDS t−1 kur kayması: aylık ortalama kullanıldı, tek günlük kayma aylık ortalamada ~1/21 ağırlık; ayrıca düzeltilmedi.
- S3: Bai-Perron yerine (i) kayan katsayılarda ruptures Binseg (BIC benzeri ceza) ve (ii) tam denklemde sup-Chow (%15 kırpma) kullanıldı.
- S4: Ek ölçü (ön kayıtta "kur-beklenti geçişi" olarak adı vardı, tanımı sonradan sabitlendi): Δb_t = a + γ·Δkur(3 ay log %)_t, 36 ay kayan, HAC.
- S5: Brezilya hedefleri 2005–18 4,5; 2019 4,25; 2020 4; 2021 3,75; 2022 3,5; 2023 3,25; 2024+ 3 [İKİNCİL]. Brezilya'da 24 ay serisi alınmadı, 12 ay Focus (Suavizada=S) aylık ortalama.
