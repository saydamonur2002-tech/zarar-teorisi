# ON_KAYIT_eksik — hesaptan ÖNCE yazıldı (2026-10-23 ~16:40 TSİ)
Amaç: dagitim tablosunda hesaba katılmayan kanalları eklemek. 2014–2025, %GSYH, reel (TÜFE ile), + = kazanç.
Ortak kural: her sayı etiketli; haber rakamı hükme girmez (yalnız [İKİNCİL] bağlam); veri bulunamazsa EKSİK yazılır, uydurulmaz.
Kanallar:
K3 KKM: ödeyen = TCMB + Hazine (resmi yayınlanmış kur farkı ödemeleri, yıl bazında); alan = hane (gerçek kişi KKM payı) + firma (tüzel payı). Σ=0 (aktarım). Payı bulamazsam hane/firma bölüşümü KKM bakiye payıyla [VEKİL].
K4 Teşvik/vergi: (a) vergi harcamaları raporu (%GSYH) → firma (kurumlar/yatırım teşviki kalemleri) ve hane (gelir vergisi kalemleri) "alan", Hazine "ödeyen". Brüt aktarım, Σ=0. (b) Kurumlar vergisi / ücret vergisi oranı yalnız bağlam (aktarım değil, karşı-olgu yok).
K5 Senyoraj: enflasyon vergisi = π/(1+π) × emisyon_{t-1}/GSYH; ödeyen hane (+firma payı bilinmiyorsa tamamı hane [VARSAYIM]), alan TCMB. Ayrıca para tabanı reel artışı/GSYH (bağlam).
K6 Konut: hane konut stoku/GSYH [VARSAYIM band] × reel konut fiyat değişimi; gerçekleşmemiş, ayrı satır; karşı tarafı yok (Σ≠0, "yeniden değerleme").
K7 Altın: yastık altı altın ton [İKİNCİL/VEKİL] × reel TL altın fiyat değişimi; gerçekleşmemiş; karşı taraf yok.
K8 TCMB swap düşülmüş: TCMB kur kanalını net rezerv − swap ile yeniden hesapla; fark D+artık satırına.
K9 D doğrudan: UYP net pozisyon (TCMB) ile reel değişim/GSYH; artık D ile karşılaştır. D_doğrudan − D_artık = ölçüm hatası.
Hüküm ölçütleri (önceden):
H1 "Firma net kaybeden" sonucu değişir ⇔ F toplam (eski+K3+K4) > 0.
H2 "Hazine net kaybeden" değişir ⇔ K toplam > 0.
H3 "Birikim hanede" değişir ⇔ hane gerçekleşmiş toplam (K1+K2+K3+K4+K5) < 0.
H4 TCMB kazancı swapla değişir ⇔ swap düşülmüş TCMB kur < 0.
H5 D artığı güvenilir ⇔ |D_UYP − D_artık| kümülatif < 2 puan GSYH.
Bir kanal etkiyi |>1 puan| kayıyorsa "sonucu değiştiren kanal" denir.
Nedensel iddia yok.
