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
