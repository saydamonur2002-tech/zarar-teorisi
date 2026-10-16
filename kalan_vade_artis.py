"""Kalan vade stokunun aylık artışı. Kurallar KALAN_VADE_ARTIS_ONKAYIT.md.

Yayımlı olmayan bileşen sıfır yazılmaz. Artık, bileşenler eksikse yazılmaz.
Brüt dış borcun döviz payı, kalan vade stokunun değerlemesine konmaz.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from evds_cek import BASE, get_json

KOK = Path(__file__).resolve().parent
SON = "16-10-2026"
K20 = "TP.KALANVADE.K20"
ORIJINAL_AY = "TP.KVDB19"


def cek(kod: str, freq: str, agg: str, start: str = "01-01-1989") -> dict[str, float]:
    body = {
        "type": "json",
        "series": kod,
        "aggregationTypes": agg,
        "formulas": "0",
        "startDate": start,
        "endDate": SON,
        "frequency": freq,
        "decimalSeperator": ".",
        "decimal": "4",
        "dateFormat": "0",
        "lang": "TR",
        "yon": "0",
        "sira": "0",
        "ozelFormuller": [],
        "groupSeperator": True,
        "isRaporSayfasi": False,
    }
    data = get_json(f"{BASE}/fe", body)
    anahtar = kod.replace(".", "_")
    out = {}
    for it in data.get("items", []):
        v = it.get(anahtar)
        if v not in (None, ""):
            out[str(it["Tarih"])] = float(str(v).replace(",", ""))
    return out


def seri_bilgi(grup: str) -> list[dict]:
    return get_json(f"{BASE}/serieList/fe/type=json&code={grup}")


def main() -> None:
    k20_meta = next(s for s in seri_bilgi("bie_kalanvade") if s["SERIE_CODE"] == K20)
    k20 = cek(K20, "5", "last")
    aylar = sorted(k20)
    delta = []
    for i in range(1, len(aylar)):
        delta.append({
            "ay": aylar[i],
            "onceki": aylar[i - 1],
            "stok": k20[aylar[i]],
            "onceki_stok": k20[aylar[i - 1]],
            "delta": k20[aylar[i]] - k20[aylar[i - 1]],
        })
    karar = next(d for d in delta if d["ay"] == "2026-07" and d["onceki"] == "2026-06")
    son12 = delta[-12:]

    orijinal = cek(ORIJINAL_AY, "5", "last", "01-01-2024")
    doviz_kv = cek("TP.KVADEDOVKOMP.USDTOPLAM", "6", "last", "01-01-2024")
    if not doviz_kv:
        doviz_kv = cek("TP.KVADEDOVKOMP.USDTOPLAM", "5", "last", "01-01-2024")

    brut = {}
    for kod in (
        "TP.BRUTDBDOVKOMP.G1",
        "TP.BRUTDBDOVKOMP.G2",
        "TP.BRUTDBDOVKOMP.G6",
        "TP.BRUTDBDOVKOMP.G8",
    ):
        brut[kod] = cek(kod, "6", "last", "01-01-2024")

    uzun_kod = {
        "tcmb_kullanim": "TP.ODEAYRSUNUM6.Q164",
        "tcmb_odeme": "TP.ODEAYRSUNUM6.Q165",
        "banka_kullanim": "TP.ODEAYRSUNUM6.Q169",
        "banka_odeme": "TP.ODEAYRSUNUM6.Q170",
        "gh_kullanim": "TP.ODEAYRSUNUM6.Q177",
        "gh_odeme": "TP.ODEAYRSUNUM6.Q178",
        "diger_kullanim": "TP.ODEAYRSUNUM6.Q182",
        "diger_odeme": "TP.ODEAYRSUNUM6.Q183",
    }
    uzun = {ad: cek(kod, "5", "sum", "01-06-2026") for ad, kod in uzun_kod.items()}

    uyp = seri_bilgi("bie_uypucay")
    uyp_ad = " ".join((s.get("SERIE_NAME") or "") + " " + (s.get("SERIE_NAME_ENG") or "") for s in uyp).lower()
    uyp_yok = {
        "degerleme": "değer" not in uyp_ad and "valuation" not in uyp_ad,
        "diger_hacim": "hacim" not in uyp_ad and "other volume" not in uyp_ad,
        "kalan_vade": "kalan" not in uyp_ad and "remaining" not in uyp_ad,
    }

    ode = seri_bilgi("bie_odeayrsunum6")
    kisa_brut_yok = []
    for s in ode:
        ad = s.get("SERIE_NAME") or ""
        if ad.endswith("Kısa Vade"):
            kod = s["SERIE_CODE"]
            cocuk = [c for c in ode if c.get("UST_SERIE_CODE") == kod]
            kisa_brut_yok.append({
                "kod": kod,
                "ad": ad,
                "cocuk": [c["SERIE_NAME"] for c in cocuk],
            })

    katalog = json.loads(Path(KOK / "evds_katalog_gruplar.json").read_text(encoding="utf-8-sig"))

    def norm(metin: str) -> str:
        return (
            metin.replace("İ", "i")
            .replace("I", "ı")
            .replace("Ş", "ş")
            .replace("Ğ", "ğ")
            .replace("Ü", "ü")
            .replace("Ö", "ö")
            .replace("Ç", "ç")
            .lower()
        )

    aranan = ("vade geç", "diğer hacim", "değerleme", "anapara takvim", "amortisman")
    katalog_yok = []
    for ibare in aranan:
        bulunan = [
            row[0]
            for row in katalog
            if norm(ibare) in norm(" ".join(str(x) for x in row))
        ]
        katalog_yok.append({"ibare": ibare, "grup": bulunan})

    ceyrek_ay = {"Q1": "03", "Q2": "06", "Q3": "09", "Q4": "12"}
    hizali = []
    for donem, kv in sorted(doviz_kv.items()):
        if "-Q" not in donem:
            continue
        yil, q = donem.split("-")
        ay = f"{yil}-{ceyrek_ay[q]}"
        hizali.append({
            "donem": donem,
            "ay": ay,
            "kvdb_doviz_toplam": kv,
            "orijinal_ay": orijinal.get(ay),
            "k20": k20.get(ay),
        })

    esit = []
    for ay, kv in sorted(doviz_kv.items()):
        esit.append({
            "donem": ay,
            "kvdb_doviz_toplam": kv,
            "k20": k20.get(ay),
            "orijinal_ay": orijinal.get(ay),
            "k20_ile_fark": None if ay not in k20 else kv - k20[ay],
            "orijinal_ile_fark": None if ay not in orijinal else kv - orijinal[ay],
        })

    bilesen = {
        "yeni_borclanma": "belirlenemiyor",
        "geri_odeme": "belirlenemiyor",
        "vade_gecisi": "belirlenemiyor",
        "degerleme": "belirlenemiyor",
        "diger_hacim": "belirlenemiyor",
    }
    sonuc = {
        "karar_ayi": karar,
        "k20_n": len(k20),
        "k20_ilk": aylar[0],
        "k20_son": aylar[-1],
        "k20_ad": k20_meta.get("SERIE_NAME"),
        "k20_grup_frekans": k20_meta.get("FREQUENCY_STR"),
        "aylik_yorum": len(k20) >= 12,
        "son12": son12,
        "bilesen": bilesen,
        "artik": "yazilmadi",
        "s1": "belirlenemiyor",
        "s2": "belirlenemiyor",
        "s3": "belirlenemiyor",
        "s4": "belirlenemiyor",
        "doviz_kv_karsilastirma": esit,
        "doviz_kv_ay_hiza": hizali,
        "brut_doviz": {k: v for k, v in brut.items()},
        "uzun_vade_kredi_2026_06_08": uzun,
        "kisa_vade_altinda_kullanim_yok": kisa_brut_yok,
        "uyp_satir_yok": uyp_yok,
        "katalog_yok": katalog_yok,
        "g19_kullanilmadi": True,
    }
    (KOK / "kalan_vade_artis_sonuc.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    with (KOK / "kalan_vade_artis_ham.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["Seri", "Donem", "Deger"])
        for ay in aylar:
            w.writerow([K20, ay, k20[ay]])
        for ay, v in sorted(orijinal.items()):
            w.writerow([ORIJINAL_AY, ay, v])
        for ay, v in sorted(doviz_kv.items()):
            w.writerow(["TP.KVADEDOVKOMP.USDTOPLAM", ay, v])
        for kod, seri in brut.items():
            for ay, v in sorted(seri.items()):
                w.writerow([kod, ay, v])
        for ad, seri in uzun.items():
            for ay, v in sorted(seri.items()):
                w.writerow([uzun_kod[ad], ay, v])
    print("k20", len(k20), aylar[0], aylar[-1], "karar", karar)
    print("doviz esit", esit[-6:])
    print("brut son", {k: list(v)[-2:] for k, v in brut.items()})
    print("uzun aylar", {ad: sorted(seri) for ad, seri in uzun.items()})


if __name__ == "__main__":
    main()
