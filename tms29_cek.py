"""2023 yıllık KAP yüzünden karşılaştırmalı 2022 satışını çeker.

İş Yatırım 2022 satışı ile eşleşme, bu dosyada iddia edilmez.
Birden fazla yıllık bildirim varsa hepsi saklanır.
"""
from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import marj_tur3_kap as kap

OUT = Path("/tmp/kap_tms29")
OUT.mkdir(exist_ok=True)
KODLAR = (
    "AKSA ARSAN ATEKS BAYRK BLCYT BOSSA BRKO BRMEN DAGI DERHL DERIM DESA "
    "DIRIT ENSRI HATEK ISSEN KORDS KRTEK LUKSK MAVI MEGAP MNDRS RALYH RODRG "
    "RUBNS SASA SKTAS SNPAM SONME SUNTK SUWEN YUNSA"
).split()


def yilliklar(oid):
    aday = []
    gor = set()
    # Uzun tek aralık KAP'ta 500 döndürür. İki kısa pencere kullanılır.
    for frm, to in (("2024-01-01", "2024-09-30"), ("2024-10-01", "2025-09-30")):
        body = {
            "fromDate": frm,
            "toDate": to,
            "disclosureClass": "FR",
            "subjectList": [kap.SUBJ],
            "mkkMemberOidList": [oid],
            "inactiveMkkMemberOidList": [],
            "bdkMemberOidList": [],
            "fromSrc": False,
            "disclosureIndexList": [],
        }
        rows = kap.http_json("https://www.kap.org.tr/tr/api/disclosure/members/byCriteria", body)
        for d in rows:
            if d.get("year") == 2023 and d.get("ruleType") and "Yıl" in d["ruleType"]:
                if d.get("disclosureIndex") not in gor:
                    gor.add(d["disclosureIndex"])
                    aday.append(d)
    aday.sort(key=lambda d: d.get("publishDate") or "")
    return aday


def tur(html: str) -> str:
    u = html[:8000].lower()
    kons = "konsolide" in u
    bir = "bireysel" in u or "solo" in u
    if kons and not bir:
        return "konsolide"
    if bir and not kons:
        return "bireysel"
    if kons and bir:
        return "ikisi_de_geciyor"
    return "belirlenemiyor"


def bir_bildirim(d):
    idx = d["disclosureIndex"]
    det = kap.http_json(f"https://www.kap.org.tr/tr/api/notification/attachment-detail/{idx}", timeout=70)
    item = det[0]
    bodies = item.get("disclosureBody") or []
    html = "\n".join(bodies)
    yuz = kap.xbrl(idx)
    return {
        "idx": idx,
        "tarih": d.get("publishDate"),
        "tur": tur(html),
        "unit": yuz.get("unit"),
        "rev": yuz.get("rev"),
        "rev_prev": yuz.get("rev_prev"),
        "n_satir": yuz.get("n_satir"),
        "url": f"https://www.kap.org.tr/tr/Bildirim/{idx}",
    }


def firma(kod, oid):
    try:
        ads = yilliklar(oid)
    except Exception as exc:  # noqa: BLE001
        rec = {"kod": kod, "hata": f"liste:{exc}", "bildirimler": []}
        (OUT / f"{kod}.json").write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
        return kod, rec["hata"]
    bildirimler = []
    for d in ads:
        try:
            bildirimler.append(bir_bildirim(d))
        except Exception as exc:  # noqa: BLE001
            bildirimler.append({"idx": d.get("disclosureIndex"), "tarih": d.get("publishDate"), "hata": str(exc)})
    rec = {"kod": kod, "oid": oid, "n": len(bildirimler), "bildirimler": bildirimler}
    (OUT / f"{kod}.json").write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
    ozet = [(b.get("tarih"), b.get("tur"), b.get("rev_prev"), b.get("hata")) for b in bildirimler]
    return kod, ozet


def main():
    oids = kap.oidler()
    isler = []
    for k in KODLAR:
        if k not in oids:
            print("oid yok", k, flush=True)
            continue
        isler.append((k, oids[k]))
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = [ex.submit(firma, k, oid) for k, oid in isler]
        for i, fut in enumerate(as_completed(futs), 1):
            kod, ozet = fut.result()
            print(f"{i}/{len(isler)} {kod} {ozet}", flush=True)


if __name__ == "__main__":
    main()
