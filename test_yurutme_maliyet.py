"""Yürütme maliyeti modeli: tutarlılık testleri (model sınaması, gerçeklik testi değil)."""
import yurutme_maliyet as Y


def test_rho_bandi_sirali_ve_pilot_payi():
    r = Y.RHO
    assert r["alt"] < r["orta"] < r["pilot"] < r["ust"]
    assert r["pilot"] == 0.25


def test_adim_1_2_stok_ust_sinir_ve_adim_3_yillik():
    h = Y.hepsi()
    for n in ("1", "2"):
        assert set(h[n]["yurutme"]) == {"alt"}
        assert abs(h[n]["yurutme"]["alt"] - h[n]["akis"] * Y.RHO["alt"]) < 1e-9
        assert h[n]["uygulanmaz"]["orta"] > 1000  # gerçekçi olmayan tutar
    assert abs(h["1"]["akis"] - 20363.4) < 0.05 and abs(h["2"]["akis"] - 14602.3) < 0.05
    # adım 3: κ arttıkça duran faiz ve yürütme artar
    k = sorted(h["3"], key=float)
    assert [h["3"][x]["akis"] for x in k] == sorted(h["3"][x]["akis"] for x in k)


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
