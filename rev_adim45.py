"""Revizyon G — Adım 4.5: TCMB nakit yükümlülüğü yalnız Analitik Bilanço ile kontrol (TP.AB.A17 Emisyon, 2026-03) ve banka kasası (TP.TOP.T01)."""
import json, pandas as pd
from pathlib import Path
KOK = Path(__file__).resolve().parent; EV = Path("/workspace/aktarim_matrisi/evds")
def deger(f, seri, donem="2026-03"):
    d = pd.read_csv(EV / f, usecols=["Donem", "Seri", "Deger"]); return float(d[(d.Seri == seri) & (d.Donem == donem)].Deger.iloc[-1]) / 1e6
a17 = deger("evds_a_analitik_bilanco_aylik.csv", "TP.AB.A17"); kasa = deger("evds_b_para_banka_aylik.csv", "TP.TOP.T01")
repo, tl_mev = 898.3, 15574.5
s = {"faz": "rev G", "A17_emisyon_2026_03": round(a17, 1), "repo_tcmb_nakit": repo, "fark": round(repo - a17, 1),
     "banka_kasasi_T01": round(kasa, 1), "banka_disi_nakit": round(a17 - kasa, 1),
     "TL_para_stoku_repo": round(repo + tl_mev, 1), "TL_para_stoku_banka_disi": round(a17 - kasa + tl_mev, 1),
     "etiket": "kanıt: 898,3 = A17 Emisyon; Emisyon banka kasasını içerir → banka dışı tanımda para stoku %0,4 düşer (aday düzeltme)"}
(KOK / "rev_adim45_sonuc.json").write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8"); print(s)
