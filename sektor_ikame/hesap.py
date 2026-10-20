"""Sektör ikamesi. Kurallar: sektor_ikame/ON_KAYIT.md."""
import csv
import itertools
import json
import math
from pathlib import Path

import numpy as np

KOK = Path(__file__).resolve().parent


def erf_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def ay_ix(t):
    y, m = t.split("-")
    return int(y) * 12 + int(m) - 1


def q_of(i):
    y, m = divmod(i, 12)
    return f"{y}-Q{m // 3 + 1}"


def sd(xs):
    return float(np.std(np.asarray(xs, float), ddof=1))


def ols(y, X):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    sse = float(resid @ resid)
    sst = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - sse / sst if sst > 0 else 0.0
    return beta, resid, r2


def nw_se(X, resid, bant):
    n, k = X.shape
    xtx = X.T @ X
    S = np.zeros((k, k))
    for t in range(n):
        xt = X[t : t + 1].T
        S += resid[t] ** 2 * (xt @ xt.T)
    for lag in range(1, bant + 1):
        w = 1.0 - lag / (bant + 1.0)
        G = np.zeros((k, k))
        for t in range(lag, n):
            a = X[t : t + 1].T
            b = X[t - lag : t - lag + 1].T
            G += resid[t] * resid[t - lag] * (a @ b.T)
        S += w * (G + G.T)
    try:
        inv = np.linalg.inv(xtx)
    except np.linalg.LinAlgError:
        return None
    V = inv @ S @ inv
    return np.sqrt(np.clip(np.diag(V), 0, None))


def shapley(y, cols):
    """cols: dict name -> vector. Pay of each name."""
    names = list(cols)
    p = len(names)
    if p == 0:
        return {}, 0.0
    phi = {n: 0.0 for n in names}
    nperm = 0
    r_full = None
    for order in itertools.permutations(names):
        nperm += 1
        prev = 0.0
        for i, name in enumerate(order):
            X = np.column_stack([np.ones(len(y))] + [cols[nm] for nm in order[: i + 1]])
            _, _, r2 = ols(y, X)
            phi[name] += r2 - prev
            prev = r2
        r_full = prev
    for n in names:
        phi[n] /= nperm
    return phi, r_full


def holm(ps):
    m = len(ps)
    order = np.argsort(ps)
    adj = np.empty(m)
    run = 0.0
    for rank, j in enumerate(order):
        run = max(run, (m - rank) * ps[j])
        adj[j] = min(1.0, run)
    return adj


def lead_test(rows, xname, controls, bant, pencere, min_pencere):
    """rows: list of dicts with emp, x, and controls. x is already lagged."""
    use = [r for r in rows if r.get("emp") is not None and r.get(xname) is not None and all(r.get(c) is not None for c in controls)]
    if len(use) < pencere:
        return {"n": len(use), "durum": "DOGRULANMADI"}
    y = np.array([r["emp"] for r in use], float)
    x = np.array([r[xname] for r in use], float)
    cols = {xname: x}
    for c in controls:
        cols[c] = np.array([r[c] for r in use], float)
    X = np.column_stack([np.ones(len(y))] + [cols[n] for n in cols])
    beta, resid, r2 = ols(y, X)
    b = float(beta[1])
    se = nw_se(X, resid, bant)
    if se is None or se[1] == 0:
        p = None
    else:
        t = b / se[1]
        p = 1.0 - erf_cdf(t)  # tek taraflı, b>0
    phi, r_full = shapley(y, cols)
    pay = None if r_full is None or r_full <= 0 else phi[xname] / r_full
    # kayan
    tutan = 0
    kurulan = 0
    if len(use) >= pencere:
        for i in range(0, len(use) - pencere + 1):
            sl = use[i : i + pencere]
            yy = np.array([r["emp"] for r in sl], float)
            cc = {xname: np.array([r[xname] for r in sl], float)}
            for c in controls:
                cc[c] = np.array([r[c] for r in sl], float)
            XX = np.column_stack([np.ones(len(yy))] + [cc[n] for n in cc])
            bb, _, _ = ols(yy, XX)
            ph, rf = shapley(yy, cc)
            py = None if rf is None or rf <= 0 else ph[xname] / rf
            kurulan += 1
            if bb[1] > 0 and py is not None and py >= 0.30:
                tutan += 1
    kayan = None if kurulan < min_pencere else tutan / kurulan
    return {
        "n": len(use),
        "b": b,
        "p": None if p is None else float(p),
        "r2": r2,
        "pay": None if pay is None else float(pay),
        "kayan_tutan": tutan,
        "kayan_kurulan": kurulan,
        "kayan": None if kayan is None else float(kayan),
        "durum": "hesap",
    }


def main():
    ham = json.loads((KOK / "ham_ay.json").read_text())

    def seri(kod):
        return {ay_ix(t): v for t, v in ham.get(kod, {}).items()}

    E = seri("TP.DK.USD.S.YTL")
    R = seri("TP.REZVARPD.K1")
    faiz_a = seri("TP.BISPOLFAIZ.TUR")

    def quarter_map(src, how):
        buckets = {}
        for i, v in src.items():
            q = q_of(i)
            buckets.setdefault(q, []).append((i, v))
        out = {}
        for q, pairs in buckets.items():
            pairs.sort()
            vals = [v for _, v in pairs]
            if how == "avg" and len(vals) == 3:
                out[q] = float(np.mean(vals))
            if how == "last" and len(vals) == 3:
                out[q] = float(pairs[-1][1])
            if how == "sonay" and len(vals) == 3:
                out[q] = float(pairs[-1][1])
            if how == "sum" and len(vals) == 3:
                out[q] = float(np.sum(vals))
        return out

    def emp_from(Eq, Rq, bas="2016-Q2", son="2025-Q4"):
        qs = sorted(set(Eq) & set(Rq))
        ee, rr, raw = [], [], {}
        for i, q in enumerate(qs):
            if i == 0:
                continue
            prev = qs[i - 1]
            # ardışık çeyrek
            y, qq = int(q[:4]), int(q[-1])
            yp, qp = int(prev[:4]), int(prev[-1])
            if (y * 4 + qq) - (yp * 4 + qp) != 1:
                continue
            if not (bas <= q <= son):
                continue
            e = 100.0 * math.log(Eq[q] / Eq[prev])
            r = 100.0 * (Rq[q] - Rq[prev]) / Rq[prev]
            ee.append(e)
            rr.append(r)
            raw[q] = (e, r)
        w = sd(ee) / sd(rr)
        emp = {q: e - w * r for q, (e, r) in raw.items()}
        return emp, w, len(ee)

    Eavg = {}
    # çeyrek ortalama ve son ay
    buckets = {}
    for i, v in E.items():
        buckets.setdefault(q_of(i), []).append((i, v))
    E_q, E_son = {}, {}
    for q, pairs in buckets.items():
        pairs.sort()
        if len(pairs) == 3:
            E_q[q] = float(np.mean([v for _, v in pairs]))
            E_son[q] = float(pairs[-1][1])
    R_q = {}
    for i, v in R.items():
        m = divmod(i, 12)[1] + 1
        if m in (3, 6, 9, 12):
            R_q[q_of(i)] = v
    emp, w, n_emp = emp_from(E_q, R_q)
    emp_s, w_s, n_s = emp_from(E_son, R_q)
    faiz_q = quarter_map(faiz_a, "avg")

    # CDS çeyrek sonu farkı
    cds_q = {}
    with open(KOK / "cds_vekili.csv") as f:
        for row in csv.DictReader(f):
            t = row["Date"][:10]
            y, m, d = map(int, t.split("-"))
            q = f"{y}-Q{(m - 1) // 3 + 1}"
            cds_q.setdefault(q, []).append((t, float(row["CDS"])))
    cds_end = {q: sorted(v)[-1][1] for q, v in cds_q.items()}
    dcds = {}
    qs_cds = sorted(cds_end)
    for i in range(1, len(qs_cds)):
        if qs_cds[i] <= "2025-Q4":
            dcds[qs_cds[i]] = cds_end[qs_cds[i]] - cds_end[qs_cds[i - 1]]

    # ISIC vekil
    divs = [f"{n:02d}" for n in range(10, 34)]

    def isic(kind, code):
        return seri(f"TP.{kind}ISICREV4.{code}")

    M = {d: isic("ITH", d) for d in divs}
    X = {d: isic("IHR", d) for d in divs}
    TT = seri("TP.ITHISICREV4.TT")
    petrol = seri("TP.ITHISICREV4.06")

    def qsum(src):
        return quarter_map(src, "sum")

    Mq = {d: qsum(M[d]) for d in divs}
    Xq = {d: qsum(X[d]) for d in divs}
    TTq = qsum(TT)
    petrol_q = qsum(petrol)

    def endeks(q):
        yog = {}
        for d in divs:
            # Boş seri (bölüm 33 mal ticareti yok) çeyreği düşürmez.
            if q not in Mq[d] or q not in Xq[d]:
                continue
            if Xq[d][q] <= 0:
                continue
            yog[d] = Mq[d][q] / (Mq[d][q] + Xq[d][q])
        imalat = sum(Mq[d][q] for d in yog)
        if imalat <= 0 or not yog:
            return None
        return sum(yog[d] * (Mq[d][q] / imalat) for d in yog)

    vekil = {q: endeks(q) for q in sorted(TTq)}
    vekil = {q: v for q, v in vekil.items() if v is not None}

    # 2017-2019 bağımlı bölümler
    yog_baz = {}
    for d in divs:
        ms, xs = 0.0, 0.0
        ok = True
        for y in (2017, 2018, 2019):
            for qq in range(1, 5):
                q = f"{y}-Q{qq}"
                if q not in Mq[d] or q not in Xq[d]:
                    ok = False
                else:
                    ms += Mq[d][q]
                    xs += Xq[d][q]
        if ok and xs > 0:
            yog_baz[d] = ms / (ms + xs)
    ortanca = float(np.median(list(yog_baz.values()))) if yog_baz else None
    bagimli = sorted(d for d, v in yog_baz.items() if v > ortanca) if ortanca is not None else []

    def pay_bagimli(qs):
        num = 0.0
        den = 0.0
        for q in qs:
            if q not in TTq:
                return None
            den += TTq[q]
            for d in bagimli:
                num += Mq[d][q]
        if den == 0:
            return None
        return num / den

    baz_pay = pay_bagimli([f"{y}-Q{qq}" for y in (2017, 2018, 2019) for qq in range(1, 5)])
    q4_pay = pay_bagimli(["2021-Q4"])
    # enerji payı, tanımlayıcı
    def pay_kod(src_q, qs):
        if any(q not in src_q for q in qs) or any(q not in TTq for q in qs):
            return None
        den = sum(TTq[q] for q in qs)
        return None if den == 0 else sum(src_q[q] for q in qs) / den

    M19 = qsum(seri("TP.ITHISICREV4.19"))

    # çeyrek satırlar
    rows = []
    qs = sorted(q for q in emp if "2016-Q2" <= q <= "2025-Q4")
    vekil_qs = sorted(vekil)
    for q in qs:
        # gecikme
        y, qq = int(q[:4]), int(q[-1])
        prev = f"{y}-Q{qq-1}" if qq > 1 else f"{y-1}-Q4"
        rows.append({
            "q": q,
            "emp": emp[q],
            "emp_son": emp_s.get(q),
            "x": vekil.get(prev),
            "faiz": faiz_q.get(q),
            "dcds": dcds.get(q),
        })

    kontroller = ["faiz", "dcds"]  # DXY düştü
    ileri = lead_test(rows, "x", kontroller, bant=2, pencere=16, min_pencere=8)
    # ters: X_t on EMP_{t-1}
    rev_rows = []
    for q in vekil_qs:
        y, qq = int(q[:4]), int(q[-1])
        prev = f"{y}-Q{qq-1}" if qq > 1 else f"{y-1}-Q4"
        if prev < "2016-Q2":
            continue
        rev_rows.append({
            "q": q,
            "emp": vekil[q],  # bağımlı değişken X
            "x": emp.get(prev),  # gecikmeli EMP, lead_test xname
            "faiz": faiz_q.get(q),
            "dcds": dcds.get(q),
        })
    # lead_test expects dep var named emp and regressor named x. Here emp slot is X, x slot is lagged EMP.
    ters = lead_test(rev_rows, "x", kontroller, bant=2, pencere=16, min_pencere=8)

    # kontrolsüz, hüküm değil
    kontrolsuz = lead_test(rows, "x", [], bant=2, pencere=16, min_pencere=8)

    # aylık robustness, kayan 36
    def aylik_emp():
        months = sorted(set(E) & set(R))
        ee, rr, raw = [], [], {}
        for i, m in enumerate(months):
            if i == 0 or months[i - 1] != m - 1:
                continue
            if m < ay_ix("2016-04") or m > ay_ix("2025-12"):
                continue
            e = 100 * math.log(E[m] / E[m - 1])
            r = 100 * (R[m] - R[m - 1]) / R[m - 1]
            ee.append(e)
            rr.append(r)
            raw[m] = e - (sd(ee) and 0)
        w_m = sd(ee) / sd(rr)
        return {m: e - w_m * r for m, (e, r) in ((m, (100 * math.log(E[m] / E[m - 1]), 100 * (R[m] - R[m - 1]) / R[m - 1])) for m in raw)}, w_m

    # düzelt: raw içinde e,r sakla
    months = sorted(set(E) & set(R))
    ee, rr, raw = [], [], {}
    for m in months:
        if m - 1 not in E or m - 1 not in R:
            continue
        if not (ay_ix("2016-04") <= m <= ay_ix("2025-12")):
            continue
        e = 100 * math.log(E[m] / E[m - 1])
        r = 100 * (R[m] - R[m - 1]) / R[m - 1]
        ee.append(e)
        rr.append(r)
        raw[m] = (e, r)
    w_m = sd(ee) / sd(rr)
    emp_m = {m: e - w_m * r for m, (e, r) in raw.items()}

    def endeks_ay(i):
        yog = {}
        for d in divs:
            if i not in M[d] or i not in X[d] or X[d][i] <= 0:
                continue
            yog[d] = M[d][i] / (M[d][i] + X[d][i])
        im = sum(M[d][i] for d in yog)
        if im <= 0:
            return None
        return sum(yog[d] * (M[d][i] / im) for d in yog)

    aylar = []
    for m in sorted(emp_m):
        prev = m - 1
        # faiz aylık düzey, cds aylık yok: çeyrek farkını aya yapıştırmayız. Aylık kontrol yalnız faiz.
        y = m // 12
        mo = m % 12 + 1
        key = f"{y}-{mo:02d}"
        aylar.append({"emp": emp_m[m], "x": endeks_ay(prev), "faiz": faiz_a.get(m)})
    aylik = lead_test(aylar, "x", ["faiz"], bant=3, pencere=36, min_pencere=8)

    # 2021-Q4 katkı
    katki = None
    if ileri.get("durum") == "hesap":
        x_prev = None
        for r in rows:
            if r["q"] == "2021-Q4":
                x_prev = r["x"]
        if x_prev is not None and emp.get("2021-Q4"):
            katki = ileri["b"] * x_prev
            katki_pay = katki / emp["2021-Q4"]

    # HS2 RCA
    hs = json.loads((KOK / "hs2.json").read_text()) if (KOK / "hs2.json").exists() else None
    rca_out = {"durum": "DOGRULANMADI"}
    if hs and hs.get("dunya") and hs.get("tur_x") and hs.get("tur_m"):
        # üç yılda da olan muhabirler
        ortak = None
        for y in ("2017", "2018", "2019"):
            s = set(hs["dunya"].get(y, {}))
            ortak = s if ortak is None else (ortak & s)
        # fasıl kümesi
        fasillar = set()
        for y in ("2017", "2018", "2019"):
            fasillar |= set(hs["tur_x"].get(y, {}))
        def toplam(yil_dict, codes):
            return sum(yil_dict.get(c, {}).get("v", 0) for c in codes)
        rca = {}
        for c in fasillar:
            tx = np.mean([hs["tur_x"].get(y, {}).get(c, {}).get("v", 0) for y in ("2017", "2018", "2019")])
            ttot = np.mean([sum(v.get("v", 0) for v in hs["tur_x"].get(y, {}).values()) for y in ("2017", "2018", "2019")])
            wx = []
            wtot = []
            for y in ("2017", "2018", "2019"):
                sx = 0.0
                st = 0.0
                for rep in ortak:
                    blok = hs["dunya"][y].get(rep, {})
                    sx += blok.get(c, {}).get("v", 0)
                    st += sum(v.get("v", 0) for v in blok.values())
                wx.append(sx)
                wtot.append(st)
            if ttot <= 0 or np.mean(wtot) <= 0 or np.mean(wx) <= 0:
                continue
            rca[c] = (tx / ttot) / (np.mean(wx) / np.mean(wtot))
        secili = sorted(c for c, v in rca.items() if v > 1)
        paylar = {}
        for y, blok in hs["tur_m"].items():
            den = sum(v.get("v", 0) for v in blok.values())
            num = sum(blok.get(c, {}).get("v", 0) for c in secili)
            paylar[y] = None if den == 0 else num / den
        # birim değer, 2017-2019, seçili fasıllar
        oranlar = []
        for c in secili:
            iv, ik, xv, xk = 0.0, 0.0, 0.0, 0.0
            for y in ("2017", "2018", "2019"):
                m = hs["tur_m"].get(y, {}).get(c, {})
                x = hs["tur_x"].get(y, {}).get(c, {})
                iv += m.get("v", 0)
                ik += m.get("kg", 0)
                xv += x.get("v", 0)
                xk += x.get("kg", 0)
            if ik > 0 and xk > 0 and xv > 0:
                oranlar.append((iv / ik) / (xv / xk))
        # Kapsam: HS2 toplamı / Dünya Bankası mal ihracatı. Üç yılın en düşüğü %70'in altındaysa RCA yok.
        wb = {2017: 17825250671274.5, 2018: 19643736517947.3, 2019: 19101899445690.9}
        kapsam_pay = {}
        for y in ("2017", "2018", "2019"):
            s = 0.0
            for rep in (ortak or set()):
                s += sum(v.get("v", 0) for v in hs["dunya"][y].get(rep, {}).values())
            kapsam_pay[y] = s / wb[int(y)]
        if not ortak or len(ortak) < 15 or min(kapsam_pay.values()) < 0.70:
            rca_out = {
                "durum": "DOGRULANMADI",
                "muhabir": len(ortak or set()),
                "kapsam": kapsam_pay,
                "neden": "ortak muhabir ya da kapsam esigi tutmadi",
            }
        else:
            rca_out = {
            "durum": "vekil",
            "muhabir": len(ortak or set()),
            "kapsam": kapsam_pay,
            "fasıl": len(rca),
            "rca_ustu": len(secili),
            "secili": secili,
            "pay": paylar,
            "birim_ortanca": None if not oranlar else float(np.median(oranlar)),
            "birim_n": len(oranlar),
        }

    # yıllık ikame öncülüğü, EMP yıl ortalaması
    yillik = {"durum": "DOGRULANMADI"}
    if rca_out.get("pay"):
        yrows = []
        for y in range(2016, 2026):
            emps = [emp[f"{y}-Q{q}"] for q in range(1, 5) if f"{y}-Q{q}" in emp]
            if len(emps) < 4:
                continue
            yrows.append({
                "q": str(y),
                "emp": float(np.mean(emps)),
                "x": rca_out["pay"].get(str(y - 1)),
                "faiz": float(np.mean([faiz_q[f"{y}-Q{q}"] for q in range(1, 5) if f"{y}-Q{q}" in faiz_q])) if all(f"{y}-Q{q}" in faiz_q for q in range(1, 5)) else None,
                "dcds": dcds.get(f"{y}-Q4"),
            })
        yillik = lead_test(yrows, "x", ["faiz", "dcds"], bant=1, pencere=8, min_pencere=8)

    ozet = {
        "emp": {"w": w, "n": n_emp, "q4": emp.get("2021-Q4"), "w_son": w_s, "q4_son": emp_s.get("2021-Q4")},
        "bagimli": bagimli,
        "ortanca_yogunluk": ortanca,
        "kur_tabani": {
            "baz_2017_2019": baz_pay,
            "q4_2021": q4_pay,
            "fark_puan": None if baz_pay is None or q4_pay is None else (q4_pay - baz_pay) * 100,
            "enerji_06_q4": pay_kod(petrol_q, ["2021-Q4"]),
            "isic19_q4": pay_kod(M19, ["2021-Q4"]),
        },
        "vekil_ileri": ileri,
        "vekil_ters": ters,
        "vekil_kontrolsuz": kontrolsuz,
        "aylik": aylik,
        "katki": None if katki is None else {"bx": katki, "pay": katki_pay, "x_2021q3": x_prev, "emp": emp.get("2021-Q4")},
        "rca": {k: v for k, v in rca_out.items() if k != "secili"} | {"secili_n": len(rca_out.get("secili") or [])},
        "rca_secili": rca_out.get("secili"),
        "yillik_rca": yillik,
        "vekil_q": {q: vekil[q] for q in vekil if "2016-Q1" <= q <= "2025-Q4"},
        "kontroller": kontroller,
    }
    (KOK / "sonuclar.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=2))
    print("EMP", round(w, 3), round(emp["2021-Q4"], 2), "son", round(w_s, 3), round(emp_s["2021-Q4"], 2))
    print("bagimli", bagimli, "ort", None if ortanca is None else round(ortanca, 3))
    print("taban", ozet["kur_tabani"])
    print("ileri", ileri)
    print("ters", ters)
    print("aylik", {k: aylik.get(k) for k in ("n", "b", "p", "pay", "kayan", "kayan_kurulan", "durum")})
    print("katki", ozet["katki"])
    print("rca", ozet["rca"])
    print("yillik", yillik)


if __name__ == "__main__":
    main()
