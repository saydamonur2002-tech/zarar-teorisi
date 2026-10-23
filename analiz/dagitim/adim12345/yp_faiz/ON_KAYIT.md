# ON_KAYIT (yp_faiz)
Repo kuralı: adim3_faiz_durma.py s.12 "SFC: F NL_t += I_t ; B′ NL_t −= I_t ; ΣNL değişmez (transfer). Alternatif: B′ yerine K′ üstlenir (ayrı sütun)." s.86 "ödeyen tek hazne (B′ ya da K′), ikisi toplanmaz." YP/TL ayrımı ve paylaşım kuralı YOK.
Veri: BDDK haftalık 30.04.2026 ticari YP 9.313,3 mlr TL, KOBİ YP 1.285,5 [VERİ]. TCMB FEALNFC 2026-08: NFC yurt dışı kredi 1.362+133.358=134.720 mn$; yurt içi banka YP kredi 182.265 mn$ [VERİ]. Faiz: TCMB haftalık akım 24.07.2026 (BMD derlemesi) USD ticari %7,92, USD mevduat %2,58, spread %5,34; EUR %7,11/%1,47 [İKİNCİL]. Akım faiz stoka uygulanır [VARSAYIM]; döviz karışımı tamamı USD [VARSAYIM], EUR duyarlılık.
Banka: özkaynak 4.771,2 mlr TL, Oca–Ağu net kâr 676,3 → yıllık 1.014,5 [HESAP], SYR %16,60 [VERİ BDDK Ağu 2026, ikincil derleme]. RAV ≈ özkaynak/SYR [VARSAYIM, yasal özkaynak≠muhasebe].
D_YP = κ·(1−A1_stok/S0)·9.313,3, A1_stok P50 4.588,5 [HESAP]. κ 0,25/0,5/1.
Senaryo: (1) banka tümü; (2) kamu tümü; (3) mevduat faizi payı (2,58/7,92) kamu, spread banka. Yurt dışı doğrudan kredi faizi durdurulamaz, firmada (KOBİ ayrımı yok → büyük [VARSAYIM]). USD/TL 49,797 (PKA cari ay) [TAHMİN]. GSYH 85.299 mlr TL [HESAP, model params]. Süre toplamı ×1,9 ve ×2,3 yıl, sabit kur.
Fonlama ayrımı (YP mevduat/sendikasyon) sayısal olarak bağlanmadı: veri parçalı.
