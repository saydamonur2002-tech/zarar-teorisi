#!/usr/bin/env python3
"""Geriye netinin işaretini κ, pol ve dolar köprüsüne göre gezdirir.

Model sayısını, varsayımı ve data/geriye.json dosyasını değiştirmez.
Formül scripts/mfin_maliyet.py ile aynıdır. Notu ISARET_DUYARLILIK.md olarak yazar.
"""

from __future__ import annotations

import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mfin_maliyet as m  # noqa: E402

KOK = Path(__file__).resolve().parents[1]
GERIYE = KOK / "data" / "geriye.json"
NOT = KOK / "ISARET_DUYARLILIK.md"

KAPPA_IZGARA = (
    Decimal("0"),
    Decimal("0.10"),
    Decimal("0.20"),
    Decimal("0.35"),
    Decimal("0.50"),
    Decimal("0.70"),
    Decimal("1"),
)
POL_IZGARA = (
    Decimal("0"),
    Decimal("0.41"),
    Decimal("0.70"),
    Decimal("0.95"),
    Decimal("1"),
)


def _d(value: Decimal | float | str) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _q(value: Decimal, basamak: str) -> str:
    return format(value.quantize(Decimal(basamak), rounding=ROUND_HALF_UP), "f")


def _parca(ad: str) -> dict[str, Decimal]:
    girdi = m.SENARYO[ad]
    kazanc = _d(girdi["kazanc"])
    return {
        "kazanc": kazanc,
        "pol": _d(girdi["pol"]),
        "kayip_oran": _d(girdi["kayip"]) / kazanc,
        "kayip_bel_oran": _d(girdi["kayip_bel"]) / kazanc,
    }


def _maliyet_bel_oran(pol: Decimal) -> Decimal:
    lo, hi = m.KAPPA_BANT
    return (hi - lo) / 2 * pol


def _bant_oran(kayip_bel_oran: Decimal, pol: Decimal) -> Decimal:
    maliyet_bel = _maliyet_bel_oran(pol)
    return (kayip_bel_oran**2 + maliyet_bel**2).sqrt()


def _net_oran(kayip_oran: Decimal, kappa: Decimal, pol: Decimal) -> Decimal:
    return Decimal("1") - kayip_oran - kappa * pol


def _isaret(deger: Decimal) -> str:
    if deger > 0:
        return "artı"
    if deger < 0:
        return "eksi"
    return "sıfır"


def _aralik(net: Decimal, bant: Decimal) -> str:
    if net - bant > 0:
        return "yalnız artı"
    if net + bant < 0:
        return "yalnız eksi"
    return "sıfırı örter"


def _kappa_esik(kayip_oran: Decimal, pol: Decimal) -> Decimal | None:
    """Nokta netin sıfır olduğu κ. pol = 0 ise maliyet yoktur, eşik yok."""
    if pol == 0:
        return None
    return (Decimal("1") - kayip_oran) / pol


def _pol_esik(kayip_oran: Decimal, kappa: Decimal) -> Decimal | None:
    if kappa == 0:
        return None
    return (Decimal("1") - kayip_oran) / kappa


def _yayin_kontrol() -> None:
    """Yayımlanan maliyet ve net, betikteki sabitlerle aynı kalsın."""
    for ad, girdi in m.SENARYO.items():
        maliyet, _bel, _oran = m.surdurme(girdi["kazanc"], girdi["pol"])
        net = float(
            m._yuvarla(
                _d(girdi["kazanc"]) - _d(girdi["kayip"]) - _d(maliyet),
                "0.001",
            )
        )
        if abs(maliyet - girdi["yayin_maliyet"]) > 1e-9 or abs(net - girdi["yayin_net"]) > 1e-9:
            raise SystemExit(f"{ad} yayın noktası sapıyor")


def _geriye_kontrol() -> dict:
    belge = json.loads(GERIYE.read_text(encoding="utf-8"))
    for satir in belge["senaryolar"]:
        alt = satir["net_mn"] - satir["bant_mn"]
        ust = satir["net_mn"] + satir["bant_mn"]
        if not (alt < 0 < ust):
            raise SystemExit(f"{satir['ad']} bandı sıfırı örtmüyor: {alt} .. {ust}")
        if satir["net_mn"] <= 0:
            raise SystemExit(f"{satir['ad']} nokta neti artı değil")
    return belge


def _tablo(baslik: list[str], satirlar: list[list[str]]) -> str:
    govde = ["| " + " | ".join(baslik) + " |", "| " + " | ".join("---" for _ in baslik) + " |"]
    govde.extend("| " + " | ".join(s) + " |" for s in satirlar)
    return "\n".join(govde)


def notu_yaz() -> str:
    _yayin_kontrol()
    belge = _geriye_kontrol()
    parcalar = {ad: _parca(ad) for ad in m.SENARYO}
    satirlar = []
    for s in belge["senaryolar"]:
        alt = s["net_mn"] - s["bant_mn"]
        ust = s["net_mn"] + s["bant_mn"]
        satirlar.append(
            [
                s["ad"],
                _q(_d(s["pol"]), "0.01"),
                _q(_d(s["net_mn"]), "0.1"),
                _q(_d(s["bant_mn"]), "0.1"),
                _q(_d(alt), "0.1"),
                _q(_d(ust), "0.1"),
                "sıfırı örter",
            ]
        )
    yayin_tablo = _tablo(
        ["Senaryo", "pol", "net mn $", "bant", "alt", "üst", "aralık"],
        satirlar,
    )

    esik_satir = []
    for ad, p in parcalar.items():
        kappa_esik = _kappa_esik(p["kayip_oran"], p["pol"])
        pol_esik = _pol_esik(p["kayip_oran"], m.KAPPA)
        esik_satir.append(
            [
                ad,
                _q(p["pol"], "0.01"),
                _q(kappa_esik, "0.001") if kappa_esik is not None else "—",
                _q(pol_esik, "0.001") if pol_esik is not None else "—",
            ]
        )
    esik_tablo = _tablo(
        ["Senaryo", "yayımlanan pol", "noktayı sıfırlayan κ", "κ=0,20 iken noktayı sıfırlayan pol"],
        esik_satir,
    )

    kappa_satir = []
    for kappa in KAPPA_IZGARA:
        hucre = [_q(kappa, "0.01")]
        for ad, p in parcalar.items():
            net = _net_oran(p["kayip_oran"], kappa, p["pol"])
            bant = _bant_oran(p["kayip_bel_oran"], p["pol"])
            hucre.append(f"{_isaret(net)}; {_aralik(net, bant)}")
        kappa_satir.append(hucre)
    kappa_tablo = _tablo(["κ", "A nokta; aralık", "B nokta; aralık", "C nokta; aralık"], kappa_satir)

    pol_satir = []
    for pol in POL_IZGARA:
        hucre = [_q(pol, "0.01")]
        for _ad, p in parcalar.items():
            net = _net_oran(p["kayip_oran"], m.KAPPA, pol)
            bant = _bant_oran(p["kayip_bel_oran"], pol)
            hucre.append(f"{_isaret(net)}; {_aralik(net, bant)}")
        pol_satir.append(hucre)
    pol_tablo = _tablo(
        ["pol", "A nokta; aralık", "B nokta; aralık", "C nokta; aralık"],
        pol_satir,
    )

    bant_satir = []
    for ad, p in parcalar.items():
        sifir_maliyet_net = Decimal("1") - p["kayip_oran"]
        bant = _bant_oran(p["kayip_bel_oran"], p["pol"])
        bant_satir.append(
            [
                ad,
                _q(p["kayip_bel_oran"], "0.0001"),
                _q(_maliyet_bel_oran(p["pol"]), "0.0001"),
                _q(bant, "0.0001"),
                _q(sifir_maliyet_net, "0.0001"),
                _aralik(sifir_maliyet_net, bant),
            ]
        )
    bant_tablo = _tablo(
        [
            "Senaryo",
            "kayıp bel / kazanç",
            "maliyet bel / kazanç",
            "bant / kazanç",
            "κ=0 net / kazanç",
            "κ=0 aralık",
        ],
        bant_satir,
    )

    kopru_satir = []
    for ad, girdi in m.SENARYO.items():
        _maliyet, maliyet_bel, _oran = m.surdurme(girdi["kazanc"], girdi["pol"])
        bant = m.net_bant(girdi["kayip_bel"], maliyet_bel)
        net = girdi["yayin_net"]
        hucre = [ad, _q(_d(net), "0.001"), _q(_d(bant), "0.001")]
        for ad_kopru in ("bop", "mal", "rant"):
            hucre.append(str(m.milyar(net, ad_kopru)))
        kopru_satir.append(hucre)
    kopru_tablo = _tablo(
        ["Senaryo", "net vekil", "bant vekil", "net BoP", "net mal", "net rant"],
        kopru_satir,
    )

    bant_kopru = []
    for ad, girdi in m.SENARYO.items():
        _maliyet, maliyet_bel, _oran = m.surdurme(girdi["kazanc"], girdi["pol"])
        bant = m.net_bant(girdi["kayip_bel"], maliyet_bel)
        hucre = [ad]
        for ad_kopru in ("bop", "mal", "rant"):
            net_d = m.milyar(girdi["yayin_net"], ad_kopru)
            bant_d = m.milyar(bant, ad_kopru)
            hucre.append(_aralik(_d(net_d), _d(bant_d)))
        bant_kopru.append(hucre)
    bant_kopru_tablo = _tablo(["Senaryo", "BoP aralık", "mal aralık", "rant aralık"], bant_kopru)

    metin = f"""# Geriye netinin işareti

`data/geriye.json` üç senaryoda nokta neti artı yazar ve bant sıfırı örter. Bu not model sayısını değiştirmez. Formül `scripts/mfin_maliyet.py` ile aynıdır. Yenilemek, bu dizinden: `python3 scripts/isaret_duyarlilik.py`.

Kazanç gözlenen net yatırım geliridir (dosyada {belge["kazanc_mn"]} mn $, {belge["bas"]} – {belge["son"]}). Kayıp ve maliyet, ileri defterdeki oranlarla bu kazançtan düşülür. Oran kazançla ölçeklendiği için işaret, on yıllık toplamda da yıl dilimlerinde de aynıdır.

## Yayımlanan dosya

{yayin_tablo}

Nokta formülü `net = kazanç − kayıp − κ × pol × kazanç`, κ = 0,20. Bant, kayıp vekilinin belirsizliği ile κ bandının (0,10–0,35) yarı genişliğinden gelen maliyet belirsizliğinin karekök toplamıdır. Maliyet belirsizliği seçilen κ'ya değil, bandın genişliğine bağlıdır.

## Nokta işareti

Nokta net, `κ × pol < 1 − kayıp/kazanç` iken artıdır. Yayımlanan pol'de bu eşiğin altındaki her κ noktayı artı bırakır. κ = 0,20 iken noktayı eksiye çeken pol, üç senaryoda da 1'in üstündedir; pol 0 ile 1 arasında noktayı çevirmez.

{esik_tablo}

κ bandının tavanı 0,35, üç eşiğin de altındadır. Bant içindeki κ nokta işaretini değiştirmez.

{kappa_tablo}

pol taraması κ'yı 0,20'de tutar. Aralık sütunu yayımlanan belirsizlik formülünü o pol'e taşır.

{pol_tablo}

## Aralığın sıfırı örtmesi

Aralığı genişleten terim kayıp belirsizliğidir. A ve B'de bu terim, sürdürme maliyeti sıfır olsa bile (κ = 0) netten büyüktür; aralık sıfırı örter. C'de kayıp belirsizliği κ = 0 netinden küçüktür. Yayımlanan pol'de (0,95) maliyet belirsizliği eklenince C de sıfırı örter. pol = 0 iken maliyet belirsizliği kalkar ve C'nin aralığı yalnız artı kalır; A ve B gene sıfırı örter.

{bant_tablo}

## Dolar köprüsü

Üç köprü (BoP {m.KOPRU["bop"]}, mal {m.KOPRU["mal"]}, rant {m.KOPRU["rant"]} mn $ / vekil) pozitif ölçektir. Vekili `köprü / 1000` ile çarpar. İşareti ve aralığın sıfırı örtüp örtmediğini değiştirmez; yalnız dolar büyüklüğünü yaklaşık iki kat oynatır.

`geriye.json` bu köprüyü kullanmaz. Geriye net, gözlenen milyon doların oranıdır. Köprü seçimi o dosyadaki işarete girmez. Aşağıdaki tablo ileri vekil netin dolar karşılığıdır.

{kopru_tablo}

{bant_kopru_tablo}

## Okuma

Yayımlanan κ ve pol nokta neti artı bırakır. Üç bandın sıfırı örtmesi, noktanın eksi olmasından gelmez; kayıp vekiline yazılan belirsizlik netten büyüktür. Dolar köprüsü bu hükmü değiştirmez.
"""
    NOT.write_text(metin, encoding="utf-8")
    return metin


def main() -> None:
    metin = notu_yaz()
    print(metin)
    print(f"Yazıldı: {NOT.relative_to(KOK)}")


if __name__ == "__main__":
    main()
