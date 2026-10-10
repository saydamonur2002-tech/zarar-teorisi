"""Dagitim stresi. Kurallar kosudan once.

Stoklar TCMB 2026-Q1. Kenar, yukumlulugun alacakli varlik payina bolunmesidir.
Girdi-cikti yoktur. Cekilmemis limit seride yoktur.

Firma haznesi 150 alt dugum. Toplam mevduat, kredi stoku ve aylik servis olculmus
toplamda kalir. Ust %10 mevduat payi: 0.10 esit, 0.40 orta, 0.70 yuksek.
Gurultu lognormal, sigma 0.15; kuvvet alpha hedef payi tutacak sekilde secilir.
Tohum TOHUM+9000+s.

Birincil stres: borc servisi ve alacak esit paylasilir, mevduat hedef payda toplanir.
Kontrol: servis ve alacak mevduat payini izler; firma basi karsilama orani agregatla aynidir.

Cizgi birincilde 0. Yan kol: bir aylik servis kadar cizgi yalnizca pozitif limitlilere.
Sifir kitle p0, mevduati en kucuk firmalardir. p0 0 ve 0.50. Bu cizgi olcum degildir.

FX cevirmeme: firma g = min(1, FX mevduat / FX kredi stoku). Doviz paylari olculmus
agregat paylardir, firma bazinda ayri pay yoktur. Valf pi, Ocak 2026 TUFE aylik
karsiligi. Esik 0.25 model kuralidir. Kilit ve alpha, agregat kosuyla aynidir.

Tekrar: esit pay, FX kapali kalicilik ortalamasi < 1 ve reel kayip < 0.01;
FX acik kalicilik < 1 ve reel kayip 0.454'ten en fazla 0.02 sapar.

Gizli tampon: yuksek konsantrasyon, esit servis, cizgi 0, FX kapali, esite gore
kalicilik pratik esikle uzar (medyan >= 2 veya ortalama >= 2 ve kosularin %25'i
en az 2, tek yanli p<0.05) VEYA reel kayip orani en az 0.05 artar (p<0.05)
VEYA kucuk firma yavaslik payi en az 0.10 artar (p<0.05).
Ayni esikler, cizgi 1 ay ve p0=0.50 eksi p0=0 icin de bakilir. Biri tutarsa
agregat tampon yerel tikanmayi gizliyor denir.

Valf: yuksek konsantrasyon, esit servis, cizgi 0, FX acik. Kaliciligi pratik
esikle kisaltmiyor ve reel kaybi 0.05'ten az dusuruyorsa olculmus enflasyon
reel FX kaybini kapatmiyor.

Zayif halka: ayni hucrede kucuk firmalarin reel kayip payi eksi defter payi
medyani < 0.05. Kucuk, mevduati alt yari firmadir.

Esik sonuca gore kaydirilmaz.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import odeme_zinciri as oz
from akis_model import IDX, INSTR, Lm, load, panel
from odeme_gercek import (
    DIGER_AY,
    DONEM,
    ESIK_VALF,
    F_KREDI,
    F_MEV,
    ISARET,
    KISA_AY,
    UZUN_AY,
    kisa_pay,
    tufe_yoy,
)
from odeme_tur2 import anlamli_uzama

KOK = Path(__file__).resolve().parent
N_FIRMA = 150
N_MC = 8 if os.environ.get("ODEME_SMOKE") else 50
KONS = (0.10, 0.40, 0.70)
HEDEF_REEL = 0.45408167359827306
H_NODE, B_NODE, K_NODE, D_NODE = 0, 1, 2, 3
F0 = 4


def _alpha(gurultu: np.ndarray, hedef: float) -> float:
    n = gurultu.size
    k = max(1, int(round(0.10 * n)))
    sira = np.arange(1, n + 1, dtype=float)
    lo, hi = 0.0, 40.0
    for _ in range(48):
        a = 0.5 * (lo + hi)
        raw = gurultu * sira ** (-a)
        raw = raw / raw.sum()
        pay = float(np.sort(raw)[-k:].sum())
        if pay < hedef:
            lo = a
        else:
            hi = a
    return 0.5 * (lo + hi)


def agirlik(n: int, hedef: float, tohum: int) -> np.ndarray:
    rng = np.random.default_rng(tohum)
    gurultu = np.exp(0.15 * rng.normal(size=n))
    if hedef <= 0.101:
        w = np.ones(n)
    else:
        a = _alpha(gurultu, hedef)
        w = gurultu * np.arange(1, n + 1, dtype=float) ** (-a)
    w = w[rng.permutation(n)]
    return w / w.sum()


def ust10(w: np.ndarray) -> float:
    k = max(1, int(round(0.10 * w.size)))
    return float(np.sort(w)[-k:].sum())


def stok_yukle() -> dict:
    stab, _, tcs, _ = load()
    A, Y = panel(stab, tcs, DONEM)
    ad = list(INSTR)
    ik, im, idg = ad.index("kredi"), ad.index("para_mevduat"), ad.index("diger")
    mat = Lm(A, Y)
    pay = kisa_pay(stab, tcs)
    kredi_ay = Y[ik] * (pay / KISA_AY + (1.0 - pay) / UZUN_AY) / 1e9
    diger_ay = Y[idg] / DIGER_AY / 1e9
    return {
        "lik": A[im] / 1e9,
        "kredi_stok": Y[ik] / 1e9,
        "kredi_ay": kredi_ay,
        "diger_ay": diger_ay,
        "mk": mat["kredi"],
        "md": mat["diger"],
    }


def ag_kur(stok: dict, mev_w: np.ndarray, srv_w: np.ndarray, line_ay: float, p0: float) -> dict:
    n = mev_w.size
    nd = F0 + n
    mk, md = stok["mk"], stok["md"]
    ih, ib, ik, id_ = IDX["H"], IDX["B"], IDX["K"], IDX["D"]
    iF = IDX["F"]
    dugum = {ih: H_NODE, ib: B_NODE, ik: K_NODE, id_: D_NODE}
    kenar: dict[tuple[int, int], float] = {}

    def ekle(j, i, w):
        if w > 1e-12 and j != i:
            kenar[(j, i)] = kenar.get((j, i), 0.0) + w

    for s, sn in dugum.items():
        for c in range(5):
            if c == s:
                continue
            w = float(stok["kredi_ay"][s] * mk[s, c] + stok["diger_ay"][s] * md[s, c])
            if c == iF:
                for f in range(n):
                    ekle(sn, F0 + f, w * srv_w[f])
            else:
                ekle(sn, dugum[c], w)
    kredi_f = float(stok["kredi_ay"][iF])
    diger_f = float(stok["diger_ay"][iF])
    for f in range(n):
        for c, cn in dugum.items():
            w = srv_w[f] * (kredi_f * mk[iF, c] + diger_f * md[iF, c])
            ekle(F0 + f, cn, w)

    borclu = np.array([a for a, _ in kenar], dtype=np.int32)
    alacakli = np.array([b for _, b in kenar], dtype=np.int32)
    w0 = np.array(list(kenar.values()), dtype=np.float64)
    borc = np.bincount(borclu, weights=w0, minlength=nd).astype(np.float64)
    alacak = np.bincount(alacakli, weights=w0, minlength=nd).astype(np.float64)
    mev = np.zeros(nd)
    mev[H_NODE] = stok["lik"][ih]
    mev[B_NODE] = stok["lik"][ib]
    mev[K_NODE] = stok["lik"][ik]
    mev[D_NODE] = stok["lik"][id_]
    mev[F0:] = float(stok["lik"][iF]) * mev_w
    servis = np.zeros(nd)
    servis[F0:] = (kredi_f + diger_f) * srv_w
    line = np.zeros(nd)
    if line_ay > 0.0 and p0 < 1.0:
        kucukten = np.argsort(mev_w, kind="mergesort")
        n0 = int(round(p0 * n))
        serbest = np.ones(n, dtype=bool)
        serbest[kucukten[:n0]] = False
        line[F0:] = np.where(serbest, line_ay * servis[F0:], 0.0)
    kredi = np.zeros(nd)
    kredi[F0:] = float(stok["kredi_stok"][iF]) * srv_w
    fx = np.ones(nd)
    var = kredi[F0:] > 1e-12
    fx[F0:][var] = (F_MEV * mev[F0:][var]) / (F_KREDI * kredi[F0:][var])
    sira = np.argsort(mev_w, kind="mergesort")
    kucuk = np.zeros(nd, dtype=bool)
    buyuk = np.zeros(nd, dtype=bool)
    kucuk[F0 + sira[: n // 2]] = True
    buyuk[F0 + sira[3 * n // 4 :]] = True
    ithal = np.zeros(nd)
    ithal[F0:] = F_KREDI
    return {
        "net": {
            "borclu": borclu,
            "alacakli": alacakli,
            "w0": w0,
            "borc": borc,
            "alacak": alacak,
            "boyut": np.maximum(mev, 1e-8),
            "buyuk": buyuk,
            "kucuk": kucuk,
            "banka_taban": np.zeros(nd),
            "idx_ku_al": np.flatnonzero(kucuk[alacakli]),
            "idx_bu_al": np.flatnonzero(buyuk[alacakli]),
            "idx_bu_borc": np.flatnonzero(buyuk[borclu]),
            "idx_b2k": np.flatnonzero(buyuk[borclu] & kucuk[alacakli]),
            "dis_akis": borc - alacak,
        },
        "lik": mev,
        "line": line,
        "fx": fx,
        "ithal": ithal,
        "kucuk_firma": kucuk[F0:],
    }


def kos(pak, pi: float, fx: bool):
    nd = pak["lik"].size
    dis = np.ones(nd, dtype=bool)
    if fx:
        dis[F0:] = False
    return oz.tek_kosu_temiz(
        pak["net"], pak["lik"], pak["line"],
        oz.KILIT[oz.ORTA][0], oz.KILIT[oz.ORTA][1], oz.GECIKME[4], dis,
        enflasyon_esik=ESIK_VALF, enflasyon_pi=pi, reel=True, ithal=pak["ithal"],
        fx_ay=1.0, fx_sok=fx, fx_carpan=pak["fx"] if fx else None, fx_hizmet=0.0,
    )


def topla(ciktilar, v0: float) -> dict:
    kal, reel, er, pi, yk, yb, pay, defter = [], [], [], [], [], [], [], []
    for h, yavas, pak in ciktilar:
        kal.append(h[oz.F_KAL])
        reel.append(h[oz.F_REEL] / (v0 * oz.T))
        er.append(h[oz.F_ER_TOP] / (v0 * oz.T))
        pi.append(h[oz.F_PI_N])
        k = pak["net"]["kucuk"]
        b = pak["net"]["buyuk"]
        yk.append(float(yavas[k].mean()) / oz.T if np.any(k) else 0.0)
        yb.append(float(yavas[b].mean()) / oz.T if np.any(b) else 0.0)
        top = h[oz.F_REEL]
        pay.append(h[oz.F_REEL_KU] / top if top > 1e-8 else np.nan)
        defter.append(pak["net"]["w0"][pak["net"]["idx_ku_al"]].sum() / pak["net"]["w0"].sum())
    fazla = np.array(pay) - np.array(defter)
    return {
        "kal": np.array(kal),
        "reel": np.array(reel),
        "erime": np.array(er),
        "pi": np.array(pi),
        "yk": np.array(yk),
        "yb": np.array(yb),
        "fazla": fazla,
        "pay": np.array(pay),
        "defter": np.array(defter),
    }


def arti(a: np.ndarray, b: np.ndarray, esik: float) -> dict:
    fark = a - b
    p = oz.wilcoxon_p(fark, "greater")
    return {
        "fark": float(np.mean(fark)),
        "p": p,
        "tuttu": bool(float(np.mean(fark)) >= esik and p < 0.05),
    }


def kal_uzadi(yeni: np.ndarray, eski: np.ndarray) -> dict:
    fark = yeni - eski
    p = oz.wilcoxon_p(fark, "greater")
    return {
        "fark": float(np.mean(fark)),
        "p": p,
        "tuttu": bool(anlamli_uzama(fark) and p < 0.05),
    }


def grafik(tablo: pd.DataFrame, dosya: Path) -> None:
    alt = tablo[(tablo.line_ay == 0) & (~tablo.eslesme) & (~tablo.valf)]
    fig, ax = plt.subplots(1, 2, figsize=(10.2, 4.3))
    x = np.arange(3)
    gen = 0.35
    kap = [float(alt[(alt.kons == k) & (~alt.fx)].kalicilik.iloc[0]) for k in KONS]
    ac = [float(alt[(alt.kons == k) & alt.fx].kalicilik.iloc[0]) for k in KONS]
    ax[0].bar(x - gen / 2, kap, width=gen, label="FX çevrilebilir", color="#4C78A8")
    ax[0].bar(x + gen / 2, ac, width=gen, label="FX çevrilemez", color="#E45756")
    ax[0].set_xticks(x, ["Üst %10 = %10", "Üst %10 = %40", "Üst %10 = %70"])
    ax[0].set_ylabel("Ortalama bloke periyot")
    ax[0].set_title("Eşit servis, çizgi yok")
    ax[0].legend(frameon=False, fontsize=8)
    reel_kap = [float(alt[(alt.kons == k) & alt.fx].reel.iloc[0]) for k in KONS]
    valf = tablo[(tablo.line_ay == 0) & (~tablo.eslesme) & tablo.valf & tablo.fx]
    reel_ac = [float(valf[valf.kons == k].reel.iloc[0]) for k in KONS]
    ax[1].bar(x - gen / 2, reel_kap, width=gen, label="Valf kapalı", color="#E45756")
    ax[1].bar(x + gen / 2, reel_ac, width=gen, label="Valf açık", color="#F58518")
    ax[1].set_xticks(x, ["Üst %10 = %10", "Üst %10 = %40", "Üst %10 = %70"])
    ax[1].set_ylabel("Reel fatura kaybı / (V0 × T)")
    ax[1].set_title("FX çevrilemez, eşit servis")
    ax[1].legend(frameon=False, fontsize=8)
    fig.suptitle("Ölçülmüş toplam stok. Mevduat dağılımı varsayım.", fontsize=11)
    fig.tight_layout()
    fig.savefig(dosya, dpi=120)
    plt.close(fig)


def hukum(k: dict) -> str:
    parca = []
    if k["tekrar"]:
        parca.append(
            "Eşit paylaşım agregatı tekrarlıyor: kalıcılık 0, döviz çevrilemezken reel kayıp önceki bantta."
        )
    else:
        parca.append("Eşit paylaşım ölçülmüş agregatı tekrarlamadı. Dağılım karşılaştırması bu yüzden zayıf.")
    if k["gizli"]:
        parca.append(
            "Yüksek konsantrasyon veya sıfır çizgi, toplam stok aynıyken bloke, yerel yavaşlık veya reel kaybı eşiğin üstünde artırıyor. "
            "Agregat tampon yerel tıkanmayı gizliyor."
        )
    else:
        parca.append(
            "Konsantrasyon ve sıfır çizgi, toplam stok aynıyken sistemik blokeyi, yerel yavaşlığı ve reel kaybı eşiğin üstünde artırmıyor. "
            "Bu vade varsayımlarıyla ölçülmüş stoklar sistemik bloke üretmiyor."
        )
    if k["valf_korur"]:
        parca.append("Ölçülmüş aylık enflasyon, yüksek konsantrasyonda reel FX kaybını ve kalıcılığı eşiğin üstünde kapatmıyor.")
    else:
        parca.append("Valf, test hücresinde kalıcılığı veya reel kaybı eşiğin üstünde indiriyor.")
    if k["zayif"]:
        parca.append("Küçük firmaların reel kayıp payı defter payını 5 puan aşmıyor. Zayıf halka bu kanalda da zayıf.")
    else:
        parca.append("Küçük firmaların reel kayıp payı defter payının en az 5 puan üstünde.")
    return " ".join(parca)


def rapor_metni(sonuc: dict, tablo: pd.DataFrame) -> str:
    k = sonuc["karar"]
    s = [
        "# Ödeme zinciri, dağılım stresi",
        "",
        sonuc["uyari"],
        "",
        "## Hüküm",
        "",
        sonuc["ozet"],
        "",
        "## Ne ölçülmüş, ne varsayım",
        "",
        "Stoklar TCMB 2026-Q1. Firma haznesi 150 alt düğüme bölündü. Toplam mevduat, kredi stoku ve aylık servis korunuyor. "
        "Kenar, yükümlülüğün alacaklı varlık payına bölünmesidir. Girdi-çıktı tablosu yok. Çekilmemiş limit seride yok.",
        "",
        "Üst yüzde 10 mevduat payı 0,10, 0,40 ve 0,70. Birincil streste borç servisi ve alacak eşit. "
        "Kontrolde ikisi de mevduat payını izliyor. Yan kolda bir aylık servis kadar çizgi, en küçük p0 firmaya kapalı. Bu çizgi ölçülmedi.",
        "",
        f"TÜFE {sonuc['tufe']['baz']}–{sonuc['tufe']['son']}: yıllık {sonuc['tufe']['yoy']:.3f}, aylık π = {sonuc['pi']:.4f}. "
        f"Monte Carlo {N_MC}. Tohum {oz.TOHUM}+9000.",
        "",
        f"Eşit paylaşım, FX çevrilemez, valf kapalı: kalıcılık {k['esit_fx_kal']:.2f}, reel kayıp {k['esit_fx_reel']:.3f}. "
        f"Agregat hedef 0,454. Sapma {k['esit_sapma']:.3f}.",
        "",
        f"Yüksek konsantrasyon, eşit servis, çizgi yok, FX yok: kalıcılık farkı {k['yuksek_kal_fark']:.2f} (p = {k['yuksek_kal_p']:.4g}), "
        f"reel fark {k['yuksek_reel_fark']:.3f} (p = {k['yuksek_reel_p']:.4g}), "
        f"küçük firma yavaşlık farkı {k['yuksek_yk_fark']:.3f} (p = {k['yuksek_yk_p']:.4g}).",
        "",
        f"Aynı hücre, FX çevrilemez: kalıcılık {k['yuksek_fx_kal']:.2f}, reel kayıp {k['yuksek_fx_reel']:.3f}. "
        f"Valf açık: kalıcılık {k['yuksek_valf_kal']:.2f}, reel {k['yuksek_valf_reel']:.3f}, "
        f"kısalma {k['valf_kisalma']:.2f} (p = {k['valf_p']:.4g}), reel düşüş {k['valf_reel']:.3f}.",
        "",
        f"Küçük firma reel payı {k['kucuk_pay']:.3f}, defter payı {k['defter']:.3f}, fazla medyan {k['fazla']:.3f}.",
        "",
        f"Eşleşen kontrol, yüksek konsantrasyon, FX çevrilemez: kalıcılık {k['eslesen_kal']:.2f}, reel kayıp {k['eslesen_reel']:.3f}, "
        f"fazla medyan {k['eslesen_fazla']:.3f}.",
        "",
        f"Varsayılmış bir aylık çizgi, yüksek konsantrasyon, p0 = 0,50 eksi p0 = 0: "
        f"kalıcılık farkı {k['p0_kal_fark']:.2f} (p = {k['p0_kal_p']:.4g}), "
        f"yavaşlık farkı {k['p0_yk_fark']:.3f} (p = {k['p0_yk_p']:.4g}).",
        "",
        "## Hücreler, valf kapalı",
        "",
        "| Üst %10 | Servis | Çizgi | p0 | FX | Kalıcılık | Reel | Küçük yavaşlık | Fazla |",
        "| ---: | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    kap = tablo[~tablo.valf]
    for _, r in kap.iterrows():
        s.append(
            f"| {r.kons:.2f} | {'eşleşen' if r.eslesme else 'eşit'} | {r.line_ay:.0f} | {r.p0:.2f} | "
            f"{'çevrilemez' if r.fx else 'çevrilebilir'} | {r.kalicilik:.2f} | {r.reel:.3f} | "
            f"{r.yavas_kucuk:.3f} | {r.fazla:.3f} |"
        )
    s.extend([
        "",
        "Tekrar: `python3 odeme_zinciri.py`.",
        "",
        "Dosyalar: `odeme_dagilim_hucre.csv`, `odeme_dagilim.png`, `odeme_dagilim_sonuc.json`.",
        "",
    ])
    return "\n".join(s)


def main_dagilim() -> None:
    tufe = tufe_yoy()
    pi_ay = (1.0 + tufe["yoy"]) ** (1.0 / 12.0) - 1.0
    stok = stok_yukle()
    print("yukleniyor", N_MC, "pi", round(pi_ay, 4))
    # Hucre anahtari: (kons, eslesme, line_ay, p0, fx, valf)
    plan = []
    for kons in KONS:
        for eslesme in (False, True):
            for fx in (False, True):
                for valf in (False, True):
                    plan.append((kons, eslesme, 0.0, 0.0, fx, valf))
    for p0 in (0.0, 0.50):
        for fx in (False, True):
            for valf in (False, True):
                plan.append((0.70, False, 1.0, p0, fx, valf))

    # Agirliklar hucreler arasinda esli: ayni tohum, ayni konsantrasyon.
    onbellek = {}
    ham = {}
    for kons, eslesme, line_ay, p0, fx, valf in plan:
        anahtar_w = (kons, eslesme, line_ay, p0)
        if anahtar_w not in onbellek:
            paketler = []
            paylar = []
            for s in range(N_MC):
                mev = agirlik(N_FIRMA, kons, oz.TOHUM + 9000 + s)
                srv = mev.copy() if eslesme else np.full(N_FIRMA, 1.0 / N_FIRMA)
                paketler.append(ag_kur(stok, mev, srv, line_ay, p0))
                paylar.append(ust10(mev))
            onbellek[anahtar_w] = (paketler, float(np.mean(paylar)))
        paketler, ust = onbellek[anahtar_w]
        pi = pi_ay if valf else 0.0
        cikti = []
        for pak in paketler:
            h, _, yavas = kos(pak, pi, fx)
            cikti.append((h, yavas, pak))
        v0 = float(paketler[0]["net"]["w0"].sum())
        ozet = topla(cikti, v0)
        ham[(kons, eslesme, line_ay, p0, fx, valf)] = ozet
        print(
            f"k={kons:.2f} es={int(eslesme)} L={line_ay:.0f} p0={p0:.2f} fx={int(fx)} v={int(valf)} "
            f"kal={ozet['kal'].mean():.2f} reel={ozet['reel'].mean():.3f} yk={ozet['yk'].mean():.3f} ust={ust:.3f}",
            flush=True,
        )

    def al(kons, eslesme, line_ay, p0, fx, valf):
        return ham[(kons, eslesme, line_ay, p0, fx, valf)]

    esit_fx = al(0.10, False, 0.0, 0.0, True, False)
    esit_yok = al(0.10, False, 0.0, 0.0, False, False)
    yuk_yok = al(0.70, False, 0.0, 0.0, False, False)
    yuk_fx = al(0.70, False, 0.0, 0.0, True, False)
    yuk_valf = al(0.70, False, 0.0, 0.0, True, True)
    esl_fx = al(0.70, True, 0.0, 0.0, True, False)
    p0_yok = al(0.70, False, 1.0, 0.0, False, False)
    p0_var = al(0.70, False, 1.0, 0.50, False, False)

    tekrar = bool(
        esit_yok["kal"].mean() < 1.0
        and esit_yok["reel"].mean() < 0.01
        and esit_fx["kal"].mean() < 1.0
        and abs(float(esit_fx["reel"].mean()) - HEDEF_REEL) <= 0.02
    )
    k_kal = kal_uzadi(yuk_yok["kal"], esit_yok["kal"])
    k_reel = arti(yuk_yok["reel"], esit_yok["reel"], 0.05)
    k_yk = arti(yuk_yok["yk"], esit_yok["yk"], 0.10)
    p_kal = kal_uzadi(p0_var["kal"], p0_yok["kal"])
    p_reel = arti(p0_var["reel"], p0_yok["reel"], 0.05)
    p_yk = arti(p0_var["yk"], p0_yok["yk"], 0.10)
    gizli = bool(k_kal["tuttu"] or k_reel["tuttu"] or k_yk["tuttu"] or p_kal["tuttu"] or p_reel["tuttu"] or p_yk["tuttu"])
    valf_kal = kal_uzadi(yuk_fx["kal"], yuk_valf["kal"])
    valf_reel = float((yuk_fx["reel"] - yuk_valf["reel"]).mean())
    valf_korur = bool((not valf_kal["tuttu"]) and valf_reel < 0.05)
    fazla = yuk_fx["fazla"]
    fazla_med = float(np.nanmedian(fazla)) if np.isfinite(fazla).any() else float("nan")
    zayif = bool((not np.isfinite(fazla).any()) or (np.isfinite(fazla_med) and fazla_med < 0.05))
    # Fazla 5 puani asiyorsa ve test anlamliysa zayif degil. Medyan esigi tek basina yeter, kural boyle yazildi.
    karar = {
        "tekrar": tekrar,
        "gizli": gizli,
        "valf_korur": valf_korur,
        "zayif": zayif,
        "esit_fx_kal": float(esit_fx["kal"].mean()),
        "esit_fx_reel": float(esit_fx["reel"].mean()),
        "esit_sapma": float(esit_fx["reel"].mean() - HEDEF_REEL),
        "yuksek_kal_fark": k_kal["fark"],
        "yuksek_kal_p": k_kal["p"],
        "yuksek_reel_fark": k_reel["fark"],
        "yuksek_reel_p": k_reel["p"],
        "yuksek_yk_fark": k_yk["fark"],
        "yuksek_yk_p": k_yk["p"],
        "yuksek_fx_kal": float(yuk_fx["kal"].mean()),
        "yuksek_fx_reel": float(yuk_fx["reel"].mean()),
        "yuksek_valf_kal": float(yuk_valf["kal"].mean()),
        "yuksek_valf_reel": float(yuk_valf["reel"].mean()),
        "valf_kisalma": valf_kal["fark"],
        "valf_p": valf_kal["p"],
        "valf_reel": valf_reel,
        "kucuk_pay": float(np.nanmean(yuk_fx["pay"])),
        "defter": float(np.nanmean(yuk_fx["defter"])),
        "fazla": fazla_med,
        "eslesen_kal": float(esl_fx["kal"].mean()),
        "eslesen_reel": float(esl_fx["reel"].mean()),
        "eslesen_fazla": float(np.nanmedian(esl_fx["fazla"])),
        "p0_kal_fark": p_kal["fark"],
        "p0_kal_p": p_kal["p"],
        "p0_yk_fark": p_yk["fark"],
        "p0_yk_p": p_yk["p"],
    }
    satir = []
    for (kons, eslesme, line_ay, p0, fx, valf), ozet in ham.items():
        satir.append({
            "kons": kons,
            "eslesme": eslesme,
            "line_ay": line_ay,
            "p0": p0,
            "fx": fx,
            "valf": valf,
            "n": N_MC,
            "ust10": onbellek[(kons, eslesme, line_ay, p0)][1],
            "kalicilik": float(ozet["kal"].mean()),
            "reel": float(ozet["reel"].mean()),
            "erime": float(ozet["erime"].mean()),
            "pi_periyot": float(ozet["pi"].mean()),
            "yavas_kucuk": float(ozet["yk"].mean()),
            "yavas_buyuk": float(ozet["yb"].mean()),
            "kucuk_reel_pay": float(np.nanmean(ozet["pay"])) if np.isfinite(ozet["pay"]).any() else float("nan"),
            "defter": float(np.nanmean(ozet["defter"])) if np.isfinite(ozet["defter"]).any() else float("nan"),
            "fazla": float(np.nanmedian(ozet["fazla"])) if np.isfinite(ozet["fazla"]).any() else float("nan"),
        })
    tablo = pd.DataFrame(satir).sort_values(["line_ay", "eslesme", "kons", "p0", "fx", "valf"])
    tablo.to_csv(KOK / "odeme_dagilim_hucre.csv", index=False)
    grafik(tablo, KOK / "odeme_dagilim.png")
    ozet_metin = hukum(karar)
    v0 = float(onbellek[(0.10, False, 0.0, 0.0)][0][0]["net"]["w0"].sum())
    sonuc = {
        "uyari": (
            "Stoklar TCMB finansal hesapları, 2026-Q1. Kenar ve firma içi dağılım varsayımdır. "
            "Çekilmemiş limit ve girdi-çıktı tablosu yoktur. Sayılar firma faturası ölçümü değildir."
        ),
        "ozet": ozet_metin,
        "karar": karar,
        "tufe": tufe,
        "pi": pi_ay,
        "n_firma": N_FIRMA,
        "n_mc": N_MC,
        "v0": v0,
        "tohum": oz.TOHUM,
    }
    (KOK / "odeme_dagilim_sonuc.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    eski = (KOK / "ODEME_ZINCIRI.md").read_text(encoding="utf-8")
    if eski.startswith("# Ödeme zinciri, dağılım") and ISARET in eski:
        eski = eski.split(ISARET, 1)[1]
    (KOK / "ODEME_ZINCIRI.md").write_text(rapor_metni(sonuc, tablo) + ISARET + eski, encoding="utf-8")
    print(ozet_metin)


if __name__ == "__main__":
    main_dagilim()
