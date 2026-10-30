# Mefan, MFİN değil

Bu dizin, Origin deposu [g-l-mse/git-harm](https://cursor.com/codebase/g-l-mse/git-harm) anlık görüntüsünün bu repodaki kopyasıdır. Depo özeldir. Commit `204fc7c` buradan doğrulanamadı; bkz. `../KAYNAKLAR.md`.

Bu kopyada Next.js uygulaması, `package.json` ve `npm run dev` yoktur. Yukarı akıştaki arayüz anlık görüntüye girmemiştir. Burada çalışan parça `scripts/mfin_maliyet.py` betiğidir; sayı dosyaları `data/` altındadır.

`saydamonur2002-tech/zarar-teorisi` deposunun `cursor/odeme-zinciri-kalicilik-f01a` dalındaki okuma. “Mefan” adını merkez finans aktörü MFİN sanmak yanlış: dosyalarda Mefa / Mefan / Mefon geçmiyor. MFİN, metnin tanımladığı merkez finans vekili.

Belirsiz kesim ayrı: `merkez_belirsiz`, kimliği yazılmayan merkez sızıntısının 36 ülkeye eşit payı.

## MFİN maliyeti

```bash
python3 scripts/mfin_maliyet.py
```

Betik, daldaki formülle sürdürme maliyetini hesaplar: `round(0,20 × pol × kazanç, 3)`. Çıktı yayın tablosundaki 1,096 / 1,438 / 0,744 ile aynıdır. Ardından üç dolar köprüsünü uygular (2.589,12 / 4.785 / 5.383 milyon dolar bölü vekil).

Aynı komut geriye hesabı da yazar. Kazanç, Eylül 2016 – Ağustos 2026 net yatırım geliri ödemesidir (130,4 milyar dolar). Kayıp ve maliyet, ileri defterdeki oranlarla bu kazançtan düşülür. Nokta netler: A +54,7 ±103,2, B +30,3 ±139,1, C +63,1 ±88,0 milyar dolar. Üç bant da sıfırı örter. Sayılar `data/geriye.json` dosyasına yazılır.

İşaretin κ, pol ve dolar köprüsüyle nasıl değiştiği `scripts/isaret_duyarlilik.py` ve `ISARET_DUYARLILIK.md` içindedir. Betik model sayısını değiştirmez.

## Dosyalar

| Dosya | Ne |
| --- | --- |
| `data/evds_odeme_dengesi_aylik.csv` | Aylık yatırım geliri gideri ve geliri |
| `data/geriye.json` | Betiğin yazdığı geçmiş on yıl |
| `data/geri_kalan.json` | Havuzdaki Türkiye dilimi ve havza satırı olmayan kaybedenler |
| `data/havza_kayip.json` | Otuz kaybeden havzanın neti. Kaynak alan `PROJEKSIYON.json bolgesel_net` |
| `scripts/mfin_maliyet.py` | Maliyet, köprü ve geriye hesabı |
| `scripts/isaret_duyarlilik.py` | İşaret duyarlılığı |

`havza_kayip.json` içindeki bölgesel net, `etki_cephesi/data/PROJEKSIYON.json` dosyasındaki `bolgesel_net.net_endeks` ile aynıdır. İleri senaryo tabloları bu repoda `yayin/KAZANC_KAYIP_MUHASEBE.md` ve `yayin/SENARYO_KARSILASTIRMA.md` altındadır.
