"""HEKIS enflasyonunu stok-akis NFP'sine tasir.

Kaynak: hekis/bind.py inflation_paths ve data/istanbul_2026.json.
Ileri patika, modelin kostugu patikadir: Agustos 2026 yillik TUFE dondurulur.
Reel degisim = -NFP * pi / (1+pi). Alacakli erir, borclu yukunden kurtulur.
"""
import json
import zipfile
from pathlib import Path

import numpy as np

from akis_model import SEC, load

ZIP = Path(r"c:\Users\asayd\Downloads\hekis-model-main.zip")
OBS = "hekis-model-main/data/istanbul_2026.json"


def inflation_paths(obs, horizon=20):
    """hekis.bind.inflation_paths ile ayni."""
    hist = obs["inflation_annual"]
    realized = [hist["2021"], hist["2022"], hist["2023"], hist["2024"], hist["2025"]]
    last = hist["2026_agustos_yoy"]
    hold = [last] * horizon
    disinflation = [last + (0.15 - last) * i / (horizon - 1) for i in range(horizon)]
    return {"hold_last": hold, "disinflation_varsayim": disinflation, "realized_2021_2025": realized}


def load_obs(zip_path=ZIP):
    with zipfile.ZipFile(zip_path) as z:
        return json.loads(z.read(OBS).decode("utf-8"))


def nfp_2026q1():
    """akis_model.main ile ayni net finansal pozisyon, bin TL."""
    stab, _, tcs, _ = load()
    return np.array([
        stab.get(("H", "2026-Q1", 1), 0) + stab.get(("NPISH", "2026-Q1", 1), 0),
        stab[("F", "2026-Q1", 1)],
        stab[("B", "2026-Q1", 1)] - tcs[("2026-Q1", 1)],
        stab[("K", "2026-Q1", 1)] + tcs[("2026-Q1", 1)],
        stab[("D", "2026-Q1", 1)],
    ], float)


def reel_degisim(nfp, pi):
    return -np.asarray(nfp, float) * pi / (1.0 + pi)


def main():
    obs = load_obs()
    paths = inflation_paths(obs)
    pi = paths["hold_last"][0]
    pi_q = (1.0 + pi) ** 0.25 - 1.0
    nfp = nfp_2026q1()
    yil = reel_degisim(nfp, pi) / 1e9
    ceyrek = reel_degisim(nfp, pi_q) / 1e9
    out = {
        "kaynak": "HEKIS bind.inflation_paths, hold_last",
        "tufe_yillik": pi,
        "tufe_ceyreklik": round(pi_q, 6),
        "gerceklesen_2021_2025": paths["realized_2021_2025"],
        "nfp_2026Q1_trilyonTL": dict(zip(SEC, (nfp / 1e9).round(3).tolist())),
        "reel_1yil_trilyonTL": dict(zip(SEC, yil.round(3).tolist())),
        "reel_1ceyrek_trilyonTL": dict(zip(SEC, ceyrek.round(3).tolist())),
        "reel_1yil_toplam": round(float(yil.sum()), 3),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
