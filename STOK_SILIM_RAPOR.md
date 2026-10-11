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

## 3. Özet (yalnız karşı bacaklı satırlar)

- **Araç ayrı** silinen/stok: — (skor satırı yok; silinen 0 / stok 0) — aynı araçta karşı bacak metinde yok (kredi tek yön, mevduat tek yön).
- **Araç birleşik, tekil çift** (3 çift): silinen **18000** milyar TL (F–PFK 7.195, H–PFK 6.772, PFK–ROW 4.033; tek sayım); iki bacak brüt 56696; oran 31.7% (18000 / 56696 milyar TL). Model tercihi; kısmi çiftler; **H-S’ye girmez**.

## 4. H-S

**test_edilemez** — H-S yalnız araç ayrı ile skorlanır; araç ayrı boş. Akış 42.7% stok dosyasında yok. Birleşik oran “karışım var/yok” kanıtı değildir.

## 5. Girmeyen kalemler (F yükümlülük)

| Kaynak | Hisse+özk. | Diğer borç | Toplam dışarıda |
| --- | --- | --- | --- |
| TCMB 2026-I V. Firmalar (141.474 milyar) | 48.6% | 32.8% | **81.4%** |
| EVDS F konsolide stok (ayrı stok, kıyas değil) | 35.5% | 12.6% | 48.1% |

`stok_dar` koşulu (rapor payı >50%): **sağlanıyor**. Etiket yine de yazılmaz: araç ayrı ölçülmeden H-S kapalı. Rapor doğrulaması: metinde 141.474 / 48,6 / 32,8 bulundu ([V. Firmalar](https://www.tcmb.gov.tr/wps/wcm/connect/44363718-828b-4c6a-95e8-066078e93247/V.+Firmalar+%28Finansal+Olmayan+Kurulu%C5%9Flar%29.pdf?CACHEID=ROOTWORKSPACE-44363718-828b-4c6a-95e8-066078e93247-p-TY44k&MOD=AJPERES)).

## 5b. Hazne adları

PFK parasal ve finansal kuruluş (banka ayrılmadı); **GY** genel yönetim; repo **K** (bankacılık dışı finansal) bu dosyada kullanılmaz.

## 6. Dosyalar

`stok_silim.csv`, `stok_silim_sonuc.json`, `stok_silim_arama_gunlugu.jsonl`

```bash
python3 stok_silim.py
```
