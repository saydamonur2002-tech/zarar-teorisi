"""Çevirme oranı ve EMP. Kurallar: cevirme_kur/ON_KAYIT.md.
Kontrollü Granger, DXY inmeden kurulmaz."""
import csv
import json
import math
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parent


def sd(xs):
    n = len(xs)
    m = sum(xs) / n
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))


def ay_ekle(y, m, k):
    i = y * 12 + (m - 1) + k
    return i // 12, i % 12 + 1


def anahtar(y, m):
    return f"{y}-{m:02d}"


def ceyrekler():
    y, q = 2015, 1
    while (y, q) <= (2025, 4):
        yield y, q
        q += 1
        if q == 5:
            y, q = y + 1, 1


def main():
    bop = json.loads((KOK / "ham_bop.json").read_text())
    ay = json.loads((KOK / "ham_aylik.json").read_text())

    def B(kod, t):
        return bop[kod].get(t)

    # Kimlik zaten 0. Oran: kullanım / geri ödeme, ikisi de pozitif.
    aylar = []
    y, m = 2006, 1
    while (y, m) <= (2026, 10):
        t = anahtar(y, m)
        row = {"t": t, "y": y, "m": m}
        for ad, kod in {
            "b_st": "TP.ODEAYRSUNUM6.Q167",
            "b_use": "TP.ODEAYRSUNUM6.Q169",
            "b_rep": "TP.ODEAYRSUNUM6.Q170",
            "c_st": "TP.ODEAYRSUNUM6.Q180",
            "c_use": "TP.ODEAYRSUNUM6.Q182",
            "c_rep": "TP.ODEAYRSUNUM6.Q183",
        }.items():
            v = B(kod, t)
            if v is not None:
                row[ad] = v
        if t in ay.get("TP.DK.USD.S.YTL", {}):
            row["E"] = ay["TP.DK.USD.S.YTL"][t]
        if t in ay.get("TP.REZVARPD.K1", {}):
            row["R"] = ay["TP.REZVARPD.K1"][t]
        if t in ay.get("TP.ODEROLL.K1", {}):
            row["yayin_b"] = ay["TP.ODEROLL.K1"][t]
        if t in ay.get("TP.ODEROLL.K2", {}):
            row["yayin_c"] = ay["TP.ODEROLL.K2"][t]
        if t in ay.get("TP.BISPOLFAIZ.TUR", {}):
            row["faiz"] = ay["TP.BISPOLFAIZ.TUR"][t]
        aylar.append(row)
        m += 1
        if m == 13:
            y, m = y + 1, 1
    ix = {r["t"]: i for i, r in enumerate(aylar)}

    def pencere_oran(i, sektor, n):
        use = rep = st_in = st_out = 0.0
        for k in range(n):
            r = aylar[i - k]
            u, g, s = r.get(f"{sektor}_use"), r.get(f"{sektor}_rep"), r.get(f"{sektor}_st")
            if None in (u, g, s):
                return None
            use += u
            rep += g
            st_in += max(s, 0.0)
            st_out += max(-s, 0.0)
        if rep <= 0:
            uzun = None
        else:
            uzun = 100.0 * use / rep
        den = rep + st_out
        if den <= 0:
            bir = None
        else:
            bir = 100.0 * (use + st_in) / den
        return uzun, bir

    for i, r in enumerate(aylar):
        for n, et in ((1, "m"), (3, "3"), (12, "12")):
            if i + 1 < n:
                continue
            for sek in ("b", "c"):
                val = pencere_oran(i, sek, n)
                if val is None:
                    continue
                r[f"{sek}_uzun_{et}"] = val[0]
                r[f"{sek}_bir_{et}"] = val[1]

    # Aylık EMP, 2008-01 .. son dolu
    ham_e, ham_r = [], []
    for r in aylar:
        if r["t"] < "2008-01":
            continue
        y0, m0 = ay_ekle(r["y"], r["m"], -1)
        p = aylar[ix[anahtar(y0, m0)]]
        if "E" in r and "E" in p and "R" in r and "R" in p and p["E"] > 0 and p["R"] != 0:
            e = 100.0 * math.log(r["E"] / p["E"])
            rr = 100.0 * (r["R"] - p["R"]) / p["R"]
            r["e"] = e
            r["r"] = rr
            ham_e.append(e)
            ham_r.append(rr)
    se, sr = sd(ham_e), sd(ham_r)
    w = se / sr
    for r in aylar:
        if "e" in r:
            r["EMP"] = r["e"] - w * r["r"]

    # Çeyreklik EMP, PR #38
    def q_ortalama(y, q, alan):
        vals = []
        for mm in range((q - 1) * 3 + 1, (q - 1) * 3 + 4):
            r = aylar[ix[anahtar(y, mm)]]
            if alan not in r:
                return None
            vals.append(r[alan])
        return sum(vals) / 3.0, vals[-1]

    q_rows = []
    for y, q in ceyrekler():
        ort = q_ortalama(y, q, "E")
        sonE = q_ortalama(y, q, "E")
        sonR = None
        mm = q * 3
        if "R" in aylar[ix[anahtar(y, mm)]]:
            sonR = aylar[ix[anahtar(y, mm)]]["R"]
        if ort is None or sonR is None:
            continue
        q_rows.append({
            "q": f"{y}-Q{q}",
            "E_ort": ort[0],
            "E_sonay": ort[1],
            "R": sonR,
        })
    qix = {r["q"]: i for i, r in enumerate(q_rows)}

    def q_emp(alan, ornek_bas="2016-Q2"):
        ham = []
        for i, r in enumerate(q_rows):
            if i == 0:
                continue
            p = q_rows[i - 1]
            if r["q"] < ornek_bas:
                continue
            if p[alan] <= 0 or p["R"] == 0:
                continue
            e = 100.0 * math.log(r[alan] / p[alan])
            rr = 100.0 * (r["R"] - p["R"]) / p["R"]
            r[f"e_{alan}"] = e
            r["rq"] = rr
            ham.append((e, rr, r["q"]))
        es = [a[0] for a in ham if a[2] <= "2025-Q4"]
        rs = [a[1] for a in ham if a[2] <= "2025-Q4"]
        # ham zaten 2016-Q2'den
        sse, ssr = sd(es), sd(rs)
        ww = sse / ssr
        out = {}
        for e, rr, q in ham:
            out[q] = {"e": e, "r": rr, "EMP": e - ww * rr, "w": ww, "se": sse, "sr": ssr}
        return out

    emp_ort = q_emp("E_ort")
    emp_son = q_emp("E_sonay")
    q4 = "2021-Q4"
    # Ağırlık 0,539 dayatması, bizim e ve r
    dayat = emp_ort[q4]["e"] - 0.539 * emp_ort[q4]["r"]

    # Yayımlı örtüşme
    def medyan_fark(biz, yayin):
        fark = []
        for r in aylar:
            if r["t"] < "2008-01":
                continue
            if biz in r and r[biz] is not None and yayin in r:
                fark.append(abs(r[biz] - r[yayin]))
        fark.sort()
        if not fark:
            return None, 0
        return fark[len(fark) // 2], len(fark)

    med_b, n_b = medyan_fark("b_bir_12", "yayin_b")
    med_c, n_c = medyan_fark("c_bir_12", "yayin_c")
    med_bu, n_bu = medyan_fark("b_uzun_12", "yayin_b")
    med_cu, n_cu = medyan_fark("c_uzun_12", "yayin_c")

    # Epizot
    pencereler = {
        "2018": ["2018-07", "2018-08", "2018-09"],
        "2021": ["2021-09", "2021-10", "2021-11", "2021-12"],
        "2023": ["2023-05", "2023-06"],
    }

    def alarm(r, sektor, et):
        key = f"{sektor}_bir_{et}"
        if key not in r or r[key] is None:
            return False
        y0, m0 = ay_ekle(r["y"], r["m"], -3)
        t0 = anahtar(y0, m0)
        if t0 not in ix:
            return False
        once = aylar[ix[t0]].get(key)
        if once is None:
            return False
        return r[key] < 100.0 and r[key] <= once - 15.0

    epizot = {}
    lead_aylari = set()
    pencere_aylari = set()
    for ad, ayl in pencereler.items():
        pencere_aylari.update(ayl)
        aday = [(aylar[ix[t]]["EMP"], t) for t in ayl if "EMP" in aylar[ix[t]]]
        aday.sort(key=lambda z: (-z[0], z[1]))
        baski = aday[0][1]
        by, bm = int(baski[:4]), int(baski[5:7])
        once = []
        for k in (1, 2, 3):
            yy, mm = ay_ekle(by, bm, -k)
            once.append(anahtar(yy, mm))
        lead_aylari.update(once)
        detay = {"baski": baski, "EMP": aday[0][0], "once": once, "sektor": {}}
        tutan = False
        for sek, adsek in (("b", "banka"), ("c", "diger")):
            alarmlar = []
            for t in once:
                if alarm(aylar[ix[t]], sek, "12"):
                    alarmlar.append(t)
            detay["sektor"][adsek] = {
                "alarm_aylari": alarmlar,
                "onar": [round(aylar[ix[t]].get(f"{sek}_bir_12"), 2) if aylar[ix[t]].get(f"{sek}_bir_12") is not None else None for t in once],
                "tutar": bool(alarmlar),
            }
            tutan = tutan or bool(alarmlar)
        detay["tutar"] = tutan
        # 3 ay yan
        detay["uc_ay"] = {}
        for sek, adsek in (("b", "banka"), ("c", "diger")):
            alarmlar = [t for t in once if alarm(aylar[ix[t]], sek, "3")]
            detay["uc_ay"][adsek] = alarmlar
        epizot[ad] = detay

    yanlis = []
    for r in aylar:
        if r["t"] < "2008-01" or r["t"] > "2026-08":
            continue
        if r["t"] in pencere_aylari or r["t"] in lead_aylari:
            continue
        if alarm(r, "b", "12") or alarm(r, "c", "12"):
            yanlis.append(r["t"])
    tutan_n = sum(1 for v in epizot.values() if v["tutar"])
    isabet = None if (tutan_n + len(yanlis)) == 0 else tutan_n / (tutan_n + len(yanlis))

    # Kutu bağlamı, hedef değil
    baglam = {}
    for t in ["2018-08", "2018-09", "2021-10", "2021-11", "2021-12", "2022-11", "2023-04", "2023-05", "2023-06"]:
        r = aylar[ix[t]]
        baglam[t] = {
            "EMP": r.get("EMP"),
            "b_bir_12": r.get("b_bir_12"),
            "c_bir_12": r.get("c_bir_12"),
            "b_uzun_12": r.get("b_uzun_12"),
            "c_uzun_12": r.get("c_uzun_12"),
            "yayin_b": r.get("yayin_b"),
            "yayin_c": r.get("yayin_c"),
            "alarm_b": alarm(r, "b", "12"),
            "alarm_c": alarm(r, "c", "12"),
        }

    # panel
    alan = ["t", "E", "R", "e", "r", "EMP", "faiz",
            "b_use", "b_rep", "b_st", "c_use", "c_rep", "c_st",
            "b_uzun_12", "c_uzun_12", "b_bir_12", "c_bir_12",
            "b_uzun_3", "c_uzun_3", "b_bir_3", "c_bir_3",
            "yayin_b", "yayin_c"]
    with (KOK / "panel.csv").open("w", newline="") as f:
        wri = csv.DictWriter(f, fieldnames=alan, extrasaction="ignore")
        wri.writeheader()
        for r in aylar:
            if r["t"] >= "2008-01":
                wri.writerow({k: r.get(k) for k in alan})

    ozet = {
        "emp_aylik": {"n": len(ham_e), "se": se, "sr": sr, "agirlik": w,
                      "ilk": next(r["t"] for r in aylar if "EMP" in r and r["t"] >= "2008-01"),
                      "son": max(r["t"] for r in aylar if "EMP" in r)},
        "emp_ceyrek": {
            "2021Q4": emp_ort[q4],
            "sonay_2021Q4": emp_son[q4],
            "agirlik_054_dayatma_2021Q4": dayat,
        },
        "ortusme_medyan_puan": {
            "banka_birlesik": med_b, "banka_n": n_b,
            "diger_birlesik": med_c, "diger_n": n_c,
            "banka_uzun": med_bu, "diger_uzun": med_cu,
        },
        "epizot": epizot,
        "tutan_epizot": tutan_n,
        "yanlis_alarm": yanlis,
        "yanlis_alarm_sayisi": len(yanlis),
        "isabet": isabet,
        "baglam": baglam,
        "fred": "DOGRULANMADI",
        "kontrollu_granger": "DOGRULANMADI",
    }
    (KOK / "sonuclar.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=2))
    print(json.dumps({k: ozet[k] for k in ("emp_aylik", "emp_ceyrek", "ortusme_medyan_puan", "tutan_epizot", "yanlis_alarm_sayisi", "isabet")}, ensure_ascii=False, indent=2))
    print("EPIZOT")
    print(json.dumps(epizot, ensure_ascii=False, indent=2))
    print("BAGLAM")
    print(json.dumps(baglam, ensure_ascii=False, indent=2))
    print("YANLIS", len(yanlis), yanlis[:12], "...", yanlis[-5:])


if __name__ == "__main__":
    main()
