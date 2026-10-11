"""Hazine vadeli mevduat ve kalıcılık testi (H-K1, H-K2).

Kalıcılık: ödeme emri günü ile nakdin 102 hesaba geçtiği gün arasındaki süre.
Hazine vadeli mevduatı: merkezi yönetim (S.1311) VF.2 vadeli bakiyesi (TP.FINHESTNKS1311.ZP8).
Üç kapı: (1) MY vadeli vade kırılımı, (2) THKH ayrımı, (3) ödenmeyen ödeme emri tutarı ve gün sayısı.
Akış %42,7, stok tavanı 18.846 ve lider mevduat 2.933,6 bu teste girmez.
Birim milyar TL, dönem sonu. Boş hücre boş kalır.
Çıktı: vadeli_kalicilik.csv, vadeli_kalicilik_sonuc.json, VADELI_KALICILIK.md
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from evds_cek import BASE, get_json

KOK = Path(__file__).resolve().parent
DONEMLER = ("2024-Q4", "2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4", "2026-Q1")
URL_MY = "https://evds3.tcmb.gov.tr/tumSeriler/bie_finhestnks1311"
URL_DTHVADE = "https://www.tcmb.gov.tr/wps/wcm/connect/81869b75-a522-40cd-a026-a65621d43510/dthvade.html?MOD=AJPERES"
URL_BDDK = "https://www.bddk.org.tr/bultenaylik"
URL_MYMY = "https://www.mevzuat.gov.tr/MevzuatMetin/yonetmelik/7.5.20357.pdf"
URL_GIB_MIZAN = "https://cdn.gib.gov.tr/api/gibportal-file/file/getFileResources?objectKey=arsiv%2Fkurumsal%2Fpdfs%2FmaliTablolar%2F2025%2Feylul%2FMizan_Son_Duzey.pdf"
URL_ADANA = "https://www.sayistay.gov.tr/reports/download/xLYGeJjgp4-adana-buyuksehir-belediyesi"
URL_SAYISTAY_HMB = "https://www.sayistay.gov.tr/reports/download/9XQWOwBQpN-hazine-ve-maliye-bakanligi"

S = {"vf2": "TP.FINHESTNKS1311.ZP5", "para": "TP.FINHESTNKS1311.ZP6", "vadesiz": "TP.FINHESTNKS1311.ZP7",
     "vadeli": "TP.FINHESTNKS1311.ZP8", "f2": "TP.FINHESTNKS1311.ZP27", "f2_vadeli": "TP.FINHESTNKS1311.ZP30",
     "tcmb_f2_vadeli": "TP.FINHESTNKS121.ZP30", "resmi_vadesiz_tl": "TP.HPBITABLO3.10", "resmi_vadeli_tl": "TP.HPBITABLO3.11"}
Q_AY = {"Q1": "03", "Q2": "06", "Q3": "09", "Q4": "12"}


def _fetch(series: list[str], freq: str) -> dict[str, dict[str, float]]:
    body = {"type": "json", "series": "-".join(series), "aggregationTypes": "-".join("last" for _ in series),
            "formulas": "-".join("0" for _ in series), "startDate": "01-10-2024", "endDate": "10-10-2026", "frequency": freq,
            "decimalSeperator": ".", "decimal": "4", "dateFormat": "0", "lang": "TR", "yon": "0", "sira": "0",
            "ozelFormuller": [], "groupSeperator": False, "isRaporSayfasi": False}
    out: dict[str, dict[str, float]] = {}
    for it in get_json(f"{BASE}/fe", body)["items"]:
        for s in series:
            v = it.get(s.replace(".", "_"))
            if v not in (None, ""):
                out.setdefault(str(it["Tarih"]), {})[s] = float(str(v).replace(",", "")) / 1e6
    return out


def cek() -> dict[str, dict[str, float | None]]:
    q = _fetch([S[k] for k in ("vf2", "para", "vadesiz", "vadeli", "f2", "f2_vadeli", "tcmb_f2_vadeli")], "6")
    m = _fetch([S["resmi_vadesiz_tl"], S["resmi_vadeli_tl"]], "5")
    veri = {}
    for d in DONEMLER:
        ay = f"{d[:4]}-{Q_AY[d[-2:]]}"
        row = {k: q.get(d, {}).get(S[k]) for k in ("vf2", "para", "vadesiz", "vadeli", "f2", "f2_vadeli", "tcmb_f2_vadeli")}
        row["resmi_vadesiz_tl"] = m.get(ay, {}).get(S["resmi_vadesiz_tl"])
        row["resmi_vadeli_tl"] = m.get(ay, {}).get(S["resmi_vadeli_tl"])
        veri[d] = row
    return veri


def r1(x):
    return None if x is None else round(x, 1)


KAPILAR = {
    "1_vade_gunu": {
        "durum": "ayrılmadı",
        "not": ("Merkezi yönetim vadeli mevduatın vade dilimi kırılımı (1 aya kadar / 1–3 / 3–6 / 6–12 / 12+) EVDS'de yok. "
                "Finansal hesaplar yalnız vadesiz/vadeli (ZP7/ZP8). TCMB 'dthvade' ve BDDK aylık bülten vade dilimini sektör toplamı için verir; "
                "tür × vade çaprazı yayımlanmaz. HPB tablo 3 resmî kuruluşlar vadesiz/vadeli (TL) GY kapsamıdır, MY diye kullanılmadı."),
        "kaynak": f"{URL_DTHVADE} ; {URL_BDDK}",
    },
    "2_thkh": {
        "durum": "ayrılmadı",
        "not": ("THKH bakiyesi için ayrı kamu serisi yok (lider_mevduat katmanı: 6 grup kodu + 2 web sorgusu). "
                "GY–GY 352 ve MY F.2 (ZP27) aday notunda kalır; vadeli diye etiketlenmez. MY F.2 vadeli (ZP30) ölçülüdür ama ihraç tarafıdır, tutulan vadeli değildir."),
        "kaynak": URL_MY,
    },
    "3_odenmeyen_emir": {
        "durum": "bulunamadı",
        "not": ("Merkezi yönetim konsolide 320 Bütçe Emanetleri ve 103 Verilen Çekler ve Gönderme Emirleri bakiyesi 2025-Q2 ve Q3 için bulunamadı. "
                "Muhasebat portalı (/portal/v2 pages: genel-yonetim-mali-istatistikleri, mali-istatistikler-gfsm-2014e-uyumlu, "
                "merkezi-yonetim-alt-sektoru-mali-istatistikleri) dosya bağlantısı vermiyor; 3 sayfa + 3 arama denendi. "
                "Bulunan ama testin nesnesi olmayan: GİB Eylül 2025 kurum mizanı (103 hesabı dönem hareketi ~525 milyar, bakiye 0,11; 320 bakiye 0,05) kurum düzeyidir; "
                "Sayıştay Adana BB 2024 raporu 320 bekleme gün tablosu belediyedir. Sayıştay HMB raporunda gün sayısı yok. Gün sayısı hiçbir kaynakta MY için yayımlanmıyor."),
        "kaynak": f"{URL_MYMY} ; {URL_GIB_MIZAN} ; {URL_ADANA} ; {URL_SAYISTAY_HMB}",
    },
}


def hipotez(veri: dict) -> dict:
    q2, q3 = veri["2025-Q2"], veri["2025-Q3"]
    d_vadeli = q3["vadeli"] - q2["vadeli"]
    d_vadesiz = q3["vadesiz"] - q2["vadesiz"]
    return {
        "girdi": {"2025-Q2_vadeli": r1(q2["vadeli"]), "2025-Q3_vadeli": r1(q3["vadeli"]), "2025-Q2_vadesiz": r1(q2["vadesiz"]),
                  "2025-Q3_vadesiz": r1(q3["vadesiz"]), "d_vadeli": r1(d_vadeli), "d_vadesiz": r1(d_vadesiz), "d_vf2": r1(q3["vf2"] - q2["vf2"])},
        "H-K1": "test_edilemez",
        "H-K1_not": "Vadeli arttı (+%.1f), vadesiz düştü (%.1f). Ödenmeyen emir ve gün ölçülmedi (kapı 3 bulunamadı). Vadeli artış tek başına lehte yazılmaz." % (d_vadeli, d_vadesiz),
        "H-K2": "ayri_stok",
        "H-K2_not": ("THKH serisi yok; sıçrama THKH ile eşleştirilemedi. Kural gereği etiket ayri_stok; bu 'ayrı olduğu gösterildi' değil "
                     "'eşleşme gösterilemedi' demektir. Kalıcılık cümlesi düşer: THKH dışı vadeli, kurum ödemesini kilitlemez."),
        "yan_olcum": {"tcmb_f2_vadeli_2025-Q3": r1(q3["tcmb_f2_vadeli"]), "my_f2_vadeli_2025-Q3": r1(q3["f2_vadeli"]),
                      "d_tcmb_f2_vadeli_Q2_Q3": r1(q3["tcmb_f2_vadeli"] - q2["tcmb_f2_vadeli"]),
                      "not": ("TCMB vadeli mevduat ihraç eder (F.2 vadeli). Q2→Q3 TCMB F.2 vadeli %+.1f, MY VF.2 vadeli %+.1f; eş hareket ölçüldü, "
                              "karşı taraf eşlemesi kimden-kime'de yok, bu yüzden eşitlenmez.") % (q3["tcmb_f2_vadeli"] - q2["tcmb_f2_vadeli"], d_vadeli)},
    }


def rapor(veri: dict, hip: dict) -> str:
    s = ["# Hazine vadeli mevduat ve kalıcılık", "",
         "Kalıcılık: ödeme emri günü → nakdin 102 hesaba geçtiği gün. Vadeli: MY VF.2 vadeli (`TP.FINHESTNKS1311.ZP8`). "
         "Borç faizi ve bankanın Hazine'ye ödediği faiz konu dışı. Akış, stok tavanı, lider mevduat bu teste girmez.", "",
         "## Üç kapı", "", "| Kapı | Durum | Not |", "| --- | --- | --- |"]
    s += [f"| {k} | **{v['durum']}** | {v['not']} |" for k, v in KAPILAR.items()]
    s += ["", "## Gözlenen (milyar TL, dönem sonu)", "",
          "| Dönem | Vadeli | Vadesiz | Para | VF.2 | MY F.2 vadeli (ihraç) | TCMB F.2 vadeli (ihraç) | Resmî TL vadeli, banka (GY) |",
          "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    f = lambda x: "" if x is None else f"{x:,.1f}"
    for d, v in veri.items():
        s.append(f"| {d} | {f(v['vadeli'])} | {f(v['vadesiz'])} | {f(v['para'])} | {f(v['vf2'])} | {f(v['f2_vadeli'])} | {f(v['tcmb_f2_vadeli'])} | {f(v['resmi_vadeli_tl'])} |")
    g = hip["girdi"]
    s += ["", f"2025-Q2 → Q3: vadeli {g['2025-Q2_vadeli']:,.1f} → {g['2025-Q3_vadeli']:,.1f} ({g['d_vadeli']:+,.1f}); "
          f"vadesiz {g['2025-Q2_vadesiz']:,.1f} → {g['2025-Q3_vadesiz']:,.1f} ({g['d_vadesiz']:+,.1f}); VF.2 {g['d_vf2']:+,.1f}. Sıçrama girdidir, nedeni değil.",
          "", "## Yanlışlayıcılar", "",
          f"- **H-K1:** `{hip['H-K1']}`. {hip['H-K1_not']}",
          f"- **H-K2:** `{hip['H-K2']}`. {hip['H-K2_not']}",
          f"- Yan ölçüm: {hip['yan_olcum']['not']}",
          "", "## Arama günlüğü", "",
          "| Nerede | Ne | Sonuç |", "| --- | --- | --- |",
          "| EVDS grup | bie_finhestnks1311 (ZP5–ZP8, ZP27–ZP30) | açıldı; vadesiz/vadeli var, vade dilimi yok |",
          "| EVDS grup | bie_hpbitablo3 (3.9–3.11) | açıldı; resmî vadesiz/vadeli TL, GY kapsamı |",
          "| EVDS grup | bie_mevdvade, bie_mevvade, bie_mevduatvade, bie_vademev, bie_mkvade, bie_pbvade, bie_hpbvade, bie_tlmevvade, bie_vadedag, bie_mevdagilim, bie_bddkmev, bie_bddkvade, bie_mbvade, bie_pbmv, bie_mevduatvadeli | boş (15 kod) |",
          "| EVDS grup | bie_zorundth | açıldı; ZK'ya tabi DTH 1 ay altı/üstü, sektör toplamı |",
          "| TCMB | dthvade.html | sektör vade dilimi, tür çaprazı yok |",
          "| BDDK | Aylık bülten: Mevduat Türler İtibarıyla / Vade İtibarıyla | ayrı tablolar, çapraz yok |",
          "| Muhasebat | /portal/v2 pages ×3, posts arama | GFSM sayfaları dosya vermiyor; 320/103 konsolide bakiye yok |",
          "| GİB | Eylül 2025 Mizan_Son_Duzey.pdf | kurum düzeyi 103/320; MY değil |",
          "| Sayıştay | HMB 2021 denetim raporu | 320/103 gün bulgusu yok |",
          "| Sayıştay | Adana BB 2024 | 320 bekleme gün tablosu; belediye, MY değil |",
          "", "Tekrar: `python3 vadeli_kalicilik.py`. Dosyalar: `vadeli_kalicilik.csv`, `vadeli_kalicilik_sonuc.json`."]
    return "\n".join(s) + "\n"


def main() -> None:
    veri = cek()
    hip = hipotez(veri)
    cols = ["donem", "vadeli_milyar", "vadesiz_milyar", "vade_kirilim", "thkh_ayrildi", "odenmeyen_emir_milyar", "ortalama_gun", "kaynak_url"]
    with open(KOK / "vadeli_kalicilik.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for d, v in veri.items():
            w.writerow({"donem": d, "vadeli_milyar": r1(v["vadeli"]), "vadesiz_milyar": r1(v["vadesiz"]), "vade_kirilim": "ayrılmadı",
                        "thkh_ayrildi": "ayrılmadı", "odenmeyen_emir_milyar": "", "ortalama_gun": "", "kaynak_url": URL_MY})
    sonuc = {"birim": "milyar TL, dönem sonu", "kapilar": KAPILAR, "hipotez": hip,
             "veri": {d: {k: r1(x) for k, x in v.items()} for d, v in veri.items()}}
    (KOK / "vadeli_kalicilik_sonuc.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8")
    (KOK / "VADELI_KALICILIK.md").write_text(rapor(veri, hip), encoding="utf-8")
    print(json.dumps(hip, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
