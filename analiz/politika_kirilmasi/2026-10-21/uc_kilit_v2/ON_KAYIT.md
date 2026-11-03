# ON_KAYIT — Üç kilit v2 (hazırlık, GEÇİCİ kur baskısı)
Yazıldı 2026-10-21 ~13:55 TSİ, ızgara koşulmadan önce. PR #44 (cipali_uc_kural/) yalnız okundu: `git fetch origin pull/44/head:pr44` (yerel ref) + `git archive` ile pr44_kopya/ altına kopya; repoya/GitHub'a yazma yok. Kopya kod değiştirilmez; sarmalayıcı (kosu_v2.py) `calistir` içindeki H, alfa_g, beta_i, alfa_pass, lam, w değerlerini dışarıdan verir. EVDS: PR'ın tahmin.json'u (EVDS3 anahtarsız uç, PR beyanı) ve önceki klasörler; yeni çekim yok. EVDS_API_KEY okunmaz. Nedensellik yok; senaryo çıktısı ölçüm değil [TAHMİN].
## PR #44'ten alınan (değişmez)
Kurallar: K1 ücret tabanı (2031-Q4 kapsama ≥ kapsama_0−0,02 ve iki çeyrek üst üste <0,95·kapsama_0 yok), K2 kredi tavanı (kilitli tüketici büyümesi ≥4 çeyrekte mevcut yoldan 0,5 puan düşük), K3 geri alma tetiki (≥1 tetik; öncül yoksa sınanmadı). Birlikte = üçü geçti. Senaryo 2026-Q4..2031-Q4, adım sırası PR'daki gibi.
## Yeni tanımlar
- Çıpa (yeni): e24 = w·(5+δ) + (1−w)·π + φ·g12. δ = çıpa sapması: 0 (resmî %5), 0,9 (ortuk_cipa: 2013–16 beklenti − TCMB ER tahmini ortalama primi [HESAP]). Alternatif "kayan örtük düzey" = son 12 ay ortalama e24 (başlangıç 2026-09 gözlemi) — δ_alt = e_son − 5.
- Mekanik yapışkanlık: ek varyant "sabitli" = PR'ın serbest terimli denklemi (e24 = 14,41 + 0,038π + 0,108 g12, R2426) — w tanımsız.
- Kur baskısı (GEÇİCİ yer tutucu): kur_sabit_terim çeyreklik α → aylık αg = α/3. Seçenekler: PR R2426 αg=2,751; taban 13,405/3; kalan (+D1, 2021–24) 3,591/3; 0. βi R2426'da kalır (−0,0271). Cursor ayrıştırması gelince αg (ve gerekirse βi) yerine konur, ızgara aynen yeniden koşulur.
- Geçiş: λ ∈ {0,160 (R1617), 0,409 (R2426)}; geçiş sabiti alfa_pass ∈ {1,951 (R2426), 0}.
- Reel faiz: sabit varyantta i ∈ {başlangıç i, π0+5, π0−5}; tepkili varyant PR faiz kuralı.
- w ızgarası 0; 0,25; 0,5; 0,75; 1.
## "Koşul" ve hüküm
Koşul bölgesi = Birlikte="gecti" olan hücreler kümesi. Bağlayıcı kısıt = en çok hücrede "kaldi"/"sinanmadi" üreten kural ve hücre durumunu tek başına değiştiren parametre (diğerleri sabitken geçiş sayısı farkı). Bölge boşsa "koşul yok — bağlayıcı: X" yazılır; eşik kaydırılmaz.
## SAPMALAR (hesap sonrası)
- S1: "Sabitli" beklenti varyantı (serbest terimli denklem) koşulmadı: PR calistir() e24'ü w·H biçiminde kuruyor, kodu değiştirmeden enjekte edilemedi. Yalnız w ızgarası + δ koşuldu.
- S2: Alternatif "kayan örtük düzey" δ = e(2026-09) − 5 = 13,32 olarak tek değerle girdi (12 ay ortalaması değil, son gözlem).
- S3: Sabit faiz varyantında reel faiz ızgarası (π0±5) sonucu neredeyse değiştirmedi; çünkü βi R2426 = −0,027 (faiz kur denklemine çok zayıf giriyor). Faiz kanalı bu modelde fiilen kapalı.
- S4: βi kur_sabit_terim'den değil PR R2426'dan; αg ile βi farklı denklemlerden karıştırıldı [VEKİL].

## EK-1 (2026-10-21 ~14:00 TSİ, yeniden koşudan ÖNCE) — Cursor PR #37 run #19 sonucu
Kaynak: parent'ın aktardığı Cursor özeti (g = 13,41 − 0,187·AOFM_{t−1}, çeyreklik 2021Q1–24Q4; 2018Q1–24Q4 parça eğimleri). Cursor store'unda (bc-cd6a16ae…) bu koşunun dosyası bulunamadı; repo dallarında da aranıp bulunamadı → sayılar [İKİNCİL-aktarım].
kosu_v2.py değiştirilmez; yeni dosya kosu_v3.py, PR calistir() kaynağını inspect ile alıp yalnız g_ham satırına ek terim ve K3-alt tanımı ekler (PR kopyası da değişmez).
- (a) cursor_dogru: αg = 13,41/3, βi = −0,187/3 (aylık; kosu g_ham = 3·(αg+βi·i_giren) → çeyreklik 13,41 − 0,187·i_{t−1}). i = APIFON4 [VEKİL AOFM].
- (b) cursor_parca: (a) + sapma biçiminde içsel parçalar: Δg_q = 0,018·(π_t−π_0) + 0,137·(e24_t−e24_0). Diğer parçalar (cari, portföy, rezerv, YP payı) son değerde sabit ⇒ sapma biçiminde katkı 0. Parça regresyonunun sabiti aktarılmadığı için düzey (a) doğrusundan alınır (SAPMA-E1).
- (c) cursor_parca_ust / _alt: π ve e eğimleri %95 uçlarında. Cursor'ın se'leri aktarılmadı; vekil se'ler benim tekrar tahminimden (g ~ aofm_l + π_l + b24_l, 2018Q1–24Q4, n=28, NW4: se π 0,172, se b24 0,718) [VEKİL] → π [−0,319; 0,355], e [−1,270; 1,544]. Benim nokta tahminlerim Cursor'la uyuşmadı (π −0,106; b24 0,610) — SAPMA-E2.
- Izgara: w {0;0,25;0,5;0,75;1} × δ {0;0,9} × kur {pr_R2426, kst_kalan, a, b, c_ust, c_alt} × λ {0,16;0,409} × α_geçiş {1,951;0} × faiz {sabit i0, tepkili}.
## EK-2 K3 duyarlılık (hükmü değiştirmez, açıkça "K3-alt" etiketli)
K3-alt: senaryo yolunda yıllık enflasyon (pi_y) en az bir çeyrekte ≤ 7 (5 hedef + 2 belirsizlik bandı) olursa "gecti"; başlangıç π0 = 29,7 > 7 olduğundan öncül var sayılır, hiç inmezse "kaldi"; patlama → "sinanmadi". Birlikte-alt = K1, K2, K3-alt.
## SAPMALAR (EK-1/EK-2 hesap sonrası)
- SAPMA-E1: (b) parça düzeyi (a) doğrusundan; parça regresyonunun sabiti yok [İKİNCİL-aktarım eksik].
- SAPMA-E2: (c) uçları için se, Cursor'dan değil benim 3 değişkenli tekrar tahminimden [VEKİL]; noktalar uyuşmadı.
- SAPMA-E3: c_ust yolları deflasyona gidiyor (2031 medyan −36 / −9); kapsama 1,5–10,9. Ekonomik olarak anlamsız uç; K1/K3-alt "geçti" hücreleri bu uçta bilgi değil.
- SAPMA-E4: c_alt, α_geçiş 1,951, λ 0,409, w 0 hücresinde K3-alt "gecti" salınım kaynaklı olabilir; ayrıca incelenmedi.
- SAPMA-E5: K2, 20 hücrede patlama yüzünden "sinanmadi" (v2'de hep "gecti" idi).
