"""İlk 100 için KAP yıllık yüzü ve finansman dipnotu.

2016 ve 2022, o yılın kendi yıllık raporundaki cari sütundur.
2023 yıllık raporunun önceki sütunu, TMS 29 karşılaştırmalı 2022'dir.
İş Yatırım 2022 sütununun bu karşılaştırmalı tutarla örtüşüp örtüşmediği yazılır.
Dipnotu yüz toplamına kapanmayan firma-yıl medyana alınmaz.
"""
from __future__ import annotations

import json
import re
import subprocess
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from marj_dipnot import blok_ayir

ROOT = Path("/workspace")
CACHE = Path("/tmp/kap_tur3")
CACHE.mkdir(exist_ok=True)
SUBJ = "4028328c594bfdca01594c0af9aa0057"
UA = {"User-Agent": "Mozilla/5.0", "Accept": "application/json", "Content-Type": "application/json",
      "Referer": "https://www.kap.org.tr/tr/bildirim-sorgu"}


def http_json(url, body=None, timeout=50):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8-sig"))


def oidler():
    whl = Path("/tmp/pykapdl/pykap-0.2.0-py3-none-any.whl")
    if not whl.exists():
        raise SystemExit("pykap tekerleği yok")
    raw = zipfile.ZipFile(whl).read("pykap/data/bist_companies_general.json")
    return {c["ticker"]: c["company_id"] for c in json.loads(raw)}


def yillik_bul(oid, yil):
    body = {
        "fromDate": f"{yil+1}-01-01", "toDate": f"{yil+1}-09-30",
        "disclosureClass": "FR", "subjectList": [SUBJ],
        "mkkMemberOidList": [oid], "inactiveMkkMemberOidList": [],
        "bdkMemberOidList": [], "fromSrc": False, "disclosureIndexList": [],
    }
    rows = http_json("https://www.kap.org.tr/tr/api/disclosure/members/byCriteria", body)
    aday = [d for d in rows if d.get("year") == yil and d.get("ruleType") and "Yıl" in d["ruleType"]]
    if not aday:
        return None
    aday.sort(key=lambda d: d.get("publishDate") or "")
    return aday[-1]


def xbrl(idx):
    det = http_json(
        f"https://www.kap.org.tr/tr/api/notification/attachment-detail/{idx}",
        timeout=70,
    )
    item = det[0]
    bodies = item.get("disclosureBody") or []
    html = "\n".join(bodies)
    unit = 1.0
    m = re.search(r"Sunum Para Birimi.*?(1(?:\.0{3})*)\s*TL", html, re.S)
    if m:
        unit = float(m.group(1).replace(".", ""))
    gelir = next((b for b in bodies if "ifrs-full_Revenue|" in b or "Kar veya Zarar Tablosu" in b), "")
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
            "label": lab.group(1) if lab else "",
            "vals": {int(c): float(v) for c, v in vals if v not in ("", "-")},
        })
    cols = sorted({c for r in rows for c in r["vals"]})
    cur = cols[0] if cols else None
    prev = cols[1] if len(cols) > 1 else None

    def al(pred):
        for r in rows:
            if pred(r):
                return r["vals"].get(cur), r["vals"].get(prev), r["label"]
        return None, None, None

    rev, rev_p, _ = al(lambda r: r["concept"].endswith("_Revenue") or r["label"] == "Hasılat")
    fg, fg_p, _ = al(lambda r: r["concept"].endswith("FinanceIncome") or (
        r["label"].startswith("Finansman Gelir") and "ncesi" not in r["label"]))
    fc, fc_p, _ = al(lambda r: r["concept"].endswith("FinanceCosts") or r["label"].startswith("Finansman Gider"))
    vo, vo_p, _ = al(lambda r: "ProfitLossBeforeTax" in r["concept"] or "VERGİ ÖNCESİ" in r["label"].upper())
    pdfs = [a for a in (item.get("attachments") or []) if str(a.get("fileExtension") or "").lower() == "pdf"]
    tr = [a for a in pdfs if "ENG" not in a.get("fileName", "").upper()]
    att = (tr or pdfs or [None])[0]
    return {
        "unit": unit, "rev": rev, "rev_prev": rev_p, "fin_gelir": fg, "fin_gelir_prev": fg_p,
        "fin_gider": fc, "fin_gider_prev": fc_p, "vo": vo, "vo_prev": vo_p,
        "att": att, "n_satir": len(rows),
    }


def pdf_metin(idx, att, kod, yil):
    if not att:
        return None, "ek_yok"
    url = f"https://www.kap.org.tr/tr/api/file/download/{att['objId']}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": f"https://www.kap.org.tr/tr/Bildirim/{idx}"})
    with urllib.request.urlopen(req, timeout=90) as r:
        raw = r.read()
    i = raw.find(b"%PDF")
    if i < 0:
        return None, "pdf_degil"
    path = CACHE / f"{kod}_{yil}.pdf"
    txt = CACHE / f"{kod}_{yil}.txt"
    path.write_bytes(raw[i:])
    subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", str(path), str(txt)], check=False, timeout=60)
    if not txt.exists():
        return None, "pdftotext_yok"
    metin = txt.read_text(encoding="utf-8", errors="replace")
    if len(metin) < 500:
        return metin, "pdf_metin_kisa"
    return metin, None


def firma(kod, oid):
    out = {"kod": kod, "oid": oid, "yillar": {}}
    for yil in (2016, 2022, 2023):
        try:
            bild = yillik_bul(oid, yil)
        except Exception as exc:  # noqa: BLE001
            out["yillar"][str(yil)] = {"hata": f"liste:{exc}"}
            continue
        if not bild:
            out["yillar"][str(yil)] = {"hata": "yillik_bildirim_yok"}
            continue
        idx = bild["disclosureIndex"]
        try:
            yuz = xbrl(idx)
        except Exception as exc:  # noqa: BLE001
            out["yillar"][str(yil)] = {"hata": f"xbrl:{exc}", "idx": idx}
            continue
        rec = {"idx": idx, "tarih": bild.get("publishDate"), **{k: yuz[k] for k in yuz if k != "att"}}
        if yil in (2016, 2022) and yuz.get("fin_gelir") is not None:
            try:
                metin, perr = pdf_metin(idx, yuz["att"], kod, yil)
            except Exception as exc:  # noqa: BLE001
                metin, perr = None, f"pdf:{exc}"
            rec["pdf_hata"] = perr
            if metin:
                rec["gelir"] = blok_ayir(metin, yuz["fin_gelir"], "gelir")
                if yuz.get("fin_gider") is not None:
                    rec["gider"] = blok_ayir(metin, yuz["fin_gider"], "gider")
                for k in ("gelir", "gider"):
                    if k in rec and "satir" in rec[k]:
                        rec[k] = {kk: vv for kk, vv in rec[k].items() if kk != "satir"} | {
                            "n_satir": len(rec[k].get("satir") or [])
                        }
        out["yillar"][str(yil)] = rec
    (CACHE / f"{kod}.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    return kod, {y: out["yillar"].get(str(y), {}).get("hata") or out["yillar"].get(str(y), {}).get("gelir", {}).get("durum") for y in (2016, 2022)}


def main():
    import csv
    from collections import defaultdict
    ham = defaultdict(dict)
    for r in csv.DictReader((ROOT / "marj_ham.csv").open(encoding="utf-8")):
        ham[r["kod"]][int(r["yil"])] = r
    liste = {r["kod"]: r for r in csv.DictReader((ROOT / "marj_sirket_liste.csv").open(encoding="utf-8"))}
    panel = []
    for kod, s in liste.items():
        if s["grup"] != "faaliyet":
            continue
        if all(y in ham[kod] and float(ham[kod][y]["satis"] or 0) > 0 for y in range(2016, 2024)):
            panel.append(kod)
    panel.sort(key=lambda k: float(ham[k][2023]["satis"]), reverse=True)
    ilk = panel[:100]
    oids = oidler()
    isler = []
    yok = []
    for k in ilk:
        if k in oids:
            isler.append((k, oids[k]))
        elif k in ("KRDMA", "KRDMB") and "KRDMD" in oids:
            isler.append((k, oids["KRDMD"]))
        else:
            yok.append(k)
    print("oid yok", yok, "cekilecek", len(isler), flush=True)
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = [ex.submit(firma, k, oid) for k, oid in isler]
        for i, fut in enumerate(as_completed(futs), 1):
            kod, ozet = fut.result()
            print(f"{i}/{len(isler)} {kod} {ozet}", flush=True)
    (ROOT / "marj_tur3_kap_ozet.json").write_text(json.dumps({"yok": yok, "n": len(isler)}, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
