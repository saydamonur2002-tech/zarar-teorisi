#!/usr/bin/env python3
"""RG mekanizma boşluk skoru — kısa devre, bağ kimliği, aralık dışı yayım.

Aile medyanı model katsayısı değildir. Norm yok kayıtları aile medyanına girmez.
Aynı RG maddesi birden fazla satırda durabilir; endekste bağ kimliğiyle bir kez sayılır.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import median, pstdev, stdev

PENCERE = ("2018-01-01", "2026-09-15")
CEKIRDEK = (
    "yetki-görev",
    "ölçüt-tarife",
    "kaynak-ödenek",
    "veri-rapor",
    "denetim-yaptırım",
    "alım-yükümlülük",
)
MIN_N = 5
SAPMA_ESIK = 0.15  # 0-1 ölçekte; üstü heterojen, medyan endeks olmaz


@dataclass
class Metin:
    tarih: str
    sayi: str
    madde: str

    @property
    def bag(self) -> str:
        return f"{self.tarih}|{self.sayi}|{self.madde}"

    @property
    def aralik_disi(self) -> bool:
        return self.tarih < PENCERE[0] or self.tarih > PENCERE[1]


@dataclass
class Mekanizma:
    ad: str
    aile: str
    alt_tip: str
    skor: float
    birincil: str
    ikincil: list[str] = field(default_factory=list)
    metinler: list[Metin] = field(default_factory=list)
    norm_yok: bool = False

    @property
    def endekse_girer(self) -> bool:
        return not self.norm_yok

    @property
    def baglar(self) -> list[str]:
        return sorted({m.bag for m in self.metinler})


def yukle() -> list[Mekanizma]:
    m4 = Metin("2016-06-22", "29750", "m.4")
    m5 = Metin("2016-06-22", "29750", "m.5")
    m9 = Metin("2016-06-22", "29750", "m.9")
    m11 = Metin("2016-06-22", "29750", "m.11")
    m18 = Metin("2016-06-22", "29750", "m.18")
    b7222_16 = Metin("2020-02-25", "31050", "7222 m.16")
    b7222_20 = Metin("2020-02-25", "31050", "7222 m.20")
    b45 = Metin("2005-11-01", "25983", "m.45")
    b67 = Metin("2005-11-01", "25983", "m.67")
    b68 = Metin("2005-11-01", "25983", "m.68")
    t18 = Metin("2015-05-22", "29363", "m.18")
    t4 = Metin("2015-05-22", "29363", "m.4")
    t2 = Metin("2015-05-22", "29363", "m.2")
    vys18 = Metin("2021-07-14", "31541", "m.18")
    vys4 = Metin("2021-07-14", "31541", "m.4")
    vys6 = Metin("2021-07-14", "31541", "m.6")
    iik13 = Metin("2018-03-15", "30361", "7101 m.13")
    iik20 = Metin("2018-03-15", "30361", "7101 m.20")
    iik36 = Metin("2018-03-15", "30361", "7101 m.36")
    return [
        Mekanizma(
            "Donuk gün eşiği",
            "ölçüt-tarife",
            "sayı yazılı eşik",
            0.34,
            "yaptırım",
            ["biçimsel kaçış"],
            [m4, m5, b7222_16],
        ),
        Mekanizma(
            "Özel karşılık tabanı",
            "ölçüt-tarife",
            "kurum veya model",
            0.61,
            "süre",
            ["biçimsel kaçış", "bilinçli düzenlememe olabilir"],
            [m9, m11, b7222_16],
        ),
        Mekanizma(
            "SYR tabanı",
            "ölçüt-tarife",
            "sayı yazılı eşik",
            0.23,
            "süre",
            ["biçimsel kaçış"],
            [b45, b67, b68],
        ),
        Mekanizma(
            "Tüketici gecikme faizi",
            "ölçüt-tarife",
            "sayı yazılı eşik",
            0.25,
            "veri",
            ["veri bağsız"],
            [t18, t4, t2],
        ),
        Mekanizma(
            "Kart gecikme faizi",
            "ölçüt-tarife",
            "kurum veya model",
            0.70,
            "yaptırım",
            ["biçimsel kaçış"],
            [b7222_20],
        ),
        Mekanizma(
            "Asgari satış bedeli",
            "ölçüt-tarife",
            "oran hükmü yok",
            1.00,
            "norm yok",
            [],
            [vys18],
            norm_yok=True,
        ),
        Mekanizma(
            "Borç sona erdirme",
            "yetki-görev",
            "oran hükmü yok",
            1.00,
            "norm yok",
            [],
            [iik13, iik20, iik36],
            norm_yok=True,
        ),
        Mekanizma(
            "VYŞ faaliyet izni",
            "izin-ruhsat",
            "sayı yazılı eşik",
            0.10,
            "ölçüt",
            ["biçimsel kaçış"],
            [vys4, vys6],
        ),
        Mekanizma(
            "İhale ile devir",
            "alım-yükümlülük",
            "sayı yazılı eşik",
            0.34,
            "yaptırım",
            ["biçimsel kaçış"],
            [vys18, b7222_16],
        ),
        Mekanizma(
            "Hane-firma yayımlama",
            "veri-rapor",
            "oran hükmü yok",
            1.00,
            "norm yok",
            [],
            [m18],
            norm_yok=True,
        ),
        Mekanizma(
            "Gün kovası kaydı",
            "veri-rapor",
            "sayı yazılı eşik",
            0.51,
            "süre",
            ["yaptırım bağsız"],
            [m18, b7222_16],
        ),
        Mekanizma(
            "İdari para bandı",
            "denetim-yaptırım",
            "sayı yazılı eşik",
            0.35,
            "ölçüt",
            ["biçimsel kaçış"],
            [b7222_16],
        ),
    ]


def sapma(skorlar: list[float]) -> float | None:
    if len(skorlar) < 2:
        return None
    return stdev(skorlar) if len(skorlar) > 1 else 0.0


def aile_ozet(ad: str, kayitlar: list[Mekanizma]) -> dict:
    giren = [k for k in kayitlar if k.endekse_girer]
    skorlar = [k.skor for k in giren]
    s = sapma(skorlar)
    heterojen = s is not None and s >= SAPMA_ESIK
    endeks = None
    gerekce = "örnek küçük"
    if len(skorlar) >= MIN_N and not heterojen:
        endeks = round(median(skorlar), 2)
        gerekce = "medyan"
    elif len(skorlar) >= MIN_N and heterojen:
        gerekce = "heterojen, medyan endeks değil"
    return {
        "aile": ad,
        "n_satir": len(kayitlar),
        "n_endeks": len(skorlar),
        "n_norm_yok": sum(1 for k in kayitlar if k.norm_yok),
        "medyan_ham": round(median(skorlar), 2) if skorlar else None,
        "sapma": round(s, 2) if s is not None else None,
        "heterojen": heterojen,
        "endeks": endeks,
        "gerekce": gerekce,
    }


def main() -> None:
    kayitlar = yukle()
    print(f"PENCERE {PENCERE[0]} — {PENCERE[1]}")
    print(f"TARANAN {len(kayitlar)}  ELENEN 3 (Kurul kararı, taslak, teklif)")
    print()
    print("SATIR")
    for k in kayitlar:
        dis = sorted({m.tarih for m in k.metinler if m.aralik_disi})
        katman = "uygulanmadı" if k.norm_yok else "skorlandı"
        print(
            f"- {k.ad} | {k.aile} | {k.alt_tip} | skor {k.skor:.2f} | "
            f"{k.birincil} | katman {katman} | endeks {'hayır' if k.norm_yok else 'aday'} | "
            f"bağ {', '.join(k.baglar)} | aralık dışı {dis or 'yok'}"
        )
    print()
    print("NORM YOK — aile medyanına girmez")
    for k in kayitlar:
        if k.norm_yok:
            print(f"- {k.ad} | {k.aile} | 1.00 | yakın metin skor kapatmaz")
    print()
    print("BAĞ — aynı madde çok satır, endekste bir kez")
    bag_map: dict[str, list[str]] = {}
    for k in kayitlar:
        for b in k.baglar:
            bag_map.setdefault(b, []).append(k.ad)
    for b, adlar in sorted(bag_map.items()):
        if len(adlar) > 1:
            print(f"- {b} | n={len(adlar)} | {', '.join(adlar)}")
    print()
    aileler: dict[str, list[Mekanizma]] = {}
    for k in kayitlar:
        aileler.setdefault(k.aile, []).append(k)
    print("AİLE")
    for ad, grup in aileler.items():
        o = aile_ozet(ad, grup)
        print(
            f"- {ad}: satır {o['n_satir']}, endeks adayı {o['n_endeks']}, "
            f"norm yok {o['n_norm_yok']}, ham medyan {o['medyan_ham']}, "
            f"sapma {o['sapma']}, {o['gerekce']}, endeks {o['endeks']}"
        )
    print()
    print("ALT TİP — ölçüt-tarife, norm yok hariç")
    alt: dict[str, list[float]] = {}
    for k in kayitlar:
        if k.aile == "ölçüt-tarife" and k.endekse_girer:
            alt.setdefault(k.alt_tip, []).append(k.skor)
    for ad, skorlar in alt.items():
        s = sapma(skorlar)
        print(
            f"- {ad}: n={len(skorlar)}, medyan {median(skorlar):.2f}, "
            f"sapma {round(s, 2) if s is not None else 'yok'}, örnek küçük"
        )
    print()
    print("ÇEKİRDEK — medyan yalnız endeks koşulları tutarsa")
    for ad in CEKIRDEK:
        o = aile_ozet(ad, aileler.get(ad, []))
        print(f"- {ad}: {o['gerekce']} | endeks {o['endeks']}")
    print()
    print("MODEL GİRDİSİ: satır skoru ve bağ kimliği. Aile medyanı rapor satırı, katsayı değil.")
    print("ÖLÇÜLMEYEN: uygulama, fiili denetim, mali sapma. Etki yüzdesi yok.")
    print("KARŞI DÖNEM yok.")


if __name__ == "__main__":
    main()
