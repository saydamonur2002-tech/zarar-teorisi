# Etki cephesi modeli: revize sonucu

Kaynak: `zarar-teorisi` dalı `cursor/odeme-zinciri-kalicilik-f01a`, `yayin/etki-cephesi-model.zip`.
Doğrulama: yama temiz zip çıkarımına uygulandı, `run_all.py` tek komutla kararlı duruma vardı (özet `f00bd56ca4523e83`),
**38 test geçti** (27 mevcut + 11 yeni; bir mevcut testin işareti güncellendi). Orijinal pipeline zip'teki raporları birebir yeniden üretiyor
(fark yalnız CRLF/LF ve bir Windows yol ayracı).

## Düzeltilen hatalar

| # | Hata | Düzeltme |
|---|---|---|
| 1 | `stok_silim_tavan` (0,2582, üst sınır, başka nesne) gerçekleşmiş silinme gibi uygulanıyordu: F.4 25.339,8 → 18.797,1 | Baz yol sabit, silinen ölçülmedi. 0 / 0,10 / 0,20 varsayım bandı. 0,2582 yalnız tutarlılık kontrolü |
| 2 | λ = 0,7181 = 1 − 0,0728/0,2582 (iki üst sınırın oranı) `simulate`'e λ diye gidiyordu | λ açık senaryo parametresi, varsayılan 0,5, bant 0,25/0,5/0,75 |
| 3 | Karşı bacağı tanımsız "refah" darbeleri SFC'ye girip tüm sektörleri artıya çekiyordu (Σ = +0,586 tr TL) | `dissal` işareti: SFC dışında raporlanır, kapanış farkı ilan edilir |
| 4 | 2026-Q1 matrisi 2024 ortalama kuruyla (32,87) çevriliyordu | Matris dönemi kuru (2026-Q1 = 44,38) |
| 5 | Finans katmanı işaret dönüşü ölçüm gibi yayınlanıyordu | "varsayım çarpanlı ham" etiketi |
| 6 | Uygulanabilirlik özeti sabit metindi ("10 yılda TR net iyileşir") | Özet sayıdan türetilir; beklenen karışımda iyileşme yoksa engel olarak yazılır |
| 7 | Pipeline kendi çıktısını girdi okuyor: yamalı sürümde tek koşu ara durum bırakıyordu | `run_all.py` kararlı duruma kadar geçer (en çok 5), `RUN_ALL_KARARLILIK.json` yazar |
| 8 | **D'nin çift muamelesi:** dış rant F'ye "zarar" yazılıp L ile D'ye kayıp yayılıyordu (D −0,223) ve ayrıca "D kârı" G ile yerli sektörlere dağıtılıyordu (D'de kalmıyordu) | Rant **F→D transferi**: F −A, D +A, doğrudan NFP, toplam sıfır. Ödeyen F, transfer payı %100 (kullanıcı kararı): 22.550 mn $ × 44,38 = 1,001 tr TL; kapsam dışı rant yok. `bolge_stok_akis` TR net = H+F+B+K (eski formül D'yi 0,45 ile ayrıca düşüyordu) |

## Önce / sonra (kararlı durum)

| Çıktı | Önce | Sonra |
|---|---|---|
| SFC entegre etki H/F/B/K/D (tr TL) | 0,119 / 0,153 / 0,088 / 0,117 / 0,109 (Σ +0,586) | **0 / −1,001 / 0 / 0 / +1,001 (Σ 0)** |
| SFC kapanış | beyan yok | **kapanış_ok = True** (Σ darbe 0) |
| Senaryo başına D'ye giden rant A / B / C (tr TL) | −0,134 / −0,540 / +0,109 (eski işaret: D kayıp taşıyordu) | **1,886 / 3,482 / 1,001** (C en az, B en çok kaçırır) |
| Bölge: TR sfc_net | +0,223 | −1,001 |
| Dışsal enjeksiyon (SFC dışı) | SFC'nin içindeydi | +0,892 tr TL, ayrı raporlanıyor |
| F.4 stok, 2036 | 18.797,1 mr TL | 25.339,8 (baz); bant 22.805,8 / 20.271,8 |
| Finans katmanı TR net (vekil) | +0,241 (sıfır yılı 2035) | **−0,489** (2037) |
| Zarar-çözüm katmanı TR net | −11,112 | −13,113 |
| Beklenen TR 10 yıl | −16,666 | −18,186 |
| Uygulanabilirlik skoru / C / beklenen | 66,4 / 71,3 / 57,3 | **62,7** / 67,1 / 54,5 |
| Senaryo skorları A / B / C | 51,0 / 50,3 / 79,7 | 50,1 / 49,4 / 73,0 |
| C yolu TR net, 10. yıl (taban → son) | −17,19 → −11,80 | −17,19 → −13,10 |
| Beklenen karışımın iyileşmesi | +0,087 skor (özet "iyileşir" diyordu) | −1,00 vekil: iyileşme yok, engel olarak yazıldı |
| Lm × rant, kur | 32,87 | 44,38; kapanış_ok = False (Σ x = +0,178) |

Not: karar hâlâ `uygulanabilir_kosullu`, ama skor eşiğin (62) yalnız 0,7 üstünde.

## Düzeltilmeyen / açık
- Ödeyenin yalnız F olması kullanıcı kararıdır; rantın bir kısmını H veya kamu ödüyorsa transfer F'ye fazla yazılır.
- `bolge_stok_akis`, `lm_rant_sektor` darbeleri sıfır toplamlı değil: yalnız ilan edildi.
- λ ve κ ölçülmüş değil. Sonuçlar senaryo bandıdır. Senaryo olasılıkları (0,22 / 0,18 / 0,60) ölçülmüş değil.
- USD akışları 2024 çapasından, matris 2026-Q1: yalnız kur düzeltildi.
- `_incoming/zarar-teorisi-main` bu pakette yok; `zarar-teorisi` reposunun `main` kopyası oraya konmalı.

## Uygulama
```
cd etki-cephesi-model; patch -p1 < etki-cephesi-revize.patch
python etki_cephesi/run_all.py     # kararlı duruma kadar geçer
python -m pytest tests -q
```
Yama kaynak, veri ve test dosyalarını içerir. Raporlar ve `data/etki_cephesi/kalibre/*.json` pipeline ürünüdür.
`etki-cephesi-model-revize.zip` aynı sonucu hazır (raporlar yenilenmiş) içerir.
