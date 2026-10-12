"""Karşı çıkabilecek aktörler — ekonomik hesap direnci (rant kanalı değil).

Senaryo; ölçüm değil. Stok-akış + gelir tablosu kalemleri; lobi bağımsız.
`direnc_yuzdesi.py` / `rant_aktor.py` ile aynı dosyayı kullanmaz; kira/rant etiketi yok.

Girdi: uc_kural_senaryo.csv, maliyet_kar_orani.csv (yoksa üretilir).
Çıktı: direnc_ekonomik.csv, direnc_ekonomik_kalem.csv, direnc_ekonomik_duyarlik.csv,
        direnc_ekonomik_sonuc.json, DIRENC_EKONOMIK.md

Çalıştır: python3 direnc_ekonomik.py
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

from direnc_yuzdesi import _stok_proxies, _uc_row
from hane_alt import ASGARI, N_A as N_A_DEFAULT
from maliyet_kar_orani import OLCULEN_FINANSMAN_FAALIYET
from uc_kural_senaryo import SENARYOLAR

KOK = Path(__file__).resolve().parent
SON = "2031-Q4"
MEVCUT = "mevcut"
AKTORLER = ("H", "F", "B", "K")
HO = "Ho"


@dataclass
class DirencEkonomikParams:
    agirlik_H: float = 0.35
    agirlik_F: float = 0.30
    agirlik_B: float = 0.20
    agirlik_K: float = 0.15
    ufuk_yil: float = 5.0
    n_a: float = N_A_DEFAULT
    ho_varlik_payi: float = 0.80
    ust_gelir_erosyon_katsayi: float = 0.55
    emlak_gelir_orani_yillik: float = 0.035  # konut stok × oran; emlak gelir akışı proxy
    emlak_yasam_elastikiyet: float = 1.0
    finans_kisit_katsayi: float = 0.08  # üretken zarf daralması × finansman hacmi
    fin_F_pay: float = 0.55
    fin_B_pay: float = 0.35
    fin_H_pay: float = 0.10
    b_nim_yillik: float = 0.028
    k_harcama_yillik_milyar: float = 8000.0  # bütçe ölçeği VARSAYIM
    k_makas_milyar_ceyrek: float = 45.0  # revize makas transferi, uc_kural ile uyumlu
    k_makas_ust_dilim: float = 0.35
    limit_kredi_ceyrek_milyar: float = 420.0  # limit_dondur açıkken çeyreklik kredi hacmi proxy
    nfp_kayip_katsayi: float = 1.0  # |ΔNFP| kötüleşme → kayıp (milyar)
    direnc_yuksek_esik: float = 0.35


def _load_inputs() -> tuple[list[dict], list[dict], pd.DataFrame]:
    p_uc = KOK / "uc_kural_senaryo.csv"
    p_mk = KOK / "maliyet_kar_orani.csv"
    if not p_uc.exists():
        from uc_kural_senaryo import run

        run()
    if not p_mk.exists():
        from maliyet_kar_orani import main as mk_main

        mk_main()
    uc = pd.read_csv(p_uc)
    mk = pd.read_csv(p_mk).to_dict("records")
    return uc.to_dict("records"), mk, uc


def _limit_ceyrek_sayisi(uc_df: pd.DataFrame, senaryo: str) -> int:
    sub = uc_df[(uc_df["senaryo"] == senaryo) & (uc_df["Donem"] >= "2026-Q4")]
    return int(sub["limit_dondur"].fillna(0).astype(int).sum())


def _nfp_kayip(delta: float) -> float:
    """ΔNFP = senaryo − mevcut; sektör için negatif Δ ekonomik kötüleşme proxy."""
    return max(0.0, -delta) * 1.0


def _faaliyet_ufuk(stok: dict, p: DirencEkonomikParams) -> dict[str, float]:
    fin = OLCULEN_FINANSMAN_FAALIYET[2024]["finansman_milyarTL"]
    faal_f = OLCULEN_FINANSMAN_FAALIYET[2024]["faaliyet_kari_milyarTL"]
    h_gelir = p.n_a * ASGARI * 12 / 1e9
    b_gelir = stok["B_varlik_milyarTL"] * p.b_nim_yillik
    k_gelir = p.k_harcama_yillik_milyar
    u = p.ufuk_yil
    return {
        "H": round(h_gelir * u, 2),
        "F": round((faal_f + fin) * u, 2),
        "B": round(b_gelir * u, 2),
        "K": round(k_gelir * u, 2),
    }


def _kalemler_aktore(
    sen: str,
    u: dict,
    m: dict,
    base_u: dict,
    base_yasam: float,
    stok: dict,
    limit_q: int,
    p: DirencEkonomikParams,
) -> tuple[dict[str, float], list[dict]]:
    yasam = float(u["yasam_maliyeti_TL"])
    d_yasam = max(0.0, (base_yasam - yasam) / base_yasam) if base_yasam else 0.0
    d_kap = float(m.get("delta_kapsama", 0))

    emlak_kayip = (
        stok["konut_stok_milyarTL"] * p.emlak_gelir_orani_yillik * d_yasam * p.emlak_yasam_elastikiyet * p.ufuk_yil
    )
    gelir_dilim = max(0.0, d_kap) * yasam * p.n_a / 1e9 * p.ho_varlik_payi * p.ust_gelir_erosyon_katsayi
    kredi_kisit = limit_q * p.limit_kredi_ceyrek_milyar

    base_uretken = float(base_u["uretken_zarf_payi"])
    uretken = float(u["uretken_zarf_payi"])
    d_uretken_daralma = max(0.0, base_uretken - uretken)
    fin_yillik = OLCULEN_FINANSMAN_FAALIYET[2024]["finansman_milyarTL"]
    finans_hacim_kaybi = d_uretken_daralma * fin_yillik * p.ufuk_yil * p.finans_kisit_katsayi

    ucret_yuku = max(0.0, float(m.get("F_ucret_kumul_milyar", 0)))
    k_butce_kumul = float(m.get("K_butce_NL_kumul_milyar", 0))
    butce_kaybi = max(0.0, -k_butce_kumul)

    n_ceyrek_makas = int(p.ufuk_yil * 4) if sen == "maliyet_ucuz_revize" else 0
    makas_kaybi = n_ceyrek_makas * p.k_makas_milyar_ceyrek * p.k_makas_ust_dilim * 0.25

    nfp_d = {a: float(u[f"NFP_{a}"]) - float(base_u[f"NFP_{a}"]) for a in ("H", "F", "B", "K")}

    h_kayip = (
        gelir_dilim
        + emlak_kayip
        + kredi_kisit
        + p.fin_H_pay * finans_hacim_kaybi
        + p.nfp_kayip_katsayi * _nfp_kayip(nfp_d["H"])
    )
    f_kayip = ucret_yuku + p.fin_F_pay * finans_hacim_kaybi + p.nfp_kayip_katsayi * _nfp_kayip(nfp_d["F"])
    b_kayip = p.fin_B_pay * finans_hacim_kaybi + p.nfp_kayip_katsayi * _nfp_kayip(nfp_d["B"])
    k_kayip = butce_kaybi + makas_kaybi + p.nfp_kayip_katsayi * _nfp_kayip(nfp_d["K"])

    by_aktor = {"H": h_kayip, "F": f_kayip, "B": b_kayip, "K": k_kayip}
    long = []
    kalem_map = {
        "H": [
            ("gelir_dilim_kaybi_milyar", gelir_dilim),
            ("emlak_gelir_dususu_milyar", emlak_kayip),
            ("kredi_hacmi_kisit_milyar", kredi_kisit),
            ("finansman_hacmi_kaybi_milyar", p.fin_H_pay * finans_hacim_kaybi),
            ("NFP_kotulesme_milyar", p.nfp_kayip_katsayi * _nfp_kayip(nfp_d["H"])),
        ],
        "F": [
            ("ucret_yuku_milyar", ucret_yuku),
            ("finansman_hacmi_kaybi_milyar", p.fin_F_pay * finans_hacim_kaybi),
            ("NFP_kotulesme_milyar", p.nfp_kayip_katsayi * _nfp_kayip(nfp_d["F"])),
        ],
        "B": [
            ("finansman_hacmi_kaybi_milyar", p.fin_B_pay * finans_hacim_kaybi),
            ("NFP_kotulesme_milyar", p.nfp_kayip_katsayi * _nfp_kayip(nfp_d["B"])),
        ],
        "K": [
            ("butce_NL_kaybi_milyar", butce_kaybi),
            ("makas_transfer_kaybi_milyar", makas_kaybi),
            ("NFP_kotulesme_milyar", p.nfp_kayip_katsayi * _nfp_kayip(nfp_d["K"])),
        ],
    }
    for akt, items in kalem_map.items():
        for kalem, val in items:
            long.append(
                {
                    "senaryo": sen,
                    "aktor": akt,
                    "kalem": kalem,
                    "kayip_milyar": round(val, 2),
                    "durum": "senaryo",
                }
            )
    long.append(
        {
            "senaryo": sen,
            "aktor": HO,
            "kalem": "gelir_dilim_kaybi_milyar",
            "kayip_milyar": round(gelir_dilim, 2),
            "durum": "senaryo",
        }
    )
    long.append(
        {
            "senaryo": sen,
            "aktor": HO,
            "kalem": "emlak_gelir_dususu_milyar",
            "kayip_milyar": round(emlak_kayip, 2),
            "durum": "senaryo",
        }
    )
    return {k: round(v, 2) for k, v in by_aktor.items()}, long


def hesapla(p: DirencEkonomikParams | None = None) -> tuple[list[dict], list[dict], dict]:
    p = p or DirencEkonomikParams()
    rows_uc, mk_rows, uc_df = _load_inputs()
    mk = {r["senaryo"]: r for r in mk_rows}
    stok = _stok_proxies()
    faal = _faaliyet_ufuk(stok, p)
    base_u = _uc_row(rows_uc, MEVCUT)
    base_yasam = float(base_u["yasam_maliyeti_TL"])
    agirlik = {"H": p.agirlik_H, "F": p.agirlik_F, "B": p.agirlik_B, "K": p.agirlik_K}

    out: list[dict] = []
    kalem_all: list[dict] = []

    for sen in SENARYOLAR:
        u = _uc_row(rows_uc, sen)
        m = mk[sen]
        limit_q = _limit_ceyrek_sayisi(uc_df, sen)
        kayip, kalemler = _kalemler_aktore(sen, u, m, base_u, base_yasam, stok, limit_q, p)
        kalem_all.extend(kalemler)
        nfp_d = {a: round(float(u[f"NFP_{a}"]) - float(base_u[f"NFP_{a}"]), 2) for a in ("H", "F", "B", "K")}
        direnc_ag = 0.0
        for akt in AKTORLER:
            payda = max(abs(nfp_d[akt]), faal[akt], 1.0)
            direnc = round(100 * kayip[akt] / payda, 2)
            direnc_ag += agirlik[akt] * direnc
            out.append(
                {
                    "senaryo": sen,
                    "donem": SON,
                    "aktor": akt,
                    "durum": "senaryo",
                    "kayip_toplam_milyar": kayip[akt],
                    "faaliyet_ufuk_milyar": faal[akt],
                    "payda_milyar": round(payda, 2),
                    "NFP_delta_milyar": nfp_d[akt],
                    "direnc_ekonomik_yuzde": direnc,
                    "limit_dondur_ceyrek": limit_q,
                    "F_ucret_kumul_milyar": float(m.get("F_ucret_kumul_milyar", 0)),
                    "K_butce_NL_kumul_milyar": float(m.get("K_butce_NL_kumul_milyar", 0)),
                    "not": "Ekonomik kalem; rant/kira etiketi kullanılmaz",
                }
            )
        out.append(
            {
                "senaryo": sen,
                "donem": SON,
                "aktor": "TOPLAM",
                "durum": "senaryo",
                "direnc_ekonomik_yuzde": round(direnc_ag, 2),
                "kayip_toplam_milyar": round(sum(kayip.values()), 2),
                "agirlik_not": "H35 F30 B20 K15",
            }
        )

    meta = {
        "durum": "senaryo",
        "olcum_degil": True,
        "rant_kanali_degil": True,
        "tanim": "direnc_ekonomik_% = aktör ekonomik kayıp / max(|ΔNFP|, faaliyet×ufuk_yil)",
        "karsı_aktor_tanimi": {
            "H": "Hazne H: üst dilim gelir + emlak gelir akışı + kredi hacmi (limit)",
            "Ho": "H içi üst dilim; gelir_dilim + emlak gelir düşüşü",
            "F": "Kurumsal F: ücret yükü (NL kanalı) + finansman hacmi + NFP",
            "B": "Bankacılık B: finansman hacmi payı + NFP",
            "K": "Kamu K′: bütçe NL kaybı + makas transfer (revize)",
        },
        "olculen_referans_F_2024": OLCULEN_FINANSMAN_FAALIYET[2024],
        "parametreler": asdict(p),
        "stok_proxy": stok,
        "faaliyet_ufuk_baseline": faal,
        "iliski_direnc_yuzdesi": "Paralel okuma; direnc_yuzdesi rant/kira kalemleri kullanır, bu modül kullanmaz.",
    }
    return out, kalem_all, meta


def _duyarlik() -> list[dict]:
    grid = []
    for ho in (0.70, 0.80, 0.90):
        for el in (0.8, 1.0, 1.2):
            p = DirencEkonomikParams(ho_varlik_payi=ho, emlak_yasam_elastikiyet=el)
            rows, _, _ = hesapla(p)
            rev = next(r for r in rows if r["senaryo"] == "maliyet_ucuz_revize" and r["aktor"] == "H")
            tot = next(r for r in rows if r["senaryo"] == "maliyet_ucuz_revize" and r["aktor"] == "TOPLAM")
            grid.append(
                {
                    "ho_varlik_payi": ho,
                    "emlak_yasam_elastikiyet": el,
                    "H_direnc_ekonomik": rev["direnc_ekonomik_yuzde"],
                    "toplam_direnc_ekonomik": tot["direnc_ekonomik_yuzde"],
                    "H_kayip_milyar": rev["kayip_toplam_milyar"],
                }
            )
    return grid


def _md(meta: dict, rows: list[dict]) -> str:
    ref = meta["olculen_referans_F_2024"]
    lines = [
        "# Ekonomik direnç (aktör × senaryo)",
        "",
        "**Senaryo; ölçüm değil.** Rant/kira kanalı yok; stok-akış ve gelir tablosu proxy.",
        "",
        f"Tanım: {meta['tanim']}",
        "",
        f"F faaliyet/finansman referansı (ölçüm, senaryo değil): **{ref['oran']}** (2024).",
        "",
        "## Karşı aktörler (2031-Q4, mevcuta göre kayıp)",
        "",
        "| Senaryo | Aktör | Kayıp (milyar) | Payda | **Direnç ekonomik %** |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for sen in SENARYOLAR:
        for akt in AKTORLER:
            r = next(x for x in rows if x["senaryo"] == sen and x["aktor"] == akt)
            lines.append(
                f"| {sen} | {akt} | {r.get('kayip_toplam_milyar')} | {r.get('payda_milyar')} | "
                f"{r.get('direnc_ekonomik_yuzde')} |"
            )
    lines.extend(["", "## Toplam ağırlıklı direnç", ""])
    for sen in SENARYOLAR:
        t = next(r for r in rows if r["senaryo"] == sen and r["aktor"] == "TOPLAM")
        lines.append(f"- **{sen}**: {t.get('direnc_ekonomik_yuzde')}%")
    lines.extend(
        [
            "",
            "## Kalemler (özet)",
            "",
            "- **H**: gelir_dilim, emlak_gelir_dususu, kredi_hacmi_kisit, finansman_hacmi, NFP_kotulesme",
            "- **F**: ucret_yuku, finansman_hacmi, NFP_kotulesme",
            "- **B**: finansman_hacmi, NFP_kotulesme",
            "- **K**: butce_NL_kaybi, makas_transfer (revize), NFP_kotulesme",
            "",
            "## Revize vs sert (yorum)",
            "",
            "Sert yol **F ücret yükünü** ve **H kredi kısıt çeyreklerini** büyütür → F/H direnç ekonomik payı yükselir. "
            "Revize yol **emlak/gelir dilimi** kaybını ve **K makas** kalemini öne çıkarır; F ücret yükü görece düşük kalır.",
            "",
            f"`direnc_yuzdesi.py` ile karşılaştırma: {meta['iliski_direnc_yuzdesi']}",
            "",
            "## Ne denmez",
            "",
            "- Rant amortisman oranı veya kira ranti hesabı değildir (`rant_aktor.py` ayrı).",
            "- Lobi gücü / seçim modeli değildir.",
            "",
        ]
    )
    return "\n".join(lines)


def main():
    rows, kalemler, meta = hesapla()
    duy = _duyarlik()
    all_cols = sorted({k for r in rows for k in r.keys()})
    with (KOK / "direnc_ekonomik.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=all_cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    with (KOK / "direnc_ekonomik_kalem.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["senaryo", "aktor", "kalem", "kayip_milyar", "durum"])
        w.writeheader()
        w.writerows(kalemler)
    with (KOK / "direnc_ekonomik_duyarlik.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(duy[0].keys()))
        w.writeheader()
        w.writerows(duy)
    (KOK / "direnc_ekonomik_sonuc.json").write_text(
        json.dumps({"meta": meta, "satirlar": rows, "duyarlik": duy}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (KOK / "DIRENC_EKONOMIK.md").write_text(_md(meta, rows), encoding="utf-8")
    print("=== direnc_ekonomik (senaryo; rant kanalı değil) ===")
    for sen in SENARYOLAR:
        tot = next(r for r in rows if r["senaryo"] == sen and r["aktor"] == "TOPLAM")
        print(sen, "toplam_direnc_ekonomik%", tot.get("direnc_ekonomik_yuzde"))


if __name__ == "__main__":
    main()
