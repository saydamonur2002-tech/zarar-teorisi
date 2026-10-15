"""Seçici kredi, ücret-üretim ve maliye modeli: ölçüm paneli (DKBE) ve 4 senaryolu simülasyon.

Kaynak: Google Sheet "Secici_Kredi_Veri_DOLU" (28 Eylül 2026). Bu dosya tablonun formüllerinin
Python'a birebir taşınmış halidir; tablonun kendi hesaplarıyla parite testi var (test_secici_kredi.py).
Kalibrasyon bu dosyada değil secici_kredi_kalibre.py içindedir.

Girdi: secici_kredi_veri.csv (V01-V39, 2015-2025; her satırın durumu ve notu), secici_kredi_param.json
(22 gösterge eşiği, Parametreler, Politika_Kolları). Etiketler: 'resmi', 'tahmin', 'varsayim', 'bos'.

Çalıştır: python3 secici_kredi.py   (çıktı: secici_kredi_olcum.csv, secici_kredi_sim.csv)
"""

import csv
import json
from pathlib import Path

KOK = Path(__file__).resolve().parent
YILLAR = list(range(2015, 2026))
T = 20


def veri():
    """{kod: {yıl: değer}}; boş hücre yok sayılır."""
    out, durum = {}, {}
    for r in csv.DictReader(open(KOK / "secici_kredi_veri.csv", encoding="utf-8-sig")):
        out[r["kod"]] = {y: float(r[str(y)]) for y in YILLAR if r.get(str(y)) not in (None, "")}
        durum[r["kod"]] = r["durum"]
    return out, durum


def sabitler():
    return json.load(open(KOK / "secici_kredi_param.json", encoding="utf-8"))


# ---- ölçüm paneli ---------------------------------------------------------------------------

def _g(V, k, y):
    return V[k].get(y)


def gostergeler(V, y):
    """22 göstergenin ham değeri (veri yoksa None). Tanımlar tablodaki formüllerdir."""
    g = lambda k: _g(V, k, y)
    ok = lambda *xs: all(x is not None for x in xs)
    d = {}
    d["A1"] = g("V02") / g("V01") if ok(g("V02"), g("V01")) else None
    d["A2"] = (g("V03") - g("V04")) / g("V01") if ok(g("V03"), g("V04"), g("V01")) else None
    d["A3"] = (g("V05") + g("V06")) / g("V01") if ok(g("V05"), g("V06"), g("V01")) else None
    d["A4"] = g("V07") / g("V08") if ok(g("V07"), g("V08")) else None
    d["A5"] = g("V09")
    d["A6"] = g("V37") / g("V36") if ok(g("V37"), g("V36")) else None
    d["B1"] = g("V11") / g("V10") if ok(g("V11"), g("V10")) else None
    d["B2"] = g("V12") - ((1 + g("V13")) * (1 + g("V24")) - 1) if ok(g("V12"), g("V13"), g("V24")) else None
    d["B3"] = g("V14") - g("V09") if ok(g("V14"), g("V09")) else None
    d["C1"] = g("V16") / g("V15") if ok(g("V16"), g("V15")) else None
    d["C2"] = g("V18") / g("V17") if ok(g("V18"), g("V17")) else None
    d["C3"] = (g("V17") - g("V18") - g("V19") - g("V20")) / g("V17") if ok(g("V17"), g("V18"), g("V19"), g("V20")) else None
    d["C4"] = g("V21") / g("V15") if ok(g("V21"), g("V15")) else None
    d["D1"] = (1 + g("V22")) / (1 + g("V24")) - 1 - g("V23") if ok(g("V22"), g("V24"), g("V23")) else None
    d["D2"] = g("V25") / g("V26") if ok(g("V25"), g("V26")) else None
    d["D3"] = g("V30") / g("V31") if ok(g("V30"), g("V31")) else None
    d["D4"] = g("V32") / g("V33") if ok(g("V32"), g("V33")) else None
    d["E1"] = g("V27") / g("V28") if ok(g("V27"), g("V28")) else None
    d["E2"] = g("V29") / g("V28") if ok(g("V29"), g("V28")) else None
    d["E3"] = g("V35") / g("V34") if ok(g("V35"), g("V34")) else None
    return d


def skor(v, guvenli, kritik):
    if v is None:
        return None
    return max(0.0, min(100.0, 100 * (v - guvenli) / (kritik - guvenli)))


def olcum(V, y):
    """Gösterge, skor, sütun skorları (A-E), DKBE ve rejim etiketi."""
    S = sabitler()["gostergeler"]
    gs = gostergeler(V, y)
    sk = {x["kod"]: skor(gs.get(x["kod"]), x["guvenli"], x["kritik"]) for x in S if x["kod"] in gs}
    kol = {}
    for c in "ABCDE":
        xs = [(x["agirlik"], sk[x["kod"]]) for x in S if x["kod"].startswith(c) and sk.get(x["kod"]) is not None]
        kol[c] = sum(w * s for w, s in xs) / sum(w for w, _ in xs) if xs else None
    ks = [v for v in kol.values() if v is not None]
    dkbe = sum(ks) / len(ks) if ks else None
    rej = None if dkbe is None else ("Geniş koridor" if dkbe < 33 else "Daralan koridor" if dkbe < 66 else "Dar koridor")
    return {"yil": y, "gosterge": gs, "skor": sk, "sutun": kol, "DKBE": dkbe, "rejim": rej, "kapsam": sum(1 for v in gs.values() if v is not None)}


def minsky(V, y):
    g = lambda k: _g(V, k, y)
    if None in (g("V01"), g("V02"), g("V05"), g("V06")):
        return None
    fark, ds, faiz = g("V01") - g("V02"), g("V05") + g("V06"), g("V05")
    return "Hedge" if fark >= ds else ("Spekülatif" if fark >= faiz else "Ponzi")


# ---- simülasyon ----------------------------------------------------------------------------

def z0(P, bilesen=False):
    """t0 talep tutarlılığı için kalibrasyon kalemi (tablonun Z0 formülü)."""
    ih = P["rn"] + P["pi0"] + P["spread"]
    yh = P["om0"] * P["AD0"]

    def hane(y, cp, d0, c, sh):
        ds = (ih + P["am"]) * d0 / (1 + P["pi0"])
        av = y - ds
        nb = min(max(0, cp - av), max(0, P["dsr_ref"] * y - ds) / (ih + P["am"]))
        cc = (cp + c * (av - cp) if av >= cp else av + nb) + P["ccp_ref"] * yh * sh
        return cc

    c1 = hane(P["th1"] * yh, P["ph1"] * P["Cf0"], P["D10"], P["c1"], P["sh1"])
    c2 = hane((1 - P["th1"]) * yh, (1 - P["ph1"]) * P["Cf0"], P["D20"], P["c2"], 1 - P["sh1"])
    ck = P["ck"] * (1 - P["om0"]) * P["AD0"]
    i_ = P["inv0"] * P["Q0"]
    g_ = P["G0"] * P["Q0"]
    m = P["mc"] * (c1 + c2 + ck) + P["mi"] * i_ + P["mx"] * P["X0"] + P["mg"] * g_
    if bilesen:
        return dict(c1=c1, c2=c2, ck=ck, i=i_, g=g_, m=m, ic_ithal=P["mc"] * (c1 + c2 + ck) + P["mi"] * i_ + P["mg"] * g_)
    return P["AD0"] - (c1 + c2 + ck + i_ + g_ + P["X0"] - m)


def kollar(s):
    """s = 1..4 -> politika kolu sözlüğü."""
    K = sabitler()["kollar"]
    return {k: v[s - 1] for k, v in K.items()}


def sim(P, arm, T=T):
    """Tablonun Sim_S sayfası: T dönemlik yol. P parametre sözlüğü, arm politika kolu."""
    a = arm
    seff = a["sp"] * (1 - a["leak"] * (1 - a["disc"]))
    Z0 = P["Z0"] if "Z0" in P else z0(P)
    prev = dict(Q=P["Q0"], AD=P["AD0"], pi=P["pi0"], rdep=0.0, om=P["om0"], D1=P["D10"], D2=P["D20"], X=P["X0"],
                loc=0.0, cad=P["cad0"], A=100.0, gprodL=P["gprod0"])
    rows = []
    for t in range(1, T + 1):
        r = {"t": t, "seff": seff}
        r["gt"] = P["tfp0"] + P["tfpk"] * (seff - P["sref"])
        r["cred"] = max(0.05, min(0.9, a["cred"] - P["chi"] * max(0, prev["cad"] - P["cads"])))
        r["pie"] = r["cred"] * P["pitar"] + (1 - r["cred"]) * prev["pi"]
        r["i"] = max(0.0, P["rn"] + r["pie"] + a["tay"] * (prev["pi"] - P["pitar"]) + a["iadd"])
        r["rr"] = r["i"] - r["pie"]
        r["dep"] = max(-0.1, r["pie"] - P["pistar"] + P["kap"] * max(0, prev["cad"] - P["cads"]) - P["rho"] * (r["rr"] - P["rn"]))
        r["ih"] = r["i"] + P["spread"]
        r["gw"] = a["ind"] * prev["pi"] + a["wr"]
        r["Yh"] = prev["om"] * prev["AD"]
        r["Cf"] = P["Cf0"] * (1 + P["gpop"]) ** t
        r["NBd"] = a["ccp"] * r["Yh"]
        r["CC"] = P["cc"] * prev["AD"]
        r["I"] = prev["Q"] * P["inv0"] * (1 - P["sig"] * (r["rr"] - P["rn"])) + P["mu"] * (seff - P["sref"]) * r["CC"]
        r["Q"] = prev["Q"] * (1 + r["gt"] + P["v"] * (r["I"] / prev["Q"] - P["irep"]))
        r["gprodL"] = r["Q"] / prev["Q"] - 1 - P["gL"]
        # hane gruplari
        res = {}
        for n, th, ph, D, c, sh in ((1, P["th1"], P["ph1"], prev["D1"], P["c1"], P["sh1"]), (2, 1 - P["th1"], 1 - P["ph1"], prev["D2"], P["c2"], 1 - P["sh1"])):
            Y = th * r["Yh"]
            Cp = ph * r["Cf"] * (1 - a["socw"])
            DS = (r["ih"] + P["am"]) * D / (1 + prev["pi"])
            Int = r["ih"] * D / (1 + prev["pi"])
            Av = Y - DS
            Gap = max(0, Cp - Av)
            NBn = min(Gap, max(0, a["dsr"] * Y - DS) / (r["ih"] + P["am"]))
            Un = Gap - NBn
            C = (Cp + c * (Av - Cp) if Av >= Cp else Av + NBn) + r["NBd"] * sh
            res[n] = dict(Y=Y, Cp=Cp, DS=DS, Int=Int, Av=Av, Gap=Gap, NBn=NBn, Un=Un, C=C, D=D, sh=sh,
                          ms="Hedge" if Y - Cp >= DS else ("Spekülatif" if Y - Cp >= Int else "Ponzi"))
        r["Ctot"] = res[1]["C"] + res[2]["C"]
        r["Ck"] = P["ck"] * (1 - prev["om"]) * prev["AD"]
        r["IB"] = max(0, r["rr"]) * P["b"] * prev["Q"]
        r["G"] = P["G0"] * prev["Q"] + a["socw"] * r["Cf"] - P["crowd"] * (r["IB"] - P["rn"] * P["b"] * prev["Q"])
        r["X"] = prev["X"] * (1 + P["gwld"] + P["ex"] * prev["rdep"] + P["qx"] * prev["loc"])
        r["loc"] = max(0.0, min(P["locmax"], prev["loc"] + P["lloc"] * (seff - P["sref"])))
        r["M"] = (P["mc"] * (r["Ctot"] + r["Ck"]) + P["mi"] * (1 - r["loc"]) * r["I"] + P["mx"] * (1 - r["loc"]) * r["X"] + P["mg"] * r["G"]) * (1 - P["em"] * prev["rdep"])
        r["NFP"] = P["nfp"] * prev["AD"]
        r["Z"] = Z0 * prev["Q"] / P["Q0"]
        r["AD"] = r["Ctot"] + r["Ck"] + r["I"] + r["G"] + r["X"] - r["M"] + r["Z"]
        r["gAD"] = r["AD"] / prev["AD"] - 1
        r["u"] = r["AD"] / r["Q"]
        r["pi"] = r["pie"] + P["alpha"] * (r["u"] - 1) + P["pt"] * r["dep"] + P["wp"] * (1 - a["rek"]) * max(0, r["gw"] - prev["pi"] - prev["gprodL"])
        r["rdep"] = r["dep"] - (r["pi"] - P["pistar"])
        r["om"] = prev["om"] * (1 + r["gw"]) / ((1 + r["pi"]) * (1 + r["gprodL"]))
        r["rw"] = 100 * (r["om"] * r["AD"] / (1 + P["gL"]) ** t) / (P["om0"] * P["AD0"])
        for n in (1, 2):
            x = res[n]
            x["Dn"] = x["D"] * (1 - P["am"]) / (1 + r["pi"]) + x["NBn"] + r["NBd"] * x["sh"]
            r[f"gu{n}"], r[f"dsr{n}"], r[f"ms{n}"] = x["NBn"] / x["Y"], x["DS"] / x["Y"], x["ms"]
            r[f"NBn{n}"], r[f"Un{n}"], r[f"D{n}"] = x["NBn"], x["Un"], x["Dn"]
        r["cad"] = (r["M"] + r["NFP"] - r["X"]) / r["AD"]
        r["ndk"] = (r["X"] - P["mx"] * (1 - r["loc"]) * r["X"] * (1 - P["em"] * prev["rdep"]) - r["NFP"]) / r["X"]
        r["A"] = prev["A"] * (1 + P["ap"] * ((1 - seff) * r["CC"] / prev["AD"] - P["unpref"]) - P["apr"] * (r["rr"] - P["rn"]))
        sc = lambda v, s, c: max(0.0, min(100.0, 100 * (v - P[s]) / (P[c] - P[s])))
        r["s1"], r["s2"] = sc(r["gu1"], "k1s", "k1c"), sc(r["dsr1"], "k2s", "k2c")
        r["s3"], r["s4"] = sc(1 - seff, "k3s", "k3c"), sc(r["cad"], "k4s", "k4c")
        r["s5"], r["s6"] = sc(r["rr"] - r["gAD"], "k5s", "k5c"), sc(r["pi"], "k6s", "k6c")
        r["kor"] = sum(r[f"s{k}"] for k in range(1, 7)) / 6
        r["rej"] = "Geniş koridor" if r["kor"] < 33 else "Daralan koridor" if r["kor"] < 66 else "Dar koridor"
        rows.append(r)
        prev = dict(Q=r["Q"], AD=r["AD"], pi=r["pi"], rdep=r["rdep"], om=r["om"], D1=r["D1"], D2=r["D2"], X=r["X"],
                    loc=r["loc"], cad=r["cad"], A=r["A"], gprodL=r["gprodL"])
    return rows


def varsayilan():
    return dict(sabitler()["parametreler"])


def main():
    V, durum = veri()
    with open(KOK / "secici_kredi_olcum.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["yil", "kapsam", "A", "B", "C", "D", "E", "DKBE", "rejim", "minsky_toplam_hane"])
        for y in YILLAR:
            o = olcum(V, y)
            w.writerow([y, o["kapsam"]] + [("" if o["sutun"][c] is None else round(o["sutun"][c], 2)) for c in "ABCDE"]
                       + ["" if o["DKBE"] is None else round(o["DKBE"], 2), o["rejim"], minsky(V, y)])
    P = varsayilan()
    with open(KOK / "secici_kredi_sim.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["senaryo", "t", "pi", "i", "dep", "gAD", "cad", "gu1", "rw", "A", "loc", "kor", "rejim"])
        for s in (1, 2, 3, 4):
            for r in sim(P, kollar(s)):
                w.writerow([f"S{s}", r["t"]] + [round(r[k], 4) for k in ("pi", "i", "dep", "gAD", "cad", "gu1", "rw", "A", "loc", "kor")] + [r["rej"]])
    print("yazıldı: secici_kredi_olcum.csv, secici_kredi_sim.csv")


if __name__ == "__main__":
    main()
