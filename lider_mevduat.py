"""Lider mevduat katmanı: yürütme rolünün tuttuğu nakit (THKH + merkezi yönetim / resmî mevduat).

Kişi, hane veya firma mevduatı değildir. GY toplamı lider değildir. Akış yüzdesi ve stok tavanı
bu dosyaya girmez. Birim milyar TL, dönem sonu stok. Girdi yalnız EVDS (anahtarsız uç nokta) ve
TCMB yıllık bilanço metin rakamı (yıl sonu altın ayrımı).

Çıktı: lider_mevduat.csv, lider_mevduat_sonuc.json, LIDER_MEVDUAT.md
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from evds_cek import BASE, get_json

KOK = Path(__file__).resolve().parent
DONEMLER = ("2024-Q4", "2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4", "2026-Q1", "2026-Q2", "2026-Q3")
Q_AY = {"Q1": "03", "Q2": "06", "Q3": "09", "Q4": "12"}

URL_EVDS = "https://evds3.tcmb.gov.tr/tumSeriler"
URL_FINHEST_GY = f"{URL_EVDS}/bie_finhestnks13"
URL_FINHEST_MY = f"{URL_EVDS}/bie_finhestnks1311"
URL_FINHEST_H = f"{URL_EVDS}/bie_finhestnks14"
URL_MBBLNCA = f"{URL_EVDS}/3003/bie_mbblnca"
URL_HPB3 = f"{URL_EVDS}/bie_hpbitablo3"
URL_YR2025 = "https://www3.tcmb.gov.tr/yillikrapor/2025/pdf/3.2%2031.12.2025%20ve%2031.12.2024%20Tarihli%20Bilan%C3%A7olar.pdf"
URL_YR2024 = "https://www3.tcmb.gov.tr/yillikrapor/2024/pdf/3.4-Aciklamalar.pdf"
URL_RG17 = "https://www.lexpera.com.tr/mevzuat/cumhurbaskani-kararlari/tek-hazine-kurumlar-hesabi-kapsamina-alinacak-kamu-idareleri-ve-hesaplarin-belirlenmesi-hakkinda-3"
URL_KIMDEN = "https://www.tcmb.gov.tr/wps/wcm/connect/bf500c17-e3d5-40bd-8475-370caca9c6fd/VII.+Kimden-Kime+Tablolar%C4%B1.pdf?CACHEID=ROOTWORKSPACE-bf500c17-e3d5-40bd-8475-370caca9c6fd-p-TY4sh&MOD=AJPERES"

# TCMB yıllık bilanço, "Hazine, Genel ve Özel Bütçeli İdareler" içindeki altın (TL). Metin rakamı.
ALTIN_YILSONU = {"2024-Q4": 180.586, "2025-Q4": 268.811}
# Kimden-kime VII, 2026-Q1: GY mevduatının tamamı GY elinde (stok_silim.csv satırı).
GY_GY_KIMDEN = 352.0

SERI_CEYREK = {
    "gy_vf2": "TP.FINHESTNKS13.ZP5",
    "my_vf2": "TP.FINHESTNKS1311.ZP5",
    "my_vadesiz": "TP.FINHESTNKS1311.ZP7",
    "my_vadeli": "TP.FINHESTNKS1311.ZP8",
    "yerel_vf2": "TP.FINHESTNKS1313.ZP5",
    "sgk_vf2": "TP.FINHESTNKS1314.ZP5",
    "hane_vf2": "TP.FINHESTNKS14.ZP5",
    "gy_f2_yuk": "TP.FINHESTNKS13.ZP27",
    "my_f2_yuk": "TP.FINHESTNKS1311.ZP27",
}
SERI_AYLIK = {
    "mb_p311_tl": "TP.BL066.A",
    "mb_p311_yp": "TP.BL082.A",
    "mb_p3111_nakit_tl": "TP.BL0661.A",
    "mb_p3111_nakit_yp": "TP.BL0821.A",
    "mb_p3112_altin_tl": "TP.BL0662.A",
    "mb_p3112_altin_yp": "TP.BL0822.A",
    "mb_p31_tl": "TP.BL065.A",
    "mb_p31_yp": "TP.BL081.A",
    "banka_resmi_tl": "TP.HPBITABLO3.9",
}


def _fetch(series: list[str], freq: str, start: str = "01-10-2024", end: str = "10-10-2026") -> dict[str, dict[str, float]]:
    body = {
        "type": "json",
        "series": "-".join(series),
        "aggregationTypes": "-".join("last" for _ in series),
        "formulas": "-".join("0" for _ in series),
        "startDate": start,
        "endDate": end,
        "frequency": freq,
        "decimalSeperator": ".",
        "decimal": "4",
        "dateFormat": "0",
        "lang": "TR",
        "yon": "0",
        "sira": "0",
        "ozelFormuller": [],
        "groupSeperator": False,
        "isRaporSayfasi": False,
    }
    data = get_json(f"{BASE}/fe", body)
    out: dict[str, dict[str, float]] = {}
    for it in data["items"]:
        t = str(it["Tarih"])
        for s in series:
            v = it.get(s.replace(".", "_"))
            if v not in (None, ""):
                out.setdefault(t, {})[s] = float(str(v).replace(",", "")) / 1e6  # bin TL -> milyar TL
    return out


def cek() -> dict[str, dict[str, float | None]]:
    q = _fetch(list(SERI_CEYREK.values()), "6")
    m = _fetch(list(SERI_AYLIK.values()), "5")
    veri: dict[str, dict[str, float | None]] = {}
    for d in DONEMLER:
        yil, ck = d.split("-")
        ay = f"{yil}-{Q_AY[ck]}"
        row: dict[str, float | None] = {}
        for k, s in SERI_CEYREK.items():
            row[k] = q.get(d, {}).get(s)
        for k, s in SERI_AYLIK.items():
            row[k] = m.get(ay, {}).get(s)
        veri[d] = row
    return veri


def _r(x: float | None) -> float | None:
    return None if x is None else round(x, 1)


def satirlar(veri: dict) -> list[dict]:
    rows = []
    for d, v in veri.items():
        gy = v["gy_vf2"]
        hane = v["hane_vf2"]
        yan = {"gy_toplam_vf2_milyar": _r(gy), "hane_vf2_milyar": _r(hane)}

        def pay(x):
            return None if (x is None or not hane) else round(100.0 * x / hane, 1)

        rows.append({
            "donem": d, "parca": "THKH", "stok_milyar": None, "seri": "",
            "kaynak_url": URL_RG17,
            "not": "ayrılmadı; 4749 m.12 ve CB Kararı 17 (RG 8.8.2018/30500) kapsam tanımlar, stok serisi yok. "
                   f"Aday: GY mevduat yükümlülüğü {_r(v['gy_f2_yuk'])} (tamamı S.1311 ihraçlı, EVDS ZP27); "
                   f"kimden-kime GY–GY {GY_GY_KIMDEN:.0f} (2026-Q1). THKH diye etiketli değil, lider sütununa geçmez.",
            "pay_hane_yuzde": None, **yan,
        })
        rows.append({
            "donem": d, "parca": "resmi_mevduat", "stok_milyar": _r(v["my_vf2"]),
            "seri": SERI_CEYREK["my_vf2"], "kaynak_url": URL_FINHEST_MY,
            "not": "Merkezi yönetim (S.1311) VF.2 para ve mevduat, konsolide olmayan stok; TCMB+banka, TL+YP; "
                   f"vadesiz {_r(v['my_vadesiz'])} + vadeli {_r(v['my_vadeli'])}. GY'den ayrı seri: "
                   f"GY {_r(gy)} = MY + yerel {_r(v['yerel_vf2'])} + SGK {_r(v['sgk_vf2'])}."
                   if v["my_vf2"] is not None else "EVDS finansal hesaplarda henüz yok",
            "pay_hane_yuzde": pay(v["my_vf2"]), **yan,
        })
        mb_tl, mb_yp = v["mb_p311_tl"], v["mb_p311_yp"]
        mb_top = None if (mb_tl is None or mb_yp is None) else mb_tl + mb_yp
        nakit = None if v["mb_p3111_nakit_tl"] is None else v["mb_p3111_nakit_tl"] + (v["mb_p3111_nakit_yp"] or 0)
        altin = None if v["mb_p3112_altin_tl"] is None else v["mb_p3112_altin_tl"] + (v["mb_p3112_altin_yp"] or 0)
        altin_yr = ALTIN_YILSONU.get(d)
        rows.append({
            "donem": d, "parca": "merkez_banka", "stok_milyar": _r(nakit),
            "seri": f"{SERI_AYLIK['mb_p3111_nakit_tl']} + {SERI_AYLIK['mb_p3111_nakit_yp']}", "kaynak_url": URL_MBBLNCA,
            "not": (f"TCMB bilançosu P3111 nakit (Hazine, genel ve özel bütçeli idareler): TL {_r(v['mb_p3111_nakit_tl'])} + YP {_r(v['mb_p3111_nakit_yp'])}. "
                    f"P311 toplam {_r(mb_top)} = nakit + altın {_r(altin)} (altın F.1, mevduat değil)"
                    + (f"; yıllık bilanço altın {altin_yr:.1f} ile uyumlu" if altin_yr else "")
                    + ". Hazine tek başına ayrılmadı; THKH bu kalemin içinde olabilir, seri ayırmaz.")
                   if nakit is not None else "veri yok",
            "pay_hane_yuzde": pay(nakit), **yan,
        })
        rows.append({
            "donem": d, "parca": "banka", "stok_milyar": None,
            "seri": SERI_AYLIK["banka_resmi_tl"], "kaynak_url": URL_HPB3,
            "not": f"ayrılmadı; HPB tablo 3 'Resmî kuruluşlar' TL {_r(v['banka_resmi_tl'])} GY kapsamıdır "
                   "(yerel yönetim ve SGK dahil), merkezi yönetim bacağı ayrılmaz; YP resmî serisi yok.",
            "pay_hane_yuzde": None, **yan,
        })
    return rows


def hipotezler(veri: dict) -> dict:
    ref = "2026-Q1"
    v = veri[ref]
    my, gy, hane = v["my_vf2"], v["gy_vf2"], v["hane_vf2"]
    mb = (v["mb_p3111_nakit_tl"] or 0) + (v["mb_p3111_nakit_yp"] or 0)
    ayri = my is not None and gy is not None and my < gy
    hl = "ayri" if ayri else "test_edilemez"
    buyukluk = None
    if ayri and hane:
        buyukluk = "buyuk" if my > 0.10 * hane else "kucuk"
    return {
        "donem": ref,
        "H-L": hl,
        "H-L_not": (f"Merkezi yönetim VF.2 {my:,.1f} < GY VF.2 {gy:,.1f}; ayrı EVDS serisi (S.1311). "
                    f"Hane VF.2 {hane:,.1f}; MY/hane = %{100*my/hane:.1f}; TCMB P3111 nakit/hane = %{100*mb/hane:.1f}. "
                    "Büyüklük kontrol kanıtı değildir."),
        "H-L_buyukluk": buyukluk,
        "H-L2": "silinen_bos",
        "H-L2_not": ("Lider parçasının ters bacağı yok: TCMB ve bankalar GY'de mevduat tutmaz; GY mevduat yükümlülüğü "
                     f"({v['gy_f2_yuk']:,.1f}) tamamı S.1311 ihraçlı ve kimden-kime GY–GY {GY_GY_KIMDEN:.0f} kendi içidir. "
                     "Skora girmez. Tavan yazılmaz."),
        "thkh": "ayrilmadi",
        "akis_ve_stok_tavani": "bu katmanda yok",
    }


def arama_gunlugu() -> list[dict]:
    return [
        {"grup": "bie_finhestnks1311", "sonuc": "açıldı", "not": "Merkezi yönetim (S.1311) konsolide olmayan stok; VF.2, F.2"},
        {"grup": "bie_finhestnks1313 / 1314", "sonuc": "açıldı", "not": "Yerel yönetim, SGK; GY toplamı kontrolü"},
        {"grup": "bie_finhestnks13", "sonuc": "açıldı", "not": "GY toplamı (yan sütun)"},
        {"grup": "bie_finhestnks14", "sonuc": "açıldı", "not": "Hane VF.2 (yüzde 10 eşiği)"},
        {"grup": "bie_mbblnca", "sonuc": "açıldı", "not": "TCMB bilançosu aylık; P311 = P3111 nakit + P3112 altın, TL/YP. Yıl sonu yıllık bilançoyla birebir (2024: 1.001,1; 2025: 1.372,4)"},
        {"grup": "bie_abanlbil", "sonuc": "açıldı, kullanılmadı", "not": "Analitik bilanço 'Kamu Mevduatı' TL; 'Kamu ve Diğer Döviz Mevduatı' karışık"},
        {"grup": "bie_hpbitablo3", "sonuc": "açıldı", "not": "Resmî kuruluşlar TL; GY kapsamı, MY ayrılmaz"},
        {"grup": "bie_hpbitablo2/4/8", "sonuc": "açıldı, boş", "not": "YP veya toplam mevduatta resmî ayrımı yok"},
        {"grup": "bie_mevduat", "sonuc": "açıldı, kullanılmadı", "not": "Arşiv seri; banka grubu bazında resmî kuruluşlar"},
        {"grup": "bie_finhestnks1312 / 71311 / 61311", "sonuc": "boş", "not": "Kimden-kime MY alt sektörü yok"},
        {"grup": "bie_hznakit, bie_hazine, bie_hazinenakit, bie_nakitdenge, bie_kamufin, bie_hzborc", "sonuc": "boş", "not": "THKH / Hazine nakit rezervi stok serisi EVDS'de bulunamadı"},
        {"grup": "web: HMB nakit gerçekleşmeleri", "sonuc": "akım", "not": "Aylık nakit dengesi akımdır; THKH bakiyesi yayımlanmıyor (2 sorgu denendi)"},
    ]


def rapor(rows: list[dict], hip: dict, veri: dict) -> str:
    s = ["# Lider mevduat katmanı", "",
         "Yürütme rolünün tuttuğu nakit. Kişi, hane, firma mevduatı değildir. Akış yüzdesi ve stok tavanı bu kata taşınmaz.", "",
         "## Parça tablosu (2026-Q1, milyar TL)", "",
         "| Parça | Durum | Stok | Seri | Not |", "| --- | --- | ---: | --- | --- |"]
    for r in rows:
        if r["donem"] != "2026-Q1":
            continue
        durum = "ayrılmadı" if r["stok_milyar"] is None else "bulundu"
        st = "" if r["stok_milyar"] is None else f"{r['stok_milyar']:,.1f}"
        s.append(f"| {r['parca']} | {durum} | {st} | `{r['seri']}` | {r['not']} |")
    s += ["", "## Dönemler", "", "| Dönem | MY VF.2 | TCMB P3111 nakit | TCMB P3112 altın | Banka resmî TL (GY) | GY VF.2 | Hane VF.2 | MY/hane % |",
          "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for d, v in veri.items():
        mb = None if v["mb_p3111_nakit_tl"] is None else v["mb_p3111_nakit_tl"] + (v["mb_p3111_nakit_yp"] or 0)
        au = None if v["mb_p3112_altin_tl"] is None else v["mb_p3112_altin_tl"] + (v["mb_p3112_altin_yp"] or 0)
        f = lambda x: "" if x is None else f"{x:,.1f}"
        pay = "" if (v["my_vf2"] is None or not v["hane_vf2"]) else f"{100*v['my_vf2']/v['hane_vf2']:.1f}"
        s.append(f"| {d} | {f(v['my_vf2'])} | {f(mb)} | {f(au)} | {f(v['banka_resmi_tl'])} | {f(v['gy_vf2'])} | {f(v['hane_vf2'])} | {pay} |")
    s += ["", "## Yanlışlayıcılar", "",
          f"- **H-L:** `{hip['H-L']}` ({hip['H-L_buyukluk']}). {hip['H-L_not']}",
          f"- **H-L2:** `{hip['H-L2']}`. {hip['H-L2_not']}",
          "- **THKH:** ayrılmadı. Dayanak 4749 m.12; CB Kararı 17 (RG 8.8.2018/30500). Stok serisi yok; haberden tutar doldurulmadı.",
          "", "## Sınır", "",
          "- GY toplamı yan sütundur, lider değildir. Resmî kuruluşlar (banka) GY kapsamıdır.",
          "- TCMB P311 = P3111 nakit + P3112 altın; merkez_banka satırı yalnız nakittir. Finansal hesaplarda altın F.1'dir, VF.2'ye girmez.",
          "- Hane 15.357 ve firma stokları lider sütununa girmez. Stok silimi tavanı ve akış %42,7 bu dosyada yok.",
          "", "## Arama günlüğü", "", "| Grup | Sonuç | Not |", "| --- | --- | --- |"]
    s += [f"| `{g['grup']}` | {g['sonuc']} | {g['not']} |" for g in arama_gunlugu()]
    s += ["", "Tekrar: `python3 lider_mevduat.py`. Dosyalar: `lider_mevduat.csv`, `lider_mevduat_sonuc.json`."]
    return "\n".join(s) + "\n"


def main() -> None:
    veri = cek()
    rows = satirlar(veri)
    hip = hipotezler(veri)
    cols = ["donem", "parca", "stok_milyar", "seri", "kaynak_url", "not", "pay_hane_yuzde", "gy_toplam_vf2_milyar", "hane_vf2_milyar"]
    with open(KOK / "lider_mevduat.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in cols})
    sonuc = {"birim": "milyar TL, dönem sonu", "hipotez": hip, "veri": {d: {k: _r(x) for k, x in v.items()} for d, v in veri.items()},
             "yilsonu_altin_metin": ALTIN_YILSONU, "kaynaklar": {"yr2025": URL_YR2025, "yr2024": URL_YR2024, "rg17": URL_RG17, "kimden_kime": URL_KIMDEN},
             "arama_gunlugu": arama_gunlugu()}
    (KOK / "lider_mevduat_sonuc.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8")
    (KOK / "LIDER_MEVDUAT.md").write_text(rapor(rows, hip, veri), encoding="utf-8")
    print(json.dumps(hip, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
