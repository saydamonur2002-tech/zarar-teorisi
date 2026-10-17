import csv
import json
from pathlib import Path

import rev_sok as rs

K = Path(__file__).resolve().parent


def _j():
    return json.loads((K / "rev_sok_sonuc.json").read_text(encoding="utf-8"))


def _grup(rows, *anahtar):
    out = {}
    for h in rows:
        out.setdefault(tuple(h[a] for a in anahtar), []).append(h)
    return out


def test_degerle_pay_ve_stok():
    s, y = rs.degerle(100.0, 0.5, 0.2)
    assert abs(s - 110.0) < 1e-12 and abs(y - 0.6 / 1.1) < 1e-12
    s0, y0 = rs.degerle(25339.8, 0.5444, 0.0)
    assert s0 == 25339.8 and y0 == 0.5444


def test_faiz_sifir_kur_kilitli_tabloyla_ayni():
    girdi = rs.yukle()
    assert abs(girdi["yp_yayin"] - 0.5444) < 1e-9
    oz = list(csv.DictReader((K / "rev_adim3_ozet.csv").open(encoding="utf-8-sig")))
    for r in oz:
        yl = rs.faiz_yillik(0, girdi["G"][r["g"]], r["r"], float(r["kappa"]), girdi)
        assert round(yl["2029"], 1) == float(r["I_2029_milyar"])
        assert round(yl["2031"], 1) == float(r["I_2031_milyar"])
        assert abs(yl["2029"] + (-yl["2029"])) == 0.0


def test_cikti_monoton_ve_sfc():
    s = _j()
    faiz = s["faiz"]
    for h in faiz:
        assert h["nl_toplam"] == 0.0 and h["nl_F"] == h["I_2029"] and h["nl_karsi"] == -h["I_2029"]
        assert h["I_2031"] + 1e-9 >= h["I_2029"]
    for _, grup in _grup(faiz, "g", "r", "kappa").items():
        ys = [h["I_2029"] for h in sorted(grup, key=lambda h: h["kur_yuzde"])]
        assert ys == sorted(ys)
    for _, grup in _grup(faiz, "kur_yuzde", "g", "r").items():
        ys = [h["I_2029"] for h in sorted(grup, key=lambda h: h["kappa"])]
        assert ys == sorted(ys) and ys[0] < ys[-1]
    sira = {a: i for i, a in enumerate(("dusus", "sabit", "yuksek"))}
    for _, grup in _grup(faiz, "kur_yuzde", "g", "kappa").items():
        ys = [h["I_2029"] for h in sorted(grup, key=lambda h: sira[h["r"]])]
        assert ys == sorted(ys)
    gsira = {a: i for i, a in enumerate(("sifir", "min", "medyan", "max", "stres"))}
    for _, grup in _grup(faiz, "kur_yuzde", "r", "kappa").items():
        ys = [h["I_2029"] for h in sorted(grup, key=lambda h: gsira[h["g"]])]
        assert ys == sorted(ys) and ys[0] < ys[-1]
    for h in s["kopru"]:
        assert h["nl_toplam"] == 0.0 and h["nl_F"] == -h["artis"] and h["nl_karsi"] == h["artis"]
    for _, grup in _grup(s["kopru"], "etiket").items():
        grup = sorted(grup, key=lambda h: h["kur_yuzde"])
        assert [h["kredi"] for h in grup] == sorted(h["kredi"] for h in grup)
        assert [h["temerrut"] for h in grup] == sorted(h["temerrut"] for h in grup)
    kilit = {("olcum", 0): (3, 52.4), ("lambda*_max", 0): (3, 45.0)}
    for h in s["kopru"]:
        if (h["etiket"], h["kur_yuzde"]) in kilit:
            assert (h["temerrut"], h["kredi"]) == kilit[(h["etiket"], h["kur_yuzde"])]


def test_kenar_toplami_artisla_ayni():
    girdi = rs.yukle()
    for kur in (0, 10, 30):
        g, artis = rs.ag_kur(kur, 1.0, girdi)
        top = sum(b.tutar for b in g.borclar if b.alacakli == "BANKA")
        assert abs(top - artis) < 1e-6
        if kur == 0:
            assert "BANKA" not in g.firmalar


def test_seyrek_yogunluk_ve_esik():
    s = _j()
    sy = {x["yogunluk"]: x for x in s["seyrek"]}
    assert sy[1.0]["temerrut_medyan"] == 3 and sy[1.0]["kredi_medyan"] == 52.4
    assert sy[0.25]["temerrut_min"] > 3 and sy[0.25]["kredi_min"] > 52.4
    med = [sy[d]["kredi_medyan"] for d in (0.25, 0.5, 0.75, 1.0)]
    assert med == sorted(med, reverse=True)
    e = s["esik_kopru"]["olcum"]
    assert e["kopru_yuzde"] == 1 and e["temerrut_yuzde"] == 3
    em = s["esik_kopru"]["lambda*_max"]
    assert em["kopru_yuzde"] == 3 and em["temerrut_yuzde"] == 4
    assert s["esik_faiz_fg_ust_yuzde"] is not None
    k1 = s["stres"]["hucre"]["k1"]
    assert k1["oran_FG_2029"] > s["girdi"]["fg_ust_yayin"]
    assert s["karar"]["adim2"]["kosul_bozulur"] is True
    assert s["karar"]["adim4"]["kanal"] is False
    assert "## Şok testleri" in (K / "YAPILABILIRLIK.md").read_text(encoding="utf-8")
