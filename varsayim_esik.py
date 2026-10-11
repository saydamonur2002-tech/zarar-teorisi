"""Varsayım eşikleri: kilitli üç kapı için koşullu satırlar. Eşik kapıyı açmaz, seri değildir.

Eşikler önceden kilitli, koşudan sonra değişmez:
  geçiş 0, 1/3, 1 (1/3 RAPOR varsayımı, kaynak değil); vade günü 30, 90, 180; ödenmeyen emir: eşik yok.
Girdi yalnız bu depodaki ölçülmüş sayı: tavan_akis_sonuc.json (2025 itiş, yüzde GSYH), tek_sistem_kopru_sonuc.json
(2025 BDDK net akış − F.4 işlem akımı), vadeli_kalicilik.csv (vade kırılımı, ödenmeyen emir: boş).
Akış yüzdesi, stok tavanı, MY, kalan pay bu dosyaya girmez.

Çıktı: varsayim_esik.csv (kapi, esik, girdi, cikti, birim, durum, not), varsayim_esik_sonuc.json, VARSAYIM_ESIK.md
Durum: varsayim | kosullu | ayrilmadi. `olculdu` olmaz.
"""

from __future__ import annotations

import csv
import json
from fractions import Fraction
from pathlib import Path

KOK = Path(__file__).resolve().parent

GECIS_ESIK = (Fraction(0), Fraction(1, 3), Fraction(1))   # kilitli
VADE_ESIK = (30, 90, 180)                                  # kilitli
IZINLI_DURUM = {"varsayim", "kosullu", "ayrilmadi"}


def _json(p: str) -> dict:
    return json.loads((KOK / p).read_text(encoding="utf-8"))


def girdiler() -> dict:
    ta = _json("tavan_akis_sonuc.json")
    r25 = next(r for r in ta["satirlar"] if r["yil"] == "2025")
    tk = _json("tek_sistem_kopru_sonuc.json")
    ak = next(r for r in tk["mutabakat"] if r["blok"] == "akim" and r["donem"] == "2025" and r["kalem"] == "Net akis ticari")
    vk_rows = list(csv.DictReader((KOK / "vadeli_kalicilik.csv").open(encoding="utf-8-sig")))
    son = vk_rows[-1] if vk_rows else {}
    return {
        "itis_2025_yuzde": r25["oran_akim"],
        "tavan_akis_tavan_dolu": any(r["tavan"] not in (None, "") for r in ta["satirlar"]),
        "bddk_net_akis_2025": ak["tek_sistem_milyar"],
        "f4_akim_2025": ak["evds_milyar"],
        "bosluk_2025": round(ak["tek_sistem_milyar"] - ak["evds_milyar"], 1),
        "vade_kirilim": son.get("vade_kirilim", ""),
        "odenmeyen_emir": son.get("odenmeyen_emir_milyar", ""),
        "ortalama_gun": son.get("ortalama_gun", ""),
        "vade_donem": son.get("donem", ""),
    }


def _esik_str(fr: Fraction) -> str:
    return str(fr.numerator) if fr.denominator == 1 else f"{fr.numerator}/{fr.denominator}"


def satirlar(g: dict) -> list[dict]:
    R: list[dict] = []
    itis = g["itis_2025_yuzde"]
    for e in GECIS_ESIK:
        R.append({
            "kapi": "gecis", "esik": _esik_str(e), "girdi": itis, "cikti": round(itis * float(e), 2), "birim": "puan",
            "durum": "varsayim",
            "not": "itiş 2025 = firma F.4 işlem akımı / GSYH (tavan_akis.csv). Geçiş payı birincil bulunamadı; eşik konuldu, ölçülmedi."
                   + (" 1/3 RAPOR varsayımı, kaynak değil; 2,5 referans notunda." if e == Fraction(1, 3) else ""),
        })
    for v in VADE_ESIK:
        R.append({
            "kapi": "vade_gunu", "esik": v, "girdi": None, "cikti": f"aşılırsa uzar; aşılmazsa uzamaz", "birim": "gün",
            "durum": "kosullu",
            "not": f"MY vade kırılımı '{g['vade_kirilim']}', ortalama gün boş, ödenmeyen emir boş ({g['vade_donem']}, vadeli_kalicilik.csv). "
                   "İki yön de koşullu; ölçüm değil. Seri gelmeden kapı açılmaz.",
        })
    R.append({
        "kapi": "odenmeyen_emir", "esik": None, "girdi": None, "cikti": None, "birim": "milyar TL", "durum": "kosullu",
        "not": "Ölçü yok (Sayıştay/HMB 320 Bütçe Emanetleri bulunamadı, vadeli_kalicilik). Eşik konmaz. 'Yok' satırı durur.",
    })
    R.append({
        "kapi": "bddk_akim", "esik": None, "girdi": g["bddk_net_akis_2025"], "cikti": g["bosluk_2025"], "birim": "milyar TL",
        "durum": "ayrilmadi",
        "not": f"2025 BDDK ticari net akış {g['bddk_net_akis_2025']:,.0f} (stok farkı) − F.4 işlem akımı {g['f4_akim_2025']:,.1f}. "
               "Kur/değerleme ile borç veren kapsamı ayrılmadı; eşikle kapatılmaz.",
    })
    return R


def etiketler(R: list[dict], g: dict) -> dict:
    durumlar = {r["durum"] for r in R}
    hv = "ihlal" if ("olculdu" in durumlar or not durumlar <= IZINLI_DURUM) else "temiz"
    # 2,54 bir sonuç sütununa (tavan_akis.csv tavan) geçti mi?
    hv2 = "siser" if g["tavan_akis_tavan_dolu"] else "ayri"
    return {"H-V": hv, "H-V2": hv2,
            "H-V_not": f"durumlar {sorted(durumlar)}; `olculdu` yok" if hv == "temiz" else "bir satır ölçüm diye yazıldı",
            "H-V2_not": "tavan_akis.csv tavan sütunu boş; 2,54 yalnız `varsayim` satırında ve referans notunda" if hv2 == "ayri"
                        else "tavan sütunu doldurulmuş; 1/3 tavanı kurmuş"}


def md(R: list[dict], g: dict, et: dict) -> str:
    def f(x):
        return "" if x is None else (f"{x:,.2f}" if isinstance(x, float) else str(x))

    s = ["# Varsayım eşikleri", "",
         "Çalıştır: `python3 varsayim_esik.py`. Çıktı: `varsayim_esik.csv`, `varsayim_esik_sonuc.json`.", "",
         "Kilitli üç kapı: vade dilimi yok, ödenmeyen emir yok, geçiş payı yok. Eşik kapıyı açmaz; koşullu satır yazar. "
         "Eşikler önceden kilitli: geçiş 0, 1/3, 1; vade günü 30, 90, 180; ödenmeyen emir eşiksiz. Konan eşik `varsayim`, `olculdu` olmaz.", "",
         f"Girdi: 2025 itiş {g['itis_2025_yuzde']} (yüzde GSYH, `tavan_akis.csv`); 2025 BDDK–akım boşluğu {g['bosluk_2025']:,.1f} milyar TL (`tek_sistem_kopru.csv`).", "",
         "## 1. Geçiş satırları", "", "| Eşik | İtiş (yüzde GSYH) | Tavan (puan) | Durum |", "| --- | ---: | ---: | --- |"]
    for r in R:
        if r["kapi"] == "gecis":
            s.append(f"| {r['esik']} | {f(r['girdi'])} | {f(r['cikti'])} | {r['durum']} |")
    s += ["", "Okuma: geçiş 1/3 varsayılırsa tavan 2,54 puan. Varsayım. RAPOR'un 2,5'i referans notunda; sonuç değil.", "",
          "## 2. Vade satırları", "", "| Eşik (gün) | Çıktı | Durum |", "| --- | --- | --- |"]
    for r in R:
        if r["kapi"] == "vade_gunu":
            s.append(f"| {r['esik']} | {r['cikti']} | {r['durum']} |")
    s += ["", f"Ödenmeyen emir boş; MY vade kırılımı '{g['vade_kirilim']}'. Üç satır da koşullu; ölçüm değil.", "",
          "## 3. Ödenmeyen emir ve BDDK–akım", ""]
    for r in R:
        if r["kapi"] in ("odenmeyen_emir", "bddk_akim"):
            s.append(f"- `{r['kapi']}`: eşik {f(r['esik']) or 'yok'}; çıktı {f(r['cikti']) or 'boş'} {r['birim']}; `{r['durum']}`. {r['not']}")
    s += ["", "## 4. Yanlışlayıcılar", "",
          f"- **H-V** (eşik ölçümü doldurur): `{et['H-V']}`. {et['H-V_not']}.",
          f"- **H-V2** (1/3 tavanı kurar): `{et['H-V2']}`. {et['H-V2_not']}.", "",
          "## Ne denmez", "",
          "- 'Enflasyon 2,5 puan iner' denmez. Geçiş 1/3 varsayılırsa tavan 2,54; varsayım.",
          "- Eşik seri diye kullanılmaz; kapı seri gelmeden açılmaz.",
          "- BDDK–akım boşluğu eşikle kapatılmaz; ayrılmadı."]
    return "\n".join(s) + "\n"


def main() -> None:
    g = girdiler()
    R = satirlar(g)
    et = etiketler(R, g)
    alan = ["kapi", "esik", "girdi", "cikti", "birim", "durum", "not"]
    with (KOK / "varsayim_esik.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=alan)
        w.writeheader()
        for r in R:
            w.writerow({a: ("" if r[a] is None else r[a]) for a in alan})
    (KOK / "varsayim_esik_sonuc.json").write_text(json.dumps({
        "esikler_kilitli": {"gecis": [_esik_str(e) for e in GECIS_ESIK], "vade_gunu": list(VADE_ESIK), "odenmeyen_emir": None},
        "girdi": g, "satirlar": R, **et,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (KOK / "VARSAYIM_ESIK.md").write_text(md(R, g, et), encoding="utf-8")
    print("=== Varsayım eşikleri ===")
    for r in R:
        print(f"{r['kapi']:<16} eşik {str(r['esik'] or ''):<5} girdi {str(r['girdi'] or ''):<8} çıktı {str(r['cikti'] if r['cikti'] is not None else ''):<32} {r['durum']}")
    print(f"H-V {et['H-V']} | H-V2 {et['H-V2']}")


if __name__ == "__main__":
    main()
