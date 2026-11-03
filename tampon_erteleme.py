"""Talep çapası verisini doldurur, tampon katmanını ve erteleme faizini hesaplar.

Kurallar: dosyada olmayan hücre boş kalır. Talep çapasında dL işlem serisidir.
Tampon katmanında yeniden değerleme = stok farkı − işlem, bilerek ayrı tutulur.
Test eşikleri (H1–H3) bu dosyada yoktur; onlar talep_capa_modeli.py içindedir.
"""
import json
import re
import urllib.request
from calendar import monthrange
from datetime import date
from pathlib import Path

import pandas as pd

KOK = Path(__file__).parent
HAM = KOK / "ham"
EVDS = "https://evds3.tcmb.gov.tr/igmevdsms-dis"
# EVDS finansal hesap ham değeri bin TL'dir (2026-Q1 F.4 = 6.755.140.613 bin TL = 6.755,1 milyar TL).
BIN_TL_TO_MILYON = 1 / 1000

SEKTOR = {
    "firma": "11",
    "finansal": "12",
    "kamu": "13",
    "hane": "14",
    "hhkok": "15",
    "dis": "2",
    "toplam": "1",
}
KALEM = {"BF9": "1", "VF0": "23", "F4": "34", "F0": "45"}
BES = ["hane_hhkok", "firma", "kamu", "finansal", "dis"]
AY = {
    "ocak": 1, "şubat": 2, "subat": 2, "mart": 3, "nisan": 4, "mayıs": 5, "mayis": 5,
    "haziran": 6, "temmuz": 7, "ağustos": 8, "agustos": 8, "eylül": 9, "eylul": 9,
    "ekim": 10, "kasım": 11, "kasim": 11, "aralık": 12, "aralik": 12,
}


def evds_json(url, body=None):
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        method="POST" if body is not None else "GET",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8-sig"))


def evds_cek(kodlar, bas="01-01-2009", bit="01-10-2026", frekans="5"):
    meta = {}
    for g in [
        "bie_finhestnks11", "bie_finhestnks12", "bie_finhestnks13", "bie_finhestnks14",
        "bie_finhestnks15", "bie_finhestnks2", "bie_finhestnks1",
        "bie_finhestnks62011", "bie_finhestnks62012", "bie_finhestnks62013",
        "bie_finhestnks62014", "bie_finhestnks62015", "bie_finhestnks6202", "bie_finhestnks6201",
        "bie_gsyhhrccar",
    ]:
        for s in evds_json(f"{EVDS}/serieList/fe/type=json&code={g}"):
            meta[s["SERIE_CODE"]] = s
    rows = []
    for i in range(0, len(kodlar), 12):
        parca = kodlar[i:i + 12]
        ag = []
        for c in parca:
            ag.append(meta[c]["DEFAULT_AGG_METHOD"] if c in meta else "sum")
        body = {
            "type": "json",
            "series": "-".join(parca),
            "aggregationTypes": "-".join(ag),
            "formulas": "-".join("0" for _ in parca),
            "startDate": bas,
            "endDate": bit,
            "frequency": frekans,
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
        data = evds_json(f"{EVDS}/fe", body)
        for it in data["items"]:
            for c in parca:
                v = it.get(c.replace(".", "_"))
                if v not in (None, ""):
                    rows.append((it["Tarih"], c, float(str(v).replace(",", ""))))
        print(f"EVDS parça {i // 12 + 1}: {len(parca)} seri")
    return pd.DataFrame(rows, columns=["donem", "seri", "deger"])


def finansal_kodlar():
    kod = []
    for suf in SEKTOR.values():
        for n in KALEM.values():
            kod.append(f"TP.FINHESTNKS{suf}.ZP{n}")
            kod.append(f"TP.FINHESTNKS620{suf}.ZP{n}")
    kod.append("TP.GSYIH20.BY.B1GQ")
    return kod


def ceyrek_ayir(donem):
    yil, q = donem.split("-Q")
    return int(yil), int(q)


def yillik_panel(ham):
    ham = ham.copy()
    ham["yil"] = ham.donem.map(lambda d: ceyrek_ayir(d)[0])
    ham["q"] = ham.donem.map(lambda d: ceyrek_ayir(d)[1])
    stok = ham[ham.seri.str.contains(r"TP\.FINHESTNKS(?!620)", regex=True)]
    akim = ham[ham.seri.str.contains("FINHESTNKS620")]
    q4 = stok[stok.q == 4].pivot_table(index="yil", columns="seri", values="deger", aggfunc="last")
    # Akım yıllık toplamı: dört çeyrek de varsa.
    say = akim.groupby(["yil", "seri"]).donem.nunique()
    tam = say[say == 4].reset_index()[["yil", "seri"]]
    akim = akim.merge(tam, on=["yil", "seri"])
    yil_ak = akim.groupby(["yil", "seri"]).deger.sum().unstack()
    return q4, yil_ak


def hucre(q4, yak, sektor_suf, kalem, yil, akim=False):
    n = KALEM[kalem]
    kod = f"TP.FINHESTNKS620{sektor_suf}.ZP{n}" if akim else f"TP.FINHESTNKS{sektor_suf}.ZP{n}"
    tablo = yak if akim else q4
    if yil not in tablo.index or kod not in tablo.columns:
        return float("nan")
    return float(tablo.loc[yil, kod])


def milyon(x):
    return x * BIN_TL_TO_MILYON


def tampon_hesapla(q4, yak):
    """NL = varlık işlemi − yükümlülük işlemi. Yeniden değerleme = Δstok(BF.9) − NL."""
    kayit = []
    yillar = sorted(set(q4.index) & set(yak.index))
    for y in yillar:
        if y - 1 not in q4.index:
            continue
        parca = {}
        for ad, suf in SEKTOR.items():
            # BF.9 akımı resmî net borç verme işlemidir. Dış âlemde VF.0−F.0 bu serinin
            # ters işaretini verir; o yüzden NL olarak yayımlanan BF.9 kullanılır.
            bf9_ak = hucre(q4, yak, suf, "BF9", y, True)
            nl = bf9_ak
            stok = hucre(q4, yak, suf, "BF9", y, False)
            stok0 = hucre(q4, yak, suf, "BF9", y - 1, False)
            d_stok = stok - stok0
            reval = d_stok - nl
            parca[ad] = {"NL": nl, "BF9_islem": bf9_ak, "d_stok": d_stok, "reval": reval}
        # Hane + HHKOK, beşli kapanış
        h = {k: parca["hane"][k] + parca["hhkok"][k] for k in parca["hane"]}
        blok = {
            "hane_hhkok": h,
            "firma": parca["firma"],
            "kamu": parca["kamu"],
            "finansal": parca["finansal"],
            "dis": parca["dis"],
        }
        for ad, d in blok.items():
            kayit.append({"yil": y, "sektor": ad, **d, "hane_S14_NL": parca["hane"]["NL"]})
        kayit.append({
            "yil": y, "sektor": "toplam_kontrol",
            "NL": sum(parca[a]["NL"] for a in ("firma", "finansal", "kamu", "hane", "hhkok", "dis")),
            "BF9_islem": float("nan"),
            "d_stok": sum(parca[a]["d_stok"] for a in ("firma", "finansal", "kamu", "hane", "hhkok", "dis")),
            "reval": sum(parca[a]["reval"] for a in ("firma", "finansal", "kamu", "hane", "hhkok", "dis")),
            "hane_S14_NL": parca["hane"]["NL"],
        })
    df = pd.DataFrame(kayit)
    # Emilim payı: α = −Δ(NL+reval) / Σ|Δ(NL+reval)|. NL+reval = d_stok.
    bes = df[df.sektor.isin(BES)].copy()
    bes["dNW"] = bes["d_stok"]
    bes["d2"] = bes.groupby("sektor")["dNW"].diff()
    for y, g in bes.groupby("yil"):
        payda = g["d2"].abs().sum()
        if payda == 0 or g["d2"].isna().any():
            bes.loc[g.index, "alpha"] = float("nan")
        else:
            bes.loc[g.index, "alpha"] = -g["d2"] / payda
    return df, bes


def gsyh_yillik(ham):
    g = ham[ham.seri == "TP.GSYIH20.BY.B1GQ"].copy()
    g["yil"] = g.donem.map(lambda d: ceyrek_ayir(d)[0])
    g["q"] = g.donem.map(lambda d: ceyrek_ayir(d)[1])
    say = g.groupby("yil").donem.nunique()
    tam = say[say == 4].index
    return g[g.yil.isin(tam)].groupby("yil").deger.sum()


def veri_csv_yaz(q4, yak, gsyh):
    """KSH kalemleri dosyada yok: boş. dL/dA/L_stok S.14 işlem ve yıl sonu stok."""
    yillar = sorted(y for y in yak.index if y in q4.index and y in gsyh.index)
    kolon = ["yil", "D1", "B2B3", "D4_alinan", "D41_odenen", "D62", "D5", "D61",
             "P3", "P51", "dL", "D7_net", "B6_tuik", "B9_tuik", "dA", "L_stok",
             "deflator_tuketim", "GSYH", "cari_denge"]
    acik = {
        "yil": "Yıl",
        "D1": "TÜİK KSH: veri yok (bülten 58286 eki indirilemedi)",
        "B2B3": "TÜİK KSH: veri yok",
        "D4_alinan": "TÜİK KSH: veri yok",
        "D41_odenen": "TÜİK KSH: veri yok",
        "D62": "TÜİK KSH: veri yok",
        "D5": "TÜİK KSH: veri yok",
        "D61": "TÜİK KSH: veri yok",
        "P3": "TÜİK KSH: veri yok",
        "P51": "TÜİK KSH: veri yok",
        "dL": "TCMB EVDS TP.FINHESTNKS62014.ZP34 F.4 yükümlülük işlemi, dört çeyrek toplamı, milyon TL",
        "D7_net": "TÜİK KSH: veri yok",
        "B6_tuik": "TÜİK KSH: veri yok",
        "B9_tuik": "TÜİK KSH: veri yok",
        "dA": "TCMB EVDS TP.FINHESTNKS62014.ZP23 VF.0 varlık işlemi, dört çeyrek toplamı, milyon TL",
        "L_stok": "TCMB EVDS TP.FINHESTNKS14.ZP34 F.4 yükümlülük stoku, yılın 4. çeyreği, milyon TL",
        "deflator_tuketim": "veri yok",
        "GSYH": "TÜİK harcama yöntemi TP.GSYIH20.BY.B1GQ; dört çeyrek toplamı; milyon TL; EVDS çekimi 16 Ekim 2026",
        "cari_denge": "veri yok (EVDS TP.ODANA6.Q01 birimi metadata'da yazmıyor; TL sütununa konmadı)",
    }
    satirlar = []
    for y in yillar:
        dl = milyon(hucre(q4, yak, "14", "F4", y, True))
        da = milyon(hucre(q4, yak, "14", "VF0", y, True))
        lst = milyon(hucre(q4, yak, "14", "F4", y, False))
        satirlar.append({
            "yil": y, "dL": round(dl, 3), "dA": round(da, 3), "L_stok": round(lst, 3),
            "GSYH": round(milyon(float(gsyh.loc[y])), 3),
        })
    df = pd.DataFrame(satirlar)
    for k in kolon:
        if k not in df.columns:
            df[k] = pd.NA
    df = df[kolon]
    yol = KOK / "veri_hanehalki.csv"
    with yol.open("w", encoding="utf-8") as f:
        f.write(",".join(kolon) + "\n")
        f.write(",".join(acik[k].replace(",", ";") for k in kolon) + "\n")
        df.to_csv(f, index=False, header=False)
    return df


def _tarih_oku(gun, ay_adi, yil):
    ay = AY[ay_adi.lower().replace("ı", "i").replace("İ", "i")] if False else AY.get(
        ay_adi.lower().translate(str.maketrans("İIŞĞÜÖÇ", "iisuoc")).replace("ı", "i"), None
    )
    # Türkçe ay adını doğrudan sözlükten çöz
    anahtar = ay_adi.strip().lower()
    for k, v in AY.items():
        if anahtar.replace("İ", "i").replace("ı", "i").replace("ş", "s").replace("ğ", "g").replace("ü", "u").replace("ö", "o").replace("ç", "c") == k.translate(str.maketrans("şğıöüç", "sgiouc")):
            ay = v
            break
    if ay is None:
        raise ValueError(ay_adi)
    return date(int(yil), ay, int(gun))


def _ay_norm(s):
    s = s.strip().lower()
    s = s.replace("ı", "i").replace("ş", "s").replace("ğ", "g").replace("ü", "u").replace("ö", "o").replace("ç", "c")
    return s


def donem_doldur(bas, bit, oran):
    """bas ve bit dahil, her ayın 1'i aralıktaysa o aya oranı yaz."""
    out = {}
    y, m = bas.year, bas.month
    while (y, m) <= (bit.year, bit.month):
        out[(y, m)] = oran
        m += 1
        if m == 13:
            m = 1
            y += 1
    return out


def kart_oranlari():
    """TL alışveriş azami akdi faiz, aylık yüzde. Dilim yoksa üç sütun aynıdır."""
    aylik = {}

    eski = (HAM / "kart_azami_2011_2020.txt").read_text(encoding="utf-8")
    # Satırda akdi ve gecikme sütunu aynı dönemi tekrarlar. İlk oran akdi faizdir.
    desen = re.compile(
        r"(\d{1,2})\s+([A-Za-zÇĞİÖŞÜçğıöşü]+)\s+(\d{4})\s*[-–]\s*(\d{1,2})\s+([A-Za-zÇĞİÖŞÜçğıöşü]+)\s+(\d{4})\s+([0-9],[0-9]{2})"
    )
    for satir in eski.splitlines():
        m = desen.search(satir)
        if not m:
            continue
        bas = _tarih_parca(m.group(1), m.group(2), m.group(3))
        bit = _tarih_parca(m.group(4), m.group(5), m.group(6))
        oran = float(m.group(7).replace(",", "."))
        for k, v in donem_doldur(bas, bit, oran).items():
            if k < (2020, 11):
                aylik[k] = {"tek": v, "alt": v, "orta": v, "ust": v, "kaynak": "TCMB 01.11.2020 öncesi arşiv, TL azami akdi"}

    yeni = (HAM / "kart_azami_2020_2025.txt").read_text(encoding="utf-8")
    sayi = re.compile(r"[0-9],[0-9]{2}")
    for satir in yeni.splitlines():
        tarih = re.match(r"\s*(\d{1,2})\.(\d{2})\.(\d{4})", satir)
        if not tarih:
            continue
        y, mo = int(tarih.group(3)), int(tarih.group(2))
        sayilar = [float(x.replace(",", ".")) for x in sayi.findall(satir)]
        # Dilimli tablo: referans + 5 çift (akdi/gecikme). Tek tablo: referans + 3 çift.
        if len(sayilar) >= 11:
            aylik[(y, mo)] = {
                "tek": None, "alt": sayilar[1], "orta": sayilar[3], "ust": sayilar[5],
                "kaynak": "TCMB 01.11.2024-31.12.2025 tablosu",
            }
        elif len(sayilar) >= 7:
            v = sayilar[1]
            aylik[(y, mo)] = {
                "tek": v, "alt": v, "orta": v, "ust": v,
                "kaynak": "TCMB 01.11.2020-31.10.2024 tablosu",
            }

    html = (HAM / "tcmb_kart_azami_2026.html").read_text(encoding="utf-8", errors="ignore")
    # Satır: tarih ardından 3,11 referans ve dilim akdi oranları
    blok = re.findall(
        r">(\d{1,2}/\d{1,2}/2026)<[\s\S]{0,800}?>\s*([0-9],[0-9]{2})\s*<[\s\S]{0,400}?>\s*([0-9],[0-9]{2})\s*<",
        html,
    )
    # Daha güvenilir: pandas ondalık virgül
    tablo = pd.read_html(HAM / "tcmb_kart_azami_2026.html", decimal=",", thousands=".")[0]
    govde = tablo.iloc[4:].copy()
    for _, row in govde.iterrows():
        parca = str(row.iloc[0]).split("/")
        if len(parca) != 3:
            continue
        y, mo = int(parca[2]), int(parca[1])
        aylik[(y, mo)] = {
            "tek": None,
            "alt": float(row.iloc[2]),
            "orta": float(row.iloc[4]),
            "ust": float(row.iloc[6]),
            "kaynak": "TCMB azami faiz sayfası, 8 Ekim 2026 çekimi, 2026 dilimleri",
        }
    return aylik, blok


def _tarih_parca(gun, ay_adi, yil):
    ay = AY[_ay_norm(ay_adi)]
    return date(int(yil), ay, int(gun))


def yillik_bilesik(aylik):
    """12 ayın hepsi varsa (1+r)^12 − 1. Eksik yıl boş."""
    kayit = []
    for y in range(2018, 2027):
        aylar = [aylik.get((y, m)) for m in range(1, 13)]
        if any(a is None for a in aylar):
            kayit.append({"yil": y, "ay_sayisi": sum(a is not None for a in aylar),
                          "i_alt": pd.NA, "i_orta": pd.NA, "i_ust": pd.NA, "tam_yil": False})
            continue
        def bilesik(anahtar):
            carpim = 1.0
            for a in aylar:
                carpim *= 1 + a[anahtar] / 100
            return carpim - 1
        kayit.append({
            "yil": y, "ay_sayisi": 12, "tam_yil": True,
            "i_alt": bilesik("alt"), "i_orta": bilesik("orta"), "i_ust": bilesik("ust"),
            "aralik_sonu_alt": aylar[-1]["alt"], "aralik_sonu_orta": aylar[-1]["orta"], "aralik_sonu_ust": aylar[-1]["ust"],
        })
    return pd.DataFrame(kayit)


def ihtiyac_faizi():
    ham = pd.read_csv(KOK / "faiz_ham.csv")
    s = ham[ham.Seri == "TP.KTF10"].copy()
    s["yil"] = s.Donem.str.slice(0, 4).astype(int)
    s["ay"] = s.Donem.str.slice(5, 7).astype(int)
    say = s.groupby("yil").ay.nunique()
    ort = s.groupby("yil").Deger.mean()
    out = pd.DataFrame({"yil": ort.index, "ihtiyac_akim_ortalama_yuzde": ort.values, "ay": say.reindex(ort.index).values})
    out.loc[out.ay < 12, "ihtiyac_akim_ortalama_yuzde"] = pd.NA
    return out


def takip_serisi():
    ham = pd.read_csv(KOK / "npl_ham.csv")
    genis = ham.pivot_table(index="Donem", columns="Seri", values="Deger", aggfunc="last")
    # Bölüm 1 canlı stok, bölüm 3 takip. Oran = takip / (canlı + takip).
    ad = {
        "TP.HPBITABLO6.2": "tuketici_canli",
        "TP.HPBITABLO6.16": "kart_canli",
        "TP.HPBITABLO6.50": "tuketici_takip",
        "TP.HPBITABLO6.54": "kart_takip",
        "TP.HPBITABLO6.19": "ticari_canli",
        "TP.HPBITABLO6.55": "ticari_takip",
    }
    df = genis[list(ad)].rename(columns=ad).sort_index()
    df["tuketici_oran"] = df.tuketici_takip / (df.tuketici_canli + df.tuketici_takip)
    df["kart_oran"] = df.kart_takip / (df.kart_canli + df.kart_takip)
    df["ticari_oran"] = df.ticari_takip / (df.ticari_canli + df.ticari_takip)
    df["bireysel_oran"] = (df.tuketici_takip) / (df.tuketici_canli + df.tuketici_takip)
    return df


def akim_stok_kontrol(q4, yak):
    """F.4 ve VF.5 için işlem toplamı stok farkına eşit mi? Eşitse akım, stok farkıdır."""
    # VF.5 stok/akım kodu ZP15; panelde yok. Kontrolü F.4 ve BF.9 üzerinden yap.
    satir = []
    for y in sorted(set(q4.index) & set(yak.index)):
        if y - 1 not in q4.index:
            continue
        for ad, kalem in (("F4", "F4"), ("BF9", "BF9")):
            ds = hucre(q4, yak, "14", kalem, y) - hucre(q4, yak, "14", kalem, y - 1)
            ak = hucre(q4, yak, "14", kalem, y, True)
            satir.append({"yil": y, "kalem": ad, "dstok_milyon": milyon(ds), "islem_milyon": milyon(ak),
                          "fark_orani": (ds - ak) / ds if ds else float("nan")})
    return pd.DataFrame(satir)


def main():
    HAM.mkdir(exist_ok=True)
    kodlar = finansal_kodlar()
    ham = evds_cek(kodlar)
    ham.to_csv(HAM / "evds_finansal_gsyh.csv", index=False)
    q4, yak = yillik_panel(ham)
    gsyh = gsyh_yillik(ham)
    print("GSYH 2024 bin TL", float(gsyh.loc[2024]) if 2024 in gsyh.index else "yok")
    print("GSYH 2025 bin TL", float(gsyh.loc[2025]) if 2025 in gsyh.index else "yok")
    veri = veri_csv_yaz(q4, yak, gsyh)
    print("veri yılları", veri.yil.min(), veri.yil.max(), "satır", len(veri))

    kontrol = akim_stok_kontrol(q4, yak)
    kontrol.to_csv(KOK / "akim_stok_kontrol.csv", index=False)

    tam, bes = tampon_hesapla(q4, yak)
    for c in ("NL", "BF9_islem", "d_stok", "reval", "hane_S14_NL"):
        if c in tam.columns:
            tam[c] = tam[c].map(lambda x: milyon(x) if pd.notna(x) else x)
        if c in bes.columns:
            bes[c] = bes[c].map(lambda x: milyon(x) if pd.notna(x) else x)
    bes["dNW"] = bes["dNW"].map(lambda x: milyon(x) if pd.notna(x) else x)
    bes["d2"] = bes.groupby("sektor")["dNW"].diff()
    # alpha milyonla bölünce değişmez; d2 yeniden hesaplandığı için alphayı tekrar yaz
    for y, g in bes.groupby("yil"):
        payda = g["d2"].abs().sum()
        if payda == 0 or g["d2"].isna().any():
            bes.loc[g.index, "alpha"] = float("nan")
        else:
            bes.loc[g.index, "alpha"] = -g["d2"] / payda
    tam.to_csv(KOK / "tampon_yillik.csv", index=False)
    sok = bes[bes.yil.isin([2018, 2021, 2023])][["yil", "sektor", "NL", "reval", "dNW", "d2", "alpha"]]
    sok.to_csv(KOK / "tampon_sok.csv", index=False)
    print(sok.round(3).to_string(index=False))

    aylik, _ = kart_oranlari()
    faiz = yillik_bilesik(aylik)
    ihtiyac = ihtiyac_faizi()
    er = faiz.merge(ihtiyac, on="yil", how="left")
    er["g_w"] = pd.NA
    er["i_ust_g_w_buyuk"] = pd.NA
    er.to_csv(KOK / "erteleme_yillik.csv", index=False)
    print(er.to_string(index=False))

    takip = takip_serisi()
    takip.to_csv(KOK / "takip_aylik.csv")
    for donem in ["2024-06", "2024-12", "2025-12", "2026-01", "2026-09"]:
        if donem in takip.index:
            r = takip.loc[donem]
            print(donem, "tuketici", round(100 * r.tuketici_oran, 2), "kart", round(100 * r.kart_oran, 2),
                  "ticari", round(100 * r.ticari_oran, 2))
        else:
            print(donem, "VERİ YOK")


if __name__ == "__main__":
    main()
