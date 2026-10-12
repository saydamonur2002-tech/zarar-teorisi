"""Hane etkisi — model çerçevesinde kanal özeti (senaryo + ölçüm sınırı).

Birleştirmez: katman sonuçları taşınmaz; bu dosya yalnızca mevcut çıktıları hane dilinde hizalar.

Çalıştır: python3 hane_model_etki.py
Çıktı: hane_model_etki.csv, hane_model_etki_sonuc.json, HANE_MODEL_ETKI.md
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

KOK = Path(__file__).resolve().parent
SENARYOLAR = ("mevcut", "uc_kural_kilitli", "maliyet_ucuz_revize")
DONEMLER = ("2026-Q4", "2031-Q4")
PONZI_ESIK = 0.40
HEDGE_ESIK = 0.30


def _load_json(name: str) -> dict:
    return json.loads((KOK / name).read_text(encoding="utf-8"))


def _uc_rows() -> list[dict]:
    return list(csv.DictReader((KOK / "uc_kural_senaryo.csv").open(encoding="utf-8-sig")))


def _band(s: float) -> str:
    if s <= HEDGE_ESIK:
        return "hedge"
    if s <= PONZI_ESIK:
        return "speculative"
    return "ponzi"


def _satirlar() -> list[dict]:
    uc = _uc_rows()
    out: list[dict] = []
    for sen in SENARYOLAR:
        for d in DONEMLER:
            r = next(x for x in uc if x["senaryo"] == sen and x["Donem"] == d)
            s = float(r["borc_servis_orani_Ha"])
            out.extend([
                {"Donem": d, "senaryo": sen, "kanal": "gelir_taban", "gosterge": "net_taban_TL",
                 "deger": float(r["net_taban_TL"]), "birim": "TL/ay", "kaynak": "uc_kural_senaryo"},
                {"Donem": d, "senaryo": sen, "kanal": "gelir_taban", "gosterge": "kapsama",
                 "deger": float(r["kapsama"]), "birim": "oran", "kaynak": "uc_kural_senaryo"},
                {"Donem": d, "senaryo": sen, "kanal": "gelir_taban", "gosterge": "yasam_maliyeti_TL",
                 "deger": float(r["yasam_maliyeti_TL"]), "birim": "TL/ay", "kaynak": "uc_kural_senaryo"},
                {"Donem": d, "senaryo": sen, "kanal": "borc_stok", "gosterge": "NFP_H",
                 "deger": float(r["NFP_H"]), "birim": "milyar TL (NFP)", "kaynak": "uc_kural_senaryo"},
                {"Donem": d, "senaryo": sen, "kanal": "servis_Ha", "gosterge": "borc_servis_orani_Ha",
                 "deger": s, "birim": "oran", "kaynak": "uc_kural_senaryo"},
                {"Donem": d, "senaryo": sen, "kanal": "servis_Ha", "gosterge": "ponzi_fazlasi_pp",
                 "deger": round(max(0.0, s - PONZI_ESIK) * 100, 2), "birim": "puan", "kaynak": "türetilmiş"},
                {"Donem": d, "senaryo": sen, "kanal": "servis_Ha", "gosterge": "minsky_band",
                 "deger": _band(s), "birim": "etiket", "kaynak": "uc_kural eşik"},
                {"Donem": d, "senaryo": sen, "kanal": "kredi_freni", "gosterge": "limit_dondur",
                 "deger": int(r["limit_dondur"]), "birim": "0/1", "kaynak": "uc_kural_senaryo"},
                {"Donem": d, "senaryo": sen, "kanal": "doviz_dolay", "gosterge": "korunmasiz_doviz_stok_mr_usd",
                 "deger": float(r["korunmasiz_doviz_stok_mr_usd"]), "birim": "milyar USD", "kaynak": "uc_kural_senaryo"},
                {"Donem": d, "senaryo": sen, "kanal": "butce_dolay", "gosterge": "K_butce_NL_milyar",
                 "deger": float(r["K_butce_NL_milyar"]), "birim": "milyar TL/çeyrek", "kaynak": "uc_kural_senaryo"},
            ])
    # ölçüm / alt hazne (tek dönem)
    ha = _load_json("akis_model_ozeti.json").get("hane_alt", {})
    ht = ha.get("H_toplam_2026Q1_trilyonTL", {})
    for grup, v in ha.get("taban_NFP_trilyonTL", {}).items():
        out.append({"Donem": "2026-Q1", "senaryo": "olcum_panel", "kanal": "hane_alt",
                    "gosterge": f"NFP_{grup}", "deger": v["NFP"], "birim": "trilyon TL", "kaynak": "hane_alt"})
    out.append({"Donem": "2026-Q1", "senaryo": "olcum_panel", "kanal": "hane_alt",
                "gosterge": "Ha_tasima_kapasitesi", "deger": ha.get("tasima_kapasitesi_trilyonTL", {}).get("Ha_asgari"),
                "birim": "trilyon TL", "kaynak": "hane_alt"})
    tak = ha.get("gozlenen_hane_stresi_trilyonTL", {})
    out.append({"Donem": "2026-09", "senaryo": "olcum_bddk", "kanal": "temerrut",
                "gosterge": "takipteki_tuketici", "deger": tak.get("takipteki_tuketici_2026-09"),
                "birim": "trilyon TL", "kaynak": "hane_alt/EVDS"})
    htaksit = _load_json("hane_taksit_ozeti.json")
    out.append({"Donem": "2024", "senaryo": "olcum_evds", "kanal": "taksit_gelir",
                "gosterge": "taksit_gelir_18y_kart_haric", "deger": htaksit.get("2024_taksit_gelir_18y"),
                "birim": "oran", "kaynak": "hane_taksit"})
    av = _load_json("acik_veri_ozet.json").get("taban_girdi", {})
    out.append({"Donem": "2026-09", "senaryo": "olcum_evds", "kanal": "borc_buyume",
                "gosterge": "kart_13h_yillik", "deger": av.get("kart_buyume_13h_yillik"),
                "birim": "yüzde", "kaynak": "acik_veri_kopru"})
    out.append({"Donem": "2026-09", "senaryo": "olcum_evds", "kanal": "borc_buyume",
                "gosterge": "tuketici_13h_yillik", "deger": av.get("tuketici_kredi_13h_yillik"),
                "birim": "yüzde", "kaynak": "acik_veri_kopru"})
    # kademe proxy (2031)
    pon = _load_json("ponzi_egilim_sonuc.json").get("ozet", {})
    k = pon.get("kademe_mevcut_taban_proxy")
    if k:
        out.append({"Donem": k["donem_son"], "senaryo": "kademe_mevcut_taban_proxy", "kanal": "servis_Ha",
                    "gosterge": "ponzi_fazlasi_pp", "deger": k["ponzi_fazlasi_pp_son"],
                    "birim": "puan", "kaynak": "ponzi_egilim"})
    return out


def _delta(sen: str, gosterge: str, rows: list[dict]) -> float | None:
    a = next((r for r in rows if r["senaryo"] == sen and r["Donem"] == "2026-Q4" and r["gosterge"] == gosterge), None)
    b = next((r for r in rows if r["senaryo"] == sen and r["Donem"] == "2031-Q4" and r["gosterge"] == gosterge), None)
    if not a or not b or a["birim"] != b["birim"]:
        return None
    if isinstance(a["deger"], str):
        return None
    return float(b["deger"]) - float(a["deger"])


def md(rows: list[dict], meta: dict) -> str:
    lines = [
        "# Hane etkisi — model çerçevesi",
        "",
        "Ölçüm ile senaryo aynı tabloda **eşitlenmez**. Ha = asgari ücretli proxy (`uc_kural` servis oranı); "
        "Hm/Ho = `hane_alt` (2026-Q1 panel). Çift kayıt: **borçlu defterinde borç nominal kalır**.",
        "",
        "Çalıştır: `python3 hane_model_etki.py`.",
        "",
        "## 2031-Q4 senaryo karşılaştırması (hane kanalları)",
        "",
        "| Kanal | `mevcut` | `uc_kural_kilitli` | `maliyet_ucuz_revize` |",
        "| --- | --- | --- | --- |",
    ]

    def v(sen, g):
        r = next(x for x in rows if x["senaryo"] == sen and x["Donem"] == "2031-Q4" and x["gosterge"] == g)
        val = r["deger"]
        if isinstance(val, float):
            if g == "kapsama":
                return f"{val:.3f}"
            if g == "borc_servis_orani_Ha":
                return f"{val:.3f} ({_band(val)})"
            return f"{val:,.1f}" if val > 100 else f"{val:.3f}"
        return str(val)

    for label, g in [
        ("Net taban (TL/ay)", "net_taban_TL"),
        ("Kapsama", "kapsama"),
        ("Ha servis/gelir", "borc_servis_orani_Ha"),
        ("Ponzi fazlası (pp)", "ponzi_fazlasi_pp"),
        ("NFP_H (milyar TL)", "NFP_H"),
        ("Korunmasız USD stok (mr)", "korunmasiz_doviz_stok_mr_usd"),
        ("Limit dondur (H kart/tüketici)", "limit_dondur"),
    ]:
        lines.append(f"| {label} | {v('mevcut', g)} | {v('uc_kural_kilitli', g)} | {v('maliyet_ucuz_revize', g)} |")

    lines += [
        "",
        "## Eğilim (2026-Q4 → 2031-Q4, senaryo)",
        "",
        "| Senaryo | Taban Δ | Servis Δ | Ponzi fazlası Δ (pp) | NFP_H Δ |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for sen in SENARYOLAR:
        lines.append(
            f"| `{sen}` | {_delta(sen, 'net_taban_TL', rows):+.0f} TL | "
            f"{_delta(sen, 'borc_servis_orani_Ha', rows):+.3f} | "
            f"{_delta(sen, 'ponzi_fazlasi_pp', rows):+.1f} | "
            f"{_delta(sen, 'NFP_H', rows):+.1f} |"
        )

    lines += [
        "",
        "## Alt hazne (2026-Q1, varsayım — `hane_alt`)",
        "",
        f"- **Ha:** NFP **−1,63 trilyon TL** (borç > varlık payı); taşıma kapasitesi **~0,92 trilyon TL** (%30 taksit/gelir, 36 ay, faiz ~%63).",
        "- **Hm / Ho:** pozitif NFP; borç yükü modelde Ha’da yoğunlaştırılır (`D_A_BASE` %40).",
        f"- Gözlenen stres: takipteki tüketici **~0,37 trilyon TL**; geniş tanım üst band **~2,47 trilyon TL**.",
        f"- İma edilen Ha borç payı üst sınırı (stres): **%17–44**; taban %40 **üst banda yakın**.",
        "",
        "## Ölçüm çelişkisi (modele girmez ama hane okuması)",
        "",
        "- **`hane_taksit` (2024):** kart hariç taksit/gelir **~%4,0** — düşük görünür.",
        "- **`uc_kural` Ha proxy (2026):** servis/gelir **~%47** — agregat, kart dahil varsayım, sabit taban.",
        "- **EVDS 13 ay (2026-09):** kart **+45,9%**, tüketici **+43,3%** stok büyümesi → `mevcut` senaryoda servis **artış eğilimi**.",
        "",
        "## Tek sistem kademeleri (hane)",
        "",
        "- **K1 mahsup:** doğrudan hane defteri yok; dolay **F itiş freni** → `kademe_mevcut_taban_proxy` ponzi fazlası **mevcuta göre daha yavaş** (bkz. `PONZI_EGILIM.md`).",
        "- **K2 stok tavan:** firma kimden-kime; **hane stokuna yazılmaz**.",
        "- **K3 mevduat adresi:** tasarruf yönlendirme; hane **YP/vadeli stok** ölçümü tek nokta, dağıtım modellenmedi.",
        "",
        "## Döviz (hane)",
        "",
        "- **`mevcut`:** korunmasız USD stok **121,8 → 162,9 mr USD** (senaryo; kur/kanallar kabaca `R_H`).",
        "- **Kilitli/revize:** **120 mr USD** tavan; hane reel kur şoku proxy’si **sınırlı**.",
        "- Brüt dış borç **ölçümde artıyor** (`DOVIZ_EGILIM.md`) — hane FX mevduatı ayrı nesne.",
        "",
        "## Ne denmez",
        "",
        "- “Kademe hane borcunu sildi” denmez.",
        "- “NFP_H milyar = hane geliri” denmez (birim ve kapsam farklı).",
        "- Ponzi etiketi = resmi temerrüt oranı değildir.",
        "",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    rows = _satirlar()
    alan = ["Donem", "senaryo", "kanal", "gosterge", "deger", "birim", "kaynak"]
    with (KOK / "hane_model_etki.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=alan)
        w.writeheader()
        w.writerows(rows)
    meta = {
        "cerceve": "uc_kural (agregat H) + hane_alt (Ha/Hm/Ho) + olcum (taksit/BDDK) + kademe/ponzi/doviz (dolay)",
        "katman_tasinmaz": True,
        "senaryolar": list(SENARYOLAR),
    }
    (KOK / "hane_model_etki_sonuc.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (KOK / "HANE_MODEL_ETKI.md").write_text(md(rows, meta), encoding="utf-8")
    print("=== hane_model_etki ===")
    print("satir:", len(rows), "| md: HANE_MODEL_ETKI.md")


if __name__ == "__main__":
    main()
