"""Adım 4.5 plasebo kontrolü ve yürütme maliyeti: tutarlılık testleri."""
import adim45_maliyet as M


def test_plasebo_paylar_lambdan_bagimsiz():
    pl, stok = M.plasebo()
    assert all(v["max_fark_pay"] < 1e-12 for v in pl.values())
    assert abs(pl["parite (repo, λ=1)"]["tl_para_toplam_yeni"] - stok["tl_para_toplam"]) < 1e-9


def test_sabit_capa_kur_repodan():
    pl, _ = M.plasebo()
    assert abs(pl["parite (repo, λ=1)"]["kur_yeni"] - 49.1274) < 1e-9
    assert abs(pl["örnek: λ=0,001"]["kur_yeni"] - 49.1274e-3) < 1e-12


def test_maliyet_banti_ve_asama():
    c = M.maliyet()
    assert 0 < c["A"][0] < c["A"][1] < c["B"][0] < c["B"][1]
    assert abs(c["B"][0] - 0.003 * 63240.5) < 1e-6
    a = M.asama(c["A"][1])
    assert abs(sum(a.values()) - c["A"][1]) < 1e-9 and len(a) == 4
