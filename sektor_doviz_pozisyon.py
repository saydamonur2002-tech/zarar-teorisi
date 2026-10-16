"""Sektör bilançosunda döviz kırılımı var mı. Kurallar SEKTOR_DOVIZ_ONKAYIT.md.

Kırılım yoksa net pozisyon, özkaynak oranı ve kur şoku yazılmaz.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

KOK = Path(__file__).resolve().parent
XLS = KOK / "Ekonomik faaliyetlere ve yıllara göre firmaların  bilanço hesapları .xls"
ESIK_KIRILGAN = 0.05
ESIK_YOGUNLASMA = 0.50


def main() -> None:
    df = pd.read_excel(XLS, sheet_name="t6", header=None)
    metin = "\n".join(df.astype(str).fillna("").values.ravel())
    kirilim_kelime = {
        k: metin.lower().count(k) for k in ("döviz", "doviz", "yabancı para", "foreign currency")
    }
    kirilim_var = any(v > 0 for v in kirilim_kelime.values())
    yillar = [int(x) for x in df.iloc[3, 2:].tolist() if pd.notna(x)]
    sektorler = []
    for s in df.iloc[:, 0].dropna().astype(str).unique():
        if s[:1] in list("ABCDEFGHIJKLMNOPQRST") and "-" in s[:4]:
            sektorler.append(s.split("\n")[0].strip())
    birim = None
    for v in df.iloc[2].tolist():
        if isinstance(v, str) and "Bin TL" in v:
            birim = v.strip()
    sonuc = {
        "kaynak": "TÜİK-TCMB, Sektör Bilançoları İstatistikleri, 2024",
        "dosya": XLS.name,
        "sayfa": "t6",
        "tablo": "Ekonomik faaliyetlere ve yıllara göre firmaların bilanço hesapları, 2009-2024",
        "birim": birim,
        "yillar": yillar,
        "sektorler": sektorler,
        "dosyada_olmayan": ["K finansal ve sigorta", "O kamu yönetimi", "bankalar ayrı kurum", "hanehalkı", "TCMB", "genel yönetim"],
        "doviz_kirilimi": "var" if kirilim_var else "yok",
        "kelime_sayimi": kirilim_kelime,
        "ozkaynak_satiri": "V-Öz kaynaklar",
        "esik_kirilganlik": ESIK_KIRILGAN,
        "esik_yogunlasma_ilk3": ESIK_YOGUNLASMA,
        "S1": "belirlenemiyor",
        "S2": "belirlenemiyor",
        "S3": "belirlenemiyor",
        "S4": "belirlenemiyor",
        "S5": "belirlenemiyor",
        "altin_mevduat": "beklemede",
        "pozisyon_yazildi": False,
    }
    (KOK / "sektor_doviz_pozisyon_sonuc.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(sonuc["doviz_kirilimi"], len(sektorler), yillar[0], yillar[-1], birim)


if __name__ == "__main__":
    main()
