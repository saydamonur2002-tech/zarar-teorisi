# Fisher ayrışması: adım 3 ve adım 4

Çalıştır: `python3 fisher_ayrisma.py`. Çıktı: `fisher_ayrisma.csv`, `fisher_ayrisma_adim3.csv`, `fisher_ayrisma_adim4.csv`, `fisher_ayrisma_sonuc.json`.

Mevcut hiçbir dosya değişmedi: `adim3*.csv`, `rev_adim3*`, `adim4*.csv` olduğu gibi durur. Burası bir ayrıştırma, yeni bir kural değil.

## İki denklem

- **Fisher ilişkisi:** `(1+i) = (1+r)(1+π)`. Nominal birimde `i = π + r(1+π)`: enflasyon telafisi artı reel getiri. `i − π` reel faiz değil, reel faizin nominal ifadesidir; fark çapraz terim `r·π`.
- **Uluslararası Fisher:** `(1+i_TL)/(1+i_YP) = beklenen USD/TRY artışı`. Faiz farkının ima ettiği değer kaybı.

## Güncel durum (2026-09, `olcum_turevi`)

TÜFE yıllık 29.73% (`bes_yil_senaryo taban`). Eşleşen ay, aynı tarih.

| Faiz | Nominal | Reel (tam) | i − π | Çapraz r·π | Enflasyon payı |
| --- | ---: | ---: | ---: | ---: | ---: |
| Ticari kredi TL (TP.KTF17) | 53.19 | 18.09 | 23.46 | 5.38 | %56 |
| Politika (AOFM) | 37.00 | 5.61 | 7.27 | 1.67 | %80 |

Tarihsel eşleşen reel kredi faizi (2011-01 → 2026-09, n=182): medyan 4.24, p10 -16.44, p90 8.75, min -36.77 (2022-11), max 20.84 (2025-06); ayların %21'inde negatif. Bugünkü 18.1% tarihsel p90 (8.75) üstünde.

## Uluslararası Fisher

| Ölçü | Yıllık % |
| --- | ---: |
| Faiz farkının ima ettiği değer kaybı (2026-09, TL kredi / USD kredi: 53.19 / 8.13) | 41.7 |
| Stok faizlerinden ima edilen (TP.BKR.TRY.1 / USD.1, 2026-08) | 36.3 |
| Anket beklentisi (USD/TRY 12 ay sonrası, `varsayim`) | 19.3 |
| Gerçekleşen, son 12 ay | 17.7 |
| YP kredinin TL maliyeti, anket kuruyla | 29.0 |
| YP kredinin TL maliyeti, gerçekleşen kurla | 27.3 |
| TL kredi faizi (karşılaştırma) | 53.2 |

Bir yıl önce (2025-09) ima edilen 43.6%, sonraki 12 ayda gerçekleşen 17.7%.
Tüm örneklem (2010-01 → 2025-09, n=189): ima edilen ortalama 15.07, gerçekleşen ortalama 25.91; Pearson korelasyonu 0.0003, sıra korelasyonu 0.228; gerçekleşen değer kaybının ima edileni aştığı ay oranı %68; YP kredi, gerçekleşen kurla TL krediden pahalı çıkan ay oranı %68. Son 60 ayda ima 26.8, gerçekleşen 43.64, YP pahalı oranı %58.

**Okuma:** son 12 ay bir istisna: faiz farkı %42 değer kaybı ima ederken gerçekleşen %18 kaldı, YP borç TL borçtan çok daha ucuz çıktı. Tüm örneklemde tersi: gerçekleşen değer kaybı ortalamada ima edileni aştı ve YP kredi ayların %68'inde TL krediden pahalıydı. Pearson korelasyonu sıfıra yakın çünkü 2021-2023'ün birkaç uç değeri (gerçekleşen %100'ü aşan) hesabı domine eder; sıra korelasyonu zayıf pozitif.

## Adım 3: duran faizin ayrışması

`rev_adim3.csv` TL ve YP parçasına yeniden kuruldu (YP payı 0.5444, TL stok faizi 46.79, USD 7.71); toplam `I_sozlesme` ile en büyük mutlak fark 1.251 milyar TL (en büyük stok satırı; YP payı `rev_adim3_sonuc.json`'da 4 haneye yuvarlı), en büyük göreli fark %0.0356 (küçük satırlarda `I`'nın 0,1'e yuvarlanması). TL parçasında enflasyon telafisi = D·(1−YP payı)·π/4, geri kalanı reel getiri.

Enflasyon yolu (yıl sonu yıllık TÜFE, `varsayim`): anket 2026: 29.6, 2027: 22.7, 2028: 18.3, 2029: 16.2, 2030: 14.2, 2031: 12.1; alt 2026: 29.6, 2027: 15.1, 2028: 10.7, 2029: 8.6, 2030: 6.5, 2031: 4.5. 2029-2030 anket yıllarının doğrusal ara değeri.

κ = 1, g = medyan (milyar TL/yıl):

| r | Yıl | Duran faiz | TL parçası | YP parçası | Enflasyon telafisi (anket) | Reel getiri (anket) | Enflasyon payı, anket / alt |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| dusus | 2029 | 12,617.6 | 9,652.9 | 2,964.3 | 5,226.5 | 4,426.4 | %54 / %29 |
| dusus | 2031 | 24,250.3 | 18,552.1 | 5,697.2 | 7,476.5 | 11,075.6 | %40 / %15 |
| sabit | 2029 | 18,020.5 | 15,055.3 | 2,964.3 | 5,226.5 | 9,828.8 | %35 / %18 |
| sabit | 2031 | 34,634.1 | 28,935.2 | 5,697.2 | 7,476.5 | 21,458.6 | %26 / %10 |
| yuksek | 2029 | 20,662.3 | 17,696.9 | 2,964.3 | 5,226.5 | 12,470.4 | %30 / %16 |
| yuksek | 2031 | 39,711.7 | 34,012.3 | 5,697.2 | 7,476.5 | 26,535.7 | %22 / %8 |

**Fisher tutarlılığı:** senaryo TL faizi ile anket enflasyonundan ima edilen reel faiz, tarihsel eşleşen reel stok faizi (p90 6.34, max 13.13, 2012-07 → 2026-01) ile karşılaştırıldı:

| r | Yıl | TL faiz (stok, ort.) | Anket π | Reel (tam) | Alt π | Reel (tam) | π bugünkü düzeyde (29.7) | Reel (tam) | Max aşıldı: anket / alt / bugün |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| dusus | 2027 | 40.3 | 22.7 | 14.3 | 15.1 | 21.9 | 29.7 | 8.1 | evet / evet / hayır |
| dusus | 2029 | 30.0 | 16.2 | 11.8 | 8.6 | 19.7 | 29.7 | 0.2 | hayır / evet / hayır |
| dusus | 2031 | 30.0 | 12.1 | 16.0 | 4.5 | 24.4 | 29.7 | 0.2 | evet / evet / hayır |
| sabit | 2027 | 46.8 | 22.7 | 19.6 | 15.1 | 27.6 | 29.7 | 13.2 | evet / evet / evet |
| sabit | 2029 | 46.8 | 16.2 | 26.3 | 8.6 | 35.1 | 29.7 | 13.2 | evet / evet / evet |
| sabit | 2031 | 46.8 | 12.1 | 31.0 | 4.5 | 40.5 | 29.7 | 13.2 | evet / evet / evet |
| yuksek | 2027 | 55.0 | 22.7 | 26.3 | 15.1 | 34.7 | 29.7 | 19.5 | evet / evet / evet |
| yuksek | 2029 | 55.0 | 16.2 | 33.3 | 8.6 | 42.7 | 29.7 | 19.5 | evet / evet / evet |
| yuksek | 2031 | 55.0 | 12.1 | 38.3 | 4.5 | 48.4 | 29.7 | 19.5 | evet / evet / evet |

15 (r, yıl) kombinasyonunun 13'i anket enflasyonuyla, 10'i enflasyon bugünkü düzeyde kalırsa tarihsel maksimum reel faizi (13.13) aşıyor. Enflasyon bugünkü düzeyde kalırsa 2029 reel faizi (tam): `dusus` 0.2 (aralıkta), `sabit` 13.2 (aşıyor), `yuksek` 19.5 (aşıyor). **Okuma:** nominal faiz yolu ile enflasyon yolu birlikte seçilmeli. Anket dezenflasyonuyla eşleşince `sabit` ve `yuksek` yolları tarihsel maksimumun 1.5-2.9 katı reel faiz ima eder; ayrı ayrı gezmek Fisher açısından tutarsız kombinasyonlar üretir.

Stok büyümesi `g` için gerekli reel (kur değerlemesi dahil) büyüme, yıllık nominal `g` ile anket enflasyonundan:

| g | Yıllık nominal % | 2027 | 2028 | 2029 | 2030 | 2031 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| sifir | 0.0 | -18.5 | -15.5 | -14.0 | -12.4 | -10.8 |
| medyan | 38.6 | 13.0 | 17.2 | 19.3 | 21.4 | 23.7 |
| min | 20.9 | -1.5 | 2.1 | 4.0 | 5.9 | 7.8 |
| max | 58.0 | 28.8 | 33.6 | 35.9 | 38.4 | 41.0 |

## Adım 4: endeks bacağı

`adim4_adres_yonlendirme.csv` `endeks_bacagi` sütunu "hesaplanmadı" diyordu. Burada Fisher ile doldurulur: nominal getiri = π + reel kupon; HEKİS senedinde reel kupon 0 (`BES_ADIM.md`), yani endeks bacağı = başlangıç stoku × π / 4 (prim ile aynı kural). **Endeks = TÜFE varsayımı;** hedef endeks TÜFE değilse geçersiz.

| θ | χ | prim % | Yıl | Prim | Endeks (anket π) | Endeks / prim | Endeks (alt π) | Endeks / prim |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.1 | 0.0 | 0.02 | 2030 | 38.8 | 274.3 | 7.07× | 126.8 | 3.27× |
| 0.1 | 0.0 | 0.05 | 2030 | 96.8 | 274.3 | 2.83× | 126.8 | 1.31× |
| 0.25 | 0.0 | 0.02 | 2030 | 96.8 | 685.7 | 7.08× | 316.9 | 3.27× |
| 0.25 | 0.0 | 0.05 | 2030 | 242.0 | 685.7 | 2.83× | 316.9 | 1.31× |
| 0.5 | 0.0 | 0.02 | 2030 | 193.6 | 1,371.5 | 7.08× | 633.8 | 3.27× |
| 0.5 | 0.0 | 0.05 | 2030 | 484.0 | 1,371.5 | 2.83× | 633.8 | 1.31× |

## Eleştirel notlar

1. Enflasyon yolu anket beklentisidir (yıl sonu, yıllık); yıl içi dalgalanma ve 2029-2030 ara değeri varsayım. Fisher beklenen enflasyona dayanır; tarihsel tabloda gerçekleşen enflasyon kullanıldı (ex-post).
2. Reel faiz `(1+i)/(1+π) − 1` ile hesaplandı; yaklaşık `i − π` yüksek enflasyonda reel faizi fazla gösterir (çapraz terim).
3. Adım 3'te YP parçasının enflasyon telafisi ayrıştırılmadı (ABD enflasyonu repoda yok); yalnız TL parçası ayrışır.
4. Uluslararası Fisher bir eşitlik değil; faiz farkı ile gerçekleşen değer kaybı arasındaki fark risk primi ve carry'dir. Pearson ve sıra korelasyonu ile pahalı-ay oranı bunu gösterir, nedenselliği değil; Pearson uç değerlere (2021-2023) çok duyarlıdır.
5. Endeks bacağı TÜFE varsayımına ve başlangıç stoku kuralına bağlı; endeksleme anaparayı büyüttüğü için gerçek maliyet biraz daha yüksek olabilir (basit çeyreklik kural).
6. Anket kuru (USD/TRY 12 ay sonrası) ile anket enflasyonu birbirinden bağımsız anketlerdir; tutarlılıkları sınanmadı.
7. 'Tarihsel maksimum' bir sınır değil, örneklemin (2012-07 → 2026-01) en yüksek değeridir; aşmak imkânsız değil, örneklemde görülmemiş demektir. Örneklem kısa ve 2021-2023 negatif reel faiz dönemini içeriyor.

## Ne denmez

- 'Duran faizin yarısı enflasyon telafisi' denmez; pay π yoluna bağlı (anket ve alt yol ayrı gösterilir).
- 'YP kredi hep ucuz' denmez; pahalı çıkan ay oranı yukarıda, kur şoklarında tersine döner.
- 'Endeks bacağı K′ maliyetidir' denmez; hedef endeks TÜFE değilse bacak farklıdır ve repoda hedef patikası yok.
- Bu sayılar `adim3.csv`, `adim4.csv`, `rev_adim3*` veya `uc_kural_senaryo.csv` içine taşınmaz.
