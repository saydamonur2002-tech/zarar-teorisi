# Stok silimi raporu (2026-Q1)

## 1. Yöntem

| Yöntem | Anlam |
| --- | --- |
| **arac_ayri** | Muhasebe: kredi, mevduat, senet ayrı mahsup |
| **arac_birlesik** | Model tercihi: aynı çiftte üç araç tek havuz |

Akış mahsupu (~42,7% brüt servis) bu tabloda **yok**.

## 2. Kaynak sınırı

- PDF: [VII. Kimden-Kime](https://www.tcmb.gov.tr/wps/wcm/connect/bf500c17-e3d5-40bd-8475-370caca9c6fd/VII.+Kimden-Kime+Tablolar%C4%B1.pdf?CACHEID=ROOTWORKSPACE-bf500c17-e3d5-40bd-8475-370caca9c6fd-p-TY4sh&MOD=AJPERES) — matris **grafik**; sayılar metin + alıntı satırları.
- Tam çift matrisi Excel: TCMB Veri Tabloları sayfasında statik link **bulunamadı** (arama günlüğü).
- B haznesi (TCMB ayrılmış banka) bu tabloya **yapıştırılmadı**.

## 3. Özet oranlar (yalnız karşı bacaklı satırlar)

- Araç ayrı silinen/stok: — (skor satırı yok; silinen 0 / stok 0)
- Araç birleşik: 63.5% (36000 / 56696 milyar TL)

## 4. H-S

**test_edilemez** (akış 42.7% ile kıyas; stok dosyasına yazılmaz)

## 5. Girmeyen kalemler (F yükümlülük, EVDS)

- Hisse payı: 35.5%
- Diğer borç payı: 12.6%

## 6. Dosyalar

`stok_silim.csv`, `stok_silim_sonuc.json`, `stok_silim_arama_gunlugu.jsonl`

```bash
python3 stok_silim.py
```
