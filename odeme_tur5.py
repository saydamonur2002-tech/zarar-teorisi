"""Tur 5: reel kisit (FX / ithal girdi). Kurallar modul belgesinde.

Enflasyon valfi yalniz TL alacagini eritir. FX hatti ve ithal gereksinim ayri durur.
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
from odeme_tur2 import C_SOK, SERT, YUMUSAK, anlamli_uzama
from odeme_tur4 import kisa_mi

KOK = Path(__file__).resolve().parent
N_MC = 8 if os.environ.get("ODEME_SMOKE") else 50
ESIK = 0.25
PI = 0.30
ISARET = "\n\n<!-- ONCEKI -->\n\n"
SOK = (("yumusak", YUMUSAK), ("c", C_SOK), ("sert", SERT))


def ithal_vektor(net) -> np.ndarray:
    return oz.ITHAL_PAY[net["sektor"]]


def hucre(net, aday, carpan, ia, ib, ic, taban, pi, reel, fx_sok, fx_ay=1.0, ithal=None, gecis=0.0, kapasite=None):
    return oz.kosu_hucre(
        net, aday, carpan, ia, ib, ic, range(N_MC),
        tabanlar=taban, enflasyon_esik=ESIK, enflasyon_pi=pi,
        reel=reel, ithal=ithal, fx_ay=fx_ay, fx_sok=fx_sok, fx_kur_gecis=gecis,
        kapasite=kapasite,
    )[0]


def soksuz(net, ithal, pi, reel, fx_ay=1.0) -> np.ndarray:
    lik, dis = oz.hazirla(net, C_SOK, None)
    return oz.tek_kosu_temiz(
        net, lik, oz.BANKA[oz.ORTA] * net["banka_taban"],
        oz.KILIT[oz.ORTA][0], oz.KILIT[oz.ORTA][1], oz.GECIKME[oz.ORTA], dis,
        enflasyon_esik=ESIK, enflasyon_pi=pi, reel=reel, ithal=ithal, fx_ay=fx_ay,
    )[0]


def v0(net) -> float:
    return float(net["w0"].sum())


def reel_oran(h, hacim) -> np.ndarray:
    return h[:, oz.F_REEL] / (hacim * oz.T)


def defter(net) -> float:
    return float(net["w0"][net["idx_ku_al"]].sum() / net["w0"].sum())


def grafik(ozet, dosya: Path) -> None:
    fig, ax = plt.subplots(1, 2, figsize=(10.6, 4.4))
    ad = ["Yumuşak", "C", "Sert"]
    x = np.arange(3)
    gen = 0.18
    seriler = (
        ("tl_kapali", "TL, valf kapalı", "#4C78A8"),
        ("fx_kapali", "TL+FX, valf kapalı", "#E45756"),
        ("fx_acik", "TL+FX, valf açık", "#F58518"),
        ("fx_iade", "FX hattı iade", "#54A24B"),
    )
    for i, (anahtar, etiket, renk) in enumerate(seriler):
        deger = [ozet[s][anahtar]["kalicilik"] for s in ("yumusak", "c", "sert")]
        ax[0].bar(x + (i - 1.5) * gen, deger, width=gen, label=etiket, color=renk)
    ax[0].set_xticks(x, ad)
    ax[0].set_ylabel("Ortalama bloke periyot")
    ax[0].set_title("Kötü köşe, kalıcılık")
    ax[0].legend(frameon=False, fontsize=7)
    for i, (anahtar, etiket, renk) in enumerate(seriler):
        deger = [ozet[s][anahtar]["reel"] for s in ("yumusak", "c", "sert")]
        ax[1].bar(x + (i - 1.5) * gen, deger, width=gen, label=etiket, color=renk)
    ax[1].set_xticks(x, ad)
    ax[1].set_ylabel("Reel fatura kaybı / (V0 × T)")
    ax[1].set_title("Kötü köşe, reel kayıp")
    ax[1].legend(frameon=False, fontsize=7)
    fig.suptitle("Reel kısıt ve enflasyon valfi. Sentetik, TCMB/KAP yok.", fontsize=11)
    fig.tight_layout()
    fig.savefig(dosya, dpi=120)
    plt.close(fig)


def hukum(k) -> tuple[str, str]:
    parca = []
    if k["soksuz_uyumsuz"]:
        parca.append("Şoksuz kontrol, FX hattı bir aylıkken kalıcılık veya reel kayıp üretti. Pay sonuca göre ayarlanmadı.")
    if k["tekrar"]:
        parca.append("Reel kısıt yokken kötü köşede kalıcılık uzun ve valf onu pratik eşiğin üstünde kısaltmıyor.")
    else:
        parca.append("Reel kısıt yokken önceki kalıp tekrarlanmadı: ya kalıcılık kısa ya da valf onu kısaltıyor.")
    if k["silim_gerekli_degil"]:
        parca.append(
            "TL+FX şokunda valf ne kalıcılığı ne reel kaybı pratik eşiğin üstünde kısaltıyor. "
            "Enflasyon siliminin reel tıkanma için gerekli olduğu desteklenmiyor."
        )
    elif k["valf_kalicilik"] and not k["valf_reel"]:
        parca.append("Valf TL kalıcılığını kısaltıyor, reel fatura kaybını pratik eşiğin üstünde düşürmüyor.")
    elif k["valf_reel"] and not k["valf_kalicilik"]:
        parca.append("Valf reel kaybı düşürüyor, kalıcılığı pratik eşiğin üstünde kısaltmıyor.")
    else:
        parca.append("Valf hem kalıcılığı hem reel kaybı pratik eşiğin üstünde indiriyor.")
    if k["kaynak_reel"]:
        parca.append("Kısıt eklenince kalıcılık uzuyor ve valf bu uzamayı kapatmıyor. Ek tıkanmanın kaynağı reel katman.")
    else:
        parca.append("Reel katmanın kalıcılığı uzattığı iddia bu eşikte kapanmadı.")
    cozen = []
    if k["fx_cozer"]:
        cozen.append("FX hattını iade etmek")
    if k["ikame_cozer"]:
        cozen.append("ithal payını sıfırlamak")
    if k["valf_kalicilik"]:
        cozen.append("enflasyon valfi")
    if cozen:
        parca.append("Kalıcılığı düşüren kanal: " + ", ".join(cozen) + ".")
    else:
        parca.append("Ne valf ne FX iadesi ne ithal ikamesi kalıcılığı pratik eşiğin üstünde düşürüyor.")
    if k["zayif"]:
        parca.append("Küçük alacaklının reel kayıp payı defter payını 5 puan aşmıyor. Zayıf halka bu kanalda da zayıf.")
    else:
        parca.append("Küçük alacaklının reel kayıp payı defter payının en az 5 puan üstünde.")
    if k.get("fx_reel"):
        parca.append("FX hattını iade etmek reel fatura kaybını en az 5 puan düşürür.")
    if k.get("ikame_reel"):
        parca.append("İthal payını sıfırlamak reel fatura kaybını en az 5 puan düşürür.")
    hipotez = " ".join(parca)
    if k["silim_gerekli_degil"] and k["kaynak_reel"] and k["zayif"] and not k["soksuz_uyumsuz"]:
        ozet = (
            "TL+FX şokunda enflasyon valfi kalıcılığı ve reel fatura kaybını pratik eşiğin üstünde kısaltmıyor. "
            "Silim yükü yazabilir; reel tıkanmayı çözdüğü desteklenmiyor. "
            "Kısıt eklenince kalıcılık uzuyor. Çözen kanal rapordaki iade ve ikame karşılaştırmasında."
        )
    else:
        ozet = hipotez
    return ozet, hipotez


def rapor_metni(sonuc, tablo) -> str:
    k = sonuc["karar"]
    s = [
        "# Ödeme zinciri, tur 5: reel kısıt",
        "",
        sonuc["uyari"],
        "",
        "## Hüküm",
        "",
        sonuc["ozet"],
        "",
        "## Kural",
        "",
        "İthal payları sentetiktir. Normal FX hattı firmanın kendi bir aylık ithal gereksinimidir. "
        "FX şokunda şoklanan firmaların hattı × 0,30. TL tahsilatı FX’e dönmez. "
        "Valf yalnız TL alacağını eritir; FX hizmetini ve ithal gereksinimini eritmez. Kur geçişkenliği birincilde 0. "
        "Üretim, FX kapsamı ile gelen yerli teslimatın minimumudur. Tahsil gerçekleşen faturaya göredir. "
        "Reel kayıp bloke sayacına yazılmaz.",
        "",
        f"Şoksuz, kısıt yok: kalıcılık {sonuc['soksuz_tl']:.2f}. "
        f"Şoksuz, kısıt var: kalıcılık {sonuc['soksuz_reel']:.2f}, reel kayıp oranı {sonuc['soksuz_reel_kayip']:.4f}.",
        "",
        "## C şoku, kötü köşe",
        "",
        f"TL yalnız, valf kapalı / açık: {k['tl_kapali']:.2f} / {k['tl_acik']:.2f}. "
        f"Kısalma {k['tl_kisalma']:.2f}, p = {k['tl_p']:.4g}.",
        "",
        f"TL+FX, valf kapalı / açık: {k['fx_kapali']:.2f} / {k['fx_acik']:.2f}. "
        f"Kısalma {k['fx_kisalma']:.2f}, p = {k['fx_p']:.4g}.",
        "",
        f"Reel kayıp oranı, TL yalnız {k['reel_tl']:.4f}, TL+FX kapalı {k['reel_fx']:.4f}, "
        f"valf açık {k['reel_fx_acik']:.4f}. Fark (kapalı − açık) {k['reel_dusme']:.4f}.",
        "",
        f"FX açığı, TL+FX kapalı {k['fx_acigi']:.3f}. Nominal erime oranı, valf açık {k['erime_fx']:.4f}.",
        "",
        f"FX hattı iade: kalıcılık {k['iade']:.2f}, reel kayıp {k['iade_reel']:.4f}, "
        f"kapalı FX’e göre kısalma {k['iade_kisalma']:.2f}, p = {k['iade_p']:.4g}.",
        "",
        f"İthal ikamesi (pay 0): kalıcılık {k['ikame']:.2f}, reel kayıp {k['ikame_reel']:.4f}, "
        f"kısalma {k['ikame_kisalma']:.2f}, p = {k['ikame_p']:.4g}.",
        "",
        f"Kur geçişkenliği 1, valf açık: kalıcılık {k['gecis']:.2f}, reel kayıp {k['gecis_reel']:.4f}. Birincil hükme girmez.",
        "",
        f"Kapasite × 0,70, FX şoku yok, valf kapalı: kalıcılık {k['kapasite']:.2f}, reel kayıp {k['kapasite_reel']:.4f}. Birincil hükme girmez.",
        "",
        f"Küçük alacaklının reel kayıp payı {k['kucuk_reel_pay']:.3f}, defter payı {k['defter']:.3f}, "
        f"fazla medyan {k['fazla_medyan']:.3f}.",
        "",
        f"İyi köşe, TL+FX, valf kapalı / açık: kalıcılık {k['iyi_kapali']:.2f} / {k['iyi_acik']:.2f}, "
        f"reel kayıp {k['iyi_reel']:.4f} / {k['iyi_reel_acik']:.4f}, valf periyodu {k['iyi_pi']:.2f}.",
        "",
        "## Şoklar, kötü köşe",
        "",
        "| Şok | TL kapalı | TL açık | FX kapalı | FX açık | FX reel | İade |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for ad in ("yumusak", "c", "sert"):
        r = sonuc["sok"][ad]
        s.append(
            f"| {ad} | {r['tl_kapali']['kalicilik']:.2f} | {r['tl_acik']['kalicilik']:.2f} | "
            f"{r['fx_kapali']['kalicilik']:.2f} | {r['fx_acik']['kalicilik']:.2f} | "
            f"{r['fx_kapali']['reel']:.3f} | {r['fx_iade']['kalicilik']:.2f} |"
        )
    s.extend([
        "",
        "## FX hattı ayı, C, kötü köşe, TL+FX",
        "",
        "| Ay | Valf | Kalıcılık | Reel kayıp | FX açığı |",
        "| ---: | --- | ---: | ---: | ---: |",
    ])
    for r in sonuc["ay_tablo"]:
        s.append(
            f"| {r['ay']:.2f} | {'açık' if r['valf'] else 'kapalı'} | {r['kalicilik']:.2f} | "
            f"{r['reel']:.3f} | {r['acik']:.3f} |"
        )
    s.extend([
        "",
        "## Hangi hipotez hangi koşulda",
        "",
        sonuc["hipotez"],
        "",
        "## Varsayımlar",
        "",
        f"Tohum {oz.TOHUM}. Limit çekimi {oz.TOHUM + 7000}. Monte Carlo {N_MC}. "
        "204 firma, 17 sektör. Banka tavanı tur 3 dağılımı. Valf eşiği 0,25, π = 0,30.",
        "",
        "İthal payı sektör sırasında: 0,12, 0,28, 0,22, 0,35, 0,55, 0,48, 0,50, 0,52, 0,45, 0,18, 0,15, 0,08, 0,30, 0,20, 0,05, 0,06, 0,08. "
        "FX hizmeti 0,05 × ithal payı × sözleşme satışı. Üç Leontief turu. Kapasite birincilde 1.",
        "",
        "Tekrar: `python3 odeme_zinciri.py`.",
        "",
        "Dosyalar: `odeme_reel_hucre.csv`, `odeme_reel.png`, `odeme_reel_sonuc.json`.",
        "",
    ])
    _ = tablo
    return "\n".join(s)


def ozet_h(h, hacim) -> dict:
    return {
        "kalicilik": float(h[:, oz.F_KAL].mean()),
        "reel": float(reel_oran(h, hacim).mean()),
        "erime": float((h[:, oz.F_ER_TOP] / (hacim * oz.T)).mean()),
        "fx_acik": float(h[:, oz.F_FX_ACIK].mean()),
        "pi": float(h[:, oz.F_PI_N].mean()),
    }


def main_tur5() -> None:
    print("ag", N_MC)
    net = oz.ag_kur(oz.TOHUM)
    print("mekanizma", oz.mekanizma_kontrol(net))
    ith = ithal_vektor(net)
    hacim = v0(net)
    defter_pay = defter(net)
    taban, _ = oz.limit_birimleri(net, N_MC, oz.TOHUM + 7000)
    s_tl = soksuz(net, ith, 0.0, False)
    s_reel = soksuz(net, ith, 0.0, True)
    print("soksuz", s_tl[oz.F_KAL], s_reel[oz.F_KAL], float(reel_oran(s_reel[None, :], hacim)[0]))

    if os.environ.get("ODEME_SMOKE"):
        carpan = oz.sok_carpanlari(net, C_SOK, N_MC, oz.TOHUM + 1000)
        tl = hucre(net, C_SOK, carpan, oz.ORTA, 4, 0, taban, 0.0, False, False, ithal=ith)
        fx = hucre(net, C_SOK, carpan, oz.ORTA, 4, 0, taban, 0.0, True, True, ithal=ith)
        ac = hucre(net, C_SOK, carpan, oz.ORTA, 4, 0, taban, PI, True, True, ithal=ith)
        print("tl", tl[:, oz.F_KAL].mean(), "fx", fx[:, oz.F_KAL].mean(), "reel", reel_oran(fx, hacim).mean())
        print("valf", ac[:, oz.F_KAL].mean(), "reel", reel_oran(ac, hacim).mean(), "pi", ac[:, oz.F_PI_N].mean())
        return

    paket = {ad: {} for ad, _ in SOK}
    for ad, aday in SOK:
        carpan = oz.sok_carpanlari(net, aday, N_MC, oz.TOHUM + 1000)
        for kose, ia, ib, ic in (("kotu", oz.ORTA, 4, 0), ("iyi", oz.ORTA, 0, 4)):
            paket[ad][f"{kose}_tl_kapali"] = hucre(net, aday, carpan, ia, ib, ic, taban, 0.0, False, False, ithal=ith)
            paket[ad][f"{kose}_tl_acik"] = hucre(net, aday, carpan, ia, ib, ic, taban, PI, False, False, ithal=ith)
            paket[ad][f"{kose}_fx_kapali"] = hucre(net, aday, carpan, ia, ib, ic, taban, 0.0, True, True, ithal=ith)
            paket[ad][f"{kose}_fx_acik"] = hucre(net, aday, carpan, ia, ib, ic, taban, PI, True, True, ithal=ith)
            paket[ad][f"{kose}_iade"] = hucre(net, aday, carpan, ia, ib, ic, taban, 0.0, True, False, ithal=ith)
        print(ad, "kotu fx", paket[ad]["kotu_fx_kapali"][:, oz.F_KAL].mean(), flush=True)

    carpan_c = oz.sok_carpanlari(net, C_SOK, N_MC, oz.TOHUM + 1000)
    ikame_ith = np.zeros(oz.N)
    ikame = hucre(net, C_SOK, carpan_c, oz.ORTA, 4, 0, taban, 0.0, True, True, ithal=ikame_ith)
    gecis = hucre(net, C_SOK, carpan_c, oz.ORTA, 4, 0, taban, PI, True, True, ithal=ith, gecis=1.0)
    # Yan kol: yuksek ithalli bes sektorun kapasitesi 0.70. Birincil hukumde yok.
    agir = np.isin(net["sektor"], [4, 5, 6, 7, 8])
    kap_vec = np.where(agir, 0.70, 1.0)
    kapasite = hucre(net, C_SOK, carpan_c, oz.ORTA, 4, 0, taban, 0.0, True, False, ithal=ith, kapasite=kap_vec)

    ay_tablo = []
    for ay in (0.50, 1.0, 2.0):
        for pi, acik in ((0.0, False), (PI, True)):
            h = hucre(net, C_SOK, carpan_c, oz.ORTA, 4, 0, taban, pi, True, True, fx_ay=ay, ithal=ith)
            ay_tablo.append({
                "ay": ay,
                "valf": acik,
                "kalicilik": float(h[:, oz.F_KAL].mean()),
                "reel": float(reel_oran(h, hacim).mean()),
                "acik": float(h[:, oz.F_FX_ACIK].mean()),
            })

    satir = []
    for ib, alpha_i in enumerate((0, 2, 4)):
        for ic, bank_i in enumerate((0, 2, 4)):
            for pi, etiket in ((0.0, "kapali"), (PI, "acik")):
                h = hucre(net, C_SOK, carpan_c, oz.ORTA, alpha_i, bank_i, taban, pi, True, True, ithal=ith)
                satir.append({
                    "kilit": oz.ORTA,
                    "alpha": oz.GECIKME[alpha_i],
                    "banka": oz.BANKA[bank_i],
                    "valf": etiket,
                    "n": N_MC,
                    "kalicilik": float(h[:, oz.F_KAL].mean()),
                    "reel": float(reel_oran(h, hacim).mean()),
                    "erime": float((h[:, oz.F_ER_TOP] / (hacim * oz.T)).mean()),
                    "fx_acik": float(h[:, oz.F_FX_ACIK].mean()),
                    "pi_periyot": float(h[:, oz.F_PI_N].mean()),
                })
    tablo = pd.DataFrame(satir)
    tablo.to_csv(KOK / "odeme_reel_hucre.csv", index=False)

    tl_k = paket["c"]["kotu_tl_kapali"]
    tl_a = paket["c"]["kotu_tl_acik"]
    fx_k = paket["c"]["kotu_fx_kapali"]
    fx_a = paket["c"]["kotu_fx_acik"]
    iade = paket["c"]["kotu_iade"]
    tl_test = kisa_mi(tl_k, tl_a)
    fx_test = kisa_mi(fx_k, fx_a)
    # kisa_mi(a, b) = a - b. FX, TL'den uzunsa fark pozitif.
    uzama = kisa_mi(fx_k, tl_k)
    iade_test = kisa_mi(fx_k, iade)
    ikame_test = kisa_mi(fx_k, ikame)
    reel_k = reel_oran(fx_k, hacim)
    reel_a = reel_oran(fx_a, hacim)
    reel_dusme = float((reel_k - reel_a).mean())
    reel_p = oz.wilcoxon_p(reel_k - reel_a, "greater")
    valf_reel = bool(reel_dusme >= 0.05 and reel_p < 0.05)
    valf_kalicilik = bool(fx_test["valf"])
    silim = bool((not valf_kalicilik) and (not valf_reel))
    tekrar = bool(float(tl_k[:, oz.F_KAL].mean()) >= 10.0 and (not tl_test["valf"]))
    kaynak = bool(tekrar and uzama["valf"] and (not valf_kalicilik))
    er = fx_k[:, oz.F_REEL]
    er_ku = fx_k[:, oz.F_REEL_KU]
    m = er > 1e-8
    fazla = np.full(N_MC, np.nan)
    if m.any():
        fazla[m] = er_ku[m] / er[m] - defter_pay
    fazla_med = float(np.nanmedian(fazla)) if np.isfinite(fazla).any() else float("nan")
    kucuk_pay = float(np.mean(er_ku[m] / er[m])) if m.any() else float("nan")
    zayif = bool((not m.any()) or (np.isfinite(fazla_med) and fazla_med < 0.05))
    iade_reel_fark = reel_k - reel_oran(iade, hacim)
    ikame_reel_fark = reel_k - reel_oran(ikame, hacim)
    fx_reel = bool(float(iade_reel_fark.mean()) >= 0.05 and oz.wilcoxon_p(iade_reel_fark, "greater") < 0.05)
    ikame_reel = bool(float(ikame_reel_fark.mean()) >= 0.05 and oz.wilcoxon_p(ikame_reel_fark, "greater") < 0.05)

    sok_ozet = {}
    grafik_gir = {}
    for ad, _ in SOK:
        grafik_gir[ad] = {}
        sok_ozet[ad] = {}
        for anahtar, ham in (
            ("tl_kapali", f"kotu_tl_kapali"),
            ("tl_acik", f"kotu_tl_acik"),
            ("fx_kapali", f"kotu_fx_kapali"),
            ("fx_acik", f"kotu_fx_acik"),
            ("fx_iade", f"kotu_iade"),
        ):
            o = ozet_h(paket[ad][ham], hacim)
            sok_ozet[ad][anahtar] = o
            grafik_gir[ad][anahtar] = o
    grafik(grafik_gir, KOK / "odeme_reel.png")

    iyi_k = paket["c"]["iyi_fx_kapali"]
    iyi_a = paket["c"]["iyi_fx_acik"]
    karar = {
        "soksuz_uyumsuz": bool(s_reel[oz.F_KAL] >= 1.0 or reel_oran(s_reel[None, :], hacim)[0] > 0.01),
        "tekrar": tekrar,
        "silim_gerekli_degil": silim,
        "valf_kalicilik": valf_kalicilik,
        "valf_reel": valf_reel,
        "kaynak_reel": kaynak,
        "fx_cozer": bool(iade_test["valf"]),
        "ikame_cozer": bool(ikame_test["valf"]),
        "zayif": zayif,
        "fx_reel": fx_reel,
        "ikame_reel": ikame_reel,
        "tl_kapali": float(tl_k[:, oz.F_KAL].mean()),
        "tl_acik": float(tl_a[:, oz.F_KAL].mean()),
        "tl_kisalma": tl_test["fark_ortalama"],
        "tl_p": tl_test["p"],
        "fx_kapali": float(fx_k[:, oz.F_KAL].mean()),
        "fx_acik": float(fx_a[:, oz.F_KAL].mean()),
        "fx_kisalma": fx_test["fark_ortalama"],
        "fx_p": fx_test["p"],
        "reel_tl": float(reel_oran(tl_k, hacim).mean()),
        "reel_fx": float(reel_k.mean()),
        "reel_fx_acik": float(reel_a.mean()),
        "reel_dusme": reel_dusme,
        "reel_p": reel_p,
        "fx_acigi": float(fx_k[:, oz.F_FX_ACIK].mean()),
        "erime_fx": float((fx_a[:, oz.F_ER_TOP] / (hacim * oz.T)).mean()),
        "iade": float(iade[:, oz.F_KAL].mean()),
        "iade_reel": float(reel_oran(iade, hacim).mean()),
        "iade_kisalma": iade_test["fark_ortalama"],
        "iade_p": iade_test["p"],
        "ikame": float(ikame[:, oz.F_KAL].mean()),
        "ikame_reel": float(reel_oran(ikame, hacim).mean()),
        "ikame_kisalma": ikame_test["fark_ortalama"],
        "ikame_p": ikame_test["p"],
        "gecis": float(gecis[:, oz.F_KAL].mean()),
        "gecis_reel": float(reel_oran(gecis, hacim).mean()),
        "kapasite": float(kapasite[:, oz.F_KAL].mean()),
        "kapasite_reel": float(reel_oran(kapasite, hacim).mean()),
        "kucuk_reel_pay": kucuk_pay,
        "defter": defter_pay,
        "fazla_medyan": fazla_med,
        "iyi_kapali": float(iyi_k[:, oz.F_KAL].mean()),
        "iyi_acik": float(iyi_a[:, oz.F_KAL].mean()),
        "iyi_reel": float(reel_oran(iyi_k, hacim).mean()),
        "iyi_reel_acik": float(reel_oran(iyi_a, hacim).mean()),
        "iyi_pi": float(iyi_a[:, oz.F_PI_N].mean()),
        "uzama": uzama["fark_ortalama"],
        "uzama_p": uzama["p"],
    }
    ozet, hipotez = hukum(karar)
    sonuc = {
        "uyari": (
            "Sentetik ağ ve sentetik ithal payları. TCMB finansal hesaplarına, KAP bildirimlerine "
            "veya bu depodaki stok-akış matrislerine kalibre edilmedi. Sayılar ölçüm değildir."
        ),
        "ozet": ozet,
        "hipotez": hipotez,
        "karar": karar,
        "sok": sok_ozet,
        "ay_tablo": ay_tablo,
        "soksuz_tl": float(s_tl[oz.F_KAL]),
        "soksuz_reel": float(s_reel[oz.F_KAL]),
        "soksuz_reel_kayip": float(reel_oran(s_reel[None, :], hacim)[0]),
        "n_mc": N_MC,
        "tohum": oz.TOHUM,
    }
    (KOK / "odeme_reel_sonuc.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2, default=oz.numpy_json) + "\n",
        encoding="utf-8",
    )
    eski = (KOK / "ODEME_ZINCIRI.md").read_text(encoding="utf-8")
    if eski.startswith("# Ödeme zinciri, tur 5") and ISARET in eski:
        eski = eski.split(ISARET, 1)[1]
    (KOK / "ODEME_ZINCIRI.md").write_text(rapor_metni(sonuc, tablo) + ISARET + eski, encoding="utf-8")
    print(ozet)


if __name__ == "__main__":
    main_tur5()
