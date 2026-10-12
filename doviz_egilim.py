"""Döviz stoku eğilimi — ölçüm (brüt dış borç) + senaryo (korunmasız USD stok).

Çalıştır: python3 doviz_egilim.py
Çıktı: doviz_egilim.csv, doviz_egilim_sonuc.json, DOVIZ_EGILIM.md
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd

KOK = Path(__file__).resolve().parent
SENARYOLAR = ("mevcut", "uc_kural_kilitli", "maliyet_ucuz_revize")
OLCUM_EGILIM_BAS = "2023-Q4"  # rapor penceresi (EVDS mevcut seri 2000'den başlar)


def _csv_uc() -> list[dict]:
    rows = []
    for r in csv.DictReader((KOK / "uc_kural_senaryo.csv").open(encoding="utf-8-sig")):
        if r["senaryo"] not in SENARYOLAR:
            continue
        rows.append({
            "Donem": r["Donem"],
            "senaryo": r["senaryo"],
            "nesne": "korunmasiz_doviz_stok_mr_usd",
            "deger_milyar_usd": float(r["korunmasiz_doviz_stok_mr_usd"]),
            "kaynak": "uc_kural_senaryo",
            "durum": "senaryo",
        })
    return rows


def _brut_dis_borc() -> list[dict]:
    p = KOK / "dis_borc_ham.csv"
    if not p.exists():
        return []
    d = pd.read_csv(p, dtype={"Donem": str})
    seriler = {
        "Toplam": "TP.BRUTDBORCLU.G1",
        "Ozel": "TP.BRUTDBORCLU.G14",
        "Kamu": "TP.BRUTDBORCLU.G2",
        "TCMB": "TP.BRUTDBORCLU.G13",
    }
    rows = []
    for ad, seri in seriler.items():
        s = d[d.Seri == seri].copy()
        s["mr"] = s.Deger / 1000.0
        for _, row in s.sort_values("Donem").iterrows():
            rows.append({
                "Donem": row["Donem"],
                "senaryo": f"olcum_brut_dis_{ad.lower()}",
                "nesne": f"brut_dis_borc_{ad}",
                "deger_milyar_usd": round(float(row["mr"]), 3),
                "kaynak": "dis_borc_ham",
                "durum": "olculdu",
            })
    return rows


def _egilim(seri: list[dict], key: str = "deger_milyar_usd") -> dict | None:
    if len(seri) < 2:
        return None
    seri = sorted(seri, key=lambda x: (int(x["Donem"][:4]), int(x["Donem"][-1])))
    a, b = seri[0], seri[-1]
    n = len(seri) - 1
    dv = b[key] - a[key]
    return {
        "donem_bas": a["Donem"],
        "donem_son": b["Donem"],
        "deger_bas": a[key],
        "deger_son": b[key],
        "delta_milyar_usd": round(dv, 3),
        "ceyrek_egim": round(dv / n, 4) if n else 0.0,
        "yillik_egim_yaklasik": round(dv / max(1, (int(b["Donem"][:4]) - int(a["Donem"][:4]))), 4),
        "yon": "azalis" if dv < 0 else ("sabit" if dv == 0 else "artis"),
    }


def md(ozet: dict, rows: list[dict]) -> str:
    top = [r for r in rows if r["senaryo"] == "olcum_brut_dis_toplam" and r["Donem"] >= OLCUM_EGILIM_BAS]
    mev = [r for r in rows if r["senaryo"] == "mevcut"]
    kil = [r for r in rows if r["senaryo"] == "uc_kural_kilitli"]
    o = ozet.get("olcum_brut_dis_toplam", {})
    om = ozet.get("mevcut", {})
    ok = ozet.get("uc_kural_kilitli", {})
    lines = [
        "# Döviz stoku eğilimi",
        "",
        "İki ayrı nesne: **ölçüm** = TCMB brüt dış borç stoku (USD); **senaryo** = `D_korunmasiz_usd_mr` "
        "(korunmasız / hedge dışı proxy, milyar USD). Aynı satır değildir.",
        "",
        "Çalıştır: `python3 doviz_egilim.py`.",
        "",
        "## Ölçüm — brüt dış borç toplam (EVDS)",
        "",
    ]
    if o:
        lines += [
            f"- **{o['donem_bas']} → {o['donem_son']}:** {o['deger_bas']:.1f} → **{o['deger_son']:.1f} milyar USD** "
            f"(Δ **{o['delta_milyar_usd']:+.1f}**, eğim **{o['ceyrek_egim']:+.2f} mr USD/çeyrek**, **{o['yon']}**).",
            "- Özel sektör payı 2023-Q4 → 2026-Q2: "
            + _ozel_pay(top),
            "",
        ]
    lines += [
        "## Senaryo — korunmasız döviz stoku (`uc_kural_senaryo`)",
        "",
        "| Senaryo | 2026-Q4 → 2031-Q4 (mr USD) | Δ | Çeyrek eğim | Yön |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for sen in SENARYOLAR:
        e = ozet.get(sen)
        if not e:
            continue
        lines.append(
            f"| `{sen}` | {e['deger_bas']:.1f} → {e['deger_son']:.1f} | {e['delta_milyar_usd']:+.1f} | "
            f"{e['ceyrek_egim']:+.2f} | **{e['yon']}** |"
        )
    if om and ok:
        lines += [
            "",
            "### Okuma",
            "",
            f"- **`mevcut`:** `fx_unhedged_buyume_mevcut` ≈ **%6/yıl** → stok **{om['deger_bas']:.1f} → {om['deger_son']:.1f} mr USD** (artış eğilimi).",
            f"- **`uc_kural_kilitli` / `maliyet_ucuz_revize`:** segment tavanı **%0** + geri bildirim (stok artarsa **önceki çeyreğe geri al**) → **{ok['deger_son']:.1f} mr USD** bandında **sabit**.",
            "- **Kademe takvimi** (`tek_sistem_kademe`) döviz stokuna **doğrudan bağlı değil**; dolay etki yalnızca üç kural senaryosu üzerinden.",
            "- **Gerçek kişi YP mevduat** (adım 4): 2026-Q1 **6 639 milyar TL** karşılığı — **zaman serisi yok**; eğilim tabloya girilmedi.",
            "",
            "## Ne denmez",
            "",
            "- Brüt dış borç = korunmasız hane/firma stoku denmez.",
            "- Senaryo 120 mr USD = EVDS 539 mr USD toplam dış borç değildir (farklı tanım).",
            "",
        ]
    return "\n".join(lines) + "\n"


def _ozel_pay(top_rows: list[dict]) -> str:
    by = {r["Donem"]: r["deger_milyar_usd"] for r in top_rows}
    ozel = {r["Donem"]: r["deger_milyar_usd"] for r in _brut_dis_borc() if r["nesne"] == "brut_dis_borc_Ozel"}
    parts = []
    for d in ("2023-Q4", "2026-Q2"):
        if d in by and d in ozel and by[d]:
            parts.append(f"{d} **%{100 * ozel[d] / by[d]:.1f}**")
    return " → ".join(parts) if parts else "—"


def main() -> None:
    uc = _csv_uc()
    olcum = _brut_dis_borc()
    all_rows = uc + olcum
    ozet = {}
    for sen in SENARYOLAR:
        seri = [r for r in uc if r["senaryo"] == sen]
        ozet[sen] = _egilim(seri)
    for tag in ("olcum_brut_dis_toplam", "olcum_brut_dis_ozel"):
        seri = [r for r in olcum if r["senaryo"] == tag and r["Donem"] >= OLCUM_EGILIM_BAS]
        ozet[tag] = _egilim(seri)

    alan = ["Donem", "senaryo", "nesne", "deger_milyar_usd", "kaynak", "durum"]
    with (KOK / "doviz_egilim.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=alan)
        w.writeheader()
        w.writerows(all_rows)

    meta = {
        "nesneler": {
            "olcum": "EVDS TP.BRUTDBORCLU.G1 (brüt dış borç toplam, milyar USD)",
            "senaryo": "uc_kural D_korunmasiz_usd_mr (VARSAYIM başlangıç 120)",
        },
        "ozet": ozet,
    }
    (KOK / "doviz_egilim_sonuc.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (KOK / "DOVIZ_EGILIM.md").write_text(md(ozet, all_rows), encoding="utf-8")
    print("=== doviz_egilim ===")
    if ozet.get("olcum_brut_dis_toplam"):
        o = ozet["olcum_brut_dis_toplam"]
        print(f"  olcum toplam: {o['deger_bas']} -> {o['deger_son']} mr USD ({o['yon']})")
    for sen in SENARYOLAR:
        e = ozet.get(sen)
        if e:
            print(f"  {sen}: {e['deger_bas']} -> {e['deger_son']} mr USD ({e['yon']})")


if __name__ == "__main__":
    main()
