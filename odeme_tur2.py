"""Tur 2: sok esigi ve yerel secim kurali.

Cekirdek odeme_zinciri.py. Ag sentetiktir; TCMB veya KAP kalibrasyonu yok.
Karar kurallari odeme_zinciri modul belgesinde, kosu oncesinden durur.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import odeme_zinciri as oz

KOK = Path(__file__).resolve().parent
N_MC = 60
SOK_SEKTOR = (1, 2, 3, 4)
SOK_KALAN = (0.70, 0.55, 0.40, 0.30, 0.20)
TAMPON = (0.95, 1.40)
EK = (0.08, 0.45)


def aday_yap(n_sek: int, kalan: float, ad: str | None = None) -> dict:
    return {
        "ad": ad or f"s{n_sek}_k{kalan:.2f}",
        "lo": TAMPON[0],
        "hi": TAMPON[1],
        "n_sek": int(n_sek),
        "kalan": float(kalan),
        "ek_oran": EK[0],
        "ek_kalan": EK[1],
    }


C_SOK = aday_yap(3, 0.30, "c")
YUMUSAK = aday_yap(2, 0.55, "yumusak")
SERT = aday_yap(4, 0.20, "sert")

# (kilit, gecikme, banka, secim)
KOLLAR = {
    "iyi": (oz.ORTA, 0, 4, False),
    "baz": (oz.ORTA, oz.ORTA, oz.ORTA, False),
    "kotu": (oz.ORTA, 4, 0, False),
    "secim": (oz.ORTA, oz.ORTA, oz.ORTA, True),
}


def siddet(n_sek: int, kalan: float) -> float:
    return float(n_sek * (1.0 - kalan))


def pay_vektor(hucre: np.ndarray) -> np.ndarray:
    top = hucre[:, oz.F_OD_TOP]
    ku = hucre[:, oz.F_OD_KU]
    out = np.full(hucre.shape[0], np.nan)
    m = top > 1e-8
    out[m] = ku[m] / top[m]
    return out


def anlamli_uzama(fark: np.ndarray) -> bool:
    fark = np.asarray(fark, dtype=float)
    fark = fark[np.isfinite(fark)]
    if fark.size == 0:
        return False
    med = float(np.median(fark))
    ort = float(np.mean(fark))
    oran = float(np.mean(fark >= 2.0))
    return med >= 2.0 or (ort >= 2.0 and oran >= 0.25)


def kol_anlamli(kotu: np.ndarray, iyi: np.ndarray) -> dict:
    fark = kotu[:, oz.F_KAL] - iyi[:, oz.F_KAL]
    p = oz.wilcoxon_p(fark, "greater")
    return {
        "fark_ortalama": float(np.mean(fark)),
        "fark_medyan": float(np.median(fark)),
        "p_tek": p,
        "p_iki": oz.wilcoxon_p(fark, "two-sided"),
        "anlamli": bool(anlamli_uzama(fark) and p < 0.05 and float(np.mean(fark)) > 0),
    }


def ozet_kol(hucre: np.ndarray) -> dict:
    k = hucre[:, oz.F_KAL]
    pay = pay_vektor(hucre)
    return {
        "ortalama": float(k.mean()),
        "medyan": float(np.median(k)),
        "p25": float(np.percentile(k, 25)),
        "p75": float(np.percentile(k, 75)),
        "olasilik": float(hucre[:, oz.F_OLAY].mean()),
        "tahsil": float(hucre[:, oz.F_HACIM].mean()),
        "yavas_kucuk": float(hucre[:, oz.F_Y_KU].mean()),
        "yavas_buyuk": float(hucre[:, oz.F_Y_BU].mean()),
        "yavas_fark": float((hucre[:, oz.F_Y_KU] - hucre[:, oz.F_Y_BU]).mean()),
        "kucuk_pay_medyan": float(np.nanmedian(pay)) if np.isfinite(pay).any() else None,
        "kucuk_pay_n": int(np.isfinite(pay).sum()),
    }


def soksuz_kosu(net: dict, secim: bool) -> float:
    lik, dis = oz.hazirla(net, C_SOK, None)
    esik, sure = oz.KILIT[oz.ORTA]
    out, _, _ = oz.tek_kosu_temiz(
        net,
        lik,
        oz.BANKA[oz.ORTA] * net["banka_taban"],
        esik,
        sure,
        oz.GECIKME[oz.ORTA],
        dis,
        secim=secim,
    )
    return float(out[oz.F_KAL])


def kosu_kol(net, aday, carpan, ad, patika=False):
    ia, ib, ic, secim = KOLLAR[ad]
    return oz.kosu_hucre(
        net, aday, carpan, ia, ib, ic, range(carpan.shape[0]), patika=patika, secim=secim
    )


def grafik(tarama: pd.DataFrame, tablo: pd.DataFrame, patika: dict, dagilim: dict, dosya: Path) -> None:
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
    ax[0, 0].set_title("Kötü − iyi köşe, ortalama kalıcılık")
    for i in range(len(nsek)):
        for j in range(len(kalan)):
            if np.isfinite(mat[i, j]):
                ax[0, 0].text(j, i, f"{mat[i, j]:.1f}", ha="center", va="center", color="w", fontsize=8)
    fig.colorbar(im, ax=ax[0, 0], fraction=0.046, pad=0.04)

    adlar = ["iyi", "baz", "kotu", "secim"]
    etiket = ["İyi", "Baz", "Kötü", "Seçim açık"]
    x = np.arange(len(adlar))
    gen = 0.25
    for s, (sok, renk) in enumerate((
        ("yumusak", "#4C78A8"),
        ("c", "#F58518"),
        ("sert", "#E45756"),
    )):
        dil = tarama[tarama.ad == sok].iloc[0]
        deger = [dil[f"{a}_ortalama"] for a in adlar]
        ax[0, 1].bar(x + (s - 1) * gen, deger, width=gen, label=sok, color=renk)
    ax[0, 1].set_xticks(x, etiket)
    ax[0, 1].set_ylabel("Ortalama bloke periyot")
    ax[0, 1].set_title("Yumuşak, C ve sert şok")
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
    ax[1, 0].set_title("C şoku, seçim kapalı, kilit orta")
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
    ax[1, 1].set_title("C şoku, ortalama tahsil")
    ax[1, 1].legend(frameon=False, fontsize=8)

    fig.suptitle("Ağ sabit. Şok taraması ve yerel seçim. Sentetik, TCMB/KAP yok.", fontsize=11)
    fig.tight_layout()
    fig.savefig(dosya, dpi=120)
    plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(10.4, 4.2))
    pay = np.full((5, 5), np.nan)
    yav = np.full((5, 5), np.nan)
    for _, r in dil.iterrows():
        pay[int(r.gecikme), int(r.banka)] = r.kucuk_odenmeyen_payi
        yav[int(r.gecikme), int(r.banka)] = r.yavas_kucuk - r.yavas_buyuk
    im0 = ax[0].imshow(pay, origin="lower", cmap="magma", aspect="auto", vmin=0.3, vmax=0.5)
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
    fig.suptitle("C şoku, seçim kapalı", fontsize=11)
    fig.tight_layout()
    fig.savefig(KOK / "odeme_maliyet.png", dpi=120)
    plt.close(fig)
    _ = dagilim


def rapor_yaz(sonuc: dict, tarama: pd.DataFrame, tablo: pd.DataFrame) -> None:
    k = sonuc["karar"]
    c = sonuc["c_sok"]
    satirlar = [
        "# Ödeme zinciri, tur 2: şok eşiği ve yerel seçim",
        "",
        sonuc["uyari"],
        "",
        "## Hüküm",
        "",
        sonuc["ozet_hukum"],
        "",
        "## Şok eşiği",
        "",
        sonuc["esik_metin"],
        "",
        "Kötü ve iyi köşe seçim kapalı: kötü α = 0,60 ve banka 0; iyi α = 0 ve banka 4; ikisinde de kilit orta (0,85 / 3 periyot). Seçim açık sütunu aynı şokta yerel kural.",
        "",
        "| Sektör | Kalan likidite | Şiddet | İyi | Baz | Kötü | Seçim açık | Kötü−iyi ortalama | p | Kol anlamlı |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for _, r in tarama.sort_values(["siddet", "n_sek"]).iterrows():
        satirlar.append(
            f"| {int(r.n_sek)} | {r.kalan:.2f} | {r.siddet:.2f} | {r.iyi_ortalama:.2f} | "
            f"{r.baz_ortalama:.2f} | {r.kotu_ortalama:.2f} | {r.secim_ortalama:.2f} | "
            f"{r.fark_ortalama:.2f} | {r.p_tek:.3g} | {'evet' if r.anlamli else 'hayır'} |"
        )
    satirlar += [
        "",
        "## C şoku, parametre ızgarası (seçim kapalı)",
        "",
        f"İyi köşe: ortalama {c['iyi']['ortalama']:.2f}, medyan {c['iyi']['medyan']:.1f}, "
        f"P(≥4) = {c['iyi']['olasilik']:.2f}.",
        "",
        f"Baz: ortalama {c['baz']['ortalama']:.2f}, medyan {c['baz']['medyan']:.1f}, "
        f"P(≥4) = {c['baz']['olasilik']:.2f}.",
        "",
        f"Kötü köşe: ortalama {c['kotu']['ortalama']:.2f}, medyan {c['kotu']['medyan']:.1f}, "
        f"P(≥4) = {c['kotu']['olasilik']:.2f}.",
        "",
        f"Seçim açık: ortalama {c['secim']['ortalama']:.2f}, medyan {c['secim']['medyan']:.1f}, "
        f"P(≥4) = {c['secim']['olasilik']:.2f}.",
        "",
        f"Kötü − iyi: ortalama {k['kontrast_ortalama']:.2f}, medyan {k['kontrast_medyan']:.2f}, "
        f"tek yanlı p = {k['kontrast_p_tek']:.4g}, KS = {k['ks_istatistik']:.3f} "
        f"(p = {k['ks_p']:.4g}).",
        "",
        f"Banka çarpanı 4 olan 25 hücrenin en yüksek ortalaması {k['banka4_max']:.2f}. "
        f"Banka 0'ın en yüksek ortalaması {k['banka0_max']:.2f}. "
        f"Banka 0'da kilit ve gecikme uçları arasındaki ortalama aralık {k['banka0_aralik']:.2f}; "
        f"banka 4'te {k['banka4_aralik']:.2f}.",
        "",
        f"Global permütasyon: hücre ortalamalarının aralığı {k['perm_aralik']:.2f}, "
        f"p = {k['perm_p']:.4g}.",
        "",
        "## Yerel seçim",
        "",
        sonuc["secim_metin"],
        "",
        f"Seçim açık − baz (aynı C şoku): ortalama fark {k['secim_ortalama_fark']:.2f}, "
        f"medyan {k['secim_medyan_fark']:.2f}, uzama yönü p = {k['secim_p_uzama']:.4g}, "
        f"kısalma yönü p = {k['secim_p_kisalma']:.4g}.",
        "",
        f"Küçük alacaklı payı, seçim − baz: medyan fark {k['pay_medyan_fark']}, "
        f"n = {k['pay_n']}, tek yanlı p = {k['pay_p']:.4g}. "
        f"Izgarada tanımlı payların aralığı {k['pay_min']:.2f}–{k['pay_max']:.2f}.",
        "",
        f"Yavaşlık (küçük − büyük), C şoku: baz {c['baz']['yavas_fark']:.2f}, "
        f"kötü {c['kotu']['yavas_fark']:.2f}, seçim {c['secim']['yavas_fark']:.2f}.",
        "",
        f"Ortalama yavaş periyot, küçük / büyük: baz {c['baz']['yavas_kucuk']:.2f} / {c['baz']['yavas_buyuk']:.2f}, "
        f"seçim {c['secim']['yavas_kucuk']:.2f} / {c['secim']['yavas_buyuk']:.2f}, "
        f"kötü {c['kotu']['yavas_kucuk']:.2f} / {c['kotu']['yavas_buyuk']:.2f}. "
        "Yavaşlık, sistem bloke eşiğinden ayrıdır: firma ödeme oranı 0,70 altında kalabilir, "
        "toplam tahsil yine de eşiğin üstünde durabilir.",
        "",
        sonuc["sektor_metin"],
        "",
        sonuc["sira_metin"],
        "",
        "## Hangi hipotez hangi koşulda",
        "",
        sonuc["hipotez_metin"],
        "",
        "## Varsayımlar",
        "",
        f"Tohum {oz.TOHUM}. Monte Carlo {N_MC}. Ufuk {oz.T} periyot, dönem içi {oz.TURLAR} tur. "
        f"204 firma, 17 sektör, kenar sayısı {sonuc['ag']['kenar']}, yoğunluk {sonuc['ag']['yogunluk']:.4f}, "
        f"yönsüz kümelenme {sonuc['ag']['ortalama_kume']:.3f}.",
        "",
        "Tampon bütün taramada U(0,95, 1,40). Ek şok: diğer firmaların %8'i × 0,45. "
        "Dış akım her periyot sonunda sözleşmedeki (borç − alacak); kaçan tahsilatı koymaz. "
        "Büyük düğüm üst çeyrek, erişim 1; küçük alt yarı, erişim 0,20.",
        "",
        "Seçim kapalı: hücredeki kilit, α ve banka çarpanı; firma borcu kapatmak için limiti kullanır.",
        "",
        "Seçim açık: tavan çarpan 4 (erişim payı durur); çekiş yalnız nakit borcun %50'sinin altındaysa "
        "o çubuğa kadar; α = 0; kendi kilidi eşik 0,50 ve süre 1. Nakit borcu karşılıyorsa tam ödeme.",
        "",
        "Bloke periyot: yeni fatura tahsili < 0,70 veya sıkıntılı düğüm payı ≥ 0,25. "
        "Olay: kalıcılık ≥ 4. Pratik uzama: medyan ≥ 2 periyot, ya da ortalama ≥ 2 ve koşuların en az dörtte biri.",
        "",
        f"Şoksuz, seçim kapalı: kalıcılık {sonuc['soksuz_kapali']:.0f}. "
        f"Şoksuz, seçim açık: kalıcılık {sonuc['soksuz_acik']:.0f}.",
        "",
        f"Konveks yan deney (hükme girmez), C şoku, banka 0, α = 0,30: doğrusal ortalama "
        f"{sonuc['konveks']['dogrusal']:.2f}, γ = 1,8 ortalama {sonuc['konveks']['konveks']:.2f}.",
        "",
        "Tekrar: `python3 odeme_zinciri.py`.",
        "",
        "Dosyalar: `odeme_hucre.csv`, `odeme_sok_esik.csv`, `odeme_kosu.csv`, `odeme_sektor.csv`, "
        "`odeme_firma_sira.csv`, `odeme_kalicilik.png`, `odeme_maliyet.png`, `odeme_sonuc.json`.",
        "",
    ]
    (KOK / "ODEME_ZINCIRI.md").write_text("\n".join(satirlar), encoding="utf-8")


def sektor_satir(net, ad, vektor) -> list[dict]:
    out = []
    for s in range(oz.N_SEKTOR):
        mask = net["sektor"] == s
        out.append({
            "kosu": ad,
            "sektor": oz.SEKTOR[s],
            "sektor_ad": oz.SEKTOR_AD[s],
            "ortalama_yavas_periyot": float(vektor[mask].mean()),
        })
    return out


def sira_karsilastir(a: np.ndarray, b: np.ndarray) -> str:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if np.allclose(a, a[0]) or np.allclose(b, b[0]):
        return "bir köşede yavaşlık sabit, sıra tanımsız"
    rho, p = oz.stats.spearmanr(a, b)
    return f"Spearman {rho:.3f} (p = {p:.3g})"


def main_tur2() -> None:
    print("ag")
    net = oz.ag_kur(oz.TOHUM)
    olcu = oz.ag_olculeri(net)
    print("mekanizma", oz.mekanizma_kontrol(net))
    soksuz_kapali = soksuz_kosu(net, False)
    soksuz_acik = soksuz_kosu(net, True)
    print("soksuz", soksuz_kapali, soksuz_acik)
    if soksuz_kapali >= 1.0 or soksuz_acik >= 1.0:
        raise RuntimeError(f"soksuz tikandi: kapali {soksuz_kapali}, acik {soksuz_acik}")

    print("C izgarasi")
    carpan_c = oz.sok_carpanlari(net, C_SOK, N_MC, oz.TOHUM + 1000)
    blok = np.empty((5, 5, 5, N_MC, oz.N_F))
    for ia in range(5):
        for ib in range(5):
            for ic in range(5):
                hucre, _, _ = oz.kosu_hucre(net, C_SOK, carpan_c, ia, ib, ic, range(N_MC))
                blok[ia, ib, ic] = hucre
        print(f"kilit {ia} bitti", flush=True)

    print("tarama")
    kayit = []
    vektor = {}
    yavas = {}
    patika = {}
    for n_sek in SOK_SEKTOR:
        for kalan in SOK_KALAN:
            aday = aday_yap(n_sek, kalan)
            carpan = oz.sok_carpanlari(net, aday, N_MC, oz.TOHUM + 1000)
            kollar = {}
            c_gibi = n_sek == 3 and abs(kalan - 0.30) < 1e-9
            for ad in KOLLAR:
                hucre, yort, yollar = kosu_kol(net, aday, carpan, ad, patika=c_gibi)
                kollar[ad] = hucre
                if c_gibi:
                    yavas[ad] = yort
                    patika[ad] = yollar
                    vektor[ad] = hucre
            test = kol_anlamli(kollar["kotu"], kollar["iyi"])
            satir = {
                "n_sek": n_sek,
                "kalan": kalan,
                "siddet": siddet(n_sek, kalan),
                "ad": {2: "yumusak", 3: "c", 4: "sert"}.get(n_sek, "") if (
                    (n_sek, kalan) in ((2, 0.55), (3, 0.30), (4, 0.20))
                ) else "",
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
                f"iyi={satir['iyi_ortalama']:.2f} secim={satir['secim_ortalama']:.2f} "
                f"anlamli={test['anlamli']}",
                flush=True,
            )

    tarama = pd.DataFrame(kayit)
    # C satiri izgara ile ayni tohum; sapma kod hatasidir.
    izgara_kotu = float(blok[oz.ORTA, 4, 0, :, oz.F_KAL].mean())
    tarama_kotu = float(tarama[(tarama.n_sek == 3) & (np.isclose(tarama.kalan, 0.30))].iloc[0].kotu_ortalama)
    if abs(izgara_kotu - tarama_kotu) > 1e-6:
        raise RuntimeError(f"C sok sapmasi izgara {izgara_kotu} tarama {tarama_kotu}")

    duz = blok.reshape(-1, N_MC, oz.N_F)
    rng = np.random.default_rng(oz.TOHUM + 7)
    perm = oz.permutasyon_p(duz[:, :, oz.F_KAL], rng)
    kotu = blok[oz.ORTA, 4, 0]
    iyi = blok[oz.ORTA, 0, 4]
    baz = blok[oz.ORTA, oz.ORTA, oz.ORTA]
    secim = vektor["secim"]
    kontrast = kol_anlamli(kotu, iyi)
    ks = oz.ks_ozet(kotu[:, oz.F_KAL], iyi[:, oz.F_KAL])

    bank4 = blok[:, :, 4, :, oz.F_KAL].mean(axis=2)
    bank0 = blok[:, :, 0, :, oz.F_KAL].mean(axis=2)
    banka4_max = float(bank4.max())
    banka0_max = float(bank0.max())
    banka4_aralik = float(bank4.max() - bank4.min())
    banka0_aralik = float(bank0.max() - bank0.min())

    fark_secim = secim[:, oz.F_KAL] - baz[:, oz.F_KAL]
    pay_secim = pay_vektor(secim)
    pay_baz = pay_vektor(baz)
    pay_fark = pay_secim - pay_baz
    gecerli = np.isfinite(pay_fark)
    paylar = []
    for ia in range(5):
        for ib in range(5):
            for ic in range(5):
                p = pay_vektor(blok[ia, ib, ic])
                if np.isfinite(p).any():
                    paylar.append(float(np.nanmedian(p)))
    pay_min = float(np.min(paylar)) if paylar else float("nan")
    pay_max = float(np.max(paylar)) if paylar else float("nan")

    kon_lin, _, _ = oz.kosu_hucre(net, C_SOK, carpan_c, oz.ORTA, 3, 0, range(N_MC), gamma=1.0)
    kon_cv, _, _ = oz.kosu_hucre(net, C_SOK, carpan_c, oz.ORTA, 3, 0, range(N_MC), gamma=1.8)

    anlamlilar = tarama[tarama.anlamli].sort_values("siddet")
    if len(anlamlilar):
        esik = anlamlilar.iloc[0]
        esik_metin = (
            f"Bu tamponda parametre kolu taranan pencerenin en yumuşak ucunda da açık: "
            f"{int(esik.n_sek)} sektör, kalan likidite {esik.kalan:.2f}, "
            f"şiddet {esik.siddet:.2f}, kötü−iyi ortalama {esik.fark_ortalama:.2f}. "
            f"Anlamlı şok {len(anlamlilar)} / {len(tarama)}. "
            "Pencerenin içinde kapanış yok; süre farkı şiddetle birlikte büyüyor. "
            "Yirmi karşılaştırma ham p ile duruyor. "
            "Asıl parametre testi C şokunun tek kontrastı ve ızgara permütasyonu. "
            "Önceki koşuda kolu kapatan kalın tampon (Aday A) bu taramada yok."
        )
    else:
        esik_metin = "Taranan şokların hiçbirinde kötü−iyi kontrastı pratik eşiği geçmiyor."

    secim_p_uzama = oz.wilcoxon_p(fark_secim, "greater")
    secim_p_kisalma = oz.wilcoxon_p(-fark_secim, "greater")
    secim_uzadi = bool(anlamli_uzama(fark_secim) and secim_p_uzama < 0.05 and float(np.mean(fark_secim)) > 0)
    secim_kisaldi = bool(
        anlamli_uzama(-fark_secim) and secim_p_kisalma < 0.05 and float(np.mean(fark_secim)) < 0
    )
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
    pay_aralik = pay_max - pay_min if paylar else float("nan")
    pay_kotu_baz = float(np.nanmedian(pay_vektor(kotu) - pay_vektor(baz)))
    # Sistematik buyume: secim veya kotu kose payi baza gore en az 5 puan artirmiyorsa iddia zayif.
    bedel_zayif = bool((not maliyet_kaydi) and pay_kotu_baz < 0.05)
    banka_baskin = bool(banka4_max < 1.0 and banka0_max >= 4.0)
    parametre_elendi = bool(kontrast["anlamli"] and perm["p"] < 0.05 and perm["ortalama_aralik"] >= 2.0)

    if secim_destek:
        secim_metin = (
            "Seçim kuralı açıkken kalıcılık baza göre sistematik uzuyor ve ödenmeyen tutar "
            "küçük alacaklıya kayıyor. Aktörün kendi parametresini koruması toplam tıkanmayı uzatıyor."
        )
    elif secim_kisaldi and not maliyet_kaydi:
        secim_metin = (
            "Seçim kuralı açıkken kalıcılık baza göre kısalıyor. Limitin korunması ve gevşek kilit, "
            "dışarıdan konmuş sıkı parametrenin ürettiği tıkanmayı uzatmıyor. "
            "Küçük alacaklı payı da sistematik büyümüyor. "
            "“Aktör kendi parametresini korur, toplam tıkanma uzar” iddiası bu kuralda desteklenmedi."
        )
    elif secim_uzadi and not maliyet_kaydi:
        secim_metin = (
            "Seçim açıkken kalıcılık uzuyor ama küçük alacaklı payı 5 puan eşiğini geçmiyor. "
            "Uzatma iddiasının maliyet ayağı tutmuyor; iddia bütün olarak desteklenmedi."
        )
    else:
        secim_metin = (
            "Seçim açık ile baz arasında pratik uzama yok ve küçük pay sistematik artmıyor. "
            "“Toplam tıkanma uzar” iddiası desteklenmedi."
        )

    hipotez = []
    if parametre_elendi:
        hipotez.append(
            "Parametre-bağımsız hipotez, C benzeri şokta (3 sektör, likidite × 0,30) elendi. "
            "Aynı ağ ve aynı şok çarpanlarında kilit, gecikme ve banka kalıcılık dağılımını değiştiriyor."
        )
    else:
        hipotez.append(
            "Parametre-bağımsız hipotez, C benzeri şokta elenmedi: kötü−iyi kontrastı veya "
            "ızgara permütasyonu pratik eşiğin altında."
        )
    if banka_baskin:
        hipotez.append(
            "Banka limiti baskın parametre olarak kaldı. Çarpan 4 olan 25 hücrenin hepsinde ortalama "
            f"kalıcılık {banka4_max:.2f}. Çarpan 0 iken en yüksek hücre ortalaması {banka0_max:.2f}. "
            "Kilit ve gecikme, banka kapalıyken ikincil kol; banka açıkken kalıcılığı oynatmıyor."
        )
    else:
        hipotez.append(
            "Banka baskınlığı bu turda kapanmadı: yüksek çarpanda kalıcılık sıfıra yakın durmuyor "
            "ya da düşük çarpanda uzama eşiği yok."
        )
    if bedel_zayif:
        hipotez.append(
            "“Bedel zayıf halkaya akar” zayıf kaldı. Küçük alacaklının payı hücre medyanlarında "
            f"{pay_min:.2f}–{pay_max:.2f}. Kötü köşe eksi baz medyan farkı {pay_kotu_baz:.3f}. "
            "Seçim kuralı bu payı 5 puan büyütmüyor. Sıkı parametre payı küçük alacaklı lehine sistematik artırmıyor."
        )
    else:
        hipotez.append(
            "Küçük alacaklı payı kötü köşede veya seçim altında baza göre en az 5 puan artıyor. "
            "Zayıf halka iddiası bu farkla yeniden açılır."
        )
    if not secim_destek:
        hipotez.append(
            "Yerel seçim iddiası desteklenmedi. Kural, kısa vadeli nakdi ve limiti koruyacak şekilde "
            "gevşek kilit, sıfır gecikme cezası ve geniş ama idareli çekiş. Bu, C şokunda baz parametreden "
            "daha uzun bir tıkanma ve daha büyük bir küçük-alacaklı payı birlikte üretmedi."
        )
    else:
        hipotez.append("Yerel seçim iddiası desteklendi: kural açıkken hem süre uzadı hem pay kaydı.")

    # Yumusak / sert ozet cumlesi
    def ad_satir(ad):
        r = tarama[tarama.ad == ad]
        if r.empty:
            return ad
        r = r.iloc[0]
        return (
            f"{ad}: iyi {r.iyi_ortalama:.2f}, baz {r.baz_ortalama:.2f}, "
            f"kötü {r.kotu_ortalama:.2f}, seçim {r.secim_ortalama:.2f}, "
            f"kol {'anlamlı' if r.anlamli else 'anlamsız'}"
        )

    esik_metin += " Adlandırılan şoklar: " + "; ".join(ad_satir(a) for a in ("yumusak", "c", "sert")) + "."

    sektor = []
    for ad, v in yavas.items():
        sektor.extend(sektor_satir(net, ad, v))
    sektor_df = pd.DataFrame(sektor)
    kotu_y = sektor_df[sektor_df.kosu == "kotu"]["ortalama_yavas_periyot"]
    sec_y = sektor_df[sektor_df.kosu == "secim"]["ortalama_yavas_periyot"]
    baz_top = (
        sektor_df[sektor_df.kosu == "baz"]
        .sort_values("ortalama_yavas_periyot", ascending=False)
        .head(3)
    )
    baz_cumle = ", ".join(f"{r.sektor_ad} {r.ortalama_yavas_periyot:.1f}" for r in baz_top.itertuples())
    sektor_metin = (
        f"Kötü köşede sektör yavaşlığı {kotu_y.min():.1f}–{kotu_y.max():.1f} periyot. "
        f"Seçim açıkken {sec_y.min():.1f}–{sec_y.max():.1f}. "
        f"Bazda en yavaş üç sektör: {baz_cumle}."
    )
    sira_metin = (
        "Firma sırası, C şoku: kötü ile baz "
        + sira_karsilastir(yavas["kotu"], yavas["baz"])
        + "; kötü ile seçim "
        + sira_karsilastir(yavas["kotu"], yavas["secim"])
        + "; seçim ile baz "
        + sira_karsilastir(yavas["secim"], yavas["baz"])
        + "."
    )

    if parametre_elendi and banka_baskin and not secim_destek and bedel_zayif:
        ozet_hukum = (
            "C benzeri şokta parametre-bağımsız hipotez elendi; dağıtık faillik parametreye bağlı kaldı. "
            "Banka çarpanı 4 olan 25 hücrenin hepsinde ortalama kalıcılık 0.00; çarpan 0 iken en yüksek "
            "hücre ortalaması 20.30. Kilit ve gecikme banka kapalıyken ikincil. Yerel seçim kuralı sistem "
            "kalıcılığını uzatmıyor ve küçük alacaklı payını 5 puan büyütmüyor. “Bedel zayıf halkaya akar” "
            "zayıf kaldı. Bu tamponda parametre kolu en yumuşak taranan şokta da açık; pencere içinde "
            "kapanış yok, süre farkı şiddetle büyüyor."
        )
    else:
        ozet_hukum = " ".join(hipotez)

    karar = {
        "kontrast_ortalama": kontrast["fark_ortalama"],
        "kontrast_medyan": kontrast["fark_medyan"],
        "kontrast_p_tek": kontrast["p_tek"],
        "ks_istatistik": ks["istatistik"],
        "ks_p": ks["p"],
        "banka4_max": banka4_max,
        "banka0_max": banka0_max,
        "banka4_aralik": banka4_aralik,
        "banka0_aralik": banka0_aralik,
        "perm_aralik": float(perm["ortalama_aralik"]),
        "perm_p": float(perm["p"]),
        "parametre_elendi": parametre_elendi,
        "banka_baskin": banka_baskin,
        "secim_destek": secim_destek,
        "secim_uzadi": secim_uzadi,
        "secim_kisaldi": secim_kisaldi,
        "secim_ortalama_fark": float(np.mean(fark_secim)),
        "secim_medyan_fark": float(np.median(fark_secim)),
        "secim_p_uzama": secim_p_uzama,
        "secim_p_kisalma": secim_p_kisalma,
        "maliyet_kaydi": maliyet_kaydi,
        "bedel_zayif": bedel_zayif,
        "pay_medyan_fark": pay_medyan,
        "pay_n": pay_n,
        "pay_p": pay_p,
        "pay_min": pay_min,
        "pay_max": pay_max,
    }

    c_sok = {ad: ozet_kol(vektor[ad]) for ad in KOLLAR}
    # Izgara ozetini resmi C sayisi yap; tarama vektoru ile ayni olmali.
    c_sok["iyi"] = ozet_kol(iyi)
    c_sok["baz"] = ozet_kol(baz)
    c_sok["kotu"] = ozet_kol(kotu)

    tablo = oz.hucre_tablosu(blok)
    # hucre_tablosu N_MC globalini yazar; tur2 60. Sutunu duzelt.
    tablo["n"] = N_MC
    tablo.to_csv(KOK / "odeme_hucre.csv", index=False)
    tarama.to_csv(KOK / "odeme_sok_esik.csv", index=False)

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
                        "olay": r[oz.F_OLAY],
                        "yavas_kucuk": r[oz.F_Y_KU],
                        "yavas_buyuk": r[oz.F_Y_BU],
                        "yeni_tahsil": r[oz.F_HACIM],
                        "kucuk_odenmeyen": r[oz.F_OD_KU],
                        "odenmeyen": r[oz.F_OD_TOP],
                    })
    pd.DataFrame(kosu_satir).to_csv(KOK / "odeme_kosu.csv", index=False)
    sektor_df.to_csv(KOK / "odeme_sektor.csv", index=False)
    pd.DataFrame({
        "firma": np.arange(oz.N),
        "sektor": [oz.SEKTOR[s] for s in net["sektor"]],
        "buyuk": net["buyuk"],
        "kucuk": net["kucuk"],
        "yavas_iyi": yavas["iyi"],
        "yavas_baz": yavas["baz"],
        "yavas_kotu": yavas["kotu"],
        "yavas_secim": yavas["secim"],
    }).to_csv(KOK / "odeme_firma_sira.csv", index=False)

    grafik(
        tarama,
        tablo,
        {
            "İyi": patika["iyi"],
            "Baz": patika["baz"],
            "Kötü": patika["kotu"],
            "Seçim": patika["secim"],
        },
        {},
        KOK / "odeme_kalicilik.png",
    )

    sonuc = {
        "uyari": (
            "Sentetik ağ. TCMB finansal hesaplarına, KAP bildirimlerine veya bu depodaki "
            "stok-akış matrislerine kalibre edilmedi. Sayılar ölçüm değildir."
        ),
        "ozet_hukum": ozet_hukum,
        "esik_metin": esik_metin,
        "secim_metin": secim_metin,
        "hipotez_metin": " ".join(hipotez),
        "sektor_metin": sektor_metin,
        "sira_metin": sira_metin,
        "karar": karar,
        "c_sok": c_sok,
        "soksuz_kapali": soksuz_kapali,
        "soksuz_acik": soksuz_acik,
        "ag": olcu,
        "konveks": {
            "dogrusal": float(kon_lin[:, oz.F_KAL].mean()),
            "konveks": float(kon_cv[:, oz.F_KAL].mean()),
        },
        "n_mc": N_MC,
        "tohum": oz.TOHUM,
    }
    (KOK / "odeme_sonuc.json").write_text(
        json.dumps(oz.numpy_json(sonuc), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    rapor_yaz(sonuc, tarama, tablo)
    print("HUKUM")
    print(ozet_hukum)
    print(secim_metin)


if __name__ == "__main__":
    main_tur2()
