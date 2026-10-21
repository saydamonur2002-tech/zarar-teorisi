# ON_KAYIT — Ataletin parçalanması
Yazıldı 2026-10-21 ~14:30 TSİ, hesaptan önce. EVDS3 anahtarsız web ön yüzü (igmevdsms-dis/fe) — BEYAN; anahtar isteyen uçlar kullanılmaz; EVDS_API_KEY okunmaz. TÜİK 403 atlatılmaz. Nedensellik yok.
## Kapsam doğrulama
Kod-kapsam eşleşmesi: TCMB "Aylık Fiyat Gelişmeleri" (birincil PDF) içinde verilen yıllık değişimler (B, C, hizmet, temel mal, enerji, gıda, alkol-tütün-altın) ile EVDS serisinin aynı ay yıllık değişimi |fark| ≤ 0,05 puan ise DOĞRULANDI; değilse [DOĞRULANMADI], seri kullanılmaz.
## Denklem (her kapsam j, 2024-01..2026-09 veya serinin bittiği ay)
π_j,t = α + ρ·π_j,t−1 + Σ_{k=0..6} λ_k g1_{t−k} + δ_O·Ocak + δ_T·Temmuz + θ·e12_t/12 ; NW gecikme 4. Ayrıca yalnız (α, ρ) ve PR biçimi (α, λ0).
Katkı: α_j × w_j / α_genel ; ρ katkısı: w_j·ρ_j·ort(π_j) / (ρ_genel·ort(π_genel)) [HESAP]. Ağırlık: TÜİK/TCMB resmî ağırlık; yoksa önceki NNLS vekil [VEKİL].
## Sebepler (genel ve hizmet/kira için sırayla eklenir; ρ ve α düşüşü)
S0 taban (α, ρ, λ0); S1 endeksleme: asgari ücret artış oranı (o ay brüt AÜ log değişimi, resmî tutarlar; yoksa ucret_kopus verisi) + kira için 12 ay TÜFE ortalaması ve yasal %25 tavan dönemi kuklası (resmî tarih yoksa [DOĞRULANMADI]); S2 yönetilen: enerji ve alkol-tütün kapsamının o ayki enflasyonu (kontrol); S3 e12/12, e24/12; S4 kredi büyümesi (tüketici kredisi aylık log değişim, EVDS varsa); S5 gıda: 11 ay kuklası + işlenmemiş gıda varsa.
Hüküm: bir sebep "atalet açıklayıcısı" AYAKTA ise eklenince ρ en az %30 düşer VE katsayısının NW GA'sı 0'ı dışlar. YANLIŞLANDI: ρ düşüşü <%10 veya ρ artar. Arası BELİRSİZ.
## Brezilya: IPCA serviços (SGS 10844), livres (11428), monitorados (4449) aylık; aynı (α, ρ) 2024-01..son. Kod-ad eşlemesi BCB SGS sayfasından; açılmazsa [DOĞRULANMADI].
## SAPMALAR (hesap sonrası)
- SP1: Özel kapsam serileri 2003=100 TP.FE.OKTG01–28 yalnız 2025-12'ye kadar; 2025 bazlı karşılıkları bulunamadı (kod tahminleri 500). Pencere 2024-01..2025-12 (n=24); genel α bu pencerede 1,848 (PR 1,951 2024-01..2026-09).
- SP2: Kod-kapsam doğrulaması TCMB "Aralık Ayı Fiyat Gelişmeleri" 2024 Tablo 1 (birincil PDF, ham/afiyat_aralik24.pdf): aylık ve yıllık değerler tam eşleşti: 01 TÜFE, 03 B, 04 C, 05 D, 06 Mallar, 07 Enerji, 08 Gıda, 09 İşlenmemiş, 10 Taze meyve-sebze, 11 Diğer işlenmemiş, 12 İşlenmiş, 13 Ekmek-tahıl, 14 Diğer işlenmiş, 15 Enerji-gıda dışı mallar, 16 Temel mal, 17 Giyim, 18 Dayanıklı, 19 Diğer temel, 21 Hizmet, 22 Kira, 23 Lokanta-otel, 24 Ulaştırma hiz., 25 Haberleşme, 26 Diğer hizmet, 28 F (yönetilen hariç). 20 (38,92) tabloda yok — alkol-tütün (39,28) ve altın (36,01) arasında → "alkol-tütün-altın" [aday]. 02 ve 27 eşleşmedi [DOĞRULANMADI], kullanılmadı. Yönetilen fiyatların kendisi yok; yalnız F (hariç) var.
- SP3: Resmî ağırlık bulunamadı (TÜİK denenmedi/EVDS'de yok) → NNLS vekil, bölüm {Enerji, Gıda, Temel mal, Alkol-tütün-altın, Hizmet} [VEKİL].
- SP4: Mevsimsel düzeltilmiş kapsam serileri kullanılmadı (kod bulunamadı); mevsimsellik kukla ile.
- SP5: Asgari ücret yalnız Ocak 2024 ve Ocak 2025'te değişiyor → Ocak kuklasıyla neredeyse aynı; S1 ve S5 ayrıştırılamıyor. Kira tavanı kuklası 2024-01..06 tarihleri [İKİNCİL-tarih / DOĞRULANMADI].
- SP6: S4 (kredi büyümesi) seri doğrulanamadığı için koşulmadı [DOĞRULANMADI]. S5 için ithalat fiyatı vekili kullanılmadı.
- SP7: Atalet iki ölçüyle: ρ1 (önceki ay) ve ρ12 (12 ay önce, yıllık yeniden fiyatlama); hüküm ρ_top = ρ1+ρ12 üzerinden (ön kayıtta "önceki ay(lar)").
- SP8: Brezilya SGS kod-ad eşlemesi BCB sayfasından doğrulanmadı [İKİNCİL].
