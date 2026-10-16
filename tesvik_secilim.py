"""Teşvik dipnot sınıflaması ve marj farkı.

Yararlanmayan, yalnızca 'belge yoktur' ya da teşvik geliri satırı sıfır olan
firma-yıldır. Dipnotta teşvik yazmayan firma yararlanmayan sayılmaz.
Eşleştirme, kontrol grubu bir firmaysa kurulmaz.
"""
from __future__ import annotations

import csv
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path("/workspace")
CACHE = Path("/tmp/kap_tur3")

BELGE = re.compile(r"yatırım teşvik belgesi", re.I)
YOK = re.compile(
    r"yatırım teşvik belgesi bulunmamakta|devlet teşvik ve yardımları bulunmamakta",
    re.I,
)
VAR_ISARET = re.compile(
    r"almıştır|aldık|sahiptir|sahip olduğu|bulunmaktadır|mevcuttur|temin edil|"
    r"yararlanılmıştır|yararlanmıştır|onaylan|sayılı|tarihli|numaralı|nolu|"
    r"düzenlen|kapsamında yapıl",
    re.I,
)
MEVZUAT = re.compile(r"kullanılması durumunda", re.I)
BASVURU = re.compile(r"başvurusu yapılacak|başvuru yapılacak", re.I)


def fnum(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def pct(xs, p):
    xs = sorted(x for x in xs if x is not None and not math.isnan(x))
    if not xs:
        return None
    if len(xs) == 1:
        return xs[0]
    k = (len(xs) - 1) * p
    lo, hi = int(math.floor(k)), int(math.ceil(k))
    if lo == hi:
        return xs[lo]
    return xs[lo] * (hi - k) + xs[hi] * (k - lo)


def ozet(xs):
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    if not xs:
        return {"n": 0, "p25": None, "medyan": None, "p75": None}
    return {"n": len(xs), "p25": pct(xs, 0.25), "medyan": statistics.median(xs), "p75": pct(xs, 0.75)}


def cekirdek(r):
    xs = [fnum(r.get(k)) for k in ("brut", "paz", "gy", "arge")]
    if any(x is None for x in xs):
        return None
    return sum(xs)


def marj(r, fn):
    s = fnum(r.get("satis"))
    v = fn(r)
    if not s or v is None:
        return None
    return v / s


def sinif_metin(text: str | None):
    if text is None:
        return {"sinif": "metin_yok", "kanit": []}
    kanit = []
    if YOK.search(text):
        kanit.append("belge_yok_cumlesi")
    belge = False
    for m in BELGE.finditer(text):
        w = re.sub(r"\s+", " ", text[max(0, m.start() - 120): m.end() + 140])
        if YOK.search(w) or BASVURU.search(w):
            continue
        if MEVZUAT.search(w) and not VAR_ISARET.search(w):
            kanit.append("mevzuat_cumlesi")
            continue
        if VAR_ISARET.search(w):
            belge = True
            kanit.append("belge:" + w[:160])
            break
    gelir_poz = False
    gelir_sifir = False
    for line in text.splitlines():
        u = line.lower()
        if "teşvik gelir" not in u and "tesvik gelir" not in u and "destek gelir" not in u:
            continue
        if any(k in u for k in ("kıdem", "kidem", "kiralama", "sendika")):
            continue
        pos = re.findall(r"(?<![\d.])\d{1,3}(?:\.\d{3})+", line)
        pos += re.findall(r"(?<![\d,])\d{1,3}(?:,\d{3})+", line)
        pos = [p for p in pos if not (1990 <= int(p.replace(".", "").replace(",", "")) <= 2035 and "." not in p and "," not in p)]
        dash = bool(re.search(r"(^|\s)-(\s|$)", line) or "--" in line)
        if pos:
            gelir_poz = True
            kanit.append("gelir:" + re.sub(r"\s+", " ", line)[:140])
        elif dash:
            gelir_sifir = True
            kanit.append("sifir:" + re.sub(r"\s+", " ", line)[:140])
    if belge:
        sinif = "yararlanan_belge"
    elif gelir_poz:
        sinif = "yararlanan_gelir_satiri"
    elif any(k == "belge_yok_cumlesi" for k in kanit):
        sinif = "yararlanmayan"
    elif gelir_sifir:
        sinif = "sifir_satir"
    elif "teşvik" in text.lower():
        sinif = "bilinmeyen_politika"
    else:
        sinif = "bilinmeyen"
    return {"sinif": sinif, "kanit": kanit[:4]}


def firma_sinif(a, b, sertifika_only=False):
    labs = {a, b}
    var = {"yararlanan_belge"} if sertifika_only else {"yararlanan_belge", "yararlanan_gelir_satiri"}
    if labs & var:
        return "yararlanan"
    if "yararlanmayan" in labs or "sifir_satir" in labs:
        return "yararlanmayan"
    return "bilinmeyen"


def smd(a, b):
    a = [x for x in a if x is not None]
    b = [x for x in b if x is not None]
    if len(a) < 2 or len(b) < 2:
        return None
    ma, mb = statistics.fmean(a), statistics.fmean(b)
    va = statistics.pvariance(a)
    vb = statistics.pvariance(b)
    sp = math.sqrt((va + vb) / 2)
    if sp == 0:
        return None
    return (ma - mb) / sp


def main():
    liste = {r["kod"]: r for r in csv.DictReader((ROOT / "marj_sirket_liste.csv").open(encoding="utf-8"))}
    ham = defaultdict(dict)
    for r in csv.DictReader((ROOT / "marj_ham.csv").open(encoding="utf-8")):
        ham[r["kod"]][int(r["yil"])] = r
    kodlar = sorted(p.stem for p in CACHE.glob("*.json"))
    firmalar = []
    for k in kodlar:
        y16 = sinif_metin((CACHE / f"{k}_2016.txt").read_text(encoding="utf-8", errors="replace") if (CACHE / f"{k}_2016.txt").exists() else None)
        y22 = sinif_metin((CACHE / f"{k}_2022.txt").read_text(encoding="utf-8", errors="replace") if (CACHE / f"{k}_2022.txt").exists() else None)
        sin = firma_sinif(y16["sinif"], y22["sinif"])
        sin_belge = firma_sinif(y16["sinif"], y22["sinif"], sertifika_only=True)
        row = {
            "kod": k,
            "sinif": sin,
            "sinif_yalniz_belge": sin_belge,
            "y2016": y16["sinif"],
            "y2022": y22["sinif"],
            "kanit": (y16["kanit"] + y22["kanit"])[:3],
            "ana": liste.get(k, {}).get("ana"),
            "grup": liste.get(k, {}).get("grup"),
            "sektor": liste.get(k, {}).get("sektor"),
        }
        if k in ham:
            for y in (2016, 2017, 2018, 2019, 2023):
                if y not in ham[k]:
                    continue
                r = ham[k][y]
                row[f"cek_{y}"] = marj(r, cekirdek)
                row[f"vo_{y}"] = marj(r, lambda z: fnum(z.get("vergi_oncesi")))
                row[f"logsat_{y}"] = None if not fnum(r.get("satis")) or fnum(r["satis"]) <= 0 else math.log(fnum(r["satis"]))
                s = fnum(r.get("satis"))
                yd = fnum(r.get("yurtdisi"))
                row[f"ihr_{y}"] = None if not s or yd is None else yd / s
            if row.get("cek_2016") is not None and row.get("cek_2023") is not None:
                row["d_cek"] = (row["cek_2023"] - row["cek_2016"]) * 100
            if row.get("vo_2016") is not None and row.get("vo_2023") is not None:
                row["d_vo"] = (row["vo_2023"] - row["vo_2016"]) * 100
        firmalar.append(row)

    def blok(alt, alan):
        return ozet([r.get(alan) for r in alt])

    def grup_tablo(sinif_alan):
        out = {}
        for ad in ("yararlanan", "yararlanmayan", "bilinmeyen"):
            alt = [r for r in firmalar if r[sinif_alan] == ad]
            out[ad] = {
                "n_firma": len(alt),
                "n_d_cek": sum(r.get("d_cek") is not None for r in alt),
                "n_d_vo": sum(r.get("d_vo") is not None for r in alt),
                "cek_2016": blok(alt, "cek_2016"),
                "cek_2023": blok(alt, "cek_2023"),
                "vo_2016": blok(alt, "vo_2016"),
                "vo_2023": blok(alt, "vo_2023"),
                "d_cek": blok(alt, "d_cek"),
                "d_vo": blok(alt, "d_vo"),
                "kod": [r["kod"] for r in alt],
            }
        return out

    def fark(tab, alan):
        a = tab["yararlanan"][alan]["medyan"]
        b = tab["yararlanmayan"][alan]["medyan"]
        if a is None or b is None:
            return None
        return a - b

    tab = grup_tablo("sinif")
    # yanlış sınıflama: bilinmeyen = yararlanmayan
    yanlis = []
    for r in firmalar:
        q = dict(r)
        if q["sinif"] == "bilinmeyen":
            q["sinif"] = "yararlanmayan"
        yanlis.append(q)
    # geçici olarak firmalar yerine yanlis kullan
    eski = firmalar
    firmalar = yanlis
    tab_yanlis = grup_tablo("sinif")
    firmalar = eski
    # yalnız belge
    tab_belge = grup_tablo("sinif_yalniz_belge")

    # Kardemir A/B düş
    firmalar_kd = [r for r in firmalar if r["kod"] not in ("KRDMA", "KRDMB")]
    eski = firmalar
    firmalar = firmalar_kd
    tab_kd = grup_tablo("sinif")
    firmalar = eski

    def denge(sol, sag):
        rows = []
        for ad, alan in (
            ("log_satis_2016", "logsat_2016"),
            ("cekirdek_2016", "cek_2016"),
            ("vergi_oncesi_2016", "vo_2016"),
            ("ihracat_payi_2016", "ihr_2016"),
        ):
            a = [r.get(alan) for r in sol]
            b = [r.get(alan) for r in sag]
            d = smd(a, b)
            rows.append({
                "degisken": ad,
                "n_yararlanan": sum(x is not None for x in a),
                "n_diger": sum(x is not None for x in b),
                "ort_yararlanan": None if not any(x is not None for x in a) else statistics.fmean(x for x in a if x is not None),
                "ort_diger": None if not any(x is not None for x in b) else statistics.fmean(x for x in b if x is not None),
                "smd": d,
                "dengesiz": None if d is None else abs(d) > 0.1,
            })
        return rows

    yar = [r for r in firmalar if r["sinif"] == "yararlanan"]
    yok = [r for r in firmalar if r["sinif"] == "yararlanmayan"]
    bil = [r for r in firmalar if r["sinif"] == "bilinmeyen"]

    # ön dönem medyan yolu
    def yol(alt, alan):
        return {str(y): ozet([r.get(f"{alan}_{y}") for r in alt]) for y in (2016, 2017, 2018, 2019, 2023)}

    sanko = next(r for r in firmalar if r["kod"] == "SANKO")
    sonuc = {
        "evren": "KAP metni önbelleği, 2023 satışına göre ilk 100 faaliyet firması. Yıl bazında BIST 100 üyeliği kurulmadı.",
        "metin": {"2016": sum(r["y2016"] != "metin_yok" for r in firmalar), "2022": sum(r["y2022"] != "metin_yok" for r in firmalar)},
        "tablo": tab,
        "fark_d_cek": fark(tab, "d_cek"),
        "fark_d_vo": fark(tab, "d_vo"),
        "yanlis_bilinmeyen_kontrol": {
            "fark_d_cek": fark(tab_yanlis, "d_cek"),
            "fark_d_vo": fark(tab_yanlis, "d_vo"),
            "d_cek": {k: tab_yanlis[k]["d_cek"] for k in tab_yanlis},
            "d_vo": {k: tab_yanlis[k]["d_vo"] for k in tab_yanlis},
        },
        "yalniz_belge": {
            "n": {k: tab_belge[k]["n_firma"] for k in tab_belge},
            "fark_d_cek": fark(tab_belge, "d_cek"),
            "fark_d_vo": fark(tab_belge, "d_vo"),
            "d_cek_yar": tab_belge["yararlanan"]["d_cek"],
            "d_vo_yar": tab_belge["yararlanan"]["d_vo"],
        },
        "kardemir_ab_dusulunce": {
            "n_yar": tab_kd["yararlanan"]["n_firma"],
            "d_cek": tab_kd["yararlanan"]["d_cek"],
            "d_vo": tab_kd["yararlanan"]["d_vo"],
        },
        "smd_gercek_kontrol": denge(yar, yok),
        "smd_bilinmeyen_yanlis": denge(yar, bil),
        "sektor_yar": dict(Counter(r["ana"] for r in yar)),
        "sektor_bil": dict(Counter(r["ana"] for r in bil)),
        "sanko": {k: sanko.get(k) for k in {"kod", "ana", "sektor", "grup", "d_cek", "d_vo", "cek_2016", "cek_2023", "vo_2016", "vo_2023", "logsat_2016", "ihr_2016"} | {f"cek_{y}" for y in (2016, 2017, 2018, 2019)} | {f"vo_{y}" for y in (2016, 2017, 2018, 2019)}},
        "yol_yar_cek": yol(yar, "cek"),
        "yol_bil_cek": yol(bil, "cek"),
        "yol_yar_vo": yol(yar, "vo"),
        "listeler": {
            "yararlanan": [r["kod"] for r in yar],
            "yararlanmayan": [r["kod"] for r in yok],
            "bilinmeyen": [r["kod"] for r in bil],
            "gelir_satiri_olup_belge_yok": [r["kod"] for r in firmalar if r["sinif"] == "yararlanan" and r["sinif_yalniz_belge"] != "yararlanan"],
        },
    }
    (ROOT / "tesvik_secilim.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8")
    print("n", {k: tab[k]["n_firma"] for k in tab})
    print("d_cek yar", tab["yararlanan"]["d_cek"])
    print("d_vo yar", tab["yararlanan"]["d_vo"])
    print("sanko d", sanko.get("d_cek"), sanko.get("d_vo"), "cek16", sanko.get("cek_2016"), "vo16", sanko.get("vo_2016"))
    print("fark cek", sonuc["fark_d_cek"], "fark vo", sonuc["fark_d_vo"])
    print("yanlis", sonuc["yanlis_bilinmeyen_kontrol"]["fark_d_cek"], sonuc["yanlis_bilinmeyen_kontrol"]["fark_d_vo"])
    print("belge", sonuc["yalniz_belge"])
    print("gelir only", sonuc["listeler"]["gelir_satiri_olup_belge_yok"])
    print("smd yanlis", json.dumps(sonuc["smd_bilinmeyen_yanlis"], ensure_ascii=False)[:800])


if __name__ == "__main__":
    main()
