"""Fisher ayrışması: adım 3 (duran faiz) ve adım 4 (endeks bacağı) için iki denklem.

(1) Fisher ilişkisi: (1+i) = (1+r)(1+π). Nominal faizin reel faiz ve enflasyon telafisine ayrışması.
    Nominal birimde: i = π + r(1+π). Yani "i − π" reel faiz değil, reel faizin nominal ifadesidir.
(2) Uluslararası Fisher: (1+i_TL)/(1+i_YP) = beklenen USD/TRY artışı. Faiz farkının ima ettiği değer kaybı.

Girdiler (yalnız repo, ağ yok): faiz_ham.csv, faiz_kur_ham.csv, bes_yil_senaryo.csv, rev_adim3.csv, rev_adim3_sonuc.json,
adim4_adres_yonlendirme.csv, acik_veri_ozet.json. Mevcut hiçbir dosyaya yazılmaz.
Çıktı: fisher_ayrisma.csv, fisher_ayrisma_adim3.csv, fisher_ayrisma_adim4.csv, fisher_ayrisma_sonuc.json, FISHER_AYRISMA.md
Çalıştırma: python3 fisher_ayrisma.py

Etiketler: reel faiz ve ima edilen değer kaybı `olcum_turevi` (eşleşen aydaki ölçülmüş iki sayıdan);
enflasyon yolu 2029-2030 arası `varsayim` (anket yıllarının doğrusal ara değeri); endeks = TÜFE `varsayim`.
"""

from __future__ import annotations

import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

KOK = Path(__file__).resolve().parent
BASLA = "2010-01"
YILLAR = range(2027, 2032)


# ---------- iki denklem ----------

def reel_tam(i: float, pi: float) -> float:
    """Tam Fisher: (1+i)/(1+π) − 1, yüzde puan."""
    return ((1 + i / 100) / (1 + pi / 100) - 1) * 100


def ayristir(i: float, pi: float) -> dict:
    """i = π + r(1+π). reel_yaklasik = i − π = r + r·π (çapraz terim dahil)."""
    r = reel_tam(i, pi)
    return {"nominal": i, "enflasyon": pi, "reel_tam": r, "reel_nominal_birim": i - pi,
            "capraz": r * pi / 100, "reel_yaklasik": i - pi}


def ima_edilen_deger_kaybi(i_tl: float, i_yp: float) -> float:
    """Uluslararası Fisher: faiz farkının ima ettiği yıllık USD/TRY artışı, yüzde."""
    return ((1 + i_tl / 100) / (1 + i_yp / 100) - 1) * 100


def yp_kredi_tl_maliyeti(i_yp: float, kayip: float) -> float:
    """YP krediyi TL gelirli borçlu için TL cinsinden maliyet: (1+i_YP)(1+değer kaybı) − 1."""
    return ((1 + i_yp / 100) * (1 + kayip / 100) - 1) * 100


# ---------- girdiler ----------

def _sayi(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if v == v else None


def oku_csv(ad: str, kok: Path = KOK) -> list[dict]:
    with open(kok / ad, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def yukle(kok: Path = KOK):
    faiz: dict = {}
    for r in oku_csv("faiz_ham.csv", kok):
        v = _sayi(r["Deger"])
        if v is not None:
            faiz.setdefault(r["Seri"], {})[r["Donem"]] = v
    kur = {r["donem"]: {"aofm": _sayi(r["aofm"]), "usd": _sayi(r["usd"]), "tufe": _sayi(r["tufe"])}
           for r in oku_csv("faiz_kur_ham.csv", kok)}
    return faiz, kur, oku_csv("bes_yil_senaryo.csv", kok)


def ay_ekle(donem: str, n: int) -> str:
    k = int(donem[:4]) * 12 + int(donem[5:7]) - 1 + n
    return f"{k // 12:04d}-{k % 12 + 1:02d}"


def tufe_yillik(kur: dict) -> dict:
    """TÜFE endeksinden (faiz_kur_ham, TP.FG.J0) 12 aylık değişim, yüzde."""
    out = {}
    for d, v in kur.items():
        eski = kur.get(ay_ekle(d, -12), {}).get("tufe")
        if v["tufe"] and eski:
            out[d] = (v["tufe"] / eski - 1) * 100
    return out


def ara_degerle(nok: dict, bas: int, son: int) -> dict:
    yil = sorted(nok)
    out = {}
    for y in range(bas, son + 1):
        if y in nok:
            out[y] = nok[y]
            continue
        a, b = max(k for k in yil if k < y), min(k for k in yil if k > y)
        out[y] = nok[a] + (nok[b] - nok[a]) * (y - a) / (b - a)
    return out


def anket_yollari(bes: list[dict]):
    """Yıl sonu yıllık TÜFE beklentisi: 'anket' (beklenti) ve 'alt' (senaryo_alt); 2029-2030 doğrusal ara değer (varsayım)."""
    nok = {"anket": {}, "alt": {}}
    taban = None
    doviz = None
    for r in bes:
        if r["degisken"] == "enflasyon_tufe_yillik":
            y = int(r["yil"])
            if _sayi(r["beklenti"]) is not None:
                nok["anket"][y] = _sayi(r["beklenti"])
            if _sayi(r["senaryo_alt"]) is not None:
                nok["alt"][y] = _sayi(r["senaryo_alt"])
            taban = taban or {"donem": r["taban_tarih"], "deger": _sayi(r["taban"])}
        if r["degisken"] == "doviz_usd_try" and r["beklenti_ufuk"] == "12 ay sonrası" and _sayi(r["beklenti"]) is not None:
            doviz = {"spot": _sayi(r["taban"]), "spot_tarih": r["taban_tarih"], "beklenen_12ay": _sayi(r["beklenti"])}
    return {ad: ara_degerle(n, 2026, 2031) for ad, n in nok.items()}, taban, doviz


# ---------- eşleşen aylık seri ----------

def seri_olustur(faiz, kur, pi_aylik, pi_taban) -> list[dict]:
    tl, yp, stok, stok_yp = faiz["TP.KTF17"], faiz["TP.KTF17.USD"], faiz["TP.BKR.TRY.1"], faiz["TP.BKR.USD.1"]
    satirlar = []
    for d in sorted(k for k in kur if k >= BASLA):
        usd = kur[d]["usd"]
        pi, kaynak = pi_aylik.get(d), "tufe_endeksi"
        if pi is None and d == pi_taban["donem"]:
            pi, kaynak = pi_taban["deger"], "bes_yil_senaryo taban"
        if pi is None:
            kaynak = ""
        ileri_d, geri_d = ay_ekle(d, 12), ay_ekle(d, -12)
        ileri = (kur[ileri_d]["usd"] / usd - 1) * 100 if kur.get(ileri_d, {}).get("usd") and usd else None
        geri = (usd / kur[geri_d]["usd"] - 1) * 100 if kur.get(geri_d, {}).get("usd") and usd else None
        i, iy, si = tl.get(d), yp.get(d), stok.get(d)
        a = ayristir(i, pi) if i is not None and pi is not None else None
        ima = ima_edilen_deger_kaybi(i, iy) if i is not None and iy is not None else None
        satirlar.append({
            "donem": d, "kredi_faizi_TL": i, "kredi_faizi_USD": iy, "stok_faizi_TL": si, "stok_faizi_USD": stok_yp.get(d),
            "aofm": kur[d]["aofm"],
            "tufe_yillik": pi, "tufe_kaynak": kaynak,
            "reel_tam_kredi": a["reel_tam"] if a else None, "reel_yaklasik_kredi": a["reel_yaklasik"] if a else None,
            "capraz_kredi": a["capraz"] if a else None, "enflasyon_payi_kredi": pi / i if a else None,
            "reel_tam_stok": reel_tam(si, pi) if si is not None and pi is not None else None,
            "reel_tam_aofm": reel_tam(kur[d]["aofm"], pi) if kur[d]["aofm"] is not None and pi is not None else None,
            "usd_try": usd, "ima_edilen_deger_kaybi": ima,
            "gerceklesen_12ay_ileri": ileri, "gerceklesen_12ay_geri": geri,
            "yp_kredi_tl_maliyeti_ileri": yp_kredi_tl_maliyeti(iy, ileri) if iy is not None and ileri is not None else None,
        })
    return satirlar


def sira(x: list[float]) -> list[float]:
    """Ortalama sıra (eşitlikte ortalama); sıra korelasyonu için."""
    s = sorted(range(len(x)), key=lambda i: x[i])
    r = [0.0] * len(x)
    i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and x[s[j + 1]] == x[s[i]]:
            j += 1
        for k in range(i, j + 1):
            r[s[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def _ozet(x: list[float]) -> dict:
    q = statistics.quantiles(x, n=10)
    return {"n": len(x), "ortalama": round(statistics.mean(x), 2), "medyan": round(statistics.median(x), 2),
            "min": round(min(x), 2), "p10": round(q[0], 2), "p90": round(q[8], 2), "max": round(max(x), 2),
            "negatif_oran": round(sum(1 for v in x if v < 0) / len(x), 3)}


def tarihsel(satirlar: list[dict]) -> dict:
    def sec(alan):
        return [(s["donem"], s[alan]) for s in satirlar if s[alan] is not None]
    kredi, stok, aofm = sec("reel_tam_kredi"), sec("reel_tam_stok"), sec("reel_tam_aofm")
    ife = [s for s in satirlar if s["gerceklesen_12ay_ileri"] is not None and s["ima_edilen_deger_kaybi"] is not None]
    ima, ger = [s["ima_edilen_deger_kaybi"] for s in ife], [s["gerceklesen_12ay_ileri"] for s in ife]
    pahali = [s for s in ife if s["yp_kredi_tl_maliyeti_ileri"] > s["kredi_faizi_TL"]]
    son60 = ife[-60:]
    return {
        "reel_kredi_faizi": _ozet([v for _, v in kredi]) | {"ilk": kredi[0][0], "son": kredi[-1][0], "min_donem": min(kredi, key=lambda t: t[1])[0], "max_donem": max(kredi, key=lambda t: t[1])[0]},
        "reel_stok_faizi": _ozet([v for _, v in stok]) | {"ilk": stok[0][0], "son": stok[-1][0]},
        "reel_aofm": _ozet([v for _, v in aofm]) | {"ilk": aofm[0][0], "son": aofm[-1][0]},
        "uluslararasi_fisher": {
            "n": len(ife), "ilk": ife[0]["donem"], "son": ife[-1]["donem"],
            "ima_ortalama": round(statistics.mean(ima), 2), "gerceklesen_ortalama": round(statistics.mean(ger), 2),
            "sapma_ortalama": round(statistics.mean(g - m for g, m in zip(ger, ima)), 2),
            "pearson_korelasyonu": round(statistics.correlation(ima, ger), 4),
            "sira_korelasyonu": round(statistics.correlation(sira(ima), sira(ger)), 3),
            "gerceklesen_asan_ay_orani": round(sum(1 for m, g in zip(ima, ger) if g > m) / len(ife), 3),
            "yp_kredi_pahali_ay_orani": round(len(pahali) / len(ife), 3),
            "son60_ima_ortalama": round(statistics.mean(s["ima_edilen_deger_kaybi"] for s in son60), 2),
            "son60_gerceklesen_ortalama": round(statistics.mean(s["gerceklesen_12ay_ileri"] for s in son60), 2),
            "son60_yp_kredi_pahali_ay_orani": round(sum(1 for s in son60 if s["yp_kredi_tl_maliyeti_ileri"] > s["kredi_faizi_TL"]) / len(son60), 3),
        },
    }


def guncel(satirlar, doviz) -> dict:
    s = satirlar[-1]
    por_donem = {x["donem"]: x for x in satirlar}
    ss = next(x for x in reversed(satirlar) if x["stok_faizi_TL"] is not None and x["stok_faizi_USD"] is not None)
    anket = (doviz["beklenen_12ay"] / doviz["spot"] - 1) * 100 if doviz else None
    return {
        "donem": s["donem"], "tufe_yillik": s["tufe_yillik"], "tufe_kaynak": s["tufe_kaynak"],
        "kredi": ayristir(s["kredi_faizi_TL"], s["tufe_yillik"]),
        "aofm": ayristir(s["aofm"], s["tufe_yillik"]),
        "uluslararasi_fisher": {
            "i_tl": s["kredi_faizi_TL"], "i_usd": s["kredi_faizi_USD"], "ima_edilen_12ay": s["ima_edilen_deger_kaybi"],
            "anket_beklenen_12ay": anket, "gerceklesen_12ay_geri": s["gerceklesen_12ay_geri"],
            "yp_kredi_tl_maliyeti_anket": yp_kredi_tl_maliyeti(s["kredi_faizi_USD"], anket) if anket is not None else None,
            "yp_kredi_tl_maliyeti_gerceklesen_geri": yp_kredi_tl_maliyeti(s["kredi_faizi_USD"], s["gerceklesen_12ay_geri"]),
            "ayni_ay_bir_yil_once": {
                "donem": ay_ekle(s["donem"], -12), "ima_edilen": por_donem[ay_ekle(s["donem"], -12)]["ima_edilen_deger_kaybi"],
                "gerceklesen_ileri": por_donem[ay_ekle(s["donem"], -12)]["gerceklesen_12ay_ileri"]},
            "stok_faizi_donemi": ss["donem"],
            "stok_faizi_ima_edilen_12ay": ima_edilen_deger_kaybi(ss["stok_faizi_TL"], ss["stok_faizi_USD"]),
        },
    }


# ---------- adım 3 ----------

def adim3(pi_yol: dict, tarihsel_stok: dict, pi_bugun: float, kok: Path = KOK) -> dict:
    s3 = json.loads((kok / "rev_adim3_sonuc.json").read_text(encoding="utf-8"))
    s_yp, rt_son, ru = s3["yp_payi"]["2026-Q1"], s3["r_son"]["TL_stok"], s3["r_son"]["USD_stok"]

    def r_tl(ad, d):
        t = (int(d[:4]) - 2026) * 4 + int(d[-1]) - 3  # 2026-Q3 = 0 (rev_adim3.py ile aynı)
        return {"sabit": rt_son, "dusus": max(30.0, rt_son - (rt_son - 30.0) * t / 9), "yuksek": 55.0}[ad]

    ac = defaultdict(lambda: defaultdict(float))
    oran_ort = defaultdict(list)
    en_buyuk_fark, en_buyuk_goreli = 0.0, 0.0
    for x in oku_csv("rev_adim3.csv", kok):
        g, r, k, d = x["g"], x["r"], x["kappa"], x["donem"]
        D, I = float(x["D_milyar"]), float(x["I_sozlesme_milyar"])
        y, rt = int(d[:4]), r_tl(r, d)
        i_tl, i_yp = D * (1 - s_yp) * rt / 400, D * s_yp * ru / 400
        en_buyuk_fark = max(en_buyuk_fark, abs(i_tl + i_yp - I))
        if I > 0:
            en_buyuk_goreli = max(en_buyuk_goreli, abs(i_tl + i_yp - I) / I)
        a = ac[(g, r, k, y)]
        a["toplam"] += I
        a["tl"] += i_tl
        a["yp"] += i_yp
        for yol in ("anket", "alt"):
            a[f"enflasyon_{yol}"] += D * (1 - s_yp) * pi_yol[yol][y] / 400
        oran_ort[(r, y)].append(rt)

    satirlar = []
    for (g, r, k, y), a in sorted(ac.items()):
        satirlar.append({"g": g, "r": r, "kappa": k, "yil": y, "I_toplam_milyar": round(a["toplam"], 1),
                         "I_TL_milyar": round(a["tl"], 1), "I_YP_milyar": round(a["yp"], 1),
                         "enflasyon_telafisi_anket_milyar": round(a["enflasyon_anket"], 1),
                         "reel_getiri_anket_milyar": round(a["tl"] - a["enflasyon_anket"], 1),
                         "enflasyon_payi_TL_anket": round(a["enflasyon_anket"] / a["tl"], 3) if a["tl"] else None,
                         "enflasyon_telafisi_alt_milyar": round(a["enflasyon_alt"], 1),
                         "enflasyon_payi_TL_alt": round(a["enflasyon_alt"] / a["tl"], 3) if a["tl"] else None})

    tutarlilik = []
    for (r, y), rs in sorted(oran_ort.items()):
        if y not in YILLAR:
            continue
        i = sum(rs) / len(rs)
        satir = {"r": r, "yil": y, "i_TL_stok_ort": round(i, 2)}
        for yol in ("anket", "alt"):
            satir[f"pi_{yol}"] = round(pi_yol[yol][y], 2)
            satir[f"reel_tam_{yol}"] = round(reel_tam(i, pi_yol[yol][y]), 2)
        satir["reel_tam_bugun"] = round(reel_tam(i, pi_bugun), 2)  # enflasyon bugünkü düzeyde kalırsa
        satir["tarihsel_max_asildi"] = satir["reel_tam_anket"] > tarihsel_stok["max"]
        satir["tarihsel_max_asildi_bugun"] = satir["reel_tam_bugun"] > tarihsel_stok["max"]
        satir["tarihsel_p90_asildi"] = satir["reel_tam_anket"] > tarihsel_stok["p90"]
        tutarlilik.append(satir)

    g_tut = []
    for ad, gq in s3["g_ceyreklik"].items():
        ga = ((1 + gq) ** 4 - 1) * 100
        g_tut.append({"g": ad, "yillik_nominal": round(ga, 1),
                      **{f"gerekli_reel_buyume_{y}": round(((1 + ga / 100) / (1 + pi_yol["anket"][y] / 100) - 1) * 100, 1) for y in YILLAR}})
    return {"yp_payi": s_yp, "r_TL_stok_son": rt_son, "r_USD_stok_son": ru,
            "yeniden_kurma_en_buyuk_fark_milyar": round(en_buyuk_fark, 3),
            "yeniden_kurma_en_buyuk_goreli_fark": round(en_buyuk_goreli, 6),
            "satirlar": satirlar, "fisher_tutarliligi": tutarlilik, "g_tutarliligi": g_tut}


# ---------- adım 4 ----------

def adim4(pi_yol: dict, kok: Path = KOK) -> list[dict]:
    """Endeks bacağı: stok_(t−1) × π_yıl / 4, prim_ceyrek ile aynı kural (başlangıç stoku, yıllık/4). Endeks = TÜFE (varsayım)."""
    grup = defaultdict(list)
    for x in oku_csv("adim4_adres_yonlendirme.csv", kok):
        grup[(x["theta"], x["chi"], x["pi"])].append(x)
    out = []
    for (th, chi, p), rows in sorted(grup.items()):
        yil = defaultdict(lambda: defaultdict(float))
        onceki = 0.0
        for x in rows:
            y, st = int(x["donem"][:4]), float(x["stok"])
            yil[y]["prim"] += float(x["prim_ceyrek"])
            yil[y]["prim_kuralla"] += onceki * float(x["pi"]) / 4
            for yol in ("anket", "alt"):
                yil[y][f"endeks_{yol}"] += onceki * pi_yol[yol][y] / 400
            onceki = st
        for y in (2030, 2031):
            a = yil[y]
            out.append({"theta": th, "chi": chi, "prim_orani": p, "yil": y, "prim_milyar": round(a["prim"], 1),
                        "endeks_anket_milyar": round(a["endeks_anket"], 1), "endeks_alt_milyar": round(a["endeks_alt"], 1),
                        "endeks_prim_oran_anket": round(a["endeks_anket"] / a["prim"], 2) if a["prim"] else None,
                        "endeks_prim_oran_alt": round(a["endeks_alt"] / a["prim"], 2) if a["prim"] else None,
                        "prim_kural_farki_milyar": round(abs(a["prim"] - a["prim_kuralla"]), 2)})
    return out


# ---------- çıktı ----------

def yaz_csv(yol: Path, satirlar: list[dict]) -> None:
    with open(yol, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(satirlar[0]))
        w.writeheader()
        for s in satirlar:
            w.writerow({k: ("" if v is None else (round(v, 4) if isinstance(v, float) else v)) for k, v in s.items()})


def f1(x, n=1):
    return f"{x:,.{n}f}"


def rapor(s: dict) -> str:
    g, h, a3, a4 = s["guncel"], s["tarihsel"], s["adim3"], s["adim4"]
    k, o, u = g["kredi"], g["aofm"], g["uluslararasi_fisher"]
    ay = u["ayni_ay_bir_yil_once"]
    tk, ts, ti = h["reel_kredi_faizi"], h["reel_stok_faizi"], h["uluslararasi_fisher"]
    pi = s["enflasyon_yollari"]
    satir = [
        "# Fisher ayrışması: adım 3 ve adım 4",
        "",
        "Çalıştır: `python3 fisher_ayrisma.py`. Çıktı: `fisher_ayrisma.csv`, `fisher_ayrisma_adim3.csv`, `fisher_ayrisma_adim4.csv`, `fisher_ayrisma_sonuc.json`.",
        "",
        "Mevcut hiçbir dosya değişmedi: `adim3*.csv`, `rev_adim3*`, `adim4*.csv` olduğu gibi durur. Burası bir ayrıştırma, yeni bir kural değil.",
        "",
        "## İki denklem",
        "",
        "- **Fisher ilişkisi:** `(1+i) = (1+r)(1+π)`. Nominal birimde `i = π + r(1+π)`: enflasyon telafisi artı reel getiri. `i − π` reel faiz değil, reel faizin nominal ifadesidir; fark çapraz terim `r·π`.",
        "- **Uluslararası Fisher:** `(1+i_TL)/(1+i_YP) = beklenen USD/TRY artışı`. Faiz farkının ima ettiği değer kaybı.",
        "",
        f"## Güncel durum ({g['donem']}, `olcum_turevi`)",
        "",
        f"TÜFE yıllık {g['tufe_yillik']:.2f}% (`{g['tufe_kaynak']}`). Eşleşen ay, aynı tarih.",
        "",
        "| Faiz | Nominal | Reel (tam) | i − π | Çapraz r·π | Enflasyon payı |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
        f"| Ticari kredi TL (TP.KTF17) | {k['nominal']:.2f} | {k['reel_tam']:.2f} | {k['reel_yaklasik']:.2f} | {k['capraz']:.2f} | %{100 * k['enflasyon'] / k['nominal']:.0f} |",
        f"| Politika (AOFM) | {o['nominal']:.2f} | {o['reel_tam']:.2f} | {o['reel_yaklasik']:.2f} | {o['capraz']:.2f} | %{100 * o['enflasyon'] / o['nominal']:.0f} |",
        "",
        f"Tarihsel eşleşen reel kredi faizi ({tk['ilk']} → {tk['son']}, n={tk['n']}): medyan {tk['medyan']}, p10 {tk['p10']}, p90 {tk['p90']}, min {tk['min']} ({tk['min_donem']}), max {tk['max']} ({tk['max_donem']}); ayların %{100 * tk['negatif_oran']:.0f}'inde negatif. Bugünkü {k['reel_tam']:.1f}% tarihsel p90 ({tk['p90']}) {'üstünde' if k['reel_tam'] > tk['p90'] else 'altında'}.",
        "",
        "## Uluslararası Fisher",
        "",
        "| Ölçü | Yıllık % |",
        "| --- | ---: |",
        f"| Faiz farkının ima ettiği değer kaybı ({g['donem']}, TL kredi / USD kredi: {u['i_tl']:.2f} / {u['i_usd']:.2f}) | {u['ima_edilen_12ay']:.1f} |",
        f"| Stok faizlerinden ima edilen (TP.BKR.TRY.1 / USD.1, {u['stok_faizi_donemi']}) | {u['stok_faizi_ima_edilen_12ay']:.1f} |",
        f"| Anket beklentisi (USD/TRY 12 ay sonrası, `varsayim`) | {u['anket_beklenen_12ay']:.1f} |",
        f"| Gerçekleşen, son 12 ay | {u['gerceklesen_12ay_geri']:.1f} |",
        f"| YP kredinin TL maliyeti, anket kuruyla | {u['yp_kredi_tl_maliyeti_anket']:.1f} |",
        f"| YP kredinin TL maliyeti, gerçekleşen kurla | {u['yp_kredi_tl_maliyeti_gerceklesen_geri']:.1f} |",
        f"| TL kredi faizi (karşılaştırma) | {u['i_tl']:.1f} |",
        "",
        f"Bir yıl önce ({ay['donem']}) ima edilen {ay['ima_edilen']:.1f}%, sonraki 12 ayda gerçekleşen {ay['gerceklesen_ileri']:.1f}%.",
        f"Tüm örneklem ({ti['ilk']} → {ti['son']}, n={ti['n']}): ima edilen ortalama {ti['ima_ortalama']}, gerçekleşen ortalama {ti['gerceklesen_ortalama']}; Pearson korelasyonu {ti['pearson_korelasyonu']}, sıra korelasyonu {ti['sira_korelasyonu']}; gerçekleşen değer kaybının ima edileni aştığı ay oranı %{100 * ti['gerceklesen_asan_ay_orani']:.0f}; YP kredi, gerçekleşen kurla TL krediden pahalı çıkan ay oranı %{100 * ti['yp_kredi_pahali_ay_orani']:.0f}. Son 60 ayda ima {ti['son60_ima_ortalama']}, gerçekleşen {ti['son60_gerceklesen_ortalama']}, YP pahalı oranı %{100 * ti['son60_yp_kredi_pahali_ay_orani']:.0f}.",
        "",
        f"**Okuma:** son 12 ay bir istisna: faiz farkı %{u['ima_edilen_12ay']:.0f} değer kaybı ima ederken gerçekleşen %{u['gerceklesen_12ay_geri']:.0f} kaldı, YP borç TL borçtan çok daha ucuz çıktı. Tüm örneklemde tersi: gerçekleşen değer kaybı ortalamada ima edileni aştı ve YP kredi ayların %{100 * ti['yp_kredi_pahali_ay_orani']:.0f}'inde TL krediden pahalıydı. Pearson korelasyonu sıfıra yakın çünkü 2021-2023'ün birkaç uç değeri (gerçekleşen %100'ü aşan) hesabı domine eder; sıra korelasyonu zayıf pozitif.",
        "",
        "## Adım 3: duran faizin ayrışması",
        "",
        f"`rev_adim3.csv` TL ve YP parçasına yeniden kuruldu (YP payı {a3['yp_payi']:.4f}, TL stok faizi {a3['r_TL_stok_son']}, USD {a3['r_USD_stok_son']}); toplam `I_sozlesme` ile en büyük mutlak fark {a3['yeniden_kurma_en_buyuk_fark_milyar']} milyar TL (en büyük stok satırı; YP payı `rev_adim3_sonuc.json`'da 4 haneye yuvarlı), en büyük göreli fark %{100 * a3['yeniden_kurma_en_buyuk_goreli_fark']:.4f} (küçük satırlarda `I`'nın 0,1'e yuvarlanması). TL parçasında enflasyon telafisi = D·(1−YP payı)·π/4, geri kalanı reel getiri.",
        "",
        f"Enflasyon yolu (yıl sonu yıllık TÜFE, `varsayim`): anket {', '.join(f'{y}: {v:.1f}' for y, v in pi['anket'].items())}; alt {', '.join(f'{y}: {v:.1f}' for y, v in pi['alt'].items())}. 2029-2030 anket yıllarının doğrusal ara değeri.",
        "",
        "κ = 1, g = medyan (milyar TL/yıl):",
        "",
        "| r | Yıl | Duran faiz | TL parçası | YP parçası | Enflasyon telafisi (anket) | Reel getiri (anket) | Enflasyon payı, anket / alt |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for x in a3["satirlar"]:
        if x["kappa"] == "1.0" and x["g"] == "medyan" and x["yil"] in (2029, 2031):
            satir.append(f"| {x['r']} | {x['yil']} | {f1(x['I_toplam_milyar'])} | {f1(x['I_TL_milyar'])} | {f1(x['I_YP_milyar'])} | {f1(x['enflasyon_telafisi_anket_milyar'])} | {f1(x['reel_getiri_anket_milyar'])} | %{100 * x['enflasyon_payi_TL_anket']:.0f} / %{100 * x['enflasyon_payi_TL_alt']:.0f} |")
    satir += ["", f"**Fisher tutarlılığı:** senaryo TL faizi ile anket enflasyonundan ima edilen reel faiz, tarihsel eşleşen reel stok faizi (p90 {ts['p90']}, max {ts['max']}, {ts['ilk']} → {ts['son']}) ile karşılaştırıldı:", "",
              f"| r | Yıl | TL faiz (stok, ort.) | Anket π | Reel (tam) | Alt π | Reel (tam) | π bugünkü düzeyde ({g['tufe_yillik']:.1f}) | Reel (tam) | Max aşıldı: anket / alt / bugün |",
              "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |"]
    for x in a3["fisher_tutarliligi"]:
        if x["yil"] in (2027, 2029, 2031):
            alt_asti = x["reel_tam_alt"] > ts["max"]
            ev = lambda b: "evet" if b else "hayır"  # noqa: E731
            satir.append(f"| {x['r']} | {x['yil']} | {x['i_TL_stok_ort']:.1f} | {x['pi_anket']:.1f} | {x['reel_tam_anket']:.1f} | {x['pi_alt']:.1f} | {x['reel_tam_alt']:.1f} | {g['tufe_yillik']:.1f} | {x['reel_tam_bugun']:.1f} | {ev(x['tarihsel_max_asildi'])} / {ev(alt_asti)} / {ev(x['tarihsel_max_asildi_bugun'])} |")
    tum = a3["fisher_tutarliligi"]
    y29 = {x["r"]: x for x in tum if x["yil"] == 2029}
    durum = ", ".join(f"`{r}` {x['reel_tam_bugun']:.1f} ({'aşıyor' if x['tarihsel_max_asildi_bugun'] else 'aralıkta'})" for r, x in sorted(y29.items()))
    kat = [x["reel_tam_anket"] / ts["max"] for x in tum if x["r"] in ("sabit", "yuksek")]
    satir += ["", f"{len(tum)} (r, yıl) kombinasyonunun {sum(1 for x in tum if x['tarihsel_max_asildi'])}'i anket enflasyonuyla, {sum(1 for x in tum if x['tarihsel_max_asildi_bugun'])}'i enflasyon bugünkü düzeyde kalırsa tarihsel maksimum reel faizi ({ts['max']}) aşıyor. Enflasyon bugünkü düzeyde kalırsa 2029 reel faizi (tam): {durum}. **Okuma:** nominal faiz yolu ile enflasyon yolu birlikte seçilmeli. Anket dezenflasyonuyla eşleşince `sabit` ve `yuksek` yolları tarihsel maksimumun {min(kat):.1f}-{max(kat):.1f} katı reel faiz ima eder; ayrı ayrı gezmek Fisher açısından tutarsız kombinasyonlar üretir.",
              "", "Stok büyümesi `g` için gerekli reel (kur değerlemesi dahil) büyüme, yıllık nominal `g` ile anket enflasyonundan:", "",
              "| g | Yıllık nominal % | " + " | ".join(str(y) for y in YILLAR) + " |", "| --- | ---: | " + " | ".join("---:" for _ in YILLAR) + " |"]
    for x in a3["g_tutarliligi"]:
        satir.append(f"| {x['g']} | {x['yillik_nominal']} | " + " | ".join(f"{x[f'gerekli_reel_buyume_{y}']}" for y in YILLAR) + " |")
    satir += ["", "## Adım 4: endeks bacağı", "",
              "`adim4_adres_yonlendirme.csv` `endeks_bacagi` sütunu \"hesaplanmadı\" diyordu. Burada Fisher ile doldurulur: nominal getiri = π + reel kupon; HEKİS senedinde reel kupon 0 (`BES_ADIM.md`), yani endeks bacağı = başlangıç stoku × π / 4 (prim ile aynı kural). **Endeks = TÜFE varsayımı;** hedef endeks TÜFE değilse geçersiz.", "",
              "| θ | χ | prim % | Yıl | Prim | Endeks (anket π) | Endeks / prim | Endeks (alt π) | Endeks / prim |", "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for x in a4:
        if x["chi"] == "0.0" and x["theta"] in ("0.1", "0.25", "0.5") and x["yil"] == 2030:
            satir.append(f"| {x['theta']} | {x['chi']} | {x['prim_orani']} | {x['yil']} | {f1(x['prim_milyar'])} | {f1(x['endeks_anket_milyar'])} | {x['endeks_prim_oran_anket']}× | {f1(x['endeks_alt_milyar'])} | {x['endeks_prim_oran_alt']}× |")
    satir += ["", "## Eleştirel notlar", "",
              "1. Enflasyon yolu anket beklentisidir (yıl sonu, yıllık); yıl içi dalgalanma ve 2029-2030 ara değeri varsayım. Fisher beklenen enflasyona dayanır; tarihsel tabloda gerçekleşen enflasyon kullanıldı (ex-post).",
              "2. Reel faiz `(1+i)/(1+π) − 1` ile hesaplandı; yaklaşık `i − π` yüksek enflasyonda reel faizi fazla gösterir (çapraz terim).",
              "3. Adım 3'te YP parçasının enflasyon telafisi ayrıştırılmadı (ABD enflasyonu repoda yok); yalnız TL parçası ayrışır.",
              "4. Uluslararası Fisher bir eşitlik değil; faiz farkı ile gerçekleşen değer kaybı arasındaki fark risk primi ve carry'dir. Pearson ve sıra korelasyonu ile pahalı-ay oranı bunu gösterir, nedenselliği değil; Pearson uç değerlere (2021-2023) çok duyarlıdır.",
              "5. Endeks bacağı TÜFE varsayımına ve başlangıç stoku kuralına bağlı; endeksleme anaparayı büyüttüğü için gerçek maliyet biraz daha yüksek olabilir (basit çeyreklik kural).",
              "6. Anket kuru (USD/TRY 12 ay sonrası) ile anket enflasyonu birbirinden bağımsız anketlerdir; tutarlılıkları sınanmadı.",
              "7. 'Tarihsel maksimum' bir sınır değil, örneklemin (2012-07 → 2026-01) en yüksek değeridir; aşmak imkânsız değil, örneklemde görülmemiş demektir. Örneklem kısa ve 2021-2023 negatif reel faiz dönemini içeriyor.",
              "", "## Ne denmez", "",
              "- 'Duran faizin yarısı enflasyon telafisi' denmez; pay π yoluna bağlı (anket ve alt yol ayrı gösterilir).",
              "- 'YP kredi hep ucuz' denmez; pahalı çıkan ay oranı yukarıda, kur şoklarında tersine döner.",
              "- 'Endeks bacağı K′ maliyetidir' denmez; hedef endeks TÜFE değilse bacak farklıdır ve repoda hedef patikası yok.",
              "- Bu sayılar `adim3.csv`, `adim4.csv`, `rev_adim3*` veya `uc_kural_senaryo.csv` içine taşınmaz.", ""]
    return "\n".join(satir)


def calistir(kok: Path = KOK) -> dict:
    faiz, kur, bes = yukle(kok)
    pi_yol, pi_taban, doviz = anket_yollari(bes)
    pi_aylik = tufe_yillik(kur)
    satirlar = seri_olustur(faiz, kur, pi_aylik, pi_taban)
    h = tarihsel(satirlar)
    a3 = adim3(pi_yol, h["reel_stok_faizi"], pi_taban["deger"], kok)
    a4 = adim4(pi_yol, kok)
    olculen = json.loads((kok / "acik_veri_ozet.json").read_text(encoding="utf-8"))["olcumler"]["tufe"]["deger"]
    sonuc = {
        "faz": "Fisher ayrışması",
        "enflasyon_yollari": {ad: {y: round(v, 2) for y, v in yol.items()} for ad, yol in pi_yol.items()},
        "kontrol": {"tufe_2026_01_endeksten": round(pi_aylik["2026-01"], 2), "tufe_2026_01_olculen": olculen},
        "guncel": guncel(satirlar, doviz), "tarihsel": h,
        "adim3": {k: v for k, v in a3.items() if k != "satirlar"} | {"kappa1_medyan_ozet": [x for x in a3["satirlar"] if x["kappa"] == "1.0" and x["g"] == "medyan" and x["yil"] in (2029, 2031)]},
        "adim4": a4,
        "etiketler": {"reel_faiz": "olcum_turevi (eşleşen ay)", "ima_edilen_deger_kaybi": "olcum_turevi",
                      "enflasyon_yolu_2029_2030": "varsayim (doğrusal ara değer)", "anket_kuru": "varsayim (anket)",
                      "endeks_bacagi": "varsayim (endeks = TÜFE)"},
    }
    yaz_csv(kok / "fisher_ayrisma.csv", satirlar)
    yaz_csv(kok / "fisher_ayrisma_adim3.csv", a3["satirlar"])
    yaz_csv(kok / "fisher_ayrisma_adim4.csv", a4)
    (kok / "fisher_ayrisma_sonuc.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=1), encoding="utf-8")
    (kok / "FISHER_AYRISMA.md").write_text(rapor({**sonuc, "adim3": a3}), encoding="utf-8")
    return sonuc


if __name__ == "__main__":
    s = calistir()
    g = s["guncel"]
    print(json.dumps({"guncel": g, "kontrol": s["kontrol"]}, ensure_ascii=False, indent=1))
