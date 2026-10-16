"""Tekstil ve giyim evreni için KAP yıllık metni ve UN Comtrade HS 50-63.

Dipnot, yalnızca indirilen PDF metninden okunur. Metni olmayan firma-yıl
bilinmeyen kalır. Comtrade miktar alanı bu önizlemede 0 dönerse miktar
yazılmaz. Yurt içi üretim bu betikte çekilmez.
"""
from __future__ import annotations

import csv
import json
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import marj_tur3_kap as kap
from marj_dipnot import blok_ayir

ROOT = Path("/workspace")
KAP_CACHE = Path("/tmp/kap_tekstil")
KAP_CACHE.mkdir(exist_ok=True)
ESKI = Path("/tmp/kap_tur3")
TRADE = Path("/tmp/comtrade_tekstil")
TRADE.mkdir(exist_ok=True)
BEC_PATH = Path(
    "/home/ubuntu/.cursor/projects/workspace/agent-tools/"
    "ea4893c2-a3b1-4944-ac15-af0801a599af.txt"
)
UA = {"User-Agent": "Mozilla/5.0"}


def tek_kodlar():
    liste = list(csv.DictReader((ROOT / "marj_sirket_liste.csv").open(encoding="utf-8")))
    return [r for r in liste if r["ana"] == "Tekstil ve giyim" and r["grup"] == "faaliyet"]


def _pdf_var(kod, yil):
    for klasor in (KAP_CACHE, ESKI):
        txt = klasor / f"{kod}_{yil}.txt"
        if txt.exists() and txt.stat().st_size > 500:
            return txt
    return None


def firma_cek(kod, oid):
    kap.CACHE = KAP_CACHE
    out = {"kod": kod, "oid": oid, "yillar": {}}
    for yil in (2016, 2022):
        if _pdf_var(kod, yil):
            out["yillar"][str(yil)] = {"hata": None, "kaynak": "onbellek"}
            # yüz tutarı yoksa yeniden çekmeyi dene; metin durur
        try:
            bild = kap.yillik_bul(oid, yil)
        except Exception as exc:  # noqa: BLE001
            out["yillar"][str(yil)] = {"hata": f"liste:{exc}"}
            continue
        if not bild:
            out["yillar"][str(yil)] = {"hata": "yillik_bildirim_yok"}
            continue
        idx = bild["disclosureIndex"]
        try:
            yuz = kap.xbrl(idx)
        except Exception as exc:  # noqa: BLE001
            out["yillar"][str(yil)] = {"hata": f"xbrl:{exc}", "idx": idx}
            continue
        rec = {
            "idx": idx,
            "tarih": bild.get("publishDate"),
            **{k: yuz[k] for k in yuz if k != "att"},
        }
        mevcut = _pdf_var(kod, yil)
        if mevcut and mevcut.parent != KAP_CACHE:
            (KAP_CACHE / f"{kod}_{yil}.txt").write_bytes(mevcut.read_bytes())
            rec["pdf_hata"] = None
            rec["metin"] = "kopyalandi"
        else:
            try:
                metin, perr = kap.pdf_metin(idx, yuz.get("att"), kod, yil)
            except Exception as exc:  # noqa: BLE001
                metin, perr = None, f"pdf:{exc}"
            rec["pdf_hata"] = perr
            rec["metin_uzunluk"] = len(metin or "")
        if rec.get("fin_gelir") is not None:
            yol = KAP_CACHE / f"{kod}_{yil}.txt"
            if yol.exists():
                metin = yol.read_text(encoding="utf-8", errors="replace")
                rec["gelir"] = _kirp(blok_ayir(metin, rec["fin_gelir"], "gelir"))
                if rec.get("fin_gider") is not None:
                    rec["gider"] = _kirp(blok_ayir(metin, rec["fin_gider"], "gider"))
        out["yillar"][str(yil)] = rec
    (KAP_CACHE / f"{kod}.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    return kod, {y: out["yillar"].get(str(y), {}).get("hata") or out["yillar"].get(str(y), {}).get("pdf_hata") or "ok" for y in (2016, 2022)}


def _kirp(blok):
    if not isinstance(blok, dict):
        return blok
    return {k: v for k, v in blok.items() if k != "satir"} | {"n_satir": len(blok.get("satir") or [])}


def kap_cek():
    oids = kap.oidler()
    isler = []
    yok = []
    for r in tek_kodlar():
        if r["kod"] in oids:
            isler.append((r["kod"], oids[r["kod"]]))
        else:
            yok.append(r["kod"])
    print("oid yok", yok, "n", len(isler), flush=True)
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = [ex.submit(firma_cek, k, oid) for k, oid in isler]
        for i, fut in enumerate(as_completed(futs), 1):
            kod, ozet = fut.result()
            print(f"{i}/{len(isler)} {kod} {ozet}", flush=True)
    (ROOT / "tekstil_kap_ozet.json").write_text(
        json.dumps({"yok": yok, "n": len(isler)}, ensure_ascii=False), encoding="utf-8"
    )


def _get(url, deneme=5):
    for i in range(deneme):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and i < deneme - 1:
                time.sleep(8 * (i + 1))
                continue
            raise
        except Exception:
            if i == deneme - 1:
                raise
            time.sleep(3 * (i + 1))
    return None


def bec_harita():
    harita = {}
    for line in BEC_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        p = line.strip().lstrip("\ufeff").split(",")
        if len(p) < 3 or not p[0].isdigit() or len(p[0]) < 6:
            continue
        if p[0][:2] not in {str(i) for i in range(50, 64)}:
            continue
        harita.setdefault(p[0], set()).add(p[1])
    return harita


def comtrade_cek():
    harita = bec_harita()
    kodlar = sorted(harita)
    yillar = list(range(2016, 2024))
    fasillar = [str(i) for i in range(50, 64)]
    kayit = []
    for yil in yillar:
        for akis in ("M", "X"):
            url = (
                "https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=792"
                f"&period={yil}&partnerCode=0&flowCode={akis}&customsCode=C00&motCode=0"
                "&cmdCode=" + ",".join(fasillar)
            )
            d = _get(url)
            for row in d.get("data") or []:
                kayit.append(_satir(row))
            print("fasil", yil, akis, d.get("count"), flush=True)
            time.sleep(1.1)
    (TRADE / "fasil.json").write_text(json.dumps(kayit, ensure_ascii=False), encoding="utf-8")

    alt = []
    parca = 40
    for yil in yillar:
        for akis in ("M", "X"):
            for i in range(0, len(kodlar), parca):
                dilim = kodlar[i:i + parca]
                url = (
                    "https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=792"
                    f"&period={yil}&partnerCode=0&flowCode={akis}&customsCode=C00&motCode=0"
                    "&cmdCode=" + ",".join(dilim)
                )
                d = _get(url)
                for row in d.get("data") or []:
                    alt.append(_satir(row))
                print(f"hs6 {yil} {akis} {i} count {d.get('count')}", flush=True)
                time.sleep(1.0)
    (TRADE / "hs6.json").write_text(json.dumps(alt, ensure_ascii=False), encoding="utf-8")
    (TRADE / "bec_harita.json").write_text(
        json.dumps({k: sorted(v) for k, v in harita.items()}, ensure_ascii=False),
        encoding="utf-8",
    )
    print("bitti fasil", len(kayit), "hs6", len(alt), flush=True)


def _satir(row):
    return {
        "yil": int(row["period"]),
        "akis": row["flowCode"],
        "kod": row["cmdCode"],
        "primary": row.get("primaryValue"),
        "cif": row.get("cifvalue"),
        "fob": row.get("fobvalue"),
        "qty": row.get("qty"),
        "netWgt": row.get("netWgt"),
        "isReported": row.get("isReported"),
        "isAggregate": row.get("isAggregate"),
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "kap":
        kap_cek()
    elif len(sys.argv) > 1 and sys.argv[1] == "ticaret":
        comtrade_cek()
    else:
        raise SystemExit("kap veya ticaret")
