# Eşiksiz ölçüm (yerel kopya, b051b9b; repoya yazılmadı)
Bayrak no_floor=True: kademeli baskı (cap) ve sıçrama/kısma (unmet, psi_jump) kapalı. Tam tablo: tablo.txt. Grafik: senaryo_esiksiz.png.
Sonuç: B1 tuttu (2029 geri dönüş yok, enflasyon sürekli iner), B2 tuttu (rezerv çok daha çok erir), B3 kısmen (gizli/S-I ~1e-12, bilanço ~1e-11; test KALDI ama eşikli orijinalde de aynı: adres_stoklari None = repo/adim4.csv yerel kopyada yok), B4 tuttu.
SAPMA E1: test_sfc_muhasebe.py yerel kopyada her iki sürümde de 'adres None' ile kalıyor; eşikten bağımsız.
SAPMA E2: cap=1 sabitlenince rezerv kaybının kura etkisi tümden kalkıyor; kur yalnızca beklenen değer kaymasıyla (ee) artıyor. Bu yüzden eşiksiz düşük enflasyon kısmen "rezerv kaybı kuru hiç etkilemiyor" varsayımından gelir.

## Sıçramasız (no_jump=True)
Tablo: tablo_uclu.txt; grafik: senaryo_sicramasiz.png. C1 tuttu (eşiksizden farklı), C3 tuttu, C4 tuttu (1e-12), C5 tuttu; brüt rezerv hiçbir sıçramasız senaryoda negatif değil (min 76,7). cap formülünde bölme sorunu yok (NR<15'te cap=0, baskı psi'de doygun). SAPMA yok; test 'adres None' (E1) sürüyor.
