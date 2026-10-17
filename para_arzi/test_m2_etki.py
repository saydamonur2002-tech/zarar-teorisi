"""M2 etkisi: kilitli kuralların aritmetiği ve EVDS kimliği."""
import json
from pathlib import Path

from para_arzi.m2_etki import (
    A_ALT,
    A_UST,
    ADRES_HAM,
    DIBS_2026_03_27,
    FIRMA_VADELI,
    GERCEK_YP,
    HANE_VADELI,
    KREDI_PAY,
    ORTUSME_ALT,
    ORTUSME_UST,
    TL_PARA_STOKU,
    adim4,
    birim_capasi,
    m2_parcala,
    stok_silim_ayak,
)

BUR = Path(__file__).resolve().parent


def test_adres_ve_ortusme_kilitli():
    assert abs(HANE_VADELI + FIRMA_VADELI + GERCEK_YP - ADRES_HAM) < 1e-9
    assert abs(ADRES_HAM - ORTUSME_UST - A_ALT) < 1e-9
    assert abs(ADRES_HAM - ORTUSME_ALT - A_UST) < 1e-9
    assert A_ALT == 12722.5
    assert A_UST == 19076.6


def test_birim_capasi_repo_ile_ortusur():
    cap = birim_capasi()
    assert abs(cap["milyar"] - 8037.1) < 0.15


def test_mevduat_ayagi_iki_sutun():
    ay = stok_silim_ayak()
    assert ay["ayri"]["m2"] == 0.0
    assert ay["mahsup_0421"]["m2"] == 0.0
    assert ay["birlesik"]["silinen"] == 18000
    assert ay["birlesik"]["mevduat_ayak_yurtici"] == 7195 + 6772
    assert ay["birlesik"]["mevduat_ayak_yurtdisi"] == 4033
    assert ay["birlesik"]["m2_aday"] == 13967


def test_ikinci_tur_stoga_eklenmez_ve_chi_tepeyi_degistirmez():
    a = adim4(0.25, 0.0, A_UST)
    b = adim4(0.25, 0.5, A_UST)
    assert a["tepe"] == b["tepe"]
    assert a["kalici"] == 0.0
    assert b["kalici"] == 0.5 * b["tepe"]
    assert a["ikinci_tur_tepe_yillik"] == round(KREDI_PAY * a["tepe"], 4)
    assert a["ikinci_tur_kalici_yillik"] == 0.0


def test_evds_kimligi_ve_senaryo_kiliti():
    ham = json.loads((BUR / "m2_ham.json").read_text(encoding="utf-8"))
    parca = m2_parcala(ham["ham_bin_tl"])
    m = parca["milyar"]
    assert abs(m["tl"] + m["yp"] - m["m2"]) < 0.05
    assert abs(m["m2"] + m["repo"] + m["ppf"] + m["menkul"] - m["m3"]) < 0.05
    assert m["menkul"] < DIBS_2026_03_27 / 10
    assert parca["menkul_m2_icinde"] is False
    assert parca["yp_m2_icinde"] is True
    doc = json.loads((BUR / "m2_etki.json").read_text(encoding="utf-8"))
    assert doc["kriter_sha256"]
    assert doc["tl_para_stoku"]["esitlik"] == "dustu"
    assert doc["tl_para_stoku"]["tl_para_stoku"] == TL_PARA_STOKU
    assert abs(doc["tl_para_stoku"]["fark"]) > 1.0
    beklenen = [
        ("dusuk", 0.10, 0.0, A_ALT, 0.0),
        ("orta", 0.25, 0.5, A_UST, 0.0),
        ("yuksek", 0.50, 0.5, A_UST, 13967.0),
    ]
    for s, (ad, th, ch, adres, adim12) in zip(doc["senaryo"], beklenen):
        assert s["ad"] == ad
        assert s["adim12_m2"] == adim12
        assert s["adim3_m2"] == s["adim45_m2"] == s["adim5_m2"] == 0.0
        tepe = th * adres
        kalici = ch * tepe
        assert abs(s["adim4_tepe"] - tepe) < 1e-6
        assert abs(s["adim4_kalici"] - kalici) < 1e-6
        assert abs(s["baslik_stok"] - (adim12 + kalici)) < 1e-6
        assert abs(s["ikinci_tur_tepe_yillik"] - KREDI_PAY * tepe) < 1e-6
        # Akış, stok başlığına eklenmemiş.
        assert s["baslik_stok"] < s["tepe_stok"] + s["ikinci_tur_tepe_yillik"]
