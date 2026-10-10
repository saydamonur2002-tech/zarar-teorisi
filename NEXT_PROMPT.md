# Sonraki koşu promptu

Firma haznesi 150 alt düğüm. Toplam TCMB 2026-Q1 mevduat, kredi stoku ve aylık servis sabit. Kenar yükümlülüğün alacaklı varlık payına bölünmesi (önceki turla aynı). Girdi-çıktı ve çekilmemiş limit serisi yok. Monte Carlo 50, tohum 20261010+11000.

Önceki turda: mevduat üst %10’da 0,70, servis eşit → sistemik bloke 0, küçük yavaşlık 0,177. Servis+alacak mevduatla dağılınca yavaşlık yok.

## Bu turda test

1. Servis de konsantre. Üst %10’un borç servisi payı 0,10 / 0,40 / 0,70. Mevduat payı aynı üç değer. 3×3 hücre. FX çevrilemez ve çevrilebilir ayrı.
2. Alacak (kenar) de konsantre. Üst %10’un alacak payı 0,10 / 0,40 / 0,70. Servis eşit ve servis konsantre ayrı.
3. Çizgi (varsayılmış bir aylık) sadece üst %10’a açık / sadece alt yarıya açık / herkese açık. Servis eşit.
4. Sistem sayacı aynı (%25). Ek sayac: küçük düğümlerin (alt yarı) yavaş payı ≥ 0,40 olunca “yerel bloke” işaretle. Sistemik ve yerel ayrı raporla.

## Rapor

- Her hücrede ortalama kalıcılık, bloke periyot, küçük yavaş pay, reel kayıp oranı (FX çevrilemezken).
- Üst %10 payı arttıkça küçük yavaşlık ve reel kayıp nasıl değişiyor (Spearman).
- Servis konsantre olunca sistemik bloke çıkıyor mu, yoksa yine sadece yerel mi.
- Alacak konsantre olunca küçük düğümlerin alacak payı düşüyor mu, reel kayıp payı artıyor mu (5 puan eşiği).
- Çizgi kime açık olursa sistemik veya yerel bloke değişiyor mu.

Varsayımlar ve tekrar komutu `ODEME_ZINCIRI.md` başına. Ağ ve toplamlar önceki turla aynı.
