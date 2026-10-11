"""TÜİK birincil NACE ağırlıkları (GitHub'daki bülten xls). Uydurma satır yok.

Çalıştırma: python3 nace_tuik_katman.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent
GUNLUK = KOK / "nace_tuik_arama_gunlugu.jsonl"
OUT_AGIRLIK = KOK / "nace_tuik_agirlik.csv"
OUT_BOLUM = KOK / "nace_bolum_donem.csv"
OUT_RAPOR = KOK / "NACE_TUIK_RAPOR.md"
OUT_SONUC = KOK / "nace_tuik_sonuc.json"

YSHI_DOSYA = "Ekonomik faaliyetlere göre temel göstergeler, 2024.xls"
YSHI_URL = "https://data.tuik.gov.tr/Bulten/Index?p=Yillik-Sanayi-ve-Hizmet-Istatistikleri-2024-54051"
YSHI_TABLO = "t2"
YSHI_YIL = 2024
SEKTOR_BIL_URL = "https://data.tuik.gov.tr/Bulten/Index?p=Sektor-Bilancolari-2024-54080"
SEKTOR_BIL_META = (
    "https://www.tcmb.gov.tr/wps/wcm/connect/TR/TCMB+TR/Main+Menu/Istatistikler/"
    "Reel+Sektor+Istatistikleri/Sektor+Bilancolari/"
)

KAPSAM_DISI = frozenset({"A", "K", "O"})
GOSTERGELER = (
    ("girisim", 2),
    ("istihdam", 3),
    ("ciro", 6),
    ("uretim_degeri", 9),
)
PAY_UYUM_ESIK = 0.10
YIL_UYARISI = "2024 faaliyet veya bilanço ağırlığı, 2026-Q1 akışına uygulandı."


def log(obj: dict) -> None:
    with GUNLUK.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def _sayi(x) -> float | None:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return None
    s = str(x).strip().lower()
    if s in ("", "c", "x", "-", "nan"):
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        try:
            return float(s.replace(".", "").replace(",", "."))
        except ValueError:
            return None


def yshi_yolu() -> Path | None:
    p = KOK / YSHI_DOSYA
    if p.exists():
        return p
    for cand in KOK.glob("Ekonomik faaliyetlere*.xls"):
        return cand
    return None


def sektor_bilanco_yolu() -> Path | None:
    oncelik = (
        "*referans*yıl*bilanço*.xls",
        "*referans*yil*bilanc*.xls",
        "*referans*bilanço*.xls",
    )
    for pat in oncelik:
        hits = sorted(KOK.glob(pat))
        if hits:
            return hits[0]
    for cand in sorted(KOK.glob("*.xls")) + sorted(KOK.glob("*.xlsx")):
        ad = cand.name.lower()
        if "bilanço hesapları" in ad or "bilanco hesap" in ad:
            if "referans" in ad or "sekt" in ad:
                return cand
        if "sekt" in ad and ("bilanç" in ad or "bilanc" in ad):
            return cand
    return None


def _referans_yil_bilanco(path: Path) -> list[dict]:
    """TÜİK–TCMB Sektör Bilançoları: NACE sütunlu referans yıl tablosu."""
    x = pd.ExcelFile(path)
    sh = "t2" if "t2" in x.sheet_names else x.sheet_names[0]
    df = pd.read_excel(path, sheet_name=sh, header=None)
    log(
        {
            "kaynak": "sektor_bilanco",
            "dosya": path.name,
            "tablo": sh,
            "format": "referans_yil_nace_sutun",
            "url": SEKTOR_BIL_URL,
        }
    )
    out: list[dict] = []
    nace_row = 4
    for j in range(1, df.shape[1]):
        h = df.iloc[nace_row, j]
        if pd.isna(h):
            continue
        m = re.match(r"^([A-Z])\s*[- ]", str(h).strip())
        if not m:
            continue
        kod = m.group(1).upper()
        ad = str(h).split("\n")[0].strip()
        aktif = _sayi(df.iloc[128, j])
        kisa = _sayi(df.iloc[130, j])
        uzun = _sayi(df.iloc[180, j])
        yab_top = None
        if kisa is not None or uzun is not None:
            yab_top = (kisa or 0.0) + (uzun or 0.0)
        ozk = None
        if aktif is not None and yab_top is not None:
            ozk = aktif - yab_top
        notu = "kapsam_disi" if kod in KAPSAM_DISI else YIL_UYARISI
        for gost, val in (
            ("aktif", aktif),
            ("kisa_vadeli_yabanci_kaynak", kisa),
            ("uzun_vadeli_yabanci_kaynak", uzun),
            ("yabanci_kaynak_toplam", yab_top),
            ("ozkaynak", ozk),
        ):
            if val is None:
                continue
            out.append(
                {
                    "kaynak": "sektor_bilanco",
                    "yil": YSHI_YIL,
                    "nace_kisim": kod,
                    "nace_ad": ad,
                    "gosterge": gost,
                    "deger": val,
                    "pay": None,
                    "dosya_url": SEKTOR_BIL_URL,
                    "tablo_adi": f"{path.name} / {sh}",
                    "not": notu,
                }
            )
    return out


def parse_yshi(path: Path) -> list[dict]:
    df = pd.read_excel(path, sheet_name=YSHI_TABLO, header=None)
    log(
        {
            "kaynak": "YSHI",
            "dosya": path.name,
            "tablo": YSHI_TABLO,
            "satir": len(df),
            "url": YSHI_URL,
        }
    )
    rows: list[dict] = []
    for i in range(len(df)):
        c0, c1 = df.iloc[i, 0], df.iloc[i, 1]
        if pd.isna(c0):
            continue
        s0 = str(c0).strip()
        if not re.match(r"^[A-Z]\s*-", s0):
            continue
        if not str(c1).strip().lower().startswith("toplam"):
            continue
        kod = s0[0].upper()
        ad = s0.split("\n")[0].strip()
        if kod in KAPSAM_DISI:
            for gost, col in GOSTERGELER:
                v = _sayi(df.iloc[i, col])
                rows.append(
                    {
                        "kaynak": "YSHI",
                        "yil": YSHI_YIL,
                        "nace_kisim": kod,
                        "nace_ad": ad,
                        "gosterge": gost,
                        "deger": v,
                        "pay": None,
                        "dosya_url": YSHI_URL,
                        "tablo_adi": f"{path.name} / {YSHI_TABLO}",
                        "not": "kapsam_disi",
                    }
                )
            continue
        for gost, col in GOSTERGELER:
            v = _sayi(df.iloc[i, col])
            rows.append(
                {
                    "kaynak": "YSHI",
                    "yil": YSHI_YIL,
                    "nace_kisim": kod,
                    "nace_ad": ad,
                    "gosterge": gost,
                    "deger": v,
                    "pay": None,
                    "dosya_url": YSHI_URL,
                    "tablo_adi": f"{path.name} / {YSHI_TABLO}",
                    "not": YIL_UYARISI,
                }
            )
    return rows


def parse_sektor_bilanco(path: Path) -> list[dict]:
    """NACE × bilanço kalemleri; referans yıl geniş tablo veya satır bazlı format."""
    ad = path.name.lower()
    if "referans" in ad and ("bilanç" in ad or "bilanc" in ad):
        return _referans_yil_bilanco(path)
    x = pd.ExcelFile(path)
    log({"kaynak": "sektor_bilanco", "dosya": path.name, "sayfa": x.sheet_names, "url": SEKTOR_BIL_URL})
    out: list[dict] = []
    for sh in x.sheet_names:
        df = pd.read_excel(path, sheet_name=sh, header=None)
        header_row = None
        for i in range(min(15, len(df))):
            line = " ".join(str(df.iloc[i, j]) for j in range(min(df.shape[1], 12)) if pd.notna(df.iloc[i, j]))
            if "nace" in line.lower() and ("yabanc" in line.lower() or "kaynak" in line.lower() or "aktif" in line.lower()):
                header_row = i
                break
        if header_row is None:
            continue
        hdr = [str(df.iloc[header_row, j]).lower() if pd.notna(df.iloc[header_row, j]) else "" for j in range(df.shape[1])]
        col_kisim = 0
        cols_yab = [j for j, h in enumerate(hdr) if "kısa" in h and "yabanc" in h]
        cols_yab += [j for j, h in enumerate(hdr) if "uzun" in h and "yabanc" in h]
        cols_yab = list(dict.fromkeys(cols_yab))
        if not cols_yab:
            cols_yab = [j for j, h in enumerate(hdr) if "yabanc" in h and "kaynak" in h]
        for i in range(header_row + 1, len(df)):
            c0 = df.iloc[i, col_kisim]
            if pd.isna(c0):
                continue
            s0 = str(c0).strip()
            m = re.match(r"^([A-Z])\s*-", s0)
            if not m:
                continue
            kod = m.group(1)
            ad = s0.split("\n")[0].strip()
            yab = sum(_sayi(df.iloc[i, j]) or 0.0 for j in cols_yab)
            aktif = None
            for j, h in enumerate(hdr):
                if "aktif" in h and "toplam" in h:
                    aktif = _sayi(df.iloc[i, j])
                    break
            if yab <= 0:
                continue
            gost = "yabanci_kaynak_toplam" if len(cols_yab) > 1 else "yabanci_kaynak"
            out.append(
                {
                    "kaynak": "sektor_bilanco",
                    "yil": YSHI_YIL,
                    "nace_kisim": kod,
                    "nace_ad": ad,
                    "gosterge": gost,
                    "deger": yab,
                    "pay": None,
                    "dosya_url": SEKTOR_BIL_URL,
                    "tablo_adi": f"{path.name} / {sh}",
                    "not": YIL_UYARISI if aktif is None else f"{YIL_UYARISI}; aktif={aktif}",
                }
            )
    return out


def pay_hesapla(rows: list[dict]) -> None:
    by_key: dict[tuple[str, str], list[dict]] = {}
    for r in rows:
        if r.get("not") == "kapsam_disi":
            continue
        if r["deger"] is None:
            continue
        key = (r["kaynak"], r["gosterge"])
        by_key.setdefault(key, []).append(r)
    for grp in by_key.values():
        tot = sum(x["deger"] for x in grp)
        if tot <= 0:
            continue
        for x in grp:
            x["pay"] = float(x["deger"]) / tot


def pay_uyumsuz(isaret: dict[str, float], ciro_pay: dict[str, float]) -> list[str]:
    bad = []
    for kod, cp in ciro_pay.items():
        yp = isaret.get(kod)
        if yp is None:
            continue
        if abs(cp - yp) > PAY_UYUM_ESIK:
            bad.append(kod)
    return bad


def f_hazne_bolum(
    hazne_path: Path,
    yabanci_pay: dict[str, float],
    ciro_pay: dict[str, float],
) -> list[dict]:
    if not yabanci_pay or not hazne_path.exists():
        return []
    hazne = pd.read_csv(hazne_path)
    f = hazne[(hazne["sektor"] == "F") & (hazne["donem"] == "2026-Q1")]
    if f.empty:
        return []
    f = f.iloc[0]
    kodlar = sorted(set(yabanci_pay) | set(ciro_pay))
    tot_pay = sum(yabanci_pay.get(k, 0.0) for k in kodlar if k in yabanci_pay)
    if tot_pay <= 0:
        return []
    rows = []
    for kod in kodlar:
        pay = yabanci_pay.get(kod)
        if pay is None:
            continue
        w = pay / tot_pay
        rows.append(
            {
                "nace_kisim": kod,
                "donem": "2026-Q1",
                "brut_cikis_once": float(f["brut_cikis_once"]) * w,
                "brut_cikis_sonra": None,
                "silinen_oran": None,
                "ciro_pay_2024": ciro_pay.get(kod),
                "yabanci_kaynak_pay_2024": pay,
                "kaynak": (
                    f"S.11 (F) hazne brüt çıkış × Sektör Bilançoları yabancı kaynak payı; {YIL_UYARISI}; "
                    "brut_cikis_sonra boş: bölümde iki yönlü kalem ölçülmedi, hazne silmesi taşınmadı; "
                    "NACE F (inşaat) ile F haznesi aynı değil"
                ),
            }
        )
    return rows


def hn_etiket(bilanco_rows: list[dict], bolum_rows: list[dict]) -> str:
    yab = [
        r
        for r in bilanco_rows
        if r["gosterge"] == "yabanci_kaynak_toplam" and r.get("not") != "kapsam_disi" and r["pay"] is not None
    ]
    if len(yab) < 5:
        return "test_edilemez"
    if not bolum_rows or all(r.get("silinen_oran") is None for r in bolum_rows):
        return "test_edilemez"
    return "hesaplandi"


def main() -> None:
    if GUNLUK.exists():
        GUNLUK.unlink()
    log({"islem": "basla", "github_xls": [p.name for p in KOK.glob("*.xls")]})

    agirlik: list[dict] = []
    yshi_path = yshi_yolu()
    if yshi_path:
        agirlik.extend(parse_yshi(yshi_path))
    else:
        log({"kaynak": "YSHI", "durum": "bulunamadı", "aranan": YSHI_DOSYA, "url": YSHI_URL})

    bil_path = sektor_bilanco_yolu()
    bilanco: list[dict] = []
    if bil_path:
        bilanco = parse_sektor_bilanco(bil_path)
        agirlik.extend(bilanco)
    else:
        log(
            {
                "kaynak": "sektor_bilanco",
                "durum": "bulunamadı",
                "not": "GitHub kökünde Sektör Bilançoları xls yok; bülten denendi",
                "url": SEKTOR_BIL_URL,
                "meta": SEKTOR_BIL_META,
            }
        )

    pay_hesapla(agirlik)
    pd.DataFrame(agirlik).to_csv(OUT_AGIRLIK, index=False, encoding="utf-8-sig")

    ciro_pay = {
        r["nace_kisim"]: r["pay"]
        for r in agirlik
        if r["kaynak"] == "YSHI" and r["gosterge"] == "ciro" and r["pay"] is not None
    }
    yab_pay = {
        r["nace_kisim"]: r["pay"]
        for r in agirlik
        if r["kaynak"] == "sektor_bilanco"
        and r["gosterge"] == "yabanci_kaynak_toplam"
        and r.get("not") != "kapsam_disi"
        and r["pay"] is not None
    }
    uyumsuz = pay_uyumsuz(yab_pay, ciro_pay)
    for r in agirlik:
        if r["nace_kisim"] in uyumsuz and r.get("not") != "kapsam_disi":
            r["not"] = (r.get("not") or "") + "; pay_uyumsuz"

    pd.DataFrame(agirlik).to_csv(OUT_AGIRLIK, index=False, encoding="utf-8-sig")

    hazne_csv = KOK / "mahsup_sektor_donem.csv"
    bolum = f_hazne_bolum(hazne_csv, yab_pay, ciro_pay)
    if not bolum and yshi_path:
        for kod, cp in ciro_pay.items():
            bolum.append(
                {
                    "nace_kisim": kod,
                    "donem": "2026-Q1",
                    "brut_cikis_once": None,
                    "brut_cikis_sonra": None,
                    "silinen_oran": None,
                    "ciro_pay_2024": cp,
                    "yabanci_kaynak_pay_2024": yab_pay.get(kod),
                    "kaynak": f"YSHI 2024 ciro payı; F hazne bölünmedi (Sektör Bilançoları yok); {YIL_UYARISI}",
                }
            )
    pd.DataFrame(bolum).to_csv(OUT_BOLUM, index=False, encoding="utf-8-sig")

    hn = hn_etiket(bilanco, bolum)
    kapsam_disi = sorted({r["nace_kisim"] for r in agirlik if r.get("not") == "kapsam_disi"})

    sonuc = {
        "yshi_dosya": yshi_path.name if yshi_path else None,
        "sektor_bilanco_dosya": bil_path.name if bil_path else None,
        "nace_surumu": "NACE Rev.2 kısım (YSHI tablosu)",
        "H-N": hn,
        "kapsam_disi": kapsam_disi,
        "pay_uyumsuz": uyumsuz,
        "yil_uyarisi": YIL_UYARISI,
        "brut_cikis_sonra": "bos",
    }
    OUT_SONUC.write_text(json.dumps(sonuc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rapor = f"""# TÜİK NACE katman raporu

## 1. İndirilen / kullanılan dosya

| Kaynak | Dosya | Tablo | Yıl | NACE |
| --- | --- | --- | --- | --- |
| YSHİ (faaliyet) | {yshi_path.name if yshi_path else 'bulunamadı'} | `{YSHI_TABLO}` | {YSHI_YIL} | Rev.2 kısım |
| Sektör Bilançoları | {bil_path.name if bil_path else 'bulunamadı (GitHub)'} | `t2` | {YSHI_YIL} | Rev.2 kısım (sütun) |

Bülten: [YSHİ 2024]({YSHI_URL}). Sektör bilanço bülteni: [{SEKTOR_BIL_URL}]({SEKTOR_BIL_URL}).

## 2. Çıktı

- `nace_tuik_agirlik.csv` ({len(agirlik)} satır)
- `nace_bolum_donem.csv` (F hazne brüt çıkışı yalnız yabancı kaynak payıyla bölündü; `brut_cikis_sonra` ve `silinen_oran` boş)

## 3. H-N

**{hn}** — `silinen_oran` ve `brut_cikis_sonra` bölüm bazında boş. F hazne silmesi yapıştırılmadı. F/B hazne yüzdeleri H-N sınavı değil.

## 4. Kapsam dışı / pay uyumsuz

- Kapsam dışı (A,K,O): {', '.join(kapsam_disi) if kapsam_disi else '(tabloda yok)'}
- pay_uyumsuz (ciro vs yabancı kaynak >10 puan): {', '.join(uyumsuz) if uyumsuz else '— (bilanço payı yok)'}

## 5. Arama günlüğü

`nace_tuik_arama_gunlugu.jsonl`

```bash
python3 nace_tuik_katman.py
```
"""
    OUT_RAPOR.write_text(rapor, encoding="utf-8")
    print(rapor)


if __name__ == "__main__":
    main()
