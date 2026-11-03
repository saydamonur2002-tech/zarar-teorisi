"""Tek dosyalık inceleme sayfası. Veri JSON'ları gömülür; sayfa ağ istemez."""
from __future__ import annotations

import json
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
BUR = Path(__file__).resolve().parent


def _yukle(ad: str) -> dict:
    return json.loads((KOK / ad).read_text(encoding="utf-8"))


def veri() -> dict:
    m2 = _yukle("para_arzi/m2_etki.json")
    enf = _yukle("para_arzi/enflasyon_etki.json")
    reel = _yukle("para_arzi/reel_rahatlama.json")
    rant = _yukle("rant_aktor_sonuc.json")
    kayip = {
        s["aktor"]: s["rant_kayip_ufuk_milyar"]
        for s in rant["satirlar"]
        if s["senaryo"] == "mevcut" and "rant_kayip_ufuk_milyar" in s
    }
    return {
        "m2": m2,
        "enf": enf,
        "reel": reel,
        "rant": {
            "durum": rant["meta"]["durum"],
            "olcum_degil": rant["meta"]["olcum_degil"],
            "baseline": rant["meta"]["baseline_rant_yillik"],
            "kayip": kayip,
        },
        "etki": {
            "kaynak": "yayin/ETKI_CEPHESI_REVIZE.md",
            "sfc": {"H": 0.0, "F": -1.001, "B": 0.0, "K": 0.0, "D": 1.001, "sigma": 0.0},
            "kapanis_ok": True,
            "once_sigma": 0.586,
            "f4_baz": 25339.8,
            "f4_bant": [22805.8, 20271.8],
            "transfer_mn_usd": 22550.0,
            "kur": 44.38,
            "transfer_tr_tl": 1.001,
        },
    }


def uret() -> str:
    sablon = (BUR / "sablon.html").read_text(encoding="utf-8")
    ham = json.dumps(veri(), ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    html = sablon.replace("@@VERI@@", ham)
    html = html.replace("@@FORMULLER@@", (BUR / "formuller.js").read_text(encoding="utf-8"))
    html = html.replace("@@UI@@", (BUR / "ui.js").read_text(encoding="utf-8"))
    if "@@" in html:
        raise SystemExit("sablon yer tutucusu kaldi")
    (BUR / "index.html").write_text(html, encoding="utf-8")
    return html


if __name__ == "__main__":
    uret()
