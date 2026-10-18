"""KOBİ kredi: BDDK çıpaları, reel kat ve korelasyonun işareti."""
import json
from pathlib import Path

import kobi_kredi_korelasyon as K


def test_aralik_ciplari():
    ham = {r["Donem"]: r for r in K._oku()}
    assert ham["2016-12"]["Nakdi_milyon"] == "420539"
    assert ham["2024-12"]["Nakdi_milyon"] == "4285659"
    assert ham["2025-12"]["Nakdi_milyon"] == "6218077"
    assert ham["2026-08"]["Nakdi_milyon"] == "7498671"
    assert ham["2026-07"]["Takip_milyon"] == "284851"
    assert ham["2016-12"]["Tufe_kaynak"] == "EVDS TP.FG.J0"
    assert "TUKFIY" in ham["2026-08"]["Tufe_kaynak"]


def test_reel_kat_ve_2024_daralma():
    s = K.hesap()
    p = s["pencere"]["2016_2025"]
    assert abs(p["nominal_kat"] - 6218077 / 420539) < 1e-9
    assert abs(p["reel_kat"] - 1.2307) < 0.002
    y24 = next(y for y in s["yillik"] if y["yil"] == 2024)
    assert abs(y24["reel_artis_%"] - (-7.43)) < 0.05
    assert abs(y24["nominal_artis_%"] - 33.65) < 0.05
    son = s["son_gozlem"]
    assert son["donem"] == "2026-08"
    assert son["npl_%"] < 4.0
    assert abs(son["nakdi_milyar"] - 7498.671) < 0.001


def test_fatura_katsayisi_pozitif_degil():
    s = K.hesap()
    tam = s["fatura"]["haziran_hepsi"]["reel_yillik"]
    sade = s["fatura"]["haziran_turetilen_2022_haric"]["reel_yillik"]
    assert tam["n"] == 5 and sade["n"] == 4
    assert tam["pearson"] < 0 and sade["pearson"] < 0
    assert tam["spearman"] < 0


def test_granger_takip_isi_negatif():
    s = K.hesap()
    g = s["granger"]["takip_stogu_reel_krediye"]
    bir, uc = g[0], g[1]
    assert bir["gecikme"] == 1 and uc["gecikme"] == 3
    assert bir["katsayi_toplami"] < 0 and uc["katsayi_toplami"] < 0
    assert bir["p"] < 0.05
    oran = s["granger"]["reel_kredi_npl_oranina"][0]
    assert oran["katsayi_toplami"] < 0


def test_json_hamdan_yeniden():
    s = K.hesap()
    kayit = json.loads(Path("kobi_kredi_korelasyon.json").read_text(encoding="utf-8"))
    assert abs(s["pencere"]["2016_2025"]["reel_kat"] - kayit["pencere"]["2016_2025"]["reel_kat"]) < 1e-12
    assert abs(s["fatura"]["haziran_hepsi"]["reel_yillik"]["pearson"] - kayit["fatura"]["haziran_hepsi"]["reel_yillik"]["pearson"]) < 1e-12
    metin = Path("KOBI_KREDI_KORELASYON.md").read_text(encoding="utf-8")
    assert "2026 Eylül bültende yok" in metin
    assert "n küçüktür" in metin
