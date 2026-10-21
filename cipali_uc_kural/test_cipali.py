"""Çıpalı varyant. Ağ yok. Kilitli üç senaryonun adı değişmez."""

from __future__ import annotations

import numpy as np

from cipali_uc_kural.kosu import birlikte, k1, k3, sarmal_mi
from cipali_uc_kural.tahmin import _beklenti_ozet, _nw
from uc_kural_senaryo import SENARYOLAR, _geri_bildirim, Params, State


def test_senaryo_adlari():
    assert SENARYOLAR == ("mevcut", "uc_kural_kilitli", "maliyet_ucuz_revize")


def test_kisitli_beklenti_w():
    rng = np.random.default_rng(0)
    n = 40
    pi = rng.normal(20, 5, n)
    g = rng.normal(10, 3, n)
    h = np.full(n, 5.0)
    w, phi = 0.4, 0.15
    e = w * h + (1 - w) * pi + phi * g
    y = e - pi
    X = np.column_stack([h - pi, g])
    fit = _nw(y, X)
    o = _beklenti_ozet(fit)
    assert abs(o["w"] - 0.4) < 1e-8
    assert abs(o["phi"] - 0.15) < 1e-8
    assert abs(o["geriye"] - 0.6) < 1e-8


def test_k1_ve_k3():
    kap0 = 0.50
    yol = {
        "kosuldu": True,
        "patlama": False,
        "kap0": kap0,
        "satir": [{"kapsama": 0.50, "pi_y": 30, "tetik_cap": False, "tetik_snap": False,
                   "oncul_pay": False, "oncul_doviz": False, "R": 10} for _ in range(8)],
    }
    assert k1(yol) == "gecti"
    assert k3(yol) == "sinanmadi"
    yol["satir"][3]["kapsama"] = 0.40
    yol["satir"][4]["kapsama"] = 0.40
    assert k1(yol) == "kaldi"
    assert birlikte("gecti", "gecti", "sinanmadi") == "belirsiz"
    assert birlikte("kaldi", "gecti", "gecti") == "kaldi"
    duz = {
        "kosuldu": True, "patlama": False,
        "satir": [{"pi_y": 10.0 + i, "R": 1} for i in range(6)],
    }
    assert sarmal_mi(duz, 9) is True
    duz["satir"] = [{"pi_y": 20, "R": 1} for _ in range(6)]
    assert sarmal_mi(duz, 10) is False


def test_geri_alma_fonksiyonu():
    st = State(nfp=np.zeros(5))
    st.stok = {"D_korunmasiz_usd_mr": 100.0}
    st.uretken_pay_gecmis = [0.30]
    st.doviz_stok_gecmis = [90.0]
    _geri_bildirim(st, "2027-Q2", "uc_kural_kilitli", 0.30, Params())
    assert st.tuketim_cap_ek_pp == -2.0
    assert st.stok["D_korunmasiz_usd_mr"] == 90.0


if __name__ == "__main__":
    test_senaryo_adlari()
    test_kisitli_beklenti_w()
    test_k1_ve_k3()
    test_geri_alma_fonksiyonu()
    print("gecti")
