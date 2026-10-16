"""Bulgu envanteri için firma-yıl tablosu ve sütun duyarlılığı.

XI_29 değerinin kaynağı marj_ham.csv'dir; KAP yayım tarihi bu dosyada yoktur.
KAP hücresi, bildirimin indeksi ve yayım tarihi yazılmadan doldurulmaz.
Pazarlama veya Ar-Ge satırı boşsa çekirdek kurulmaz.
KRDMA ve KRDMB ana analizde yoktur; konsolide satır KRDMD'dir.
"""
from __future__ import annotations

import csv
import json
import math
import statistics
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import marj_tur3_kap as kap
import tms29_analiz as ta

ROOT = Path("/workspace")
KODLAR32 = (
    "AKSA ARSAN ATEKS BAYRK BLCYT BOSSA BRKO BRMEN DAGI DERHL DERIM DESA "
    "DIRIT ENSRI HATEK ISSEN KORDS KRTEK LUKSK MAVI MEGAP MNDRS RALYH RODRG "
    "RUBNS SASA SKTAS SNPAM SONME SUNTK SUWEN YUNSA"
).split()
ORNEK = (
    "AKSA KORDS MAVI SASA MNDRS BOSSA DERHL DIRIT YUNSA SUWEN HATEK DESA BLCYT KRTEK "
    "TUPRS THYAO BIMAS AEFES TCELL EREGL FROTO SISE ENKAI PGSUS CCOLA ARCLK TOASO ASELS"
).split()
PAY = {"KRDMA": "KRDMD", "KRDMB": "KRDMD", "KRDMD": "KRDMD"}
CPI16 = 280.84583333333336
CPI22 = 967.7108333333334


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


def ozet(xs):
    return {
        "n": sum(x is not None for x in xs),
        "medyan": medyan(xs),
        "p25": pct(xs, 0.25),
        "p75": pct(xs, 0.75),
    }


def isaret(a, b):
    if a is None or b is None or a == 0 or b == 0:
        return "belirlenemiyor"
    return "evet" if (a > 0) != (b > 0) else "hayir"


def cekirdek_siki(rec, sutun):
    if not rec:
        return None, "tablo_yok"
    u = rec["unit"]
    parca = {
        "brut": ta.tl(rec["kalem"], "GrossProfit", sutun, u),
        "paz": ta.tl(rec["kalem"], "MarketingExpense", sutun, u),
        "gy": ta.tl(rec["kalem"], "AdministrativeExpense", sutun, u),
        "arge": ta.tl(rec["kalem"], "ResearchAndDevelopmentExpense", sutun, u),
    }
    bos = [k for k, v in parca.items() if v is None]
    if bos:
        return None, "bos:" + ",".join(bos)
    brut, paz, gy, arge = parca["brut"], parca["paz"], parca["gy"], parca["arge"]
    if paz > 0:
        paz = -paz
    if gy > 0:
        gy = -gy
    if arge > 0:
        arge = -arge
    return brut + paz + gy + arge, "tam"


def cekirdek_xi(r):
    xs = [r.get(k) for k in ("brut", "paz", "gy", "arge")]
    if any(x is None for x in xs):
        return None
    return sum(xs)


def net_fin(gelir, gider):
    if gelir is None or gider is None:
        return None
    return gelir + gider


def hucre(v):
    if v is None:
        return "veri yok"
    if isinstance(v, float):
        if math.isnan(v):
            return "veri yok"
        return f"{v:.6g}"
    return str(v)


def kap_yil_oku(kod):
    out = {}
    for kok in (Path("/tmp/kap_tur3"), Path("/tmp/kap_tekstil")):
        p = kok / f"{kod}.json"
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        for y, v in d.get("yillar", {}).items():
            if y not in out or (out[y].get("rev") is None and v.get("rev") is not None):
                out[y] = v
    return out


def xbrl_oku(idx):
    if not idx:
        return None
    p = Path("/tmp/kap_xbrl_satir") / f"{idx}.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def yillik_aday(oid, yil):
    body = {
        "fromDate": f"{yil+1}-01-01", "toDate": f"{yil+1}-09-30",
        "disclosureClass": "FR", "subjectList": [kap.SUBJ],
        "mkkMemberOidList": [oid], "inactiveMkkMemberOidList": [],
        "bdkMemberOidList": [], "fromSrc": False, "disclosureIndexList": [],
    }
    rows = kap.http_json("https://www.kap.org.tr/tr/api/disclosure/members/byCriteria", body)
    aday = [d for d in rows if d.get("year") == yil and d.get("ruleType") and "Yıl" in d["ruleType"]]
    aday.sort(key=lambda d: d.get("publishDate") or "")
    return aday


def cek_indeksler(idxler):
    eksik = [i for i in sorted(set(idxler)) if i and not (Path("/tmp/kap_xbrl_satir") / f"{i}.json").exists()]
    print(f"xbrl eksik {len(eksik)}", flush=True)

    def bir(i):
        try:
            ta.xbrl_cek(i)
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
            if n % 25 == 0 or n == len(eksik):
                print(f"  {n}/{len(eksik)} hata {len(hatalar)}", flush=True)
    return hatalar


def panel_yayin(ham):
    return ta.panel_100(ham)


def panel_kanonik(ham):
    return [k for k in panel_yayin(ham) if k not in ("KRDMA", "KRDMB")]


def deg_xi(ham, kod, fn):
    a, b = fn(ham[kod][2022]), fn(ham[kod][2016])
    sa, sb = ham[kod][2022].get("satis"), ham[kod][2016].get("satis")
    if a is None or b is None or not sa or not sb:
        return None
    return (a / sa - b / sb) * 100


def ana():
    ham = ta.ham_yukle()
    liste = list(csv.DictReader((ROOT / "marj_sirket_liste.csv").open(encoding="utf-8")))
    oids = kap.oidler()
    idxler = []
    for kod in set(panel_yayin(ham) + KODLAR32):
        for y, v in kap_yil_oku(kod).items():
            if y in ("2016", "2022", "2023") and v.get("idx"):
                idxler.append(v["idx"])
    print("hazir indeks", len(set(idxler)), flush=True)
    hatalar = cek_indeksler(idxler)

    ornek_2017 = {}
    for kod in ORNEK:
        oid = oids.get(kod)
        if not oid:
            ornek_2017[kod] = {"hata": "oid_yok"}
            continue
        try:
            aday = yillik_aday(oid, 2017)
        except Exception as exc:  # noqa: BLE001
            ornek_2017[kod] = {"hata": f"liste:{exc}"}
            continue
        if not aday:
            ornek_2017[kod] = {"hata": "yillik_bildirim_yok"}
            continue
        kayit = []
        for d in (aday[0], aday[-1]) if len(aday) > 1 else (aday[0],):
            try:
                rec = ta.xbrl_cek(d["disclosureIndex"])
            except Exception as exc:  # noqa: BLE001
                kayit.append({"idx": d["disclosureIndex"], "tarih": d.get("publishDate"), "hata": str(exc)})
                continue
            kayit.append({
                "idx": d["disclosureIndex"],
                "tarih": d.get("publishDate"),
                "n_sutun": rec.get("n_sutun"),
                "nitelik": rec.get("nitelik"),
                "unit": rec.get("unit"),
                "rev_cur": ta.tl(rec["kalem"], "Revenue", "cur", rec["unit"]),
                "rev_prev": ta.tl(rec["kalem"], "Revenue", "prev", rec["unit"]),
                "vo_cur": ta.tl(rec["kalem"], "ProfitLossBeforeTax", "cur", rec["unit"]),
                "vo_prev": ta.tl(rec["kalem"], "ProfitLossBeforeTax", "prev", rec["unit"]),
            })
        ornek_2017[kod] = {"n_bildirim": len(aday), "kayit": kayit}
        print("2017", kod, len(aday), flush=True)

    # CSV
    alan = [
        "kod", "kanonik", "yil", "grup", "ana", "alt", "analiz", "pay_sinifi",
        "tablo_turu", "satis_xi29", "satis_kap_cari", "satis_kap_karsilastirmali",
        "brut_xi29", "paz_xi29", "gy_xi29", "arge_xi29", "faaliyet_xi29",
        "fin_gelir_xi29", "fin_gider_xi29", "vo_xi29",
        "brut_kap", "paz_kap", "gy_kap", "arge_kap", "paz_bos", "arge_bos",
        "fin_gelir_kap", "fin_gider_kap", "vo_kap",
        "cekirdek_xi29", "cekirdek_kap",
        "kaynak_xi29", "kaynak_kap_cari", "kaynak_kap_kars",
    ]
    rows = []
    dolu = defaultdict(int)
    hucre_n = 0
    for s in liste:
        kod = s["kod"]
        kanonik = PAY.get(kod, kod)
        grup = s["grup"]
        analiz = "ana" if grup == "faaliyet" and kod not in ("KRDMA", "KRDMB") else "disi"
        if grup == "holding":
            analiz = "disi_holding"
        elif grup == "finans_disi":
            analiz = "disi_finans"
        elif kod in ("KRDMA", "KRDMB"):
            analiz = "disi_pay_sinifi"
        kaplar = kap_yil_oku(kod) if kod in set(panel_yayin(ham) + KODLAR32) else {}
        for yil in range(2016, 2024):
            h = ham[kod].get(yil) or {}
            ky = kaplar.get(str(yil), {})
            rec = xbrl_oku(ky.get("idx")) if ky.get("rev") is not None else None
            cari = None if ky.get("rev") is None else ky["rev"] * (ky.get("unit") or 1)
            kars = None
            kaynak_kars = "veri yok"
            if str(yil) == "2022":
                k23 = kaplar.get("2023", {})
                if k23.get("rev_prev") is not None:
                    kars = k23["rev_prev"] * (k23.get("unit") or 1)
                    kaynak_kars = f"KAP {k23.get('idx')} onceki sutun, yayim {k23.get('tarih')}, birim {k23.get('unit')}"
            if str(yil) == "2016" and kod in ornek_2017 and ornek_2017[kod].get("kayit"):
                ilk = ornek_2017[kod]["kayit"][0]
                if ilk.get("rev_prev") is not None:
                    kars = ilk["rev_prev"]
                    kaynak_kars = f"KAP 2017 bildirimi {ilk.get('idx')} onceki sutun, yayim {ilk.get('tarih')}"
            if str(yil) == "2023":
                p24 = Path(f"/tmp/kap_2024/{kod}.json")
                if p24.exists():
                    k24 = json.loads(p24.read_text(encoding="utf-8"))
                    if k24.get("rev_prev") is not None:
                        kars = k24["rev_prev"]
                        kaynak_kars = (
                            f"KAP {k24.get('idx')} 2024 bildirimi onceki sutun, "
                            f"yayim {k24.get('tarih')}, birim {k24.get('unit')}"
                        )
            brut = paz = gy = arge = fg = fc = vo = None
            paz_bos = arge_bos = "veri yok"
            cek_kap = None
            if rec:
                u = rec["unit"]
                brut = ta.tl(rec["kalem"], "GrossProfit", "cur", u)
                paz = ta.tl(rec["kalem"], "MarketingExpense", "cur", u)
                gy = ta.tl(rec["kalem"], "AdministrativeExpense", "cur", u)
                arge = ta.tl(rec["kalem"], "ResearchAndDevelopmentExpense", "cur", u)
                fg = ta.tl(rec["kalem"], "FinanceIncome", "cur", u) if "FinanceIncome" in str(rec.get("kalem")) else None
                # FinanceIncome is not in ISTENEN. fin comes from the year json.
                fg = ky.get("fin_gelir")
                fc = ky.get("fin_gider")
                if fg is not None:
                    fg = fg * (ky.get("unit") or 1)
                if fc is not None:
                    fc = fc * (ky.get("unit") or 1)
                vo = ky.get("vo")
                if vo is not None:
                    vo = vo * (ky.get("unit") or 1)
                paz_bos = "evet" if paz is None else "hayir"
                arge_bos = "evet" if arge is None else "hayir"
                cek_kap, _ = cekirdek_siki(rec, "cur")
            elif ky.get("rev") is not None:
                fg = ky.get("fin_gelir")
                fc = ky.get("fin_gider")
                vo = ky.get("vo")
                unit = ky.get("unit") or 1
                if fg is not None:
                    fg *= unit
                if fc is not None:
                    fc *= unit
                if vo is not None:
                    vo *= unit
            tur = None
            if rec and rec.get("nitelik"):
                tur = rec.get("nitelik")
            kaynak_cari = "veri yok"
            if cari is not None:
                kaynak_cari = f"KAP {ky.get('idx')} cari sutun, yayim {ky.get('tarih')}, birim {ky.get('unit')}"
            xi_kaynak = "veri yok"
            if h:
                xi_kaynak = "marj_ham.csv XI_29; 3C satis, 3D brut, 3DA paz, 3DB gy, 3DC arge, 3DF faaliyet, 3HB fin_gelir, 3HC fin_gider, 3I vo; yayim tarihi yok"
            row = {
                "kod": kod,
                "kanonik": kanonik,
                "yil": yil,
                "grup": grup,
                "ana": s.get("ana"),
                "alt": s.get("sektor"),
                "analiz": analiz,
                "pay_sinifi": "Kardemir konsolide pay sinifi" if kod in PAY else "tek",
                "tablo_turu": tur or "veri yok",
                "satis_xi29": h.get("satis"),
                "satis_kap_cari": cari,
                "satis_kap_karsilastirmali": kars,
                "brut_xi29": h.get("brut"),
                "paz_xi29": h.get("paz"),
                "gy_xi29": h.get("gy"),
                "arge_xi29": h.get("arge"),
                "faaliyet_xi29": h.get("faaliyet"),
                "fin_gelir_xi29": h.get("fin_gelir"),
                "fin_gider_xi29": h.get("fin_gider"),
                "vo_xi29": h.get("vergi_oncesi"),
                "brut_kap": brut,
                "paz_kap": paz,
                "gy_kap": gy,
                "arge_kap": arge,
                "paz_bos": paz_bos,
                "arge_bos": arge_bos,
                "fin_gelir_kap": fg,
                "fin_gider_kap": fc,
                "vo_kap": vo,
                "cekirdek_xi29": cekirdek_xi(h) if h else None,
                "cekirdek_kap": cek_kap,
                "kaynak_xi29": xi_kaynak,
                "kaynak_kap_cari": kaynak_cari,
                "kaynak_kap_kars": kaynak_kars,
            }
            rows.append(row)
            for k, v in row.items():
                hucre_n += 1
                if v is not None and v != "veri yok":
                    dolu[k] += 1

    with (ROOT / "temel_veri.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=alan)
        w.writeheader()
        for row in rows:
            w.writerow({k: hucre(row[k]) for k in alan})

    # duyarlilik
    def reel(s16, s22):
        if not s16 or not s22 or s16 <= 0 or s22 <= 0:
            return None
        return (s22 / CPI22) / (s16 / CPI16) - 1

    def kap_satis(kod, yil):
        ky = kap_yil_oku(kod).get(str(yil), {})
        if ky.get("rev") is None:
            return None
        return ky["rev"] * (ky.get("unit") or 1)

    def kap_vo(kod, yil):
        ky = kap_yil_oku(kod).get(str(yil), {})
        if ky.get("vo") is None or ky.get("rev") is None:
            return None
        return ky["vo"] * (ky.get("unit") or 1), ky["rev"] * (ky.get("unit") or 1)

    def kap_fin(kod, yil):
        ky = kap_yil_oku(kod).get(str(yil), {})
        if ky.get("fin_gelir") is None or ky.get("fin_gider") is None or ky.get("rev") is None:
            return None
        u = ky.get("unit") or 1
        return (ky["fin_gelir"] + ky["fin_gider"]) * u, ky["rev"] * u

    def kap_cek(kod, yil):
        ky = kap_yil_oku(kod).get(str(yil), {})
        rec = xbrl_oku(ky.get("idx")) if ky.get("rev") is not None else None
        if not rec:
            return None
        cek, bay = cekirdek_siki(rec, "cur")
        satis = ky["rev"] * (ky.get("unit") or 1)
        if cek is None or not satis:
            return None
        return cek, satis, bay

    def seri(kodlar):
        reel_x, reel_k = [], []
        cek_x, cek_k = [], []
        vo_x, vo_k = [], []
        fin_x, fin_k = [], []
        for kod in kodlar:
            if 2016 not in ham[kod] or 2022 not in ham[kod]:
                continue
            reel_x.append(reel(ham[kod][2016].get("satis"), ham[kod][2022].get("satis")))
            reel_k.append(reel(kap_satis(kod, 2016), kap_satis(kod, 2022)))
            cek_x.append(deg_xi(ham, kod, cekirdek_xi))
            a, b = kap_cek(kod, 2016), kap_cek(kod, 2022)
            if a and b:
                cek_k.append((b[0] / b[1] - a[0] / a[1]) * 100)
            else:
                cek_k.append(None)
            def marj_xi(y, anahtar):
                s = ham[kod][y].get("satis")
                v = ham[kod][y].get(anahtar) if anahtar != "fin" else net_fin(ham[kod][y].get("fin_gelir"), ham[kod][y].get("fin_gider"))
                if anahtar == "vergi_oncesi":
                    v = ham[kod][y].get("vergi_oncesi")
                if not s or v is None:
                    return None
                return v / s
            if marj_xi(2016, "vergi_oncesi") is not None and marj_xi(2022, "vergi_oncesi") is not None:
                vo_x.append((marj_xi(2022, "vergi_oncesi") - marj_xi(2016, "vergi_oncesi")) * 100)
            else:
                vo_x.append(None)
            if marj_xi(2016, "fin") is not None and marj_xi(2022, "fin") is not None:
                fin_x.append((marj_xi(2022, "fin") - marj_xi(2016, "fin")) * 100)
            else:
                fin_x.append(None)
            va, vb = kap_vo(kod, 2016), kap_vo(kod, 2022)
            if va and vb and va[1] and vb[1]:
                vo_k.append((vb[0] / vb[1] - va[0] / va[1]) * 100)
            else:
                vo_k.append(None)
            fa, fb = kap_fin(kod, 2016), kap_fin(kod, 2022)
            if fa and fb and fa[1] and fb[1]:
                fin_k.append((fb[0] / fb[1] - fa[0] / fa[1]) * 100)
            else:
                fin_k.append(None)
        return {
            "reel_xi29": ozet(reel_x),
            "reel_kap_cari": ozet(reel_k),
            "cekirdek_xi29": ozet(cek_x),
            "cekirdek_kap_cari": ozet(cek_k),
            "vo_xi29": ozet(vo_x),
            "vo_kap_cari": ozet(vo_k),
            "fin_xi29": ozet(fin_x),
            "fin_kap_cari": ozet(fin_k),
            "isaret": {
                "reel": isaret(medyan(reel_x), medyan(reel_k)),
                "cekirdek": isaret(medyan(cek_x), medyan(cek_k)),
                "vo": isaret(medyan(vo_x), medyan(vo_k)),
                "fin": isaret(medyan(fin_x), medyan(fin_k)),
            },
        }

    # 2016 eslesme: XI_29 satis vs KAP cari, ve 2017 onceki
    esles = []
    for kod in panel_kanonik(ham) + [k for k in KODLAR32 if k not in panel_kanonik(ham)]:
        b = kap_satis(kod, 2016)
        a = ham[kod][2016].get("satis") if 2016 in ham[kod] else None
        if a and b:
            esles.append({"kod": kod, "xi": a, "kap": b, "oran": a / b, "yakin": abs(a - b) < 1 or abs(a - b) / a < 0.001})
    tarama = []
    for kod, bl in ornek_2017.items():
        b = kap_satis(kod, 2016)
        rec2016 = None
        ky = kap_yil_oku(kod).get("2016", {})
        if ky.get("idx"):
            rec2016 = {"idx": ky.get("idx"), "tarih": ky.get("tarih"), "nitelik": (xbrl_oku(ky["idx"]) or {}).get("nitelik")}
        if bl.get("hata"):
            tarama.append({"kod": kod, "durum": bl["hata"], "kap_2016": b, "kap_2016_kaynak": rec2016})
            continue
        for kay in bl["kayit"]:
            prev = kay.get("rev_prev")
            durum = "veri yok"
            if b and prev:
                if abs(b - prev) < 1 or abs(b - prev) / b < 0.001:
                    durum = "ayni"
                else:
                    durum = "farkli"
            tarama.append({
                "kod": kod,
                "durum": durum,
                "kap_2016": b,
                "kap_2016_kaynak": rec2016,
                "kars_2016": prev,
                "oran": None if not (b and prev) else prev / b,
                "idx_2017": kay.get("idx"),
                "tarih_2017": kay.get("tarih"),
                "n_sutun": kay.get("n_sutun"),
                "nitelik_2017": kay.get("nitelik"),
                "n_bildirim": bl.get("n_bildirim"),
                "vo_2016": (kap_vo(kod, 2016) or [None])[0],
                "vo_kars": kay.get("vo_prev"),
            })

    # bos hucre, analiz evreni
    evren = set(panel_kanonik(ham) + KODLAR32)
    alt = [r for r in rows if r["kod"] in evren]
    def oran_bos(alan_adi, secim):
        xs = [r for r in secim]
        bos = sum(1 for r in xs if r[alan_adi] is None or r[alan_adi] == "veri yok")
        return {"n": len(xs), "bos": bos, "bos_oran": None if not xs else bos / len(xs)}

    sonuc = {
        "tanim": {
            "satis_ana_analiz": "KAP yillik bildirimin cari sutunu (pencere yil+1 Ocak-Eylul, son yillik). XI_29 ayri kolondadir. 2022 XI_29, 2023 bildiriminin karsilastirmali sutunudur. 2023 XI_29, 2024 bildiriminin karsilastirmali sutunudur (/tmp/kap_2024). Hangisi dogru ilan edilmez.",
            "xi29_kaynak": "marj_ham.csv, liste marj_sirket_liste.csv 16 Ekim 2026. Yayim tarihi yok.",
            "marj": {
                "cekirdek": "(3D brut + 3DA paz + 3DB gy + 3DC arge) / 3C. KAP'ta GrossProfit, MarketingExpense, AdministrativeExpense, ResearchAndDevelopmentExpense. Bos satir cekirdege girmez.",
                "faaliyet": "3DF / 3C. Diger faaliyet gelir ve gideri dahildir.",
                "vergi_oncesi": "3I / 3C. KAP ProfitLossBeforeTax / Revenue.",
                "net_finansman": "(3HB + 3HC) / 3C. KAP FinanceIncome + FinanceCosts, gider XI_29'da negatiftir.",
            },
            "pay": "KRDMA ve KRDMB analiz disi. Kanonik KRDMD.",
            "holding_finans": "grup holding ve finans_disi tabloda durur, analiz disi.",
            "cpi": {"2016": CPI16, "2022": CPI22, "seri": "TP.GENENDEKS.T1 yil ortalamasi"},
        },
        "kapsam": {
            "liste_hisse": len(liste),
            "satir": len(rows),
            "yil": "2016-2023",
            "kanonik_ilk100": panel_kanonik(ham),
            "n_kanonik_ilk100": len(panel_kanonik(ham)),
            "n_yayin_ilk100": len(panel_yayin(ham)),
            "tekstil32": KODLAR32,
        },
        "bos": {
            "tum_tablo_satis_kap_cari": oran_bos("satis_kap_cari", rows),
            "tum_tablo_satis_xi29": oran_bos("satis_xi29", rows),
            "evren_satis_kap_cari": oran_bos("satis_kap_cari", alt),
            "evren_satis_xi29": oran_bos("satis_xi29", alt),
            "evren_cekirdek_kap": oran_bos("cekirdek_kap", alt),
            "evren_vo_kap": oran_bos("vo_kap", alt),
            "evren_yil_2022_satis_kap": oran_bos("satis_kap_cari", [r for r in alt if r["yil"] == 2022]),
            "evren_yil_2016_satis_kap": oran_bos("satis_kap_cari", [r for r in alt if r["yil"] == 2016]),
            "evren_yil_2017_2021_satis_kap": oran_bos("satis_kap_cari", [r for r in alt if r["yil"] in (2017, 2018, 2019, 2020, 2021)]),
        },
        "duyarlilik_yayin_100": seri(panel_yayin(ham)),
        "duyarlilik_kanonik": seri(panel_kanonik(ham)),
        "duyarlilik_32": seri(KODLAR32),
        "duyarlilik_32_holding_haric": seri([k for k in KODLAR32 if k not in ("ARSAN", "DERHL", "RALYH")]),
        "xi29_2016_kap_2016": {
            "n": len(esles),
            "yakin": sum(1 for e in esles if e["yakin"]),
            "aykiri": [e for e in esles if not e["yakin"]],
        },
        "tarama_2017": tarama,
        "xbrl_hata": hatalar,
    }
    (ROOT / "temel_veri_ozet.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: sonuc[k] for k in ("duyarlilik_yayin_100", "duyarlilik_kanonik", "duyarlilik_32", "xi29_2016_kap_2016") if k != "aykiri"}, ensure_ascii=False, indent=2)[:4000])
    print("TARAMA")
    for t in tarama:
        print(t["kod"], t["durum"], t.get("oran"), t.get("n_sutun"), t.get("tarih_2017"))


if __name__ == "__main__":
    ana()
