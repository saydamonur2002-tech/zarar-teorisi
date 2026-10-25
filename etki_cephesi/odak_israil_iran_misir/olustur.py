#!/usr/bin/env python3
"""İsrail, İran ve Mısır bölümünü mevcut dosyalardan üretir.

Model sayısını değiştirmez. Havza neti olmayan yere null yazar.
"""

from __future__ import annotations

import json
import zipfile
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

KOK = Path(__file__).resolve().parents[2]
DIZIN = Path(__file__).resolve().parent
HAVZA_YOL = KOK / "etki_cephesi" / "git-harm" / "data" / "havza_kayip.json"
PROJE_YOL = KOK / "etki_cephesi" / "data" / "PROJEKSIYON.json"
GERI_YOL = KOK / "etki_cephesi" / "git-harm" / "data" / "geri_kalan.json"
ZIP_YOL = KOK / "yayin" / "etki-cephesi-model.zip"
JSON_YOL = DIZIN / "odak_ulkeler.json"
NOT_YOL = DIZIN / "README.md"

SENARYO = ("A", "B", "C")
ULKELER = (
    {
        "kod": "IR",
        "ad": "İran",
        "havza": ("iran_guney", "iran_dogu", "iran_bati"),
    },
    {
        "kod": "EG",
        "ad": "Mısır",
        "havza": ("misir",),
    },
    {
        "kod": "IL",
        "ad": "İsrail",
        "havza": (),
    },
)
AKTOR_ALAN = (
    "aktor",
    "ad",
    "havza_kayip",
    "havza_net",
    "dis_kazanc_vekili",
    "kanal_kazanc",
    "ikame_kazanc",
    "merkez_sizinti",
    "merkez_belirsiz_vekil",
    "kayip_kapsam",
    "kazanc_kapsam",
    "net_kapsam",
    "surdurme_maliyeti",
    "surdurme_maliyet_belirsizligi",
    "surdurme_maliyet_orani",
    "net_birlesik_vekil",
    "net_birlesik_maliyetli",
    "durum",
)
DIS_ALAN = (
    "aktor",
    "ad",
    "kanal_kazanc",
    "matris_kazanc",
    "ikame_kazanc",
    "ikame_hesap_ham_havza_girisinde_sayildi",
    "fayda_endeks",
    "kanal_alternatif_kazanc",
)
YAN_KAYIT = (
    "data/etki_cephesi/gozlem/duyarlilik/phi_kosu1_rs_az.json",
    "data/etki_cephesi/gozlem/duyarlilik/phi_kosu3_phi1_uye.json",
    "data/etki_cephesi/gozlem/duyarlilik/anomali_2026_10_17.json",
)


def _yukle(yol: Path):
    return json.loads(yol.read_text(encoding="utf-8"))


def _sayi(deger: Decimal, basamak: str) -> float:
    nicel = deger.quantize(Decimal(basamak), rounding=ROUND_HALF_UP)
    return json.loads(format(nicel, "f"))


def _pay(net: Decimal, toplam: Decimal) -> float:
    return _sayi(abs(net) / abs(toplam) * Decimal(100), "0.01")


def _d(deger: float) -> Decimal:
    return Decimal(str(deger))


def _zip_json(arsiv: zipfile.ZipFile, uye: str):
    return json.loads(arsiv.read(uye))


def _havza_satir(kayit: dict, toplam: dict[str, Decimal]) -> dict:
    senaryolar = {}
    for ad in SENARYO:
        net = _d(kayit[ad]["net"])
        senaryolar[ad] = {"net": kayit[ad]["net"], "pay": _pay(net, toplam[ad])}
    return {"bolge": kayit["bolge"], "ad": kayit["ad"], "senaryolar": senaryolar}


def _aktor(senaryo: dict, kod: str) -> dict:
    kayit = next(a for a in senaryo["aktör_birlesik"] if a["aktor"] == kod)
    return {alan: kayit[alan] for alan in AKTOR_ALAN}


def _ulke_kaybi(senaryo: dict, kod: str) -> dict | None:
    kayit = next((a for a in senaryo["ulke_kayiplari"] if a.get("ulke") == kod), None)
    if kayit is None:
        return None
    return {k: v for k, v in kayit.items() if not isinstance(v, (dict, list))}


def _dis(senaryo: dict, kod: str) -> dict | None:
    kayit = next((a for a in senaryo["dis_aktör_kazanc"] if a.get("aktor") == kod), None)
    if kayit is None:
        return None
    return {alan: kayit[alan] for alan in DIS_ALAN}


def _pay_katsayilari(kod: str, havza_pay: dict, aktor_pay: dict, ulke_bolge: dict) -> dict:
    havza = []
    for bolge, satirlar in havza_pay["bolge_ulke_pay"].items():
        for satir in satirlar:
            if satir.get("ulke") == kod:
                havza.append({"bolge": bolge, "pay": satir["pay"]})
    aktor = []
    for bolge, paylar in aktor_pay["bolge_pay"].items():
        if kod in paylar:
            aktor.append({"bolge": bolge, "pay": paylar[kod]})
    bolge = []
    for ad, satirlar in ulke_bolge["bolge_ulkeler"].items():
        for satir in satirlar:
            if satir.get("iso") == kod:
                bolge.append(
                    {
                        "bolge": ad,
                        "kazanc_katsayi": satir["kazanc_katsayi"],
                        "zarar_katsayi": satir["zarar_katsayi"],
                    }
                )
    return {
        "not": "Katsayıdır, havza neti değildir. Kaynak zip içindeki girdi dosyaları.",
        "ulke_havza_pay": havza,
        "dis_aktor_bolge_pay": aktor,
        "ulkeler_bolge": bolge,
    }


def _ticaret(kod: str, ticaret: dict) -> dict:
    ihracat = ticaret["ihracat_mn_usd"].get(kod)
    gsyh = ticaret["gsyh_mn_usd"].get(kod)
    return {
        "kaynak": "yayin/etki-cephesi-model.zip data/etki_cephesi/gozlem/dis_ticaret_gsyh_2023.json",
        "yil": ticaret["yil"],
        "kalibrasyon_aktoru": kod in ticaret["kalibrasyon_aktorleri"],
        "gsyh_mn_usd": gsyh,
        "ihracat_mn_usd": ihracat,
    }


def _geri_kalan(kod: str, ad: str, geri: dict) -> dict | None:
    for aktor in geri["aktorler"]:
        if aktor.get("kod") == kod or aktor.get("ad") == ad:
            return aktor
    return None


def belge() -> dict:
    havza = _yukle(HAVZA_YOL)
    proje = _yukle(PROJE_YOL)
    geri = _yukle(GERI_YOL)
    toplam = {ad: _d(havza["toplam_net"][ad]) for ad in SENARYO}
    havza_indeks = {satir["bolge"]: satir for satir in havza["havzalar"]}
    senaryolar = {s["id"]: s for s in proje["senaryolar"]}
    with zipfile.ZipFile(ZIP_YOL) as arsiv:
        sistem = _zip_json(arsiv, "data/etki_cephesi/dis_ulke_sistemi.json")
        havza_pay = _zip_json(arsiv, "data/etki_cephesi/ulke_havza_pay.json")
        aktor_pay = _zip_json(arsiv, "data/etki_cephesi/dis_aktör_pay.json")
        ulke_bolge = _zip_json(arsiv, "data/etki_cephesi/ulkeler_bolge.json")
        ticaret = _zip_json(arsiv, "data/etki_cephesi/gozlem/dis_ticaret_gsyh_2023.json")
        gecen = {}
        for tanim in ULKELER:
            ad_b = tanim["ad"].encode()
            gecen[tanim["kod"]] = sum(1 for ad in arsiv.namelist() if ad_b in arsiv.read(ad))

    ulkeler = []
    for tanim in ULKELER:
        kod = tanim["kod"]
        satirlar = []
        for bolge in tanim["havza"]:
            if bolge not in havza_indeks:
                raise SystemExit(f"havza yok: {bolge}")
            satirlar.append(_havza_satir(havza_indeks[bolge], toplam))
        if satirlar:
            senaryo_toplam = {}
            for ad in SENARYO:
                net = sum((_d(s["senaryolar"][ad]["net"]) for s in satirlar), Decimal(0))
                senaryo_toplam[ad] = {"net": _sayi(net, "0.001"), "pay": _pay(net, toplam[ad])}
            ulke_toplam = {
                "kaynak": "havza netlerinin toplamı; pay otuz havza toplamına göre",
                "senaryolar": senaryo_toplam,
            }
        else:
            ulke_toplam = None
        aktor = {ad: _aktor(senaryolar[ad], kod) for ad in SENARYO}
        if ulke_toplam is None:
            havza_eslesme = None
        else:
            havza_eslesme = {
                ad: aktor[ad]["havza_net"] == ulke_toplam["senaryolar"][ad]["net"]
                for ad in SENARYO
            }
        sistem_ulke = sistem["ulkeler"][kod]
        ulkeler.append(
            {
                "kod": kod,
                "ad": tanim["ad"],
                "havza_dosyasinda": bool(satirlar),
                "havzalar": satirlar or None,
                "ulke_toplam": ulke_toplam,
                "aktor_havza_neti_toplama_esit": havza_eslesme,
                "aktor": {
                    "kaynak": "PROJEKSIYON.json senaryolar[].aktör_birlesik",
                    "senaryolar": aktor,
                },
                "ulke_kaybi": {
                    "kaynak": "PROJEKSIYON.json senaryolar[].ulke_kayiplari",
                    "senaryolar": {ad: _ulke_kaybi(senaryolar[ad], kod) for ad in SENARYO},
                },
                "dis_aktor_kazanc": {
                    "kaynak": "PROJEKSIYON.json senaryolar[].dis_aktör_kazanc",
                    "senaryolar": {ad: _dis(senaryolar[ad], kod) for ad in SENARYO},
                },
                "sistem": {
                    "kaynak": "yayin/etki-cephesi-model.zip data/etki_cephesi/dis_ulke_sistemi.json",
                    "ad": sistem_ulke["ad"],
                    "rol": sistem_ulke["rol"],
                    "refah_endeks": sistem_ulke["refah_endeks"],
                },
                "pay_katsayilari": _pay_katsayilari(kod, havza_pay, aktor_pay, ulke_bolge),
                "ticaret_2023": _ticaret(kod, ticaret),
                "geri_kalan_aktor": _geri_kalan(kod, tanim["ad"], geri),
                "zipte_ad_gecen_uye": gecen[kod],
            }
        )
    return {
        "olusturan": "etki_cephesi/odak_israil_iran_misir/olustur.py",
        "sayi_uydurulmadi": True,
        "pay_kurali": "yuzde = mutlak net / otuz havza net toplamının mutlak değeri × 100; iki ondalık, yarım yukarı",
        "havza_toplam_net": havza["toplam_net"],
        "havza_kaynak": "etki_cephesi/git-harm/data/havza_kayip.json",
        "projeksiyon_kaynak": "etki_cephesi/data/PROJEKSIYON.json",
        "israil_havza_notu": (
            "İsrail havza_kayip.json otuz havzasında ve geri_kalan.json aktörlerinde yok. "
            "Kendi havza neti ve ülke toplamı null. Aktör IL PROJEKSIYON.json içinde var; "
            "başka havzaların pay katsayılarında da geçer. O katsayılar net değildir."
        ),
        "yan_kayit_ana_model_okumaz": {
            "not": "Bu dosyalarda IR, IL ve EG sayıları vardır. Dosyaların kendi notu ana modelin onları okumadığını söyler. Bölüm o sayıları kopyalamaz.",
            "dosyalar": list(YAN_KAYIT),
        },
        "ulkeler": ulkeler,
    }


def _hucre(deger) -> str:
    if deger is None:
        return "—"
    if isinstance(deger, float):
        return format(deger, "f").rstrip("0").rstrip(".")
    return str(deger)


def _tablo(baslik: list[str], satirlar: list[list[object]]) -> str:
    govde = [
        "| " + " | ".join(baslik) + " |",
        "| " + " | ".join("---" for _ in baslik) + " |",
    ]
    for satir in satirlar:
        govde.append("| " + " | ".join(_hucre(h) for h in satir) + " |")
    return "\n".join(govde)


def not_metni(data: dict) -> str:
    by = {u["kod"]: u for u in data["ulkeler"]}
    parcalar = [
        "# Odak: İsrail, İran, Mısır",
        "",
        "Bu bölüm modeli değiştirmez. Sayılar `olustur.py` ile mevcut dosyalardan okunur. Havza satırı olmayan yer null kalır.",
        "",
        "Yenilemek, repo kökünden: `python3 etki_cephesi/odak_israil_iran_misir/olustur.py`.",
        "",
        "Havza payı, `havza_kayip.json` ile aynı kuraldır: mutlak net bölü otuz havzanın net toplamının mutlak değeri, yüzde, iki ondalık. Toplam net A −15,247, B −25,727, C −9,899.",
        "",
        "## İran",
        "",
        "Üç havza. Ülke toplamı bu üç netin toplamıdır. Aktör kodu IR. Aktör defterindeki `havza_net`, üç havzanın toplamına eşittir.",
        "",
    ]
    parcalar.append(_havza_tablosu(by["IR"]))
    parcalar.extend(["", "## Mısır", ""])
    parcalar.append(
        "Tek havza: `misir`, Kuzey Afrika — Mısır (Nil). Ülke toplamı bu satırdır. Aktör kodu EG. Aktör defterindeki `havza_net` bu havza satırından farklıdır; iki kaynak yan yana durur, biri diğerine çekilmedi."
    )
    parcalar.extend(["", _havza_tablosu(by["EG"]), ""])
    parcalar.extend(
        [
            "## İsrail",
            "",
            data["israil_havza_notu"],
            "",
            "Kendi havza neti: null. Ülke toplamı: null.",
            "",
            "Bulunan İsrail sayıları aktör defterindedir (kod IL), 2023 dış ticaret gözleminde ve başka havzalara yazılmış pay katsayılarındadır. Katsayı, o havzanın neti değildir.",
            "",
            "`ulke_havza_pay.json` içindeki İsrail payı:",
            "",
            _tablo(
                ["Havza", "ulke_havza_pay"],
                [[s["bolge"], s["pay"]] for s in by["IL"]["pay_katsayilari"]["ulke_havza_pay"]],
            ),
            "",
            "`dis_aktör_pay.json` içindeki İsrail payı. Aynı havza adı iki dosyada ayrı katsayı taşır.",
            "",
            _tablo(
                ["Havza", "dis_aktör_pay"],
                [[s["bolge"], s["pay"]] for s in by["IL"]["pay_katsayilari"]["dis_aktor_bolge_pay"]],
            ),
            "",
        ]
    )
    parcalar.extend(["## Aktör defteri", "", "Kaynak: `PROJEKSIYON.json` `aktör_birlesik`. Birim vekil.", ""])
    baslik = ["Ülke", "Senaryo", "havza_net", "dış kazanç", "net, maliyet düşülmüş", "durum"]
    satirlar = []
    for kod in ("IR", "EG", "IL"):
        ulke = by[kod]
        for ad in SENARYO:
            a = ulke["aktor"]["senaryolar"][ad]
            satirlar.append(
                [ulke["ad"], ad, a["havza_net"], a["dis_kazanc_vekili"], a["net_birlesik_maliyetli"], a["durum"]]
            )
    parcalar.append(_tablo(baslik, satirlar))
    parcalar.extend(["", "## Gözlem, 2023", ""])
    parcalar.append(
        "Kaynak, güncel model zipindeki `data/etki_cephesi/gozlem/dis_ticaret_gsyh_2023.json`. İhracat ortak ülke vektörü `odak_ulkeler.json` içindedir. GSYH milyon dolar."
    )
    parcalar.extend(["", _tablo(
        ["Ülke", "kalibrasyon aktörü", "GSYH mn $", "ihracat ortağı"],
        [
            [
                by[kod]["ad"],
                "evet" if by[kod]["ticaret_2023"]["kalibrasyon_aktoru"] else "hayır",
                by[kod]["ticaret_2023"]["gsyh_mn_usd"],
                len(by[kod]["ticaret_2023"]["ihracat_mn_usd"] or {}),
            ]
            for kod in ("IR", "EG", "IL")
        ],
    )])
    parcalar.extend(
        [
            "",
            "## Sistem ve pay katsayısı",
            "",
            "Rol ve refah endeksi `dis_ulke_sistemi.json` içindedir. Pay katsayıları `ulke_havza_pay.json`, `dis_aktör_pay.json` ve `ulkeler_bolge.json` içindedir. Üçü de zip girdisidir. Ayrıntı `odak_ulkeler.json`.",
            "",
            _tablo(
                ["Ülke", "rol", "refah endeksi", "kendi havzası"],
                [
                    [
                        by[kod]["ad"],
                        by[kod]["sistem"]["rol"],
                        by[kod]["sistem"]["refah_endeks"],
                        "var" if by[kod]["havza_dosyasinda"] else "yok",
                    ]
                    for kod in ("IR", "EG", "IL")
                ],
            ),
            "",
            "## Okunmayan yan kayıt",
            "",
            data["yan_kayit_ana_model_okumaz"]["not"],
            "",
        ]
    )
    for yol in data["yan_kayit_ana_model_okumaz"]["dosyalar"]:
        parcalar.append(f"- `{yol}`")
    parcalar.extend(
        [
            "",
            "`geri_kalan.json` aktörlerinde İran, Mısır ve İsrail yoktur.",
            "",
        ]
    )
    return "\n".join(parcalar)


def _havza_tablosu(ulke: dict) -> str:
    satirlar = []
    for havza in ulke["havzalar"] or []:
        satir = [havza["ad"]]
        for ad in SENARYO:
            hucre = havza["senaryolar"][ad]
            satir.extend([hucre["net"], hucre["pay"]])
        satirlar.append(satir)
    if ulke["ulke_toplam"] is None:
        satirlar.append(["ülke toplamı", "—", "—", "—", "—", "—", "—"])
    else:
        satir = ["ülke toplamı"]
        for ad in SENARYO:
            hucre = ulke["ulke_toplam"]["senaryolar"][ad]
            satir.extend([hucre["net"], hucre["pay"]])
        satirlar.append(satir)
    return _tablo(["", "A net", "A pay", "B net", "B pay", "C net", "C pay"], satirlar)


def yaz() -> None:
    data = belge()
    JSON_YOL.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    NOT_YOL.write_text(not_metni(data), encoding="utf-8")


def main() -> None:
    yaz()
    print(f"Yazıldı: {JSON_YOL.relative_to(KOK)}")
    print(f"Yazıldı: {NOT_YOL.relative_to(KOK)}")


if __name__ == "__main__":
    main()
