"""Faz 5 — Geçiş payı kapısı için band daraltma: kredi itişi → TÜFE geçişi, OLS + Newey-West.

`tavan_akis.csv` gecis/tavan sütunları BOŞ kalır (kilitli kapı; birincil ölçüm yok). Burada ekonometrik TAHMİN üretilir, ayrı dosyaya
yazılır ve `tahmin_ols` etiketi taşır: ölçüm değil, kapıya taşınmaz. bes_yil enflasyon bandı [0, −7,62] bu tahminle daraltılır
(ayrı satır; `bes_yil_senaryo` dosyaları yazılmaz).

Veri (EVDS, anahtarsız uç nokta; önbellek gecis_payi_ham.csv):
  TP.FG.J0                 TÜFE genel endeks (aylık) → çeyrek ortalaması
  TP.DK.USD.A.YTL          USD/TRY alış (aylık ort.) → çeyrek ortalaması
  TP.FINHESTNKS62011.ZP34  F F.4 kredi akımı (konsolide olmayan, çeyrek, bin TL)
  TP.GSYIH20.BY.B1GQ       GSYH cari (çeyrek, bin TL)
Değişkenler: π_t = 400·Δlog TÜFE (yıllıklandırılmış çeyrek), kur_t = 100·Δlog USD/TRY, kredi_t = 100·akım_t/GSYH_t.
Model: π_t = α + Σ_q δ_q + Σ_{k=0..2} b_k kredi_{t−k} + c_0 kur_t + c_1 kur_{t−1} + ρ π_{t−1} + ε_t
Uzun dönem geçiş payı LR = Σb_k / (1−ρ): 1 puan GSYH kredi akımı → yıllık TÜFE puanı. Delta yöntemi + Newey-West(4) se.
Band = [LR − 1,96 se, LR + 1,96 se] ∩ [0, 1].

Çıktı: gecis_payi_ham.csv, gecis_payi_band.csv, gecis_payi_band_sonuc.json, GECIS_PAYI_BAND.md.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

KOK = Path(__file__).resolve().parent
sys.path.insert(0, str(KOK))
from evds_cek import BASE, get_json  # noqa: E402

HAM = KOK / "gecis_payi_ham.csv"
S_TUFE, S_USD, S_AKIM, S_GSYH = "TP.FG.J0", "TP.DK.USD.A.YTL", "TP.FINHESTNKS62011.ZP34", "TP.GSYIH20.BY.B1GQ"
ITIS_GSYH_YUZDE = 7.62  # tavan_akis 2025: F.4 akımı / GSYH; bes_yil band [0, −7,62]
RAPOR_VARSAYIM = 1 / 3  # tek-sistem RAPOR 'üçte biri'; varsayım


def _govde(series, agg, freq, start="01-01-2010", end="10-10-2026"):
    return {"type": "json", "series": "-".join(series), "aggregationTypes": "-".join(agg), "formulas": "-".join("0" for _ in series),
            "startDate": start, "endDate": end, "frequency": freq, "decimalSeperator": ".", "decimal": "4", "dateFormat": "0", "lang": "TR",
            "yon": "0", "sira": "0", "ozelFormuller": [], "groupSeperator": False, "isRaporSayfasi": False}


def _cek_items(series, agg, freq) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for it in get_json(f"{BASE}/fe", _govde(series, agg, freq))["items"]:
        for s in series:
            v = it.get(s.replace(".", "_"))
            if v not in (None, ""):
                out.setdefault(str(it["Tarih"]), {})[s] = float(str(v).replace(",", ""))
    return out


def veri() -> dict[str, dict[str, float]]:
    try:
        ay = _cek_items([S_TUFE, S_USD], ["avg", "avg"], "5")
        ck = _cek_items([S_AKIM, S_GSYH], ["sum", "sum"], "6")
    except Exception as exc:  # noqa: BLE001
        if not HAM.exists():
            raise
        print("EVDS erişilemedi, önbellek:", exc)
        q: dict[str, dict[str, float]] = {}
        for r in csv.DictReader(HAM.open(encoding="utf-8-sig")):
            q.setdefault(r["donem"], {})[r["seri"]] = float(r["deger"])
        return q
    q: dict[str, dict[str, float]] = {}
    gr: dict[str, dict[str, list[float]]] = {}
    for d, v in ay.items():
        y, m = d.split("-")
        key = f"{y}-Q{(int(m) - 1) // 3 + 1}"
        for s, x in v.items():
            gr.setdefault(key, {}).setdefault(s, []).append(x)
    for key, sv in gr.items():
        for s, xs in sv.items():
            if len(xs) == 3:
                q.setdefault(key, {})[s] = sum(xs) / 3
    for d, v in ck.items():
        for s, x in v.items():
            q.setdefault(d, {})[s] = x
    with HAM.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh); w.writerow(["donem", "seri", "deger"])
        for d in sorted(q):
            for s, x in q[d].items():
                w.writerow([d, s, f"{x:.6f}"])
    return q


def _ols_nw(y: np.ndarray, X: np.ndarray, gecikme: int = 4):
    n, k = X.shape
    XtX_inv = np.linalg.inv(X.T @ X)
    b = XtX_inv @ X.T @ y
    e = y - X @ b
    S = sum(np.outer(X[t] * e[t], X[t] * e[t]) for t in range(n))
    for L in range(1, gecikme + 1):
        w = 1 - L / (gecikme + 1)
        G = sum(np.outer(X[t] * e[t], X[t - L] * e[t - L]) for t in range(L, n))
        S += w * (G + G.T)
    V = XtX_inv @ S @ XtX_inv
    r2 = 1 - float(e @ e) / float(((y - y.mean()) ** 2).sum())
    return b, V, r2, e


def _qi(d: str) -> int:
    y, qq = d.split("-Q")
    return int(y) * 4 + int(qq) - 1


def _qd(i: int) -> str:
    return f"{i // 4}-Q{i % 4 + 1}"


def tahmin(q: dict, bas: str, etiket: str, dinamik: bool = True, gecikme_k: int = 2) -> dict:
    """Yalnız ardışık çeyrekler: F.4 akımı 2015-Q1 öncesi yıllık (Q4'e yazılı); o noktalar dışarıda kalır."""
    tam = {d for d in q if all(s in q[d] for s in (S_TUFE, S_USD, S_AKIM, S_GSYH)) and q[d][S_GSYH] > 0}
    fiyat = {d for d in q if S_TUFE in q[d] and S_USD in q[d]}
    pi = {d: 400 * math.log(q[d][S_TUFE] / q[_qd(_qi(d) - 1)][S_TUFE]) for d in fiyat if _qd(_qi(d) - 1) in fiyat}
    kur = {d: 100 * math.log(q[d][S_USD] / q[_qd(_qi(d) - 1)][S_USD]) for d in fiyat if _qd(_qi(d) - 1) in fiyat}
    kredi = {d: 100 * q[d][S_AKIM] / q[d][S_GSYH] for d in tam}
    rows, ys, ds = [], [], []
    for d in sorted(tam):
        if d < bas:
            continue
        l1, l2 = _qd(_qi(d) - 1), _qd(_qi(d) - 2)
        if not (l1 in kredi and l2 in kredi and d in pi and l1 in pi and d in kur and l1 in kur):
            continue
        qd = int(d[-1])
        x = [1.0, float(qd == 2), float(qd == 3), float(qd == 4), kredi[d], kredi[l1]] + ([kredi[l2]] if gecikme_k == 2 else []) + [kur[d], kur[l1]]
        if dinamik:
            x.append(pi[l1])
        rows.append(x); ys.append(pi[d]); ds.append(d)
    X, y = np.array(rows), np.array(ys)
    b, V, r2, e = _ols_nw(y, X)
    ib = [4, 5, 6] if gecikme_k == 2 else [4, 5]
    ik = ib[-1] + 1
    irho = ik + 2
    sb = float(b[ib].sum())
    if dinamik:
        rho = float(b[irho])
        LR = sb / (1 - rho)
        g = np.zeros(len(b)); g[ib] = 1 / (1 - rho); g[irho] = sb / (1 - rho) ** 2
    else:
        rho, LR = None, sb
        g = np.zeros(len(b)); g[ib] = 1
    se = float(math.sqrt(g @ V @ g))
    alt, ust = LR - 1.96 * se, LR + 1.96 * se
    band = [max(0.0, alt), min(1.0, ust)]
    if band[0] > band[1]:
        band = None
    b68 = [max(0.0, LR - se), min(1.0, LR + se)]
    if b68[0] > b68[1]:
        b68 = None
    return {"spesifikasyon": etiket, "dinamik": dinamik, "orneklem": f"{ds[0]}..{ds[-1]}", "n": len(ds), "r2": round(r2, 3),
            "b_kredi": [round(float(v), 4) for v in b[ib]], "b_kredi_toplam": round(sb, 4), "rho": None if rho is None else round(rho, 4),
            "c_kur": [round(float(b[ik]), 4), round(float(b[ik + 1]), 4)],
            "LR_gecis_payi": round(LR, 4), "se_nw4": round(se, 4), "ci95": [round(alt, 4), round(ust, 4)],
            "band_0_1": None if band is None else [round(band[0], 4), round(band[1], 4)],
            "band68_0_1": None if b68 is None else [round(b68[0], 4), round(b68[1], 4)],
            "bes_yil_enflasyon_puan_68": None if b68 is None else [round(-ITIS_GSYH_YUZDE * b68[1], 2), round(-ITIS_GSYH_YUZDE * b68[0], 2)],
            "bes_yil_enflasyon_puan": None if band is None else [round(-ITIS_GSYH_YUZDE * band[1], 2), round(-ITIS_GSYH_YUZDE * band[0], 2)],
            "durum": "tahmin_ols", "not": "Newey-West(4); mevsim kuklası; LR delta yöntemi. Ölçüm değil; kapıya taşınmaz."}


def _md_table(baslik, satirlar):
    s = ["| " + " | ".join(baslik) + " |", "| " + " | ".join("---" for _ in baslik) + " |"]
    for r in satirlar:
        s.append("| " + " | ".join("" if x is None else str(x) for x in r) + " |")
    return "\n".join(s)


def main() -> dict:
    q = veri()
    spesler = [tahmin(q, "2015-Q3", "tam örneklem (2015-Q3+), dinamik"), tahmin(q, "2015-Q3", "tam örneklem (2015-Q3+), statik", dinamik=False),
               tahmin(q, "2015-Q3", "tam örneklem, k=0..1, dinamik (az parametre)", gecikme_k=1),
               tahmin(q, "2018-Q1", "2018+ (kur şokları), dinamik"), tahmin(q, "2021-Q1", "2021+ (yüksek enflasyon), dinamik")]
    ana = spesler[0]
    alan = ["nesne", "spesifikasyon", "orneklem", "n", "r2", "b_kredi_toplam", "rho", "LR_gecis_payi", "se_nw4", "ci95_alt", "ci95_ust",
            "band_alt", "band_ust", "band68_alt", "band68_ust", "bes_yil_puan_alt", "bes_yil_puan_ust", "bes_yil_puan68_alt", "bes_yil_puan68_ust", "durum", "not"]
    satirlar = []
    for s in spesler:
        satirlar.append({"nesne": "gecis_payi", "spesifikasyon": s["spesifikasyon"], "orneklem": s["orneklem"], "n": s["n"], "r2": s["r2"],
                         "b_kredi_toplam": s["b_kredi_toplam"], "rho": s["rho"], "LR_gecis_payi": s["LR_gecis_payi"], "se_nw4": s["se_nw4"],
                         "ci95_alt": s["ci95"][0], "ci95_ust": s["ci95"][1],
                         "band_alt": None if s["band_0_1"] is None else s["band_0_1"][0], "band_ust": None if s["band_0_1"] is None else s["band_0_1"][1],
                         "band68_alt": None if s["band68_0_1"] is None else s["band68_0_1"][0], "band68_ust": None if s["band68_0_1"] is None else s["band68_0_1"][1],
                         "bes_yil_puan_alt": None if s["bes_yil_enflasyon_puan"] is None else s["bes_yil_enflasyon_puan"][0],
                         "bes_yil_puan_ust": None if s["bes_yil_enflasyon_puan"] is None else s["bes_yil_enflasyon_puan"][1],
                         "bes_yil_puan68_alt": None if s["bes_yil_enflasyon_puan_68"] is None else s["bes_yil_enflasyon_puan_68"][0],
                         "bes_yil_puan68_ust": None if s["bes_yil_enflasyon_puan_68"] is None else s["bes_yil_enflasyon_puan_68"][1],
                         "durum": s["durum"], "not": s["not"]})
    satirlar.append({"nesne": "gecis_payi", "spesifikasyon": "RAPOR 'üçte biri'", "LR_gecis_payi": round(RAPOR_VARSAYIM, 4), "durum": "varsayim",
                     "not": "tek-sistem RAPOR cümlesi; kaynak yok"})
    satirlar.append({"nesne": "bes_yil_enflasyon_band", "spesifikasyon": "mevcut (bes_yil_senaryo)", "bes_yil_puan_alt": -ITIS_GSYH_YUZDE, "bes_yil_puan_ust": 0.0,
                     "durum": "band_tam", "not": "geçiş 0..1 × itiş 7,62 puan GSYH"})
    satirlar.append({"nesne": "bes_yil_enflasyon_band", "spesifikasyon": "daraltılmış (ana tahmin)", "orneklem": ana["orneklem"],
                     "bes_yil_puan_alt": None if ana["bes_yil_enflasyon_puan"] is None else ana["bes_yil_enflasyon_puan"][0],
                     "bes_yil_puan_ust": None if ana["bes_yil_enflasyon_puan"] is None else ana["bes_yil_enflasyon_puan"][1],
                     "bes_yil_puan68_alt": None if ana["bes_yil_enflasyon_puan_68"] is None else ana["bes_yil_enflasyon_puan_68"][0],
                     "bes_yil_puan68_ust": None if ana["bes_yil_enflasyon_puan_68"] is None else ana["bes_yil_enflasyon_puan_68"][1],
                     "durum": "tahmin_ols", "not": "95: CI∩[0,1]×7,62 (daralmadı); 68: (LR±se)∩[0,1]×7,62; bes_yil_senaryo dosyaları yazılmadı"})
    with (KOK / "gecis_payi_band.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=alan); w.writeheader()
        for s in satirlar:
            w.writerow({a: ("" if s.get(a) is None else s.get(a)) for a in alan})
    sonuc = {"faz": 5, "kapi": "gecis_payi", "tavan_akis_csv": "yazilmadi; gecis/tavan bos (kilitli kapi)", "ana": ana, "spesifikasyonlar": spesler,
             "rapor_varsayim": RAPOR_VARSAYIM, "itis_gsyh_yuzde": ITIS_GSYH_YUZDE, "seriler": [S_TUFE, S_USD, S_AKIM, S_GSYH],
             "etiket": "tahmin_ols: ölçüm değil, varsayım değil; kapıya taşınmaz"}
    (KOK / "gecis_payi_band_sonuc.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    md = ["# Faz 5 — Geçiş payı kapısı: band daraltma (OLS + Newey-West)", "",
          "Çalıştır: `python3 gecis_payi_band.py`. Çıktı: `gecis_payi_ham.csv`, `gecis_payi_band.csv`, `gecis_payi_band_sonuc.json`.", "",
          "`tavan_akis.csv` gecis/tavan boş kalır; kapı kilitli. Burada üretilen sayı ekonometrik tahmindir (`tahmin_ols`): birincil ölçüm değil, "
          "kapıya taşınmaz; bes_yil bandını daraltmak için ayrı satırda durur.", "",
          "## Model", "",
          "- π_t = 400·Δlog TÜFE; kredi_t = 100·F.4 akım/GSYH (çeyrek); kur_t = 100·Δlog USD/TRY.",
          "- π_t = α + mevsim + Σ_{k=0..2} b_k kredi_{t−k} + c_0 kur_t + c_1 kur_{t−1} + ρ π_{t−1} + ε; LR = Σb/(1−ρ); NW(4) se; delta yöntemi.",
          "- Band = CI95 ∩ [0,1]. Yorum: 1 puan GSYH kredi akımı → LR puan yıllık TÜFE.", "",
          "## Tahminler", "",
          _md_table(["spesifikasyon", "örneklem", "n", "R²", "Σb", "ρ", "LR", "se", "CI95", "band95 ∩ [0,1]", "band68 ∩ [0,1]", "bes_yil puan (68)"],
                    [[s["spesifikasyon"], s["orneklem"], s["n"], s["r2"], s["b_kredi_toplam"], s["rho"], s["LR_gecis_payi"], s["se_nw4"],
                      f"[{s['ci95'][0]}, {s['ci95'][1]}]", "boş" if s["band_0_1"] is None else f"[{s['band_0_1'][0]}, {s['band_0_1'][1]}]",
                      "boş" if s["band68_0_1"] is None else f"[{s['band68_0_1'][0]}, {s['band68_0_1'][1]}]",
                      "boş" if s["bes_yil_enflasyon_puan_68"] is None else f"[{s['bes_yil_enflasyon_puan_68'][0]}, {s['bes_yil_enflasyon_puan_68'][1]}]"] for s in spesler]), "",
          f"- RAPOR 'üçte biri' ({RAPOR_VARSAYIM:.3f}) varsayımı ana CI95 içinde mi: "
          f"**{'evet' if ana['ci95'][0] <= RAPOR_VARSAYIM <= ana['ci95'][1] else 'hayır'}**.",
          f"- bes_yil enflasyon bandı: mevcut [−{ITIS_GSYH_YUZDE}, 0] → daraltılmış "
          + ("boş (CI [0,1] dışında)" if ana["bes_yil_enflasyon_puan"] is None else f"**[{ana['bes_yil_enflasyon_puan'][0]}, {ana['bes_yil_enflasyon_puan'][1]}]**")
          + " puan (95, ana tahmin); 68 bandı "
          + ("boş" if ana["bes_yil_enflasyon_puan_68"] is None else f"**[{ana['bes_yil_enflasyon_puan_68'][0]}, {ana['bes_yil_enflasyon_puan_68'][1]}]**")
          + " puan. `bes_yil_senaryo` dosyaları yazılmadı.",
          f"- Sonuç: tek sayıya inmez. Nokta tahmin LR {ana['LR_gecis_payi']:.2f} (tam geçişe yakın) ama se {ana['se_nw4']:.2f}; 95 bandı [0,1]'i "
          "daraltmaz, 68 bandı alt ucu 0'dan kaldırır. Kredi katsayıları her spesifikasyonda pozitif; kesinlik yok.", "",
          "## Sınırlar", "",
          "- Kredi akımı içsel (enflasyon krediyi de etkiler); OLS geçiş payı nedensel değil. Kur ve gecikmeli π kontrol; araç değişken yok.",
          "- Örneklem rejim değiştiriyor (2018 kur şoku, 2021+ yüksek enflasyon); alt örneklem satırları bunun için.",
          "- F.4 akımı 2015-Q1 öncesi yıllık (Q4'e yazılı), çeyrek yok; TP.FG.J0 (2003=100) 2026'da bitiyor → örneklem 2015-Q3..2025-Q4.",
          "- Band tek sayıya inmez; se bunu söyler. Daralan band kapıya yazılmaz; kapı birincil ölçüm ister.", ""]
    (KOK / "GECIS_PAYI_BAND.md").write_text("\n".join(md), encoding="utf-8")
    for s in spesler:
        print(f"{s['spesifikasyon']:<34} n {s['n']:<3} LR {s['LR_gecis_payi']:>7.3f} se {s['se_nw4']:.3f} CI {s['ci95']} band {s['band_0_1']} bes_yil {s['bes_yil_enflasyon_puan']}")
    return sonuc


if __name__ == "__main__":
    main()
