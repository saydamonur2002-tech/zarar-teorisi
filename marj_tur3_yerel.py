"""Yerel yeniden hesap: büyüklük, beta, TCMB, 2016 boşluğu, çıkan firmalar.

2022 İş Yatırım sütunu, KAP 2023 raporunun TMS 29 karşılaştırmalısı olabilir.
Bu dosya o sütunu olduğu gibi kullanır ve bunu belirtir. Dipnot ayrımı burada yoktur.
"""
from __future__ import annotations

import csv
import json
import math
import statistics
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path

import xlrd

ROOT = Path("/workspace")
YILLAR = list(range(2016, 2024))
ISY = "https://www.isyatirim.com.tr/_layouts/15/IsYatirim.Website/Common/Data.aspx/MaliTablo"
KALEM = {
    "3C": "satis", "3CA": "sm", "3D": "brut", "3DA": "paz", "3DB": "gy", "3DC": "arge",
    "3DD": "diger_gelir", "3DE": "diger_gider", "3DF": "faaliyet",
    "3HA": "yat_gelir", "3HAA": "yat_gider", "3HB": "fin_gelir", "3HC": "fin_gider", "3I": "vergi_oncesi",
    "1AA": "nakit", "2A": "kv_yuk", "2AA": "finborc_kv", "2BA": "finborc_uv",
    "4B": "amortisman", "4C": "isletme_nakit",
}


def fnum(v):
    if v is None or v == "":
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(" ", "").replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def medyan(xs):
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    return None if not xs else statistics.median(xs)


def ortalama(xs):
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    return None if not xs else statistics.fmean(xs)


def pct(xs, p):
    xs = sorted(x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x)))
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
    return {"n": sum(x is not None for x in xs), "p25": pct(xs, 0.25), "medyan": medyan(xs), "p75": pct(xs, 0.75), "ortalama": ortalama(xs)}


def cekirdek(r):
    xs = [fnum(r.get(k)) for k in ("brut", "paz", "gy", "arge")]
    if any(x is None for x in xs):
        return None
    return sum(xs)


def net(r, a, b):
    x, y = fnum(r.get(a)), fnum(r.get(b))
    if x is None or y is None:
        return None
    return x + y


def marj(r, fn):
    s = fnum(r.get("satis"))
    v = fn(r)
    if s is None or s == 0 or v is None:
        return None
    return v / s


def deg(h, kod, fn):
    a, b = marj(h[kod][2022], fn), marj(h[kod][2016], fn)
    if a is None or b is None:
        return None
    return (a - b) * 100


def fold(s):
    return (s.replace("İ", "I").replace("İ", "I").replace("Ş", "S").replace("Ğ", "G")
            .replace("Ü", "U").replace("Ö", "O").replace("Ç", "C").replace("ı", "I").upper())


def sinif_kapanan(ad, kod_ham):
    u = fold(ad + " " + kod_ham)
    if str(kod_ham).endswith(".F") or "BYF" in u or "PORTFOY" in u:
        return "fon"
    if any(k in u for k in ("BANK", "SIGORTA", "GAYRIMENKUL", "YATIRIM ORTAK")):
        return "finans"
    if "HOLDING" in u or "YATIRIM" in u:
        return "holding"
    return "faaliyet"


def kapanan_oku():
    wb = xlrd.open_workbook("/tmp/kapanan.xls")
    sh = wb.sheet_by_index(0)
    rows = []
    for r in range(4, sh.nrows):
        kod = str(sh.cell_value(r, 0)).strip()
        if not kod:
            continue
        raw = sh.cell_value(r, 2)
        if not isinstance(raw, (int, float)):
            continue
        tarih = datetime(1899, 12, 30) + timedelta(days=int(raw))
        if not (datetime(2016, 1, 1) <= tarih <= datetime(2023, 12, 31)):
            continue
        rows.append({
            "kod_ham": kod,
            "kod": kod.split(".")[0].split(":")[0],
            "ad": str(sh.cell_value(r, 1)).strip(),
            "tarih": tarih.date().isoformat(),
            "yil": tarih.year,
            "aciklama": str(sh.cell_value(r, 3)).strip(),
            "sinif": sinif_kapanan(str(sh.cell_value(r, 1)), kod),
        })
    return rows


def isy_cek(kod):
    def cagri(yillar):
        qs = "&".join(f"year{i}={y}&period{i}=12" for i, y in enumerate(yillar, 1))
        url = f"{ISY}?companyCode={kod}&exchange=TRY&financialGroup=XI_29&{qs}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=40) as r:
            data = json.loads(r.read().decode("utf-8-sig"))
        out = {y: {} for y in yillar}
        for it in data.get("value") or []:
            code = str(it.get("itemCode") or "").strip()
            if code not in KALEM:
                continue
            for i, y in enumerate(yillar, 1):
                out[y][KALEM[code]] = fnum(it.get(f"value{i}"))
        return out
    a = cagri((2016, 2017, 2018, 2019))
    b = cagri((2020, 2021, 2022, 2015))
    a.update(b)
    return a


def gostergeler(r):
    if not r or fnum(r.get("satis")) in (None, 0):
        return None
    s = fnum(r["satis"])
    nakit_akis = fnum(r.get("isletme_nakit"))
    kv = fnum(r.get("kv_yuk"))
    borc = None
    if fnum(r.get("finborc_kv")) is not None or fnum(r.get("finborc_uv")) is not None:
        borc = (fnum(r.get("finborc_kv")) or 0) + (fnum(r.get("finborc_uv")) or 0) - (fnum(r.get("nakit")) or 0)
    favok = None
    if fnum(r.get("faaliyet")) is not None and fnum(r.get("amortisman")) is not None:
        favok = fnum(r["faaliyet"]) + abs(fnum(r["amortisman"]))
    fin_g = fnum(r.get("fin_gider"))
    return {
        "cek": marj(r, cekirdek),
        "vo": marj(r, lambda x: fnum(x.get("vergi_oncesi"))),
        "nakit_kv": None if nakit_akis is None or not kv else nakit_akis / kv,
        "netborc_favok": None if borc is None or not favok else borc / favok,
        "faaliyet_fin_gider": None if fin_g in (None, 0) or fnum(r.get("faaliyet")) is None else fnum(r["faaliyet"]) / abs(fin_g),
        "satis": s,
    }


def evds_yillik(kodlar):
    body = {
        "type": "json", "series": "-".join(kodlar),
        "aggregationTypes": "-".join("avg" for _ in kodlar),
        "formulas": "-".join("0" for _ in kodlar),
        "startDate": "01-01-2015", "endDate": "31-12-2023", "frequency": "5",
        "decimalSeperator": ".", "decimal": "4", "dateFormat": "0", "lang": "TR",
        "yon": "0", "sira": "0", "ozelFormuller": [], "groupSeperator": True, "isRaporSayfasi": False,
    }
    req = urllib.request.Request(
        "https://evds3.tcmb.gov.tr/igmevdsms-dis/fe", data=json.dumps(body).encode(),
        headers={"Accept": "application/json", "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as r:
        data = json.loads(r.read().decode("utf-8-sig"))
    ay = {k: defaultdict(list) for k in kodlar}
    for it in data.get("items") or []:
        y = int(str(it["Tarih"])[:4])
        for k in kodlar:
            v = fnum(it.get(k.replace(".", "_")))
            if v is not None:
                ay[k][y].append(v)
    return {k: {y: statistics.fmean(vs) for y, vs in d.items() if len(vs) >= 10} for k, d in ay.items()}


def ols(xs, ys):
    n = len(xs)
    if n < 5:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    varx = sum((x - mx) ** 2 for x in xs)
    if varx <= 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / varx


def beta(h, kod, endeks):
    xs, ys = [], []
    for y in range(2017, 2023):
        if y not in endeks or y - 1 not in endeks:
            continue
        s1, s0 = fnum(h[kod][y]["satis"]), fnum(h[kod][y - 1]["satis"])
        c1, c0 = fnum(h[kod][y]["sm"]), fnum(h[kod][y - 1]["sm"])
        if None in (s1, s0, c1, c0) or min(s1, s0) <= 0:
            continue
        a1, a0 = abs(c1) / endeks[y], abs(c0) / endeks[y - 1]
        b1, b0 = s1 / endeks[y], s0 / endeks[y - 1]
        if min(a1, a0, b1, b0) <= 0:
            continue
        xs.append(math.log(a1) - math.log(a0))
        ys.append(math.log(b1) - math.log(b0))
    return ols(xs, ys)


def tcmb():
    wb = xlrd.open_workbook(ROOT / "Ekonomik faaliyetlere ve yıllara göre firmaların  gelir tablosu .xls")
    sh = wb.sheet_by_name("t7")
    yillar = [int(sh.cell_value(3, c)) for c in range(2, sh.ncols)]
    starts = [r for r in range(4, sh.nrows) if sh.cell_value(r, 0)]
    for i, r0 in enumerate(starts):
        if not str(sh.cell_value(r0, 0)).startswith("C-"):
            continue
        r1 = starts[i + 1]
        kal = {}
        for r in range(r0, r1):
            et = str(sh.cell_value(r, 1)).split("\n")[0].strip()
            kal[et] = {yillar[j]: sh.cell_value(r, 2 + j) for j in range(len(yillar))}

        def g(parca):
            for et, vals in kal.items():
                if parca in et:
                    return vals
            raise KeyError(parca)

        ns, br, eg, fa = g("C-Net satış"), g("Brüt satış karı"), g("E-Faaliyet gider"), g("Faaliyet karı veya")
        kk, kz = g("7-Kambiyo kar"), g("4-Kambiyo zar")
        out = {}
        for y in (2016, 2022):
            out[y] = {
                "brut": br[y] / ns[y],
                "gider": eg[y] / ns[y],
                "faaliyet": fa[y] / ns[y],
                "net_kambiyo": ((kk[y] or 0) - (kz[y] or 0)) / ns[y],
            }
        d_brut = out[2022]["brut"] - out[2016]["brut"]
        d_gider = out[2022]["gider"] - out[2016]["gider"]
        d_faal = out[2022]["faaliyet"] - out[2016]["faaliyet"]
        return {
            "duzey": out,
            "d_brut_pp": d_brut * 100,
            "d_gider_orani_pp": d_gider * 100,
            "d_faaliyet_pp": d_faal * 100,
            "gider_dususu_marja_pp": -d_gider * 100,
            "kimlik_kalan_pp": (d_faal - d_brut + d_gider) * 100,
            "d_net_kambiyo_pp": (out[2022]["net_kambiyo"] - out[2016]["net_kambiyo"]) * 100,
            "kambiyo_faaliyet_icine_giren_pp": 0.0,
        }
    return None


def neden(aciklama):
    u = fold(aciklama)
    if not aciklama:
        return "dosyada aciklama bos"
    if "KONKORDATO" in u:
        return "konkordato ifadesi dosyada var"
    if "BIRLES" in u or "DEVROL" in u or "DEVRAL" in u:
        return "birlesme veya devir ifadesi dosyada var"
    if "IFLAS" in u:
        return "iflas ifadesi dosyada var"
    return "dosyada baska aciklama var"


def main():
    liste = {r["kod"]: r for r in csv.DictReader((ROOT / "marj_sirket_liste.csv").open(encoding="utf-8"))}
    ham = defaultdict(dict)
    for r in csv.DictReader((ROOT / "marj_ham.csv").open(encoding="utf-8")):
        ham[r["kod"]][int(r["yil"])] = r
    panel = [k for k, s in liste.items() if s["grup"] == "faaliyet" and all(
        y in ham[k] and fnum(ham[k][y].get("satis")) not in (None, 0) and fnum(ham[k][y]["satis"]) > 0 for y in YILLAR)]
    panel.sort(key=lambda k: fnum(ham[k][2023]["satis"]), reverse=True)
    ilk = panel[:100]
    dis = [k for k in panel if k not in set(ilk)]

    def blok(kodlar):
        return {
            "n_firma": len(kodlar),
            "cek": ozet([deg(ham, k, cekirdek) for k in kodlar]),
            "faal": ozet([deg(ham, k, lambda r: fnum(r.get("faaliyet"))) for k in kodlar]),
            "vo": ozet([deg(ham, k, lambda r: fnum(r.get("vergi_oncesi"))) for k in kodlar]),
            "fin": ozet([deg(ham, k, lambda r: net(r, "fin_gelir", "fin_gider")) for k in kodlar]),
        }

    # satış eşiği: tam panelin 2023 satış yüzdelikleri
    satis = sorted((fnum(ham[k][2023]["satis"]), k) for k in panel)
    esikler = {}
    for ad, p in (("p20", 0.2), ("p40", 0.4), ("p60", 0.6), ("p80", 0.8), ("p100_ilk100", None)):
        if ad == "p100_ilk100":
            ust, alt = ilk, dis
            sinir = fnum(ham[ilk[-1]][2023]["satis"])
        else:
            sinir = pct([s for s, _ in satis], p)
            ust = [k for s, k in satis if s >= sinir]
            alt = [k for s, k in satis if s < sinir]
        esikler[ad] = {"sinir_tl": sinir, "ust": blok(ust), "alt": blok(alt)}

    # 2016 çekirdek medyanının üstü / altı
    c16 = [(marj(ham[k][2016], cekirdek), k) for k in panel]
    m16 = medyan([c for c, _ in c16])
    esikler["c2016_medyan"] = {
        "sinir": m16,
        "ust": blok([k for c, k in c16 if c is not None and c >= m16]),
        "alt": blok([k for c, k in c16 if c is not None and c < m16]),
    }

    # beta
    from marj_ayristirma import UFE_PARCA, deflatorler
    secilen, sektor_kod, notlar, yillik = deflatorler()
    cpi = yillik[secilen["tufe"]]
    def endeks_ufe(kod):
        alt = liste[kod]["sektor"]
        kodu = sektor_kod.get(alt)
        if not kodu:
            return None, notlar.get(alt, "ufe yok")
        return yillik.get(kodu), notlar.get(alt)

    b_tufe, b_ufe, b_yok = [], [], []
    for k in ilk:
        bt = beta(ham, k, cpi)
        bu_seri, notu = endeks_ufe(k)
        bu = beta(ham, k, bu_seri) if bu_seri else None
        dc = deg(ham, k, cekirdek)
        b_tufe.append((bt, dc, k))
        if bu is None:
            b_yok.append({"kod": k, "not": notu, "ana": liste[k]["ana"]})
        else:
            b_ufe.append((bu, dc, k))

    def esik_tablo(pairs):
        out = {}
        for t in (0.5, 0.7, 0.8, 0.9, 1.0):
            ust = [dc for b, dc, _ in pairs if b is not None and b >= t]
            out[str(t)] = {"n_beta": sum(b is not None for b, _, _ in pairs), "pay": len(ust) / max(1, sum(b is not None for b, _, _ in pairs)), "cek": ozet(ust)}
        return out

    # 2016 boş
    faal = [s for s in liste.values() if s["grup"] == "faaliyet"]
    bos = []
    for s in faal:
        k = s["kod"]
        v = fnum(ham[k][2016].get("satis")) if 2016 in ham[k] else None
        if v is not None and v > 0:
            continue
        yillar = sorted(y for y in YILLAR if y in ham[k] and fnum(ham[k][y].get("satis")) not in (None, 0) and fnum(ham[k][y]["satis"]) > 0)
        bos.append({
            "kod": k, "ana": s["ana"], "sektor": s["sektor"],
            "ilk_dolu_yil": yillar[0] if yillar else None,
            "satis_2023": fnum(ham[k][2023].get("satis")) if 2023 in ham[k] else None,
        })
    by_yil = defaultdict(int)
    by_ana = defaultdict(int)
    for b in bos:
        by_yil[str(b["ilk_dolu_yil"])] += 1
        by_ana[b["ana"]] += 1
    buyuk = [b for b in bos if b["satis_2023"] and b["satis_2023"] >= fnum(ham[ilk[-1]][2023]["satis"])]

    # çıkanlar
    kapan = kapanan_oku()
    hedef = []
    gor = set()
    for row in kapan:
        if row["sinif"] != "faaliyet" or row["kod"] in gor:
            continue
        gor.add(row["kod"])
        hedef.append(row)

    def cek(row):
        try:
            return row["kod"], isy_cek(row["kod"]), None
        except Exception as exc:  # noqa: BLE001
            return row["kod"], None, str(exc)

    gelen = {}
    with ThreadPoolExecutor(max_workers=6) as ex:
        for fut in as_completed([ex.submit(cek, row) for row in hedef]):
            kod, veri, err = fut.result()
            gelen[kod] = (veri, err)

    cikan = []
    veri_yok = []
    for row in hedef:
        veri, err = gelen.get(row["kod"], (None, "cekilmedi"))
        kayit = {**row, "neden": neden(row["aciklama"])}
        if veri is None:
            kayit["hata"] = err
            veri_yok.append(kayit)
            continue
        dolu = {}
        for y, r in veri.items():
            g = gostergeler(r)
            if g and g["cek"] is not None:
                dolu[str(y)] = g
        if not dolu:
            kayit["hata"] = "hicbir yilda marj yok"
            veri_yok.append(kayit)
            continue
        son = max(int(y) for y in dolu if int(y) < row["yil"]) if any(int(y) < row["yil"] for y in dolu) else None
        once = None
        if son:
            aday = [int(y) for y in dolu if int(y) < son]
            once = max(aday) if aday else None
        kayit["yillar"] = dolu
        kayit["son_tam_yil"] = son
        kayit["onceki_tam_yil"] = once
        kayit["son"] = dolu.get(str(son)) if son else None
        kayit["onceki"] = dolu.get(str(once)) if once else None
        if kayit["son"] and kayit["onceki"] and kayit["son"]["vo"] is not None and kayit["son"]["nakit_kv"] is not None and kayit["onceki"]["nakit_kv"] is not None:
            kar_arti = kayit["son"]["vo"] > 0
            nakit_eksi = kayit["son"]["nakit_kv"] < 0
            kayit["kar_nakit_ayrisir"] = bool(kar_arti and nakit_eksi)
        else:
            kayit["kar_nakit_ayrisir"] = None
        cikan.append(kayit)

    sonuc = {
        "n_panel": len(panel),
        "ilk100": blok(ilk),
        "kucuk": blok(dis),
        "esik": esikler,
        "beta_tufe": {"medyan": medyan([b for b, _, _ in b_tufe]), "esik": esik_tablo(b_tufe)},
        "beta_ufe": {"n": len(b_ufe), "medyan": medyan([b for b, _, _ in b_ufe]), "esik": esik_tablo(b_ufe), "ufe_yok_n": len(b_yok)},
        "beta_ufe_yok": b_yok,
        "tcmb": tcmb(),
        "bos_2016": {"n": len(bos), "faaliyet_n": len(faal), "dolu_n": len(faal) - len(bos), "ilk_yil": dict(by_yil), "ana": dict(by_ana), "esik_ustu_2023": [b["kod"] for b in buyuk]},
        "cikan_olculen": cikan,
        "cikan_veri_yok": veri_yok,
        "kapanan_sayim": {s: sum(1 for row in kapan if row["sinif"] == s) for s in ("faaliyet", "holding", "finans", "fon")},
    }
    (ROOT / "marj_tur3_yerel.json").write_text(json.dumps(sonuc, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "panel": len(panel),
        "ilk": sonuc["ilk100"],
        "kucuk_fin": sonuc["kucuk"]["fin"],
        "kucuk_cek": sonuc["kucuk"]["cek"],
        "tcmb": sonuc["tcmb"],
        "bos": sonuc["bos_2016"]["n"],
        "cikan": len(cikan),
        "veri_yok": len(veri_yok),
        "beta_tufe": sonuc["beta_tufe"]["medyan"],
        "beta_ufe": sonuc["beta_ufe"]["medyan"],
        "ufe_yok": sonuc["beta_ufe"]["ufe_yok_n"],
    }, ensure_ascii=False, indent=2)[:4000])


if __name__ == "__main__":
    main()
