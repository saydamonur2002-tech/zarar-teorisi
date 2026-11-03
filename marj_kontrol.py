"""Önceki tur iddialarını ham tablodan yeniden hesaplar.

Finansman yüz kırılımı, hayatta kalma, pay sınıfı, beta eşiği, TMS 29 ve
TCMB-KAP farkı. Dipnot okumaz. Dolaylı ithalat testi yoktur.
"""

from __future__ import annotations

import csv
import json
import math
import statistics
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path

import xlrd

ROOT = Path(__file__).resolve().parent
YILLAR = list(range(2016, 2024))
ISY = "https://www.isyatirim.com.tr/_layouts/15/IsYatirim.Website/Common/Data.aspx/MaliTablo"
KALEM = {
    "3C": "satis", "3CA": "sm", "3D": "brut", "3DA": "paz", "3DB": "gy", "3DC": "arge",
    "3DD": "diger_gelir", "3DE": "diger_gider", "3DF": "faaliyet",
    "3HA": "yat_gelir", "3HAA": "yat_gider", "3HAC": "oy_yontem",
    "3HB": "fin_gelir", "3HC": "fin_gider", "3HCA": "vo_diger", "3I": "vergi_oncesi",
}


def fnum(v):
    if v in (None, ""):
        return None
    if isinstance(v, str):
        v = v.replace(" ", "").replace(",", "")
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def fold(s):
    return (str(s).upper()
            .replace("İ", "I").replace("İ", "I")
            .replace("Ş", "S").replace("Ğ", "G")
            .replace("Ü", "U").replace("Ö", "O").replace("Ç", "C"))


def medyan(xs):
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    return None if not xs else statistics.median(xs)


def ortalama(xs):
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    return None if not xs else statistics.fmean(xs)


def pct(xs, p):
    xs = sorted(x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x)))
    if not xs:
        return None
    if len(xs) == 1:
        return xs[0]
    k = (len(xs) - 1) * p
    lo, hi = int(math.floor(k)), int(math.ceil(k))
    if lo == hi:
        return xs[lo]
    return xs[lo] * (hi - k) + xs[hi] * (k - lo)


def ozet(xs):
    return {"n": sum(x is not None for x in xs), "p25": pct(xs, 0.25), "medyan": medyan(xs), "p75": pct(xs, 0.75), "ortalama": ortalama(xs)}


def bol(a, b):
    if a is None or b is None or b == 0:
        return None
    return a / b


def dlog(a, b):
    if a is None or b is None or a <= 0 or b <= 0:
        return None
    return math.log(a) - math.log(b)


def ols(xs, ys):
    n = len(xs)
    if n < 5:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    varx = sum((x - mx) ** 2 for x in xs)
    if varx <= 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / varx


def evds_yillik(kod):
    body = {
        "type": "json", "series": kod, "aggregationTypes": "avg", "formulas": "0",
        "startDate": "01-01-2015", "endDate": "31-12-2023", "frequency": "5",
        "decimalSeperator": ".", "decimal": "4", "dateFormat": "0", "lang": "TR",
        "yon": "0", "sira": "0", "ozelFormuller": [], "groupSeperator": True, "isRaporSayfasi": False,
    }
    req = urllib.request.Request(
        "https://evds3.tcmb.gov.tr/igmevdsms-dis/fe",
        data=json.dumps(body).encode(),
        headers={"Accept": "application/json", "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read().decode("utf-8-sig"))
    ay = defaultdict(list)
    key = kod.replace(".", "_")
    for it in data.get("items") or []:
        v = fnum(it.get(key))
        if v is not None:
            ay[int(str(it["Tarih"])[:4])].append(v)
    return {y: statistics.fmean(vs) for y, vs in ay.items() if len(vs) >= 10}


def cekirdek(r):
    xs = [fnum(r.get(k)) for k in ("brut", "paz", "gy", "arge")]
    if any(x is None for x in xs):
        return None
    return sum(xs)


def net(r, a, b):
    x, y = fnum(r.get(a)), fnum(r.get(b))
    if x is None or y is None:
        return None
    return x + y


def yukle():
    liste = {r["kod"]: r for r in csv.DictReader((ROOT / "marj_sirket_liste.csv").open(encoding="utf-8"))}
    ham = defaultdict(dict)
    for r in csv.DictReader((ROOT / "marj_ham.csv").open(encoding="utf-8")):
        ham[r["kod"]][int(r["yil"])] = r
    return liste, ham


def tam_panel(liste, ham):
    out = []
    for kod, s in liste.items():
        if s["grup"] != "faaliyet":
            continue
        seri = ham.get(kod) or {}
        if any(y not in seri or fnum(seri[y].get("satis")) is None or fnum(seri[y]["satis"]) <= 0 for y in YILLAR):
            continue
        out.append(kod)
    out.sort(key=lambda k: fnum(ham[k][2023]["satis"]), reverse=True)
    return out


def marj(ham, kod, yil, fn):
    r = ham[kod][yil]
    return bol(fn(r), fnum(r.get("satis")))


def degisim(ham, kod, fn):
    a, b = marj(ham, kod, 2022, fn), marj(ham, kod, 2016, fn)
    if a is None or b is None:
        return None
    return (a - b) * 100


def beta_reel(ham, kod, cpi):
    xs, ys = [], []
    for y in range(2017, 2023):
        s1, s0 = fnum(ham[kod][y]["satis"]), fnum(ham[kod][y - 1]["satis"])
        c1, c0 = fnum(ham[kod][y]["sm"]), fnum(ham[kod][y - 1]["sm"])
        if None in (s1, s0, c1, c0) or y not in cpi or (y - 1) not in cpi:
            continue
        ds = dlog(s1 / cpi[y], s0 / cpi[y - 1])
        dc = dlog(abs(c1) / cpi[y], abs(c0) / cpi[y - 1])
        if ds is None or dc is None:
            continue
        xs.append(dc)
        ys.append(ds)
    return ols(xs, ys)


def pay_sinifi_grup(liste, ham, kodlar):
    """Ada göre (A)/(B)/(C)/(D) ve sekiz yılda sabit satış oranı."""
    gruplar = defaultdict(list)
    for k in kodlar:
        ad = liste[k]["ad"]
        kok = ad
        for ek in (" (A)", " (B)", " (C)", " (D)"):
            if ad.endswith(ek):
                kok = ad[: -len(ek)]
        gruplar[(liste[k]["sektor"], kok)].append(k)
    ad_ile = [v for v in gruplar.values() if len(v) > 1]
    # sabit oran
    oran = []
    sec = [k for k in kodlar if all(y in ham[k] for y in YILLAR)]
    for i, a in enumerate(sec):
        sa = [fnum(ham[a][y]["satis"]) for y in YILLAR]
        for b in sec[i + 1:]:
            if liste[a]["sektor"] != liste[b]["sektor"]:
                continue
            sb = [fnum(ham[b][y]["satis"]) for y in YILLAR]
            if any(x is None or x <= 0 or y is None or y <= 0 for x, y in zip(sa, sb)):
                continue
            oranlar = [x / y for x, y in zip(sa, sb)]
            if max(oranlar) / min(oranlar) < 1.005:
                oran.append((a, b, statistics.fmean(oranlar)))
    return ad_ile, oran


def sektor_ozet(liste, ham, kodlar):
    by = defaultdict(list)
    for k in kodlar:
        by[liste[k]["ana"]].append(k)
    out = []
    for ana, ks in sorted(by.items()):
        out.append({
            "ana": ana,
            "n": len(ks),
            "kodlar": ks,
            "cek": ozet([degisim(ham, k, cekirdek) for k in ks]),
            "faal": ozet([degisim(ham, k, lambda r: fnum(r.get("faaliyet"))) for k in ks]),
            "vo": ozet([degisim(ham, k, lambda r: fnum(r.get("vergi_oncesi"))) for k in ks]),
            "fin": ozet([degisim(ham, k, lambda r: net(r, "fin_gelir", "fin_gider")) for k in ks]),
        })
    return out


def kapanan_oku():
    wb = xlrd.open_workbook("/tmp/kapanan.xls")
    sh = wb.sheet_by_index(0)
    rows = []
    for r in range(4, sh.nrows):
        kod = str(sh.cell_value(r, 0)).strip()
        if not kod:
            continue
        raw = sh.cell_value(r, 2)
        if not isinstance(raw, (int, float)):
            continue
        tarih = datetime(1899, 12, 30) + timedelta(days=int(raw))
        if not (datetime(2016, 1, 1) <= tarih <= datetime(2023, 12, 31)):
            continue
        rows.append({
            "kod_ham": kod,
            "kod": kod.split(".")[0].split(":")[0],
            "ad": str(sh.cell_value(r, 1)).strip(),
            "tarih": tarih.date().isoformat(),
            "aciklama": str(sh.cell_value(r, 3)).strip(),
        })
    return rows


def sinif_kapanan(ad, kod_ham):
    u = fold(ad + " " + kod_ham)
    if str(kod_ham).endswith(".F") or "BYF" in u or "PORTFOY" in u:
        return "fon"
    if any(k in u for k in ("BANK", "SIGORTA", "GAYRIMENKUL", "YATIRIM ORTAK")):
        return "finans"
    if "HOLDING" in u or "YATIRIM" in u:
        return "holding"
    return "faaliyet"


def mali_2016(kod):
    qs = "&".join(
        f"year{i}={y}&period{i}=12" for i, y in enumerate((2022, 2020, 2018, 2016), 1)
    )
    url = f"{ISY}?companyCode={kod}&exchange=TRY&financialGroup=XI_29&{qs}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as r:
        data = json.loads(r.read().decode("utf-8-sig"))
    out = {y: {} for y in (2022, 2020, 2018, 2016)}
    for it in data.get("value") or []:
        code = str(it.get("itemCode") or "").strip()
        if code not in KALEM:
            continue
        for i, y in enumerate((2022, 2020, 2018, 2016), 1):
            out[y][KALEM[code]] = fnum(it.get(f"value{i}"))
    return out


def tcmb_imalat():
    wb = xlrd.open_workbook(ROOT / "Ekonomik faaliyetlere ve yıllara göre firmaların  gelir tablosu .xls")
    sh = wb.sheet_by_name("t7")
    yillar = [int(sh.cell_value(3, c)) for c in range(2, sh.ncols)]
    starts = [r for r in range(4, sh.nrows) if sh.cell_value(r, 0)]
    for i, r0 in enumerate(starts):
        ad = str(sh.cell_value(r0, 0)).split("\n")[0]
        if not ad.startswith("C-"):
            continue
        r1 = starts[i + 1]
        kalem = {}
        for r in range(r0, r1):
            et = str(sh.cell_value(r, 1)).split("\n")[0].strip()
            kalem[et] = {yillar[j]: (sh.cell_value(r, 2 + j) if isinstance(sh.cell_value(r, 2 + j), (int, float)) else None) for j in range(len(yillar))}
        def bul(parca):
            for et, vals in kalem.items():
                if parca in et:
                    return vals
            return None
        net, faal = bul("C-Net satışlar"), bul("Faaliyet karı veya zararı")
        ftop, gtop = bul("F-Diğer faal"), bul("G-Diğer faal")
        donem = bul("Dönem kar veya zararı")
        kk, kz = bul("7-Kambiyo karları"), bul("4-Kambiyo zararları")
        enf_k, enf_z = bul("9-Enflasyon düzeltmesi karları"), bul("6-Enflasyon düzeltmesi zararları")
        faiz = bul("3-Faiz gelirleri")
        out = []
        for y in (2016, 2022):
            ns = net[y]
            out.append({
                "yil": y,
                "cekirdek": faal[y] / ns,
                "genis": (faal[y] + ftop[y] - gtop[y]) / ns,
                "vo": donem[y] / ns,
                "net_kambiyo": ((kk[y] or 0) - (kz[y] or 0)) / ns,
                "kambiyo_kar_F": kk[y] / ftop[y],
                "faiz_F": faiz[y] / ftop[y],
                "enf_net": ((enf_k[y] or 0) - (enf_z[y] or 0)) / ns,
            })
        return out
    return None


def firma_sayisi():
    wb = xlrd.open_workbook(ROOT / "Ekonomik faaliyetlere ve yıllara göre temel göstergeler.xls")
    sh = wb.sheet_by_index(0)
    def col(year):
        return 2 + (year - 2009) * 11
    for r in range(sh.nrows):
        if str(sh.cell_value(r, 0)).startswith("C-"):
            return {str(y): sh.cell_value(r, col(y)) for y in (2016, 2022, 2023)} | {
                "buyuk_" + str(y): sh.cell_value(r + 4, col(y)) for y in (2016, 2022)
            }
    return {}


def main():
    liste, ham = yukle()
    cpi = evds_yillik("TP.GENENDEKS.T1")
    panel = tam_panel(liste, ham)
    ilk = panel[:100]
    dup_ad, dup_oran = pay_sinifi_grup(liste, ham, panel)
    # Kardemir ve ad ile yakalananlar: en yüksek 2023 satış kalsın
    atilacak = set()
    for g in dup_ad:
        g2 = sorted(g, key=lambda k: fnum(ham[k][2023]["satis"]), reverse=True)
        atilacak.update(g2[1:])
    birlesik = [k for k in ilk if k not in atilacak]
    # 100 tekil doldurma: panelden atılacaklar çıkınca ilk 100
    panel_tek = [k for k in panel if k not in atilacak]
    yuz_tek = panel_tek[:100]

    def parca(kodlar):
        rows = []
        for k in kodlar:
            d = {
                "kod": k,
                "ana": liste[k]["ana"],
                "cek": degisim(ham, k, cekirdek),
                "faal": degisim(ham, k, lambda r: fnum(r.get("faaliyet"))),
                "nd": degisim(ham, k, lambda r: net(r, "diger_gelir", "diger_gider")),
                "yat": degisim(ham, k, lambda r: net(r, "yat_gelir", "yat_gider")),
                "fin": degisim(ham, k, lambda r: net(r, "fin_gelir", "fin_gider")),
                "vo": degisim(ham, k, lambda r: fnum(r.get("vergi_oncesi"))),
                "beta": beta_reel(ham, k, cpi),
                "cek_2016": marj(ham, k, 2016, cekirdek),
                "vo_2016": marj(ham, k, 2016, lambda r: fnum(r.get("vergi_oncesi"))),
            }
            if None not in (d["vo"], d["cek"], d["nd"], d["yat"], d["fin"]):
                d["res"] = d["vo"] - (d["cek"] + d["nd"] + d["yat"] + d["fin"])
            else:
                d["res"] = None
            rows.append(d)
        return rows

    r100 = parca(ilk)
    rbir = parca(birlesik)
    rtek = parca(yuz_tek)

    def blok(rows):
        return {k: ozet([r[k] for r in rows]) for k in ("cek", "faal", "nd", "yat", "fin", "vo", "res", "beta")}

    # eşik
    esik = {}
    for t in (0.5, 0.7, 0.8, 0.9, 1.0):
        b = [r["beta"] for r in r100 if r["beta"] is not None]
        esik[str(t)] = {
            "n_beta": len(b),
            "pay_beta_ge": sum(x >= t for x in b) / len(b),
            "n_beta_alt_ve_cek_arti_3": sum(r["beta"] is not None and r["beta"] < t and r["cek"] is not None and r["cek"] > 3 for r in r100),
        }

    # hâlâ listede, 2016 satışı var, ilk 100 değil
    disarida = []
    for kod, s in liste.items():
        if s["grup"] != "faaliyet" or kod in ilk or kod in atilacak:
            continue
        seri = ham.get(kod) or {}
        if 2016 not in seri or fnum(seri[2016].get("satis")) is None or fnum(seri[2016]["satis"]) <= 0:
            continue
        disarida.append(kod)

    def duzey(kodlar, yil, fn):
        return [marj(ham, k, yil, fn) for k in kodlar if yil in ham[k]]

    # 2016 ve 2022'si olan, listede kalan, ilk 100 dışı
    cift = [k for k in disarida if 2022 in ham[k] and fnum(ham[k][2022].get("satis")) not in (None, 0)]

    kapan = kapanan_oku()
    for row in kapan:
        row["sinif"] = sinif_kapanan(row["ad"], row["kod_ham"])
    # Adana A/B pay sınıfını C ile birleştir: yalnız ADNAC çekilsin, ADANA ve ADBGR aynı şirket
    cekilecek = []
    gorulen = set()
    for row in kapan:
        if row["sinif"] != "faaliyet":
            continue
        if row["kod"] in ("ADANA", "ADBGR"):
            continue
        if row["kod"] in gorulen:
            continue
        gorulen.add(row["kod"])
        cekilecek.append(row)

    gelen = {}

    def cek(row):
        try:
            return row["kod"], mali_2016(row["kod"]), None
        except Exception as exc:  # noqa: BLE001
            return row["kod"], None, str(exc)

    with ThreadPoolExecutor(max_workers=8) as ex:
        for fut in as_completed([ex.submit(cek, row) for row in cekilecek]):
            kod, veri, err = fut.result()
            gelen[kod] = {"veri": veri, "hata": err}

    delist_olcu = []
    for row in cekilecek:
        g = gelen.get(row["kod"]) or {}
        veri = g.get("veri") or {}
        r16 = veri.get(2016) or {}
        s = r16.get("satis")
        if s is None or s <= 0 or cekirdek(r16) is None or r16.get("vergi_oncesi") is None:
            row["marj"] = None
            row["hata"] = g.get("hata") or "2016 satis veya kar bos"
            continue
        if abs(cekirdek(r16) / s) > 1 or abs(r16["vergi_oncesi"] / s) > 2:
            row["marj"] = "olcek_disi"
            row["cek_2016"] = cekirdek(r16) / s
            continue
        rec = {
            "kod": row["kod"],
            "ad": row["ad"],
            "tarih": row["tarih"],
            "aciklama": row["aciklama"][:180],
            "cek_2016": cekirdek(r16) / s,
            "vo_2016": r16["vergi_oncesi"] / s,
        }
        r22 = veri.get(2022) or {}
        if r22.get("satis") not in (None, 0) and cekirdek(r22) is not None and r22.get("vergi_oncesi") is not None:
            rec["cek_2022"] = cekirdek(r22) / r22["satis"]
            rec["vo_2022"] = r22["vergi_oncesi"] / r22["satis"]
            rec["d_cek"] = (rec["cek_2022"] - rec["cek_2016"]) * 100
            rec["d_vo"] = (rec["vo_2022"] - rec["vo_2016"]) * 100
        delist_olcu.append(rec)
        row["marj"] = "var"

    imalat_ana = {"Gıda ve içecek", "Kimya", "Otomotiv", "Ana metal", "Mineral ürünler", "Tekstil ve giyim", "Dayanıklı tüketim", "Kağıt", "Makine ve teçhizat"}
    kap_imalat = [r for r in r100 if r["ana"] in imalat_ana and r["kod"] not in atilacak]

    sonuc = {
        "cpi_2016": cpi.get(2016),
        "cpi_2022": cpi.get(2022),
        "tam_panel": len(panel),
        "esik_satis_2023": fnum(ham[ilk[-1]][2023]["satis"]),
        "ilk100_kod": ilk,
        "pay_sinifi_ad": dup_ad,
        "pay_sinifi_oran": dup_oran,
        "atilan": sorted(atilacak),
        "birlesik_n": len(birlesik),
        "yuz_tek_giren": [k for k in yuz_tek if k not in ilk],
        "blok_100": blok(r100),
        "blok_birlesik": blok(rbir),
        "blok_yuz_tek": blok(rtek),
        "esik": esik,
        "beta_sirali": sorted((round(r["beta"], 4), r["kod"]) for r in r100 if r["beta"] is not None),
        "sektor_once": sektor_ozet(liste, ham, ilk),
        "sektor_birlesik": sektor_ozet(liste, ham, birlesik),
        "listede_2016_var_ilk100_degil_n": len(disarida),
        "listede_cift_2016_2022_n": len(cift),
        "duzey_2016_ilk100": {"cek": ozet([r["cek_2016"] for r in r100]), "vo": ozet([r["vo_2016"] for r in r100])},
        "duzey_2016_disari": {"cek": ozet(duzey(disarida, 2016, cekirdek)), "vo": ozet(duzey(disarida, 2016, lambda r: fnum(r.get("vergi_oncesi"))))},
        "duzey_2016_disari_olcek_ici": {
            "n_kural": "2016 çekirdek marjının mutlak değeri 1'den küçük",
            "kod_n": sum(1 for k in disarida if (m := marj(ham, k, 2016, cekirdek)) is not None and abs(m) <= 1),
            "cek": ozet([m for k in disarida if (m := marj(ham, k, 2016, cekirdek)) is not None and abs(m) <= 1]),
            "vo": ozet([marj(ham, k, 2016, lambda r: fnum(r.get("vergi_oncesi"))) for k in disarida if (m := marj(ham, k, 2016, cekirdek)) is not None and abs(m) <= 1]),
        },
        "degisim_disari_cift": {
            "cek": ozet([degisim(ham, k, cekirdek) for k in cift]),
            "vo": ozet([degisim(ham, k, lambda r: fnum(r.get("vergi_oncesi"))) for k in cift]),
            "fin": ozet([degisim(ham, k, lambda r: net(r, "fin_gelir", "fin_gider")) for k in cift]),
        },
        "kapanan_sayim": {s: sum(1 for row in kapan if row["sinif"] == s) for s in ("faaliyet", "holding", "finans", "fon")},
        "kapanan": [{k: row[k] for k in ("kod", "ad", "tarih", "sinif", "aciklama")} for row in kapan],
        "delist_olcu": delist_olcu,
        "delist_ayiklanan": [{"kod": row["kod"], "ad": row["ad"], "marj": row.get("marj"), "hata": row.get("hata"), "cek_2016": row.get("cek_2016")} for row in cekilecek if row.get("marj") != "var"],
        "delist_2016": {
            "cek": ozet([r["cek_2016"] for r in delist_olcu]),
            "vo": ozet([r["vo_2016"] for r in delist_olcu]),
        },
        "delist_degisim_olan": [r for r in delist_olcu if "d_cek" in r],
        "kap_imalat_n": len(kap_imalat),
        "kap_imalat_cek": ozet([r["cek"] for r in kap_imalat]),
        "kap_imalat_faal": ozet([r["faal"] for r in kap_imalat]),
        "tcmb_imalat": tcmb_imalat(),
        "tcmb_firma_sayisi": firma_sayisi(),
        "res_buyuk": [r["kod"] for r in r100 if r["res"] is not None and abs(r["res"]) > 1],
    }
    (ROOT / "marj_kontrol.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "cpi": [sonuc["cpi_2016"], sonuc["cpi_2022"]],
        "blok_100": sonuc["blok_100"],
        "esik": sonuc["esik"],
        "atilan": sonuc["atilan"],
        "giren": sonuc["yuz_tek_giren"],
        "delist_n": len(delist_olcu),
        "delist_2016": sonuc["delist_2016"],
        "disari_n": sonuc["listede_2016_var_ilk100_degil_n"],
        "disari_2016": sonuc["duzey_2016_disari"],
        "ilk_2016": sonuc["duzey_2016_ilk100"],
        "cift": sonuc["degisim_disari_cift"],
        "kap_imalat": sonuc["kap_imalat_n"],
        "kap_imalat_cek": sonuc["kap_imalat_cek"],
        "tcmb": sonuc["tcmb_imalat"],
        "firma": sonuc["tcmb_firma_sayisi"],
        "kapanan": sonuc["kapanan_sayim"],
        "sektor_n": [(s["ana"], s["n"], s["cek"]["medyan"], s["cek"]["p25"], s["cek"]["p75"]) for s in sonuc["sektor_birlesik"]],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
