"""Hane taksit/gelir payı. Stok-akış kimliğine ve L matrisine yazılmaz.

Pay: kart hariç tüketici kredisi stoku (ihtiyaç + taşıt + konut) / TÜİK hane kullanılabilir geliri.
Faiz: TCMB stok serisi TP.BKR.TRY.KTFTUK, yıl sonu (Aralık).
Katsayı: i / (1 - (1+i)^(-n)). Vade uzadıkça katsayı faize yaklaşır.
18 yıl, BIS hane serisinin vade varsayımıdır. 5 yıl, kısa vade ihtimalidir; ölçülmüş kalan vade değildir.
2025 kullanılabilir geliri yayımlanmadığı için yerli oran 2024'te durur.
"""
import json
from pathlib import Path

DIR = Path(__file__).parent

# stok/gelir ve Aralık stok faizi, kullanıcı tablosu (2024 stok 2.012 milyar TL, kart 1.795 milyar TL)
YILLAR = (
    {"yil": 2022, "stok_gelir": 0.117, "faiz": 0.231},
    {"yil": 2023, "stok_gelir": 0.093, "faiz": 0.347},
    {"yil": 2024, "stok_gelir": 0.075, "faiz": 0.530, "tuketici_stok_milyarTL": 2012, "kart_stok_milyarTL": 1795},
)
VADELER = (18, 5)

# BIS hane serisi, 1999-Q1..2026-Q1, 109 çeyrek, kendi ortalamasından sapma (puan). Türkiye bu 17'de yok.
BIS_HANE_SAPMA = {"NO": 6.2, "DK": -4.8, "NL": -3.8}

# BIS özel kesim toplamı / GSYH. Ortalama 2002-Q1..2026-Q1, n=97.
OZEL_KESIM = {"2024Q4": 0.287, "2026Q1": 0.258, "ortalama": 0.137, "sapma_puan": 12.1}


def katsayi(faiz, vade):
    if faiz <= 0:
        return 1.0 / vade
    return faiz / (1.0 - (1.0 + faiz) ** (-vade))


def satir(stok_gelir, faiz, vade):
    k = katsayi(faiz, vade)
    taksit = stok_gelir * k
    faiz_pay = stok_gelir * faiz
    return {
        "taksit_gelir": taksit,
        "faiz_gelir": faiz_pay,
        "anapara_gelir": taksit - faiz_pay,
    }


def ozet():
    yillar = []
    for row in YILLAR:
        hucre = {
            "yil": row["yil"],
            "stok_gelir": row["stok_gelir"],
            "aralik_faiz": row["faiz"],
        }
        for v in VADELER:
            s = satir(row["stok_gelir"], row["faiz"], v)
            hucre[f"taksit_gelir_{v}y"] = round(s["taksit_gelir"], 4)
            hucre[f"anapara_gelir_{v}y"] = round(s["anapara_gelir"], 4)
        hucre["faiz_gelir"] = round(row["stok_gelir"] * row["faiz"], 4)
        yillar.append(hucre)
    son = yillar[-1]
    return {
        "nesne": "kart hariç tüketici kredisi taksiti / hane kullanılabilir geliri",
        "kimlige_giris": "yok",
        "L_giris": "yok",
        "aciklama": "Borç açılışı NL işlemidir. Kayıp, ödeme dönmeyince L ile dağılır. Bu pay ikisine de yazılmaz.",
        "faiz_serisi": "TP.BKR.TRY.KTFTUK",
        "kart": "2024 kart stoku 1.795 milyar TL, tüketici stoku 2.012 milyar TL. Kart orana girmez.",
        "yillar": yillar,
        "2024_taksit_gelir_18y": son["taksit_gelir_18y"],
        "2024_taksit_gelir_5y": son["taksit_gelir_5y"],
        "2024_faiz_gelir": son["faiz_gelir"],
        "bis_hane_2026Q1_eksi_ortalama_puan": BIS_HANE_SAPMA,
        "turkiye_ozel_kesim_gsyh": OZEL_KESIM,
    }


def main():
    out = ozet()
    (DIR / "hane_taksit_ozeti.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
