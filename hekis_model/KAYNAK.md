# Kaynak

[saydamonur2002-tech/hekis-model](https://github.com/saydamonur2002-tech/hekis-model) `6c34a63` olduğu gibi kopyalandı (`.git`, `.github`, `__pycache__` hariç). Kod, veri notları ve belgeler hekis-model'in kendi işidir; bu depoda yeniden ölçülmedi.

Kapsam: İstanbul (Anadolu 7 büyükşehir ayrı), veri Ağustos–Ekim 2026, kişisel modelleme. Üç defter: mülkiyet, oturan, senet.

Bu depodaki bağlar:

- `../hekis_enflasyon.py` — HEKİS enflasyon patikası (`hekis/bind.py inflation_paths`, `data/istanbul_2026.json`) → stok-akış NFP reel değişimi.
- `../diger_repo_kopru.py` — HEKİS nesneleri (kira akışı, boş stok, yerleşen hane, bedel, sub, senet) commit etiketiyle yan yana; H-R / H-R2; yan kontrol (KFE reel, konut kredisi stoku EVDS). Çıktı `../DIGER_REPO_KOPRU.md`, `../diger_repo_kopru.csv`.

Testler buradan koşar: `cd hekis_model && python3 -m unittest discover -s tests` (86 test).
