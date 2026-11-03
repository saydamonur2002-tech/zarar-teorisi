"""Arayüz formülleri kilitli JSON ile aynıdır; sayfa o formülü gömer."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from para_arzi.enflasyon_etki import GERCEK_YP as ENF_YP
from para_arzi.enflasyon_etki import KIRA_W
from para_arzi.m2_etki import GERCEK_YP, KREDI_PAY
from para_arzi.reel_rahatlama import I0, PI0

KOK = Path(__file__).resolve().parents[1]
BUR = Path(__file__).resolve().parent


def test_sabitler_betikle_ayni():
    js = (BUR / "formuller.js").read_text(encoding="utf-8")
    assert GERCEK_YP == ENF_YP == 6639.4
    assert f"GERCEK_YP = {GERCEK_YP}" in js
    assert f"KREDI_PAY = {KREDI_PAY}" in js
    assert f"I0 = {I0}" in js
    assert f"PI0 = {PI0}" in js
    assert f"KIRA_W = {KIRA_W}" in js


def test_formuller_json_ile_esit():
    subprocess.check_call(["node", str(BUR / "esitlik.js")], cwd=KOK)


def test_sayfa_formulu_gomer_ve_ag_istemez():
    html = (BUR / "index.html").read_text(encoding="utf-8")
    js = (BUR / "formuller.js").read_text(encoding="utf-8")
    assert js in html
    assert "https://" not in html
    assert "http://" not in html
    assert "src=" not in html
    m = re.search(r'<script id="veri" type="application/json">(.*?)</script>', html, re.S)
    assert m
    gomulu = json.loads(m.group(1))
    dosya = json.loads((KOK / "para_arzi/m2_etki.json").read_text(encoding="utf-8"))
    assert gomulu["m2"]["m2"]["milyar"]["m2"] == dosya["m2"]["milyar"]["m2"]
    assert gomulu["reel"]["hukum"]["hukum"] == "yanlis"
    assert gomulu["etki"]["sfc"]["sigma"] == 0
