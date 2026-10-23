# Karşı-olgu testi: H (maliyeti üst gelir/sermaye taşımadı)
Dosyalar: ON_KAYIT.md (veri öncesi), wb_ham.csv, epizod.csv, testler.csv, karsi_olgu.png, SAPMA.md.

**(a) Şok sabit, yüksek kur şoku grubu (%48–191):**
- Y skoru en yüksek olan COL'da enflasyon %5,0; en düşük olan ARG'de %48,0 [HESAP]. Bu sıralama H yönünde.
- Ama TUR 2018 de "üste yük" skoru yüksek (+3,5) çıkıyor ve enflasyon %15,7. Sebep, vekilin ölçtüğü şey: dolaylı vergi payı düştüğü için skor yükseliyor, üst %10 payı ise arttı.
- Grup içinde H ile sonuç arasında tutarlı bir sıralama yok.

**(b) R1 (kur) ve R2 (reel faiz) kontrol edilince:**
- Y'nin eklediği R² artışı enflasyonda 0,03, faiz/gelirde 0,03. Önceden kaydedilen eşik 0,15 idi.
- Kısmi korelasyon enflasyonda −0,89 (H yönü), faiz/gelirde +0,69 (H'ye ters).
- n=5; sonuçlar güvenilir değil.
- NPL ve toparlanma için örneklem yetersiz.

**(c) Sentetik kontrol:** Yapılmadı (veri yetersiz).

**Karar: BELİRSİZ.** Ön kayıttaki yanlışlama koşulu (R² artışı <0,05) teknik olarak sağlanıyor. Ancak örneklem bunu yanlışlama saymaya yetmeyecek kadar küçük. Mevcut veri H'yi ne destekliyor ne çürütüyor. Dış şok ve para politikası (kur kaybı, negatif reel faiz: ARG, EGY) enflasyon farkını tek başına büyük ölçüde açıklıyor.

**Ters nedensellik:** Kötü sonuç (enflasyon, kur) dağılımı bozabilir. Bu tasarım yönü ayıramaz. Nedensellik iddiası yoktur.

## Yeniden çalıştırma (SAPMA-1, Drive WID paneli) — keşifsel
- Y2 = −Δüst%10 (WID) + Δemek payı (WID) − Δdolaylı pay. 10 epizod (TUR reel faiz yok, dışarıda). Dolaylı payı eksik olan epizodlarda bu terim 0 alındı.
- Enflasyon (log): H'nin ek R²'si 0,00, kısmi r −0,14. Kalite bayrağı >1 olan yıllarla (n=7): 0,01 ve −0,61.
- Faiz/gelir: ek R² 0,06, kısmi r +0,77 (H'ye ters). NPL: ek R² 0,01.
- Önceden kayıtlı kurala göre (R² artışı <0,05) H "Yanlışlandı" bölgesine kayıyor. Ancak eklenti sonuç görüldükten sonra yapıldı (doğrulayıcı değil), n küçük, Mısır 2016'daki emek payı sıçraması (+13 puan) şüpheli.
- **Karar: BELİRSİZ (H aleyhine eğilim).** Bu örneklemde dış şok ve reel faiz enflasyon farkını büyük ölçüde açıklıyor, yük dağılımı vekili belirgin bir şey eklemiyor.
