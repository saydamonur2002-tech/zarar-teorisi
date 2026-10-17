# Yapılabilirlik değerlendirmesi (rev, 17.10.2026 dondurulmuş veri)

Ölçütler: depoda adım başına ölçüt yok (GIDISAT_RAPORU.md'deki `kisitli_uygulanabilir` skoru bütün model içindir). Bu yüzden dört ölçüt kullanıldı:
(1) iç SFC tutarlılığı, (2) kaynak yeterliliği, (3) yan etki sınırları, (4) varsayım bandına duyarlılık.

| Adım | Karar | Temel gerekçe |
| --- | --- | --- |
| 1 Mahsup | koşullu yapılabilir (koşul: firma ağı yoğunluğu yüksek / merkezi takas) | Tam graf oranı 2011–2024 arasında 0,886–0,925 (kanıt, SB). Seyrek ağda 0,12–0,91 (aday, yoğunluk varsayımı). |
| 2 Ağ/likidite | koşullu yapılabilir (koşul: çeyreklik köprü ~45–52 milyar TL, 3 kısım temerrüdü çözülür) | β etkisiz; λ* 5 çapada dar banttadır (0,89–0,92 stok, 1,02–1,05 akım). |
| 3 Faiz durması | koşullu yapılabilir (koşul: κ küçük + faiz düşüş patikası; ödeyen hazne açıkça seçilir) | Transfer ΣNL=0 (kanıt). κ=1'de 2029 tutarı FG2024'ün 1,4–9,9 katı (aday). |
| 4 Adres yönlendirme | bu veriyle karar verilemez (kredi katsayısı 0,08 ile 0,79 arasında; çift sayım düzeltildi) | Hane DİBS payı %4,6 (kanıt). Kredi tepkisi 7–10 kat belirsiz. |
| 4.5 Birim | yapılabilir (etkisiz: plasebo) | 898,3 = A17 Emisyon (kanıt). |
| 5 Kira | yapılabilir (H içi transfer; tutar bandı geniş) | N doğrulandı; kiracı oranı TÜİK fert %27 (hane bazlı yok). |

Ayrıntı: rev_adim{1,2,3,4,45}_sonuc.json, adim5_kira_aralik.csv.
