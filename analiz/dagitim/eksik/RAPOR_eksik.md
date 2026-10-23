# RAPOR_eksik — dağıtım tablosuna eksik kanalların eklenmesi (2014–25, %GSYH reel, kümülatif)
Dosyalar: tablo_aktor_kanal_tam.csv (eski + yeni kanallar, NET), yeni_kanallar_yil.csv, eksik.png, ON_KAYIT_eksik.md, SAPMA_eksik.md, e.py, g.py, ham/.

## Net tablo [HESAP]
| Aktör | Eski (TL+kur) | KKM | Senyoraj | Banka altın | Swap | NET (VH hariç) | Vergi harc. | NET (VH dahil) |
|---|---|---|---|---|---|---|---|---|
| Hane (toplam; üst/alt ayrımı yalnız eski kanallarda) | +6,46 | +3,83 | −3,93 | +3,96 | 0 | **+10,32** | +16,20 | +26,52 |
| Firma | −8,17 | +1,35 | 0 | 0 | 0 | **−6,82** | +7,76 | **+0,94** |
| Banka | −1,18 | 0 | 0 | 0 | 0 | −1,18 | 0 | −1,18 |
| Hazine | −6,08 | −0,82 | 0 | 0 | 0 | **−6,90** | −36,65 | −43,56 |
| TCMB | +3,89 | −4,35 | +4,17 | 0 | −2,23 | **+1,48** | 0 | +1,48 |
| Yurt dışı+artık | +5,07 | 0 | −0,25 | −3,96 | +2,23 | **+3,10** | 0 | +3,10 |
| KDV/ÖTV/diğer (ayrılamadı) | | | | | | | +12,69 | +12,69 |
Her sütunda Σ=0.

Gerçekleşmemiş değerleme (karşı tarafı yok): kiradaki konut +26,7 [VEKİL]; yastık altı altın (2017–25) +38,9 (3.739 ton) ile +22,9 (2.200 ton) arası [VARSAYIM].

## Ön kayıtlı ölçütler
- H1 (firma kaybeden mi): ön kayıtlı tanım (K4 dahil) F = +0,94 > 0, yani sonuç **DEĞİŞİYOR**. Ama kırılgan: 2017–25 için +0,43 ve bu değer tamamen kurumlar vergisi harcamasından geliyor (2017 yöntem kırılması). Vergi harcaması hariç F = −6,8, yani kayıp sürüyor.
- H2 (Hazine kaybeden): değişmedi (−6,9; VH dahil −43,6).
- H3 (birikim hanede): değişmedi, güçlendi (+10,3 gerçekleşen, buna ek olarak konut ve altın).
- H4 (TCMB swap): swap düşülünce TCMB kur kazancı +3,89'dan +1,66'ya iniyor, işaret değişmiyor. Ama KKM eklenince TCMB neti +1,5'e iniyor. 2021'de TCMB net kaybeden (−0,9), 2023'te de (−2,8).
- H5 (D artığı güvenilir mi): UYP'den doğrudan D = −0,75, artık = +5,07, fark 5,8 > 2. Artık **güvenilmez**. 2017–25'te D_UYP +1,17. Doğrudan ölçüm "yurt dışı kazandı" sonucunu desteklemiyor.

## Sonucu değiştiren kanallar (|etki| > 1 puan)
KKM (TCMB −4,4 → hane +3,8), senyoraj (hane −3,9 → TCMB +4,2), banka altın (hane +4,0), swap (TCMB −2,2). Vergi harcaması ölçek olarak hepsini bastırıyor, ama nakit akımı değil.
Yorum [aday]: hane kazancının yarısından fazlası kur, KKM ve altın kaynaklı. Senyoraj bunu kısmen geri alıyor. KKM, TCMB'nin kur kazancını büyük ölçüde haneye ve firmaya aktarmış görünüyor. Nedensel iddia yok.

## Hesaplanamayanlar
Kurumlar vergisi/ücret vergisi yükü; SGK prim ve yatırım teşviki nakit destekleri; KDV/ÖTV vergi harcamasının aktöre bölüşümü; KKM'nin hane üst/alt ayrımı; sahibinin oturduğu konut; 2014–16 kur ve altın; TCMB KKM giderinden YUVAM ve fiziki altın payının ayrıştırılması.

## Kaynaklar
TCMB yıllık rapor 2023–2024 "3.4 Açıklamalar" ve 2025 YFR (KKM gideri); FİR 2024-I; ER 2025-I Kutu 2.5; TCMB uyp.pdf ve bop.pdf; analitik bilanço (yerel dosya); BIS QTRR628BIS; vergi harcamaları (dergipark derlemesi, GİB 2024 raporu) [İKİNCİL]; Hazine KKM [İKİNCİL]. Haber rakamları (Karahan 400–500 mlr $, İKO 5.000 ton) hükme girmedi.
