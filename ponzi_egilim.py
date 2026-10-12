"""Ponzi bandı eğilimi — Ha servis/gelir proxy (uc_kural) + kademe fren senaryosu.

Ponzi fazlası (model): max(0, borc_servis_orani_Ha − ponzi_servis_esik) × 100 puan.
Eşik: 0,40 (`uc_kural_senaryo.Params`). Ölçüm değil; Minsky etiketi parametresidir.

Çalıştır: python3 ponzi_egilim.py
Çıktı: ponzi_egilim.csv, ponzi_egilim_sonuc.json, PONZI_EGILIM.md
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

KOK = Path(__file__).resolve().parent
PONZI_ESIK = 0.40
HEDGE_ESIK = 0.30
SENARYOLAR = ("mevcut", "uc_kural_kilitli", "maliyet_ucuz_revize")
# Kademe + donuk taban: hane tüketici/kart yıllık stok büyümesi proxy (acik_veri ~%43–46 → orta)
H_BUYUME_YILLIK = 0.45


def _csv(ad: str) -> list[dict]:
    return list(csv.DictReader((KOK / ad).open(encoding="utf-8-sig")))


def _band(s: float) -> str:
    if s <= HEDGE_ESIK:
        return "hedge"
    if s <= PONZI_ESIK:
        return "speculative"
    return "ponzi"


def _ponzi_fazlasi_pp(s: float) -> float:
    return max(0.0, s - PONZI_ESIK) * 100.0


def uc_kural_serileri() -> list[dict]:
    rows = []
    for r in _csv("uc_kural_senaryo.csv"):
        if r["senaryo"] not in SENARYOLAR:
            continue
        s = float(r["borc_servis_orani_Ha"])
        rows.append({
            "Donem": r["Donem"],
            "senaryo": r["senaryo"],
            "borc_servis_orani_Ha": round(s, 4),
            "ponzi_fazlasi_pp": round(_ponzi_fazlasi_pp(s), 2),
            "minsky_band": _band(s),
            "kaynak": "uc_kural_senaryo",
        })
    return rows


def kademe_ponzi_proxy(mevcut: dict[str, float]) -> list[dict]:
    """Mevcut senaryo servisi × kademe birikimli itiş çarpanı (donuk taban; uc_kural dışı)."""
    kad = {r["Donem"]: r for r in _csv("tek_sistem_kademe.csv")}
    gq = (1 + H_BUYUME_YILLIK) ** 0.25 - 1
    cum_b, cum_e = 1.0, 1.0
    rows = []
    for donem in sorted(kad.keys(), key=lambda d: (int(d[:4]), int(d[-1]))):
        k = kad[donem]
        baz = float(k["f4_net_yeni_baseline_milyar_ceyrek"])
        etk = float(k["f4_net_yeni_etkin_milyar_ceyrek"])
        carpan = etk / baz if baz > 0 else 1.0
        if donem >= "2027-Q1":
            cum_b *= 1 + gq
            cum_e *= 1 + gq * carpan
        oran = cum_e / cum_b if cum_b > 0 else 1.0
        s_m = mevcut.get(donem, 0.473)
        s = s_m * oran
        rows.append({
            "Donem": donem,
            "senaryo": "kademe_mevcut_taban_proxy",
            "borc_servis_orani_Ha": round(s, 4),
            "ponzi_fazlasi_pp": round(_ponzi_fazlasi_pp(s), 2),
            "minsky_band": _band(s),
            "kademe_carpan_ceyrek": round(carpan, 4),
            "kademe_birikim_oran": round(oran, 4),
            "kaynak": "tek_sistem_kademe",
        })
    return rows


def _egilim(seri: list[dict]) -> dict:
    if len(seri) < 2:
        return {}
    s0, s1 = seri[0], seri[-1]
    p0, p1 = s0["ponzi_fazlasi_pp"], s1["ponzi_fazlasi_pp"]
    n = len(seri) - 1
    return {
        "donem_bas": s0["Donem"],
        "donem_son": s1["Donem"],
        "servis_bas": s0["borc_servis_orani_Ha"],
        "servis_son": s1["borc_servis_orani_Ha"],
        "ponzi_fazlasi_pp_bas": p0,
        "ponzi_fazlasi_pp_son": p1,
        "ponzi_fazlasi_pp_delta": round(p1 - p0, 2),
        "ponzi_ceyrek_egim_pp": round((p1 - p0) / n, 3) if n else 0.0,
        "yon": "azalis" if p1 < p0 else ("sabit" if p1 == p0 else "artis"),
    }


def md(ozet: dict, all_rows: list[dict]) -> str:
    lines = [
        "# Ponzi fazlası eğilimi",
        "",
        "**Ponzi yüzdesi (bu dosyada):** `ponzi_fazlasi_pp` = servis/gelir proxy’sinin **%40 eşiğinin üstünde kalan kısmı** (puan).",
        "Tam oran `borc_servis_orani_Ha`; band: hedge ≤%30, speculative %30–40, ponzi etiketi >%40.",
        "",
        "Çalıştır: `python3 ponzi_egilim.py`. Kaynak: `uc_kural_senaryo.csv`, `tek_sistem_kademe.csv`.",
        "",
        "## Senaryo özeti (2026-Q4 → 2031-Q4)",
        "",
        "| Senaryo | Servis baş → son | Ponzi fazlası (pp) baş → son | Δ | Çeyrek eğim (pp/çeyrek) | Yön |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]
    for key, o in ozet.items():
        lines.append(
            f"| `{key}` | {o['servis_bas']:.3f} → {o['servis_son']:.3f} | "
            f"{o['ponzi_fazlasi_pp_bas']:.1f} → {o['ponzi_fazlasi_pp_son']:.1f} | "
            f"{o['ponzi_fazlasi_pp_delta']:+.1f} | {o['ponzi_ceyrek_egim_pp']:+.3f} | **{o['yon']}** |"
        )
    k = ozet.get("kademe_mevcut_taban_proxy", {})
    if k:
        lines += [
            "",
            "## Kademe freni proxy (`kademe_mevcut_taban_proxy`)",
            "",
            "Donuk taban (28 076 TL) + `tek_sistem_kademe` F4 itiş çarpanı → Ha stok büyümesi `%45` yıllık varsayım × çarpan. "
            "**uc_kural’a bağlı değil**; yalnız kademeli etkinin ponzi fazlasını aşağı çekme yönünü gösterir.",
            "",
            f"- Ponzi fazlası: **{k['ponzi_fazlasi_pp_bas']:.1f} → {k['ponzi_fazlasi_pp_son']:.1f} pp** ({k['yon']}, eğim {k['ponzi_ceyrek_egim_pp']:+.3f} pp/çeyrek).",
        ]
        for d in ("2027-Q4", "2029-Q4", "2031-Q4"):
            r = next(x for x in all_rows if x["senaryo"] == "kademe_mevcut_taban_proxy" and x["Donem"] == d)
            lines.append(
                f"- {d}: servis **{100 * r['borc_servis_orani_Ha']:.1f}%**, ponzi fazlası **{r['ponzi_fazlasi_pp']:.1f} pp**, band `{r['minsky_band']}`."
            )
    lines += [
        "",
        "## Okuma",
        "",
        "- **`mevcut` / `maliyet_ucuz_revize`:** ponzi fazlası **artış** (+11 pp civarı); servis ~%47 → ~%59 / ~%59.",
        "- **`uc_kural_kilitli`:** ponzi fazlası **sıfıra iner** (2031-Q4 servis %31,8 → speculative/hedge sınırında); eğim **−0,12 pp/çeyrek** (2026–2031).",
        "- **Kademe proxy (mevcut × birikimli itiş oranı):** ponzi fazlası mevcuta göre **daha yavaş artar** (eğim daha düşük); taban donukken tek başına sıfıra inmez — **azalış eğilimi** ancak `uc_kural_kilitli` ile gelir.",
        "",
        "## Ne denmez",
        "",
        "- “Ponzi yüzdesi ölçüldü” denmez; Ha ortalaması bilinmiyor (`MINSKY_GUNCEL_KARSILASTIRMA.md`).",
        "- Kademe satırı hane borcunu otomatik düşürmez; F4 çarpanı → Ha büyüme **varsayımı**.",
        "",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    uc = uc_kural_serileri()
    mevcut_map = {r["Donem"]: r["borc_servis_orani_Ha"] for r in uc if r["senaryo"] == "mevcut"}
    kad = kademe_ponzi_proxy(mevcut_map)
    all_rows = uc + kad
    ozet = {}
    for sen in SENARYOLAR:
        seri = [r for r in uc if r["senaryo"] == sen]
        ozet[sen] = _egilim(seri)
    ozet["kademe_mevcut_taban_proxy"] = _egilim(kad)

    alan = ["Donem", "senaryo", "borc_servis_orani_Ha", "ponzi_fazlasi_pp", "minsky_band", "kaynak"]
    extra = [a for a in kad[0].keys() if a not in alan]
    alan = alan + extra
    with (KOK / "ponzi_egilim.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=alan, extrasaction="ignore")
        w.writeheader()
        w.writerows(all_rows)

    out = {
        "ponzi_servis_esik": PONZI_ESIK,
        "hedge_servis_esik": HEDGE_ESIK,
        "ponzi_fazlasi_tanim": "max(0, borc_servis_orani_Ha - ponzi_esik) * 100 puan",
        "ozet": ozet,
        "kademe_h_buyume_yillik_varsayim": H_BUYUME_YILLIK,
    }
    (KOK / "ponzi_egilim_sonuc.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (KOK / "PONZI_EGILIM.md").write_text(md(ozet, all_rows), encoding="utf-8")
    print("=== ponzi_egilim ===")
    for k, o in ozet.items():
        print(f"  {k}: ponzi fazlasi {o['ponzi_fazlasi_pp_bas']:.1f} -> {o['ponzi_fazlasi_pp_son']:.1f} pp ({o['yon']}, egim {o['ponzi_ceyrek_egim_pp']:+.3f}/Q)")


if __name__ == "__main__":
    main()
