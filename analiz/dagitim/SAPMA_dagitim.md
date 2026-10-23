# SAPMA_dagitim
1. Kur kanalı yalnız 2017–25 (hane DTH ve TCMB net rezerv serileri 2016'dan başlıyor). 2014–16 = EKSİK.
2. D (yurt dışı) her kanalda kapanış kalemi: D = −Σ diğerleri → "D+artık". Bağımsız ölçüm değil; Σ=0 tanım gereği.
3. Firma döviz pozisyonu: TCMB FKDFDVY (PDF, 2026-06 sürümü) net döviz pozisyonu [VERİ]; ihracat alacağı, DYY, ithalat borcu içerir, finansal hesap enstrümanlarıyla birebir değil [VEKİL].
4. Hane döviz = gerçek kişi DTH (BDDK, mn TL varsayımı) [VEKİL]; altın ve yastık altı döviz yok.
5. TCMB döviz = net rezerv (zincir/ceyrek_zincir.csv NR, mlr $) [VEKİL]; swap ayrıca düşülmedi. TCMB TL tarafı finansal hesaplarda B içinde varsayıldı [DOĞRULANMADI].
6. Hazine döviz = merkezi yönetim brüt dış borç / GSYH (HMB Ağu-2026); YP iç borç ve 2025 (2024 oranı taşındı) [VEKİL].
7. Banka döviz pozisyonu 0 [VEKİL].
8. Yabancı para faizi 0; TL faizi politika faizi yıl ortalaması [VEKİL].
9. Hane üst/alt: TL kanalında gerçek kişi ≥1 mn TL mevduat payı, kurda ≥1 mn TL DTH payı [VEKİL]; nominal eşik enflasyonla kayıyor → üst pay şişer.
10. Pasta büyümesi = nominal GSYH büyümesi / TÜFE − 1 [VEKİL]; GSYH deflatörü ≠ TÜFE, 2021–23'te çok şişik → güvenilmez.
11. EKSİK: KKM maliyeti (kamuya açık Hazine/TCMB ayrık tutar bulunamadı), transfer/teşvik/vergi aktör ayrımı, senyoraj ayrı satırı (TCMB TL yükümlülüğü kanal 1 içinde), konut yeniden değerlemesi. Hane hisse satırı akım dahil reel değişim, gerçekleşmemiş.
12. Finansal hesaplar EVDS3 anahtarsız uçtan 7.10.2026 önceden çekilmiş (BEYAN). FKDFDVY PDF'i tcmb.gov.tr'den doğrudan indirildi.
