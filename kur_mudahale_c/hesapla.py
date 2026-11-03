"""Kur müdahalesinin rezerv maliyeti c. Ön kayıt: ON_KAYIT.md.

EVDS dışı uç nokta (igmevdsms-dis). Anahtar yok. İç uç nokta yok. Sertifika doğrulaması açık.
"""
from __future__ import annotations

import csv
import json
import math
import urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
from pypdf import PdfReader

KOK = Path(__file__).resolve().parent
HAM = KOK / "ham"
HAM.mkdir(exist_ok=True)
BASE = "https://evds3.tcmb.gov.tr/igmevdsms-dis"
AY = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12,
}
EPIZOT = [
    ("E1", "2018-Q3", "2018-Q4"),
    ("E2", "2019-Q1", "2020-Q4"),
    ("E3", "2021-Q4", "2021-Q4"),
    ("E4", "2023-Q1", "2023-Q2"),
    ("E5", "2023-Q3", "2023-Q4"),
    ("E6", "2025-Q1", "2025-Q1"),
]


def evds(seriler: list[str], bas: str, bit: str, frekans: str, agg: str) -> list[dict]:
    n = len(seriler)
    govde = {
        "type": "json",
        "series": "-".join(seriler),
        "aggregationTypes": "-".join([agg] * n),
        "formulas": "-".join(["0"] * n),
        "startDate": bas,
        "endDate": bit,
        "frequency": frekans,
        "decimalSeperator": ".",
        "decimal": "6",
        "dateFormat": "0",
        "lang": "TR",
        "yon": "0",
        "sira": "0",
        "ozelFormuller": [],
        "groupSeperator": False,
        "isRaporSayfasi": False,
    }
    istek = urllib.request.Request(
        f"{BASE}/fe",
        data=json.dumps(govde).encode(),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "kur-mudahale-c",
            "Referer": "https://evds3.tcmb.gov.tr/",
        },
        method="POST",
    )
    with urllib.request.urlopen(istek, timeout=180) as r:
        veri = json.loads(r.read().decode("utf-8-sig"))
    return veri["items"]


def sayi(v):
    if v in (None, ""):
        return None
    try:
        return float(str(v).replace(",", ""))
    except ValueError:
        return None


def ay_anahtar(tarih: str) -> str | None:
    s = (tarih or "").strip()
    for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%Y-%m", "%m-%Y"):
        try:
            d = datetime.strptime(s, fmt)
            return f"{d.year:04d}-{d.month:02d}"
        except ValueError:
            pass
    parca = s.split("-")
    if len(parca) == 2 and parca[0].isdigit() and len(parca[0]) == 4:
        return f"{int(parca[0]):04d}-{int(parca[1]):02d}"
    if len(parca) == 2 and parca[1].isdigit() and len(parca[1]) == 4:
        return f"{int(parca[1]):04d}-{int(parca[0]):02d}"
    return None


def ceyrek(ay: str) -> str:
    y, m = ay.split("-")
    return f"{y}-Q{(int(m) - 1) // 3 + 1}"


def qi(d: str) -> int:
    y, q = d.split("-Q")
    return int(y) * 4 + int(q) - 1


def qd(i: int) -> str:
    return f"{i // 4}-Q{i % 4 + 1}"


def pencere_icinde(d: str, a: str, b: str) -> bool:
    return qi(a) <= qi(d) <= qi(b)


def epizot_mu(d: str) -> str | None:
    for kod, a, b in EPIZOT:
        if pencere_icinde(d, a, b):
            return kod
    return None


def pdf_satis() -> dict[str, dict]:
    """TCMB aylık alım-satım PDF. Sütun x konumundan okunur. Milyon ABD doları."""
    yol = HAM / "aylik_en.pdf"
    if not yol.exists():
        raise SystemExit("aylik PDF yok")
    reader = PdfReader(str(yol))
    hucre: dict[tuple[str, str], float] = {}
    for page in reader.pages:
        satir = defaultdict(list)

        def visitor(text, cm, tm, fontDict, fontSize):
            if text and text.strip():
                satir[round(tm[5], 0)].append((tm[4], text.strip()))

        page.extract_text(visitor_text=visitor)
        for _, hucreler in satir.items():
            hucreler.sort()
            tarih = None
            for x, t in hucreler:
                if any(t.startswith(a) for a in AY):
                    tarih = t
                    continue
                if tarih is None:
                    continue
                try:
                    v = float(t.replace(",", ""))
                except ValueError:
                    continue
                if 240 <= x < 450:
                    sutun = "reeskont_alim"
                elif 740 <= x < 870:
                    sutun = "kit_satim"
                elif 870 <= x < 1100:
                    sutun = "dogrudan_mudahale_satim"
                elif 140 <= x < 240:
                    sutun = "alim_ihale"
                elif 620 <= x < 740:
                    sutun = "satim_ihale"
                else:
                    continue
                ad, yy = tarih.split("-")
                ay = f"{2000 + int(yy):04d}-{AY[ad]:02d}"
                hucre[(ay, sutun)] = v
    aylar = sorted({a for a, _ in hucre})
    out = {}
    for ay in aylar:
        # Ay PDF'te varsa boş sütun yayımlanmış sıfırdır; müdahale yalnız satış olduğu ayda basılır.
        def h(sutun, bos_sifir=True):
            if (ay, sutun) in hucre:
                return hucre[(ay, sutun)]
            return 0.0 if bos_sifir else None

        out[ay] = {
            "reeskont_alim_mn": h("reeskont_alim"),
            "kit_satim_mn": h("kit_satim"),
            "dogrudan_mudahale_satim_mn": h("dogrudan_mudahale_satim"),
            "alim_ihale_mn": h("alim_ihale"),
            "satim_ihale_mn": h("satim_ihale"),
        }
    return out


def indir_evds() -> dict[str, dict[str, float]]:
    onbellek = HAM / "evds_aylik.json"
    if onbellek.exists():
        return json.loads(onbellek.read_text(encoding="utf-8"))
    istekler = [
        (["TP.DK.USD.S.YTL", "TP.DK.USD.A.YTL", "TP.MK.LON.YTL", "TP.BISPOLFAIZ.TUR", "TP.APIFON4"], "avg"),
        (["TP.AB.B1", "TP.AB.B2", "TP.AB.B4", "TP.AB.B6"], "last"),
        ([
            "TP.REZVARPD.K1", "TP.REZVARPD.K2", "TP.REZVARPD.K10", "TP.REZVARPD.K11",
            "TP.DOVVARNC.K1", "TP.DOVVARNC.K2", "TP.DOVVARNC.K14", "TP.DOVVARNC.K15",
            "TP.DOVVARNC.K19", "TP.DOVVARNC.K23",
        ], "last"),
        (["TP.ODANA6.Q01", "TP.ODANA6.Q16", "TP.ODANA6.Q17", "TP.ODANA6.Q33", "TP.ODANA6.Q34"], "sum"),
        (["TP.KKM.K1", "TP.KKM.K4", "TP.RKDRK01"], "last"),
        (["TP.KM.G01", "TP.KM.G49", "TP.KM.G57"], "last"),
    ]
    ham: dict[str, dict[str, float]] = defaultdict(dict)
    for seriler, agg in istekler:
        for s in seriler:
            try:
                items = evds([s], "01-01-2016", "31-12-2025", "5", agg)
            except Exception as exc:  # noqa: BLE001
                print("HATA", s, type(exc).__name__, exc)
                continue
            n = 0
            for it in items:
                ay = ay_anahtar(str(it.get("Tarih", "")))
                if not ay:
                    continue
                v = sayi(it.get(s.replace(".", "_")))
                if v is not None:
                    ham[ay][s] = v
                    n += 1
            print("indi", s, agg, "gozlem", n, "tarih", items[0].get("Tarih") if items else None)
    onbellek.write_text(json.dumps(ham, ensure_ascii=False), encoding="utf-8")
    return ham


def ols_nw(y: np.ndarray, X: np.ndarray, gecikme: int = 4):
    n, k = X.shape
    xtx = X.T @ X
    xtx_inv = np.linalg.inv(xtx)
    b = xtx_inv @ X.T @ y
    e = y - X @ b
    S = np.zeros((k, k))
    for t in range(n):
        xt = X[t][:, None]
        S += float(e[t] ** 2) * (xt @ xt.T)
    for L in range(1, gecikme + 1):
        w = 1 - L / (gecikme + 1)
        G = np.zeros((k, k))
        for t in range(L, n):
            xt = X[t][:, None]
            xl = X[t - L][:, None]
            G += float(e[t] * e[t - L]) * (xt @ xl.T)
        S += w * (G + G.T)
    V = xtx_inv @ S @ xtx_inv
    sst = float(((y - y.mean()) ** 2).sum())
    r2 = 1 - float(e @ e) / sst if sst else None
    return b, V, r2, e


def aralik(b, se):
    if se is None or not math.isfinite(se) or se < 0:
        return None
    return (b - 1.96 * se, b + 1.96 * se)


def sifir_disi(ar) -> bool:
    if ar is None:
        return False
    return ar[0] > 0 or ar[1] < 0


def c_nokta(theta):
    if theta is None or not math.isfinite(theta) or theta >= 0:
        return None
    return -1.0 / theta


def c_se(theta, se_theta):
    if theta is None or se_theta is None or theta >= 0 or not math.isfinite(se_theta):
        return None
    return se_theta / (theta ** 2)


def panel_kur(evds_ay, satis):
    aylar = sorted(set(evds_ay) | set(satis))
    aylik = []
    for ay in aylar:
        e = evds_ay.get(ay, {})
        s = satis.get(ay, {})
        row = {"ay": ay, "ceyrek": ceyrek(ay)}
        row["usd_satis"] = e.get("TP.DK.USD.S.YTL")
        row["usd_alis"] = e.get("TP.DK.USD.A.YTL")
        row["ons_fiyat"] = e.get("TP.MK.LON.YTL")
        row["faiz"] = e.get("TP.BISPOLFAIZ.TUR")
        row["aofm"] = e.get("TP.APIFON4")
        row["brut_mn"] = e.get("TP.REZVARPD.K1")
        row["altin_mn"] = e.get("TP.REZVARPD.K10")
        row["ons_mn"] = e.get("TP.REZVARPD.K11")
        row["swap_net_mn"] = e.get("TP.DOVVARNC.K14")
        row["swap_acik_mn"] = e.get("TP.DOVVARNC.K15")
        row["swap_fazla_mn"] = e.get("TP.DOVVARNC.K19")
        row["diger_mn"] = e.get("TP.DOVVARNC.K23")
        row["drain21_mn"] = e.get("TP.DOVVARNC.K1")
        row["ca_mn"] = e.get("TP.ODANA6.Q01")
        row["portfoy_varlik_mn"] = e.get("TP.ODANA6.Q16")
        row["portfoy_yukumluluk_mn"] = e.get("TP.ODANA6.Q17")
        row["rezerv_akis_mn"] = e.get("TP.ODANA6.Q33")
        row["kkm_usd_bn"] = e.get("TP.KKM.K1")
        row["kkm_tl_bn"] = e.get("TP.KKM.K4")
        row["reeskont_stok_mn"] = e.get("TP.RKDRK01")
        row["mev_tl"] = e.get("TP.KM.G01")
        row["mev_yp"] = e.get("TP.KM.G49")
        row["mev_top"] = e.get("TP.KM.G57")
        for k, v in s.items():
            row[k] = v
        if row["brut_mn"] is not None and row["swap_net_mn"] is not None and row["diger_mn"] is not None:
            row["r_swap_haric_mn"] = row["brut_mn"] + row["swap_net_mn"] + row["diger_mn"]
        else:
            row["r_swap_haric_mn"] = None
        if row["mev_yp"] is not None and row["mev_top"] not in (None, 0):
            row["dolarizasyon"] = row["mev_yp"] / row["mev_top"]
        else:
            row["dolarizasyon"] = None
        aylik.append(row)

    # aylık altın değerlemesi
    onceki_ons = None
    onceki_fiyat = None
    for row in aylik:
        if onceki_ons is not None and onceki_fiyat is not None and row["ons_fiyat"] is not None:
            row["degerleme_mn"] = onceki_ons * (row["ons_fiyat"] - onceki_fiyat)
        else:
            row["degerleme_mn"] = None
        if row["ons_mn"] is not None:
            onceki_ons = row["ons_mn"]
        if row["ons_fiyat"] is not None:
            onceki_fiyat = row["ons_fiyat"]

    grup = defaultdict(list)
    for row in aylik:
        grup[row["ceyrek"]].append(row)

    ceyrekler = []
    onceki_r = None
    onceki_cq = None
    for cq in sorted(grup):
        rs = grup[cq]

        def n_dolu(alan):
            return sum(1 for r in rs if r.get(alan) is not None)

        def ort(alan, tam=True):
            vs = [r[alan] for r in rs if r.get(alan) is not None]
            if tam and len(vs) != 3:
                return None
            return sum(vs) / len(vs) if vs else None

        def son(alan):
            vs = [r for r in rs if r.get(alan) is not None]
            return vs[-1][alan] if vs else None

        def toplam(alan):
            vs = [r[alan] for r in rs if r.get(alan) is not None]
            if len(vs) != 3:
                return None
            return sum(vs)

        def toplam_var(alan):
            vs = [r[alan] for r in rs if r.get(alan) is not None]
            return sum(vs) if vs else None

        r_son = son("r_swap_haric_mn")
        degerleme = toplam("degerleme_mn")
        ca = toplam("ca_mn")
        ardisik = onceki_cq is not None and qi(cq) == qi(onceki_cq) + 1
        delta_r = (r_son - onceki_r) if (r_son is not None and onceki_r is not None and ardisik) else None
        # milyar
        def mlr(x):
            return None if x is None else x / 1000.0

        dlt = mlr(delta_r)
        deg = mlr(degerleme)
        ca_b = mlr(ca)
        s_literal = None
        s_vekil = None
        if dlt is not None and deg is not None and ca_b is not None:
            s_literal = max(0.0, -dlt - deg + min(ca_b, 0.0))
            s_vekil = max(0.0, -dlt + deg + min(ca_b, 0.0))
        kit = toplam("kit_satim_mn")
        mud = toplam("dogrudan_mudahale_satim_mn")
        ihale = toplam("satim_ihale_mn")
        # yayımlanmış doğrudan satış: üç sütun da o çeyrekte okunduysa
        if kit is not None and mud is not None and ihale is not None:
            s_tcmb = (kit + mud + ihale) / 1000.0
        elif kit is not None or mud is not None:
            parcalar = [x for x in (kit, mud, ihale) if x is not None]
            s_tcmb = sum(parcalar) / 1000.0
        else:
            s_tcmb = None
        rec = {
            "ceyrek": cq,
            "n_ay": len(rs),
            "E": ort("usd_satis"),
            "faiz": ort("faiz"),
            "aofm": ort("aofm"),
            "ca_bn": ca_b,
            "ca_tam": ca is not None and len([r for r in rs if r.get("ca_mn") is not None]) == 3,
            "portfoy_bn": mlr(toplam("portfoy_yukumluluk_mn")),
            "portfoy_varlik_bn": mlr(toplam("portfoy_varlik_mn")),
            "dolarizasyon": ort("dolarizasyon"),
            "r_bn": mlr(r_son),
            "brut_bn": mlr(son("brut_mn")),
            "altin_bn": mlr(son("altin_mn")),
            "ons_mn": son("ons_mn"),
            "swap_net_bn": mlr(son("swap_net_mn")),
            "delta_r_bn": dlt,
            "degerleme_bn": deg,
            "s_vekil": s_vekil,
            "s_literal": s_literal,
            "s_tcmb": s_tcmb,
            "kit_bn": None if kit is None else kit / 1000.0,
            "mudahale_bn": None if mud is None else mud / 1000.0,
            "reeskont_akis_bn": mlr(toplam_var("reeskont_alim_mn")),
            "kkm_usd_bn": son("kkm_usd_bn"),
            "reeskont_stok_bn": mlr(son("reeskont_stok_mn")),
            "epizot": epizot_mu(cq),
        }
        ceyrekler.append(rec)
        if r_son is not None:
            onceki_r = r_son
            onceki_cq = cq
    # g
    for i, rec in enumerate(ceyrekler):
        oncek = ceyrekler[i - 1] if i else None
        if oncek and rec["E"] and oncek["E"] and qi(rec["ceyrek"]) == qi(oncek["ceyrek"]) + 1:
            rec["g"] = 100.0 * math.log(rec["E"] / oncek["E"])
        else:
            rec["g"] = None
    return aylik, ceyrekler


def tasarim(rows, s_alan, ekstra=None):
    """2018-Q1–2025-Q4, gecikmeli kontroller. CDS yok."""
    by = {r["ceyrek"]: r for r in rows}
    xs, ys, ds = [], [], []
    for r in rows:
        if r["ceyrek"] < "2018-Q1" or r["ceyrek"] > "2025-Q4":
            continue
        once = qd(qi(r["ceyrek"]) - 1)
        p = by.get(once)
        if p is None or r["g"] is None or r.get(s_alan) is None:
            continue
        kontroller = [p.get("faiz"), p.get("ca_bn"), p.get("portfoy_bn"), p.get("dolarizasyon"), p.get("g")]
        if any(v is None for v in kontroller):
            continue
        x = [1.0, r[s_alan], *kontroller]
        if ekstra:
            for alan in ekstra:
                if r.get(alan) is None and alan != "etkilesim":
                    x = None
                    break
            if x is None:
                continue
            if "birikim" in (ekstra or []):
                x.append(p.get("birikim") if p.get("birikim") is not None else None)
                if x[-1] is None:
                    continue
            if "etkilesim" in (ekstra or []):
                if p.get("r_bn") is None:
                    continue
                x.append(r[s_alan] * p["r_bn"])
        xs.append(x)
        ys.append(r["g"])
        ds.append(r["ceyrek"])
    if not xs:
        return None
    return np.array(ys, float), np.array(xs, float), ds


def coz(y, X, adlar):
    b, V, r2, e = ols_nw(y, X, 4)
    se = np.sqrt(np.clip(np.diag(V), 0, None))
    # negatif varyans
    ham_se = []
    for i in range(len(b)):
        v = V[i, i]
        ham_se.append(math.sqrt(v) if v >= 0 and math.isfinite(v) else None)
    kats = {}
    for i, ad in enumerate(adlar):
        kats[ad] = {
            "b": float(b[i]),
            "se": None if ham_se[i] is None else float(ham_se[i]),
            "aralik": None if ham_se[i] is None else [float(b[i] - 1.96 * ham_se[i]), float(b[i] + 1.96 * ham_se[i])],
        }
    return {"n": int(len(y)), "r2": None if r2 is None else float(r2), "katsayi": kats, "b": b, "V": V, "e": e}


def epizot_olcu(rows, s_alan):
    by = {r["ceyrek"]: r for r in rows}
    dis = []
    for r in rows:
        if r["ceyrek"] < "2018-Q1" or r["ceyrek"] > "2025-Q4":
            continue
        if r["epizot"]:
            continue
        once = qd(qi(r["ceyrek"]) - 1)
        p = by.get(once)
        if p is None or r["g"] is None:
            continue
        kontroller = [p.get("faiz"), p.get("ca_bn"), p.get("portfoy_bn"), p.get("g")]
        if any(v is None for v in kontroller):
            continue
        dis.append((r, kontroller))
    if len(dis) < 6:
        return {"hata": "epizot dışı örnek yetersiz", "n": len(dis)}
    y = np.array([r["g"] for r, _ in dis], float)
    X = np.array([[1.0, *k] for _, k in dis], float)
    b, V, r2, e = ols_nw(y, X, 4)
    P = {}
    for r in rows:
        if r["ceyrek"] < "2018-Q1" or r["ceyrek"] > "2025-Q4" or r["g"] is None:
            continue
        once = qd(qi(r["ceyrek"]) - 1)
        p = by.get(once)
        if p is None:
            continue
        k = [p.get("faiz"), p.get("ca_bn"), p.get("portfoy_bn"), p.get("g")]
        if any(v is None for v in k):
            continue
        P[r["ceyrek"]] = float(np.array([1.0, *k]) @ b)
    # bastırma
    for r in rows:
        pt = P.get(r["ceyrek"])
        s = r.get(s_alan)
        if pt is None or r["g"] is None or s is None:
            r["P"] = pt
            r["bast"] = None
            r["fazla"] = None
            continue
        r["P"] = pt
        r["fazla"] = max(0.0, r["g"] - pt)
        if s > 0:
            r["bast"] = max(0.0, pt - r["g"])
        else:
            r["bast"] = 0.0
    sonuclar = []
    for kod, a, b0 in EPIZOT:
        pencere = [r for r in rows if r["ceyrek"] >= "2018-Q1" and pencere_icinde(r["ceyrek"], a, b0)]
        if any(r.get("bast") is None or r.get(s_alan) is None for r in pencere):
            sonuclar.append({"kod": kod, "pencere": f"{a}–{b0}", "c": None, "not": "eksik çeyrek"})
            continue
        s_top = sum(r[s_alan] for r in pencere)
        bast_top = sum(r["bast"] for r in pencere if r[s_alan] > 0)
        # bast zaten S>0 ise dolu, S<=0 ise 0. Payda tanımı: S>0 çeyreklerin bast toplamı
        c = None
        notu = "bastırmadı"
        if bast_top > 0 and s_top > 0:
            c = s_top / bast_top
            notu = "bastırma var"
        elif s_top <= 0:
            notu = "pencerede satış yok"
        # leave one quarter out
        loo = []
        if len(pencere) >= 2 and c is not None:
            for i in range(len(pencere)):
                alt = pencere[:i] + pencere[i + 1 :]
                st = sum(x[s_alan] for x in alt)
                bt = sum(x["bast"] for x in alt if x[s_alan] > 0)
                if bt > 0 and st > 0:
                    loo.append(st / bt)
        # erteleme
        bit = qi(b0)
        sonraki = []
        eksik = False
        for k in range(1, 5):
            d = qd(bit + k)
            if d > "2025-Q4":
                eksik = True
                break
            rr = by.get(d)
            if rr is None or rr.get("fazla") is None:
                eksik = True
                break
            sonraki.append(rr["fazla"])
        if eksik:
            erteleme = None
            fazla_top = None
        else:
            fazla_top = sum(sonraki)
            if bast_top <= 0:
                erteleme = None
            else:
                oran = fazla_top / bast_top
                if oran >= 0.70:
                    erteleme = "erteledi"
                elif oran < 0.30:
                    erteleme = "baskıyı o pencerede karşı-olgudan daha fazla geri getirmedi"
                else:
                    erteleme = "kısmi"
        sonuclar.append({
            "kod": kod,
            "pencere": f"{a}–{b0}",
            "s_bn": s_top,
            "bastirilan_puan": bast_top,
            "c": c,
            "not": notu,
            "loo_min": min(loo) if loo else None,
            "loo_max": max(loo) if loo else None,
            "loo_n": len(loo),
            "fazla_4c": fazla_top,
            "erteleme": erteleme,
            "ceyrekler": [
                {"t": r["ceyrek"], "g": r["g"], "P": r["P"], "S": r[s_alan], "bast": r["bast"]}
                for r in pencere
            ],
        })
    return {
        "n_dis": len(dis),
        "r2_dis": float(r2),
        "b": [float(x) for x in b],
        "epizot": sonuclar,
        "P": P,
    }


def birikim_fifo(rows):
    from collections import deque
    kuyruk = deque()
    for r in rows:
        if r["ceyrek"] < "2018-Q1" or r["ceyrek"] > "2025-Q4":
            r["birikim"] = None
            continue
        fazla = r.get("fazla") or 0.0
        kalan = fazla
        while kuyruk and kalan > 0:
            if kuyruk[0] <= kalan:
                kalan -= kuyruk[0]
                kuyruk.popleft()
            else:
                kuyruk[0] -= kalan
                kalan = 0.0
        bast = r.get("bast") or 0.0
        if bast > 0:
            kuyruk.append(bast)
        r["birikim"] = sum(kuyruk)


def satis_agirlikli(epizotlar):
    pay = 0.0
    payda = 0.0
    for e in epizotlar:
        if e.get("c") is None or not e.get("s_bn") or e["s_bn"] <= 0:
            continue
        pay += e["c"] * e["s_bn"]
        payda += e["s_bn"]
    if payda <= 0:
        return None
    return pay / payda


def birinci_asama_F(rows, s_alan):
    by = {r["ceyrek"]: r for r in rows}
    ys, xs = [], []
    for r in rows:
        if r["ceyrek"] < "2018-Q1" or r["ceyrek"] > "2025-Q4":
            continue
        once = qd(qi(r["ceyrek"]) - 1)
        p = by.get(once)
        if p is None or r.get(s_alan) is None:
            continue
        k = [p.get("faiz"), p.get("ca_bn"), p.get("portfoy_bn"), p.get("dolarizasyon"), p.get("g")]
        if any(v is None for v in k):
            continue
        z = 1.0 if r["epizot"] else 0.0
        xs.append([1.0, z, *k])
        ys.append(r[s_alan])
    if len(ys) < 10:
        return {"n": len(ys), "F": None}
    y = np.array(ys, float)
    X = np.array(xs, float)
    b, V, r2, e = ols_nw(y, X, 4)
    se = math.sqrt(V[1, 1]) if V[1, 1] > 0 else None
    if se is None or se == 0:
        return {"n": len(y), "F": None, "bz": float(b[1])}
    t = float(b[1] / se)
    return {"n": int(len(y)), "bz": float(b[1]), "se": float(se), "F": t * t, "r2": float(r2)}


def json_temiz(o):
    if isinstance(o, dict):
        return {k: json_temiz(v) for k, v in o.items() if not isinstance(v, np.ndarray)}
    if isinstance(o, list):
        return [json_temiz(v) for v in o]
    if isinstance(o, float):
        if not math.isfinite(o):
            return None
        return o
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    return o


def f4(x):
    if x is None:
        return "—"
    return f"{x:.4f}".replace(".", ",")


def f2(x):
    if x is None:
        return "—"
    return f"{x:.2f}".replace(".", ",")


def f1(x):
    if x is None:
        return "—"
    return f"{x:.1f}".replace(".", ",")


def main():
    satis = pdf_satis()
    (HAM / "tcmb_satis_aylik.json").write_text(json.dumps(satis, ensure_ascii=False, indent=2), encoding="utf-8")
    ev = indir_evds()
    aylik, rows = panel_kur(ev, satis)
    # altın kimlik kontrolü
    oranlar = []
    for r in aylik:
        if r.get("altin_mn") and r.get("ons_mn") and r.get("ons_fiyat"):
            carpan = r["ons_mn"] * r["ons_fiyat"]
            if carpan:
                oranlar.append(r["altin_mn"] / carpan)
    s_alan = "s_vekil"
    epi = epizot_olcu(rows, s_alan)
    birikim_fifo(rows)
    # ana regresyon
    adlar = ["sabit", "S", "faiz_gecikme", "ca_gecikme", "portfoy_gecikme", "dolarizasyon_gecikme", "g_gecikme"]
    tas = tasarim(rows, s_alan)
    ana = None
    if tas:
        y, X, ds = tas
        ana = coz(y, X, adlar)
        ana["donem"] = ds
        th = ana["katsayi"]["S"]
        theta, se = th["b"], th["se"]
        ana["theta"] = theta
        ana["se_theta"] = se
        ana["theta_aralik"] = th["aralik"]
        ana["theta_sifir_disi"] = sifir_disi(tuple(th["aralik"]) if th["aralik"] else None) if th["aralik"] else False
        cp = c_nokta(theta)
        ana["c_nokta"] = cp
        if ana["theta_sifir_disi"] and theta < 0 and se is not None:
            sc = c_se(theta, se)
            ana["c_se"] = sc
            ana["c_aralik"] = [cp - 1.96 * sc, cp + 1.96 * sc] if sc is not None else None
        else:
            ana["c_se"] = None
            ana["c_aralik"] = None
    # yayımlanmış TCMB satışı duyarlılık
    tas2 = tasarim(rows, "s_tcmb")
    duy = None
    if tas2:
        y2, X2, ds2 = tas2
        duy = coz(y2, X2, adlar)
        th = duy["katsayi"]["S"]
        duy["donem"] = ds2
        duy["c_nokta"] = c_nokta(th["b"])
        duy["theta_sifir_disi"] = bool(th["aralik"] and sifir_disi(tuple(th["aralik"])))
        if duy["theta_sifir_disi"] and th["b"] < 0 and th["se"]:
            sc = c_se(th["b"], th["se"])
            duy["c_aralik"] = [duy["c_nokta"] - 1.96 * sc, duy["c_nokta"] + 1.96 * sc]
        else:
            duy["c_aralik"] = None
    # birikme
    adlar_b = adlar + ["birikim_gecikme"]
    tasb = tasarim(rows, s_alan, ekstra=["birikim"])
    bir = None
    if tasb:
        yb, Xb, dsb = tasb
        bir = coz(yb, Xb, adlar_b)
        bir["donem"] = dsb
    # doğrusal olmayan: R medyan > 0
    ornek_r = []
    by = {r["ceyrek"]: r for r in rows}
    for r in rows:
        if "2018-Q1" <= r["ceyrek"] <= "2025-Q4":
            p = by.get(qd(qi(r["ceyrek"]) - 1))
            if p and p.get("r_bn") is not None and r.get(s_alan) is not None:
                ornek_r.append(p["r_bn"])
    r_medyan = float(np.median(ornek_r)) if ornek_r else None
    nonlin = None
    if r_medyan is not None and r_medyan > 0:
        # etkileşim S * (R / medyan). tasarim ham R ekliyor; ölçekle
        tasn = tasarim(rows, s_alan, ekstra=["etkilesim"])
        if tasn:
            yn, Xn, dsn = tasn
            Xn = Xn.copy()
            Xn[:, -1] = Xn[:, -1] / r_medyan
            nonlin = coz(yn, Xn, adlar + ["S_carpi_R_bolu_medyan"])
            nonlin["donem"] = dsn
            nonlin["r_medyan"] = r_medyan
    else:
        nonlin = {"kosulmadi": True, "r_medyan": r_medyan, "n_r": len(ornek_r)}
    iv = birinci_asama_F(rows, s_alan)
    # birincil seçim
    epizotlar = epi.get("epizot") or []
    c_epi = satis_agirlikli(epizotlar)
    birincil = {"kaynak": None, "c": None, "aralik": None, "kararsiz": False, "etiket": "VEKİL"}
    if ana and ana.get("c_aralik") and ana["theta"] < 0:
        birincil.update(kaynak="ols", c=ana["c_nokta"], aralik=ana["c_aralik"])
    elif c_epi is not None:
        birincil.update(kaynak="epizot_agirlikli", c=c_epi, aralik=None, not_="OLS ayırt edilemedi")
    else:
        birincil.update(kaynak="yok", c=None, etiket="DOĞRULANMADI")
    if ana and ana.get("c_nokta") and c_epi:
        oran = max(ana["c_nokta"], c_epi) / min(ana["c_nokta"], c_epi)
        if oran > 2:
            birincil["kararsiz"] = True
            birincil["ayrim_kat"] = oran
    # ızgara
    ar = birincil.get("aralik")
    if birincil["c"] is None or ar is None:
        izgara = "BELİRSİZ"
        yanlis_10 = False
        yanlis_30 = False
    else:
        lo, hi = ar
        yanlis_10 = lo > 10
        yanlis_30 = hi < 30
        if lo <= 10 <= hi and lo <= 30 <= hi:
            izgara = "BELİRSİZ"
        elif yanlis_10 and yanlis_30:
            izgara = "c≤10 yanlışlandı ve c≥30 yanlışlandı"
        elif yanlis_10:
            izgara = "c≤10 yanlışlandı"
        elif yanlis_30:
            izgara = "c≥30 yanlışlandı"
        else:
            izgara = "ne c≤10 ne c≥30 yanlışlandı"
    # model
    model = list(Path("/workspace").rglob("model_rr.py"))
    model_satir = "DOĞRULANMADI" if not model else str(model)
    # panel csv
    alanlar = [
        "ceyrek", "n_ay", "E", "g", "faiz", "ca_bn", "portfoy_bn", "dolarizasyon",
        "r_bn", "brut_bn", "delta_r_bn", "degerleme_bn", "s_vekil", "s_literal",
        "s_tcmb", "kit_bn", "mudahale_bn", "reeskont_akis_bn", "kkm_usd_bn",
        "P", "bast", "fazla", "birikim", "epizot",
    ]
    with (KOK / "ceyrek_panel.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=alanlar, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            if r["ceyrek"] < "2017-Q1" or r["ceyrek"] > "2025-Q4":
                continue
            w.writerow({k: r.get(k) for k in alanlar})
    # cari yıllık kontrol
    ca_yil = defaultdict(float)
    ca_n = defaultdict(int)
    for r in rows:
        if r.get("ca_bn") is not None:
            ca_yil[r["ceyrek"][:4]] += r["ca_bn"]
            ca_n[r["ceyrek"][:4]] += 1
    sonuc = {
        "altin_oran_min": min(oranlar) if oranlar else None,
        "altin_oran_max": max(oranlar) if oranlar else None,
        "altin_oran_n": len(oranlar),
        "ca_yil": {y: ca_yil[y] for y in sorted(ca_yil) if y >= "2018"},
        "ca_yil_n": {y: ca_n[y] for y in sorted(ca_n) if y >= "2018"},
        "ana": json_temiz(ana) if ana else None,
        "ana_donem": ana["donem"] if ana else None,
        "duyarlilik_tcmb": json_temiz(duy) if duy else None,
        "epizot": json_temiz(epi),
        "birikim_reg": json_temiz(bir) if bir else None,
        "nonlin": json_temiz(nonlin) if nonlin else None,
        "iv": iv,
        "c_epizot_agirlikli": c_epi,
        "birincil": birincil,
        "izgara": izgara,
        "yanlis_10": yanlis_10 if birincil["c"] is not None else False,
        "yanlis_30": yanlis_30 if birincil["c"] is not None else False,
        "model_rr": model_satir,
        "r_medyan": r_medyan,
        "son_ceyrek_evds": max((r["ceyrek"] for r in rows if r.get("E")), default=None),
        "s_vekil_2025q4": by.get("2025-Q4", {}).get("s_vekil"),
        "tam_2025q4": by.get("2025-Q4", {}).get("n_ay"),
    }
    (KOK / "sonuclar.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8")
    yaz_rapor(sonuc, rows)
    print(json.dumps({k: sonuc[k] for k in ("birincil", "izgara", "iv", "c_epizot_agirlikli", "model_rr", "altin_oran_min", "altin_oran_max")}, ensure_ascii=False, indent=2))


def yaz_rapor(s, rows):
    # rapor ana() sonunda dolar; sayılar JSON'dan
    p = []
    a = lambda t: p.append(t)
    b = s["birincil"]
    a("# Kur müdahalesinin rezerv maliyeti")
    a("")
    a("Ön kayıt `ON_KAYIT.md` içinde 2026-10-20T09:12:13Z kilitlendi. Katsayılar ondan sonra hesaplandı. Eşikler kaydırılmadı. Ayrılan yerler o dosyada SAPMA diye durur.")
    a("")
    a("## Hüküm")
    a("")
    if b["c"] is None:
        a("Birincil c [DOĞRULANMADI]. Sıfır yazılmadı. Üç kural modeli koşulmadı.")
    else:
        kaynak = "tam örnek OLS" if b["kaynak"] == "ols" else "bastırma görülen epizotların satış ağırlıklı ortalaması"
        ar = b.get("aralik")
        ar_yazi = "sınırlı değil" if not ar else f"[{f2(ar[0])}, {f2(ar[1])}]"
        kar = " Kararsız: epizot c’si ile regresyon noktası 2 kattan fazla ayrılıyor." if b.get("kararsiz") else ""
        a(f"Birincil c = {f2(b['c'])} milyar dolar / puan [{b['etiket']}], kaynak: {kaynak}. Bu sayı yalnız 2019-Q1–2020-Q4 penceresinden gelir. %95 aralık: {ar_yazi}.{kar} Aralık olmadığı için “c ≤ 10” ve “c ≥ 30” yanlışlanamaz.")
    a("")
    a(f"Izgara hükmü: {s['izgara']}. “c ≤ 10” yanlışlandı: {'evet' if s.get('yanlis_10') else 'hayır'}. “c ≥ 30” yanlışlandı: {'evet' if s.get('yanlis_30') else 'hayır'}. Aralık hem 10’u hem 30’u örtüyorsa veya aralık yoksa ön kayıt BELİRSİZ der.")
    a("")
    a(f"`model_rr.py` çalışma ağacında yok ({s['model_rr']}). b = 1,26 ve b = 0,42 için üç kural koşusu yapılmadı. Hüküm, rezervin bittiği çeyrek ve TÜFE yolu her iki b için de [DOĞRULANMADI]. 2029-Q3 ve 2031 tarihleri bu dosyada üretilmedi.")
    a("")
    a("Bu c, koşullu beraberliktir. Satış baskı yükselince arttığı için OLS, θ’yı sıfıra veya pozitife iter ve c’yi büyük gösterebilir. Karşı-olgusuz nedensellik cümlesi yok. Epizot P’si “epizot dışı beraberlikten sapma”dır [HESAP]; “müdahale olmasaydı kur şöyle olurdu” denmez.")
    a("")
    a("## Veri")
    a("")
    a("Kur E, TCMB USD/TRY döviz satış kurunun aylık ortalamasının çeyrek içi aritmetik ortalamasıdır [VERİ] `TP.DK.USD.S.YTL`. g = 100 × ln(E_t / E_{t−1}) [HESAP].")
    a("")
    a("Politika faizi, BIS derlemesi Türkiye merkez bankası politika faizi aylık düzeyinin çeyrek ortalamasıdır [VERİ] `TP.BISPOLFAIZ.TUR`. Bir hafta repo bu seridedir. Ağırlıklı ortalama fonlama (`TP.APIFON4`) panelde durur, denkleme girmez.")
    a("")
    a("Cari işlemler [VERİ] `TP.ODANA6.Q01`, milyon dolardan milyar dolara bölündü, çeyrek toplamı. Portföy, yurt dışı yerleşik tarafı [VERİ] `TP.ODANA6.Q17` (portföy net yükümlülük oluşumu). Pozitif değer, şablonun “yükümlülük oluşumu” işaretidir. Dolarizasyon [VERİ] `TP.KM.G49` / `TP.KM.G57` (döviz tevdiat / mevduat toplamı, bin TL, oran birimsiz).")
    a("")
    a("CDS serisi bulunamadı [DOĞRULANMADI]. γ3 ve epizot denklemindeki b3 çıktı (SAPMA-kontrol).")
    a("")
    a("Swap hariç net [HESAP], milyar dolar: (resmi rezerv `TP.REZVARPD.K1` + forward/swap net `TP.DOVVARNC.K14` + diğer `TP.DOVVARNC.K23`) / 1000. Ons [VERİ] `TP.REZVARPD.K11` milyon troy ons. Ons fiyatı [VERİ] `TP.MK.LON.YTL` ABD doları/ons. Değerleme = önceki ayın ons × fiyat farkı [HESAP].")
    a("")
    oran_min, oran_max = s.get("altin_oran_min"), s.get("altin_oran_max")
    a(f"Altın stoku / (ons × fiyat) oranı, gözlem olduğu her ayda {f2(oran_min)} ile {f2(oran_max)} arasında kaldı (n = {s.get('altin_oran_n')}) [HESAP]. 1’den uzaklık, Londra satış fiyatı ile TCMB’nin altın değerleme fiyatının aynı olmamasından gelebilir.")
    a("")
    a("Birincil S kurulamadı. Doğrudan TCMB satışı yayımlı; kamu bankası (arka kapı) satışı çeyrek çeyrek yayımlı değil [DOĞRULANMADI]. Ön kayıt, ikisi birden yoksa toplamı kurmaz ve eksiği diğeriyle doldurmaz. Dolaşan “yaklaşık 128 milyar dolar” rakamı S’ye yazılmadı. Hükmün satış serisi vekildir [VEKİL], SAPMA-formul işaret düzeltmesiyle.")
    a("")
    a("Yayımlanmış TCMB satışı ayrı sütundur [VERİ]: aylık PDF’te KİT’lere satış + doğrudan müdahale satışı + satım ihalesi. 2018–2025’te satım ihalesi sütunu boştu; dolu olanlar KİT satışı ve, yalnız Aralık 2021 ile Mart 2025’te, doğrudan müdahaledir. PDF: TCMB “Monthly Buying and Selling Amounts”, milyon ABD doları. Aralık 2021 müdahalesi 7,278 milyar, Mart 2025 müdahalesi 1,134 milyar; aynı iki tutar “Doğrudan döviz müdahaleleri” listesinde de durur.")
    a("")
    a("Yan kanal, S’ye eklenmedi. İhracat reeskontu [VERİ] aynı PDF’in alım sütunu ve stok `TP.RKDRK01`. KKM stoku [VERİ] `TP.KKM.K1` milyar dolar; dönüşümün döviz satış tutarı ayrı yayımlanmadığı için akıma çevrilmedi [DOĞRULANMADI]. İhracatçı döviz teslim zorunluluğunun tutarı ayrı seri olarak bulunamadı [DOĞRULANMADI].")
    a("")
    a("EVDS çağrısı `https://evds3.tcmb.gov.tr/igmevdsms-dis/fe` POST, anahtarsız, `groupSeperator` false. İç uç nokta kullanılmadı. Sertifika atlanmadı. TÜİK’e gidilmedi.")
    a("")
    yillar = s.get("ca_yil") or {}
    parca = ", ".join(f"{y}: {f1(yillar[y])} (çeyrek sayısı {s['ca_yil_n'][y]})" for y in yillar)
    a(f"Cari işlemler yıllık toplamı, milyar dolar [VERİ, çeyreklerin toplamı]: {parca}.")
    a("")
    a("## Yöntem")
    a("")
    a("Örnek 2018-Q1–2025-Q4. 2026 yok. Eksik çeyrek doldurulmadı. Denklem, CDS’siz:")
    a("")
    a("g_t = α + θ S_t + γ1 i_{t−1} + γ2 CA_{t−1} + γ4 portföy_{t−1} + γ5 dolarizasyon_{t−1} + γ6 g_{t−1} + ε")
    a("")
    a("S, vekil satış, milyar dolar. Newey-West gecikme 4. c = −1/θ. θ’nın %95 aralığı sıfırı içerirse veya θ negatif değilse c’nin sonlu aralığı yazılmaz. Aralık sıfırın dışında ve θ negatifse se(c) = se(θ) / θ², aralık c ± 1,96 se(c).")
    a("")
    a("Vekil: S = max(0, −ΔR + altın değerlemesi + min(CA, 0)). Literal kilitli işaret (−ΔR − değerleme) panelde `s_literal` diye durur, hükme girmez (SAPMA-formul).")
    a("")
    a("Epizot karşı-olgusu yalnız epizot dışı çeyreklerde, CDS’siz ve dolarizasyonsuz kurulur. Bastırılan puan = max(0, P − g) ve ancak S > 0 ise. Epizot c = S toplamı / bastırılan puan. Payda ≤ 0 ise “bastırmadı”, ortalamaya girmez. Sonraki 4 çeyrekteki fazla değer kaybı Σ max(0, g − P). ≥ %70 erteledi, < %30 geri gelmedi, arası kısmi. 4 çeyrek yoksa test boş.")
    a("")
    a("Araç Z, kilitli epizot pencerelerinde 1. Birinci aşama F, Newey-West t istatistiğinin karesidir. F < 10 ise IV birincil değildir.")
    a("")
    a("## Epizotlar")
    a("")
    a("| Kod | Pencere | S, milyar $ [VEKİL] | Bastırılan puan [HESAP] | c | Çeyrek dışarıda min–max | Sonraki 4 çeyrek |")
    a("| --- | --- | --- | --- | --- | --- | --- |")
    for e in (s.get("epizot") or {}).get("epizot") or []:
        if e.get("c") is not None:
            c = f2(e["c"])
        elif e.get("not") == "pencerede satış yok":
            c = "satış yok"
        elif e.get("not") == "bastırmadı":
            c = "bastırmadı"
        else:
            c = e.get("not") or "—"
        if e.get("loo_n"):
            loo = f"{f2(e['loo_min'])} – {f2(e['loo_max'])}"
        else:
            loo = "yok"
        if e.get("erteleme"):
            ert = f"{e['erteleme']}; fazla {f2(e.get('fazla_4c'))} puan"
        elif e.get("fazla_4c") is not None:
            ert = f"sınıflanmadı; fazla {f2(e['fazla_4c'])} puan"
        else:
            ert = "4 çeyrek yok"
        a(f"| {e['kod']} | {e['pencere']} | {f2(e.get('s_bn'))} | {f2(e.get('bastirilan_puan'))} | {c} | {loo} | {ert} |")
    a("")
    a("Min–max, örnekleme anlamında %95 aralık değildir. Epizot dışı regresyonun gözlem sayısı ve R² raporun sayı ekinde.")
    a("")
    a(f"Bastırma görülen epizotların satış ağırlıklı c’si: {f2(s.get('c_epizot_agirlikli'))} [VEKİL] [HESAP]. Bu ortalama tek epizottan gelir: E2. Diğer pencereler paydada sıfır kaldığı için ortalamaya girmedi.")
    a("")
    by = {r["ceyrek"]: r for r in rows}
    payda_disi = [d for d in ("2019-Q1", "2019-Q2", "2019-Q3", "2019-Q4", "2020-Q1", "2020-Q2", "2020-Q3", "2020-Q4") if by.get(d) and (by[d].get("bast") or 0) <= 0 and (by[d].get("s_vekil") or 0) > 0]
    payda_ici = [d for d in ("2019-Q1", "2019-Q2", "2019-Q3", "2019-Q4", "2020-Q1", "2020-Q2", "2020-Q3", "2020-Q4") if by.get(d) and (by[d].get("bast") or 0) > 0]
    dis_yazi = ", ".join(f"{d} satışı {f2(by[d]['s_vekil'])}" for d in payda_disi) or "yok"
    a(f"E2’nin payı, penceredeki bütün vekil satıştır; g’nin P’nin üstünde kaldığı çeyrekler de paydadır. Bastırmayan ama satışı olan çeyrekler: {dis_yazi} [HESAP]. Bastıran çeyrekler: {', '.join(payda_ici) or 'yok'}.")
    a("")
    a("E2’den sonraki dört çeyrek [HESAP]:")
    a("")
    a("| Çeyrek | g | P | fazla = max(0, g−P) |")
    a("| --- | --- | --- | --- |")
    for d in ("2021-Q1", "2021-Q2", "2021-Q3", "2021-Q4"):
        r = by.get(d) or {}
        a(f"| {d} | {f2(r.get('g'))} | {f2(r.get('P'))} | {f2(r.get('fazla'))} |")
    a("")
    e2 = next(e for e in (s.get("epizot") or {}).get("epizot") or [] if e["kod"] == "E2")
    f21 = (by.get("2021-Q4") or {}).get("fazla")
    a(f"Toplam fazla {f2(e2.get('fazla_4c'))} puan, bastırılan {f2(e2.get('bastirilan_puan'))} puanın yanında ön kaydın %70 eşiğine göre “{e2.get('erteleme')}” diye yazılır. 2021-Q4’ün fazlası {f2(f21)} puandır. Bu, “baskı kalıcı olarak dengelendi” cümlesi değildir. P yapısal karşı-olgu değildir.")
    a("")
    a("Aynı P ile, yayımlanmış TCMB satışı (KİT + müdahale + ihale) [VERİ] epizot oranı ayrıca şöyledir. Bu sütun hükmün c’si değildir. Payda 0,05 puandan küçükse c yazılmaz. Küçük c, az yayımlanmış satışın büyük bir P−g farkına bölünmesidir; o fark satışa bağlanmaz.")
    a("")
    a("| Kod | S, milyar $ [VERİ] | Bastırılan puan | c |")
    a("| --- | --- | --- | --- |")
    for kod, a0, b0 in EPIZOT:
        pencere = [r for r in rows if a0 <= r["ceyrek"] <= b0 and r.get("s_tcmb") is not None and r.get("P") is not None and r.get("g") is not None]
        if not pencere:
            a(f"| {kod} | — | — | eksik |")
            continue
        st = sum(r["s_tcmb"] for r in pencere)
        bt = sum(max(0.0, r["P"] - r["g"]) for r in pencere if r["s_tcmb"] > 0)
        if st <= 0:
            hucre = "satış yok"
        elif bt < 0.05:
            hucre = "bastırmadı"
        else:
            hucre = f2(st / bt)
        a(f"| {kod} | {f2(st)} | {f2(bt)} | {hucre} |")
    a("")
    a("Aralık 2021 doğrudan müdahalesi 7,278 milyar dolar ve o çeyreğin KİT satışıyla birlikte S = 13,12’dir [VERİ]. g = 25,97, P = 7,88; değer kaybı epizot dışı uyumun üstünde kaldı, bastırılan puan 0. Mart 2025 müdahalesi 1,134 milyar dolardır [VERİ]. O çeyrekte g ve P ikisi de 4,80; bastırılan puan 0’a yapışıktır, c üretilmedi.")
    a("")
    r24 = by.get("2024-Q1") or {}
    a(f"Kilitli pencere dışında 2024-Q1 vekil satışı {f2(r24.get('s_vekil'))} milyar dolardır [VEKİL]; yayımlanmış TCMB satışı o çeyrekte {f2(r24.get('s_tcmb'))}. Yeni epizot eklenmedi.")
    a("")
    a("## Havuz regresyonu")
    a("")
    ana = s.get("ana") or {}
    if not ana:
        a("Tam örnek regresyon kurulamadı.")
    else:
        th = ana["katsayi"]["S"]
        a(f"n = {ana['n']}, R² = {f2(ana.get('r2'))}. İlk çeyrek {ana.get('donem', ['?'])[0] if False else (s.get('ana_donem') or ['?'])[0]}, son {(s.get('ana_donem') or ['?'])[-1]}.")
        a("")
        a(f"θ = {f4(th['b'])}, Newey-West se = {f4(th['se'])}, %95 [{f2(th['aralik'][0]) if th.get('aralik') else '—'}, {f2(th['aralik'][1]) if th.get('aralik') else '—'}].")
        if ana.get("c_aralik"):
            a(f"c = {f2(ana['c_nokta'])}, se(c) = {f2(ana.get('c_se'))}, %95 [{f2(ana['c_aralik'][0])}, {f2(ana['c_aralik'][1])}] [VEKİL] [HESAP].")
        elif ana.get("c_nokta"):
            a(f"θ noktası negatif, c noktası {f2(ana['c_nokta'])}, fakat %95 aralık sıfırı içerdiği için sonlu c aralığı yazılmadı: sınırlı değil.")
        else:
            a("θ pozitif ve aralık sıfırı içeriyor. Bastırma beraberliği ayırt edilemedi. Pozitif işaret, ön kayıttaki içsellikle uyumludur: satış, değer kaybı yüksekken artınca θ yukarı itilir. Bu, “satış değer kaybını artırdı” iddiası değildir.")
        a("")
        a("Diğer katsayılar (gecikmeli kontroller), aynı Newey-West:")
        a("")
        a("| Katsayı | Nokta | se | %95 |")
        a("| --- | --- | --- | --- |")
        for ad, kv in ana["katsayi"].items():
            ar = kv.get("aralik")
            ars = "—" if not ar else f"[{f2(ar[0])}, {f2(ar[1])}]"
            a(f"| {ad} | {f4(kv['b'])} | {f4(kv['se'])} | {ars} |")
    a("")
    iv = s.get("iv") or {}
    a(f"Birinci aşama: n = {iv.get('n')}, Z katsayısı = {f4(iv.get('bz'))}, F = {f2(iv.get('F'))}. F < 10 ise IV birincil değildir. Bu turda IV {'birincil değil' if (iv.get('F') is None or iv.get('F') < 10) else 'F eşiğini geçti; yine de ön kayıt birincil sırası OLS’ten başlar'}.")
    a("")
    a("## Yayımlanmış TCMB satışı (hüküm değil)")
    a("")
    duy = s.get("duyarlilik_tcmb")
    if not duy:
        a("Kurulamadı.")
    else:
        th = duy["katsayi"]["S"]
        a(f"S = KİT satışı + doğrudan müdahale + satım ihalesi [VERİ]. n = {duy['n']}, θ = {f4(th['b'])}, se = {f4(th['se'])}.")
        if duy.get("c_aralik"):
            a(f"c = {f2(duy['c_nokta'])}, %95 [{f2(duy['c_aralik'][0])}, {f2(duy['c_aralik'][1])}]. Bu sütun kamu bankası satışını içermez. Hükmün c’si değildir.")
        elif duy.get("c_nokta"):
            a(f"c noktası {f2(duy['c_nokta'])}; aralık sıfırı içeriyor, sonlu aralık yok. Hükmün c’si değildir.")
        else:
            a("θ pozitif ve aralık sıfırın dışında. Yayımlanmış satış ile çeyreklik değer kaybı aynı yönde beraber hareket ediyor. Karşı-olgu yok; bu bir neden cümlesi değildir. c yazılmadı.")
    a("")
    a("## Birikme ve rezerv düzeyi")
    a("")
    br = s.get("birikim_reg")
    if not br:
        a("Birikme regresyonu kurulamadı.")
    else:
        kv = br["katsayi"].get("birikim_gecikme") or {}
        ar = kv.get("aralik")
        if ar and ar[0] > 0:
            hukum_b = "bastırılan baskı sonraki değer kaybıyla beraber artıyor"
        else:
            hukum_b = "birikme ayırt edilemedi"
        a(f"φ = {f4(kv.get('b'))}, se = {f4(kv.get('se'))}, %95 {('[' + f2(ar[0]) + ', ' + f2(ar[1]) + ']') if ar else '—'}. {hukum_b}. φ tek başına neden değildir. n = {br['n']}.")
    a("")
    nl = s.get("nonlin") or {}
    if nl.get("kosulmadi"):
        a(f"Doğrusal olmayan maliyet koşulmadı. R medyanı = {f2(nl.get('r_medyan'))}. Ön kayıt, medyan sıfırdan büyük değilse oranı kurmaz. “c, rezerv düşünce yükseliyor” ayırt edilemedi.")
    else:
        kv = (nl.get("katsayi") or {}).get("S_carpi_R_bolu_medyan") or {}
        ar = kv.get("aralik")
        th0 = (nl.get("katsayi") or {}).get("S") or {}
        if ar and kv.get("b", 0) > 0 and ar[0] > 0 and th0.get("b", 0) < 0:
            hukum_n = "c, rezerv düşünce yükseliyor"
        else:
            hukum_n = "yükseliş ayırt edilemedi"
        a(f"R medyanı = {f2(nl.get('r_medyan'))} milyar dolar. θ0 = {f4(th0.get('b'))}, θ1 = {f4(kv.get('b'))}, θ1 %95 {('[' + f2(ar[0]) + ', ' + f2(ar[1]) + ']') if ar else '—'}. {hukum_n}.")
    a("")
    a("## Zayıf noktalar")
    a("")
    a("- Birincil c tek pencereden gelir ve o pencere “erteledi” diye sınıflanmıştır. Sonraki fazla değer kaybının büyük parçası 2021-Q4’tedir. Kalıcı dengeleme diye okunmaz.")
    a("- Epizot c’sinin payı, bastırmayan çeyreklerin satışını da içerir. Bu, kilitli oran kuralıdır ve c’yi, yalnız bastıran çeyrekler alınsaydı çıkacak orandan büyük tutar.")
    a("- Vekil satış, swap hariç netin düşüşünden cari açık ve altın fiyatı ayrıldıktan sonra kalan artı kısımdır. Brüt rezerv artmadan forward/swap açığı büyürse bu düşüş vekile girer. Kamu bankasının kendi bilançosundan sattığı döviz, TCMB’nin bu ölçülen stokunu o çeyrekte düşürmediyse vekile girmez. 69,60 milyar dolar, dolaşan 128 milyar dolarlık iddianın karşılığı değildir.")
    a("- Epizot dışı örnek 16 çeyrektir. P’nin faiz katsayısı bu kısa örnekte pozitiftir. P yapısal değildir.")
    a("- İçsellik durur. Anlatı aracı epizot takvimidir; dışsallık kanıtlanmadı. Birinci aşama F eşiğin altında kaldı, IV birincil yazılmadı.")
    a("- Newey-West gecikme 4, çeyrek sayısı 32 iken standart hatalar geniştir. Havuz θ’sının aralığı sıfırı içerir ve işaret pozitiftir; havuzdan sonlu c çıkmaz. Izgara BELİRSİZ’dir çünkü birincil c’nin örnekleme aralığı yoktur. Çeyrek dışarıda bırakma aralığı %95 diye kullanılmadı. Eşik kaydırılmadı.")
    a("- `model_rr.py` repoda ve çalışma ağacında yoktu. b = 1,26 ve b = 0,42 koşusu, tükeniş çeyreği ve TÜFE yolu üretilmedi.")
    a("- Kamu bankası satışının resmi çeyreklik satırı bulunamadı. Sayıştay düzenlilik raporları ve TBMM soru önergesi bu tutarı bir zaman serisi olarak vermiyor. 128 milyar dolar S’ye yazılmadı.")
    a("")
    a("## Sayı eki")
    a("")
    a("Çeyrek panel `ceyrek_panel.csv`. Ham EVDS `ham/evds_aylik.json`. Aylık TCMB satış `ham/tcmb_satis_aylik.json`. Makine özeti `sonuclar.json`.")
    epi = s.get("epizot") or {}
    a(f"Epizot dışı n = {epi.get('n_dis')}, R² = {f2(epi.get('r2_dis'))}. Katsayı sırası: sabit, faiz, cari, portföy, g gecikmesi. Noktalar: {', '.join(f4(x) for x in (epi.get('b') or []))}.")
    (KOK / "RAPOR.md").write_text("\n".join(p) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
