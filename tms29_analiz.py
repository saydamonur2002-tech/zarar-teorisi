"""TMS 29 kaynak testi: 2022 orijinal, 2023 karşılaştırmalı ve XI_29.

Sayılar bu dosyanın çalıştırılmasıyla yeniden hesaplanır.
Eşleşme iddiası, ancak TL farkı 1'in altında veya satışa göre
göreli fark 0,001'in altındaysa yazılır. Eksik tablo doldurulmaz.
"""
from __future__ import annotations

import csv
import json
import math
import re
import statistics
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import marj_tur3_kap as kap

ROOT = Path("/workspace")
CACHE = Path("/tmp/kap_xbrl_satir")
CACHE.mkdir(exist_ok=True)
KODLAR = (
    "AKSA ARSAN ATEKS BAYRK BLCYT BOSSA BRKO BRMEN DAGI DERHL DERIM DESA "
    "DIRIT ENSRI HATEK ISSEN KORDS KRTEK LUKSK MAVI MEGAP MNDRS RALYH RODRG "
    "RUBNS SASA SKTAS SNPAM SONME SUNTK SUWEN YUNSA"
).split()
ISTENEN = (
    "Revenue",
    "CostOfSales",
    "GrossProfit",
    "MarketingExpense",
    "AdministrativeExpense",
    "ResearchAndDevelopmentExpense",
    "ProfitLossBeforeTax",
)


def fnum(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


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


def medyan(xs):
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    return None if not xs else statistics.median(xs)


def yakin(a, b, taban):
    if a is None or b is None:
        return False
    if abs(a - b) < 1:
        return True
    if taban and abs(taban) > 0 and abs(a - b) / abs(taban) < 0.001:
        return True
    return False


def gelir_govde(bodies):
    return next((b for b in bodies if "ifrs-full_Revenue|" in b or "Kar veya Zarar Tablosu" in b), "")


def satirlar(gelir):
    rows = []
    for row in re.split(r"<tr class=\"", gelir):
        cm = re.search(r'taxonomy-field-name">([^<|]+)', row)
        if not cm:
            continue
        lab = re.search(r'content-tr" style="display: block;">([^<]+)', row)
        vals = re.findall(r'col-order-class-(\d+)".*?title="([^"]*)"', row, re.S)
        if not vals:
            titles = re.findall(r'taxonomy-context-value".*?title="([^"]*)"', row, re.S)
            vals = [(str(i + 1), t) for i, t in enumerate(titles)]
        if not vals:
            continue
        rows.append({
            "concept": cm.group(1),
            "label": lab.group(1).strip() if lab else "",
            "vals": {int(c): float(v) for c, v in vals if v not in ("", "-")},
        })
    return rows


def sec(rows, ad):
    for r in rows:
        if r["concept"].endswith(ad) or r["concept"].endswith("_" + ad):
            return r
    return None


def nitelik_bul(html):
    m = re.search(r"Finansal Tablo Niteliği.{0,400}?>(Konsolide|Bireysel|Solo)<", html, re.S | re.I)
    if m:
        return m.group(1)
    m = re.search(r"Finansal Tablo Niteliği.{0,200}", html, re.S)
    return ("ham:" + re.sub(r"\s+", " ", m.group(0))[:180]) if m else None


def xbrl_cek(idx):
    yol = CACHE / f"{idx}.json"
    if yol.exists():
        return json.loads(yol.read_text(encoding="utf-8"))
    det = kap.http_json(f"https://www.kap.org.tr/tr/api/notification/attachment-detail/{idx}", timeout=70)
    item = det[0]
    bodies = item.get("disclosureBody") or []
    html = "\n".join(bodies)
    unit = 1.0
    m = re.search(r"Sunum Para Birimi.*?(1(?:\.0{3})*)\s*TL", html, re.S)
    if m:
        unit = float(m.group(1).replace(".", ""))
    rows = satirlar(gelir_govde(bodies))
    cols = sorted({c for r in rows for c in r["vals"]})
    cur = cols[0] if cols else None
    prev = cols[1] if len(cols) > 1 else None
    kalem = {}
    for ad in ISTENEN:
        r = sec(rows, ad)
        if not r:
            kalem[ad] = None
            continue
        kalem[ad] = {
            "concept": r["concept"],
            "label": r["label"],
            "cur": r["vals"].get(cur),
            "prev": r["vals"].get(prev),
        }
    pdfs = [a for a in (item.get("attachments") or []) if str(a.get("fileExtension") or "").lower() == "pdf"]
    tr = [a for a in pdfs if "ENG" not in str(a.get("fileName") or "").upper()]
    att = (tr or pdfs or [None])[0]
    rec = {
        "idx": idx,
        "unit": unit,
        "n_satir": len(rows),
        "cur_col": cur,
        "prev_col": prev,
        "nitelik": nitelik_bul(html),
        "kalem": kalem,
        "pdf_obj": None if not att else att.get("objId"),
        "pdf_ad": None if not att else att.get("fileName"),
    }
    yol.write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
    return rec


def tl(kalem, ad, sutun, unit):
    k = (kalem or {}).get(ad)
    if not k or k.get(sutun) is None:
        return None
    return k[sutun] * unit


def ham_yukle():
    ham = defaultdict(dict)
    for r in csv.DictReader((ROOT / "marj_ham.csv").open(encoding="utf-8")):
        ham[r["kod"]][int(r["yil"])] = {k: fnum(v) if k not in ("kod",) else v for k, v in r.items()}
        ham[r["kod"]][int(r["yil"])]["kod"] = r["kod"]
    return ham


def cekirdek_ham(r):
    xs = [r.get(k) for k in ("brut", "paz", "gy", "arge")]
    if any(x is None for x in xs):
        return None
    return sum(xs)


def cekirdek_kap(rec, sutun):
    """Brüt + pazarlama + GYG + Ar-Ge. Giderler ham ile aynı işaretle (eksi)."""
    if not rec:
        return None, "tablo_yok"
    u = rec["unit"]
    brut = tl(rec["kalem"], "GrossProfit", sutun, u)
    paz = tl(rec["kalem"], "MarketingExpense", sutun, u)
    gy = tl(rec["kalem"], "AdministrativeExpense", sutun, u)
    arge = tl(rec["kalem"], "ResearchAndDevelopmentExpense", sutun, u)
    eksik = [ad for ad, v in (("brut", brut), ("paz", paz), ("gy", gy)) if v is None]
    if eksik:
        return None, "eksik:" + ",".join(eksik)
    if arge is None:
        arge = 0.0
        bayrak = "arge_satiri_yok_sifir"
    else:
        bayrak = "dort_kalem"
    # KAP gideri artı yazılmışsa eksiye çevir. Brüt kâr artı kalır.
    if paz > 0:
        paz = -paz
    if gy > 0:
        gy = -gy
    if arge > 0:
        arge = -arge
    return brut + paz + gy + arge, bayrak


def evds_ay():
    body = {
        "type": "json", "series": "TP.GENENDEKS.T1", "aggregationTypes": "avg", "formulas": "0",
        "startDate": "01-01-2016", "endDate": "31-12-2023", "frequency": "5",
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
    ay = {}
    for it in data.get("items") or []:
        raw = it.get("TP_GENENDEKS_T1")
        if raw in (None, ""):
            continue
        t = str(it["Tarih"])
        parca = re.findall(r"\d+", t)
        if len(parca) < 2:
            continue
        if len(parca[0]) == 4:
            yil, ay_no = int(parca[0]), int(parca[1])
        else:
            ay_no, yil = int(parca[0]), int(parca[-1])
        ay[f"{yil}-{ay_no}"] = float(str(raw).replace(",", ""))
    return ay


def panel_100(ham):
    liste = {r["kod"]: r for r in csv.DictReader((ROOT / "marj_sirket_liste.csv").open(encoding="utf-8"))}
    panel = []
    for kod, s in liste.items():
        if s["grup"] != "faaliyet":
            continue
        if all(y in ham[kod] and (ham[kod][y].get("satis") or 0) > 0 for y in range(2016, 2024)):
            panel.append(kod)
    panel.sort(key=lambda k: ham[k][2023]["satis"], reverse=True)
    return panel[:100]


def idx_topla(ham):
    isler = {}
    for kod in KODLAR:
        y22 = json.loads(Path(f"/tmp/kap_tekstil/{kod}.json").read_text(encoding="utf-8"))["yillar"]["2022"]
        y23 = json.loads(Path(f"/tmp/kap_tms29/{kod}.json").read_text(encoding="utf-8"))
        isler[("2022", kod)] = y22["idx"]
        for b in y23["bildirimler"]:
            isler[("2023", kod, b["idx"])] = b["idx"]
    for kod in panel_100(ham):
        p = Path(f"/tmp/kap_tur3/{kod}.json")
        if not p.exists():
            continue
        y = json.loads(p.read_text(encoding="utf-8")).get("yillar", {}).get("2022", {})
        if y.get("idx"):
            isler[("top", kod)] = y["idx"]
    return isler


def cek_hepsi(idxler):
    benzersiz = sorted(set(idxler))
    eksik = [i for i in benzersiz if not (CACHE / f"{i}.json").exists()]
    print(f"xbrl {len(benzersiz)} indeks, onbellek disi {len(eksik)}", flush=True)

    def bir(i):
        try:
            xbrl_cek(i)
            return i, None
        except Exception as exc:  # noqa: BLE001
            return i, str(exc)

    hatalar = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = [ex.submit(bir, i) for i in eksik]
        for n, fut in enumerate(as_completed(futs), 1):
            i, err = fut.result()
            if err:
                hatalar[i] = err
            if n % 20 == 0 or n == len(eksik):
                print(f"  {n}/{len(eksik)} hata {len(hatalar)}", flush=True)
    return hatalar


def main():
    ham = ham_yukle()
    isler = idx_topla(ham)
    hatalar = cek_hepsi(isler.values())
    ay = evds_ay()
    ort2022 = statistics.fmean([ay[f"2022-{m}"] for m in range(1, 13)])
    ort2016 = statistics.fmean([ay[f"2016-{m}"] for m in range(1, 13)])
    dec22 = ay["2022-12"]
    dec23 = ay["2023-12"]
    tufe = {
        "seri": "TP.GENENDEKS.T1",
        "n_ay_2022": sum(1 for m in range(1, 13) if f"2022-{m}" in ay),
        "ort_2016": ort2016,
        "ort_2022": ort2022,
        "aralik_2022": dec22,
        "aralik_2023": dec23,
        "aralik23_bolu_aralik22": dec23 / dec22,
        "aralik23_bolu_ort2022": dec23 / ort2022,
        "ort2022_bolu_ort2016": ort2022 / ort2016,
    }

    satirlar_32 = []
    for kod in KODLAR:
        y22 = json.loads(Path(f"/tmp/kap_tekstil/{kod}.json").read_text(encoding="utf-8"))["yillar"]["2022"]
        y23 = json.loads(Path(f"/tmp/kap_tms29/{kod}.json").read_text(encoding="utf-8"))
        a = ham[kod][2022]["satis"]
        b_rec = None
        if (CACHE / f"{y22['idx']}.json").exists():
            b_rec = json.loads((CACHE / f"{y22['idx']}.json").read_text(encoding="utf-8"))
        b = None if not b_rec else tl(b_rec["kalem"], "Revenue", "cur", b_rec["unit"])
        bildirimler = []
        for b23 in y23["bildirimler"]:
            rec = None
            yol = CACHE / f"{b23['idx']}.json"
            if yol.exists():
                rec = json.loads(yol.read_text(encoding="utf-8"))
            c = None if not rec else tl(rec["kalem"], "Revenue", "prev", rec["unit"])
            vo_c = None if not rec else tl(rec["kalem"], "ProfitLossBeforeTax", "prev", rec["unit"])
            cek_c, cek_bay = cekirdek_kap(rec, "prev")
            bildirimler.append({
                "idx": b23["idx"],
                "tarih": b23.get("tarih"),
                "tur_html": b23.get("tur"),
                "nitelik": None if not rec else rec.get("nitelik"),
                "unit": None if not rec else rec.get("unit"),
                "c": c,
                "vo_c": vo_c,
                "cekirdek_c": cek_c,
                "cekirdek_bayrak": cek_bay,
                "url": b23.get("url"),
            })
        ilk = bildirimler[0] if bildirimler else {}
        son = bildirimler[-1] if bildirimler else {}
        c = ilk.get("c")
        cek_b, cek_b_bay = cekirdek_kap(b_rec, "cur")
        vo_b = None if not b_rec else tl(b_rec["kalem"], "ProfitLossBeforeTax", "cur", b_rec["unit"])
        h = ham[kod][2022]
        satirlar_32.append({
            "kod": kod,
            "a": a,
            "b": b,
            "c_ilk": c,
            "c_son": son.get("c"),
            "b_bolu_a": None if not a else b / a,
            "c_bolu_a": None if not (a and c is not None) else c / a,
            "c_bolu_b": None if not (b and c is not None) else c / b,
            "cson_bolu_b": None if not (b and son.get("c") is not None) else son["c"] / b,
            "a_esit_c_ilk": yakin(a, c, a),
            "a_esit_c_son": yakin(a, son.get("c"), a),
            "a_esit_b": yakin(a, b, a),
            "vo_ham": h.get("vergi_oncesi"),
            "vo_b": vo_b,
            "vo_c": ilk.get("vo_c"),
            "vo_ham_esit_c": yakin(h.get("vergi_oncesi"), ilk.get("vo_c"), a),
            "cek_ham": cekirdek_ham(h),
            "cek_b": cek_b,
            "cek_b_bayrak": cek_b_bay,
            "cek_c": ilk.get("cekirdek_c"),
            "cek_c_bayrak": ilk.get("cekirdek_bayrak"),
            "cek_ham_esit_c": yakin(cekirdek_ham(h), ilk.get("cekirdek_c"), a),
            "nitelik_2022": None if not b_rec else b_rec.get("nitelik"),
            "nitelik_2023": ilk.get("nitelik"),
            "tur_2023_html": ilk.get("tur_html"),
            "tarih_b": y22.get("tarih"),
            "idx_b": y22.get("idx"),
            "unit_b": y22.get("unit"),
            "tarih_c": ilk.get("tarih"),
            "idx_c": ilk.get("idx"),
            "unit_c": ilk.get("unit"),
            "n_2023": len(bildirimler),
            "bildirimler": [{k: v for k, v in b23.items() if k in ("idx", "tarih", "c", "nitelik", "tur_html")} for b23 in bildirimler],
            "hata_idx": [hatalar[i] for i in (y22.get("idx"), ilk.get("idx")) if i in hatalar],
        })

    oran = [r["c_bolu_b"] for r in satirlar_32 if r["c_bolu_b"] is not None]
    katsayi = {
        "n": len(oran),
        "medyan": medyan(oran),
        "p25": pct(oran, 0.25),
        "p75": pct(oran, 0.75),
        "min": min(oran) if oran else None,
        "max": max(oran) if oran else None,
        "ortalama": statistics.fmean(oran) if oran else None,
    }
    hedef = tufe["aralik23_bolu_ort2022"]
    yilsonu = tufe["aralik23_bolu_aralik22"]
    for r in satirlar_32:
        cb = r["c_bolu_b"]
        r["c_b_bolu_ort_faktor"] = None if cb is None else cb / hedef
        r["c_b_eksi_ort_faktor"] = None if cb is None else cb - hedef
        r["yuzde5_ort_bandinda"] = None if cb is None else abs(cb / hedef - 1) <= 0.05

    # Reel satış: ilk 100, ham 2022 ve KAP 2022 cari sütun
    ilk = panel_100(ham)
    reel_ham = []
    reel_orj = []
    cek_ham_deg = []
    cek_orj_deg = []
    orj_yok = []
    for kod in ilk:
        s16 = ham[kod][2016]["satis"]
        s22 = ham[kod][2022]["satis"]
        reel_ham.append((s22 / ort2022) / (s16 / ort2016) - 1)
        p = Path(f"/tmp/kap_tur3/{kod}.json")
        y = json.loads(p.read_text(encoding="utf-8")).get("yillar", {}).get("2022", {}) if p.exists() else {}
        rec = None
        if y.get("idx") and (CACHE / f"{y['idx']}.json").exists():
            rec = json.loads((CACHE / f"{y['idx']}.json").read_text(encoding="utf-8"))
        b = None if not rec else tl(rec["kalem"], "Revenue", "cur", rec["unit"])
        if b is None or b <= 0:
            orj_yok.append(kod)
        else:
            reel_orj.append((b / ort2022) / (s16 / ort2016) - 1)
        m16 = cekirdek_ham(ham[kod][2016])
        m22 = cekirdek_ham(ham[kod][2022])
        if m16 is not None and m22 is not None and s16 and s22:
            cek_ham_deg.append((m22 / s22 - m16 / s16) * 100)
        cek_b, _ = cekirdek_kap(rec, "cur")
        if cek_b is not None and b and m16 is not None and s16:
            cek_orj_deg.append((cek_b / b - m16 / s16) * 100)

    # 32 firma, 2016 ham satışı olanlar
    alt = []
    for r in satirlar_32:
        kod = r["kod"]
        if 2016 not in ham[kod] or not (ham[kod][2016].get("satis") or 0):
            r["reel_2016_var"] = False
            continue
        r["reel_2016_var"] = True
        s16 = ham[kod][2016]["satis"]
        r["reel_ham"] = (r["a"] / ort2022) / (s16 / ort2016) - 1
        r["reel_orj"] = None if not r["b"] else (r["b"] / ort2022) / (s16 / ort2016) - 1
        m16 = cekirdek_ham(ham[kod][2016])
        if m16 is not None and r["cek_ham"] is not None and r["a"]:
            r["cek_deg_ham_pp"] = (r["cek_ham"] / r["a"] - m16 / s16) * 100
        else:
            r["cek_deg_ham_pp"] = None
        if m16 is not None and r["cek_b"] is not None and r["b"]:
            r["cek_deg_orj_pp"] = (r["cek_b"] / r["b"] - m16 / s16) * 100
        else:
            r["cek_deg_orj_pp"] = None
        if r["vo_ham"] is not None and r["a"]:
            r["vo_marj_ham"] = r["vo_ham"] / r["a"]
        if r["vo_b"] is not None and r["b"]:
            r["vo_marj_b"] = r["vo_b"] / r["b"]
        if r.get("vo_marj_ham") is not None and r.get("vo_marj_b") is not None:
            r["vo_marj_fark_pp"] = (r["vo_marj_ham"] - r["vo_marj_b"]) * 100
        alt.append(r)

    def ozet_reel(xs):
        return {"n": len(xs), "medyan": medyan(xs), "p25": pct(xs, 0.25), "p75": pct(xs, 0.75), "ortalama": statistics.fmean(xs) if xs else None}

    sonuc = {
        "tufe": tufe,
        "katsayi_ilk_bildirim": katsayi,
        "eslesme": {
            "n": len(satirlar_32),
            "a_esit_c_ilk": sum(1 for r in satirlar_32 if r["a_esit_c_ilk"]),
            "a_esit_c_son": sum(1 for r in satirlar_32 if r["a_esit_c_son"]),
            "a_esit_b": sum(1 for r in satirlar_32 if r["a_esit_b"]),
            "vo_ham_esit_c": sum(1 for r in satirlar_32 if r["vo_ham_esit_c"]),
            "cek_ham_esit_c": sum(1 for r in satirlar_32 if r["cek_ham_esit_c"]),
            "band_5": sum(1 for r in satirlar_32 if r["yuzde5_ort_bandinda"]),
        },
        "ilk100_reel_ham": ozet_reel(reel_ham),
        "ilk100_reel_orj": ozet_reel(reel_orj),
        "ilk100_orj_yok": orj_yok,
        "ilk100_cek_deg_ham_pp": ozet_reel(cek_ham_deg),
        "ilk100_cek_deg_orj_pp": ozet_reel(cek_orj_deg),
        "tekstil32_reel_ham": ozet_reel([r["reel_ham"] for r in alt if r.get("reel_ham") is not None]),
        "tekstil32_reel_orj": ozet_reel([r["reel_orj"] for r in alt if r.get("reel_orj") is not None]),
        "tekstil32_cek_deg_ham": ozet_reel([r["cek_deg_ham_pp"] for r in alt if r.get("cek_deg_ham_pp") is not None]),
        "tekstil32_cek_deg_orj": ozet_reel([r["cek_deg_orj_pp"] for r in alt if r.get("cek_deg_orj_pp") is not None]),
        "tekstil32_vo_marj_fark_pp": ozet_reel([r["vo_marj_fark_pp"] for r in alt if r.get("vo_marj_fark_pp") is not None]),
        "firmalar": satirlar_32,
        "xbrl_hata": hatalar,
        "not": "c ilk 2023 yıllık bildiriminin önceki sütunudur. a marj_ham.csv 2022 satis. b 2022 yıllık bildiriminin cari hasılatıdır.",
    }
    (ROOT / "tms29_satis_sonuc.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: sonuc[k] for k in sonuc if k != "firmalar"}, ensure_ascii=False, indent=2))
    print("---firmalar---")
    for r in satirlar_32:
        print(
            f"{r['kod']:6} a={r['a']:.0f} b={r['b']} c={r['c_ilk']} cb={r['c_bolu_b']} "
            f"esit={r['a_esit_c_ilk']} vo={r['vo_ham_esit_c']} cek={r['cek_ham_esit_c']} "
            f"nit22={r['nitelik_2022']} nit23={r['nitelik_2023']}"
        )


if __name__ == "__main__":
    main()
