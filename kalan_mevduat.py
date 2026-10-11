"""Kalan mevduat payı: VF.2 (para ve mevduat varlığı) içinde merkezi yönetim dışı sektörlerin payı.

Payda iki türlü: (a) bütün = H + F + GY + PFK + ROW (MY, GY'nin içindedir); (b) yalnız H + F + GY.
Konsolide olmayan EVDS grupları; konsolide 71011 kullanılmaz. Yüzde 70 hesaplanır, varsayılmaz.
Akış %42,7, stok tavanı, MY 2.933,6 ve vadeli sıçrama bu teste girmez; MY sonucu kalana yapıştırılmaz.
Birim milyar TL, dönem sonu. Boş hücre boş kalır.
Çıktı: kalan_mevduat.csv, kalan_mevduat_sonuc.json, KALAN_MEVDUAT.md
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from evds_cek import BASE, get_json

KOK = Path(__file__).resolve().parent
DONEMLER = ("2025-Q2", "2025-Q3", "2026-Q1")
URL = "https://evds3.tcmb.gov.tr/tumSeriler"
URL_KIMDEN = ("https://www.tcmb.gov.tr/wps/wcm/connect/bf500c17-e3d5-40bd-8475-370caca9c6fd/VII.+Kimden-Kime+Tablolar%C4%B1.pdf"
              "?CACHEID=ROOTWORKSPACE-bf500c17-e3d5-40bd-8475-370caca9c6fd-p-TY4sh&MOD=AJPERES")
SEKTOR = {"H": "14", "F": "11", "GY": "13", "MY": "1311", "PFK": "12T", "ROW": "2"}
AD = {"H": "Hane", "F": "Firmalar", "GY": "Genel yönetim", "MY": "Merkezi yönetim", "PFK": "Parasal ve finansal kuruluşlar", "ROW": "Dünyanın geri kalanı"}
EK = {"HHKAOK": "15", "S12": "12", "S1": "1"}  # payda dışı, not için
# Kimden-kime VII (2026-Q1) metin rakamı, stok_silim.csv satırları; başka dönem metni yok.
KIMDEN_KIME = {"2026-Q1": {"H": 15361.0, "F": 7195.0}}
ESIK_70 = 0.70
BIRLIKTE_TOL = 0.10  # oransal değişim farkı eşiği (mutlak, pay cinsinden)


def _fetch(series: list[str]) -> dict[str, dict[str, float]]:
    body = {"type": "json", "series": "-".join(series), "aggregationTypes": "-".join("last" for _ in series),
            "formulas": "-".join("0" for _ in series), "startDate": "01-04-2025", "endDate": "10-10-2026", "frequency": "6",
            "decimalSeperator": ".", "decimal": "4", "dateFormat": "0", "lang": "TR", "yon": "0", "sira": "0",
            "ozelFormuller": [], "groupSeperator": False, "isRaporSayfasi": False}
    out: dict[str, dict[str, float]] = {}
    for it in get_json(f"{BASE}/fe", body)["items"]:
        for s in series:
            v = it.get(s.replace(".", "_"))
            if v not in (None, ""):
                out.setdefault(str(it["Tarih"]), {})[s] = float(str(v).replace(",", "")) / 1e6
    return out


def seri(kod: str, zp: int) -> str:
    return f"TP.FINHESTNKS{kod}.ZP{zp}"


def cek() -> dict:
    kodlar = list(SEKTOR.values()) + list(EK.values())
    q = _fetch([seri(k, z) for k in kodlar for z in (5, 7, 8)])
    veri = {}
    for d in DONEMLER:
        row = {}
        for s, k in {**SEKTOR, **EK}.items():
            row[s] = {"vf2": q.get(d, {}).get(seri(k, 5)), "vadesiz": q.get(d, {}).get(seri(k, 7)), "vadeli": q.get(d, {}).get(seri(k, 8))}
        veri[d] = row
    return veri


def r1(x):
    return None if x is None else round(x, 1)


def r3(x):
    return None if x is None else round(x, 3)


def paylar(veri: dict) -> tuple[list[dict], dict]:
    rows, ozet = [], {}
    for d, v in veri.items():
        if any(v[s]["vf2"] is None for s in SEKTOR):
            ozet[d] = {"payda": "kurulamadı", "eksik": [s for s in SEKTOR if v[s]["vf2"] is None]}
            continue
        butun = sum(v[s]["vf2"] for s in ("H", "F", "GY", "PFK", "ROW"))
        hfg = sum(v[s]["vf2"] for s in ("H", "F", "GY"))
        my = v["MY"]["vf2"]
        for s in SEKTOR:
            x = v[s]
            rows.append({"donem": d, "sektor": s, "vf2_milyar": r1(x["vf2"]), "vadesiz": r1(x["vadesiz"]), "vadeli": r1(x["vadeli"]),
                         "pay_butun": r3(x["vf2"] / butun), "pay_hfg": r3(x["vf2"] / hfg) if s in ("H", "F", "GY", "MY") else None,
                         "seri": f"{seri(SEKTOR[s], 5)} | {seri(SEKTOR[s], 7)} | {seri(SEKTOR[s], 8)}",
                         "kaynak_url": f"{URL}/bie_finhestnks{SEKTOR[s].lower()}"})
        kalan_b, kalan_h = 1 - my / butun, 1 - my / hfg
        ozet[d] = {
            "payda_butun": r1(butun), "payda_hfg": r1(hfg), "my": r1(my),
            "pay_my_butun": r3(my / butun), "pay_my_hfg": r3(my / hfg),
            "kalan_butun": r3(kalan_b), "kalan_hfg": r3(kalan_h),
            "yuzde70_butun": "tuttu" if kalan_b >= ESIK_70 else "yüzde 70 tutmadı",
            "yuzde70_hfg": "tuttu" if kalan_h >= ESIK_70 else "yüzde 70 tutmadı",
            "H_pay_hfg": r3(v["H"]["vf2"] / hfg), "F_pay_hfg": r3(v["F"]["vf2"] / hfg),
            "GY_disi_MY_pay_hfg": r3((v["GY"]["vf2"] - my) / hfg),
            "payda_disi": {"HHKAOK": r1(v["HHKAOK"]["vf2"]), "diger_finansal_S12_eksi_PFK": r1(v["S12"]["vf2"] - v["PFK"]["vf2"]),
                           "S1_toplam_ekonomi": r1(v["S1"]["vf2"])},
            "cift_sayim_notu": "PFK VF.2 bankalararası, TCMB'deki banka mevduatı ve kendi içini tutar; bütün payda bu yüzden brüttür.",
            "kimden_kime_banka_bacagi": KIMDEN_KIME.get(d, {}),
        }
    return rows, ozet


def hipotez(veri: dict, ozet: dict) -> dict:
    hp = "olculdu" if all(isinstance(o.get("kalan_hfg"), float) for o in ozet.values()) else "test_edilemez"
    q2, q3 = veri["2025-Q2"], veri["2025-Q3"]

    def oran(s):
        a, b = q2[s]["vadeli"], q3[s]["vadeli"]
        return None if (a in (None, 0) or b is None) else (b - a) / a

    o = {s: oran(s) for s in ("MY", "H", "F", "GY", "PFK", "ROW")}
    birlikte = [s for s in ("H", "F") if o[s] is not None and o["MY"] is not None and abs(o[s] - o["MY"]) <= BIRLIKTE_TOL]
    hp2 = "birlikte" if birlikte else "ayri"
    return {
        "H-P": hp,
        "H-P_not": "H+F+GY paydasında MY dışı pay her dönem için yazıldı." if hp == "olculdu" else "Payda kurulamadı.",
        "H-P2": hp2,
        "H-P2_not": ("2025-Q2→Q3 vadeli oransal değişim: " + ", ".join(f"{s} {o[s]:+.1%}" for s in o if o[s] is not None)
                     + f". Eşik ±{BIRLIKTE_TOL:.0%}. " + ("Birlikte hareket eden: " + ", ".join(birlikte) + ". Birlikte, aynı neden demek değildir."
                                                          if birlikte else "H ve F vadelisi MY ile aynı oranda değil.")),
        "vadeli_oransal_degisim_Q2_Q3": {s: r3(x) for s, x in o.items()},
        "vadeli_mutlak_degisim_Q2_Q3": {s: r1(q3[s]["vadeli"] - q2[s]["vadeli"]) for s in o},
        "vade_dilimi": "ayrılmadı (sektör toplamı vade dilimi var, tür kırılımı yok); kalıcılık cümlesi yazılmaz; H-K1 kapalı",
    }


def rapor(rows: list[dict], ozet: dict, hip: dict) -> str:
    s = ["# Kalan mevduat payı", "",
         "Kalan = VF.2 − merkezi yönetim. Pay, aynı dönem aynı tanım toplam VF.2 içindeki oran. Konsolide olmayan. Yüzde 70 hesaplanır.", "",
         "## Pay tablosu", "", "| Dönem | Payda bütün | Payda H+F+GY | MY | MY/bütün | MY/HFG | Kalan/bütün | Kalan/HFG | %70 (bütün) | %70 (HFG) |",
         "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |"]
    for d, o in ozet.items():
        if "payda_butun" not in o:
            s.append(f"| {d} | kurulamadı ({', '.join(o['eksik'])}) | | | | | | | | |")
            continue
        s.append(f"| {d} | {o['payda_butun']:,.1f} | {o['payda_hfg']:,.1f} | {o['my']:,.1f} | {o['pay_my_butun']:.1%} | {o['pay_my_hfg']:.1%} | "
                 f"{o['kalan_butun']:.1%} | {o['kalan_hfg']:.1%} | {o['yuzde70_butun']} | {o['yuzde70_hfg']} |")
    s += ["", "## Sektör payları (H+F+GY paydası; H ve F ayrı)", "", "| Dönem | H | F | GY−MY (yerel+SGK) | MY |", "| --- | ---: | ---: | ---: | ---: |"]
    s += [f"| {d} | {o['H_pay_hfg']:.1%} | {o['F_pay_hfg']:.1%} | {o['GY_disi_MY_pay_hfg']:.1%} | {o['pay_my_hfg']:.1%} |" for d, o in ozet.items() if "payda_butun" in o]
    s += ["", "## Sektör stokları ve vade (milyar TL)", "", "| Dönem | Sektör | VF.2 | Vadesiz (ZP7) | Vadeli (ZP8) | Pay bütün | Pay HFG |", "| --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    f = lambda x: "" if x is None else f"{x:,.1f}"
    for r in rows:
        s.append(f"| {r['donem']} | {r['sektor']} | {f(r['vf2_milyar'])} | {f(r['vadesiz'])} | {f(r['vadeli'])} | "
                 f"{'' if r['pay_butun'] is None else format(r['pay_butun'], '.1%')} | {'' if r['pay_hfg'] is None else format(r['pay_hfg'], '.1%')} |")
    o1 = ozet["2026-Q1"]
    s += ["", f"Çift sayım: {o1['cift_sayim_notu']} Payda dışı (2026-Q1): HHKAOK {o1['payda_disi']['HHKAOK']:,.1f}, "
          f"diğer finansal (S.12 − PFK) {o1['payda_disi']['diger_finansal_S12_eksi_PFK']:,.1f}; S.1 toplam {o1['payda_disi']['S1_toplam_ekonomi']:,.1f}.",
          "", "## Vade dilimi", "", f"- {hip['vade_dilimi']}.",
          "", "## Karşı taraf (kimden-kime, metin)", ""]
    for d, kk in ((d, o.get("kimden_kime_banka_bacagi", {})) for d, o in ozet.items()):
        s.append(f"- {d}: " + (", ".join(f"{k}→PFK mevduat {v:,.0f}" for k, v in kk.items()) if kk else "metin yok, boş"))
    s += ["", "## Yanlışlayıcılar", "", f"- **H-P:** `{hip['H-P']}`. {hip['H-P_not']}", f"- **H-P2:** `{hip['H-P2']}`. {hip['H-P2_not']}",
          "- Ödenmeyen emir bu dosyada yok; H-K1 kapalı.",
          "", "## Arama günlüğü", "", "| Grup | Sonuç |", "| --- | --- |",
          "| bie_finhestnks14 / 11 / 13 / 1311 / 12T / 2 | açıldı; ZP5, ZP7, ZP8 dolu |",
          "| bie_finhestnks15 / 12 / 1 | açıldı; payda dışı not |",
          "| bie_finhestnks12t (küçük t) | boş; 12T kullanıldı |",
          "| bie_finhestnks71011 (konsolide) | kullanılmadı |",
          "| Vade dilimi (tür × vade) | yok; vadeli_kalicilik günlüğü (15 kod) |",
          "| Kimden-kime 2025-Q2 / Q3 metni | depoda yok; yalnız 2026-Q1 |",
          "", "Tekrar: `python3 kalan_mevduat.py`. Dosyalar: `kalan_mevduat.csv`, `kalan_mevduat_sonuc.json`."]
    return "\n".join(s) + "\n"


def main() -> None:
    veri = cek()
    rows, ozet = paylar(veri)
    hip = hipotez(veri, ozet)
    cols = ["donem", "sektor", "vf2_milyar", "vadesiz", "vadeli", "pay_butun", "pay_hfg", "seri", "kaynak_url"]
    with open(KOK / "kalan_mevduat.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in cols})
    (KOK / "kalan_mevduat_sonuc.json").write_text(json.dumps({"birim": "milyar TL, dönem sonu", "ozet": ozet, "hipotez": hip}, ensure_ascii=False, indent=2), encoding="utf-8")
    (KOK / "KALAN_MEVDUAT.md").write_text(rapor(rows, ozet, hip), encoding="utf-8")
    print(json.dumps({"ozet": {d: {k: o.get(k) for k in ("kalan_butun", "kalan_hfg", "yuzde70_butun", "yuzde70_hfg")} for d, o in ozet.items()}, "hipotez": hip}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
