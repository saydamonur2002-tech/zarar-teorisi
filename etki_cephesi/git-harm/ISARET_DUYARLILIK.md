# Geriye netinin işareti

`data/geriye.json` üç senaryoda nokta neti artı yazar ve bant sıfırı örter. Bu not model sayısını değiştirmez. Formül `scripts/mfin_maliyet.py` ile aynıdır. Yenilemek, bu dizinden: `python3 scripts/isaret_duyarlilik.py`.

Kazanç gözlenen net yatırım geliridir (dosyada 130392.0 mn $, 2016-09 – 2026-08). Kayıp ve maliyet, ileri defterdeki oranlarla bu kazançtan düşülür. Oran kazançla ölçeklendiği için işaret, on yıllık toplamda da yıl dilimlerinde de aynıdır.

## Yayımlanan dosya

| Senaryo | pol | net mn $ | bant | alt | üst | aralık |
| --- | --- | --- | --- | --- | --- | --- |
| A | 0.70 | 54731.3 | 103213.1 | -48481.8 | 157944.4 | sıfırı örter |
| B | 0.41 | 30264.0 | 139094.7 | -108830.7 | 169358.7 | sıfırı örter |
| C | 0.95 | 63052.1 | 88001.4 | -24949.3 | 151053.5 | sıfırı örter |

Nokta formülü `net = kazanç − kayıp − κ × pol × kazanç`, κ = 0,20. Bant, kayıp vekilinin belirsizliği ile κ bandının (0,10–0,35) yarı genişliğinden gelen maliyet belirsizliğinin karekök toplamıdır. Maliyet belirsizliği seçilen κ'ya değil, bandın genişliğine bağlıdır.

## Nokta işareti

Nokta net, `κ × pol < 1 − kayıp/kazanç` iken artıdır. Yayımlanan pol'de bu eşiğin altındaki her κ noktayı artı bırakır. κ = 0,20 iken noktayı eksiye çeken pol, üç senaryoda da 1'in üstündedir; pol 0 ile 1 arasında noktayı çevirmez.

| Senaryo | yayımlanan pol | noktayı sıfırlayan κ | κ=0,20 iken noktayı sıfırlayan pol |
| --- | --- | --- | --- |
| A | 0.70 | 0.800 | 2.799 |
| B | 0.41 | 0.766 | 1.571 |
| C | 0.95 | 0.709 | 3.368 |

κ bandının tavanı 0,35, üç eşiğin de altındadır. Bant içindeki κ nokta işaretini değiştirmez.

| κ | A nokta; aralık | B nokta; aralık | C nokta; aralık |
| --- | --- | --- | --- |
| 0.00 | artı; sıfırı örter | artı; sıfırı örter | artı; sıfırı örter |
| 0.10 | artı; sıfırı örter | artı; sıfırı örter | artı; sıfırı örter |
| 0.20 | artı; sıfırı örter | artı; sıfırı örter | artı; sıfırı örter |
| 0.35 | artı; sıfırı örter | artı; sıfırı örter | artı; sıfırı örter |
| 0.50 | artı; sıfırı örter | artı; sıfırı örter | artı; sıfırı örter |
| 0.70 | artı; sıfırı örter | artı; sıfırı örter | artı; sıfırı örter |
| 1.00 | eksi; sıfırı örter | eksi; sıfırı örter | eksi; sıfırı örter |

pol taraması κ'yı 0,20'de tutar. Aralık sütunu yayımlanan belirsizlik formülünü o pol'e taşır.

| pol | A nokta; aralık | B nokta; aralık | C nokta; aralık |
| --- | --- | --- | --- |
| 0.00 | artı; sıfırı örter | artı; sıfırı örter | artı; yalnız artı |
| 0.41 | artı; sıfırı örter | artı; sıfırı örter | artı; sıfırı örter |
| 0.70 | artı; sıfırı örter | artı; sıfırı örter | artı; sıfırı örter |
| 0.95 | artı; sıfırı örter | artı; sıfırı örter | artı; sıfırı örter |
| 1.00 | artı; sıfırı örter | artı; sıfırı örter | artı; sıfırı örter |

## Aralığın sıfırı örtmesi

Aralığı genişleten terim kayıp belirsizliğidir. A ve B'de bu terim, sürdürme maliyeti sıfır olsa bile (κ = 0) netten büyüktür; aralık sıfırı örter. C'de kayıp belirsizliği κ = 0 netinden küçüktür. Yayımlanan pol'de (0,95) maliyet belirsizliği eklenince C de sıfırı örter. pol = 0 iken maliyet belirsizliği kalkar ve C'nin aralığı yalnız artı kalır; A ve B gene sıfırı örter.

| Senaryo | kayıp bel / kazanç | maliyet bel / kazanç | bant / kazanç | κ=0 net / kazanç | κ=0 aralık |
| --- | --- | --- | --- | --- | --- |
| A | 0.7867 | 0.0875 | 0.7916 | 0.5597 | sıfırı örter |
| B | 1.0655 | 0.0513 | 1.0667 | 0.3141 | sıfırı örter |
| C | 0.6644 | 0.1188 | 0.6749 | 0.6736 | sıfırı örter |

## Dolar köprüsü

Üç köprü (BoP 2589.12, mal 4785, rant 5383 mn $ / vekil) pozitif ölçektir. Vekili `köprü / 1000` ile çarpar. İşareti ve aralığın sıfırı örtüp örtmediğini değiştirmez; yalnız dolar büyüklüğünü yaklaşık iki kat oynatır.

`geriye.json` bu köprüyü kullanmaz. Geriye net, gözlenen milyon doların oranıdır. Köprü seçimi o dosyadaki işarete girmez. Aşağıdaki tablo ileri vekil netin dolar karşılığıdır.

| Senaryo | net vekil | bant vekil | net BoP | net mal | net rant |
| --- | --- | --- | --- | --- | --- |
| A | 3.284 | 6.194 | 8.50 | 15.71 | 17.68 |
| B | 4.071 | 18.710 | 10.54 | 19.48 | 21.91 |
| C | 1.895 | 2.644 | 4.91 | 9.07 | 10.20 |

| Senaryo | BoP aralık | mal aralık | rant aralık |
| --- | --- | --- | --- |
| A | sıfırı örter | sıfırı örter | sıfırı örter |
| B | sıfırı örter | sıfırı örter | sıfırı örter |
| C | sıfırı örter | sıfırı örter | sıfırı örter |

## Okuma

Yayımlanan κ ve pol nokta neti artı bırakır. Üç bandın sıfırı örtmesi, noktanın eksi olmasından gelmez; kayıp vekiline yazılan belirsizlik netten büyüktür. Dolar köprüsü bu hükmü değiştirmez.
