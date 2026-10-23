# Tek Sistem katsayıları — karşılaştırma

Modeldeki paket, beş adımı bu SFC'nin kaldıraçlarına çevirir. Repodaki sayı aynı nesne ise koda bağlandı. Aynı nesne değilse sayı durur; bu dosya farkı yazar. Etiketler: **kanıt** depodaki ölçüm ya da kilitli formülün bu girdilerle ürettiği sayı; **aday** ölçek veya eşleşme vekili; **tahmin** regresyon; **varsayım** atanmış katsayı.

| Model | Değer | Repo | Karar |
| --- | --- | --- | --- |
| Adres havuzu | 19.361,9 milyar TL; döviz payı 6.639,4 / 19.361,9 | `adim4.csv` üç `olculdu` satır: hane vadeli 8.322,4, firma vadeli 4.400,1, gerçek kişi YP 6.639,4. Toplam `tek_sistem_kademe.MEVDUAT_ADRES_MILYAR`. **kanıt** (stok). Senet satırı `modellenmedi`. | Hardcode kaldırıldı. Koşu `adim4.csv` okur. Toplam birebir aynı. |
| Adım 4 havuzdan senede kayan pay | 0,02 / 0,05 / 0,10 | `adim4_adres_yonlendirme.py` θ ∈ {0,10; 0,25; 0,50}, **varsayım**. K3 kredi itişi 0,08, **varsayım**. | Yerine konmadı. θ, adres stokunun yönlendirilen payıdır; modeldeki pay, rapor V1 havuz payıdır. İkisi aynı karar değil. |
| Adım 1–2 silinen borç payı | 0,14 / 0,20 / 0,25 | `bes_adim_sonuc.json` yeni_tavan 0,2582 (**aday**, Σortak/Σbrüt üst sınır). Silinen sütun boş: kimden-kime tablosu yok. | Yerine konmadı. 0,2582 silinen pay değildir. |
| `TS_NPL_COEF` | 0,5 **varsayım** | `OKU.txt` / `kalibre_lambda`: değerleme zararının provizyona geçişi ölçülemedi; θ ≈ −0,03; ≥ %4 geçiş reddedilir. `L_cift_kayit` borç silinmez. | Yerine konmadı. 0,5 «silinen borcun yarısı temerrütten çıkar» der. Repo, değerleme→provizyon geçişini ölçer ve silmenin olmadığını yazar. Nesneler ayrı. |
| Adım 3 κ | 0,50 / 0,50 / 0,50 | `adim3` κ ∈ {0,25; 0,5; 1}, **varsayım**. | Aynı orta değer. Karar parametresi olarak durur. |
| Atalet ρ (paket) | 0,59 / 0,55 / 0,45; ölçek tabanı 0,59 | `hekis/kalibre.py`: yıllık TÜFE `ρ = 0,68` (se 0,16, n=10), **tahmin**. `gecis_payi_band_sonuc.json` çeyreklik `ρ = 0,4513`, **tahmin**. `a_pi = 0,70` modelin kendi enflasyon ağırlığı. | Yerine konmadı. 0,59 «bugün» diye paketin iç ölçeğidir. 0,68 yıllık AR, 0,45 çeyreklik AR; ikisi de `a_pi` değil. 0,59'u 0,68 yapmak kötümser senaryoyu sessizce gevşetirdi. |
| Adım 5 HEKİS | tam ölçek −0,16 puan | `hekis_model/SISTEMLER.md`: iki sistem ulusal TÜFE −0,16 puan (**aday**, esneklik 0,6). Ayrı ayrı −0,055 ve −0,10. | Sayı durur. Kayıtlı iki sistem toplamı ile aynı. Tek şehir ulusal payı (−0,05 civarı) başka toplama. |
| Banka özkaynağı | 4,565252392 tn TL | EVDS `TP.TOP.V28`, 2026-07, 4.565.252.392 bin TL (**kanıt**). Aynı seri Haziran 4.530.228.129 bin TL, `L_cift_kayit.E_TOT = 4,530`. | Yerine kondu. Eski sayfa iddiası 4,65 bulunamadı. Açılış banka net serveti bu sabite eşitlenir; fark `M_b` kalemine yazılır. |

Haftalık girdilerin seri kodu, tarihi ve etiketi `veriler.json` → `dogrulama` içindedir. TÜFE, USD/TRY (22.10.2026 ForexBuying), politika faizi (duyuru 2026-45), brüt rezerv, kalan vadeli KV dış borç, TÜFE bazlı REK ve yabancı hisse stoku **kanıt**. Swap hariç net rezerv başlığı, emek payı, büyüme, yabancı takas payı ve BIST 100 **[DOĞRULANMADI]**; sayıları durur.
