# ON_KAYIT (sim4_v2) — sim4_kalibre + uyarılar
Taban: sim4_kalibre aynen (A1-A2 model12 MC, A3 κ=0,5 BDDK anapara+güncel faiz).
1) Süre TL/YP ayrı: tl_yp/t.py mantığı, kural (a) orantılı, OVP, kur beklentisi (2026 +%19, sonra (1+π)/1,025) [VARSAYIM tl_yp]. Başlangıç TL κ·f·9.905,7, YP κ·f·9.313,3; KOBİ TL 5.712,8 / YP 1.285,5 [VERİ/HESAP BDDK 30.04.2026].
2) Kredi daralması 0,08×7.869,8=629,6/yıl [HESAP, repo ×0,08]. Varsayım [VARSAYIM]: daralma ticari kredi payına göre firmalara dağılır; firma bunu (i) piyasa faiziyle yeniden finanse eder → F += 629,6×%53,19 (yeni kredi durdurma kapsamı dışında), ve (ii) yeniden finansman bulamadığı kısım yok sayılır; süreye etki: ödeme kapasitesi bu ek faiz kadar azalır. Duyarlılık: tam erişim kaybı (ödeme −629,6/yıl).
3) Kim taşıyor: A1 net faiz (stok×mahsup×spread) = banka net faiz geliri kaybı [HESAP, model12 tanımı]; A2 firma–firma ticari borç, faizsiz → banka/kamu yükü 0; köprü kredi talebi kaybı banka için fırsat geliri (kopru_faiz) ayrı satır.
4) Firma mevduatı 4.400,1 TL/YP: ticari kuruluş YP payı = 82,7 mlr$×(12.560/256,2) / 11.454 ≈ %35,4 [HESAP, BDDK 9.10.2026 İKİNCİL]. Senede oranı TL %19,8, YP %30,2; kayıp TL (π−%43,30), YP (π−%2,58).
GSYH 85.299, kâr 1.014,5, RAV 4.771,2/0,166.
