# Ülke karşılaştırması

Çalıştır: `python3 ulke_karsilastirma.py`.

Test, yerli para kâğıdının alacaklısının yerli olup olmadığıdır. Döviz sözleşmesi modelin dışında kalır. Beş adım bu ülkelerde ölçülmedi. Eşik 0,20 karşılaştırma kuralıdır. Kuralın oturduğu boşluk aşağıda ölçülmüştür.

Yazılanlar: **Japonya, Çin, Brezilya, Meksika, Polonya**.

| Ülke | Dönem | Stok | Yurt dışı | Yerli | Döviz | Yerli para | Etiket |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| Türkiye | 2025-12 | merkezi yönetim iç borç | 7.6% | 92.4% | 21.4% | 78.6% | yerli para bacağı |
| Japonya | 2026-06 | JGB + T-bill | 13.1% | 86.9% | 0.0% | 100.0% | yazılır |
| ABD | 2025-06 | Treasury | 34.0% | 66.0% | 0.0% | 100.0% | yabancı alacaklı büyük |
| Çin | 2025-12 | tahvil saklama, bütün piyasa | 1.8% | 98.2% | 0.0% | 100.0% | yazılır |
| Arjantin | 2025-12 | merkezi idare brüt borç | 34.3% | 65.7% | 57.8% | 42.2% | döviz bacağı dışarıda |
| Brezilya | 2026-08 | federal kamu borcu | 9.9% | 90.1% | 3.8% | 96.2% | yazılır |
| Almanya | 2025-12 | devlet borç kâğıdı | 57.2% | 42.8% | 0.0% | 100.0% | yabancı alacaklı büyük |
| Fransa | 2025-12 | genel yönetim uzun vadeli borç kâğıdı | 54.6% | 45.4% | 0.0% | 100.0% | yabancı alacaklı büyük |
| İtalya | 2025-12 | devlet borç kâğıdı | 31.8% | 68.2% | 0.0% | 100.0% | yabancı alacaklı büyük |
| İspanya | 2025-12 | devlet borç kâğıdı | 47.3% | 52.7% | 0.0% | 100.0% | yabancı alacaklı büyük |
| Euro alanı | 2024-Q4 | genel yönetim borcu | 23.0% | 77.0% | 0.0% | 100.0% | yabancı alacaklı büyük |
| İngiltere | 2024-09 | gilt | 32.0% | 68.0% | 0.0% | 100.0% | yabancı alacaklı büyük |
| Güney Kore | 2025-12 | hazine tahvili | 25.7% | 74.3% | 0.0% | 100.0% | yabancı alacaklı büyük |
| Meksika | 2025-12 | devlet iç kâğıdı | 11.4% | 88.6% | 0.0% | 100.0% | yazılır |
| Polonya | 2025-11 | yurt içi hazine kâğıdı | 11.7% | 88.3% | 0.0% | 100.0% | yazılır |
| Endonezya | 2025-08-11 | SBN | 14.6% | 85.4% | — | — | yerli alacaklı, döviz ayrılmadı |

## Aralık ölçümü

Durum: ölçüm. Kesit (alt, üst] aralığında kaydırıldı. İçindeki satır, iki kenarın arasına düşen paydır.

| Aralık | Genişlik | İçindeki satır | 0,20 alttan | 0,20 üstten | Etiket değişen |
| --- | ---: | ---: | ---: | ---: | ---: |
| Yurt dışı | 8,39 puan | 0 | 5,39 | 3,00 | 0 |
| Döviz | 17,66 puan | 0 | 16,25 | 1,41 | 0 |

Yurt dışı kenarları 14,6% (Endonezya, 2025-08-11) ve 23,0% (Euro alanı, 2024-Q4). Euro alanı üst kenarı kaynağın yaklaşık yüzde 23 rakamıdır. n=16.
Döviz kenarları 3,8% (Brezilya, 2026-08) ve 21,4% (Türkiye, 2025-12). Para kırılımı ölçülen satır n=3.
En geniş komşu boşluk, yurt dışında 12,99 puan (Arjantin–İspanya), dövizde 36,42 puan (Türkiye–Arjantin).

Kâğıt cinsinden konan döviz 0 bu aralığa girmez: Japonya, ABD, Çin, Almanya, Fransa, İtalya, İspanya, Euro alanı, İngiltere, Güney Kore, Meksika, Polonya.
Döviz kırılımı ayrılmayan: Endonezya.

## Satır notu

- **Türkiye** (2025-12): Yurt dışı yerleşik payı yüzde 7,6. İç borcun 1.745,8 / 8.152,8'i döviz. ROW→F 6.575 ve ROW→GY 3.131 başka stoktur, bu paydaya girmez. Kaynak: https://ms.hmb.gov.tr/uploads/2026/08/Kamu-borc-Yonetimi-Raporu-2026-2f52a814a2d37854.pdf
- **Japonya** (2026-06): Yabancı 149,9 / 1.142,0 trilyon yen. T-bill hariç JGB'de yabancı yüzde 7,9 (79,9 / 1.006,5). BOJ, JGB'nin yüzde 46,7'si. Kâğıt yen cinsidir. Kaynak: https://www.mof.go.jp/english/policy/jgbs/reference/Others/holdings01.pdf
- **ABD** (2025-06): Rapor: yabancılar Treasury'nin yüzde 34'ü. Uzun vadeli Treasury tutma 7.665 milyar dolar. Kâğıt dolar cinsidir. Kaynak: https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/shl2025r.pdf
- **Çin** (2025-12): Yurt dışı kurum saklaması 3,5 / 196,7 trilyon yuan, yüzde 1,8. Stok bütün tahvil piyasasıdır, yalnız hazine kâğıdı değildir. Kâğıt yuan cinsidir. Kaynak: http://english.people.com.cn/n3/2026/0218/c90000-20426924.html
- **Arjantin** (2025-12): Yurt dışı yerleşik 155,3 / 452,7 milyar dolar, yüzde 34,3. Döviz 261,8 / 452,7. Yerli para yüzde 42,2. Para ve yerleşim çaprazı bu iki tabloda yok. Kaynak: https://www.argentina.gob.ar/sites/default/files/deuda_publica_31-12-2025.xlsx
- **Brezilya** (2026-08): Yerleşik olmayanlar DFPD'nin yüzde 9,91'i. Dış federal borç stokun yüzde 3,75'i (348,3 milyar real, 67,2 milyar dolar). DFPD 8.944,5 milyar real. Kaynak: https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/55920_2565378/Texto_RMD_Ingles%20Aug26.pdf
- **Almanya** (2025-12): Yurt dışı = euro alanı bankası 3,5 + euro alanı banka dışı 19,4 + euro dışı 34,3. Yerli banka ve banka dışı 14,9. Basılan satırlar 72,1 eder. Kalan 27,9 kutu metninde Eurosistemdir, ayrı satır basılmadı. Kâğıt euro cinsidir. Kaynak: https://www.bde.es/f/webbe/Secciones/Publicaciones/InformesBoletinesRevistas/InformesEstabilidadFinancera/26/FSR_2026_1_Box4_2.pdf
- **Fransa** (2025-12): Yerleşik olmayanların payı yüzde 54,6. 2024 sonu yüzde 52,8. Kâğıt euro cinsidir. Kaynak: https://www.banque-france.fr/system/files/webstats/Emission_et_detention_de_titres_francais_2025T4_20260414/EN_Stat_Info_Securities_issues_by_French_residents_2025Q4.pdf
- **İtalya** (2025-12): Yurt dışı = euro alanı bankası 6,1 + euro alanı banka dışı 13,6 + euro dışı 12,1. Yerli banka 14,5, yerli banka dışı 30,7. Kâğıt euro cinsidir. Kaynak: https://www.bde.es/f/webbe/Secciones/Publicaciones/InformesBoletinesRevistas/InformesEstabilidadFinancera/26/FSR_2026_1_Box4_2.pdf
- **İspanya** (2025-12): Yurt dışı = euro alanı bankası 10,3 + euro alanı banka dışı 19,2 + euro dışı 17,8. Yerli banka 14,0, yerli banka dışı 13,8. Kâğıt euro cinsidir. Kaynak: https://www.bde.es/f/webbe/Secciones/Publicaciones/InformesBoletinesRevistas/InformesEstabilidadFinancera/26/FSR_2026_1_Box4_2.pdf
- **Euro alanı** (2024-Q4): Alan dışı yerleşikler stokun yüzde 23'ü, yaklaşık 2.600 milyar euro. Alan içi tutma bu payda yerlidir. Ülke satırlarının toplamı değildir. Kaynak: https://www.ecb.europa.eu/press/other-publications/ire/article/html/ecb.ireart202506_01~a8b7241329.en.html
- **İngiltere** (2024-09): Yurt dışı yatırımcı gilt stokunun yüzde 32'si. İngiltere Merkez Bankası APF yüzde 24. Sigorta ve emeklilik yüzde 21. Kâğıt sterlin cinsidir. Kaynak: https://www.gov.uk/government/publications/debt-management-report-2025-26/debt-management-report-2025-26-accessible
- **Güney Kore** (2025-12): Yabancı pay yüzde 25,7. Tutulan stok 297,4 trilyon won. 2024 payı yüzde 22,8. Kâğıt won cinsidir. Kaynak: https://ktb.mofe.go.kr/eng/publications.do
- **Meksika** (2025-12): Kayıtlı yerleşik pay yüzde 88,6. Kayıtlı yurt dışı pay yüzde 11,4. Not, yerleşik saklamanın bir kısmında lehtarın yabancı olabileceğini yazar. Bu satır Banxico kaydını kullanır. Kâğıt peso cinsidir. Kaynak: https://www.monex.com.mx/portal/download/reportes/260121%20Reconfiguracion%20demanda%20extranjera.pdf
- **Polonya** (2025-11): Yerleşik olmayan portföy 169,6 milyar zloti, yurt içi hazine kâğıdının yüzde 11,7'si. İhraç yeri yurt dışı olan borç, hazine borcunun yüzde 20,4'üdür ve bu paydanın dışındadır. Kâğıt zloti cinsidir. Kaynak: https://www.gov.pl/attachment/fe7a3cce-e597-4289-b09e-972d337e798e
- **Endonezya** (2025-08-11): Yabancı 938,28 / 6.420,62 trilyon rupiah, yüzde 14,6. Bank Indonesia yüzde 24,2. Ticari banka yüzde 20,3. SBN'nin döviz kırılımı bu haberde yok. Kaynak: https://premium.bisnis.com/read/20250815/664/1902826/comparing-foreign-bondholders-in-the-government-bond-sbn-during-the-eras-of-sby-jokowi-and-prabowo

## Ne denmez

- Japonya'da yen alacaklısı yabancıdır denmez. Haziran 2026'da yurt dışı payı yüzde 13,1'dir.
- Beş adım bu ülkelerde kuruldu denmez. Burada yalnız alacaklı payı vardır.
- Paylar toplanıp tek sıra yapılmaz. Stoklar ve tarihler ayrıdır.
- Eşik 0,20 ölçülmüş bir yasa denmez. Karşılaştırma kuralıdır.
- Aralık bir yasa denmez. Bu tablodaki boşluktur. Stoklar ve tarihler ayrı kalır.
- Kâğıt cinsinden konan döviz 0, döviz eşiğinin ölçümüne girmez.
