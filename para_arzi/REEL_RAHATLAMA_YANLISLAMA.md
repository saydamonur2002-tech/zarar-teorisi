# Reel rahatlama — yanlışlama ölçütü

Bu dosya hesap çalışmadan yazıldı. `reel_rahatlama.py` sayıyı ancak bu kurallarla üretir. Ölçüt değişirse json'daki `kriter_sha256` tutmaz.

Köprü adım denklemine yazılmaz. `adim3_faiz_durma.py` bu dosyayı okumaz.

## İddia

Net reel rahatlama β = 1'de bile modelin sabit tablosundan büyükse iddia ayaktadır. β = 0,5'te küçükse iddia yanlıştır.

Hüküm yalnız tanım içi ve Δπ < 0 hücrelerindedir.

- Ayakta: bu hücrelerin hepsinde net reel rahatlama (β = 1) > 0.
- Yanlış: bu hücrelerin herhangi birinde net reel rahatlama (β = 0,5) < 0. Bu kol, ayakta kolundan önce gelir.
- İkisi de değilse hüküm «ayakta değil»dir: β = 1 hücresi tabloyu geçememiştir, β = 0,5 kolu da yanlışı ilan etmemiştir.
- Δπ = 0 sapma üretmez; hükme girmez.
- Δπ > 0 enflasyonun arttığı uçtur. İddia cümlesi düşüş içindir; bu uçlar hükme girmez, tabloda durur.
- |Δπ| > 53,1925 olan hücre tanım dışıdır. Sayı yazılır, hükme girmez.

## Tanımlar

i₀ = 53,1925. **Kanıt.** `adim3_faiz_durma.py` son TP.KTF17'yi sabitler.

π₀ = 29,73. **Kanıt.** `bes_yil_senaryo.csv`, 2026-09 TÜFE.

I₀, senaryonun yıllık duran faizidir. **Kanıt** (önceki kilit): düşük 1.207,6, orta 2.415,6, yüksek 4.830,8 milyar TL. κ eşlemesi aynı kilitten: 0,25 / 0,5 / 1. Serbest κ çarpımı yazılmaz. Δπ bandının maliyet ucu zaten o satırın κ'sını taşır; ikinci bir κ, maliyeti iki kez sayar.

Δπ, `enflasyon_etki.json` içinde senaryonun 2029, 2030 ve 2031 `toplam` bandının iki ucudur. **Aday.** Kredi hariç bant hükme girmez.

β ∈ {0; 0,5; 1}.

İşaretli Fisher: i(β) = i₀ + β·Δπ. Δπ < 0 iken bu, i₀ − β·|Δπ| ile aynıdır. Δπ > 0 iken faiz artar. Her iki uca eksi mutlak değer yazmak, enflasyon artarken faizi düşürür; o kural kullanılmaz.

Alt sınır 0'dır: i(β) = max(0, i₀ + β·Δπ).

Gerekçe. Tam Fisher reel oranı i₀ − π₀ = 23,4625 puanda tutar. Bu oran 0'ın üzerindedir. «Reel faiz ≥ 0» tabanı Fisher yolunda bağlayıcı değildir. «Reel oranın kendisini nominal taban yapmak» (i ≥ 23,4625) ise yeni enflasyon eksiye inince reel oranı 23,4625'in üzerine çıkarır; bu tam Fisher değildir. Bağlayan sınır, ticari oranın 0'ın altına yazılmamasıdır. TP.KTF17 eksi gözlenmez. Modelde eksi faiz kuralı yoktur.

I(β) = I₀ · i(β) / i₀. **Aday.** Formül I = ψ·(r/4)·D, ψ ve D sabitken doğrusaldır. ψ ve D'nin faiz düşünce durduğu ölçülmedi.

(a) nominal duran faiz = I(β).

(b) nominal fazlalık = I₀ − I(β). Sabit tablonun, uyumlu nominalden büyük kalan kısmı. β = 0'da 0.

(c) reel değer = I(β) / (1 + (π₀ + Δπ) / 100). Bir yıllık akış, o yılın fiyat çarpanı. Üç yıl bileşiklenmez.

(d) net reel rahatlama = (c) − I₀ / (1 + π₀ / 100). Modelin sabit-fiyat reel değeri, sabit nominalin π₀ ile bir yıl indirgenmesidir.

Fiyat çarpanı 0'ın altına inerse hücre boş kalır, sayı uydurulmaz.

Etiket: i₀, π₀, I₀ kanıt. β, taban ve net rahatlama aday.
