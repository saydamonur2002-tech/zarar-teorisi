# Ülke modeli testi

Çalıştır: `python3 ulke_model_test.py`.

Tam model çalışan: **0 / 16**.

Kapı: yazılan stok, fatura kuponu, beş adım bir arada. Üçü birlikte yoksa ülke kalır.
Yazılan kapısı geçen: 6. Fatura kapısı geçen: 0. Beş adım bir arada: bulunamadi (18 sorgu).

Bağımsız toplam, ölçüm: Türkiye yerli para 6.407,0 + döviz 1.745,8 = 8.152,8. Arjantin yerleşim 155,312 + 297,345 = 452,657. Arjantin para 190,904 + 261,753 = 452,657.
Yerli alacaklı = stok − yurt dışı olan satırda toplam kurulumdur. Ayrı ölçüm sayılmaz.

Türkiye 2029 faiz-37 faturası 5.338, `orta_vade_senaryo.json`. Bu koşuya girmez.

| Ülke | Kimlik | Yazılan | Fatura | Adım kaydı | Beş adım | Çalışıyor |
| --- | --- | --- | --- | --- | --- | --- |
| Türkiye | kurulum | kaldi | veri_yok | taramada_yok | bulunamadi | hayir |
| Japonya | bagimsiz_gecti | gecti | veri_yok | taramada_yok | bulunamadi | hayir |
| ABD | veri_yok | kaldi | veri_yok | taramada_yok | bulunamadi | hayir |
| Çin | bagimsiz_gecti | gecti | veri_yok | uygulandi_tarihsel; adım 3 tersi, kredi enjeksiyonu | bulunamadi | hayir |
| Arjantin | bagimsiz_gecti | kaldi | veri_yok | taramada_yok | bulunamadi | hayir |
| Brezilya | kurulum | gecti | veri_yok | adim4_5_kismi; yeni inşa, 1964 | bulunamadi | hayir |
| Almanya | veri_yok | kaldi | veri_yok | taramada_yok | bulunamadi | hayir |
| Fransa | veri_yok | kaldi | veri_yok | taramada_yok | bulunamadi | hayir |
| İtalya | veri_yok | kaldi | veri_yok | ozel_platform | bulunamadi | hayir |
| İspanya | veri_yok | kaldi | veri_yok | ozel_platform; adim5_bulundu | bulunamadi | hayir |
| Euro alanı | kurulum | gecti | veri_yok | taramada_yok | bulunamadi | hayir |
| İngiltere | veri_yok | kaldi | veri_yok | taramada_yok | bulunamadi | hayir |
| Güney Kore | kurulum | gecti | veri_yok | taramada_yok | bulunamadi | hayir |
| Meksika | veri_yok | kaldi | veri_yok | adim2_4_kismi; nesne banka kredisi, 1995 | bulunamadi | hayir |
| Polonya | kurulum | gecti | veri_yok | taramada_yok | bulunamadi | hayir |
| Endonezya | bagimsiz_gecti | kaldi | veri_yok | taramada_yok | bulunamadi | hayir |

Aralık 0,15'te etiket değişen: 0. 0,25'te etiket değişen: Euro alanı, Türkiye.

## Ne denmez

- Model bu ülkelerde çalışıyor denmez. Tam kapı 0 ülkede kapandı.
- Kurulum toplamı bağımsız ölçüm denmez.
- Kısmi adım kaydı, beş adımın kurulduğu anlamına gelmez.
- 5.338 bu testin faturası denmez. Ayrı dosyadadır.
