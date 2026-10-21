"""Birincil serileri indir. Kurallar: tesvik_cipa/ON_KAYIT.md. EVDS3, anahtarsız."""
import json
import ssl
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
import xml.etree.ElementTree as ET

KOK = Path(__file__).resolve().parent
HAM = KOK / "ham"
HAM.mkdir(exist_ok=True)
CTX = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0 (research; primary-source)", "Accept": "*/*"}


def getir(u, timeout=40, data=None, headers=None):
    h = dict(UA)
    if headers:
        h.update(headers)
    req = urllib.request.Request(u, data=data, headers=h, method="POST" if data else "GET")
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.status, r.geturl(), r.read()


def evds_aylik(kod, bas, son, agg="avg"):
    body = {
        "type": "json", "series": kod, "aggregationTypes": agg, "formulas": "0",
        "startDate": bas, "endDate": son, "frequency": "5",
        "decimalSeperator": ".", "decimal": "4", "dateFormat": "0", "lang": "TR",
        "yon": "0", "sira": "0", "ozelFormuller": [], "groupSeperator": False, "isRaporSayfasi": False,
    }
    _, _, raw = getir(
        "https://evds3.tcmb.gov.tr/igmevdsms-dis/fe",
        data=json.dumps(body).encode(),
        headers={"Accept": "application/json", "Content-Type": "application/json",
                 "Referer": "https://evds3.tcmb.gov.tr/"},
    )
    return json.loads(raw.decode("utf-8-sig"))


def kur_gun(d):
    u = f"https://www.tcmb.gov.tr/kurlar/{d:%Y%m}/{d:%d%m%Y}.xml"
    try:
        _, _, raw = getir(u, timeout=25)
    except Exception as e:
        code = getattr(e, "code", None)
        if code == 404:
            return None
        return {"hata": type(e).__name__}
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return None
    for c in root.iter():
        if c.tag.endswith("Currency") and (c.get("Kod") == "USD" or c.get("CurrencyCode") == "USD"):
            alis = c.findtext("ForexBuying")
            satis = c.findtext("ForexSelling")
            if satis:
                return {"alis": float(alis), "satis": float(satis)}
    return None


def dene(ad, u):
    try:
        status, son, raw = getir(u, timeout=40)
        bas = raw[:180].decode("utf-8", "replace").replace("\n", " ")
        red = "Request Rejected" in bas or "Access Denied" in bas
        return {"ad": ad, "url": u, "son_url": son, "status": status, "bayt": len(raw),
                "engel": red, "bas": bas[:160]}
    except Exception as e:
        return {"ad": ad, "url": u, "hata": f"{type(e).__name__}: {e}"}


def main():
    g = evds_aylik("TP.PKAUO.S01.F.U", "01-01-2013", "21-10-2026", "avg")
    (HAM / "beklenti_ham.json").write_text(json.dumps(g, ensure_ascii=False))
    print("beklenti", len(g.get("items") or []))

    faiz_not = []
    for code in ["bie_ppkfaiz", "bie_apifon", "bie_faizorani", "bie_pyfaiz"]:
        try:
            _, _, raw = getir(
                f"https://evds3.tcmb.gov.tr/igmevdsms-dis/serieList/fe/type=json&code={code}",
                timeout=30,
            )
            ser = json.loads(raw.decode("utf-8-sig"))
            adlar = [(s.get("SERIE_CODE"), s.get("SERIE_NAME")) for s in ser[:8]]
            faiz_not.append({"grup": code, "n": len(ser), "ornek": adlar})
            print("grup", code, len(ser), adlar[:3])
        except Exception as e:
            faiz_not.append({"grup": code, "hata": f"{type(e).__name__}: {e}"})
            print("grup hata", code, type(e).__name__)
    (HAM / "faiz_grup.json").write_text(json.dumps(faiz_not, ensure_ascii=False, indent=1))

    for ad, u in {
        "brl": "https://www.federalreserve.gov/releases/h10/hist/dat00_bz.htm",
        "mxn": "https://www.federalreserve.gov/releases/h10/hist/dat00_mx.htm",
        "zar": "https://www.federalreserve.gov/releases/h10/hist/dat00_sf.htm",
        "inr": "https://www.federalreserve.gov/releases/h10/hist/dat00_in.htm",
    }.items():
        try:
            _, _, raw = getir(u, timeout=60)
            (HAM / f"h10_{ad}.htm").write_bytes(raw)
            print("h10", ad, len(raw))
        except Exception as e:
            print("h10 hata", ad, e)

    kur = {}
    eski = HAM / "kurlar_2016_2021.json"
    if eski.exists():
        kur.update(json.loads(eski.read_text()))
    d0, d1 = datetime(2022, 1, 1), datetime(2026, 10, 21)
    gunler = []
    d = d0
    while d <= d1:
        gunler.append(d)
        d += timedelta(days=1)
    yeni = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(kur_gun, g): g for g in gunler}
        for fut in as_completed(futs):
            g = futs[fut]
            row = fut.result()
            if row and "satis" in row:
                kur[g.strftime("%Y-%m-%d")] = row
                yeni += 1
    (HAM / "kurlar.json").write_text(json.dumps(kur, ensure_ascii=False))
    print("kur", len(kur), "yeni", yeni)

    durum = []
    for ad, u in [
        ("stb_tesvik", "https://www.sanayi.gov.tr/istatistikler/yatirim-tesvik-istatistikleri"),
        ("stb_ana", "https://www.sanayi.gov.tr/"),
        ("hmb_vergi", "https://www.hmb.gov.tr/bumko-vergi-harcamalari"),
        ("hmb_ana", "https://www.hmb.gov.tr/"),
        ("kgf", "https://www.kgf.com.tr/"),
        ("comtrade", "https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=792&period=2019&cmdCode=84&flowCode=M&partnerCode=0"),
        ("tuik", "https://data.tuik.gov.tr/"),
    ]:
        row = dene(ad, u)
        durum.append(row)
        print(ad, row.get("status") or row.get("hata"), "engel" if row.get("engel") else "")
    (HAM / "erisim.json").write_text(json.dumps(durum, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
