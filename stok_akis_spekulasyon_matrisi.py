"""Stok-akış aktör matrisi (H, F, B, K, D) + spekülasyona yakınlık.

Ölçüm: EVDS 2026-Q1 panel (akis_model), BDDK/uc_kural proxy'leri.
Senaryo eşikleri: hedge ≤0,30, spekülatif 0,30–0,40, ponzi etiketi >0,40 (Ha servis/gelir).

Çalıştır: python3 stok_akis_spekulasyon_matrisi.py
Çıktı: stok_akis_aktör_matrisi.csv, stok_akis_spekulasyon_matrisi.csv, STOK_AKIS_SPEKULASYON.md
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from akis_model import IDX, SEC, load, panel

KOK = Path(__file__).resolve().parent
DONEM = "2026-Q1"
ESIK_HEDGE = 0.30
ESIK_PONZI = 0.40


def _nfp_nl_r(stab, ftab, tcs, tcf, p: str, p_prev: str) -> dict:
    As, Ys = panel(stab, tcs, p)
    Af, Yf = panel(ftab, tcf, p)
    Ap, Yp = panel(stab, tcs, p_prev)
    nl = (Af - Yf).sum(axis=0)
    r = (As - Ap - Af).sum(axis=0) - (Ys - Yp - Yf).sum(axis=0)
    nfp = As.sum(axis=0) - Ys.sum(axis=0)
    varlik = As.sum(axis=0)
    borc = Ys.sum(axis=0)
    return {
        "varlik_binTL": varlik,
        "borc_binTL": borc,
        "NFP_binTL": nfp,
        "NL_binTL": nl,
        "R_binTL": r,
    }


def _rejim_servis(servis: float | None) -> str:
    if servis is None or np.isnan(servis):
        return "olculmedi"
    if servis <= ESIK_HEDGE:
        return "hedge"
    if servis <= ESIK_PONZI:
        return "speculative"
    return "ponzi_band"


def _yakinlik_servis(servis: float | None) -> float | None:
    """0=hedge sınırı, 1=ponzi eşiği üstü (cap 1.2)."""
    if servis is None or np.isnan(servis):
        return None
    return round(float(np.clip((servis - ESIK_HEDGE) / (ESIK_PONZI - ESIK_HEDGE), 0, 1.2)), 3)


def _yakinlik_fin_faal(oran: float | None) -> float | None:
    """Finansman/faaliyet: ~0,5 alt hedge; 0,5–1,0 spekülatif; >1,0 ponzi baskısı."""
    if oran is None or np.isnan(oran):
        return None
    return round(float(np.clip((oran - 0.5) / 0.5, 0, 1.2)), 3)


def main() -> None:
    stab, ftab, tcs, tcf = load()
    prev = "2025-Q4"
    core = _nfp_nl_r(stab, ftab, tcs, tcf, DONEM, prev)

    acik = {}
    p_acik = KOK / "acik_veri_ozet.json"
    if p_acik.exists():
        acik = json.loads(p_acik.read_text(encoding="utf-8"))

    uc = pd.read_csv(KOK / "uc_kural_senaryo.csv")
    row_uc = uc[(uc["Donem"] == "2026-Q4") & (uc["senaryo"] == "mevcut")].iloc[0]

    oz = {}
    p_oz = KOK / "akis_model_ozeti.json"
    if p_oz.exists():
        oz = json.loads(p_oz.read_text(encoding="utf-8"))

    g1 = oz.get("odemeyen_gosterge", {}).get("G1_takip_orani_%", {})
    fin_faal = 0.839
    try:
        from maliyet_kar_orani import OLCULEN_FINANSMAN_FAALIYET

        fin_faal = float(OLCULEN_FINANSMAN_FAALIYET[2024]["oran"])
    except Exception:
        pass

    butce_faiz = float(acik.get("olcumler", {}).get("butce_faiz_harcama_pay", {}).get("deger", 0.1441))
    kart_b = float(acik.get("taban_girdi", {}).get("kart_buyume_13h_yillik", 45.88)) / 100.0
    tuk_b = float(acik.get("taban_girdi", {}).get("tuketici_kredi_13h_yillik", 43.28)) / 100.0

    aktor_meta = {
        "H": {
            "ad": "Hane (S.14+15)",
            "servis_gelir_proxy": float(row_uc["borc_servis_orani_Ha"]),
            "takip_G1_yuzde": g1.get("hane", {}).get("2026-09"),
            "stok_buyume_proxy": max(kart_b, tuk_b),
            "fin_faal": None,
        },
        "Ha": {
            "ad": "Asgari ücretli proxy (Ha)",
            "servis_gelir_proxy": float(row_uc["borc_servis_orani_Ha"]),
            "takip_G1_yuzde": g1.get("hane", {}).get("2026-09"),
            "stok_buyume_proxy": max(kart_b, tuk_b),
            "fin_faal": None,
        },
        "F": {
            "ad": "Firmalar (S.11)",
            "servis_gelir_proxy": None,
            "takip_G1_yuzde": g1.get("firma", {}).get("2026-09"),
            "stok_buyume_proxy": None,
            "fin_faal": fin_faal,
        },
        "B": {
            "ad": "Bankalar B′ (S.12−TCMB)",
            "servis_gelir_proxy": None,
            "takip_G1_yuzde": g1.get("firma", {}).get("2026-09"),
            "stok_buyume_proxy": None,
            "fin_faal": None,
        },
        "K": {
            "ad": "Kamu K′ (S.13+TCMB)",
            "servis_gelir_proxy": butce_faiz,
            "takip_G1_yuzde": None,
            "stok_buyume_proxy": None,
            "fin_faal": None,
        },
        "D": {
            "ad": "Dış alem (S.2)",
            "servis_gelir_proxy": None,
            "takip_G1_yuzde": None,
            "stok_buyume_proxy": None,
            "fin_faal": None,
        },
    }

    rows = []
    for code in ("H", "Ha", "F", "B", "K", "D"):
        if code == "Ha":
            j = IDX["H"]
        elif code in SEC:
            j = IDX[code]
        else:
            continue
        m = aktor_meta[code]
        servis = m["servis_gelir_proxy"]
        yakin = _yakinlik_servis(servis) if code in ("H", "Ha") else None
        rejim = _rejim_servis(servis) if code in ("H", "Ha") else None
        if code == "F" and m["fin_faal"] is not None:
            yakin = _yakinlik_fin_faal(m["fin_faal"])
            ff = m["fin_faal"]
            if ff <= 0.5:
                rejim = "hedge"
            elif ff <= 1.0:
                rejim = "speculative"
            else:
                rejim = "ponzi_band"
        if code == "K" and servis is not None:
            yakin = round(min(1.2, max(0, (servis - 0.08) / 0.12)), 3)
            rejim = "speculative" if servis > 0.12 else "hedge"
        if code == "B":
            nl_kredi = float(
                pd.read_csv(KOK / "sfc_islem_akis_matrisi.csv")
                .query("Donem == @DONEM and Enstruman == 'kredi'")
                .iloc[0]["B"]
            )
            yakin = round(min(1.0, abs(nl_kredi) / 5e11), 3) if nl_kredi else None
            rejim = "aracı_kredi_genislemesi"
        if code == "D":
            yakin = 0.35
            rejim = "dis_finansman"

        rows.append(
            {
                "Donem": DONEM,
                "Aktor": code,
                "Aktor_ad": m["ad"],
                "Varlik_trilyonTL": round(core["varlik_binTL"][j] / 1e9, 3),
                "Borc_trilyonTL": round(core["borc_binTL"][j] / 1e9, 3),
                "NFP_trilyonTL": round(core["NFP_binTL"][j] / 1e9, 3),
                "NL_ceyrek_trilyonTL": round(core["NL_binTL"][j] / 1e9, 3),
                "R_ceyrek_trilyonTL": round(core["R_binTL"][j] / 1e9, 3),
                "servis_gelir_proxy": servis,
                "finansman_faaliyet_orani": m["fin_faal"],
                "takip_G1_yuzde": m["takip_G1_yuzde"],
                "stok_buyume_yillik_proxy": m["stok_buyume_proxy"],
                "spekulasyon_yakinlik_0_1": yakin,
                "minsky_rejim_okuma": rejim,
                "durum": "olcum+proxy",
            }
        )

    df = pd.DataFrame(rows)
    df.sort_values("spekulasyon_yakinlik_0_1", ascending=False, na_position="last", inplace=True)
    df.to_csv(KOK / "stok_akis_aktor_matrisi.csv", index=False, encoding="utf-8-sig")

    cross = []
    for _, r in df.iterrows():
        for met in ("NFP", "NL", "R"):
            cross.append(
                {
                    "Donem": DONEM,
                    "Kaynak_aktör": r["Aktor"],
                    "Kalem": met,
                    "Deger_trilyonTL": r[f"{met}_ceyrek_trilyonTL" if met != "NFP" else "NFP_trilyonTL"],
                    "Hedef": "net_pozisyon" if met == "NFP" else "ceyrek_akis",
                }
            )
    pd.DataFrame(cross).to_csv(KOK / "stok_akis_spekulasyon_matrisi.csv", index=False, encoding="utf-8-sig")

    sfc = pd.read_csv(KOK / "sfc_islem_akis_matrisi.csv")
    sfc_p = sfc[sfc["Donem"] == DONEM].copy()
    sfc_p.to_csv(KOK / "stok_akis_enstruman_matrisi_2026Q1.csv", index=False, encoding="utf-8-sig")

    yuksek = df[df["spekulasyon_yakinlik_0_1"].fillna(0) >= 0.55].copy()

    def _md_table(sub: pd.DataFrame) -> str:
        cols = list(sub.columns)
        lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
        for _, row in sub.iterrows():
            lines.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
        return "\n".join(lines)

    ozet = df[
        [
            "Aktor",
            "NFP_trilyonTL",
            "NL_ceyrek_trilyonTL",
            "R_ceyrek_trilyonTL",
            "spekulasyon_yakinlik_0_1",
            "minsky_rejim_okuma",
        ]
    ]
    md = [
        "# Stok-akış matrisi ve spekülasyona yakın aktörler",
        "",
        f"**Dönem (EVDS stok/akış):** {DONEM}. **Ha servis proxy:** 2026-Q4 `mevcut` senaryo girişi.",
        "",
        "## Aktör özeti (NFP = varlık − borç, trilyon TL)",
        "",
        _md_table(ozet),
        "",
        "## Spekülasyona en yakın (yakinlik ≥ 0,55)",
        "",
        _md_table(yuksek[["Aktor", "Aktor_ad", "spekulasyon_yakinlik_0_1", "minsky_rejim_okuma"]])
        if len(yuksek)
        else "_Eşik altında kayıt yok._",
        "",
        "## Eşikler",
        "",
        f"- Hane servis/gelir: hedge ≤ **{ESIK_HEDGE:.0%}**, ponzi etiketi > **{ESIK_PONZI:.0%}**",
        "- Firma: finansman/faaliyet kârı ≤0,5 hedge; 0,5–1,0 spekülatif; >1,0 ponzi baskısı",
        "- Kamu: bütçe faiz/harcama payı >%12 spekülatif baskı (fiscal)",
        "",
        "## Dosyalar",
        "",
        "- `stok_akis_aktor_matrisi.csv` — aktör satırları",
        "- `stok_akis_enstruman_matrisi_2026Q1.csv` — enstrüman × H,F,B,K,D işlem net (bin TL)",
        "- `sfc_islem_akis_matrisi.csv` — tam zaman serisi",
        "",
        "Çalıştır: `python3 stok_akis_spekulasyon_matrisi.py`",
    ]
    (KOK / "STOK_AKIS_SPEKULASYON.md").write_text("\n".join(md), encoding="utf-8")

    out = {
        "donem": DONEM,
        "esikler": {"hedge_servis": ESIK_HEDGE, "ponzi_servis": ESIK_PONZI},
        "spekulasyona_yakin_aktörler": yuksek[["Aktor", "spekulasyon_yakinlik_0_1", "minsky_rejim_okuma"]].to_dict(
            "records"
        ),
        "matris_dosyalari": [
            "stok_akis_aktor_matrisi.csv",
            "stok_akis_enstruman_matrisi_2026Q1.csv",
            "stok_akis_spekulasyon_matrisi.csv",
        ],
    }
    (KOK / "stok_akis_spekulasyon_sonuc.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
