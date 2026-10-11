"""Diğer mevduatlar: lider mevduat dışındaki tüm mevduat stokunun sahip × ihraççı haritası.

Üç ölçülmüş blok, bir türetilmiş blok:
  A. TCMB finansal hesaplar (konsolide olmayan, stok): sektör VF.2 (tutulan) ve F.2 (ihraç edilen).
  B. TCMB bilançosu (bie_mbblnca): P3 mevduat kırılımı — kamu / bankacılık / diğer, TL+YP, nakit/altın.
  C. Bankalar (HPB tablo 2-3): sahip kırılımı — gerçek, ticari, resmî, HHKAOK, BDFK, bankalar, yurt dışı.
  D. Türetilmiş (seri değil, fark): MY banka bacağı, GY YP banka bacağı. Skor değildir.
Birim milyar TL, dönem sonu. Akış ve stok tavanı bu dosyada yok.
Çıktı: diger_mevduat.csv, diger_mevduat_sonuc.json, DIGER_MEVDUAT.md
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from evds_cek import BASE, get_json

KOK = Path(__file__).resolve().parent
DONEMLER = ("2025-Q4", "2026-Q1")
Q_AY = {"Q1": "03", "Q2": "06", "Q3": "09", "Q4": "12"}
URL = "https://evds3.tcmb.gov.tr/tumSeriler"

SEKTOR = {
    "11": "F firmalar", "121": "TCMB", "122": "Mevduat kabul eden kuruluşlar (bankalar)", "123": "Para piyasası fonları",
    "124": "Diğer yatırım fonları", "125": "Diğer finansal aracılar", "126": "Finansal yardımcılar",
    "127": "Sigorta ve emeklilik", "1311": "Merkezi yönetim", "1313": "Yerel yönetimler", "1314": "SGK",
    "14": "H hane", "15": "HHKAOK", "2": "ROW", "1": "Toplam ekonomi (S.1)", "13": "GY toplam",
}
ZP = {"vf2": 5, "vf2_para": 6, "vf2_vadesiz": 7, "vf2_vadeli": 8, "f2": 27, "f2_para": 28, "f2_vadesiz": 29, "f2_vadeli": 30}

MB = {  # TCMB bilançosu, (TL seri, YP seri)
    "P3 Mevduat": ("TP.BL064.A", "TP.BL080.A"),
    "P31 Kamu sektörü": ("TP.BL065.A", "TP.BL081.A"),
    "P311 Hazine, genel ve özel bütçeli idareler": ("TP.BL066.A", "TP.BL082.A"),
    "P3111 Nakit": ("TP.BL0661.A", "TP.BL0821.A"),
    "P3112 Altın": ("TP.BL0662.A", "TP.BL0822.A"),
    "P312 Kamu diğer": ("TP.BL067.A", "TP.BL083.A"),
    "P32 Bankacılık sektörü": ("TP.BL068.A", "TP.BL084.A"),
    "P321 Yurt içi bankalar": ("TP.BL069.A", "TP.BL085.A"),
    "P322 Yurt dışı bankalar": ("TP.BL070.A", "TP.BL086.A"),
    "P323 Zorunlu karşılık bloke": ("TP.BL071.A", "TP.BL087.A"),
    "P324 Bankacılık diğer": ("TP.BL074.A", "TP.BL090.A"),
    "P33 Diğer mevduat": ("TP.BL075.A", "TP.BL091.A"),
    "P331 İşçi dövizleri": ("TP.BL076.A", "TP.BL092.A"),
    "P332 Uluslararası kuruluşlar": ("TP.BL077.A", "TP.BL093.A"),
    "P333 Fonlar": ("TP.BL078.A", "TP.BL094.A"),
    "P334 Diğer": ("TP.BL079.A", "TP.BL095.A"),
}
BANKA = {  # HPB; (seri, para birimi)
    "Toplam mevduat": ("TP.HPBITABLO2.1", "TL+YP"),
    "Yurt içi yerleşikler": ("TP.HPBITABLO2.2", "TL+YP"),
    "Yurt içi TL": ("TP.HPBITABLO3.2", "TL"),
    "Gerçek kişiler": ("TP.HPBITABLO3.3", "TL"),
    "Ticari kuruluşlar": ("TP.HPBITABLO3.6", "TL"),
    "Resmî kuruluşlar": ("TP.HPBITABLO3.9", "TL"),
    "HHKAOK": ("TP.HPBITABLO3.12", "TL"),
    "Banka dışı finansal kuruluşlar": ("TP.HPBITABLO3.15", "TL"),
    "Yurt içi YP": ("TP.HPBITABLO2.6", "YP"),
    "Gerçek kişiler YP": ("TP.HPBITABLO2.7", "YP"),
    "Tüzel kişiler YP (ticari+resmî+BDFK+HHKAOK ayrılmaz)": ("TP.HPBITABLO2.8", "YP"),
    "Yurt içi bankalar": ("TP.HPBITABLO2.13", "TL+YP"),
    "Yurt dışı yerleşikler": ("TP.HPBITABLO2.16", "TL+YP"),
    "Yurt dışı bankalar": ("TP.HPBITABLO2.19", "TL+YP"),
}


def _fetch(series: list[str], freq: str, start: str = "01-10-2025", end: str = "10-10-2026") -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for i in range(0, len(series), 25):
        ch = series[i:i + 25]
        body = {"type": "json", "series": "-".join(ch), "aggregationTypes": "-".join("last" for _ in ch),
                "formulas": "-".join("0" for _ in ch), "startDate": start, "endDate": end, "frequency": freq,
                "decimalSeperator": ".", "decimal": "4", "dateFormat": "0", "lang": "TR", "yon": "0", "sira": "0",
                "ozelFormuller": [], "groupSeperator": False, "isRaporSayfasi": False}
        for it in get_json(f"{BASE}/fe", body)["items"]:
            for s in ch:
                v = it.get(s.replace(".", "_"))
                if v not in (None, ""):
                    out.setdefault(str(it["Tarih"]), {})[s] = float(str(v).replace(",", "")) / 1e6
    return out


def cek() -> tuple[dict, dict]:
    fh = _fetch([f"TP.FINHESTNKS{k}.ZP{n}" for k in SEKTOR for n in ZP.values()], "6")
    ay = _fetch([s for tl, yp in MB.values() for s in (tl, yp)] + [s for s, _ in BANKA.values()], "5")
    return fh, ay


def r1(x):
    return None if x is None else round(x, 1)


def satirlar(fh: dict, ay: dict) -> tuple[list[dict], dict]:
    rows: list[dict] = []
    ozet: dict = {}
    for d in DONEMLER:
        q = fh.get(d, {})
        m = ay.get(f"{d[:4]}-{Q_AY[d[-2:]]}", {})

        def g(k, n):
            return q.get(f"TP.FINHESTNKS{k}.ZP{n}")

        # A. finansal hesaplar
        for k, ad in SEKTOR.items():
            for yon, n in (("tutulan_VF2", 5), ("ihrac_F2", 27)):
                v = g(k, n)
                if v is None:
                    continue
                rows.append({"donem": d, "blok": "A_finansal_hesaplar", "kalem": ad, "yon": yon, "stok_milyar": r1(v),
                             "para": r1(g(k, n + 1)), "vadesiz": r1(g(k, n + 2)), "vadeli": r1(g(k, n + 3)),
                             "seri": f"TP.FINHESTNKS{k}.ZP{n}", "kaynak_url": f"{URL}/bie_finhestnks{k}", "tur": "olculmus", "not": ""})
        # B. TCMB bilançosu
        for ad, (stl, syp) in MB.items():
            tl, yp = m.get(stl), m.get(syp)
            if tl is None and yp is None:
                continue
            rows.append({"donem": d, "blok": "B_tcmb_bilanco", "kalem": ad, "yon": "TCMB_yukumluluk", "stok_milyar": r1((tl or 0) + (yp or 0)),
                         "para": None, "vadesiz": None, "vadeli": None, "seri": f"{stl} + {syp}", "kaynak_url": f"{URL}/3003/bie_mbblnca",
                         "tur": "olculmus", "not": f"TL {r1(tl)} + YP {r1(yp)}"})
        # C. bankalar
        for ad, (s, pb) in BANKA.items():
            v = m.get(s)
            if v is None:
                continue
            rows.append({"donem": d, "blok": "C_banka_sahip", "kalem": ad, "yon": "banka_yukumluluk", "stok_milyar": r1(v),
                         "para": None, "vadesiz": None, "vadeli": None, "seri": s, "kaynak_url": f"{URL}/{'bie_hpbitablo3' if 'TABLO3' in s else 'bie_hpbitablo2'}",
                         "tur": "olculmus", "not": pb})
        # D. türetilmiş
        my_vf2, my_para = g("1311", 5), g("1311", 6)
        gy_vf2, gy_para = g("13", 5), g("13", 6)
        mb_nakit = (m.get("TP.BL0661.A") or 0) + (m.get("TP.BL0821.A") or 0)
        mb_altin = (m.get("TP.BL0662.A") or 0) + (m.get("TP.BL0822.A") or 0)
        resmi_tl = m.get("TP.HPBITABLO3.9")
        turet = []
        if my_vf2 is not None:
            my_banka = my_vf2 - (my_para or 0) - mb_nakit
            turet.append(("Merkezi yönetim banka bacağı (TL+YP)", my_banka, "MY VF.2 − MY para − TCMB P3111 nakit; P311 kapsamı MY ile örtüşür varsayımı"))
        if gy_vf2 is not None and resmi_tl is not None:
            gy_yp_banka = gy_vf2 - (gy_para or 0) - mb_nakit - resmi_tl
            turet.append(("GY YP banka bacağı", gy_yp_banka, "GY VF.2 − GY para − TCMB P3111 nakit − resmî TL (HPB 3.9); resmî YP serisi yok"))
        for ad, v, nt in turet:
            rows.append({"donem": d, "blok": "D_turetilmis", "kalem": ad, "yon": "fark", "stok_milyar": r1(v), "para": None, "vadesiz": None,
                         "vadeli": None, "seri": "", "kaynak_url": "", "tur": "turetilmis_skor_degil", "not": nt})
        # kimlik
        s1_vf2, row_vf2, s1_f2, row_f2 = g("1", 5), g("2", 5), g("1", 27), g("2", 27)
        acik = None
        if None not in (s1_vf2, row_vf2, s1_f2, row_f2):
            acik = (s1_vf2 + row_vf2) - (s1_f2 + row_f2)
        ozet[d] = {
            "tutulan_toplam_S1_ROW": r1(None if s1_vf2 is None else s1_vf2 + (row_vf2 or 0)),
            "ihrac_toplam_S1_ROW": r1(None if s1_f2 is None else s1_f2 + (row_f2 or 0)),
            "kimlik_acigi": r1(acik),
            "tcmb_P3_toplam": r1((m.get("TP.BL064.A") or 0) + (m.get("TP.BL080.A") or 0)),
            "tcmb_P33_diger": r1((m.get("TP.BL075.A") or 0) + (m.get("TP.BL091.A") or 0)),
            "tcmb_P311_nakit": r1(mb_nakit), "tcmb_P311_altin": r1(mb_altin),
            "banka_toplam": r1(m.get("TP.HPBITABLO2.1")),
            "lider_disi_tutulan": r1(None if (s1_vf2 is None or my_vf2 is None) else s1_vf2 + (row_vf2 or 0) - my_vf2),
            "turetilmis": {ad: r1(v) for ad, v, _ in turet},
        }
    return rows, ozet


def rapor(rows: list[dict], ozet: dict) -> str:
    d = "2026-Q1"
    o = ozet[d]
    s = ["# Diğer mevduatlar — sahip × ihraççı haritası", "",
         "Lider mevduat (merkezi yönetim VF.2) dışındaki stok. Birim milyar TL, dönem sonu. Akış ve stok tavanı yok.", "",
         f"## A. Finansal hesaplar, {d} (konsolide olmayan)", "",
         "| Sektör | Tutulan VF.2 | para / vadesiz / vadeli | İhraç F.2 |", "| --- | ---: | --- | ---: |"]
    A = {(r["kalem"], r["yon"]): r for r in rows if r["donem"] == d and r["blok"] == "A_finansal_hesaplar"}
    for k, ad in SEKTOR.items():
        t, i = A.get((ad, "tutulan_VF2")), A.get((ad, "ihrac_F2"))
        if not t:
            continue
        s.append(f"| {ad} | {t['stok_milyar']:,.1f} | {t['para']:,.1f} / {t['vadesiz']:,.1f} / {t['vadeli']:,.1f} | {(i or {}).get('stok_milyar', 0):,.1f} |")
    s += ["", f"Tutulan (S.1+ROW) {o['tutulan_toplam_S1_ROW']:,.1f}; ihraç (S.1+ROW) {o['ihrac_toplam_S1_ROW']:,.1f}; "
          f"**kimlik açığı {o['kimlik_acigi']:,.1f}**. Açık ölçülmüştür, nedeni dosyada yoktur; kapatılmaz.",
          f"Lider dışı tutulan: {o['lider_disi_tutulan']:,.1f}.", "",
          f"## B. TCMB bilançosu, {d[:4]}-{Q_AY[d[-2:]]}", "", "| Kalem | TL+YP | Not |", "| --- | ---: | --- |"]
    s += [f"| {r['kalem']} | {r['stok_milyar']:,.1f} | {r['not']} |" for r in rows if r["donem"] == d and r["blok"] == "B_tcmb_bilanco"]
    s += ["", f"TCMB'de banka ve kamu dışı mevduat (P33) {o['tcmb_P33_diger']:,.1f}: hane ve firma TCMB'de mevduat tutmaz. "
          f"P311 nakit {o['tcmb_P311_nakit']:,.1f}, altın {o['tcmb_P311_altin']:,.1f} (altın F.1'dir, VF.2'ye girmez).", "",
          f"## C. Bankalar, sahip kırılımı, {d[:4]}-{Q_AY[d[-2:]]}", "", "| Kalem | Stok | Para birimi |", "| --- | ---: | --- |"]
    s += [f"| {r['kalem']} | {r['stok_milyar']:,.1f} | {r['not']} |" for r in rows if r["donem"] == d and r["blok"] == "C_banka_sahip"]
    s += ["", "## D. Türetilmiş (fark, seri değil, skor değil)", "", "| Kalem | Değer | Nasıl |", "| --- | ---: | --- |"]
    s += [f"| {r['kalem']} | {r['stok_milyar']:,.1f} | {r['not']} |" for r in rows if r["donem"] == d and r["blok"] == "D_turetilmis"]
    C = {r["kalem"]: r["stok_milyar"] for r in rows if r["donem"] == d and r["blok"] == "C_banka_sahip"}
    s += ["", "## Okuma", "",
          "- Mevduat ihraççısı dört kapı: bankalar, TCMB, GY (yalnız kendi içine), ROW. Firma, hane, fon, sigorta mevduat ihraç etmez (F.2 = 0).",
          "- TCMB'nin mevduat yükümlülüğü bankacılık (ZK bloke dahil) ve kamu; 'diğer' kalemi önemsizdir.",
          "- Banka tarafında YP mevduat sahip kırılımı yalnız gerçek/tüzel; resmî YP ve ticari YP ayrılmaz. Bu yüzden MY ve GY banka bacakları türetilmiştir.",
          f"- Hane VF.2 {A[('H hane','tutulan_VF2')]['stok_milyar']:,.1f} − para {A[('H hane','tutulan_VF2')]['para']:,.1f} = {A[('H hane','tutulan_VF2')]['stok_milyar']-A[('H hane','tutulan_VF2')]['para']:,.1f}; "
          f"banka gerçek kişi TL+YP {C['Gerçek kişiler']+C['Gerçek kişiler YP']:,.1f}; fark {A[('H hane','tutulan_VF2')]['stok_milyar']-A[('H hane','tutulan_VF2')]['para']-C['Gerçek kişiler']-C['Gerçek kişiler YP']:,.1f} (sınıflama; açıklanmaz).",
          "", "Tekrar: `python3 diger_mevduat.py`. Dosyalar: `diger_mevduat.csv`, `diger_mevduat_sonuc.json`."]
    return "\n".join(s) + "\n"


def main() -> None:
    fh, ay = cek()
    rows, ozet = satirlar(fh, ay)
    cols = ["donem", "blok", "kalem", "yon", "stok_milyar", "para", "vadesiz", "vadeli", "seri", "kaynak_url", "tur", "not"]
    with open(KOK / "diger_mevduat.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in cols})
    (KOK / "diger_mevduat_sonuc.json").write_text(json.dumps({"birim": "milyar TL, dönem sonu", "ozet": ozet}, ensure_ascii=False, indent=2), encoding="utf-8")
    (KOK / "DIGER_MEVDUAT.md").write_text(rapor(rows, ozet), encoding="utf-8")
    print(json.dumps(ozet, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
