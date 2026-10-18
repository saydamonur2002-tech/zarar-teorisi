import csv
import json
from pathlib import Path

import fisher_ayrisma as f

K = Path(__file__).resolve().parent
j = lambda a: json.loads((K / a).read_text(encoding="utf-8"))  # noqa: E731


def test_fisher_ozdesligi():
    for i, pi in ((53.1925, 29.73), (10, 5), (5, 0), (30, 40), (0, 0)):
        a = f.ayristir(i, pi)
        assert abs((1 + i / 100) - (1 + a["reel_tam"] / 100) * (1 + pi / 100)) < 1e-12
        assert abs(a["reel_tam"] * (1 + pi / 100) - (i - pi)) < 1e-9  # i − π = r(1+π)
        assert abs(a["reel_tam"] + a["capraz"] - a["reel_yaklasik"]) < 1e-9
    assert abs(f.reel_tam(53.1925, 29.73) - 18.086) < 1e-3


def test_uluslararasi_fisher():
    assert abs(f.ima_edilen_deger_kaybi(46.79, 7.71) - 36.28) < 0.01
    assert f.ima_edilen_deger_kaybi(8, 8) == 0
    # ima edilen artış kadar değer kaybında YP kredi, TL kredi faizine eşit maliyetli olur
    assert abs(f.yp_kredi_tl_maliyeti(7.71, f.ima_edilen_deger_kaybi(46.79, 7.71)) - 46.79) < 1e-9


def test_enflasyon_yolu_ara_degerleri():
    pi = j("fisher_ayrisma_sonuc.json")["enflasyon_yollari"]
    for ad in ("anket", "alt"):
        y = {int(k): v for k, v in pi[ad].items()}
        assert y[2028] > y[2029] > y[2030] > y[2031]
        assert abs(y[2029] - (y[2028] + (y[2031] - y[2028]) / 3)) < 0.01  # doğrusal ara değer
    assert f.ara_degerle({2026: 10.0, 2028: 20.0}, 2026, 2028)[2027] == 15.0


def test_ay_ekle_ve_sira():
    assert f.ay_ekle("2026-01", -12) == "2025-01" and f.ay_ekle("2025-12", 1) == "2026-01"
    assert f.sira([30, 10, 20, 20]) == [4.0, 1.0, 2.5, 2.5]


def test_tufe_girdi_tutarliligi():
    k = j("fisher_ayrisma_sonuc.json")["kontrol"]  # endeksten türetilen = acik_veri_ozet.json ölçülen
    assert abs(k["tufe_2026_01_endeksten"] - k["tufe_2026_01_olculen"]) < 0.05


def test_guncel_eslesen_ay():
    g = j("fisher_ayrisma_sonuc.json")["guncel"]
    assert g["donem"] == "2026-09" and abs(g["tufe_yillik"] - 29.73) < 1e-9
    k = g["kredi"]
    assert abs(k["reel_yaklasik"] - (k["nominal"] - k["enflasyon"])) < 1e-9 and k["reel_tam"] < k["reel_yaklasik"]
    u = g["uluslararasi_fisher"]
    assert u["ima_edilen_12ay"] > u["gerceklesen_12ay_geri"] > 0 and u["yp_kredi_tl_maliyeti_anket"] < u["i_tl"]


def test_adim3_yeniden_kurma_dogru():
    a3 = j("fisher_ayrisma_sonuc.json")["adim3"]
    assert a3["yeniden_kurma_en_buyuk_goreli_fark"] < 1e-3  # TL + YP parçaları rev_adim3.csv ile örtüşür
    assert a3["yeniden_kurma_en_buyuk_fark_milyar"] < 2.0
    for x in a3["kappa1_medyan_ozet"]:
        # YP payı json'da 4 haneye yuvarlı: beklenen göreli hata ≈ 5e-5·(r_USD − r_TL)/karışık faiz ≈ 8e-5
        assert abs(x["I_TL_milyar"] + x["I_YP_milyar"] - x["I_toplam_milyar"]) < 1e-4 * x["I_toplam_milyar"]
        assert 0 < x["enflasyon_payi_TL_anket"] < 1 and x["enflasyon_payi_TL_alt"] < x["enflasyon_payi_TL_anket"]


def test_adim3_yillik_toplam_kaynakla_ayni():
    # fisher_ayrisma_adim3.csv yıllık I_toplam, rev_adim3_ozet.csv'deki 2029 ve 2031 ile aynı
    oz = {(r["g"], r["r"], r["kappa"]): r for r in csv.DictReader(open(K / "rev_adim3_ozet.csv", encoding="utf-8-sig"))}
    for r in csv.DictReader(open(K / "fisher_ayrisma_adim3.csv", encoding="utf-8-sig")):
        if r["yil"] in ("2029", "2031"):
            beklenen = float(oz[(r["g"], r["r"], r["kappa"])][f"I_{r['yil']}_milyar"])
            assert abs(float(r["I_toplam_milyar"]) - beklenen) < 1.0


def test_adim4_prim_kurali_ve_endeks_bacagi():
    for x in j("fisher_ayrisma_sonuc.json")["adim4"]:
        assert x["prim_kural_farki_milyar"] < 0.5  # prim_ceyrek = başlangıç stoku × prim / 4
        if x["prim_milyar"]:
            assert x["endeks_alt_milyar"] < x["endeks_anket_milyar"]
            pi = j("fisher_ayrisma_sonuc.json")["enflasyon_yollari"]["anket"][str(x["yil"])]
            beklenen = pi / (float(x["prim_orani"]) * 100)  # oran = π / prim; prim_ceyrek 0,1'e yuvarlı, küçük tabanda %1'e kadar sapar
            assert abs(x["endeks_prim_oran_anket"] - beklenen) < 0.01 * beklenen


def test_adim3_ve_adim4_dosyalari_degismedi():
    # bu çalışma mevcut çıktılara yazmaz; adim4 csv'de endeks bacağı hâlâ 'hesaplanmadı'
    satir = next(csv.DictReader(open(K / "adim4_adres_yonlendirme.csv", encoding="utf-8-sig")))
    assert "hesaplanmadi" in satir["endeks_bacagi"]
