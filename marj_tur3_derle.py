"""Tur 3 ara sayıları: dipnot, eşik, beta çifti, TCMB alt kalem, çıkan özet.

Medyanlar toplanmaz. Eksik firma doldurulmaz. 2022 İş Yatırım sütunu
TMS 29 karşılaştırmalısı olabilir; dipnot kırılımı özgün bildirimdendir.
"""
from __future__ import annotations

import csv
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import xlrd

from marj_dipnot import blok_ayir
from marj_tur3_yerel import (
    beta,
    cekirdek,
    deg,
    fnum,
    fold,
    kapanan_oku,
    marj,
    medyan,
    net,
    ortalama,
    ozet,
    pct,
)

ROOT = Path("/workspace")
CACHE = Path("/tmp/kap_tur3")
YILLAR = list(range(2016, 2024))
IMALAT = {
    "Gıda ve içecek", "Mineral ürünler", "Makine ve teçhizat", "Kimya",
    "Tekstil ve giyim", "Dayanıklı tüketim", "Kağıt", "Ana metal", "Otomotiv",
}


def yukle():
    liste = {r["kod"]: r for r in csv.DictReader((ROOT / "marj_sirket_liste.csv").open(encoding="utf-8"))}
    ham = defaultdict(dict)
    for r in csv.DictReader((ROOT / "marj_ham.csv").open(encoding="utf-8")):
        ham[r["kod"]][int(r["yil"])] = r
    return liste, ham


def panel_sirali(liste, ham):
    panel = [k for k, s in liste.items() if s["grup"] == "faaliyet" and all(
        y in ham[k] and (fnum(ham[k][y].get("satis")) or 0) > 0 for y in YILLAR)]
    panel.sort(key=lambda k: fnum(ham[k][2023]["satis"]), reverse=True)
    return panel


def pp(a, b):
    if a is None or b is None or b == 0:
        return None
    return (a - b) * 100


def dipnot():
    """Özgün 2016 ve 2022 bildirimlerinin PDF dipnotu. Yüz = aynı bildirimin XBRL'i."""
    say = Counter()
    firmalar = []
    for path in sorted(CACHE.glob("*.json")):
        j = json.loads(path.read_text(encoding="utf-8"))
        rec = {"kod": j["kod"], "yil": {}}
        for yil in ("2016", "2022"):
            y = j["yillar"].get(yil) or {}
            taraf = {}
            for ad, anahtar in (("gelir", "fin_gelir"), ("gider", "fin_gider")):
                if y.get("hata"):
                    taraf[ad] = {"durum": y["hata"]}
                    continue
                hedef = y.get(anahtar)
                txt = CACHE / f"{j['kod']}_{yil}.txt"
                if hedef is None:
                    taraf[ad] = {"durum": "yuz_toplami_yok"}
                    continue
                if not txt.exists():
                    taraf[ad] = {"durum": y.get("pdf_hata") or "pdf_metin_yok"}
                    continue
                metin = txt.read_text(encoding="utf-8", errors="replace")
                blok = blok_ayir(metin, hedef, ad)
                blok.pop("satir", None)
                taraf[ad] = blok
                say[f"{yil}_{ad}_{blok.get('durum')}"] += 1
            rev = y.get("rev")
            vo = y.get("vo")
            fg, fh = y.get("fin_gelir"), y.get("fin_gider")
            rec["yil"][yil] = {
                "taraf": taraf,
                "rev": rev,
                "vo_marj": None if not rev or vo is None else vo / rev,
                "fin_marj": None if not rev or fg is None or fh is None else (fg + fh) / rev,
                "unit": y.get("unit"),
            }
        # 2023 karşılaştırmalı sütun
        y3 = j["yillar"].get("2023") or {}
        rec["restated_2022"] = {
            "rev": y3.get("rev_prev"),
            "vo_marj": None if not y3.get("rev_prev") or y3.get("vo_prev") is None else y3["vo_prev"] / y3["rev_prev"],
            "fin_marj": None if not y3.get("rev_prev") or y3.get("fin_gelir_prev") is None or y3.get("fin_gider_prev") is None
            else (y3["fin_gelir_prev"] + y3["fin_gider_prev"]) / y3["rev_prev"],
        }
        firmalar.append(rec)
    return say, firmalar


def _eko(blok, gider: bool) -> dict | None:
    """Kapanan bloğu 'gelir pozitif, gider pozitif' işaretine çevirir.

    PDF gideri bazen parantezle (XBRL ile aynı, negatif), bazen pozitif yazar.
    Blok toplamı negatifse tüm kalemlerin işareti çevrilir; böylece kapalı
    toplam korunur. Satır satır mutlak değer, eksi yönlü kalemi gider sanır.
    """
    if not blok or blok.get("durum") != "kapandi":
        return None
    flip = (blok.get("toplam") or 0) < 0
    return {k: (-blok[k] if flip else blok[k]) for k in ("kur", "faiz", "diger")}


def kalem_degisim(firmalar):
    """Her kalem, iki yılda da o taraf kapandıysa. Net = gelir − gider, ekonomik işarette."""
    kalemler = ("kur", "faiz", "diger")
    out = {}
    for taraf, gider in (("gelir", False), ("gider", True)):
        for kal in kalemler:
            xs = []
            for f in firmalar:
                a = _eko(f["yil"]["2016"]["taraf"].get(taraf), gider)
                b = _eko(f["yil"]["2022"]["taraf"].get(taraf), gider)
                ra, rb = f["yil"]["2016"]["rev"], f["yil"]["2022"]["rev"]
                if a is None or b is None or not ra or not rb:
                    continue
                xs.append((b[kal] / rb - a[kal] / ra) * 100)
            out[f"{taraf}_{kal}"] = {"n": len(xs), "ozet": ozet(xs)}
    netler = {k: [] for k in ("kur", "faiz", "diger", "vo", "fin")}
    netler_abs = {k: [] for k in kalemler}
    kod_net = []
    karisik = 0
    for f in firmalar:
        parca = {}
        parca_abs = {}
        ok = True
        for yil in ("2016", "2022"):
            g = _eko(f["yil"][yil]["taraf"].get("gelir"), False)
            d = _eko(f["yil"][yil]["taraf"].get("gider"), True)
            rev = f["yil"][yil]["rev"]
            if g is None or d is None or not rev:
                ok = False
                break
            ham_g = f["yil"][yil]["taraf"]["gelir"]
            ham_d = f["yil"][yil]["taraf"]["gider"]
            if any(v < 0 for v in (ham_g["kur"], ham_g["faiz"], ham_g["diger"])) and any(
                v > 0 for v in (ham_g["kur"], ham_g["faiz"], ham_g["diger"])
            ):
                karisik += 1
            if any(v < 0 for v in (ham_d["kur"], ham_d["faiz"], ham_d["diger"])) and any(
                v > 0 for v in (ham_d["kur"], ham_d["faiz"], ham_d["diger"])
            ):
                karisik += 1
            for kal in kalemler:
                parca[(yil, kal)] = (g[kal] - d[kal]) / rev
                parca_abs[(yil, kal)] = (abs(ham_g[kal]) - abs(ham_d[kal])) / rev
        if not ok:
            continue
        kod_net.append(f["kod"])
        for kal in kalemler:
            netler[kal].append((parca[("2022", kal)] - parca[("2016", kal)]) * 100)
            netler_abs[kal].append((parca_abs[("2022", kal)] - parca_abs[("2016", kal)]) * 100)
        if f["yil"]["2016"]["vo_marj"] is not None and f["yil"]["2022"]["vo_marj"] is not None:
            netler["vo"].append((f["yil"]["2022"]["vo_marj"] - f["yil"]["2016"]["vo_marj"]) * 100)
        else:
            netler["vo"].append(None)
        if f["yil"]["2016"]["fin_marj"] is not None and f["yil"]["2022"]["fin_marj"] is not None:
            netler["fin"].append((f["yil"]["2022"]["fin_marj"] - f["yil"]["2016"]["fin_marj"]) * 100)
        else:
            netler["fin"].append(None)
    ozet_net = {k: ozet(v) for k, v in netler.items()}
    med_toplam = sum(ozet_net[k]["medyan"] or 0 for k in kalemler)
    ort_toplam = sum(ozet_net[k]["ortalama"] or 0 for k in kalemler)
    return {
        "kalem": out,
        "iki_taraf_kapali": {
            "n": len(kod_net),
            "kod": kod_net,
            "karisik_isaret_blok_sayisi": karisik,
            "ozet": ozet_net,
            "abs_satir_ozet": {k: ozet(v) for k, v in netler_abs.items()},
            "medyanlar_toplami": med_toplam,
            "medyan_toplam_eksi_vo_medyan": None if ozet_net["vo"]["medyan"] is None else med_toplam - ozet_net["vo"]["medyan"],
            "medyan_toplam_eksi_fin_medyan": None if ozet_net["fin"]["medyan"] is None else med_toplam - ozet_net["fin"]["medyan"],
            "ortalamalar_toplami": ort_toplam,
            "ortalama_toplam_eksi_fin_ortalama": None if ozet_net["fin"]["ortalama"] is None else ort_toplam - ozet_net["fin"]["ortalama"],
            "ortalama_toplam_eksi_vo_ortalama": None if ozet_net["vo"]["ortalama"] is None else ort_toplam - ozet_net["vo"]["ortalama"],
        },
    }


def ayrilamayan(firmalar):
    """İki yılda da iki tarafı kapanmayan her firma, engel gerekçesiyle."""
    rows = []
    for f in firmalar:
        engel = []
        tam = True
        for yil in ("2016", "2022"):
            for taraf in ("gelir", "gider"):
                d = f["yil"][yil]["taraf"].get(taraf) or {"durum": "yok"}
                if d.get("durum") != "kapandi":
                    tam = False
                    engel.append(f"{yil} {taraf}: {d.get('durum')}")
        if not tam:
            rows.append({"kod": f["kod"], "engel": engel})
    grup = Counter()
    for r in rows:
        # ilk engel değil; her yıl-taraf çiftinin durumu
        for e in r["engel"]:
            grup[e.split(": ", 1)[1]] += 1
    return {"n": len(rows), "satir": rows, "durum_sayisi": dict(grup)}


def xbrl_marj(firmalar, ham, ilk):
    """Özgün bildirim marjı ile İş Yatırım 2022 sütununun karşılaştırmalısı."""
    ham_esit = []
    orig_vo, orig_fin = [], []
    rest_vo, rest_fin = [], []
    fark_vo, fark_fin = [], []
    for f in firmalar:
        if f["kod"] not in set(ilk):
            continue
        h22 = fnum(ham[f["kod"]][2022].get("satis"))
        rprev = f["restated_2022"]["rev"]
        unit = None
        y22 = json.loads((CACHE / f"{f['kod']}.json").read_text(encoding="utf-8"))["yillar"].get("2023") or {}
        unit = y22.get("unit") or 1
        if h22 and rprev and unit:
            ham_esit.append(abs(h22 - rprev * unit) / h22 < 0.002)
        a, b = f["yil"]["2016"]["vo_marj"], f["yil"]["2022"]["vo_marj"]
        if a is not None and b is not None:
            orig_vo.append((b - a) * 100)
        a, b = f["yil"]["2016"]["fin_marj"], f["yil"]["2022"]["fin_marj"]
        if a is not None and b is not None:
            orig_fin.append((b - a) * 100)
        if f["yil"]["2016"]["vo_marj"] is not None and f["restated_2022"]["vo_marj"] is not None:
            rest_vo.append((f["restated_2022"]["vo_marj"] - f["yil"]["2016"]["vo_marj"]) * 100)
        if f["yil"]["2016"]["fin_marj"] is not None and f["restated_2022"]["fin_marj"] is not None:
            rest_fin.append((f["restated_2022"]["fin_marj"] - f["yil"]["2016"]["fin_marj"]) * 100)
        if f["yil"]["2022"]["vo_marj"] is not None and f["restated_2022"]["vo_marj"] is not None:
            fark_vo.append((f["yil"]["2022"]["vo_marj"] - f["restated_2022"]["vo_marj"]) * 100)
        if f["yil"]["2022"]["fin_marj"] is not None and f["restated_2022"]["fin_marj"] is not None:
            fark_fin.append((f["yil"]["2022"]["fin_marj"] - f["restated_2022"]["fin_marj"]) * 100)
    return {
        "ham2022_karsilastirmali_eslesen": sum(ham_esit),
        "ham2022_karsilastirma_n": len(ham_esit),
        "ozgun_vo": ozet(orig_vo),
        "ozgun_fin": ozet(orig_fin),
        "karsilastirmali_vo": ozet(rest_vo),
        "karsilastirmali_fin": ozet(rest_fin),
        "ozgun_eksi_karsilastirmali_vo": ozet(fark_vo),
        "ozgun_eksi_karsilastirmali_fin": ozet(fark_fin),
    }


def ham_karsilastirma(firmalar, ham):
    """İş Yatırım TL sütunu ile KAP XBRL × sunum birimi. Göreli fark |Δ|/|ham|."""
    def yakin(h, k, olcek):
        if h is None or k is None or olcek in (None, 0) or h == 0:
            return None
        return abs(h - k * olcek) / abs(h) < 0.01

    say = Counter()
    ornek = []
    for f in firmalar:
        j = json.loads((CACHE / f"{f['kod']}.json").read_text(encoding="utf-8"))
        for etiket, yil_ham, yil_kap, prev in (
            ("2016", 2016, "2016", False),
            ("2022_ozgun", 2022, "2022", False),
            ("2022_karsilastirma", 2022, "2023", True),
        ):
            y = j["yillar"].get(yil_kap) or {}
            unit = y.get("unit") or 1
            suf = "_prev" if prev else ""
            hr = ham[f["kod"]].get(yil_ham) or {}
            for alan_h, alan_k in (("satis", "rev"), ("fin_gelir", "fin_gelir"), ("fin_gider", "fin_gider"), ("vergi_oncesi", "vo")):
                ok = yakin(fnum(hr.get(alan_h)), y.get(alan_k + suf), unit)
                say[f"{etiket}_{alan_h}"] += 1 if ok else 0
                say[f"{etiket}_{alan_h}_n"] += 1 if ok is not None else 0
            if etiket == "2016" and len(ornek) < 3:
                ornek.append({
                    "kod": f["kod"],
                    "ham_fin_gider": fnum(hr.get("fin_gider")),
                    "kap_fin_gider": None if y.get("fin_gider") is None else y.get("fin_gider") * unit,
                })
    return {"eslesen": {k: v for k, v in say.items() if not k.endswith("_n")}, "n": {k: v for k, v in say.items() if k.endswith("_n")}, "ornek_isaret": ornek}


def blok(ham, kodlar):
    return {
        "n_firma": len(kodlar),
        "cek": ozet([deg(ham, k, cekirdek) for k in kodlar]),
        "faal": ozet([deg(ham, k, lambda r: fnum(r.get("faaliyet"))) for k in kodlar]),
        "vo": ozet([deg(ham, k, lambda r: fnum(r.get("vergi_oncesi"))) for k in kodlar]),
        "fin": ozet([deg(ham, k, lambda r: net(r, "fin_gelir", "fin_gider")) for k in kodlar]),
    }


def dilimler(ham, panel):
    satis = sorted((fnum(ham[k][2023]["satis"]), k) for k in panel)
    n = len(satis)
    quint = {}
    for i in range(5):
        lo, hi = int(i * n / 5), int((i + 1) * n / 5)
        kodlar = [k for _, k in satis[lo:hi]]
        sinir = (satis[lo][0], satis[hi - 1][0])
        quint[f"Q{i+1}"] = {"n": len(kodlar), "satis_min": sinir[0], "satis_max": sinir[1], **blok(ham, kodlar)}
    c16 = [(marj(ham[k][2016], cekirdek), k) for k in panel]
    m16 = medyan([c for c, _ in c16 if c is not None])
    ilk = set(panel[:100])
    hucre = {}
    for buyuk in (True, False):
        for yuksek in (True, False):
            ks = [k for c, k in c16 if c is not None and ((k in ilk) == buyuk) and ((c >= m16) == yuksek)]
            ad = ("buyuk" if buyuk else "kucuk") + "_" + ("yuksek2016" if yuksek else "dusuk2016")
            hucre[ad] = blok(ham, ks)
    # değişim büyüklüğü: |çekirdek değişimi| medyanının üstü/altı, büyüklükle çapraz
    mut = []
    for k in panel:
        d = deg(ham, k, cekirdek)
        if d is not None:
            mut.append((abs(d), k))
    mm = medyan([a for a, _ in mut])
    capraz = {}
    for buyuk in (True, False):
        for genis in (True, False):
            ks = [k for a, k in mut if ((k in ilk) == buyuk) and ((a >= mm) == genis)]
            ad = ("buyuk" if buyuk else "kucuk") + "_" + ("genis_degisim" if genis else "dar_degisim")
            capraz[ad] = {"abs_cek_sinir": mm, **blok(ham, ks)}
    return {"quintil": quint, "c2016_sinir": m16, "buyukluk_x_c2016": hucre, "buyukluk_x_absdeg": capraz}


def tcmb_alt():
    wb = xlrd.open_workbook(ROOT / "Ekonomik faaliyetlere ve yıllara göre firmaların  gelir tablosu .xls")
    sh = wb.sheet_by_name("t7")
    yillar = [int(sh.cell_value(3, c)) for c in range(2, sh.ncols)]
    starts = [r for r in range(4, sh.nrows) if sh.cell_value(r, 0)]
    for i, r0 in enumerate(starts):
        if not str(sh.cell_value(r0, 0)).startswith("C-"):
            continue
        r1 = starts[i + 1]
        kal = {}
        for r in range(r0, r1):
            et = str(sh.cell_value(r, 1)).split("\n")[0].strip()
            kal[et] = {yillar[j]: sh.cell_value(r, 2 + j) for j in range(len(yillar))}

        def g(parca):
            for et, vals in kal.items():
                if parca in et:
                    return vals
            raise KeyError(parca)

        ns = g("C-Net satış")
        parcalar = {
            "brut": g("Brüt satış karı"),
            "arge": g("1-Araştırma"),
            "paz": g("2-Pazarlama"),
            "gy": g("3-Genel yönetim"),
            "faaliyet": g("Faaliyet karı veya"),
            "kambiyo_kar": g("7-Kambiyo kar"),
            "kambiyo_zar": g("4-Kambiyo zar"),
            "faiz_gelir": g("3-Faiz gelir"),
            "fin_gider": g("H-Finansman"),
        }
        out = {}
        for ad, seri in parcalar.items():
            out[ad] = {str(y): (seri[y] or 0) / ns[y] for y in (2016, 2022)}
        d = {ad: (out[ad]["2022"] - out[ad]["2016"]) * 100 for ad in out}
        # gider satırlarının düşmesi marjı yükseltir
        d["arge_dususu_marja"] = -d["arge"]
        d["paz_dususu_marja"] = -d["paz"]
        d["gy_dususu_marja"] = -d["gy"]
        d["opex_dususu_marja"] = d["arge_dususu_marja"] + d["paz_dususu_marja"] + d["gy_dususu_marja"]
        d["faaliyet_kimlik_kalan"] = d["faaliyet"] - d["brut"] - d["opex_dususu_marja"]
        d["net_kambiyo"] = d["kambiyo_kar"] - d["kambiyo_zar"]
        return {"marj": out, "delta_pp": d}
    return None


def kap_imalat(liste, ham, panel):
    im = [k for k in panel if liste[k]["ana"] in IMALAT]
    im100 = [k for k in panel[:100] if liste[k]["ana"] in IMALAT]

    def agrega(kodlar):
        def oran(yil, fn):
            pay = top = 0.0
            n = 0
            for k in kodlar:
                r = ham[k][yil]
                s = fnum(r.get("satis"))
                v = fn(r)
                if s and v is not None and s > 0:
                    pay += v
                    top += s
                    n += 1
            return None if not top else pay / top, n
        d = {}
        for ad, fn in (
            ("cek", cekirdek),
            ("faal", lambda r: fnum(r.get("faaliyet"))),
            ("vo", lambda r: fnum(r.get("vergi_oncesi"))),
        ):
            a, n2 = oran(2022, fn)
            b, n1 = oran(2016, fn)
            d[ad] = {"n_2016": n1, "n_2022": n2, "delta_pp": None if a is None or b is None else (a - b) * 100}
        return d

    return {
        "tanim": sorted(IMALAT),
        "panel_imalat_n": len(im),
        "ilk100_imalat_n": len(im100),
        "panel_medyan": blok(ham, im),
        "ilk100_medyan": blok(ham, im100),
        "panel_agrega": agrega(im),
        "ilk100_agrega": agrega(im100),
    }


def beta_cift(liste, ham, ilk):
    from marj_ayristirma import UFE_PARCA, deflatorler
    secilen, sektor_kod, notlar, yillik = deflatorler()
    cpi = yillik[secilen["tufe"]]
    cift = []
    yok = []
    for k in ilk:
        bt = beta(ham, k, cpi)
        alt = liste[k]["sektor"]
        kodu = sektor_kod.get(alt)
        bu = beta(ham, k, yillik.get(kodu)) if kodu and kodu in yillik else None
        dc = deg(ham, k, cekirdek)
        if bu is None:
            yok.append({"kod": k, "sektor": alt, "ana": liste[k]["ana"], "not": notlar.get(alt, "ufe haritasi yok"), "beta_tufe": bt})
        else:
            cift.append({"kod": k, "sektor": alt, "beta_tufe": bt, "beta_ufe": bu, "fark": None if bt is None else bu - bt, "cek": dc})

    def esik(rows, alan):
        out = {}
        n = sum(r[alan] is not None for r in rows)
        for t in (0.5, 0.7, 0.8, 0.9, 1.0):
            ust = [r["cek"] for r in rows if r[alan] is not None and r[alan] >= t]
            out[str(t)] = {"n_beta": n, "n_ust": len(ust), "pay": None if not n else len(ust) / n, "cek": ozet(ust)}
        return out

    return {
        "n_cift": len(cift),
        "n_ufe_yok": len(yok),
        "tufe_medyan_cift": medyan([r["beta_tufe"] for r in cift]),
        "ufe_medyan_cift": medyan([r["beta_ufe"] for r in cift]),
        "fark_ufe_eksi_tufe_medyan": medyan([r["fark"] for r in cift]),
        "esik_tufe_ayni_41": esik(cift, "beta_tufe"),
        "esik_ufe_ayni_41": esik(cift, "beta_ufe"),
        "yok_not": dict(Counter(r["not"] for r in yok)),
        "yok_ana": dict(Counter(r["ana"] for r in yok)),
    }


def cikan_ozet():
    d = json.loads((ROOT / "marj_tur3_yerel.json").read_text(encoding="utf-8"))
    olculen = []
    for r in d["cikan_olculen"]:
        def marj16(alan):
            g = (r.get("yillar") or {}).get("2016")
            return None if not g else g.get(alan)
        olculen.append({
            "kod": r["kod"],
            "ad": r["ad"],
            "tarih": r["tarih"],
            "yil": r["yil"],
            "neden": r["neden"],
            "aciklama_bos": not (r.get("aciklama") or "").strip(),
            "aciklama": (r.get("aciklama") or "").split("\n")[0][:180],
            "cek_2016": marj16("cek"),
            "vo_2016": marj16("vo"),
            "son_tam_yil": r.get("son_tam_yil"),
            "onceki_tam_yil": r.get("onceki_tam_yil"),
            "son": r.get("son"),
            "onceki": r.get("onceki"),
            "kar_nakit_ayrisir": r.get("kar_nakit_ayrisir"),
            "2017_2021_son_yil_var": r.get("son_tam_yil") in (2017, 2018, 2019, 2020, 2021),
        })
    # konkordato tüm dosyada
    wb = xlrd.open_workbook("/tmp/kapanan.xls")
    sh = wb.sheet_by_index(0)
    kon = 0
    yat_holding = []
    for r in range(4, sh.nrows):
        ad = str(sh.cell_value(r, 1))
        ac = str(sh.cell_value(r, 3))
        kod = str(sh.cell_value(r, 0))
        if "KONKORDATO" in fold(ac) or "KONKORDATO" in fold(ad):
            kon += 1
        raw = sh.cell_value(r, 2)
        if not isinstance(raw, (int, float)):
            continue
        from datetime import datetime, timedelta
        tarih = datetime(1899, 12, 30) + timedelta(days=int(raw))
        if not (datetime(2016, 1, 1) <= tarih <= datetime(2023, 12, 31)):
            continue
        if "YATIRIM" in fold(ad) and "HOLDING" not in fold(ad):
            yat_holding.append({"kod": kod, "ad": ad, "tarih": tarih.date().isoformat()})
    return {
        "olculen": olculen,
        "veri_yok": d["cikan_veri_yok"],
        "konkordato_dosya_satir": kon,
        "yatirim_adi_holding_sinifi": yat_holding,
    }


def olcek_suren(ham, kodlar, fn):
    xs = [(k, deg(ham, k, fn)) for k in kodlar]
    xs = [(k, v) for k, v in xs if v is not None]
    if not xs:
        return None
    ort = sum(v for _, v in xs) / len(xs)
    sirali = sorted(xs, key=lambda t: abs(t[1]), reverse=True)
    return {"en_buyuk": [{"kod": k, "pp": v} for k, v in sirali[:5]], "ortalama": ort, "n": len(xs)}


def main():
    liste, ham = yukle()
    panel = panel_sirali(liste, ham)
    ilk = panel[:100]
    say, firmalar = dipnot()
    # yalnızca ilk 100 kodları cache'te
    firmalar = [f for f in firmalar if f["kod"] in set(ilk)]
    sonuc = {
        "n_panel": len(panel),
        "ilk100_kod_n": len(ilk),
        "kardemir": [k for k in ilk if k.startswith("KRD")],
        "dipnot_durum_sayaci": dict(say),
        "kalem": kalem_degisim(firmalar),
        "ayrilamayan": ayrilamayan(firmalar),
        "xbrl": xbrl_marj(firmalar, ham, ilk),
        "ham_eslesme": ham_karsilastirma(firmalar, ham),
        "dilim": dilimler(ham, panel),
        "tcmb_alt": tcmb_alt(),
        "kap_imalat": kap_imalat(liste, ham, panel),
        "kucuk_olcek": olcek_suren(ham, panel[100:], cekirdek),
        "cikan": cikan_ozet(),
    }
    try:
        sonuc["beta_cift"] = beta_cift(liste, ham, ilk)
    except Exception as exc:  # noqa: BLE001
        sonuc["beta_cift"] = {"hata": str(exc)}
    (ROOT / "marj_tur3_sayilar.json").write_text(json.dumps(sonuc, ensure_ascii=False), encoding="utf-8")
    k = sonuc["kalem"]["iki_taraf_kapali"]
    print("kapali", k["n"], "med", {a: k["ozet"][a]["medyan"] for a in k["ozet"]})
    print("med toplam", k["medyanlar_toplami"], "gap vo", k["medyan_toplam_eksi_vo_medyan"])
    print("ayrilamayan", sonuc["ayrilamayan"]["n"])
    print("xbrl", json.dumps(sonuc["xbrl"], ensure_ascii=False)[:1500])
    print("beta", sonuc["beta_cift"].get("hata") or {
        "n": sonuc["beta_cift"]["n_cift"],
        "tufe": sonuc["beta_cift"]["tufe_medyan_cift"],
        "ufe": sonuc["beta_cift"]["ufe_medyan_cift"],
        "fark": sonuc["beta_cift"]["fark_ufe_eksi_tufe_medyan"],
    })
    print("tcmb kalan", sonuc["tcmb_alt"]["delta_pp"]["faaliyet_kimlik_kalan"])
    print("imalat", sonuc["kap_imalat"]["panel_imalat_n"], sonuc["kap_imalat"]["panel_medyan"]["cek"]["medyan"], sonuc["kap_imalat"]["panel_agrega"])


if __name__ == "__main__":
    main()
