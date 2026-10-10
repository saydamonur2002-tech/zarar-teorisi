"""Tur 6: ayni odeme kurali, TCMB 2026-Q1 stoklari.

Kimden kime kenar, olculmus bilateral fatura degildir. Her enstruman icinde
yukumluluk, alacaklilara varlik paylariyla bolunur (kalibre_matris.mat).
Kisa kredi 12 ayda, uzun kredi 60 ayda, diger hesap 12 ayda servis edilir.
Bu vade modeli olcum degildir. Cizilmemis banka limiti EVDS'te yoktur; cizgi 0.
Ithal girdi-cikti katsayisi depoda yoktur. Reel kisit, firma döviz kredisinin
cevrilmemesidir: FX mevduat / FX kredi stoku. Valf pi, Ocak 2026 yillik TUFE'nin
aylik karsiligidir.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import odeme_zinciri as oz
from akis_model import IDX, INSTR, SEC, Lm, load, panel

KOK = Path(__file__).resolve().parent
DONEM = "2026-Q1"
KISA_AY = 12.0
UZUN_AY = 60.0
DIGER_AY = 12.0
ESIK_VALF = 0.25
ISARET = "\n\n<!-- ONCEKI -->\n\n"
F_KREDI = 0.5962755835053216
F_MEV = 0.5801292831604365


def tufe_yoy() -> dict:
    """EVDS TP.FG.J0. Ag yoksa 2025-01 ve 2026-01 gozlemi."""
    try:
        import urllib.request

        body = {
            "type": "json", "series": "TP.FG.J0", "aggregationTypes": "last", "formulas": "0",
            "startDate": "01-01-2025", "endDate": "01-10-2026", "frequency": "5",
            "decimalSeperator": ".", "decimal": "2", "dateFormat": "0", "lang": "TR",
            "yon": "0", "sira": "0", "ozelFormuller": [], "groupSeperator": True,
            "isRaporSayfasi": False,
        }
        req = urllib.request.Request(
            "https://evds3.tcmb.gov.tr/igmevdsms-dis/fe",
            data=json.dumps(body).encode(),
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            method="POST",
        )
        raw = urllib.request.urlopen(req, timeout=60).read().decode("utf-8-sig")
        items = json.loads(raw)["items"]
        son = items[-1]
        once = next(it for it in items if it["Tarih"] == _yil_once(son["Tarih"]))
        a = float(str(son["TP_FG_J0"]).replace(",", ""))
        b = float(str(once["TP_FG_J0"]).replace(",", ""))
        return {"yoy": a / b - 1.0, "son": son["Tarih"], "baz": once["Tarih"], "kaynak": "EVDS TP.FG.J0"}
    except Exception:
        return {"yoy": 3683.83 / 2819.65 - 1.0, "son": "2026-01", "baz": "2025-01", "kaynak": "EVDS TP.FG.J0, kayitli gozlem"}


def _yil_once(tarih: str) -> str:
    yil, ay = tarih.split("-")
    return f"{int(yil) - 1}-{ay}"


def kisa_pay(stab, tcs) -> np.ndarray:
    """Kredi yukumlulugunun kisa vade payi. B'den TCMB K'ye tasinir. D cevrilir."""
    def g(h, zp):
        return float(stab.get((h, DONEM, zp), 0.0) or 0.0)

    y = np.zeros(5)
    kisa = np.zeros(5)
    for h, s in (("H", "H"), ("NPISH", "H"), ("F", "F"), ("B", "B"), ("K", "K")):
        y[IDX[s]] += g(h, 34)
        kisa[IDX[s]] += g(h, 35)
    # D varlik/yukumluluk etiketi ters; panel ile ayni cevirme.
    y[IDX["D"]] += g("D", 12)
    kisa[IDX["D"]] += g("D", 13)
    tc_y, tc_k = float(tcs.get((DONEM, 34), 0.0) or 0.0), float(tcs.get((DONEM, 35), 0.0) or 0.0)
    y[IDX["B"]] -= tc_y
    kisa[IDX["B"]] -= tc_k
    y[IDX["K"]] += tc_y
    kisa[IDX["K"]] += tc_k
    pay = np.ones(5)
    var = y > 1.0
    pay[var] = np.clip(kisa[var] / y[var], 0.0, 1.0)
    return pay


def mevduat_dususu(stab, tcs) -> float:
    """Firma mevduat varliginin en buyuk ceyreklik dususu. 2018-Q4 beklenir."""
    stok = []
    donemler = sorted({k[1] for k in stab if k[0] == "F"})
    for p in donemler:
        A, _ = panel(stab, tcs, p)
        stok.append(A[list(INSTR).index("para_mevduat"), IDX["F"]])
    d = np.diff(np.array(stok)) / np.array(stok[:-1])
    return float(np.nanmin(d))


def ag_olc() -> dict:
    stab, _, tcs, _ = load()
    A, Y = panel(stab, tcs, DONEM)
    ad = list(INSTR)
    ik, im, idg = ad.index("kredi"), ad.index("para_mevduat"), ad.index("diger")
    mat = Lm(A, Y)
    pay = kisa_pay(stab, tcs)
    aylik = np.zeros((2, 5))
    aylik[0] = Y[ik] * (pay / KISA_AY + (1.0 - pay) / UZUN_AY)
    aylik[1] = Y[idg] / DIGER_AY
    kenar = {}
    for blok, M in ((0, mat["kredi"]), (1, mat["diger"])):
        for j in range(5):
            for i in range(5):
                if i == j:
                    continue
                w = float(aylik[blok, j] * M[j, i] / 1e9)
                if w > 1e-8:
                    kenar[(j, i)] = kenar.get((j, i), 0.0) + w
    borclu = np.array([k[0] for k in kenar], dtype=np.int32)
    alacakli = np.array([k[1] for k in kenar], dtype=np.int32)
    w0 = np.array([kenar[k] for k in kenar], dtype=np.float64)
    borc = np.bincount(borclu, weights=w0, minlength=5)
    alacak = np.bincount(alacakli, weights=w0, minlength=5)
    kucuk = np.zeros(5, dtype=bool)
    kucuk[IDX["H"]] = True
    buyuk = np.zeros(5, dtype=bool)
    buyuk[IDX["B"]] = True
    lik = A[im] / 1e9
    fx_kredi = F_KREDI * float(Y[ik, IDX["F"]])
    fx_mev = F_MEV * float(A[im, IDX["F"]])
    kapsama = fx_mev / fx_kredi
    net = {
        "sektor": np.arange(5),
        "boyut": (A[im] + Y[ik]) / 1e9,
        "borclu": borclu,
        "alacakli": alacakli,
        "w0": w0,
        "borc": borc,
        "alacak": alacak,
        "buyuk": buyuk,
        "kucuk": kucuk,
        "banka_taban": np.zeros(5),
        "idx_ku_al": np.flatnonzero(kucuk[alacakli]),
        "idx_bu_al": np.flatnonzero(buyuk[alacakli]),
        "idx_bu_borc": np.flatnonzero(buyuk[borclu]),
        "idx_b2k": np.flatnonzero(buyuk[borclu] & kucuk[alacakli]),
        "dis_akis": borc - alacak,
    }
    olcu = {
        "likidite_trilyon": {s: float(lik[i]) for i, s in enumerate(SEC)},
        "kredi_yukumluluk_trilyon": {s: float(Y[ik, i] / 1e9) for i, s in enumerate(SEC)},
        "diger_yukumluluk_trilyon": {s: float(Y[idg, i] / 1e9) for i, s in enumerate(SEC)},
        "kisa_pay": {s: float(pay[i]) for i, s in enumerate(SEC)},
        "aylik_servis_trilyon": {s: float((aylik[0, i] + aylik[1, i]) / 1e9) for i, s in enumerate(SEC)},
        "fx_kredi_payi_F": F_KREDI,
        "fx_mevduat_payi_F": F_MEV,
        "fx_kapsama_F": float(kapsama),
        "mevduat_dususu_F": mevduat_dususu(stab, tcs),
        "kenar": int(w0.size),
        "V0": float(w0.sum()),
    }
    return {"net": net, "lik": lik, "olcu": olcu, "kapsama": float(kapsama)}


def kos(net, lik, pi, reel, fx_sok, fx_kalan, ithal):
    sok = np.ones(5, dtype=bool)
    if fx_sok:
        sok[IDX["F"]] = False
    return oz.tek_kosu_temiz(
        net, lik, np.zeros(5), oz.KILIT[oz.ORTA][0], oz.KILIT[oz.ORTA][1], oz.GECIKME[4], sok,
        enflasyon_esik=ESIK_VALF, enflasyon_pi=pi, reel=reel, ithal=ithal,
        fx_ay=1.0, fx_sok=fx_sok, fx_kalan=fx_kalan, fx_hizmet=0.0, patika=True,
    )


def grafik(paket, dosya: Path) -> None:
    ad = ["Şoksuz", "Mevduat şoku", "FX çevirmeme", "İkisi"]
    anahtar = ["soksuz", "mevduat", "fx", "iki"]
    fig, ax = plt.subplots(1, 2, figsize=(10.2, 4.3))
    x = np.arange(4)
    gen = 0.36
    kap = [paket[k]["kapali"]["kalicilik"] for k in anahtar]
    ac = [paket[k]["acik"]["kalicilik"] for k in anahtar]
    ax[0].bar(x - gen / 2, kap, width=gen, label="Valf kapalı", color="#4C78A8")
    ax[0].bar(x + gen / 2, ac, width=gen, label="Valf açık", color="#F58518")
    ax[0].set_xticks(x, ad, rotation=15, ha="right")
    ax[0].set_ylim(0, 1)
    ax[0].set_ylabel("Bloke periyot")
    ax[0].set_title("Kalıcılık, tek patika")
    ax[0].legend(frameon=False, fontsize=8)
    kapr = [paket[k]["kapali"]["reel"] for k in anahtar]
    acr = [paket[k]["acik"]["reel"] for k in anahtar]
    ax[1].bar(x - gen / 2, kapr, width=gen, label="Valf kapalı", color="#E45756")
    ax[1].bar(x + gen / 2, acr, width=gen, label="Valf açık", color="#F58518")
    ax[1].set_xticks(x, ad, rotation=15, ha="right")
    ax[1].set_ylim(0, 0.6)
    ax[1].set_ylabel("Reel fatura kaybı / (V0 × T)")
    ax[1].set_title("Reel kayıp")
    ax[1].legend(frameon=False, fontsize=8)
    fig.suptitle("TCMB 2026-Q1 stokları. Bilateral kenar orantılı dağıtımdır.", fontsize=11)
    fig.tight_layout()
    fig.savefig(dosya, dpi=120)
    plt.close(fig)


def hukum(p, pi) -> str:
    fx = p["fx"]
    if p["soksuz"]["kapali"]["kalicilik"] >= 1:
        giris = "Şoksuz patika bloke üretiyor. Vade varsayımı sonuca göre kısaltılmadı."
    else:
        giris = "Şoksuz patika bloke üretmiyor."
    kis_kal = fx["kapali"]["kalicilik"] - fx["acik"]["kalicilik"]
    kis_reel = fx["kapali"]["reel"] - fx["acik"]["reel"]
    if kis_kal < 2 and kis_reel < 0.05:
        silim = (
            "FX çevirmeme şokunda valf kalıcılığı 2 periyottan az değiştiriyor ve reel kaybı 5 puandan az düşürüyor. "
            "Ölçülmüş aylık enflasyon bu kısıtı kapatmıyor."
        )
    else:
        silim = "Valf, FX çevirmeme şokunda kalıcılığı veya reel kaybı eşiğin üstünde indiriyor."
    return (
        f"{giris} Firma mevduatının ölçülmüş en büyük çeyreklik düşüşü kalıcılığı "
        f"{p['mevduat']['kapali']['kalicilik']:.0f} periyotta bırakıyor. "
        f"Döviz kredisinin çevrilmediği patikada kalıcılık {fx['kapali']['kalicilik']:.0f}, "
        f"reel kayıp {fx['kapali']['reel']:.3f}. Valf açıkken {fx['acik']['kalicilik']:.0f} ve {fx['acik']['reel']:.3f}. "
        f"π aylık {pi:.4f}. Valf periyodu 0: zincir bloke olmayınca valf açılmıyor, erime 0. {silim} "
        "Kenar, finansal hesap stokunun orantılı karşı taraf dağılımıdır; firma faturası değildir. "
        f"Aynı ağda firma mevduatını × 0,30 kesmek, ölçülmüş düşüş değildir: kalıcılık "
        f"{p['asiri']['kapali']['kalicilik']:.0f}."
    )


def rapor(sonuc: dict) -> str:
    o = sonuc["olcu"]
    p = sonuc["paket"]
    s = [
        "# Ödeme zinciri, ölçülmüş stoklar",
        "",
        sonuc["uyari"],
        "",
        "## Hüküm",
        "",
        sonuc["ozet"],
        "",
        "## Ne ölçülmüş, ne varsayım",
        "",
        f"Dönem {DONEM}. Birim trilyon TL. Firma mevduatı {o['likidite_trilyon']['F']:.2f}, "
        f"firma kredi yükümlülüğü {o['kredi_yukumluluk_trilyon']['F']:.2f}, "
        f"diğer yükümlülük {o['diger_yukumluluk_trilyon']['F']:.2f}.",
        "",
        f"Kredi döviz payı (değerleme regresyonu, F yükümlülük) {o['fx_kredi_payi_F']:.3f}. "
        f"Mevduat döviz payı {o['fx_mevduat_payi_F']:.3f}. "
        f"FX mevduat / FX kredi stoku = {o['fx_kapsama_F']:.3f}. "
        f"Firma mevduatının en büyük çeyreklik düşüşü {o['mevduat_dususu_F']:.3f}. "
        f"Firma aylık servis {o['aylik_servis_trilyon']['F']:.2f}; mevduat bunun "
        f"{o['likidite_trilyon']['F'] / o['aylik_servis_trilyon']['F']:.1f} katı.",
        "",
        f"TÜFE {sonuc['tufe']['baz']}–{sonuc['tufe']['son']}: yıllık {sonuc['tufe']['yoy']:.3f}, "
        f"aylık π = {sonuc['pi_aylik']:.4f}. Kaynak {sonuc['tufe']['kaynak']}.",
        "",
        "Kısa kredi 12 ay, uzun kredi 60 ay, diğer hesap 12 ay servis edilir. Bu vade ölçülmedi. "
        "Çekilmemiş banka limiti seride yok, çizgi sıfır. Valf eşiği 0,25 model kuralıdır. "
        "Girdi-çıktı ithal katsayısı yok. Reel kısıt, firmanın döviz kredisini çevirememesidir.",
        "",
        "Karşı taraf matrisi `Lm`: borçlunun yükümlülüğü, alacaklıların varlık payına bölünür. "
        "Bu, depodaki kendi uyarısıyla ölçülmüş bir fatura ağı değildir.",
        "",
        "## Tek patika",
        "",
        "Monte Carlo yok. Matris tek. Kısalma eşiği 2 bloke periyot, reel kayıp eşiği 0,05. p-değeri yok. "
        "`asiri` satırı ölçülmüş düşüş değildir: önceki turlardaki × 0,30 likidite kesimi, bu stoklara uygulanır.",
        "",
        "| Patika | Valf | Bloke | Reel kayıp | Erime | Valf periyodu |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for ad in ("soksuz", "mevduat", "fx", "iki", "asiri"):
        for kap, et in (("kapali", "kapalı"), ("acik", "açık")):
            r = p[ad][kap]
            s.append(
                f"| {ad} | {et} | {r['kalicilik']:.0f} | {r['reel']:.3f} | {r['erime']:.3f} | {r['pi']:.0f} |"
            )
    h_pay = sonuc["hane_reel_pay"]
    s.extend([
        "",
        f"FX çevirmemede hane, alacaklı olarak reel kaybın {h_pay:.3f} kadarını taşır. "
        f"Hane defter payı {sonuc['hane_defter']:.3f}.",
        "",
        "Tekrar: `python3 odeme_zinciri.py`.",
        "",
        "Dosyalar: `odeme_gercek.png`, `odeme_gercek_sonuc.json`.",
        "",
    ])
    return "\n".join(s)


def paketle(h, v0) -> dict:
    return {
        "kalicilik": float(h[oz.F_KAL]),
        "reel": float(h[oz.F_REEL] / (v0 * oz.T)),
        "erime": float(h[oz.F_ER_TOP] / (v0 * oz.T)),
        "pi": float(h[oz.F_PI_N]),
        "fx_acik": float(h[oz.F_FX_ACIK]),
    }


def main_gercek() -> None:
    tufe = tufe_yoy()
    pi = (1.0 + tufe["yoy"]) ** (1.0 / 12.0) - 1.0
    kur = ag_olc()
    net, lik, olcu = kur["net"], kur["lik"], kur["olcu"]
    print("olcu", {k: olcu[k] for k in ("fx_kapsama_F", "mevduat_dususu_F", "V0", "kenar")})
    ith = np.zeros(5)
    ith[IDX["F"]] = F_KREDI
    kalan = olcu["fx_kapsama_F"]
    dus = olcu["mevduat_dususu_F"]
    lik_sok = lik.copy()
    lik_sok[IDX["F"]] *= 1.0 + dus
    v0 = olcu["V0"]

    lik_asiri = lik.copy()
    lik_asiri[IDX["F"]] *= 0.30
    ham = {}
    for ad, lik0, reel, fx in (
        ("soksuz", lik, True, False),
        ("mevduat", lik_sok, True, False),
        ("fx", lik, True, True),
        ("iki", lik_sok, True, True),
        ("asiri", lik_asiri, True, False),
    ):
        ham[ad] = {
            "kapali": kos(net, lik0, 0.0, reel, fx, kalan, ith),
            "acik": kos(net, lik0, pi, reel, fx, kalan, ith),
        }
        print(ad, ham[ad]["kapali"][0][oz.F_KAL], ham[ad]["acik"][0][oz.F_KAL], ham[ad]["kapali"][0][oz.F_REEL])

    paket = {
        ad: {"kapali": paketle(ham[ad]["kapali"][0], v0), "acik": paketle(ham[ad]["acik"][0], v0)}
        for ad in ham
    }
    grafik({k: paket[k] for k in ("soksuz", "mevduat", "fx", "iki")}, KOK / "odeme_gercek.png")
    fx_h = ham["fx"]["kapali"][0]
    hane_pay = float(fx_h[oz.F_REEL_KU] / fx_h[oz.F_REEL]) if fx_h[oz.F_REEL] > 1e-8 else 0.0
    defter = float(net["w0"][net["idx_ku_al"]].sum() / net["w0"].sum()) if net["idx_ku_al"].size else 0.0
    ozet = hukum(paket, pi)
    sonuc = {
        "uyari": (
            "Stoklar TCMB finansal hesapları, 2026-Q1, milyar TL biriminden trilyona çevrildi. "
            "Kenar ölçülmüş fatura değildir: yükümlülük, alacaklı varlık payına bölünür. "
            "Vade ve valf eşiği varsayımdır. Çekilmemiş limit yoktur."
        ),
        "ozet": ozet,
        "olcu": olcu,
        "tufe": tufe,
        "pi_aylik": pi,
        "paket": paket,
        "hane_reel_pay": hane_pay,
        "hane_defter": defter,
    }
    (KOK / "odeme_gercek_sonuc.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    eski = (KOK / "ODEME_ZINCIRI.md").read_text(encoding="utf-8")
    if eski.startswith("# Ödeme zinciri, ölçülmüş") and ISARET in eski:
        eski = eski.split(ISARET, 1)[1]
    (KOK / "ODEME_ZINCIRI.md").write_text(rapor(sonuc) + ISARET + eski, encoding="utf-8")
    print(ozet)


if __name__ == "__main__":
    main_gercek()
