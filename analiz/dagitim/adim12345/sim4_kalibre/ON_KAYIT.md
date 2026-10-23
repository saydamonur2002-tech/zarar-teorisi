# ON_KAYIT (sim4_kalibre)
A1–A2: model/model12 aynen (MC seed 1, N params.json) [HESAP].
A3 kalibre: κ=0,5 sabit [VARSAYIM kullanıcı]; I3 = κ·(1−A1_stok/25.339,8)·(TL 9.905,7·%53,19 + YP 9.313,3·%7,92) [VERİ BDDK 30.04.2026; faiz VERİ/İKİNCİL], F1'e kırpılır. KOBİ payı model çekilişi.
A4 kalibre: senede TL 4.055,9 (%19,8) + YP 3.814,0 (%30,2) = 7.869,8 [HESAP adim4_mevduat]. Firma etkisi: firma vadeli mevduatı 4.400,1 [VERİ] × 0,238 × (π − r_mev) — firmanın faiz geliri kaybı (TL %43,30 ağırlığıyla, YP payı ayrıştırılmadı [VARSAYIM]); oran etkisi 0 (EFK dışı). Kredi daralması 0,08 × 7.869,8 [repo sabiti].
Taşıyan: banka marj 604,7 → kâr 1.014,5, RAV 4.771,2/0,166; kamu prim 7.869,8·π, GSYH 85.299; mevduat sahibi kaybı = faiz − prim.
Süre: sure/dinamik/d.py sim(), OVP, kur beklentisi, c=1 ve 0,5, κ=0,5 sabit.
