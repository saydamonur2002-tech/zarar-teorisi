"""Direnç yüzdesi — revize reforma karşı kazanan kesimlerin kayıp payı.

Senaryo; ölçüm değil. Politik ekonomi proxy'si; lobi gücü veya seçim etkisi değildir.
Direnç % = (kira + finans + üst gelir + kamu üst unvan net kayıp) / toplam sistem kazancı × 100

Girdi: uc_kural_senaryo.csv, maliyet_kar_orani.csv (yoksa üretilir).
Çıktı: direnc_yuzdesi.csv, direnc_yuzdesi_duyarlik.csv, direnc_yuzdesi_sonuc.json, DIRENC_YUZDESI.md

Çalıştır: python3 direnc_yuzdesi.py
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

from akis_model import IDX, load, panel
from hane_alt import N_A as N_A_DEFAULT
from maliyet_kar_orani import OLCULEN_FINANSMAN_FAALIYET
from uc_kural_senaryo import SENARYOLAR

KOK = Path(__file__).resolve().parent
SON = "2031-Q4"
MEVCUT = "mevcut"


@dataclass
class DirencParams:
    """Kalem ağırlıkları duyarlılık için; kayıp hesabı doğrudan proxy ile."""

    agirlik_kira: float = 0.40
    agirlik_finans: float = 0.30
    agirlik_ust_gelir: float = 0.20
    agirlik_kamu_unvan: float = 0.10
    konut_H_varlik_payi: float = 0.25  # VARSAYIM
    kira_getiri_orani_yillik: float = 0.035  # VARSAYIM; konut stok × oran = yıllık kira hacmi proxy
    kira_yasam_elastikiyet: float = 1.0  # yaşam sepet düşüşü → kira geliri
    finans_kisit_katsayi: float = 0.08  # üretken zarf × yıllık finansman hacmi proxy
    ufuk_yil: float = 5.0
    finansman_faaliyet_ref: float = 0.84  # 2024 ölçüm; ölçek referansı
    ho_varlik_payi: float = 0.80  # hane_alt VARSAYIM
    ust_gelir_erosyon_katsayi: float = 0.55  # kapsama artışının Ho göreli kaybı
    kamu_ust_dilim_payi: float = 0.35  # personel gideri üst dilim VARSAYIM
    kamu_makas_milyar_ceyrek: float = 45.0  # uc_kural Params ile uyumlu
    direnc_yuksek_esik: float = 0.50  # >%50 → yüksek direnç etiketi
    n_a: float = N_A_DEFAULT


def _stok_proxies() -> dict:
    stab, tcs, _, _ = load()
    A, Y = panel(stab, tcs, "2026-Q1")
    h_var = float(A[:, IDX["H"]].sum() / 1e9) * 1000  # milyar TL
    f_borc = float(Y[:, IDX["F"]].sum() / 1e9) * 1000
    b_var = float(A[:, IDX["B"]].sum() / 1e9) * 1000
    return {
        "H_varlik_milyarTL": round(h_var, 1),
        "F_borc_milyarTL": round(f_borc, 1),
        "B_varlik_milyarTL": round(b_var, 1),
        "konut_stok_milyarTL": round(h_var * 0.25, 1),
        "durum": "proxy_EVDS_2026Q1",
    }


def _uc_row(rows: list[dict], senaryo: str) -> dict:
    return next(r for r in rows if r["senaryo"] == senaryo and r["Donem"] == SON)


def _kayiplar(
    base_yasam: float,
    base_uretken: float,
    s: dict,
    mk: dict,
    stok: dict,
    p: DirencParams,
) -> dict:
    yasam = float(s["yasam_maliyeti_TL"])
    d_yasam = max(0.0, (base_yasam - yasam) / base_yasam) if base_yasam else 0.0
    kira_hacim = stok["konut_stok_milyarTL"] * p.kira_getiri_orani_yillik
    kayip_kira = kira_hacim * d_yasam * p.kira_yasam_elastikiyet * p.ufuk_yil

    d_uretken = max(0.0, float(s["uretken_zarf_payi"]) - base_uretken)
    fin_yillik = OLCULEN_FINANSMAN_FAALIYET[2024]["finansman_milyarTL"]  # ölçüm; stok değil
    kayip_finans = d_uretken * fin_yillik * p.ufuk_yil * p.finans_kisit_katsayi
    f_ucret = float(mk.get("F_ucret_kumul_milyar", 0))
    if f_ucret > 0:
        kayip_finans += max(0.0, f_ucret - 912.0) * 0.015  # sert kredi/faiz hacmi, VARSAYIM

    d_kap = float(mk.get("delta_kapsama", 0))
    kar_g = float(mk.get("kar_proxy_kapsama_milyar", 0))
    kayip_ust = max(0.0, d_kap) * yasam * p.n_a / 1e9 * p.ho_varlik_payi * p.ust_gelir_erosyon_katsayi

    # Kamu üst unvan: yalnız makas daraltma senaryosunda (revize)
    n_ceyrek_makas = int(p.ufuk_yil * 4) if s["senaryo"] == "maliyet_ucuz_revize" else 0
    kayip_kamu = n_ceyrek_makas * p.kamu_makas_milyar_ceyrek * p.kamu_ust_dilim_payi * 0.25  # transferin üst dilime düşen payı, VARSAYIM

    return {
        "kira_konut_ranti_milyar": round(kayip_kira, 2),
        "finansal_rant_milyar": round(kayip_finans, 2),
        "ust_gelir_Ho_milyar": round(kayip_ust, 2),
        "kamu_ust_unvan_milyar": round(kayip_kamu, 2),
    }


def _hesapla(rows_uc: list[dict], mk_rows: list[dict], p: DirencParams) -> list[dict]:
    stok = _stok_proxies()
    mk = {r["senaryo"]: r for r in mk_rows}
    base_u = _uc_row(rows_uc, MEVCUT)
    base_yasam = float(base_u["yasam_maliyeti_TL"])
    base_uretken = float(base_u["uretken_zarf_payi"])
    out = []
    for sen in SENARYOLAR:
        u = _uc_row(rows_uc, sen)
        m = mk[sen]
        G_kapsama = float(m["kar_proxy_kapsama_milyar"])
        yasam = float(u["yasam_maliyeti_TL"])
        tasarruf_yillik = max(0.0, (base_yasam - yasam) * p.n_a / 1e9)
        G = G_kapsama + tasarruf_yillik * p.ufuk_yil  # kapsama + sepet tasarrufu (VARSAYIM)
        kalemler = _kayiplar(base_yasam, base_uretken, u, m, stok, p)
        toplam = sum(kalemler.values())
        agirlikli = (
            p.agirlik_kira * kalemler["kira_konut_ranti_milyar"]
            + p.agirlik_finans * kalemler["finansal_rant_milyar"]
            + p.agirlik_ust_gelir * kalemler["ust_gelir_Ho_milyar"]
            + p.agirlik_kamu_unvan * kalemler["kamu_ust_unvan_milyar"]
        )
        direnc = round(100 * toplam / G, 2) if G > 1e-6 else None
        direnc_ag = round(100 * agirlikli / G, 2) if G > 1e-6 else None
        uygulanabilirlik = None
        if direnc is not None:
            uygulanabilirlik = "yuksek_direnc" if direnc / 100 >= p.direnc_yuksek_esik else "orta_dusuk_direnc"
        out.append(
            {
                "senaryo": sen,
                "donem": SON,
                "durum": "senaryo",
                "sistem_kazanci_kar_proxy_milyar": round(G_kapsama, 2),
                "sistem_kazanci_tasarruf_milyar": round(tasarruf_yillik * p.ufuk_yil, 2),
                "sistem_kazanci_toplam_milyar": round(G, 2),
                **kalemler,
                "kayip_toplam_milyar": round(toplam, 2),
                "direnc_yuzdesi": direnc,
                "direnc_yuzdesi_agirlikli": direnc_ag,
                "uygulanabilirlik_revize": uygulanabilirlik if sen == "maliyet_ucuz_revize" else "",
                "not": "Kayıp = mevcuta göre kazanan kesim proxy; payda = kar_proxy + tasarruf",
            }
        )
    return out


def _duyarlik(rows_uc: list[dict], mk_rows: list[dict]) -> list[dict]:
    grid = []
    for wk, wf, wu, wkamu in (
        (0.40, 0.30, 0.20, 0.10),
        (0.50, 0.25, 0.15, 0.10),
        (0.30, 0.40, 0.20, 0.10),
        (0.35, 0.35, 0.20, 0.10),
    ):
        p = DirencParams(agirlik_kira=wk, agirlik_finans=wf, agirlik_ust_gelir=wu, agirlik_kamu_unvan=wkamu)
        for row in _hesapla(rows_uc, mk_rows, p):
            if row["senaryo"] != "maliyet_ucuz_revize":
                continue
            grid.append(
                {
                    "tur": "agirlik_grid",
                    "agirlik_kira": wk,
                    "agirlik_finans": wf,
                    "agirlik_ust_gelir": wu,
                    "agirlik_kamu_unvan": wkamu,
                    "direnc_yuzdesi": row["direnc_yuzdesi"],
                    "kayip_toplam_milyar": row["kayip_toplam_milyar"],
                    "sistem_kazanci_kar_proxy_milyar": row["sistem_kazanci_kar_proxy_milyar"],
                }
            )
    for el in (0.8, 1.0, 1.2):
        p = DirencParams(kira_yasam_elastikiyet=el)
        r = _hesapla(rows_uc, mk_rows, p)
        rev = next(x for x in r if x["senaryo"] == "maliyet_ucuz_revize")
        grid.append({"tur": "kira_elastikiyet", "kira_yasam_elastikiyet": el, **{k: rev[k] for k in ("direnc_yuzdesi", "kayip_toplam_milyar")}})
    return grid


def _load_inputs() -> tuple[list[dict], list[dict]]:
    p_uc = KOK / "uc_kural_senaryo.csv"
    p_mk = KOK / "maliyet_kar_orani.csv"
    if not p_uc.exists():
        from uc_kural_senaryo import run

        rows, _ = run()
    else:
        rows = pd.read_csv(p_uc).to_dict("records")
    if not p_mk.exists():
        from maliyet_kar_orani import main as mk_main

        mk_main()
    mk = pd.read_csv(p_mk).to_dict("records")
    return rows, mk


def main():
    rows_uc, mk_rows = _load_inputs()
    p = DirencParams()
    ana = _hesapla(rows_uc, mk_rows, p)
    duy = _duyarlik(rows_uc, mk_rows)
    stok = _stok_proxies()
    meta = {
        "durum": "senaryo",
        "olcum_degil": True,
        "direnc_politik_ekonomi_proxy": True,
        "tanim": "direnc_% = sum(kalem kayıpları) / (kar_proxy_kapsama + yaşam tasarrufu) × 100",
        "olculen_referans_finansman_faaliyet_2024": OLCULEN_FINANSMAN_FAALIYET[2024]["oran"],
        "parametreler": asdict(p),
        "stok_proxy": stok,
        "yorum": (
            "Revize yöntem kira/finans/üst gelir lehine mevcut düzeni bozar; direnç yüksek çıkabilir. "
            "Sert zam görünür maliyeti F'ye yükler; kira sepeti revizede düştüğü için kalem kaybı büyür."
        ),
    }
    rev = next(r for r in ana if r["senaryo"] == "maliyet_ucuz_revize")
    meta["revize_ozet"] = {
        "direnc_yuzdesi": rev["direnc_yuzdesi"],
        "uygulanabilirlik": rev["uygulanabilirlik_revize"],
        "sert_direnc": next(r["direnc_yuzdesi"] for r in ana if r["senaryo"] == "uc_kural_kilitli"),
    }
    with (KOK / "direnc_yuzdesi.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(ana[0].keys()))
        w.writeheader()
        w.writerows(ana)
    # kalem uzun format
    long_rows = []
    for r in ana:
        for k in ("kira_konut_ranti_milyar", "finansal_rant_milyar", "ust_gelir_Ho_milyar", "kamu_ust_unvan_milyar"):
            long_rows.append({"senaryo": r["senaryo"], "kalem": k, "kayip_milyar": r[k], "G_milyar": r["sistem_kazanci_kar_proxy_milyar"]})
    with (KOK / "direnc_yuzdesi_kalem.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["senaryo", "kalem", "kayip_milyar", "G_milyar"])
        w.writeheader()
        w.writerows(long_rows)
    with (KOK / "direnc_yuzdesi_duyarlik.csv").open("w", newline="", encoding="utf-8-sig") as f:
        if duy:
            w = csv.DictWriter(f, fieldnames=sorted({k for d in duy for k in d.keys()}))
            w.writeheader()
            w.writerows(duy)
    (KOK / "direnc_yuzdesi_sonuc.json").write_text(
        json.dumps({"meta": meta, "senaryolar": ana, "duyarlik": duy}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (KOK / "DIRENC_YUZDESI.md").write_text(_md(meta, ana), encoding="utf-8")
    print("=== direnc_yuzdesi (senaryo; ölçüm değil) ===")
    print(json.dumps(ana, ensure_ascii=False, indent=2))


def _md(meta: dict, ana: list[dict]) -> str:
    lines = [
        "# Direnç yüzdesi (SFC senaryo proxy)",
        "",
        "**Senaryo; ölçüm değil.** Politik ekonomi proxy'si; lobi veya seçim modeli değildir.",
        "",
        f"Tanım: {meta['tanim']}",
        "",
        f"Ölçülen referans (ayrı): 2024 finansman/faaliyet kârı = **{meta['olculen_referans_finansman_faaliyet_2024']}**",
        "",
        "## Senaryo karşılaştırma (2031-Q4)",
        "",
        "| Senaryo | G (kar proxy) | Kayıp toplam | **Direnç %** | Uygulanabilirlik (revize) |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for r in ana:
        lines.append(
            f"| {r['senaryo']} | {r['sistem_kazanci_kar_proxy_milyar']} | {r['kayip_toplam_milyar']} | "
            f"{r['direnc_yuzdesi']} | {r.get('uygulanabilirlik_revize', '')} |"
        )
    lines.extend(["", "## Kalemler (milyar TL kayıp)", ""])
    for r in ana:
        lines.append(
            f"- **{r['senaryo']}**: kira {r['kira_konut_ranti_milyar']}, finans {r['finansal_rant_milyar']}, "
            f"Ho {r['ust_gelir_Ho_milyar']}, kamu üst {r['kamu_ust_unvan_milyar']}"
        )
    lines.extend(["", meta["yorum"], "", "## Ne denmez", "", "- Gerçek direnç anketi değildir.", ""])
    return "\n".join(lines)


if __name__ == "__main__":
    main()
