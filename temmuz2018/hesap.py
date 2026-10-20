"""Temmuz 2018 çıpa kopuşu. Kurallar: temmuz2018/ON_KAYIT.md."""
import json
import math
import re
import ssl
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

KOK = Path(__file__).resolve().parent
CTX = ssl.create_default_context()
AY = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
      "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}


def getir(u, timeout=40):
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0", "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.read()


def yil_iki(yy):
    n = int(yy)
    return 2000 + n if n < 70 else 1900 + n


def parse_h10(yol):
    html = Path(yol).read_text(errors="replace")
    out = {}
    for m in re.finditer(r">\s*(\d{1,2})-([A-Z]{3})-(\d{2})\s*</th>\s*<td[^>]*>\s*([0-9.]+|ND|na)?\s*<", html):
        d, mon, yy, val = m.group(1), m.group(2), m.group(3), m.group(4)
        if not val or val in ("ND", "na"):
            continue
        dt = datetime(yil_iki(yy), AY[mon], int(d))
        out[dt] = float(val)
    return out


def iso(d):
    return d.strftime("%Y-%m-%d")


def cum(seri, gunler, i_son, i_ilk):
    a, b = gunler[i_son], gunler[i_ilk]
    if a not in seri or b not in seri or seri[b] <= 0 or seri[a] <= 0:
        return None
    return 100.0 * math.log(seri[a] / seri[b])


def esit(try_c, emsaller, gunler, i_son, i_ilk):
    """Eşit ağırlık. En az 3 emsalin iki ucu varsa."""
    parca = []
    for ad, seri in emsaller.items():
        c = cum(seri, gunler, i_son, i_ilk)
        if c is not None:
            parca.append(c)
    if len(parca) < 3 or try_c is None:
        return None, len(parca)
    return try_c - float(np.mean(parca)), len(parca)


def sentetik_agirlik(try_s, emsaller, gunler):
    """2017-01-03 .. 2018-04-30, ızgara, ağırlık ≥ 0, toplam 1."""
    bas, son = datetime(2017, 1, 3), datetime(2018, 4, 30)
    adlar = list(emsaller)
    xs, ys = [], []
    for i in range(1, len(gunler)):
        t, p = gunler[i], gunler[i - 1]
        if not (bas <= t <= son):
            continue
        rt = cum(try_s, gunler, i, i - 1)
        if rt is None:
            continue
        row = []
        iyi = True
        for ad in adlar:
            c = cum(emsaller[ad], gunler, i, i - 1)
            if c is None:
                iyi = False
                break
            row.append(c)
        if iyi:
            xs.append(row)
            ys.append(rt)
    X = np.asarray(xs, float)
    y = np.asarray(ys, float)
    if len(y) < 50:
        return None, len(y)
    # ızgara 0.1. Dört ağırlık.
    eniyi, en_hata = None, None
    adim = np.linspace(0, 1, 11)
    for a in adim:
        for b in adim:
            if a + b > 1:
                continue
            for c in adim:
                if a + b + c > 1:
                    continue
                d = 1 - a - b - c
                if d < -1e-9:
                    continue
                w = np.array([a, b, c, max(d, 0.0)])
                hata = float(np.mean((y - X @ w) ** 2))
                if en_hata is None or hata < en_hata:
                    en_hata, eniyi = hata, w
    return {ad: float(w) for ad, w in zip(adlar, eniyi)}, len(y)


def sentetik_fark(try_c, emsaller, gunler, i_son, i_ilk, agirlik):
    if try_c is None or agirlik is None:
        return None
    top = 0.0
    for ad, w in agirlik.items():
        c = cum(emsaller[ad], gunler, i_son, i_ilk)
        if c is None:
            return None
        top += w * c
    return try_c - top


def holm(ps):
    m = len(ps)
    order = np.argsort(ps)
    adj = np.empty(m)
    run = 0.0
    for rank, j in enumerate(order):
        run = max(run, (m - rank) * float(ps[j]))
        adj[j] = min(1.0, run)
    return adj


def p_tek(goz, dagilim):
    return (1 + np.sum(np.asarray(dagilim) >= goz)) / (1 + len(dagilim))


def evds_aylik(kod, bas, son):
    body = {
        "type": "json", "series": kod, "aggregationTypes": "avg", "formulas": "0",
        "startDate": bas, "endDate": son, "frequency": "5",
        "decimalSeperator": ".", "decimal": "4", "dateFormat": "0", "lang": "TR",
        "yon": "0", "sira": "0", "ozelFormuller": [], "groupSeperator": False, "isRaporSayfasi": False,
    }
    req = urllib.request.Request(
        "https://evds3.tcmb.gov.tr/igmevdsms-dis/fe",
        data=json.dumps(body).encode(),
        headers={"Accept": "application/json", "Content-Type": "application/json",
                 "Referer": "https://evds3.tcmb.gov.tr/"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
        data = json.loads(r.read().decode("utf-8-sig"))
    out = {}
    anahtar = kod.replace(".", "_")
    for it in data.get("items") or []:
        v = it.get(anahtar)
        if v not in (None, ""):
            out[it["Tarih"]] = float(v)
    return out


def ppk_faiz(duy):
    u = f"https://www.tcmb.gov.tr/wps/wcm/connect/TR/TCMB+TR/Main+Menu/Duyurular/Basin/2018/{duy}"
    html = getir(u).decode("utf-8", "replace")
    text = re.sub("<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    m = re.search(r"yüzde\s+([0-9]+,[0-9]+|[0-9]+)", text, flags=re.I)
    oran = None
    if m:
        oran = float(m.group(1).replace(",", "."))
    sabit = "sabit" in text.lower()
    return {"metin_var": "faiz" in text.lower(), "oran": oran, "sabit": sabit, "parca": text[text.lower().find("yüzde"):text.lower().find("yüzde") + 80] if m else text[:180]}


def gazete_gunleri():
    aralik = []
    for y, m, a, b in [(2019, 7, 1, 15), (2020, 11, 1, 15), (2021, 3, 15, 25)]:
        d = datetime(y, m, a)
        while d <= datetime(y, m, b):
            aralik.append(d)
            d += timedelta(days=1)
    bulunan = []
    for d in aralik:
        u = f"https://www.resmigazete.gov.tr/eskiler/{d:%Y/%m/%Y%m%d}.htm"
        try:
            html = getir(u, timeout=20).decode("latin-1", "replace")
        except Exception:
            continue
        text = re.sub("<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text).lower()
        if "merkez bank" in text and "atan" in text:
            bulunan.append(iso(d))
    return bulunan


def main():
    usd_ham = json.loads((KOK / "usd.json").read_text())
    try_s = {}
    for k, v in usd_ham.items():
        dt = datetime.strptime(k, "%d-%m-%Y")
        try_s[dt] = v
    gunler = sorted(try_s)
    yer = {d: i for i, d in enumerate(gunler)}

    emsaller = {
        "brl": parse_h10(KOK / "h10_brl.htm"),
        "zar": parse_h10(KOK / "h10_zar.htm"),
        "mxn": parse_h10(KOK / "h10_mxn.htm"),
        "inr": parse_h10(KOK / "h10_inr.htm"),
    }
    agirlik, n_fit = sentetik_agirlik(try_s, emsaller, gunler)

    olaylar = [
        ("PPK-05", datetime(2018, 5, 23)),
        ("PPK-06", datetime(2018, 6, 7)),
        ("SECIM", datetime(2018, 6, 25)),
        ("GAZETE", datetime(2018, 7, 10)),
        ("PPK-07", datetime(2018, 7, 24)),
        ("OFAC", datetime(2018, 8, 7)),
        ("CELIK", datetime(2018, 8, 15)),
        ("PPK-09", datetime(2018, 9, 13)),
    ]

    def gun0(d):
        while d not in yer and d < datetime(2019, 12, 31):
            d += timedelta(days=1)
        return d if d in yer else None

    olay_gun = []
    for ad, d in olaylar:
        g = gun0(d)
        olay_gun.append((ad, d, g))

    # karşılaştırma
    kars = gazete_gunleri()
    kars_gun = []
    for s in kars:
        d = datetime.strptime(s, "%Y-%m-%d")
        g = gun0(d)
        kars_gun.append((s, g))

    kilitli = [g for _, _, g in olay_gun if g] + [g for _, g in kars_gun if g]

    def yakin(i):
        return any(abs(i - yer[g]) <= 5 for g in kilitli if g in yer)

    def pencere_olc(i):
        if i - 4 < 0 or i + 10 >= len(gunler):
            return None
        try3 = cum(try_s, gunler, i + 3, i - 4)
        try1 = cum(try_s, gunler, i + 1, i - 2)
        kal = cum(try_s, gunler, i + 10, i - 1)
        esit3, n3 = esit(try3, emsaller, gunler, i + 3, i - 4)
        esit1, _ = esit(try1, emsaller, gunler, i + 1, i - 2)
        esitk, _ = esit(kal, emsaller, gunler, i + 10, i - 1)
        sen3 = sentetik_fark(try3, emsaller, gunler, i + 3, i - 4, agirlik)
        return {
            "try3": try3, "try1": try1, "kal": kal,
            "esit3": esit3, "esit1": esit1, "esitk": esitk, "n_emsal": n3,
            "sen3": sen3,
        }

    rng = np.random.default_rng(20180724)
    aday = [i for i in range(4, len(gunler) - 10) if not yakin(i) and datetime(2016, 1, 4) <= gunler[i] <= datetime(2019, 12, 31)]
    sec = rng.choice(aday, size=2000, replace=False) if len(aday) >= 2000 else np.array(aday)
    plasebo = []
    for i in sec:
        olc = pencere_olc(int(i))
        if olc and olc["esit3"] is not None:
            plasebo.append(olc["esit3"])
    plasebo = np.asarray(plasebo, float)

    def skor(ad, g):
        if g is None or g not in yer:
            return {"ad": ad, "durum": "DOGRULANMADI"}
        i = yer[g]
        olc = pencere_olc(i)
        if olc is None or olc["esit3"] is None or len(plasebo) < 100:
            return {"ad": ad, "gun": iso(g), "durum": "DOGRULANMADI", "olc": olc}
        p = float(p_tek(olc["esit3"], plasebo))
        yuzde = 100.0 * float(np.mean(plasebo < olc["esit3"]))
        kalici = None
        if olc["esit3"] > 0 and olc["esitk"] is not None:
            kalici = olc["esitk"] >= 0.5 * olc["esit3"]
        ayni = None
        if olc["sen3"] is not None:
            ayni = (olc["esit3"] > 0 and olc["sen3"] > 0) or (olc["esit3"] < 0 and olc["sen3"] < 0) or olc["esit3"] == 0
        return {"ad": ad, "gun": iso(g), "durum": "hesap", "p": p, "yuzdelik": yuzde, "kalici": kalici, "ayni_isaret": ayni, **{k: olc[k] for k in olc}}

    skorlar = [skor(ad, g) for ad, _, g in olay_gun]
    hesapli = [s for s in skorlar if s.get("durum") == "hesap"]
    if hesapli:
        adj = holm([s["p"] for s in hesapli])
        for s, a in zip(hesapli, adj):
            s["holm"] = float(a)
            buyuk = s["esit3"] > 0 and s["yuzdelik"] >= 90 and s["holm"] < 0.10 and s["kalici"] and s["ayni_isaret"] is True
            s["cubuk"] = bool(buyuk)

    # çıpa
    bek = evds_aylik("TP.PKAUO.S01.F.U", "01-01-2018", "31-12-2018")
    beklenti_faiz = evds_aylik("TP.PKAUO.S04.C.U", "01-05-2018", "30-09-2018")
    # tarihler YYYY-MM veya MM-YYYY? EVDS dateFormat 0 was YYYY-MM in earlier monthly calls... 
    # the daily call used DD-MM-YYYY because frequency daily. Monthly earlier in the project was YYYY-MM.
    g = {}
    for t, v in bek.items():
        g[t] = v - 5.0

    ppk = {
        "PPK-05": ppk_faiz("DUY2018-18"),
        "PPK-06": ppk_faiz("DUY2018-23"),
        "PPK-07": ppk_faiz("DUY2018-27"),
        "PPK-09": ppk_faiz("DUY2018-38"),
    }
    kars_skor = [skor("KARS-" + s, datetime.strptime(s, "%Y-%m-%d")) for s, _g in [(s, None) for s in kars]]
    # gazete günü iş günü değilse gun0
    kars_skor = []
    for s in kars:
        d = datetime.strptime(s, "%Y-%m-%d")
        kars_skor.append(skor("KARS", gun0(d)) | {"gazete": s})

    ozet = {
        "agirlik": agirlik,
        "n_fit": n_fit,
        "n_plasebo": int(len(plasebo)),
        "plasebo_p90": None if len(plasebo) == 0 else float(np.quantile(plasebo, 0.90)),
        "olay": skorlar,
        "karsilastirma_gun": kars,
        "karsilastirma": kars_skor,
        "bek24": bek,
        "g": g,
        "beklenti_faiz": beklenti_faiz,
        "ppk": ppk,
        "emsal_n": {k: len(v) for k, v in emsaller.items()},
    }
    (KOK / "sonuclar.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=2, default=str))
    print("fit", n_fit, "agirlik", agirlik, "plasebo", len(plasebo), "p90", ozet["plasebo_p90"])
    for s in skorlar:
        print(s.get("ad"), s.get("gun"), s.get("durum"),
              "esit3", None if s.get("esit3") is None else round(s["esit3"], 2),
              "sen", None if s.get("sen3") is None else round(s["sen3"], 2),
              "p", s.get("p"), "holm", s.get("holm"), "kal", s.get("kalici"), "cubuk", s.get("cubuk"),
              "try3", None if s.get("try3") is None else round(s["try3"], 2))
    print("g", g)
    print("faiz bek", beklenti_faiz)
    print("ppk", {k: {a: b for a, b in v.items() if a != "parca"} for k, v in ppk.items()})
    print("kars", kars)
    for s in kars_skor:
        print("kars", s.get("gazete"), s.get("gun"), None if s.get("esit3") is None else round(s["esit3"], 2))


if __name__ == "__main__":
    main()
