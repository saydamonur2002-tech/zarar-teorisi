# Beş yıl senaryosu: model uygulandı varsayımı, optimum aralık (2027–2031)

Senaryo; ölçüm değil. Çalıştır: `python3 bes_yil_senaryo.py`. Çıktı: `bes_yil_senaryo.csv`, `bes_yil_senaryo_sonuc.json`.

Taban: TÜFE yıllık 29.73 (2026-09); AOFM 37.0 (2026-10); USD/TRY 49.13 (2026-10); firma F.4 stoku 25,339.8 milyar (2026-Q1). Beklenti: EVDS Piyasa Katılımcıları Anketi, 2026-09.

Optimum aralık tanımı: model beş adımı tam uygular; yeni kredi itişi 0 (adım 3), eski stok silinen 0 ile yeni_tavan 0,2582 arası (adım 1 stok). Geçiş payı kapısı boş; enflasyon etkisi mantıksal sınırlarla [0, 1] bant olarak verilir. Faiz ve döviz için model etkisi `modellenmedi`; senaryo anket beklentisine eşit.

## Tablo (alt / üst)

| Yıl | Değişken | Taban | Beklenti / model yok | Model etkisi | Senaryo | Etki etiketi | Üç kapı |
| ---: | --- | ---: | ---: | ---: | ---: | --- | --- |
| 2026 | enflasyon_tufe_yillik | 29.73 | 29.61 | — | 29.61 / 29.61 | taban_yili | bos, bos, bos |
| 2026 | faiz_politika | 37.00 | 35.07 | — | 35.07 / 35.07 | taban_yili | bos, bos, bos |
| 2026 | doviz_usd_try | 49.13 | 51.57 | — | 51.57 / 51.57 | taban_yili | bos, bos, bos |
| 2026 | stok_firma_f4_kredi | 25,339.8 | — (taban_yili) | — | — | taban_yili | bos, bos, bos |
| 2027 | enflasyon_tufe_yillik | 29.73 | 22.69 | -7.62 / 0.00 | 15.07 / 22.69 | varsayim | bos, bos, bos |
| 2027 | faiz_politika | 37.00 | 27.16 | — | 27.16 / 27.16 | modellenmedi | bos, bos, bos |
| 2027 | doviz_usd_try | 49.13 | 58.60 | — | 58.60 / 58.60 | modellenmedi | bos, bos, bos |
| 2027 | stok_firma_f4_kredi | 25,339.8 | 30,160.7 | -11,363.6 / -4,820.9 | 18,797.1 / 25,339.8 | varsayim | bos, bos, bos |
| 2028 | enflasyon_tufe_yillik | 29.73 | 18.32 | -7.62 / 0.00 | 10.70 / 18.32 | varsayim | bos, bos, bos |
| 2028 | faiz_politika | 37.00 | 22.43 | — | 22.43 / 22.43 | modellenmedi | bos, bos, bos |
| 2028 | doviz_usd_try | 49.13 | — (bulunamadi) | — | — | modellenmedi | bos, bos, bos |
| 2028 | stok_firma_f4_kredi | 25,339.8 | 34,981.6 | -16,184.5 / -9,641.8 | 18,797.1 / 25,339.8 | varsayim | bos, bos, bos |
| 2029 | enflasyon_tufe_yillik | 29.73 | — (bulunamadi) | -7.62 / 0.00 | — | varsayim | bos, bos, bos |
| 2029 | faiz_politika | 37.00 | — (bulunamadi) | — | — | modellenmedi | bos, bos, bos |
| 2029 | doviz_usd_try | 49.13 | — (bulunamadi) | — | — | modellenmedi | bos, bos, bos |
| 2029 | stok_firma_f4_kredi | 25,339.8 | 39,802.5 | -21,005.4 / -14,462.7 | 18,797.1 / 25,339.8 | varsayim | bos, bos, bos |
| 2030 | enflasyon_tufe_yillik | 29.73 | — (bulunamadi) | -7.62 / 0.00 | — | varsayim | bos, bos, bos |
| 2030 | faiz_politika | 37.00 | — (bulunamadi) | — | — | modellenmedi | bos, bos, bos |
| 2030 | doviz_usd_try | 49.13 | — (bulunamadi) | — | — | modellenmedi | bos, bos, bos |
| 2030 | stok_firma_f4_kredi | 25,339.8 | 44,623.4 | -25,826.3 / -19,283.6 | 18,797.1 / 25,339.8 | varsayim | bos, bos, bos |
| 2031 | enflasyon_tufe_yillik | 29.73 | 12.09 | -7.62 / 0.00 | 4.47 / 12.09 | varsayim | bos, bos, bos |
| 2031 | faiz_politika | 37.00 | — (bulunamadi) | — | — | modellenmedi | bos, bos, bos |
| 2031 | doviz_usd_try | 49.13 | — (bulunamadi) | — | — | modellenmedi | bos, bos, bos |
| 2031 | stok_firma_f4_kredi | 25,339.8 | 49,444.3 | -30,647.2 / -24,104.5 | 18,797.1 / 25,339.8 | varsayim | bos, bos, bos |

## Üç kilitli ölçüt, yıl yıl

- Vade dilimi: `bos`. MY vade kırılımı 'ayrılmadı', ortalama gün boş (vadeli_kalicilik.csv). Adım 2 ödeme planının süresi bu yüzden yazılmaz.
- Ödenmeyen emir: `bos`. Kamu bacağı ölçüsü yok. Senaryoda kamu satırı yok.
- Geçiş payı: `bos`. Enflasyon bandının hangi ucunun geçerli olduğu bu kapıya bağlı; kapı boşken tek sayı yazılmaz.

## Yanlışlayıcılar

- **H-Y1** (senaryo ölçüm diye yazılır): `temiz`. senaryo hücresi ölçüm etiketi taşımaz.
- **H-Y2** (kapı doldurulur): `temiz`. üç kapı boş; geçiş sayısı yazılmadı.
- **H-Y3** (silinen veya senet dolar): `temiz`. silinen boş, senet kilidi duruyor.

## Varsayımlar (ölçüm değil)

- İtiş 2025 değeri (4.820,9 milyar; 7,62 puan GSYH) beş yıl nominal sabit. GSYH yolu yok; stok sütunu nominal, GSYH payı verilmez.
- Model 2027 başında tam uygulanır; etki her yıl aynı. Geçiş süresi, kısmi uygulama yok.
- Enflasyon etkisi: −geçiş × 7,62; geçiş 0 ve 1 mantıksal uç. varsayim_esik.csv eşikleri (0, 1/3, 1) buraya taşınmadı.
- 2029–2030 için anket ufku yok; beklenti `bulunamadi`, senaryo boş. 2031 yalnız TÜFE (5 yıl sonrası).
- Eski stok faizinin durması ve faiz tahakkuku modellenmedi; stok sütunu anapara.

## Ne denmez

- 'Enflasyon 7,6 puan iner' denmez. Bant [0, −7,62]; geçiş kapısı boş.
- 'Stok yüzde 26 silindi' denmez. Tavan 0,2582 üst sınır; silinen boş.
- 'Faiz düşer', 'kur durur' denmez. İkisi `modellenmedi`; senaryo anket beklentisidir.
- Anket beklentisi gerçekleşme değil; EVDS katılımcı ortalaması.
