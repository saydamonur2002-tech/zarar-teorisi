# Ülke modeli denemesi

Çalıştır: `python3 ulke_model_dene.py`.

Ayrı dosyadır. Türkiye faiz faturası çağrılmaz. Beş adım kurulmaz. Kupon ve fatura boştur.

Yerli alacaklı stoku yazılan: **6**. Fatura hesaplanan: **0**.

| Ülke | Dönem | Birim | Etiket | Stok | Yerli alacaklı | Yurt dışı | Döviz | Yazılan | Durum |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Türkiye | 2025-12 | milyar TL | yerli_para_bacagi | 8.152,8 | 7.533,2 | 619,6 | 1.745,8 | — | capraz_yok |
| Japonya | 2026-06 | trilyon yen | yazilir | 1.142,0 | 992,1 | 149,9 | — | 992,1 | yazildi |
| ABD | 2025-06 | — | yabanci_alacakli_buyuk | — | — | — | — | — | stok_yok |
| Çin | 2025-12 | trilyon yuan | yazilir | 196,7 | 193,2 | 3,5 | — | 193,2 | yazildi |
| Arjantin | 2025-12 | milyar dolar | doviz_bacagi_disarida | 452,7 | 297,3 | 155,3 | 261,8 | — | capraz_yok |
| Brezilya | 2026-08 | milyar real | yazilir | 8.944,5 | 8.058,1 | 886,4 | — | 8.058,1 | yazildi |
| Almanya | 2025-12 | — | yabanci_alacakli_buyuk | — | — | — | — | — | stok_yok |
| Fransa | 2025-12 | — | yabanci_alacakli_buyuk | — | — | — | — | — | stok_yok |
| İtalya | 2025-12 | — | yabanci_alacakli_buyuk | — | — | — | — | — | stok_yok |
| İspanya | 2025-12 | — | yabanci_alacakli_buyuk | — | — | — | — | — | stok_yok |
| Euro alanı | 2024-Q4 | milyar euro | yabanci_alacakli_buyuk | 11.304,3 | 8.704,3 | 2.600,0 | — | 8.704,3 | yazildi |
| İngiltere | 2024-09 | — | yabanci_alacakli_buyuk | — | — | — | — | — | stok_yok |
| Güney Kore | 2025-12 | trilyon won | yabanci_alacakli_buyuk | 1.157,2 | 859,8 | 297,4 | — | 859,8 | yazildi |
| Meksika | 2025-12 | — | yazilir | — | — | — | — | — | stok_yok |
| Polonya | 2025-11 | milyar zloti | yazilir | 1.449,6 | 1.280,0 | 169,6 | — | 1.280,0 | yazildi |
| Endonezya | 2025-08-11 | trilyon rupiah | yerli_alacakli_doviz_ayrilmadi | 6.420,6 | 5.482,3 | 938,3 | — | — | doviz_ayrilmadi |

Yazılan, yerli alacaklı sütunudur. Para kırılımı ile yerleşim çaprazı olmayan satırda bu hücre boştur.
Brezilya'da döviz sütunu boştur. Dış federal borç 348,3 milyar real, ayrı stoktur ve yazılana girmez.
Euro alanı stoku, yaklaşık 2.600 milyar euro ve yaklaşık yüzde 23 payından türer.
Güney Kore ve Polonya stoku, yayımlanan yurt dışı düzey ile paydan türer.
λ=1 satırında fark 0'dır. Bu, yazılan stokun adını değiştirir. Faturayı hesaplamaz.

## Ne denmez

- Fatura durdu denmez. Kupon bu dosyada yoktur.
- Beş adım bu ülkelerde kuruldu denmez.
- Satırlar toplanmaz. Birimler ve tarihler ayrıdır.
- Kâğıt cinsi, ölçülmüş döviz stoku 0 diye yazılmaz.
