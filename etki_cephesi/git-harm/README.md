# Mefan, MFİN değil

Depo: [g-l-mse/git-harm](https://cursor.com/codebase/g-l-mse/git-harm). Görünürlük özel. Bunu o sayfadaki ayarlardan değiştirebilirsin.

Makineye almak için:

```bash
# Install the Origin CLI
curl -fsSL https://downloads.cursor.com/origin/install.sh | sh

# Sign in (also sets up git credentials)
origin auth login

# Clone the repository
origin repo clone g-l-mse/git-harm
```

Kurulumdan sonra `origin` bulunamazsa `~/.local/bin` yolunu kalıcı ekle:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Origin CLI belgeleri: https://cursor.com/docs/origin/cli

`saydamonur2002-tech/zarar-teorisi` deposunun `cursor/odeme-zinciri-kalicilik-f01a` dalındaki okuma. “Mefan” adını merkez finans aktörü MFİN sanmak yanlış: dosyalarda Mefa / Mefan / Mefon geçmiyor. MFİN, metnin tanımladığı merkez finans vekili.

Belirsiz kesim ayrı: `merkez_belirsiz`, kimliği yazılmayan merkez sızıntısının 36 ülkeye eşit payı.

## MFİN maliyeti

```bash
python3 scripts/mfin_maliyet.py
```

Betik, daldaki formülle sürdürme maliyetini hesaplar: `round(0,20 × pol × kazanç, 3)`. Çıktı yayın tablosundaki 1,096 / 1,438 / 0,744 ile aynıdır. Ardından üç dolar köprüsünü uygular (2.589,12 / 4.785 / 5.383 milyon dolar bölü vekil).

Aynı komut geriye hesabı da yazar. Kazanç, Eylül 2016 – Ağustos 2026 net yatırım geliri ödemesidir (130,4 milyar dolar). Kayıp ve maliyet, ileri defterdeki oranlarla bu kazançtan düşülür. Nokta netler: A +54,7 ±103,2, B +30,3 ±139,1, C +63,1 ±88,0 milyar dolar. Üç bant da sıfırı örter. Sayılar `src/data/geriye.json` dosyasına yazılır; sayfa oradan okur.

## Çalıştırma

```bash
npm install
npm run dev
```

Uygulama [http://127.0.0.1:43123](http://127.0.0.1:43123) adresinde açılır. `/kesim` dosya kesimi, `/kesim#havza-kayip` otuz kaybeden havzanın net payı, `/kesim#geri-kalan` havuzun Türkiye dilimi ve havza satırı olmayan kaybedenler, `/kesim#senaryolar` A, B, C ve D’nin bağı, `/kesim#veri` geçmiş on yılın seriye ne yazdığı, `/kesim#senaryo-d` C üzerine durdurma taraması, `/tahvil` 2021 Hazine ihraçlarının hesap dağılımı. MFİN bu ihraçlarda bir alıcı adı olarak geçmez; kupon, geriye hesaptaki yatırım geliri giderinin içindedir.

Sayılar bu dalın `yayin/ETKI_CEPHESI_REVIZE.md` dosyasından. `main` dalında bu dosya yok.
