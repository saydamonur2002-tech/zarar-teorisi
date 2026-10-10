"""Tur 3: heterojen banka limiti. KAP agi yok.

Karar kurallari odeme_zinciri modul belgesinde, kosu oncesinden durur.
Basamak erisim tur 2 dosyalarinda durur; bu kosu onlari ezmez.
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
from odeme_tur2 import (
    C_SOK,
    KOLLAR,
    SOK_KALAN,
    SOK_SEKTOR,
    aday_yap,
    anlamli_uzama,
    kol_anlamli,
    ozet_kol,
    pay_vektor,
    sektor_satir,
    sira_karsilastir,
)

KOK = Path(__file__).resolve().parent
N_MC = 8 if os.environ.get("ODEME_SMOKE") else 60
TOHUM_LIMIT = oz.TOHUM + 7000
ISARET = "\n\n<!-- TUR2 -->\n\n"


def kosu_kol(net, aday, carpan, ad, tabanlar, patika=False):
    ia, ib, ic, secim = KOLLAR[ad]
    return oz.kosu_hucre(
        net, aday, carpan, ia, ib, ic, range(N_MC),
        patika=patika, secim=secim, tabanlar=tabanlar,
    )


def soksuz_ortalama(net, tabanlar, secim=False) -> float:
    lik, dis = oz.hazirla(net, C_SOK, None)
    esik, sure = oz.KILIT[oz.ORTA]
    alpha = oz.GECIKME[oz.ORTA]
    kal = np.empty(N_MC)
    for s in range(N_MC):
        birim = net["banka_taban"] if tabanlar is None else tabanlar[s]
        out, _, _ = oz.tek_kosu_temiz(
            net, lik, oz.BANKA[oz.ORTA] * birim, esik, sure, alpha, dis,
            secim=secim, secim_taban=birim,
        )
        kal[s] = out[oz.F_KAL]
    return float(kal.mean())


def erisim_ozet(net, erisim: np.ndarray) -> dict:
    def parca(mask):
        alt = erisim[:, mask]
        pozitif = alt[alt > 0]
        return {
            "sifir_pay": float((alt == 0).mean()),
            "pozitif_medyan": float(np.median(pozitif)) if pozitif.size else 0.0,
            "medyan": float(np.median(alt)),
        }

    orta = ~net["kucuk"] & ~net["buyuk"]
    return {
        "kucuk": parca(net["kucuk"]),
        "orta": parca(orta),
        "buyuk": parca(net["buyuk"]),
    }


def tarama_yap(net, carpan_hazir, tabanlar) -> tuple[pd.DataFrame, dict, dict, dict]:
    kayit = []
    vektor = {}
    yavas = {}
    patika = {}
    for n_sek in SOK_SEKTOR:
        for kalan in SOK_KALAN:
            aday = aday_yap(n_sek, kalan)
            carpan = carpan_hazir.get((n_sek, kalan))
            if carpan is None:
                carpan = oz.sok_carpanlari(net, aday, N_MC, oz.TOHUM + 1000)
            c_gibi = n_sek == 3 and abs(kalan - 0.30) < 1e-9
            kollar = {}
            for ad in KOLLAR:
                hucre, yort, yollar = kosu_kol(net, aday, carpan, ad, tabanlar, patika=c_gibi)
                kollar[ad] = hucre
                if c_gibi:
                    yavas[ad] = yort
                    patika[ad] = yollar
                    vektor[ad] = hucre
            test = kol_anlamli(kollar["kotu"], kollar["iyi"])
            ad_etiket = ""
            if (n_sek, round(kalan, 2)) in ((2, 0.55), (3, 0.30), (4, 0.20)):
                ad_etiket = {2: "yumusak", 3: "c", 4: "sert"}[n_sek]
            satir = {
                "n_sek": n_sek,
                "kalan": kalan,
                "siddet": float(n_sek * (1.0 - kalan)),
                "ad": ad_etiket,
            }
            for ad in KOLLAR:
                ozc = ozet_kol(kollar[ad])
                satir[f"{ad}_ortalama"] = ozc["ortalama"]
                satir[f"{ad}_medyan"] = ozc["medyan"]
                satir[f"{ad}_olasilik"] = ozc["olasilik"]
                satir[f"{ad}_yavas_fark"] = ozc["yavas_fark"]
                satir[f"{ad}_pay"] = ozc["kucuk_pay_medyan"]
            satir.update(test)
            kayit.append(satir)
            print(
                f"sok n={n_sek} k={kalan:.2f} kotu={satir['kotu_ortalama']:.2f} "
                f"iyi={satir['iyi_ortalama']:.2f} baz={satir['baz_ortalama']:.2f} "
                f"secim={satir['secim_ortalama']:.2f} anlamli={test['anlamli']}",
                flush=True,
            )
    return pd.DataFrame(kayit), vektor, yavas, patika


def grafik(tarama, tablo, patika, basamak_c, dosya: Path) -> None:
    fig, ax = plt.subplots(2, 2, figsize=(11.2, 8.2))
    kalan = list(SOK_KALAN)
    nsek = list(SOK_SEKTOR)
    mat = np.full((len(nsek), len(kalan)), np.nan)
    for _, r in tarama.iterrows():
        i = nsek.index(int(r.n_sek))
        j = int(np.argmin([abs(float(r.kalan) - k) for k in kalan]))
        mat[i, j] = r.fark_ortalama
    im = ax[0, 0].imshow(mat, origin="lower", cmap="viridis", aspect="auto")
    ax[0, 0].set_xticks(range(len(kalan)), [f"{k:.2f}" for k in kalan])
    ax[0, 0].set_yticks(range(len(nsek)), [str(n) for n in nsek])
    ax[0, 0].set_xlabel("Kalan likidite (şok sonrası)")
    ax[0, 0].set_ylabel("Şoklanan sektör sayısı")
    ax[0, 0].set_title("Dağılım, kötü − iyi")
    for i in range(len(nsek)):
        for j in range(len(kalan)):
            if np.isfinite(mat[i, j]):
                ax[0, 0].text(j, i, f"{mat[i, j]:.1f}", ha="center", va="center", color="w", fontsize=8)
    fig.colorbar(im, ax=ax[0, 0], fraction=0.046, pad=0.04)

    adlar = ["iyi", "baz", "kotu", "secim"]
    etiket = ["İyi", "Baz", "Kötü", "Seçim"]
    x = np.arange(len(adlar))
    gen = 0.36
    dag = [basamak_c["dagilim"][a]["ortalama"] for a in adlar]
    bas = [basamak_c["basamak"][a]["ortalama"] for a in adlar]
    ax[0, 1].bar(x - gen / 2, bas, width=gen, label="Basamak", color="#4C78A8")
    ax[0, 1].bar(x + gen / 2, dag, width=gen, label="Dağılım", color="#F58518")
    ax[0, 1].set_xticks(x, etiket)
    ax[0, 1].set_ylabel("Ortalama bloke periyot")
    ax[0, 1].set_title("C şoku, iki limit kuralı")
    ax[0, 1].legend(frameon=False, fontsize=8)

    dil = tablo[tablo.kilit == oz.ORTA]
    isi = np.zeros((5, 5))
    for _, r in dil.iterrows():
        isi[int(r.gecikme), int(r.banka)] = r.kalicilik_ortalama
    im2 = ax[1, 0].imshow(isi, origin="lower", cmap="viridis", aspect="auto")
    ax[1, 0].set_xticks(range(5), [str(v) for v in oz.BANKA])
    ax[1, 0].set_yticks(range(5), [str(v) for v in oz.GECIKME])
    ax[1, 0].set_xlabel("Banka çarpanı")
    ax[1, 0].set_ylabel("Gecikme α")
    ax[1, 0].set_title("Dağılım, C şoku, kilit orta")
    for i in range(5):
        for j in range(5):
            ax[1, 0].text(j, i, f"{isi[i, j]:.1f}", ha="center", va="center", color="w", fontsize=8)
    fig.colorbar(im2, ax=ax[1, 0], fraction=0.046, pad=0.04)

    for ad, yol in patika.items():
        ax[1, 1].plot(np.arange(1, oz.T + 1), yol.mean(axis=0), label=ad)
    ax[1, 1].axhline(oz.HACIM_ESIK, color="0.4", ls="--", lw=0.8, label="Eşik 0.70")
    ax[1, 1].set_ylim(0, 1.15)
    ax[1, 1].set_xlabel("Periyot")
    ax[1, 1].set_ylabel("Yeni fatura tahsil oranı")
    ax[1, 1].set_title("Dağılım, C şoku, ortalama tahsil")
    ax[1, 1].legend(frameon=False, fontsize=8)
    fig.suptitle("Heterojen limit. Sentetik ağ, TCMB/KAP yok.", fontsize=11)
    fig.tight_layout()
    fig.savefig(dosya, dpi=120)
    plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(10.4, 4.2))
    pay = np.full((5, 5), np.nan)
    yav = np.full((5, 5), np.nan)
    for _, r in dil.iterrows():
        pay[int(r.gecikme), int(r.banka)] = r.kucuk_odenmeyen_payi
        yav[int(r.gecikme), int(r.banka)] = r.yavas_kucuk - r.yavas_buyuk
    im0 = ax[0].imshow(pay, origin="lower", cmap="magma", aspect="auto", vmin=0.3, vmax=0.55)
    im1 = ax[1].imshow(yav, origin="lower", cmap="coolwarm", aspect="auto")
    for a, bas in (
        (ax[0], "Küçük alacaklının ödenmeyen payı"),
        (ax[1], "Yavaşlık: küçük − büyük"),
    ):
        a.set_xticks(range(5), [str(v) for v in oz.BANKA])
        a.set_yticks(range(5), [str(v) for v in oz.GECIKME])
        a.set_xlabel("Banka çarpanı")
        a.set_ylabel("Gecikme α")
        a.set_title(bas)
    for i in range(5):
        for j in range(5):
            if np.isfinite(pay[i, j]):
                ax[0].text(j, i, f"{pay[i, j]:.2f}", ha="center", va="center", color="w", fontsize=8)
            if np.isfinite(yav[i, j]):
                ax[1].text(j, i, f"{yav[i, j]:.1f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im0, ax=ax[0], fraction=0.046, pad=0.04)
    fig.colorbar(im1, ax=ax[1], fraction=0.046, pad=0.04)
    fig.suptitle("Dağılım, C şoku, seçim kapalı", fontsize=11)
    fig.tight_layout()
    fig.savefig(KOK / "odeme_limit_maliyet.png", dpi=120)
    plt.close(fig)


def banka4_cumle(tablo: pd.DataFrame) -> str:
    sert = tablo[(tablo.banka == 4) & (tablo.kalicilik_ortalama >= 1.0)].sort_values(
        "kalicilik_ortalama", ascending=False
    )
    if sert.empty:
        return "Çarpan 4 olan hücrelerin hepsinde ortalama kalıcılık 1'in altında."
    parca = [
        f"eşik {r.kilit_esik:.2f} / süre {int(r.kilit_sure)}, α {r.gecikme_alpha:.2f}, ortalama {r.kalicilik_ortalama:.2f}"
        for r in sert.itertuples()
    ]
    sifir_alpha = tablo[(tablo.banka == 4) & (np.isclose(tablo.gecikme_alpha, 0.0))]
    ek = ""
    if len(sifir_alpha) and float(sifir_alpha.kalicilik_ortalama.max()) < 1e-9:
        ek = " α = 0 iken çarpan 4, kilit ne olursa olsun ortalama 0."
    return (
        "Çarpan 4'te ortalaması 1 ve üstü olan hücreler: "
        + "; ".join(parca)
        + "."
        + ek
    )


def rapor_metni(sonuc, tarama, tablo) -> str:
    k = sonuc["karar"]
    e = sonuc["erisim"]

    def sinif_cumle(ad, p):
        return (
            f"{ad}: sıfır payı {p['sifir_pay']:.2f}, "
            f"pozitiflerin medyan erişimi {p['pozitif_medyan']:.2f}"
        )

    satirlar = [
        "# Ödeme zinciri, tur 3: heterojen limit",
        "",
        sonuc["uyari"],
        "",
        "## Hüküm",
        "",
        sonuc["ozet_hukum"],
        "",
        "## Limit varsayımı",
        "",
        "KAP ağı eklenmedi. Depoda firma düzeyinde KAP kenarı yok; finansal hesap matrisi kimden kime ödeme ağı değil.",
        "",
        "Birim tavan A × (aylık borç + 0,25 × boyut). A, sınıf içinde: küçük P(0)=0,50 ve değilse LogNormal(ln 0,35; 0,60); "
        "orta P(0)=0,25 ve LogNormal(ln 0,80; 0,50); büyük P(0)=0,05 ve LogNormal(ln 1,50; 0,45). Tavan 6,0'da kırpılır. "
        "Hücre çarpanı bunu çarpar. Sıfır erişim her çarpanda sıfır kalır. Çekim tohumu 20261010+7000+koşu, hücreler arası eşli. "
        "Bu dağılım ölçüm değildir.",
        "",
        f"Gerçekleşen erişim. {sinif_cumle('Küçük', e['kucuk'])}. "
        f"{sinif_cumle('Orta', e['orta'])}. {sinif_cumle('Büyük', e['buyuk'])}.",
        "",
        f"Şoksuz, basamak, çarpan 1: ortalama kalıcılık {sonuc['soksuz_basamak']:.2f}. "
        f"Şoksuz, dağılım, çarpan 1: {sonuc['soksuz_dagilim']:.2f}. "
        f"Şoksuz, dağılım, seçim açık: {sonuc['soksuz_dagilim_secim']:.2f}.",
        "",
        "## C şoku",
        "",
        f"Basamak iyi / baz / kötü / seçim: "
        f"{k['basamak_iyi']:.2f} / {k['basamak_baz']:.2f} / {k['basamak_kotu']:.2f} / {k['basamak_secim']:.2f}.",
        "",
        f"Dağılım iyi / baz / kötü / seçim: "
        f"{k['dagilim_iyi']:.2f} / {k['dagilim_baz']:.2f} / {k['dagilim_kotu']:.2f} / {k['dagilim_secim']:.2f}.",
        "",
        f"Dağılım, kötü − iyi: ortalama {k['kontrast_ortalama']:.2f}, medyan {k['kontrast_medyan']:.2f}, "
        f"tek yanlı p = {k['kontrast_p_tek']:.4g}.",
        "",
        f"Çarpan 4, 25 hücrenin en yüksek ortalaması {k['banka4_max']:.2f}. "
        f"Çarpan 0, en yüksek hücre ortalaması {k['banka0_max']:.2f}. "
        f"Çarpan 4'te ortalama aralık {k['banka4_aralik']:.2f}; çarpan 0'da {k['banka0_aralik']:.2f}.",
        "",
        banka4_cumle(tablo),
        "",
        f"Permütasyon: hücre ortalamalarının aralığı {k['perm_aralik']:.2f}, p = {k['perm_p']:.3f}.",
        "",
        f"Çarpan 0'da kötü köşe, basamak {k['basamak_kotu']:.2f}, dağılım {k['dagilim_kotu']:.2f}. "
        "Çarpan sıfır her iki kuralda da tavanı siler.",
        "",
        sonuc["secim_metin"],
        "",
        f"Seçim − baz, dağılım: ortalama fark {k['secim_ortalama_fark']:.2f}, medyan {k['secim_medyan_fark']:.2f}, "
        f"uzama p = {k['secim_p_uzama']:.4g}.",
        "",
        f"Küçük alacaklı payı, seçim − baz: medyan fark {k['pay_medyan_fark'] if k['pay_medyan_fark'] is None else float(k['pay_medyan_fark']):.4f}, n = {k['pay_n']}, "
        f"tek yanlı p = {k['pay_p']:.4g}. Kötü − baz medyan farkı {k['pay_kotu_baz']:.3f}. "
        f"Hücre medyanları {k['pay_min']:.2f}–{k['pay_max']:.2f}.",
        "",
        sonuc["sektor_metin"],
        "",
        sonuc["sira_metin"],
        "",
        "## Şok taraması, dağılım",
        "",
        sonuc["esik_metin"],
        "",
        "| Sektör | Kalan | Şiddet | İyi | Baz | Kötü | Seçim | Kötü−iyi | p | Kol |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for r in tarama.sort_values("siddet").itertuples():
        satirlar.append(
            f"| {int(r.n_sek)} | {r.kalan:.2f} | {r.siddet:.2f} | {r.iyi_ortalama:.2f} | "
            f"{r.baz_ortalama:.2f} | {r.kotu_ortalama:.2f} | {r.secim_ortalama:.2f} | "
            f"{r.fark_ortalama:.2f} | {r.p_tek:.3g} | {'evet' if r.anlamli else 'hayır'} |"
        )
    satirlar.extend([
        "",
        "## Hangi hipotez hangi koşulda",
        "",
        sonuc["hipotez_metin"],
        "",
        "## Varsayımlar",
        "",
        f"Tohum {oz.TOHUM}. Limit çekimi {TOHUM_LIMIT}+koşu. Monte Carlo {N_MC}. "
        f"Ufuk {oz.T} periyot. 204 firma, 17 sektör. Ağ tur 2 ile aynı sentetik çizim.",
        "",
        "Seçim, firmanın kendi birim tavanını 4 katına çıkarır. Sıfır çizgiyi doldurmaz. α = 0, kilit eşiği 0,50, süre 1.",
        "",
        "Bloke periyot ve pratik uzama tur 2 ile aynı: yeni fatura tahsili < 0,70 veya sıkıntılı düğüm payı ≥ 0,25; "
        "uzama medyan ≥ 2, ya da ortalama ≥ 2 ve koşuların en az dörtte biri.",
        "",
        "Tekrar: `python3 odeme_zinciri.py`. Tur 2 tabloları `odeme_hucre.csv` ve `odeme_sok_esik.csv` içinde durur.",
        "",
        "Dosyalar: `odeme_limit_hucre.csv`, `odeme_limit_sok.csv`, `odeme_limit_kosu.csv`, "
        "`odeme_limit.png`, `odeme_limit_maliyet.png`, `odeme_limit_sonuc.json`.",
        "",
    ])
    return "\n".join(satirlar)


def hukum_kur(karar, esik_metin) -> tuple[str, str, str]:
    parcalar = []
    if karar["soksuz_uyumsuz"]:
        parcalar.append(
            "Dağılım, çarpan 1 ve orta parametrede şoksuz ortalamayı 1 periyodun üstüne çıkardı. "
            "Ölçek sonuca bakılarak yeniden ayarlanmadı."
        )
    if karar["kol"]:
        parcalar.append(
            "Parametre kolu heterojen limitte de açık: C şokunda kötü köşe iyiden pratik eşiğin üstünde uzun."
        )
    else:
        parcalar.append(
            "Parametre kolu heterojen limitte pratik eşiği geçmiyor. Tur 2'deki bağımlılık basamak erişime özgü kaldı."
        )
    if karar["baskin"]:
        parcalar.append(
            "Banka baskınlığı sürüyor. Çarpan 4, sıfır çizgi kitlesi dururken de 25 hücrenin hepsinde ortalama kalıcılığı 1'in altında tutuyor."
        )
    else:
        parcalar.append(
            "Tam baskınlık kırıldı. Çarpan 4, herkese pozitif basamak verildiği tur 2'deki gibi bütün hücreleri sıfıra yapıştırmıyor. "
            "Sıfır çizgi kitlesi, yüksek çarpanın sistemi tek başına kapatmasını engelliyor."
        )
    if karar["secim_destek"]:
        secim = (
            "Seçim kuralı dağılım altında kalıcılığı uzatıyor ve küçük alacaklı payını kaydırıyor."
        )
    else:
        secim = (
            "Seçim kuralı kendi tavanını 4 kata çıkarıyor ama sıfır çizgiyi doldurmuyor. "
            "Bu, bazdan daha uzun bir sistem tıkanması ve daha büyük bir küçük-alacaklı payını birlikte üretmedi."
        )
    parcalar.append(secim)
    if karar["bedel_zayif"]:
        parcalar.append(
            "“Bedel zayıf halkaya akar” dağılımda da zayıf kaldı. Sıkı parametre ve seçim, küçük alacaklı payını 5 puan büyütmüyor."
        )
    else:
        parcalar.append(
            "Küçük alacaklı payı kötü köşede veya seçim altında baza göre en az 5 puan artıyor."
        )
    hipotez = " ".join(parcalar)
    if karar["soksuz_uyumsuz"]:
        ozet = hipotez
    elif karar["kol"] and karar["baskin"] and not karar["secim_destek"] and karar["bedel_zayif"]:
        ozet = (
            "Heterojen limit ve sıfır çizgi kitlesi, C şokunda parametre kolunu kapatmıyor ve banka baskınlığını bozmuyor. "
            "Çarpan 4 hâlâ bütün hücreleri kısa tutuyor. Seçim kuralı tıkanmayı uzatmıyor. "
            "Küçük alacaklı payı sistematik kaymıyor. KAP ağı bu turda yok."
        )
    elif karar["kol"] and not karar["baskin"] and not karar["secim_destek"]:
        ozet = (
            "Heterojen limitte parametre kolu C şokunda açık kalıyor, tam banka baskınlığı kırılıyor. "
            "Çarpan 4, sıfır çizgisi olan firmalar dururken her hücreyi sıfıra yapıştırmıyor. "
            "Tur 2'deki tam baskınlık, herkese pozitif basamak limiti verilmesine bağlıydı. "
            "Seçim kuralı sistem kalıcılığını uzatmıyor. KAP ağı bu turda yok."
        )
    else:
        ozet = hipotez
    return ozet, hipotez, esik_metin + " " + secim


def main_tur3() -> None:
    print("ag", "mc", N_MC)
    net = oz.ag_kur(oz.TOHUM)
    print("mekanizma", oz.mekanizma_kontrol(net))
    tavan, erisim = oz.limit_birimleri(net, N_MC, TOHUM_LIMIT)
    erisim_k = erisim_ozet(net, erisim)
    print("erisim", erisim_k)

    soksuz_basamak = soksuz_ortalama(net, None, False)
    soksuz_dagilim = soksuz_ortalama(net, tavan, False)
    soksuz_secim = soksuz_ortalama(net, tavan, True)
    print("soksuz", soksuz_basamak, soksuz_dagilim, soksuz_secim)
    if soksuz_basamak >= 1.0:
        raise RuntimeError(f"basamak soksuz bozuldu: {soksuz_basamak}")

    if os.environ.get("ODEME_SMOKE"):
        carpan = oz.sok_carpanlari(net, C_SOK, N_MC, oz.TOHUM + 1000)
        for ad in KOLLAR:
            hucre, _, _ = kosu_kol(net, C_SOK, carpan, ad, tavan)
            print("dagilim", ad, float(hucre[:, oz.F_KAL].mean()))
        for ad in ("iyi", "kotu"):
            hucre, _, _ = kosu_kol(net, C_SOK, carpan, ad, None)
            print("basamak", ad, float(hucre[:, oz.F_KAL].mean()))
        return

    print("C izgarasi, dagilim")
    carpan_c = oz.sok_carpanlari(net, C_SOK, N_MC, oz.TOHUM + 1000)
    blok = np.empty((5, 5, 5, N_MC, oz.N_F))
    for ia in range(5):
        for ib in range(5):
            for ic in range(5):
                hucre, _, _ = oz.kosu_hucre(
                    net, C_SOK, carpan_c, ia, ib, ic, range(N_MC), tabanlar=tavan,
                )
                blok[ia, ib, ic] = hucre
        print(f"kilit {ia} bitti", flush=True)

    print("basamak koseleri")
    basamak = {}
    for ad in KOLLAR:
        hucre, _, _ = kosu_kol(net, C_SOK, carpan_c, ad, None)
        basamak[ad] = hucre
        print(ad, float(hucre[:, oz.F_KAL].mean()), flush=True)

    eski = pd.read_csv(KOK / "odeme_hucre.csv")
    eski_kotu = float(
        eski[(eski.kilit == oz.ORTA) & (eski.gecikme == 4) & (eski.banka == 0)].iloc[0].kalicilik_ortalama
    )
    if abs(float(basamak["kotu"][:, oz.F_KAL].mean()) - eski_kotu) > 1e-6:
        raise RuntimeError(
            f"basamak kotu tur 2'den sapti: {basamak['kotu'][:, oz.F_KAL].mean()} vs {eski_kotu}"
        )
    if abs(float(blok[oz.ORTA, 4, 0, :, oz.F_KAL].mean()) - float(basamak["kotu"][:, oz.F_KAL].mean())) > 1e-6:
        raise RuntimeError("carpan 0 dagilim ile basamak kotu kosesi ayrisiyor")

    print("tarama")
    tarama, vektor, yavas, patika = tarama_yap(net, {(3, 0.30): carpan_c}, tavan)
    izgara_kotu = float(blok[oz.ORTA, 4, 0, :, oz.F_KAL].mean())
    tarama_kotu = float(tarama[(tarama.n_sek == 3) & np.isclose(tarama.kalan, 0.30)].iloc[0].kotu_ortalama)
    if abs(izgara_kotu - tarama_kotu) > 1e-6:
        raise RuntimeError(f"C sapmasi izgara {izgara_kotu} tarama {tarama_kotu}")

    duz = blok.reshape(-1, N_MC, oz.N_F)
    perm = oz.permutasyon_p(duz[:, :, oz.F_KAL], np.random.default_rng(oz.TOHUM + 7))
    kotu = blok[oz.ORTA, 4, 0]
    iyi = blok[oz.ORTA, 0, 4]
    baz = blok[oz.ORTA, oz.ORTA, oz.ORTA]
    secim = vektor["secim"]
    kontrast = kol_anlamli(kotu, iyi)

    ort = duz[:, :, oz.F_KAL].mean(axis=1).reshape(5, 5, 5)
    banka4 = ort[:, :, 4]
    banka0 = ort[:, :, 0]
    banka4_max = float(banka4.max())
    banka0_max = float(banka0.max())
    banka4_aralik = float(banka4.max() - banka4.min())
    banka0_aralik = float(banka0.max() - banka0.min())

    fark_secim = secim[:, oz.F_KAL] - baz[:, oz.F_KAL]
    secim_p = oz.wilcoxon_p(fark_secim, "greater")
    secim_uzadi = bool(anlamli_uzama(fark_secim) and secim_p < 0.05 and float(np.mean(fark_secim)) > 0)
    pay_fark = pay_vektor(secim) - pay_vektor(baz)
    gecerli = np.isfinite(pay_fark)
    if gecerli.any():
        pay_medyan = float(np.median(pay_fark[gecerli]))
        pay_p = oz.wilcoxon_p(pay_fark[gecerli], "greater")
        pay_n = int(gecerli.sum())
    else:
        pay_medyan = None
        pay_p = 1.0
        pay_n = 0
    maliyet_kaydi = bool(pay_n >= 30 and pay_medyan is not None and pay_medyan >= 0.05 and pay_p < 0.05)
    secim_destek = bool(secim_uzadi and maliyet_kaydi)
    paylar = []
    for ia in range(5):
        for ib in range(5):
            for ic in range(5):
                p = pay_vektor(blok[ia, ib, ic])
                if np.isfinite(p).any():
                    paylar.append(float(np.nanmedian(p)))
    pay_min = float(np.min(paylar)) if paylar else float("nan")
    pay_max = float(np.max(paylar)) if paylar else float("nan")
    pay_kotu_baz = float(np.nanmedian(pay_vektor(kotu) - pay_vektor(baz)))
    bedel_zayif = bool((not maliyet_kaydi) and pay_kotu_baz < 0.05)
    baskin = bool(banka4_max < 1.0 and banka0_max >= 4.0)
    kol = bool(kontrast["anlamli"] and perm["p"] < 0.05 and perm["ortalama_aralik"] >= 2.0)

    anlamlilar = tarama[tarama.anlamli].sort_values("siddet")
    if len(anlamlilar):
        esik = anlamlilar.iloc[0]
        esik_metin = (
            f"Dağılımda parametre kolu taranan pencerenin en yumuşak ucunda da "
            f"{'açık' if bool(esik.anlamli) else 'kapalı'}: "
            f"{int(esik.n_sek)} sektör, kalan likidite {esik.kalan:.2f}, "
            f"kötü−iyi ortalama {esik.fark_ortalama:.2f}. "
            f"Anlamlı şok {len(anlamlilar)} / {len(tarama)}. "
            "Yirmi karşılaştırma ham p ile duruyor."
        )
        if len(anlamlilar) == len(tarama):
            esik_metin += " Pencerenin içinde kapanış yok."
        else:
            kapali = tarama[~tarama.anlamli].sort_values("siddet")
            son = kapali.iloc[-1]
            esik_metin += (
                f" Kolun kapandığı en sert uç: {int(son.n_sek)} sektör, kalan {son.kalan:.2f}, "
                f"kötü−iyi {son.fark_ortalama:.2f}."
            )
    else:
        esik_metin = "Taranan şokların hiçbirinde kötü−iyi kontrastı pratik eşiği geçmiyor."

    def ad_satir(ad):
        r = tarama[tarama.ad == ad]
        if r.empty:
            return ad
        r = r.iloc[0]
        return (
            f"{ad}: iyi {r.iyi_ortalama:.2f}, baz {r.baz_ortalama:.2f}, "
            f"kötü {r.kotu_ortalama:.2f}, seçim {r.secim_ortalama:.2f}"
        )

    esik_metin += " Adlandırılan şoklar: " + "; ".join(ad_satir(a) for a in ("yumusak", "c", "sert")) + "."

    if secim_destek:
        secim_metin = "Seçim açıkken kalıcılık uzuyor ve ödenmeyen tutar küçük alacaklıya kayıyor."
    elif secim_uzadi:
        secim_metin = "Seçim açıkken kalıcılık uzuyor ama küçük alacaklı payı 5 puan eşiğini geçmiyor."
    else:
        secim_metin = "Seçim açık ile baz arasında pratik uzama yok."

    sektor = []
    for ad, v in yavas.items():
        sektor.extend(sektor_satir(net, ad, v))
    sektor_df = pd.DataFrame(sektor)
    baz_top = (
        sektor_df[sektor_df.kosu == "baz"].sort_values("ortalama_yavas_periyot", ascending=False).head(3)
    )
    baz_cumle = ", ".join(f"{r.sektor_ad} {r.ortalama_yavas_periyot:.1f}" for r in baz_top.itertuples())
    sektor_metin = (
        f"Dağılım, kötü köşede sektör yavaşlığı "
        f"{sektor_df[sektor_df.kosu == 'kotu']['ortalama_yavas_periyot'].min():.1f}–"
        f"{sektor_df[sektor_df.kosu == 'kotu']['ortalama_yavas_periyot'].max():.1f}. "
        f"Seçimde "
        f"{sektor_df[sektor_df.kosu == 'secim']['ortalama_yavas_periyot'].min():.1f}–"
        f"{sektor_df[sektor_df.kosu == 'secim']['ortalama_yavas_periyot'].max():.1f}. "
        f"Bazda en yavaş üç: {baz_cumle}."
    )
    sira_metin = (
        "Firma sırası, dağılım, C şoku: kötü ile baz "
        + sira_karsilastir(yavas["kotu"], yavas["baz"])
        + "; seçim ile baz "
        + sira_karsilastir(yavas["secim"], yavas["baz"])
        + "."
    )

    karar = {
        "soksuz_uyumsuz": bool(soksuz_dagilim >= 1.0),
        "basamak_iyi": float(basamak["iyi"][:, oz.F_KAL].mean()),
        "basamak_baz": float(basamak["baz"][:, oz.F_KAL].mean()),
        "basamak_kotu": float(basamak["kotu"][:, oz.F_KAL].mean()),
        "basamak_secim": float(basamak["secim"][:, oz.F_KAL].mean()),
        "dagilim_iyi": float(iyi[:, oz.F_KAL].mean()),
        "dagilim_baz": float(baz[:, oz.F_KAL].mean()),
        "dagilim_kotu": float(kotu[:, oz.F_KAL].mean()),
        "dagilim_secim": float(secim[:, oz.F_KAL].mean()),
        "kontrast_ortalama": kontrast["fark_ortalama"],
        "kontrast_medyan": kontrast["fark_medyan"],
        "kontrast_p_tek": kontrast["p_tek"],
        "banka4_max": banka4_max,
        "banka0_max": banka0_max,
        "banka4_aralik": banka4_aralik,
        "banka0_aralik": banka0_aralik,
        "perm_aralik": float(perm["ortalama_aralik"]),
        "perm_p": float(perm["p"]),
        "kol": kol,
        "baskin": baskin,
        "secim_destek": secim_destek,
        "secim_uzadi": secim_uzadi,
        "secim_ortalama_fark": float(np.mean(fark_secim)),
        "secim_medyan_fark": float(np.median(fark_secim)),
        "secim_p_uzama": secim_p,
        "maliyet_kaydi": maliyet_kaydi,
        "bedel_zayif": bedel_zayif,
        "pay_medyan_fark": pay_medyan,
        "pay_n": pay_n,
        "pay_p": pay_p,
        "pay_min": pay_min,
        "pay_max": pay_max,
        "pay_kotu_baz": pay_kotu_baz,
    }
    ozet, hipotez, _ = hukum_kur(karar, esik_metin)

    tablo = oz.hucre_tablosu(blok)
    tablo["n"] = N_MC
    tablo.to_csv(KOK / "odeme_limit_hucre.csv", index=False)
    tarama.to_csv(KOK / "odeme_limit_sok.csv", index=False)
    kosu_satir = []
    for ia in range(5):
        for ib in range(5):
            for ic in range(5):
                for s in range(N_MC):
                    r = blok[ia, ib, ic, s]
                    kosu_satir.append({
                        "kilit": ia,
                        "gecikme": ib,
                        "banka": ic,
                        "tohum": s,
                        "kalicilik": r[oz.F_KAL],
                        "kucuk_odenmeyen": r[oz.F_OD_KU],
                        "odenmeyen": r[oz.F_OD_TOP],
                        "yavas_kucuk": r[oz.F_Y_KU],
                        "yavas_buyuk": r[oz.F_Y_BU],
                    })
    pd.DataFrame(kosu_satir).to_csv(KOK / "odeme_limit_kosu.csv", index=False)
    sektor_df.to_csv(KOK / "odeme_limit_sektor.csv", index=False)

    grafik(
        tarama,
        tablo,
        patika,
        {
            "basamak": {ad: ozet_kol(basamak[ad]) for ad in KOLLAR},
            "dagilim": {ad: ozet_kol(vektor[ad]) for ad in KOLLAR},
        },
        KOK / "odeme_limit.png",
    )

    sonuc = {
        "uyari": (
            "Sentetik ağ ve varsayılmış limit dağılımı. TCMB finansal hesaplarına, KAP bildirimlerine "
            "veya bu depodaki stok-akış matrislerine kalibre edilmedi. Sayılar ölçüm değildir. "
            "KAP tabanlı ağ bu turda yok."
        ),
        "ozet_hukum": ozet,
        "hipotez_metin": hipotez,
        "esik_metin": esik_metin,
        "secim_metin": secim_metin,
        "sektor_metin": sektor_metin,
        "sira_metin": sira_metin,
        "karar": karar,
        "erisim": erisim_k,
        "soksuz_basamak": soksuz_basamak,
        "soksuz_dagilim": soksuz_dagilim,
        "soksuz_dagilim_secim": soksuz_secim,
        "n_mc": N_MC,
        "tohum": oz.TOHUM,
        "tohum_limit": TOHUM_LIMIT,
    }
    (KOK / "odeme_limit_sonuc.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2, default=oz.numpy_json) + "\n",
        encoding="utf-8",
    )
    eski_md = (KOK / "ODEME_ZINCIRI.md").read_text(encoding="utf-8")
    if ISARET in eski_md:
        tur2 = eski_md.split(ISARET, 1)[1]
    else:
        tur2 = eski_md
    (KOK / "ODEME_ZINCIRI.md").write_text(
        rapor_metni(sonuc, tarama, tablo) + ISARET + tur2,
        encoding="utf-8",
    )
    print(ozet)


if __name__ == "__main__":
    main_tur3()
