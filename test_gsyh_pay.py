"""GSYH payı: tutarlılık testleri (payda yolu varsayımdır)."""
import gsyh_pay as G


def test_yol_2025_olculen_ve_buyuyor():
    g, t = G.gsyh_yolu()
    assert abs(g[2025] - 63240.5) < 0.1
    assert all(g[y] > g[y - 1] for y in G.YILLAR)


def test_senaryo_sirasi():
    out, _ = G.akislar()
    for y in G.YILLAR:
        d, o, h = (sum(out[a][y].values()) for a in ("düşük", "orta", "yüksek"))
        assert d <= o <= h
