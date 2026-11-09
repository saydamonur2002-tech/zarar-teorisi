# Beş yıl senaryosu: model uygulandı varsayımı, optimum aralık (2027–2031)

Senaryo; ölçüm değil. Çalıştır: `python3 bes_yil_senaryo.py`. Çıktı: `bes_yil_senaryo.csv`, `bes_yil_senaryo_sonuc.json`.

Taban: TÜFE yıllık 29.77 (2026-10); AOFM 36.0 (2026-11); USD/TRY 50.09 (2026-11); firma F.4 stoku 27,441.9 milyar (2026-Q2). Beklenti: EVDS Piyasa Katılımcıları Anketi, 2026-10.

Optimum aralık tanımı: model beş adımı tam uygular; yeni kredi itişi 0 (adım 3), eski stok silinen 0 ile yeni_tavan 0,2582 arası (adım 1 stok). Geçiş payı kapısı boş; enflasyon etkisi mantıksal sınırlarla [0, 1] bant olarak verilir. Faiz ve döviz için model etkisi `modellenmedi`; senaryo anket beklentisine eşit.

## Tablo (alt / üst)

| Yıl | Değişken | Taban | Beklenti / model yok | Model etkisi | Senaryo | Etki etiketi | Üç kapı |
| ---: | --- | ---: | ---: | ---: | ---: | --- | --- |
| 2026 | enflasyon_tufe_yillik | 29.77 | 29.63 | — | 29.63 / 29.63 | taban_yili | bos, bos, bos |
| 2026 | faiz_politika | 36.00 | 35.00 | — | 35.00 / 35.00 | taban_yili | bos, bos, bos |
| 2026 | doviz_usd_try | 50.09 | 51.55 | — | 51.55 / 51.55 | taban_yili | bos, bos, bos |
| 2026 | stok_firma_f4_kredi | 27,441.9 | — (taban_yili) | — | — | taban_yili | bos, bos, bos |
| 2027 | enflasyon_tufe_yillik | 29.77 | 23.33 | -7.61 / 0.00 | 15.72 / 23.33 | varsayim | bos, bos, bos |
| 2027 | faiz_politika | 36.00 | 27.93 | — | 27.93 / 27.93 | modellenmedi | bos, bos, bos |
| 2027 | doviz_usd_try | 50.09 | 59.26 | — | 59.26 / 59.26 | modellenmedi | bos, bos, bos |
| 2027 | stok_firma_f4_kredi | 27,441.9 | 32,254.6 | -11,898.2 / -4,812.7 | 20,356.4 / 27,441.9 | varsayim | bos, bos, bos |
| 2028 | enflasyon_tufe_yillik | 29.77 | 17.94 | -7.61 / 0.00 | 10.33 / 17.94 | varsayim | bos, bos, bos |
| 2028 | faiz_politika | 36.00 | 22.39 | — | 22.39 / 22.39 | modellenmedi | bos, bos, bos |
| 2028 | doviz_usd_try | 50.09 | — (bulunamadi) | — | — | modellenmedi | bos, bos, bos |
| 2028 | stok_firma_f4_kredi | 27,441.9 | 37,067.3 | -16,710.9 / -9,625.4 | 20,356.4 / 27,441.9 | varsayim | bos, bos, bos |
| 2029 | enflasyon_tufe_yillik | 29.77 | — (bulunamadi) | -7.61 / 0.00 | — | varsayim | bos, bos, bos |
| 2029 | faiz_politika | 36.00 | — (bulunamadi) | — | — | modellenmedi | bos, bos, bos |
| 2029 | doviz_usd_try | 50.09 | — (bulunamadi) | — | — | modellenmedi | bos, bos, bos |
| 2029 | stok_firma_f4_kredi | 27,441.9 | 41,880.0 | -21,523.6 / -14,438.1 | 20,356.4 / 27,441.9 | varsayim | bos, bos, bos |
| 2030 | enflasyon_tufe_yillik | 29.77 | — (bulunamadi) | -7.61 / 0.00 | — | varsayim | bos, bos, bos |
| 2030 | faiz_politika | 36.00 | — (bulunamadi) | — | — | modellenmedi | bos, bos, bos |
| 2030 | doviz_usd_try | 50.09 | — (bulunamadi) | — | — | modellenmedi | bos, bos, bos |
| 2030 | stok_firma_f4_kredi | 27,441.9 | 46,692.7 | -26,336.3 / -19,250.8 | 20,356.4 / 27,441.9 | varsayim | bos, bos, bos |
| 2031 | enflasyon_tufe_yillik | 29.77 | 12.17 | -7.61 / 0.00 | 4.56 / 12.17 | varsayim | bos, bos, bos |
| 2031 | faiz_politika | 36.00 | — (bulunamadi) | — | — | modellenmedi | bos, bos, bos |
| 2031 | doviz_usd_try | 50.09 | — (bulunamadi) | — | — | modellenmedi | bos, bos, bos |
| 2031 | stok_firma_f4_kredi | 27,441.9 | 51,505.4 | -31,149.0 / -24,063.5 | 20,356.4 / 27,441.9 | varsayim | bos, bos, bos |

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
