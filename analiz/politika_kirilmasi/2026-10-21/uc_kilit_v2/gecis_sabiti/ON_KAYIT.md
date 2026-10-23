# ON_KAYIT — Geçiş sabiti α_geçiş = 1,951 parçalama
Yazıldı 2026-10-21 ~14:20 TSİ, hesaptan önce. PR #44 yalnız okunur (../pr44_kopya). Yeni EVDS çekimi: EVDS3 anahtarsız web ön yüzü (igmevdsms-dis/fe) — BEYAN; EVDS_API_KEY okunmaz. TÜİK engeli atlatılmaz. Nedensellik yok.
## Denklem (PR birebir): π1_t = α + λ·g1_t, π1 = 100·ln(P_t/P_{t−1}), g1 = 100·ln(USD_t/USD_{t−1}), R2426 = 2024-01..son, NW Bartlett gecikme 4.
1) Yeniden üretim: |α−1,951|<0,01 ve |λ−0,409|<0,01 değilse SAPMA ve sonraki adımlar kendi üretimimle.
2) Alt gruplar (EVDS'de bulunanlar: hizmet, kira, enerji, gıda, temel mal, alkol-tütün, çekirdek B/C, yönetilen fiyat varsa): her grup için aynı denklem; katkı = α_j × w_j (w_j: EVDS'de yayımlanan resmî TÜFE ağırlığı; yoksa [DOĞRULANMADI], katkı hesaplanmaz). Kapsama = Σkatkı/α_toplam. Ölçüt: kapsama 0,9–1,1 → ayrıştırma tutarlı; dışında → ağırlık/endeks uyumsuzluğu not.
   Hüküm "hizmet/kira ağırlıklı": hizmet+kira katkısı ≥ %50.
3) Model hatası: sırayla ekle, her adımda kalan α ve NW %95 GA:
   M0 PR; M1 + g1 gecikme 1..6 (λ toplamı); M2 + π1_{t−1} (atalet; uzun dönem α/(1−ρ) de yazılır); M3 + Δe24 ve e24 düzeyi/12 (aylık beklenti); M4 + Ocak kuklası (asgari ücret ve vergi ayları: Ocak, Temmuz); M5 + 11 ay kuklası (mevsimsellik; α = aylar ortalaması olarak yeniden tanımlanır).
   Ölçüt: "α model hatası" AYAKTA: M2–M3'te α'nın GA'sı 0'ı içeriyor. YANLIŞLANDI: tüm modellerde α alt GA > 0,5.
4) Kira/hizmet ataleti: hizmet ve kira π1'inde ρ (π1_{t−1} katsayısı) ve 12 ay geçmiş yıllık enflasyona regresyon; Ocak/Temmuz ücret aylarında ortalama sıçrama. AYAKTA (ücret–hizmet bağı): Ocak/Temmuz kuklası hizmette pozitif ve NW GA 0'ı dışlıyor.
5) Brezilya: IPCA aylık (SGS 433) ve BRL (SGS 3698) aynı denklem 2024-01..son; α ve λ.
6) Izgara: uc_kilit_v2/kosu_v3.py mantığıyla (kosu_v3.py değiştirilmez; yeni dosya) α_geçiş ∈ {kalan α (en tam M), atalet modeli: π1 = α_M2 + ρ·π1_{t−1} + λ g1 — PR kodunda atalet yok; sarmalayıcı aylık ataleti çeyreklik yaklaşıma çevirir: π_q = 3α_M2 + ρ·π_q,önceki + λ g [VEKİL]}. K3 PR ve K3-alt (≤7) raporlanır.
## SAPMALAR (hesap sonrası)
- S1: Alt gruplar 2025=100 COICOP-2018 ana grupları (01–13) + 041/0411/045/0451/072 (EVDS3). Hizmet, temel mal, enerji özel kapsamı ve çekirdek B/C 2025 bazında kod tahminiyle bulunamadı (500); EVDS3 metadata ucu anahtar istiyor (kullanılmadı) → [DOĞRULANMADI]. 2003 bazlı TP.FE.OKTG01–06 2025-12'ye kadar var ama kod-ad eşlemesi doğrulanamadı → kullanılmadı.
- S2: Resmî ağırlık serisi EVDS'de bulunamadı → ağırlık VEKİL: genel π1'in 13 grup π1'ine negatif olmayan EKK (NNLS) katsayıları, toplam 0,994'ten 1'e ölçeklendi [HESAP/VEKİL]. 041 ve 0411 aynı seri çıktı.
- S3: Alt grup denklemleri 2025 baz genel endeksle; genel α 1,950 (PR 1,951 ile uyumlu).
- S4: Adım 6 "en tam M" yerine M5 (12 ay kuklası + atalet + kur gecikmeleri, α=ay sabitleri ortalaması 1,302) kullanıldı; M3/M4'te α yalnız içsel beklenti terimiyle birlikte anlamlı. Ek varyant "beklenti_M3" (π_q = 3(−0,841 + 2,156·e24/12) + λg) ön kayıtta yoktu, etiketli EK.
- S5: Atalet çeyreğe π_q = 3α + ρ·π_q,önceki ile taşındı (ρ aylık 0,481 olduğu gibi) [VEKİL].
