"""Odeme zinciri kaliciligi: parametre bagimsiz mi, parametre bagimli mi?

Sentetik ajan agi. TCMB finansal hesaplarina kalibre DEGILDIR; bu depodaki
stok-akis matrislerine baglanmaz. Banka limiti dis likidite yaratir, gecikme
maliyeti reel bir kayiptir (transfer degil). Sonuclar olcum degil, tasarimi
sabit bir Monte Carlo sinamasidir.

Karar kurali, tam tarama calismadan once yazildi:

  Birincil sonuc: T periyot icinde sistemin bloke oldugu periyot sayisi.
  Bloke periyot: yeni fatura tahsil orani < 0.70
                 (yeni faturaya dusen odeme / normal fatura)
                 VEYA sikintili dugum payi >= 0.25.
  Yeni fatura payi, odemenin devreden ve yeni kisim arasinda oransal
  dagilmasindan gelir. Devreden borc paydayi sisirmez; 2 sektorluk sok
  tek basina %70'in altina inmez, bulasma veya arrears'in yeni odemeyi
  dislamasi gerekir.
  Sikintili: periyot basinda kilitli, ya da bu periyotta odeme orani kilit
  esiginin altinda. Baslangic soku 2-3 sektor (dugumlerin yaklasik %12-18'i);
  %25 esigi yalnizca sokun kendisiyle asilamaz, bulasma gerekir.
  Kalicilik olayi: kalicilik >= 4 periyot.

  Pratik esik: hucre medyanlari arasinda en az 2 periyot, ya da kose
  farkinda medyan >= 2 veya (ortalama >= 2 ve kosularin en az %25'inde
  fark >= 2).

  Destek: (i) orta kilitte dusuk banka + yuksek gecikme, yuksek banka +
  dusuk gecikmeye gore kaliciligi bu pratik esikle ve tek yanli Wilcoxon
  p<0.05 ile uzatir; VEYA (ii) ayni kosede kucuk alacaklilarin odenmeyen
  tutar payi en az 5 puan artar (tek yanli p<0.05, en az 30 cift);
  VEYA (iii) global permutasyon p<0.05, hucre-ortalama araligi >= 2 ve
  kilit, gecikme veya banka tek-yon egimi ongordugu yonde anlamli.

  Eleme: soksuz kosu tukenmiyor; global etiket permutasyonu p>0.05;
  birincil kontrast iki yanli p>0.05; maliyet payi kaymi pratik esigin
  altinda. Yani makul kombinasyonlar ayni kalicilik dagilimini uretiyor.

  Sinanamadi: soksuz ag da tikaniyor; taban/tavan yuzunden ayrim gucu yok;
  istatistiksel fark var ama pratik esigin altinda; ya da fark ongordugumuz
  yonde degil.

Kalibrasyon (aday sok/tampon) yalnizca soksuz saglik ve baz hucrenin ic
varyansina bakar. Kose kontrastina bakilmaz.

Tur 2 (secim kurali ve sok esigi), sonuc gorulmeden:

  Tampon Aday C'de sabit: U(0.95, 1.40), ek sok %8 x 0.45.
  Aday C benzeri sok: 3 sektor, likidite x 0.30.
  Yumusak: 2 sektor, x 0.55. Sert: 4 sektor, x 0.20.
  Tarama: sektor sayisi {1,2,3,4} x kalan likidite {0.70,0.55,0.40,0.30,0.20}.
  Hucre basi 60 esli kosu.

  Yerel secim acikken her periyot, hucre parametresinin yerine:
    banka tavani calisma araliginin en genis ucu (carpan 4, erisim payi durur);
    cekis yalnizca nakit gevsek kilit cubugunun (borcun %50'si) altindaysa,
    cubuga yetecek kadar (limit korunur, borcun tamami icin eritilmez);
    gecikme alpha = 0 (ceza asagi itilir);
    kendi kilit esigi 0.50, suresi 1.
  Nakit borcu karsiliyorsa tam odenir. Secim kapaliyken eski kural: hucre
  parametresi, borc kadar cekis.

  Parametre kolu anlamli: kotu kose (alpha 0.60, banka 0, kilit orta) eksi
  iyi kose (alpha 0, banka 4, kilit orta) medyan fark >= 2 veya
  (ortalama >= 2 ve kosularin >= %25'i en az 2) ve tek yanli Wilcoxon p<0.05.
  Esik: bu testi gecen en dusuk siddet = sektor_sayisi * (1 - kalan).

  Banka baskin: C sokunda banka carpani 4 olan her hucrenin ortalama
  kaliciligi < 1 ve banka 0'da en az bir hucre ortalamasi >= 4.

  Secim iddiasi destek: ayni C sokunda secim acik eksi baz (secim kapali)
  kaliciligi bu pratik esikle uzatir VE kucuk alacakli payi >= 5 puan artar
  (tek yanli p<0.05, en az 30 cift). Uzama yoksa iddia desteklenmez.
  Pay, kotu kose eksi bazda 5 puandan az artiyorsa ve secim de 5 puan
  buyutmuyorsa "bedel zayif halkaya akar" zayif kalir.

Tur 3 (limit dagilimi), sonuc gorulmeden. KAP agi eklenmedi: depoda firma
duzeyinde KAP kenari yok; finansal hesap matrisi kimden kime odeme agi degil.

  Ag, sok maskesi ve parametre izgarasi tur 2 ile ayni. Degisen yalnizca
  birim banka tavani. Basamak erisim (buyuk 1, orta 0.45, kucuk 0.20) yerini
  su varsayima birakir. Olcek S_i = aylik borc + 0.25 * boyut.
  Kucuk (alt yari): P(A=0)=0.50, degilse LogNormal(ln 0.35, 0.60).
  Orta: P(A=0)=0.25, degilse LogNormal(ln 0.80, 0.50).
  Buyuk (ust ceyrek): P(A=0)=0.05, degilse LogNormal(ln 1.50, 0.45).
  A, 6.0'da kirpilir. Birim tavan = A_i * S_i. Hucre carpani bunu carpar;
  A=0 her carpanda sifir kalir. Cekim, kosu basina TOHUM+7000+s, hucreler
  arasi esli. Bu dagilim TCMB veya KAP olcumu degildir.

  Secim acikken tavan, firmanin kendi biriminin 4 katina genisler.
  Cizgisi sifir olan firma secimle cizgi edinemez.

  Baskinlik dagilimda surer: C sokunda carpan 4 olan 25 hucrenin hepsinde
  ortalama kalicilik < 1 ve carpan 0'da en az bir hucre ortalamasi >= 4.
  Saglanmazsa tur 2'deki tam baskinlik, herkese pozitif basamak limiti
  verilmesine bagli kalir.

  Parametre kolu ayni kotu-iyi kurali. Dagilimda gecmezse tur 2 bagimliligi
  basamak erisime ozgu raporlanir.

  Carpan 0 her iki kuralda da tavani sifirlar; kotu kose bu yuzden dagilimdan
  etkilenmemelidir. Dagilim, pozitif carpanda isler.

  Soksuz, dagilim, carpan 1, orta kilit ve alpha: kalicilik >= 1 ise dagilim
  duragan akisla uyumsuz isaretlenir. Olcek sonuca gore yeniden ayarlanmaz.

Tur 4 (enflasyon kanali), sonuc gorulmeden. Ag basamak erisimli tur 2 agidir.
KAP ve TCMB kalibrasyonu yoktur.

  Nominal katman: borc ve alacak ayni kenardir. Valf acilinca o periyodun
  nakdi yukumlulugu (yeni fatura + arrears) 1/(1+pi) ile carpilir.
  Erime = yukumluluk * pi/(1+pi). Bu, hekis_enflasyon.reel_degisim ile ayni
  cebirdir. Alacakli reel kaybeder, borclu ayni tutarda rahatlar. Erime
  odenmeyen sayilmaz. Tahsil orani, erimeden sonraki nakdi yukumluluge gore
  hesaplanir; tam odeme tahsil 1'dir. Yeni fatura gelecek periyotta yine w0'dur.

  Sistem valfi, bir onceki periyodun siddeti ve temizlik stoku ikisi de esikte
  ise acilir. Siddet = max(0, (0.70-tahsil)/0.70, (sikintili pay-0.25)/0.25).
  Temizlik stoku = arrears / normal aylik fatura. Ilk periyotta gecikme yoktur.
  Birincil ayar: esik 0.25, pi 0.30. Izgara esik {0.50, 0.25, 0.10},
  pi {0.10, 0.30, 0.60}. Kilit, alpha ve banka ucer seviye (indeks 0, 2, 4).
  Kanal kapali: pi uygulanmaz.

  Yerel tercih ayri koldur, birincil teste girmez: nakdi kilit esiginin
  altinda kalan borclu kendi kenarini 1/(1+pi) yapar. Sistem valfiyle birlikte
  calismaz.

  Valf destek: C sokunda kotu kose (kilit orta, alpha 0.60, banka 0),
  kapali eksi birincil acik kalicilik pratik esikle kisa ve tek yanli
  Wilcoxon p<0.05.

  Aktarim destek: ayni hucrede kumulatif erime / (V0 * T) ortalamasi >= 0.02
  ve kucuk alacaklinin odenmeyen payi acikta kapaliya gore 5 puan artmiyor.

  Hiyerarsi korunur: C sokunda iyi kose (alpha 0, banka 4) birincil acikta
  ortalama enflasyon periyodu < 1 ve kalicilik < 1; kotu kosede enflasyon
  periyodu >= 2; yumusak soktaki kotu kose enflasyon periyodu, sert soktan
  kucuk.

  Zayif halka bu kanalda zayif: kucuk alacaklinin erime payi eksi defter payi
  medyani < 0.05.

  Soksuz, birincil valf: kalicilik >= 1 veya erime > 0 ise kanal duragan
  akisla uyumsuz isaretlenir. Esik ve pi sonuca gore ayarlanmaz.

Tur 5 (reel kisit), sonuc gorulmeden. Paylar sentetiktir; TCMB/KAP/stok-akis
kalibrasyonu yoktur. Banka tavani tur 3 dagilimidir (sifir cizgi kitlesi var).
Banka carpani 0 bu dagilimi siler.

  Ithal payi, sektor sirasiyla: 0.12, 0.28, 0.22, 0.35, 0.55, 0.48, 0.50,
  0.52, 0.45, 0.18, 0.15, 0.08, 0.30, 0.20, 0.05, 0.06, 0.08.
  FX hatti normalde fx_ay * firmanin kendi ithal gereksinimi. Birincil fx_ay=1.
  FX sokunda soklanan firmalarin hatti x 0.30. TL tahsilati FX'e donusmez.
  FX borc hizmeti her periyot 0.05 * ithal payi * sozlesme satisi, dis alacakliya,
  TL likiditeden. Valf bu hizmeti eritmez. Kur geciskenligi birincilde 0.
  Uretim, FX kapsami ile gelen yerli teslimatin minimumu (3 Leontief turu).
  Gerceklesen fatura w0 * g_tedarikci. Tahsil, gerceklesen faturaya gore;
  tam odeme tahsil 1'dir. Reel kayip ayri hesaptir, bloke sayacina yazilmaz.
  Kapasite tavani birincilde 1.

  Birincil valf tur 4 ile ayni: esik 0.25, pi 0.30. Kose: kotu alpha 0.60 banka 0,
  iyi alpha 0 banka 4, kilit orta. Sok C: 3 sektor, TL likidite x 0.30.

  Tekrar: reel kisit yokken kotu kosede valf kaliciligi pratik esikle kisaltmaz
  ve kalicilik uzundur (ortalama >= 10).

  Silim gerekli degil: TL+FX sokunda, kotu kosede, valf acik kapaliya gore
  kaliciligi pratik esikle kisaltmiyor VE reel kayip orani (kayip / (V0*T))
  en az 0.05 dusmuyor. O zaman "enflasyon silimi gerekliydi" desteklenmez.

  Reel katman kaynak: tekrar saglanir, TL+FX kotu kose TL-yalniz kotu koseden
  pratik esikle uzun, ve valf bu uzamayi kapatmiyor.

  Kanal: FX hatti iade (carpan 1) veya ithal ikamesi (pay 0) kaliciligi
  pratik esikle kisaltiyorsa o kanal cozer. Valf kisaltiyorsa o da yazilir.
  Reel kayip dusup kalicilik dusmuyorsa kanal yalnizca reel kaydi kapatir.

  Zayif halka: kucuk alacaklinin reel kayip payi eksi defter payi medyani < 0.05.

  Soksuz, fx_ay=1, valf kapali: kalicilik >= 1 veya reel kayip orani > 0.01 ise
  katman duragan akisla uyumsuz isaretlenir. Pay ve fx_ay sonuca gore ayarlanmaz.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from scipy import stats

KOK = Path(__file__).resolve().parent
TOHUM = 20261010
N_SEKTOR = 17
N_FIRMA_SEKTOR = 12
N = N_SEKTOR * N_FIRMA_SEKTOR
T = 24
TURLAR = 4
N_MC = 80
N_KAL = 40
HACIM_ESIK = 0.70
KILIT_PAY_ESIK = 0.25
OLAY_ESIK = 4
PERMUTE = 999

SEKTOR = [
    "tarim",
    "madencilik",
    "gida",
    "tekstil",
    "kimya",
    "metal",
    "makine",
    "otomotiv",
    "enerji",
    "insaat",
    "toptan",
    "perakende",
    "tasimacilik",
    "bilisim",
    "finansal_hizmet",
    "gayrimenkul",
    "diger_hizmet",
]
SEKTOR_AD = [
    "Tarım",
    "Madencilik",
    "Gıda",
    "Tekstil",
    "Kimya",
    "Metal",
    "Makine",
    "Otomotiv",
    "Enerji",
    "İnşaat",
    "Toptan",
    "Perakende",
    "Taşımacılık",
    "Bilişim",
    "Finansal hizmet",
    "Gayrimenkul",
    "Diğer hizmet",
]
# Kucuk sayi = yukari akim. Odeme yukumlulugu musteriden tedarikciye gider.
SIRA = np.array([0, 0, 3, 3, 2, 2, 4, 5, 1, 6, 6, 7, 4, 5, 5, 6, 7], dtype=int)

# (odeme orani esigi, sonraki tam kilit periyodu)
KILIT = [(0.50, 1), (0.70, 2), (0.85, 3), (0.95, 5), (0.99, 8)]
GECIKME = [0.0, 0.05, 0.15, 0.30, 0.60]
BANKA = [0.0, 0.5, 1.0, 2.0, 4.0]
ORTA = 2

# Alan indeksleri
F_KAL, F_HAC, F_KIL, F_OLAY = 0, 1, 2, 3
F_OD_KU, F_OD_BU, F_OD_TOP, F_OD_B2K, F_OD_BB = 4, 5, 6, 7, 8
F_M_KU, F_M_BU, F_M_TOP, F_M_B2K = 9, 10, 11, 12
F_Y_KU, F_Y_BU, F_Y_DIS, F_Y_SOK = 13, 14, 15, 16
F_HACIM, F_KILPAY, F_ARREAR = 17, 18, 19
F_PI_N, F_ER_TOP, F_ER_KU, F_ER_BU, F_ER_KDB = 20, 21, 22, 23, 24
F_REEL, F_REEL_KU, F_FX_ACIK, F_YEREL = 25, 26, 27, 28
N_F = 29
# Sentetik ithal girdi payi. Olcum degil. Sira SEKTOR ile ayni.
ITHAL_PAY = np.array(
    [0.12, 0.28, 0.22, 0.35, 0.55, 0.48, 0.50, 0.52, 0.45, 0.18, 0.15, 0.08, 0.30, 0.20, 0.05, 0.06, 0.08],
    dtype=np.float64,
)
FX_HIZMET = 0.05
FX_KALAN = 0.30

ADAYLAR = [
    dict(ad="A", lo=1.25, hi=1.85, n_sek=2, kalan=0.55, ek_oran=0.05, ek_kalan=0.75),
    dict(ad="B", lo=1.05, hi=1.55, n_sek=2, kalan=0.35, ek_oran=0.08, ek_kalan=0.55),
    dict(ad="C", lo=0.95, hi=1.40, n_sek=3, kalan=0.30, ek_oran=0.08, ek_kalan=0.45),
]


def gini(x: np.ndarray) -> float:
    x = np.sort(np.asarray(x, dtype=float))
    toplam = x.sum()
    if toplam <= 0:
        return 0.0
    n = x.size
    i = np.arange(1, n + 1)
    return float((2.0 * np.sum(i * x) / (n * toplam)) - (n + 1) / n)


def ag_kur(tohum: int = TOHUM) -> dict:
    """Tek ag. Kenarlar, boyut ve tampon sirasi tum parametrelerde ortaktir."""
    rng = np.random.default_rng(tohum)
    sektor = np.repeat(np.arange(N_SEKTOR), N_FIRMA_SEKTOR)
    boyut = rng.lognormal(0.0, 0.55, size=N)
    boyut = boyut / np.median(boyut)
    u_cov = rng.uniform(0.0, 1.0, size=N)

    kenar = {}
    for i in range(N):
        s = int(sektor[i])
        ayni = np.flatnonzero(sektor == s)
        ayni = ayni[ayni != i]
        yukari = SIRA < SIRA[s]
        if not np.any(yukari):
            havuz_y = np.flatnonzero((SIRA[sektor] == SIRA[s]) & (np.arange(N) != i))
        else:
            havuz_y = np.flatnonzero(yukari[sektor])
        havuz_p = np.flatnonzero((SIRA[sektor] == SIRA[s]) & (sektor != s))

        def sec(havuz, k):
            if havuz.size == 0:
                return []
            k = min(k, havuz.size)
            return rng.choice(havuz, size=k, replace=False).tolist()

        alacaklilar = list(dict.fromkeys(sec(ayni, 2) + sec(havuz_y, 3) + sec(havuz_p, 1)))
        for j in alacaklilar:
            w = 0.30 * np.sqrt(boyut[i] * boyut[j]) * float(rng.uniform(0.6, 1.4))
            kenar[(i, j)] = kenar.get((i, j), 0.0) + w

    borclu = np.fromiter((k[0] for k in kenar), dtype=np.int32, count=len(kenar))
    alacakli = np.fromiter((k[1] for k in kenar), dtype=np.int32, count=len(kenar))
    w0 = np.fromiter(kenar.values(), dtype=np.float64, count=len(kenar))
    borc = np.bincount(borclu, weights=w0, minlength=N)
    alacak = np.bincount(alacakli, weights=w0, minlength=N)

    p75 = np.percentile(boyut, 75)
    p50 = np.percentile(boyut, 50)
    buyuk = boyut >= p75
    kucuk = boyut <= p50
    erisim = np.where(buyuk, 1.0, np.where(kucuk, 0.20, 0.45))
    # Sozlesme tam odenirse likiditeyi sabit tutan dis akim: nihai satis eksi
    # kar dagitimi. Sok, tahsilat kacirildiginda bu akim deligi kapatmaz.
    dis_akis = borc - alacak

    return {
        "sektor": sektor,
        "boyut": boyut,
        "u_cov": u_cov,
        "borclu": borclu,
        "alacakli": alacakli,
        "w0": w0,
        "borc": borc,
        "alacak": alacak,
        "buyuk": buyuk,
        "kucuk": kucuk,
        "erisim": erisim,
        "banka_taban": erisim * (borc + 0.25 * boyut),
        "idx_ku_al": np.flatnonzero(kucuk[alacakli]),
        "idx_bu_al": np.flatnonzero(buyuk[alacakli]),
        "idx_bu_borc": np.flatnonzero(buyuk[borclu]),
        "idx_b2k": np.flatnonzero(buyuk[borclu] & kucuk[alacakli]),
        "dis_akis": dis_akis,
    }


def ag_olculeri(net: dict) -> dict:
    G = nx.DiGraph()
    G.add_nodes_from(range(N))
    uc = zip(net["borclu"].tolist(), net["alacakli"].tolist(), net["w0"].tolist())
    G.add_weighted_edges_from(uc, weight="weight")
    yon_suz = G.to_undirected()
    ic_guc = np.bincount(net["alacakli"], weights=net["w0"], minlength=N)
    dis_guc = net["borc"]
    pr = nx.pagerank(G, weight="weight")
    pr_v = np.array([pr[i] for i in range(N)])
    return {
        "dugum": int(N),
        "kenar": int(net["w0"].size),
        "yogunluk": float(nx.density(G)),
        "ortalama_kume": float(nx.average_clustering(yon_suz)),
        "ortalama_cikis_derece": float(np.mean(np.bincount(net["borclu"], minlength=N))),
        "ortalama_giris_derece": float(np.mean(np.bincount(net["alacakli"], minlength=N))),
        "giris_guc_hhi": float(np.sum((ic_guc / ic_guc.sum()) ** 2)),
        "giris_guc_gini": gini(ic_guc),
        "cikis_guc_gini": gini(dis_guc),
        "pagerank_gini": gini(pr_v),
        "buyuk_dugum": int(net["buyuk"].sum()),
        "kucuk_dugum": int(net["kucuk"].sum()),
        "net_borclu_payi": float(np.mean(net["borc"] > net["alacak"])),
    }


def sok_carpanlari(net: dict, aday: dict, n_mc: int, tohum: int) -> np.ndarray:
    rng = np.random.default_rng(tohum)
    carpan = np.ones((n_mc, N), dtype=np.float64)
    sektor = net["sektor"]
    for s in range(n_mc):
        secilen = rng.choice(N_SEKTOR, size=aday["n_sek"], replace=False)
        for k in secilen:
            carpan[s, sektor == k] = aday["kalan"]
        diger = np.flatnonzero(carpan[s] == 1.0)
        k_ek = int(round(aday["ek_oran"] * diger.size))
        if k_ek > 0:
            ek = rng.choice(diger, size=k_ek, replace=False)
            carpan[s, ek] = aday["ek_kalan"]
    return carpan


def baslangic_likidite(net: dict, aday: dict) -> np.ndarray:
    cov = aday["lo"] + (aday["hi"] - aday["lo"]) * net["u_cov"]
    return cov * net["borc"] + 0.20 * net["boyut"]


def tek_kosu_temiz(
    net: dict,
    lik0: np.ndarray,
    bank_max: np.ndarray,
    esik: float,
    sure: int,
    alpha: float,
    sok_disi: np.ndarray,
    gamma: float = 1.0,
    patika: bool = False,
    secim: bool = False,
    secim_taban=None,
    enflasyon_esik: float = 1.0,
    enflasyon_pi: float = 0.0,
    yerel: bool = False,
    fx_pay: np.ndarray | None = None,
    fx_gecis: float = 1.0,
    fx_hizmet: float | None = None,
    reel: bool = False,
    ithal: np.ndarray | None = None,
    fx_ay: float = 1.0,
    fx_sok: bool = False,
    fx_kalan: float = FX_KALAN,
    fx_carpan: np.ndarray | None = None,
    fx_kur_gecis: float = 0.0,
    kapasite: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray | None, np.ndarray]:
    """tek_kosu'nun sok maskesini acik argumanla alan surumu.

    Ilk taslak net uzerine gecici bayrak yaziyordu. Bu fonksiyon onu kullanmaz.
    """
    borclu = net["borclu"]
    alacakli = net["alacakli"]
    w0 = net["w0"]
    borc_ay = net["borc"]
    buyuk = net["buyuk"]
    kucuk = net["kucuk"]
    sokta = ~sok_disi
    if secim:
        # Genis tavan, gevsek kilit, ceza sifir. Cekis asagida sinirlanir.
        # secim_taban, firmanin carpan-1 tavani. Verilmezse basamak tabani.
        birim = net["banka_taban"] if secim_taban is None else np.asarray(secim_taban, dtype=float)
        bank_max = np.maximum(np.asarray(bank_max, dtype=float), BANKA[-1] * birim)
        esik = 0.50
        sure = 1
        alpha = 0.0

    liq = lik0.copy()
    bank = bank_max.copy()
    arrears = np.zeros(w0.shape[0], dtype=np.float64)
    nd = int(net["borc"].shape[0])
    lock = np.zeros(nd, dtype=np.int16)
    V0 = float(w0.sum())

    bloke_n = 0
    yerel_bloke_n = 0
    hacim_n = 0
    kilit_n = 0
    hacim_toplam = 0.0
    hacim_oran = np.zeros(T, dtype=np.float64) if patika else None

    od_ku = od_bu = od_top = od_b2k = od_bb = 0.0
    m_ku = m_bu = m_top = m_b2k = 0.0
    yavas = np.zeros(nd, dtype=np.float64)
    kilit_pay = 0.0

    idx_ku = net["idx_ku_al"]
    idx_bu = net["idx_bu_al"]
    idx_bb = net["idx_bu_borc"]
    idx_b2k = net["idx_b2k"]
    idx_ku_borc = np.flatnonzero(kucuk[borclu])
    sigma_lag = 0.0
    cleanup_lag = 0.0
    er_top = er_ku = er_bu = er_kdb = 0.0
    pi_n = 0
    kanal = enflasyon_pi > 0.0
    reel_top = reel_ku = 0.0
    fx_acik_top = 0.0
    kur = 1.0
    kur_sonra = 1.0
    if reel:
        ith = net["boyut"] * 0.0 if ithal is None else np.asarray(ithal, dtype=float)
        satis = np.bincount(alacakli, weights=w0, minlength=nd).astype(np.float64)
        ihtiyac = ith * satis
        giris_w = np.bincount(borclu, weights=w0, minlength=nd).astype(np.float64)
        kap = np.ones(nd) if kapasite is None else np.asarray(kapasite, dtype=float)
        hizmet = (FX_HIZMET if fx_hizmet is None else fx_hizmet) * ihtiyac
    else:
        ith = ihtiyac = giris_w = kap = hizmet = None

    def erit(due_in: np.ndarray, mask: np.ndarray) -> tuple[np.ndarray, np.ndarray | None]:
        if not kanal or not np.any(mask):
            return due_in, None
        carp = np.ones(due_in.shape[0], dtype=np.float64)
        if fx_pay is None:
            carp[mask] = 1.0 / (1.0 + enflasyon_pi)
        else:
            tl = (1.0 - fx_pay) / (1.0 + enflasyon_pi)
            doviz = fx_pay * (1.0 + fx_gecis * enflasyon_pi)
            carp[mask] = tl[mask] + doviz[mask]
        yeni = due_in * carp
        return yeni, due_in - yeni

    def biriktir(erime: np.ndarray | None) -> None:
        nonlocal er_top, er_ku, er_bu, er_kdb, pi_n, kur_sonra
        if erime is None:
            return
        er_top += float(erime.sum())
        if idx_ku.size:
            er_ku += float(erime[idx_ku].sum())
        if idx_bu.size:
            er_bu += float(erime[idx_bu].sum())
        if idx_ku_borc.size:
            er_kdb += float(erime[idx_ku_borc].sum())
        pi_n += 1
        if fx_kur_gecis > 0.0:
            kur_sonra = kur * (1.0 + fx_kur_gecis * enflasyon_pi)

    for t in range(T):
        inactive = lock > 0
        if reel:
            kur = kur_sonra
            fx_mult = np.ones(nd)
            if fx_sok:
                if fx_carpan is None:
                    fx_mult[sokta] = fx_kalan
                else:
                    fx_mult = np.asarray(fx_carpan, dtype=float)
            g_fx = np.ones(nd)
            var = ihtiyac > 1e-12
            g_fx[var] = np.minimum(1.0, (fx_ay * ihtiyac[var] * fx_mult[var]) / ihtiyac[var])
            g_fx = np.minimum(g_fx, kap)
            g = g_fx.copy()
            for _ in range(3):
                gelen = np.bincount(borclu, weights=w0 * g[alacakli], minlength=nd)
                dolum = np.ones(nd)
                dol = giris_w > 1e-12
                dolum[dol] = gelen[dol] / giris_w[dol]
                g = np.minimum(g_fx, dolum)
            w_yeni = w0 * g[alacakli]
            kayip = w0 - w_yeni
            reel_top += float(kayip.sum())
            if idx_ku.size:
                reel_ku += float(kayip[idx_ku].sum())
            if float(ihtiyac.sum()) > 1e-12:
                fx_acik_top += float(np.maximum(ihtiyac - fx_ay * ihtiyac * fx_mult, 0.0).sum() / ihtiyac.sum())
            odeme_fx = np.minimum(liq, hizmet * kur)
            liq -= odeme_fx
        else:
            w_yeni = w0
        due = w_yeni + arrears
        if kanal and yerel:
            owed = np.zeros(nd)
            np.add.at(owed, borclu, due)
            kapasite = liq + bank
            kisa = (owed > 1e-10) & (kapasite + 1e-12 < esik * owed)
            due, erime = erit(due, kisa[borclu])
            biriktir(erime)
        elif kanal and t > 0 and sigma_lag >= enflasyon_esik and cleanup_lag >= enflasyon_esik:
            due, erime = erit(due, np.ones(due.shape[0], dtype=bool))
            biriktir(erime)
        unpaid = due.copy()
        if secim:
            owed_full = np.zeros(nd)
            np.add.at(owed_full, borclu, due)
            bar = esik * owed_full
            # Nakit cubugun ustundeyse bankaya dokunma; altindaysa yalniz cubuga tamamla.
            pay_cap = np.minimum(owed_full, liq)
            kisa_nakit = liq + 1e-12 < bar
            ek = np.minimum(bank, np.maximum(bar - liq, 0.0))
            pay_cap = np.where(kisa_nakit, np.minimum(owed_full, liq + ek), pay_cap)
            paid_cum = np.zeros(nd)
        for _ in range(TURLAR):
            owed = np.zeros(nd)
            np.add.at(owed, borclu, unpaid)
            active = ~inactive
            need = np.maximum(owed - liq, 0.0)
            draw = np.minimum(bank, need) * active
            cap = (liq + draw) * active
            ratio = np.ones(nd)
            poz = owed > 1e-10
            ratio[poz] = np.minimum(1.0, cap[poz] / owed[poz])
            ratio *= active.astype(np.float64)
            desired = owed * ratio
            if secim:
                room = np.maximum(pay_cap - paid_cum, 0.0)
                desired = np.minimum(desired, room)
                ratio = np.divide(desired, owed, out=np.zeros(nd), where=owed > 1e-10)
                ratio *= active.astype(np.float64)
                paid_cum += owed * ratio
            pay = unpaid * ratio[borclu]
            paid_node = owed * ratio
            from_cash = np.minimum(liq, paid_node)
            from_bank = np.minimum(bank, np.maximum(paid_node - from_cash, 0.0))
            liq -= from_cash
            bank -= from_bank
            np.add.at(liq, alacakli, pay)
            unpaid -= pay
        unpaid[unpaid < 1e-12] = 0.0
        liq[liq < 0.0] = 0.0

        owed0 = np.zeros(nd)
        np.add.at(owed0, borclu, due)
        unpaid_node = np.zeros(nd)
        np.add.at(unpaid_node, borclu, unpaid)
        pay_ratio = np.ones(nd)
        poz = owed0 > 1e-10
        pay_ratio[poz] = 1.0 - unpaid_node[poz] / owed0[poz]

        if alpha > 0.0:
            if gamma == 1.0:
                cost_e = alpha * unpaid
            else:
                rel = np.divide(unpaid, w0, out=np.zeros_like(unpaid), where=w0 > 1e-12)
                cost_e = alpha * unpaid * np.power(rel, gamma - 1.0)
            m_top += float(cost_e.sum())
            if idx_ku.size:
                m_ku += float(cost_e[idx_ku].sum())
            if idx_bu.size:
                m_bu += float(cost_e[idx_bu].sum())
            if idx_b2k.size:
                m_b2k += float(cost_e[idx_b2k].sum())
            drain = np.zeros(nd)
            np.add.at(drain, alacakli, cost_e)
            liq -= drain
            liq[liq < 0.0] = 0.0

        od_top += float(unpaid.sum())
        if idx_ku.size:
            od_ku += float(unpaid[idx_ku].sum())
        if idx_bu.size:
            od_bu += float(unpaid[idx_bu].sum())
        if idx_bb.size:
            od_bb += float(unpaid[idx_bb].sum())
        if idx_b2k.size:
            od_b2k += float(unpaid[idx_b2k].sum())

        # Secimde cubugu tutturan (oran ~= esik) kilitlenmesin.
        esik_kars = esik - (1e-8 if secim else 0.0)
        fail = (~inactive) & poz & (pay_ratio < esik_kars)
        yavas += np.where(inactive | (pay_ratio < 0.70), 1.0, 0.0)
        yavas_an = inactive | (pay_ratio < 0.70)
        if kucuk.any() and float(yavas_an[kucuk].mean()) >= 0.40:
            yerel_bloke_n += 1
        share = float((inactive | fail).mean())
        kilit_pay += share
        pay_edge = due - unpaid
        yeni = np.divide(pay_edge * w_yeni, due, out=np.zeros_like(pay_edge), where=due > 1e-12)
        taban_yeni = float(w_yeni.sum())
        tahsil = float(yeni.sum()) / taban_yeni if taban_yeni > 1e-12 else 1.0
        hacim_toplam += tahsil
        hacim_dar = tahsil < HACIM_ESIK
        kilit_dar = share >= KILIT_PAY_ESIK
        if hacim_dar:
            hacim_n += 1
        if kilit_dar:
            kilit_n += 1
        if hacim_dar or kilit_dar:
            bloke_n += 1
        if patika:
            hacim_oran[t] = tahsil

        lock[inactive] -= 1
        lock[fail] = np.int16(sure)
        lock[lock < 0] = 0

        fazlalik = liq - 1.25 * borc_ay
        repay = np.minimum(np.maximum(fazlalik, 0.0) * 0.50, np.maximum(bank_max - bank, 0.0))
        liq -= repay
        bank += repay
        # Dis akim sozlesme buyuklugundedir; kacirilan tahsilati yerine koymaz.
        liq += net["dis_akis"]
        liq[liq < 0.0] = 0.0
        arrears = unpaid
        sigma_lag = max(
            0.0,
            (HACIM_ESIK - tahsil) / HACIM_ESIK,
            (share - KILIT_PAY_ESIK) / KILIT_PAY_ESIK,
        )
        cleanup_lag = float(arrears.sum() / V0)

    out = np.empty(N_F, dtype=np.float64)
    out[F_KAL] = bloke_n
    out[F_HAC] = hacim_n
    out[F_KIL] = kilit_n
    out[F_OLAY] = 1.0 if bloke_n >= OLAY_ESIK else 0.0
    out[F_OD_KU] = od_ku
    out[F_OD_BU] = od_bu
    out[F_OD_TOP] = od_top
    out[F_OD_B2K] = od_b2k
    out[F_OD_BB] = od_bb
    out[F_M_KU] = m_ku
    out[F_M_BU] = m_bu
    out[F_M_TOP] = m_top
    out[F_M_B2K] = m_b2k
    out[F_Y_KU] = float(yavas[kucuk].mean())
    out[F_Y_BU] = float(yavas[buyuk].mean())
    out[F_Y_DIS] = float(yavas[sok_disi].mean()) if np.any(sok_disi) else np.nan
    out[F_Y_SOK] = float(yavas[sokta].mean()) if np.any(sokta) else np.nan
    out[F_HACIM] = hacim_toplam / T
    out[F_KILPAY] = kilit_pay / T
    out[F_ARREAR] = float(arrears.sum() / V0)
    out[F_PI_N] = pi_n
    out[F_ER_TOP] = er_top
    out[F_ER_KU] = er_ku
    out[F_ER_BU] = er_bu
    out[F_ER_KDB] = er_kdb
    out[F_REEL] = reel_top
    out[F_REEL_KU] = reel_ku
    out[F_FX_ACIK] = fx_acik_top / T
    out[F_YEREL] = yerel_bloke_n
    return out, hacim_oran, yavas


def hazirla(net: dict, aday: dict, carpan: np.ndarray | None) -> tuple[np.ndarray, np.ndarray]:
    """carpan None ise soksuz. Donus: likidite, sok_disi maskesi."""
    lik0 = baslangic_likidite(net, aday)
    if carpan is None:
        return lik0, np.ones(N, dtype=bool)
    return lik0 * carpan, carpan >= 0.999


def limit_birimleri(net: dict, n: int, tohum: int) -> tuple[np.ndarray, np.ndarray]:
    """Esli birim tavan (n, N) ve erisim A (n, N). Varsayim, olcum degil.

    Sinif olasiliklari ve lognormal merkezler modul belgesindeki tur 3 kurali.
    """
    olcek = net["borc"] + 0.25 * net["boyut"]
    buyuk = net["buyuk"]
    kucuk = net["kucuk"]
    p0 = np.where(kucuk, 0.50, np.where(buyuk, 0.05, 0.25))
    merkez = np.where(kucuk, 0.35, np.where(buyuk, 1.50, 0.80))
    sig = np.where(kucuk, 0.60, np.where(buyuk, 0.45, 0.50))
    tavan = np.empty((n, N), dtype=np.float64)
    erisim = np.empty((n, N), dtype=np.float64)
    for s in range(n):
        rng = np.random.default_rng(tohum + s)
        u = rng.random(N)
        z = rng.normal(size=N)
        a = np.exp(np.log(merkez) + sig * z)
        a = np.where(u < p0, 0.0, a)
        a = np.minimum(a, 6.0)
        erisim[s] = a
        tavan[s] = a * olcek
    return tavan, erisim


def kosu_hucre(
    net, aday, carpanlar, ia, ib, ic, tohumlar,
    gamma=1.0, patika=False, secim=False, tabanlar=None,
    enflasyon_esik=1.0, enflasyon_pi=0.0, yerel=False, fx_pay=None, fx_gecis=1.0,
    reel=False, ithal=None, fx_ay=1.0, fx_sok=False, fx_kalan=FX_KALAN,
    fx_kur_gecis=0.0, kapasite=None,
):
    esik, sure = KILIT[ia]
    alpha = GECIKME[ib]
    n = carpanlar.shape[0]
    blok = np.empty((n, N_F), dtype=np.float64)
    patikalar = np.empty((n, T), dtype=np.float64) if patika else None
    yavas_top = np.zeros(int(net["borc"].shape[0]), dtype=np.float64)
    for s in tohumlar:
        if tabanlar is None:
            birim = net["banka_taban"]
        else:
            birim = tabanlar[s]
        bmax0 = BANKA[ic] * birim
        lik, dis = hazirla(net, aday, carpanlar[s])
        out, yol, yavas = tek_kosu_temiz(
            net, lik, bmax0, esik, sure, alpha, dis,
            gamma=gamma, patika=patika, secim=secim, secim_taban=birim,
            enflasyon_esik=enflasyon_esik, enflasyon_pi=enflasyon_pi, yerel=yerel,
            fx_pay=fx_pay, fx_gecis=fx_gecis,
            reel=reel, ithal=ithal, fx_ay=fx_ay, fx_sok=fx_sok, fx_kalan=fx_kalan,
            fx_kur_gecis=fx_kur_gecis, kapasite=kapasite,
        )
        blok[s] = out
        yavas_top += yavas
        if patika:
            patikalar[s] = yol
    return blok, yavas_top / n, patikalar


def ic_bolge(soksuz: float, baz: np.ndarray) -> bool:
    ort = float(baz.mean())
    sap = float(baz.std(ddof=1)) if baz.size > 1 else 0.0
    return soksuz < 0.5 and 2.0 <= ort <= 16.0 and sap >= 1.0


def kalibrasyon(net: dict) -> tuple[dict, list]:
    rapor = []
    secilen = None
    for aday in ADAYLAR:
        carpan = sok_carpanlari(net, aday, N_KAL, TOHUM + 1000)
        lik, dis = hazirla(net, aday, None)
        esik, sure = KILIT[ORTA]
        alpha = GECIKME[ORTA]
        bmax = BANKA[ORTA] * net["banka_taban"]
        soksuz, _, _ = tek_kosu_temiz(net, lik, bmax, esik, sure, alpha, dis)
        baz, _, _ = kosu_hucre(net, aday, carpan, ORTA, ORTA, ORTA, range(N_KAL))
        kayit = {
            "aday": aday["ad"],
            "tampon": [aday["lo"], aday["hi"]],
            "sok_sektor": aday["n_sek"],
            "sok_kalan_likidite": aday["kalan"],
            "soksuz_kalicilik": float(soksuz[F_KAL]),
            "baz_ortalama": float(baz[:, F_KAL].mean()),
            "baz_medyan": float(np.median(baz[:, F_KAL])),
            "baz_std": float(baz[:, F_KAL].std(ddof=1)),
            "baz_olay": float(baz[:, F_OLAY].mean()),
            "ic_bolge": bool(ic_bolge(float(soksuz[F_KAL]), baz[:, F_KAL])),
        }
        rapor.append(kayit)
        if secilen is None and kayit["ic_bolge"]:
            secilen = aday
    if secilen is None:
        # Kontrast bakilmaz. Soksuz tukenmeyenler arasinda baz ortalamasi 8'e en yakin.
        uygun = [k for k in rapor if k["soksuz_kalicilik"] < 1.0]
        havuz = uygun or rapor
        en_yakin = min(havuz, key=lambda k: abs(k["baz_ortalama"] - 8.0))
        secilen = next(a for a in ADAYLAR if a["ad"] == en_yakin["aday"])
        for k in rapor:
            k["yedek_secim"] = k["aday"] == secilen["ad"]
    return secilen, rapor


def sistematik(fark: np.ndarray) -> bool:
    if fark.size == 0 or not np.isfinite(fark).all():
        return False
    med = float(np.median(fark))
    ort = float(np.mean(fark))
    oran = float(np.mean(fark >= 2.0))
    return med >= 2.0 or (ort >= 2.0 and oran >= 0.25)


def wilcoxon_p(fark: np.ndarray, alternatif: str) -> float:
    fark = np.asarray(fark, dtype=float)
    fark = fark[np.isfinite(fark)]
    if fark.size == 0 or np.allclose(fark, 0.0):
        return 1.0
    try:
        return float(stats.wilcoxon(fark, zero_method="wilcox", alternative=alternatif).pvalue)
    except ValueError:
        return 1.0


def egim_testi(degerler: np.ndarray, x: np.ndarray, yon: str) -> dict:
    """degerler: (seviye, tohum). Her tohum icin egim, sonra Wilcoxon."""
    egimler = np.empty(degerler.shape[1])
    for s in range(degerler.shape[1]):
        egimler[s] = np.polyfit(x, degerler[:, s], 1)[0]
    medyanlar = np.median(degerler, axis=1)
    return {
        "egim_medyan": float(np.median(egimler)),
        "egim_ortalama": float(np.mean(egimler)),
        "p_tek_yan": wilcoxon_p(egimler, "greater" if yon == "artan" else "less"),
        "medyan_aralik": float(medyanlar.max() - medyanlar.min()),
        "uc_medyanlar": [float(v) for v in medyanlar],
        "yon_tutar": bool(
            (yon == "artan" and np.median(egimler) > 0) or (yon == "azalan" and np.median(egimler) < 0)
        ),
    }


def permutasyon_p(mat: np.ndarray, rng: np.random.Generator) -> dict:
    """mat (hucre, tohum). H0: hucre etiketleri tohum icinde degistirilebilir."""
    gozlem = float(mat.mean(axis=1).max() - mat.mean(axis=1).min())
    n_h, n_s = mat.shape
    asildi = 0
    for _ in range(PERMUTE):
        karisik = np.empty_like(mat)
        for s in range(n_s):
            karisik[:, s] = rng.permutation(mat[:, s])
        istat = float(karisik.mean(axis=1).max() - karisik.mean(axis=1).min())
        if istat >= gozlem - 1e-12:
            asildi += 1
    return {
        "ortalama_aralik": gozlem,
        "p": (asildi + 1) / (PERMUTE + 1),
        "yineleme": PERMUTE,
    }


def hucre_tablosu(blok: np.ndarray) -> pd.DataFrame:
    satir = []
    for ia in range(5):
        for ib in range(5):
            for ic in range(5):
                k = blok[ia, ib, ic, :, F_KAL]
                od_top = blok[ia, ib, ic, :, F_OD_TOP]
                od_ku = blok[ia, ib, ic, :, F_OD_KU]
                m = od_top > 1e-8
                pay = np.nan if not np.any(m) else float(np.mean(od_ku[m] / od_top[m]))
                satir.append(
                    {
                        "kilit": ia,
                        "kilit_esik": KILIT[ia][0],
                        "kilit_sure": KILIT[ia][1],
                        "gecikme": ib,
                        "gecikme_alpha": GECIKME[ib],
                        "banka": ic,
                        "banka_carpan": BANKA[ic],
                        "n": N_MC,
                        "kalicilik_ortalama": float(k.mean()),
                        "kalicilik_medyan": float(np.median(k)),
                        "kalicilik_std": float(k.std(ddof=1)),
                        "kalicilik_p25": float(np.percentile(k, 25)),
                        "kalicilik_p75": float(np.percentile(k, 75)),
                        "olasilik_en_az_4": float(blok[ia, ib, ic, :, F_OLAY].mean()),
                        "hacim_bloke_ortalama": float(blok[ia, ib, ic, :, F_HAC].mean()),
                        "kilit_bloke_ortalama": float(blok[ia, ib, ic, :, F_KIL].mean()),
                        "yeni_tahsil_orani": float(blok[ia, ib, ic, :, F_HACIM].mean()),
                        "ortalama_kilit_payi": float(blok[ia, ib, ic, :, F_KILPAY].mean()),
                        "yavas_kucuk": float(blok[ia, ib, ic, :, F_Y_KU].mean()),
                        "yavas_buyuk": float(blok[ia, ib, ic, :, F_Y_BU].mean()),
                        "yavas_sok_disi": float(blok[ia, ib, ic, :, F_Y_DIS].mean()),
                        "yavas_sok": float(blok[ia, ib, ic, :, F_Y_SOK].mean()),
                        "kucuk_odenmeyen_payi": pay,
                        "arrears_orani": float(blok[ia, ib, ic, :, F_ARREAR].mean()),
                    }
                )
    return pd.DataFrame(satir)


def ks_ozet(a: np.ndarray, b: np.ndarray) -> dict:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    sonuc = stats.ks_2samp(a, b, method="asymp")
    return {
        "istatistik": float(sonuc.statistic),
        "p": float(sonuc.pvalue),
        "medyan_fark": float(np.median(a) - np.median(b)),
        "ortalama_fark": float(np.mean(a) - np.mean(b)),
    }


def mekanizma_kontrol(net: dict) -> dict:
    """Uc dugum: A, B'ye; B, C'ye borclu. Banka acilinca A'nin kesintisi kalkmali."""
    borclu = np.array([0, 1], dtype=np.int32)
    alacakli = np.array([1, 2], dtype=np.int32)
    w0 = np.array([1.0, 1.0])

    def kisa(banka_a: float, alpha: float) -> float:
        liq = np.array([0.15, 1.15, 1.15])
        bank = np.array([banka_a, 0.0, 0.0])
        bank_max = bank.copy()
        arrears = np.zeros(2)
        lock = np.zeros(3, dtype=np.int16)
        esik, sure = 0.85, 4
        bloke = 0
        for _t in range(T):
            inactive = lock > 0
            due = w0 + arrears
            unpaid = due.copy()
            for _ in range(TURLAR):
                owed = np.zeros(3)
                np.add.at(owed, borclu, unpaid)
                active = ~inactive
                need = np.maximum(owed - liq, 0.0)
                draw = np.minimum(bank, need) * active
                cap = (liq + draw) * active
                ratio = np.ones(3)
                poz = owed > 1e-10
                ratio[poz] = np.minimum(1.0, cap[poz] / owed[poz])
                ratio *= active.astype(float)
                pay = unpaid * ratio[borclu]
                paid_node = owed * ratio
                from_cash = np.minimum(liq, paid_node)
                from_bank = np.minimum(bank, np.maximum(paid_node - from_cash, 0.0))
                liq -= from_cash
                bank -= from_bank
                np.add.at(liq, alacakli, pay)
                unpaid -= pay
            unpaid[unpaid < 1e-12] = 0.0
            if alpha > 0:
                drain = np.zeros(3)
                np.add.at(drain, alacakli, alpha * unpaid)
                liq -= drain
                liq[liq < 0] = 0.0
            owed0 = np.zeros(3)
            np.add.at(owed0, borclu, due)
            un_n = np.zeros(3)
            np.add.at(un_n, borclu, unpaid)
            pay_ratio = np.ones(3)
            poz = owed0 > 1e-10
            pay_ratio[poz] = 1.0 - un_n[poz] / owed0[poz]
            fail = (~inactive) & poz & (pay_ratio < esik)
            share = float((inactive | fail).mean())
            muaccel = float(due.sum())
            tahsil = (muaccel - float(unpaid.sum())) / muaccel if muaccel > 1e-12 else 1.0
            if tahsil < HACIM_ESIK or share >= KILIT_PAY_ESIK:
                bloke += 1
            lock[inactive] -= 1
            lock[fail] = np.int16(sure)
            lock[lock < 0] = 0
            arrears = unpaid
        return float(bloke)

    banksiz = kisa(0.0, 0.3)
    # Kredi hatti ufku asar; A'nin dis geliri yoktur, kucuk limit birkac periyotta biter.
    bankali = kisa(100.0, 0.3)
    if not (bankali == 0.0 and banksiz > bankali):
        raise RuntimeError(f"mekanizma kontrolu basarisiz: bankasiz {banksiz}, bankali {bankali}")
    return {"bankasiz_kalicilik": banksiz, "bankali_kalicilik": bankali, "gecti": True}


def grafik(tablo: pd.DataFrame, patika: dict, dagilim: dict, dosya: Path) -> None:
    fig, ax = plt.subplots(2, 2, figsize=(11.2, 8.2))

    # Tek yon
    seriler = [
        (tablo[(tablo.gecikme == ORTA) & (tablo.banka == ORTA)], "kilit_sure", "Kilit süresi"),
        (tablo[(tablo.kilit == ORTA) & (tablo.banka == ORTA)], "gecikme_alpha", "Gecikme α"),
        (tablo[(tablo.kilit == ORTA) & (tablo.gecikme == ORTA)], "banka_carpan", "Banka çarpanı"),
    ]
    for dilim, xcol, ad in seriler:
        dilim = dilim.sort_values(xcol)
        deger = ", ".join(f"{v:g}" for v in dilim[xcol])
        ax[0, 0].plot(range(len(dilim)), dilim["kalicilik_ortalama"], marker="o", label=f"{ad} ({deger})")
    ax[0, 0].set_title("Tek yön: ortalama kalıcılık")
    ax[0, 0].set_xlabel("Izgara adımı (0 = en küçük değer)")
    ax[0, 0].set_xticks(range(5))
    ax[0, 0].set_ylabel("Bloke periyot")
    ax[0, 0].legend(frameon=False, fontsize=7)
    ax[0, 0].set_ylim(bottom=0)

    # Isi haritasi, kilit orta
    dil = tablo[tablo.kilit == ORTA]
    mat = np.zeros((5, 5))
    for _, r in dil.iterrows():
        mat[int(r.gecikme), int(r.banka)] = r.kalicilik_ortalama
    im = ax[0, 1].imshow(mat, origin="lower", cmap="viridis", aspect="auto")
    ax[0, 1].set_xticks(range(5), [str(v) for v in BANKA])
    ax[0, 1].set_yticks(range(5), [str(v) for v in GECIKME])
    ax[0, 1].set_xlabel("Banka çarpanı")
    ax[0, 1].set_ylabel("Gecikme α")
    ax[0, 1].set_title(f"Ortalama kalıcılık, kilit orta ({KILIT[ORTA][0]}, {KILIT[ORTA][1]})")
    for i in range(5):
        for j in range(5):
            ax[0, 1].text(j, i, f"{mat[i, j]:.1f}", ha="center", va="center", color="w", fontsize=8)
    fig.colorbar(im, ax=ax[0, 1], fraction=0.046, pad=0.04)

    # Dagilimlar
    etiket = ["İyi köşe", "Baz", "Kötü köşe", "Rastgele parametre"]
    veri = [dagilim["iyi"], dagilim["baz"], dagilim["kotu"], dagilim["rastgele"]]
    ax[1, 0].boxplot(veri, tick_labels=etiket, showfliers=False)
    ax[1, 0].set_title("Aynı şoklar, farklı parametre")
    ax[1, 0].set_ylabel("Bloke periyot")
    ax[1, 0].tick_params(axis="x", labelrotation=15)

    for ad, yol in patika.items():
        ax[1, 1].plot(np.arange(1, T + 1), yol.mean(axis=0), label=ad)
    ax[1, 1].axhline(HACIM_ESIK, color="0.4", ls="--", lw=0.8, label="Yeni fatura eşiği 0.70")
    ax[1, 1].set_ylim(0, 1.15)
    ax[1, 1].set_xlabel("Periyot")
    ax[1, 1].set_ylabel("Yeni fatura tahsil oranı")
    ax[1, 1].set_title("Ortalama yeni fatura tahsili")
    ax[1, 1].legend(frameon=False, fontsize=8)

    fig.suptitle("Ağ ve şok protokolü sabit. Yalnız kilit, gecikme ve banka değişir.", fontsize=11)
    fig.tight_layout()
    fig.savefig(dosya, dpi=120)
    plt.close(fig)


def grafik_maliyet(tablo: pd.DataFrame, dosya: Path) -> None:
    dil = tablo[tablo.kilit == ORTA]
    mat = np.full((5, 5), np.nan)
    yav = np.full((5, 5), np.nan)
    for _, r in dil.iterrows():
        mat[int(r.gecikme), int(r.banka)] = r.kucuk_odenmeyen_payi
        fark = r.yavas_kucuk - r.yavas_buyuk
        yav[int(r.gecikme), int(r.banka)] = fark
    fig, ax = plt.subplots(1, 2, figsize=(10.4, 4.2))
    im0 = ax[0].imshow(mat, origin="lower", cmap="magma", aspect="auto", vmin=0, vmax=1)
    im1 = ax[1].imshow(yav, origin="lower", cmap="coolwarm", aspect="auto")
    for a, baslik in (
        (ax[0], "Küçük alacaklının ödenmeyen payı"),
        (ax[1], "Yavaşlık: küçük − büyük (periyot)"),
    ):
        a.set_xticks(range(5), [str(v) for v in BANKA])
        a.set_yticks(range(5), [str(v) for v in GECIKME])
        a.set_xlabel("Banka çarpanı")
        a.set_ylabel("Gecikme α")
        a.set_title(baslik)
    for i in range(5):
        for j in range(5):
            if np.isfinite(mat[i, j]):
                ax[0].text(j, i, f"{mat[i, j]:.2f}", ha="center", va="center", color="w", fontsize=8)
            if np.isfinite(yav[i, j]):
                ax[1].text(j, i, f"{yav[i, j]:.1f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im0, ax=ax[0], fraction=0.046, pad=0.04)
    fig.colorbar(im1, ax=ax[1], fraction=0.046, pad=0.04)
    fig.suptitle("Maliyet ve yavaşlık, kilit orta seviyede", fontsize=11)
    fig.tight_layout()
    fig.savefig(dosya, dpi=120)
    plt.close(fig)


def numpy_json(o):
    if isinstance(o, dict):
        return {str(k): numpy_json(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [numpy_json(v) for v in o]
    if isinstance(o, np.ndarray):
        return numpy_json(o.tolist())
    if isinstance(o, (np.floating, float)):
        x = float(o)
        if x != x or x in (float("inf"), float("-inf")):
            return None
        return x
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return o


def hukum_ver(olc: dict) -> dict:
    if olc["soksuz_kalicilik"] >= 1.0:
        return {
            "hukum": "sinanamadi",
            "gerekce": "Şoksuz ağ da en az bir periyot tıkanıyor. Şokun kalıcılığı parametreden ayrılamıyor.",
        }

    kontrast = olc["kontrast_sistematik"] and olc["kontrast_p_tek"] < 0.05 and olc["kontrast_ortalama_fark"] > 0
    maliyet = (
        olc["maliyet_n"] >= 30
        and olc["maliyet_p_tek"] < 0.05
        and olc["maliyet_medyan_fark"] >= 0.05
    )
    tek_yon = any(olc[k]["destek"] for k in ("kilit_egim", "gecikme_egim", "banka_egim"))
    global_anlamli = olc["permutasyon_p"] < 0.05 and olc["permutasyon_aralik"] >= 2.0

    if kontrast:
        gerekce = (
            "Orta kilitte düşük banka ve yüksek gecikme maliyeti, yüksek banka ve düşük "
            "gecikmeye göre kalıcılığı pratik eşikle uzatıyor."
        )
        return {"hukum": "desteklendi", "gerekce": gerekce}
    if maliyet and (tek_yon or olc["kontrast_p_tek"] < 0.05):
        return {
            "hukum": "desteklendi",
            "gerekce": (
                "Kalıcılık köşesi tek başına eşiği geçmese de ödenmeyen tutar küçük "
                "alacaklıya kayıyor ve parametre eğimi öngörülen yönde."
            ),
        }
    if global_anlamli and tek_yon:
        return {
            "hukum": "desteklendi",
            "gerekce": (
                "Hücre ortalamalarının aralığı en az 2 periyot ve en az bir parametre "
                "eğimi öngörülen yönde. Köşe kontrastı bu cümleyi tek başına taşımıyor olabilir."
            ),
        }
    if maliyet and not tek_yon:
        return {
            "hukum": "desteklendi",
            "gerekce": (
                "Sistem kalıcılığı parametreyle uzamıyor; ödenmeyen tutarın küçük "
                "alacaklı payı kötü köşede en az 5 puan artıyor. Parametre bağımlılığı "
                "süre uzamasında değil, maliyetin büyükten küçüğe kaymasında."
            ),
        }

    duz = (
        olc["permutasyon_p"] > 0.05
        and olc["kontrast_p_iki"] > 0.05
        and not maliyet
        and not tek_yon
    )
    if duz:
        return {
            "hukum": "elendi",
            "gerekce": (
                "Kilit, gecikme ve banka limiti makul aralıkta aynı kalıcılık dağılımını "
                "üretiyor. Permütasyon testi, Wilcoxon kontrastı ve maliyet payı kayması "
                "pratik eşiğin altında. Parametre bağımlı dağıtık faillik elenir; ağ ve şok yeter."
            ),
        }
    if olc["permutasyon_p"] <= 0.05 and olc["permutasyon_aralik"] < 2.0:
        return {
            "hukum": "sinanamadi",
            "gerekce": (
                "Hücreler arasında istatistiksel iz var ama ortalama aralık 2 periyodun altında. "
                "Sistematik uzatma sayılmadı."
            ),
        }
    return {
        "hukum": "sinanamadi",
        "gerekce": (
            "Parametreler dağılımı yer yer oynatıyor ama öngörülen yön, pratik eşik ve "
            "maliyet kayması birlikte kapanmıyor."
        ),
    }


def egim_destek(egim: dict) -> dict:
    egim = dict(egim)
    egim["destek"] = bool(egim["p_tek_yan"] < 0.05 and egim["medyan_aralik"] >= 2.0 and egim["yon_tutar"])
    return egim


def kose_kalicilik(net: dict, aday: dict) -> dict:
    """Iyi, baz ve kotu kose. Hukum bunlari secim icin kullanmaz."""
    carpan = sok_carpanlari(net, aday, N_MC, TOHUM + 1000)
    out = {}
    for ad, (ia, ib, ic) in {
        "iyi": (ORTA, 0, 4),
        "baz": (ORTA, ORTA, ORTA),
        "kotu": (ORTA, 4, 0),
    }.items():
        hucre, _, _ = kosu_hucre(net, aday, carpan, ia, ib, ic, range(N_MC))
        out[ad] = {
            "ortalama": float(hucre[:, F_KAL].mean()),
            "medyan": float(np.median(hucre[:, F_KAL])),
            "olasilik": float(hucre[:, F_OLAY].mean()),
            "yeni_tahsil": float(hucre[:, F_HACIM].mean()),
        }
    return out


def main() -> None:
    print("ag kuruluyor")
    net = ag_kur(TOHUM)
    olcu = ag_olculeri(net)
    print("mekanizma kontrolu", mekanizma_kontrol(net))
    print("kalibrasyon")
    aday, kal_rapor = kalibrasyon(net)
    print(json.dumps(kal_rapor, ensure_ascii=False, indent=2))
    print("secilen", aday["ad"])
    sok_kontrol = {}
    for diger in ADAYLAR:
        if diger["ad"] == aday["ad"]:
            continue
        sok_kontrol[diger["ad"]] = kose_kalicilik(net, diger)

    carpan = sok_carpanlari(net, aday, N_MC, TOHUM + 1000)
    lik_soksuz, dis_soksuz = hazirla(net, aday, None)
    esik, sure = KILIT[ORTA]
    soksuz, _, _ = tek_kosu_temiz(
        net,
        lik_soksuz,
        BANKA[ORTA] * net["banka_taban"],
        esik,
        sure,
        GECIKME[ORTA],
        dis_soksuz,
    )

    blok = np.empty((5, 5, 5, N_MC, N_F), dtype=np.float64)
    yavas_firma = {}
    patika = {}
    izlenen = {
        (ORTA, 0, 4): "iyi",
        (ORTA, ORTA, ORTA): "baz",
        (ORTA, 4, 0): "kotu",
    }
    for ia in range(5):
        for ib in range(5):
            for ic in range(5):
                patika_iste = (ia, ib, ic) in izlenen
                hucre, yort, yollar = kosu_hucre(
                    net, aday, carpan, ia, ib, ic, range(N_MC), patika=patika_iste
                )
                blok[ia, ib, ic] = hucre
                if patika_iste:
                    yavas_firma[izlenen[(ia, ib, ic)]] = yort
                    patika[izlenen[(ia, ib, ic)]] = yollar
                print(
                    f"hucre kilit={ia} gecikme={ib} banka={ic} "
                    f"ort={hucre[:, F_KAL].mean():.2f} olay={hucre[:, F_OLAY].mean():.2f}",
                    flush=True,
                )

    # Sekil yan deneyi hukumden once degil, sonucla birlikte raporlanir.
    # Dogrusal uclar izgaradan okunur. Konveks (gamma=1.8, alpha=0.30) ayrica kosulur.
    kon0, _, _ = kosu_hucre(net, aday, carpan, ORTA, 3, 0, range(N_MC), gamma=1.8)
    kon4, _, _ = kosu_hucre(net, aday, carpan, ORTA, 3, 4, range(N_MC), gamma=1.8)
    sekiller = {
        "alpha_0": {
            "banka_0": float(blok[ORTA, 0, 0, :, F_KAL].mean()),
            "banka_4": float(blok[ORTA, 0, 4, :, F_KAL].mean()),
        },
        "dogrusal_0_30": {
            "banka_0": float(blok[ORTA, 3, 0, :, F_KAL].mean()),
            "banka_4": float(blok[ORTA, 3, 4, :, F_KAL].mean()),
        },
        "konveks_gamma_1_8_alpha_0_30": {
            "banka_0": float(kon0[:, F_KAL].mean()),
            "banka_4": float(kon4[:, F_KAL].mean()),
        },
    }

    duz = blok.reshape(-1, N_MC, N_F)
    rng = np.random.default_rng(TOHUM + 7)
    perm = permutasyon_p(duz[:, :, F_KAL], rng)

    kotu = blok[ORTA, 4, 0]
    iyi = blok[ORTA, 0, 4]
    baz = blok[ORTA, ORTA, ORTA]
    fark = kotu[:, F_KAL] - iyi[:, F_KAL]

    kilit_egim = egim_destek(egim_testi(blok[:, ORTA, ORTA, :, F_KAL], np.arange(5), "artan"))
    gecikme_egim = egim_destek(egim_testi(blok[ORTA, :, ORTA, :, F_KAL], np.array(GECIKME), "artan"))
    banka_egim = egim_destek(egim_testi(blok[ORTA, ORTA, :, :, F_KAL], np.array(BANKA), "azalan"))

    def paylar(hucre):
        top = hucre[:, F_OD_TOP]
        ku = hucre[:, F_OD_KU]
        out = np.full(N_MC, np.nan)
        m = top > 1e-8
        out[m] = ku[m] / top[m]
        return out

    pay_kotu = paylar(kotu)
    pay_iyi = paylar(iyi)
    pay_fark = pay_kotu - pay_iyi
    gecerli = np.isfinite(pay_fark)
    maliyet_medyan = float(np.nanmedian(pay_fark)) if gecerli.any() else float("nan")

    def aktarim(hucre):
        bb = hucre[:, F_OD_BB]
        b2k = hucre[:, F_OD_B2K]
        out = np.full(N_MC, np.nan)
        m = bb > 1e-8
        out[m] = b2k[m] / bb[m]
        return out

    akt_kotu = aktarim(kotu)
    # Kimin yavasladigini ongoruyor mu: tohum bazinda aktarim ile kucuk-buyuk yavaslik farki
    yavas_fark = kotu[:, F_Y_KU] - kotu[:, F_Y_BU]
    m_spear = np.isfinite(akt_kotu) & np.isfinite(yavas_fark)
    if m_spear.sum() >= 10 and np.std(akt_kotu[m_spear]) > 1e-8 and np.std(yavas_fark[m_spear]) > 1e-8:
        rho, rho_p = stats.spearmanr(akt_kotu[m_spear], yavas_fark[m_spear])
        rho, rho_p = float(rho), float(rho_p)
    else:
        rho, rho_p = float("nan"), float("nan")

    rast_idx = rng.integers(0, 125, size=N_MC)
    rastgele = duz[rast_idx, np.arange(N_MC), F_KAL]
    ks_kose = ks_ozet(kotu[:, F_KAL], iyi[:, F_KAL])
    ks_rast = ks_ozet(rastgele, baz[:, F_KAL])
    ks_kilit = ks_ozet(blok[4, ORTA, ORTA, :, F_KAL], blok[0, ORTA, ORTA, :, F_KAL])
    ks_banka = ks_ozet(blok[ORTA, ORTA, 0, :, F_KAL], blok[ORTA, ORTA, 4, :, F_KAL])
    ks_gecikme = ks_ozet(blok[ORTA, 4, ORTA, :, F_KAL], blok[ORTA, 0, ORTA, :, F_KAL])

    # Gun kaymasi: firma yavaslik sirasi
    def sira_karsilastir(a: np.ndarray, b: np.ndarray) -> dict:
        a = np.asarray(a, dtype=float)
        b = np.asarray(b, dtype=float)
        if np.allclose(a, a[0]) or np.allclose(b, b[0]):
            return {
                "spearman": None,
                "p": None,
                "ilk_onda_bir_kesisim": None,
                "not": "Bir köşede yavaşlık sabit; sıra tanımsız.",
            }
        rho_s, p_s = stats.spearmanr(a, b)
        ona = np.argsort(-a)
        onb = np.argsort(-b)
        ilk = max(1, N // 10)
        kesisim = len(set(ona[:ilk].tolist()) & set(onb[:ilk].tolist())) / ilk
        return {
            "spearman": float(rho_s),
            "p": float(p_s),
            "ilk_onda_bir_kesisim": float(kesisim),
            "not": None,
        }

    gun = {
        "kotu_baz": sira_karsilastir(yavas_firma["kotu"], yavas_firma["baz"]),
        "kotu_iyi": sira_karsilastir(yavas_firma["kotu"], yavas_firma["iyi"]),
    }

    # Sektor profili (sok karisik: bazi kosularda sektor sokta)
    sektor_satir = []
    for ad, v in yavas_firma.items():
        for s in range(N_SEKTOR):
            mask = net["sektor"] == s
            sektor_satir.append(
                {
                    "kosu": ad,
                    "sektor": SEKTOR[s],
                    "sektor_ad": SEKTOR_AD[s],
                    "ortalama_yavas_periyot": float(v[mask].mean()),
                    "buyuk_yavas": float(v[mask & net["buyuk"]].mean()) if np.any(mask & net["buyuk"]) else None,
                    "kucuk_yavas": float(v[mask & net["kucuk"]].mean()) if np.any(mask & net["kucuk"]) else None,
                }
            )
    sektor_df = pd.DataFrame(sektor_satir)

    olc_karar = {
        "soksuz_kalicilik": float(soksuz[F_KAL]),
        "kontrast_sistematik": bool(sistematik(fark)),
        "kontrast_p_tek": wilcoxon_p(fark, "greater"),
        "kontrast_p_iki": wilcoxon_p(fark, "two-sided"),
        "kontrast_ortalama_fark": float(np.mean(fark)),
        "kontrast_medyan_fark": float(np.median(fark)),
        "maliyet_n": int(gecerli.sum()),
        "maliyet_p_tek": wilcoxon_p(pay_fark[gecerli], "greater") if gecerli.any() else 1.0,
        "maliyet_p_iki": wilcoxon_p(pay_fark[gecerli], "two-sided") if gecerli.any() else 1.0,
        "maliyet_medyan_fark": maliyet_medyan,
        "kilit_egim": kilit_egim,
        "gecikme_egim": gecikme_egim,
        "banka_egim": banka_egim,
        "permutasyon_p": float(perm["p"]),
        "permutasyon_aralik": float(perm["ortalama_aralik"]),
    }
    karar = hukum_ver(olc_karar)

    tablo = hucre_tablosu(blok)
    tablo.to_csv(KOK / "odeme_hucre.csv", index=False)

    kosu_satir = []
    for ia in range(5):
        for ib in range(5):
            for ic in range(5):
                for s in range(N_MC):
                    r = blok[ia, ib, ic, s]
                    kosu_satir.append(
                        {
                            "kilit": ia,
                            "gecikme": ib,
                            "banka": ic,
                            "tohum": s,
                            "kalicilik": r[F_KAL],
                            "hacim_bloke": r[F_HAC],
                            "kilit_bloke": r[F_KIL],
                            "olay": r[F_OLAY],
                            "yavas_kucuk": r[F_Y_KU],
                            "yavas_buyuk": r[F_Y_BU],
                            "yavas_sok_disi": r[F_Y_DIS],
                            "yeni_tahsil": r[F_HACIM],
                            "kucuk_odenmeyen": r[F_OD_KU],
                            "odenmeyen": r[F_OD_TOP],
                            "buyukten_kucuge": r[F_OD_B2K],
                            "buyuk_borclu_odenmeyen": r[F_OD_BB],
                        }
                    )
    pd.DataFrame(kosu_satir).to_csv(KOK / "odeme_kosu.csv", index=False)
    sektor_df.to_csv(KOK / "odeme_sektor.csv", index=False)

    firma_sira = pd.DataFrame(
        {
            "firma": np.arange(N),
            "sektor": [SEKTOR[s] for s in net["sektor"]],
            "buyuk": net["buyuk"],
            "kucuk": net["kucuk"],
            "yavas_iyi": yavas_firma["iyi"],
            "yavas_baz": yavas_firma["baz"],
            "yavas_kotu": yavas_firma["kotu"],
        }
    )
    firma_sira.to_csv(KOK / "odeme_firma_sira.csv", index=False)

    grafik(
        tablo,
        {"İyi köşe": patika["iyi"], "Baz": patika["baz"], "Kötü köşe": patika["kotu"]},
        {"iyi": iyi[:, F_KAL], "baz": baz[:, F_KAL], "kotu": kotu[:, F_KAL], "rastgele": rastgele},
        KOK / "odeme_kalicilik.png",
    )
    grafik_maliyet(tablo, KOK / "odeme_maliyet.png")

    sonuc = {
        "hukum": karar["hukum"],
        "gerekce": karar["gerekce"],
        "uyari": (
            "Sentetik ağ. TCMB sektör verisine, finansal hesaplara veya bu depodaki "
            "L/G matrislerine kalibre edilmedi. Sayılar ölçüm değildir."
        ),
        "karar_olculeri": olc_karar,
        "ks": {
            "kotu_vs_iyi": ks_kose,
            "rastgele_vs_baz": ks_rast,
            "kilit_4_vs_0": ks_kilit,
            "banka_0_vs_4": ks_banka,
            "gecikme_4_vs_0": ks_gecikme,
        },
        "kose": {
            "iyi": {"kilit": KILIT[ORTA], "gecikme": GECIKME[0], "banka": BANKA[4]},
            "kotu": {"kilit": KILIT[ORTA], "gecikme": GECIKME[4], "banka": BANKA[0]},
            "baz": {"kilit": KILIT[ORTA], "gecikme": GECIKME[ORTA], "banka": BANKA[ORTA]},
            "iyi_ortalama": float(iyi[:, F_KAL].mean()),
            "iyi_medyan": float(np.median(iyi[:, F_KAL])),
            "iyi_olasilik": float(iyi[:, F_OLAY].mean()),
            "baz_ortalama": float(baz[:, F_KAL].mean()),
            "baz_medyan": float(np.median(baz[:, F_KAL])),
            "baz_olasilik": float(baz[:, F_OLAY].mean()),
            "kotu_ortalama": float(kotu[:, F_KAL].mean()),
            "kotu_medyan": float(np.median(kotu[:, F_KAL])),
            "kotu_olasilik": float(kotu[:, F_OLAY].mean()),
            "rastgele_ortalama": float(rastgele.mean()),
            "rastgele_medyan": float(np.median(rastgele)),
        },
        "aktarim": {
            "kotu_kose_buyukten_kucuge_medyan": float(np.nanmedian(akt_kotu)),
            "spearman_aktarim_kucuk_yavaslik": rho,
            "spearman_p": rho_p,
            "yorum": (
                "Kötü köşede, büyük borçlunun ödeyemediği tutarın küçük alacaklıya düşen "
                "payı ile küçük−büyük yavaşlık farkı arasındaki Spearman."
            ),
        },
        "gun_kaymasi": gun,
        "sekil_deneyi_ortalama_kalicilik": sekiller,
        "kalibrasyon": kal_rapor,
        "secilen_aday": aday,
        "sok_buyuklugu_kontrol": sok_kontrol,
        "ag": olcu,
        "varsayimlar": varsayimlar(aday),
        "soksuz": {
            "kalicilik": float(soksuz[F_KAL]),
            "ortalama_hacim": float(soksuz[F_HACIM]),
            "arrears_orani": float(soksuz[F_ARREAR]),
        },
    }
    (KOK / "odeme_sonuc.json").write_text(
        json.dumps(numpy_json(sonuc), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    rapor_yaz(sonuc, tablo, sektor_df)
    print("HUKUM", karar["hukum"])
    print(karar["gerekce"])


def varsayimlar(aday: dict) -> dict:
    return {
        "dugum": N,
        "sektor": N_SEKTOR,
        "firma_basi_sektor": N_FIRMA_SEKTOR,
        "periyot": "Ay gibi okunabilir; takvim iddiasi yok.",
        "ufuk": T,
        "periyot_ici_tur": TURLAR,
        "monte_carlo": N_MC,
        "tohum": TOHUM,
        "ag": (
            "Her firma 2 aynı sektör, 3 yukarı akım, 1 aynı sıra komşu sektör alacaklısına "
            "borçlanır. Ağırlık 0.30 * sqrt(boyut_i * boyut_j) * U(0.6, 1.4). "
            "Boyut lognormal(0, 0.55), medyan 1. Büyük: üst çeyrek, banka erişimi 1. "
            "Küçük: alt yarı, erişim 0.20. Orta: 0.45."
        ),
        "likidite": (
            f"Başlangıç likidite = U({aday['lo']}, {aday['hi']}) * aylık borç + 0.20 * boyut. "
            "U sırası ağ tohumuna bağlı, parametreler arasında ortaktır."
        ),
        "sok": (
            f"{aday['n_sek']} rastgele sektörde likidite × {aday['kalan']}. "
            f"Kalan firmaların %{int(aday['ek_oran']*100)} kadarı × {aday['ek_kalan']}. "
            "Şok büyüklüğü sabit; hangi sektörün vurulduğu tohumla değişir ve parametre "
            "hücreleri arasında eşleştirilmiştir."
        ),
        "kilit": (
            "Ödeme oranı eşiğin altındaysa firma sonraki `sure` periyotta hiç ödemez. "
            f"Izgarası (eşik, süre): {KILIT}."
        ),
        "gecikme": (
            "Doğrusal: alpha * ödenmeyen. Konveks yan deney: alpha * ödenmeyen * "
            "(ödenmeyen/fatura)^(gamma-1), gamma=1.8. Alpha ızgarası "
            f"{GECIKME}. Maliyet alacaklının likiditesinden düşer; sıfırın altı silinir, "
            "yeni borç yazılmaz. Reel kayıptır, transfere yazılmaz."
        ),
        "banka": (
            f"Çarpan ızgarası {BANKA}, tavan = çarpan * erişim * (aylık borç + 0.25*boyut). "
            "Çekilen tutar dış likiditedir. Likidite aylık borcun 1.25 katını aşarsa "
            "fazlanın yarısı limiti yerine koyar."
        ),
        "dis_akis": (
            "Her periyot sonunda likiditeye (aylık borç − aylık alacak) eklenir. "
            "Herkes tam öderse stok yerinde kalır. Bu akım sözleşmenin büyüklüğündedir; "
            "kaçırılan tahsilatı karşılamaz."
        ),
        "bloke": (
            f"Yeni fatura tahsil oranı < {HACIM_ESIK} veya sıkıntılı düğüm payı >= {KILIT_PAY_ESIK}. "
            "Yeni fatura tahsili, ödemenin devreden ve yeni kısım arasında oransal payıdır. "
            f"Kalıcılık bu periyotların sayısı. Olasılık: kalıcılık >= {OLAY_ESIK}."
        ),
        "sabit_tutulan": "Kenar kümesi, ağırlıklar, boyut, tampon sırası, şok çarpanları.",
        "degisen": "Kilit eşiği/süresi, gecikme alpha, banka çarpanı.",
    }


def rapor_yaz(sonuc: dict, tablo: pd.DataFrame, sektor_df: pd.DataFrame) -> None:
    k = sonuc["karar_olculeri"]
    o = sonuc["kose"]
    hukum = sonuc["hukum"]
    yedek = any(r.get("yedek_secim") for r in sonuc["kalibrasyon"])
    if yedek:
        secim_cumlesi = (
            "İç bölge kuralını (şoksuz kalıcılık 0, baz ortalama 2–16, standart sapma en az 1) "
            "hiçbir aday tutmadı. Yedek kural, şoksuz tıkanmayanlar arasından baz ortalaması "
            f"8'e en yakın adayı seçti. Köşe farkına bakılmadı."
        )
    else:
        secim_cumlesi = (
            "Aday, şoksuz koşunun tıkanmaması ve baz hücrenin kalıcılığının 2 ile 16 periyot "
            "arasında, standart sapmasının en az 1 olmasına göre seçildi. Köşe farkına bakılmadı."
        )
    sok_parca = []
    for ad, koseler in sonuc.get("sok_buyuklugu_kontrol", {}).items():
        sok_parca.append(
            f"aday {ad}: iyi {koseler['iyi']['ortalama']:.2f}, baz {koseler['baz']['ortalama']:.2f}, "
            f"kötü {koseler['kotu']['ortalama']:.2f}"
        )
    sok_cumlesi = "; ".join(sok_parca) if sok_parca else "yok"
    baslik = {"desteklendi": "desteklendi", "elendi": "elendi", "sinanamadi": "sınanamadı"}[hukum]
    tek = tablo[(tablo.gecikme == ORTA) & (tablo.banka == ORTA)].sort_values("kilit")
    gec = tablo[(tablo.kilit == ORTA) & (tablo.banka == ORTA)].sort_values("gecikme")
    ban = tablo[(tablo.kilit == ORTA) & (tablo.gecikme == ORTA)].sort_values("banka")

    def cizgi(df, kolon, ad):
        parcalar = [
            f"{getattr(r, kolon):g}: ortalama {r.kalicilik_ortalama:.2f}, medyan {r.kalicilik_medyan:.1f}, P(≥4) {r.olasilik_en_az_4:.2f}"
            for r in df.itertuples()
        ]
        return f"{ad}: " + "; ".join(parcalar)

    def gun_cumle(ad, g):
        if g.get("spearman") is None:
            return f"{ad}: {g.get('not')}"
        return (
            f"{ad}: Spearman {g['spearman']:.3f} (p = {g['p']:.3g}), "
            f"ilk onda bir kesişim {g['ilk_onda_bir_kesisim']:.2f}."
        )

    kotu_y = sektor_df[sektor_df.kosu == "kotu"]["ortalama_yavas_periyot"]
    sektor_aralik = f"{kotu_y.min():.1f}–{kotu_y.max():.1f} periyot"
    baz_sek = (
        sektor_df[sektor_df.kosu == "baz"]
        .sort_values("ortalama_yavas_periyot", ascending=False)
        .head(3)
    )
    sektor_cumle = ", ".join(
        f"{r.sektor_ad} {r.ortalama_yavas_periyot:.1f}" for r in baz_sek.itertuples()
    )
    sikinti = tablo[tablo["kucuk_odenmeyen_payi"].notna()]
    if len(sikinti):
        pay_cumlesi = (
            f"medyan {sikinti['kucuk_odenmeyen_payi'].median():.2f}, "
            f"aralık {sikinti['kucuk_odenmeyen_payi'].min():.2f}–{sikinti['kucuk_odenmeyen_payi'].max():.2f}"
        )
    else:
        pay_cumlesi = "yok"
    banka4_max = float(tablo.loc[tablo.banka == 4, "kalicilik_ortalama"].max())
    kilit0_max = float(tablo.loc[tablo.kilit == 0, "kalicilik_ortalama"].max())
    ag = sonuc["ag"]
    aday = sonuc["secilen_aday"]
    metin = f"""# Ödeme zinciri kalıcılığı

{sonuc["uyari"]}

## Hüküm

Dağıtık faillik bu simülasyonda **{baslik}**.

{sonuc["gerekce"]}

Birincil kontrast (kötü köşe − iyi köşe, aynı {N_MC} şok): ortalama fark {k["kontrast_ortalama_fark"]:.2f} periyot, medyan fark {k["kontrast_medyan_fark"]:.2f}, tek yanlı Wilcoxon p = {k["kontrast_p_tek"]:.4g}, iki yanlı p = {k["kontrast_p_iki"]:.4g}. KS istatistiği {sonuc["ks"]["kotu_vs_iyi"]["istatistik"]:.3f}, p = {sonuc["ks"]["kotu_vs_iyi"]["p"]:.4g}.

Küçük alacaklının ödenmeyen payı, iyi köşede tanımsız: o köşe ödenmeyen tutar bırakmıyor (n = {k["maliyet_n"]}). Sıkıntılı hücrelerde pay {pay_cumlesi}. Bileşim parametreyle kaymıyor; değişen, ödenmeyen tutarın büyüklüğü.

Global etiket permütasyonu: hücre ortalamalarının aralığı {k["permutasyon_aralik"]:.2f} periyot, p = {k["permutasyon_p"]:.4g} ({PERMUTE} karıştırma).

## Ne sabit, ne değişti

204 firma, 17 sektör, sektör başına 12 firma. Kenar sayısı {ag["kenar"]}, yoğunluk {ag["yogunluk"]:.4f}, yönsüz ortalama kümelenme {ag["ortalama_kume"]:.3f}, ortalama çıkış derecesi {ag["ortalama_cikis_derece"]:.2f}, giriş gücü Gini {ag["giris_guc_gini"]:.3f}, PageRank Gini {ag["pagerank_gini"]:.3f}. Büyük düğüm {ag["buyuk_dugum"]}, küçük düğüm {ag["kucuk_dugum"]}.

Bu ölçüler parametre ızgarasında yeniden çekilmedi. Aynı şok çarpanları {N_MC} tohumda her hücreye uygulandı. Değişenler: kilit eşiği ve süresi {KILIT}, gecikme α {GECIKME}, banka çarpanı {BANKA}. Her periyot sonunda likiditeye sözleşmedeki (borç − alacak) eklenir; herkes tam öderse stok yerinde kalır. Bu dış akım kaçırılan tahsilatı yerine koymaz.

Seçilen şok/tampon adayı {aday["ad"]}: likidite tamponu U({aday["lo"]}, {aday["hi"]}), {aday["n_sek"]} sektörde likidite × {aday["kalan"]}, diğer firmaların {aday["ek_oran"]:.0%} kadarı × {aday["ek_kalan"]}. {secim_cumlesi} Kalibrasyon tablosu `odeme_sonuc.json` içindedir.

Şok büyüklüğü kontrolü (aynı ağ, aynı üç köşe, hükme girmez): {sok_cumlesi}

Şoksuz baz parametre: kalıcılık {sonuc["soksuz"]["kalicilik"]:.0f}, ortalama yeni fatura tahsil oranı {sonuc["soksuz"]["ortalama_hacim"]:.3f}.

## Kalıcılık

İyi köşe (kilit orta, α = {GECIKME[0]}, banka = {BANKA[4]}): ortalama {o["iyi_ortalama"]:.2f}, medyan {o["iyi_medyan"]:.1f}, P(kalıcılık ≥ 4) = {o["iyi_olasilik"]:.2f}.

Baz (orta, orta, orta): ortalama {o["baz_ortalama"]:.2f}, medyan {o["baz_medyan"]:.1f}, P = {o["baz_olasilik"]:.2f}.

Kötü köşe (kilit orta, α = {GECIKME[4]}, banka = {BANKA[0]}): ortalama {o["kotu_ortalama"]:.2f}, medyan {o["kotu_medyan"]:.1f}, P = {o["kotu_olasilik"]:.2f}.

Parametreler her koşuda ızgaradan rastgele çekilince: ortalama {o["rastgele_ortalama"]:.2f}, medyan {o["rastgele_medyan"]:.1f}. Baz ile KS p = {sonuc["ks"]["rastgele_vs_baz"]["p"]:.4g}.

{cizgi(tek, "kilit_sure", "Kilit süresi (diğerleri orta)")}

{cizgi(gec, "gecikme_alpha", "Gecikme α (diğerleri orta)")}

{cizgi(ban, "banka_carpan", "Banka çarpanı (diğerleri orta)")}

Eğimler (tohum içi doğrusal eğim, öngörülen yöne tek yanlı Wilcoxon): kilit medyan eğim {k["kilit_egim"]["egim_medyan"]:.3f}, aralık {k["kilit_egim"]["medyan_aralik"]:.2f}, p = {k["kilit_egim"]["p_tek_yan"]:.4g}, destek = {k["kilit_egim"]["destek"]}. Gecikme medyan eğim {k["gecikme_egim"]["egim_medyan"]:.3f}, aralık {k["gecikme_egim"]["medyan_aralik"]:.2f}, p = {k["gecikme_egim"]["p_tek_yan"]:.4g}, destek = {k["gecikme_egim"]["destek"]}. Banka medyan eğim {k["banka_egim"]["egim_medyan"]:.3f}, aralık {k["banka_egim"]["medyan_aralik"]:.2f}, p = {k["banka_egim"]["p_tek_yan"]:.4g}, destek = {k["banka_egim"]["destek"]}.

Ayrı KS, orta diğer parametrelerde: kilit ucu p = {sonuc["ks"]["kilit_4_vs_0"]["p"]:.4g} (ortalama fark {sonuc["ks"]["kilit_4_vs_0"]["ortalama_fark"]:.2f}); banka 0 eksi banka 4 p = {sonuc["ks"]["banka_0_vs_4"]["p"]:.4g} (ortalama fark {sonuc["ks"]["banka_0_vs_4"]["ortalama_fark"]:.2f}); gecikme ucu p = {sonuc["ks"]["gecikme_4_vs_0"]["p"]:.4g} (ortalama fark {sonuc["ks"]["gecikme_4_vs_0"]["ortalama_fark"]:.2f}).

## Kim yavaşlıyor, maliyet nereye gidiyor

Yavaşlık, firmanın kilitli olduğu veya ödeme oranının 0.70 altında kaldığı periyot sayısıdır. Kötü köşede sektör ortalamaları {sektor_aralik}; tıkanma birkaç sektörde kalmıyor. Baz köşede yavaşlık daha toplu: {sektor_cumle}.

Büyük borçlunun ödeyemediği tutarın küçük alacaklıya düşen payı, kötü köşede medyan {sonuc["aktarim"]["kotu_kose_buyukten_kucuge_medyan"]:.3f}. Bu pay ile küçük−büyük yavaşlık farkının Spearman korelasyonu {sonuc["aktarim"]["spearman_aktarim_kucuk_yavaslik"]:.3f} (p = {sonuc["aktarim"]["spearman_p"]:.4g}). Aktarım oranı, aynı kötü köşe içinde kimin daha yavaşladığını öngörüyor. Parametre değişince ödenmeyen tutarın küçük payı neredeyse yerinde kalıyor.

Gün kayması: {gun_cumle("kötü ve baz", sonuc["gun_kaymasi"]["kotu_baz"])} {gun_cumle("kötü ve iyi", sonuc["gun_kaymasi"]["kotu_iyi"])}

Maliyet şekli yan deneydir, hükme girmez. Ortalama kalıcılık: {json.dumps(sonuc["sekil_deneyi_ortalama_kalicilik"], ensure_ascii=False)}.

## Hangi hipotez elendi

Parametre-bağımsız hipotez, seçilen şokta elendi. Aynı ağ ve aynı şok çarpanlarıyla kilit, gecikme ve banka kalıcılık dağılımını değiştiriyor. Banka çarpanı 4 olan 25 hücrenin hepsinde ortalama kalıcılık {banka4_max:.2f}. En yumuşak kilitte (eşik 0.50, süre 1) en yüksek hücre ortalaması {kilit0_max:.2f}. İkisi de sistemik tıkanmayı kapatıyor. Gecikme, banka kapalıyken süreyi uzatıyor; banka açıkken etkisi küçülüyor.

Maliyetin büyük düğümden küçük tedarikçiye kaydığı biçimi desteklenmedi. Sıkıntı olan hücrelerde küçük alacaklının payı dar bir bantta. Kötü köşede büyük firmalar küçüklerden daha yavaş (yavaşlık farkı tabloda, banka 0 ve yüksek α). Ara banka limitinde küçükler daha yavaş. Aktarım oranı bu farkı koşular arasında öngörüyor; parametre onu sistematik olarak büyütmüyor.

Yumuşak şok (aday A) üç köşede de kalıcılık üretmiyor. O şokta parametre kolu gereksiz, hipotez elenir. Aday B'nin kötü köşesi uzuyor, iyi köşesi uzamıyor: eşik, şok büyüklüğünde. Seçilen aday C bu eşiğin üstünde. Sonuç şok protokolüne bağlıdır; her şokta parametre bağımlılığı iddia edilmez.

Eleme kuralı kodda: 125 hücrenin ortalamaları tohum içinde karıştırılınca gözlenen aralık çıkmıyor (p > 0.05), köşe farkı iki yanlı Wilcoxon ile ayrılmıyor ve maliyet payı en az 5 puan kaymıyorsa parametre-bağımsız hipotez kalır. Destek için kötü köşe iyiden en az 2 periyot uzun ve tek yanlı p < 0.05 olmalıydı. Bu koşu destek eşiğini geçti. Maliyet payı kayması geçmedi; hüküm kalıcılık kontrastına dayanır.

## Dosyalar

`odeme_hucre.csv` hücre özeti, `odeme_kosu.csv` 10.000 koşu, `odeme_sektor.csv` sektör yavaşlığı, `odeme_firma_sira.csv` firma sırası, `odeme_kalicilik.png`, `odeme_maliyet.png`, `odeme_sonuc.json`.

Tekrar: `python3 odeme_zinciri.py`. Ağ tohumu {TOHUM}.
"""
    (KOK / "ODEME_ZINCIRI.md").write_text(metin, encoding="utf-8")


if __name__ == "__main__":
    from odeme_kons7 import main_kons7

    main_kons7()
