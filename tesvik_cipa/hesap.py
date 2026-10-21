"""Teşvik-çıpa. Kurallar: tesvik_cipa/ON_KAYIT.md. Eşik orada kilitli."""
import json
import math
import re
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

KOK = Path(__file__).resolve().parent
HAM = KOK / "ham"
AY = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
      "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}

# RG sayı tarihi, kısa ad, ayrışır mı, not. Ayrışma gazete fihristinden, getiriden önce.
KARARLAR = [
    ("2016-04-08", "3305 değişiklik", None, "pencere dışı"),
    ("2016-10-05", "2016/9139", False, "W1; aynı sayıda 2016/9256 ÖTV"),
    ("2016-11-26", "2016/9495", True, "W1; kurucu proje bazlı karar"),
    ("2017-02-22", "3305 değişiklik", None, "pencere dışı"),
    ("2017-05-03", "3305 değişiklik", None, "pencere dışı"),
    ("2017-08-17", "3305 değişiklik", None, "pencere dışı"),
    ("2017-12-30", "3305 değişiklik", None, "pencere dışı; 3. mükerrer"),
    ("2018-02-22", "3305 değişiklik", None, "pencere dışı"),
    ("2018-04-28", "3305 değişiklik", None, "pencere dışı"),
    ("2018-06-22", "2018/11816 ve 2018/11930", True, "W2; iki karar, tek gün"),
    ("2018-09-14", "91", True, "W2; bakanlık adı ve üç fıkra"),
    ("2018-11-09", "323", None, "pencere dışı"),
    ("2019-02-28", "798", None, "pencere dışı"),
    ("2019-08-07", "1402", False, "W3; aynı sayıda CBK 43, 3 sayılı CBK cetveli"),
    ("2020-05-09", "2501", None, "pencere dışı"),
    ("2020-08-21", "2846", None, "pencere dışı"),
    ("2020-12-17", "3307", None, "pencere dışı"),
    ("2021-06-29", "4191", None, "pencere dışı"),
    ("2022-02-24", "5209", None, "pencere dışı; W4 31 Ocak'ta biter"),
    ("2022-05-13", "5548", None, "pencere dışı"),
    ("2022-11-30", "6435", None, "pencere dışı"),
    ("2023-03-10", "6923", None, "pencere dışı"),
    ("2023-04-20", "7108", None, "pencere dışı"),
    ("2024-08-29", "8860", None, "pencere dışı"),
    ("2025-05-30", "9903", None, "pencere dışı; yeni karar"),
]

PENCERE = [
    ("W1", datetime(2016, 10, 1), datetime(2016, 12, 31)),
    ("W2", datetime(2018, 5, 1), datetime(2018, 9, 30)),
    ("W3", datetime(2019, 7, 1), datetime(2019, 9, 30)),
    ("W4", datetime(2021, 11, 1), datetime(2022, 1, 31)),
    ("W5", datetime(2023, 10, 1), datetime(2023, 12, 31)),
]


def iso(d):
    return d.strftime("%Y-%m-%d")


def yil_iki(yy):
    n = int(yy)
    return 2000 + n if n < 70 else 1900 + n


def parse_h10(yol):
    html = Path(yol).read_text(errors="replace")
    birim = "per U.S. dollar" in html
    out = {}
    for m in re.finditer(r">\s*(\d{1,2})-([A-Z]{3})-(\d{2})\s*</th>\s*<td[^>]*>\s*([0-9.]+|ND|na)?\s*<", html):
        d, mon, yy, val = m.group(1), m.group(2), m.group(3), m.group(4)
        if not val or val in ("ND", "na"):
            continue
        out[datetime(yil_iki(yy), AY[mon], int(d))] = float(val)
    return out, birim


def pencere_adi(d):
    for ad, a, b in PENCERE:
        if a <= d <= b:
            return ad
    return None


def p_tek(goz, dagilim):
    d = np.asarray(dagilim, float)
    return float((1 + np.sum(d >= goz)) / (1 + len(d)))


def yuzdelik90(dagilim):
    s = np.sort(np.asarray(dagilim, float))
    idx = int(math.ceil(0.90 * len(s))) - 1
    return float(s[max(idx, 0)])


def holm(ps):
    m = len(ps)
    order = np.argsort(ps)
    adj = np.empty(m)
    run = 0.0
    for rank, j in enumerate(order):
        run = max(run, (m - rank) * float(ps[j]))
        adj[j] = min(1.0, run)
    return adj


def ay_ekle(y, m, k):
    m0 = y * 12 + (m - 1) + k
    return m0 // 12, m0 % 12 + 1


def ay_anahtar(y, m):
    return f"{y:04d}-{m:02d}"


def main():
    kur = json.loads((HAM / "kurlar.json").read_text())
    try_s = {}
    for k, v in kur.items():
        try_s[datetime.strptime(k, "%Y-%m-%d")] = float(v["satis"])
    gunler = sorted(try_s)
    emsaller = {}
    birimler = {}
    for ad in ("brl", "mxn", "zar", "inr"):
        seri, birim = parse_h10(HAM / f"h10_{ad}.htm")
        emsaller[ad] = seri
        birimler[ad] = birim
    if not all(birimler[a] for a in ("brl", "mxn", "zar")):
        raise SystemExit(f"Eş birimi yerel/dolar değil: {birimler}")

    def getir_kur(seri, gun, kayma=0):
        return seri.get(gun + timedelta(days=kayma))

    def gunluk(i, kayma=0, kume=("brl", "mxn", "zar")):
        t, p = gunler[i], gunler[i - 1]
        e1, e0 = try_s[t], try_s[p]
        if e1 <= 0 or e0 <= 0:
            return None
        r_try = 100.0 * math.log(e1 / e0)
        parca = []
        for ad in kume:
            a = getir_kur(emsaller[ad], t, kayma)
            b = getir_kur(emsaller[ad], p, kayma)
            if a is None or b is None or a <= 0 or b <= 0:
                continue
            parca.append(100.0 * math.log(a / b))
        if len(parca) < 2:
            return None
        return r_try - float(np.mean(parca)), r_try, len(parca)

    idx = {g: i for i, g in enumerate(gunler)}

    def day0(rg):
        if rg in idx:
            return rg
        for g in gunler:
            if g > rg:
                return g
        return None

    olay_gun = []
    for tarih, ad, ayr, notu in KARARLAR:
        rg = datetime.strptime(tarih, "%Y-%m-%d")
        g0 = day0(rg)
        olay_gun.append({"rg": tarih, "ad": ad, "ayrisir": ayr, "not": notu,
                         "pencere": pencere_adi(rg), "gun0": iso(g0) if g0 else None})

    # ±5 bülten günü, bütün teşvik gün-0'ları
    disla = set()
    for o in olay_gun:
        if not o["gun0"]:
            continue
        i = idx[datetime.strptime(o["gun0"], "%Y-%m-%d")]
        for j in range(max(1, i - 5), min(len(gunler), i + 6)):
            disla.add(gunler[j])

    def havuz(yil, dis_yil):
        out = []
        for i in range(1, len(gunler)):
            g = gunler[i]
            if g in disla:
                continue
            if dis_yil:
                if g.year == yil or g.year in (2018, 2021):
                    continue
            elif g.year != yil:
                continue
            row = gunluk(i)
            if row is not None:
                out.append(row[0])
        return out

    # Benzersiz gün-0
    gunler_olay = []
    gorulen = set()
    for o in olay_gun:
        if o["gun0"] and o["gun0"] not in gorulen:
            gorulen.add(o["gun0"])
            gunler_olay.append(o["gun0"])

    olcum = {}
    for g0s in gunler_olay:
        g0 = datetime.strptime(g0s, "%Y-%m-%d")
        i = idx[g0]
        ana = gunluk(i) if i >= 1 else None
        kay1 = gunluk(i, 1) if i >= 1 else None
        kaym = gunluk(i, -1) if i >= 1 else None
        inr = gunluk(i, 0, ("brl", "mxn", "zar", "inr")) if i >= 1 else None

        def car(k):
            top, n = 0.0, 0
            for j in range(i - k, i + k + 1):
                if j < 1 or j >= len(gunler):
                    continue
                row = gunluk(j)
                if row is None:
                    continue
                top += row[0]
                n += 1
            return None if n == 0 else {"toplam": top, "gun": n}

        if ana is None:
            olcum[g0s] = {"bos": True}
            continue
        yil_h = havuz(g0.year, False)
        dis_h = havuz(g0.year, True)
        p_yil = p_tek(ana[0], yil_h) if len(yil_h) >= 1 else None
        p90 = yuzdelik90(yil_h) if yil_h else None
        p_dis = p_tek(ana[0], dis_h) if len(dis_h) >= 1 else None
        isaret = [ana[0] > 0]
        for alt in (kay1, kaym):
            isaret.append(None if alt is None else alt[0] > 0)
        olcum[g0s] = {
            "bos": False,
            "ozgu": ana[0],
            "try": ana[1],
            "es": ana[2],
            "p_yil": p_yil,
            "p90": p90,
            "n_yil": len(yil_h),
            "p_dis": p_dis,
            "n_dis": len(dis_h),
            "kay1": None if kay1 is None else kay1[0],
            "kaym1": None if kaym is None else kaym[0],
            "inr": None if inr is None else inr[0],
            "isaret_ayni": all(x is True for x in isaret) or all(x is False for x in isaret),
            "car1": car(1),
            "car3": car(3),
        }

    hesapli = [g for g in gunler_olay if not olcum[g].get("bos") and olcum[g].get("p_yil") is not None]
    if hesapli:
        adj = holm([olcum[g]["p_yil"] for g in hesapli])
        for g, a in zip(hesapli, adj):
            olcum[g]["holm"] = float(a)

    def kur_hukum(g0s):
        o = olcum.get(g0s) or {"bos": True}
        if o.get("bos") or o.get("n_yil", 0) < 100 or o.get("p_yil") is None:
            return "belirsiz"
        gecti = o["p_yil"] <= 0.10 and o["ozgu"] >= o["p90"] and o.get("holm", 1) <= 0.10
        if not gecti:
            return "kaldi"
        if o["p_dis"] is None or o["p_dis"] > 0.10 or o["n_dis"] < 100 or not o["isaret_ayni"]:
            return "belirsiz"
        return "gecti"

    # Beklenti
    ham = json.loads((HAM / "beklenti_ham.json").read_text())
    bek = {}
    for it in ham.get("items") or []:
        v = it.get("TP_PKAUO_S01_F_U")
        if v not in (None, ""):
            bek[it["Tarih"]] = float(v)
    gser = {k: v - 5.0 for k, v in bek.items()}

    def dg(y, m):
        k, o = ay_anahtar(y, m), ay_anahtar(*ay_ekle(y, m, -1))
        if k not in gser or o not in gser:
            return None
        return gser[k] - gser[o]

    taban = []
    y, m = 2013, 1
    while (y, m) <= (2016, 9):
        d = dg(y, m)
        if d is not None:
            taban.append(d)
        y, m = ay_ekle(y, m, 1)

    def beklenti_hukum(tarih):
        rg = datetime.strptime(tarih, "%Y-%m-%d")
        d = dg(rg.year, rg.month)
        if d is None or len(taban) < 24:
            return {"hukum": "belirsiz", "dg": d, "n": len(taban)}
        p = p_tek(d, taban)
        hukum = "gecti" if d > 0 and p <= 0.10 else "kaldi"
        return {"hukum": hukum, "dg": d, "p": p, "n": len(taban),
                "g": gser.get(ay_anahtar(rg.year, rg.month))}

    for o in olay_gun:
        o["beklenti"] = beklenti_hukum(o["rg"])
        o["kur"] = kur_hukum(o["gun0"]) if o["gun0"] else "belirsiz"
        o["olcum"] = olcum.get(o["gun0"])

    # Takılma bandı
    band = []
    y, m = 2023, 11
    son = max(gser)
    sy, sm = int(son[:4]), int(son[5:7])
    while (y, m) <= (sy, sm):
        k = ay_anahtar(y, m)
        if k in gser:
            band.append({"ay": k, "g": gser[k]})
        y, m = ay_ekle(y, m, 1)
    gs = [b["g"] for b in band]
    takilma = bool(gs) and min(gs) >= 10 and max(gs) <= 16 and (max(gs) - min(gs)) <= 4

    # Duyarlılık, hüküm dışı
    ay_ort = {}
    for g, e in try_s.items():
        ay_ort.setdefault(ay_anahtar(g.year, g.month), []).append(e)
    ay_ort = {k: float(np.mean(v)) for k, v in ay_ort.items()}
    aylar = sorted(ay_ort)
    r_ay = {}
    for i in range(1, len(aylar)):
        a, b = ay_ort[aylar[i]], ay_ort[aylar[i - 1]]
        if a > 0 and b > 0:
            r_ay[aylar[i]] = 100.0 * math.log(a / b)
    cift = []
    for k in aylar:
        if k in r_ay and k in gser:
            y, m = int(k[:4]), int(k[5:7])
            d = dg(y, m)
            if d is not None:
                cift.append((k, d, r_ay[k]))

    def beta_aralik(a, b):
        xs, ys = [], []
        for k, d, r in cift:
            if a <= k <= b:
                # 24 aylık kayan pencerenin bu ayda biten eğimi, sonra ortalama
                penc = [(d2, r2) for k2, d2, r2 in cift if k2 <= k]
                penc = penc[-24:]
                if len(penc) < 24:
                    continue
                x = np.array([p[1] for p in penc], float)
                y = np.array([p[0] for p in penc], float)
                if np.std(x) == 0:
                    continue
                xs.append(k)
                ys.append(float(np.polyfit(x, y, 1)[0]))
        return None if not ys else {"n": len(ys), "ortalama": float(np.mean(ys))}

    duyar = {
        "2014-01_2016-09": beta_aralik("2014-01", "2016-09"),
        "2018-10_2021-11": beta_aralik("2018-10", "2021-11"),
        "2023-11_son": beta_aralik("2023-11", son),
    }

    # H-T1
    pencerede = [o for o in olay_gun if o["pencere"]]
    ayrisan = [o for o in pencerede if o["ayrisir"] is True]
    def gecti(o):
        return o["kur"] == "gecti" and o["beklenti"]["hukum"] == "gecti"
    if not pencerede:
        ht1 = "Yanlışlandı"
    elif not ayrisan:
        ht1 = "BELİRSİZ"
    elif any(gecti(o) for o in ayrisan):
        ht1 = "Ayakta"
    elif any(o["kur"] == "belirsiz" or o["beklenti"]["hukum"] == "belirsiz" for o in ayrisan
             if not (o["kur"] == "kaldi" or o["beklenti"]["hukum"] == "kaldi")):
        ht1 = "BELİRSİZ"
    else:
        # her ayrışan olayda en az bir ayak kaldı
        hepsi_kaldi = all(o["kur"] == "kaldi" or o["beklenti"]["hukum"] == "kaldi" for o in ayrisan)
        ht1 = "Yanlışlandı" if hepsi_kaldi else "BELİRSİZ"

    sonuc = {
        "evds3": True,
        "birim": birimler,
        "n_bulten": len(gunler),
        "bulten_ilk": iso(gunler[0]),
        "bulten_son": iso(gunler[-1]),
        "n_taban_dg": len(taban),
        "takilma": {"tutar": takilma, "n": len(gs), "min": min(gs) if gs else None,
                    "max": max(gs) if gs else None, "son_ay": son,
                    "son_g": gser.get(son)},
        "duyarlilik": duyar,
        "ht1": ht1,
        "olay": olay_gun,
        "g_2018": {k: gser[k] for k in sorted(gser) if k.startswith("2018")},
    }
    (KOK / "sonuclar.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=1))
    print("H-T1", ht1)
    print("takilma", sonuc["takilma"])
    print("duyar", duyar)
    for o in olay_gun:
        if o["pencere"] or (o["olcum"] and not o["olcum"].get("bos") and o["olcum"].get("p_yil", 1) <= 0.10):
            oz = None if not o["olcum"] or o["olcum"].get("bos") else round(o["olcum"]["ozgu"], 2)
            print(o["rg"], o["ad"], o["pencere"], "kur", o["kur"], "dg", o["beklenti"].get("dg"), "ozgu", oz, "p", None if not o["olcum"] or o["olcum"].get("bos") else o["olcum"].get("p_yil"))


if __name__ == "__main__":
    main()
