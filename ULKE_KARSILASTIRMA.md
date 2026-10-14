# Ülke karşılaştırması

Çalıştır: `python3 ulke_karsilastirma.py`.

Test, yerli para kâğıdının alacaklısının yerli olup olmadığıdır. Döviz sözleşmesi modelin dışında kalır. Beş adım bu ülkelerde ölçülmedi. Eşik 0,20 karşılaştırma kuralıdır.

Yazılanlar: **Japonya, Çin, Brezilya**.

| Ülke | Dönem | Stok | Yurt dışı | Yerli | Döviz | Yerli para | Etiket |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| Türkiye | 2025-12 | merkezi yönetim iç borç | 7.6% | 92.4% | 21.4% | 78.6% | yerli para bacağı |
| Japonya | 2026-06 | JGB + T-bill | 13.1% | 86.9% | 0.0% | 100.0% | yazılır |
| ABD | 2025-06 | Treasury | 34.0% | 66.0% | 0.0% | 100.0% | yabancı alacaklı büyük |
| Çin | 2025-12 | tahvil saklama, bütün piyasa | 1.8% | 98.2% | 0.0% | 100.0% | yazılır |
| Arjantin | 2025-12 | merkezi idare brüt borç | 34.3% | 65.7% | 57.8% | 42.2% | döviz bacağı dışarıda |
| Brezilya | 2026-08 | federal kamu borcu | 9.9% | 90.1% | 3.8% | 96.2% | yazılır |

## Satır notu

- **Türkiye** (2025-12): Yurt dışı yerleşik payı yüzde 7,6. İç borcun 1.745,8 / 8.152,8'i döviz. ROW→F 6.575 ve ROW→GY 3.131 başka stoktur, bu paydaya girmez. Kaynak: https://ms.hmb.gov.tr/uploads/2026/08/Kamu-borc-Yonetimi-Raporu-2026-2f52a814a2d37854.pdf
- **Japonya** (2026-06): Yabancı 149,9 / 1.142,0 trilyon yen. T-bill hariç JGB'de yabancı yüzde 7,9 (79,9 / 1.006,5). BOJ, JGB'nin yüzde 46,7'si. Kâğıt yen cinsidir. Kaynak: https://www.mof.go.jp/english/policy/jgbs/reference/Others/holdings01.pdf
- **ABD** (2025-06): Rapor: yabancılar Treasury'nin yüzde 34'ü. Uzun vadeli Treasury tutma 7.665 milyar dolar. Kâğıt dolar cinsidir. Kaynak: https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/shl2025r.pdf
- **Çin** (2025-12): Yurt dışı kurum saklaması 3,5 / 196,7 trilyon yuan, yüzde 1,8. Stok bütün tahvil piyasasıdır, yalnız hazine kâğıdı değildir. Kâğıt yuan cinsidir. Kaynak: http://english.people.com.cn/n3/2026/0218/c90000-20426924.html
- **Arjantin** (2025-12): Yurt dışı yerleşik 155,3 / 452,7 milyar dolar, yüzde 34,3. Döviz 261,8 / 452,7. Yerli para yüzde 42,2. Para ve yerleşim çaprazı bu iki tabloda yok. Kaynak: https://www.argentina.gob.ar/sites/default/files/deuda_publica_31-12-2025.xlsx
- **Brezilya** (2026-08): Yerleşik olmayanlar DFPD'nin yüzde 9,91'i. Dış federal borç stokun yüzde 3,75'i (348,3 milyar real, 67,2 milyar dolar). DFPD 8.944,5 milyar real. Kaynak: https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/55920_2565378/Texto_RMD_Ingles%20Aug26.pdf

## Ne denmez

- Japonya'da yen alacaklısı yabancıdır denmez. Haziran 2026'da yurt dışı payı yüzde 13,1'dir.
- Beş adım bu ülkelerde kuruldu denmez. Burada yalnız alacaklı payı vardır.
- Paylar toplanıp tek sıra yapılmaz. Stoklar ve tarihler ayrıdır.
- Eşik 0,20 ölçülmüş bir yasa denmez. Karşılaştırma kuralıdır.
