"""Faiz → kur: AOFM'nin sonraki çeyrek USD/TRY değer kaybına etkisi.

Kimlik değil, regresyon. Kullanılan belirtim:
  g_t = α + β · AOFM_{t−1} + ε
  g_t = 100 · ln(USD_t / USD_{t−1}), çeyrek ortalaması

β, 2021-Q1..2024-Q4 üzerinde Newey-West(4) ile çözülür. Sınav: 2025-Q1..2026-Q2.
2018-Q1..2024-Q4 aynı β'yi verir; kontrol diye durur.
Reel faiz (AOFM − yıllık TÜFE) belirtimi aynı sınavda dağılır; ileri hesaba girmez.

Beş adımın faiz düğmesi bu dosyada yoktur. Girdi ölçülmüş AOFM ya da anket faizidir.
Kur yolu orta_vade_senaryo faturasına eklenir; iç kupon r_ic değişmez.

Çalıştır: python3 faiz_kur_kalibre.py
Çıktı: faiz_kur_ham.csv, faiz_kur_kalibre.json, FAIZ_KUR_KALIBRE.md
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from evds_cek import BASE, get_json
from gecis_payi_band import _ols_nw

KOK = Path(__file__).resolve().parent
HAM = KOK / "faiz_kur_ham.csv"
ANA = ("2021-Q1", "2024-Q4")
UZUN = ("2018-Q1", "2024-Q4")
SINAV = ("2025-Q1", "2026-Q2")
SON_TAM_AY = "2026-09"  # 2026-10 çekimi 14 Ekimde kesik; çeyreğe girmez
SON_FAIZ = 37.0  # Eylül 2026 tam ay ve 1–14 Ekim, AOFM


def _qi(d: str) -> int:
    y, q = d.split("-Q")
    return int(y) * 4 + int(q) - 1


def _qd(i: int) -> str:
    return f"{i // 4}-Q{i % 4 + 1}"


def _cek() -> pd.DataFrame:
    body = {
        "type": "json", "series": "TP.APIFON4-TP.DK.USD.A.YTL-TP.FG.J0",
        "aggregationTypes": "avg-avg-avg", "formulas": "0-0-0",
        "startDate": "01-01-2010", "endDate": "14-10-2026", "frequency": "5",
        "decimalSeperator": ".", "decimal": "4", "dateFormat": "0", "lang": "TR",
        "yon": "0", "sira": "0", "ozelFormuller": [], "groupSeperator": False, "isRaporSayfasi": False,
    }
    try:
        items = get_json(f"{BASE}/fe", body)["items"]
        rows = []
        for it in items:
            if str(it["Tarih"]) > SON_TAM_AY:
                continue
            rows.append({
                "donem": it["Tarih"],
                "aofm": float(it["TP_APIFON4"]) if it.get("TP_APIFON4") not in (None, "") else math.nan,
                "usd": float(it["TP_DK_USD_A_YTL"]) if it.get("TP_DK_USD_A_YTL") not in (None, "") else math.nan,
                "tufe": float(it["TP_FG_J0"]) if it.get("TP_FG_J0") not in (None, "") else math.nan,
            })
        df = pd.DataFrame(rows)
        df.to_csv(HAM, index=False)
        return df
    except Exception as exc:  # noqa: BLE001
        if not HAM.exists():
            raise
        print(f"EVDS alınamadı ({exc}); önbellek {HAM.name}")
        return pd.read_csv(HAM)


def _ceyrek(ay: pd.DataFrame) -> pd.DataFrame:
    d = ay.copy()
    d["y"] = d.donem.str.slice(0, 4).astype(int)
    d["m"] = d.donem.str.slice(5, 7).astype(int)
    d["q"] = d.y.astype(str) + "-Q" + ((d.m - 1) // 3 + 1).astype(str)
    parca = []
    for q, g in d.groupby("q"):
        if g.aofm.notna().sum() == 3 and g.usd.notna().sum() == 3:
            parca.append({
                "q": q,
                "aofm": float(g.aofm.mean()),
                "usd": float(g.usd.mean()),
                "tufe": float(g.tufe.mean()) if g.tufe.notna().sum() == 3 else math.nan,
            })
    p = pd.DataFrame(parca).set_index("q").sort_index()
    p["g"] = 100 * np.log(p.usd / p.usd.shift(1))
    p["enf"] = 100 * (p.tufe / p.tufe.shift(4) - 1)
    p["reel"] = p.aofm - p.enf
    p["faiz_lag"] = p.aofm.shift(1)
    p["reel_lag"] = p.reel.shift(1)
    return p


def _uy(p: pd.DataFrame, bas: str, son: str, xcol: str) -> dict:
    d = p.loc[bas:son].dropna(subset=["g", xcol])
    y = d.g.to_numpy(float)
    X = np.column_stack([np.ones(len(d)), d[xcol].to_numpy(float)])
    b, V, r2, _e = _ols_nw(y, X, 4)
    se = np.sqrt(np.diag(V))
    return {
        "bas": bas, "son": son, "n": int(len(d)), "r2": round(float(r2), 3),
        "alfa": float(b[0]), "beta": float(b[1]),
        "se_alfa": float(se[0]), "se_beta": float(se[1]),
        "x": xcol,
    }


def _sinav(p: pd.DataFrame, kats: dict) -> dict:
    u = float(p.loc["2024-Q4"].usd)
    satir = []
    for i in range(_qi(SINAV[0]), _qi(SINAV[1]) + 1):
        q = _qd(i)
        ghat = kats["alfa"] + kats["beta"] * float(p.loc[_qd(i - 1)].aofm)
        u *= math.exp(ghat / 100)
        satir.append({"donem": q, "g": round(float(p.loc[q].g), 2), "ghat": round(ghat, 2)})
    olculen = float(p.loc[SINAV[1]].usd)
    return {
        "bas": SINAV[0], "son": SINAV[1], "satir": satir,
        "usd_tahmin": round(u, 2), "usd_olcum": round(olculen, 2),
        "sapma_yuzde": round(100 * (u / olculen - 1), 2),
    }


def _anket_faiz() -> dict[int, float]:
    b = pd.read_csv(KOK / "bes_yil_senaryo.csv")
    f = b[(b.degisken == "faiz_politika") & b.beklenti.notna()]
    return {int(r.yil): float(r.beklenti) for r in f.itertuples()}


def _faiz_yollari(p: pd.DataFrame) -> dict[str, dict[str, float]]:
    """2026-Q4'ten 2029-Q4'e faiz düzeyi. 2026-Q3 ölçülmüş çeyrek, iki yolda da durur."""
    anket = _anket_faiz()
    son_anket_yil = max(anket)
    yillar = {}
    for y in range(2026, 2030):
        yillar[y] = anket.get(y, anket[son_anket_yil])
    # yıl sonu çeyrekleri; araları eşit adım
    uc = {f"{y}-Q4": yillar[y] for y in range(2026, 2030)}
    anket_q = {}
    for y in range(2026, 2029):
        a, b = uc[f"{y}-Q4"], uc[f"{y + 1}-Q4"]
        for k, q in enumerate((1, 2, 3, 4)):
            # 2027-Q1, k=0 iken adım yıl sonundan bir çeyrek
            anket_q[f"{y + 1}-Q{q}"] = a + (b - a) * (k + 1) / 4
    anket_q["2026-Q4"] = uc["2026-Q4"]
    anket_q["2026-Q3"] = float(p.loc["2026-Q3"].aofm)
    son = {"2026-Q3": float(p.loc["2026-Q3"].aofm)}
    for i in range(_qi("2026-Q4"), _qi("2029-Q4") + 1):
        son[_qd(i)] = SON_FAIZ
        anket_q.setdefault(_qd(i), anket[son_anket_yil])
    return {"son": son, "anket": anket_q, "anket_yil_sonu": {str(k): v for k, v in anket.items()},
            "son_anket_yili": son_anket_yil}


def _kur_yolu(p: pd.DataFrame, kats: dict, faiz: dict[str, float]) -> dict[str, float]:
    kur = {"2026-Q3": float(p.loc["2026-Q3"].usd)}
    faiz = {**{"2026-Q3": float(p.loc["2026-Q3"].aofm)}, **faiz}
    u = kur["2026-Q3"]
    for i in range(_qi("2026-Q4"), _qi("2029-Q4") + 1):
        q = _qd(i)
        lag = _qd(i - 1)
        g = kats["alfa"] + kats["beta"] * faiz[lag]
        u *= math.exp(g / 100)
        kur[q] = u
    return {k: round(v, 4) for k, v in kur.items()}


def _md(s: dict) -> str:
    k = s["ana"]
    u = s["uzun"]
    z = s["reel"]
    n = s["sinav"]
    return "\n".join([
        "# Faiz → kur kalibrasyonu",
        "",
        "Soru: politika faizi (AOFM) sonraki çeyreğin dolar kurunu nasıl kaydırır?",
        "",
        "Denklem: g = α + β · AOFM gecikmesi. g, çeyrek ortalaması USD/TRY'nin log farkı, yüzde puan.",
        "",
        "## Katsayı",
        "",
        f"- Ana pencere {k['bas']} → {k['son']}, n={k['n']}. α **{k['alfa']:.2f}**, β **{k['beta']:.3f}** (se {k['se_beta']:.3f}). R² {k['r2']:.3f}.",
        f"- Bir puan AOFM, sonraki çeyreğin değer kaybını **{abs(k['beta']):.2f} puan** azaltır.",
        f"- Uzun pencere {u['bas']} → {u['son']}, n={u['n']}. β **{u['beta']:.3f}** (se {u['se_beta']:.3f}). İki pencerede eğim aynıdır.",
        f"- Reel faiz belirtimi (AOFM − yıllık TÜFE, gecikmeli) {z['bas']} → {z['son']}: β {z['beta']:.3f} (se {z['se_beta']:.3f}), R² {z['r2']:.3f}. İleri hesaba girmez.",
        "",
        "## Sınav, 2025-Q1 → 2026-Q2",
        "",
        f"- Katsayı 2024-Q4 kurundan yürütülünce 2026-Q2 **{n['usd_tahmin']:.2f}** çıkar. Ölçülen {n['usd_olcum']:.2f}. Sapma **{n['sapma_yuzde']:+.1f}%**. 2026 ilk yarıda tahmin, ölçülen değer kaybının üstündedir.",
        "",
        "| Çeyrek | Ölçülen g | Tahmin g |",
        "| --- | ---: | ---: |",
        *[f"| {r['donem']} | {r['g']:.2f} | {r['ghat']:.2f} |" for r in n["satir"]],
        "",
        "## İleri faiz yolları",
        "",
        f"- Son faiz: 2026-Q4 ve sonrası **{SON_FAIZ:.2f}**. Eylül 2026 tam ayı ve 1–14 Ekim bu düzeydedir. Çeyrek kapanmadı; düzey varsayımdır.",
        "- Anket: yıl sonu hedefleri `bes_yil_senaryo.csv` içinden okunur. 2026-Q4 anket yılı, sonrası yıl sonuna eşit adım. Son anket yılından sonra faiz sabit kalır.",
        "- 2026-Q3 faizi iki yolda da ölçülmüş çeyrek ortalamasıdır. Kur çapası 2026-Q3 ölçülmüş çeyrek ortalamasıdır. İlk tahmin 2026-Q4.",
        "",
        "Bu denklem beş adımın faizini üretmez. O düğme `adim_faiz_tepki.py` içindedir. `bes_yil_senaryo` faiz hücresi durur: o dosya beş adımın kendi satırını anketle doldurur.",
        "",
        "## Ne denmez",
        "",
        "- R² yüksek bir kur denklemi denmez. Faiz, çeyrek hareketinin küçük bir parçasıdır.",
        "- Reel faiz kuru kalibre etti denmez. O belirtimin R²'si sıfıra yakındır.",
        "- Beş adım faizi indirdi ya da kuru durdurdu denmez. Girdi AOFM yoludur.",
        "- İç borç kuponu bu kanalla değişir denmez. r_ic 2025 kimliğinde durur. Kuran dış faiz bacağı değişir.",
        "",
    ])


def main() -> dict:
    p = _ceyrek(_cek())
    ana = _uy(p, *ANA, "faiz_lag")
    uzun = _uy(p, *UZUN, "faiz_lag")
    reel = _uy(p, *UZUN, "reel_lag")
    sinav = _sinav(p, ana)
    yollar = _faiz_yollari(p)
    kur = {
        "son": _kur_yolu(p, ana, yollar["son"]),
        "anket": _kur_yolu(p, ana, yollar["anket"]),
    }
    blob = {
        "ana": ana, "uzun": uzun, "reel": reel, "sinav": sinav,
        "faiz_yol": {"son": yollar["son"], "anket": yollar["anket"]},
        "anket_yil_sonu": yollar["anket_yil_sonu"],
        "kur_yol": kur,
        "capa": {"donem": "2026-Q3", "usd": round(float(p.loc["2026-Q3"].usd), 4),
                 "aofm": round(float(p.loc["2026-Q3"].aofm), 4)},
        "etiket": {
            "beta": "kalibrasyon_2021Q1_2024Q4",
            "sinav": "2025Q1_2026Q2",
            "reel": "tutmadi",
            "bes_adim_faiz": "adim_faiz_tepki",
            "ileri_faiz_son": "varsayim_son_ay",
            "ileri_faiz_anket": "anket",
        },
    }
    (KOK / "faiz_kur_kalibre.json").write_text(json.dumps(blob, ensure_ascii=False, indent=2), encoding="utf-8")
    (KOK / "FAIZ_KUR_KALIBRE.md").write_text(_md(blob), encoding="utf-8")
    print(f"beta {ana['beta']:.4f} se {ana['se_beta']:.4f} r2 {ana['r2']}")
    print(f"sinav {sinav['usd_tahmin']} / {sinav['usd_olcum']} sapma {sinav['sapma_yuzde']:+.2f}%")
    print("2029-Q4 kur son", kur["son"]["2029-Q4"], "anket", kur["anket"]["2029-Q4"])
    return blob


if __name__ == "__main__":
    main()
