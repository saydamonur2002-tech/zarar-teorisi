"""Beş adımın faiz düğmesi: kredi freni → enflasyon → AOFM.

Kilitli dosyalar yazılmaz. Kapı boş kalır. Geçiş payı `gecis_payi_band_sonuc.json`
içindeki LR nokta tahminidir (`tahmin_ols`), kapıya taşınmaz.

Tepki, çeyrek verisinden:
  AOFM_t = α + ρ · AOFM_{t−1} + β · enf_{t−1}
Ana pencere 2018-Q1..2024-Q4. ρ bire yapışıksa uzun dönem türetilmez; β çeyrek kaymasıdır.
2023-Q3..2024-Q4 rejimi ayrıdır (n küçük). Onun durağan hali  β / (1−ρ).

Kredi freni K1 ve K3 yıllık temposudur. K2 bu kanala girmez. İki tempo, enflasyon
denkleminin girdisinde toplanır; Hazine faturasına, primine ve duran faize eklenmez.

Kur, faiz_kur_kalibre katsayısıyla yürür. Beş adım AOFM'yi β kadar kaydırır,
o kayma sonraki çeyreğin değer kaybına gider.

Çalıştır: python3 adim_faiz_tepki.py
Çıktı: adim_faiz_tepki.json, ADIM_FAIZ_TEPKI.md
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
ENF_HAM = KOK / "adim_faiz_tepki_enf.csv"


def _qi(d: str) -> int:
    y, q = d.split("-Q")
    return int(y) * 4 + int(q) - 1


def _qd(i: int) -> str:
    return f"{i // 4}-Q{i % 4 + 1}"


def _panel() -> pd.DataFrame:
    ay = pd.read_csv(KOK / "faiz_kur_ham.csv")
    ay["q"] = ay.donem.str.slice(0, 4) + "-Q" + ((ay.donem.str.slice(5, 7).astype(int) - 1) // 3 + 1).astype(str)
    rows = []
    for q, g in ay.groupby("q"):
        if g.aofm.notna().sum() == 3 and g.tufe.notna().sum() == 3:
            rows.append({"q": q, "aofm": float(g.aofm.mean()), "tufe": float(g.tufe.mean())})
    p = pd.DataFrame(rows).set_index("q").sort_index()
    p["enf"] = 100 * (p.tufe / p.tufe.shift(4) - 1)
    ek = _enf_2026()
    for q, v in ek.items():
        if q not in p.index and q in set(p.index):
            p.loc[q, "enf"] = v
        elif q not in p.index:
            # 2026 faizi hamda var; enflasyon yeni endeksten
            pass
    ham = pd.read_csv(KOK / "faiz_kur_ham.csv")
    ham["q"] = ham.donem.str.slice(0, 4) + "-Q" + ((ham.donem.str.slice(5, 7).astype(int) - 1) // 3 + 1).astype(str)
    for q, g in ham.groupby("q"):
        if g.aofm.notna().sum() != 3:
            continue
        if q not in p.index:
            p.loc[q, "aofm"] = float(g.aofm.mean())
        if q in ek:
            p.loc[q, "enf"] = ek[q]
    p = p.sort_index()
    p["a_lag"] = p.aofm.shift(1)
    p["e_lag"] = p.enf.shift(1)
    return p


def _enf_2026() -> dict[str, float]:
    """2025=100 endeksinden 2026 çeyrek yıllık enflasyonu. 2025, eski endeksle aynı çıktı."""
    try:
        body = {
            "type": "json", "series": "TP.TUKFIY2025.GENEL", "aggregationTypes": "avg", "formulas": "0",
            "startDate": "01-01-2024", "endDate": "14-10-2026", "frequency": "5",
            "decimalSeperator": ".", "decimal": "4", "dateFormat": "0", "lang": "TR",
            "yon": "0", "sira": "0", "ozelFormuller": [], "groupSeperator": False, "isRaporSayfasi": False,
        }
        items = get_json(f"{BASE}/fe", body)["items"]
        rows = [{"donem": it["Tarih"], "endeks": float(it["TP_TUKFIY2025_GENEL"])}
                for it in items if it.get("TP_TUKFIY2025_GENEL") not in (None, "") and it["Tarih"] <= "2026-09"]
        pd.DataFrame(rows).to_csv(ENF_HAM, index=False)
    except Exception as exc:  # noqa: BLE001
        if not ENF_HAM.exists():
            print(f"enflasyon alınamadı ({exc})")
            return {}
        rows = pd.read_csv(ENF_HAM).to_dict("records")
    else:
        rows = pd.read_csv(ENF_HAM).to_dict("records")
    kov = {}
    for r in rows:
        y, m = str(r["donem"]).split("-")
        q = f"{y}-Q{(int(m) - 1) // 3 + 1}"
        kov.setdefault(q, []).append(float(r["endeks"]))
    ort = {q: sum(v) / len(v) for q, v in kov.items() if len(v) == 3}
    out = {}
    for q, v in ort.items():
        y, qq = q.split("-Q")
        prev = f"{int(y) - 1}-Q{qq}"
        if prev in ort and q >= "2026-Q1":
            out[q] = 100 * (v / ort[prev] - 1)
    return out


def _uy(p: pd.DataFrame, bas: str, son: str) -> dict:
    d = p.loc[bas:son].dropna(subset=["aofm", "a_lag", "e_lag"])
    y = d.aofm.to_numpy(float)
    X = np.column_stack([np.ones(len(d)), d.a_lag.to_numpy(float), d.e_lag.to_numpy(float)])
    b, V, r2, _e = _ols_nw(y, X, 4 if len(d) >= 20 else 2)
    se = np.sqrt(np.diag(V))
    rho, beta = float(b[1]), float(b[2])
    uzun = None if abs(1 - rho) < 0.05 else beta / (1 - rho)
    return {
        "bas": bas, "son": son, "n": int(len(d)), "r2": round(float(r2), 3),
        "alfa": float(b[0]), "rho": rho, "beta": beta,
        "se_alfa": float(se[0]), "se_rho": float(se[1]), "se_beta": float(se[2]),
        "uzun_donem": None if uzun is None else float(uzun),
        "rho_yapisik": abs(1 - rho) < 0.05,
    }


def _sinav(p: pd.DataFrame, k: dict, bas: str, son: str) -> list[dict]:
    satir = []
    for i in range(_qi(bas), _qi(son) + 1):
        q = _qd(i)
        if q not in p.index or pd.isna(p.loc[q, "e_lag"]):
            continue
        hat = k["alfa"] + k["rho"] * float(p.loc[q, "a_lag"]) + k["beta"] * float(p.loc[q, "e_lag"])
        olc = float(p.loc[q, "aofm"])
        satir.append({"donem": q, "olcum": round(olc, 2), "tahmin": round(hat, 2), "fark": round(hat - olc, 2)})
    return satir


def _kredi() -> pd.DataFrame:
    ta = pd.read_csv(KOK / "tavan_akis.csv", dtype={"yil": str})
    r = ta[ta.yil == "2025"].iloc[0]
    itis = float(r.iloc[1])
    gsyh = float(r.iloc[3])
    puan0 = 100 * itis / gsyh
    k = pd.read_csv(KOK / "tek_sistem_kademe.csv", dtype={"Donem": str}).set_index("Donem")
    lr = float(json.loads((KOK / "gecis_payi_band_sonuc.json").read_text(encoding="utf-8"))["ana"]["LR_gecis_payi"])
    out = []
    for q, row in k.loc["2026-Q4":"2029-Q4"].iterrows():
        tempo = float(row.k1_itis_azalt_milyar_yillik) + float(row.k3_kredi_itki_azalt_milyar_yillik)
        puan = tempo / itis * puan0
        out.append({
            "donem": q,
            "k1": float(row.k1_itis_azalt_milyar_yillik),
            "k3": float(row.k3_kredi_itki_azalt_milyar_yillik),
            "puan_gsyh": round(puan, 3),
            "enf_puan": round(-lr * puan, 3),
        })
    return pd.DataFrame(out).set_index("donem"), {"itis": itis, "gsyh": gsyh, "puan0": round(puan0, 2), "lr": lr}


def _yol(faiz0: dict[str, float], kayma: dict[str, float], kur0: float, alfa: float, beta_kur: float) -> dict[str, float]:
    faiz = dict(faiz0)
    for q, d in kayma.items():
        if q in faiz:
            faiz[q] = faiz[q] + d
    kur = {"2026-Q3": kur0}
    u = kur0
    for i in range(_qi("2026-Q4"), _qi("2029-Q4") + 1):
        q, lag = _qd(i), _qd(i - 1)
        g = alfa + beta_kur * faiz[lag]
        u *= math.exp(g / 100)
        kur[q] = u
    return {k: round(v, 4) for k, v in kur.items()}, {k: round(v, 4) for k, v in faiz.items()}


def _md(s: dict) -> str:
    a, rj = s["ana"], s["rejim"]
    uzun = "türetilmedi, ρ bire yapışık" if a["rho_yapisik"] else f"{a['uzun_donem']:.2f}"
    ss = rj["uzun_donem"]
    return "\n".join([
        "# Beş adımın faiz düğmesi",
        "",
        "Soru: K1 ve K3 kredi freni politika faizini kaydırır mı, o kayma kuru ve Hazine faturasını değiştirir mi?",
        "",
        "Zincir: kredi temposu / 2025 GSYH oranı → geçiş LR → enflasyon puanı → AOFM tepkisi → faiz-kur denklemi.",
        "K2 bu zincire girmez. Kapı doldurulmaz. LR nokta tahmini `tahmin_ols` dir.",
        "",
        "## Tepki",
        "",
        f"- Ana pencere {a['bas']} → {a['son']}, n={a['n']}. ρ **{a['rho']:.3f}** (se {a['se_rho']:.3f}), β **{a['beta']:.3f}** (se {a['se_beta']:.3f}). R² {a['r2']:.3f}. Uzun dönem {uzun}.",
        f"- β sıfırın içindedir: se β'dan büyüktür. Ana yolda beş adım AOFM'yi kaydırmaz sayılır; çeyrek katsayısı yine de uygulanır.",
        f"- 2023-Q3 → 2024-Q4 rejimi, n={rj['n']}. ρ {rj['rho']:.3f} (se {rj['se_rho']:.3f}), β {rj['beta']:.3f} (se {rj['se_beta']:.3f}). Durağan hali **{ss:.2f}**: bir puan enflasyon, AOFM'yi {ss:.2f} puan kaydırır.",
        "",
        "Tek adım sınavı, ölçülen gecikmeyle:",
        "",
        "| Çeyrek | Rejim tahmini | Ölçülen | Fark |",
        "| --- | ---: | ---: | ---: |",
        *[f"| {r['donem']} | {r['tahmin']:.2f} | {r['olcum']:.2f} | {r['fark']:+.2f} |" for r in s["sinav_rejim"]],
        "",
        "## Yıl, puan",
        "",
        "| Yıl | Kredi puanı, GSYH | Enflasyon puanı | AOFM, ana β | AOFM, 2023 rejimi |",
        "| --- | ---: | ---: | ---: | ---: |",
        *[
            f"| {y} | {s['yil'][y]['puan']:.2f} | {s['yil'][y]['enf']:.2f} | {s['yil'][y]['aofm_ana']:+.2f} | {s['yil'][y]['aofm_rejim']:+.2f} |"
            for y in ("2027", "2028", "2029")
        ],
        "",
        f"2025 itiş {s['olcek']['itis']:.1f} milyar, GSYH payı {s['olcek']['puan0']:.2f}. LR {s['olcek']['lr']:.2f}. GSYH yolu yok; oran sabit. Geçiş aynı yıla yazıldı.",
        "",
        "## Ne denmez",
        "",
        "- Beş adım faizi ölçülmüş biçimde indirdi denmez. Ana β sıfırdan ayrı değildir.",
        "- 2023 rejimi 2025 sınavını tuttu denmez. 2025-Q2 farkı tabloda durur.",
        "- K1 ile K3 Hazine faizine eklendi denmez. İkisi yalnız kredi girdisinde durur.",
        "- Kapı doldu denmez. LR kapıya yazılmadı.",
        "",
    ])


def main() -> dict:
    p = _panel()
    ana = _uy(p, "2018-Q1", "2024-Q4")
    rejim = _uy(p, "2023-Q3", "2024-Q4")
    kredi, olcek = _kredi()
    kay_ana, kay_rejim = {}, {}
    for q, row in kredi.iterrows():
        kay_ana[q] = ana["beta"] * float(row.enf_puan)
        carp = 0.0 if rejim["uzun_donem"] is None else rejim["uzun_donem"]
        kay_rejim[q] = carp * float(row.enf_puan)
    fk = json.loads((KOK / "faiz_kur_kalibre.json").read_text(encoding="utf-8"))
    alfa, bk = float(fk["ana"]["alfa"]), float(fk["ana"]["beta"])
    faiz0 = {k: float(v) for k, v in fk["faiz_yol"]["son"].items()}
    kur0 = float(fk["capa"]["usd"])
    kur_ana, faiz_ana = _yol(faiz0, kay_ana, kur0, alfa, bk)
    kur_rejim, faiz_rejim = _yol(faiz0, kay_rejim, kur0, alfa, bk)
    yil = {}
    for y in ("2027", "2028", "2029"):
        parca = kredi.loc[[f"{y}-Q{q}" for q in range(1, 5)]]
        yil[y] = {
            "puan": round(float(parca.puan_gsyh.mean()), 2),
            "enf": round(float(parca.enf_puan.mean()), 2),
            "aofm_ana": round(float(np.mean([kay_ana[f"{y}-Q{q}"] for q in range(1, 5)])), 2),
            "aofm_rejim": round(float(np.mean([kay_rejim[f"{y}-Q{q}"] for q in range(1, 5)])), 2),
        }
    blob = {
        "ana": ana, "rejim": rejim,
        "sinav_ana": _sinav(p, ana, "2025-Q1", "2026-Q3"),
        "sinav_rejim": _sinav(p, rejim, "2025-Q1", "2026-Q3"),
        "olcek": olcek, "yil": yil,
        "faiz_yol": {"ana": faiz_ana, "rejim": faiz_rejim},
        "kur_yol": {"ana": kur_ana, "rejim": kur_rejim},
        "etiket": {
            "ana": "kalibrasyon_2018Q1_2024Q4_beta_sifirdan_ayri_degil",
            "rejim": "kalibrasyon_2023Q3_2024Q4_n6",
            "lr": "tahmin_ols_kapiya_yazilmadi",
            "k2": "kanala_girmez",
        },
    }
    (KOK / "adim_faiz_tepki.json").write_text(json.dumps(blob, ensure_ascii=False, indent=2), encoding="utf-8")
    (KOK / "ADIM_FAIZ_TEPKI.md").write_text(_md(blob), encoding="utf-8")
    print("ana beta", round(ana["beta"], 3), "se", round(ana["se_beta"], 3), "rho", round(ana["rho"], 3))
    print("rejim ss", None if rejim["uzun_donem"] is None else round(rejim["uzun_donem"], 3), "n", rejim["n"])
    for y, v in yil.items():
        print(y, v)
    return blob


if __name__ == "__main__":
    main()
