"""Kilitlenmiş taslak başlıkları. Modeli yeniden koşmaz."""
from __future__ import annotations

import json
from pathlib import Path

CIKTI = Path(__file__).resolve().parent


def _j(ad: str) -> dict:
    return json.loads((CIKTI / ad).read_text(encoding="utf-8"))


def test_bacak_baslik():
    d = _j("bacak_sonuc.json")
    assert d["artis_banka"] == 2660.8843
    assert d["lam"] == 1.0357
    assert d["tam_min_F"]["acik|kopru"] == 443.87
    assert d["tam_min_F"]["borc|kopru"] == 5362.42
    assert d["A"]["on"] == 12722.5
    assert d["tam"]["borc|stok|on|0.0"]["temerrut"] == 7
    assert d["tam"]["borc|stok|on|0.0"]["kilitli"] == 10


def test_rant_baslik():
    d = _j("rant_sonuc.json")
    assert d["tam"]["bol_butce"]["cekilen"] == 46.7652 or abs(d["tam"]["bol_butce"]["cekilen"] - 46.77) < 0.02
    assert d["tam"]["temerrut"] == 7
    assert d["tam"]["kopru"] == 443.87
    assert d["k5_siki_uygun_pay"] == 0.0
    assert d["seyrek"]["min_araci"]["yok"] == 0
    assert d["seyrek"]["n"] == 30


def test_prim_odenen_sifir():
    d = _j("prim_tavan_sonuc.json")
    assert all(h["odenen"] == 0.0 for h in d["kupon"])
    assert d["tavan_milyar_tl"]["2025"]["musd"]["ara"] == 250228.0
    assert d["dar_2025"] > 7000


def test_fx_artis_ayni():
    d = _j("fx_durdur_sonuc.json")
    assert d["artis_ayni"] is True
    assert d["artis"] == 2660.8843
    assert d["tam"]["temerrut"] == 7
    assert d["adim2_kosul_bu_taslakta"]["uc_kosul"] is False


def test_olcek_ondalik():
    d = _j("olcek_sonuc.json")
    assert d["N_FIRMA"] == 150
    assert d["ust_onda_adet"] == 15
    assert d["emme"]["piyasa"] == 10339.8
