"""Aktör bazlı rant kanalı direnci ve kâr amorti etme yüzdesi.

Lobi bağımsız; stok-akış + gelir tablosu proxy. Senaryo; ölçüm değil.
Girdi: uc_kural_senaryo.csv, maliyet_kar_orani.csv, direnc_yuzdesi.csv (yoksa üretilir).

Çalıştır: python3 rant_aktor.py  (dönüş yılı için: python3 rant_donus_yili.py)
Çıktı: rant_aktor.csv, rant_aktor_kalem.csv, rant_aktor_duyarlik.csv,
        rant_aktor_sonuc.json, RANT_AKTOR.md
        rant_donus_yili → rant_aktor_donus.csv, rant_donus_yili_*, RANT_DONUS_YILI.md
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

from akis_model import IDX, load, panel
from direnc_yuzdesi import DirencParams, _stok_proxies, _uc_row
from hane_alt import ASGARI, N_A as N_A_DEFAULT
from maliyet_kar_orani import OLCULEN_FINANSMAN_FAALIYET
from uc_kural_senaryo import SENARYOLAR

KOK = Path(__file__).resolve().parent
SON = "2031-Q4"
MEVCUT = "mevcut"
AKTORLER = ("H", "F", "B", "K")


@dataclass
class RantAktorParams:
    agirlik_H: float = 0.40
    agirlik_F: float = 0.30
    agirlik_B: float = 0.20
    agirlik_K: float = 0.10
    ho_varlik_payi: float = 0.80
    h_finansal_gelir_orani: float = 0.12  # H rant içinde finansal varlık payı, VARSAYIM
    fin_kayip_F: float = 0.50  # direnc finansal_rant → F
    fin_kayip_B: float = 0.35
    fin_kayip_H: float = 0.15
    b_nim_yillik: float = 0.028  # net faiz marjı proxy, VARSAYIM
    f_finansal_gelir_katsayi: float = 0.46  # finansman gideri → F finansal rant geliri proxy
    k_faiz_harcama_payi_olculdu: float = 0.131  # 2025 bütce, milyar TL ham toplam
    ufuk_yil: float = 5.0
    kira_getiri: float = 0.035
    n_a: float = N_A_DEFAULT


def _load_tables() -> tuple[list[dict], list[dict], list[dict]]:
    for mod, name in (("uc_kural_senaryo", "uc_kural_senaryo.csv"), ("maliyet_kar_orani", "maliyet_kar_orani.csv")):
        p = KOK / name
        if not p.exists():
            __import__(mod).main()
    if not (KOK / "direnc_yuzdesi.csv").exists():
        from direnc_yuzdesi import main as dmain

        dmain()
    uc = pd.read_csv(KOK / "uc_kural_senaryo.csv").to_dict("records")
    mk = pd.read_csv(KOK / "maliyet_kar_orani.csv").to_dict("records")
    dr = pd.read_csv(KOK / "direnc_yuzdesi.csv").to_dict("records")
    return uc, mk, dr


def _rant_gelir_baseline(stok: dict, p: RantAktorParams) -> dict[str, float]:
    """Yıllık rant geliri proxy (milyar TL)."""
    kira = stok["konut_stok_milyarTL"] * p.kira_getiri * p.ho_varlik_payi
    h_fin = stok["H_varlik_milyarTL"] * p.h_finansal_gelir_orani * 0.015  # varlık × getiri, VARSAYIM
    h_rant = kira + h_fin
    faaliyet_f = OLCULEN_FINANSMAN_FAALIYET[2024]["faaliyet_kari_milyarTL"]
    fin = OLCULEN_FINANSMAN_FAALIYET[2024]["finansman_milyarTL"]
    f_fin = fin * p.f_finansal_gelir_katsayi
    b_rant = stok["B_varlik_milyarTL"] * p.b_nim_yillik
    # K: faiz gideri = rant çıkışı; gelir tabanı harcama
    k_harcama_proxy = 8000.0  # milyar TL/yıl, VARSAYIM (bütce ölçeği)
    k_faiz = k_harcama_proxy * p.k_faiz_harcama_payi_olculdu
    h_faaliyet = p.n_a * ASGARI * 12 / 1e9  # ücret geliri proxy
    return {
        "H": round(h_rant, 2),
        "F": round(f_fin, 2),
        "B": round(b_rant, 2),
        "K": round(k_faiz, 2),
        "H_faaliyet_proxy": round(h_faaliyet, 2),
        "F_faaliyet_olculdu": round(faaliyet_f, 2),
        "B_faaliyet_proxy": round(b_rant * 0.35, 2),  # komisyon/diğer, VARSAYIM
        "K_faaliyet_proxy": round(k_harcama_proxy - k_faiz, 2),
    }


def _kayip_aktore(d: dict) -> dict[str, float]:
    fin = float(d.get("finansal_rant_milyar", 0))
    return {
        "H": float(d.get("kira_konut_ranti_milyar", 0))
        + float(d.get("ust_gelir_Ho_milyar", 0))
        + 0.15 * fin,
        "F": 0.50 * fin,
        "B": 0.35 * fin,
        "K": float(d.get("kamu_ust_unvan_milyar", 0)) + 0.05 * fin,
    }


def _amorti(rant: float, faaliyet: float) -> float | None:
    if rant + faaliyet <= 0:
        return None
    return round(100 * rant / (faaliyet + rant), 2)


def _nfp_delta(uc: list[dict], sen: str, mk: dict) -> dict[str, float]:
    base = _uc_row(uc, MEVCUT)
    cur = _uc_row(uc, sen)
    return {a: float(cur[f"NFP_{a}"]) - float(base[f"NFP_{a}"]) for a in ("H", "F", "B", "K", "D")}


def hesapla(p: RantAktorParams | None = None) -> tuple[list[dict], list[dict], dict]:
    p = p or RantAktorParams()
    uc, mk_rows, dr_rows = _load_tables()
    stok = _stok_proxies()
    base_rant = _rant_gelir_baseline(stok, p)
    dr = {r["senaryo"]: r for r in dr_rows}
    mk = {r["senaryo"]: r for r in mk_rows}
    rows = []
    kalem_rows = []

    for sen in SENARYOLAR:
        drow = dr[sen]
        kayip = _kayip_aktore(drow)
        nfp_d = _nfp_delta(uc, sen, mk)
        agirlik = {"H": p.agirlik_H, "F": p.agirlik_F, "B": p.agirlik_B, "K": p.agirlik_K}
        direnc_agirlikli = 0.0
        for akt in AKTORLER:
            rant_g = base_rant[akt]
            rant_g_son = max(0.0, rant_g - kayip[akt] / p.ufuk_yil)  # yıllık kayıp
            if akt == "H":
                faal = base_rant["H_faaliyet_proxy"]
            elif akt == "F":
                faal = base_rant["F_faaliyet_olculdu"]
            elif akt == "B":
                faal = base_rant["B_faaliyet_proxy"]
            else:
                faal = base_rant["K_faaliyet_proxy"]
            amorti_once = _amorti(rant_g, faal)
            amorti_sonra = _amorti(rant_g_son, faal)
            payda = max(abs(nfp_d.get(akt, 0)), rant_g * p.ufuk_yil, 1.0)
            direnc = round(100 * kayip[akt] / payda, 2)
            direnc_agirlikli += agirlik[akt] * direnc
            row = {
                "senaryo": sen,
                "aktor": akt,
                "durum": "senaryo",
                "rant_gelir_yillik_baseline_milyar": rant_g,
                "rant_kayip_ufuk_milyar": round(kayip[akt], 2),
                "rant_gelir_yillik_sonra_milyar": round(rant_g_son, 2),
                "faaliyet_proxy_milyar": faal,
                "kar_amorti_yuzde_once": amorti_once,
                "kar_amorti_yuzde_sonra": amorti_sonra,
                "kar_amorti_dusus_puan": None
                if amorti_once is None or amorti_sonra is None
                else round(amorti_once - amorti_sonra, 2),
                "rant_direnci_yuzde": direnc,
                "payda_NFP_delta_milyar": round(nfp_d.get(akt, 0), 2),
                "finansman_faaliyet_ref_F": OLCULEN_FINANSMAN_FAALIYET[2024]["oran"] if akt == "F" else "",
            }
            rows.append(row)
            for k in ("kira", "finans", "diger"):
                kalem_rows.append(
                    {
                        "senaryo": sen,
                        "aktor": akt,
                        "kalem": k,
                        "kayip_milyar": round(
                            {
                                "kira": float(drow.get("kira_konut_ranti_milyar", 0)) if akt == "H" else 0,
                                "finans": kayip[akt] if k == "finans" else 0,
                                "diger": float(drow.get("kamu_ust_unvan_milyar", 0)) if akt == "K" and k == "diger" else 0,
                            }[k],
                            2,
                        ),
                    }
                )
        rows.append(
            {
                "senaryo": sen,
                "aktor": "TOPLAM",
                "durum": "senaryo",
                "rant_direnci_yuzde": round(direnc_agirlikli, 2),
                "agirlik_not": "H40 F30 B20 K10 varsayılan",
            }
        )

    meta = {
        "durum": "senaryo",
        "olcum_degil": True,
        "lobi_bagimsiz": True,
        "tanim_rant_direnci": "rant_kayip / max(|ΔNFP|, rant_baseline×ufuk)",
        "tanim_amorti": "100 × rant / (faaliyet + rant)",
        "olculen_F_finansman_faaliyet_2024": OLCULEN_FINANSMAN_FAALIYET[2024],
        "parametreler": asdict(p),
        "stok_proxy": stok,
        "baseline_rant_yillik": {k: base_rant[k] for k in AKTORLER},
    }
    return rows, kalem_rows, meta


def _duyarlik() -> list[dict]:
    out = []
    for ho in (0.70, 0.80, 0.90):
        for el in (0.8, 1.0, 1.2):
            p = RantAktorParams(ho_varlik_payi=ho, kira_getiri=0.035 * el)
            rows, _, _ = hesapla(p)
            rev = [r for r in rows if r["senaryo"] == "maliyet_ucuz_revize" and r["aktor"] == "H"][0]
            tot = [r for r in rows if r["senaryo"] == "maliyet_ucuz_revize" and r["aktor"] == "TOPLAM"][0]
            out.append(
                {
                    "ho_varlik_payi": ho,
                    "kira_elastikiyet": el,
                    "H_rant_direnci": rev["rant_direnci_yuzde"],
                    "toplam_rant_direnci": tot["rant_direnci_yuzde"],
                    "H_amorti_dusus_puan": rev["kar_amorti_dusus_puan"],
                }
            )
    return out


def main():
    rows, kalem_rows, meta = hesapla()
    duy = _duyarlik()
    with (KOK / "rant_aktor.csv").open("w", newline="", encoding="utf-8-sig") as f:
        cols = [c for c in rows[0].keys() if c in rows[-1] or rows[0].get(c) is not None]
        all_cols = sorted({k for r in rows for k in r.keys()})
        w = csv.DictWriter(f, fieldnames=all_cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    with (KOK / "rant_aktor_kalem.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["senaryo", "aktor", "kalem", "kayip_milyar"])
        w.writeheader()
        w.writerows(kalem_rows)
    with (KOK / "rant_aktor_duyarlik.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(duy[0].keys()))
        w.writeheader()
        w.writerows(duy)
    (KOK / "rant_aktor_sonuc.json").write_text(
        json.dumps({"meta": meta, "satirlar": rows, "duyarlik": duy}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (KOK / "RANT_AKTOR.md").write_text(_md(meta, rows), encoding="utf-8")
    print("=== rant_aktor (senaryo; ölçüm değil) ===")
    for sen in SENARYOLAR:
        tot = next(r for r in rows if r["senaryo"] == sen and r["aktor"] == "TOPLAM")
        print(sen, "toplam_rant_direnci%", tot.get("rant_direnci_yuzde"))


def _md(meta: dict, rows: list[dict]) -> str:
    ref = meta["olculen_F_finansman_faaliyet_2024"]
    lines = [
        "# Aktör bazlı rant kanalı direnci",
        "",
        "**Senaryo; ölçüm değil.** Lobi bağımsız muhasebe proxy.",
        "",
        f"F referans (ölçüm, senaryo değil): finansman/faaliyet kârı **{ref['oran']}** ({ref['finansman_milyarTL']}/{ref['faaliyet_kari_milyarTL']} milyar TL, 2024).",
        "",
        "## Revize vs sert — H ve F (2031-Q4)",
        "",
        "| Senaryo | Aktör | Rant kayıp | Rant direnci % | Amorti önce | Amorti sonra | Δ puan |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for sen in ("uc_kural_kilitli", "maliyet_ucuz_revize"):
        for akt in ("H", "F", "B", "K"):
            r = next(x for x in rows if x["senaryo"] == sen and x["aktor"] == akt)
            lines.append(
                f"| {sen} | {akt} | {r.get('rant_kayip_ufuk_milyar')} | {r.get('rant_direnci_yuzde')} | "
                f"{r.get('kar_amorti_yuzde_once')} | {r.get('kar_amorti_yuzde_sonra')} | {r.get('kar_amorti_dusus_puan')} |"
            )
    lines.extend(["", "## Toplam ağırlıklı rant direnci", ""])
    for sen in SENARYOLAR:
        t = next(r for r in rows if r["senaryo"] == sen and r["aktor"] == "TOPLAM")
        lines.append(f"- **{sen}**: {t.get('rant_direnci_yuzde')}%")
    lines.extend(
        [
            "",
            "## Duyarlılık (revize, H)",
            "",
            "Ho varlık payı %70–90 ve kira elastikiyeti 0,8–1,2: toplam rant direnci ~%7,7–%12,6; H ~%17,8–%29,9. `rant_aktor_duyarlik.csv`.",
            "",
            "Payda: `max(|ΔNFP|, yıllık rant × ufuk_yil)`. Sert senaryoda H |ΔNFP| büyük → rant direnci düşük; revize kira kaybı baskın → H direnci yüksek.",
            "",
            "## Ne denmez",
            "",
            "- Ekonomik rantın tam ölçümü değildir; 0,84 yalnız F finansman/faaliyet referansıdır.",
            "- K′ harcama ölçeği (8000 milyar TL/yıl) VARSAYIM; faiz payı %13,1 bütçe ham toplamından ölçülüdür.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
