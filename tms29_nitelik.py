"""Gelir tablosu gövdesindeki Finansal Tablo Niteliği alanını okur."""
from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import marj_tur3_kap as kap

KODLAR = (
    "AKSA ARSAN ATEKS BAYRK BLCYT BOSSA BRKO BRMEN DAGI DERHL DERIM DESA "
    "DIRIT ENSRI HATEK ISSEN KORDS KRTEK LUKSK MAVI MEGAP MNDRS RALYH RODRG "
    "RUBNS SASA SKTAS SNPAM SONME SUNTK SUWEN YUNSA"
).split()


def nitelik(idx):
    det = kap.http_json(f"https://www.kap.org.tr/tr/api/notification/attachment-detail/{idx}", timeout=70)
    bodies = det[0].get("disclosureBody") or []
    govde = next((b for b in bodies if "ifrs-full_Revenue|" in b), "")
    m = re.search(r"Finansal Tablo Niteliği(.{0,300})", govde, re.S)
    if not m:
        return "alan_yok"
    text = re.sub(r"<[^>]+>", " ", m.group(0))
    text = re.sub(r"\s+", " ", text)
    m2 = re.search(r"Finansal Tablo Niteliği\s+(.+?)\s+(?:Dipnot|<|$)", text)
    return (m2.group(1).strip() if m2 else text[:80])


def bir(kod, yil, idx):
    try:
        return kod, yil, idx, nitelik(idx), None
    except Exception as exc:  # noqa: BLE001
        return kod, yil, idx, None, str(exc)


def main():
    isler = []
    for kod in KODLAR:
        y22 = json.loads(Path(f"/tmp/kap_tekstil/{kod}.json").read_text())["yillar"]["2022"]
        isler.append((kod, "2022", y22["idx"]))
        y23 = json.loads(Path(f"/tmp/kap_tms29/{kod}.json").read_text())
        for b in y23["bildirimler"]:
            isler.append((kod, "2023", b["idx"]))
    out = []
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = [ex.submit(bir, *x) for x in isler]
        for n, fut in enumerate(as_completed(futs), 1):
            kod, yil, idx, nit, err = fut.result()
            out.append({"kod": kod, "yil": yil, "idx": idx, "nitelik": nit, "hata": err})
            print(f"{n}/{len(isler)} {kod} {yil} {idx} {nit or err}", flush=True)
    Path("/tmp/tms29_nitelik.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
