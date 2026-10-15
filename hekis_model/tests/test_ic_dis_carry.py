"""Ic/dis carry ayrimi: kimlik testi (acik artisi = ic + dis + diger) ve veri tutarliligi."""
from hekis.ic_dis_carry import YILLAR, ayir


def test_kanallar_aciga_kapanir():
    for t in YILLAR:
        r = ayir(t)
        assert abs(r["ic_kanal"] + r["dis_kanal"] + r["diger"] - r["acik_artisi"]) < 0.2


def test_2024_ic_agirlikli_2025_dis_artar():
    a, b = ayir(2024), ayir(2025)
    assert a["ic_kanal"] > a["dis_kanal"]
    assert b["dis_kanal"] > a["dis_kanal"]
