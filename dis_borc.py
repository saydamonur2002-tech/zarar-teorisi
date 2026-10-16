"""Dış borçta sahip ve ödeyen. Kurallar DIS_BORC_ONKAYIT.md.

Değerleme satırı yoksa artık yazılmaz. Kısa vade brüt ödemesi yoksa S2 yazılmaz.
"""

from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

from evds_cek import BASE, get_json

KOK = Path(__file__).resolve().parent
SON = "16-10-2026"
TOL = 0.01

STOK = {
    "sdds_toplam": "TP.BRUTDBSDDS.G1",
    "sdds_gh": "TP.BRUTDBSDDS.G2",
    "sdds_tcmb": "TP.BRUTDBSDDS.G16",
    "sdds_banka": "TP.BRUTDBSDDS.G30",
    "sdds_diger": "TP.BRUTDBSDDS.G43",
    "sdds_dy": "TP.BRUTDBSDDS.G56",
    "sdds_gh_kisa": "TP.BRUTDBSDDS.G3",
    "sdds_tcmb_kisa": "TP.BRUTDBSDDS.G17",
    "sdds_banka_kisa": "TP.BRUTDBSDDS.G31",
    "sdds_diger_kisa": "TP.BRUTDBSDDS.G44",
    "borclu_toplam": "TP.BRUTDBORCLU.G1",
    "borclu_kamu": "TP.BRUTDBORCLU.G2",
    "borclu_gh": "TP.BRUTDBORCLU.G3",
    "borclu_kamu_banka": "TP.BRUTDBORCLU.G8",
    "borclu_tcmb": "TP.BRUTDBORCLU.G13",
    "borclu_ozel": "TP.BRUTDBORCLU.G14",
    "borclu_ozel_banka": "TP.BRUTDBORCLU.G16",
    "borclu_kisa": "TP.BRUTDBORCLU.G19",
    "kur_toplam": "TP.BRUTDBDOVKOMP.G1",
    "kur_usd": "TP.BRUTDBDOVKOMP.G2",
    "kur_eur": "TP.BRUTDBDOVKOMP.G3",
    "kur_jpy": "TP.BRUTDBDOVKOMP.G4",
    "kur_sdr": "TP.BRUTDBDOVKOMP.G5",
    "kur_tl": "TP.BRUTDBDOVKOMP.G6",
    "kur_diger": "TP.BRUTDBDOVKOMP.G7",
}
AKIM = {
    "tcmb_uzun_kullanim": "TP.ODEAYRSUNUM6.Q164",
    "tcmb_uzun_odeme": "TP.ODEAYRSUNUM6.Q165",
    "tcmb_imf_kullanim": "TP.ODEAYRSUNUM6.Q160",
    "tcmb_imf_odeme": "TP.ODEAYRSUNUM6.Q161",
    "banka_uzun_kullanim": "TP.ODEAYRSUNUM6.Q169",
    "banka_uzun_odeme": "TP.ODEAYRSUNUM6.Q170",
    "gh_uzun_kullanim": "TP.ODEAYRSUNUM6.Q177",
    "gh_uzun_odeme": "TP.ODEAYRSUNUM6.Q178",
    "gh_imf_kullanim": "TP.ODEAYRSUNUM6.Q173",
    "gh_imf_odeme": "TP.ODEAYRSUNUM6.Q174",
    "diger_uzun_kullanim": "TP.ODEAYRSUNUM6.Q182",
    "diger_uzun_odeme": "TP.ODEAYRSUNUM6.Q183",
    "hata_noksan": "TP.ODEAYRSUNUM6.Q210",
    "banka_kisa_net": "TP.ODEAYRSUNUM6.Q167",
    "gh_kisa_net": "TP.ODEAYRSUNUM6.Q175",
    "diger_kisa_net": "TP.ODEAYRSUNUM6.Q180",
    "tcmb_kisa_net": "TP.ODEAYRSUNUM6.Q162",
}
KVDB = {
    "kvdb_tcmb": "TP.KALANVADE.K1",
    "kvdb_gh": "TP.KALANVADE.K4",
    "kvdb_banka": "TP.KALANVADE.K5",
    "kvdb_diger": "TP.KALANVADE.K12",
    "kvdb_toplam": "TP.KALANVADE.K20",
}


def cek(kodlar: list[str], freq: str, agg: str) -> tuple[dict, dict]:
    out = {k: {} for k in kodlar}
    ad = {}
    for kod in kodlar:
        body = {
            "type": "json", "series": kod, "aggregationTypes": agg, "formulas": "0",
            "startDate": "01-01-1989", "endDate": SON, "frequency": freq,
            "decimalSeperator": ".", "decimal": "4", "dateFormat": "0", "lang": "TR",
            "yon": "0", "sira": "0", "ozelFormuller": [], "groupSeperator": False,
            "isRaporSayfasi": False,
        }
        try:
            data = get_json(f"{BASE}/fe", body)
        except Exception as exc:  # noqa: BLE001
            ad[kod] = f"hata:{exc}"[:180]
            continue
        key = kod.replace(".", "_")
        ad[kod] = (data.get("seriesNames") or {}).get(key)
        for it in data.get("items") or []:
            v = it.get(key)
            if v not in (None, ""):
                out[kod][str(it.get("Tarih"))] = float(str(v).replace(",", ""))
    return out, ad


def ortak(seri: dict, kodlar: list[str]) -> list[str]:
    kume = None
    for k in kodlar:
        tarihler = set(seri[k])
        kume = tarihler if kume is None else kume & tarihler
    return sorted(kume or [])


def yil_ay(tarih: str) -> tuple[int, int] | None:
    if "-Q" in tarih:
        y, q = tarih.split("-Q")
        return int(y), int(q) * 3
    parca = tarih.split("-")
    if len(parca) == 2 and len(parca[0]) == 4:
        return int(parca[0]), int(parca[1])
    return None


def ceyrek_sonu_ay(tarih: str) -> str | None:
    """Çeyrek etiketini KVDB ayına çevirir: 2024-Q4 -> 2024-12."""
    ya = yil_ay(tarih)
    if not ya:
        return None
    return f"{ya[0]:04d}-{ya[1]:02d}"


def tam_yillar(aylik: dict) -> list[int]:
    say = {}
    for t in aylik:
        ya = yil_ay(t)
        if ya:
            say[ya[0]] = say.get(ya[0], 0) + 1
    return sorted(y for y, n in say.items() if n == 12)


def yil_toplam(aylik: dict, yil: int) -> float:
    return sum(v for t, v in aylik.items() if t.startswith(f"{yil}-"))


def main() -> None:
    stok, ad_s = cek(list(STOK.values()), "6", "last")
    akim, ad_a = cek(list(AKIM.values()), "5", "sum")
    kvdb, ad_k = cek(list(KVDB.values()), "5", "last")
    ad = {**ad_s, **ad_a, **ad_k}
    kod = {**STOK, **AKIM, **KVDB}

    def S(rol):
        return stok[kod[rol]]

    def A(rol):
        return akim[kod[rol]]

    ceyrekler = ortak(stok, [kod[r] for r in ("sdds_toplam", "sdds_gh", "sdds_tcmb", "sdds_banka", "sdds_diger", "sdds_dy")])
    if not ceyrekler:
        raise SystemExit("SDDS stok boş")
    son_c = ceyrekler[-1]

    def paylar(t):
        top = S("sdds_toplam")[t]
        parca = {
            "genel_hukumet": S("sdds_gh")[t],
            "tcmb": S("sdds_tcmb")[t],
            "bankalar": S("sdds_banka")[t],
            "diger": S("sdds_diger")[t],
            "dogrudan_yatirim": S("sdds_dy")[t],
        }
        fark = top - sum(parca.values())
        return top, parca, fark, abs(fark) / top if top else None

    top, parca, fark, fark_oran = paylar(son_c)
    kimlik_ok = fark_oran is not None and fark_oran <= TOL
    gh_fark = None
    if son_c in S("borclu_gh") and son_c in S("borclu_toplam"):
        gh_fark = abs(S("borclu_gh")[son_c] - parca["genel_hukumet"]) / top if top else None
    s1 = "belirlenemiyor"
    kamu_disi = None
    if kimlik_ok and gh_fark is not None and gh_fark <= TOL and top:
        kamu_disi = 1 - parca["genel_hukumet"] / top
        s1 = "destekleniyor" if kamu_disi > 0.50 else "curuyor"

    kur_t = ortak(stok, [kod[r] for r in ("kur_toplam", "kur_usd", "kur_eur", "kur_jpy", "kur_sdr", "kur_tl", "kur_diger")])
    kur = None
    if kur_t:
        t = kur_t[-1]
        bilesen = sum(S(r)[t] for r in ("kur_usd", "kur_eur", "kur_jpy", "kur_sdr", "kur_tl", "kur_diger"))
        topk = S("kur_toplam")[t]
        if topk and abs(topk - bilesen) / topk <= TOL:
            kur = {"donem": t, "toplam": topk, "tl": S("kur_tl")[t], "doviz_payi": 1 - S("kur_tl")[t] / topk,
                   "usd": S("kur_usd")[t], "eur": S("kur_eur")[t], "jpy": S("kur_jpy")[t],
                   "sdr": S("kur_sdr")[t], "diger": S("kur_diger")[t]}

    yillar = tam_yillar(A("gh_uzun_odeme"))
    akim_yil = yillar[-1] if yillar else None
    akim_ozet = None
    if akim_yil:
        akim_ozet = {}
        for rol in AKIM:
            if kod[rol] in akim and tam_yillar(akim[kod[rol]]) and akim_yil in tam_yillar(akim[kod[rol]]):
                akim_ozet[rol] = yil_toplam(akim[kod[rol]], akim_yil)
            else:
                akim_ozet[rol] = None

    # KVDB ile çeyrek kısa vade, son ortak çeyrek
    kvdb_kars = None
    if S("borclu_kisa") and kvdb[kod["kvdb_toplam"]]:
        for t in reversed(sorted(S("borclu_kisa"))):
            ay = ceyrek_sonu_ay(t)
            if ay and ay in kvdb[kod["kvdb_toplam"]]:
                a, b = S("borclu_kisa")[t], kvdb[kod["kvdb_toplam"]][ay]
                kvdb_kars = {"ceyrek": t, "ay": ay, "borclu_kisa": a, "kvdb": b,
                             "fark_oran": abs(a - b) / a if a else None}
                break

    yilsonu = []
    for t in ceyrekler:
        if not t.endswith("Q4"):
            continue
        top_t, parca_t, fark_t, fo = paylar(t)
        satir = {"donem": t, "toplam": top_t, **parca_t, "toplam_farki": fark_t, "fark_oran": fo}
        if t in S("borclu_kisa") and t in S("borclu_toplam") and S("borclu_toplam")[t]:
            satir["kisa_orijinal"] = S("borclu_kisa")[t]
            satir["kisa_pay"] = S("borclu_kisa")[t] / S("borclu_toplam")[t]
        if t in S("kur_tl") and t in S("kur_toplam") and S("kur_toplam")[t]:
            satir["tl"] = S("kur_tl")[t]
            satir["doviz_payi"] = 1 - S("kur_tl")[t] / S("kur_toplam")[t]
        yilsonu.append(satir)

    kapsam = []
    for rol, k in kod.items():
        seri = stok.get(k) or akim.get(k) or kvdb.get(k)
        tarihler = sorted(seri)
        kapsam.append({"rol": rol, "kod": k, "ad": ad.get(k), "n": len(tarihler),
                       "ilk": tarihler[0] if tarihler else None, "son": tarihler[-1] if tarihler else None})

    ham = []
    for kaynak, blok in (("stok", stok), ("akim", akim), ("kvdb", kvdb)):
        for k, seri in blok.items():
            for t, v in seri.items():
                ham.append((kaynak, k, ad.get(k), t, v))
    with (KOK / "dis_borc_sahip_ham.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["kaynak", "kod", "ad", "donem", "deger"])
        w.writerows(ham)

    net_kod = "TP.ODEAYRSUNUM6.Q168"
    net, ad_net = cek([net_kod], "5", "sum")
    net_2025 = yil_toplam(net[net_kod], 2025) if akim_yil == 2025 else None
    kullanim_eksi = None
    if akim_ozet and akim_ozet.get("banka_uzun_kullanim") is not None:
        kullanim_eksi = akim_ozet["banka_uzun_kullanim"] - akim_ozet["banka_uzun_odeme"]

    sonuc = {
        "cekilme": date.today().isoformat(),
        "birim_stok": "milyon ABD doları",
        "birim_akim": "milyon ABD doları",
        "birim_kaynak": "TCMB Dış Borç Metaveri, 12 Mart 2026; Ödemeler Dengesi Metaveri; KVDB Metaveri",
        "son_ceyrek": son_c,
        "sdds_toplam": top,
        "sdds_parca": parca,
        "sdds_fark": fark,
        "sdds_fark_oran": fark_oran,
        "gh_iki_tablo_fark_oran": gh_fark,
        "kamu_disi": kamu_disi,
        "S1": s1,
        "S2": "belirlenemiyor",
        "S3": "belirlenemiyor",
        "S4_sektor": "belirlenemiyor",
        "S4_borc_gsyh": "belirlenemiyor",
        "kur": kur,
        "ozdeslik": "belirlenemiyor",
        "akim_yil": akim_yil,
        "akim": akim_ozet,
        "banka_uzun_net_2025": net_2025,
        "banka_uzun_kullanim_eksi_odeme": kullanim_eksi,
        "banka_uzun_net_ad": ad_net.get(net_kod),
        "kvdb_karsilastirma": kvdb_kars,
        "borclu_son": {r: (S(r).get(son_c) if son_c in S(r) else None)
                       for r in ("borclu_toplam", "borclu_kamu", "borclu_gh", "borclu_kamu_banka",
                                 "borclu_tcmb", "borclu_ozel", "borclu_ozel_banka", "borclu_kisa")},
        "yilsonu_son8": yilsonu[-8:],
        "kapsam": kapsam,
    }
    (KOK / "dis_borc_sonuc.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("son", son_c, "S1", s1, "kamu_disi", None if kamu_disi is None else round(kamu_disi, 4))
    print("fark", fark, "gh_fark", gh_fark)
    print("kur", None if not kur else (kur["donem"], round(kur["doviz_payi"], 4)))
    print("akim_yil", akim_yil)
    if akim_ozet:
        for k in ("gh_uzun_odeme", "banka_uzun_odeme", "diger_uzun_odeme", "tcmb_uzun_odeme", "hata_noksan"):
            print(k, akim_ozet.get(k))
    print("kvdb", kvdb_kars)


if __name__ == "__main__":
    main()
