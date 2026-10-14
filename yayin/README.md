# Yayın dosyaları

| Dosya | Açıklama |
| --- | --- |
| [ZARAR_TEORISI_MINSKY_BULGULAR.docx](./ZARAR_TEORISI_MINSKY_BULGULAR.docx) | Bulgular, çözüm yöntemi, mekanizma, sınırlar (Minsky / kur / borç / yaşam) |
| [TEK_SISTEM_SORUN_COZUM.docx](./TEK_SISTEM_SORUN_COZUM.docx) | Beş adımın sorunu ve çözümü, parça parça |
| [anlatim/index.html](./anlatim/index.html) | Etkileşimli anlatım. Kaydırıcılar varsayım bandını gezdirir |
| [anlatim/tek_sistem_anlatim.mp4](./anlatim/tek_sistem_anlatim.mp4) | Aynı anlatımın videosu, yaklaşık 13 dakika |
| [anlatim/hukuk.html](./anlatim/hukuk.html) | Dosyadaki hukuk: temlik, kira ipi, boş oda taslağı |
| [anlatim/hukuk_anlatim.mp4](./anlatim/hukuk_anlatim.mp4) | Aynı hukukun analojik videosu, kadın ses, yaklaşık 12 dakika |
| [anlatim/etki.html](./anlatim/etki.html) | Etki cephesi: fabrika, beş halka, uluslararası defter, üç yolun kaydırıcısı |
| [anlatim/etki_anlatim.mp4](./anlatim/etki_anlatim.mp4) | Aynı anlatımın videosu, 19,5 dakika |
| [etki-cephesi-model.zip](./etki-cephesi-model.zip) | Etki cephesi model paketi (revize: SFC köprüsü hataları düzeltildi). Video eski sürümü anlatır |
| [etki-cephesi-revize.patch](./etki-cephesi-revize.patch) | Revize yaması (CRLF; `patch -p1`). Zip bu yamayla yeniden üretildi |
| [ETKI_CEPHESI_REVIZE.md](./ETKI_CEPHESI_REVIZE.md) | Düzeltilen hatalar, önce/sonra sayıları, açıkta kalanlar |
| [OLASILIK_DUYARLILIK.md](./OLASILIK_DUYARLILIK.md) | C senaryosu olasılığı 0,30–0,80 duyarlılık bandı (olasılık ölçülmedi; yeni olasılık üretmez) |
| [C_DINAMIK_OLCUT.md](./C_DINAMIK_OLCUT.md) | C'nin gerçekleşmesini ölçen dinamik ölçüt (sıralı Bayes, EVDS merkez sızıntı oranı); güç analizi: bu gösterge C'yi ayırt edemez |
| [OLASILIK_KAPILAR.md](./OLASILIK_KAPILAR.md) | P(C) ölçülebilir kapılarla yeniden kuruldu: tekdüze prior, EVDS borç çevirme kapısı, kapı sonuç tablosu; tek kapı karar eşiğini geçirmez; olabilirlikler geçmişten (`_gecmis.py`: senaryo = geçmiş rejimi), ana pipeline bu olasılığı kullanır (`_olasilik.py`, döngü yok) |
| [SENARYO_KARSILASTIRMA.md](./SENARYO_KARSILASTIRMA.md) | A, B, C yan yana: aynı 9 bölüm, aynı alanlar (zip içinde `SENARYO_RAPOR_{A,B,C}.md`); üretim/finans katmanlarının senaryoya özgü gerçekleşmesi (g_u, g_f) ve F.4 stok yolunun senaryodan bağımsızlığı notuyla |
| [GECMIS_PROJEKSIYON.md](./GECMIS_PROJEKSIYON.md) | Salt geçmiş projeksiyonu: yalnız EVDS gözlem serisinden ileri uzatma (senaryo, olasılık, katman çarpanı yok); geriye test: üç yöntem de 2023–2025'i eksik tahmin etti |

Yenilemek: repo kökünde `python3 yayin_zarar_teorisi_docx.py` — çıktı kökte oluşur; kopya buraya `cp ZARAR_TEORISI_MINSKY_BULGULAR.docx yayin/` ile alınır.

**Dal:** `cursor/odeme-zinciri-kalicilik-f01a` (PR #5). `main` üzerinde yoksa bu dalı checkout edin veya PR’ı merge edin.
