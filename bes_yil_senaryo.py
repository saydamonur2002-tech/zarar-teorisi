"""Beş yıl senaryosu: model uygulandı varsayımı (optimum aralık), 2027–2031.

Ölçüm değil, senaryo. Dört katman, her hücrede ayrı etiket:
  taban      `olculdu`     EVDS son değer (TÜFE yıllık, AOFM, USD/TRY, firma F.4 stoku).
  beklenti   `anket`       EVDS Piyasa Katılımcıları Anketi (bie_pkauo), son ay; ufuk yoksa `bulunamadi`.
  model_etki `varsayim`    depodaki parametreden türetilmiş bant; `modellenmedi` ise boş.
  senaryo    `senaryo`     beklenti + model etkisi; etki boşsa beklentiye eşit; beklenti yoksa boş.

Optimum aralık (model kendi beş adımını tam uygular):
  Adım 3: yeni net kredi itişi 0 (odeme_mahsup kredi_ihtiyaci_sart 0,0 `modellendi`). Itiş tabanı 2025 ölçümü:
          firma F.4 işlem akımı 4.820,9 milyar = 7,62 puan GSYH (tavan_akis.csv). Varsayım: itiş yıllık sabit.
  Adım 1 stok: eski stok silinen ∈ [0, yeni_tavan 0,2582] (adim1_stok.csv; silinen boş, xls yok). Bant uçları: 0 ve üst sınır.
  Enflasyon: tavan = itiş × geçiş (tavan_akis.py). Geçiş payı kapısı boş; bant mantıksal sınırlardan [0, 1], eşik değil.
             varsayim_esik.csv eşikleri (0, 1/3, 1) buraya taşınmaz.
  Faiz: politika faizi (AOFM) mekanizması depoda yok → etki boş. Firma kredi faizinin durması adim3.csv
        satırında, etiket modellendi_varsayim_kappa; AOFM hücresine ve F.4 anapara stokuna yazılmaz.
  Döviz: senet `modellenmedi` (adim4.csv, senet_kilit.txt); dovize_kacis 0,4 parametre, veri değil → etki boş.

Üç kilitli kapı (vade dilimi, ödenmeyen emir, geçiş payı) her yıl `bos`; bu dosya kapıyı doldurmaz.
Çıktı: bes_yil_senaryo.csv, bes_yil_senaryo_sonuc.json, BES_YIL_SENARYO.md, bes_yil_senaryo_ham.json (EVDS önbellek)
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from evds_cek import BASE, get_json

KOK = Path(__file__).resolve().parent
HAM = KOK / "bes_yil_senaryo_ham.json"
TABAN_YIL = 2026
YILLAR = [2027, 2028, 2029, 2030, 2031]
KAPILAR = ("vade_dilimi", "odenmeyen_emir", "gecis_payi")

S_TUFE = "TP.TUKFIY2025.GENEL"
S_AOFM = "TP.APIFON4"
S_USD = "TP.DK.USD.A.YTL"
PK = {  # (seri, ufuk etiketi) — anket ayı 2026-09 ise ufuk yılı
    "enf": {2026: ("TP.PKAUO.S01.D.U", "cari yıl sonu"), 2027: ("TP.PKAUO.S01.I.U", "gelecek yıl sonu"),
            2028: ("TP.PKAUO.S01.F.U", "24 ay sonrası"), 2031: ("TP.PKAUO.S01.G.U", "5 yıl sonrası")},
    "faiz": {2026: ("TP.PKAUO.S04.H.U", "cari yıl sonu"), 2027: ("TP.PKAUO.S04.I.U", "gelecek yıl sonu"),
             2028: ("TP.PKAUO.S04.E.U", "24 ay sonrası")},
    "usd": {2026: ("TP.PKAUO.S05.B.U", "cari yıl sonu"), 2027: ("TP.PKAUO.S05.C.U", "12 ay sonrası")},
}
URL = {"pk": "https://evds3.tcmb.gov.tr/tumSeriler/bie_pkauo", "aofm": "https://evds3.tcmb.gov.tr/tumSeriler/bie_apifon",
       "usd": "https://evds3.tcmb.gov.tr/tumSeriler/bie_dkdovytl", "tufe": "https://evds3.tcmb.gov.tr/tumSeriler/bie_tukfiy2025"}


def _fetch(series: list[str], start="01-01-2024", end="11-10-2026") -> dict[str, dict[str, float]]:
    body = {"type": "json", "series": "-".join(series), "aggregationTypes": "-".join("last" for _ in series),
            "formulas": "-".join("0" for _ in series), "startDate": start, "endDate": end, "frequency": "5",
            "decimalSeperator": ".", "decimal": "4", "dateFormat": "0", "lang": "TR", "yon": "0", "sira": "0",
            "ozelFormuller": [], "groupSeperator": False, "isRaporSayfasi": False}
    d = get_json(f"{BASE}/fe", body)
    out: dict[str, dict[str, float]] = {}
    for it in d["items"]:
        for s in series:
            v = it.get(s.replace(".", "_"))
            if v not in (None, ""):
                out.setdefault(str(it["Tarih"]), {})[s] = float(str(v).replace(",", ""))
    return out


def evds() -> dict:
    seriler = [S_TUFE, S_AOFM, S_USD] + [s for grp in PK.values() for s, _ in grp.values()]
    try:
        ham = _fetch(seriler)
        HAM.write_text(json.dumps(ham, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 — çevrimdışıysa önbellek
        if not HAM.exists():
            raise
        print(f"EVDS alınamadı ({exc}); önbellek {HAM.name}")
        ham = json.loads(HAM.read_text(encoding="utf-8"))

    def son(s):
        t = max(k for k, v in ham.items() if s in v)
        return t, ham[t][s]

    t_enf, endeks = son(S_TUFE)
    y, m = t_enf.split("-")
    onceki = ham.get(f"{int(y) - 1}-{m}", {}).get(S_TUFE)
    enf_yillik = round((endeks / onceki - 1) * 100, 2) if onceki else None
    t_pk = max(k for k, v in ham.items() if PK["enf"][2026][0] in v)
    bek = {g: {yil: ham[t_pk].get(s) for yil, (s, _) in grp.items()} for g, grp in PK.items()}
    return {"tufe": {"tarih": t_enf, "yillik": enf_yillik, "onceki_endeks_var": onceki is not None},
            "aofm": dict(zip(("tarih", "deger"), son(S_AOFM))), "usd": dict(zip(("tarih", "deger"), son(S_USD))),
            "anket_ayi": t_pk, "beklenti": bek}


def depo() -> dict:
    kop = list(csv.DictReader((KOK / "tek_sistem_kopru.csv").open(encoding="utf-8-sig")))
    f4 = next(r for r in kop if r["blok"] == "mutabakat" and r["donem"] == "2026-Q1" and r["evds_anahtar"] == "F_F4_yuk")
    ta = next(r for r in csv.DictReader((KOK / "tavan_akis.csv").open(encoding="utf-8-sig")) if r["yil"] == "2025")
    a1 = json.loads((KOK / "bes_adim_sonuc.json").read_text(encoding="utf-8"))["adimlar"]["1"]
    om = json.loads((KOK / "odeme_mahsup_sonuc.json").read_text(encoding="utf-8"))
    a3 = list(csv.DictReader((KOK / "adim3.csv").open(encoding="utf-8-sig")))
    a4 = list(csv.DictReader((KOK / "adim4.csv").open(encoding="utf-8-sig")))
    senet = next(r for r in a4 if "senet" in r["nesne"])
    return {"stok_2026q1": float(f4["evds_milyar"]), "itis_milyar_2025": float(ta["f4_akim"]), "itis_puan_gsyh_2025": float(ta["oran_akim"]),
            "gecis_bos": ta["gecis"] == "" and ta["tavan"] == "", "yeni_tavan": a1["yeni_tavan"], "eski_tavan": a1["eski_tavan"],
            "silinen_bos": a1["silinen"] is None, "kredi_ihtiyaci_sart": om["ozet"]["kredi_ihtiyaci_sart"],
            "dovize_kacis_parametre": om["parametreler"]["dovize_kacis"],
            "faiz_durmasi": "firma stok faizi modellendi_varsayim_kappa" if any(r["durum"] == "modellendi_varsayim_kappa" for r in a3) else "Faizin durması modellenmedi",
            "senet_durum": senet["durum"], "senet_kilit": (KOK / "senet_kilit.txt").read_text(encoding="utf-8").strip()}


def satirlar(ev: dict, dp: dict) -> list[dict]:
    rows: list[dict] = []
    kapi = {k: "bos" for k in KAPILAR}
    itis = dp["itis_puan_gsyh_2025"]
    akim = dp["itis_milyar_2025"]
    stok0 = dp["stok_2026q1"]
    tav = dp["yeni_tavan"]

    def ek(yil, degisken, taban, taban_tarih, taban_seri, bek, bek_seri, bek_ufuk, etki_alt, etki_ust, etki_durum, birim, varsayim, not_):
        if bek is None:
            sen_alt = sen_ust = None; bek_durum = "bulunamadi"
        else:
            bek_durum = "anket"
            sen_alt = round(bek + (etki_alt or 0), 2) if etki_durum != "modellenmedi" else round(bek, 2)
            sen_ust = round(bek + (etki_ust or 0), 2) if etki_durum != "modellenmedi" else round(bek, 2)
        rows.append({"yil": yil, "degisken": degisken, "taban": taban, "taban_tarih": taban_tarih, "taban_seri": taban_seri, "taban_durum": "olculdu",
                     "beklenti": bek, "beklenti_seri": bek_seri, "beklenti_ufuk": bek_ufuk, "beklenti_durum": bek_durum,
                     "model_etki_alt": etki_alt, "model_etki_ust": etki_ust, "model_etki_durum": etki_durum,
                     "senaryo_alt": sen_alt, "senaryo_ust": sen_ust, "senaryo_durum": "senaryo" if bek is not None else "bos",
                     "birim": birim, **kapi, "varsayim": varsayim, "not": not_})

    for yil in [TABAN_YIL] + YILLAR:
        t = yil - TABAN_YIL
        model = t >= 1
        # enflasyon
        s, ufuk = PK["enf"].get(yil, (None, None))
        bek = ev["beklenti"]["enf"].get(yil)
        ek(yil, "enflasyon_tufe_yillik", ev["tufe"]["yillik"], ev["tufe"]["tarih"], S_TUFE, bek, s, ufuk,
           -round(itis, 2) if model else None, 0.0 if model else None, "varsayim" if model else "taban_yili",
           "yüzde puan (yıllık TÜFE)",
           "itiş 2025 = 7,62 puan GSYH sabit; model itişi 0'a çeker; etki = −geçiş×itiş; geçiş ∈ [0,1] mantıksal sınır, kapı boş" if model else "",
           "Alt uç geçiş 1, üst uç geçiş 0. Eşik değil. 2029–2030 anket ufku yok." if model else "Taban: TÜFE 2025=100 yıllık değişim; anket cari yıl sonu.")
        # faiz
        s, ufuk = PK["faiz"].get(yil, (None, None))
        bek = ev["beklenti"]["faiz"].get(yil)
        ek(yil, "faiz_politika", ev["aofm"]["deger"], ev["aofm"]["tarih"], S_AOFM, bek, s, ufuk, None, None,
           "modellenmedi" if model else "taban_yili", "yüzde",
           "" , f"Politika faizi (AOFM) mekanizması depoda yok. {dp['faiz_durmasi']}; firma kredi stoğu içindir, AOFM hücresine yazılmaz. Senaryo = anket." if model else "Taban: AOFM son ay.")
        # döviz
        s, ufuk = PK["usd"].get(yil, (None, None))
        bek = ev["beklenti"]["usd"].get(yil)
        ek(yil, "doviz_usd_try", ev["usd"]["deger"], ev["usd"]["tarih"], S_USD, bek, s, ufuk, None, None,
           "modellenmedi" if model else "taban_yili", "TL/USD", "",
           f"Senet {dp['senet_durum']} (kilit {dp['senet_kilit']}); dovize_kacis {dp['dovize_kacis_parametre']} parametre, veri değil. Senaryo = anket." if model
           else "Taban: USD döviz alış son ay.")
        # stok
        if model:
            model_yok = round(stok0 + akim * t, 1)
            alt = round(stok0 * (1 - tav), 1)   # silinen üst sınırda
            ust = round(stok0, 1)               # silinen 0
            rows.append({"yil": yil, "degisken": "stok_firma_f4_kredi", "taban": stok0, "taban_tarih": "2026-Q1", "taban_seri": "TP.FINHESTNKS11.ZP34",
                         "taban_durum": "olculdu", "beklenti": model_yok, "beklenti_seri": "TP.FINHESTNKS62011.ZP34", "beklenti_ufuk": f"model yok: 2026-Q1 + 2025 akımı × {t}",
                         "beklenti_durum": "varsayim", "model_etki_alt": round(alt - model_yok, 1), "model_etki_ust": round(ust - model_yok, 1),
                         "model_etki_durum": "varsayim", "senaryo_alt": alt, "senaryo_ust": ust, "senaryo_durum": "senaryo", "birim": "milyar TL (nominal)",
                         **kapi, "varsayim": f"yeni itiş 0 (kredi_ihtiyaci_sart {dp['kredi_ihtiyaci_sart']}); eski stok silinen ∈ [0, {tav}] tek sefer; stok sütunu anapara, duran faiz stoktan düşülmez",
                         "not": f"Alt uç yeni_tavan {tav} üst sınırında, üst uç silinen 0. Silinen boş, xls yok. 'Model yok' sütunu 2025 nominal akımı sabit varsayımı; GSYH yolu yok."})
        else:
            rows.append({"yil": yil, "degisken": "stok_firma_f4_kredi", "taban": stok0, "taban_tarih": "2026-Q1", "taban_seri": "TP.FINHESTNKS11.ZP34",
                         "taban_durum": "olculdu", "beklenti": None, "beklenti_seri": None, "beklenti_ufuk": None, "beklenti_durum": "taban_yili",
                         "model_etki_alt": None, "model_etki_ust": None, "model_etki_durum": "taban_yili", "senaryo_alt": None, "senaryo_ust": None,
                         "senaryo_durum": "bos", "birim": "milyar TL (nominal)", **kapi, "varsayim": "", "not": "Taban: firma F.4 kredi yükümlülüğü, konsolide olmayan."})
    return rows


def kontrol(rows: list[dict], dp: dict) -> dict:
    hy1 = "temiz" if all(r["senaryo_durum"] in ("senaryo", "bos") for r in rows) and not any(r["model_etki_durum"] == "olculdu" for r in rows) else "ihlal"
    hy2 = "temiz" if (dp["gecis_bos"] and all(r[k] == "bos" for r in rows for k in KAPILAR)) else "ihlal"
    hy3 = "temiz" if (dp["silinen_bos"] and dp["senet_durum"] == "modellenmedi" and dp["senet_kilit"] == "modellenmedi") else "ihlal"
    return {"H-Y1": hy1, "H-Y1_not": "senaryo hücresi ölçüm etiketi taşımaz",
            "H-Y2": hy2, "H-Y2_not": "üç kapı boş; geçiş sayısı yazılmadı",
            "H-Y3": hy3, "H-Y3_not": "silinen boş, senet kilidi duruyor"}


def md(rows: list[dict], ev: dict, dp: dict, kn: dict) -> str:
    f = lambda x, n=2: "" if x is None else f"{x:,.{n}f}"
    s = ["# Beş yıl senaryosu: model uygulandı varsayımı, optimum aralık (2027–2031)", "",
         "Senaryo; ölçüm değil. Çalıştır: `python3 bes_yil_senaryo.py`. Çıktı: `bes_yil_senaryo.csv`, `bes_yil_senaryo_sonuc.json`.", "",
         f"Taban: TÜFE yıllık {f(ev['tufe']['yillik'])} ({ev['tufe']['tarih']}); AOFM {f(ev['aofm']['deger'], 1)} ({ev['aofm']['tarih']}); "
         f"USD/TRY {f(ev['usd']['deger'])} ({ev['usd']['tarih']}); firma F.4 stoku {f(dp['stok_2026q1'], 1)} milyar (2026-Q1). "
         f"Beklenti: EVDS Piyasa Katılımcıları Anketi, {ev['anket_ayi']}.", "",
         "Optimum aralık tanımı: model beş adımı tam uygular; yeni kredi itişi 0 (adım 3), eski stok silinen 0 ile yeni_tavan 0,2582 arası (adım 1 stok). "
         "Geçiş payı kapısı boş; enflasyon etkisi mantıksal sınırlarla [0, 1] bant olarak verilir. Politika faizi ve döviz için model etkisi `modellenmedi`; senaryo anket beklentisine eşit. Firma kredi faizinin durması ayrı satırdadır.", "",
         "## Tablo (alt / üst)", "",
         "| Yıl | Değişken | Taban | Beklenti / model yok | Model etkisi | Senaryo | Etki etiketi | Üç kapı |",
         "| ---: | --- | ---: | ---: | ---: | ---: | --- | --- |"]
    for r in rows:
        bek = f(r["beklenti"], 1 if "stok" in r["degisken"] else 2) if r["beklenti"] is not None else f"— ({r['beklenti_durum']})"
        etki = f"{f(r['model_etki_alt'], 1 if 'stok' in r['degisken'] else 2)} / {f(r['model_etki_ust'], 1 if 'stok' in r['degisken'] else 2)}" if r["model_etki_alt"] is not None else "—"
        sen = f"{f(r['senaryo_alt'], 1 if 'stok' in r['degisken'] else 2)} / {f(r['senaryo_ust'], 1 if 'stok' in r['degisken'] else 2)}" if r["senaryo_alt"] is not None else "—"
        s.append(f"| {r['yil']} | {r['degisken']} | {f(r['taban'], 1 if 'stok' in r['degisken'] else 2)} | {bek} | {etki} | {sen} | {r['model_etki_durum']} | "
                 f"{', '.join(r[k] for k in KAPILAR)} |")
    s += ["", "## Üç kilitli ölçüt, yıl yıl", "",
          "- Vade dilimi: `bos`. MY vade kırılımı 'ayrılmadı', ortalama gün boş (vadeli_kalicilik.csv). Adım 2 ödeme planının süresi bu yüzden yazılmaz.",
          "- Ödenmeyen emir: `bos`. Kamu bacağı ölçüsü yok. Senaryoda kamu satırı yok.",
          "- Geçiş payı: `bos`. Enflasyon bandının hangi ucunun geçerli olduğu bu kapıya bağlı; kapı boşken tek sayı yazılmaz.", "",
          "## Yanlışlayıcılar", "",
          f"- **H-Y1** (senaryo ölçüm diye yazılır): `{kn['H-Y1']}`. {kn['H-Y1_not']}.",
          f"- **H-Y2** (kapı doldurulur): `{kn['H-Y2']}`. {kn['H-Y2_not']}.",
          f"- **H-Y3** (silinen veya senet dolar): `{kn['H-Y3']}`. {kn['H-Y3_not']}.", "",
          "## Varsayımlar (ölçüm değil)", "",
          "- İtiş 2025 değeri (4.820,9 milyar; 7,62 puan GSYH) beş yıl nominal sabit. GSYH yolu yok; stok sütunu nominal, GSYH payı verilmez.",
          "- Model 2027 başında tam uygulanır; etki her yıl aynı. Geçiş süresi, kısmi uygulama yok.",
          "- Enflasyon etkisi: −geçiş × 7,62; geçiş 0 ve 1 mantıksal uç. varsayim_esik.csv eşikleri (0, 1/3, 1) buraya taşınmadı.",
          "- 2029–2030 için anket ufku yok; beklenti `bulunamadi`, senaryo boş. 2031 yalnız TÜFE (5 yıl sonrası).",
          "- Stok sütunu anaparadır. Duran faiz `adim3.csv` satırında, etiket `modellendi_varsayim_kappa`; stoktan düşülmez. Politika faizi (AOFM) mekanizması yoktur.", "",
          "## Ne denmez", "",
          "- 'Enflasyon 7,6 puan iner' denmez. Bant [0, −7,62]; geçiş kapısı boş.",
          "- 'Stok yüzde 26 silindi' denmez. Tavan 0,2582 üst sınır; silinen boş.",
          "- 'Faiz düşer', 'kur durur' denmez. İkisi `modellenmedi`; senaryo anket beklentisidir.",
          "- Anket beklentisi gerçekleşme değil; EVDS katılımcı ortalaması."]
    return "\n".join(s) + "\n"


def main() -> None:
    ev = evds()
    dp = depo()
    rows = satirlar(ev, dp)
    kn = kontrol(rows, dp)
    alan = ["yil", "degisken", "taban", "taban_tarih", "taban_seri", "taban_durum", "beklenti", "beklenti_seri", "beklenti_ufuk", "beklenti_durum",
            "model_etki_alt", "model_etki_ust", "model_etki_durum", "senaryo_alt", "senaryo_ust", "senaryo_durum", "birim", *KAPILAR, "varsayim", "not"]
    with (KOK / "bes_yil_senaryo.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=alan)
        w.writeheader()
        for r in rows:
            w.writerow({a: ("" if r.get(a) is None else r.get(a)) for a in alan})
    (KOK / "bes_yil_senaryo_sonuc.json").write_text(json.dumps(
        {"durum": "senaryo", "taban": ev, "depo_parametre": dp, "kaynak_url": URL, "kontrol": kn, "satirlar": rows},
        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (KOK / "BES_YIL_SENARYO.md").write_text(md(rows, ev, dp, kn), encoding="utf-8")
    print("=== Beş yıl senaryosu (senaryo; ölçüm değil) ===")
    for r in rows:
        if r["yil"] == TABAN_YIL or r["senaryo_alt"] is not None or r["beklenti_durum"] == "bulunamadi":
            print(f"{r['yil']} {r['degisken']:<24} taban {str(r['taban']):>9} bek {str(r['beklenti']):>9} etki [{r['model_etki_alt']}, {r['model_etki_ust']}] "
                  f"senaryo [{r['senaryo_alt']}, {r['senaryo_ust']}] {r['model_etki_durum']}/{r['beklenti_durum']}")
    print(kn)


if __name__ == "__main__":
    main()
