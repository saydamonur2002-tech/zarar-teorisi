# RAPOR_paylas2 (2026-10-23 TSİ)
Ayrıntı: tablo_paylas2.csv (aktör×düzey S1,S2,S1−S2), ozet_S1eksiS2.csv, paylas2.png, q.py. Ön kayıt: ON_KAYIT_paylas2.md; sapmalar: SAPMA_paylas2.md.

## S1 (erteleme) — artık her düzeyde aynı [HESAP]
Hane alt +0,13 | orta +0,45 | üst +9,74 | KOBİ −1,92 | Büyük −4,90 | Banka −1,08 (eski −1,18) | Hazine −3,78 (eski −6,90) | TCMB −1,65 (eski +1,48) | Yurt dışı+artık +3,00.
Değişim: TCMB→Hazine kâr aktarımı 2019–21 = 1,78+0,86+0,48 = 3,12 GSYH puanı [VERİ: TCMB 2020 ve 2021 yasal/IFRS finansal tabloları, özkaynak değişim tablosu: 2019 37,52+40,77; 2020 39,11+5,35; 2021 30,21+5,58 milyar TL]. Banka YP pozisyonu +0,09 [İKİNCİL×VARSAYIM].

## S1−S2 (ertelemenin getirisi), düşük / orta / yüksek [HESAP; S2 VARSAYIM]
| Aktör | düşük (simetrik≈statik) | orta (κ=0,5) | yüksek (κ=1) |
|---|---|---|---|
| Hane alt | +0,21 | −0,26 | −0,66 |
| Hane orta | +0,44 | −0,57 | −1,43 |
| Hane üst | +2,20 | −3,61 | −9,25 |
| KOBİ | +1,34 | +4,58 | +7,79 |
| Büyük firma | +2,36 | +9,55 | +16,69 |
| Banka | −1,18 | −1,18 | −1,18 |
| Hazine | +5,28 | +8,89 | +14,80 |
| TCMB | −10,07 | −11,19 | −15,02 |
| Yurt dışı+artık | −0,59 | −6,20 | −11,75 |
Ek kur (log, kümülatif): ≈0 / 0,41 / 0,82. Gizli maliyet S1: 8,46; S2 görünür TCMB sermayesi: 5,63 / 2,75 / 2,21.

## Ölçütler
C1 üst20 ertelemeden kazanır her düzeyde: TUTMADI (yalnız düşükte +; orta/yüksekte −). Dinamik S2'de kur daha çok kayacağı için dövizli üst gelir dondurmadan daha çok kazanırdı.
C2 TCMB en büyük kaybeden: TUTTU (üç düzey).
C3 gizli > görünür: TUTTU (8,46 > 5,63/2,75/2,21).
C4 büyük firma en büyük kazanan (orta): TUTTU, ama sınırda (9,55 vs Hazine 8,89).
C5 alt40 |S1−S2|<0,5: KIRILGAN (yüksekte 0,66).
Hiçbiri nedensel değildir; S2 tek denklemli karşı-olgu (genel denge, faiz, büyüme, davranış yok).

## Kapanan / kalan zayıf noktalar
Kapandı: statik S2 (dinamik aralık), TCMB kârı Hazine'ye (2019–21), banka döviz pozisyonu ≠0 (kısmen, 2020–22), yurt dışı: UYP doğrudan −0,75 ayrı gösterildi; artık = 3,00 − (−0,75) = 3,75 puan açıklanamayan kalıntı [HESAP].
Kalan: banka net kâr/NIM/KKM komisyonu (çekilmedi); 2014–18 TCMB aktarımları; firma ölçeğine göre YP pozisyonu ve 2024–25 ölçek verisi; servet tabanlı hane anahtarı (HFTA mikro verisi kamuya açık değil); GYKA 2024 yalnız ikincil kaynak; S2 hâlâ kısmi denge.
EVDS kullanılmadı (kur kuralı girdileri yerel kalibre_faiz dosyasından; o seri daha önce derlendi). Repoya yazılmadı.
