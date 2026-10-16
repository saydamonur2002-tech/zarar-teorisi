"""H1–H7 sınaması. Karar kuralları ZINCIR_ONKAYIT.md ile aynıdır; katsayıdan sonra değiştirilmez.

Çalıştır: python3 zincir_h1h7.py
Çıktı: zincir_h1h7_sonuc.json, zincir_h1h7_ham.csv
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import numpy as np
import urllib.request

from evds_cek import BASE, get_json

KOK = Path(__file__).resolve().parent
CEKILME = date.today().isoformat()
LAG = 3
LAG_DUYAR = 6
MIN_N = 36
H1_H = 9
H1_RAPOR = (6, 9, 12)
H5_H = 3

# Kırılma pencereleri (şok ayı). YYYY-MM.
KIRILMA = {
    "d2018": ("2018-08", "2018-12"),
    "d2020": ("2020-03", "2020-06"),
    "d2122": ("2021-09", "2022-12"),
    "d2023": ("2023-06", "2099-12"),
}


def fetch(series: list[str], agg: list[str], start: str, end: str, freq: str) -> tuple[dict, dict]:
    body = {
        "type": "json",
        "series": "-".join(series),
        "aggregationTypes": "-".join(agg),
        "formulas": "-".join("0" for _ in series),
        "startDate": start,
        "endDate": end,
        "frequency": freq,
        "decimalSeperator": ".",
        "decimal": "4",
        "dateFormat": "0",
        "lang": "TR",
        "yon": "0",
        "sira": "0",
        "ozelFormuller": [],
        "groupSeperator": False,
        "isRaporSayfasi": False,
    }
    try:
        data = get_json(f"{BASE}/fe", body)
    except Exception as exc:  # noqa: BLE001
        return {}, {"hata": str(exc)[:300], "seri": series}
    names = data.get("seriesNames") or {}
    out: dict[str, dict[str, float]] = {s: {} for s in series}
    for it in data.get("items") or []:
        t = str(it.get("Tarih"))
        for s in series:
            v = it.get(s.replace(".", "_"))
            if v not in (None, ""):
                out[s][t] = float(str(v).replace(",", ""))
    found = {s: bool(out[s]) for s in series}
    return out, {"ad": {s: names.get(s.replace(".", "_")) for s in series}, "var": found}


def aylar(index: list[str]) -> list[str]:
    return sorted(index)


def yoy(level: dict[str, float], aylar_: list[str]) -> dict[str, float]:
    ix = {a: i for i, a in enumerate(aylar_)}
    out = {}
    for a in aylar_:
        i = ix[a]
        if i < 12:
            continue
        b = aylar_[i - 12]
        if a in level and b in level and level[b] != 0:
            out[a] = level[a] / level[b] - 1
    return out


def reel(nom: dict[str, float], cpi: dict[str, float], aylar_: list[str]) -> dict[str, float]:
    """(S/P)_t / (S/P)_{t-12} - 1. İki seri de aynı ay ızgarasında."""
    ix = {a: i for i, a in enumerate(aylar_)}
    out = {}
    for a in aylar_:
        i = ix[a]
        if i < 12:
            continue
        b = aylar_[i - 12]
        if a in nom and b in nom and a in cpi and b in cpi and nom[b] and cpi[b]:
            out[a] = (nom[a] / cpi[a]) / (nom[b] / cpi[b]) - 1
    return out


def dlog(level: dict[str, float], aylar_: list[str]) -> dict[str, float]:
    ix = {a: i for i, a in enumerate(aylar_)}
    out = {}
    for a in aylar_:
        i = ix[a]
        if i < 1:
            continue
        b = aylar_[i - 1]
        if a in level and b in level and level[a] > 0 and level[b] > 0:
            out[a] = float(np.log(level[a]) - np.log(level[b]))
    return out


def diff(level: dict[str, float], aylar_: list[str]) -> dict[str, float]:
    ix = {a: i for i, a in enumerate(aylar_)}
    out = {}
    for a in aylar_:
        i = ix[a]
        if i < 1:
            continue
        b = aylar_[i - 1]
        if a in level and b in level:
            out[a] = level[a] - level[b]
    return out


def kirilma(ay: str) -> list[float]:
    def icinde(a, lo, hi):
        return lo <= a <= hi
    return [1.0 if icinde(ay, lo, hi) else 0.0 for lo, hi in KIRILMA.values()]


def hizala(seriler: list[dict[str, float]]) -> list[str]:
    if not seriler:
        return []
    ortak = set(seriler[0])
    for s in seriler[1:]:
        ortak &= set(s)
    return sorted(ortak)


def nw_se(X: np.ndarray, e: np.ndarray, bant: int) -> np.ndarray:
    n, k = X.shape
    u = X * e[:, None]
    S = u.T @ u
    L = max(int(bant), 0)
    for lag in range(1, L + 1):
        w = 1.0 - lag / (L + 1.0)
        G = u[lag:].T @ u[:-lag]
        S += w * (G + G.T)
    xtx = np.linalg.pinv(X.T @ X)
    V = xtx @ S @ xtx
    se = np.sqrt(np.clip(np.diag(V), 0, None))
    return se


def lp(y: dict[str, float], shock: dict[str, float], kontroller: list[dict[str, float]],
       aylar_: list[str], h: int, n_lag: int, cagdas: list[dict[str, float]] | None = None,
       kir: bool = True) -> dict:
    """y_{t+h} on shock_t, lags of shock and y, extra lag controls, break dummies."""
    ix = {a: i for i, a in enumerate(aylar_)}
    rows_x, rows_y, used = [], [], []
    for a in aylar_:
        t = ix[a]
        if t + h >= len(aylar_) or t < n_lag:
            continue
        ah = aylar_[t + h]
        if ah not in y or a not in shock:
            continue
        rec = [1.0, shock[a]]
        ok = True
        for k in range(1, n_lag + 1):
            ak = aylar_[t - k]
            if ak not in shock or ak not in y:
                ok = False
                break
            rec.append(shock[ak])
            rec.append(y[ak])
        if not ok:
            continue
        for c in kontroller:
            for k in range(1, n_lag + 1):
                ak = aylar_[t - k]
                if ak not in c:
                    ok = False
                    break
                rec.append(c[ak])
            if not ok:
                break
        if not ok:
            continue
        for c in cagdas or []:
            if a not in c:
                ok = False
                break
            rec.append(c[a])
        if not ok:
            continue
        if kir:
            rec.extend(kirilma(a))
        rows_x.append(rec)
        rows_y.append(y[ah])
        used.append(a)
    if len(rows_y) < MIN_N:
        return {"n": len(rows_y), "karar": "belirlenemiyor", "neden": f"n<{MIN_N}"}
    X = np.asarray(rows_x, float)
    yy = np.asarray(rows_y, float)
    b, *_ = np.linalg.lstsq(X, yy, rcond=None)
    e = yy - X @ b
    se = nw_se(X, e, h + 1)
    beta, s = float(b[1]), float(se[1])
    if not np.isfinite(s) or s == 0:
        return {"n": int(len(yy)), "beta": beta, "karar": "belirlenemiyor", "neden": "standart hata yok"}
    lo, hi = beta - 1.96 * s, beta + 1.96 * s
    return {
        "n": int(len(yy)),
        "beta": round(beta, 6),
        "se": round(s, 6),
        "ci95": [round(lo, 6), round(hi, 6)],
        "ilk": used[0],
        "son": used[-1],
        "birim": "bağımlı bir kesir; şok 1 yüzde puan AOFM",
    }


def karar_isaret(sonuc: dict, beklenen: str) -> str:
    if sonuc.get("karar") == "belirlenemiyor" or "ci95" not in sonuc:
        return "belirlenemiyor"
    lo, hi = sonuc["ci95"]
    if beklenen == "negatif":
        if hi < 0:
            return "destekleniyor"
        if lo > 0:
            return "curuyor"
        return "belirlenemiyor"
    if lo > 0:
        return "destekleniyor"
    if hi < 0:
        return "curuyor"
    return "belirlenemiyor"


def granger(y: dict[str, float], x: dict[str, float], aylar_: list[str], n_lag: int) -> dict:
    """x, y'yi Granger öngörür mü. p eşiği 0,05 ön kayıtta."""
    ix = {a: i for i, a in enumerate(aylar_)}
    Y, Ylag, Xlag = [], [], []
    for a in aylar_:
        t = ix[a]
        if t < n_lag or a not in y:
            continue
        ok = True
        yl, xl = [], []
        for k in range(1, n_lag + 1):
            ak = aylar_[t - k]
            if ak not in y or ak not in x:
                ok = False
                break
            yl.append(y[ak])
            xl.append(x[ak])
        if not ok:
            continue
        Y.append(y[a])
        Ylag.append(yl)
        Xlag.append(xl)
    n = len(Y)
    if n < MIN_N:
        return {"n": n, "karar": "belirlenemiyor", "neden": f"n<{MIN_N}"}
    yv = np.asarray(Y, float)
    YL = np.asarray(Ylag, float)
    XL = np.asarray(Xlag, float)
    Xu = np.column_stack([np.ones(n), YL, XL])
    Xr = np.column_stack([np.ones(n), YL])
    bu, *_ = np.linalg.lstsq(Xu, yv, rcond=None)
    br, *_ = np.linalg.lstsq(Xr, yv, rcond=None)
    ssu = float(np.sum((yv - Xu @ bu) ** 2))
    ssr = float(np.sum((yv - Xr @ br) ** 2))
    q = n_lag
    k = Xu.shape[1]
    if ssu <= 0 or n <= k:
        return {"n": n, "karar": "belirlenemiyor", "neden": "F paydası yok"}
    F = ((ssr - ssu) / q) / (ssu / (n - k))
    # F sağ kuyruk, düzenli tamamlanmamış beta ile yaklaşık p (SciPy yoksa normal-olmayan):
    # Wilson-Hilferty olmadan, kaba: p'yi F dağılımından numpy ile sayısal integral.
    p = f_sf(F, q, n - k)
    return {"n": n, "F": round(float(F), 4), "p": round(float(p), 4), "anlamli_005": bool(p < 0.05)}


def f_sf(F: float, d1: int, d2: int) -> float:
    """Sağ kuyruk. Beta düzenli tamamlanmamış fonksiyon, devamlı kesir."""
    if F <= 0 or not np.isfinite(F):
        return 1.0
    x = d1 * F / (d1 * F + d2)
    # P(Beta > x) düzenlileştirilmiş = 1 - I_x(d1/2, d2/2)
    return 1.0 - betainc(d1 / 2, d2 / 2, x)


def betainc(a: float, b: float, x: float) -> float:
    """Düzenli tamamlanmamış beta, sayısal. a,b yarı tamsayı olabilir."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    # Lentz continued fraction (Numerical Recipes, betacf) + log beta
    from math import lgamma, exp, log
    def cont():
        MAX = 200
        EPS = 3e-12
        qab = a + b
        qap = a + 1
        qam = a - 1
        c = 1.0
        d = 1.0 - qab * x / qap
        if abs(d) < 1e-30:
            d = 1e-30
        d = 1 / d
        h = d
        for m in range(1, MAX + 1):
            m2 = 2 * m
            aa = m * (b - m) * x / ((qam + m2) * (a + m2))
            d = 1 + aa * d
            if abs(d) < 1e-30:
                d = 1e-30
            c = 1 + aa / c
            if abs(c) < 1e-30:
                c = 1e-30
            d = 1 / d
            h *= d * c
            aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
            d = 1 + aa * d
            if abs(d) < 1e-30:
                d = 1e-30
            c = 1 + aa / c
            if abs(c) < 1e-30:
                c = 1e-30
            d = 1 / d
            delta = d * c
            h *= delta
            if abs(delta - 1) < EPS:
                break
        return h
    front = exp(a * log(x) + b * log(1 - x) - log(a) - lgamma(a) - lgamma(b) + lgamma(a + b))
    if x < (a + 1) / (a + b + 2):
        return front * cont()
    return 1 - _betainc_cf(b, a, 1 - x)


def _betainc_cf(a: float, b: float, x: float) -> float:
    from math import lgamma, exp, log
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    MAX = 200
    EPS = 3e-12
    qab = a + b
    qap = a + 1
    qam = a - 1
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < 1e-30:
        d = 1e-30
    d = 1 / d
    h = d
    for m in range(1, MAX + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < EPS:
            break
    front = exp(a * log(x) + b * log(1 - x) - log(a) - lgamma(a) - lgamma(b) + lgamma(a + b))
    return front * h


def ols_kontrol(y: dict, xler: list[dict], aylar_: list[str], bant: int = 4) -> dict:
    rows_x, rows_y = [], []
    for a in aylar_:
        if a not in y:
            continue
        rec = [1.0]
        ok = all(a in x for x in xler)
        if not ok:
            continue
        for x in xler:
            rec.append(x[a])
        rows_x.append(rec)
        rows_y.append(y[a])
    if len(rows_y) < MIN_N:
        return {"n": len(rows_y), "karar": "belirlenemiyor", "neden": f"n<{MIN_N}"}
    X = np.asarray(rows_x, float)
    yy = np.asarray(rows_y, float)
    # sabit varyanslı sütun at
    keep = [0]
    for j in range(1, X.shape[1]):
        if np.nanstd(X[:, j]) > 0:
            keep.append(j)
    X = X[:, keep]
    b, *_ = np.linalg.lstsq(X, yy, rcond=None)
    e = yy - X @ b
    se = nw_se(X, e, bant)
    beta, s = float(b[1]), float(se[1])
    lo, hi = beta - 1.96 * s, beta + 1.96 * s
    return {"n": int(len(yy)), "beta": round(beta, 6), "se": round(s, 6),
            "ci95": [round(lo, 6), round(hi, 6)], "r2": round(float(1 - np.var(e) / np.var(yy)), 4)}


def main() -> None:
    end = "16-10-2026"
    start = "01-01-2013"
    aylik_seri = [
        "TP.APIFON4", "TP.TUKFIY2025.GENEL", "TP.DK.USD.A.YTL",
        "TP.HPBITABLO6.20", "TP.HPBITABLO6.3", "TP.HPBITABLO6.11", "TP.HPBITABLO6.2", "TP.HPBITABLO6.1",
        "TP.HPBITABLO2.3", "TP.HPBITABLO2.6", "TP.HPBITABLO2.10", "TP.HPBITABLO5.1",
        "TP.KFE.TR", "TP.PKAUO.S05.C.U", "TP.AB.TOPLAM", "TP.KKM.K1", "TP.KKM.K4",
    ]
    agg_a = ["avg", "last", "last", "last", "last", "last", "last", "last", "last", "last", "last", "last", "last", "avg", "last", "last", "last"]
    ham_a, meta_a = fetch(aylik_seri, agg_a, start, end, "5")
    ceyrek_seri = [
        "TP.GSYIH20.BY.B1GQ", "TP.FINHESTNKS13.ZP34", "TP.FINHESTNKS11.ZP34",
        "TP.FINHESTNKS62011.ZP34", "TP.FINHESTNKS62014.ZP34", "TP.FINHESTNKS14.ZP34",
    ]
    ham_c, meta_c = fetch(ceyrek_seri, ["sum"] + ["last"] * 5, start, end, "6")

    def M(kod):
        return ham_a.get(kod, {})

    cpi = M("TP.TUKFIY2025.GENEL")
    aofm = M("TP.APIFON4")
    usd = M("TP.DK.USD.A.YTL")
    izgara = aylar(list(cpi))
    di = diff(aofm, izgara)
    dkur = dlog(usd, izgara)
    enf = yoy(cpi, izgara)

    sektor = {
        "ticari": "TP.HPBITABLO6.20",
        "ihtiyac": "TP.HPBITABLO6.11",
        "konut": "TP.HPBITABLO6.3",
    }
    greel = {k: reel(M(s), cpi, izgara) for k, s in sektor.items()}
    gtoplam = reel(M("TP.HPBITABLO6.1"), cpi, izgara)
    gkfe = yoy(M("TP.KFE.TR"), izgara)

    h1 = {}
    for ad, g in greel.items():
        h1[ad] = {}
        for h in H1_RAPOR:
            for lag, et in ((LAG, "lag3"), (LAG_DUYAR, "lag6")):
                r = lp(g, di, [dkur, enf], izgara, h, lag)
                r["isaret_karari"] = karar_isaret(r, "negatif")
                h1[ad][f"h{h}_{et}"] = r
        b3 = h1[ad]["h9_lag3"]
        b6 = h1[ad]["h9_lag6"]
        is3 = b3.get("isaret_karari", "belirlenemiyor")
        s3, s6 = b3.get("beta"), b6.get("beta")
        if is3 in ("destekleniyor", "curuyor") and s3 is not None and s6 is not None and (s3 > 0) != (s6 > 0):
            h1[ad]["sektor_karar"] = "belirlenemiyor"
            h1[ad]["neden"] = "gecikme 6 birincil katsayının işaretini çeviriyor"
        else:
            h1[ad]["sektor_karar"] = is3
        # kuklasız duyarlılık, karar değil
        # kırılmayı kapatmak için lp kopyası: kirilma fonksiyonunu geçici sıfırlamak yerine ayrı çağrı yazılmadı;
        # aşağıda kuklasız yeniden hesap.
    h1_kuklasiz = {}
    for ad, g in greel.items():
        r = lp(g, di, [dkur, enf], izgara, H1_H, LAG, kir=False)
        r["isaret_karari"] = karar_isaret(r, "negatif")
        h1_kuklasiz[ad] = r

    destek_n = sum(1 for ad in greel if h1[ad]["sektor_karar"] == "destekleniyor")
    curu_n = sum(1 for ad in greel if h1[ad]["sektor_karar"] == "curuyor")
    if destek_n >= 2:
        h1_butun = "destekleniyor"
    elif curu_n >= 2 and destek_n == 0:
        h1_butun = "curuyor"
    else:
        h1_butun = "belirlenemiyor"

    # H3 Granger
    g_tl = yoy(M("TP.HPBITABLO2.3"), izgara)
    g_yp_tl = yoy(M("TP.HPBITABLO2.6"), izgara)
    g_yp_usd = yoy(M("TP.HPBITABLO2.10"), izgara)
    g_tic = yoy(M("TP.HPBITABLO6.20"), izgara)  # nominal, Granger için aynı birim: 12 ay nominal büyüme
    h3 = {}
    for ad, gdep in (("tl", g_tl), ("yp_tl_karsiligi", g_yp_tl), ("yp_usd", g_yp_usd)):
        ileri = granger(gdep, g_tic, izgara, LAG)
        geri = granger(g_tic, gdep, izgara, LAG)
        if ileri.get("anlamli_005") and not geri.get("anlamli_005"):
            karar = "sinirli"
        elif ileri.get("anlamli_005") and geri.get("anlamli_005"):
            karar = "belirlenemiyor"
        elif (not ileri.get("anlamli_005")) and geri.get("anlamli_005"):
            karar = "curuyor"
        else:
            karar = "belirlenemiyor"
        if ileri.get("karar") == "belirlenemiyor" or geri.get("karar") == "belirlenemiyor":
            karar = "belirlenemiyor"
        h3[ad] = {"kredi_mevduat": ileri, "mevduat_kredi": geri, "karar": karar,
                  "not": "Banka bilançosu yok. destekleniyor etiketi verilmez."}

    # H4
    pka = M("TP.PKAUO.S05.C.U")
    # beklenen 12 ay değer kaybı: anket kuru / spot - 1
    bek_kur = {}
    for a in izgara:
        if a in pka and a in usd and usd[a]:
            bek_kur[a] = pka[a] / usd[a] - 1
    parite = M("TP.HPBITABLO5.1")
    # parite serisi zaten bir değişim olabilir; düzey farkı alınmaz
    h4_cikti = parite
    h4_kontolsuz = ols_kontrol(h4_cikti, [g_tic], izgara)
    h4_kontrollu = ols_kontrol(h4_cikti, [g_tic, dkur, bek_kur], izgara)
    if "ci95" not in h4_kontrollu:
        h4_karar = "belirlenemiyor"
    else:
        h4_karar = karar_isaret(h4_kontrollu, "pozitif")
        if h4_karar == "curuyor":
            pass
        # çürüyor: bant sıfırın altında veya (kural) sıfırı içeriyorsa da H4 "zayıflar" = curuyor
        # karar_isaret sıfırı içerirse belirlenemiyor döner. Ön kayıt: bant sıfırı içeriyorsa çürüyor.
        if h4_karar == "belirlenemiyor" and h4_kontrollu.get("n", 0) >= MIN_N:
            h4_karar = "curuyor"
    # TL payı, karar değil
    pay = {}
    tl, yp = M("TP.HPBITABLO2.3"), M("TP.HPBITABLO2.6")
    for a in izgara:
        if a in tl and a in yp and (tl[a] + yp[a]) != 0:
            pay[a] = yp[a] / (tl[a] + yp[a])
    dpay = diff(pay, izgara)
    h4_pay = ols_kontrol(dpay, [g_tic, dkur, bek_kur], izgara)

    # H5
    h5 = lp(gtoplam, gkfe, [di], izgara, H5_H, LAG, cagdas=[di])
    # lp kontrolleri 1..lag gecikme alır; di çağdaş değil. Ön kayıt çağdaş AOFM'yi de ister.
    # Çağdaş şoku ikinci bir regresyonla, gkfe ile birlikte ols'ta kurmak ön kayda daha uygun.
    h5_ols = ols_kontrol(gtoplam, [gkfe, di], izgara)
    # ufuk h=3 için lp, kontrol listesine di'nin gecikmeleri girer; çağdaş di ayrıca X'e konmaz.
    # Ön kaydı karşılamak için lp'yi gkfe şokuyla ve di gecikmeleriyle çalıştırdık.
    h5_karar = karar_isaret(h5, "pozitif")
    # korelasyon gecikmesi -6..6
    ortak = hizala([gkfe, gtoplam])
    corr = {}
    gv = np.array([gkfe[a] for a in ortak])
    cv = np.array([gtoplam[a] for a in ortak])
    for k in range(-6, 7):
        if k < 0:
            a1, a2 = gv[-k:], cv[:k]
        elif k > 0:
            a1, a2 = gv[:-k], cv[k:]
        else:
            a1, a2 = gv, cv
        if len(a1) > 12 and np.std(a1) > 0 and np.std(a2) > 0:
            corr[str(k)] = round(float(np.corrcoef(a1, a2)[0, 1]), 4)
    lag_max = max(corr, key=lambda z: abs(corr[z])) if corr else None

    # H2 çeyreklik — özdeşlik ve akım
    gsyh = ham_c.get("TP.GSYIH20.BY.B1GQ", {})
    f4_nfc = ham_c.get("TP.FINHESTNKS11.ZP34", {})
    f4_gov = ham_c.get("TP.FINHESTNKS13.ZP34", {})
    akim_nfc = ham_c.get("TP.FINHESTNKS62011.ZP34", {})
    akim_h = ham_c.get("TP.FINHESTNKS62014.ZP34", {})
    # BDDK çeyrek sonu: aylık seriden Mar/Haz/Eyl/Ara
    def ceyrek_son(seri: dict[str, float]) -> dict[str, float]:
        out = {}
        for a, v in seri.items():
            if len(a) == 7 and a[5:] in ("03", "06", "09", "12"):
                y, m = a.split("-")
                q = {"03": "Q1", "06": "Q2", "09": "Q3", "12": "Q4"}[m]
                out[f"{y}-{q}"] = v
        return out

    def oran(stok_q: dict[str, float]) -> dict[str, float]:
        qs = sorted(gsyh)
        ix = {q: i for i, q in enumerate(qs)}
        out = {}
        for q, s in stok_q.items():
            if q not in ix or ix[q] < 3:
                continue
            i = ix[q]
            pencere = qs[i - 3:i + 1]
            if any(g not in gsyh or not gsyh[g] for g in pencere):
                continue
            gdp = sum(gsyh[g] for g in pencere)
            # BDDK bin TL, GSYH bin TL mi? EVDS GSYH çoğu bin TL. Birim JSON'da şüphe olarak yazılır.
            if gdp:
                out[q] = s / gdp
        return out

    h2 = {"nedensel": "belirlenemiyor", "neden": "Aynı stokun büyümesi özdeşliktir; ayrı akımla sınama aşağıda."}
    # akım varsa: delta oran on akim/gdp
    bddk_tic_q = ceyrek_son(M("TP.HPBITABLO6.20"))
    bddk_kon_q = ceyrek_son(M("TP.HPBITABLO6.3"))
    bddk_iht_q = ceyrek_son(M("TP.HPBITABLO6.11"))
    oranlar = {"ticari": oran(bddk_tic_q), "konut": oran(bddk_kon_q), "ihtiyac": oran(bddk_iht_q)}
    # birim kontrolü: medyan oran makul mü (0 ile 5 arası borç/GSYH)
    birim_not = {}
    for ad, o in oranlar.items():
        if o:
            med = float(np.median(list(o.values())))
            birim_not[ad] = {"medyan_oran": round(med, 4), "n": len(o),
                             "uyari": "Medyan 0,05–5 dışında. Birim (bin TL / bin TL) tutmayabilir; oran karar sayısı değildir." if not (0.05 <= med <= 5) else "Medyan borç/GSYH aralığında."}

    def delta(seri: dict[str, float]) -> dict[str, float]:
        ks = sorted(seri)
        return {ks[i]: seri[ks[i]] - seri[ks[i - 1]] for i in range(1, len(ks)) if ks[i][:4] >= "2014"}

    # işlem akımı / GSYH
    h2_akim = {}
    if akim_nfc:
        qs = sorted(set(akim_nfc) & set(gsyh))
        akim_oran = {q: akim_nfc[q] / gsyh[q] for q in qs if gsyh[q]}
        d_oran = delta(oranlar["ticari"])
        # GSYH büyümesi
        g_gdp = {}
        qss = sorted(gsyh)
        for i in range(4, len(qss)):
            g_gdp[qss[i]] = gsyh[qss[i]] / gsyh[qss[i - 4]] - 1
        # çeyrekte n<36 olabilir. MIN_N aylık içindi. Çeyrek için ön kayıt 36 demişti; çeyrekte 36 yıl eder.
        # Ön kayıt "gözlem 36'nın altı belirlenemiyor" dedi, frekans ayrımı yok. Çeyrek H2 bu yüzden büyük olasılıkla n<36.
        r = ols_kontrol(d_oran, [akim_oran, g_gdp], sorted(set(d_oran) | set(akim_oran)), bant=2)
        h2_akim = r
        if r.get("n", 0) < MIN_N:
            h2["nedensel"] = "belirlenemiyor"
            h2["neden"] = f"Çeyreklik akım regresyonu n={r.get('n')}; ön kayıt eşiği {MIN_N}."
        else:
            h2["nedensel"] = karar_isaret(r, "pozitif")
    else:
        h2["neden"] = "Firma işlem akımı serisi gelmedi."

    # stok-akış: BDDK ticari çeyrek farkı vs F.4 stok farkı vs işlem akımı
    stok_akis = {}
    d_bddk = delta(bddk_tic_q)
    d_f4 = delta(f4_nfc)
    ortak_q = sorted(set(d_bddk) & set(d_f4) & set(akim_nfc))
    if ortak_q:
        b = np.array([d_bddk[q] for q in ortak_q])
        f = np.array([d_f4[q] for q in ortak_q])
        a = np.array([akim_nfc[q] for q in ortak_q])
        # Birimleri yaz: BDDK bin TL, finansal hesap bin TL varsayımı doğrulanmadan oran.
        stok_akis = {
            "donem": [ortak_q[0], ortak_q[-1]],
            "n": len(ortak_q),
            "bddk_fark_medyan": round(float(np.median(b)), 1),
            "f4_fark_medyan": round(float(np.median(f)), 1),
            "akim_medyan": round(float(np.median(a)), 1),
            "medyan_bddk_bolu_f4": round(float(np.median(b / f)), 4) if np.all(f != 0) else None,
            "medyan_akim_bolu_f4fark": round(float(np.median(a / f)), 4) if np.all(f != 0) else None,
            "not": "Üçü aynı nesne değil. BDDK banka kredisi; F.4 tüm borç verenler, konsolide olmayan. Fark kapatılmaz.",
        }

    # H6 — tebliğ bu betikte çekilmedi. Seri başlangıcı tarih sayılmaz.
    kkm = M("TP.KKM.K1")
    h6 = {
        "karar": "belirlenemiyor",
        "neden": "KKM tebliğ metni bu turda indirilmedi. Seri başlangıcı ilan tarihi sayılmaz.",
        "kkm_k1_ilk_ay": min(kkm) if kkm else None,
        "kkm_k1_n": len(kkm),
    }

    # H7
    rezerv = M("TP.AB.TOPLAM")
    h7 = {
        "lcr": {"esik": "asgari %100", "olcum": None, "neden": "EVDS katalog taramasında LCR/LKO serisi bulunamadı."},
        "kv_dis_borc_rezerv": {"esik": "analitik: kısa vadeli dış borç / brüt rezerv > 1", "olcum": None, "neden": "Kısa vadeli dış borç serisi bu çekimde yok."},
        "yp_pozisyon": {"esik": "kullanılmadı", "neden": "Yönetmelik maddesi dosyaya inmedi. %20 yazılmadı."},
        "net_rezerv_swap": {"esik": "negatif ise sorun", "olcum": None, "neden": "Swap stoku serisi yok. Brüt rezervden net rezerv türetilmedi."},
        "brut_rezerv_milyon_usd": {"seri": "TP.AB.TOPLAM", "son": ({"ay": max(rezerv), "deger": rezerv[max(rezerv)]} if rezerv else None)},
        "karar": "belirlenemiyor",
    }

    # rakipler
    rakipler = {
        "kuresel": {"karar": "belirlenemiyor", "neden": "VIX, EMBI veya Fed fonlama serisi izin verilen kaynakta çekilmedi."},
        "kur_soku": {"kuklali_h1": {ad: h1[ad]["h9_lag3"] for ad in greel},
                     "kuklasiz_h1_h9": h1_kuklasiz,
                     "not": "Karar kuklalı belirtimdir. Kuklasız sütun rakibin ayırt ediciliğini gösterir."},
        "maliye": {"nesne": "TP.FINHESTNKS13.ZP34 genel yönetim F.4, Hazine iç borç stoku değil",
                   "var": bool(f4_gov), "karar": "belirlenemiyor",
                   "neden": "Özel kredi büyümesini açıklayan ayrı bir maliye regresyonu, nesne Hazine stoku olmadığı için karar sayılmadı."},
        "reel_gelir": {"karar": "belirlenemiyor", "neden": "Resmî zincirlenmiş hacim GSYH bu çekimde yok. Vekil kurulmadı."},
    }

    # kapsama
    kapsam = {}
    for kod, d in {**{k: M(k) for k in aylik_seri}, **ham_c}.items():
        if d:
            kapsam[kod] = {"ilk": min(d), "son": max(d), "n": len(d)}
        else:
            kapsam[kod] = None

    sonuc = {
        "cekilme": CEKILME,
        "onkait": "ZINCIR_ONKAYIT.md",
        "merkezi_iddia_20_30": "Bu tur türetilmedi. Kredi ikame bandı ölçülmedi.",
        "sok": "TP.APIFON4 AOFM, yüzde puan farkı. Bir haftalık repo ihale faizi değil.",
        "meta_aylik": meta_a,
        "meta_ceyrek": meta_c,
        "kapsam": kapsam,
        "H1": {"butun": h1_butun, "sektor": h1, "kuklasiz_h9": h1_kuklasiz},
        "H2": {"karar": h2["nedensel"], "neden": h2["neden"], "akim_regresyon": h2_akim, "birim_notu": birim_not,
               "akim_nfc_var": bool(akim_nfc), "akim_hane_var": bool(akim_h), "kamu_f4_var": bool(f4_gov)},
        "H3": h3,
        "H4": {"karar": h4_karar, "kontolsuz": h4_kontolsuz, "kontrollu": h4_kontrollu, "tl_pay_kontrollu_karar_degil": h4_pay,
               "cikti": "TP.HPBITABLO5.1"},
        "H5": {"karar": h5_karar, "lp_h3": h5, "cagdas_ols_karar_degil": h5_ols, "korelasyon_gecikme": corr, "en_buyuk_mutlak": lag_max},
        "H6": h6,
        "H7": h7,
        "rakipler": rakipler,
        "stok_akis": stok_akis,
        "zayiflik": {
            "banka_bilancosu": "kapanmadi",
            "kredi_gelir_karisikligi": "kapanmadi; H2 özdeşlik diye ayrıldı, nedensel etiket verilmedi",
            "birim": birim_not,
            "yil_etiketi": "bu turda iki yıl etiketi düzeltilmedi",
            "band_20_30": "kapanmadi; bu turda türetilmedi",
        },
    }
    (KOK / "zincir_h1h7_sonuc.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # ham, aylık, seyrek
    with (KOK / "zincir_h1h7_ham.csv").open("w", encoding="utf-8-sig") as fh:
        fh.write("seri,donem,deger\n")
        for kod, d in ham_a.items():
            for t, v in sorted(d.items()):
                fh.write(f"{kod},{t},{v}\n")
        for kod, d in ham_c.items():
            for t, v in sorted(d.items()):
                fh.write(f"{kod},{t},{v}\n")
    print("H1", h1_butun, {ad: h1[ad]["sektor_karar"] for ad in greel})
    print("H2", h2["nedensel"], h2["neden"])
    print("H3", {k: v["karar"] for k, v in h3.items()})
    print("H4", h4_karar, h4_kontrollu)
    print("H5", h5_karar, h5.get("beta"), h5.get("ci95"), "lag", lag_max)
    print("H6", h6["karar"])
    print("H7", h7["karar"])
    print("stok_akis", stok_akis)
    print("birim", birim_not)
    print("kapsam AOFM", kapsam.get("TP.APIFON4"), "CPI", kapsam.get("TP.TUKFIY2025.GENEL"), "ticari", kapsam.get("TP.HPBITABLO6.20"))


if __name__ == "__main__":
    main()
