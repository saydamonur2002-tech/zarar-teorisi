"""Stok silimi — TCMB Finansal Hesaplar 2026-I kimden-kime (metin + EVDS pay).

Akış mahsupu (yüzde 42,7) bu dosyaya girmez. Birim: rapor milyar TL (2026-Q1 dönem sonu).

Çalıştırma: python3 stok_silim.py
"""

from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

import pandas as pd

KOK = Path(__file__).resolve().parent
GUNLUK = KOK / "stok_silim_arama_gunlugu.jsonl"
OUT_CSV = KOK / "stok_silim.csv"
OUT_RAPOR = KOK / "STOK_SILIM_RAPOR.md"
OUT_SONUC = KOK / "stok_silim_sonuc.json"
PDF_URL = (
    "https://www.tcmb.gov.tr/wps/wcm/connect/bf500c17-e3d5-40bd-8475-370caca9c6fd/"
    "VII.+Kimden-Kime+Tablolar%C4%B1.pdf?CACHEID=ROOTWORKSPACE-bf500c17-e3d5-40bd-8475-370caca9c6fd-p-TY4sh&MOD=AJPERES"
)
PDF_KOK = KOK / "tcmb_kimden_kime_2026Q1.pdf"
AKIS_ORAN_REF = 0.427  # yalnız H-S kıyası; stok_silim.csv'ye yazılmaz
HS_ESIK = 0.15
FIRMALAR_PDF_URL = (
    "https://www.tcmb.gov.tr/wps/wcm/connect/44363718-828b-4c6a-95e8-066078e93247/"
    "V.+Firmalar+%28Finansal+Olmayan+Kurulu%C5%9Flar%29.pdf"
    "?CACHEID=ROOTWORKSPACE-44363718-828b-4c6a-95e8-066078e93247-p-TY44k&MOD=AJPERES"
)
FIRMALAR_PDF_KOK = KOK / "tcmb_firmalar_2026Q1.pdf"
# Hazne adları: PFK parasal ve finansal kuruluş (banka ayrılmadı); GY genel yönetim;
# repo K (bankacılık dışı finansal) bu dosyada kullanılmaz.
HAZNE_AD = {"F": "finansal olmayan", "H": "hanehalkı", "PFK": "parasal ve finansal", "GY": "genel yönetim", "ROW": "dünyanın geri kalanı"}

ARACLAR = ("kredi", "mevduat", "borclanma_senedi")


def log(obj: dict) -> None:
    with GUNLUK.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def pdf_indir() -> Path | None:
    if PDF_KOK.exists() and PDF_KOK.stat().st_size > 10_000:
        log({"islem": "pdf", "durum": "onbellek", "dosya": PDF_KOK.name})
        return PDF_KOK
    try:
        req = urllib.request.Request(PDF_URL, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=120).read()
        PDF_KOK.write_bytes(data)
        log({"islem": "pdf", "durum": "indi", "url": PDF_URL, "byte": len(data)})
        return PDF_KOK
    except Exception as exc:  # noqa: BLE001
        log({"islem": "pdf", "durum": "hata", "url": PDF_URL, "detay": str(exc)})
        return None


def pdf_metin(path: Path) -> str:
    import pdfplumber

    parts = []
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            parts.append(p.extract_text() or "")
        log({"islem": "pdf_okuma", "sayfa": len(pdf.pages), "tablo_sayisi": sum(len(p.extract_tables() or []) for p in pdf.pages)})
    return "\n".join(parts)


def kenarlar_rapor_metni() -> list[dict]:
    """VII. bölüm metninden sayısı yazılı çiftler (grafik matrisi PDF'te vektör değil)."""
    return [
        {
            "arac": "kredi",
            "alacakli": "PFK",
            "borclu": "F",
            "stok": 18729.0,
            "alinti": "PFK 18.729 milyar TL kredi F'ye",
            "kaynak_url": PDF_URL,
        },
        {
            "arac": "kredi",
            "alacakli": "PFK",
            "borclu": "H",
            "stok": 6772.0,
            "alinti": "PFK 6.772 milyar TL kredi hanehalkına",
            "kaynak_url": PDF_URL,
        },
        {
            "arac": "kredi",
            "alacakli": "ROW",
            "borclu": "F",
            "stok": 6575.0,
            "alinti": "ROW kredi 6.575 milyar TL F kullandı",
            "kaynak_url": PDF_URL,
        },
        {
            "arac": "kredi",
            "alacakli": "ROW",
            "borclu": "PFK",
            "stok": 4033.0,
            "alinti": "ROW kredi 4.033 milyar TL PFK",
            "kaynak_url": PDF_URL,
        },
        {
            "arac": "kredi",
            "alacakli": "ROW",
            "borclu": "GY",
            "stok": 492.0,
            "alinti": "ROW kredi 492 milyar TL genel yönetim",
            "kaynak_url": PDF_URL,
        },
        {
            "arac": "mevduat",
            "alacakli": "H",
            "borclu": "PFK",
            "stok": 15361.0,
            "alinti": "PFK mevduat 15.361 milyar TL hanehalkına ait",
            "kaynak_url": PDF_URL,
        },
        {
            "arac": "mevduat",
            "alacakli": "F",
            "borclu": "PFK",
            "stok": 7195.0,
            "alinti": "PFK mevduat 7.195 milyar TL F'ye ait",
            "kaynak_url": PDF_URL,
        },
        {
            "arac": "mevduat",
            "alacakli": "PFK",
            "borclu": "PFK",
            "stok": 10258.0,
            "alinti": "PFK kendi içi mevduat 10.258 milyar TL",
            "kaynak_url": PDF_URL,
            "karsi_yok": True,
        },
        {
            "arac": "mevduat",
            "alacakli": "PFK",
            "borclu": "ROW",
            "stok": 4606.0,
            "alinti": "ROW mevduat 4.606 milyar TL PFK açtı",
            "kaynak_url": PDF_URL,
        },
        {
            "arac": "mevduat",
            "alacakli": "GY",
            "borclu": "GY",
            "stok": 352.0,
            "alinti": "Genel yönetim mevduat 352 tamamı GY",
            "kaynak_url": PDF_URL,
            "karsi_yok": True,
        },
        {
            "arac": "borclanma_senedi",
            "alacakli": "PFK",
            "borclu": "GY",
            "stok": 10105.0,
            "alinti": "GY senet 10.105 milyar TL PFK elinde",
            "kaynak_url": PDF_URL,
        },
        {
            "arac": "borclanma_senedi",
            "alacakli": "ROW",
            "borclu": "GY",
            "stok": 2639.0,
            "alinti": "GY senet 2.639 milyar TL ROW elinde",
            "kaynak_url": PDF_URL,
        },
    ]


def evds_f_yukumluluk_2026q1() -> dict:
    """F (S.11) yükümlülük stokları — girmeyen kalemler payı (EVDS bin TL → rapor milyar)."""
    ham = KOK / "mahsup_evds_ham.csv"
    if not ham.exists():
        return {}
    df = pd.read_csv(ham)
    df = df[(df.Grup == "bie_finhestnks71011") & (df.Donem == "2026-Q1")]
    keys = {
        "kredi": "F.4.Krediler, Finansal Olmayan",
        "mevduat": "F.2.Para ve Mevduat, Finansal Olmayan",
        "borclanma_senedi": "F.3.Borçlanma Senetleri, Finansal Olmayan",
        "hisse": "F.5.Hisse Senetleri ve Özkaynaklar, Finansal Olmayan",
        "diger_borc": "F.8.Diğer Borçlar, Finansal Olmayan",
    }
    out = {}
    for k, frag in keys.items():
        hit = df[df.Ad.str.contains(frag, na=False) & df.Ad.str.startswith("F.")]
        if not hit.empty:
            out[k] = float(hit.iloc[0].Deger) / 1e6
    if out:
        out["toplam_yukumluluk"] = sum(v for k, v in out.items() if k not in ("toplam_yukumluluk",))
    return out


def rapor_f_yukumluluk_paylari() -> dict:
    """TCMB 2026-I V. Firmalar: yükümlülük 141.474 milyar; pay % (Grafik 20). PDF metninden doğrulanır."""
    sabit = {
        "toplam_yukumluluk_milyar": 141474.0,
        "hisse_pay": 0.486,
        "diger_borc_pay": 0.328,
        "kredi_pay": 0.179,
        "borclanma_senedi_pay": 0.007,
        "kaynak_url": FIRMALAR_PDF_URL,
        "dogrulama": "indirilemedi",
    }
    try:
        if not (FIRMALAR_PDF_KOK.exists() and FIRMALAR_PDF_KOK.stat().st_size > 10_000):
            req = urllib.request.Request(FIRMALAR_PDF_URL, headers={"User-Agent": "Mozilla/5.0"})
            FIRMALAR_PDF_KOK.write_bytes(urllib.request.urlopen(req, timeout=120).read())
        import pdfplumber

        with pdfplumber.open(FIRMALAR_PDF_KOK) as pdf:
            txt = "\n".join(p.extract_text() or "" for p in pdf.pages)
        ok = all(k in txt for k in ("141.474", "48,6", "32,8"))
        sabit["dogrulama"] = "metinde 141.474 / 48,6 / 32,8 bulundu" if ok else "metin eşleşmedi"
        log({"islem": "firmalar_pdf", "dosya": FIRMALAR_PDF_KOK.name, "dogrulama": sabit["dogrulama"]})
    except Exception as exc:  # noqa: BLE001
        log({"islem": "firmalar_pdf", "hata": str(exc)})
    return sabit


def karsi_bacak_bul(kenarlar: list[dict], alacakli: str, borclu: str, arac: str) -> float | None:
    for k in kenarlar:
        if k["alacakli"] == borclu and k["borclu"] == alacakli and k["arac"] == arac:
            return float(k["stok"])
    return None


def satirlar_uret(kenarlar: list[dict], yontem: str) -> list[dict]:
    rows = []
    if yontem == "arac_ayri":
        for k in kenarlar:
            if k.get("karsi_yok"):
                kb = None
                sil = None
            else:
                kb = karsi_bacak_bul(kenarlar, k["alacakli"], k["borclu"], k["arac"])
                sil = min(float(k["stok"]), kb) if kb is not None else None
            net = float(k["stok"]) - sil if sil is not None else None
            rows.append(
                {
                    "arac": k["arac"],
                    "alacakli": k["alacakli"],
                    "borclu": k["borclu"],
                    "stok": k["stok"],
                    "karsi_bacak": kb,
                    "silinen": sil,
                    "net_kalan": net,
                    "yontem": yontem,
                    "kaynak_url": k["kaynak_url"],
                    "alinti": k["alinti"],
                }
            )
        return rows

    # arac_birlesik: sırasız çift bir kez yazılır; silinen = min(bacak_ab, bacak_ba) tek sayım.
    from collections import defaultdict

    fwd: dict[tuple[str, str], float] = defaultdict(float)
    meta: dict[tuple[str, str], str] = {}
    skip_pairs = set()
    for k in kenarlar:
        if k.get("karsi_yok"):
            skip_pairs.add((k["alacakli"], k["borclu"]))
            continue
        key = (k["alacakli"], k["borclu"])
        fwd[key] += float(k["stok"])
        meta[key] = k["alinti"][:60]
    gorulen: set[frozenset[str]] = set()
    for (a, b), st in sorted(fwd.items()):
        if (a, b) in skip_pairs or a == b:
            continue
        pair = frozenset((a, b))
        if pair in gorulen:
            continue
        gorulen.add(pair)
        rev = fwd.get((b, a), 0.0)
        # büyük bacak "stok", küçük bacak "karsi_bacak" olarak tek satır
        if rev >= st:
            a, b, st, rev = b, a, rev, st
        kb = rev if rev > 0 else None
        sil = min(st, rev) if rev > 0 else None
        net = st - sil if sil is not None else None
        rows.append(
            {
                "arac": "birlesik",
                "alacakli": a,
                "borclu": b,
                "stok": st,
                "karsi_bacak": kb,
                "silinen": sil,
                "net_kalan": net,
                "yontem": yontem,
                "kaynak_url": PDF_URL,
                "alinti": meta.get((a, b), meta.get((b, a), "")),
            }
        )
    return rows


def _oran_metin(oran: float | None, sil: float, stok: float) -> str:
    if oran is None or stok <= 0:
        return f"— (skor satırı yok; silinen {sil:.0f} / stok {stok:.0f})"
    return f"{100 * oran:.1f}% ({sil:.0f} / {stok:.0f} milyar TL)"


def hs_etiket(rows_ayri: list[dict], rapor_pay: dict) -> str:
    """H-S yalnız araç ayrı ile. Araç ayrı silinen yoksa test_edilemez; stok_dar koşulu ayrı raporlanır."""
    scored = [
        r
        for r in rows_ayri
        if r["silinen"] is not None
        and not (r["alacakli"] == "PFK" and r["borclu"] == "PFK" and r["arac"] == "mevduat")
    ]
    if not scored:
        return "test_edilemez"
    stok_top = sum(float(r["stok"]) for r in scored)
    sil_top = sum(float(r["silinen"]) for r in scored)
    if stok_top <= 0:
        return "test_edilemez"
    oran = sil_top / stok_top
    if abs(oran - AKIS_ORAN_REF) <= HS_ESIK:
        return "hipotez_duser"
    if oran < AKIS_ORAN_REF - HS_ESIK:
        return "stok_ayri"
    if stok_dar_kosulu(rapor_pay):
        return "stok_dar"
    return "test_edilemez"


def stok_dar_kosulu(rapor_pay: dict) -> bool:
    return (rapor_pay.get("hisse_pay", 0.0) + rapor_pay.get("diger_borc_pay", 0.0)) > 0.5


def main() -> None:
    if GUNLUK.exists():
        GUNLUK.unlink()
    log({"islem": "basla", "donem": "2026-Q1"})

    pdf = pdf_indir()
    if pdf:
        txt = pdf_metin(pdf)
        if "10.258" not in txt:
            log({"islem": "pdf_dogrulama", "uyari": "10.258 metni bulunamadı"})
        if len(re.findall(r"\d+\.\d+\s*milyar", txt, re.I)) < 5:
            log({"islem": "pdf_dogrulama", "uyari": "az sayısal ifade"})
    else:
        log({"islem": "pdf", "not": "metin kenarları PDF olmadan da sabit listeden"})

    kenarlar = kenarlar_rapor_metni()
    log({"islem": "kenar", "kaynak": "VII_metin", "adet": len(kenarlar), "bos_cift": "matris tablosu PDF'te vektör yok"})

    rows = satirlar_uret(kenarlar, "arac_ayri") + satirlar_uret(kenarlar, "arac_birlesik")
    pd.DataFrame(rows).to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    f_yuk = evds_f_yukumluluk_2026q1()
    rapor_pay = rapor_f_yukumluluk_paylari()
    ayri = [r for r in rows if r["yontem"] == "arac_ayri"]
    hs = hs_etiket(ayri, rapor_pay)

    sil_ayri = sum(float(r["silinen"]) for r in ayri if r["silinen"] is not None)
    stok_ayri = sum(float(r["stok"]) for r in ayri if r["silinen"] is not None)
    # Birleşik: sırasız çift tek satır; silinen = min tek sayım; payda = iki bacak brüt (büyük + küçük).
    bir = [r for r in rows if r["yontem"] == "arac_birlesik" and r["silinen"] is not None]
    sil_bir = sum(float(r["silinen"]) for r in bir)
    stok_bir = sum(float(r["stok"]) + float(r["karsi_bacak"]) for r in bir)

    girmeyen_evds = {}
    if f_yuk.get("toplam_yukumluluk"):
        t = f_yuk["toplam_yukumluluk"]
        girmeyen_evds = {
            "hisse_pay": f_yuk.get("hisse", 0) / t,
            "diger_borc_pay": f_yuk.get("diger_borc", 0) / t,
        }
    rapor_disi_pay = rapor_pay["hisse_pay"] + rapor_pay["diger_borc_pay"]

    sonuc = {
        "donem": "2026-Q1",
        "birim": "milyar TL (Finansal Hesaplar raporu)",
        "H-S": hs,
        "H-S_not": "araç ayrı silinen yok; H-S yalnız araç ayrı ile skorlanır; xls gelmeden kapalı",
        "arac_ayri_silinen_milyar": sil_ayri,
        "arac_ayri_silinen_oran": sil_ayri / stok_ayri if stok_ayri else None,
        "arac_birlesik_tekil": {
            "cift_sayisi": len(bir),
            "silinen_milyar": sil_bir,
            "iki_bacak_brut_milyar": stok_bir,
            "silinen_iki_bacak_brut_oran": sil_bir / stok_bir if stok_bir else None,
            "not": "model tercihi; kısmi çiftler; H-S'ye girmez",
        },
        "akis_oran_kiyaslama_disinda": AKIS_ORAN_REF,
        "stok_dar_kosulu_rapor": stok_dar_kosulu(rapor_pay),
        "girmeyen_pay_rapor": {
            "hisse_pay": rapor_pay["hisse_pay"],
            "diger_borc_pay": rapor_pay["diger_borc_pay"],
            "toplam": rapor_disi_pay,
            "yukumluluk_milyar": rapor_pay["toplam_yukumluluk_milyar"],
            "dogrulama": rapor_pay["dogrulama"],
        },
        "girmeyen_pay_evds_ayri_stok": girmeyen_evds,
        "f_yukumluluk_evds_milyar": f_yuk,
        "banka_ayrimi": "banka ayrılmadı (PFK konsolide)",
        "hazne_adlari": HAZNE_AD,
    }
    OUT_SONUC.write_text(json.dumps(sonuc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rapor = f"""# Stok silimi raporu (2026-Q1)

## 1. Yöntem

| Yöntem | Anlam |
| --- | --- |
| **arac_ayri** | Muhasebe: kredi, mevduat, senet ayrı mahsup |
| **arac_birlesik** | Model tercihi: aynı çiftte üç araç tek havuz |

Akış mahsupu (~42,7% brüt servis) bu tabloda **yok**.

## 2. Kaynak sınırı

- PDF: [VII. Kimden-Kime]({PDF_URL}) — matris **grafik**; sayılar metin + alıntı satırları.
- Tam çift matrisi Excel: TCMB Veri Tabloları sayfasında statik link **bulunamadı** (arama günlüğü).
- B haznesi (TCMB ayrılmış banka) bu tabloya **yapıştırılmadı**.

## 3. Özet (yalnız karşı bacaklı satırlar)

- **Araç ayrı** silinen/stok: {_oran_metin(sonuc['arac_ayri_silinen_oran'], sil_ayri, stok_ayri)} — aynı araçta karşı bacak metinde yok (kredi tek yön, mevduat tek yön).
- **Araç birleşik, tekil çift** ({len(bir)} çift): silinen **{sil_bir:.0f}** milyar TL (F–PFK 7.195, H–PFK 6.772, PFK–ROW 4.033; tek sayım); iki bacak brüt {stok_bir:.0f}; oran {_oran_metin(sonuc['arac_birlesik_tekil']['silinen_iki_bacak_brut_oran'], sil_bir, stok_bir)}. Model tercihi; kısmi çiftler; **H-S’ye girmez**.

## 4. H-S

**{hs}** — H-S yalnız araç ayrı ile skorlanır; araç ayrı boş. Akış {100*AKIS_ORAN_REF:.1f}% stok dosyasında yok. Birleşik oran “karışım var/yok” kanıtı değildir.

## 5. Girmeyen kalemler (F yükümlülük)

| Kaynak | Hisse+özk. | Diğer borç | Toplam dışarıda |
| --- | --- | --- | --- |
| TCMB 2026-I V. Firmalar (141.474 milyar) | {100*rapor_pay['hisse_pay']:.1f}% | {100*rapor_pay['diger_borc_pay']:.1f}% | **{100*rapor_disi_pay:.1f}%** |
| EVDS F konsolide stok (ayrı stok, kıyas değil) | {100*girmeyen_evds.get('hisse_pay', 0):.1f}% | {100*girmeyen_evds.get('diger_borc_pay', 0):.1f}% | {100*(girmeyen_evds.get('hisse_pay', 0)+girmeyen_evds.get('diger_borc_pay', 0)):.1f}% |

`stok_dar` koşulu (rapor payı >50%): **{'sağlanıyor' if stok_dar_kosulu(rapor_pay) else 'sağlanmıyor'}**. Etiket yine de yazılmaz: araç ayrı ölçülmeden H-S kapalı. Rapor doğrulaması: {rapor_pay['dogrulama']} ([V. Firmalar]({FIRMALAR_PDF_URL})).

## 5b. Hazne adları

PFK parasal ve finansal kuruluş (banka ayrılmadı); **GY** genel yönetim; repo **K** (bankacılık dışı finansal) bu dosyada kullanılmaz.

## 6. Dosyalar

`stok_silim.csv`, `stok_silim_sonuc.json`, `stok_silim_arama_gunlugu.jsonl`

```bash
python3 stok_silim.py
```
"""
    OUT_RAPOR.write_text(rapor, encoding="utf-8")
    print(rapor)


if __name__ == "__main__":
    main()
