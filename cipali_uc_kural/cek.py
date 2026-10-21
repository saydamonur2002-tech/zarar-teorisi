"""Birincil seriler. EVDS3, anahtarsız. EVDS_API_KEY okunmaz.

Uç: https://evds3.tcmb.gov.tr/igmevdsms-dis
Ön kayıt: ON_KAYIT.md. Bu dosya katsayı üretmez.
"""

from __future__ import annotations

import json
import ssl
import urllib.request
from pathlib import Path

KOK = Path(__file__).resolve().parent
HAM = KOK / "ham"
BASE = "https://evds3.tcmb.gov.tr/igmevdsms-dis"
CTX = ssl.create_default_context()
UA = "Mozilla/5.0 (research; primary-source)"

SERILER = {
    "e24": ("TP.PKAUO.S01.F.U", "avg"),
    "i": ("TP.APIFON4", "avg"),
    "usd": ("TP.DK.USD.S.YTL", "avg"),
    "p_arsiv": ("TP.FG.J0", "avg"),
    "p_2025": ("TP.TUKFIY2025.GENEL", "avg"),
    "rezerv": ("TP.AB.TOPLAM", "last"),
}


def _istek(url: str, body: dict | None = None) -> dict | str:
    veri = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=veri,
        headers={
            "Accept": "application/json,text/html;q=0.8",
            "Content-Type": "application/json",
            "User-Agent": UA,
        },
        method="POST" if body is not None else "GET",
    )
    with urllib.request.urlopen(req, timeout=180, context=CTX) as r:
        ham = r.read()
    metin = ham.decode("utf-8-sig", errors="replace")
    if metin.lstrip().startswith(("{", "[")):
        return json.loads(metin)
    return metin


def evds(kod: str, agg: str, bas: str = "01-01-2011", bit: str = "21-10-2026") -> list[dict]:
    govde = {
        "type": "json",
        "series": kod,
        "aggregationTypes": agg,
        "formulas": "0",
        "startDate": bas,
        "endDate": bit,
        "frequency": "5",
        "decimalSeperator": ".",
        "decimal": "6",
        "dateFormat": "0",
        "lang": "TR",
        "yon": "0",
        "sira": "0",
        "ozelFormuller": [],
        "groupSeperator": False,
        "isRaporSayfasi": False,
    }
    cevap = _istek(f"{BASE}/fe", govde)
    if not isinstance(cevap, dict) or "items" not in cevap:
        raise RuntimeError(f"EVDS3 yanıtı items taşımıyor: {kod}")
    anahtar = kod.replace(".", "_")
    out = []
    for it in cevap["items"]:
        v = it.get(anahtar)
        if v in (None, ""):
            continue
        out.append({"ay": str(it.get("Tarih")), "deger": float(str(v).replace(",", ""))})
    return out


def _faiz_tablosu() -> dict:
    """Bir hafta repo tablosu. İnmezse hüküm faizi APIFON4 kalır."""
    adresler = [
        "https://www.tcmb.gov.tr/wps/wcm/connect/TR/TCMB+TR/Main+Menu/Temel+Faaliyetler/Para+Politikasi/Merkez+Bankasi+Faiz+Oranlari",
        "https://www.tcmb.gov.tr/wps/wcm/connect/EN/TCMB+EN/Main+Menu/Core+Functions/Monetary+Policy/Central+Bank+Interest+Rates",
    ]
    notlar = []
    for url in adresler:
        try:
            metin = _istek(url)
        except Exception as exc:  # noqa: BLE001
            notlar.append({"url": url, "hata": type(exc).__name__})
            continue
        if not isinstance(metin, str):
            notlar.append({"url": url, "hata": "json"})
            continue
        (HAM / "faiz_sayfa.html").write_text(metin[:200000], encoding="utf-8")
        notlar.append({"url": url, "bayt": len(metin), "repo_yok": "1 Hafta" not in metin and "one-week" not in metin.lower() and "1-week" not in metin.lower()})
    return {"bulundu": False, "deneme": notlar}


def _hedef_belgesi() -> dict:
    adresler = [
        "https://www.tcmb.gov.tr/wps/wcm/connect/TR/TCMB+TR/Main+Menu/Temel+Faaliyetler/Para+Politikasi/Fiyat+Istikrari+ve+Enflasyon",
        "https://www.tcmb.gov.tr/wps/wcm/connect/EN/TCMB+EN/Main+Menu/Core+Functions/Monetary+Policy/PRICE+STABILITY+AND+INFLATION",
    ]
    notlar = []
    for url in adresler:
        try:
            metin = _istek(url)
        except Exception as exc:  # noqa: BLE001
            notlar.append({"url": url, "hata": type(exc).__name__})
            continue
        if not isinstance(metin, str):
            notlar.append({"url": url, "hata": "json"})
            continue
        (HAM / "hedef_sayfa.html").write_text(metin[:200000], encoding="utf-8")
        notlar.append({"url": url, "bayt": len(metin)})
    return {"yil_hedefi": {}, "deneme": notlar, "etiket": "DOGRULANMADI"}


def cek() -> dict:
    HAM.mkdir(exist_ok=True)
    paket = {"uc": BASE, "evds3": True, "anahtar": "okunmadi", "seriler": {}}
    for ad, (kod, agg) in SERILER.items():
        rows = evds(kod, agg)
        paket["seriler"][ad] = {"kod": kod, "agg": agg, "n": len(rows), "satir": rows}
        print(ad, kod, len(rows), rows[0]["ay"] if rows else None, rows[-1]["ay"] if rows else None)
    paket["faiz_tablo"] = _faiz_tablosu()
    paket["hedef_belge"] = _hedef_belgesi()
    (HAM / "aylik.json").write_text(json.dumps(paket, ensure_ascii=False), encoding="utf-8")
    return paket


if __name__ == "__main__":
    cek()
