"""Odak bölümündeki sayıların kaynak dosyalarla aynı kaldığını denetler."""

from __future__ import annotations

import importlib.util
import json
import zipfile
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

DIZIN = Path(__file__).resolve().parent
KOK = DIZIN.parents[1]


def _modul():
    yol = DIZIN / "olustur.py"
    spec = importlib.util.spec_from_file_location("odak_olustur", yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _sayi(deger: Decimal, basamak: str) -> float:
    nicel = deger.quantize(Decimal(basamak), rounding=ROUND_HALF_UP)
    return json.loads(format(nicel, "f"))


def test_dosya_betikle_ayni():
    mod = _modul()
    disk = json.loads((DIZIN / "odak_ulkeler.json").read_text(encoding="utf-8"))
    assert disk == mod.belge()
    assert (DIZIN / "README.md").read_text(encoding="utf-8") == mod.not_metni(disk)


def test_havza_ve_toplam_kaynakla_ayni():
    mod = _modul()
    odak = mod.belge()
    havza = json.loads(mod.HAVZA_YOL.read_text(encoding="utf-8"))
    indeks = {s["bolge"]: s for s in havza["havzalar"]}
    assert odak["havza_toplam_net"] == havza["toplam_net"]
    by = {u["kod"]: u for u in odak["ulkeler"]}

    for bolge in ("iran_guney", "iran_dogu", "iran_bati"):
        kaynak = indeks[bolge]
        bulunan = next(h for h in by["IR"]["havzalar"] if h["bolge"] == bolge)
        for ad in ("A", "B", "C"):
            assert bulunan["senaryolar"][ad]["net"] == kaynak[ad]["net"]
            assert bulunan["senaryolar"][ad]["pay"] == kaynak[ad]["pay"]
    iran_esit = {}
    for ad in ("A", "B", "C"):
        toplam = sum((Decimal(str(indeks[b][ad]["net"])) for b in ("iran_guney", "iran_dogu", "iran_bati")), Decimal(0))
        pay = _sayi(abs(toplam) / abs(Decimal(str(havza["toplam_net"][ad]))) * Decimal(100), "0.01")
        assert by["IR"]["ulke_toplam"]["senaryolar"][ad]["net"] == _sayi(toplam, "0.001")
        assert by["IR"]["ulke_toplam"]["senaryolar"][ad]["pay"] == pay
        iran_esit[ad] = True
    assert by["IR"]["aktor_havza_neti_toplama_esit"] == {"A": True, "B": True, "C": True}

    misir = indeks["misir"]
    assert len(by["EG"]["havzalar"]) == 1
    for ad in ("A", "B", "C"):
        assert by["EG"]["havzalar"][0]["senaryolar"][ad]["net"] == misir[ad]["net"]
        assert by["EG"]["havzalar"][0]["senaryolar"][ad]["pay"] == misir[ad]["pay"]
        assert by["EG"]["ulke_toplam"]["senaryolar"][ad]["net"] == misir[ad]["net"]
        assert by["EG"]["aktor"]["senaryolar"][ad]["havza_net"] != misir[ad]["net"]
    assert iran_esit == {"A": True, "B": True, "C": True}


def test_israil_havzasi_yok_aktor_sayisi_kaynakta():
    mod = _modul()
    odak = mod.belge()
    havza = json.loads(mod.HAVZA_YOL.read_text(encoding="utf-8"))
    proje = json.loads(mod.PROJE_YOL.read_text(encoding="utf-8"))
    geri = json.loads(mod.GERI_YOL.read_text(encoding="utf-8"))
    adlar = " ".join(f"{s['bolge']} {s['ad']}" for s in havza["havzalar"])
    assert "İsrail" not in adlar
    assert "israil" not in adlar.casefold()
    israil = next(u for u in odak["ulkeler"] if u["kod"] == "IL")
    assert israil["havza_dosyasinda"] is False
    assert israil["havzalar"] is None
    assert israil["ulke_toplam"] is None
    assert israil["geri_kalan_aktor"] is None
    assert israil["aktor"]["senaryolar"]["A"]["havza_net"] == -0.232

    for kod in ("IR", "EG", "IL"):
        ulke = next(u for u in odak["ulkeler"] if u["kod"] == kod)
        assert ulke["geri_kalan_aktor"] is None
        for senaryo in proje["senaryolar"]:
            kaynak = next(a for a in senaryo["aktör_birlesik"] if a["aktor"] == kod)
            kopya = ulke["aktor"]["senaryolar"][senaryo["id"]]
            for alan in mod.AKTOR_ALAN:
                assert kopya[alan] == kaynak[alan]
            kayip = next(a for a in senaryo["ulke_kayiplari"] if a["ulke"] == kod)
            assert ulke["ulke_kaybi"]["senaryolar"][senaryo["id"]]["net_endeks"] == kayip["net_endeks"]
    assert all(a["kod"] not in {"IR", "EG", "IL"} for a in geri["aktorler"])


def test_zip_girdisi_ve_yan_kayit():
    mod = _modul()
    odak = mod.belge()
    by = {u["kod"]: u for u in odak["ulkeler"]}
    with zipfile.ZipFile(mod.ZIP_YOL) as arsiv:
        sistem = json.loads(arsiv.read("data/etki_cephesi/dis_ulke_sistemi.json"))
        ticaret = json.loads(arsiv.read("data/etki_cephesi/gozlem/dis_ticaret_gsyh_2023.json"))
        havza_pay = json.loads(arsiv.read("data/etki_cephesi/ulke_havza_pay.json"))
    for kod in ("IR", "EG", "IL"):
        assert by[kod]["sistem"]["rol"] == sistem["ulkeler"][kod]["rol"]
        assert by[kod]["sistem"]["refah_endeks"] == sistem["ulkeler"][kod]["refah_endeks"]
        assert by[kod]["ticaret_2023"]["gsyh_mn_usd"] == ticaret["gsyh_mn_usd"][kod]
        assert by[kod]["ticaret_2023"]["ihracat_mn_usd"] == ticaret["ihracat_mn_usd"][kod]
    israil_pay = [s for s in by["IL"]["pay_katsayilari"]["ulke_havza_pay"]]
    assert israil_pay
    assert all(s["pay"] == next(x["pay"] for x in havza_pay["bolge_ulke_pay"][s["bolge"]] if x["ulke"] == "IL") for s in israil_pay)
    for yol in odak["yan_kayit_ana_model_okumaz"]["dosyalar"]:
        metin = (KOK / yol).read_text(encoding="utf-8")
        assert "IL" in metin or "İsrail" in metin
    assert "model_kayip" not in json.dumps(by["IL"]["aktor"])
