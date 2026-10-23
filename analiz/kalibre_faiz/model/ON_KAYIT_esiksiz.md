# ON_KAYIT — eşiksiz (2026-10-23, hesaplamadan önce)
Kaynak: zararin_muhasebesi @ b051b9b (yerel kopya). Değişiklik: `no_floor=True` bayrağı → cap=1 (kademeli psi·(1−cap) baskısı kapalı), unmet=0 (psi_jump sıçraması + dolarizasyon/sıcak para kısması kapalı). MIN_CB (MAK göstergesi) 15'te kaldı; dinamiğe girmez.
Beklenti: (B1) 2029 enflasyon geri dönüşü (2029 max − 2028Q4..min) eşikliye göre en az yarı yarıya küçülür; (B2) net rezerv min eşikliden daha düşük (daha çok erir); (B3) gizli denklem ve S-I < 1e-9, bilanço hatası ~0; test geçer; (B4) S5 reel GSYH > S4 ve borç/GSYH S5 < S4 eşiksiz de korunur.
Başarısızlık: herhangi biri tutmazsa SAPMA/sonuç olarak yazılır, beklenti değiştirilmez.

## Ek — sıçramasız (no_jump=True), hesaplamadan önce (14:20 TSİ)
Yalnız unmet=0 (psi_jump sıçraması + dolarizasyon/sıcak para kısması kapalı); cap=clip((NR−15)/30,0,1) ve psi aynen. NR<15'te cap=0 → baskı psi'de doygun sürer (bölme sorunu yok).
Beklenti: (C1) sonuçlar tam eşiksizden farklı; (C2) 2029 geri dönüşü eşikliden küçük ama eşiksizden büyük olabilir; (C3) rezerv eşikliden daha çok erir; (C4) muhasebe ~1e-11; (C5) S5>S4 korunur.
