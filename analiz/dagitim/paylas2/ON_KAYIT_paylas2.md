# ON_KAYIT_paylas2 — hesaptan ÖNCE yazıldı (2026-10-23 TSİ)
Taban: paylas/tablo_paylas.csv (S1 erteleme, S2 statik dondur). Birim: 2014–25 kümülatif %GSYH reel, + kazanç.

## Düzeltmeler ve beklenen etki
D1 Dinamik S2 [VARSAYIM]: S2'de TCMB net rezerv satmaz → baskı kura gider. Kalibre kur kuralı y = psi·x (psi=3.4, x = −ΔNR·4/Yd, kalibre_faiz/ceyrek_veri.csv). Ek değer kaybı_t = κ·psi·x_t (x>0 çeyrekler), κ ∈ {düşük 0.25, orta 0.5, yüksek 1.0}. Yıllık k2 (aktör) × (1 + ek_t/gerçek_dlogE_t). Enflasyon geçişi β ∈ {0.2, 0.3, 0.45} → k5 senyoraj × (1+β·ek_t/π_t). k1 S2'de 0 kalır (pozitif reel faiz varsayımı). Beklenen: firmalar, Hazine S2'de daha çok kaybeder → ertelemenin firmalara getirisi büyür; TCMB S2 kazancı büyür.
D2 TCMB kâr dağıtımı → Hazine: resmi TCMB/Hazine kaynağından yıllık Hazine'ye aktarılan tutar bulunursa her iki senaryoda TCMB'den düşülür, Hazine'ye eklenir. Bulunamazsa açık kalır.
D3 Banka: BDDK/TBB net kâr, YP net genel pozisyon bulunursa banka k2 ≠ 0 yazılır. Bulunamazsa açık.
D4 Firma ölçek YP pozisyonu ve 2024–25 ölçek verisi: bulunursa k2 anahtarı güncellenir.
D5 Hane anahtarı: en güncel GYKA gelir dilim payları bulunursa güncellenir; servet anahtarı yalnız kamuya açık tablo varsa.
D6 Yurt dışı: UYP doğrudan değer ayrı satır, artık açıkça gösterilir.

## Ölçütler (sonuç hayatta kalıyor mu)
C1 Üst %20 ertelemeden kazanır (S1−S2 > 0) üç κ düzeyinin hepsinde.
C2 TCMB ertelemenin en büyük kaybedeni (S1−S2 en negatif) üç düzeyde de.
C3 "Erteleme gizli maliyeti > dondurma görünür bütçe maliyeti" (P3) üç düzeyde de; görünür maliyet = TCMB sermaye ihtiyacı (dinamik S2).
C4 Büyük firmalar ertelemenin en büyük kazananı (S1−S2 en büyük) orta düzeyde.
C5 Alt %40 için |S1−S2| < 0.5 puan üç düzeyde.
Bir ölçüt herhangi bir düzeyde bozulursa "kırılgan" yazılır. Nedensel iddia yok; S2 tek-denklemli bir karşı-olgu, genel denge değil.
