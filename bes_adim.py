"""Beş adım, sırayla, tek koşu.

Ön kayıt 87f0317. Her adım kendi dosyasını yazar; sonraki adım öncekinin etiketini okur, `ihlal` ise durur.
Girdi yalnız bu depodaki dosyalar: stok_silim.csv, odeme_mahsup_sonuc.json, tek_sistem_kopru.csv,
tek_sistem_esleme.csv, diger_repo_kopru.csv, tavan_akis.csv, vadeli_kalicilik.csv.

Taşınmaz: akış 0,4270 (`baska_nesne`, dokunulmaz), MY 2.933,6, kalan 0,893, BDDK–akım 387,1, geçiş 0/1/3/1.
Kilitli üç kapı (vade dilimi, ödenmeyen emir, geçiş payı) boş kalır; biri dolu çıkarsa `ihlal`, koşu düşer.

Adım 1 stok: eski_tavan 0,0728 (stok_silim.py arac_ayri_oran_ust_sinir; her tek yön bacağa aynı araçta EVDS üst
sınırı, aynı EVDS stoku birden çok satırda) ve yeni_tavan (çift düzeyi: iki yön metinden, araçlar toplanır; ters yön
metinde yoksa EVDS konsolide olmayan aynı-araç üst sınırı; ortak = min; yeni_tavan = Σortak / Σbrüt). İkisi ayrı
sütun. Silinen boş: kimden-kime xls depoda yok. Üst sınır, skor değil.

Çıktı: adim1_stok.csv, adim2.csv, adim3.csv, adim4.csv, adim5.csv, bes_adim_sonuc.json (kosu; son boş), BES_ADIM.md\nSon satır (`son`) test_bes_adim.py'den gelir; koşu yazmaz.

Yan dosyalar (Faz 1–6; kilit dışı, yalnız okunur, md'de listelenir): adim1_nace.py, adim2_nace_ag.py, adim3_faiz_durma.py,
adim4_adres_yonlendirme.py, gecis_payi_band.py, adim5_kira.py; harita girdi_haritasi.py. Hiçbiri bu adım dosyalarına yazmaz.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

KOK = Path(__file__).resolve().parent
ON_KAYIT = "87f0317"
ESKI_TAVAN = 0.0728
XLS_VAR = False
AKIS_SATIRI = {"deger": 0.427, "durum": "baska_nesne"}  # dokunulmaz; yalnız okunur


def _csv(ad: str) -> list[dict]:
    return list(csv.DictReader((KOK / ad).open(encoding="utf-8-sig")))


def _yaz(ad: str, alan: list[str], satirlar: list[dict]) -> None:
    with (KOK / ad).open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=alan)
        w.writeheader()
        for s in satirlar:
            w.writerow({a: ("" if s.get(a) is None else s.get(a)) for a in alan})


def _bos(x) -> bool:
    return x is None or str(x).strip() == ""


# ---------------------------------------------------------------- ön kontrol
def on_kontrol() -> dict:
    esl = _csv("tek_sistem_esleme.csv")
    akis = [r for r in esl if r["adim"] == "1" and r["dosya"] == "mahsup_sektor_ozet.json"]
    ok = len(akis) == 1 and float(akis[0]["deger"]) == AKIS_SATIRI["deger"] and akis[0]["durum"] == AKIS_SATIRI["durum"]
    return {"on_kayit": ON_KAYIT, "akis_satiri": AKIS_SATIRI, "akis_satiri_degismedi": ok}


# ---------------------------------------------------------------- adım 1 stok
def adim1() -> dict:
    legs = [r for r in _csv("stok_silim.csv") if r["yontem"] == "arac_ayri" and r["tavan_tipi"] != "kendi_ici"]
    g: dict[tuple, dict] = defaultdict(lambda: {"yon": defaultdict(float), "evds": defaultdict(list), "arac": set()})
    for r in legs:
        a, b = r["alacakli"], r["borclu"]
        p = g[tuple(sorted((a, b)))]
        p["yon"][(a, b)] += float(r["stok"])
        p["arac"].add(r["arac"])
        if not _bos(r["karsi_bacak_tavan"]):
            p["evds"][(b, a)].append((float(r["karsi_bacak_tavan"]), r["tavan_seri"]))
    satirlar = []
    for (x, y), p in g.items():
        ab, ba = p["yon"].get((x, y)), p["yon"].get((y, x))
        k_ab = "metin" if ab is not None else None
        k_ba = "metin" if ba is not None else None
        seri = ""
        if k_ab is None and p["evds"].get((x, y)):
            ab = sum(t for t, _ in p["evds"][(x, y)]); k_ab = "evds_ust_sinir"
            seri = "; ".join(s for _, s in p["evds"][(x, y)])
        if k_ba is None and p["evds"].get((y, x)):
            ba = sum(t for t, _ in p["evds"][(y, x)]); k_ba = "evds_ust_sinir"
            seri = "; ".join(s for _, s in p["evds"][(y, x)])
        dolu = k_ab is not None and k_ba is not None
        satirlar.append({
            "cift": f"{x}–{y}", "yon_ab": f"{x}→{y}", "bacak_ab": None if ab is None else round(ab, 1), "kaynak_ab": k_ab,
            "yon_ba": f"{y}→{x}", "bacak_ba": None if ba is None else round(ba, 1), "kaynak_ba": k_ba,
            "araclar": "+".join(sorted(p["arac"])),
            "ortak_stok": round(min(ab, ba), 1) if dolu else None,
            "brut": round(ab + ba, 1) if dolu else None,
            "silinen": None, "eski_tavan": None, "yeni_tavan": None, "evds_seri": seri,
            "not": "iki yön metinde" if k_ab == k_ba == "metin" else
                   ("ters yön EVDS konsolide olmayan aynı-araç üst sınırı; metinde yok" if dolu else "ters yön bulunamadı; boş"),
        })
    dolu = [s for s in satirlar if s["ortak_stok"] is not None]
    ortak, brut = sum(s["ortak_stok"] for s in dolu), sum(s["brut"] for s in dolu)
    metin = [s for s in dolu if s["kaynak_ab"] == s["kaynak_ba"] == "metin"]
    o_m, b_m = sum(s["ortak_stok"] for s in metin), sum(s["brut"] for s in metin)
    yeni = round(ortak / brut, 4) if brut else None
    yeni_metin = round(o_m / b_m, 4) if b_m else None
    silinen_dolu = any(s["silinen"] is not None for s in satirlar)
    hs1 = "temiz" if (yeni is not None and abs(yeni - ESKI_TAVAN) > 1e-9) else "ihlal"
    hs2 = "ihlal" if (silinen_dolu and not XLS_VAR) else "temiz"
    toplam = {"cift": "TOPLAM", "ortak_stok": round(ortak, 1), "brut": round(brut, 1), "silinen": None,
              "eski_tavan": ESKI_TAVAN, "yeni_tavan": yeni,
              "not": f"eski: stok_silim.py arac_ayri_oran_ust_sinir, satır toplamı; yeni: Σortak/Σbrüt, {len(dolu)}/{len(satirlar)} çift dolu; "
                     f"yalnız metin iki yön {len(metin)} çift: {yeni_metin}. Üst sınır, skor değil. Silinen boş: xls yok."}
    alan = ["cift", "yon_ab", "bacak_ab", "kaynak_ab", "yon_ba", "bacak_ba", "kaynak_ba", "araclar", "ortak_stok", "brut", "silinen",
            "eski_tavan", "yeni_tavan", "evds_seri", "not"]
    _yaz("adim1_stok.csv", alan, satirlar + [toplam])
    etiket = "temiz" if hs1 == hs2 == "temiz" else "ihlal"
    return {"adim": 1, "dosya": "adim1_stok.csv", "eski_tavan": ESKI_TAVAN, "yeni_tavan": yeni, "yeni_tavan_yalniz_metin": yeni_metin,
            "ortak_milyar": round(ortak, 1), "brut_milyar": round(brut, 1), "cift": len(satirlar), "dolu_cift": len(dolu),
            "silinen": None, "xls": XLS_VAR, "H-S1": hs1, "H-S2": hs2, "etiket": etiket}


# ---------------------------------------------------------------- adım 2
def adim2() -> dict:
    om = json.load((KOK / "odeme_mahsup_sonuc.json").open(encoding="utf-8"))
    oz, pr = om["ozet"], om["parametreler"]
    satir = {"adim": 2, "kaynak": "odeme_mahsup.py", "nesne": "temerrüt sayısı, şart kaldıracı sonrası", "donem": "2026-Q1",
             "ag": f"sentetik {oz['araci_sayisi']} firma, {om['kenar_sayisi']} kenar", "deger": oz["temerrut_sart"], "birim": "adet",
             "durum": "modellendi",
             "parametre": f"holding_odeme_orani {pr['holding_odeme_orani']}; ucret_gecis_beta {pr['ucret_gecis_beta']}",
             "parametre_turu": "parametre, veri değil",
             "not": "Ağ sentetik; ölçüm değil. Alta inen pay ücret: beta parametre. Firma düzeyi veri yok.", "dosya": "odeme_mahsup_sonuc.json"}
    alan = list(satir.keys())
    _yaz("adim2.csv", alan, [satir])
    ha2 = "temiz" if (satir["durum"] == "modellendi" and satir["parametre_turu"] == "parametre, veri değil"
                     and oz["araci_sayisi"] == 150 and oz["temerrut_sart"] == 0) else "ihlal"
    return {"adim": 2, "dosya": "adim2.csv", "temerrut": oz["temerrut_sart"], "durum": "modellendi",
            "parametre": satir["parametre"], "H-A2": ha2, "etiket": ha2}


# ---------------------------------------------------------------- adım 3
def adim3() -> dict:
    om = json.load((KOK / "odeme_mahsup_sonuc.json").open(encoding="utf-8"))
    kop = _csv("tek_sistem_kopru.csv")
    f4 = next(r for r in kop if r["blok"] == "mutabakat" and r["donem"] == "2026-Q1" and r["evds_anahtar"] == "F_F4_yuk")
    bddk = next(r for r in kop if r["blok"] == "mutabakat" and r["donem"] == "2025-Q4" and r["evds_anahtar"] == "F_F4_yuk")
    fg24 = next(r for r in kop if r["blok"] == "referans" and r["donem"] == "2024" and r["kalem"] == "firma finansman gideri")
    fg25 = next(r for r in kop if r["blok"] == "referans" and r["donem"] == "2025" and r["kalem"] == "firma finansman gideri")
    s1 = {"adim": 3, "kaynak": "odeme_mahsup.py", "nesne": "kredi ihtiyacı, şart sonrası", "donem": "2026-Q1 (sentetik 150 firma)",
          "deger": om["ozet"]["kredi_ihtiyaci_sart"], "birim": "trilyon TL/ay", "durum": "modellendi",
          "not": f"Faizin durması modellenmedi. 2025 finansman gideri birincilde yok (Sektör Bilançoları son yayın 2024). "
                 f"2024 {float(fg24['evds_milyar']):.1f} milyar referans; eşitlenmez. RAPOR {float(fg25['tek_sistem_milyar']):.0f} ölçülmedi.",
          "dosya": "odeme_mahsup_sonuc.json"}
    s2 = {"adim": 3, "kaynak": "tek_sistem_kopru.py", "nesne": "firma F.4 kredi yükümlülüğü (EVDS konsolide olmayan)", "donem": "2026-Q1",
          "deger": float(f4["evds_milyar"]), "birim": "milyar TL", "durum": "olculdu",
          "not": f"adım değil, stok. BDDK ticari 2025 {float(bddk['tek_sistem_milyar']):.0f}; EVDS/BDDK {float(bddk['evds_bolu_tek']):.2f} durur "
                 f"({f4['seri']}).", "dosya": "tek_sistem_kopru.csv"}
    alan = list(s1.keys())
    _yaz("adim3.csv", alan, [s1, s2])
    ha3 = "temiz" if (s1["durum"] == "modellendi" and s2["durum"] == "olculdu" and s2["not"].startswith("adım değil")
                     and _bos(fg25["evds_milyar"]) and float(bddk["tek_sistem_milyar"]) == 17302.0) else "ihlal"
    return {"adim": 3, "dosya": "adim3.csv", "kredi_ihtiyaci": s1["deger"], "f_f4_yuk": s2["deger"],
            "finansman_gideri_2024": float(fg24["evds_milyar"]), "finansman_gideri_2025": None,
            "bddk_2025": float(bddk["tek_sistem_milyar"]), "evds_bolu_bddk": float(bddk["evds_bolu_tek"]), "H-A3": ha3, "etiket": ha3}


# ---------------------------------------------------------------- adım 4
def adim4() -> dict:
    esl = [r for r in _csv("tek_sistem_esleme.csv") if r["adim"] == "4" and r["durum"] == "olculdu"]
    satirlar = []
    for r in esl:
        satirlar.append({"adim": 4, "kaynak": r["katman"], "nesne": r["nesne"], "donem": r["donem"], "deger": float(r["deger"]),
                         "birim": r["birim"], "durum": "olculdu", "ihrac": None, "prim": None, "cikis": None,
                         "not": "adres adayı, senet değil", "dosya": r["dosya"]})
    satirlar.append({"adim": 4, "kaynak": None, "nesne": "hedef primli endeksli senet", "donem": None, "deger": None, "birim": None,
                     "durum": "modellenmedi", "ihrac": None, "prim": None, "cikis": None,
                     "not": "Ne ödeme zinciri ne mahsup paketi içerir. HEKİS senedi (hekis-model, TÜFE endeksli, reel kupon 0) ile eşitlenmez.",
                     "dosya": None})
    alan = list(satirlar[0].keys())
    _yaz("adim4.csv", alan, satirlar)
    senet = satirlar[-1]
    ha4 = "temiz" if (len(satirlar) == 4 and senet["durum"] == "modellenmedi" and all(_bos(senet[k]) for k in ("ihrac", "prim", "cikis", "deger"))
                     and all(s["not"] == "adres adayı, senet değil" for s in satirlar[:3])) else "ihlal"
    return {"adim": 4, "dosya": "adim4.csv", "adres_adayi": {s["nesne"]: s["deger"] for s in satirlar[:3]},
            "senet": "modellenmedi", "ihrac": None, "prim": None, "cikis": None, "H-A4": ha4, "etiket": ha4}


# ---------------------------------------------------------------- adım 5
def adim5() -> dict:
    kira = next(r for r in _csv("tek_sistem_esleme.csv") if r["adim"] == "5")
    hek = next(r for r in _csv("diger_repo_kopru.csv") if r["repo"] == "hekis-model" and r["nesne"].startswith("kira akışı: havuz"))
    s1 = {"adim": 5, "kaynak": None, "nesne": "kira akışı (tek sistem)", "donem": None, "deger": None, "birim": None, "durum": "olculmedi",
          "not": kira["not"], "dosya": None}
    s2 = {"adim": 5, "kaynak": f"{hek['repo']} {hek['commit']}", "nesne": hek["nesne"], "donem": hek["donem"], "deger": float(hek["deger"]),
          "birim": hek["birim"], "durum": "modellendi", "not": "Politika kirası; kaynak alanı 'model varsayimi, gozlem degil'. Tek sistem kira satırına yazılmaz.",
          "dosya": hek["dosya"]}
    alan = list(s1.keys())
    _yaz("adim5.csv", alan, [s1, s2])
    ha5 = "temiz" if (s1["durum"] == "olculmedi" and _bos(s1["deger"]) and s2["durum"] == "modellendi") else "ihlal"
    return {"adim": 5, "dosya": "adim5.csv", "kira": "olculmedi", "hekis_kira_tl_ay": s2["deger"], "hekis": "modellendi", "H-A5": ha5, "etiket": ha5}


# ---------------------------------------------------------------- kilitli kapılar
def kilitli_kapilar() -> dict:
    ta = _csv("tavan_akis.csv")
    vk = _csv("vadeli_kalicilik.csv")
    gecis_bos = all(_bos(r["gecis"]) and _bos(r["tavan"]) for r in ta)
    vade_bos = all(r["vade_kirilim"] == "ayrılmadı" and _bos(r["ortalama_gun"]) for r in vk)
    emir_bos = all(_bos(r["odenmeyen_emir_milyar"]) for r in vk)
    kapilar = {"gecis_payi": {"bos": gecis_bos, "dosya": "tavan_akis.csv", "sutun": "gecis, tavan"},
               "vade_dilimi": {"bos": vade_bos, "dosya": "vadeli_kalicilik.csv", "sutun": "vade_kirilim, ortalama_gun"},
               "odenmeyen_emir": {"bos": emir_bos, "dosya": "vadeli_kalicilik.csv", "sutun": "odenmeyen_emir_milyar"}}
    etiket = "temiz" if all(k["bos"] for k in kapilar.values()) else "ihlal"
    return {"kapilar": kapilar, "etiket": etiket, "not": "varsayim_esik.csv eşikleri varsayım; kapıya taşınmaz."}


# ---------------------------------------------------------------- yan dosyalar (Faz 1–6; yalnız okunur)
YAN = (
    ("1", "adim1_nace_sonuc.json", "adim1_nace.py", ("b_nace_taban", "silinen_max_oran"), "F içi silinen_max oranı", "ust_sinir_nace"),
    ("2", "adim2_nace_ag_sonuc.json", "adim2_nace_ag.py", ("kalibrasyon", "lambda"), "λ* (G1 çapası)", "kalibrasyon_varsayim"),
    ("3", "adim3_faiz_durma_sonuc.json", "adim3_faiz_durma.py", ("psi", "psi"), "ψ etkin faiz payı", "olcum_turevi"),
    ("4", "adim4_adres_yonlendirme_sonuc.json", "adim4_adres_yonlendirme.py", ("adres_toplam_milyar",), "adres toplamı milyar", "olcum"),
    ("kapı", "gecis_payi_band_sonuc.json", "gecis_payi_band.py", ("ana", "LR_gecis_payi"), "geçiş payı nokta tahmini", "tahmin_ols"),
    ("5", "adim5_kira_sonuc.json", "adim5_kira.py", ("birim_kira", "tl_m2_ay"), "birim kira TL/m²/ay", "olcum"),
)


def yan_dosyalar() -> list[dict]:
    out = []
    for adim, dosya, kod, yol, ad, etiket in YAN:
        p = KOK / dosya
        if not p.exists():
            continue
        v = json.loads(p.read_text(encoding="utf-8"))
        for k in yol:
            v = v.get(k) if isinstance(v, dict) else None
        out.append({"adim": adim, "dosya": dosya, "kod": kod, "sayi": f"{ad}: {v}", "etiket": etiket})
    return out


# ---------------------------------------------------------------- md
def md(son: dict) -> str:
    a = son["adimlar"]
    f = lambda x, n=1: "" if x is None else f"{x:,.{n}f}"
    s = ["# Beş adım, sırayla, tek koşu", "",
         f"Ön kayıt `{ON_KAYIT}`. Çalıştır: `python3 bes_adim.py`. Çıktı: `adim1_stok.csv`, `adim2.csv`, `adim3.csv`, `adim4.csv`, `adim5.csv`, `bes_adim_sonuc.json`.", "",
         "Her adım kendi dosyasını yazar; sonraki, öncekinin etiketini okur; `ihlal` ise durur. Önceki katman sayıları taşınmaz. "
         "Adım 1 akış satırı (0,4270, `baska_nesne`) dokunulmadı.", "",
         "## Etiketler", "", "| Adım | Dosya | Yanlışlayıcı | Etiket | Sayı |", "| --- | --- | --- | --- | --- |"]
    if "1" in a:
        x = a["1"]
        s.append(f"| 1 stok | `adim1_stok.csv` | H-S1 {x['H-S1']}, H-S2 {x['H-S2']} | `{x['etiket']}` | eski_tavan {x['eski_tavan']:.4f}; yeni_tavan {f(x['yeni_tavan'], 4)}; silinen boş |")
    if "2" in a:
        x = a["2"]
        s.append(f"| 2 | `adim2.csv` | H-A2 {x['H-A2']} | `{x['etiket']}` | temerrüt {x['temerrut']}, `modellendi`; {x['parametre']} parametre |")
    if "3" in a:
        x = a["3"]
        s.append(f"| 3 | `adim3.csv` | H-A3 {x['H-A3']} | `{x['etiket']}` | kredi ihtiyacı {x['kredi_ihtiyaci']} `modellendi`; F F.4 {f(x['f_f4_yuk'])} `olculdu` (stok) |")
    if "4" in a:
        x = a["4"]
        s.append(f"| 4 | `adim4.csv` | H-A4 {x['H-A4']} | `{x['etiket']}` | üç adres adayı `olculdu`; senet `modellenmedi`, ihraç/prim/çıkış boş |")
    if "5" in a:
        x = a["5"]
        s.append(f"| 5 | `adim5.csv` | H-A5 {x['H-A5']} | `{x['etiket']}` | kira `olculmedi`; HEKİS havuz kirası {f(x['hekis_kira_tl_ay'], 0)} TL/ay `modellendi` |")
    k = son["kilitli_kapilar"]
    s += ["", "## Kilitli üç kapı", ""]
    if k is None:
        s.append(f"- Bakılmadı: koşu önce durdu ({son.get('neden', '')}).")
    else:
        for ad, v in k["kapilar"].items():
            s.append(f"- {ad}: {'boş' if v['bos'] else 'DOLU'} (`{v['dosya']}` {v['sutun']})")
        s.append(f"- Etiket: `{k['etiket']}`. {k['not']}")
    s += ["", f"## Koşunun sözü: `{son['kosu']}`" + (f" ({son['neden']})" if son.get("neden") else ""), "",
          "Son satır (`bes_adim_sonuc.json` `son`) koşudan gelmez; `python3 test_bes_adim.py` yazar. Kaynak test.", ""]
    if "1" in a:
        x = a["1"]
        s += ["## Adım 1 stok, iki sütun", "",
              f"- `eski_tavan` {x['eski_tavan']:.4f}: stok_silim.py, her tek yön bacağa aynı araçta EVDS üst sınırı; aynı EVDS stoku birden çok satırda; "
              "metindeki ters bacak (başka araç) görülmez. Durur, silinmez.",
              f"- `yeni_tavan` {f(x['yeni_tavan'], 4)}: çift düzeyi; iki yön metinden (araçlar toplanır), ters yön metinde yoksa EVDS konsolide olmayan "
              f"aynı-araç üst sınırı; ortak = min; Σortak {f(x['ortak_milyar'])} / Σbrüt {f(x['brut_milyar'])}; {x['dolu_cift']}/{x['cift']} çift dolu. "
              f"Yalnız metin iki yön: {f(x['yeni_tavan_yalniz_metin'], 4)}.",
              "- Silinen boş: kimden-kime xls depoda yok. İki sayı üst sınır; skor değil. 'Yaklaşık yüzde 20' bu kuralla çıkmadı; bulunamadı.", ""]
    yan = yan_dosyalar()
    if yan:
        s += ["## Kilit dışı yan dosyalar (Faz 1–6; girdi, sonuç değil)", "",
              "Adım dosyalarına ve kapılara yazılmaz; etiketiyle okunur. Harita: `GIRDI_HARITASI.md`.", "",
              "| Adım | Yan dosya | Kod | Sayı | Etiket |", "| --- | --- | --- | --- | --- |"]
        s += [f"| {y['adim']} | `{y['dosya']}` | `{y['kod']}` | {y['sayi']} | `{y['etiket']}` |" for y in yan]
        s.append("")
    s += ["## Maliyet ve yürütme maliyeti", "",
          "Adım adım: `BES_ADIM_MALIYET.md` (`python3 bes_adim_maliyet.py`; model: `yurutme_maliyet.py`). Adım 4 ve 5 maliyeti band (varsayım). Yürütme maliyeti (tespit + tahsil + idari) = program akışı × ρ, ρ bandı varsayım (%0,4 / %9 / %25 pilot payı / %29); adım 1 (ortak stok) ve 2 (mahsupla silinen) için stok, yalnız alt ρ ile üst sınır; adım 3 (duran faiz) için yıllık akış. Adım 4.5 (yeni para birimine geçiş, plasebo; adım 4 ile 5 arası): `ADIM45_PARA_BIRIMI.md`; fayda 0, yürütme maliyeti rejime göre 0,39 – 445,9 milyar TL (tek sefer).", ""]
    s += ["## Ne denmez", "",
          "- 'Beş adım kuruldu' denmez. Şu adım şu etiket; kilitli kapı boş.",
          "- 'Stok yüzde X silindi' denmez; silinen boş.",
          "- 'HEKİS döngüyü kırdı' denmez; adım 5 kira `olculmedi`, HEKİS `modellendi`.",
          "- HEKİS senedi ile hedef primli senet eşitlenmez; senet `modellenmedi`."]
    return "\n".join(s) + "\n"


def main() -> None:
    son: dict = {"on_kontrol": on_kontrol(), "adimlar": {}, "kilitli_kapilar": None, "kosu": None,
                 "son": None, "son_kaynak": "test_bes_adim.py; koşu yazmaz"}
    if not son["on_kontrol"]["akis_satiri_degismedi"]:
        son["kosu"] = "durdu"; son["neden"] = "adım 1 akış satırı değişmiş"
    else:
        for i, fn in enumerate((adim1, adim2, adim3, adim4, adim5), start=1):
            r = fn()
            son["adimlar"][str(i)] = r
            print(f"adım {i}: {r['etiket']}  ({r['dosya']})")
            if r["etiket"] == "ihlal":
                son["kosu"] = "durdu"; son["neden"] = f"adım {i} ihlal"
                break
        else:
            son["kilitli_kapilar"] = kilitli_kapilar()
            print("kilitli kapı:", {k: ("boş" if v["bos"] else "DOLU") for k, v in son["kilitli_kapilar"]["kapilar"].items()})
            son["kosu"] = "bitti" if son["kilitli_kapilar"]["etiket"] == "temiz" else "durdu"
            if son["kosu"] == "durdu":
                son["neden"] = "kilitli kapı dolu"
    (KOK / "bes_adim_sonuc.json").write_text(json.dumps(son, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (KOK / "BES_ADIM.md").write_text(md(son), encoding="utf-8")
    a1 = son["adimlar"].get("1")
    if a1:
        print(f"adım 1 stok: eski_tavan {a1['eski_tavan']} | yeni_tavan {a1['yeni_tavan']} | silinen boş")
    print("koşu:", son["kosu"], "| son: boş; test_bes_adim.py yazar")


if __name__ == "__main__":
    main()
