"""Eski gelir düzeyine dönüş yılı — rant_aktor uzantısı.

dönüş yılı = rant_kayip / yıllık_rant_dışı_gelir_artışı (milyar TL).
Senaryo; ölçüm değil. Rant dışı büyüme VARSAYIM.

Çalıştır: python3 rant_donus_yili.py  (rant_aktor.csv yoksa rant_aktor.main())
Çıktı: rant_aktor_donus.csv, rant_donus_yili_duyarlik.csv, rant_donus_yili_sonuc.json, RANT_DONUS_YILI.md
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

from hane_alt import N_A as N_A_DEFAULT
from rant_aktor import AKTORLER, KOK, SENARYOLAR, RantAktorParams, hesapla as rant_hesapla
from uc_kural_senaryo import SENARYOLAR as UC_SEN

SON = "2031-Q4"
BAS = "2026-Q4"
SURESIZ = "telafi yok / süresiz"


@dataclass
class DonusParams:
    reel_buyume_H: float = 0.04  # VARSAYIM %3–5 bandı ortası
    reel_buyume_F: float = 0.05  # VARSAYIM %4–6
    reel_buyume_B: float = 0.03  # VARSAYIM %2–4
    reel_buyume_K: float = 0.02  # VARSAYIM ikincil
    ho_agirlik_H: float = 0.80  # Ho ağırlıklı ücret tabanı, VARSAYIM
    f_zarf_katsayi: float = 0.35  # üretken zarf → faaliyet kârı artışı, VARSAYIM
    yasam_tasarruf_H_payi: float = 0.45  # yaşam sepet düşüşünün H gelirine yansıması, VARSAYIM
    ufuk_yil: float = 5.0
    n_a: float = N_A_DEFAULT


def _mk_map() -> dict[str, dict]:
    p = KOK / "maliyet_kar_orani.csv"
    if not p.exists():
        from maliyet_kar_orani import main as mm

        mm()
    return {r["senaryo"]: r for r in pd.read_csv(p).to_dict("records")}


def _uc_end_base() -> tuple[dict[str, dict], dict[str, dict]]:
    p = KOK / "uc_kural_senaryo.csv"
    if not p.exists():
        from uc_kural_senaryo import main as um

        um()
    df = pd.read_csv(p)
    end, base = {}, {}
    for sen in UC_SEN:
        sub = df[df.senaryo == sen]
        end[sen] = sub[sub.Donem == SON].iloc[0].to_dict()
        base[sen] = sub[sub.Donem == BAS].iloc[0].to_dict()
    return end, base


def _reel_oran(akt: str, p: DonusParams) -> float:
    return {"H": p.reel_buyume_H, "F": p.reel_buyume_F, "B": p.reel_buyume_B, "K": p.reel_buyume_K}[akt]


def yillik_rant_dis_artis(
    akt: str,
    sen: str,
    faaliyet_proxy: float,
    mk: dict,
    uc_end: dict,
    uc_bas: dict,
    p: DonusParams,
) -> tuple[float, str]:
    """Yıllık rant dışı gelir artışı (milyar TL) ve kısa not."""
    reel = _reel_oran(akt, p)
    taban = faaliyet_proxy
    if akt == "H":
        taban = faaliyet_proxy * p.ho_agirlik_H
    duz = taban * reel
    ek = 0.0
    notlar = [f"reel %{reel*100:.0f}×taban {taban:.1f}"]
    if akt == "H":
        ek += float(mk.get("kar_proxy_kapsama_yasam_agirlikli_milyar", 0) or 0)
        yas_d = float(uc_bas.get("yasam_maliyeti_TL", 0)) - float(uc_end.get("yasam_maliyeti_TL", 0))
        if yas_d > 0:
            yas_yillik = yas_d * p.n_a / 1e9 / p.ufuk_yil
            ek += yas_yillik * p.yasam_tasarruf_H_payi
            notlar.append(f"yasam_tasarruf {yas_yillik*p.yasam_tasarruf_H_payi:.1f}")
        if ek:
            notlar.append(f"kapsama_proxy {float(mk.get('kar_proxy_kapsama_yasam_agirlikli_milyar',0) or 0):.1f}")
    elif akt == "F":
        dz = float(uc_end.get("uretken_zarf_payi", 0)) - float(uc_bas.get("uretken_zarf_payi", 0))
        if dz > 0:
            ek += taban * dz * p.f_zarf_katsayi
            notlar.append(f"zarf×{dz:.2f}")
    elif akt == "K":
        k_nl = abs(float(mk.get("K_butce_NL_kumul_mutlak_milyar", 0) or 0))
        if k_nl > 0:
            ek += k_nl / p.ufuk_yil
            notlar.append(f"butce_kanal {k_nl/p.ufuk_yil:.1f}")
    toplam = duz + ek
    return round(toplam, 2), "; ".join(notlar)


def _donus_yili(kayip: float, artis: float) -> tuple[float | None, str]:
    if kayip <= 0:
        return 0.0, "0"
    if artis <= 0:
        return None, SURESIZ
    yil = round(kayip / artis, 2)
    return yil, str(yil)


def enrich_rows(
    rant_rows: list[dict],
    meta: dict,
    dp: DonusParams | None = None,
) -> list[dict]:
    dp = dp or DonusParams()
    mk = _mk_map()
    uc_end, uc_bas = _uc_end_base()
    out = []
    for r in rant_rows:
        row = dict(r)
        if row.get("aktor") == "TOPLAM" or row.get("aktor") not in AKTORLER:
            out.append(row)
            continue
        akt = row["aktor"]
        sen = row["senaryo"]
        faal = float(row.get("faaliyet_proxy_milyar") or 0)
        kayip = float(row.get("rant_kayip_ufuk_milyar") or 0)
        artis, artis_not = yillik_rant_dis_artis(akt, sen, faal, mk[sen], uc_end[sen], uc_bas[sen], dp)
        yil, yil_str = _donus_yili(kayip, artis)
        row["yillik_rant_dis_gelir_artisi_milyar"] = artis
        row["rant_dis_artis_not"] = artis_not
        row["eski_gelir_donus_yili"] = yil_str
        row["eski_gelir_donus_yili_sayisal"] = yil
        out.append(row)
    return out


def _duyarlik_buyume(rant_rows: list[dict], meta: dict) -> list[dict]:
    out = []
    for g in (0.02, 0.03, 0.05):
        dp = DonusParams(reel_buyume_H=g, reel_buyume_F=g, reel_buyume_B=g, reel_buyume_K=g)
        en = enrich_rows(rant_rows, meta, dp)
        for sen in ("uc_kural_kilitli", "maliyet_ucuz_revize"):
            for akt in AKTORLER:
                r = next(x for x in en if x["senaryo"] == sen and x["aktor"] == akt)
                out.append(
                    {
                        "rant_dis_reel_oran_hepsi": g,
                        "senaryo": sen,
                        "aktor": akt,
                        "eski_gelir_donus_yili": r.get("eski_gelir_donus_yili"),
                        "yillik_rant_dis_gelir_artisi_milyar": r.get("yillik_rant_dis_gelir_artisi_milyar"),
                    }
                )
    return out


def hesapla_tam(dp: DonusParams | None = None) -> tuple[list[dict], list[dict], dict]:
    rp = RantAktorParams(ufuk_yil=(dp or DonusParams()).ufuk_yil, n_a=(dp or DonusParams()).n_a)
    rant_rows, _, meta = rant_hesapla(rp)
    dp = dp or DonusParams()
    rows = enrich_rows(rant_rows, meta, dp)
    duy = _duyarlik_buyume(rant_rows, meta)
    meta2 = {
        **meta,
        "donus_tanim": "rant_kayip_ufuk / yillik_rant_dis_gelir_artisi",
        "donus_parametreler": asdict(dp),
        "uyari": "Senaryo; ölçüm değil. Dönüş yılı rant dışı büyüme varsayımına bağlıdır.",
    }
    return rows, duy, meta2


def _md(rows: list[dict]) -> str:
    lines = [
        "# Eski gelir düzeyine dönüş yılı (rant kanalı)",
        "",
        "**Senaryo; ölçüm değil.** Payda: ücret/kapsama/yasam tasarrufu (H), faaliyet+zarf (F), faaliyet (B), vergi/transfer (K) — hepsi VARSAYIM reel büyüme ile.",
        "",
        "| Senaryo | Aktör | Rant kayıp | Rant direnci % | Amorti Δ | **Dönüş yılı** | Rant dışı artış (milyar/yıl) |",
        "| --- | --- | ---: | ---: | ---: | --- | ---: |",
    ]
    for sen in SENARYOLAR:
        for akt in list(AKTORLER) + ["TOPLAM"]:
            r = next((x for x in rows if x["senaryo"] == sen and x["aktor"] == akt), None)
            if not r:
                continue
            if akt == "TOPLAM":
                lines.append(f"| {sen} | TOPLAM | | {r.get('rant_direnci_yuzde','')} | | | |")
                continue
            lines.append(
                f"| {sen} | {akt} | {r.get('rant_kayip_ufuk_milyar')} | {r.get('rant_direnci_yuzde')} | "
                f"{r.get('kar_amorti_dusus_puan')} | **{r.get('eski_gelir_donus_yili')}** | "
                f"{r.get('yillik_rant_dis_gelir_artisi_milyar')} |"
            )
    lines.extend(
        [
            "",
            "## Revize vs sert (H)",
            "",
            "Revize kira kaybı büyük, ücret/kapsama kazancı sınırlı → **H dönüş yılı en uzun**. Sert H rantı korunduğu için kayıp düşük → dönüş kısa veya 0.",
            "",
            "Duyarlılık: tüm aktörlerde rant dışı reel büyüme %2 / %3 / %5 → `rant_donus_yili_duyarlik.csv`.",
            "",
            "## Ne denmez",
            "",
            "- Kira arzı artmazsa H gerçek süresi daha uzun olabilir.",
            "- Dönüş yılı ölçülen gelir geri kazanım süresi değildir.",
            "",
        ]
    )
    return "\n".join(lines)


def main():
    if not (KOK / "rant_aktor.csv").exists():
        from rant_aktor import main as rm

        rm()
    rows, duy, meta = hesapla_tam()
    all_cols = sorted({k for r in rows for k in r.keys()})
    with (KOK / "rant_aktor_donus.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=all_cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    with (KOK / "rant_donus_yili_duyarlik.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(duy[0].keys()))
        w.writeheader()
        w.writerows(duy)
    (KOK / "rant_donus_yili_sonuc.json").write_text(
        json.dumps({"meta": meta, "satirlar": rows, "duyarlik": duy}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (KOK / "RANT_DONUS_YILI.md").write_text(_md(rows), encoding="utf-8")
    # rant_aktor.csv güncelle (aynı satırlar + dönüş sütunları)
    with (KOK / "rant_aktor.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=all_cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print("=== rant_donus_yili (senaryo; ölçüm değil) ===")
    for sen in ("uc_kural_kilitli", "maliyet_ucuz_revize"):
        h = next(r for r in rows if r["senaryo"] == sen and r["aktor"] == "H")
        print(sen, "H_donus_yili", h["eski_gelir_donus_yili"], "kayip", h["rant_kayip_ufuk_milyar"])


if __name__ == "__main__":
    main()
