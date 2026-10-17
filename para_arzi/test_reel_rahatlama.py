"""Reel rahatlama: kilitli formül, enflasyon bandının iki ucu."""
import hashlib
import json
from pathlib import Path

from para_arzi.reel_rahatlama import (
    I0,
    I_KILIT,
    KRITER,
    PI0,
    hucre,
    hukum,
    i_beta,
)

BUR = Path(__file__).resolve().parent
KOK = BUR.parent


def _doc():
    return json.loads((BUR / "reel_rahatlama.json").read_text(encoding="utf-8"))


def _enf():
    return json.loads((BUR / "enflasyon_etki.json").read_text(encoding="utf-8"))


def test_kriter_hesaptan_once_kilitli():
    doc = _doc()
    assert doc["kriter_sha256"] == hashlib.sha256(KRITER.read_bytes()).hexdigest()
    metin = KRITER.read_text(encoding="utf-8")
    assert "hesap çalışmadan yazıldı" in metin
    assert "β = 1'de bile" in metin
    assert "β = 0,5'te küçükse" in metin
    assert "enflasyon_etki" not in (KOK / "adim3_faiz_durma.py").read_text(encoding="utf-8")
    assert "reel_rahatlama" not in (KOK / "adim3_faiz_durma.py").read_text(encoding="utf-8")


def test_beta_sifir_fazlalik_sifir_ve_tam_fisher_tabani():
    assert i_beta(0.0, -40.0) == I0
    assert i_beta(1.0, -10.0) == I0 - 10.0
    assert i_beta(0.5, -10.0) == I0 - 5.0
    assert i_beta(1.0, -84.0) == 0.0
    h = hucre(1207.6, 0.0, -10.0)
    assert h["fazlalik"] == 0.0
    assert h["nominal"] == 1207.6
    assert abs(h["net"] - (1207.6 / (1 + (PI0 - 10) / 100) - 1207.6 / (1 + PI0 / 100))) < 1e-9


def test_json_formulle_ayni_ve_iki_uc():
    doc = _doc()
    enf = _enf()
    beklenen = []
    for s in enf["senaryo"]:
        for yil in ("2029", "2030", "2031"):
            for dpi in s["yil"][yil]["toplam"]:
                beklenen.append((s["ad"], int(yil), dpi))
    assert len(doc["satirlar"]) == len(beklenen) * 3
    for h in doc["satirlar"]:
        assert h["I0"] == I_KILIT[h["senaryo"]]
        assert h["beta"] in (0.0, 0.5, 1.0)
        yeniden = hucre(h["I0"], h["beta"], h["delta_pi"])
        assert abs(h["nominal"] - round(yeniden["nominal"], 8)) < 1e-8
        assert abs(h["fazlalik"] - round(yeniden["fazlalik"], 8)) < 1e-8
        assert abs(h["reel"] - round(yeniden["reel"], 8)) < 1e-8
        assert abs(h["net"] - round(yeniden["net"], 8)) < 1e-8
        assert h["tanim_disi"] is (abs(h["delta_pi"]) > I0)
    yuksek = [h for h in doc["satirlar"] if h["senaryo"] == "yuksek" and h["yil"] == 2029]
    assert any(h["tanim_disi"] for h in yuksek)
    assert any(not h["tanim_disi"] for h in yuksek)
    assert all(h["durum"] == "olculdu" for h in yuksek)


def test_hukum_kilitli_kurala_uyar():
    doc = _doc()
    kapsam = [h for h in doc["satirlar"] if h["hukme_girer"]]
    bir = [h["net"] for h in kapsam if h["beta"] == 1.0]
    yari = [h["net"] for h in kapsam if h["beta"] == 0.5]
    if any(x < 0 for x in yari):
        assert doc["hukum"]["hukum"] == "yanlis"
    elif bir and all(x > 0 for x in bir):
        assert doc["hukum"]["hukum"] == "ayakta"
    else:
        assert doc["hukum"]["hukum"] == "ayakta_degil"
    assert hukum(doc["satirlar"])["hukum"] == doc["hukum"]["hukum"]
    assert all(h["yil"] != 2031 or not h["hukme_girer"] or h["delta_pi"] < 0 for h in doc["satirlar"])
    artis = [h for h in doc["satirlar"] if h["delta_pi"] > 0]
    assert artis and all(not h["hukme_girer"] for h in artis)
