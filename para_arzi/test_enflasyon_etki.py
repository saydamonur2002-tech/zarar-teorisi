"""Enflasyon köprüsü: kilitli kurallar, EVDS hamından yeniden hesap."""
import hashlib
import json
from pathlib import Path

from para_arzi.enflasyon_etki import (
    GECIS,
    GERCEK_YP,
    GSYH_2025,
    I_YIL,
    KIRA_ALT,
    KIRA_UST,
    KIRA_W,
    KRITER,
    R_SABIT,
    _dlog_aradan,
    _dlog_seviye,
    hesap,
)

BUR = Path(__file__).resolve().parent
KOK = BUR.parent


def _ham():
    return json.loads((BUR / "enflasyon_ham.json").read_text(encoding="utf-8"))


def _doc():
    return json.loads((BUR / "enflasyon_etki.json").read_text(encoding="utf-8"))


def test_json_hamdan_yeniden_hesaplanir():
    doc = hesap(_ham())
    kayit = _doc()
    assert doc["kriter_sha256"] == kayit["kriter_sha256"]
    assert doc["para"]["b1"] == kayit["para"]["b1"]
    assert doc["para"]["b2"] == kayit["para"]["b2"]
    assert doc["kredi_model"]["d"] == kayit["kredi_model"]["d"]
    assert doc["kredi_model"]["h"] == kayit["kredi_model"]["h"]
    assert doc["senaryo"][1]["yil"]["2029"]["toplam"] == kayit["senaryo"][1]["yil"]["2029"]["toplam"]
    assert doc["kur_model"]["durum"] == kayit["kur_model"]["durum"]


def test_kriter_hash_ve_cumle():
    doc = _doc()
    assert doc["kriter_sha256"] == hashlib.sha256(KRITER.read_bytes()).hexdigest()
    metin = (BUR / "ENFLASYON_ETKI.md").read_text(encoding="utf-8")
    cumle = "Modelde enflasyon dışsaldır; bu hesap model dışı bir köprüdür, sonuç modele geri beslenmez"
    assert cumle in metin.split("##")[0]
    assert doc["dissallik"]["geri_besleme"] is False


def test_adim_dosyalari_kopruyu_okumaz():
    for ad in (
        "adim3_faiz_durma.py",
        "adim4_adres_yonlendirme.py",
        "adim45_birim.py",
        "adim45_maliyet.py",
        "bes_yil_senaryo.py",
        "gsyh_pay.py",
    ):
        assert "enflasyon_etki" not in (KOK / ad).read_text(encoding="utf-8")
    a3 = (KOK / "adim3_faiz_durma.py").read_text(encoding="utf-8").splitlines()
    assert "TP.KTF17" in a3[9]
    assert "r_son" in a3[76]
    assert "KUR = 49.1274" in (KOK / "adim45_maliyet.py").read_text(encoding="utf-8").splitlines()[19]
    birim = (KOK / "adim45_birim.py").read_text(encoding="utf-8").splitlines()
    assert "USD stok durur" in birim[8]
    assert "Faiz oranı durur" in birim[8]


def test_maliyet_alfa_yalniz_0_ve_1_ve_adim45_sifir():
    doc = _doc()
    assert doc["adim45"] == 0.0
    assert 0.69 not in GECIS
    for s in doc["senaryo"]:
        assert s["maliyet"]["alfa0"] == 0.0
        assert s["maliyet"]["alfa1"] == round(-100.0 * I_YIL[s["ad"]] / GSYH_2025, 8)
        assert set(s["maliyet"]) >= {"alfa0", "alfa1"}
        assert "alfa05" not in s["maliyet"]
        assert s["yil"]["2030"]["adim45"] == 0.0
        assert s["kira"]["yil"] is None
        lo = -100.0 * KIRA_W * s["kira"]["kapsama"] * (KIRA_ALT[0] / KIRA_ALT[1])
        hi = -100.0 * KIRA_W * s["kira"]["kapsama"] * (KIRA_UST[0] / KIRA_UST[1])
        assert s["kira"]["puan"] == [round(min(lo, hi), 8), round(max(lo, hi), 8)]


def test_m1_alt_sifir_kur_alt_sifir_ve_ikinci_tur_stoga_girmez():
    m2 = json.loads((BUR / "m2_etki.json").read_text(encoding="utf-8"))
    doc = _doc()
    assert doc["kur_model"]["durum"] == "tahmin_edilemedi"
    assert doc["kur_model"]["n"] < 8
    for s, m in zip(doc["senaryo"], m2["senaryo"]):
        assert s["ad"] == m["ad"]
        assert s["adim4_tepe"] == m["adim4_tepe"]
        assert s["adim4_kalici"] == m["adim4_kalici"]
        assert s["ikinci_tur_tepe"] == m["ikinci_tur_tepe_yillik"]
        assert s["ikinci_tur_kalici"] == m["ikinci_tur_kalici_yillik"]
        assert s["dm1_tepe"][0] == 0.0
        assert s["dm1_kalici"][0] == 0.0
        assert s["para_tepe"]["alt"]["dm1"] == 0.0
        assert s["para_tepe"]["alt"]["dm2"] == s["adim4_tepe"]
        assert s["para_tepe"]["alt"]["dm2"] != s["adim4_tepe"] + s["ikinci_tur_tepe"]
        assert s["yil"]["2029"]["kur"] == 0.0
        assert s["hiz"]["fiyata_eklendi"] is False
    assert doc["senaryo"][2]["adim12_m2"] == 13967.0
    assert doc["senaryo"][2]["para_tepe"]["alt"]["dm2"] == doc["senaryo"][2]["adim4_tepe"]
    assert doc["birlesik_2028"]["dm2"] == 13967.0
    assert doc["birlesik_2028"]["skora_girer"] is False
    assert doc["senaryo"][2]["yil"]["2028"]["toplam"] == [0.0, 0.0]


def test_buyume_enflasyon_toplamina_girmez_ve_h_noktasi_sifir():
    doc = _doc()
    assert doc["kredi_model"]["h"]["sifir_icerir"] is True
    assert doc["kredi_model"]["h"]["nokta"] == 0.0
    for s in doc["senaryo"]:
        h = s["yil"]["2030"]
        assert abs((h["toplam"][0] - h["toplam_kredisiz"][0]) - h["kredi"]) < 1e-8
        assert abs((h["toplam"][1] - h["toplam_kredisiz"][1]) - h["kredi"]) < 1e-8
        assert s["buyume"]["tepe"]["nokta"] == 0.0
        assert s["buyume"]["kalici"]["nokta"] == 0.0


def test_para_gecisi_ile_geri_donus_net_duzeye_iner():
    doc = _doc()
    m1, m2 = doc["m1"], doc["m2"]
    for s in doc["senaryo"]:
        for i in (0, 1):
            d1, k1 = s["dm1_tepe"][i], s["dm1_kalici"][i]
            d2, k2 = s["adim4_tepe"], s["adim4_kalici"]
            a = _dlog_seviye(m1, m2, d1, d2)
            b = _dlog_aradan(m1, m2, d1, d2, k1, k2)
            c = _dlog_seviye(m1, m2, k1, k2)
            assert abs(a[0] + b[0] - c[0]) < 1e-9
            assert abs(a[1] + b[1] - c[1]) < 1e-9
        assert s["dm1_tepe"][1] <= GERCEK_YP * s["theta"] + 1e-6
        assert s["dm1_tepe"][1] <= doc["vadesiz_yp"] + 1e-6


def test_fisher_formulu_ve_2027_sifir():
    doc = _doc()
    assert doc["senaryo"][0]["yil"]["2027"]["toplam"] == [0.0, 0.0]
    orta = next(t for t in doc["tutarlilik"] if t["senaryo"] == "orta" and t["yil"] == 2029 and t["kose"] == "kredi_dahil")
    I = I_YIL["orta"]
    assert abs(orta["nominal_fazla_milyar"] - I * abs(orta["delta_pi"]) / R_SABIT) < 1e-6
    assert abs(orta["reel_oran"] - (abs(orta["delta_pi"]) / 100.0) / (1.0 + 29.73 / 100.0)) < 1e-8
    assert all(t["yil"] != 2031 for t in doc["tutarlilik"])
