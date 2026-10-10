# Sonraki koşu promptu (Tur 14)

Firma haznesi 150 alt düğüm. Toplam TCMB 2026-Q1 mevduat, kredi stoku ve aylık servis sabit. Kenar yükümlülüğün alacaklı varlık payına bölünmesi. Girdi-çıktı ve çekilmemiş limit serisi yok. Monte Carlo 50, tohum 20261010+14000.

## Bağlam

- Lider = en yüksek mevduatlı sentetik düğüm. TCMB sektör toplamının bölünmesi. Resmi kaynakta isimli karşılığı yok. Bu turda isim aranmaz.
- Tur 13: faiz gecikme (α) sistemik kalıcılığı artırmadı. Elendi.
- Tur 7: mevduat + servis birlikte 0,70 iken sistemik bloke çıktı. Servis eşitken çıkmadı.

## Test

1. Servis konsantrasyonu bağlayıcı mı.
   - Mevduat üst %10 sabit 0,70.
   - Servis üst %10: 0,10 / 0,30 / 0,50 / 0,70.
   - FX çevrilebilir ve çevrilemez ayrı.
   - Ölç: sistemik kalıcılık, küçük yavaş, yerel bloke, reel kayıp.

2. Servis eşit, mevduat değişken (kontrol).
   - Servis eşit.
   - Mevduat üst %10: 0,10 / 0,40 / 0,70.
   - Aynı ölçümler.

3. Lider düğümün servis payını sıfırla (mevduatı yerinde).
   - Mev 0,70 + servis 0,70 hücresinde liderin servisini kalanlara eşit dağıt.
   - Kalıcılık farkı (lider servis var − lider servis sıfır).

## Çürütme

- Servis payı 0,10’dan 0,70’e çıkarken kalıcılık artmıyorsa (medyan fark < 2, p > 0,05) “servis konsantrasyonu bağlayıcı” elenir.
- Liderin servisi sıfırlanınca kalıcılık düşmüyorsa “tek düğüm servisi belirliyor” elenir.
- Mevduat tek başına (servis eşit) kalıcılık üretmiyorsa önceki tur tekrarlıyor.

## Rapor

- Her hücrede kalıcılık, küçük yavaş, yerel bloke, reel kayıp.
- Spearman: servis payı – kalıcılık, mevduat payı – kalıcılık.
- Lider servis sıfır farkı ve p.
- Varsayımlar ve tekrar komutu `ODEME_ZINCIRI.md` başına. Ağ ve toplamlar önceki turla aynı.
