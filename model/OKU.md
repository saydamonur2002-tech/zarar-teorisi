# Modeller

Depoya hesaplanmış değerler gitti. Excel formülü yerel dosyada duruyor; bu kapı metin alıyor.

- gercek/Turetim.csv: özel sektör net, sepet farkı, kişi başı kredi, açlık iddiası
- gercek/Model.csv: medyan ücret vekili, açık, sahte talep
- pasta/Olcum.csv: kopma payı
- pasta/Kredi_Akisi.csv: stok ve akış
- pasta/Yasam.csv: açlık ve sepet
- pasta/C1C2.csv: maaş artı yeni kredi

2025 kopma payı yüzde 22,2. Özel net ile sepet farkı 2024 artı 13,6 puan, 2025 Ağustos eksi 6,6 puan.

Mahsup mekanizmasının simülasyon modeli: [mahsup/](../mahsup/). Ödeme zinciri ağı köprüsü: `python3 odeme_mahsup.py` veya `ODEME_MAHSUP=1 python3 odeme_zinciri.py`.
