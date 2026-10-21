"""Rejim katsayıları. Kurallar: ON_KAYIT.md. Katsayılar [TAHMİN]."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from gecis_payi_band import _ols_nw

KOK = Path(__file__).resolve().parent
HAM = KOK / "ham" / "aylik.json"
CIKTI = KOK / "tahmin.json"

REJIM = {
    "R2013": ("2013-01", "2013-12"),
    "R1617": ("2016-01", "2017-12"),
    "R1823": ("2018-01", "2023-12"),
    "R2426": ("2024-01", "2026-10"),
}
Y2018 = ("2018-01", "2018-12")
COKUS = ("2024-01", "2025-12")
REZERV_Q = ("2018-Q1", "2025-Q4")
FARK_ENDEKS = 0.30
TOHUM = 20261021
B = 1000


def _ay_ok(a: str, lo: str, hi: str) -> bool:
    return lo <= a <= hi


def _lag(ay: str, k: int) -> str:
    y, m = int(ay[:4]), int(ay[5:7])
    m -= k
    while m <= 0:
        m += 12
        y -= 1
    return f"{y:04d}-{m:02d}"


def _qi(q: str) -> int:
    y, qq = q.split("-Q")
    return int(y) * 4 + int(qq) - 1


def _qd(i: int) -> str:
    return f"{i // 4}-Q{i % 4 + 1}"


def _ceyrek(ay: str) -> str:
    y, m = ay.split("-")
    return f"{y}-Q{(int(m) - 1) // 3 + 1}"


def _ln_oran(a: float, b: float) -> float | None:
    if a is None or b is None or a <= 0 or b <= 0:
        return None
    return 100.0 * math.log(a / b)


def panel_kur(ham: dict) -> tuple[list[dict], list[dict]]:
    """Aylık panel ve sapma satırları. Hedef 5; belge yıl hedefi vermediyse [DOĞRULANMADI]."""
    sapma: list[dict] = []
    seri = ham["seriler"]

    def harita(ad: str) -> dict[str, float]:
        return {r["ay"]: r["deger"] for r in seri[ad]["satir"] if len(r["ay"]) >= 7}

    e_map, i_map = harita("e24"), harita("i")
    usd, arsiv, yeni = harita("usd"), harita("p_arsiv"), harita("p_2025")
    hedef_yil = ham.get("hedef_belge", {}).get("yil_hedefi") or {}
    if not hedef_yil:
        sapma.append({
            "kod": "hedef-belge",
            "not": "Nokta hedef belgesi inip yıl yılı 5'ten farklı bir sayı vermedi. Bütün aylar 5. Etiket DOĞRULANMADI. Eşik kaymadı.",
        })
    if not ham.get("faiz_tablo", {}).get("bulundu"):
        sapma.append({
            "kod": "SAPMA-faiz",
            "not": "Bir hafta repo tablosu hüküm serisi olacak biçimde inmedi. Hüküm faizi TP.APIFON4, ağırlıklı ortalama fonlama maliyeti [VEKİL]. Eşik kaymadı.",
        })

    def fiyat(ay: str) -> tuple[float | None, str]:
        geri = _lag(ay, 12)
        if ay in arsiv and geri in arsiv:
            return arsiv[ay], "arsiv"
        if ay in yeni and geri in yeni:
            return yeni[ay], "baz2025"
        return None, ""

    aylar = sorted(set(e_map) | set(i_map) | set(usd) | set(arsiv) | set(yeni))
    satir = []
    for ay in aylar:
        if ay < "2012-01" or ay > "2026-10":
            continue
        p, kaynak = fiyat(ay)
        geri12 = _lag(ay, 12)
        geri1 = _lag(ay, 1)
        p12, _ = fiyat(geri12)
        p1, k1 = fiyat(geri1)
        pi = None
        if p is not None and p12 is not None and p12 > 0:
            pi_arsiv = pi_yeni = None
            if ay in arsiv and geri12 in arsiv and arsiv[geri12] > 0:
                pi_arsiv = 100.0 * (arsiv[ay] / arsiv[geri12] - 1.0)
            if ay in yeni and geri12 in yeni and yeni[geri12] > 0:
                pi_yeni = 100.0 * (yeni[ay] / yeni[geri12] - 1.0)
            if pi_arsiv is not None and pi_yeni is not None and abs(pi_arsiv - pi_yeni) > FARK_ENDEKS:
                pi = pi_yeni
                sapma.append({"kod": "SAPMA-endeks", "ay": ay, "arsiv": pi_arsiv, "baz2025": pi_yeni})
            elif pi_arsiv is not None:
                pi = pi_arsiv
            else:
                pi = pi_yeni
        pi1 = None
        if p is not None and p1 is not None and p1 > 0 and (kaynak == k1 or k1 == "" or True):
            # Aynı endeks ailesi: fiyat() 12 ay koşuluna bağlı. Aylık log için iki düzey aynı haritadan.
            if ay in arsiv and geri1 in arsiv and arsiv[geri1] > 0:
                pi1 = _ln_oran(arsiv[ay], arsiv[geri1])
            elif ay in yeni and geri1 in yeni and yeni[geri1] > 0:
                pi1 = _ln_oran(yeni[ay], yeni[geri1])
        g12 = _ln_oran(usd.get(ay), usd.get(geri12))
        g1 = _ln_oran(usd.get(ay), usd.get(geri1))
        g3 = _ln_oran(usd.get(ay), usd.get(_lag(ay, 3)))
        geri6 = _lag(ay, 6)
        p6_arsiv = arsiv.get(geri6)
        p6_yeni = yeni.get(geri6)
        pi6 = None
        if ay in arsiv and p6_arsiv and p6_arsiv > 0:
            pi6 = 100.0 * (arsiv[ay] / p6_arsiv - 1.0) * 2.0
        elif ay in yeni and p6_yeni and p6_yeni > 0:
            pi6 = 100.0 * (yeni[ay] / p6_yeni - 1.0) * 2.0
        yil = ay[:4]
        h = float(hedef_yil.get(yil, 5.0))
        satir.append({
            "ay": ay,
            "e": e_map.get(ay),
            "i": i_map.get(ay),
            "usd": usd.get(ay),
            "pi": pi,
            "pi1": pi1,
            "pi6": pi6,
            "g12": g12,
            "g1": g1,
            "g3": g3,
            "h": h,
        })
    # yinelenen endeks sapmalarını tekle
    gor = set()
    tek = []
    for s in sapma:
        im = (s.get("kod"), s.get("ay"))
        if im in gor:
            continue
        gor.add(im)
        tek.append(s)
    return satir, tek


def _pencere(satir: list[dict], lo: str, hi: str, alanlar: list[str]) -> list[dict]:
    out = []
    for r in satir:
        if not _ay_ok(r["ay"], lo, hi):
            continue
        if any(r.get(a) is None or not math.isfinite(r[a]) for a in alanlar):
            continue
        out.append(r)
    return out


def _nw(y: np.ndarray, X: np.ndarray) -> dict | None:
    n, k = X.shape
    if n < 10 or n < k + 2:
        return None
    # Sabit terim sütunu varyansı sıfırdır; bu, regresörün tanımlanamaması değildir.
    egim = X[:, 1:] if k > 1 and np.allclose(X[:, 0], 1.0) else X
    if egim.size and np.any(np.std(egim, axis=0) < 1e-12):
        return None
    gecikme = 2 if n < 24 else 4
    try:
        b, V, r2, _e = _ols_nw(y, X, gecikme)
    except np.linalg.LinAlgError:
        return None
    se = np.sqrt(np.clip(np.diag(V), 0, None))
    if not np.all(np.isfinite(b)) or not np.all(np.isfinite(se)):
        return None
    return {
        "n": int(n),
        "k": int(k),
        "b": [float(x) for x in b],
        "se": [float(x) for x in se],
        "r2": float(r2),
        "gecikme": gecikme,
    }


def _uc(b: float, se: float) -> list[float]:
    return [b - 1.96 * se, b + 1.96 * se]


def _boot_ekle(rng: np.random.Generator, y: np.ndarray, X: np.ndarray) -> list[list[float]]:
    n = len(y)
    ciz = []
    for _ in range(B):
        ix = rng.integers(0, n, n)
        try:
            b = np.linalg.lstsq(X[ix], y[ix], rcond=None)[0]
        except np.linalg.LinAlgError:
            continue
        if np.all(np.isfinite(b)):
            ciz.append([float(x) for x in b])
    return ciz


def _yuzdelik(ciz: list[list[float]], sutun: int) -> dict:
    if len(ciz) < 500:
        return {"kuruldu": False, "n_gecerli": len(ciz)}
    kol = np.array([c[sutun] for c in ciz], float)
    return {
        "kuruldu": True,
        "n_gecerli": len(ciz),
        "p2_5": float(np.percentile(kol, 2.5)),
        "p97_5": float(np.percentile(kol, 97.5)),
    }


def _beklenti_xy(rows: list[dict], pi_alan: str = "pi", g_alan: str = "g12") -> tuple[np.ndarray, np.ndarray] | None:
    if len(rows) < 10:
        return None
    e = np.array([r["e"] for r in rows], float)
    pi = np.array([r[pi_alan] for r in rows], float)
    g = np.array([r[g_alan] for r in rows], float)
    h = np.array([r["h"] for r in rows], float)
    y = e - pi
    X = np.column_stack([h - pi, g])
    return y, X


def _beklenti_ozet(fit: dict) -> dict:
    w, phi = fit["b"]
    sw, sp = fit["se"]
    return {
        "n": fit["n"],
        "w": w,
        "phi": phi,
        "geriye": 1.0 - w,
        "se_w": sw,
        "se_phi": sp,
        "uc_w": _uc(w, sw),
        "uc_phi": _uc(phi, sp),
        "r2": fit["r2"],
        "gecikme": fit["gecikme"],
        "etiket": "TAHMIN",
    }


def _serbest(rows: list[dict]) -> dict | None:
    e = np.array([r["e"] for r in rows], float)
    pi = np.array([r["pi"] for r in rows], float)
    g = np.array([r["g12"] for r in rows], float)
    h = np.array([r["h"] for r in rows], float)
    X = np.column_stack([np.ones(len(rows)), h, pi, g])
    # Hedef sabitken sabit terim ile hedef katsayısı ayrılmaz.
    if np.std(h) < 1e-12:
        X = np.column_stack([np.ones(len(rows)), pi, g])
        fit = _nw(e, X)
        if fit is None:
            return None
        return {"n": fit["n"], "ayrik": False, "b": fit["b"], "se": fit["se"], "r2": fit["r2"], "ad": ["sabit", "pi", "g12"]}
    fit = _nw(e, X)
    if fit is None:
        return None
    return {"n": fit["n"], "ayrik": True, "b": fit["b"], "se": fit["se"], "r2": fit["r2"], "ad": ["sabit", "h", "pi", "g12"]}


def _gecis_xy(rows: list[dict], g_alan: str = "g1") -> tuple[np.ndarray, np.ndarray]:
    y = np.array([r["pi1"] for r in rows], float)
    g = np.array([r[g_alan] for r in rows], float)
    X = np.column_stack([np.ones(len(rows)), g])
    return y, X


def _gecis_ozet(fit: dict) -> dict:
    a, lam = fit["b"]
    sa, sl = fit["se"]
    return {
        "n": fit["n"],
        "alfa": a,
        "lam": lam,
        "se_alfa": sa,
        "se_lam": sl,
        "uc_lam": _uc(lam, sl),
        "r2": fit["r2"],
        "gecikme": fit["gecikme"],
        "etiket": "TAHMIN",
    }


def _faiz_xy(satir: list[dict], rows: list[dict]) -> tuple[np.ndarray, np.ndarray] | None:
    by_ay = {r["ay"]: r for r in satir}
    y, X = [], []
    for r in rows:
        once = by_ay.get(_lag(r["ay"], 1))
        if once is None:
            continue
        if any(once.get(k) is None for k in ("i", "pi", "e", "h")):
            continue
        y.append(r["i"])
        X.append([1.0, once["i"], once["pi"], once["e"] - once["h"]])
    if len(y) < 10:
        return None
    return np.array(y, float), np.array(X, float)


def _faiz_ozet(fit: dict) -> dict:
    ad = ["alfa", "rho", "beta_pi", "beta_e"]
    out = {"n": fit["n"], "r2": fit["r2"], "gecikme": fit["gecikme"], "etiket": "TAHMIN"}
    for i, a in enumerate(ad):
        out[a] = fit["b"][i]
        out[f"se_{a}"] = fit["se"][i]
        out[f"uc_{a}"] = _uc(fit["b"][i], fit["se"][i])
    return out


def _kur_xy(satir: list[dict], rows: list[dict]) -> tuple[np.ndarray, np.ndarray] | None:
    by_ay = {r["ay"]: r for r in satir}
    y, X = [], []
    for r in rows:
        once = by_ay.get(_lag(r["ay"], 1))
        if once is None or once.get("i") is None or r.get("g1") is None:
            continue
        y.append(r["g1"])
        X.append([1.0, once["i"]])
    if len(y) < 10:
        return None
    return np.array(y, float), np.array(X, float)


def _kur_ozet(fit: dict) -> dict:
    return {
        "n": fit["n"],
        "alfa_g": fit["b"][0],
        "beta_i": fit["b"][1],
        "se_alfa_g": fit["se"][0],
        "se_beta_i": fit["se"][1],
        "uc_beta_i": _uc(fit["b"][1], fit["se"][1]),
        "r2": fit["r2"],
        "gecikme": fit["gecikme"],
        "etiket": "TAHMIN",
    }


def _rezerv(ham: dict, satir: list[dict]) -> dict:
    rmap = {r["ay"]: r["deger"] / 1000.0 for r in ham["seriler"]["rezerv"]["satir"]}
    usd = {r["ay"]: r["usd"] for r in satir if r.get("usd") is not None}
    iay = {r["ay"]: r["i"] for r in satir if r.get("i") is not None}
    ceyrek: dict[str, dict] = {}
    for ay, u in usd.items():
        q = _ceyrek(ay)
        ceyrek.setdefault(q, {"usd": [], "i": [], "r": []})
        ceyrek[q]["usd"].append(u)
        if ay in iay:
            ceyrek[q]["i"].append(iay[ay])
        if ay in rmap:
            ceyrek[q]["r"].append((ay, rmap[ay]))
    qlar = sorted(ceyrek)
    hazir = {}
    for q in qlar:
        d = ceyrek[q]
        if len(d["usd"]) < 3 or len(d["i"]) < 3 or not d["r"]:
            continue
        hazir[q] = {
            "usd": sum(d["usd"]) / len(d["usd"]),
            "i": sum(d["i"]) / len(d["i"]),
            "r": d["r"][-1][1],
        }
    y, X, qs = [], [], []
    for q, d in hazir.items():
        if not (REZERV_Q[0] <= q <= REZERV_Q[1]):
            continue
        once = _qd(_qi(q) - 1)
        if once not in hazir:
            continue
        g = _ln_oran(d["usd"], hazir[once]["usd"])
        if g is None:
            continue
        s = max(0.0, -(d["r"] - hazir[once]["r"]))
        y.append(g)
        X.append([1.0, s, hazir[once]["i"]])
        qs.append(q)
    y_a = np.array(y, float)
    X_a = np.array(X, float) if X else np.zeros((0, 3))
    fit = _nw(y_a, X_a) if len(y) else None
    out: dict = {"n": len(y), "ilk": qs[0] if qs else None, "son": qs[-1] if qs else None, "etiket": "VEKIL", "c": None}
    if fit is None:
        out["kuruldu"] = False
        out["neden"] = "denklem kurulamadı"
        return out
    theta, se_t = fit["b"][1], fit["se"][1]
    uc = _uc(theta, se_t)
    out.update({
        "kuruldu": True,
        "alfa": fit["b"][0],
        "theta": theta,
        "gamma": fit["b"][2],
        "se_theta": se_t,
        "uc_theta": uc,
        "r2": fit["r2"],
        "gecikme": fit["gecikme"],
        "b": fit["b"],
        "se": fit["se"],
    })
    if theta < 0 and uc[1] < 0:
        c = -1.0 / theta
        se_c = se_t / theta**2
        out["c"] = c
        out["se_c"] = se_c
        out["uc_c"] = _uc(c, se_c)
    else:
        out["c"] = None
        out["c_not"] = "sınırlı değil"
    out["_y"] = y_a
    out["_X"] = X_a
    return out


def _duyarlilik(satir: list[dict]) -> dict:
    out = {}
    for ad, (lo, hi) in {**REJIM, "Y2018": Y2018}.items():
        rows6 = _pencere(satir, lo, hi, ["e", "pi6", "g12", "h"])
        xy = _beklenti_xy(rows6, "pi6", "g12") if rows6 else None
        fit = _nw(*xy) if xy else None
        rows3 = _pencere(satir, lo, hi, ["e", "pi", "g3", "h"])
        xy3 = _beklenti_xy(rows3, "pi", "g3") if rows3 else None
        fit3 = _nw(*xy3) if xy3 else None
        # gecikmeli kur: g1_{t-1} pi1_t ile. Satırda g1 gecikmesi ayrıca.
        out[ad] = {
            "pi6": None if fit is None else {"n": fit["n"], "w": fit["b"][0], "geriye": 1 - fit["b"][0], "phi": fit["b"][1], "se_w": fit["se"][0]},
            "g3": None if fit3 is None else {"n": fit3["n"], "w": fit3["b"][0], "phi": fit3["b"][1], "se_phi": fit3["se"][1]},
        }
    # geçiş, g1 gecikmeli
    by = {r["ay"]: r for r in satir}
    gec = {}
    for ad, (lo, hi) in REJIM.items():
        y, X = [], []
        for r in satir:
            if not _ay_ok(r["ay"], lo, hi) or r.get("pi1") is None:
                continue
            once = by.get(_lag(r["ay"], 1))
            if once is None or once.get("g1") is None:
                continue
            y.append(r["pi1"])
            X.append([1.0, once["g1"]])
        fit = _nw(np.array(y, float), np.array(X, float)) if len(y) >= 10 else None
        gec[ad] = None if fit is None else {"n": fit["n"], "lam": fit["b"][1], "se_lam": fit["se"][1], "uc_lam": _uc(fit["b"][1], fit["se"][1])}
    return {"beklenti": out, "gecis_gecikme": gec}


def tahmin(ham: dict | None = None) -> dict:
    if ham is None:
        ham = json.loads(HAM.read_text(encoding="utf-8"))
    satir, sapma = panel_kur(ham)
    sapma.append({
        "kod": "SAPMA-sabit-terim",
        "not": (
            "İlk kod, sabit terim sütununun varyansı sıfır diye geçiş, faiz, kur ve rezerv denklemlerini kurmuyordu. "
            "Sabit terim tanımlama koşulu değildir; eğim sütunları denetlenir. Düzeltme senaryo hükmünden önce yapıldı. Eşik kaymadı."
        ),
    })
    rng = np.random.default_rng(TOHUM)
    bek: dict[str, dict] = {}
    bek_boot: dict[str, list] = {}
    pencereler = list(REJIM.items()) + [("Y2018", Y2018)]
    ham_xy: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for ad, (lo, hi) in pencereler:
        rows = _pencere(satir, lo, hi, ["e", "pi", "g12", "h"])
        xy = _beklenti_xy(rows) if rows else None
        fit = _nw(*xy) if xy else None
        if fit is None or xy is None:
            bek[ad] = {"kuruldu": False, "n": 0 if xy is None else int(len(xy[0]))}
        else:
            bek[ad] = {"kuruldu": True, **_beklenti_ozet(fit), "serbest": _serbest(rows)}
            ham_xy[ad] = xy
    for ad, _ in pencereler:
        if ad not in ham_xy:
            continue
        y, X = ham_xy[ad]
        ciz = _boot_ekle(rng, y, X)
        o = bek[ad]
        o["boot_w"] = _yuzdelik(ciz, 0)
        o["boot_phi"] = _yuzdelik(ciz, 1)
        bek_boot[ad] = ciz

    gec: dict[str, dict] = {}
    gec_xy: dict[str, tuple] = {}
    for ad, (lo, hi) in pencereler:
        rows = _pencere(satir, lo, hi, ["pi1", "g1"])
        if len(rows) < 10:
            gec[ad] = {"kuruldu": False, "n": len(rows)}
            continue
        xy = _gecis_xy(rows)
        fit = _nw(*xy)
        if fit is None:
            gec[ad] = {"kuruldu": False, "n": len(rows)}
        else:
            gec[ad] = {"kuruldu": True, **_gecis_ozet(fit)}
            gec_xy[ad] = xy
    for ad, _ in pencereler:
        if ad not in gec_xy:
            continue
        y, X = gec_xy[ad]
        ciz = _boot_ekle(rng, y, X)
        gec[ad]["boot_alfa"] = _yuzdelik(ciz, 0)
        gec[ad]["boot_lam"] = _yuzdelik(ciz, 1)

    rows_c = _pencere(satir, COKUS[0], COKUS[1], ["pi1", "g1"])
    fit_c = _nw(*_gecis_xy(rows_c)) if len(rows_c) >= 10 else None
    cokus = {"kuruldu": fit_c is not None, "pencere": list(COKUS)}
    if fit_c:
        cokus.update(_gecis_ozet(fit_c))

    faiz: dict[str, dict] = {}
    faiz_xy: dict[str, tuple] = {}
    for ad, (lo, hi) in REJIM.items():
        rows = [r for r in satir if _ay_ok(r["ay"], lo, hi) and r.get("i") is not None]
        xy = _faiz_xy(satir, rows)
        fit = _nw(*xy) if xy else None
        if fit is None:
            faiz[ad] = {"kuruldu": False, "n": 0 if xy is None else int(len(xy[0]))}
        else:
            faiz[ad] = {"kuruldu": True, **_faiz_ozet(fit)}
            faiz_xy[ad] = xy
    for ad in REJIM:
        if ad not in faiz_xy:
            continue
        y, X = faiz_xy[ad]
        ciz = _boot_ekle(rng, y, X)
        for i, a in enumerate(["alfa", "rho", "beta_pi", "beta_e"]):
            faiz[ad][f"boot_{a}"] = _yuzdelik(ciz, i)

    kur: dict[str, dict] = {}
    kur_xy: dict[str, tuple] = {}
    for ad, (lo, hi) in REJIM.items():
        rows = [r for r in satir if _ay_ok(r["ay"], lo, hi)]
        xy = _kur_xy(satir, rows)
        fit = _nw(*xy) if xy else None
        if fit is None:
            kur[ad] = {"kuruldu": False, "n": 0 if xy is None else int(len(xy[0]))}
        else:
            kur[ad] = {"kuruldu": True, **_kur_ozet(fit)}
            kur_xy[ad] = xy
    for ad in REJIM:
        if ad not in kur_xy:
            continue
        y, X = kur_xy[ad]
        ciz = _boot_ekle(rng, y, X)
        kur[ad]["boot_alfa_g"] = _yuzdelik(ciz, 0)
        kur[ad]["boot_beta_i"] = _yuzdelik(ciz, 1)

    rezerv = _rezerv(ham, satir)
    if rezerv.get("_y") is not None and rezerv.get("kuruldu"):
        ciz = _boot_ekle(rng, rezerv["_y"], rezerv["_X"])
        rezerv["boot_theta"] = _yuzdelik(ciz, 1)
    rezerv.pop("_y", None)
    rezerv.pop("_X", None)

    duyar = _duyarlilik(satir)
    lam2013 = gec.get("R2013", {})
    cokus_hukum = "belirsiz"
    if cokus.get("kuruldu") and lam2013.get("kuruldu"):
        ust = cokus["uc_lam"][1]
        if cokus["lam"] < 0.5 * lam2013["lam"] and ust < lam2013["lam"]:
            cokus_hukum = "tutar"
        else:
            cokus_hukum = "tutmaz"
    else:
        cokus_hukum = "belirsiz"

    son_gozlem = {}
    for r in reversed(satir):
        if all(r.get(k) is not None for k in ("e", "i", "pi", "g12", "usd")) and r["ay"] < "2026-10":
            son_gozlem = {k: r[k] for k in ("ay", "e", "i", "pi", "g12", "usd", "h")}
            break
    # çeyreklik başlangıç penceresi: 2025-Q4 .. 2026-Q3
    def q_ort(alan_ay: dict[str, float], q: str) -> float | None:
        y, qq = q.split("-Q")
        m0 = (int(qq) - 1) * 3 + 1
        vals = []
        for m in range(m0, m0 + 3):
            ay = f"{y}-{m:02d}"
            if ay in alan_ay and alan_ay[ay] is not None:
                vals.append(alan_ay[ay])
        if len(vals) < 3:
            return None
        return sum(vals) / 3

    usd_ay = {r["ay"]: r["usd"] for r in satir if r.get("usd")}
    # çeyrek log farkı için çeyrek ortalaması
    qlar = ["2025-Q3", "2025-Q4", "2026-Q1", "2026-Q2", "2026-Q3"]
    q_usd = {q: q_ort(usd_ay, q) for q in qlar}
    g_q = []
    for a, bq in zip(qlar, qlar[1:]):
        g = _ln_oran(q_usd[bq], q_usd[a]) if q_usd[a] and q_usd[bq] else None
        g_q.append(g)
    # fiyat çeyrek: arşiv veya 2025, aylık düzeylerin ortalaması zor; pi1 toplamı
    pi_q = []
    for q in qlar[1:]:
        y, qq = q.split("-Q")
        m0 = (int(qq) - 1) * 3 + 1
        parca = []
        for m in range(m0, m0 + 3):
            ay = f"{y}-{m:02d}"
            rec = next((r for r in satir if r["ay"] == ay), None)
            if rec and rec.get("pi1") is not None:
                parca.append(rec["pi1"])
        pi_q.append(sum(parca) if len(parca) == 3 else None)

    rmap = {r["ay"]: r["deger"] / 1000.0 for r in ham["seriler"]["rezerv"]["satir"]}
    r_son = None
    r_ay = None
    for ay in sorted(rmap):
        if ay < "2026-10":
            r_son, r_ay = rmap[ay], ay

    blob = {
        "etiket": "TAHMIN",
        "evds3": True,
        "hedef_etiket": "DOGRULANMADI" if not (ham.get("hedef_belge") or {}).get("yil_hedefi") else "VERI",
        "faiz_etiket": "VEKIL" if not (ham.get("faiz_tablo") or {}).get("bulundu") else "VERI",
        "sapma": sapma,
        "beklenti": bek,
        "gecis": gec,
        "cokus_2024_2025": {**cokus, "tanim": cokus_hukum},
        "faiz": faiz,
        "kur": kur,
        "rezerv": rezerv,
        "duyarlilik": duyar,
        "baslangic": {
            "gozlem": son_gozlem,
            "g_ceyrek_son4": g_q,
            "pi_ceyrek_son4": pi_q,
            "rezerv_milyar": r_son,
            "rezerv_ay": r_ay,
        },
        "n_ay": len(satir),
    }
    CIKTI.write_text(json.dumps(blob, ensure_ascii=False, indent=1), encoding="utf-8")
    return blob


if __name__ == "__main__":
    t = tahmin()
    for ad, b in t["beklenti"].items():
        if b.get("kuruldu"):
            print(ad, "w", round(b["w"], 3), "geriye", round(b["geriye"], 3), "phi", round(b["phi"], 3), "n", b["n"])
        else:
            print(ad, "beklenti kurulamadı", b.get("n"))
    print("cokus", t["cokus_2024_2025"].get("tanim"), t["cokus_2024_2025"].get("lam"))
    print("c", t["rezerv"].get("c"), "theta", t["rezerv"].get("theta"))
