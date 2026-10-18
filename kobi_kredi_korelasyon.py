"""KOBİ nakdi kredi stoku: nominal ve reel artış, geç ödeme ile korelasyon, Granger.

Stok: BDDK Aylık Bülten, tablo 6, sektör, milyon TL, 2014-01 .. 2026-08.
Reel: stok / TÜFE. TP.FG.J0 2026-01'de kesilir; sonrası bir önceki yılın aynı ayı
çarpı TP.TUKFIY2025.GENEL_3 yıllık yüzde değişimidir (2026-01'de sapma binde 0,03).

Geç ödeme iki ayrı nesnedir ve birbirine eklenmez:
  fatura değeri payı  — Atradius, vadesi geçmiş B2B faturalarının değer payı
  şirket oranı        — gecikme bildiren katılımcı payı
Banka takibi üçüncü nesnedir: BDDK takip stoku / nakdi stok. Ticari alacak gecikmesi değildir.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np
from scipy import stats

KOK = Path(__file__).resolve().parent
HAM = KOK / "kobi_kredi_ham.csv"
JSON_YOL = KOK / "kobi_kredi_korelasyon.json"
MD_YOL = KOK / "KOBI_KREDI_KORELASYON.md"
YILLIK_YOL = KOK / "kobi_kredi_yillik.csv"

# Fatura değerindeki vadesi geçmiş pay. Anket yılı, saha dönemine yazılır.
# 2022 satırı metinde ayrıca basılmamıştır: 2023 raporunda zamanında %49, batık %6,
# kalan %45. Korelasyon bu satırla ve bu satır olmadan ayrı hesaplanır.
FATURA = (
    {"yil": 2017, "vadesi_gecmis_%": 55.9, "turetilen": False,
     "kaynak": "Atradius Payment Practices Barometer Eastern Europe, Eylül 2018: 2017 ortalaması %55,9'dan 2018'de %59,9'a",
     "url": "https://www.lemoci.com/wp-content/uploads/2018/09/Atradius-Payment-Practices-Barometer-Eastern-Europe-2018.pdf"},
    {"yil": 2018, "vadesi_gecmis_%": 59.9, "turetilen": False,
     "kaynak": "Aynı rapor. Yurt içi ve yurt dışı faturaların ortalaması. Katılımcıların %91,7'si sık geç ödeme bildirdi; bu şirket oranıdır, fatura payı değildir.",
     "url": "https://www.lemoci.com/wp-content/uploads/2018/09/Atradius-Payment-Practices-Barometer-Eastern-Europe-2018.pdf"},
    {"yil": 2022, "vadesi_gecmis_%": 45.0, "turetilen": True,
     "kaynak": "Atradius Türkiye 2023 grafiği: 2022 zamanında %49, batık %6. Vadesi geçmiş = 100 − 49 − 6.",
     "url": "https://atradiuscollections.com/dam/jcr:79cb1861-b022-4e54-af19-3ca14679315a/payment-practices-barometer-eastern-europe-2023-turkey-en.pdf"},
    {"yil": 2023, "vadesi_gecmis_%": 43.0, "turetilen": False,
     "kaynak": "Aynı raporun metni: vadesi geçmiş ortalama %43, zamanında %53, batık %4. Saha 2023 ilk çeyrek sonu–ikinci çeyrek ortası.",
     "url": "https://atradiuscollections.com/dam/jcr:79cb1861-b022-4e54-af19-3ca14679315a/payment-practices-barometer-eastern-europe-2023-turkey-en.pdf"},
    {"yil": 2025, "vadesi_gecmis_%": 61.0, "turetilen": False,
     "kaynak": "Atradius Türkiye 2025 metni: vadesi geçmiş %61, zamanında %28. Batık metinde yaklaşık %10, grafikte %11. Saha 2025 ilk çeyrek sonu–ikinci çeyrek ortası.",
     "url": "https://atradius.com.tr/dam/jcr:69398cfe-175d-433a-93fc-cd22140ed154/2025_06_10_p%20%C3%B6deme%20uygulamalar%C4%B1%20barometresi%20-%20Orta%20ve%20Do%C4%9Fu%20Avrupa%202025%20-%20T%C3%BCrkiye.pdf"},
)

SIRKET_ORANI = (
    {"yil": 2018, "oran_%": 91.7, "tanim": "sık geç ödeme bildiren katılımcı payı",
     "url": "https://www.lemoci.com/wp-content/uploads/2018/09/Atradius-Payment-Practices-Barometer-Eastern-Europe-2018.pdf"},
    {"yil": 2026, "oran_%": 86.0, "tanim": "müşteriden gecikme bildiren şirket payı; fatura değer payı 'üçte birin üzerinde' diye yazılmış, nokta tahmin yok",
     "url": "https://group.atradius.com/knowledge-and-research/reports/b2b-payment-practices-trends-in-turkey-2026"},
)


def _tr(x: float, nd: int = 1) -> str:
    neg = x < 0
    s = f"{abs(x):.{nd}f}"
    whole, _, frac = s.partition(".")
    parca = []
    while whole:
        parca.append(whole[-3:])
        whole = whole[:-3]
    govde = ".".join(reversed(parca))
    metin = govde if nd == 0 else f"{govde},{frac}"
    return ("-" if neg else "") + metin


def _oku() -> list[dict]:
    with HAM.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _f(satir: dict, ad: str) -> float:
    return float(satir[ad])


def _ay_ekle(donem: str, n: int) -> str:
    y, m = (int(p) for p in donem.split("-"))
    m += n
    while m > 12:
        y, m = y + 1, m - 12
    while m < 1:
        y, m = y - 1, m + 12
    return f"{y:04d}-{m:02d}"


def _ols(X: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    e = y - X @ b
    return b, e, float(e @ e)


def granger(y: np.ndarray, x: np.ndarray, gecikme: int) -> dict:
    """Klasik Granger F. y'nin kendi gecikmelerine x'in gecikmeleri eklenir. HAC yok."""
    y = np.asarray(y, float)
    x = np.asarray(x, float)
    n = len(y)
    T = n - gecikme
    Y = y[gecikme:]
    cols = [np.ones(T)]
    for i in range(1, gecikme + 1):
        cols.append(y[gecikme - i:n - i])
    Xr = np.column_stack(cols)
    for i in range(1, gecikme + 1):
        cols.append(x[gecikme - i:n - i])
    Xu = np.column_stack(cols)
    _, _, ssr_r = _ols(Xr, Y)
    bu, e, ssr_u = _ols(Xu, Y)
    q = gecikme
    k = Xu.shape[1]
    df = T - k
    F = ((ssr_r - ssr_u) / q) / (ssr_u / df)
    p = float(1 - stats.f.cdf(F, q, df))
    cx = bu[-gecikme:]
    dw = float(np.sum(np.diff(e) ** 2) / np.sum(e ** 2)) if np.sum(e ** 2) else math.nan
    return {
        "gecikme": gecikme, "T": int(T), "F": float(F), "p": p,
        "katsayi_toplami": float(cx.sum()), "durbin_watson": dw,
    }


def _korel(x: list[float], y: list[float]) -> dict:
    r, p = stats.pearsonr(x, y)
    rho, sp = stats.spearmanr(x, y)
    return {"n": len(x), "pearson": float(r), "pearson_p": float(p), "spearman": float(rho), "spearman_p": float(sp)}


def hesap() -> dict:
    ham = _oku()
    by = {r["Donem"]: r for r in ham}

    def nakdi(d: str) -> float:
        return _f(by[d], "Nakdi_milyon")

    def takip(d: str) -> float:
        return _f(by[d], "Takip_milyon")

    def tufe(d: str) -> float:
        return _f(by[d], "Tufe_2003")

    def reel(d: str) -> float:
        return nakdi(d) / tufe(d)

    def npl(d: str) -> float:
        return 100.0 * takip(d) / nakdi(d)

    yillar = []
    for y in range(2014, 2026):
        d, o = f"{y}-12", f"{y - 1}-12"
        satir = {
            "yil": y, "donem": d,
            "nakdi_milyar": nakdi(d) / 1000.0,
            "takip_milyar": takip(d) / 1000.0,
            "npl_%": npl(d),
            "mikro_pay_%": 100.0 * _f(by[d], "Mikro_nakdi_milyon") / nakdi(d),
            "kucuk_pay_%": 100.0 * _f(by[d], "Kucuk_nakdi_milyon") / nakdi(d),
            "orta_pay_%": 100.0 * _f(by[d], "Orta_nakdi_milyon") / nakdi(d),
            "musteri": int(float(by[d]["Musteri_net"])),
            "tufe": tufe(d),
        }
        if o in by:
            satir["nominal_artis_%"] = 100.0 * (nakdi(d) / nakdi(o) - 1.0)
            satir["reel_artis_%"] = 100.0 * (reel(d) / reel(o) - 1.0)
            satir["takip_artis_%"] = 100.0 * (takip(d) / takip(o) - 1.0)
            satir["npl_fark_puan"] = npl(d) - npl(o)
            satir["tufe_artis_%"] = 100.0 * (tufe(d) / tufe(o) - 1.0)
        yillar.append(satir)

    def kat(a: str, b: str) -> dict:
        ay = (int(b[:4]) - int(a[:4])) * 12 + (int(b[5:]) - int(a[5:]))
        nom = nakdi(b) / nakdi(a)
        re = reel(b) / reel(a)
        return {
            "bas": a, "son": b, "ay": ay,
            "nominal_kat": nom, "reel_kat": re,
            "nominal_bilesik_%": 100.0 * (nom ** (12.0 / ay) - 1.0),
            "reel_bilesik_%": 100.0 * (re ** (12.0 / ay) - 1.0),
            "npl_bas_%": npl(a), "npl_son_%": npl(b),
            "takip_bas_milyar": takip(a) / 1000.0, "takip_son_milyar": takip(b) / 1000.0,
        }

    pencereler = {
        "2016_2025": kat("2016-12", "2025-12"),
        "2016_2019": kat("2016-12", "2019-12"),
        "2019_2021": kat("2019-12", "2021-12"),
        "2021_2023": kat("2021-12", "2023-12"),
        "2023_2026_08": kat("2023-12", "2026-08"),
        "2025_2026_08": kat("2025-12", "2026-08"),
    }

    # Ağustos 2025 eşiği: o ayın artışı, 2025'in diğer aylarının ortalama artışıyla değiştirilir.
    mom = {}
    donemler = [r["Donem"] for r in ham]
    for i in range(1, len(donemler)):
        a, b = donemler[i - 1], donemler[i]
        mom[b] = nakdi(b) / nakdi(a) - 1.0
    diger = [mom[f"2025-{m:02d}"] for m in range(1, 13) if m != 8]
    ort = float(np.mean(diger))
    duzey = nakdi("2025-07") * (1.0 + ort)
    for m in range(9, 13):
        duzey *= 1.0 + mom[f"2025-{m:02d}"]
    reel_cf = 100.0 * ((duzey / tufe("2025-12")) / reel("2024-12") - 1.0)
    esik = {
        "karar": "7 Ağustos 2025, Cumhurbaşkanı Kararı 10182: KOBİ net satış veya bilanço üst sınırı 500 milyondan 1 milyara",
        "agustos_2025_nominal_artis_%": 100.0 * mom["2025-08"],
        "diger_2025_aylari_ortalama_artis_%": 100.0 * ort,
        "orta_pay_temmuz_%": 100.0 * _f(by["2025-07"], "Orta_nakdi_milyon") / nakdi("2025-07"),
        "orta_pay_agustos_%": 100.0 * _f(by["2025-08"], "Orta_nakdi_milyon") / nakdi("2025-08"),
        "musteri_temmuz": int(float(by["2025-07"]["Musteri_net"])),
        "musteri_agustos": int(float(by["2025-08"]["Musteri_net"])),
        "reel_2025_%": next(s["reel_artis_%"] for s in yillar if s["yil"] == 2025),
        "reel_2025_agustos_ortalamaya_cekilirse_%": reel_cf,
        "uyari": "Ağustos sıçramasının tamamı sınıflama değildir; aynı ayda kullandırım da vardır. Karşı olgu üst sınır diye okunmaz.",
    }

    def fatura_esle(ay: str) -> list[dict]:
        out = []
        for f in FATURA:
            d = f"{f['yil']}-{ay}"
            o = f"{f['yil'] - 1}-{ay}"
            out.append({
                **f,
                "stok_donem": d,
                "nakdi_milyar": nakdi(d) / 1000.0,
                "reel_yillik_%": 100.0 * (reel(d) / reel(o) - 1.0),
                "nominal_yillik_%": 100.0 * (nakdi(d) / nakdi(o) - 1.0),
                "npl_%": npl(d),
            })
        return out

    haziran = fatura_esle("06")
    aralik = fatura_esle("12")

    def blok(satirlar: list[dict]) -> dict:
        x = [s["vadesi_gecmis_%"] for s in satirlar]
        return {
            "reel_yillik": _korel(x, [s["reel_yillik_%"] for s in satirlar]),
            "nominal_yillik": _korel(x, [s["nominal_yillik_%"] for s in satirlar]),
            "nakdi_duzey": _korel(x, [s["nakdi_milyar"] for s in satirlar]),
            "npl": _korel(x, [s["npl_%"] for s in satirlar]),
        }

    tam = [s for s in haziran]
    sade = [s for s in haziran if not s["turetilen"]]
    fatura_test = {
        "esleme": "Anket yılı Haziran stoku ve Haziran/Haziran artış. 2018 raporu Eylül'de, 2023 ve 2025 saha işi ilk yarıda.",
        "haziran_hepsi": blok(tam),
        "haziran_turetilen_2022_haric": blok(sade),
        "aralik_hepsi": blok(aralik),
        "gozlem_haziran": [{k: s[k] for k in ("yil", "vadesi_gecmis_%", "turetilen", "reel_yillik_%", "nominal_yillik_%", "npl_%", "nakdi_milyar")} for s in haziran],
    }

    artis = [s for s in yillar if "reel_artis_%" in s]
    yillik_banka = {
        "reel_artis_ile_npl_farki": _korel([s["reel_artis_%"] for s in artis], [s["npl_fark_puan"] for s in artis]),
        "reel_artis_ile_takip_artisi": _korel([s["reel_artis_%"] for s in artis], [s["takip_artis_%"] for s in artis]),
        "nominal_artis_ile_tufe": _korel([s["nominal_artis_%"] for s in artis], [s["tufe_artis_%"] for s in artis]),
    }

    greel, gtak, gnom, npl_a = [], [], [], []
    for i in range(1, len(donemler)):
        a, b = donemler[i - 1], donemler[i]
        greel.append(math.log(reel(b) / reel(a)))
        gtak.append(math.log(takip(b) / takip(a)))
        gnom.append(math.log(nakdi(b) / nakdi(a)))
        npl_a.append(npl(b) / 100.0)
    greel_a = np.array(greel)
    gtak_a = np.array(gtak)
    npl_arr = np.array(npl_a)
    yonler = {
        "takip_stogu_reel_krediye": (greel_a, gtak_a),
        "reel_kredi_takip_stoguna": (gtak_a, greel_a),
        "npl_orani_reel_krediye": (greel_a, npl_arr),
        "reel_kredi_npl_oranina": (npl_arr, greel_a),
    }
    granger_sonuc = {
        ad: [granger(y, x, L) for L in (1, 3, 6, 12)]
        for ad, (y, x) in yonler.items()
    }
    aylik_korel = {
        "npl_reel_buyume": _korel(npl_a, greel),
        "npl_nominal_buyume": _korel(npl_a, gnom),
        "takip_buyume_reel_buyume": _korel(gtak, greel),
    }

    son = ham[-1]
    return {
        "tanim": {
            "stok": "BDDK Aylık Bülten tablo 6, Toplam KOBİ Kredileri, nakdi, milyon TL, sektör (taraf 10001)",
            "aralik": f"{ham[0]['Donem']} .. {son['Donem']}",
            "tufe": "EVDS TP.FG.J0 (2003=100). 2026-02 .. 2026-08: önceki yılın aynı ayı x (1 + TP.TUKFIY2025.GENEL_3 / 100)",
            "toplam_kredi": "EVDS TP.KREHACBS.A1 bin TL. BDDK temel göstergeler toplamından farklıdır; pay hesabında kullanılmadı.",
            "gec_odeme": "Fatura değeri payı ile şirket oranı ayrıdır. Banka takip oranı ticari alacak gecikmesi değildir.",
        },
        "son_gozlem": {
            "donem": son["Donem"],
            "nakdi_milyar": _f(son, "Nakdi_milyon") / 1000.0,
            "takip_milyar": _f(son, "Takip_milyon") / 1000.0,
            "npl_%": 100.0 * _f(son, "Takip_milyon") / _f(son, "Nakdi_milyon"),
            "mikro_npl_%": 100.0 * _f(son, "Mikro_takip_milyon") / _f(son, "Mikro_nakdi_milyon"),
            "kucuk_npl_%": 100.0 * _f(son, "Kucuk_takip_milyon") / _f(son, "Kucuk_nakdi_milyon"),
            "orta_npl_%": 100.0 * _f(son, "Orta_takip_milyon") / _f(son, "Orta_nakdi_milyon"),
        },
        "yillik": yillar,
        "pencere": pencereler,
        "esik_2025": esik,
        "fatura": fatura_test,
        "sirket_orani": SIRKET_ORANI,
        "yillik_banka": yillik_banka,
        "granger": granger_sonuc,
        "aylik_korelasyon": aylik_korel,
        "birincil": [
            "Fatura payı ile Haziran/Haziran reel artış: Pearson ve Spearman, n=5 ve n=4.",
            "Aylık dlog(takip) ile dlog(reel kredi): Granger gecikme 1 ve 3, iki yön.",
        ],
    }


def _satir_md(s: dict) -> str:
    art = ""
    if "nominal_artis_%" in s:
        art = f" | {_tr(s['nominal_artis_%'])} | {_tr(s['reel_artis_%'])} | {_tr(s['tufe_artis_%'])} | {_tr(s['takip_artis_%'])} | {_tr(s['npl_fark_puan'], 2)}"
    else:
        art = " |  |  |  |  | "
    return (
        f"| {s['yil']} | {_tr(s['nakdi_milyar'])} | {_tr(s['takip_milyar'])} | {_tr(s['npl_%'], 2)}"
        f"{art} |"
    )


def _p(p: float) -> str:
    if p < 0.001:
        return "p < 0,001"
    return f"p = {_tr(p, 3)}"


def _korel_md(k: dict) -> str:
    return (
        f"n = {k['n']}, Pearson {_tr(k['pearson'], 2)} ({_p(k['pearson_p'])}), "
        f"Spearman {_tr(k['spearman'], 2)} ({_p(k['spearman_p'])})"
    )


def _gr_md(g: dict) -> str:
    return (
        f"gecikme {g['gecikme']}: F = {_tr(g['F'], 2)}, p = {_tr(g['p'], 3)}, "
        f"katsayı toplamı {_tr(g['katsayi_toplami'], 3)}, T = {g['T']}, DW = {_tr(g['durbin_watson'], 2)}"
    )


def rapor(s: dict) -> str:
    p = s["pencere"]
    a, b = p["2016_2025"], p["2023_2026_08"]
    son = s["son_gozlem"]
    fh = s["fatura"]["haziran_hepsi"]["reel_yillik"]
    fs = s["fatura"]["haziran_turetilen_2022_haric"]["reel_yillik"]
    fa = s["fatura"]["aralik_hepsi"]["reel_yillik"]
    g1 = s["granger"]["takip_stogu_reel_krediye"]
    g2 = s["granger"]["reel_kredi_takip_stoguna"]
    yb = s["yillik_banka"]
    e = s["esik_2025"]
    satirlar = "\n".join(_satir_md(y) for y in s["yillik"] if y["yil"] >= 2015)
    goz = "\n".join(
        f"| {g['yil']} | {_tr(g['vadesi_gecmis_%'], 1)} | {'türetilen' if g['turetilen'] else 'metin'} | {_tr(g['reel_yillik_%'])} | {_tr(g['nominal_yillik_%'])} | {_tr(g['npl_%'], 2)} |"
        for g in s["fatura"]["gozlem_haziran"]
    )
    return f"""# KOBİ kredi artışı ve geç ödeme

BDDK Aylık Bülten tablo 6, nakdi KOBİ kredisi, sektör toplamı. Son gözlem {son['donem']}: stok {_tr(son['nakdi_milyar'])} milyar TL, takip {_tr(son['takip_milyar'])} milyar TL, takip oranı %{_tr(son['npl_%'], 2)} (mikro %{_tr(son['mikro_npl_%'], 2)}, küçük %{_tr(son['kucuk_npl_%'], 2)}, orta %{_tr(son['orta_npl_%'], 2)}). 2026 Eylül bültende yok. Ekim için %4,2 takip oranı bu tabloda yok.

Reel stok = nakdi / TÜFE (`TP.FG.J0`, 2003=100). 2026-02 .. 2026-08 endeksi, bir önceki yılın aynı ayı çarpı `TP.TUKFIY2025.GENEL_3` yıllık değişimdir. 2026-01'de bu kural EVDS endeksinden binde 0,03 sapar.

## Nominal ve reel

Aralık/Aralık. Artışlar bir önceki Aralık'a göredir. TÜFE aynı pencerede Aralık/Aralık'tır.

| Yıl | Nakdi (milyar TL) | Takip (milyar TL) | Takip oranı % | Nominal % | Reel % | TÜFE % | Takip stoku % | Takip oranı farkı (puan) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
{satirlar}

2016 Aralık – 2025 Aralık nominal kat {_tr(a['nominal_kat'], 2)}, yıllık bileşik %{_tr(a['nominal_bilesik_%'])}. Reel kat {_tr(a['reel_kat'], 2)}, yıllık bileşik %{_tr(a['reel_bilesik_%'])}. Dokuz yılda reel stok %{_tr(100 * (a['reel_kat'] - 1))} artar.

Alt pencereler, reel bileşik:

| Pencere | Nominal kat | Reel kat | Reel bileşik % | Takip oranı |
| --- | --- | --- | --- | --- |
| 2016-12 → 2019-12 | {_tr(p['2016_2019']['nominal_kat'], 2)} | {_tr(p['2016_2019']['reel_kat'], 2)} | {_tr(p['2016_2019']['reel_bilesik_%'])} | %{_tr(p['2016_2019']['npl_bas_%'], 2)} → %{_tr(p['2016_2019']['npl_son_%'], 2)} |
| 2019-12 → 2021-12 | {_tr(p['2019_2021']['nominal_kat'], 2)} | {_tr(p['2019_2021']['reel_kat'], 2)} | {_tr(p['2019_2021']['reel_bilesik_%'])} | %{_tr(p['2019_2021']['npl_bas_%'], 2)} → %{_tr(p['2019_2021']['npl_son_%'], 2)} |
| 2021-12 → 2023-12 | {_tr(p['2021_2023']['nominal_kat'], 2)} | {_tr(p['2021_2023']['reel_kat'], 2)} | {_tr(p['2021_2023']['reel_bilesik_%'])} | %{_tr(p['2021_2023']['npl_bas_%'], 2)} → %{_tr(p['2021_2023']['npl_son_%'], 2)} |
| 2023-12 → 2026-08 | {_tr(b['nominal_kat'], 2)} | {_tr(b['reel_kat'], 2)} | {_tr(b['reel_bilesik_%'])} | %{_tr(b['npl_bas_%'], 2)} → %{_tr(b['npl_son_%'], 2)} |

2023 Aralık – 2026 Ağustos nominal stok {_tr(b['nominal_kat'], 2)} katına çıkar. Reel stok {_tr(b['reel_kat'], 2)} kattır. Aynı aralıkta takip stoku {_tr(b['takip_bas_milyar'])} milyardan {_tr(b['takip_son_milyar'])} milyara çıkar. 2020-2023'te takip stoku 58 milyar TL dolayında dururken nakdi stok büyümüş, oran %6,89'dan %1,78'e inmiştir.

Yıllık nominal artış ile Aralık/Aralık TÜFE: {_korel_md(yb['nominal_artis_ile_tufe'])}.

## 2025 eşiği

{e['karar']}. Ağustos 2025 nominal artış %{_tr(e['agustos_2025_nominal_artis_%'])}; 2025'in diğer aylarının ortalaması %{_tr(e['diger_2025_aylari_ortalama_artis_%'])}. Orta ölçeğin payı Temmuz %{_tr(e['orta_pay_temmuz_%'])} iken Ağustos %{_tr(e['orta_pay_agustos_%'])}. Müşteri sayısı {_tr(e['musteri_temmuz'] / 1000, 0)} binden {_tr(e['musteri_agustos'] / 1000, 0)} bine çıkar. Ağustos artışı diğer ayların ortalamasına çekilirse 2025 reel artış %{_tr(e['reel_2025_%'])} yerine %{_tr(e['reel_2025_agustos_ortalamaya_cekilirse_%'])} kalır. {e['uyari']}

25 Mayıs 2023 yönetmeliği eşikleri daha önce de yükseltmişti. 2023 aylık stokunda Ağustos 2025'tekine benzer tek ay sıçraması ayrılmadı. 13 Kasım 2025 BDDK kararı sermaye yeterliliği ciro sınırını 1 milyar TL yapar; bültenin bu kararla yeniden sınıflanıp sınıflanmadığı burada ayrılmadı.

## Fatura değeri ile reel kredi

Korelasyon, fatura değerindeki vadesi geçmiş pay ile Haziran/Haziran reel artış arasındadır. 2018 fatura payı %59,9'dur. Aynı yıl katılımcıların %91,7'si sık geç ödeme bildirmiştir. 2026 şirket oranı %86'dır; 2026 özetinde fatura payı "üçte birin üzerinde" diye geçer, nokta tahmin yoktur. Korelasyon yalnız fatura payını kullanır.

2021 için "%58 zamanında ödeme" bu Atradius ülke fatura dağılımında yoktur. Dun & Bradstreet zamanında ödeme performansı ayrı tanımdır (2023: %40,6; 2021'e göre 7,8 puan düşük) ve hesaba girmedi.

| Anket yılı | Vadesi geçmiş fatura değeri % | Kaynak | Reel Haziran/Haziran % | Nominal % | Takip oranı % |
| --- | --- | --- | --- | --- | --- |
{goz}

Vadesi geçmiş pay ile reel yıllık artış, Haziran eşlemesi, beş nokta: {_korel_md(fh)}. 2022 türetilen noktası çıkarılınca dört nokta: {_korel_md(fs)}. n küçüktür; bu p değerleri bir etkiyi elemez.

Aralık eşlemesinde aynı beş nokta: {_korel_md(fa)}. İşaret, stokun Haziran veya Aralık alınmasıyla değişir. Her iki eşlemede de p 0,5'in üstündedir.

Bu seri yıllık, aralıklı ve beştir. Granger, VAR ve enflasyonu kontrol eden kısmi korelasyon bu n ile kurulmaz. Kısmi korelasyon için serbestlik kalmaz.

## Banka takibi

Takip, bankanın kendi nakdi KOBİ kredisidir. Ticari alacak gecikmesinin yerine konmaz.

Yıllık, Aralık/Aralık, n = 11. Reel kredi artışı ile takip stoku artışı: {_korel_md(yb['reel_artis_ile_takip_artisi'])}. Reel kredi artışı ile takip oranının puan farkı: {_korel_md(yb['reel_artis_ile_npl_farki'])}. Oran, payda büyüyünce kendiliğinden düşer; 2020-2023'teki oran düşüşü bu özdeşliğin içindedir.

Aylık Granger, 2014-02 .. 2026-08 log farkları. Klasik F, HAC yok. Birincil gecikme 1 ve 3'tür; 6 ve 12 duyarlılıktır. Dört birincil test birlikte okunur (iki yön, iki gecikme).

Takip stoku büyümesi → reel kredi büyümesi:

- {_gr_md(g1[0])}
- {_gr_md(g1[1])}

Reel kredi büyümesi → takip stoku büyümesi:

- {_gr_md(g2[0])}
- {_gr_md(g2[1])}

Katsayı toplamları negatiftir. Takip stoku hızlanınca sonraki reel kredi büyümesi yavaşlar. Reel kredi hızlanınca sonraki takip stoku büyümesi yavaşlar. Dört birincil p değerinin hepsi Bonferroni eşiği 0,0125'in üstündedir. Gecikme 1 DW {_tr(g1[0]['durbin_watson'], 2)} ve {_tr(g2[0]['durbin_watson'], 2)}. HAC uygulanmadı.

Takip oranı ile reel kredi büyümesinin aylık Pearson'ı {_korel_md(s['aylik_korelasyon']['npl_reel_buyume'])} şeklindedir. Oranın nominal büyümeyle Pearson'ı {_korel_md(s['aylik_korelasyon']['npl_nominal_buyume'])} şeklindedir.

## Üç yön

Geç ödeme → kredi artışı. Haziran eşlemesinde fatura payı ile reel kredi artışının Pearson'ı {_tr(fh['pearson'], 2)} ({_p(fh['pearson_p'])}). Banka takip stokundan reel krediye Granger katsayı toplamı gecikme 1'de {_tr(g1[0]['katsayi_toplami'], 3)}, gecikme 3'te {_tr(g1[1]['katsayi_toplami'], 3)}. 2023 Aralık – 2026 Ağustos nominal kat {_tr(b['nominal_kat'], 2)}, reel kat {_tr(b['reel_kat'], 2)}.

Kredi artışı → geç ödeme. Reel krediden takip stokuna Granger katsayı toplamı gecikme 3'te {_tr(g2[1]['katsayi_toplami'], 3)} ({_p(g2[1]['p'])}). 2020-2023 takip oranı düşüşü, takip stoku 58 milyar TL dolayında dururken nakdi stokun büyümesinden gelir.

Ortak fiyat. Nominal yıllık artış ile TÜFE yıllık artışı birlikte hareket eder ({_korel_md(yb['nominal_artis_ile_tufe'])}). 2016-2025 reel bileşik %{_tr(a['reel_bilesik_%'])}.

Kesin ticari-alacak nedenselliği için firma düzeyinde vade aşımı ve yeni kullandırım gerekir. Eldeki nesne stoktur; brüt kullandırım ile itfa birbirini götürebilir.

## Kaynak

- BDDK Aylık Bülten, KOBİ kredileri, `tabloNo=6`, `taraf=10001`, TL. https://www.bddk.org.tr/bultenaylik
- KOSGEB, Türkiye'deki KOBİ'lere İlişkin Bazı İstatistiki Göstergeler 2025, Tablo 6. 2015-2024 milyar TL yuvarlaması bu bültenin Aralık ayıdır. https://webdosya.kosgeb.gov.tr/Content/Upload/Dosya/Kurumsal/2025/Tu%CC%88rkiye%27deki_KOBI%CC%87%27lere_I%CC%87lis%CC%A7kin_Baz%C4%B1_I%CC%87statistiki_Go%CC%88stergeler_2025.pdf
- TÜFE: EVDS `TP.FG.J0`; 2026 uzatması `hekis_model/data/tufe_yillik_aylik.json`
- Atradius fatura payları yukarıdaki tablonun URL'lerindedir. 2026 şirket oranı: https://group.atradius.com/knowledge-and-research/reports/b2b-payment-practices-trends-in-turkey-2026
- Eşik: 25 Mayıs 2023, 7297 sayılı Cumhurbaşkanı Kararı; 7 Ağustos 2025, 10182 sayılı Karar. https://www.mevzuat.gov.tr/MevzuatMetin/21.5.7297.pdf
"""


def yaz() -> dict:
    s = hesap()
    JSON_YOL.write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")
    MD_YOL.write_text(rapor(s), encoding="utf-8")
    with YILLIK_YOL.open("w", newline="", encoding="utf-8") as f:
        alan = ["yil", "nakdi_milyar", "takip_milyar", "npl_%", "nominal_artis_%", "reel_artis_%", "tufe_artis_%", "takip_artis_%", "npl_fark_puan", "orta_pay_%", "musteri"]
        w = csv.DictWriter(f, fieldnames=alan, extrasaction="ignore")
        w.writeheader()
        for y in s["yillik"]:
            w.writerow({k: (round(y[k], 6) if isinstance(y.get(k), float) else y.get(k, "")) for k in alan})
    return s


if __name__ == "__main__":
    s = yaz()
    print(s["pencere"]["2016_2025"])
    print(s["fatura"]["haziran_hepsi"]["reel_yillik"])
    print(s["son_gozlem"])
