"""Seçici kredi modelinin Türkiye'ye kalibrasyonu (secici_kredi.py üzerinde).

İki katman, ayrı etiketli:
  1) ÇAPALAR: ölçülebilen başlangıç durumu parametreleri, Veri_Girişi serisinden (2025) doğrudan türetilir.
     Etiket: 'olcum' (resmî seri), 'tahmin' (resmî seriden türetilmiş ama tabloda tahmin işaretli), 'ayni' (ölçülemedi, tablodaki
     temsilî değer korundu).
  2) DAVRANIŞ: alpha, pt, rho ve S1 kolunun tay, cred değerleri. Anketlerin (PKA, bes_yil_senaryo.csv) 2026-2027 yolu
     (TÜFE, politika faizi, kur) 6 momenti üzerinde Nelder-Mead ile uydurulur; 2028 (TÜFE, faiz) ve 2031 (TÜFE) örnek DIŞI.
     Beş serbest parametre, altı moment: neredeyse tam belirlenmiş; bu bir kestirim değil, bir ayardır.
Ek: tablonun kendi "Eleştiri_ve_Testler" #12 sınaması: kalibre edilmiş davranış parametreleriyle t0 = 2017..2024 başlangıçlarından
ileri 1 yıllık TÜFE tahmini ile naif tahminin (TÜFE_t) kıyası.

Çalıştır: python3 secici_kredi_kalibre.py   (çıktı: secici_kredi_kalibre.json, SECICI_KREDI.md)
"""

import csv
import json
import math
from pathlib import Path

import secici_kredi as K

KOK = Path(__file__).resolve().parent
S1_IND = 0.77  # Ocak asgari ücret artışı / önceki yıl TÜFE, 2024 0,76 / 2025 0,68 / 2026 0,87 ortalaması (hekis_model/ENFLASYON.md, ucret.py)
BORC_BOL = 0.4  # H1'in borç payı: tablonun varsayılan D10/(D10+D20) = 4/10, ölçülemedi
KUR = {2025: 42.88}  # TCMB 31.12.2025 (hekis_model/hekis/kalibre.py)
SERBEST = ("alpha", "pt", "rho", "tay", "cred")
SINIR = {"alpha": (0.1, 1.6), "pt": (0.0, 0.8), "rho": (0.0, 1.5), "tay": (0.0, 1.6), "cred": (0.05, 0.9)}


def capa(V, y):
    """Yıl y verisinden başlangıç durumu parametreleri ve etiketleri. Veri yoksa değer eklenmez."""
    g = lambda k, yy=y: V[k].get(yy)
    P, et = {}, {}
    gs = K.gostergeler(V, y)
    if g("V24") is not None:
        P["pi0"], et["pi0"] = g("V24"), ("olcum", "V24 TÜFE Aralık/Aralık")
    if g("V01") and g("V15"):
        P["om0"], et["om0"] = g("V01") / g("V15"), ("tahmin", "V01/V15; V01 tabloda GSYH×0,600 (TÜİK 2023-24 oranı)")
    if g("V16") is not None and g("V15"):
        P["cad0"], et["cad0"] = g("V16") / g("V15"), ("olcum", "V16/V15 (C1 göstergesi)")
    if g("V17") and g("V15"):
        P["X0"], et["X0"] = 100 * g("V17") / g("V15"), ("tahmin", "V17/V15; V17 tabloda (mal+seyahat)×1,25×kur")
    if g("V20") is not None and g("V15"):
        P["nfp"], et["nfp"] = g("V20") / g("V15"), ("tahmin", "V20/V15; ikincil gelir dahil vekil")
    if gs["A1"] is not None and "om0" in P:
        P["Cf0"], et["Cf0"] = gs["A1"] * P["om0"] * 100, ("tahmin", "A1 × Yh0; V02 tabloda tahmin")
    if g("V03") and g("V01") and "om0" in P:
        tot = g("V03") / g("V01") * P["om0"] * 100
        P["D10"], P["D20"] = BORC_BOL * tot, (1 - BORC_BOL) * tot
        et["D10"] = et["D20"] = ("tahmin", "V03/V01 × Yh0 toplam; H1/H2 bölüşümü 0,4/0,6 ölçülemedi")
    if g("V10") and g(("V10"), y - 1) and g("V03") and g("V04") and g("V15"):
        P["cc"], et["cc"] = ((g("V10") - g("V10", y - 1)) - (g("V03") - g("V04"))) / g("V15"), ("olcum", "(ΔV10 − bireysel kredi artışı)/V15")
    if gs["A2"] is not None:
        P["ccp_ref"], et["ccp_ref"] = gs["A2"], ("olcum", "A2 (V03−V04)/V01")
    if g("V28") and g("V25") is not None and g("V15"):
        P["G0"], et["G0"] = (g("V28") - g("V25")) / g("V15"), ("olcum", "(V28 − V25)/V15 faiz hariç merkezi yönetim gideri")
    if g("V18") and g("V17"):
        P["mx"], et["mx"] = g("V18") / g("V17"), ("tahmin", "C2 = V18/V17 (Kavram_Gösterge: C2 ↔ mx); iç satışa giden ara girdiyi de içerir, üst sınır")
    return P, et


def baz(V, y):
    P = K.varsayilan()
    P.pop("Z0", None)
    c, et = capa(V, y)
    P.update(c)
    # ithal içerik ölçeği: mc, mi, mg birlikte tek çarpanla, t0 ithalat kimliği M0 = X0 + cad0·AD0 − nfp·AD0 tutsun.
    # (mx ölçülmüş C2'ye bağlandı; geri kalan üç oran ölçülemedi, yalnız ortak ölçekleri kimlikten gelir.)
    if all(k in c for k in ("cad0", "X0", "nfp")):
        b = K.z0(P, bilesen=True)
        hedef = P["X0"] + P["cad0"] * P["AD0"] - P["nfp"] * P["AD0"] - P["mx"] * P["X0"]
        if b["ic_ithal"] > 0 and hedef > 0:
            lam = hedef / b["ic_ithal"]
            for k in ("mc", "mi", "mg"):
                P[k] *= lam
            et["mc"] = et["mi"] = et["mg"] = ("kalibre", f"t0 ithalat kimliği: ortak ölçek ×{lam:.3f}")
    P["Z0"] = K.z0(P)
    return P, et


def kol_s1(P, ccp=None, ind=S1_IND, tay=None, cred=None):
    a = dict(K.kollar(1))
    if ccp is not None:
        a["ccp"] = ccp
    a["ind"] = ind
    if tay is not None:
        a["tay"] = tay
    if cred is not None:
        a["cred"] = cred
    return a


def uygula(P0, arm0, x):
    P = dict(P0)
    a = dict(arm0)
    for k, v in zip(SERBEST, x):
        if k in ("tay", "cred"):
            a[k] = v
        else:
            P[k] = v
    return P, a


# Hedefler: PKA / bes_yil_senaryo.csv (anket). t=1 ↔ 2026 (t0 = 2025).
HEDEF = {
    "pi": {1: 0.2961, 2: 0.2269, 3: 0.1832, 6: 0.1209},
    "i": {1: 0.3507, 2: 0.2716, 3: 0.2243},
    "dep": {1: 51.5716 / 42.88 - 1, 2: 58.6049 / 51.5716 - 1},
}
ICERI = {"pi": (1, 2), "i": (1, 2), "dep": (1, 2)}
DISARI = {"pi": (3, 6), "i": (3,)}


def hata(rows, hedef, anahtar):
    return [(k, t, rows[t - 1][k] - hedef[k][t]) for k, ts in anahtar.items() for t in ts]


def kayip(x, P0, arm0, lam=0.02, x0=None):
    P, a = uygula(P0, arm0, x)
    try:
        rows = K.sim(P, a, T=2)
    except (ZeroDivisionError, OverflowError, ValueError):
        return 1e9
    e = [v for _, _, v in hata(rows, HEDEF, ICERI)]
    if any(not math.isfinite(v) for v in e):
        return 1e9
    pen = sum(max(0, lo - xi) ** 2 + max(0, xi - hi) ** 2 for xi, (lo, hi) in zip(x, (SINIR[k] for k in SERBEST))) * 1e3
    ridge = lam * sum((xi - x0i) ** 2 for xi, x0i in zip(x, x0)) if x0 else 0
    return sum(v * v for v in e) + pen + ridge


def nelder_mead(f, x0, adim=0.15, it=1500, tol=1e-12):
    n = len(x0)
    S = [list(x0)] + [[xi + (adim if i == j else 0) for j, xi in enumerate(x0)] for i in range(n)]
    F = [f(s) for s in S]
    for _ in range(it):
        o = sorted(range(n + 1), key=F.__getitem__)
        S, F = [S[i] for i in o], [F[i] for i in o]
        if abs(F[-1] - F[0]) < tol:
            break
        c = [sum(S[i][j] for i in range(n)) / n for j in range(n)]
        xr = [c[j] + (c[j] - S[-1][j]) for j in range(n)]
        fr = f(xr)
        if fr < F[0]:
            xe = [c[j] + 2 * (c[j] - S[-1][j]) for j in range(n)]
            fe = f(xe)
            S[-1], F[-1] = (xe, fe) if fe < fr else (xr, fr)
        elif fr < F[-2]:
            S[-1], F[-1] = xr, fr
        else:
            xc = [c[j] + 0.5 * (S[-1][j] - c[j]) for j in range(n)]
            fc = f(xc)
            if fc < F[-1]:
                S[-1], F[-1] = xc, fc
            else:
                S = [S[0]] + [[S[0][j] + 0.5 * (S[i][j] - S[0][j]) for j in range(n)] for i in range(1, n + 1)]
                F = [F[0]] + [f(s) for s in S[1:]]
    i = min(range(n + 1), key=F.__getitem__)
    return S[i], F[i]


def kalibre(V):
    P0, et = baz(V, 2025)
    arm0 = kol_s1(P0, ccp=P0["ccp_ref"])
    x0 = [P0["alpha"], P0["pt"], P0["rho"], arm0["tay"], arm0["cred"]]
    best = None
    # çoklu başlangıç: yerel minimum riskine karşı
    for k in range(8):
        xs = [min(max(v * (0.6 + 0.2 * ((k * (j + 3)) % 5)), SINIR[n][0] + 1e-3), SINIR[n][1] - 1e-3) for j, (v, n) in enumerate(zip(x0, SERBEST))]
        x, fx = nelder_mead(lambda z: kayip(z, P0, arm0, x0=x0), xs)
        if best is None or fx < best[1]:
            best = (x, fx)
    x = best[0]
    P, a = uygula(P0, arm0, x)
    return P0, arm0, P, a, x0, x, et


def geri_test(V, x, yillar=range(2017, 2025)):
    """t0 = y başlangıcından ileri 1 yıllık TÜFE: kalibre model ve naif (TÜFE_y) kıyası."""
    out = []
    for y in yillar:
        if V["V24"].get(y) is None or V["V24"].get(y + 1) is None or not V["V10"].get(y - 1):
            continue
        P0, _ = baz(V, y)
        a0 = kol_s1(P0, ccp=P0.get("ccp_ref", 0.04))
        P, a = uygula(P0, a0, x)
        tahmin = K.sim(P, a, T=1)[0]["pi"]
        gercek = V["V24"][y + 1]
        out.append({"yil": y + 1, "gercek": gercek, "model": tahmin, "naif": V["V24"][y]})
    return out


def senaryolar(P, a1):
    """S1 kalibre kolla, S2-S4 tablonun politika kollarıyla (kalibre davranış parametreleri ortak)."""
    sonuc = {}
    for s in (1, 2, 3, 4):
        arm = dict(K.kollar(s))
        if s == 1:
            arm = dict(a1)
        else:
            arm["tay"] = arm["tay"]
        rows = K.sim(P, arm)
        sonuc[s] = rows
    return sonuc


def main():
    V, _ = K.veri()
    P0, arm0, P, a, x0, x, et = kalibre(V)
    iceri = hata(K.sim(P, a, T=6), HEDEF, ICERI)
    disari = hata(K.sim(P, a, T=6), HEDEF, DISARI)
    onc = K.sim(K.varsayilan(), K.kollar(1), T=6)
    iceri0 = hata(onc, HEDEF, ICERI)
    disari0 = hata(onc, HEDEF, DISARI)
    gt = geri_test(V, x)
    sc = senaryolar(P, a)
    sc0 = {s: K.sim(K.varsayilan(), K.kollar(s)) for s in (1, 2, 3, 4)}
    rapor = {
        "serbest": dict(zip(SERBEST, x)), "baslangic": dict(zip(SERBEST, x0)),
        "iceri": [(k, t, round(v, 4)) for k, t, v in iceri], "disari": [(k, t, round(v, 4)) for k, t, v in disari],
        "iceri_kalibresiz": [(k, t, round(v, 4)) for k, t, v in iceri0], "disari_kalibresiz": [(k, t, round(v, 4)) for k, t, v in disari0],
        "geri_test": gt,
        "capa": {k: {"deger": P[k], "eski": K.varsayilan().get(k), "sinif": et[k][0], "kaynak": et[k][1]} for k in et},
        "Z0": P["Z0"],
    }
    json.dump(rapor, open(KOK / "secici_kredi_kalibre.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    with open(KOK / "secici_kredi_kalibre.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["senaryo", "kalibrasyon", "t", "pi", "i", "dep", "gAD", "cad", "gu1", "rw", "A", "loc", "kor", "rejim"])
        for kal, S in (("once", sc0), ("sonra", sc)):
            for s, rows in S.items():
                for r in rows:
                    w.writerow([f"S{s}", kal, r["t"]] + [round(r[k], 4) for k in ("pi", "i", "dep", "gAD", "cad", "gu1", "rw", "A", "loc", "kor")] + [r["rej"]])
    yaz(V, rapor, P, a, sc, sc0, et, x0, x)
    print(json.dumps({k: rapor[k] for k in ("serbest", "iceri", "disari", "iceri_kalibresiz", "disari_kalibresiz")}, ensure_ascii=False))
    print([(g["yil"], round(g["gercek"], 3), round(g["model"], 3), round(g["naif"], 3)) for g in gt])


def yaz(V, rapor, P, a, sc, sc0, et, x0, x):
    f2 = lambda v, d=3: f"{v:.{d}f}"
    L = ["# Seçici kredi modeli: Türkiye kalibrasyonu", "",
         "Çalıştır: `python3 secici_kredi_kalibre.py`. Model: `secici_kredi.py` (Google Sheet \"Secici_Kredi_Veri_DOLU\" formüllerinin birebir taşınması; "
         "tablonun Sim_S1-S4 ve ölçüm paneli sonuçlarıyla parite testi var). Kalibrasyon iki katmanlı ve her parametre etiketli.", "",
         "## 1. Çapalar: ölçülebilen başlangıç durumu (t0 = 2025)", "",
         "| Parametre | Tablodaki temsilî değer | Türkiye çapası | Sınıf | Kaynak |", "| --- | ---: | ---: | --- | --- |"]
    for k, v in rapor["capa"].items():
        L.append(f"| `{k}` | {f2(v['eski'])} | {f2(v['deger'])} | {v['sinif']} | {v['kaynak']} |")
    L += ["", f"Z0 (t0 talep tutarlılığı kalemi) yeniden hesaplandı: {f2(rapor['Z0'], 4)} (tablodaki 0,3468).", "",
          "Ölçülemeyenler tablodaki temsilî değerinde bırakıldı: `ph1` ve `th1` (alt gelir grubunun taban ve gelir payı: V37 boş), `inv0`, `b`, `spread`, `am`, `sig`, `rn`, eşikler (k1s...k6c). Bunlar kalibre DEĞİL. `mc`, `mi`, `mg` ayrı ayrı ölçülemedi; yalnızca ortak ölçekleri t0 ithalat kimliğinden geldi, oranları birbirine göre tablodaki gibi.", "",
          "## 2. Davranış parametreleri: anket yolu üzerinde ayar", "",
          "Hedef: PKA ve `bes_yil_senaryo.csv` yıl sonu beklentileri. t=1 → 2026. İçeri örnek: 2026-2027 TÜFE, politika faizi, kur (6 moment). "
          "Örnek dışı: 2028 TÜFE ve faiz, 2031 TÜFE. Serbest: alpha, pt, rho (davranış), S1 kolunun tay ve cred'i. "
          "5 serbest parametre, 6 moment: neredeyse tam belirlenmiş; bu ayardır, kestirim değil. Hedefin kendisi bir anket (tahmin), gerçekleşme değil.", "",
          "| Parametre | Tablodaki | Kalibre |", "| --- | ---: | ---: |"]
    for k, a0, a1 in zip(SERBEST, x0, x):
        L.append(f"| `{k}` | {f2(a0)} | {f2(a1)} |")
    L += ["", "| Gösterge | Yıl (t) | Hedef | Kalibresiz hata | Kalibre hata | Örnek |", "| --- | --- | ---: | ---: | ---: | --- |"]
    ic0, di0 = rapor["iceri_kalibresiz"], rapor["disari_kalibresiz"]
    for lab, ic, ic0_ in (("içi", rapor["iceri"], ic0), ("dışı", rapor["disari"], di0)):
        pass
    for lab, kal, kal0 in (("içi", rapor["iceri"], rapor["iceri_kalibresiz"]), ("dışı", rapor["disari"], rapor["disari_kalibresiz"])):
        for (k, t, e), (_, _, e0) in zip(kal, kal0):
            L.append(f"| {k} | {2025 + t} ({t}) | {f2(HEDEF[k][t])} | {f2(e0)} | {f2(e)} | {lab} |")
    L += ["", "Hata = model − hedef. İçeri hatalar sıfıra yakınsa bu uydurmanın doğal sonucudur. Örnek dışı satırlar asıl bilgidir.", "",
          "## 3. Tablonun kendi sınaması (Eleştiri #12): geçmişi üretebiliyor mu?", "",
          "Kalibre davranış parametreleriyle, t0 = y için tablodaki çapalar yıl y verisinden kurulur ve y+1 TÜFE'si tahmin edilir; naif tahmin TÜFE(y).", "",
          "| Yıl | Gerçek TÜFE | Model | Naif (önceki yıl) | Model hata | Naif hata |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    mm = nn = 0
    for g in rapor["geri_test"]:
        L.append(f"| {g['yil']} | {f2(g['gercek'])} | {f2(g['model'])} | {f2(g['naif'])} | {f2(g['model'] - g['gercek'])} | {f2(g['naif'] - g['gercek'])} |")
        mm += abs(g["model"] - g["gercek"])
        nn += abs(g["naif"] - g["gercek"])
    n = max(1, len(rapor["geri_test"]))
    L += ["", f"Ortalama mutlak hata: model {f2(mm / n)}, naif {f2(nn / n)}.", ""]
    L += ["## 4. Senaryolar: kalibresiz ve kalibre", "",
          "S1 kalibre kolla, S2-S4 tablonun politika kollarıyla (davranış parametreleri ortak). Dar Koridor skoru ve ana göstergeler:", "",
          "| Senaryo | Kal. | Enflasyon t=1 | t=5 | t=10 | t=20 | Cari açık t=5 | Koridor t=1 | t=10 | t=20 | Rejim t=20 |", "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |"]
    for s in (1, 2, 3, 4):
        for kal, S in (("önce", sc0), ("sonra", sc)):
            r = S[s]
            L.append(f"| S{s} | {kal} | {f2(r[0]['pi'])} | {f2(r[4]['pi'])} | {f2(r[9]['pi'])} | {f2(r[19]['pi'])} | {f2(r[4]['cad'])} | {f2(r[0]['kor'], 1)} | {f2(r[9]['kor'], 1)} | {f2(r[19]['kor'], 1)} | {r[19]['rej']} |")
    neg = [(s, r["t"]) for s in (1, 2, 3, 4) for r in sc[s] if r["pi"] < 0]
    if neg:
        L += ["", "**Uyarı.** Kalibre yolda negatif enflasyon çıkıyor: " + ", ".join(f"S{s} t={t}" for s, t in neg[:6]) + (" ..." if len(neg) > 6 else "") +
              ". Uzun vadede enflasyon hedefe değil hedefin altına gidiyor; bu modelin yapısal sınırıdır (TL değer kaybı −%10 tabanına bağlanıyor, beklenti hedefe çıpalı), kalibrasyon bunu düzeltmez."]
    o = K.olcum(V, 2025)
    L += ["", f"Karşılaştırma: ölçülmüş Dar Koridor Basınç Endeksi 2025 = {f2(o['DKBE'], 1)} ({o['rejim']}; 12 gösterge, kapsam %{o['kapsam'] * 5}). Simülasyonun `kor` skoru 6 bileşenlidir, ölçümün 22 göstergeli DKBE'si "
          "farklı bir bileşimdir; ikisi birebir kıyaslanmaz.", "",
          "## Ne denmez", "",
          "- Model Türkiye için tahmin üretir denmez. Davranış parametreleri bir anket yoluna ayarlandı, gerçekleşmeye değil.",
          "- 'Kalibre' sözü, parametrelerin tamamı için kullanılmaz: yalnızca yukarıda 'olcum' ve 'tahmin' işaretli çapalar ile 5 davranış parametresi için.",
          "- Seçici kredi, ücret ve yerlileşme kanalları (sp, leak, disc, socw, wr, rek, mu, lloc, tfpk, locmax) ölçülemedi; S2-S4 farkları büyük ölçüde bu temsilî değerlerin sonucudur.",
          "- Teşvik skorkartı, kurtarma sırası ve sektörel net döviz sayfaları kurgusal firma/sektör satırlarıyla geliyor; veri olmadan bu modüle taşınmadı.",
          "- S3 ile S4 farkı (kurumsal disiplin) bir varsayımdır; model bunu ölçmez."]
    (KOK / "SECICI_KREDI.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
