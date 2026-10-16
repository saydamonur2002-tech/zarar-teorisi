"""Tekstil ve giyim: üç değişkenin ölçülüp ölçülemediği.

Sınıf kaynağı İş Yatırım alt sektörüdür. KAP sektör kodu bu dosyada yoktur.
Medyanlar toplanmaz. Teşvik sınıfı yalnızca okunan dipnottan gelir.
Bilinmeyen, yararlanmayan sayılmaz.
"""
from __future__ import annotations

import csv
import json
import math
import re
import statistics
from collections import defaultdict
from pathlib import Path

from marj_dipnot import blok_ayir
from tesvik_secilim import ozet, sinif_metin

ROOT = Path("/workspace")
KAP = Path("/tmp/kap_tekstil")
ESKI = Path("/tmp/kap_tur3")
TRADE = Path("/tmp/comtrade_tekstil")

HOLDING_AD = {"ARSAN", "DERHL", "RALYH"}
# Ad ve bilinen ürün: ikinci bir NACE kodu değil. Rapor bunu "ad okuması" diye yazar.
COK_SEKTOR_AD = {
    "SASA": "polyester; kimya ile tekstil sınırı, ad okuması",
    "AKSA": "elyaf; endüstriyel tekstil, ad okuması",
    "KORDS": "kord bezi; otomotiv ve tekstil, ad okuması",
    "KOPOL": "polyester; ad okuması",
    "MEGAP": "polietilen köpük; tekstil dışı ürün adı",
    "BAYRK": "taban; ayakkabı ara malı, ad okuması",
    "ISSEN": "sentetik; ad okuması",
}


def fnum(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def cekirdek_tutar(r):
    xs = [fnum(r.get(k)) for k in ("brut", "paz", "gy", "arge")]
    if any(x is None for x in xs):
        return None
    return sum(xs)


def marj_oran(r, tutar):
    s = fnum(r.get("satis"))
    if not s or tutar is None:
        return None
    return tutar / s


def metin_yolu(kod, yil):
    for klasor in (KAP, ESKI):
        p = klasor / f"{kod}_{yil}.txt"
        if p.exists() and p.stat().st_size > 500:
            return p
    return None


def json_yolu(kod):
    for klasor in (KAP, ESKI):
        p = klasor / f"{kod}.json"
        if p.exists():
            return p
    return None


def _eko(blok):
    if not blok or blok.get("durum") != "kapandi":
        return None
    flip = (blok.get("toplam") or 0) < 0
    return {k: (-blok[k] if flip else blok[k]) for k in ("kur", "faiz", "diger", "toplam")}


def satir_tesvik(metin: str):
    """Teşvik ifadesi ile aynı satırdaki muhasebe kalemi. Komşu sütun sayılmaz."""
    if not metin:
        return []
    bulunan = []
    for line in metin.splitlines():
        u = line.lower()
        if not any(k in u for k in ("teşvik", "tesvik", "yatırıma katkı", "yatirima katki")):
            continue
        if any(k in u for k in ("kıdem", "kidem", "kiralama")):
            continue
        pencere = re.sub(r"\s+", " ", line).strip()[:180]
        if any(k in u for k in ("sgk", "5510", "istihdam teşvik", "sigorta prim")):
            ad = "personel gideri"
        elif any(k in u for k in ("faiz destek", "faiz indir")):
            ad = "finansman gideri"
        elif any(k in u for k in ("yatırıma katkı", "yatirima katki", "kurumlar vergisi indir")):
            ad = "vergi gideri"
        elif any(k in u for k in ("teşvik gelir", "tesvik gelir", "destek gelir", "teşvik ve destek")):
            ad = "diger faaliyet geliri"
        else:
            ad = "satir_belirlenemiyor"
        bulunan.append({"satir": ad, "pencere": pencere})
    # aynı satır adı bir kez
    gor = []
    cikti = []
    for s in bulunan:
        if s["satir"] in gor:
            continue
        gor.append(s["satir"])
        cikti.append(s)
    return cikti


def firma_rol(a: str, b: str) -> str:
    """Okunmayan yıl yararlanmayan yapılmaz. Tek yıldaki yok, firmayı yararlanmayan yapmaz."""
    def kova(s):
        if s in ("yararlanan_belge", "yararlanan_gelir_satiri"):
            return "yararlanan"
        if s in ("yararlanmayan", "sifir_satir"):
            return "yararlanmayan"
        if s in (None, "metin_yok"):
            return "okunmadi"
        return "bilinmeyen"
    labs = [kova(a), kova(b)]
    if "yararlanan" in labs:
        return "yararlanan"
    if labs == ["yararlanmayan", "yararlanmayan"]:
        return "yararlanmayan"
    if "yararlanmayan" in labs:
        return "karisik_bir_yil_acik_yok"
    return "bilinmeyen"


def yuz_marjlari():
    liste = [r for r in csv.DictReader((ROOT / "marj_sirket_liste.csv").open(encoding="utf-8")) if r["ana"] == "Tekstil ve giyim"]
    ham = defaultdict(dict)
    for r in csv.DictReader((ROOT / "marj_ham.csv").open(encoding="utf-8")):
        ham[r["kod"]][int(r["yil"])] = r
    firmalar = []
    for s in liste:
        kod = s["kod"]
        kayit = {
            "kod": kod,
            "ad": s["ad"],
            "alt": s["sektor"],
            "ana": s["ana"],
            "sinif_kaynagi": "İş Yatırım alt sektörü, marj_sirket_liste.csv, 16 Ekim 2026",
            "kap_sektor_kodu": "bu turda alınamadı",
            "holding_adi": kod in HOLDING_AD,
            "cok_sektor_ad": COK_SEKTOR_AD.get(kod),
            "yillar": {},
        }
        for y in range(2016, 2024):
            r = ham[kod].get(y)
            if not r or not fnum(r.get("satis")) or fnum(r["satis"]) <= 0:
                kayit["yillar"][str(y)] = None
                continue
            fin_g = fnum(r.get("fin_gelir"))
            fin_d = fnum(r.get("fin_gider"))
            vo = fnum(r.get("vergi_oncesi"))
            kayit["yillar"][str(y)] = {
                "cekirdek": marj_oran(r, cekirdek_tutar(r)),
                "faaliyet": marj_oran(r, fnum(r.get("faaliyet"))),
                "vo": marj_oran(r, vo),
                "fin": None if fin_g is None or fin_d is None else (fin_g + fin_d) / fnum(r["satis"]),
                "ihracat_pay": None if not fnum(r.get("yurtdisi")) else fnum(r["yurtdisi"]) / fnum(r["satis"]),
            }
        firmalar.append(kayit)
    return firmalar


def _cift(firmalar, y0, y1, alan, alt=None, holding_haric=False):
    xs0, xs1, dx = [], [], []
    for f in firmalar:
        if alt and f["alt"] != alt:
            continue
        if holding_haric and f["holding_adi"]:
            continue
        a = (f["yillar"].get(str(y0)) or {}).get(alan) if f["yillar"].get(str(y0)) else None
        b = (f["yillar"].get(str(y1)) or {}).get(alan) if f["yillar"].get(str(y1)) else None
        if a is None or b is None:
            continue
        xs0.append(a * 100)
        xs1.append(b * 100)
        dx.append((b - a) * 100)
    return {"duzey_bas": ozet(xs0), "duzey_son": ozet(xs1), "degisim_pp": ozet(dx)}


def dipnotlar(firmalar):
    """2016 ve 2022 orijinal bildirim. Kapanmayan kırılım medyana girmez."""
    out = []
    for f in firmalar:
        rec = {"kod": f["kod"], "alt": f["alt"], "yillar": {}}
        jyol = json_yolu(f["kod"])
        j = json.loads(jyol.read_text(encoding="utf-8")) if jyol else {"yillar": {}}
        for yil in (2016, 2022):
            yol = metin_yolu(f["kod"], yil)
            yj = (j.get("yillar") or {}).get(str(yil)) or {}
            if yol is None:
                rec["yillar"][str(yil)] = {
                    "metin": False,
                    "neden": yj.get("hata") or "metin_yok",
                    "tesvik": "bilinmeyen",
                    "kirilim": "belirlenemiyor",
                }
                continue
            metin = yol.read_text(encoding="utf-8", errors="replace")
            tes = sinif_metin(metin)
            satir = satir_tesvik(metin) if tes["sinif"] in ("yararlanan_belge", "yararlanan_gelir_satiri") else []
            kir = {"gelir": None, "gider": None, "neden": []}
            rev = yj.get("rev")
            for taraf, anahtar in (("gelir", "fin_gelir"), ("gider", "fin_gider")):
                hedef = yj.get(anahtar)
                if hedef is None:
                    kir["neden"].append(f"{taraf}:yuz_tutari_yok")
                    continue
                blok = blok_ayir(metin, hedef, taraf)
                eko = _eko(blok)
                kir[taraf] = {
                    "durum": blok.get("durum"),
                    "fark": blok.get("fark"),
                    "kur": None if eko is None else eko["kur"],
                    "faiz": None if eko is None else eko["faiz"],
                    "diger": None if eko is None else eko["diger"],
                }
                if blok.get("durum") != "kapandi":
                    kir["neden"].append(f"{taraf}:{blok.get('durum')}")
            net = None
            if rev and kir["gelir"] and kir["gider"] and kir["gelir"]["durum"] == "kapandi" and kir["gider"]["durum"] == "kapandi":
                net = {}
                for k in ("kur", "faiz", "diger"):
                    net[k] = (kir["gelir"][k] - kir["gider"][k]) / rev
                net["fin"] = sum(net.values())
            rec["yillar"][str(yil)] = {
                "metin": True,
                "uzunluk": len(metin),
                "tesvik_yil": tes["sinif"],
                "kanit": tes["kanit"][:2],
                "satir": [{"satir": s["satir"], "pencere": s["pencere"][:180]} for s in satir],
                "kirilim": kir,
                "net_marj": net,
                "rev": rev,
                "vo": yj.get("vo"),
                "tms29": False,
            }
        a = rec["yillar"]["2016"].get("tesvik_yil") or "metin_yok"
        b = rec["yillar"]["2022"].get("tesvik_yil") or "metin_yok"
        rec["tesvik"] = firma_rol(a, b)
        out.append(rec)
    return out


def bec_sinif(kodlar):
    if len(kodlar) != 1:
        return "coklu_veya_yok"
    k = kodlar[0]
    if k in ("21", "22"):
        return "ara_mal"
    if k in ("61", "62", "63"):
        return "tuketim"
    if k == "42":
        return "sermaye_parca"
    return "diger_" + k


def ticaret():
    fasil = json.loads((TRADE / "fasil.json").read_text(encoding="utf-8")) if (TRADE / "fasil.json").exists() else []
    hs6 = json.loads((TRADE / "hs6.json").read_text(encoding="utf-8")) if (TRADE / "hs6.json").exists() else []
    harita = json.loads((TRADE / "bec_harita.json").read_text(encoding="utf-8")) if (TRADE / "bec_harita.json").exists() else {}
    return {"fasil": fasil, "hs6": hs6, "harita": {k: bec_sinif(v) for k, v in harita.items()}, "ham_harita": harita}


def grupla_ticaret(tic):
    """Fasıl toplamı ve, altılı değer varsa, BEC değer payı. Kod sayısı payı değer değildir."""
    yillar = list(range(2016, 2024))
    fasil = defaultdict(lambda: {"M": 0.0, "X": 0.0, "qty": []})
    for row in tic["fasil"]:
        fasil[(row["yil"], row["kod"])][row["akis"]] = row["primary"] or 0
        fasil[(row["yil"], row["kod"])]["qty"].append(row.get("qty"))
    grup = {
        "tekstil_fasil_50_60": [str(i) for i in range(50, 61)],
        "giyim_fasil_61_62": ["61", "62"],
        "mensucat_fasil_63": ["63"],
    }
    ozet_f = {}
    for ad, kodlar in grup.items():
        seri = []
        for y in yillar:
            m = sum(fasil[(y, k)]["M"] for k in kodlar)
            x = sum(fasil[(y, k)]["X"] for k in kodlar)
            seri.append({"yil": y, "ithalat_usd": m, "ihracat_usd": x, "ithalat_ihracat": None if x == 0 else m / x})
        if seri and seri[0]["ithalat_usd"]:
            artis = seri[-1]["ithalat_usd"] / seri[0]["ithalat_usd"] - 1
        else:
            artis = None
        ozet_f[ad] = {"seri": seri, "ithalat_artis_2016_2023": artis}
    def grup_ad(hs):
        if hs[:2] in {str(i) for i in range(50, 61)}:
            return "50_60"
        if hs[:2] in ("61", "62"):
            return "61_62"
        if hs[:2] == "63":
            return "63"
        return "diger"

    kov = defaultdict(float)
    qty_sifir = 0
    qty_var = 0
    coklu_kod = set()
    for row in tic["hs6"]:
        sin = tic["harita"].get(row["kod"], "haritada_yok")
        if sin == "coklu_veya_yok":
            coklu_kod.add(row["kod"])
        kov[(row["yil"], row["akis"], grup_ad(row["kod"]), sin)] += row["primary"] or 0
        if (row.get("qty") or 0) == 0:
            qty_sifir += 1
        else:
            qty_var += 1
    bec_yil = []
    for y in yillar:
        rec = {"yil": y, "grup": {}}
        for g in ("50_60", "61_62", "63"):
            rec["grup"][g] = {}
            for akis, ad in (("M", "ithalat"), ("X", "ihracat")):
                parca = {}
                for (yy, a, gg, sin), val in kov.items():
                    if yy == y and a == akis and gg == g:
                        parca[sin] = val
                toplam = sum(parca.values())
                rec["grup"][g][ad] = {
                    "usd": parca,
                    "pay": {k: (v / toplam if toplam else None) for k, v in parca.items()},
                    "toplam": toplam,
                }
        bec_yil.append(rec)
    # Fasıl toplamı ile altılı toplam aynı evren değilse fark yazılır; kalan kalem yapılmaz.
    hs6_fasil = defaultdict(float)
    for row in tic["hs6"]:
        hs6_fasil[(row["yil"], row["kod"][:2], row["akis"])] += row["primary"] or 0
    farklar = []
    for y in yillar:
        for k in [str(i) for i in range(50, 64)]:
            for akis in ("M", "X"):
                hedef = fasil[(y, k)][akis]
                alt = hs6_fasil.get((y, k, akis), 0.0)
                if hedef:
                    farklar.append({"yil": y, "fasil": k, "akis": akis, "fasil_usd": hedef, "hs6_usd": alt, "oran": alt / hedef - 1})
    return {
        "fasil_grup": ozet_f,
        "bec_deger": bec_yil,
        "hs6_fasil_fark": farklar,
        "coklu_bec_kod": sorted(coklu_kod),
        "qty_sifir": qty_sifir,
        "qty_var": qty_var,
        "n_hs6": len(tic["hs6"]),
        "uretim": "yok",
        "yogunluk": "hesaplanmadi",
        "kaynak": "UN Comtrade önizleme, raporlayan 792, partner 0, HS, primaryValue ABD doları. TÜİK tablosu indirilmedi.",
    }


def main():
    firmalar = yuz_marjlari()
    alts = sorted({f["alt"] for f in firmalar})
    kapsam = []
    for alt in alts:
        alt_f = [f for f in firmalar if f["alt"] == alt]
        kapsam.append({
            "alt": alt,
            "n": len(alt_f),
            "holding_adi": sum(1 for f in alt_f if f["holding_adi"]),
            "cok_sektor_ad": sum(1 for f in alt_f if f["cok_sektor_ad"]),
            "satis_2016_ve_2023": sum(1 for f in alt_f if f["yillar"].get("2016") and f["yillar"].get("2023")),
        })
    yuz = {}
    for alt in alts:
        ad = alt
        yuz[ad] = {}
        for y0, y1, et in ((2016, 2022, "2016_2022_ham"), (2016, 2023, "2016_2023_ham_tms29")):
            yuz[ad][et] = {
                alan: _cift(firmalar, y0, y1, alan, alt, holding_haric=True)
                for alan in ("cekirdek", "faaliyet", "vo", "fin")
            }
    dip = dipnotlar(firmalar)
    okunan = []
    for d in dip:
        n_ok = sum(1 for y in ("2016", "2022") if d["yillar"][y].get("metin"))
        kapali = []
        for y in ("2016", "2022"):
            k = d["yillar"][y].get("kirilim")
            if isinstance(k, dict) and k.get("gelir") and k.get("gider"):
                if k["gelir"]["durum"] == "kapandi" and k["gider"]["durum"] == "kapandi":
                    kapali.append(y)
        okunan.append({
            "kod": d["kod"], "alt": d["alt"], "metin_yil": n_ok,
            "iki_yil_kapali": kapali == ["2016", "2022"],
            "tesvik": d["tesvik"],
            "neden": {y: d["yillar"][y].get("kirilim", {}).get("neden") if isinstance(d["yillar"][y].get("kirilim"), dict) else d["yillar"][y].get("neden") for y in ("2016", "2022")},
        })
    tic = None
    ticaret_ozet = None
    if (TRADE / "fasil.json").exists():
        tic = ticaret()
        ticaret_ozet = grupla_ticaret(tic)
    # H1 için iki yılda kapanan net kalemler, alt sektör içinde
    h1 = []
    for d in dip:
        if not all(d["yillar"][y].get("net_marj") for y in ("2016", "2022")):
            continue
        a, b = d["yillar"]["2016"]["net_marj"], d["yillar"]["2022"]["net_marj"]
        h1.append({
            "kod": d["kod"],
            "alt": d["alt"],
            **{f"d_{k}": (b[k] - a[k]) * 100 for k in ("kur", "faiz", "diger", "fin")},
        })
    sonuc = {
        "kapsam": kapsam,
        "n_firma": len(firmalar),
        "firmalar": [{k: f[k] for k in ("kod", "ad", "alt", "holding_adi", "cok_sektor_ad", "sinif_kaynagi", "kap_sektor_kodu")} | {"marj": f["yillar"]} for f in firmalar],
        "yuz": yuz,
        "dipnot_ozet": okunan,
        "dipnot": dip,
        "h1_kapali": h1,
        "ticaret": ticaret_ozet,
    }
    (ROOT / "tekstil_giyim.json").write_text(json.dumps(sonuc, ensure_ascii=False), encoding="utf-8")
    print("firma", len(firmalar), "dipnot json", sum(1 for d in dip if any(d["yillar"][y].get("metin") for y in ("2016", "2022"))))
    print("iki yil kapali", sum(1 for x in okunan if x["iki_yil_kapali"]))
    print("ticaret", "var" if ticaret_ozet else "yok")


if __name__ == "__main__":
    main()
