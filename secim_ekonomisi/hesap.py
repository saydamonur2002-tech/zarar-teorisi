"""Seçim ekonomisi. Kurallar: secim_ekonomisi/ON_KAYIT.md."""
import json
import math
from pathlib import Path

import numpy as np

KOK = Path(__file__).resolve().parent
SEED = 20261020
N_PL = 2000

GENEL = ["2002-11", "2007-07", "2011-06", "2015-06", "2015-11", "2018-06", "2023-05"]
YEREL = ["2004-03", "2009-03", "2014-03", "2019-03", "2024-03"]
REF = ["2010-09", "2017-04"]
OLAY = GENEL + YEREL + REF


def ay_ix(t):
    y, m = t.split("-")
    return int(y) * 12 + int(m) - 1


def ix_ay(i):
    y, m = divmod(i, 12)
    return f"{y}-{m+1:02d}"


def sd(xs):
    xs = np.asarray(xs, float)
    return float(xs.std(ddof=1))


def holm(ps):
    m = len(ps)
    order = np.argsort(ps)
    adj = np.empty(m)
    run = 0.0
    for rank, j in enumerate(order):
        run = max(run, (m - rank) * ps[j])
        adj[j] = min(1.0, run)
    return adj


def takvim_cek(rng, uygun, n=7):
    uygun = np.asarray(sorted(uygun))
    if len(uygun) < n:
        return None
    for _ in range(400):
        sec = np.sort(rng.choice(uygun, size=n, replace=False))
        if np.all(np.diff(sec) >= 12):
            return sec
    return None


def main():
    ham = json.loads((KOK / "ham_ay.json").read_text())
    son = json.loads((KOK / "ay_sonu_kur.json").read_text())

    # Ay sonu kur, 2005 öncesi eski lira
    e_son = {}
    for t, rec in son.items():
        v = rec["kur"]
        if t < "2005-01":
            v = v / 1_000_000.0
        e_son[t] = v

    # Ortak ay indeksi
    tum = set()
    for d in ham.values():
        tum.update(d)
    tum.update(e_son)
    idx = sorted(ay_ix(t) for t in tum)
    i0, i1 = idx[0], idx[-1]

    def seri(kod):
        src = ham.get(kod, {})
        out = {}
        for t, v in src.items():
            out[ay_ix(t)] = v
        return out

    E = seri("TP.DK.USD.S.YTL")
    R = seri("TP.REZVARPD.K1")
    faiz = seri("TP.BISPOLFAIZ.TUR")
    fon = seri("TP.APIFON4")
    cpi = seri("TP.GENENDEKS.T1")
    gid = seri("TP.KB.GID002")
    per = seri("TP.KB.GID003")
    trn = seri("TP.KB.GID026")
    kre = seri("TP.KREHACBS.A1")
    a02 = seri("TP.AB.A02")
    a10 = seri("TP.AB.A10")
    swap = seri("TP.SWAPTEKTAR.TOTALSTOKALIMYONLU")
    Es = {ay_ix(t): v for t, v in e_son.items()}

    def log_emp(kur, rezerv, bas="2002-01"):
        b = ay_ix(bas)
        ee, rr, emap = [], [], {}
        for i in range(b, i1 + 1):
            if i not in kur or i - 1 not in kur or i not in rezerv or i - 1 not in rezerv:
                continue
            if kur[i - 1] <= 0 or rezerv[i - 1] == 0:
                continue
            e = 100.0 * math.log(kur[i] / kur[i - 1])
            r = 100.0 * (rezerv[i] - rezerv[i - 1]) / rezerv[i - 1]
            ee.append(e)
            rr.append(r)
            emap[i] = (e, r)
        w = sd(ee) / sd(rr)
        emp = {i: e - w * r for i, (e, r) in emap.items()}
        return emp, w, sd(ee), sd(rr), len(ee)

    emp, w, se, sr, n_emp = log_emp(E, R)
    emp_s, w_s, se_s, sr_s, n_s = log_emp(Es, R)

    def fark(src):
        return {i: src[i] - src[i - 1] for i in src if i - 1 in src}

    d_faiz = fark(faiz)
    d_fon = fark(fon)

    def r_yuzde(src):
        out = {}
        for i in src:
            if i - 1 in src and src[i - 1] != 0:
                out[i] = 100.0 * (src[i] - src[i - 1]) / src[i - 1]
        return out

    dR = r_yuzde(R)

    # Net rezerv, bin TL / kur / 1000 = milyon dolar
    net = {}
    for i in a02:
        if i in a10 and i in E and E[i] > 0:
            net[i] = (a02[i] - a10[i]) / E[i] / 1000.0
    net_swap = {}
    for i in net:
        if i in swap:
            net_swap[i] = net[i] - swap[i]
    d_net = r_yuzde(net)
    d_nets = r_yuzde(net_swap)

    arka = {}
    for i in R:
        if i - 1 in R and i in swap and i - 1 in swap:
            arka[i] = -(R[i] - R[i - 1]) + (swap[i] - swap[i - 1])

    def reel_yoy(nom):
        out = {}
        for i in nom:
            if i - 12 in nom and i in cpi and i - 12 in cpi and cpi[i] and cpi[i - 12] and nom[i - 12]:
                real = nom[i] / cpi[i]
                real0 = nom[i - 12] / cpi[i - 12]
                if real0 != 0:
                    out[i] = 100.0 * (real / real0 - 1.0)
        return out

    g_gid = reel_yoy(gid)
    g_per = reel_yoy(per)
    g_trn = reel_yoy(trn)

    def yoy(src):
        out = {}
        for i in src:
            if i - 12 in src and src[i - 12]:
                out[i] = 100.0 * (src[i] / src[i - 12] - 1.0)
        return out

    g_kre = yoy(kre)

    # Bütçe birikimli mi? Ocak, şubatın üstünde olabiliyor. Akım = düzey.
    butce_not = "aylik_akim"

    olay_i = [ay_ix(t) for t in OLAY]
    genel_i = [ay_ix(t) for t in GENEL]

    def yakin(i):
        return any(abs(i - o) <= 12 for o in olay_i)

    def pencere(i, a, b):
        return list(range(i + a, i + b + 1))

    def tam(src, aylar):
        return all(k in src for k in aylar)

    def ortalama(src, aylar):
        return float(np.mean([src[k] for k in aylar]))

    # Göstergeler: ad, seri, gevşeme yönü (-1 negatif gevşeme), h1'e girer mi
    gostergeler = [
        ("faiz", d_faiz, -1),
        ("fonlama", d_fon, -1),
        ("rezerv", dR, -1),
        ("net_swap", d_nets, -1),
        ("arka", arka, +1),
        ("harcama", g_gid, +1),
        ("transfer", g_trn, +1),
        ("personel", g_per, +1),
        ("kredi", g_kre, +1),
    ]

    def uygun_on(src):
        out = []
        for i in range(i0, i1 + 1):
            ay = pencere(i, -6, -1)
            if tam(src, ay):
                out.append(i)
        return out

    def uygun_son(src):
        out = []
        for i in range(i0, i1 + 1):
            ay = pencere(i, 1, 6)
            if tam(src, ay):
                out.append(i)
        return out

    def taban_ort(src):
        xs = [src[i] for i in src if not yakin(i)]
        if len(xs) < 24:
            return None, len(xs)
        return float(np.mean(xs)), len(xs)

    def plasebo_on(src, yon):
        rng = np.random.default_rng(SEED)
        uygun = uygun_on(src)
        takvimler = []
        deneme = 0
        while len(takvimler) < N_PL and deneme < N_PL * 40:
            deneme += 1
            tk = takvim_cek(rng, uygun)
            if tk is not None:
                takvimler.append(tk)
        if len(takvimler) < N_PL:
            return None
        olay_deger = []
        havuz = []
        tb, _ = taban_ort(src)
        for tk in takvimler:
            ortlar = []
            aylar = []
            for ev in tk:
                ay = pencere(int(ev), -6, -1)
                ortlar.append(ortalama(src, ay))
                aylar.extend(ay)
            olay_deger.extend(ortlar)
            havuz.append(float(np.mean([src[a] for a in set(aylar)])) - tb)
        return np.asarray(olay_deger), np.asarray(havuz), tb

    def yuzdelik(deger, dagilim):
        return 100.0 * float(np.mean(dagilim < deger))

    def uc_mu(deger, dagilim, yon):
        p = yuzdelik(deger, dagilim)
        if yon < 0:
            return p <= 10.0, p
        return p >= 90.0, p

    sonuclar = {}
    h1_p = []
    h1_ad = []
    for ad, src, yon in gostergeler:
        gen_tam = []
        for t in GENEL:
            i = ay_ix(t)
            if tam(src, pencere(i, -6, -1)):
                gen_tam.append(t)
        tb, n_tb = taban_ort(src)
        rec = {
            "n_genel": len(gen_tam),
            "genel": gen_tam,
            "taban": tb,
            "n_taban": n_tb,
            "cubuk": "DOGRULANMADI" if len(gen_tam) < 6 or tb is None else "hesap",
        }
        if rec["cubuk"] == "DOGRULANMADI":
            # Yine de olan seçimleri yaz, hükme girmez
            rec["secim"] = {}
            for t in gen_tam:
                i = ay_ix(t)
                rec["secim"][t] = ortalama(src, pencere(i, -6, -1))
            sonuclar[ad] = rec
            continue
        pack = plasebo_on(src, yon)
        if pack is None:
            rec["cubuk"] = "DOGRULANMADI"
            sonuclar[ad] = rec
            continue
        olay_d, havuz_d, tb = pack
        secim = {}
        uc_n = 0
        for t in gen_tam:
            i = ay_ix(t)
            val = ortalama(src, pencere(i, -6, -1))
            uc, pctl = uc_mu(val, olay_d, yon)
            secim[t] = {"ort": val, "yuzdelik": pctl, "uc": uc, "fark": val - tb}
            uc_n += int(uc)
        havuz_goz = ortalama(src, sorted({a for t in gen_tam for a in pencere(ay_ix(t), -6, -1)})) - tb
        if yon < 0:
            p = (1 + np.sum(havuz_d <= havuz_goz)) / (1 + N_PL)
        else:
            p = (1 + np.sum(havuz_d >= havuz_goz)) / (1 + N_PL)
        rec.update({
            "secim": secim,
            "uc": uc_n,
            "uc_oran": uc_n / len(gen_tam),
            "secim_cubugu": uc_n / len(gen_tam) >= 2 / 3,
            "havuz": havuz_goz,
            "p": float(p),
        })
        sonuclar[ad] = rec
        h1_p.append(float(p))
        h1_ad.append(ad)

    if h1_p:
        adj = holm(h1_p)
        for ad, p, a in zip(h1_ad, h1_p, adj):
            sonuclar[ad]["holm"] = float(a)
            sonuclar[ad]["iki_cubuk"] = bool(sonuclar[ad]["secim_cubugu"] and a < 0.05)

    # H2 EMP ve faiz
    def h2(ad, src, yon):
        gen_tam = [t for t in GENEL if tam(src, pencere(ay_ix(t), 1, 6))]
        tb, n_tb = taban_ort(src)
        rec = {"n_genel": len(gen_tam), "taban": tb, "n_taban": n_tb}
        if len(gen_tam) < 6 or tb is None:
            rec["cubuk"] = "DOGRULANMADI"
            rec["secim"] = {}
            for t in gen_tam:
                rec["secim"][t] = ortalama(src, pencere(ay_ix(t), 1, 6))
            return rec
        rng = np.random.default_rng(SEED)
        uygun = uygun_son(src)
        takvimler = []
        den = 0
        while len(takvimler) < N_PL and den < N_PL * 40:
            den += 1
            tk = takvim_cek(rng, uygun)
            if tk is not None:
                takvimler.append(tk)
        havuz_d = []
        for tk in takvimler:
            aylar = []
            for ev in tk:
                aylar.extend(pencere(int(ev), 1, 6))
            havuz_d.append(float(np.mean([src[a] for a in set(aylar)])) - tb)
        havuz_d = np.asarray(havuz_d)
        aylar = sorted({a for t in gen_tam for a in pencere(ay_ix(t), 1, 6)})
        havuz = ortalama(src, aylar) - tb
        if yon > 0:
            p = (1 + np.sum(havuz_d >= havuz)) / (1 + len(takvimler))
        else:
            p = (1 + np.sum(havuz_d <= havuz)) / (1 + len(takvimler))
        secim = {}
        poz = 0
        for t in gen_tam:
            val = ortalama(src, pencere(ay_ix(t), 1, 6))
            fark = val - tb
            secim[t] = {"ort": val, "fark": fark}
            if yon > 0 and fark > 0:
                poz += 1
            if yon < 0 and fark < 0:
                poz += 1
        rec.update({
            "cubuk": "hesap",
            "secim": secim,
            "havuz": havuz,
            "p": float(p),
            "pozitif_secim": poz,
            "pozitif_oran": poz / len(gen_tam),
            "n_pl": len(takvimler),
        })
        return rec

    h2_emp = h2("emp", emp, +1)
    h2_faiz = h2("faiz", d_faiz, +1)
    h2_fon = h2("fonlama", d_fon, +1)
    # ay sonu havuz işareti
    h2_son = h2("emp_son", emp_s, +1)

    h2_aile = []
    h2_isim = []
    for ad, rec in (("emp", h2_emp), ("faiz", h2_faiz), ("fonlama", h2_fon)):
        if rec.get("cubuk") == "hesap":
            h2_aile.append(rec["p"])
            h2_isim.append(ad)
    if h2_aile:
        for ad, a in zip(h2_isim, holm(h2_aile)):
            {"emp": h2_emp, "faiz": h2_faiz, "fonlama": h2_fon}[ad]["holm"] = float(a)

    # H3
    def h3_bir(src, yon):
        q = [ay_ix(t) for t in ("2021-10", "2021-11", "2021-12")]
        if not tam(src, q):
            return {"durum": "DOGRULANMADI"}
        v21 = ortalama(src, q)
        onceler = []
        uzak = []
        for t in GENEL:
            if t == "2023-05":
                continue
            i = ay_ix(t)
            a = pencere(i, -6, -1)
            b = pencere(i, -20, -18)
            if tam(src, a):
                onceler.append(ortalama(src, a))
            if tam(src, b):
                uzak.append(ortalama(src, b))
        if len(onceler) < 4 or len(uzak) < 4:
            return {"durum": "DOGRULANMADI", "v21": v21}
        m = float(np.mean(onceler))
        s = sd(onceler)
        benzer = abs(v21 - m) <= s
        # gevşeme yönünde ve 2021'in en az yarısı
        if yon < 0:
            gev = v21 < 0
            yari = sum(1 for u in uzak if u <= 0.5 * v21) if gev else 0
        else:
            gev = v21 > 0
            yari = sum(1 for u in uzak if u >= 0.5 * v21) if gev else 0
        diger = yari >= math.ceil(len(uzak) / 2)
        uyar = bool(benzer and diger and gev)
        return {
            "durum": "uyar" if uyar else "aciklanamaz",
            "v21": v21,
            "on_ortalama": m,
            "on_sd": s,
            "benzer": benzer,
            "uzak": uzak,
            "diger": diger,
        }

    # Çeyreklik mutabakat, PR #38
    def q_of(i):
        y, m = divmod(i, 12)
        return y, (m // 3) + 1

    qE, qR = {}, {}
    for i, v in E.items():
        y, q = q_of(i)
        qE.setdefault((y, q), []).append(v)
    for i, v in R.items():
        y, q = q_of(i)
        m = divmod(i, 12)[1] + 1
        if m in (3, 6, 9, 12):
            qR[(y, q)] = v
    qs = sorted(set(qE) & set(qR))
    ham_e, ham_r = [], []
    qemp = {}
    for k in range(1, len(qs)):
        y, q = qs[k]
        if (y, q) < (2016, 2) or (y, q) > (2025, 4):
            continue
        yp, qp = qs[k - 1]
        # ardışık çeyrek
        if ay_ix(f"{y}-{q*3:02d}") - ay_ix(f"{yp}-{qp*3:02d}") != 3:
            continue
        vals = qE[(y, q)]
        prev = qE[(yp, qp)]
        if len(vals) < 3 or len(prev) < 3:
            continue
        Ee, Ep = sum(vals) / 3, sum(prev) / 3
        e = 100 * math.log(Ee / Ep)
        r = 100 * (qR[(y, q)] - qR[(yp, qp)]) / qR[(yp, qp)]
        ham_e.append(e)
        ham_r.append(r)
        qemp[(y, q)] = (e, r)
    wq = sd(ham_e) / sd(ham_r)
    e21, r21 = qemp[(2021, 4)]
    emp21 = e21 - wq * r21
    emp21_w = e21 - 0.568 * r21

    # Olay yolu, genel, birincil EMP ve faiz
    yol = {}
    for ad, src in (("emp", emp), ("faiz", d_faiz)):
        yol[ad] = {}
        for h in range(-12, 13):
            xs = []
            for t in GENEL:
                i = ay_ix(t) + h
                if i in src:
                    xs.append(src[i])
            yol[ad][str(h)] = None if len(xs) < 5 else float(np.mean(xs))

    # Seçim tablosu
    tablo = []
    for t, tur in [(x, "genel") for x in GENEL] + [(x, "yerel") for x in YEREL] + [(x, "referandum") for x in REF]:
        i = ay_ix(t)
        row = {"secim": t, "tur": tur}
        for ad, src in (
            ("faiz", d_faiz), ("fonlama", d_fon), ("rezerv", dR),
            ("emp", emp), ("emp_son", emp_s),
            ("harcama", g_gid), ("transfer", g_trn), ("personel", g_per),
            ("kredi", g_kre), ("arka", arka), ("net_swap", d_nets),
        ):
            pre, post = pencere(i, -6, -1), pencere(i, 1, 6)
            row[ad + "_pre"] = ortalama(src, pre) if tam(src, pre) else None
            row[ad + "_post"] = ortalama(src, post) if tam(src, post) else None
        tablo.append(row)

    # 2023 öncesi 12 ay faiz ve EMP, H3 için düz bakış
    ozet = {
        "emp_ay": {"n": n_emp, "se": se, "sr": sr, "w": w},
        "emp_son": {"n": n_s, "se": se_s, "sr": sr_s, "w": w_s},
        "mutabakat": {
            "e_2021q4": e21, "r_2021q4": r21, "w": wq, "emp": emp21,
            "emp_w0568": emp21_w,
        },
        "butce": butce_not,
        "net_2021_12": {
            "net_mn": net.get(ay_ix("2021-12")),
            "swap": swap.get(ay_ix("2021-12")),
            "net_swap": net_swap.get(ay_ix("2021-12")),
            "brut": R.get(ay_ix("2021-12")),
        },
        "h1": {k: {kk: vv for kk, vv in rec.items() if kk != "secim"} | {"secim": rec.get("secim")} for k, rec in sonuclar.items()},
        "h2": {"emp": h2_emp, "faiz": h2_faiz, "fonlama": h2_fon, "emp_son": {k: v for k, v in h2_son.items() if k != "secim"} | {"secim": h2_son.get("secim")}},
        "h3": {"faiz": h3_bir(d_faiz, -1), "emp": h3_bir(emp, +1), "harcama": h3_bir(g_gid, +1)},
        "yol": yol,
        "tablo": tablo,
        "fred": "DOGRULANMADI",
    }
    (KOK / "sonuclar.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=2))
    print("EMP w", round(w, 3), "n", n_emp, "son w", round(w_s, 3))
    print("Q4", round(emp21, 2), "w", round(wq, 3), "dayatma", round(emp21_w, 2))
    print("H1")
    for ad, rec in sonuclar.items():
        print(ad, rec.get("cubuk"), "n", rec.get("n_genel"), "uc", rec.get("uc"), "p", rec.get("p"), "holm", rec.get("holm"), "havuz", rec.get("havuz"), "iki", rec.get("iki_cubuk"))
    print("H2 emp", {k: h2_emp.get(k) for k in ("havuz", "p", "holm", "pozitif_secim", "n_genel")})
    print("H2 faiz", {k: h2_faiz.get(k) for k in ("havuz", "p", "holm", "pozitif_secim", "n_genel")})
    print("H2 fon", {k: h2_fon.get(k) for k in ("havuz", "p", "holm", "pozitif_secim", "cubuk")})
    print("H2 son", {k: h2_son.get(k) for k in ("havuz", "p", "pozitif_secim", "n_genel")})
    print("H3", json.dumps(ozet["h3"], ensure_ascii=False)[:800])


if __name__ == "__main__":
    main()
