"""Faiz dışsallığı. Kurallar FAIZ_DISSALLIK_ONKAYIT.md ile aynıdır.

Çalıştır: python3 faiz_dissallik.py
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import numpy as np

from evds_cek import BASE, get_json

KOK = Path(__file__).resolve().parent
CEKILME = date.today().isoformat()
MIN_N = 36
T_ESIK = 1.96
HEDEF = 5.0
HP_LAMBDA = 14400.0

KUKLA = {
    "d2018": ("2018-08", "2018-12"),
    "d2020": ("2020-03", "2020-06"),
    "d2122": ("2021-09", "2022-12"),
    "d2023": ("2023-06", "2099-12"),
}
DONEM = [
    ("p1", "0000-01", "2018-07"),
    ("p2", "2018-08", "2020-02"),
    ("p3", "2020-03", "2021-08"),
    ("p4", "2021-09", "2023-05"),
    ("p5", "2023-06", "2099-12"),
]


def fetch(series: list[str], agg: list[str], start: str, end: str) -> tuple[dict, dict]:
    body = {
        "type": "json",
        "series": "-".join(series),
        "aggregationTypes": "-".join(agg),
        "formulas": "-".join("0" for _ in series),
        "startDate": start,
        "endDate": end,
        "frequency": "5",
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
    data = get_json(f"{BASE}/fe", body)
    names = data.get("seriesNames") or {}
    out = {s: {} for s in series}
    for it in data.get("items") or []:
        t = str(it.get("Tarih"))
        for s in series:
            v = it.get(s.replace(".", "_"))
            if v not in (None, ""):
                out[s][t] = float(str(v).replace(",", ""))
    meta = {s: names.get(s.replace(".", "_")) for s in series}
    return out, meta


def kapsam(d: dict) -> dict | None:
    if not d:
        return None
    ks = sorted(d)
    return {"ilk": ks[0], "son": ks[-1], "n": len(ks)}


def yoy(level: dict[str, float]) -> dict[str, float]:
    ks = sorted(level)
    ix = {a: i for i, a in enumerate(ks)}
    out = {}
    for a in ks:
        i = ix[a]
        if i < 12:
            continue
        b = ks[i - 12]
        if level[b]:
            out[a] = 100.0 * (level[a] / level[b] - 1.0)
    return out


def dlog100(level: dict[str, float]) -> dict[str, float]:
    ks = sorted(level)
    out = {}
    for i in range(1, len(ks)):
        a, b = ks[i], ks[i - 1]
        if level[a] > 0 and level[b] > 0:
            out[a] = 100.0 * (np.log(level[a]) - np.log(level[b]))
    return out


def hp_cycle(level: dict[str, float]) -> dict[str, float]:
    ks = sorted(a for a, v in level.items() if v and v > 0)
    y = np.log(np.array([level[a] for a in ks], float))
    n = len(y)
    D = np.zeros((n - 2, n))
    for i in range(n - 2):
        D[i, i] = 1.0
        D[i, i + 1] = -2.0
        D[i, i + 2] = 1.0
    trend = np.linalg.solve(np.eye(n) + HP_LAMBDA * (D.T @ D), y)
    cyc = 100.0 * (y - trend)
    return {a: float(cyc[i]) for i, a in enumerate(ks)}


def nw_se(X: np.ndarray, e: np.ndarray, bant: int) -> np.ndarray:
    u = X * e[:, None]
    S = u.T @ u
    for lag in range(1, max(int(bant), 0) + 1):
        w = 1.0 - lag / (bant + 1.0)
        G = u[lag:].T @ u[:-lag]
        S += w * (G + G.T)
    V = np.linalg.pinv(X.T @ X) @ S @ np.linalg.pinv(X.T @ X)
    return np.sqrt(np.clip(np.diag(V), 0, None))


def bant_genisligi(n: int) -> int:
    return max(1, int(np.floor(4.0 * (n / 100.0) ** (2.0 / 9.0))))


def onceki_ay(a: str) -> str:
    y, m = map(int, a.split("-"))
    m -= 1
    if m == 0:
        y -= 1
        m = 12
    return f"{y:04d}-{m:02d}"


def tahmin(aylar: list[str], faiz: dict, sapma: dict, acik: dict, kur: dict, kredi: dict, kukla: bool) -> dict:
    rows_x, rows_y, used = [], [], []
    for a in aylar:
        once = onceki_ay(a)
        if a not in faiz or once not in faiz:
            continue
        if a not in sapma or a not in acik or a not in kur or a not in kredi:
            continue
        rec = [1.0, sapma[a], acik[a], kur[a], kredi[a], faiz[once]]
        if kukla:
            rec.extend(1.0 if lo <= a <= hi else 0.0 for lo, hi in KUKLA.values())
        rows_x.append(rec)
        rows_y.append(faiz[a])
        used.append(a)
    n = len(rows_y)
    if n < MIN_N:
        return {"n": n, "karar": "belirlenemiyor", "neden": f"n<{MIN_N}", "ilk": used[0] if used else None, "son": used[-1] if used else None}
    X = np.asarray(rows_x, float)
    y = np.asarray(rows_y, float)
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    e = y - X @ b
    L = bant_genisligi(n)
    se = nw_se(X, e, L)
    adlar = ["a", "b1_enflasyon_sapmasi", "b2_uretim_acigi", "b3_kur", "b4_kredi", "b5_faiz_gecikme"]
    if kukla:
        adlar += list(KUKLA)
    katsayi = []
    for j, ad in enumerate(adlar):
        s = float(se[j])
        bj = float(b[j])
        t = bj / s if s > 0 and np.isfinite(s) else None
        katsayi.append({
            "ad": ad,
            "katsayi": round(bj, 4),
            "se": round(s, 4) if np.isfinite(s) else None,
            "t": round(t, 2) if t is not None and np.isfinite(t) else None,
            "anlamli_005": bool(t is not None and abs(t) > T_ESIK),
        })
    sst = float(np.sum((y - y.mean()) ** 2))
    r2 = None if sst <= 0 else round(float(1 - np.sum(e ** 2) / sst), 4)
    anlamli = {k["ad"]: k["anlamli_005"] for k in katsayi}
    ic = anlamli["b1_enflasyon_sapmasi"] or anlamli["b3_kur"] or anlamli["b4_kredi"]
    kir = kukla and any(anlamli[k] for k in KUKLA)
    return {
        "n": n,
        "ilk": used[0],
        "son": used[-1],
        "bant": L,
        "r2": r2,
        "katsayi": katsayi,
        "dissallik": "icsel" if ic else "dissal",
        "kirilma": bool(kir) if kukla else None,
    }


def pencere(aylar: list[str], lo: str, hi: str) -> list[str]:
    return [a for a in aylar if lo <= a <= hi]


def ortak_ay(seriler: list[dict]) -> list[str]:
    k = set(seriler[0])
    for s in seriler[1:]:
        k &= set(s)
    return sorted(k)


def reel(faiz: dict, bek: dict) -> dict:
    bos = []
    span = sorted(set(faiz) & set(range(0)))  # placeholder, replaced below
    ks = sorted(set(faiz) | set(bek))
    if not ks:
        return {}
    # boşluk sayımı, beklentinin kendi aralığında
    bk = sorted(bek)
    dolu = {}
    if bk:
        y1, m1 = map(int, bk[0].split("-"))
        y2, m2 = map(int, bk[-1].split("-"))
        ay = y1 * 12 + (m1 - 1)
        son = y2 * 12 + (m2 - 1)
        var = set(bk)
        while ay <= son:
            et = f"{ay // 12:04d}-{ay % 12 + 1:02d}"
            if et not in var:
                bos.append(et)
            ay += 1
    for a in ks:
        if a in faiz and a in bek:
            dolu[a] = faiz[a] - bek[a]
    dolu["_bos"] = bos  # type: ignore
    return dolu


def main() -> None:
    seri = [
        "TP.APIFON4", "TP.PY.P06.ON", "TP.TUKFIY2025.GENEL", "TP.FE.OKTG03", "TP.FE.OKTG04",
        "TP.TSANAYMT2021.BCD", "TP.DK.USD.A.YTL", "TP.KREDI.L001", "TP.PKAUO.S01.E.U",
    ]
    agg = ["avg", "avg", "last", "last", "last", "last", "last", "last", "avg"]
    ham, ad = fetch(seri, agg, "01-01-2006", "16-10-2026")
    enf = yoy(ham["TP.TUKFIY2025.GENEL"])
    sapma = {a: v - HEDEF for a, v in enf.items()}
    acik = hp_cycle(ham["TP.TSANAYMT2021.BCD"])
    kur = dlog100(ham["TP.DK.USD.A.YTL"])
    kredi = yoy(ham["TP.KREDI.L001"])
    bek = ham["TP.PKAUO.S01.E.U"]

    def blok(faiz: dict) -> dict:
        aylar = ortak_ay([faiz, sapma, acik, kur, kredi])
        # gecikme için bir önceki ay faiz sözlüğünde olsun diye faiz ayları zaten ortakla kesişir;
        # ortak liste ardışık olmayabilir. tahmin() kendi içinde önceki ayı arar.
        tam = tahmin(aylar, faiz, sapma, acik, kur, kredi, kukla=False)
        kir = tahmin(aylar, faiz, sapma, acik, kur, kredi, kukla=True)
        donemler = []
        for kod, lo, hi in DONEM:
            alt = pencere(aylar, lo, hi)
            d = tahmin(alt, faiz, sapma, acik, kur, kredi, kukla=False)
            if d.get("n", 0) < MIN_N:
                d = {"donem": kod, "sinir": [lo, hi], "n": d.get("n", 0), "ilk": d.get("ilk"), "son": d.get("son"),
                     "karar": "belirlenemiyor", "neden": f"n<{MIN_N}"}
            else:
                d["donem"] = kod
                d["sinir"] = [lo, hi]
                d["karar"] = d["dissallik"]
            donemler.append(d)
        kirilma_var = bool(kir.get("kirilma"))
        if tam.get("n", 0) < MIN_N:
            seri_karar = "belirlenemiyor"
        elif not kirilma_var:
            seri_karar = tam.get("dissallik", "belirlenemiyor")
        else:
            etiket = [d.get("karar") for d in donemler]
            if "icsel" in etiket:
                seri_karar = "icsel"
            elif any(e == "belirlenemiyor" for e in etiket):
                seri_karar = "belirlenemiyor"
            elif etiket and all(e == "dissal" for e in etiket):
                seri_karar = "dissal"
            else:
                seri_karar = "belirlenemiyor"
        return {"tam": tam, "kirilma_denklemi": kir, "donem": donemler, "kirilma_var": kirilma_var, "seri_karar": seri_karar,
                "ortak_ilk": aylar[0] if aylar else None, "ortak_son": aylar[-1] if aylar else None, "ortak_ay_sayisi": len(aylar)}

    fon = blok(ham["TP.APIFON4"])
    gecelik = blok(ham["TP.PY.P06.ON"])

    def reel_ozet(faiz: dict, kod: str) -> dict:
        bk = sorted(bek)
        bos = []
        if bk:
            y1, m1 = map(int, bk[0].split("-"))
            y2, m2 = map(int, bk[-1].split("-"))
            ay, son = y1 * 12 + m1 - 1, y2 * 12 + m2 - 1
            var = set(bk)
            while ay <= son:
                et = f"{ay // 12:04d}-{ay % 12 + 1:02d}"
                if et not in var:
                    bos.append(et)
                ay += 1
        dolu = {a: faiz[a] - bek[a] for a in faiz if a in bek}
        ks = sorted(dolu)
        return {
            "faiz": kod,
            "beklenti": "TP.PKAUO.S01.E.U",
            "doldurma": "yok",
            "beklenti_bos_ay": bos,
            "beklenti_bos_n": len(bos),
            "reel_n": len(ks),
            "reel_ilk": ks[0] if ks else None,
            "reel_son": ks[-1] if ks else None,
            "reel_son_deger": round(dolu[ks[-1]], 2) if ks else None,
        }

    sonuc = {
        "cekilme": CEKILME,
        "onkait": "FAIZ_DISSALLIK_ONKAYIT.md",
        "hedef": {
            "deger": HEDEF,
            "kaynak": "https://www.tcmb.gov.tr/wps/wcm/connect/EN/TCMB+EN/Main+Menu/Core+Functions/Monetary+Policy/Price+Stability+and+Inflation/Inflation+Targets",
            "indirildi": CEKILME,
            "not": "Sayfadaki tabloda 2012-2028 hedefi 5. Sapma = 12 aylık TÜFE − 5.",
        },
        "ad": ad,
        "kapsam": {k: kapsam(v) for k, v in ham.items()},
        "turev_kapsam": {
            "tufe_12ay": kapsam(enf),
            "sapma": kapsam(sapma),
            "uretim_acigi": kapsam(acik),
            "kur_degisim": kapsam(kur),
            "kredi_12ay": kapsam(kredi),
        },
        "politika_faizi": {
            "seri": None,
            "seri_karar": "belirlenemiyor",
            "neden": "Bir haftalık repo ihale faizi EVDS kataloğunda yok. Elle kodlanmadı.",
        },
        "fonlama": {"seri": "TP.APIFON4", **fon},
        "gecelik": {"seri": "TP.PY.P06.ON", **gecelik},
        "reel": [
            reel_ozet(ham["TP.APIFON4"], "TP.APIFON4"),
            reel_ozet(ham["TP.PY.P06.ON"], "TP.PY.P06.ON"),
        ],
    }
    (KOK / "faiz_dissallik_sonuc.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("fonlama", fon["seri_karar"], "kirilma", fon["kirilma_var"], "n", fon["tam"].get("n"), "r2", fon["tam"].get("r2"))
    print("gecelik", gecelik["seri_karar"], "kirilma", gecelik["kirilma_var"], "n", gecelik["tam"].get("n"), "r2", gecelik["tam"].get("r2"))
    for adim in ("fonlama", "gecelik"):
        blok_ = fon if adim == "fonlama" else gecelik
        print(adim, "donem", [(d["donem"], d.get("n"), d.get("karar")) for d in blok_["donem"]])
        if blok_["tam"].get("katsayi"):
            for k in blok_["tam"]["katsayi"]:
                if k["ad"].startswith("b"):
                    print(" ", k["ad"], k["katsayi"], "t", k["t"], k["anlamli_005"])
        if blok_["kirilma_denklemi"].get("katsayi"):
            for k in blok_["kirilma_denklemi"]["katsayi"]:
                if k["ad"].startswith("d"):
                    print(" ", k["ad"], k["katsayi"], "t", k["t"], k["anlamli_005"])


if __name__ == "__main__":
    main()
