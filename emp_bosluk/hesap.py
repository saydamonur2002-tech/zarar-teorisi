"""EMP boşluk testleri. Kurallar: emp_bosluk/ON_KAYIT.md. Eşik yok, yalnız kilitli formül."""
import csv
import json
import math
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

KOK = Path(__file__).resolve().parent
HAM = KOK / "ham"


def yukle_ay(yol):
    return json.loads(yol.read_text())


def ceyrek(anahtar):
    y, m = anahtar.split("-")
    return int(y), (int(m) - 1) // 3 + 1


def ay_anahtarlari(y, q):
    m0 = (q - 1) * 3 + 1
    return [f"{y}-{m:02d}" for m in range(m0, m0 + 3)]


def uc_ay(seri, y, q, nasil):
    vals = []
    for k in ay_anahtarlari(y, q):
        v = seri.get(k)
        if v is None:
            return None
        vals.append(float(v))
    if nasil == "ort":
        return sum(vals) / 3.0
    if nasil == "son":
        return vals[-1]
    if nasil == "toplam":
        return sum(vals)
    raise ValueError(nasil)


def sd(xs):
    n = len(xs)
    m = sum(xs) / n
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))


def r2_beta(y, X):
    beta, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    rank = int(np.linalg.matrix_rank(X, tol=1e-8))
    yhat = X @ beta
    sst = float(np.sum((y - y.mean()) ** 2))
    ssr = float(np.sum((y - yhat) ** 2))
    r2 = None if sst <= 0 else 1.0 - ssr / sst
    return r2, beta, rank, yhat


def shapley(y, kolonlar):
    """Sıralama ağırlıklı Shapley. φ, R² biriminde."""
    k = len(kolonlar)
    onbellek = {}

    def coz(mask):
        if mask not in onbellek:
            cols = [np.ones(len(y))]
            for i in range(k):
                if mask & (1 << i):
                    cols.append(kolonlar[i])
            X = np.column_stack(cols)
            onbellek[mask] = r2_beta(y, X)
        return onbellek[mask]

    tam = (1 << k) - 1
    r_tam, beta, rank, yhat = coz(tam)
    phis = []
    for i in range(k):
        diger = [j for j in range(k) if j != i]
        phi = 0.0
        m = len(diger)
        for s in range(1 << m):
            mask = 0
            bits = 0
            for b in range(m):
                if s & (1 << b):
                    mask |= 1 << diger[b]
                    bits += 1
            r_ile = coz(mask | (1 << i))[0]
            r_siz = coz(mask)[0]
            w = math.factorial(bits) * math.factorial(k - bits - 1) / math.factorial(k)
            phi += w * (r_ile - r_siz)
        phis.append(phi)
    return {
        "r2": r_tam,
        "rank": rank,
        "k": k,
        "n": int(len(y)),
        "beta": [float(b) for b in beta],
        "phi": phis,
        "pay": [None if r_tam is None or r_tam <= 0 else p / r_tam for p in phis],
        "yhat": yhat,
        "tekil": rank < k + 1,
    }


def model(panel, endeks, adlar):
    y = np.array([panel[i]["EMP"] for i in endeks], dtype=float)
    kolonlar = [np.array([panel[i][a] for i in endeks], dtype=float) for a in adlar]
    out = shapley(y, kolonlar)
    out["adlar"] = adlar
    out["ceyrekler"] = [panel[i]["q"] for i in endeks]
    return out


def pencere_ozet(panel, endeks, adlar, aday):
    """16 çeyrek. Tutar: pay>=0.30 ve katsayı>0. Tekil tutmaz, paydadadır."""
    kurulan = 0
    tutan = 0
    ayrinti = []
    ia = adlar.index(aday)
    for s in range(0, len(endeks) - 15):
        sl = endeks[s : s + 16]
        kurulan += 1
        m = model(panel, sl, adlar)
        pay = m["pay"][ia]
        kats = m["beta"][ia + 1]
        if m["tekil"] or pay is None:
            tutar = False
        else:
            tutar = pay >= 0.30 and kats > 0
        if tutar:
            tutan += 1
        ayrinti.append({
            "ilk": panel[sl[0]]["q"],
            "son": panel[sl[-1]]["q"],
            "tekil": m["tekil"],
            "pay": pay,
            "katsayi": kats,
            "tutar": tutar,
        })
    return {
        "kurulan": kurulan,
        "tutan": tutan,
        "oran": None if kurulan == 0 else tutan / kurulan,
        "dogrulanmadi": kurulan < 8,
        "pencereler": ayrinti,
    }


def main():
    ay = yukle_ay(HAM / "evds_aylik.json")
    bop = yukle_ay(HAM / "bop_aylik.json")
    hafta = {
        datetime.strptime(k, "%d-%m-%Y"): float(v)
        for k, v in yukle_ay(HAM / "dibs_hafta.json").items()
    }
    gun = {datetime.strptime(k, "%Y-%m-%d"): float(v) for k, v in yukle_ay(HAM / "usd_gunluk.json").items()}
    cds_satir = list(csv.DictReader((HAM / "cds_vekili.csv").open()))
    cds = [(datetime.strptime(r["Date"], "%Y-%m-%d"), float(r["CDS"])) for r in cds_satir]

    def ceyrek_son_hafta(y, q):
        m1, m2 = (q - 1) * 3 + 1, q * 3
        aday = [(d, v) for d, v in hafta.items() if d.year == y and m1 <= d.month <= m2]
        if not aday:
            return None
        return max(aday)[1]

    def ceyrek_son_cds(y, q):
        m1, m2 = (q - 1) * 3 + 1, q * 3
        aday = [(d, v) for d, v in cds if d.year == y and m1 <= d.month <= m2]
        if not aday:
            return None
        return max(aday)[1]

    ceyrekler = []
    y, q = 2016, 1
    while (y, q) <= (2025, 4):
        ceyrekler.append((y, q))
        q += 1
        if q == 5:
            y, q = y + 1, 1

    stok = {}
    for y, q in ceyrekler:
        e = uc_ay(ay["TP.DK.USD.S.YTL"], y, q, "ort")
        r = uc_ay(ay["TP.REZVARPD.K1"], y, q, "son")
        nhn = uc_ay(ay["TP.ODANA6.Q31"], y, q, "toplam")
        kacis = uc_ay(bop["TP.ODEAYRSUNUM6.Q142"], y, q, "toplam")
        altin_net_ihr = uc_ay(bop["TP.ODEAYRSUNUM6.Q17"], y, q, "toplam")
        tic = uc_ay(bop["TP.ODEAYRSUNUM6.Q188"], y, q, "toplam")
        g49 = uc_ay(ay["TP.KM.G49"], y, q, "son")
        g57 = uc_ay(ay["TP.KM.G57"], y, q, "son")
        bek = uc_ay(ay["TP.BEK.S05.C.U"], y, q, "ort")
        vade = None
        if all(uc_ay(ay[c], y, q, "son") is not None for c in ("TP.FDVY28", "TP.FDVY30", "TP.FDVY33", "TP.FDVY35")):
            vade = sum(uc_ay(ay[c], y, q, "son") for c in ("TP.FDVY28", "TP.FDVY30", "TP.FDVY33", "TP.FDVY35"))
        poz = uc_ay(ay["TP.FDVY37"], y, q, "son")
        tahvil = ceyrek_son_hafta(y, q)
        cds_q = ceyrek_son_cds(y, q)
        stok[(y, q)] = {
            "E": e, "R": r, "NHN_m": nhn, "KACIS_m": kacis, "ALTIN_netihr_m": altin_net_ihr,
            "TIC_yuk_m": tic, "G49": g49, "G57": g57, "BEK": bek, "VADE_m": vade,
            "POZ_m": poz, "TAHVIL_m": tahvil, "CDS": cds_q,
        }

    # EMP, tam örnek 2016-Q2..2025-Q4
    ham_e, ham_r = [], []
    for y, q in ceyrekler:
        if (y, q) < (2016, 2):
            continue
        py, pq = (y, q - 1) if q > 1 else (y - 1, 4)
        E, Ep = stok[(y, q)]["E"], stok[(py, pq)]["E"]
        R, Rp = stok[(y, q)]["R"], stok[(py, pq)]["R"]
        if None in (E, Ep, R, Rp) or Ep <= 0 or Rp == 0:
            continue
        ham_e.append(100.0 * math.log(E / Ep))
        ham_r.append(100.0 * (R - Rp) / Rp)
    se, sr = sd(ham_e), sd(ham_r)
    w = se / sr

    panel = []
    for y, q in ceyrekler:
        if (y, q) < (2016, 2):
            continue
        py, pq = (y, q - 1) if q > 1 else (y - 1, 4)
        a, b = stok[(y, q)], stok[(py, pq)]
        if None in (a["E"], b["E"], a["R"], b["R"]) or b["E"] <= 0 or b["R"] == 0:
            continue
        e = 100.0 * math.log(a["E"] / b["E"])
        r = 100.0 * (a["R"] - b["R"]) / b["R"]
        row = {
            "q": f"{y}-Q{q}",
            "y": y,
            "qq": q,
            "e": e,
            "r": r,
            "EMP": e - w * r,
            "E": a["E"],
            "R": a["R"],
        }
        if a["NHN_m"] is not None:
            row["NHN"] = -a["NHN_m"] / 1000.0
        if a["TAHVIL_m"] is not None and b["TAHVIL_m"] is not None:
            row["TAHVIL"] = -(a["TAHVIL_m"] - b["TAHVIL_m"]) / 1000.0
        if None not in (a["G49"], a["G57"], b["G49"], b["G57"]) and a["G57"] and b["G57"]:
            row["DOLAR"] = 100.0 * (a["G49"] / a["G57"] - b["G49"] / b["G57"])
        if a["KACIS_m"] is not None:
            row["KACIS"] = a["KACIS_m"] / 1000.0
        if a["ALTIN_netihr_m"] is not None:
            row["ALTIN"] = -a["ALTIN_netihr_m"] / 1000.0
        if a["TIC_yuk_m"] is not None:
            row["TICARI"] = -a["TIC_yuk_m"] / 1000.0
        if a["VADE_m"] is not None and b["VADE_m"] is not None:
            row["VADE"] = (a["VADE_m"] - b["VADE_m"]) / 1000.0
        if a["POZ_m"] is not None and b["POZ_m"] is not None:
            row["POZ"] = -(a["POZ_m"] - b["POZ_m"]) / 1000.0
        if a["CDS"] is not None and b["CDS"] is not None:
            row["CDS"] = a["CDS"] - b["CDS"]
        if a["BEK"] is not None and b["BEK"] is not None and a["BEK"] > 0 and b["BEK"] > 0:
            row["BEK"] = 100.0 * math.log(a["BEK"] / b["BEK"])
        panel.append(row)

    taban = ["NHN", "TAHVIL", "DOLAR", "KACIS", "ALTIN", "TICARI"]
    adaylar = ["VADE", "POZ", "CDS", "BEK"]

    def tam_endeks(adlar):
        return [i for i, row in enumerate(panel) if all(k in row for k in adlar)]

    taban_ix = tam_endeks(taban)
    taban_model = model(panel, taban_ix, taban)

    def kalinti_katki(aday):
        ix = tam_endeks(taban + [aday])
        m0 = model(panel, ix, taban)
        m1 = model(panel, ix, taban + [aday])
        qlar = m0["ceyrekler"]
        j = qlar.index("2021-Q4")
        b = panel[ix[j]]["EMP"] - float(m0["yhat"][j])
        fark = float(m1["yhat"][j]) - float(m0["yhat"][j])
        if abs(b) < 1.0:
            durum = "kalinti_yok"
            oran = None
        elif b == 0:
            durum = "kalinti_yok"
            oran = None
        elif fark * b > 0:
            oran = abs(fark) / abs(b)
            durum = "kapandi" if oran >= 0.50 else "esik_alti"
        else:
            oran = 0.0
            durum = "ters_yon"
        return {
            "n": len(ix),
            "ilk": qlar[0],
            "son": qlar[-1],
            "EMP": panel[ix[j]]["EMP"],
            "taban_uyum": float(m0["yhat"][j]),
            "aday_uyum": float(m1["yhat"][j]),
            "b": b,
            "fark": fark,
            "oran": oran,
            "durum": durum,
            "r2_taban": m0["r2"],
            "r2_aday": m1["r2"],
            "katsayi": m1["beta"][len(taban) + 1],
            "pay": m1["pay"][len(taban)],
            "phi": m1["phi"][len(taban)],
            "tekil": m1["tekil"],
        }

    sonuclar_aday = {}
    kayan = {}
    for aday in adaylar:
        ix = tam_endeks(taban + [aday])
        m = model(panel, ix, taban + [aday])
        sonuclar_aday[aday] = {
            "n": m["n"],
            "ilk": m["ceyrekler"][0],
            "son": m["ceyrekler"][-1],
            "r2": m["r2"],
            "tekil": m["tekil"],
            "katsayi": m["beta"][-1],
            "pay": m["pay"][-1],
            "phi": m["phi"][-1],
            "taban_pay": {ad: m["pay"][i] for i, ad in enumerate(taban)},
            "kalinti": kalinti_katki(aday),
        }
        kayan[aday] = pencere_ozet(panel, ix, taban + [aday], aday)
        kayan[aday].pop("pencereler")

    ortak = tam_endeks(taban + adaylar)
    birlikte = model(panel, ortak, taban + adaylar)
    birlikte_ozet = {
        "n": birlikte["n"],
        "r2": birlikte["r2"],
        "tekil": birlikte["tekil"],
        "katsayi": {ad: birlikte["beta"][i + 1] for i, ad in enumerate(taban + adaylar)},
        "pay": {ad: birlikte["pay"][i] for i, ad in enumerate(taban + adaylar)},
    }

    # 2021-Q4 taban ayrıştırması (ortak taban örneklemi)
    j = taban_model["ceyrekler"].index("2021-Q4")
    b_taban = panel[taban_ix[j]]["EMP"] - float(taban_model["yhat"][j])

    # C1
    gunler = sorted(gun)
    def log_fark(i):
        return math.log(gun[gunler[i]] / gun[gunler[i - 1]])

    def c1(tarih):
        once = [i for i, d in enumerate(gunler) if d < tarih and i > 0]
        sonra = [i for i, d in enumerate(gunler) if d >= tarih and i > 0]
        if len(once) < 5 or len(sonra) < 5:
            return {"durum": "DOGRULANMADI"}
        po = once[-5:]
        ps = sonra[:5]
        s_once = sum(log_fark(i) for i in po)
        s_sonra = sum(log_fark(i) for i in ps)
        onde = s_once > 0 and s_once > s_sonra
        return {
            "once_toplam": s_once,
            "sonra_toplam": s_sonra,
            "once_gunler": [gunler[i].strftime("%Y-%m-%d") for i in po],
            "sonra_gunler": [gunler[i].strftime("%Y-%m-%d") for i in ps],
            "fiyat_pencerede_onde": onde,
        }

    olaylar = {
        "2021-09-23": "faiz",
        "2021-10-21": "faiz",
        "2021-11-18": "faiz",
        "2021-12-16": "faiz",
        "2021-12-20": "kkm",
        "2023-05-14": "secim",
        "2023-05-28": "secim",
    }
    c1_sonuc = {t: c1(datetime.strptime(t, "%Y-%m-%d")) | {"tur": tur} for t, tur in olaylar.items()}
    kume_2021 = [c1_sonuc[t]["fiyat_pencerede_onde"] for t in olaylar if t.startswith("2021")]
    c1_kume = sum(bool(x) for x in kume_2021) >= 3

    # C2
    def kur_veya_once(d):
        # Tatil gününde satış kuru yoksa, indirilen aralıktaki son kur.
        # Üç günlük tavan yok: 2023-06-30 Kurban tatiline denk gelir.
        if d in gun:
            return gun[d], False, 0
        once = [x for x in gunler if x <= d]
        if not once:
            return None, True, None
        p = once[-1]
        return gun[p], True, (d - p).days

    def c2(bas, son):
        bas_d, son_d = datetime.strptime(bas, "%Y-%m-%d"), datetime.strptime(son, "%Y-%m-%d")
        fr = sorted(d for d in hafta if bas_d <= d <= son_d)
        if len(fr) < 2:
            return {"durum": "DOGRULANMADI", "neden": "haftalik stok yok"}
        adim = []
        cp = cf = 0.0
        vekil_kur = 0
        en_uzun_bosluk = 0
        for d in fr:
            oncekiler = [x for x in hafta if x < d]
            if not oncekiler:
                continue
            d0 = max(oncekiler)
            p1, v1, g1 = kur_veya_once(d)
            p0, v0, g0 = kur_veya_once(d0)
            if p1 is None or p0 is None or p0 <= 0:
                return {"durum": "DOGRULANMADI", "neden": "kur eslesmedi", "gun": d.strftime("%Y-%m-%d")}
            vekil_kur += int(v1 or v0)
            en_uzun_bosluk = max(en_uzun_bosluk, g1 or 0, g0 or 0)
            dp = 100.0 * math.log(p1 / p0)
            df = -(hafta[d] - hafta[d0]) / 1000.0
            cp += dp
            cf += df
            adim.append({"tarih": d.strftime("%Y-%m-%d"), "dp": dp, "df": df, "cp": cp, "cf": cf})
        if not adim:
            return {"durum": "DOGRULANMADI"}
        son_p, son_f = adim[-1]["cp"], adim[-1]["cf"]
        if son_p <= 0 or son_f <= 0:
            hukum = "yon_yok"
            tp = tf = None
        else:
            tp = next(i for i, a in enumerate(adim) if a["cp"] >= 0.5 * son_p)
            tf = next(i for i, a in enumerate(adim) if a["cf"] >= 0.5 * son_f)
            if tp < tf:
                hukum = "fiyat_once"
            elif tf < tp:
                hukum = "akim_once"
            else:
                hukum = "ayni_hafta"
        return {
            "durum": hukum,
            "son_deger_kaybi": son_p,
            "son_tahvil_satisi": son_f,
            "hafta_fiyat": None if tp is None else adim[tp]["tarih"],
            "hafta_akim": None if tf is None else adim[tf]["tarih"],
            "vekil_kur_sayisi": vekil_kur,
            "en_uzun_bosluk_gun": en_uzun_bosluk,
            "adim": adim,
        }

    c2_sonuc = {
        "2021": c2("2021-09-01", "2022-01-15"),
        "2018": c2("2018-07-01", "2018-09-30"),
        "2023": c2("2023-04-01", "2023-06-30"),
    }

    # korelasyon, skor değil
    def kor(a, b, ix):
        xa = np.array([panel[i][a] for i in ix])
        xb = np.array([panel[i][b] for i in ix])
        if xa.std() == 0 or xb.std() == 0:
            return None
        return float(np.corrcoef(xa, xb)[0, 1])

    ix_nt = tam_endeks(["NHN", "TICARI"])
    ix_n = tam_endeks(["NHN", "TAHVIL"])

    # panel yaz
    alanlar = ["q", "e", "r", "EMP", "E", "R", "NHN", "TAHVIL", "DOLAR", "KACIS", "ALTIN", "TICARI", "VADE", "POZ", "CDS", "BEK"]
    with (KOK / "panel.csv").open("w", newline="") as f:
        wri = csv.DictWriter(f, fieldnames=alanlar, extrasaction="ignore")
        wri.writeheader()
        for row in panel:
            wri.writerow({k: row.get(k) for k in alanlar})

    q2021 = next(row for row in panel if row["q"] == "2021-Q4")
    ozet = {
        "emp": {
            "n": len(ham_e),
            "se": se,
            "sr": sr,
            "agirlik": w,
            "ilk": panel[0]["q"],
            "son": panel[-1]["q"],
            "q2021": {k: q2021[k] for k in ("EMP", "e", "r", "E", "R")},
        },
        "taban": {
            "n": taban_model["n"],
            "ilk": taban_model["ceyrekler"][0],
            "son": taban_model["ceyrekler"][-1],
            "r2": taban_model["r2"],
            "tekil": taban_model["tekil"],
            "katsayi": {ad: taban_model["beta"][i + 1] for i, ad in enumerate(taban)},
            "pay": {ad: taban_model["pay"][i] for i, ad in enumerate(taban)},
            "q2021_EMP": panel[taban_ix[j]]["EMP"],
            "q2021_uyum": float(taban_model["yhat"][j]),
            "q2021_b": b_taban,
        },
        "aday": sonuclar_aday,
        "kayan": kayan,
        "birlikte": birlikte_ozet,
        "c1": c1_sonuc,
        "c1_2021_cogunluk": c1_kume,
        "c2": {k: {kk: vv for kk, vv in v.items() if kk != "adim"} | {"adim_sayisi": len(v.get("adim") or [])} for k, v in c2_sonuc.items()},
        "korelasyon": {
            "NHN_TICARI": {"r": kor("NHN", "TICARI", ix_nt), "n": len(ix_nt)},
            "NHN_TAHVIL": {"r": kor("NHN", "TAHVIL", ix_n), "n": len(ix_n)},
        },
    }
    # C2 adımlarını da sakla
    ozet["c2_adim"] = {k: v.get("adim") for k, v in c2_sonuc.items()}
    (KOK / "sonuclar.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=2))
    print(json.dumps({k: ozet[k] for k in ("emp", "taban", "aday", "kayan", "birlikte", "c1", "c1_2021_cogunluk", "c2", "korelasyon")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
