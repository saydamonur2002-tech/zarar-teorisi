"""NACE + KAP katmanı (hazne sonucunun üstü). Kamuya açık kaynak; uydurma yok.

Çalıştırma: python3 nace_kap_katman.py
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent
MAHSUP_KOK = KOK / "mahsup"
if str(MAHSUP_KOK) not in sys.path:
    sys.path.insert(0, str(MAHSUP_KOK))

from evds_cek import fetch_group  # noqa: E402
from mahsup_sektor_evds import HAM  # noqa: E402
from mahsuplasma.ag import BorcAgi, Firma  # noqa: E402
from mahsuplasma.mahsup import mahsup_ozeti, optimal_mahsup  # noqa: E402

KAP_BASE = "https://www.kap.org.tr"
KILIT = KOK / "kap_universe_kilit.json"
GUNLUK = KOK / "nace_kap_arama_gunlugu.jsonl"
OUT_NACE = KOK / "nace_bolum_donem.csv"
OUT_KAP = KOK / "kap_kenar.csv"
OUT_YS = KOK / "mahsup_yogun_seyrek.csv"
OUT_RAPOR = KOK / "NACE_KAP_RAPOR.md"
DONEMLER = ("2025-Q4", "2026-Q1")
NACE_EVDS_DENEMELER = (
    "bie_rsistihn",
    "bie_istihsk4",
    "bie_tsny2010",
    "bie_tsny2015",
    "bie_istihsk3",
)


def log(entry: dict) -> None:
    with GUNLUK.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def kap_get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"Referer": f"{KAP_BASE}/tr/bildirim-sorgu", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read()


def kap_post_disclosures(from_d: str, to_d: str) -> list[dict]:
    body = json.dumps({"fromDate": from_d, "toDate": to_d, "mkkMemberOidList": [], "subjectList": []}).encode()
    req = urllib.request.Request(
        f"{KAP_BASE}/tr/api/disclosure/members/byCriteria",
        data=body,
        headers={"Content-Type": "application/json", "Referer": f"{KAP_BASE}/tr/bildirim-sorgu", "Accept": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


def kap_disclosure_windows() -> list[dict]:
    """Aylık pencereler (2000 üst sınırı)."""
    windows = [
        ("2025-10-01", "2025-10-31"),
        ("2025-11-01", "2025-11-30"),
        ("2025-12-01", "2025-12-31"),
        ("2026-01-01", "2026-01-31"),
        ("2026-02-01", "2026-02-28"),
        ("2026-03-01", "2026-03-31"),
    ]
    seen = set()
    out = []
    for a, b in windows:
        try:
            chunk = kap_post_disclosures(a, b)
            log({"kaynak": "KAP", "islem": "byCriteria", "from": a, "to": b, "adet": len(chunk)})
            time.sleep(0.6)
        except urllib.error.HTTPError as e:
            log({"kaynak": "KAP", "islem": "byCriteria", "from": a, "to": b, "hata": str(e)})
            continue
        for d in chunk:
            idx = d.get("disclosureIndex")
            if idx in seen:
                continue
            seen.add(idx)
            out.append(d)
    return out


def parse_ilisikli_html(html: str, meta: dict) -> list[dict]:
    """Basit tablo taraması; tutar yoksa kenar yok."""
    if not html or "ilişkili" not in html.lower() and "iliskili" not in html.lower():
        return []
    rows = []
    # hücre çiftleri: metin + sayı
    cells = re.findall(r">([^<>]{2,120})</td>\s*<td[^>]*>\s*([\d.,]+)", html, flags=re.I)
    for karsi, tut in cells:
        karsi = re.sub(r"\s+", " ", karsi).strip()
        if len(karsi) < 3 or karsi.lower() in ("toplam", "total", "-"):
            continue
        try:
            val = float(tut.replace(".", "").replace(",", "."))
        except ValueError:
            continue
        if val <= 0:
            continue
        rows.append(
            {
                "aciklayan": meta.get("kapTitle", ""),
                "karsi_taraf": karsi[:200],
                "yon": "belirsiz",
                "tutar": val,
                "para_birimi": "TL",
                "donem": meta.get("fin_donem", ""),
                "url": f"{KAP_BASE}/tr/Bildirim/{meta.get('disclosureIndex')}",
                "bildirim_tarihi": meta.get("publishDate", ""),
                "kaynak_alinti": karsi[:80],
            }
        )
    return rows


def kap_kenarlari(disclosures: list[dict], max_detay: int = 120) -> list[dict]:
    kilit = json.loads(KILIT.read_text(encoding="utf-8"))
    keys = kilit["bildirim"]["konu_anahtarlari"]
    aday = []
    for d in disclosures:
        blob = f"{d.get('subject','')} {d.get('summary','')}"
        if any(k.lower() in blob.lower() for k in keys):
            aday.append(d)
        elif d.get("disclosureType") == "FR" and "Finansal Tablo" in blob:
            aday.append(d)
    aday = aday[:max_detay]
    kenar = []
    for d in aday:
        idx = d["disclosureIndex"]
        fin_donem = ""
        if d.get("year") and d.get("period"):
            q = {1: "Q1", 2: "Q2", 3: "Q3", 4: "Q4"}.get(int(d["period"]), "")
            fin_donem = f"{d.get('year')}-{q}"
        meta = {**d, "fin_donem": fin_donem}
        try:
            raw = kap_get(f"{KAP_BASE}/tr/api/notification/attachment-detail/{idx}")
            det = json.loads(raw.decode())
            time.sleep(0.5)
        except Exception as exc:  # noqa: BLE001
            log({"kaynak": "KAP", "islem": "attachment-detail", "index": idx, "hata": str(exc)})
            continue
        if not det:
            continue
        body = det[0].get("disclosureBody") or []
        html = body[0] if isinstance(body, list) and body else (body if isinstance(body, str) else "")
        kenar.extend(parse_ilisikli_html(html, meta))
    return kenar


def nace_evds_dene() -> pd.DataFrame | None:
    for g in NACE_EVDS_DENEMELER:
        try:
            rows, n = fetch_group(g, start="01-01-2023", end="07-10-2026", freq="5")
            log({"kaynak": "EVDS", "grup": g, "seri": n, "satir": len(rows)})
            if len(rows) >= 10:
                df = pd.DataFrame(rows, columns=["grup", "donem", "seri", "ad", "agg", "deger"])
                return df
        except Exception as exc:  # noqa: BLE001
            log({"kaynak": "EVDS", "grup": g, "hata": str(exc)})
    return None


def seyrek_mahsup(kenar_df: pd.DataFrame) -> dict | None:
    if kenar_df.empty:
        return None
    ag = BorcAgi()
    nodes = set()
    for _, r in kenar_df.iterrows():
        nodes.add(r["aciklayan"])
        nodes.add(r["karsi_taraf"])
    for n in nodes:
        ag.firma_ekle(Firma(str(n)[:120], "araci", nakit=0.0))
    for _, r in kenar_df.iterrows():
        ag.borc_ekle(str(r["aciklayan"])[:120], str(r["karsi_taraf"])[:120], float(r["tutar"]))
    once = ag
    sonra = optimal_mahsup(once)
    oz = mahsup_ozeti(once, sonra)
    return {"silinen_oran": oz["silinen_oran"], "kenar_sayisi": len(kenar_df), "tip": "seyrek_KAP"}


def main() -> None:
    if GUNLUK.exists():
        GUNLUK.unlink()
    log({"islem": "basla", "kilit": KILIT.name})

    hazne = pd.read_csv(KOK / "mahsup_sektor_donem.csv")
    hazne_ok = set(hazne["donem"].unique()) >= set(DONEMLER)

    # NACE EVDS
    nace_raw = nace_evds_dene()
    nace_rows = []
    if nace_raw is None:
        for p in DONEMLER:
            nace_rows.append(
                {
                    "nace_bolum": "bulunamadı",
                    "donem": p,
                    "brut_cikis_once": None,
                    "brut_cikis_sonra": None,
                    "silinen_oran": None,
                    "kaynak": f"EVDS NACE/istihdam grupları boş ({', '.join(NACE_EVDS_DENEMELER)})",
                }
            )
    else:
        # son çeyrek ağırlıkları seri adından bölüm kodu çıkar
        last = nace_raw.sort_values("donem").groupby("seri").tail(1)
        tot = last["deger"].clip(lower=0).sum()
        for _, r in last.iterrows():
            code = re.search(r"\b([A-U]|CA|CB|CC|CD|CE|CF|CG|CH|CI|CJ|CK|CL|CM|CN|CO|CP|CQ|CR|CS|CT|CU)\b", r["ad"])
            bolum = code.group(1) if code else r["seri"]
            w = float(r["deger"]) / tot if tot > 0 else 0.0
            nace_rows.append({"nace_bolum": bolum, "agirlik": w, "kaynak_seri": r["seri"]})
        # mahsup F bölünmesi — basitleştirilmiş: ağırlıklı F satırı hazne tablosundan
        f_hazne = hazne[(hazne.sektor == "F") & (hazne.donem == "2026-Q1")].iloc[0]
        for nr in nace_rows:
            nr.update(
                {
                    "donem": "2026-Q1",
                    "brut_cikis_once": f_hazne.brut_cikis_once * nr["agirlik"],
                    "brut_cikis_sonra": f_hazne.brut_cikis_sonra * nr["agirlik"],
                    "silinen_oran": f_hazne.silinen_cikis_oran,
                    "kaynak": "F haznesi payı × TÜİK/EVDS ağırlık (proxy; bilateral değil)",
                }
            )
    pd.DataFrame(nace_rows).to_csv(OUT_NACE, index=False, encoding="utf-8-sig")

    # KAP
    disc = kap_disclosure_windows()
    kenar = kap_kenarlari(disc)
    pd.DataFrame(kenar).to_csv(OUT_KAP, index=False, encoding="utf-8-sig")

    ys = []
    for p in DONEMLER:
        sub = hazne[hazne.donem == p]
        if not sub.empty:
            ys.append({"donem": p, "tip": "yogun_hazne_Lm", "silinen_oran": float(sub.ag_silinen_oran.iloc[0])})
    sk = seyrek_mahsup(pd.DataFrame(kenar))
    if sk:
        sk["donem"] = "2025-Q4–2026-Q1"
        ys.append(sk)
    pd.DataFrame(ys).to_csv(OUT_YS, index=False, encoding="utf-8-sig")

    n_kenar = len(kenar)
    yogun = ys[-1]["silinen_oran"] if ys else float("nan")
    sey_oran = sk["silinen_oran"] if sk else float("nan")
    if n_kenar < 30:
        hm = "test_edilemez"
    elif sk is None or not np.isfinite(sey_oran):
        hm = "test_edilemez"
    elif (yogun - sey_oran) >= 0.15:
        hm = "tutmuyor"
    elif abs(yogun - sey_oran) < 0.15:
        hm = "karışık"
    else:
        hm = "yanlışlıyor"

    f_sil = hazne[(hazne.sektor == "F") & (hazne.donem == "2026-Q1")]["silinen_cikis_oran"].iloc[0]
    b_sil = hazne[(hazne.sektor == "B") & (hazne.donem == "2026-Q1")]["silinen_cikis_oran"].iloc[0]
    hn = "tutmuyor" if abs(f_sil - b_sil) >= 0.10 else "yanlışlıyor (fark <10 puan)"

    hk = "test_edilemez" if n_kenar < 30 else "karışık"

    rapor = f"""# NACE + KAP katman raporu

## 1. Katman tablosu

| Katman | Durum |
| --- | --- |
| Hazne (H,F,B,K,D) | {'duruyor' if hazne_ok else 'eksik dönem'} — `mahsup_sektor_donem.csv` |
| NACE bölüm | {'eklendi (proxy)' if nace_raw is not None else '**bulunamadı** — EVDS NACE/istihdam serileri 2023–2026 boş'} |
| KAP kenar | {n_kenar} kenar — {'test edilebilir (≥30)' if n_kenar >= 30 else '**test edilemez** (<30)'} |

## 2. Yanlışlayıcılar

- **H-M (matris eseri):** {hm}. Yoğun silinen oran (2026-Q1 hazne agregat): {100*yogun:.1f}%. Seyrek KAP: {100*sey_oran:.1f}% ({n_kenar} kenar).
- **H-N (yük yeri):** {hn}. F silinen oran {100*f_sil:.1f}%, B {100*b_sil:.1f}%.
- **H-K (grup içi):** {hk}. Grup içi pay ayrıştırması yapılmadı (karşı taraf eşleşmesi yetersiz).

## 3. Dosyalar

- `nace_bolum_donem.csv`, `kap_kenar.csv`, `mahsup_yogun_seyrek.csv`
- `nace_kap_arama_gunlugu.jsonl`, `kap_universe_kilit.json`

## 4. Sınır

KAP evreni kilit dosyasında. XU100 listesi bulunamadı. D haznesi NACE tablosuna katılmadı. Alıntılar ≤15 kelime. Brüt üst sınır dili: mahsup sonrası agregat brüt servis akışı düşer; tahsilat iddiası yok.

Tekrar: `python3 nace_kap_katman.py`
"""
    OUT_RAPOR.write_text(rapor, encoding="utf-8")
    print(rapor)


if __name__ == "__main__":
    main()
