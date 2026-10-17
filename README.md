# Zarar Teorisi — stok-akış (SFC) modeli

Türkiye finansal hesapları üzerine stok-akış tutarlı (stock-flow consistent) bir aktarım/zarar modeli. Ham seri TCMB EVDS3’ten 7 Ekim 2026’da çekildi. Birim: bin TL (aksi belirtilmedikçe).

Hazneler: **H** (S.14+S.15 hane), **F** (S.11 firmalar), **B′** (S.12 − TCMB), **K′** (S.13 + TCMB), **D** (S.2 dış alem), **U** (uyumsuzluk).

Ayrıntılı not: [`OKU.txt`](OKU.txt). **Model kusurları (revize):** [`MODEL_KUSURLARI.md`](MODEL_KUSURLARI.md). Ölçülmemiş paylar: [`VARSAYIM_UYARISI.md`](VARSAYIM_UYARISI.md). **Yayın (DOCX):** [`yayin/ZARAR_TEORISI_MINSKY_BULGULAR.docx`](yayin/ZARAR_TEORISI_MINSKY_BULGULAR.docx) — `python3 yayin_zarar_teorisi_docx.py` (kök + `yayin/` kopyası). Aktör uyarıları: [`zarar_teorisi_uyarilar.docx`](zarar_teorisi_uyarilar.docx). Teşhis-tedavi bulgusu: [`belgeler/zt_teshis_tedavi.docx`](belgeler/zt_teshis_tedavi.docx).
Tek sistem kaynak kopyası (birebir çiftler atlandı): [`tek_sistem_kaynak/KAYNAKLAR.md`](tek_sistem_kaynak/KAYNAKLAR.md).

## Ne işe yarar, ne işe yaramaz

Bu bir kapalı muhasebe iskeleti ve kalibrasyon çalışmasıdır; politika reçetesi değildir. Stok-akış kimliği 2021’den beri işlem akışlarında kapanıyor:

`NFP_t = NFP_{t-1} + NL_t (işlem) + R_t (değerleme)`

İskelet her kaydın bir yerde oturmasını gösterir; tanımanın **neden/ne zaman/nasıl** olduğunu kurumsal veya davranışsal olarak açıklamaz ([`MODEL_KUSURLARI.md`](MODEL_KUSURLARI.md)). Hane alt bölünmesi (taban Ha borç payı **%40**), mükellef-hazne, VYS payı, gecikme faizi ve sermaye eşiği ölçüm değildir. `OKU.txt` içinde “DOĞRULANMADI” işaretli satırlar sonuç gibi okunmamalı; F→K ~%24 bulgusu geri çekilmiştir.

## Çalıştırma sırası

```text
evds_cek.py          ham veri (stok / akım / bütçe)        -> *_ham.csv
kalibre_matris.py    v1 matrisler (arşiv; geçerli olan v2)
akis_model.py        v2 panel, SFC matrisi, L/G, Lm
butce_kanali.py      K′ vergi / faiz / harcama + fiscal_shock()
entegre_ve_test.py   bütçe uyumu, geriye dönük test, ikinci tur OLS
kur_kanali.py        döviz maruziyet payı
bilateral_D.py       D satırı, brüt dış borçla kısıtlı L
hane_taksit.py       hane taksit/gelir (karta dahil değil; NL ve L’ye yazılmaz)
```

Bağımlılık: Python 3, `pandas`, `numpy`, `openpyxl`.

```bash
pip install -r requirements.txt
```

`evds_cek.py` ağı kullanır; repodaki `*_ham.csv` dosyaları 7 Ekim 2026 çekimidir, yeniden çekmeden de sonraki adımlar çalışır.

## Haftalık veri güncellemesi

`haftalik_guncelle.py` sekiz EVDS ham dosyasını (37 grup) yeniden çeker, `veri_canli/` altındaki canlı kopyayla karşılaştırır; değişiklik varsa kopyayı ve `SON_GUNCELLEME.md` özetini yazar. Dondurulmuş `*_ham.csv` dosyalarına dokunmaz ve model çıktılarını yeniden hesaplamaz. GitHub Actions ile her Pazartesi 05:17 UTC çalışır (`.github/workflows/haftalik-veri.yml`; zamanlama yalnızca `main` dalındaki dosyayla işler). Ayrıntı ve doğrulama durumu: [`veri_canli/OKU.md`](veri_canli/OKU.md).

## Ana çıktılar

| Dosya | Ne |
| --- | --- |
| `temiz_stok_akis_paneli.csv` | stok, işlem, değerleme; enstrüman × hazne × taraf, 2015-Q1 … 2026-Q1 |
| `sfc_islem_akis_matrisi.csv` | enstrüman × hazne net edinim + NL |
| `L_v2_*`, `G_v2_*`, `Lm_*` | 2026-Q1 matrisleri; zaman serisi `matris_v2_zaman_serisi.csv` |
| `L_bil_*` | D satırı gerçek dış borçla kısıtlı L |
| `butce_aktarim_ceyreklik.csv` | merkezi yönetim kanalı, aylıktan çeyreğe |
| `fx_maruziyet.csv` | hazne × enstrüman × taraf döviz payı |
| `*_ozeti.json` | test özetleri |

## Düzeltilen anomaliler (kısa)

- **A1** EVDS S.2 kalemleri ters etiketliydi; çevrildi (stok ve akımda oran 1,000).
- **A2** S.12 TCMB’yi içeriyordu: B′ = S.12 − S.121, K′ = S.13 + S.121.
- **A3** 2010–2020 D uyumsuzluğu parasal altın ve SDR’de; 2021’den sonra 0. U haznesinde. Nedeni doğrulanmadı.
- **A4** 2010–2014 yalnız yıl sonu; akış/değerleme 2015-Q1’den.
- **A5** K′nin kâr kanalı yoktu; bütçe kanalı eklendi. Mükellef ayrımı varsayım.
- **A6** Toplu L enstrüman heterojenliğini gizliyordu; Lm matrisleri ayrı.
- **A7** D satırı brüt dış borç (borçlu sektöre göre) ile bilateral kısıtlandı.

## Kaynak

TCMB EVDS3, anahtarsız uç nokta. Sendika tarifesi için repodaki Temmuz 2026 PDF’leri ham belge; model onları ölçüm gibi kullanmaz, hane senaryosunun girdisidir.
