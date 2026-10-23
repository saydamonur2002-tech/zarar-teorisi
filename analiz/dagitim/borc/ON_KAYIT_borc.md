# ON_KAYIT_borc (yazıldı: 2026-10-23, hesaptan ÖNCE)
Soru: Varlık/ücret kaybı ne kadar borçla ikame edildi? 2014-25, % GSYH, kümülatif.
Tanımlar:
- A_ücret = Σ_{2015..25} (ws_t − ws_2014), ws = AMECO ALCD0 düzeltilmiş ücret payı (% GSYH piyasa fiyatı) [VERİ]. Net ve brüt (yalnız negatif yıllar) ikisi raporlanır.
- A_finans (hane) = k1_TL + k5_senyoraj (dagitim/eksik, hane3) [HESAP].
- A_firma = k2_kur (−10,58) [HESAP]; makine payı düşüşü yalnız nitel (stok oranı, GSYH değil).
- B_akım = Σ ΔD_t / GSYH_t (nominal net yeni borç), B_stok = Δ(D/GSYH) 2014→2025. D: finansal hesaplar F.4 kredi yükümlülüğü (S.14 hane ZP34, S.11 firma ZP34) [VERİ; dosya EVDS3 anahtarsız uçtan 2026-10-07 çekildi → beyan].
- Kayış payı = B_akım / |A|.
- Grup ayrımı: ücret kaybı K_gelir [VEKİL]; borç K_borc = borçlanma yaygınlığı(dilim) × gelir payı [VEKİL, İKİNCİL yaygınlık]; duyarlılık K_tuketim.
- Tüketim/varlık ayrımı: BDDK 2019-25 konut (varlık) vs ihtiyaç+taşıt+kart (tüketim) net akış payı [VERİ].
Kriterler:
K1: alt40 kayış payı > üst20 kayış payı (ana anahtarla ve duyarlılıkta) → TUTTU/TUTMADI.
K2: Hane yeni borcunun >%50'si tüketim (ihtiyaç+kart) → "ücret kaybı tüketim borcuyla ikame edildi" adayı.
K3: Yıllık: ücret payı düşüş yılı ile hane tüketim kredisi reel büyümesi arasında korelasyon > 0 (n küçük, yalnız betimsel; nedensellik iddiası yok).
K4: Firma B_akım > |A_firma| → firma kur kaybı borçla kapatılmış olabilir [aday].
