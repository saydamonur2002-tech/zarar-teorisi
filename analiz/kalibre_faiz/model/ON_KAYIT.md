# Ön kayıt — Zararın Muhasebesi entegrasyonu

Koşu henüz yok. Aşağıdaki eşikler, entegre kodun ilk koşusundan önce yazıldı. Sapma `SAPMA.md` dosyasına düşer. Bu sayfa, sonucu gördükten sonra eşik gevşetmek için kullanılmaz.

Referans koşu: zipteki model, aynı `veriler.json`, `once_ozet.json`. Etiket: **aday** (model çıktısı, ölçüm değil).

## Beklenen

1. **Muhasebe.** Her senaryoda (S0–S7 ve zombi kapalı kopyalar) gizli denklem, tasarruf–yatırım ve bilanço (`ΣV − pK`) mutlak hatası `< 1e-8` trilyon TL. Açılışta finansal enstrüman satırlarının altı kesim toplamı mutlak değeri `< 1e-6`. Sabit sermaye satırı `pK`'ya toplanır; o satırın sıfır olması beklenmez. Kesim net servetleri toplamı ile `pK` farkı `< 1e-6`. Bu cümle, koşudan önce düzeltildi: ilk yazım her satırın sıfır toplanmasını istiyordu; sermaye satırı sıfır toplamlı değildir.
2. **S0–S7 sayısal kimlik.** 2029 enflasyonu, 2029 net rezerv, 2028Q4 net rezerv, 2027Q4 net rezerv, 2029 kamu borcu/GSYH, 2029 reel GSYH endeksi, 2029 USD/TL: `once_ozet.json` ile mutlak fark `< 1e-6`. Katsayılar yerine konmadığı için fark beklenmiyor.
3. **Tek Sistem paketi.** Baz ve dış şok arka planında paketsiz / kötümser / olası / iyimser için aynı altı gösterge, aynı tolerans. `TS_NPL_COEF` 0,5 kalır. Adres stoku `adim4.csv` üzerinden okunur; toplam 19.361,9 milyar TL ile birebir aynıdır.
4. **Zombi kanalı kapalı (yapısal).** S4z ve S5z, S4 ve S5'in `γ_z = 0` kopyasıdır; başka katsayı değişmez. Beklenen yön, denklemin işareti: S4z'nin 2029 reel GSYH endeksi S4'ten büyüktür; S5 − S4 kümülatif üretim farkı, S5z − S4z farkından büyüktür (tanımanın avantajı kanal kapanınca küçülür). Bu, modelin kendi kapanışıdır.
5. **Log.** Yeni haftalık kayıtta `kod_surumu.git` ve `kod_surumu.sfc_sha256` dolu olur. Aynı veri kesiminde kod kimliği değişirse önceki kayıt silinmez.

## Yerine konmayan katsayılar (karar, koşudan önce)

Ölçülmüş sayı, modeldeki nesnenin aynısı değilse yerine konmaz. Karşılaştırma `KATSAYI.md` içindedir.

- `TS_NPL_COEF = 0,5` durur. Repoda «silinen borcun temerrütten çıkan payı» diye bir ölçüm yok.
- Atalet `ρ = 0,59` durur. Repodaki yıllık `ρ ≈ 0,68` ve çeyreklik `ρ = 0,4513` başka denklemlerdir.
- `BANKA_OZKAYNAK_TN = 4,65` durur. Temmuz 2026 iddiasının birincil tablosu repoda yok.

## Nedensellik

S4z/S5z bir parametre kapatmasıdır. Türkiye için zombi kredisinin nedensel etkisi bu koşuda tanımlı değildir: veri karşı-olgusu yok. Paket senaryoları da politika etkisi tahmini değildir.

## Ek — birincil veri güncellemesi (ikinci koşudan önce)

Bu bölüm, girdi güncellemesinin koşusundan önce yazıldı. `once_ozet.json` bu koşunun referansı değildir; o dosya zip tabanıdır. «Eski» sütun, bu klasörde güncellemeden hemen önceki 2029Q4 tablosudur (`SAPMA.md`). Patikanın o tablodan ayrılması, girdi değişiminin etkisidir; kimlik testi olarak sayılmaz.

Karar: sayı, ancak okunan birincil gözlemle değişir. Bulunamayan satır aynı sayıda ve **[DOĞRULANMADI]** kalır. Rakam uydurulmaz. Ortamda EVDS anahtarı yok; resmi EVDS API çağrılmadı. EVDS3 iç uç noktası kullanılmadı.

Değişecek ya da etiketi kanıta dönecek girdiler:

- `usd_try` 49,54 → 49,5389. TCMB gösterge kurlar, `ForexBuying`, 22.10.2026, bülten 2026/200. 23.10.2026 bülteni yok.
- `politika_faizi` 0,36 durur; etiket **kanıt**. TCMB basın duyurusu 2026-45, 22.10.2026, bir hafta vadeli repo ihale faizi %37 → %36. AOFM (`TP.APIFON4`, 2026-10: 37,0) başka seridir, yerine konmaz.
- `brut_rezerv` 169,1 → 169,096. TCMB URDL, 16.10.2026, I.A resmi rezerv varlıkları, 169.096 milyon ABD doları.
- `kv_dis_borc_kalan_vade` 243,3 → 243,276. TCMB Kısa Vadeli Dış Borç, Tablo 5 toplam, Ağustos 2026, 243.276 milyon ABD doları. Orijinal vade toplamı 176.564 ayrı nesnedir, modele yazılmaz.
- `reel_efektif_kur` 105,45 durur; etiket **kanıt**. TCMB REK gelişmeleri, Eylül 2026, TÜFE bazlı, 2025=100.
- `yabanci_hisse` 33,98 → 33,9811. TCMB Menkul Kıymet İstatistikleri, Tablo 1 hisse senedi stoku, 16.10.2026, 33.981,1 milyon ABD doları. Repo EVDS `TP.MKNETHAR.M1` 09.10.2026 = 35.921,4, aynı tablonun önceki haftasıyla birebir.
- `banka_ozkaynak_tn` 4,65 → 4,565252392. EVDS `TP.TOP.V28` (bie_pbtop, 49.ÖZKAYNAKLAR), 2026-07, 4.565.252.392 bin TL. Haziran aynı seri 4.530.228.129 bin TL, repodaki 4,530 kaydıyla aynı yuvarlamadır. BDDK başlığı 4,65 bulunamadı.

Aynı sayıda kalacaklar, etiket **[DOĞRULANMADI]**:

- `swap_haric_net_rezerv` 39,34. URDL’de bu başlık yok. Bileşenler `veriler.json` içine yazılır; bileşenlerden artık üretilmez. Açılış net rezervi bu sayıda kalır. Brüt 169,096 olunca bankaların TCMB’deki dövizi (brüt − bu sayı) kıpırdar.
- `emek_payi` 0,381 ve `buyume_yillik` 0,023. TÜİK bülten sayfası sayı içermeyen kabuk döndü. Sayı uydurulmadı.
- `yabanci_takas_payi` 0,344 ve `bist100` 11220,37. Borsa İstanbul birincil tablosu okunmadı. `bist100` açılış durumuna girmez.

Beklenen, bu koşu:

1. Muhasebe eşikleri durur: gizli denklem, tasarruf–yatırım ve bilanço `< 1e-8` tn TL; açılış finansal satır ve `nw − pK` `< 1e-6`.
2. S4z’nin 2029 reel GSYH endeksi S4’ten büyüktür; S5 − S4 kümülatif üretim farkı, S5z − S4z farkından büyüktür. Model içi karşı-olgudur, Türkiye için nedensel tahmin değildir.
3. `once_ozet.json` ile mutlak fark `< 1e-6` bu koşuda aranmaz.
