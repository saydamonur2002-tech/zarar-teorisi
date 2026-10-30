#!/usr/bin/env python3
"""MFİN sürdürme maliyetini ve geçmiş 10 yıl geriye netini ölçer.

Formül, zarar-teorisi dalındaki `_surdurme_alanlari` ile aynıdır:

    oran = kappa * pol
    maliyet = round(oran * kazanç, 3)
    belirsizlik = round((kappa_hi - kappa_lo) / 2 * pol * kazanç, 3)

Girdiler `yayin/KAZANC_KAYIP_MUHASEBE.md` ve `SENARYO_KARSILASTIRMA.md`
tablolarından. Kappa ölçülmüş fatura değil; dosyanın varsayımı (0,20; bant 0,10–0,35).
Yalnız TR muaf. MFİN de maliyete katlanır.
"""

from __future__ import annotations

import csv
import json
import math
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

GOZLEM = Path(__file__).resolve().parents[1] / "data" / "evds_odeme_dengesi_aylik.csv"

KAPPA = Decimal("0.20")
KAPPA_BANT = (Decimal("0.10"), Decimal("0.35"))

# Kazanç ve kayıp vekili: KAZANC_KAYIP_MUHASEBE, K1 sonrası defter.
# pol: SENARYO_KARSILASTIRMA bölüm 10 (0,20 × pol).
SENARYO = {
    "A": {
        "kazanc": 7.825,
        "pol": 0.70,
        "kayip": 3.445,
        "kayip_bel": 6.156,
        "yayin_maliyet": 1.096,
        "yayin_net": 3.284,
    },
    "B": {
        "kazanc": 17.539,
        "pol": 0.41,
        "kayip": 12.030,
        "kayip_bel": 18.688,
        "yayin_maliyet": 1.438,
        "yayin_net": 4.071,
    },
    "C": {
        "kazanc": 3.918,
        "pol": 0.95,
        "kayip": 1.279,
        "kayip_bel": 2.603,
        "yayin_maliyet": 0.744,
        "yayin_net": 1.895,
    },
}


def _d(value: float) -> Decimal:
    return Decimal(str(value))


def _yuvarla(value: Decimal, basamak: str) -> Decimal:
    """Yayın tablosu yarımda yukarı yuvarlar. İkili float round() A'da 1,095'e düşer."""
    return value.quantize(Decimal(basamak), rounding=ROUND_HALF_UP)


def surdurme(kazanc: float, pol: float) -> tuple[float, float, float]:
    """MFİN sürdürme maliyeti ve kappa bandının yarı aralığı."""
    kazanc_d = _d(kazanc)
    pol_d = _d(pol)
    oran = KAPPA * pol_d
    maliyet = _yuvarla(oran * kazanc_d, "0.001")
    lo, hi = KAPPA_BANT
    belirsizlik = _yuvarla((hi - lo) / 2 * pol_d * kazanc_d, "0.001")
    return float(maliyet), float(belirsizlik), float(_yuvarla(oran, "0.0001"))


# Dosyanın üç USD köprüsü, mn $ / vekil. BoP için metindeki 2.589,12.
# Aynı vekil, yıllık akış ölçeğinde: C'de TR kaybı 43–90 milyar $/yıl bu üç oranla çıkar.
KOPRU = {
    "bop": Decimal("2589.12"),
    "mal": Decimal("4785"),
    "rant": Decimal("5383"),
}


def milyar(vekil: float, kopru: str) -> Decimal:
    """Vekili milyar dolara çevirir. 1 vekil × (mn $/vekil) / 1000."""
    return _yuvarla(_d(vekil) * KOPRU[kopru] / Decimal("1000"), "0.01")


def net_bant(kayip_bel: float, maliyet_bel: float) -> float:
    """Sınıf bandı: kayıp vekilinin belirsizliği ile maliyet belirsizliği, karesel."""
    return round(math.sqrt(kayip_bel**2 + maliyet_bel**2), 3)


def olc() -> list[dict[str, float | str]]:
    satirlar = []
    for ad, girdi in SENARYO.items():
        maliyet, maliyet_bel, oran = surdurme(girdi["kazanc"], girdi["pol"])
        net = float(
            _yuvarla(_d(girdi["kazanc"]) - _d(girdi["kayip"]) - _d(maliyet), "0.001")
        )
        bant = net_bant(girdi["kayip_bel"], maliyet_bel)
        if abs(maliyet - girdi["yayin_maliyet"]) > 1e-9:
            raise SystemExit(f"{ad} maliyeti yayından sapıyor: {maliyet} != {girdi['yayin_maliyet']}")
        if abs(net - girdi["yayin_net"]) > 1e-9:
            raise SystemExit(f"{ad} neti yayından sapıyor: {net} != {girdi['yayin_net']}")
        satirlar.append(
            {
                "senaryo": ad,
                "kazanc": girdi["kazanc"],
                "pol": girdi["pol"],
                "oran": oran,
                "maliyet": maliyet,
                "maliyet_bel": maliyet_bel,
                "kayip": girdi["kayip"],
                "kayip_bel": girdi["kayip_bel"],
                "net": net,
                "bant": bant,
                "pay": round(maliyet / girdi["kazanc"], 4),
            }
        )
    return satirlar


def gozlem_aylari() -> list[tuple[str, Decimal, Decimal, Decimal]]:
    """Ay, net (gider−gelir), gider, gelir. Birim: milyon dolar."""
    with GOZLEM.open(encoding="utf-8", newline="") as handle:
        aylar = []
        for row in csv.DictReader(handle):
            gider = Decimal(row["YG_yatirim_geliri_gideri"])
            gelir = Decimal(row["YG_yatirim_geliri_geliri"])
            aylar.append((row["Donem"], gider - gelir, gider, gelir))
    return aylar


def son_on_yil() -> list[tuple[str, Decimal, Decimal, Decimal]]:
    """Dosyanın son 120 ayı: 2016-09 .. 2026-08."""
    pencere = gozlem_aylari()[-120:]
    if len(pencere) != 120:
        raise SystemExit(f"120 ay yok: {len(pencere)}")
    return pencere


def gecmis_on_yil() -> dict[str, Decimal | str]:
    """Son 120 ayın gözlenen kazancı: net yatırım geliri = gider − gelir."""
    pencere = son_on_yil()
    return {
        "bas": pencere[0][0],
        "son": pencere[-1][0],
        "net": sum((m[1] for m in pencere), Decimal("0")),
        "gider": sum((m[2] for m in pencere), Decimal("0")),
        "gelir": sum((m[3] for m in pencere), Decimal("0")),
    }


def _geriye_oran(ad: str) -> dict[str, Decimal]:
    """İleri defterdeki birimsiz oranlar. Geçmişte ayrı ölçüm yok; ölçek bunlar."""
    girdi = SENARYO[ad]
    kazanc = _d(girdi["kazanc"])
    pol = _d(girdi["pol"])
    lo, hi = KAPPA_BANT
    return {
        "kayip": _d(girdi["kayip"]) / kazanc,
        "maliyet": KAPPA * pol,
        "kayip_bel": _d(girdi["kayip_bel"]) / kazanc,
        "maliyet_bel": (hi - lo) / 2 * pol,
    }


def geriye_uygula(kazanc_mn: Decimal, ad: str) -> dict[str, Decimal]:
    """Gözlenen kazanca ileri formülü uygular.

    kayıp = kazanç × (ileri kayıp / ileri kazanç)
    maliyet = kazanç × 0,20 × pol
    net = kazanç − kayıp − maliyet
    bant = kazanç × karekök(kayıp belirsizliği² + maliyet belirsizliği²)
    """
    oran = _geriye_oran(ad)
    kayip = kazanc_mn * oran["kayip"]
    maliyet = kazanc_mn * oran["maliyet"]
    net = kazanc_mn - kayip - maliyet
    bant = kazanc_mn * (oran["kayip_bel"] ** 2 + oran["maliyet_bel"] ** 2).sqrt()
    return {
        "kazanc": kazanc_mn,
        "kayip": kayip,
        "maliyet": maliyet,
        "net": net,
        "bant": bant,
        "kayip_oran": oran["kayip"],
        "maliyet_oran": oran["maliyet"],
        "bant_oran": bant / kazanc_mn if kazanc_mn else Decimal("0"),
    }


def yil_dilimleri(
    pencere: list[tuple[str, Decimal, Decimal, Decimal]],
) -> list[tuple[str, str, Decimal]]:
    """On adet Eylül–Ağustos dilimi. Her dilim 12 ay."""
    if len(pencere) != 120:
        raise SystemExit(f"yıl dilimi 120 ay ister: {len(pencere)}")
    dilimler = []
    for i in range(10):
        parca = pencere[i * 12 : (i + 1) * 12]
        kazanc = sum((ay[1] for ay in parca), Decimal("0"))
        dilimler.append((parca[0][0], parca[-1][0], kazanc))
    return dilimler


def _mn(value: Decimal) -> float:
    return float(_yuvarla(value, "0.1"))


def geriye_yaz() -> dict[str, object]:
    """Geriye neti data/geriye.json dosyasına yazar."""
    pencere = son_on_yil()
    toplam = gecmis_on_yil()
    kazanc = Decimal(str(toplam["net"]))
    senaryolar = []
    for ad in SENARYO:
        satir = geriye_uygula(kazanc, ad)
        senaryolar.append(
            {
                "ad": ad,
                "pol": SENARYO[ad]["pol"],
                "kayip_mn": _mn(satir["kayip"]),
                "maliyet_mn": _mn(satir["maliyet"]),
                "net_mn": _mn(satir["net"]),
                "bant_mn": _mn(satir["bant"]),
                "kayip_oran": float(_yuvarla(satir["kayip_oran"], "0.0001")),
                "maliyet_oran": float(_yuvarla(satir["maliyet_oran"], "0.0001")),
                "bant_oran": float(_yuvarla(satir["bant_oran"], "0.0001")),
            }
        )
    yillar = []
    for bas, son, dilim_kazanc in yil_dilimleri(pencere):
        netler = {ad: _mn(geriye_uygula(dilim_kazanc, ad)["net"]) for ad in SENARYO}
        yillar.append(
            {
                "bas": bas,
                "son": son,
                "etiket": f"{bas[:4]}/{son[2:4]}",
                "kazanc_mn": _mn(dilim_kazanc),
                "net_mn": netler,
            }
        )
    dilim_toplam = sum(Decimal(str(yil["kazanc_mn"])) for yil in yillar)
    if dilim_toplam != _yuvarla(kazanc, "0.1"):
        raise SystemExit(f"yıl dilimleri toplamı kazanca eşit değil: {dilim_toplam} != {kazanc}")
    belge = {
        "bas": toplam["bas"],
        "son": toplam["son"],
        "gider_mn": _mn(Decimal(str(toplam["gider"]))),
        "gelir_mn": _mn(Decimal(str(toplam["gelir"]))),
        "kazanc_mn": _mn(kazanc),
        "senaryolar": senaryolar,
        "yillar": yillar,
    }
    hedef = Path(__file__).resolve().parents[1] / "data" / "geriye.json"
    hedef.parent.mkdir(parents=True, exist_ok=True)
    hedef.write_text(json.dumps(belge, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return belge


def main() -> None:
    print("MFİN sürdürme maliyeti  (birim: defter vekili, dolar değil)")
    print("maliyet = round(0,20 × pol × kazanç, 3)")
    print()
    baslik = f"{'senaryo':<8}{'maliyet':>10}{'±maliyet':>10}{'net':>10}{'±bant':>10}{'pay':>8}"
    print(baslik)
    print("-" * len(baslik))
    for s in olc():
        print(
            f"{s['senaryo']:<8}{s['maliyet']:>10.3f}{s['maliyet_bel']:>10.3f}"
            f"{s['net']:>10.3f}{s['bant']:>10.3f}{s['pay']:>8.1%}"
        )
    print()
    print("Yayın tablosuyla aynı: A 1,096 · B 1,438 · C 0,744.")
    print("±maliyet, kappa 0,10–0,35 aralığının yarı genişliği × pol × kazanç.")
    print("±bant, kayıp vekili belirsizliği ile maliyet belirsizliğinin karesel toplamı.")
    print()
    print("Parasal hacim, milyar $/yıl  (BoP 2.589,12 · mal 4.785 · rant 5.383 mn $/vekil)")
    baslik = f"{'senaryo':<8}{'maliyet BoP':>12}{'maliyet mal':>12}{'maliyet rant':>13}{'kazanç BoP':>12}{'kazanç rant':>12}"
    print(baslik)
    print("-" * len(baslik))
    for s in olc():
        print(
            f"{s['senaryo']:<8}"
            f"{milyar(float(s['maliyet']), 'bop'):>12}"
            f"{milyar(float(s['maliyet']), 'mal'):>12}"
            f"{milyar(float(s['maliyet']), 'rant'):>13}"
            f"{milyar(float(s['kazanc']), 'bop'):>12}"
            f"{milyar(float(s['kazanc']), 'rant'):>12}"
        )
    print()
    print("Tek dolar yok: üç köprü yaklaşık 2 kat ayrılıyor. C'de MFIN kenarı, BoP ile 10.144 mn $; bu, kazanç satırı.")
    print()
    g = gecmis_on_yil()
    kazanc = Decimal(str(g["net"]))
    print(f"Geriye hesap, {g['bas']} .. {g['son']}, milyon dolar")
    print("Kazanç = gözlenen net yatırım geliri (gider − gelir).")
    print("Kayıp = kazanç × (ileri kayıp / ileri kazanç). Maliyet = kazanç × 0,20 × pol.")
    print(f"gider {g['gider']:,}  gelir {g['gelir']:,}  kazanç {kazanc:,} mn $")
    print()
    baslik = f"{'senaryo':<8}{'kayıp':>12}{'maliyet':>12}{'net':>12}{'±bant':>12}"
    print(baslik)
    print("-" * len(baslik))
    for ad in SENARYO:
        s = geriye_uygula(kazanc, ad)
        print(
            f"{ad:<8}{float(s['kayip']):>12,.0f}{float(s['maliyet']):>12,.0f}"
            f"{float(s['net']):>12,.0f}{float(s['bant']):>12,.0f}"
        )
    print()
    print("Yıl dilimleri, Eylül–Ağustos, net milyon dolar")
    baslik = f"{'dilim':<10}{'kazanç':>12}{'net A':>12}{'net B':>12}{'net C':>12}"
    print(baslik)
    print("-" * len(baslik))
    for bas, son, dilim in yil_dilimleri(son_on_yil()):
        netler = {ad: geriye_uygula(dilim, ad)["net"] for ad in SENARYO}
        etiket = f"{bas[:4]}/{son[2:4]}"
        print(
            f"{etiket:<10}{float(dilim):>12,.0f}"
            f"{float(netler['A']):>12,.0f}{float(netler['B']):>12,.0f}{float(netler['C']):>12,.0f}"
        )
    print()
    print("Dosya bu geriye neti koşmamış. Sayı, aynı defter oranlarının gözlenen akışa uygulanması.")
    print("Üç noktada net artı. Üçünde de bant sıfırı örtüyor; işaret belli değil.")
    geriye_yaz()
    print("Yazıldı: data/geriye.json")


if __name__ == "__main__":
    main()
