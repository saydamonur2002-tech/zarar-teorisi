# Ekonomik direnç (aktör × senaryo)

**Senaryo; ölçüm değil.** Rant/kira kanalı yok; stok-akış ve gelir tablosu proxy.

Tanım: direnc_ekonomik_% = aktör ekonomik kayıp / max(|ΔNFP|, faaliyet×ufuk_yil)

F faaliyet/finansman referansı (ölçüm, senaryo değil): **0.839** (2024).

## Karşı aktörler (2031-Q4, mevcuta göre kayıp)

| Senaryo | Aktör | Kayıp (milyar) | Payda | **Direnç ekonomik %** |
| --- | --- | ---: | ---: | ---: |
| mevcut | H | 0.0 | 11539.03 | 0.0 |
| mevcut | F | 0.0 | 34448.0 | 0.0 |
| mevcut | B | 0.0 | 7994.42 | 0.0 |
| mevcut | K | 0.0 | 40000.0 | 0.0 |
| uc_kural_kilitli | H | 8882.7 | 11539.03 | 76.98 |
| uc_kural_kilitli | F | 32959.1 | 34448.0 | 95.68 |
| uc_kural_kilitli | B | 968.2 | 7994.42 | 12.11 |
| uc_kural_kilitli | K | 0.0 | 40000.0 | 0.0 |
| maliyet_ucuz_revize | H | 4467.55 | 11539.03 | 38.72 |
| maliyet_ucuz_revize | F | 834.9 | 34448.0 | 2.42 |
| maliyet_ucuz_revize | B | 0.0 | 7994.42 | 0.0 |
| maliyet_ucuz_revize | K | 118.15 | 40000.0 | 0.3 |

## Toplam ağırlıklı direnç

- **mevcut**: 0.0%
- **uc_kural_kilitli**: 58.07%
- **maliyet_ucuz_revize**: 14.32%

## Kalemler (özet)

- **H**: gelir_dilim, emlak_gelir_dususu, kredi_hacmi_kisit, finansman_hacmi, NFP_kotulesme
- **F**: ucret_yuku, finansman_hacmi, NFP_kotulesme
- **B**: finansman_hacmi, NFP_kotulesme
- **K**: butce_NL_kaybi, makas_transfer (revize), NFP_kotulesme

## Revize vs sert (yorum)

Sert yol **F ücret yükünü** ve **H kredi kısıt çeyreklerini** büyütür → F/H direnç ekonomik payı yükselir. Revize yol **emlak/gelir dilimi** kaybını ve **K makas** kalemini öne çıkarır; F ücret yükü görece düşük kalır.

`direnc_yuzdesi.py` ile karşılaştırma: Paralel okuma; direnc_yuzdesi rant/kira kalemleri kullanır, bu modül kullanmaz.

## Ne denmez

- Rant amortisman oranı veya kira ranti hesabı değildir (`rant_aktor.py` ayrı).
- Lobi gücü / seçim modeli değildir.
