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

## Şok testleri

Çalıştır: `python3 rev_sok.py` (zincire bağlı). Çıktı: `rev_sok_sonuc.json`, `rev_sok_sonuc.csv`. Kilitli formül ve kilitli dosya değişmez. `kanıt` ölçülen veya mevcut formülün bu girdilerle ürettiği sayıdır; `aday` şok büyüklüğü, vade veya kapsam taşımasıdır.

Kur, F.4 2026-Q1 stokuna (25.339,8 milyar TL) YP payı %54,44 ile uygulanır (kanıt, ölçüm türevi). Yeni stok S = S0·(1+yp·δ), yeni pay yp·(1+δ)/(1+yp·δ). δ ızgarası 0/10/20/30/50 adaydır. Faiz, `rev_adim3` sözleşme formülüdür; ψ yok; F'ye yazılan faiz alacaklıdan düşülür, ΣNL = 0 (kanıt, kimlik).

Köprüye yalnız değerleme farkı girer. Dağılım, Sektör Bilançoları 2024 banka kredisinin kısım payıdır (toplam 11.469,0 milyar TL; F.4 ile aynı stok değil, aday). Vade kırılımı kapısı boş olduğu için fark bu çeyrekte isteniyor (aday). δ=0 ağda ek düğüm yok.

Büyüme bandı çeyreklik: yok 0, min %4,85, medyan %8,51, azami %12,12 (kanıt, ölçüm türevi). Stres = azaminin iki katı, %24,24 (aday). GSYH paydası 2029 141.198,5, 2031 178.999,3 (aday, reel %3 yolu).

Kur, düz stok ve sabit faiz, 2029 sözleşme faizi: κ=0,25 için δ=0 1.616,4 (%1,14 GSYH), δ=30 1.696,2, δ=50 1.749,4; κ=1 için δ=0 6.465,7, δ=50 6.997,5. USD stok faizi TL faizinin altında olduğu için kur, tutarı stok kadar şişirmez; yön yine artıştır.

Büyüme, δ=0 ve sabit faiz, 2029: κ=0,25 yok 1.616,4 (%1,14), medyan 4.505,1 (%3,19), azami 6.808,1 (%4,82), stres 25.079,3 (%17,76). Aynı sıra κ=1: 6.465,7, 18.020,5, 27.232,4, 100.317,3.

Çeyreklik köprü, λ=1, β tavan: δ=0 iken 52,4 milyar TL ve 3 kısım (kilitli hücre, kanıt). δ=10 220,8 ve 7 kısım; δ=30 964,8 ve 10 kısım; δ=50 3.474,3 ve 15 kısım. λ=1'de köprü yayımlanmış üst ucu kur %1 iken aşar (kredi 55,5). Temerrüt 3'ün üstüne kur %3 iken çıkar (4 kısım). λ* üst uçta (nakit 1,0471) köprü üst ucu kur %3 (kredi 54,2), temerrüt artışı kur %4 (4 kısım).

Seyrek ağ Adım 2'de koşulur: Adım 1 ile aynı kenar maskesi ve `rev_adim1.ras`, sonra mevcut `ag` ve `calistir`. Yoğunluk 1, kilitli hücreyi yeniden üretir (3 kısım, kredi 52,4). Yoğunluk 0,25, 30 tohum: temerrüt 4–15 (ortanca 11), köprü 62,5–7.461,8 (ortanca 3.786,8). Kur şoku olmadan da koşul bozulur. Adım 1'deki LP silinen oranı ile bu köprü aynı sayı değildir; biri mahsup tavanı, öteki çeyreklik ödeme açığıdır.

Birleşik stres (kur %30, faiz %55, azami büyüme): κ=1 için 2029 faizi 32.568,5 milyar TL, FG2024'ün 10,36 katı, 2029 GSYH'sinin %23,07'i; 2031'de 81.318,5 (%45,43). κ=0,25'te 2029 8.142,1 (%5,77), FG katı 2,59. κ=1 ve azami büyüme, kur sıfırken FG katı yayımlanmış üst uçtur (9,93). Bu uç, kur %1 iken aşılır.

Karar cümleleri tabloda durur; bu şoklar onları 'yapılamaz' diye yeniden yazmaz. Adım 2'nin koşulu tam ağda kur eşiğinde, seyrek ağda kur olmadan bozulur. Adım 3'ün koşulu (küçük κ ve düşüş patikası) birleşik streste tutmaz; κ=1 tavan hücresi kur eşiğinde yayımlanmış FG bandının dışına çıkar. Adım 1 kararı zaten yoğunluğa bağlıdır. Adım 4, 4.5 ve 5 için bu şokların kanalı yoktur.
