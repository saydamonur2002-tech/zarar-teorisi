"""Yürütme maliyeti modeli: tutarlılık testleri (model sınaması, gerçeklik testi değil)."""
import yurutme_maliyet as Y


def test_rho_bandi_sirali_ve_pilot_payi():
    r = Y.RHO
    assert r["alt"] < r["orta"] < r["pilot"] < r["ust"]
    assert r["pilot"] == 0.25


def test_adim_1_3_akis_yok():
    h = Y.hepsi()
    assert h["1"] is None and h["2"] is None and h["3"] is None


def test_adim_5_yurutme_akis_carpi_rho():
    h = Y.hepsi()
    for k, a in h["5"].items():
        for ad, (lo, hi) in a["yurutme"].items():
            assert abs(lo - a["akis_alt"] * Y.RHO[ad]) < 1e-9 and abs(hi - a["akis_ust"] * Y.RHO[ad]) < 1e-9
    # kapsama arttıkça akış ve yürütme artar
    assert h["5"]["20"]["akis_ust"] < h["5"]["50"]["akis_ust"] < h["5"]["100"]["akis_ust"]


def test_adim_4_yurutme_monoton():
    y = Y.hepsi()["4"]["yurutme"]
    assert y["alt"][1] < y["orta"][1] < y["pilot"][1] < y["ust"][1]
    assert y["alt"][0] < y["alt"][1]
