"""Faz 6 — Adım 5: kira akışı için band (ölçüm + işaretli varsayım), `adim5.csv` dokunulmadan.

`adim5.csv` kira satırı `olculmedi` kalır: tek sistemin kira kolu birincil ölçüm ister (kiracı hane × ödenen kira). Burada o kol
için hesaplanabilir bir band kurulur ve ayrı dosyaya yazılır; satıra taşınmaz.

Yol A (birim kira × alan × kiracı hane):
  b   = TP.BK.TR Türkiye konut birim kirası (TL/m²/ay, TCMB değerleme raporları, çeyrek)          → ölçüm (kapsam: değerlemesi yapılan konut)
  m²  ∈ {90, 110}                                                                                   → varsayım
  N   = hane sayısı (TÜİK ADNKS 2024; depoda yok, elle)                                             → dis_kaynak_elle
  κ   = kiracı hane oranı ∈ {0,25; 0,30} (TÜİK GYKA ~%27 civarı; depoda yok)                        → varsayım
  Kira_yıllık = b · m² · N · κ · 12
Yol B (depodaki proxy): konut_stok_milyarTL (direnc_yuzdesi: H varlık × 0,25) × kira getirisi 0,035 → varsayım; A ile karşılaştırılır.
Karşılaştırma: HEKİS havuz kirası 20.000 TL/ay (modellendi) / piyasa 100 m² kirası (b × 100).
SFC: kira H(kiracı) → H(ev sahibi) hazne içi transfer; H toplam NL değişmez, Ha/Ho dağılımı değişir. F (kurumsal ev sahibi) payı ölçülmedi.

Çıktı: adim5_kira_ham.csv, adim5_kira.csv, adim5_kira_sonuc.json, ADIM5_KIRA.md.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent
sys.path.insert(0, str(KOK))
from evds_cek import BASE, get_json  # noqa: E402

HAM = KOK / "adim5_kira_ham.csv"
S_BK, S_YKKE = "TP.BK.TR", "TP.YKKE.TR"
M2 = (90.0, 110.0)
KIRACI_ORANI = (0.25, 0.30)
HANE_SAYISI = 26_400_000  # TÜİK ADNKS 2024 hane sayısı; depoda yok, elle; doğrulanmadı
KIRA_GETIRI_PROXY = 0.035  # direnc_yuzdesi.py varsayımı


def _govde(series, agg, freq, start):
    return {"type": "json", "series": "-".join(series), "aggregationTypes": "-".join(agg), "formulas": "-".join("0" for _ in series),
            "startDate": start, "endDate": "10-10-2026", "frequency": freq, "decimalSeperator": ".", "decimal": "4", "dateFormat": "0",
            "lang": "TR", "yon": "0", "sira": "0", "ozelFormuller": [], "groupSeperator": False, "isRaporSayfasi": False}


def _cek(series, agg, freq, start) -> dict[str, float]:
    out = {}
    for it in get_json(f"{BASE}/fe", _govde([series], [agg], freq, start))["items"]:
        v = it.get(series.replace(".", "_"))
        if v not in (None, ""):
            out[str(it["Tarih"])] = float(str(v).replace(",", ""))
    return out


def veri() -> dict[str, dict[str, float]]:
    try:
        bk = _cek(S_BK, "avg", "6", "01-01-2018")
        yk = _cek(S_YKKE, "avg", "5", "01-01-2018")
    except Exception as exc:  # noqa: BLE001
        if not HAM.exists():
            raise
        print("EVDS erişilemedi, önbellek:", exc)
        q: dict[str, dict[str, float]] = {}
        for r in csv.DictReader(HAM.open(encoding="utf-8-sig")):
            q.setdefault(r["seri"], {})[r["donem"]] = float(r["deger"])
        return q
    q = {S_BK: bk, S_YKKE: yk}
    with HAM.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh); w.writerow(["seri", "donem", "deger"])
        for s, d in q.items():
            for k in sorted(d):
                w.writerow([s, k, f"{d[k]:.4f}"])
    return q


def _yoy(d: dict[str, float], son: str, aylik: bool) -> float | None:
    if aylik:
        y, m = son.split("-"); onceki = f"{int(y) - 1}-{m}"
    else:
        y, qq = son.split("-Q"); onceki = f"{int(y) - 1}-Q{qq}"
    return None if onceki not in d else d[son] / d[onceki] - 1


def main() -> dict:
    q = veri()
    bk, yk = q[S_BK], q[S_YKKE]
    son_bk, son_yk = max(bk), max(yk)
    b = bk[son_bk]
    hek = next(r for r in csv.DictReader((KOK / "diger_repo_kopru.csv").open(encoding="utf-8-sig"))
               if r["repo"] == "hekis-model" and r["nesne"].startswith("kira akışı: havuz"))
    hekis_tl_ay = float(hek["deger"])
    konut_stok = json.loads((KOK / "direnc_yuzdesi_sonuc.json").read_text(encoding="utf-8"))
    def _bul(o):
        if isinstance(o, dict):
            if "konut_stok_milyarTL" in o:
                return float(o["konut_stok_milyarTL"])
            for v in o.values():
                r = _bul(v)
                if r is not None:
                    return r
        return None
    konut_stok_milyar = _bul(konut_stok)

    satirlar = []
    for m2 in M2:
        for kap in KIRACI_ORANI:
            yillik = b * m2 * HANE_SAYISI * kap * 12 / 1e9
            satirlar.append({"yol": "A", "birim_kira_tl_m2_ay": b, "donem": son_bk, "m2": m2, "hane_sayisi": HANE_SAYISI, "kiraci_orani": kap,
                             "kiraci_hane": int(HANE_SAYISI * kap), "aylik_kira_tl": round(b * m2), "kira_yillik_milyar": round(yillik, 1),
                             "durum": "band_varsayim", "etiket": "b ölçüm; m² varsayım; N dis_kaynak_elle; κ varsayım"})
    a_min, a_max = min(s["kira_yillik_milyar"] for s in satirlar), max(s["kira_yillik_milyar"] for s in satirlar)
    yol_b = konut_stok_milyar * KIRA_GETIRI_PROXY if konut_stok_milyar else None
    satirlar.append({"yol": "B", "donem": "2026-Q1", "kira_yillik_milyar": None if yol_b is None else round(yol_b, 1), "durum": "varsayim_proxy",
                     "etiket": f"konut_stok {konut_stok_milyar} (H varlık × 0,25) × {KIRA_GETIRI_PROXY}; direnc_yuzdesi proxy"})
    piyasa_100 = b * 100
    satirlar.append({"yol": "karsilastirma", "donem": son_bk, "aylik_kira_tl": round(piyasa_100), "durum": "karsilastirma",
                     "etiket": f"HEKİS havuz kirası {hekis_tl_ay:,.0f} TL/ay / piyasa 100 m² {piyasa_100:,.0f} TL/ay = {hekis_tl_ay / piyasa_100:.2f}"})
    alan = ["yol", "birim_kira_tl_m2_ay", "donem", "m2", "hane_sayisi", "kiraci_orani", "kiraci_hane", "aylik_kira_tl", "kira_yillik_milyar", "durum", "etiket"]
    with (KOK / "adim5_kira.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=alan); w.writeheader()
        for s in satirlar:
            w.writerow({a: ("" if s.get(a) is None else s.get(a)) for a in alan})

    yoy_bk, yoy_yk = _yoy(bk, son_bk, False), _yoy(yk, son_yk, True)
    sonuc = {"faz": 6, "adim": 5, "adim5_csv": "yazilmadi; kira satiri olculmedi kalir",
             "birim_kira": {"seri": S_BK, "donem": son_bk, "tl_m2_ay": b, "yoy": None if yoy_bk is None else round(yoy_bk, 4), "durum": "olcum",
                            "kapsam": "değerlemesi yapılan konutlar (kredili alım ağırlıklı); tüm kiralık stok değil"},
             "yeni_kiraci_endeksi": {"seri": S_YKKE, "donem": son_yk, "deger": yk[son_yk], "yoy": None if yoy_yk is None else round(yoy_yk, 4), "durum": "olcum"},
             "yol_A_band_milyar": [a_min, a_max], "yol_B_proxy_milyar": None if yol_b is None else round(yol_b, 1),
             "hekis_bolu_piyasa_100m2": round(hekis_tl_ay / piyasa_100, 3), "hane_sayisi": HANE_SAYISI, "m2": list(M2), "kiraci_orani": list(KIRACI_ORANI),
             "sfc": "H içi transfer (kiracı → ev sahibi); H toplam NL 0; Ha/Ho dağılımı; F kurumsal ev sahibi payı ölçülmedi",
             "etiketler": {"b": "olcum", "m2": "varsayim", "N": "dis_kaynak_elle (doğrulanmadı)", "kiraci_orani": "varsayim", "yol_B": "varsayim_proxy"}}
    (KOK / "adim5_kira_sonuc.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    f = lambda x, n=1: "" if x is None else f"{x:,.{n}f}"
    md = ["# Faz 6 — Adım 5: kira akışı bandı (satır `olculmedi` kalır)", "",
          "Çalıştır: `python3 adim5_kira.py`. Çıktı: `adim5_kira_ham.csv`, `adim5_kira.csv`, `adim5_kira_sonuc.json`.", "",
          "`adim5.csv` kira satırı `olculmedi`; bu dosya onu doldurmaz. Kol için hesaplanabilir band burada, her girdi etiketli.", "",
          "## Ölçüm", "",
          f"- Birim kira {S_BK} {son_bk}: **{b:.2f} TL/m²/ay**; yıllık değişim {f(None if yoy_bk is None else yoy_bk * 100)}%. Kapsam: değerlemesi yapılan konutlar.",
          f"- Yeni kiracı kira endeksi {S_YKKE} {son_yk}: {yk[son_yk]:.2f}; yıllık {f(None if yoy_yk is None else yoy_yk * 100)}%.", "",
          "## Yol A: b × m² × N × κ × 12 (milyar TL/yıl)", "",
          "| m² | κ | kiracı hane | aylık kira TL | yıllık milyar |", "| --- | --- | --- | --- | --- |"]
    md += [f"| {s['m2']:.0f} | {s['kiraci_orani']} | {s['kiraci_hane']:,} | {s['aylik_kira_tl']:,} | {f(s['kira_yillik_milyar'])} |" for s in satirlar if s["yol"] == "A"]
    md += ["", f"- Band **[{f(a_min)}, {f(a_max)}] milyar TL/yıl**. N = {HANE_SAYISI:,} hane (`dis_kaynak_elle`, doğrulanmadı); κ, m² varsayım.", "",
           "## Yol B: depodaki proxy", "",
           f"- konut_stok {f(konut_stok_milyar)} milyar (H varlık × 0,25, direnc_yuzdesi) × {KIRA_GETIRI_PROXY} = **{f(yol_b)} milyar/yıl**. "
           "Yol A'nın çok altında: proxy finansal varlık payıdır, konut serveti değil. İki yol toplanmaz; A ölçüme yakın, B varsayım.", "",
           "## HEKİS ile karşılaştırma", "",
           f"- HEKİS havuz kirası {hekis_tl_ay:,.0f} TL/ay (`modellendi`) / piyasa 100 m² {piyasa_100:,.0f} TL/ay = **{hekis_tl_ay / piyasa_100:.2f}**. Oran; eşitlenmez.", "",
           "## SFC", "", f"- {sonuc['sfc']}.", "",
           "## Ne denmez", "",
           "- 'Kira ölçüldü' denmez; satır `olculmedi`. Band: b ölçüm, geri kalanı varsayım/elle.",
           "- 'HEKİS döngüyü kırdı' denmez; oran karşılaştırmadır.", ""]
    (KOK / "ADIM5_KIRA.md").write_text("\n".join(md), encoding="utf-8")
    print(f"birim kira {son_bk} {b:.2f} TL/m²/ay | yol A band [{a_min:,.1f}, {a_max:,.1f}] milyar | yol B {yol_b} | HEKİS/piyasa {hekis_tl_ay / piyasa_100:.2f}")
    return sonuc


if __name__ == "__main__":
    main()
