# Varsayım eşikleri

Çalıştır: `python3 varsayim_esik.py`. Çıktı: `varsayim_esik.csv`, `varsayim_esik_sonuc.json`.

Kilitli üç kapı: vade dilimi yok, ödenmeyen emir yok, geçiş payı yok. Eşik kapıyı açmaz; koşullu satır yazar. Eşikler önceden kilitli: geçiş 0, 1/3, 1; vade günü 30, 90, 180; ödenmeyen emir eşiksiz. Konan eşik `varsayim`, `olculdu` olmaz.

Girdi: 2025 itiş 7.62 (yüzde GSYH, `tavan_akis.csv`); 2025 BDDK–akım boşluğu 387.1 milyar TL (`tek_sistem_kopru.csv`).

## 1. Geçiş satırları

| Eşik | İtiş (yüzde GSYH) | Tavan (puan) | Durum |
| --- | ---: | ---: | --- |
| 0 | 7.62 | 0.00 | varsayim |
| 1/3 | 7.62 | 2.54 | varsayim |
| 1 | 7.62 | 7.62 | varsayim |

Okuma: geçiş 1/3 varsayılırsa tavan 2,54 puan. Varsayım. RAPOR'un 2,5'i referans notunda; sonuç değil.

## 2. Vade satırları

| Eşik (gün) | Çıktı | Durum |
| --- | --- | --- |
| 30 | aşılırsa uzar; aşılmazsa uzamaz | kosullu |
| 90 | aşılırsa uzar; aşılmazsa uzamaz | kosullu |
| 180 | aşılırsa uzar; aşılmazsa uzamaz | kosullu |

Ödenmeyen emir boş; MY vade kırılımı 'ayrılmadı'. Üç satır da koşullu; ölçüm değil.

## 3. Ödenmeyen emir ve BDDK–akım

- `odenmeyen_emir`: eşik yok; çıktı boş milyar TL; `kosullu`. Ölçü yok (Sayıştay/HMB 320 Bütçe Emanetleri bulunamadı, vadeli_kalicilik). Eşik konmaz. 'Yok' satırı durur.
- `bddk_akim`: eşik yok; çıktı 387.10 milyar TL; `ayrilmadi`. 2025 BDDK ticari net akış 5,208 (stok farkı) − F.4 işlem akımı 4,820.9. Kur/değerleme ile borç veren kapsamı ayrılmadı; eşikle kapatılmaz.

## 4. Yanlışlayıcılar

- **H-V** (eşik ölçümü doldurur): `temiz`. durumlar ['ayrilmadi', 'kosullu', 'varsayim']; `olculdu` yok.
- **H-V2** (1/3 tavanı kurar): `ayri`. tavan_akis.csv tavan sütunu boş; 2,54 yalnız `varsayim` satırında ve referans notunda.

## Ne denmez

- 'Enflasyon 2,5 puan iner' denmez. Geçiş 1/3 varsayılırsa tavan 2,54; varsayım.
- Eşik seri diye kullanılmaz; kapı seri gelmeden açılmaz.
- BDDK–akım boşluğu eşikle kapatılmaz; ayrılmadı.
