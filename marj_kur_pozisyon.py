"""İlk 100 ve holdingler için net yabancı para pozisyonu (XI_29 4BE).

4BE dipnottaki döviz cinsi alım değildir. Net parasal döviz pozisyonudur.
Diğer gelir kalemleriyle birlikte hareket testi C içindir; tek başına C'yi kanıtlamaz.
"""

import csv
import json
import math
import statistics
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ISY = "https://www.isyatirim.com.tr/_layouts/15/IsYatirim.Website/Common/Data.aspx/MaliTablo"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode("utf-8-sig"))


def sayi(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def cek(kod):
    out = {}
    for years in ((2023, 2022, 2021, 2020), (2019, 2018, 2017, 2016)):
        qs = "&".join(f"year{i}={y}&period{i}=12" for i, y in enumerate(years, 1))
        url = f"{ISY}?companyCode={kod}&exchange=TRY&financialGroup=XI_29&{qs}"
        data = get(url)
        for it in data.get("value") or []:
            if str(it.get("itemCode") or "").strip() != "4BE":
                continue
            for i, y in enumerate(years, 1):
                out[y] = sayi(it.get(f"value{i}"))
    return out


def ffloat(v):
    if v in (None, ""):
        return None
    return float(v)


def med(xs):
    xs = [x for x in xs if x is not None]
    return None if not xs else statistics.median(xs)


def main():
    firmalar = list(csv.DictReader((ROOT / "marj_firma_ozet.csv").open(encoding="utf-8")))
    hedefler = [r for r in firmalar if r["grup"] == "holding" or r.get("ilk100") == "True"]
    ham = defaultdict(dict)
    for r in csv.DictReader((ROOT / "marj_ham.csv").open(encoding="utf-8")):
        ham[r["kod"]][int(r["yil"])] = r

    fx = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(cek, r["kod"]): r["kod"] for r in hedefler}
        for fut in as_completed(futs):
            kod = futs[fut]
            try:
                fx[kod] = fut.result()
            except Exception as exc:  # noqa: BLE001
                fx[kod] = {"hata": str(exc)}

    sok = [2018, 2021, 2022]
    sakin = [2016, 2017, 2019, 2020]

    def olc(r):
        kod = r["kod"]
        poz = fx.get(kod) or {}
        if "hata" in poz:
            return None
        seri = ham.get(kod) or {}

        def oran(y, alanlar, mutlak_topla=False):
            rec = seri.get(y)
            if not rec:
                return None
            satis = ffloat(rec["satis"])
            if not satis:
                return None
            vals = [ffloat(rec[a]) for a in alanlar]
            if any(v is None for v in vals):
                return None
            return sum(vals) / satis

        def fx_oran(y):
            rec = seri.get(y)
            if not rec or poz.get(y) is None:
                return None
            satis = ffloat(rec["satis"])
            if not satis:
                return None
            return poz[y] / satis

        if any(fx_oran(y) is None for y in sakin + sok):
            return None
        taban = fx_oran(2017)
        if taban is None:
            return None

        def fark(fn):
            a = [fn(y) for y in sok]
            b = [fn(y) for y in sakin]
            if any(v is None for v in a + b):
                return None
            return statistics.fmean(a) - statistics.fmean(b)

        return {
            "kod": kod,
            "grup": r["grup"],
            "ana": r["ana"],
            "fx_satis_2017": taban,
            "kisa": taban < 0,
            "d_net_diger": fark(lambda y: oran(y, ["diger_gelir", "diger_gider"])),
            "d_fin_net": fark(lambda y: oran(y, ["fin_gelir", "fin_gider"])),
            "d_diger_brut": fark(lambda y: oran(y, ["diger_gelir"])),
        }

    olculer = [o for r in hedefler if (o := olc(r))]

    def ozet(ad, grup):
        kisa = [o for o in grup if o["kisa"]]
        uzun = [o for o in grup if not o["kisa"]]
        return {
            "grup": ad,
            "n": len(grup),
            "n_kisa_2017": len(kisa),
            "n_uzun_2017": len(uzun),
            "med_d_net_diger_kisa_pp": None if not kisa else med([o["d_net_diger"] for o in kisa]) * 100,
            "med_d_net_diger_uzun_pp": None if not uzun else med([o["d_net_diger"] for o in uzun]) * 100,
            "med_d_fin_kisa_pp": None if not kisa else med([o["d_fin_net"] for o in kisa]) * 100,
            "med_d_fin_uzun_pp": None if not uzun else med([o["d_fin_net"] for o in uzun]) * 100,
            "med_d_brut_kisa_pp": None if not kisa else med([o["d_diger_brut"] for o in kisa]) * 100,
            "med_d_brut_uzun_pp": None if not uzun else med([o["d_diger_brut"] for o in uzun]) * 100,
        }

    ilk = [o for o in olculer if o["grup"] == "faaliyet"]
    hol = [o for o in olculer if o["grup"] == "holding"]
    sonuc = {
        "tanim": "2017 net yabancı para pozisyonu/satış < 0 ise kısa. Fark = 2018+2021+2022 ortalaması eksi 2016+2017+2019+2020 ortalaması, satışa oran, yüzde puan.",
        "kaynak": "XI_29 kalem 4BE Net Yabancı Para Pozisyonu. İthalat miktarı değil.",
        "ilk100": ozet("ilk100", ilk),
        "holding": ozet("holding", hol),
        "kapsam_disi": len(hedefler) - len(olculer),
    }
    (ROOT / "marj_kur_pozisyon.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(sonuc, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
