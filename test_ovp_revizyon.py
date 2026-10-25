"""OVP çapa: EVDS önceliği, gelecek yıl OVP, stok-akışa yazmama."""

from datetime import date
from pathlib import Path

import ovp_revizyon as O
from uc_kural_senaryo import Params

KOK = Path(__file__).resolve().parent
REFERANS = date(2026, 10, 25)
SENARYO = (
    "uc_kural_senaryo.csv",
    "uc_kural_senaryo_sonuc.json",
    "UC_KURAL_SENARYO.md",
)


def _capa():
    return O.capalar(O.yukle(), O.evds_oku(), REFERANS)


def _hucre(capa, degisken, yil):
    return next(h for h in capa["hucreler"] if h["degisken"] == degisken and h["yil"] == yil)


def test_son_yayin_2027_2029():
    son = O.son_yayin(O.yukle())
    assert son["ovp_donemi"] == "2027-2029"
    assert son["yayin_tarihi"] == "2026-09-06"
    once = O.onceki_yayin(O.yukle())
    assert once["ovp_donemi"] == "2026-2028"


def test_gecmis_tufe_evds_gelecek_ovp():
    capa = _capa()
    t25 = _hucre(capa, "tufe_yil_sonu", 2025)
    assert t25["kaynak"] == "evds"
    assert t25["deger"] == 30.89
    assert t25["deger"] != 30.9
    t26 = _hucre(capa, "tufe_yil_sonu", 2026)
    assert t26["kaynak"] == "ovp" and t26["deger"] == 28.4 and t26["rol"] == "gt"
    t27 = _hucre(capa, "tufe_yil_sonu", 2027)
    assert t27["deger"] == 21.0 and t27["rol"] == "program"
    assert _hucre(capa, "tufe_yil_sonu", 2028)["deger"] == 13.5
    assert _hucre(capa, "tufe_yil_sonu", 2029)["deger"] == 9.0
    assert _hucre(capa, "tufe_yil_sonu", 2024)["deger"] is None
    assert capa["tufe_yol_ovp_program"]["2027"] == 0.21
    assert capa["senaryo_tufe_yol_dokunulmadi"] == 0.28


def test_kur_ve_buyume_bosluklari():
    capa = _capa()
    assert all(h["deger"] is None for h in capa["hucreler"] if h["degisken"] == "usd_try")
    assert _hucre(capa, "gsyh_buyume", 2025)["deger"] is None
    assert _hucre(capa, "gsyh_buyume", 2025)["kaynak"] == "bos"
    assert _hucre(capa, "gsyh_buyume", 2027)["deger"] == 4.2
    assert _hucre(capa, "gsyh_buyume", 2026)["deger"] == 3.3


def test_revizyon_farki():
    g = O.gunluk(O.yukle())
    satir = {(s["degisken"], s["yil"]): s for s in g["satirlar"]}
    assert satir[("tufe_yil_sonu", 2027)]["fark"] == 12.0
    assert satir[("tufe_yil_sonu", 2026)]["fark"] == 12.4
    assert satir[("tufe_yil_sonu", 2028)]["fark"] == 5.5
    assert satir[("gsyh_buyume", 2027)]["fark"] == -0.1
    assert satir[("tufe_yil_sonu", 2029)]["onceki"] is None
    assert satir[("tufe_yil_sonu", 2029)]["fark"] is None


def test_idempotent(tmp_path):
    (tmp_path / "ovp_revizyonlar.json").write_text((KOK / "ovp_revizyonlar.json").read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "bes_yil_senaryo_ham.json").write_text((KOK / "bes_yil_senaryo_ham.json").read_text(encoding="utf-8"), encoding="utf-8")
    O.yaz(tmp_path, REFERANS)
    ilk = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    O.yaz(tmp_path, REFERANS)
    ikinci = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    assert ilk == ikinci


def test_stok_akis_degismez():
    once = {ad: (KOK / ad).read_bytes() for ad in SENARYO}
    metin = (KOK / "uc_kural_senaryo.py").read_text(encoding="utf-8")
    assert "ovp_revizyon" not in metin
    assert "import akis_model" not in Path(O.__file__).read_text(encoding="utf-8")
    O.yaz(KOK, REFERANS)
    sonra = {ad: (KOK / ad).read_bytes() for ad in SENARYO}
    assert once == sonra
    assert Params().tufe_yol == 0.28
    capa = json_capa()
    assert capa["stok_akis_baglanti"] is False
    assert "NFP" not in capa
    assert "borc_servis_orani_Ha" not in capa


def json_capa():
    import json
    return json.loads((KOK / "ovp_capalar.json").read_text(encoding="utf-8"))
