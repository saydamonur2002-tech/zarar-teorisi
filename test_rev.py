import json
from pathlib import Path
K = Path(__file__).resolve().parent
j = lambda a: json.loads((K / a).read_text(encoding="utf-8"))

def test_adim1_bant():
    r = j("rev_adim1_sonuc.json"); z = r["zaman_istikrari"]
    assert 0 < z["tam_graf_oran_min"] <= z["tam_graf_oran_2024"] <= z["tam_graf_oran_max"] < 1
    assert "yüzde 20" not in (K / "ADIM1_NACE.md").read_text(encoding="utf-8").split("## (e)")[1].split("kaldırıldı")[1]

def test_adim2_beta_tavan():
    r = j("rev_adim2_sonuc.json"); assert abs(r["beta_tavan"] - 0.0439) < 1e-3 and r["beta_bandi"][1] < 0.3

def test_adim3_psi_ve_yp():
    r = j("rev_adim3_sonuc.json"); assert 0.4 < r["yp_payi"]["2026-Q1"] < 0.7 and r["psi"]["evds_tl_yp"] > r["psi"]["eski_repo"]

def test_adim4_cift_sayim():
    c = j("rev_adim4_sonuc.json")["cift_sayim"]; assert c["ortusme_alt"] > 0 and c["adres_toplam_yeni_bandi"][1] < c["adres_toplam_eski"]

def test_adim45_a17():
    assert j("rev_adim45_sonuc.json")["fark"] == 0.0
