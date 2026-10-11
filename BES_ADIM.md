# Beş adım, sırayla, tek koşu

Ön kayıt `87f0317`. Çalıştır: `python3 bes_adim.py`. Çıktı: `adim1_stok.csv`, `adim2.csv`, `adim3.csv`, `adim4.csv`, `adim5.csv`, `bes_adim_sonuc.json`.

Her adım kendi dosyasını yazar; sonraki, öncekinin etiketini okur; `ihlal` ise durur. Önceki katman sayıları taşınmaz. Adım 1 akış satırı (0,4270, `baska_nesne`) dokunulmadı.

## Etiketler

| Adım | Dosya | Yanlışlayıcı | Etiket | Sayı |
| --- | --- | --- | --- | --- |
| 1 stok | `adim1_stok.csv` | H-S1 temiz, H-S2 temiz | `temiz` | eski_tavan 0.0728; yeni_tavan 0.2582; silinen boş |
| 2 | `adim2.csv` | H-A2 temiz | `temiz` | temerrüt 0, `modellendi`; holding_odeme_orani 0.5; ucret_gecis_beta 0.3 parametre |
| 3 | `adim3.csv` | H-A3 temiz | `temiz` | kredi ihtiyacı 0.0 `modellendi`; F F.4 25,339.8 `olculdu` (stok) |
| 4 | `adim4.csv` | H-A4 temiz | `temiz` | üç adres adayı `olculdu`; senet `modellenmedi`, ihraç/prim/çıkış boş |
| 5 | `adim5.csv` | H-A5 temiz | `temiz` | kira `olculmedi`; HEKİS havuz kirası 20,000 TL/ay `modellendi` |

## Kilitli üç kapı

- gecis_payi: boş (`tavan_akis.csv` gecis, tavan)
- vade_dilimi: boş (`vadeli_kalicilik.csv` vade_kirilim, ortalama_gun)
- odenmeyen_emir: boş (`vadeli_kalicilik.csv` odenmeyen_emir_milyar)
- Etiket: `temiz`. varsayim_esik.csv eşikleri varsayım; kapıya taşınmaz.

## Koşunun sözü: `bitti`

Son satır (`bes_adim_sonuc.json` `son`) koşudan gelmez; `python3 test_bes_adim.py` yazar. Kaynak test.

## Adım 1 stok, iki sütun

- `eski_tavan` 0.0728: stok_silim.py, her tek yön bacağa aynı araçta EVDS üst sınırı; aynı EVDS stoku birden çok satırda; metindeki ters bacak (başka araç) görülmez. Durur, silinmez.
- `yeni_tavan` 0.2582: çift düzeyi; iki yön metinden (araçlar toplanır), ters yön metinde yoksa EVDS konsolide olmayan aynı-araç üst sınırı; ortak = min; Σortak 20,363.4 / Σbrüt 78,870.4; 6/6 çift dolu. Yalnız metin iki yön: 0.3175.
- Silinen boş: kimden-kime xls depoda yok. İki sayı üst sınır; skor değil. 'Yaklaşık yüzde 20' bu kuralla çıkmadı; bulunamadı.

## Ne denmez

- 'Beş adım kuruldu' denmez. Şu adım şu etiket; kilitli kapı boş.
- 'Stok yüzde X silindi' denmez; silinen boş.
- 'HEKİS döngüyü kırdı' denmez; adım 5 kira `olculmedi`, HEKİS `modellendi`.
- HEKİS senedi ile hedef primli senet eşitlenmez; senet `modellenmedi`.
