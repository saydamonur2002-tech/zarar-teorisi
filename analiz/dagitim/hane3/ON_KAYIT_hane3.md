# ON_KAYIT_hane3 — hane satırının alt/orta/üst ayrımı (hesaptan ÖNCE yazıldı, 2026-10-23 TSİ)
Gruplar: alt = gelir beşlisi Q1+Q2 (%40), orta = Q3+Q4 (%40), üst = Q5 (%20). Eşdeğer hanehalkı kullanılabilir fert geliri (TÜİK GYKA).
Girdi: eksik/tablo_aktor_kanal_tam.csv 2014-25 hane kanal toplamları (değişmez; yalnız bölüştürülür, Σ korunur).
Ana anahtarlar (plan):
- k1 TL erimesi, k2 kur (DTH), k3 KKM, k7 banka altını: menkul kıymet/faiz geliri beşli dağılımı (GYKA 2018, gelir türü × beşli payı × beşli gelir payı) [VEKİL]
- k5 senyoraj (nakit): HBA tüketim payı 2022 [VEKİL]
- k4 gelir vergisi harcaması: gelir beşli payı [VEKİL]
- konut kâğıt serveti: gayrimenkul (kira) geliri beşli dağılımı GYKA 2018 [VEKİL]
- yastık altı altın: gelir payı [VEKİL] (beşliye göre altın varlığı verisi yok)
Duyarlılık: (a) KKM %90 "yüksek tutarlı" hesaplarda (TCMB ER 2024-II, ikincil) → üst %90; (b) DTH/TL için ≥1 mn TL mevduat payı üst, kalan Q1-4 gelir payıyla; (c) tüm kanallar gelir payıyla (alt sınır eşitsizlik); (d) senyoraj gelir payıyla; altın tüketim payıyla.
Ölçütler:
- Ö1: üstün hane net kazancındaki payı (VH hariç) > üstün gelir payı (~%47-48) → "kazanç gelirden daha yoğun".
- Ö2: alt %40 net (VH hariç) < 0 → "alt net kaybeden".
- Ö3: Ö1 ve Ö2 tüm duyarlılık setlerinde aynı yönde mi (sağlam) yoksa anahtara bağlı mı.
Hisse (MKK) kanalı ayrı satır değil; erişilirse yalnız kâğıt servet olarak eklenir.
