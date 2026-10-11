# Diğer repo köprüsü

Çalıştır: `python3 diger_repo_kopru.py`. Çıktı: `diger_repo_kopru.csv`, `diger_repo_kopru_sonuc.json`.

Kural: sayı kaynak commit'ten; kullanıcı kaynak repoları revizyonla güncelleyecek, köprü eski sayıyı güncel diye yazmaz. Akış yüzdesi, stok tavanı, MY, kalan pay ve tek-sistem köprüsü bu dosyaya taşınmadı. HEKİS TÜFE puanı, Gini ve yerleşen hane zarar-teorisi serisine yapıştırılmadı; yan yana durur.

## 1. Repo tablosu

| Repo | Commit | Tarih | Ne var | Durum |
| --- | --- | --- | --- | --- |
| [hekis-model](https://github.com/saydamonur2002-tech/hekis-model) | 6c34a63 | 2026-10-08 | HEKİS: İstanbul ve Anadolu (7 büyükşehir) ayrı sistem; üç defter mülkiyet/oturan/senet; hekis/ paketi, data/ notları, 86 test; kopyası hekis_model/ | kopyalandı |
| [tek-sistem](https://github.com/saydamonur2002-tech/tek-sistem) | c01b60a | 2026-10-04 | RAPOR.md beş adım, model/pasta ve model/gercek CSV, mahsup paketi; a9344f1 ile bağlı | bağlı (a9344f1); yeniden kopyalanmadı |
| [modeller](https://github.com/saydamonur2002-tech/modeller) |  |  | bulunamadı; 3 sorgu denendi (gh repo view, users/.../repos, search/repositories). hekis-model README.md 'Not kopyasi' diye atıf yapar; herkese açık kayıt yok. | bulunamadı |

## 2. Nesneler (`diger_repo_kopru.csv`)

| Repo | Commit | Dosya | Nesne | Değer | Birim | Dönem | Durum |
| --- | --- | --- | --- | ---: | --- | --- | --- |
| hekis-model | 6c34a63 | `hekis/bind.py; data/istanbul_2026.json` | kira akışı: havuz kirası 2+1 | 20,000 | TL/ay | 2026-08 | modellendi |
| hekis-model | 6c34a63 | `hekis/kira.py; data/ykke_2026_08.json` | kira akışı: YKKE gecikmeli yeniden fiyatlama |  |  | 2018-01..2026-08 | modellendi |
| hekis-model | 6c34a63 | `data/istanbul_2026.json` | boş stok: İstanbul gözlem aralığı (alt) | 225,000 | konut |  | modellendi |
| hekis-model | 6c34a63 | `SISTEMLER.md` | boş stok tam ölçek: İstanbul | 450,000 | konut | tam ölçek (7. yıl) | modellendi |
| hekis-model | 6c34a63 | `SISTEMLER.md` | boş stok tam ölçek: Anadolu (7 şehir) | 664,000 | konut | tam ölçek (7. yıl) | modellendi |
| hekis-model | 6c34a63 | `hekis/zones.py` | yerleşen hane: İstanbul tam ölçek (koşu) | 36,963 | hane | tam ölçek, erozyonsuz | modellendi |
| hekis-model | 6c34a63 | `SISTEMLER.md` | yerleşen hane: Anadolu tam ölçek | 66,900 | hane | tam ölçek | modellendi |
| hekis-model | 6c34a63 | `hekis/zones.py` | bedel geliri: İstanbul (koşu) | 9.37 | milyar TL/yıl | tam ölçek, erozyonsuz | modellendi |
| hekis-model | 6c34a63 | `hekis/zones.py` | sübvansiyon: İstanbul yıl 1 (koşu) | 3.92 | milyar TL/yıl | tam ölçek, erozyonsuz | modellendi |
| hekis-model | 6c34a63 | `SISTEMLER.md` | sub / bedel 7. yıl+ (erozyonlu): İstanbul | 3.92 | milyar TL/yıl (sub) | 7. yıl+ | modellendi |
| hekis-model | 6c34a63 | `SISTEMLER.md` | sub / bedel 7. yıl+ (erozyonlu): Anadolu (7 şehir) | 3.18 | milyar TL/yıl (sub) | 7. yıl+ | modellendi |
| hekis-model | 6c34a63 | `SISTEMLER.md` | yerel TÜFE puanı: İstanbul | -0.3 | puan | tam ölçek | modellendi |
| hekis-model | 6c34a63 | `SISTEMLER.md` | ΔGini: İstanbul | -0.00066 | Gini | tam ölçek | modellendi |
| hekis-model | 6c34a63 | `SISTEMLER.md` | yerel TÜFE puanı: Anadolu (7 şehir) | -0.35 | puan | tam ölçek | modellendi |
| hekis-model | 6c34a63 | `SISTEMLER.md` | ΔGini: Anadolu (7 şehir) | -0.00036 | Gini | tam ölçek | modellendi |
| hekis-model | 6c34a63 | `hekis/senet.py; data/SENET.md` | HEKİS senedi: ihraç (İstanbul baz) | 89.20 | milyar TL | 2026-10-05 tasarım | modellendi |
| tek-sistem | c01b60a | `model/RAPOR.md` | hedef primli endeksli senet |  |  | 2026-10-04 metin | taslak |
| hekis-model + tek-sistem | 6c34a63 + c01b60a | `hekis/senet.py ↔ model/RAPOR.md` | HEKİS senedi ↔ hedef primli senet |  |  |  | esitlenmez |
| tek-sistem | c01b60a | `model/RAPOR.md` | adım 5: kira kolu |  |  |  | olculmedi |
| hekis-model | 6c34a63 | `hekis/zones.py; hekis/bind.py; hekis/kira.py` | adım 5: kira kolunun modeli |  |  | 2026-10-08 | modellendi |
| hekis-model | 6c34a63 | `PILOT.md` | sistem aktifi / mevduat (HEKİS hesabı) | 0.0029 | oran | pilot notu | modellendi |
| modeller |  | `` | HEKİS kapalı kira-üretim devresi notu |  |  |  | taslak |

Notlar satır sırasıyla:

- kira akışı: havuz kirası 2+1: policy_rent 15000/10000 1+1/1+0, aidat 3000; kaynak alanı 'model varsayimi, gozlem degil'. Gözlem girdisi ayrı: İstanbul ort. kira 45,510 (Emlakjet-Endeksa), Esenyurt medyan 20,000.
- kira akışı: YKKE gecikmeli yeniden fiyatlama: TCMB YKKE girdisiyle hipotez: TÜFE kira_t ~ YKKE yıllık_(t−12); tek nokta; kimlik testi değil (dosya başlığı).
- boş stok: İstanbul gözlem aralığı (alt): elektrik aboneliği tabanlı; İBB 450,000–750,000; stok 4,500,000. Yöntem farkı, tek sayı değil (kaynak alanı). Model girdisi; bu depoda ölçülmedi.
- boş stok tam ölçek: İstanbul: metin rakamı; en olası senaryo, erozyon %25
- boş stok tam ölçek: Anadolu (7 şehir): metin rakamı; en olası senaryo, erozyon %25
- yerleşen hane: İstanbul tam ölçek (koşu): run_three_zone() varsayılan; kapsam uygun kiracıya 6.6%. Ölçüm değil.
- yerleşen hane: Anadolu tam ölçek: metin rakamı; Kocaeli, Konya, Adana fiyat/kira yer tutucu (SISTEMLER.md sınırlar)
- bedel geliri: İstanbul (koşu): genel %1, lüks %5; parçalar 1.06, 1.76, 6.54 (HEKİS/tampon/lüks); lüks tahsilat %40 varsayım
- sübvansiyon: İstanbul yıl 1 (koşu): bedel/sub 2.39; 20 yıl reel yük 83.8 milyar TL
- sub / bedel 7. yıl+ (erozyonlu): İstanbul: bedel 7.03 milyar TL/yıl; metin rakamı
- sub / bedel 7. yıl+ (erozyonlu): Anadolu (7 şehir): bedel 5.02 milyar TL/yıl; metin rakamı
- yerel TÜFE puanı: İstanbul: ulusal -0.055 (hane payı ile ölçekli); kira esneklik 0,6: -4.5%. zarar-teorisi TÜFE/NFP serisine girmez (hekis_enflasyon.py ayrı patika).
- ΔGini: İstanbul: Δyoksulluk -0.16 puan; gelir dağılımı ulusal lognormal varsayım
- yerel TÜFE puanı: Anadolu (7 şehir): ulusal -0.1 (hane payı ile ölçekli); kira esneklik 0,6: -5.2%. zarar-teorisi TÜFE/NFP serisine girmez (hekis_enflasyon.py ayrı patika).
- ΔGini: Anadolu (7 şehir): Δyoksulluk -0.085 puan; gelir dağılımı ulusal lognormal varsayım
- HEKİS senedi: ihraç (İstanbul baz): boş stok karşılığı; anapara TÜFE endeksli, reel kupon 0; prim min(0,10; 0,04×(fiziki endeks−1)); sahip payı 1/7 (tasarım payı); dış alıcıya kapalı; ikincil piyasa yok, 20 yıl kilit; itfa yalnız sistem içinde
- hedef primli endeksli senet: anapara lira, enflasyona endeksli; kupon faiz değil, üretim hedefi tutarsa tasarruftan prim (ithal ikamesi döviz tasarrufu payı); çıkış senedi başkasına satmak; ihraç büyüklüğü ve prim formülü yok; kod yok
- HEKİS senedi ↔ hedef primli senet: ihraç farklı (boş konut stoku 89,2 vs tanımsız); prim farklı (fiziki endeks, 1/7 vs ithal ikamesi tasarrufu); çıkış farklı (20 yıl kilit, ikincil piyasa yok vs satış). H-R2 ayri.
- adım 5: kira kolu: 'Bu kol ölçülmedi.' Tek-sistem cümlesi durur.
- adım 5: kira kolunun modeli: HEKİS kira-havuz-oturan modeli var; ölçüm değil; İstanbul ve Anadolu ayrı; tek-sistem adım 5 etiketi değişmez. H-R modellendi.
- sistem aktifi / mevduat (HEKİS hesabı): 'Sistem aktifi mevduatın %0,29'u, senet %0,28'i' (PILOT.md). Bu deponun mevduat stoklarıyla yeniden oranlanmadı.
- HEKİS kapalı kira-üretim devresi notu: bulunamadı; 3 sorgu denendi. hekis-model README: 'Calisma taslagidir, dogrulanmis bir kamu maliyesi modeli degildir.' Sayı girmez.

## 3. Yanlışlayıcılar

- **H-R** (HEKİS adım 5'i doldurur): `modellendi`. hekis-model 6c34a63 içinde kira akışı modeli var (`hekis/zones.py`, `hekis/bind.py`, `hekis/kira.py`). Ölçüm değil. Tek-sistem 'Bu kol ölçülmedi' cümlesi durur.
- **H-R2** (iki senet aynıdır): `ayri`. İhraç, prim ve çıkış üçü de farklı; aynı diye yazılmaz.

## 4. Yan kontrol (kamuya açık kayıt; CSV'ye girmez)

- `data/istanbul_2026.json kfe_reel_yillik` 2013–2025 (Aralık/Aralık, TR geneli): EVDS `TP.KFE.TR` / `TP.FG.J0` ile yeniden hesaplandı, 13 yılın 13'ü üçüncü ondalığa kadar eşit.
- `data/KREDI.md` 'Yil sonu serisi bulunamadi' (konut kredisi stoku): EVDS `TP.HPBITABLO6.3` (bankacılık sektörü yurt içi, TL+YP) 2024-12 510,8; 2025-12 675,1; 2026-09 838,1 milyar TL. KREDI.md'nin 25 Eylül 2026 = 838,1 noktası tutar. Seri 2024-06'dan başlar; 2023 ve öncesi bu grupta bulunamadı (arşiv grupları denenmedi).
- `hekis_enflasyon.py` artık `hekis_model/data/istanbul_2026.json` okur (eski yerel zip yolu kaldırıldı); patika ve sayılar değişmedi.

## 5. Güncellenecek liste (kullanıcı revizyonla çeker; köprü beklemez)

- hekis-model: 6c34a63 sonrası revizyon gelirse `hekis_model/` yeniden kopyalanır, `KAYNAK.md` commit'i değişir, bu dosya yeniden koşar.
- hekis-model `data/KREDI.md`: konut kredisi yıl sonu için EVDS `TP.HPBITABLO6.3` (yukarıda). Köprü bunu HEKİS'e yazmaz.
- hekis-model `SISTEMLER.md` Anadolu: Kocaeli, Konya, Adana yer tutucu; şok testleri koşulmadı (kendi sınırlar notu).
- tek-sistem c01b60a: adım 1 etiketi (`tek_sistem_esleme.csv`) bu turda düzeltilmedi; ayrı gedik.
- modeller: herkese açık kayıt bulunamadı; açılırsa yalnız 'taslak, ölçülmedi' notu girer, sayı girmez.

## Ne denmez

- 'HEKİS döngüyü kırdı' denmez. Şu commit'te şu model var, ölçüm değil.
- HEKİS senedi ile hedef primli senet aynı denmez.
- Tek-sistem adım 1 akış yüzdesine bağlanmaz (bu dosyada yok).
