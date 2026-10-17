"""Beş adımın enflasyon köprüsü.

Kurallar hesap öncesi para_arzi/ENFLASYON_YANLISLAMA.md dosyasında kilitlendi.
Esneklik yıl sonu EVDS farklarının OLS'idir. Katsayı uydurulmaz.
Köprü adım denklemlerine yazılmaz.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np

KOK = Path(__file__).resolve().parents[1]
BUR = Path(__file__).resolve().parent
KRITER = BUR / "ENFLASYON_YANLISLAMA.md"
HAM = BUR / "enflasyon_ham.json"
CIKTI = BUR / "enflasyon_etki.json"
RAPOR = BUR / "ENFLASYON_ETKI.md"

BASE = "https://evds3.tcmb.gov.tr/igmevdsms-dis"
S_TUFE = "TP.FG.J0"
S_M1 = "TP.HPBITABLO1.2"
S_M2 = "TP.HPBITABLO1.11"
S_USD = "TP.DK.USD.A.YTL"
S_YP_USD = "TP.HPBITABLO2.11"
S_YP_TL = "TP.HPBITABLO2.7"
S_KREDI = "TP.KREHACBS.A1"
S_GSYH = "TP.GSYIH20.CY.B1GQ"

YIL0, YIL1 = 2010, 2025  # son tam yıl sonu 2025; 2026 Aralık yok
MIN_N = 8
Z = 1.96

GERCEK_YP = 6639.4
I_YIL = {"dusuk": 1207.6, "orta": 2415.6, "yuksek": 4830.8}
KAPSAM = {"dusuk": 0.20, "orta": 0.50, "yuksek": 1.00}
GSYH_2025 = 63240.5
R_SABIT = 53.1925
PI_TABAN = 29.73
KIRA_W = 0.068028
KIRA_ALT = (4783.0, 30291.0)
KIRA_UST = (10291.0, 24783.0)
GECIS = (0.26, 0.38, 0.40)
CULE = (
    "Modelde enflasyon dışsaldır; bu hesap model dışı bir köprüdür, "
    "sonuç modele geri beslenmez"
)


def _sha(yol: Path) -> str:
    return hashlib.sha256(yol.read_bytes()).hexdigest()


def _get(url: str, body: dict | None = None) -> dict:
    import urllib.request

    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        method="POST" if body is not None else "GET",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8-sig"))


def _cek(series: list[str], freq: str, start: str, end: str, agg: str = "last") -> dict[str, list[tuple[str, float]]]:
    body = {
        "type": "json",
        "series": "-".join(series),
        "aggregationTypes": "-".join(agg for _ in series),
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
    data = _get(f"{BASE}/fe", body)
    out: dict[str, list[tuple[str, float]]] = {s: [] for s in series}
    for it in data.get("items") or []:
        t = str(it.get("Tarih"))
        for s in series:
            v = it.get(s.replace(".", "_"))
            if v not in (None, ""):
                out[s].append((t, float(str(v).replace(",", ""))))
    return out


def _yil_sonu_ay(rows: list[tuple[str, float]]) -> dict[str, float]:
    return {t[:4]: v for t, v in rows if len(t) == 7 and t.endswith("-12")}


def _gsyh_yil(rows: list[tuple[str, float]]) -> dict[str, float]:
    kova: dict[str, dict[str, float]] = {}
    for t, v in rows:
        if "-Q" not in t:
            continue
        yil, q = t.split("-Q")
        kova.setdefault(yil, {})[q] = v
    return {y: sum(qs[k] for k in "1234") for y, qs in kova.items() if all(k in qs for k in "1234")}


def cek_ham() -> dict:
    ay = _cek([S_TUFE, S_USD, S_KREDI], "5", "01-01-2005", "17-10-2026")
    stok = _cek([S_M1, S_M2, S_YP_USD, S_YP_TL], "5", "01-01-2005", "17-10-2026")
    gsyh = _cek([S_GSYH], "6", "01-01-1998", "17-10-2026")
    tufe = _yil_sonu_ay(ay[S_TUFE])
    m1 = _yil_sonu_ay(stok[S_M1])
    m2 = _yil_sonu_ay(stok[S_M2])
    usd = _yil_sonu_ay(ay[S_USD])
    kredi = _yil_sonu_ay(ay[S_KREDI])
    g = _gsyh_yil(gsyh[S_GSYH])
    yillar = sorted(set(tufe) & set(m1) & set(m2) & set(usd) & set(kredi) & set(g))
    yil_sonu = {
        y: {"tufe": tufe[y], "m1": m1[y], "m2": m2[y], "usd": usd[y], "kredi": kredi[y], "gsyh": g[y]}
        for y in yillar
    }
    yp_usd = _yil_sonu_ay(stok[S_YP_USD])
    mart = next((v for t, v in stok[S_YP_TL] if t == "2026-03"), None)
    if mart is None:
        raise RuntimeError("2026-03 gerçek kişi YP yok")
    son_kredi = max(ay[S_KREDI], key=lambda tv: tv[0])
    return {
        "seri": {
            "tufe": S_TUFE,
            "m1": S_M1,
            "m2": S_M2,
            "usd": S_USD,
            "yp_usd": S_YP_USD,
            "yp_tl": S_YP_TL,
            "kredi": S_KREDI,
            "gsyh": S_GSYH,
        },
        "yil_sonu": yil_sonu,
        "yp_usd_yil_sonu": yp_usd,
        "yp_tl_2026_03_bin": mart,
        "kredi_son": {"tarih": son_kredi[0], "ham": son_kredi[1]},
        "pencere_hedef": [YIL0, YIL1],
        "not": "Yıl sonu Aralık. 2026 Aralık yok. Tanımlar eklenmedi.",
    }


def _fark(ham: dict, anahtar: list[str]) -> tuple[list[int], dict[str, list[float]]]:
    ys = ham["yil_sonu"]
    yillar: list[int] = []
    cols: dict[str, list[float]] = {k: [] for k in anahtar}
    for t in range(YIL0, YIL1 + 1):
        a, b = ys.get(str(t)), ys.get(str(t - 1))
        if a is None or b is None:
            continue
        if any(k not in a or k not in b or a[k] <= 0 or b[k] <= 0 for k in anahtar):
            continue
        yillar.append(t)
        for k in anahtar:
            cols[k].append(math.log(a[k]) - math.log(b[k]))
    return yillar, cols


def ols(y: list[float], xs: list[list[float]]) -> dict:
    yv = np.asarray(y, dtype=float)
    X = np.column_stack([np.ones(len(yv))] + [np.asarray(x, dtype=float) for x in xs])
    n, k = X.shape
    bos = {"durum": "tahmin_edilemedi", "n": int(n), "k": int(k)}
    if n < MIN_N or n <= k:
        return bos
    try:
        beta, *_ = np.linalg.lstsq(X, yv, rcond=None)
        cov = float(np.sum((yv - X @ beta) ** 2) / (n - k)) * np.linalg.inv(X.T @ X)
    except np.linalg.LinAlgError:
        return bos
    resid = yv - X @ beta
    se = np.sqrt(np.diag(cov))
    ss = float(np.sum((yv - yv.mean()) ** 2))
    r2 = None if ss == 0 else 1.0 - float(resid @ resid) / ss
    return {
        "durum": "olculdu",
        "n": int(n),
        "k": int(k),
        "beta": [float(v) for v in beta],
        "se": [float(v) for v in se],
        "cov": [[float(v) for v in row] for row in cov],
        "r2": None if r2 is None else float(r2),
    }


def _katsayi(beta: float, se: float) -> dict:
    lo, hi = beta - Z * se, beta + Z * se
    icerir = lo <= 0.0 <= hi
    return {
        "coef": beta,
        "se": se,
        "aralik": [lo, hi],
        "sifir_icerir": icerir,
        "nokta": 0.0 if icerir else beta,
        "etiket": "aday",
    }


def _sirala(a: float, b: float) -> list[float]:
    return [a, b] if a <= b else [b, a]


def gsyh_2025() -> float:
    import csv

    for x in csv.DictReader((KOK / "tavan_akis.csv").open(encoding="utf-8-sig")):
        if x["yil"] == "2025":
            return float(x["gsyh"])
    raise KeyError("tavan_akis 2025")


def _para_puan(model: dict, dlog_m1: float, dlog_r: float) -> dict:
    if model["durum"] != "olculdu":
        return {"durum": "tahmin_edilemedi", "nokta": None, "aralik": None, "merkez": None}
    b1, b2 = model["b1"], model["b2"]
    nokta = 100.0 * (b1["nokta"] * dlog_m1 + b2["nokta"] * dlog_r)
    w = np.array([0.0, dlog_m1, dlog_r])
    cov = np.asarray(model["cov"], dtype=float)
    se = float(np.sqrt(w @ cov @ w))
    merkez = 100.0 * (b1["coef"] * dlog_m1 + b2["coef"] * dlog_r)
    return {
        "durum": "olculdu",
        "dlog_m1": dlog_m1,
        "dlog_oran": dlog_r,
        "nokta": nokta,
        "merkez": merkez,
        "aralik": _sirala(merkez - 100.0 * Z * se, merkez + 100.0 * Z * se),
        "etiket": "aday",
    }


def _dlog_seviye(m1: float, m2: float, dm1: float, dm2: float) -> tuple[float, float]:
    if dm2 < dm1 - 1e-6 or m1 <= dm1 or m2 <= dm2:
        raise RuntimeError(f"para şoku stoğu aşıyor: dm1={dm1} dm2={dm2}")
    dlm1 = math.log(m1 - dm1) - math.log(m1)
    dlr = math.log((m2 - dm2) / (m1 - dm1)) - math.log(m2 / m1)
    return dlm1, dlr


def _dlog_aradan(m1: float, m2: float, dm1_a: float, dm2_a: float, dm1_b: float, dm2_b: float) -> tuple[float, float]:
    """A düzeyinden B düzeyine. dm, taban stoktan düşüştür."""
    a1, a2 = m1 - dm1_a, m2 - dm2_a
    b1, b2 = m1 - dm1_b, m2 - dm2_b
    if min(a1, a2, b1, b2) <= 0:
        raise RuntimeError("ara düzey eksi")
    return math.log(b1) - math.log(a1), math.log(b2 / b1) - math.log(a2 / a1)


def _m1_cift(carpan: float, dm2: float, vadesiz: float) -> tuple[float, float]:
    ust = min(carpan * GERCEK_YP, vadesiz, dm2)
    return 0.0, max(0.0, ust)


def _tek_puan(kat: dict, dlog: float) -> dict:
    if kat is None:
        return {"durum": "tahmin_edilemedi", "nokta": None, "aralik": None, "merkez": None}
    merkez = 100.0 * kat["coef"] * dlog
    yarim = 100.0 * Z * kat["se"] * abs(dlog)
    return {
        "durum": "olculdu",
        "dlog": dlog,
        "nokta": 100.0 * kat["nokta"] * dlog,
        "merkez": merkez,
        "aralik": _sirala(merkez - yarim, merkez + yarim),
        "etiket": "aday",
    }


def _topla(parcalar: list[dict], anahtar: str) -> dict:
    if any(p.get(anahtar) is None for p in parcalar):
        return {"nokta": None, "aralik": None}
    nokta = sum(p["nokta"] for p in parcalar)
    lo = sum(p["aralik"][0] for p in parcalar)
    hi = sum(p["aralik"][1] for p in parcalar)
    return {"nokta": nokta, "aralik": _sirala(lo, hi), "etiket": "aday", "not": "Uçların toplamı ortak aralık değildir."}


def hesap(ham: dict) -> dict:
    if not KRITER.exists():
        raise SystemExit("kriter dosyası yok")
    gsyh = gsyh_2025()
    if abs(gsyh - GSYH_2025) > 0.05:
        raise SystemExit(f"GSYH 2025 kilitli değil: {gsyh}")
    m2doc = json.loads((BUR / "m2_etki.json").read_text(encoding="utf-8"))
    milyon = m2doc["m2"]["milyar"]
    m1, m2 = float(milyon["m1"]), float(milyon["m2"])
    vadesiz = float(milyon["vadesiz_yp"])
    yp_stok = ham["yp_tl_2026_03_bin"] / 1e6
    if abs(yp_stok - GERCEK_YP) > 0.1:
        raise SystemExit(f"YP stok adresle örtüşmüyor: {yp_stok}")
    kredi_stok = ham["kredi_son"]["ham"] / 1e6

    y_para, c_para = _fark(ham, ["tufe", "m1", "m2"])
    dlog_r = [m2_ - m1_ for m1_, m2_ in zip(c_para["m1"], c_para["m2"])]
    para_ols = ols(c_para["tufe"], [c_para["m1"], dlog_r])
    para_model: dict = {"durum": para_ols["durum"], "yillar": y_para, "n": para_ols["n"]}
    if para_ols["durum"] == "olculdu":
        para_model["b1"] = _katsayi(para_ols["beta"][1], para_ols["se"][1])
        para_model["b2"] = _katsayi(para_ols["beta"][2], para_ols["se"][2])
        para_model["sabit"] = para_ols["beta"][0]
        para_model["r2"] = para_ols["r2"]
        para_model["cov"] = para_ols["cov"]
        para_model["denklem"] = "dlog TÜFE = a + b1 dlog M1 + b2 dlog(M2/M1)"
        para_model["dlog_m2_min"] = min(c_para["m2"])
        para_model["dlog_m2_max"] = max(c_para["m2"])

    y_kr, c_kr = _fark(ham, ["tufe", "kredi", "gsyh"])
    dlog_reel = [k - p for k, p in zip(c_kr["kredi"], c_kr["tufe"])]
    enf_ols = ols(c_kr["tufe"], [dlog_reel])
    buy_ols = ols(c_kr["gsyh"], [dlog_reel])
    kredi_model: dict = {"durum": enf_ols["durum"], "yillar": y_kr, "n": enf_ols["n"], "buyume_n": buy_ols["n"]}
    if enf_ols["durum"] == "olculdu":
        kredi_model["d"] = _katsayi(enf_ols["beta"][1], enf_ols["se"][1])
        kredi_model["r2"] = enf_ols["r2"]
    if buy_ols["durum"] == "olculdu":
        kredi_model["h"] = _katsayi(buy_ols["beta"][1], buy_ols["se"][1])
        kredi_model["buyume_r2"] = buy_ols["r2"]
        kredi_model["buyume_durum"] = "olculdu"
    else:
        kredi_model["buyume_durum"] = "tahmin_edilemedi"

    yp = ham["yp_usd_yil_sonu"]
    yp_yil = sorted(int(y) for y in yp)
    yp_fark = []
    for t in yp_yil:
        if str(t - 1) in yp and yp[str(t)] > 0 and yp[str(t - 1)] > 0 and str(t) in ham["yil_sonu"] and str(t - 1) in ham["yil_sonu"]:
            usd0 = ham["yil_sonu"][str(t - 1)]["usd"]
            usd1 = ham["yil_sonu"][str(t)]["usd"]
            if usd0 > 0 and usd1 > 0:
                yp_fark.append((t, math.log(usd1) - math.log(usd0), math.log(yp[str(t)]) - math.log(yp[str(t - 1)])))
    if len(yp_fark) < MIN_N:
        kur_model = {"durum": "tahmin_edilemedi", "n": len(yp_fark), "yillar": [t for t, *_ in yp_fark], "neden": "tek tanımda yıl sonu farkı 8'den az"}
    else:
        kur_ols = ols([a for _, a, _ in yp_fark], [[b for _, _, b in yp_fark]])
        kur_model = {"durum": kur_ols["durum"], "n": kur_ols["n"], "yillar": [t for t, *_ in yp_fark]}
        if kur_ols["durum"] == "olculdu":
            kur_model["beta"] = _katsayi(kur_ols["beta"][1], kur_ols["se"][1])
            kur_model["r2"] = kur_ols["r2"]

    def kur_puan_dlog(dlog: float) -> dict:
        if kur_model["durum"] != "olculdu":
            return {"durum": "tahmin_edilemedi", "dlog_yp": dlog, "alt_de": 0.0, "alt_puan": 0.0}
        kat = kur_model["beta"]
        de_nokta = kat["nokta"] * dlog
        de_merkez = kat["coef"] * dlog
        de_ar = _sirala((kat["coef"] - Z * kat["se"]) * dlog, (kat["coef"] + Z * kat["se"]) * dlog)

        def carp(de: float) -> dict:
            return {f"g{int(g * 100)}": 100.0 * de * g for g in GECIS}

        return {
            "durum": "olculdu",
            "dlog_yp": dlog,
            "de_nokta": de_nokta,
            "de_aralik": de_ar,
            "puan_nokta": carp(de_nokta),
            "puan_merkez": carp(de_merkez),
            "alt_de": 0.0,
            "alt_puan": 0.0,
            "etiket": "aday",
        }

    senaryolar = []
    for s in m2doc["senaryo"]:
        ad = s["ad"]
        theta, chi = float(s["theta"]), float(s["chi"])
        tepe, kalici = float(s["adim4_tepe"]), float(s["adim4_kalici"])
        dm1_tepe = _m1_cift(theta, tepe, vadesiz)
        dm1_kal = _m1_cift(chi * theta, kalici, vadesiz)
        para_tepe, para_geri, para_net = {}, {}, {}
        for adim, dm1 in (("alt", 0), ("ust", 1)):
            d1, d2 = dm1_tepe[0 if adim == "alt" else 1], tepe
            k1, k2 = dm1_kal[0 if adim == "alt" else 1], kalici
            para_tepe[adim] = _para_puan(para_model, *_dlog_seviye(m1, m2, d1, d2))
            para_geri[adim] = _para_puan(para_model, *_dlog_aradan(m1, m2, d1, d2, k1, k2))
            para_net[adim] = _para_puan(para_model, *_dlog_seviye(m1, m2, k1, k2))
            para_tepe[adim]["dm1"] = d1
            para_tepe[adim]["dm2"] = d2
            para_geri[adim]["dm1_bas"] = d1
            para_geri[adim]["dm2_bas"] = d2
            para_geri[adim]["dm1_son"] = k1
            para_geri[adim]["dm2_son"] = k2
        oran_tepe = theta * GERCEK_YP / yp_stok
        oran_kal = chi * theta * GERCEK_YP / yp_stok
        if oran_tepe >= 1 or oran_kal >= 1:
            raise RuntimeError("YP oranı 1'i aşıyor")
        log_tepe = 0.0 if oran_tepe == 0 else math.log(1.0 - oran_tepe)
        log_kal = 0.0 if oran_kal == 0 else math.log(1.0 - oran_kal)
        kur_tepe = kur_puan_dlog(log_tepe)
        kur_geri = kur_puan_dlog(log_kal - log_tepe)
        maliyet_1 = -100.0 * I_YIL[ad] / gsyh
        kira_lo = -100.0 * KIRA_W * KAPSAM[ad] * (KIRA_ALT[0] / KIRA_ALT[1])
        kira_hi = -100.0 * KIRA_W * KAPSAM[ad] * (KIRA_UST[0] / KIRA_UST[1])
        akim = {
            "tepe": float(s["ikinci_tur_tepe_yillik"]),
            "kalici": float(s["ikinci_tur_kalici_yillik"]),
        }
        kredi_puan = {}
        buyume_puan = {}
        for adim, ak in akim.items():
            if ak > kredi_stok:
                raise RuntimeError("kredi akışı stoktan büyük")
            dlog = 0.0 if ak == 0 else math.log(1.0 - ak / kredi_stok)
            kat_d = kredi_model.get("d")
            kat_h = kredi_model.get("h")
            kredi_puan[adim] = _tek_puan(kat_d, dlog) if kat_d else {"durum": "tahmin_edilemedi", "nokta": None, "aralik": None}
            buyume_puan[adim] = _tek_puan(kat_h, dlog) if kat_h else {"durum": "tahmin_edilemedi", "nokta": None, "aralik": None}
            kredi_puan[adim]["akim"] = ak
            kredi_puan[adim]["oran"] = 0.0 if kredi_stok == 0 else ak / kredi_stok

        def hucre(para: dict, kur: dict, mali: float, kredi: dict) -> dict:
            kur_nokta = 0.0 if kur["durum"] != "olculdu" else kur["puan_nokta"]["g26"]

            def bant(kredi_n: float) -> list[float]:
                vals = [
                    p + kur_nokta + m + kredi_n
                    for p in (para["alt"]["nokta"], para["ust"]["nokta"])
                    for m in (0.0, mali)
                ]
                return [min(vals), max(vals)]

            return {
                "para_alt": para["alt"]["nokta"],
                "para_ust": para["ust"]["nokta"],
                "para_alt_aralik": para["alt"]["aralik"],
                "para_ust_aralik": para["ust"]["aralik"],
                "kur": kur_nokta,
                "kur_durum": kur["durum"],
                "maliyet": [0.0, mali],
                "kredi": kredi["nokta"],
                "kredi_aralik": kredi["aralik"],
                "adim45": 0.0,
                "toplam": bant(kredi["nokta"]),
                "toplam_kredisiz": bant(0.0),
            }

        bos_kredi = {"nokta": 0.0, "aralik": [0.0, 0.0]}
        bos_para = {
            "alt": {"nokta": 0.0, "aralik": [0.0, 0.0]},
            "ust": {"nokta": 0.0, "aralik": [0.0, 0.0]},
        }
        bos_kur = {"durum": "alt_sinir", "puan_nokta": {"g26": 0.0}}
        yil = {
            "2027": hucre(bos_para, bos_kur, 0.0, bos_kredi),
            "2028": hucre(bos_para, bos_kur, 0.0, bos_kredi),
            "2029": hucre(para_tepe, kur_tepe, maliyet_1, bos_kredi),
            "2030": hucre(bos_para, bos_kur, maliyet_1, kredi_puan["tepe"]),
            "2031": hucre(para_geri, kur_geri, maliyet_1, kredi_puan["kalici"]),
        }
        senaryolar.append({
            "ad": ad,
            "theta": theta,
            "chi": chi,
            "adim4_tepe": tepe,
            "adim4_kalici": kalici,
            "adim12_m2": float(s["adim12_m2"]),
            "ikinci_tur_tepe": akim["tepe"],
            "ikinci_tur_kalici": akim["kalici"],
            "dm1_tepe": list(dm1_tepe),
            "dm1_kalici": list(dm1_kal),
            "para_tepe": para_tepe,
            "para_geri": para_geri,
            "para_net": para_net,
            "kur_tepe": kur_tepe,
            "kur_geri": kur_geri,
            "maliyet": {"alfa0": 0.0, "alfa1": maliyet_1, "I": I_YIL[ad], "etiket": "aday"},
            "kira": {
                "kapsama": KAPSAM[ad],
                "puan": _sirala(kira_lo, kira_hi),
                "yil": None,
                "etiket": "aday",
            },
            "kredi": kredi_puan,
            "buyume": buyume_puan,
            "yil": yil,
            "hiz": {"tepe": -tepe / m2, "kalici": -kalici / m2, "fiyata_eklendi": False},
        })

    # Birleşik ayak, skor dışı, 2028, M1 payı ölçülmedi → dm1 = 0
    ayak = 13967.0
    birlesik = None
    if para_model["durum"] == "olculdu":
        birlesik = _para_puan(para_model, *_dlog_seviye(m1, m2, 0.0, ayak))
        birlesik["dm1"] = 0.0
        birlesik["dm2"] = ayak
        birlesik["yil"] = 2028
        birlesik["skora_girer"] = False
        birlesik["etiket"] = "aday"

    def sapma(dpi: float, I: float) -> dict:
        return {
            "delta_pi": dpi,
            "nominal_fazla_milyar": I * abs(dpi) / R_SABIT,
            "reel_oran": (abs(dpi) / 100.0) / (1.0 + PI_TABAN / 100.0),
        }

    tutarlilik = []
    for s in senaryolar:
        for yil, h in s["yil"].items():
            if yil not in ("2029", "2030", "2031"):
                continue
            for ad, bant in (("kredi_dahil", h["toplam"]), ("kredi_haric", h["toplam_kredisiz"])):
                dpi = min(bant)
                if dpi >= 0:
                    continue
                tutarlilik.append({"senaryo": s["ad"], "yil": int(yil), "kose": ad, **sapma(dpi, s["maliyet"]["I"])})

    doc = {
        "kriter_sha256": _sha(KRITER),
        "cumle": CULE,
        "dissallik": {
            "enflasyon": True,
            "faiz": True,
            "kur": True,
            "geri_besleme": False,
            "tek_yon_bant": "bes_yil_senaryo enflasyon model etkisi −7,62…0 varsayım; faiz ve döviz modellenmedi. Bu bant r_t, kur ve ihracı güncellemez.",
            "gsyh_pay": "gsyh_pay.py enflasyon senaryosunu yalnız GSYH paydasını büyütür. O payda I_t'ye girmez.",
        },
        "m1": m1,
        "m2": m2,
        "vadesiz_yp": vadesiz,
        "yp_stok_2026_03": yp_stok,
        "kredi_stok_milyar": kredi_stok,
        "kredi_stok_tarih": ham["kredi_son"]["tarih"],
        "gsyh_2025": gsyh,
        "para": {k: v for k, v in para_model.items() if k != "cov"} | {"cov": para_model.get("cov")},
        "kredi_model": kredi_model,
        "kur_model": kur_model,
        "senaryo": senaryolar,
        "birlesik_2028": birlesik,
        "tutarlilik": tutarlilik,
        "adim45": 0.0,
        "gecis": list(GECIS),
        "kira_agirlik": KIRA_W,
    }
    return _yuvarla(doc)


def _yuvarla(x, n=8):
    if isinstance(x, dict):
        return {k: _yuvarla(v, n) for k, v in x.items()}
    if isinstance(x, list):
        return [_yuvarla(v, n) for v in x]
    if isinstance(x, float):
        return round(x, n)
    return x


def _tr(x, n=2) -> str:
    if x is None:
        return "—"
    if abs(x) < 5 * 10 ** (-(n + 1)):
        x = 0.0
    s = f"{x:,.{n}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def _ar(p, n=2) -> str:
    if not p or p.get("aralik") is None:
        return "—"
    a, b = p["aralik"]
    return f"{_tr(a, n)} … {_tr(b, n)}"


def _halk(d: dict) -> str:
    orta = next(s for s in d["senaryo"] if s["ad"] == "orta")
    b2029 = sorted(abs(x) for x in orta["yil"]["2029"]["toplam_kredisiz"])
    mali = abs(orta["maliyet"]["alfa1"])
    if d["kur_model"]["durum"] != "olculdu":
        kur = "Kurun ne kadar oynayacağı bu seriyle ölçülememiştir. Skor, kurun 49,1274'te kalmasıdır."
    else:
        kur = "Kur kanalı bir eğim üretir. Skorun alt ucu, kurun yerinde kalmasıdır."
    return (
        "Model enflasyonu, faizi ve dolar kurunu kendisi üretmez; onları dışarıdan sabit alır. "
        "Buradaki hesap o sabitlere geri yazılmaz. "
        "Geçmişte yıl sonu M2 her yıl artmıştır. Eğim bu artışlardan gelir. Adımların M2'yi düşürmesi bu örneklemin dışındadır. "
        f"Denklem yine de uygulanırsa orta senaryoda 2029'da fiyat artışı {_tr(b2029[0])} ile {_tr(b2029[1])} puan daha yavaştır. "
        "Bu, stokun düştüğü yılın geçişidir; her yıl süren bir oran değildir. "
        "2031'de senetlerin bir kısmı mevduata dönünce bu puanın bir kısmı geri gelir. "
        f"Durdurulan faizin fiyata geçişi ayrıdır: ortada 0 ile {_tr(mali)} puan daha yavaş, 2029-2031 boyunca her yıl. "
        "Kredi daralmasının geçmişteki izi fiyatı yavaşlatmak yönünde çıkmamıştır; büyüme puanının noktası 0'dır. "
        "Kira ayrıdır; hangi yıla denk geleceği repoda yazılı değildir. "
        f"{kur}"
    )


def rapor(d: dict) -> str:
    p = d["para"]
    k = d["kredi_model"]
    kur = d["kur_model"]

    def kat(blok, ad):
        if blok.get("durum") != "olculdu" or ad not in blok:
            return "tahmin edilemedi"
        c = blok[ad]
        return (
            f"{_tr(c['coef'], 3)} (SE {_tr(c['se'], 3)}; aralık {_tr(c['aralik'][0], 3)} … {_tr(c['aralik'][1], 3)}; "
            f"nokta {_tr(c['nokta'], 3)})"
        )

    def bant_hucre(h, anahtar):
        lo, hi = h[anahtar]
        return f"{_tr(lo)} … {_tr(hi)}"

    yil_haric, yil_dahil = [], []
    for yil in ("2027", "2028", "2029", "2030", "2031"):
        haric = [bant_hucre(s["yil"][yil], "toplam_kredisiz") for s in d["senaryo"]]
        dahil = [bant_hucre(s["yil"][yil], "toplam") for s in d["senaryo"]]
        yil_haric.append(f"| {yil} | " + " | ".join(haric) + " |")
        yil_dahil.append(f"| {yil} | " + " | ".join(dahil) + " |")

    detay = []
    for s in d["senaryo"]:
        detay.append(
            f"| {s['ad']} | {_tr(s['para_tepe']['alt']['nokta'])} … {_tr(s['para_tepe']['ust']['nokta'])} | "
            f"{_tr(s['para_geri']['alt']['nokta'])} … {_tr(s['para_geri']['ust']['nokta'])} | "
            f"{_tr(s['maliyet']['alfa0'])} … {_tr(s['maliyet']['alfa1'])} | "
            f"{_tr(s['kredi']['tepe']['nokta'])} | {_tr(s['kredi']['kalici']['nokta'])} | "
            f"{_tr(s['kira']['puan'][0])} … {_tr(s['kira']['puan'][1])} | "
            f"{_tr(s['buyume']['tepe']['nokta'])} | {_tr(s['buyume']['kalici']['nokta'])} |"
        )

    sapma = []
    for t in d["tutarlilik"]:
        if t["kose"] != "kredi_dahil":
            continue
        sapma.append(
            f"| {t['senaryo']} | {t['yil']} | {_tr(t['delta_pi'])} | {_tr(t['nominal_fazla_milyar'], 1)} | {_tr(100 * t['reel_oran'])} |"
        )

    birlesik = d["birlesik_2028"]
    birlesik_metin = "tahmin edilemedi"
    if birlesik and birlesik.get("nokta") is not None:
        birlesik_metin = (
            f"nokta {_tr(birlesik['nokta'])} puan, aralık {_tr(birlesik['aralik'][0])} … {_tr(birlesik['aralik'][1])}"
        )

    para_n = f"{p['yillar'][0]}–{p['yillar'][-1]}" if p.get("yillar") else "—"
    kr_n = f"{k['yillar'][0]}–{k['yillar'][-1]}" if k.get("yillar") else "—"
    return "\n".join([
        "# Beş adımın enflasyon köprüsü",
        "",
        CULE + ".",
        "",
        "Beş adımın denklemleri fiyat, ticari faiz ve kur üretmez. Bu dosyadaki puan o denklemlere girdi olmaz. "
        f"Kriter özeti `{d['kriter_sha256'][:12]}`.",
        "",
        "## Dışsallık",
        "",
        "- `adim3_faiz_durma.py:10` — r_t = TP.KTF17; gözlem 2026-09'a kadar, sonrası son değer sabit. "
        "`adim3_faiz_durma.py:77` tam çeyrek yoksa son gözlemi yazar. Beş adımın çıktısı bu satırı güncellemez. Son gözlem %53,1925.",
        "- `adim45_maliyet.py:20` — `KUR = 49.1274` sabittir. `bes_yil_senaryo.py:148-151` döviz model etkisini `modellenmedi` bırakır; senaryo ankete eşittir.",
        "- `adim45_birim.py:8-10` — λ = 1 iken kur çarpanı λ'dır, USD stoku durur, faiz oranı durur.",
        "- `bes_yil_senaryo.py:134-138` — 2027–2031 enflasyon model etkisi −7,62 ile 0 arası `varsayim` bandıdır. "
        "`bes_yil_senaryo.py:142-144` faiz model etkisini `modellenmedi` bırakır. "
        "`bes_yil_senaryo.py:188` bu bandın geçiş payı kapısından geldiğini, faiz ve dövizin anketle kaldığını yazar.",
        "- `gsyh_pay.py:31-36` enflasyon senaryosunu yalnız GSYH paydasını büyütmek için okur. Adım 3'ün I_t formülü (`adim3_faiz_durma.py:9-10`) o paydayı kullanmaz.",
        "- `adim4_adres_yonlendirme.py:46` — «kur riski kâğıda taşınır mı, karar yok». İhraç denklemi TÜFE, TP.KTF17 veya 49,1274 okumaz.",
        "",
        "Tek yönlü bant şudur: `bes_yil_senaryo` enflasyona mantıksal bir aralık yazar ve `gsyh_pay` onu paydada kullanır. Aralık adım 3'ün faizine, adım 4.5'in kuruna ve adım 4'ün ihraçına geri dönmez.",
        "",
        "## Örneklem ve esneklik",
        "",
        f"Yıl sonu Aralık, tek tanım, ekleme yok. Hedef 2010–2026; 2026 Aralık henüz yok, son tam yıl 2025. "
        f"TÜFE `{S_TUFE}` (2003=100). M1 `{S_M1}`, M2 `{S_M2}`. "
        f"Para örneklemi {para_n}, n = {p['n']}. "
        f"b1 {_katsayi_yazi(p, 'b1')}. b2 {_katsayi_yazi(p, 'b2')}. "
        + (f"Belirtme katsayısı {_tr(p.get('r2'), 3)}." if p.get("r2") is not None else ""),
        "",
        f"Kredi `{S_KREDI}`, reel = nominal / TÜFE. GSYH `{S_GSYH}` yıl toplamı (dört çeyrek zincirlenmiş hacim). "
        f"Örneklem {kr_n}, n = {k['n']}. d {kat(k, 'd')}. h {kat(k, 'h')}. "
        "h büyüme puanıdır, enflasyon toplamına yazılmaz.",
        "",
        f"Kur eğimi `{S_YP_USD}` (gerçek kişi YP, milyon ABD doları) üzerinde. n = {kur['n']}. Durum: {kur['durum']}. "
        + (kur.get("neden") or "Arşiv tanımı eklenmedi."),
        "",
        "Aralık 0'ı kesen katsayının nokta puanı 0 yazılır; ±1,96 standart hata aralığı durur. "
        "Para kanalında iki katsayının ortak aralığı OLS kovaryansından gelir.",
        "",
        "Hız özdeşliği, PY sabitken ΔV/V = −ΔM2/M2. Fiyat denklemine eklenmez.",
        "",
        f"Örneklemde yıl sonu M2 daralmaz. En küçük Δlog M2 {_tr(p.get('dlog_m2_min'), 3)}, en büyük {_tr(p.get('dlog_m2_max'), 3)}. "
        "Düşük senaryonun tepe daralması bunun tersi yöndedir. Orta, yüksek ve 13.967'lik ayak, görülmüş bir daralmanın ölçeğinde değildir. "
        "Puan, kilitli denklemin bu şoka uygulanmasıdır.",
        "",
        "## Yıllık TÜFE puanı",
        "",
        "Eksi, endeksin o yıl daha yavaş artmasıdır. Para puanı stokun değiştiği yıla yazılır: düşüş 2029'da (tepe), "
        "2029-Q1 ihraçının ilk vadesi 2031'de geri gelir. 2030'da stok tepede durur, ek para puanı yoktur. "
        "χ = 0 ise 2031 geri dönüşü 2029 düşüşünü kapatır. χ = 0,5 ise kalıcı düzey kalır; bu, enflasyon oranına her yıl yeniden eklenen puan değildir.",
        "",
        "Maliyet 2029, 2030 ve 2031'de aynı akıştır (α = 0 ve α = 1). Kredi akışı 2030'da tepe, 2031'de kalıcıdır; 2029 tam tepe yılı diye yazılmaz. "
        "Adım 4.5 her yıl 0. Kurun skorlanan ucu Δe = 0'dır. Kira bu tabloya girmez: yılı repoda yoktur.",
        "",
        "Hücre, M1 alt/üst ile α = 0/1 köşelerinin nokta bandıdır. **Aday.** Kanallar aynı şokun parçası olabilir. İki tablo vardır: kredi hariç ve kredi dahil.",
        "",
        "Kredi hariç:",
        "",
        "| Yıl | düşük | orta | yüksek |",
        "| --- | ---: | ---: | ---: |",
        *yil_haric,
        "",
        "Kredi dahil:",
        "",
        "| Yıl | düşük | orta | yüksek |",
        "| --- | ---: | ---: | ---: |",
        *yil_dahil,
        "",
        "2028 skorlanan toplam 0'dır. Araç birleşik yurt içi ayak 13.967 milyar TL ayrıdır, skora girmez, M1 payı 0 sayılır (ölçülmedi): "
        f"{birlesik_metin}.",
        "",
        "## Kanallar",
        "",
        "| Senaryo | Para 2029 (M1 alt…üst) | Para 2031 geri | Maliyet α 0…1 | Kredi 2030 | Kredi 2031 | Kira (yıl yok) | Büyüme 2030 | Büyüme 2031 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        *detay,
        "",
        "Para kanalının ±1,96 ortak aralığı, M1 alt 2029 noktası için: "
        + "; ".join(
            f"{s['ad']} {_tr(s['para_tepe']['alt']['nokta'])} ({_tr(s['para_tepe']['alt']['aralik'][0])} … {_tr(s['para_tepe']['alt']['aralik'][1])})"
            for s in d["senaryo"]
        )
        + ".",
        "",
        "Para M1 alt sınırı 0'dır: çevrilen stok vadeli sayılır. Üst sınır, θ × 6.639,4'ün vadesiz YP'ye sığan kısmıdır. "
        "Maliyet paydası GSYH 2025 = 63.240,5. α = 0,5 yazılmaz. "
        "Kira ağırlığı 0,068028 (TÜİK 2025, başlık 04111). Konut grubu kullanılmaz. "
        "Kur geçişkenliği Öğünç ve Özel, TCMB Çalışma Tebliği 25/05: bir yıl 0,26, uzun dönem 0,38 ve 0,40. Büyük-şok 0,69 kullanılmaz. "
        "Veri ucu tahmin edilemediği için geçişkenlik puan üretmez.",
        "",
        "Kredi katsayısı d negatiftir. Örneklemde yüksek enflasyon yıllarında reel kredi gerilemiştir. "
        "Daralma şoku bu yüzden eksi değil artı puan verir. Bu bir talep çarpanı değildir. "
        "Büyüme katsayısı h'nin aralığı 0'ı keser; büyüme noktası 0'dır, aralık durur.",
        "",
        "Kredi stoku, EVDS son gözlem "
        f"{d['kredi_stok_tarih']}: {_tr(d['kredi_stok_milyar'], 1)} milyar TL (ham / 1e6). "
        "Yüzde daralma = ikinci tur / bu stok. Akışın stoğa bölümüdür. Büyüme satırı toplamın dışındadır.",
        "",
        "Adım 4.5: 0. **Kanıt.** λ = 1 fiyatların TL sayısını değiştirmez (`adim45_birim.py:8-10`).",
        "",
        "## Tutarlılık",
        "",
        "Aşağıdaki sapma adım dosyasına yazılmaz. Δπ, o yılın kredi dahil bandının en eksi köşesidir. "
        "2031'de para stoku geri geldiği için net nokta eksi değildir; o yıla sapma yazılmaz. "
        "Fisher adayı: model r = 53,1925'i tuttuğu için nominal duran faiz I · |Δπ| / 53,1925 kadar büyük kalır. "
        "Yön: tablodaki milyar TL, enflasyonla birlikte faizin de düştüğü bir dünyaya göre şişkindir. "
        "Reel karşılık (|Δπ| / 100) / (1 + 0,2973) oranında daha büyüktür. π_taban = 29,73. "
        "Yön: reel rahatlama, nominal tablonun sabit fiyatta ima ettiğinden büyüktür.",
        "",
        "| Senaryo | Yıl | Δπ | Nominal fazla, milyar TL | Reel rahatlama, % |",
        "| --- | ---: | ---: | ---: | ---: |",
        *sapma,
        "",
        "Kur sabiti: skorlanan Δe = 0 iken TL'ye çevrilmiş YP stoğu bu kanaldan sapmaz. "
        "Veriden Δe üretilemediği için |Δe/e| kadar şişkinlik sayısı yoktur. "
        "Δe eksi olsaydı sabit 49,1274, değerlenen TL dünyasında YP'yi büyük gösterirdi.",
        "",
        "α = 0 köşesinde maliyet 0'dır; o köşede Fisher sapması da 0'dır. Bant bu iki uçtur. Orta diye α = 0,5 konmaz. "
        "Yüksek 2029 köşesinde |Δπ| yüzde 53,19'u aşar. I · |Δπ| / r o köşede duran faizin kendisinden büyük çıkar. "
        "Formül kilitli olduğu için sayı durur; bu köşe, faizin enflasyon kadar inip pozitif kaldığı bir okumanın dışındadır.",
        "",
        "## Halk dili",
        "",
        _halk(d),
        "",
    ])


def _katsayi_yazi(blok: dict, ad: str) -> str:
    if blok.get("durum") != "olculdu" or ad not in blok:
        return "tahmin edilemedi"
    c = blok[ad]
    return (
        f"{_tr(c['coef'], 3)} (SE {_tr(c['se'], 3)}; {_tr(c['aralik'][0], 3)} … {_tr(c['aralik'][1], 3)}; "
        f"nokta {_tr(c['nokta'], 3)}; 0'ı içerir: {'evet' if c['sifir_icerir'] else 'hayır'})"
    )


def main() -> dict:
    ham = cek_ham()
    HAM.write_text(json.dumps(ham, ensure_ascii=False, indent=2), encoding="utf-8")
    doc = hesap(ham)
    CIKTI.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    RAPOR.write_text(rapor(doc), encoding="utf-8")
    return doc


if __name__ == "__main__":
    main()
