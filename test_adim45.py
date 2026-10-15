"""Adım 4.5 (yeni para birimi, plasebo): tutarlılık testleri."""
import adim45_para_birimi as P


def test_oranlar_cevirmeden_sonra_ayni():
    k = P.kalemler()
    for s in (1 / 1000, 1 / 100, 7.5):
        o0, o1 = P.oranlar(k), P.oranlar(P.cevir(k, s))
        assert all(abs(o0[a] - o1[a]) < 1e-12 for a in o0)


def test_parasal_kalemler_olcek_alir():
    k = P.kalemler()
    c = P.cevir(k, 0.001)
    assert all(abs(b[2] - a[2] * 0.001) < 1e-9 for a, b in zip(k, c) if a[3] == "para")


def test_maliyet_banti():
    c = P.maliyet()
    assert 0 < c["A"][0] < c["A"][1] < c["B"][0] < c["B"][1]
    assert abs(c["B"][0] - 0.003 * P.GSYH_MLR_TL) < 1e-9


def test_uc_kural_plasebo_ve_maliyet_sirasi():
    k = P.kalemler()
    o0 = P.oranlar(k)
    for ad, s in P.KURALLAR.items():
        o1 = P.oranlar(P.cevir(k, s))
        assert all(abs(o0[a] - o1[a]) < 1e-12 for a in o0), ad
    km = P.kural_maliyet()
    assert km["basa_bas"][1] <= km["sifir_atma"][1] < km["sabit_capa"][0]
    assert abs(P.KURALLAR["sabit_capa"] - 1 / P.KUR) < 1e-12
