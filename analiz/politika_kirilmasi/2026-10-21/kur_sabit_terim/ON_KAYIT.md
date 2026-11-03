# ON_KAYIT — kur_sabit_terim (yazıldı: 2026-10-21, hesaptan önce)
Taban: g_q = α + β·AOFM_{q-1}; g = çeyrek ort. USD/TRY log farkı ×100 (FAIZ_KUR_KALIBRE.md). Ana pencere 2021Q1–2024Q4 (n=16), uzun 2018Q1–2026Q3.
Kalemler sırayla eklenir; her adımda α, β, R², "kalan α payı" = α_yeni/α_taban raporlanır.
- D1 enflasyon farkı: π_TR−π_US (çeyreklik log ×100, aynı çeyrek). Yanlışlama: katsayı %95 GA 1'i dışlarsa ve 0'ı içerirse "PPP α'yı taşıyor" düşer. Kabul: α kalan payı <%50 ve katsayı GA'sı 0'ı dışlar → ayakta [aday].
- D2 cari denge vekili: (mal ihr−ith + yatırım geliri net)/ithalat, çeyrek. Katsayı 0'ı içerirse ve ΔR²<0.05 → yanlışlandı.
- D3 DTH: veri box'ta yoksa [DOĞRULANMADI]; dış kaynak bloğu atlatılmaz.
- D4 CDS: anahtarsız resmi kaynak yoksa [DOĞRULANMADI].
- D5 kayan γ (cipa_kur_hep gecis_TR_b24, çeyrek ort, gecikmeli): katsayı 0'ı içerirse yanlışlandı. Not: γ kurdan türediği için mekanik içsellik riski — en fazla [aday].
- Eşzamanlı D1 ters yön (kur→enflasyon) içerir; gecikmeli D1 duyarlılık olarak koşulur. Nedensellik iddiası yok.
- t−1 düzeltmesi: günlük tcmb_gunluk.csv (2019+) ile bir iş günü geri kaydırılmış çeyrek ortalaması; |Δβ|>0.05 ise SAPMA olarak yazılır.
- Emsal: FRED BRL/MXN/ZAR ve TÜFE erişilirse aynı D1 regresyonu; değilse [DOĞRULANMADI].
