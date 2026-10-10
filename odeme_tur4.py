"""Tur 4: enflasyon kanali. Karar kurallari modul belgesinde, kosu oncesinden.

Ag basamak erisimli sentetik agdir. TCMB/KAP kalibrasyonu yok.
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
from odeme_tur2 import C_SOK, SERT, YUMUSAK, aday_yap, anlamli_uzama

KOK = Path(__file__).resolve().parent
N_MC = 8 if os.environ.get("ODEME_SMOKE") else 50
ESIKLER = (0.50, 0.25, 0.10)
PILER = (0.10, 0.30, 0.60)
KILIT_IX = (0, 2, 4)
ALPHA_IX = (0, 2, 4)
BANK_IX = (0, 2, 4)
BIRINCIL_E = 1  # 0.25
BIRINCIL_P = 1  # 0.30
KOTU = (1, 2, 0)  # orta kilit, alpha 0.60, banka 0
IYI = (1, 0, 2)  # orta kilit, alpha 0, banka 4
BAZ = (1, 1, 1)
SOK_AD = ("yumusak", "c", "sert")
SOK_ADAY = (YUMUSAK, C_SOK, SERT)
ISARET = "\n\n<!-- ONCEKI -->\n\n"


def hucre(net, aday, carpan, ia, ib, ic, esik, pi, yerel=False, fx_pay=None):
    return oz.kosu_hucre(
        net, aday, carpan, ia, ib, ic, range(N_MC),
        enflasyon_esik=esik, enflasyon_pi=pi, yerel=yerel, fx_pay=fx_pay,
    )[0]


def soksuz(net, esik, pi, yerel=False) -> np.ndarray:
    lik, dis = oz.hazirla(net, C_SOK, None)
    return oz.tek_kosu_temiz(
        net, lik, oz.BANKA[oz.ORTA] * net["banka_taban"],
        oz.KILIT[oz.ORTA][0], oz.KILIT[oz.ORTA][1], oz.GECIKME[oz.ORTA], dis,
        enflasyon_esik=esik, enflasyon_pi=pi, yerel=yerel,
    )[0]


def pay_kucuk(h):
    top = h[:, oz.F_OD_TOP]
    ku = h[:, oz.F_OD_KU]
    out = np.full(h.shape[0], np.nan)
    m = top > 1e-8
    out[m] = ku[m] / top[m]
    return out


def erime_oran(h, v0) -> np.ndarray:
    return h[:, oz.F_ER_TOP] / (v0 * oz.T)


def kisa_mi(kapali, acik) -> dict:
    fark = kapali[:, oz.F_KAL] - acik[:, oz.F_KAL]
    p = oz.wilcoxon_p(fark, "greater")
    return {
        "fark_ortalama": float(np.mean(fark)),
        "fark_medyan": float(np.median(fark)),
        "p": p,
        "valf": bool(anlamli_uzama(fark) and p < 0.05 and float(np.mean(fark)) > 0),
    }


def defter_payi(net) -> float:
    return float(net["w0"][net["idx_ku_al"]].sum() / net["w0"].sum())


def fx_kenar(net) -> np.ndarray:
    """Yan deney. Buyuk borclu 0.40, orta 0.20, kucuk 0.05. Olcum degil."""
    borclu = net["borclu"]
    pay = np.full(borclu.shape[0], 0.20)
    pay[net["kucuk"][borclu]] = 0.05
    pay[net["buyuk"][borclu]] = 0.40
    return pay


def kalibrasyon_notu() -> str:
    return (
        "İkinci aşama kapanmadı. `hekis_enflasyon.py` yıllık TÜFE’yi "
        "`hekis-model-main/data/istanbul_2026.json` içinden okur; dosya bu ortamda yok. "
        "Sektör makro çalışma kitabı da yok. Kanalın cebiri o dosyadaki formülle aynı: "
        "reel değişim = −alacak × π / (1+π). Izgaradaki π ölçülmüş enflasyon değildir."
    )


def grafik(ozet_sok, tablo, dosya: Path) -> None:
    fig, ax = plt.subplots(2, 2, figsize=(11.2, 8.2))
    adlar = ["Yumuşak", "C", "Sert"]
    x = np.arange(3)
    gen = 0.36
    kap = [ozet_sok[a]["kotu_kapali"] for a in SOK_AD]
    ac = [ozet_sok[a]["kotu_acik"] for a in SOK_AD]
    ax[0, 0].bar(x - gen / 2, kap, width=gen, label="Kanal kapalı", color="#4C78A8")
    ax[0, 0].bar(x + gen / 2, ac, width=gen, label="Birincil valf", color="#F58518")
    ax[0, 0].set_xticks(x, adlar)
    ax[0, 0].set_ylabel("Ortalama bloke periyot")
    ax[0, 0].set_title("Kötü köşe, kalıcılık")
    ax[0, 0].legend(frameon=False, fontsize=8)

    dil = tablo[(tablo.kilit == oz.ORTA) & np.isclose(tablo.esik, 0.25) & np.isclose(tablo.pi, 0.30)]
    isi = np.full((3, 3), np.nan)
    for _, r in dil.iterrows():
        i = ALPHA_IX.index(int(r.gecikme))
        j = BANK_IX.index(int(r.banka))
        isi[i, j] = r.kisalma
    im = ax[0, 1].imshow(isi, origin="lower", cmap="viridis", aspect="auto")
    ax[0, 1].set_xticks(range(3), [str(oz.BANKA[i]) for i in BANK_IX])
    ax[0, 1].set_yticks(range(3), [str(oz.GECIKME[i]) for i in ALPHA_IX])
    ax[0, 1].set_xlabel("Banka çarpanı")
    ax[0, 1].set_ylabel("Gecikme α")
    ax[0, 1].set_title("C, kısalma (kapalı − açık), kilit orta")
    for i in range(3):
        for j in range(3):
            if np.isfinite(isi[i, j]):
                ax[0, 1].text(j, i, f"{isi[i, j]:.1f}", ha="center", va="center", color="w", fontsize=8)
    fig.colorbar(im, ax=ax[0, 1], fraction=0.046, pad=0.04)

    siddet = [ozet_sok[a]["siddet"] for a in SOK_AD]
    ax[1, 0].plot(siddet, [ozet_sok[a]["pi_kotu"] for a in SOK_AD], "o-", label="Kötü, valf periyodu")
    ax[1, 0].plot(siddet, [ozet_sok[a]["pi_iyi"] for a in SOK_AD], "s-", label="İyi, valf periyodu")
    ax[1, 0].set_xlabel("Şok şiddeti = sektör × (1 − kalan)")
    ax[1, 0].set_ylabel("Ortalama enflasyon periyodu")
    ax[1, 0].set_title("Valf ne zaman açılıyor")
    ax[1, 0].legend(frameon=False, fontsize=8)

    ax[1, 1].bar(x - gen / 2, [ozet_sok[a]["erime_kotu"] for a in SOK_AD], width=gen, label="Kötü", color="#E45756")
    ax[1, 1].bar(x + gen / 2, [ozet_sok[a]["erime_iyi"] for a in SOK_AD], width=gen, label="İyi", color="#54A24B")
    ax[1, 1].axhline(0.02, color="0.4", ls="--", lw=0.8, label="Eşik 0,02")
    ax[1, 1].set_xticks(x, adlar)
    ax[1, 1].set_ylabel("Erime / (V0 × T)")
    ax[1, 1].set_title("Reel erime, birincil valf")
    ax[1, 1].legend(frameon=False, fontsize=8)
    fig.suptitle("Enflasyon kanalı. Sentetik ağ, TCMB/KAP yok.", fontsize=11)
    fig.tight_layout()
    fig.savefig(dosya, dpi=120)
    plt.close(fig)


def rapor_metni(sonuc, tarama) -> str:
    k = sonuc["karar"]
    satir = [
        "# Ödeme zinciri, tur 4: enflasyon kanalı",
        "",
        sonuc["uyari"],
        "",
        "## Hüküm",
        "",
        sonuc["ozet"],
        "",
        "## Kural",
        "",
        "Valf, bir önceki periyodun şiddeti ve ödenmeyen stok / aylık fatura ikisi de eşiği geçince açılır. "
        "Açılınca nakit yükümlülük 1/(1+π) olur. Erime = yükümlülük × π/(1+π); alacaklının reel kaybı, borçlunun rahatlaması. "
        "Erime ödenmeyen tutara yazılmaz. Tahsil, erimeden sonraki yükümlülüğe göredir. Birincil ayar: eşik 0,25, π = 0,30. "
        "Kilit orta, kötü köşe α = 0,60 ve banka 0, iyi köşe α = 0 ve banka 4.",
        "",
        sonuc["kalibrasyon"],
        "",
        f"Şoksuz, kanal kapalı: kalıcılık {sonuc['soksuz_kapali']:.2f}. "
        f"Şoksuz, birincil valf: kalıcılık {sonuc['soksuz_acik']:.2f}, erime oranı {sonuc['soksuz_erime']:.4f}. "
        f"Şoksuz, yerel tercih: kalıcılık {sonuc['soksuz_yerel']:.2f}, erime oranı {sonuc['soksuz_yerel_erime']:.4f}.",
        "",
        "## C şoku, birincil valf",
        "",
        f"Kötü köşe kapalı / açık: {k['kotu_kapali']:.2f} / {k['kotu_acik']:.2f}. "
        f"Kısalma ortalama {k['kisalma_ortalama']:.2f}, medyan {k['kisalma_medyan']:.2f}, tek yanlı p = {k['kisalma_p']:.4g}.",
        "",
        f"İyi köşe kapalı / açık: {k['iyi_kapali']:.2f} / {k['iyi_acik']:.2f}. "
        f"Baz kapalı / açık: {k['baz_kapali']:.2f} / {k['baz_acik']:.2f}.",
        "",
        f"Kötü köşede ortalama enflasyon periyodu {k['pi_kotu']:.2f}, iyi köşede {k['pi_iyi']:.2f}.",
        "",
        f"Erime / (V0 × T), kötü {k['erime_kotu']:.4f}, iyi {k['erime_iyi']:.4f}. "
        f"Küçük alacaklının erime payı {k['erime_kucuk_pay']:.3f}, defter payı {k['defter_pay']:.3f}, "
        f"fazla medyan {k['erime_fazla_medyan']:.3f}.",
        "",
        f"Küçük alacaklının ödenmeyen payı, açık − kapalı medyan {k['pay_fark_medyan']:.4f}, "
        f"n = {k['pay_n']}, tek yanlı p = {k['pay_p']:.4g}.",
        "",
        f"Küçük borçluya düşen erime payı {k['kucuk_borclu_pay']:.3f}. Büyük alacaklının erime payı {k['buyuk_erime_pay']:.3f}.",
        "",
        sonuc["yerel_metin"],
        "",
        sonuc["fx_metin"],
        "",
        "## Şoklar, kötü köşe, birincil valf",
        "",
        "| Şok | Şiddet | Kapalı | Açık | Kısalma | p | Valf periyodu | Erime oranı | Valf |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for ad in SOK_AD:
        r = tarama[tarama.ad == ad].iloc[0]
        satir.append(
            f"| {ad} | {r.siddet:.2f} | {r.kapali:.2f} | {r.acik:.2f} | {r.kisalma:.2f} | "
            f"{r.p:.3g} | {r.pi_periyot:.2f} | {r.erime:.4f} | {'evet' if r.valf else 'hayır'} |"
        )
    satir.extend([
        "",
        "## Eşik × şiddet, C şoku, kötü köşe",
        "",
        "| Eşik | π | Kapalı | Açık | Kısalma | Erime | Valf periyodu | Valf |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ])
    for r in sonuc["esik_tablo"]:
        satir.append(
            f"| {r['esik']:.2f} | {r['pi']:.2f} | {r['kapali']:.2f} | {r['acik']:.2f} | "
            f"{r['kisalma']:.2f} | {r['erime']:.4f} | {r['pi_periyot']:.2f} | "
            f"{'evet' if r['valf'] else 'hayır'} |"
        )
    satir.extend([
        "",
        "## Hangi hipotez hangi koşulda",
        "",
        sonuc["hipotez"],
        "",
        "## Varsayımlar",
        "",
        f"Tohum {oz.TOHUM}. Monte Carlo {N_MC}. Ufuk {oz.T}. Ağ tur 2 ile aynı sentetik çizim, basamak banka erişimi. "
        "Şok tamponu U(0,95, 1,40), ek şok firmaların %8’i × 0,45. "
        "Yumuşak: 2 sektör × 0,55. C: 3 sektör × 0,30. Sert: 4 sektör × 0,20.",
        "",
        "Izgara: kilit, α ve banka indeks {0, 2, 4}; eşik {0,50, 0,25, 0,10}; π {0,10, 0,30, 0,60}.",
        "",
        "Yerel tercih birincil teste girmez. FX yan deneyi de girmez: büyük borçluda pay 0,40, ortada 0,20, küçükte 0,05; geçişkenlik 1. Bu paylar ölçüm değildir.",
        "",
        "Tekrar: `python3 odeme_zinciri.py`.",
        "",
        "Dosyalar: `odeme_enf_hucre.csv`, `odeme_enf_sok.csv`, `odeme_enf.png`, `odeme_enf_sonuc.json`.",
        "",
    ])
    return "\n".join(satir)


def hukum(k) -> tuple[str, str]:
    parca = []
    if k["soksuz_uyumsuz"]:
        parca.append(
            "Birincil valf şoksuz kontrolde kalıcılık veya erime üretti. Eşik sonuca göre ayarlanmadı."
        )
    if k["valf"]:
        parca.append(
            "Kötü köşede, C şokunda enflasyon kanalı kalıcılığı pratik eşiğin üstünde kısaltıyor. Valf işliyor."
        )
    else:
        parca.append(
            "Kötü köşede, C şokunda enflasyon kanalı kalıcılığı pratik eşiğin üstünde kısaltmıyor. Valf işlemiyor."
        )
    if k["aktarim"]:
        parca.append(
            "Aynı hücrede reel erime belirgin ve zincir içi küçük alacaklı payı 5 puan büyümüyor. "
            "Yük borçludan alacaklıya enflasyonla geçmiş olabilir."
        )
    else:
        parca.append(
            "Aktarım iddiası desteklenmedi: ya erime 0,02 eşiğinin altında ya da küçük alacaklının ödenmeyen payı sistematik büyüyor."
        )
    if k["hiyerarsi"]:
        parca.append(
            "Hiyerarşi duruyor. İyi köşede valf neredeyse açılmıyor ve kalıcılık kısa. "
            "Kötü köşede valf açılıyor. Yumuşak şokta enflasyon periyodu sert şoktan az."
        )
    else:
        parca.append(
            "Hiyerarşi kapanmadı: valf banka limiti genişken de açılıyor, kötü köşede açılmıyor, ya da şok büyüdükçe periyot artmıyor."
        )
    if k["zayif"]:
        parca.append(
            "Küçük alacaklının erime payı defter payını 5 puan aşmıyor. Zayıf halka bu kanalda da zayıf."
        )
    else:
        parca.append(
            "Küçük alacaklının erime payı defter payının en az 5 puan üstünde. Zayıf halka bu kanalda yeniden açılır."
        )
    hipotez = " ".join(parca)
    if k["valf"] and k["aktarim"] and k["hiyerarsi"] and k["zayif"] and not k["soksuz_uyumsuz"]:
        ozet = (
            "Büyük şokta, banka kapalıyken enflasyon valfi kalıcılığı kısaltıyor ve reel yükü alacaklıya yazıyor. "
            "Zincir içi küçük pay sistematik büyümüyor. Banka limiti genişken valf açılmıyor. "
            "Küçük alacaklı, defter payından fazla erime taşımıyor. Kalibrasyon kapanmadı."
        )
    elif (not k["valf"]) and k["hiyerarsi"]:
        ozet = (
            "Enflasyon kanalı bu kuralda kalıcılığı pratik eşiğin üstünde kısaltmıyor. "
            "Banka limiti genişken valf yine kapalı. Aktarımın enflasyona kaydığı iddiası desteklenmedi. "
            "Kalibrasyon kapanmadı."
        )
    else:
        ozet = hipotez
    return ozet, hipotez


def main_tur4() -> None:
    print("ag", N_MC)
    net = oz.ag_kur(oz.TOHUM)
    print("mekanizma", oz.mekanizma_kontrol(net))
    v0 = float(net["w0"].sum())
    defter = defter_payi(net)
    s0 = soksuz(net, 1.0, 0.0)
    s1 = soksuz(net, ESIKLER[BIRINCIL_E], PILER[BIRINCIL_P])
    s2 = soksuz(net, ESIKLER[BIRINCIL_E], PILER[BIRINCIL_P], yerel=True)
    print(
        "soksuz",
        s0[oz.F_KAL], s1[oz.F_KAL], float(erime_oran(s1[None, :], v0)[0]),
        s2[oz.F_KAL], float(erime_oran(s2[None, :], v0)[0]),
    )

    if os.environ.get("ODEME_SMOKE"):
        carpan = oz.sok_carpanlari(net, C_SOK, N_MC, oz.TOHUM + 1000)
        ia, ib, ic = (oz.ORTA, 4, 0)
        kap = hucre(net, C_SOK, carpan, ia, ib, ic, 1.0, 0.0)
        ac = hucre(net, C_SOK, carpan, ia, ib, ic, 0.25, 0.30)
        iyi = hucre(net, C_SOK, carpan, oz.ORTA, 0, 4, 0.25, 0.30)
        print("kotu kapali", kap[:, oz.F_KAL].mean(), "acik", ac[:, oz.F_KAL].mean(), "pi", ac[:, oz.F_PI_N].mean())
        print("erime", erime_oran(ac, v0).mean(), "iyi", iyi[:, oz.F_KAL].mean(), "iyi pi", iyi[:, oz.F_PI_N].mean())
        return

    acik = np.empty((3, 3, 3, 3, 3, 3, N_MC, oz.N_F))
    kapali = np.empty((3, 3, 3, 3, N_MC, oz.N_F))
    for si, aday in enumerate(SOK_ADAY):
        carpan = oz.sok_carpanlari(net, aday, N_MC, oz.TOHUM + 1000)
        for a, ia in enumerate(KILIT_IX):
            for b, ib in enumerate(ALPHA_IX):
                for c, ic in enumerate(BANK_IX):
                    kapali[si, a, b, c] = hucre(net, aday, carpan, ia, ib, ic, 1.0, 0.0)
                    for e, esik in enumerate(ESIKLER):
                        for p, pi in enumerate(PILER):
                            acik[si, a, b, c, e, p] = hucre(net, aday, carpan, ia, ib, ic, esik, pi)
            print(f"sok {SOK_AD[si]} kilit {a} bitti", flush=True)

    # Tarama: birincil valf, kotu ve iyi, 20 sok
    tarama_satir = []
    for n_sek in (1, 2, 3, 4):
        for kalan in (0.70, 0.55, 0.40, 0.30, 0.20):
            aday = aday_yap(n_sek, kalan)
            carpan = oz.sok_carpanlari(net, aday, N_MC, oz.TOHUM + 1000)
            kap = hucre(net, aday, carpan, oz.ORTA, 4, 0, 1.0, 0.0)
            ac = hucre(net, aday, carpan, oz.ORTA, 4, 0, ESIKLER[BIRINCIL_E], PILER[BIRINCIL_P])
            iyi = hucre(net, aday, carpan, oz.ORTA, 0, 4, ESIKLER[BIRINCIL_E], PILER[BIRINCIL_P])
            test = kisa_mi(kap, ac)
            tarama_satir.append({
                "n_sek": n_sek,
                "kalan": kalan,
                "siddet": float(n_sek * (1.0 - kalan)),
                "ad": { (2, 0.55): "yumusak", (3, 0.30): "c", (4, 0.20): "sert" }.get((n_sek, kalan), ""),
                "kapali": float(kap[:, oz.F_KAL].mean()),
                "acik": float(ac[:, oz.F_KAL].mean()),
                "kisalma": test["fark_ortalama"],
                "p": test["p"],
                "valf": test["valf"],
                "pi_periyot": float(ac[:, oz.F_PI_N].mean()),
                "pi_iyi": float(iyi[:, oz.F_PI_N].mean()),
                "erime": float(erime_oran(ac, v0).mean()),
                "erime_iyi": float(erime_oran(iyi, v0).mean()),
                "iyi_kalicilik": float(iyi[:, oz.F_KAL].mean()),
            })
            print(f"tarama {n_sek} {kalan:.2f} kisalma {test['fark_ortalama']:.2f}", flush=True)
    tarama = pd.DataFrame(tarama_satir)

    def dilim(sok, kose, esik_i=BIRINCIL_E, pi_i=BIRINCIL_P, kanal="acik"):
        a, b, c = kose
        if kanal == "kapali":
            return kapali[sok, a, b, c]
        return acik[sok, a, b, c, esik_i, pi_i]

    c_test = kisa_mi(dilim(1, KOTU, kanal="kapali"), dilim(1, KOTU))
    kotu_ac = dilim(1, KOTU)
    kotu_ka = dilim(1, KOTU, kanal="kapali")
    iyi_ac = dilim(1, IYI)
    iyi_ka = dilim(1, IYI, kanal="kapali")
    baz_ac = dilim(1, BAZ)
    baz_ka = dilim(1, BAZ, kanal="kapali")

    erime_k = erime_oran(kotu_ac, v0)
    erime_i = erime_oran(iyi_ac, v0)
    er_top = kotu_ac[:, oz.F_ER_TOP]
    er_ku = kotu_ac[:, oz.F_ER_KU]
    m = er_top > 1e-8
    fazla = np.full(N_MC, np.nan)
    fazla[m] = er_ku[m] / er_top[m] - defter
    fazla_med = float(np.nanmedian(fazla)) if np.isfinite(fazla).any() else float("nan")
    kucuk_pay = float(np.mean(er_ku[m] / er_top[m])) if m.any() else float("nan")
    buyuk_pay = float(np.mean(kotu_ac[m, oz.F_ER_BU] / er_top[m])) if m.any() else float("nan")
    kdb = float(np.mean(kotu_ac[m, oz.F_ER_KDB] / er_top[m])) if m.any() else float("nan")

    pay_fark = pay_kucuk(kotu_ac) - pay_kucuk(kotu_ka)
    gecerli = np.isfinite(pay_fark)
    if gecerli.any():
        pay_med = float(np.median(pay_fark[gecerli]))
        pay_p = oz.wilcoxon_p(pay_fark[gecerli], "greater")
        pay_n = int(gecerli.sum())
    else:
        pay_med, pay_p, pay_n = float("nan"), 1.0, 0
    pay_buyumedi = bool(pay_n < 30 or not np.isfinite(pay_med) or pay_med < 0.05 or pay_p >= 0.05)

    valf = bool(c_test["valf"])
    aktarim = bool(float(np.mean(erime_k)) >= 0.02 and pay_buyumedi)
    pi_kotu = float(kotu_ac[:, oz.F_PI_N].mean())
    pi_iyi = float(iyi_ac[:, oz.F_PI_N].mean())
    yumusak_pi = float(dilim(0, KOTU)[:, oz.F_PI_N].mean())
    sert_pi = float(dilim(2, KOTU)[:, oz.F_PI_N].mean())
    hiyerarsi = bool(
        pi_iyi < 1.0
        and float(iyi_ac[:, oz.F_KAL].mean()) < 1.0
        and pi_kotu >= 2.0
        and yumusak_pi < sert_pi
    )
    zayif = bool(np.isfinite(fazla_med) and fazla_med < 0.05) or (not m.any())

    esik_tablo = []
    for e, esik in enumerate(ESIKLER):
        for p, pi in enumerate(PILER):
            ac = dilim(1, KOTU, e, p)
            test = kisa_mi(kotu_ka, ac)
            esik_tablo.append({
                "esik": esik,
                "pi": pi,
                "kapali": float(kotu_ka[:, oz.F_KAL].mean()),
                "acik": float(ac[:, oz.F_KAL].mean()),
                "kisalma": test["fark_ortalama"],
                "erime": float(erime_oran(ac, v0).mean()),
                "pi_periyot": float(ac[:, oz.F_PI_N].mean()),
                "valf": test["valf"],
            })

    # Yerel ve FX, C, kotu ve iyi
    carpan_c = oz.sok_carpanlari(net, C_SOK, N_MC, oz.TOHUM + 1000)
    yerel_k = hucre(net, C_SOK, carpan_c, oz.ORTA, 4, 0, 0.25, 0.30, yerel=True)
    yerel_i = hucre(net, C_SOK, carpan_c, oz.ORTA, 0, 4, 0.25, 0.30, yerel=True)
    yerel_test = kisa_mi(kotu_ka, yerel_k)
    fx = hucre(net, C_SOK, carpan_c, oz.ORTA, 4, 0, 0.25, 0.30, fx_pay=fx_kenar(net))
    fx_test = kisa_mi(kotu_ka, fx)
    yerel_metin = (
        f"Yerel tercih, C, kötü köşe: kalıcılık {yerel_k[:, oz.F_KAL].mean():.2f}, "
        f"kapalıya göre kısalma {yerel_test['fark_ortalama']:.2f}, p = {yerel_test['p']:.4g}, "
        f"erime oranı {erime_oran(yerel_k, v0).mean():.4f}. "
        f"İyi köşe kalıcılık {yerel_i[:, oz.F_KAL].mean():.2f}, "
        f"enflasyon periyodu {yerel_i[:, oz.F_PI_N].mean():.2f}. Birincil hükme girmez."
    )
    fx_metin = (
        f"FX yan deneyi, kötü köşe, geçişkenlik 1: kalıcılık {fx[:, oz.F_KAL].mean():.2f}, "
        f"kısalma {fx_test['fark_ortalama']:.2f}, erime oranı {erime_oran(fx, v0).mean():.4f}. "
        "Birincil hükme girmez."
    )

    # Hucre tablosu, C, acik kanal
    satirlar = []
    for a, ia in enumerate(KILIT_IX):
        for b, ib in enumerate(ALPHA_IX):
            for c, ic in enumerate(BANK_IX):
                for e, esik in enumerate(ESIKLER):
                    for p, pi in enumerate(PILER):
                        h = acik[1, a, b, c, e, p]
                        kap = kapali[1, a, b, c]
                        satirlar.append({
                            "sok": "c",
                            "kilit": ia,
                            "kilit_esik": oz.KILIT[ia][0],
                            "gecikme": ib,
                            "gecikme_alpha": oz.GECIKME[ib],
                            "banka": ic,
                            "banka_carpan": oz.BANKA[ic],
                            "esik": esik,
                            "pi": pi,
                            "n": N_MC,
                            "kalicilik_acik": float(h[:, oz.F_KAL].mean()),
                            "kalicilik_kapali": float(kap[:, oz.F_KAL].mean()),
                            "kisalma": float((kap[:, oz.F_KAL] - h[:, oz.F_KAL]).mean()),
                            "pi_periyot": float(h[:, oz.F_PI_N].mean()),
                            "erime_oran": float(erime_oran(h, v0).mean()),
                            "kucuk_odenmeyen_payi": float(np.nanmean(pay_kucuk(h))),
                        })
    tablo = pd.DataFrame(satirlar)
    tablo.to_csv(KOK / "odeme_enf_hucre.csv", index=False)
    tarama.to_csv(KOK / "odeme_enf_sok.csv", index=False)

    ozet_sok = {}
    for i, ad in enumerate(SOK_AD):
        ozet_sok[ad] = {
            "kotu_kapali": float(dilim(i, KOTU, kanal="kapali")[:, oz.F_KAL].mean()),
            "kotu_acik": float(dilim(i, KOTU)[:, oz.F_KAL].mean()),
            "pi_kotu": float(dilim(i, KOTU)[:, oz.F_PI_N].mean()),
            "pi_iyi": float(dilim(i, IYI)[:, oz.F_PI_N].mean()),
            "erime_kotu": float(erime_oran(dilim(i, KOTU), v0).mean()),
            "erime_iyi": float(erime_oran(dilim(i, IYI), v0).mean()),
            "siddet": float(SOK_ADAY[i]["n_sek"] * (1.0 - SOK_ADAY[i]["kalan"])),
        }

    karar = {
        "soksuz_uyumsuz": bool(s1[oz.F_KAL] >= 1.0 or erime_oran(s1[None, :], v0)[0] > 1e-8),
        "valf": valf,
        "aktarim": aktarim,
        "hiyerarsi": hiyerarsi,
        "zayif": zayif,
        "kotu_kapali": float(kotu_ka[:, oz.F_KAL].mean()),
        "kotu_acik": float(kotu_ac[:, oz.F_KAL].mean()),
        "iyi_kapali": float(iyi_ka[:, oz.F_KAL].mean()),
        "iyi_acik": float(iyi_ac[:, oz.F_KAL].mean()),
        "baz_kapali": float(baz_ka[:, oz.F_KAL].mean()),
        "baz_acik": float(baz_ac[:, oz.F_KAL].mean()),
        "kisalma_ortalama": c_test["fark_ortalama"],
        "kisalma_medyan": c_test["fark_medyan"],
        "kisalma_p": c_test["p"],
        "pi_kotu": pi_kotu,
        "pi_iyi": pi_iyi,
        "pi_yumusak": yumusak_pi,
        "pi_sert": sert_pi,
        "erime_kotu": float(np.mean(erime_k)),
        "erime_iyi": float(np.mean(erime_i)),
        "erime_kucuk_pay": kucuk_pay,
        "erime_fazla_medyan": fazla_med,
        "defter_pay": defter,
        "buyuk_erime_pay": buyuk_pay,
        "kucuk_borclu_pay": kdb,
        "pay_fark_medyan": pay_med,
        "pay_n": pay_n,
        "pay_p": pay_p,
        "pay_buyumedi": pay_buyumedi,
    }
    ozet, hipotez = hukum(karar)
    grafik(ozet_sok, tablo, KOK / "odeme_enf.png")
    sonuc = {
        "uyari": (
            "Sentetik ağ. TCMB finansal hesaplarına, KAP bildirimlerine veya bu depodaki "
            "stok-akış matrislerine kalibre edilmedi. Sayılar ölçüm değildir."
        ),
        "ozet": ozet,
        "hipotez": hipotez,
        "kalibrasyon": kalibrasyon_notu(),
        "karar": karar,
        "esik_tablo": esik_tablo,
        "yerel_metin": yerel_metin,
        "fx_metin": fx_metin,
        "soksuz_kapali": float(s0[oz.F_KAL]),
        "soksuz_acik": float(s1[oz.F_KAL]),
        "soksuz_erime": float(erime_oran(s1[None, :], v0)[0]),
        "soksuz_yerel": float(s2[oz.F_KAL]),
        "soksuz_yerel_erime": float(erime_oran(s2[None, :], v0)[0]),
        "n_mc": N_MC,
        "tohum": oz.TOHUM,
    }
    (KOK / "odeme_enf_sonuc.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2, default=oz.numpy_json) + "\n",
        encoding="utf-8",
    )
    eski = (KOK / "ODEME_ZINCIRI.md").read_text(encoding="utf-8")
    if ISARET in eski:
        eski = eski.split(ISARET, 1)[1]
    (KOK / "ODEME_ZINCIRI.md").write_text(rapor_metni(sonuc, tarama) + ISARET + eski, encoding="utf-8")
    print(ozet)


if __name__ == "__main__":
    main_tur4()
