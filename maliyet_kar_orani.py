"""Maliyet/kar oranı analizi — uc_kural SFC senaryoları.

Senaryo; ölçüm değil. Kar proxy muhasebe kârı değildir.
Maliyet = NL/R ile hazneye yazılan yük (F ücret kanalı + K′ bütçe kanalı).
Kar (fayda) = hedef değişken iyileşmesi (proxy).

Ölçülen referans (senaryo değil): Sektör Bilançoları finansman / faaliyet kârı.

Çalıştır: python3 maliyet_kar_orani.py  (önce uc_kural_senaryo.csv veya run() gerekir)
Çıktı: maliyet_kar_orani.csv, maliyet_kar_orani_sonuc.json, MALIYET_KAR_ORANI.md
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd

from hane_alt import N_A as N_A_DEFAULT
from uc_kural_senaryo import Params, SENARYOLAR, run, run_one

KOK = Path(__file__).resolve().parent
SON_DONEM = "2031-Q4"
BAS_DONEM = "2026-Q4"

# Ölçülen referans — tek_sistem_kopru / Sektör Bilançoları (17 NACE); senaryo ile karıştırılmaz
OLCULEN_FINANSMAN_FAALIYET = {
    2023: {"finansman_milyarTL": 2120.2, "faaliyet_kari_milyarTL": 3797.9, "oran": 0.558},
    2024: {"finansman_milyarTL": 3143.4, "faaliyet_kari_milyarTL": 3746.2, "oran": 0.839},
    "kaynak": "TÜİK-TCMB Sektör Bilançoları gelir tablosu; K/O hariç 17 kesim toplamı",
    "durum": "olculdu",
}


def _rows_from_disk() -> list[dict] | None:
    p = KOK / "uc_kural_senaryo.csv"
    if not p.exists():
        return None
    return pd.read_csv(p).to_dict("records")


def _maliyet_kanallari(sub: pd.DataFrame) -> dict:
    f = float(sub["F_ucret_kanali_kumul_milyar"].iloc[-1])
    k_sum = float(sub["K_butce_NL_milyar"].sum())
    k_abs = abs(k_sum)
    return {
        "F_ucret_kumul_milyar": round(f, 2),
        "K_butce_NL_kumul_milyar": round(k_sum, 2),
        "K_butce_NL_kumul_mutlak_milyar": round(k_abs, 2),
        "maliyet_proxy_toplam_milyar": round(f + k_abs, 2),
    }


def _kar_proxies(
    e: dict,
    base_kap: float,
    base_h: float,
    base_servis: float,
    n_a: float,
    yasam_agirlik: float,
) -> dict:
    d_kap = float(e["kapsama"]) - base_kap
    yasam = float(e["yasam_maliyeti_TL"])
    # Ana proxy (VARSAYIM): kapsama × yaşam × asgari sayısı
    kar_kapsama = d_kap * yasam * n_a / 1e9  # milyar TL/yıl benzeri
    kar_kapsama_w = d_kap * yasam * yasam_agirlik * n_a / 1e9
    d_nfp_h = float(e["NFP_H"]) - base_h
    d_servis = base_servis - float(e["borc_servis_orani_Ha"])
    return {
        "delta_kapsama": round(d_kap, 4),
        "kar_proxy_kapsama_milyar": round(kar_kapsama, 2),
        "kar_proxy_kapsama_yasam_agirlikli_milyar": round(kar_kapsama_w, 2),
        "kar_proxy_NFP_H_milyar": round(d_nfp_h, 2),
        "kar_proxy_Ha_servis_dusus": round(d_servis, 4),
        "yasam_maliyeti_TL": yasam,
        "N_A_varsayim": n_a,
        "yasam_agirlik": yasam_agirlik,
    }


def _oranlar(maliyet: float, kar: float, f_ucret: float, d_nfp_f: float) -> dict:
    mk = round(maliyet / kar, 2) if kar and kar > 1e-9 else None
    f_ozel = round(1000 * f_ucret / abs(d_nfp_f), 2) if d_nfp_f else None
    return {"maliyet_kar_orani": mk, "F_maliyet_bine_delta_NFP_F": f_ozel}


def senaryo_satir(rows: list[dict], senaryo: str, n_a: float = N_A_DEFAULT, yasam_agirlik: float = 1.0) -> dict:
    df = pd.DataFrame(rows)
    sub = df[df.senaryo == senaryo].sort_values("Donem")
    base = sub[sub.Donem == BAS_DONEM].iloc[0]
    end = sub[sub.Donem == SON_DONEM].iloc[0]
    e = end.to_dict()
    base_kap = float(base["kapsama"])
    kanal = _maliyet_kanallari(sub)
    kar = _kar_proxies(e, base_kap, float(base["NFP_H"]), float(base["borc_servis_orani_Ha"]), n_a, yasam_agirlik)
    d_nfp_f = float(e["NFP_F"]) - float(base["NFP_F"])
    oran = _oranlar(
        kanal["maliyet_proxy_toplam_milyar"],
        kar["kar_proxy_kapsama_milyar"],
        kanal["F_ucret_kumul_milyar"],
        d_nfp_f,
    )
    oran_alt = _oranlar(
        kanal["maliyet_proxy_toplam_milyar"],
        kar["kar_proxy_NFP_H_milyar"] if kar["kar_proxy_NFP_H_milyar"] > 0 else None,
        kanal["F_ucret_kumul_milyar"],
        d_nfp_f,
    )
    return {
        "senaryo": senaryo,
        "donem_son": SON_DONEM,
        "durum": "senaryo",
        **kanal,
        **kar,
        "delta_NFP_F_milyar": round(d_nfp_f, 2),
        **oran,
        "maliyet_kar_orani_kar_NFP_H": oran_alt["maliyet_kar_orani"],
        "maliyet_kar_orani_kar_servis": round(
            kanal["maliyet_proxy_toplam_milyar"] / kar["kar_proxy_Ha_servis_dusus"], 2
        )
        if kar["kar_proxy_Ha_servis_dusus"] > 1e-6
        else None,
    }


def duyarlik(rows_base: list[dict] | None = None) -> list[dict]:
    """Yaşam düşüş, N_A, yaşam ağırlığı — yalnız maliyet_ucuz_revize (+ sert sabit karşılaştırma)."""
    out = []
    if rows_base is None:
        rows_base = _rows_from_disk()
    # Tablo A: mevcut csv üzerinde N_A / ağırlık (uc_kural yeniden koşmadan)
    if rows_base:
        for n_a in (6.0e6, N_A_DEFAULT, 7.5e6):
            for w in (0.8, 1.0, 1.2):
                for s in SENARYOLAR:
                    r = senaryo_satir(rows_base, s, n_a=n_a, yasam_agirlik=w)
                    out.append(
                        {
                            "tur": "kar_proxy_formul",
                            "N_A": n_a,
                            "yasam_agirlik": w,
                            **{k: r[k] for k in r if k not in ("senaryo", "donem_son", "durum")},
                            "senaryo": s,
                        }
                    )
    # Tablo B: yaşam düşüş — uc_kural yeniden koş
    from akis_model import L_G, load, panel
    from butce_kanali import fiscal_shock  # noqa: F401 — kanal import side
    import pandas as pd

    stab, _, tcs, _ = load()
    A, Y = panel(stab, tcs, "2026-Q1")
    L, G = L_G(A, Y)
    nfp_bin = (A - Y).sum(axis=0)
    kanal = pd.read_csv(KOK / "K_kanal_paylari_son4ceyrek.csv", index_col=0)
    for dusus in (0.03, 0.04, 0.05):
        p = Params(yasam_reel_dusus_yillik=dusus)
        rws, _ = run_one(p, stab, tcs, L, G, nfp_bin, kanal, ("maliyet_ucuz_revize",))
        r = senaryo_satir(rws, "maliyet_ucuz_revize")
        out.append(
            {
                "tur": "yasam_dusus_kosusu",
                "yasam_reel_dusus_yillik": dusus,
                "senaryo": "maliyet_ucuz_revize",
                "maliyet_proxy_toplam_milyar": r["maliyet_proxy_toplam_milyar"],
                "kar_proxy_kapsama_milyar": r["kar_proxy_kapsama_milyar"],
                "maliyet_kar_orani": r["maliyet_kar_orani"],
                "F_maliyet_bine_delta_NFP_F": r["F_maliyet_bine_delta_NFP_F"],
                "delta_kapsama": r["delta_kapsama"],
            }
        )
    return out


def main():
    rows = _rows_from_disk()
    if rows is None:
        rows, _ = run()
    ana = [senaryo_satir(rows, s) for s in SENARYOLAR]
    duy = duyarlik(rows)
    meta = {
        "durum": "senaryo",
        "olcum_degil": True,
        "kar_proxy_muhasebe_kari_degil": True,
        "olculen_referans_finansman_faaliyet": OLCULEN_FINANSMAN_FAALIYET,
        "not": "Ölçülen 0,84 (2024) ile senaryo maliyet/kar oranı aynı tabloda yan yana; anlamları farklı.",
        "maliyet_tanim": "F_ucret_kanali_kumul + |Σ K_butce_NL| (milyar TL)",
        "kar_tanim": "Δkapsama × yaşam_maliyeti × N_A (milyar TL; VARSAYIM)",
        "donem": f"{BAS_DONEM}..{SON_DONEM}",
    }
    # CSV: ana tablo
    cols = list(ana[0].keys())
    with (KOK / "maliyet_kar_orani.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(ana)
    with (KOK / "maliyet_kar_orani_duyarlik.csv").open("w", newline="", encoding="utf-8-sig") as f:
        if duy:
            w = csv.DictWriter(f, fieldnames=sorted({k for d in duy for k in d.keys()}))
            w.writeheader()
            w.writerows(duy)
    (KOK / "maliyet_kar_orani_sonuc.json").write_text(
        json.dumps({"meta": meta, "senaryolar_2031Q4": ana, "duyarlik": duy}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = _md(meta, ana, duy)
    (KOK / "MALIYET_KAR_ORANI.md").write_text(md, encoding="utf-8")
    print("=== maliyet_kar_orani (senaryo; ölçüm değil) ===")
    print(json.dumps(ana, ensure_ascii=False, indent=2))


def _md(meta: dict, ana: list[dict], duy: list[dict]) -> str:
    ref = OLCULEN_FINANSMAN_FAALIYET
    lines = [
        "# Maliyet/kar oranı (SFC senaryo)",
        "",
        "**Senaryo; ölçüm değil.** Kar proxy muhasebe kârı değildir.",
        "",
        "Çalıştır: `python3 maliyet_kar_orani.py` (`uc_kural_senaryo.csv` veya otomatik `run()`).",
        "",
        "## Ölçülen referans (senaryo değil)",
        "",
        f"| Yıl | Finansman | Faaliyet kârı | Oran |",
        f"| --- | ---: | ---: | ---: |",
        f"| 2023 | {ref[2023]['finansman_milyarTL']} | {ref[2023]['faaliyet_kari_milyarTL']} | {ref[2023]['oran']} |",
        f"| 2024 | {ref[2024]['finansman_milyarTL']} | {ref[2024]['faaliyet_kari_milyarTL']} | {ref[2024]['oran']} |",
        "",
        "Faiz yükünün faaliyet kârını ne kadar yediği. Senaryo maliyet/kar ile **karıştırılmaz**.",
        "",
        "## Senaryo proxy (2031-Q4)",
        "",
        "| Senaryo | F maliyet | K′ maliyet (|küm.|) | Toplam maliyet | Kar (kapsama) | Maliyet/kar | F özel (×1000/|ΔNFP_F|) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in ana:
        lines.append(
            f"| {r['senaryo']} | {r['F_ucret_kumul_milyar']} | {r['K_butce_NL_kumul_mutlak_milyar']} | "
            f"{r['maliyet_proxy_toplam_milyar']} | {r['kar_proxy_kapsama_milyar']} | "
            f"{r['maliyet_kar_orani']} | {r['F_maliyet_bine_delta_NFP_F']} |"
        )
    lines.extend(["", "## Alternatif kar proxy (isteğe bağlı)", ""])
    for r in ana:
        lines.append(
            f"- **{r['senaryo']}**: NFP_H Δ={r['kar_proxy_NFP_H_milyar']} milyar → maliyet/kar={r['maliyet_kar_orani_kar_NFP_H']}; "
            f"Ha servis düşüş={r['kar_proxy_Ha_servis_dusus']} → maliyet/kar={r['maliyet_kar_orani_kar_servis']}"
        )
    lines.extend(["", "## Duyarlılık özeti", ""])
    rev_d = [d for d in duy if d.get("tur") == "yasam_dusus_kosusu" and d["senaryo"] == "maliyet_ucuz_revize"]
    for d in rev_d:
        lines.append(
            f"- yaşam düşüş `{d.get('yasam_reel_dusus_yillik')}`: maliyet/kar={d.get('maliyet_kar_orani')}, "
            f"Δkapsama={d.get('delta_kapsama')}"
        )
    lines.extend(["", "## Ne denmez", "", "- Politika vaadi değil.", "- K′ ≠ tam kamu konsolidasyonu.", ""])
    return "\n".join(lines)


if __name__ == "__main__":
    main()
