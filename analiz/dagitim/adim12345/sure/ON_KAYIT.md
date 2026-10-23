# ON_KAYIT (sure)
D (faizi durdurulan anapara, etkin) = κ·ψ·(S0−A1_stok) [HESAP; model.py ile aynı kapsam]. I3 = A3_faiz (model).
Kapasite/yıl = c·I3 + max(EFK − F_kalan,0)·(1−τ)·(1−φ). c∈{0.5,1}; τ=0.25 kurumlar vergisi [VARSAYIM]; φ yatırım payı U(0.3,0.7), merkez 0.5 [VARSAYIM].
T = D/kapasite (nominal sabit, 2025 GELTAB tabanı; büyüme/enflasyon yok).
Kalkınca oran (L yılda) = (F_kalan + I3·max(1−L/T,0))/EFK. Asgari L (oran<%33): L* = T·(1−(0.33·EFK−F_kalan)/I3); F_kalan/EFK≥0.33 ise "mümkün değil".
KOBİ/büyük: kobi_payi ile bölünür. MC: model.mc() çekilişleri, c ayrı koşu.
