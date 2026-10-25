# Etki cephesi kaynak kopyası

Birebir aynı dosyalar yeniden kopyalanmadı. Kopyalananlar kaynak baytlarıyla durur.
Arama: `zarar-teorisi` uzak dalları (31), `saydamonur2002-tech/tek-sistem` `c01b60a`, `saydamonur2002-tech/hekis-model` `6c34a63`, Origin `g-l-mse/*`.

## Origin `g-l-mse/git-harm`

Commit `204fc7c` doğrulanamadı. 2026-10-25 denemesi: `gh api repos/g-l-mse/git-harm/commits/204fc7c` HTTP 404; `origin repo view g-l-mse/git-harm` kimliksiz (`Not authenticated`). Tarih, yazar ve ağaç uydurulmadı. Aşağıdaki tablo kopyanın ilk baytlarıdır; kaynak depodaki `204fc7c` ile aynı olduğu gösterilemedi.

Eklenen ağaç ekteki `git_harm_parcalar.tar.gz` üyeleridir; Next.js arayüzü pakette yoktu. JSON’lar `data/` altında. İlk README `src/data/geriye.json` ve `npm run dev` diyordu; pakette bu yol ve bu uygulama yoktu. Betik artık `data/geriye.json` yazar. README bu kopyayı anlatır, arayüz tarif etmez.

| Kaynak | Kaynak yol | Commit | Hedef | Bayt | SHA-256 |
| --- | --- | --- | --- | ---: | --- |
| `g-l-mse/git-harm` (ek) | `README.md` | `204fc7c` (doğrulanmadı) | `etki_cephesi/git-harm/README.md` | 2434 | `daac129f3c5f0dc71e814b6d78192656afef77e0339d071a5e824b64bffeac06` |
| `g-l-mse/git-harm` (ek) | `scripts/mfin_maliyet.py` | `204fc7c` (doğrulanmadı) | `etki_cephesi/git-harm/scripts/mfin_maliyet.py` | 12364 | `7786b48d49609a64b311420b8c39a2904751995e08918942f448d3fec988ca79` |
| `g-l-mse/git-harm` (ek) | `data/evds_odeme_dengesi_aylik.csv` | `204fc7c` (doğrulanmadı) | `etki_cephesi/git-harm/data/evds_odeme_dengesi_aylik.csv` | 6357 | `61de03fbf2b7e2a03cdadd24d45d9ab758cda81fe94101b0deca64393b56a4b9` |
| `g-l-mse/git-harm` (ek) | `data/geri_kalan.json` | `204fc7c` (doğrulanmadı) | `etki_cephesi/git-harm/data/geri_kalan.json` | 2250 | `f1134ee5d15487efaa1d00cb6439a72b0030ca4cc6b2b942566930b5bae09668` |
| `g-l-mse/git-harm` (ek) | `data/geriye.json` | `204fc7c` (doğrulanmadı) | `etki_cephesi/git-harm/data/geriye.json` | 2910 | `ef006e66c25dccf5d8f46adc76708431bf1d909f441ad4963607b3ae0b476662` |
| `g-l-mse/git-harm` (ek) | `data/havza_kayip.json` | `204fc7c` (doğrulanmadı) | `etki_cephesi/git-harm/data/havza_kayip.json` | 8477 | `a62556bb4442c86fdc327b504be8d8de40574b05aeb18499b54b2d76222d63f9` |

`data/evds_odeme_dengesi_aylik.csv` baytları, `main` üzerindeki `yayin/etki-cephesi-model.zip` içindeki `data/etki_cephesi/gozlem/evds_odeme_dengesi_aylik.csv` ile aynıdır. Ayrı dosya olarak çalışma ağacında yoktu; anlık görüntü bütünü kopyalandı.

Yerel düzeltme: `README.md` ve `scripts/mfin_maliyet.py` ilk bayttan ayrıldı. `data/geriye.json` aynı kaldı (`ef006e66…`, 2910 bayt). Betik bu dosyayı yeniden yazar; çıktı `cmp` ile ilk dosyaya eşittir.

| Dosya | Bayt | SHA-256 |
| --- | ---: | --- |
| `etki_cephesi/git-harm/README.md` | 2481 | `a9d3ed4f62d9edafafe37d235f66bb7433e64b3dd4944eb27edfe3d0e42d5c27` |
| `etki_cephesi/git-harm/scripts/mfin_maliyet.py` | 12340 | `e2f73ddbebe114a68e9cd544ae0e3dc8826c5e7f815d67c46cff317e3674ce55` |

`scripts/isaret_duyarlilik.py` ve `ISARET_DUYARLILIK.md` κ, pol ve üç dolar köprüsünde işaretin nasıl gezdiğini yazar. Model sayısı ve `geriye.json` değişmez.

## Kopyalanan (zarar-teorisi, revize öncesi paket)

`e0cc05f` üzerindeki `yayin/etki-cephesi-model.zip` 599810 bayt, SHA-256 `101b0d2534b01b2bd5309c8bc12b3a50a457b9f1868e3fbfd6634fc8e614ac3f` (aşağıdaki atlanan çiftler tablosu). Bu ağaçtaki dosya sonradan değişmiştir: 587739 bayt, SHA-256 `5b31c6435d860d891e2818fc674c86989f4ad8af7a914df036e13b6ceb680ccb`. İçindeki `reports/etki_cephesi/PROJEKSIYON.json` 467500 bayt, SHA-256 `47c370af6ac1c6b944fd2db47a5b3a31a121374d850a8207711f69deb467ddf2`.

Aşağıdaki zip, `cursor/orta-vade-senaryo-f01a` ucundaki eski pakettir. İlk kopya 362057 bayt, SHA-256 `27649252f1dd7a6173a4841110ffc9166bf87fdcbaaf539c98ebb4c3185a35f1` (dokuz dalda aynı blob). Üye yolları ters bölüydü. `dis_aktör_pay.json` adı arşivde UTF-8 (`c3 b6`) ve bit 11 ile duruyordu; içerik bozuk değildi. Info-ZIP 6.00 ters bölüyü dizine çevirirken bu adı CP437 `dis_akt├╢r_pay.json` olarak açıyordu. Güncel paket zaten `yayin/etki-cephesi-model.zip` olduğu için eski paketin yerine konmadı. Eski paket yerinde yeniden paketlendi: yollar `/`, üye içeriklerinin SHA-256’si aynı, `unzip` adı `dis_aktör_pay.json` olarak açıyor. Yeni arşiv 362057 bayt, SHA-256 `acd88cfea07203252559e45459407eebc804a6b901804ed8ca4f0b6693a196ad`. İlk blob `main` geçmişindedir.

| Kaynak depo / dal | Kaynak yol | Commit | Hedef | Bayt | SHA-256 |
| --- | --- | --- | --- | ---: | --- |
| `zarar-teorisi` `cursor/orta-vade-senaryo-f01a` | `yayin/etki-cephesi-model.zip` | `a9a35a2f256d0f954574fe4a1fc1343937215353` | `etki_cephesi/zarar-teorisi/cursor/orta-vade-senaryo-f01a/yayin/etki-cephesi-model.zip` | 362057 | `acd88cfea07203252559e45459407eebc804a6b901804ed8ca4f0b6693a196ad` (onarım; kaynak blob `27649252…`) |
| `zarar-teorisi` `cursor/orta-vade-senaryo-f01a` | `yayin/README.md` | `a9a35a2f256d0f954574fe4a1fc1343937215353` | `etki_cephesi/zarar-teorisi/cursor/orta-vade-senaryo-f01a/yayin/README.md` | 1444 | `02692c04f0a3762c8f5b2abef1e4a90cd29afbbe57762c947f9573c89862334f` |

Kaynak blob `27649252…` ile aynı olan diğer dal uçları: `cursor/adim3-faiz-satiri-f01a` `f85d403a`, `cursor/borc-prim-f01a` `22721239`, `cursor/dis-borc-sahip-odeyen-f01a` `9e5f1958`, `cursor/faiz-dissallik-f01a` `b0d96d09`, `cursor/kalan-vade-artis-f01a` `43c92959`, `cursor/ndv-altin-artik-f01a` `bdacc55a`, `cursor/sektor-doviz-pozisyon-f01a` `a9952251`, `cursor/zincir-h1h7-sinama-f01a` `23c75956`.

`PROJEKSIYON.json` hiçbir dalda git yolu değildir. Eski zip içinde `reports/etki_cephesi/PROJEKSIYON.json` (420988 bayt, SHA-256 `9e1cd028eab9aa97aa4695ff7d396f071d765a9fa02354f13f3e85abe3761e59`). Güncel zip içindeki sürüm düz dosya olarak çıkarıldı: `etki_cephesi/data/PROJEKSIYON.json` (467500 bayt, SHA-256 `47c370af6ac1c6b944fd2db47a5b3a31a121374d850a8207711f69deb467ddf2`, zip üyesiyle aynı bayt).

`etki_cephesi/git-harm/data/havza_kayip.json` kaynağını `PROJEKSIYON.json bolgesel_net` diye yazar. İki sürümün `senaryolar[].bolgesel_net[].net_endeks` alanları otuz havzada A, B ve C için bu dosyayla aynıdır (0 sapma). Toplam net A −15,247, B −25,727, C −9,899. Düz dosya güncel sürümdür.

## Test

Zip içindeki `tests/` ve `.github/workflows/etki-cephesi.yml` kendi başına çalışmıyordu: iş akışı repo kökünde `etki_cephesi/` bekler, bu depoda o yol harm kopyasıdır. `etki_cephesi/run_model_tests.py` her iki zipi geçici dizine açar, reponun kökünü `_incoming/zarar-teorisi-main` diye bağlar (`akis_model.py`, `akis_model_ozeti.json`, `L_v2_2026-Q1.csv`, `G_v2_2026-Q1.csv`; güncel revize testi bunu ister, dizin zipte yoktur) ve `tests/test_etki_cephesi_*.py` çalıştırır. 2026-10-25: güncel paket 78 geçti, eski paket 27 geçti. `durum_ozeti.py` iki pakette de eksik dosya görmedi. İş akışı `.github/workflows/etki-cephesi-model.yml`.

## Odak: İsrail, İran, Mısır

`etki_cephesi/odak_israil_iran_misir/` mevcut sayılardan üretilir (`olustur.py`). Havza netleri `havza_kayip.json`, aktör defteri `PROJEKSIYON.json`, pay ve 2023 ticaret güncel zip girdisidir. İsrail'in otuz havzada satırı yoktur; havza neti null. Yan kayıtlar (`data/etki_cephesi/gozlem/duyarlilik/`) ana modelin okumadığı dökümdür, bölüme kopyalanmadı.

## Atlanan birebir çiftler

`cursor/odeme-zinciri-kalicilik-f01a` `48676a332a7acf886c4826cd21fff388494020f1` `main`’in atasıdır. Aşağıdaki yollar `main` (`e0cc05f72db17d99d9ccf40147e6b50f876410d1`) ile aynı bayttır.

| Kaynak yol | Bayt | SHA-256 | Zarar-teorisi |
| --- | ---: | --- | --- |
| `yayin/ETKI_CEPHESI_REVIZE.md` | 525336 | `272f26e3e577920f70da0c14168e241e4f83f4dbf1e1d155dfc7c2108385e95c` | `yayin/ETKI_CEPHESI_REVIZE.md` |
| `yayin/KAZANC_KAYIP_MUHASEBE.md` | 2951 | `231575d05138ae80bd4f19d3d94134f6d7a4db640c8dd1909385cf54d1684c2d` | `yayin/KAZANC_KAYIP_MUHASEBE.md` |
| `yayin/SENARYO_KARSILASTIRMA.md` | 6431 | `2cde3af95ef5a25dae5b0be9a6113808f0b2f6c8137ae79fdbd41d58f67be873` | `yayin/SENARYO_KARSILASTIRMA.md` |
| `yayin/GECMIS_PROJEKSIYON.md` | 2423 | `6e1c7e2767cd2f5270d97842ac05c5b0586638306918e5d04dadbce3bddde862` | `yayin/GECMIS_PROJEKSIYON.md` |
| `yayin/README.md` | 6193 | `9c601010a1facc48c997da5922f98901e31f5dad79701a3670accbcd5209d291` | `yayin/README.md` |
| `yayin/etki-cephesi-model.zip` | 599810 | `101b0d2534b01b2bd5309c8bc12b3a50a457b9f1868e3fbfd6634fc8e614ac3f` | `yayin/etki-cephesi-model.zip` |
| `yayin/etki-cephesi-revize.patch` | 448302 | `89be883275cca218f39b9c17f22427fa3f3b8c33479783cbf8235f2edf6df013` | `yayin/etki-cephesi-revize.patch` |
| `yayin/anlatim/etki.html` | 30309 | `2f1372e1d8d91ad40f454c641be63f7cfbec2d93b42f4f8cd9f73aae8c75b333` | `yayin/anlatim/etki.html` |
| `yayin/anlatim/etki_anlatim.srt` | 19308 | `7e7041b578f3542028a5e3f2576d37587ce4fdd839fcb5cc67d6ca563592efbe` | `yayin/anlatim/etki_anlatim.srt` |
| `yayin/anlatim/etki_anlatim.mp4` | 17741603 | `bf5d16a1b5d5a753951e0783982dca28b955acc84e0a32152b1a43def62b7331` | `yayin/anlatim/etki_anlatim.mp4` |
| `yayin/anlatim/yayin_etki_video.py` | 30182 | `1128db3683a20ab7cb48c5720c8cd465951d3e2be70f9e015db0fe37da5789f1` | `yayin/anlatim/yayin_etki_video.py` |
| `yayin/BANT_SINAMA.md` | 11138 | `4ce6be55a888a6785c611dd18f17be97f4a2326ccda7f7ee46e63c58b4c583e4` | `yayin/BANT_SINAMA.md` |
| `yayin/C_DINAMIK_OLCUT.md` | 2268 | `c3e46489511ab01212884c397236d81393dea54ce21bbe18c89823589c69028d` | `yayin/C_DINAMIK_OLCUT.md` |
| `yayin/DURDURMA_YOLU_KURAL.md` | 6589 | `616df6b60aecf9f8f2b1c379df71eb2de3ed4451542ba5e3832e08d7111e28ee` | `yayin/DURDURMA_YOLU_KURAL.md` |
| `yayin/GIDISAT_RAPORU.md` | 3678 | `5335689f5993b1cece173856adb5c28937163cc4fa353f7d0edc41e9f2572620` | `yayin/GIDISAT_RAPORU.md` |
| `yayin/GORECELI_KONUM.md` | 5642 | `61bca3c0ef49b2a5706dcec8ef08bd159450b5ed0b8f4cf50dd168f07c4670c7` | `yayin/GORECELI_KONUM.md` |
| `yayin/HAVZA_KAZANAN_KISA_VADE.md` | 4160 | `b999163fd5925532167ecea36e5bcc09901da00411b632205b4bb3d1fec88869` | `yayin/HAVZA_KAZANAN_KISA_VADE.md` |
| `yayin/IKAME_CIFT_SAYIM.md` | 887 | `4e43f44fab8ad3da25c287c0bed72fd6fd7380d8b1955c63f630c62ecd69200d` | `yayin/IKAME_CIFT_SAYIM.md` |
| `yayin/OLASILIK_DUYARLILIK.md` | 2186 | `75a22b2c2b0fe59b902523babafd93c4ba94336cbfb945620aefa8ecc4ef790d` | `yayin/OLASILIK_DUYARLILIK.md` |
| `yayin/OLASILIK_KAPILAR.md` | 2603 | `06a44129d6a1ecf420a7695fd26001a7213c298bd8328e45cd8d2893c1161441` | `yayin/OLASILIK_KAPILAR.md` |
| `yayin/OLU_AGIRLIK_AYRISMA.md` | 1993 | `617b2a73546262e3229da1d95d2943766d25d3ef2f38a444045047030fa07a4b` | `yayin/OLU_AGIRLIK_AYRISMA.md` |
| `yayin/TABAN_DUYARLILIK.md` | 7712 | `8ad33e0bc4a7ae42df397835783b311375fe4f1c97e821f9e02fb919bab13737` | `yayin/TABAN_DUYARLILIK.md` |
| `yayin/TR_OLCEK_SINAMA.md` | 5778 | `cfa45c85234e71567b5df9edec15ef902d258461046678673451d9d8b8179a4e` | `yayin/TR_OLCEK_SINAMA.md` |
| `yayin/URETIM_KATMAN_MODEL.md` | 2944 | `3fbf46a7bf5066a5de555eb04301d0e64e0a4b2928dadbe0b07773d861d02def` | `yayin/URETIM_KATMAN_MODEL.md` |
| `yayin/ZARAR_DURDURMA_SENARYOSU.md` | 3343 | `176bf0e26e5929ecb3f556a1998783c58fe20f28abf8263c8041b9d5139d6d0e` | `yayin/ZARAR_DURDURMA_SENARYOSU.md` |

`yayin/TEK_SISTEM_SORUN_COZUM.docx` dalda `main`’den farklıdır (dal 44762 bayt `6f9ceace…`, main 44771 bayt `d33be881…`). Metinde «etki cephesi» geçmez; kuram kopyası sayılmadı.

`tek-sistem` ve `hekis-model` içinde «etki cephesi» / «etki-cephesi» eşleşmesi yok. Başka `g-l-mse/*` deposu listelenemedi.
