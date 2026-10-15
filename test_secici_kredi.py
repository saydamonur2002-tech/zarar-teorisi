"""Seçici kredi modeli: tablo paritesi ve kalibrasyon sağlık testleri (model sınaması, gerçeklik testi değil)."""
import json

import secici_kredi as K
import secici_kredi_kalibre as C


def test_sim_tablo_ile_ayni():
    ref = json.load(open(K.KOK / "secici_kredi_sheet_ref.json"))
    P = K.varsayilan()
    for s in (1, 2, 3, 4):
        rows = K.sim(P, K.kollar(s))
        for k, vs in ref[f"S{s}"].items():
            assert max(abs(rows[t][k] - vs[t]) for t in range(20)) < 1e-6, (s, k)


def test_olcum_dkbe_tablo_ile_ayni():
    V, _ = K.veri()
    beklenen = [19.58, 16.201, 26.873, 16.359, 23.159, 41.007, 22.091, 26.139, 19.435, 18.642, 32.521]
    for y, e in zip(K.YILLAR, beklenen):
        assert abs(K.olcum(V, y)["DKBE"] - e) < 5e-3, y


def test_z0_tablodaki_deger():
    assert abs(K.z0(K.varsayilan()) - K.varsayilan()["Z0"]) < 1e-8


def test_kalibre_capalar_ve_ithalat_kimligi():
    V, _ = K.veri()
    P, et = C.baz(V, 2025)
    assert abs(P["pi0"] - 0.3089) < 1e-9 and et["pi0"][0] == "olcum"
    b = K.z0(P, bilesen=True)
    m_hedef = P["X0"] + P["cad0"] * P["AD0"] - P["nfp"] * P["AD0"]
    assert abs(b["m"] - m_hedef) < 1e-6  # t0 ithalat kimliği


def test_kalibre_ayar_ve_orneg_disi_hata_makul():
    V, _ = K.veri()
    P0, arm0, P, a, x0, x, et = C.kalibre(V)
    rows = K.sim(P, a, T=6)
    ic = [abs(v) for _, _, v in C.hata(rows, C.HEDEF, C.ICERI)]
    assert max(ic) < 0.05  # içeri örnek (ayar): 6 momentin hepsi 5 puan içinde
    di = {(k, t): v for k, t, v in C.hata(rows, C.HEDEF, C.DISARI)}
    assert abs(di[("pi", 3)]) < 0.06 and abs(di[("i", 3)]) < 0.06  # 2028 örnek dışı
