"""Prim tavanı. Ödenen prim, ölçülmüş ikame tasarrufu yoksa 0.

R gerçekleşen: repoda hedef patikası yok (adim4 kagit_patikasi endeks bacağı
«hesaplanmadi»). İthalat faturası tavan, gerçekleşen R değil.

Tavan rakamları Ticaret Bakanlığı Ekonomik Görünüm Aralık 2025, BEC milyon USD.
Kaynak: https://ticaret.gov.tr/data/5e18288613b8761dccd355ce/Ekonomik%20Görünüm%202025%20Aralık.pdf
TÜİK derler; bu dosya bakanlık PDF satırını kullanır. 2024 ara 238.253, sermaye 50.633,
tüketim 54.469, toplam 344.010. 2025 ara 250.228, sermaye 54.892, tüketim 59.237,
toplam 365.524. Enerji / fası 27: 2024 65.590, 2025 62.590 milyon USD.
Kur: faiz_kur_ham aylık ortalama (aday: stok kuru değil, ortalama).
Ara maldan tüm fası 27'yi düşürmek örtüşme kimliği değildir (aday).
"""
from __future__ import annotations

from ortak import adres, r2, r4, usd_ay, yaz_csv, yaz_json

# milyon USD, bakanlık PDF
BEC = {
    "2024": {"ara": 238253.0, "sermaye": 50633.0, "tuketim": 54469.0, "toplam": 344010.0, "enerji": 65590.0},
    "2025": {"ara": 250228.0, "sermaye": 54892.0, "tuketim": 59237.0, "toplam": 365524.0, "enerji": 62590.0},
}
KAYNAK = "https://ticaret.gov.tr/data/5e18288613b8761dccd355ce/Ekonomik%20Görünüm%202025%20Aralık.pdf"


def ortalama(yil: str, usd: dict[str, float]) -> tuple[float, int]:
    xs = [v for k, v in usd.items() if k.startswith(yil + "-")]
    if not xs:
        raise SystemExit(yil)
    return sum(xs) / len(xs), len(xs)


def tl(musd: float, kur: float) -> float:
    return musd * kur / 1000.0


def main():
    A = adres()
    usd = usd_ay()
    kur = {}
    for yil in ("2024", "2025", "2026"):
        ort, n = ortalama(yil, usd)
        son = [k for k in sorted(usd) if k.startswith(yil + "-")][-1]
        kur[yil] = {"ortalama": r4(ort), "n": n, "son_ay": son, "son": r4(usd[son])}
    tavan = {}
    for yil, b in BEC.items():
        k = kur[yil]["ortalama"]
        ara, enerji = tl(b["ara"], k), tl(b["enerji"], k)
        tavan[yil] = {
            "kur_ortalama": k,
            "ara": r2(ara),
            "enerji": r2(enerji),
            "ara_eksi_enerji": r2(ara - enerji),
            "ara_arti_sermaye": r2(ara + tl(b["sermaye"], k)),
            "toplam": r2(tl(b["toplam"], k)),
            "musd": b,
        }
    dar_2025 = tavan["2025"]["ara_eksi_enerji"]
    hucre = []
    for theta in (0.10, 0.30):
        for ad, AA in (("on", A["A_on"]), ("uc", A["A_uc"])):
            M = theta * AA
            for pi in (0.02, 0.05):
                kupon = pi * M
                hucre.append({
                    "theta": theta,
                    "adres": ad,
                    "A": AA,
                    "pi": pi,
                    "M": r2(M),
                    "tasarim_kupon": r2(kupon),
                    "pay_dar_2025": r4(100.0 * kupon / dar_2025),
                    "odenen": 0.0,
                    "tau": 0,
                    "nl_toplam": 0.0,
                    "neden": "R olculmedi; endeks 1.00; Pi = tau * min(pi*M, R) = 0",
                })
    out = {
        "etiket": "aday: kur ortalamasi ve ara-enerji cikarma; gerceklesen R olculmedi",
        "kaynak": KAYNAK,
        "derleyen": "TÜİK, bakanlık PDF satırı",
        "kur": kur,
        "tavan_milyar_tl": tavan,
        "dar_2025": dar_2025,
        "kupon": hucre,
        "sfc": {
            "tau0": "NL hepsi 0, toplam 0",
            "tau1_R_yeterli": "yalniz kupon kadar ikame yazilir: NL_H = +Pi, NL_D = -Pi, toplam 0",
            "havadan": "K' primi R'siz oderse toplam NL yine 0; RAPOR 'Prim havadan gelmez' bozulur",
        },
    }
    yaz_json("prim_tavan_sonuc.json", out)
    yaz_csv(
        "prim_tavan.csv",
        ["theta", "adres", "pi", "M", "tasarim_kupon", "pay_dar_2025", "odenen"],
        hucre,
    )
    print("prim dar", dar_2025, "kupon", hucre[0]["tasarim_kupon"], hucre[-1]["tasarim_kupon"])


if __name__ == "__main__":
    main()
