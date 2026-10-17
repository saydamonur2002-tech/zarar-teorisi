"""Diğer repo köprüsü: hekis-model (HEKİS) ve modeller deposu → bu modelin yanına, içine değil.

Kural: sayı kaynak commit'ten; revizyon gelmeden "güncel" yazılmaz. Akış %42,1, stok tavanı, MY 2.933,6,
kalan %89,3 ve tek-sistem köprüsü bu dosyaya taşınmaz. HEKİS TÜFE puanı, Gini, yerleşen hane zarar-teorisi
serisine yapıştırılmaz; yan yana durur. tek-sistem a9344f1 ile bağlı, yeniden kopyalanmaz; adım 1 etiketi
bu turda düzeltilmez.

Girdi: hekis_model/ (hekis-model 6c34a63 kopyası), model/RAPOR.md (tek-sistem c01b60a), kamuya açık GitHub kaydı.
Çıktı: diger_repo_kopru.csv (repo, commit, dosya, nesne, deger, birim, donem, durum, not), diger_repo_kopru_sonuc.json,
DIGER_REPO_KOPRU.md
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent
HEKIS_DIR = KOK / "hekis_model"

REPOLAR = {
    "hekis-model": {
        "url": "https://github.com/saydamonur2002-tech/hekis-model",
        "commit": "6c34a63", "tarih": "2026-10-08",
        "ne_var": "HEKİS: İstanbul ve Anadolu (7 büyükşehir) ayrı sistem; üç defter mülkiyet/oturan/senet; "
                  "hekis/ paketi, data/ notları, 86 test; kopyası hekis_model/",
        "durum": "kopyalandı",
    },
    "tek-sistem": {
        "url": "https://github.com/saydamonur2002-tech/tek-sistem",
        "commit": "c01b60a", "tarih": "2026-10-04",
        "ne_var": "RAPOR.md beş adım, model/pasta ve model/gercek CSV, mahsup paketi; a9344f1 ile bağlı",
        "durum": "bağlı (a9344f1); yeniden kopyalanmadı",
    },
    "modeller": {
        "url": "https://github.com/saydamonur2002-tech/modeller",
        "commit": None, "tarih": None,
        "ne_var": "bulunamadı; 3 sorgu denendi (gh repo view, users/.../repos, search/repositories). "
                  "hekis-model README.md 'Not kopyasi' diye atıf yapar; herkese açık kayıt yok.",
        "durum": "bulunamadı",
    },
}
HK = REPOLAR["hekis-model"]["commit"]
TK = REPOLAR["tek-sistem"]["commit"]

# SISTEMLER.md (6c34a63) tablosu: metin rakamı, kod koşusu değil. Anadolu için koşu fonksiyonu bu köprüde çağrılmadı.
SISTEMLER_MD = {
    "İstanbul": {"bos_stok_tam_olcek": 450_000, "yerlesen": 36_900, "sub_7yil_mr": 3.92, "bedel_7yil_mr": 7.03,
                 "gini": -0.00066, "yoksulluk_puan": -0.16, "yerel_tufe_puan": -0.30, "ulusal_tufe_puan": -0.055,
                 "kira_esneklik06": -0.045},
    "Anadolu (7 şehir)": {"bos_stok_tam_olcek": 664_000, "yerlesen": 66_900, "sub_7yil_mr": 3.18, "bedel_7yil_mr": 5.02,
                          "gini": -0.00036, "yoksulluk_puan": -0.085, "yerel_tufe_puan": -0.35, "ulusal_tufe_puan": -0.10,
                          "kira_esneklik06": -0.052},
}


def hekis_kosu() -> dict:
    """hekis.zones.run_three_zone() — İstanbul en olası senaryo, erozyonsuz tam ölçek. Kod 6c34a63."""
    sys.path.insert(0, str(HEKIS_DIR))
    from hekis import zones  # noqa: PLC0415

    z = zones.run_three_zone()
    return {
        "yerlesen_hane": z["N"], "sub_yil1_tl": z["sub1"], "bedel_tl_yil": z["rev"], "oran": z["ratio"],
        "senet_ihrac_tl": z["entry"], "yuk_20yil_tl": z["yuk"], "kapsam": z["coverage"], "bedel_parcalari": z["rev_parts"],
    }


def hekis_veri() -> dict:
    return json.loads((HEKIS_DIR / "data" / "istanbul_2026.json").read_text(encoding="utf-8"))


def satirlar(k: dict, v: dict) -> list[dict]:
    mr = 1e9
    R = []

    def ek(repo, commit, dosya, nesne, deger, birim, donem, durum, not_):
        R.append({"repo": repo, "commit": commit, "dosya": dosya, "nesne": nesne, "deger": deger, "birim": birim,
                  "donem": donem, "durum": durum, "not": not_})

    # --- HEKİS nesneleri (adım 5 kolunun modeli; ölçüm değil) ---
    pr = v["policy_rent"]
    ek("hekis-model", HK, "hekis/bind.py; data/istanbul_2026.json", "kira akışı: havuz kirası 2+1", pr["2+1"], "TL/ay",
       "2026-08", "modellendi", f"policy_rent {pr['1+1']}/{pr['1+0']} 1+1/1+0, aidat {pr['aidat']}; kaynak alanı 'model varsayimi, gozlem degil'. "
       f"Gözlem girdisi ayrı: İstanbul ort. kira {v['rent']['istanbul_ortalama_tl']:,} (Emlakjet-Endeksa), Esenyurt medyan {v['rent']['esenyurt_medyan_tl']:,}.")
    ek("hekis-model", HK, "hekis/kira.py; data/ykke_2026_08.json", "kira akışı: YKKE gecikmeli yeniden fiyatlama", None, "",
       "2018-01..2026-08", "modellendi", "TCMB YKKE girdisiyle hipotez: TÜFE kira_t ~ YKKE yıllık_(t−12); tek nokta; kimlik testi değil (dosya başlığı).")
    bs = v["bos_stok"]
    ek("hekis-model", HK, "data/istanbul_2026.json", "boş stok: İstanbul gözlem aralığı (alt)", bs["elektrik_aboneligi_tabanli"], "konut",
       "", "modellendi", f"elektrik aboneliği tabanlı; İBB {bs['ibb_elektrik_su_tabanli']:,}–{bs['ibb_ust_tahmin']:,}; stok {bs['istanbul_konut_stoku']:,}. "
       "Yöntem farkı, tek sayı değil (kaynak alanı). Model girdisi; bu depoda ölçülmedi.")
    for sis, s in SISTEMLER_MD.items():
        ek("hekis-model", HK, "SISTEMLER.md", f"boş stok tam ölçek: {sis}", s["bos_stok_tam_olcek"], "konut", "tam ölçek (7. yıl)", "modellendi",
           "metin rakamı; en olası senaryo, erozyon %25")
    ek("hekis-model", HK, "hekis/zones.py", "yerleşen hane: İstanbul tam ölçek (koşu)", round(k["yerlesen_hane"]), "hane", "tam ölçek, erozyonsuz",
       "modellendi", f"run_three_zone() varsayılan; kapsam uygun kiracıya {100 * k['kapsam']:.1f}%. Ölçüm değil.")
    ek("hekis-model", HK, "SISTEMLER.md", "yerleşen hane: Anadolu tam ölçek", SISTEMLER_MD["Anadolu (7 şehir)"]["yerlesen"], "hane", "tam ölçek",
       "modellendi", "metin rakamı; Kocaeli, Konya, Adana fiyat/kira yer tutucu (SISTEMLER.md sınırlar)")
    ek("hekis-model", HK, "hekis/zones.py", "bedel geliri: İstanbul (koşu)", round(k["bedel_tl_yil"] / mr, 2), "milyar TL/yıl", "tam ölçek, erozyonsuz",
       "modellendi", f"genel %1, lüks %5; parçalar {', '.join(f'{p / mr:.2f}' for p in k['bedel_parcalari'])} (HEKİS/tampon/lüks); lüks tahsilat %40 varsayım")
    ek("hekis-model", HK, "hekis/zones.py", "sübvansiyon: İstanbul yıl 1 (koşu)", round(k["sub_yil1_tl"] / mr, 2), "milyar TL/yıl", "tam ölçek, erozyonsuz",
       "modellendi", f"bedel/sub {k['oran']:.2f}; 20 yıl reel yük {k['yuk_20yil_tl'] / mr:.1f} milyar TL")
    for sis, s in SISTEMLER_MD.items():
        ek("hekis-model", HK, "SISTEMLER.md", f"sub / bedel 7. yıl+ (erozyonlu): {sis}", s["sub_7yil_mr"], "milyar TL/yıl (sub)", "7. yıl+",
           "modellendi", f"bedel {s['bedel_7yil_mr']} milyar TL/yıl; metin rakamı")
    # --- HEKİS kendi etki sayıları: yan yana, seriye yapıştırılmaz ---
    for sis, s in SISTEMLER_MD.items():
        ek("hekis-model", HK, "SISTEMLER.md", f"yerel TÜFE puanı: {sis}", s["yerel_tufe_puan"], "puan", "tam ölçek", "modellendi",
           f"ulusal {s['ulusal_tufe_puan']} (hane payı ile ölçekli); kira esneklik 0,6: {100 * s['kira_esneklik06']:.1f}%. "
           "zarar-teorisi TÜFE/NFP serisine girmez (hekis_enflasyon.py ayrı patika).")
        ek("hekis-model", HK, "SISTEMLER.md", f"ΔGini: {sis}", s["gini"], "Gini", "tam ölçek", "modellendi",
           f"Δyoksulluk {s['yoksulluk_puan']} puan; gelir dağılımı ulusal lognormal varsayım")
    # --- Senetler ---
    ek("hekis-model", HK, "hekis/senet.py; data/SENET.md", "HEKİS senedi: ihraç (İstanbul baz)", round(k["senet_ihrac_tl"] / mr, 1), "milyar TL",
       "2026-10-05 tasarım", "modellendi", "boş stok karşılığı; anapara TÜFE endeksli, reel kupon 0; prim min(0,10; 0,04×(fiziki endeks−1)); "
       "sahip payı 1/7 (tasarım payı); dış alıcıya kapalı; ikincil piyasa yok, 20 yıl kilit; itfa yalnız sistem içinde")
    ek("tek-sistem", TK, "model/RAPOR.md", "hedef primli endeksli senet", None, "", "2026-10-04 metin", "taslak",
       "anapara lira, enflasyona endeksli; kupon faiz değil, üretim hedefi tutarsa tasarruftan prim (ithal ikamesi döviz tasarrufu payı); "
       "çıkış senedi başkasına satmak; ihraç büyüklüğü ve prim formülü yok; kod yok")
    ek("hekis-model + tek-sistem", f"{HK} + {TK}", "hekis/senet.py ↔ model/RAPOR.md", "HEKİS senedi ↔ hedef primli senet", None, "", "",
       "esitlenmez", "ihraç farklı (boş konut stoku 89,2 vs tanımsız); prim farklı (fiziki endeks, 1/7 vs ithal ikamesi tasarrufu); "
       "çıkış farklı (20 yıl kilit, ikincil piyasa yok vs satış). H-R2 ayri.")
    # --- Adım 5 ---
    ek("tek-sistem", TK, "model/RAPOR.md", "adım 5: kira kolu", None, "", "", "olculmedi",
       "'Bu kol ölçülmedi.' Tek-sistem cümlesi durur.")
    ek("hekis-model", HK, "hekis/zones.py; hekis/bind.py; hekis/kira.py", "adım 5: kira kolunun modeli", None, "", "2026-10-08", "modellendi",
       "HEKİS kira-havuz-oturan modeli var; ölçüm değil; İstanbul ve Anadolu ayrı; tek-sistem adım 5 etiketi değişmez. H-R modellendi.")
    # --- Ölçek oranı: HEKİS'in kendi hesabı ---
    ek("hekis-model", HK, "PILOT.md", "sistem aktifi / mevduat (HEKİS hesabı)", 0.0029, "oran", "pilot notu", "modellendi",
       "'Sistem aktifi mevduatın %0,29'u, senet %0,28'i' (PILOT.md). Bu deponun mevduat stoklarıyla yeniden oranlanmadı.")
    # --- modeller ---
    ek("modeller", None, "", "HEKİS kapalı kira-üretim devresi notu", None, "", "", "taslak",
       "bulunamadı; 3 sorgu denendi. hekis-model README: 'Calisma taslagidir, dogrulanmis bir kamu maliyesi modeli degildir.' Sayı girmez.")
    return R


def md_yaz(R: list[dict], k: dict, hr: str, hr2: str) -> str:
    s = ["# Diğer repo köprüsü", "",
         "Çalıştır: `python3 diger_repo_kopru.py`. Çıktı: `diger_repo_kopru.csv`, `diger_repo_kopru_sonuc.json`.", "",
         "Kural: sayı kaynak commit'ten; kullanıcı kaynak repoları revizyonla güncelleyecek, köprü eski sayıyı güncel diye yazmaz. "
         "Akış yüzdesi, stok tavanı, MY, kalan pay ve tek-sistem köprüsü bu dosyaya taşınmadı. HEKİS TÜFE puanı, Gini ve yerleşen hane "
         "zarar-teorisi serisine yapıştırılmadı; yan yana durur.", "",
         "## 1. Repo tablosu", "", "| Repo | Commit | Tarih | Ne var | Durum |", "| --- | --- | --- | --- | --- |"]
    for ad, r in REPOLAR.items():
        s.append(f"| [{ad}]({r['url']}) | {r['commit'] or ''} | {r['tarih'] or ''} | {r['ne_var']} | {r['durum']} |")
    s += ["", "## 2. Nesneler (`diger_repo_kopru.csv`)", "",
          "| Repo | Commit | Dosya | Nesne | Değer | Birim | Dönem | Durum |", "| --- | --- | --- | --- | ---: | --- | --- | --- |"]
    for r in R:
        d = r["deger"]
        ds = "" if d is None else (f"{d:,}" if isinstance(d, int) else (f"{d:.5f}".rstrip("0").rstrip(".") if abs(d) < 1 else f"{d:,.2f}"))
        s.append(f"| {r['repo']} | {r['commit'] or ''} | `{r['dosya']}` | {r['nesne']} | {ds} | {r['birim']} | {r['donem']} | {r['durum']} |")
    s += ["", "Notlar satır sırasıyla:", ""]
    for r in R:
        s.append(f"- {r['nesne']}: {r['not']}")
    s += ["", "## 3. Yanlışlayıcılar", "",
          f"- **H-R** (HEKİS adım 5'i doldurur): `{hr}`. hekis-model {HK} içinde kira akışı modeli var (`hekis/zones.py`, `hekis/bind.py`, "
          "`hekis/kira.py`). Ölçüm değil. Tek-sistem 'Bu kol ölçülmedi' cümlesi durur.",
          f"- **H-R2** (iki senet aynıdır): `{hr2}`. İhraç, prim ve çıkış üçü de farklı; aynı diye yazılmaz.", "",
          "## 4. Yan kontrol (kamuya açık kayıt; CSV'ye girmez)", "",
          "- `data/istanbul_2026.json kfe_reel_yillik` 2013–2025 (Aralık/Aralık, TR geneli): EVDS `TP.KFE.TR` / `TP.FG.J0` ile yeniden "
          "hesaplandı, 13 yılın 13'ü üçüncü ondalığa kadar eşit.",
          "- `data/KREDI.md` 'Yil sonu serisi bulunamadi' (konut kredisi stoku): EVDS `TP.HPBITABLO6.3` (bankacılık sektörü yurt içi, TL+YP) "
          "2024-12 510,8; 2025-12 675,1; 2026-09 838,1 milyar TL. KREDI.md'nin 25 Eylül 2026 = 838,1 noktası tutar. Seri 2024-06'dan başlar; "
          "2023 ve öncesi bu grupta bulunamadı (arşiv grupları denenmedi).",
          "- `hekis_enflasyon.py` artık `hekis_model/data/istanbul_2026.json` okur (eski yerel zip yolu kaldırıldı); patika ve sayılar değişmedi.", "",
          "## 5. Güncellenecek liste (kullanıcı revizyonla çeker; köprü beklemez)", "",
          f"- hekis-model: {HK} sonrası revizyon gelirse `hekis_model/` yeniden kopyalanır, `KAYNAK.md` commit'i değişir, bu dosya yeniden koşar.",
          "- hekis-model `data/KREDI.md`: konut kredisi yıl sonu için EVDS `TP.HPBITABLO6.3` (yukarıda). Köprü bunu HEKİS'e yazmaz.",
          "- hekis-model `SISTEMLER.md` Anadolu: Kocaeli, Konya, Adana yer tutucu; şok testleri koşulmadı (kendi sınırlar notu).",
          "- tek-sistem c01b60a: adım 1 etiketi (`tek_sistem_esleme.csv`) bu turda düzeltilmedi; ayrı gedik.",
          "- modeller: herkese açık kayıt bulunamadı; açılırsa yalnız 'taslak, ölçülmedi' notu girer, sayı girmez.", "",
          "## Ne denmez", "",
          "- 'HEKİS döngüyü kırdı' denmez. Şu commit'te şu model var, ölçüm değil.",
          "- HEKİS senedi ile hedef primli senet aynı denmez.",
          "- Tek-sistem adım 1 akış yüzdesine bağlanmaz (bu dosyada yok)."]
    return "\n".join(s) + "\n"


def main() -> None:
    k = hekis_kosu()
    v = hekis_veri()
    R = satirlar(k, v)
    hr = "modellendi"  # kira akışı modeli var (hekis/zones.py, bind.py, kira.py); ölçüm değil
    hr2 = "ayri"       # ihraç, prim, çıkış üçü farklı

    alan = ["repo", "commit", "dosya", "nesne", "deger", "birim", "donem", "durum", "not"]
    with (KOK / "diger_repo_kopru.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=alan)
        w.writeheader()
        for r in R:
            w.writerow({a: ("" if r[a] is None else r[a]) for a in alan})
    (KOK / "diger_repo_kopru_sonuc.json").write_text(json.dumps({
        "repolar": REPOLAR, "H-R": hr, "H-R2": hr2,
        "hekis_kosu_6c34a63": {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in k.items() if kk != "bedel_parcalari"},
        "satirlar": R,
        "kural": "sayı kaynak commit'ten; eski sayı güncel diye yazılmaz; önceki katman sonuçları taşınmaz",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (KOK / "DIGER_REPO_KOPRU.md").write_text(md_yaz(R, k, hr, hr2), encoding="utf-8")

    print("=== Diğer repo köprüsü ===")
    for ad, r in REPOLAR.items():
        print(f"{ad:<12} {r['commit'] or '—':<8} {r['tarih'] or '—':<11} {r['durum']}")
    print(f"H-R {hr} | H-R2 {hr2} | satır {len(R)}")
    for r in R:
        print(f"  {r['durum']:<12} {r['repo']:<24} {r['nesne']} = {r['deger'] if r['deger'] is not None else ''} {r['birim']}")


if __name__ == "__main__":
    main()
