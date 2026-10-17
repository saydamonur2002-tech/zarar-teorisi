"""Şok testleri. Mevcut faiz ve ağ formüllerini çağırır; kilitli çıktı dosyalarını yazmaz.

(a) Kur: F.4 2026-Q1 YP payı δ ile değerlenir. Sözleşme faizi rev_adim3 formülüdür (ψ yok).
    Değerleme farkı, Adım 2 ağına vade=1 yükümlülük olarak girer (mevcut ag + calistir).
(b) Stok büyümesi: rev_adim3 bandı (yok, min, medyan, azami) ve örneklem dışı stres = 2×azami.
(c) Seyrek ağ: Adım 1 maskesi + rev_adim1.ras, sonra Adım 2 köprüsü.
(d) Birleşik: kur %30, faiz %55, azami çeyreklik büyüme.

Etiket: kur oranı ve büyüme patikası varsayım (aday); stok, YP payı ve kilitli hücre ölçüm türevi (kanıt).
Çıktı: rev_sok_sonuc.json, rev_sok_sonuc.csv. YAPILABILIRLIK.md içine 'Şok testleri' bölümünü yazar.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent
sys.path.insert(0, str(KOK))
sys.path.insert(0, str(KOK / "mahsup"))

import numpy as np
import adim1_nace as a1
import adim2_nace_ag as a2
import adim3_faiz_durma as a3
import rev_adim1
import rev_adim2 as r2
import rev_adim3 as r3
import rev_veri as rv
import tek_sistem_kademe as tk
from mahsuplasma.ag import Firma
from mahsuplasma.model import Parametreler, calistir

KUR = (0, 10, 20, 30, 50)
KAPPA = (0.25, 0.5, 1.0)
R_AD = ("dusus", "sabit", "yuksek")
G_AD = ("sifir", "min", "medyan", "max", "stres")
YOGUNLUK = (0.25, 0.5, 0.75, 1.0)
TOHUM = 30


def degerle(s0: float, yp: float, delta: float) -> tuple[float, float]:
    """TL kısmı sabit, YP kısmı (1+δ) ile değerlenir. Yeni stok ve yeni YP payı."""
    carp = 1.0 + yp * delta
    return s0 * carp, (yp * (1.0 + delta) / carp if carp else yp)


def _gsyh() -> dict[int, float]:
    out = {}
    for r in csv.DictReader((KOK / "gsyh_pay.csv").open(encoding="utf-8-sig")):
        y, g = int(r["yil"]), float(r["gsyh_milyar_TL"])
        if y in out and abs(out[y] - g) > 1e-6:
            raise ValueError(f"GSYH {y} senaryolar arasında ayrışıyor")
        out[y] = g
    return out


def _kopru_kilit() -> list[dict]:
    rows = list(csv.DictReader((KOK / "rev_adim2.csv").open(encoding="utf-8-sig")))
    sec = []
    for et in ("olcum", "lambda*_max"):
        r = next(x for x in rows if x["rejim"] == "ceyreklik_akim" and x["lambda_etiket"] == et
                 and x["beta_etiket"] == "tavan" and float(x["holding"]) == 0.5)
        sec.append({"etiket": et, "lambda": round(float(r["lambda"]), 4), "beta": round(float(r["beta"]), 4),
                    "holding": float(r["holding"]), "temerrut": int(float(r["temerrut_sart"])),
                    "kredi": float(r["kredi_sart"])})
    return sec


def yukle() -> dict:
    usd = {r["donem"]: float(r["usd"]) for r in csv.DictReader((KOK / "faiz_kur_ham.csv").open(encoding="utf-8-sig")) if r["usd"]}
    stok = a3.f4_stok()
    nk = r3.fkd()
    yp = {}
    for ay, q in (("2023-12", "2023-Q4"), ("2024-12", "2024-Q4"), ("2025-12", "2025-Q4"), ("2026-03", "2026-Q1")):
        yp[q] = nk[ay] * usd[ay] / 1000 / stok[q]
    rT, rU = r3.aylik("TP.BKR.TRY.1"), r3.aylik("TP.BKR.USD.1")
    qs = sorted(k for k in stok if k >= "2024-Q1")
    gr = [stok[b] / stok[a] - 1 for a, b in zip(qs, qs[1:])][-8:]
    gr_s = sorted(gr)
    G = {"sifir": 0.0, "medyan": gr_s[len(gr_s) // 2], "min": gr_s[0], "max": gr_s[-1]}
    G["stres"] = 2.0 * G["max"]
    b = a1.bilanco()
    personel, calisan = a1.personel_maliyeti(), a1.calisan_sayisi()
    dp = a2.evds_dis_payi()
    dis = float(b["ticari_alacak"].sum()) * dp["alacak_dis_payi"]
    kenar, _ = a1.cekim_kenarlari(b, dis_brut_borc=dis)
    p24 = rv.nace_panel()
    p24 = p24[p24.yil == 2024].set_index("nace")
    dpo = (p24.tb_kv / p24.net_satis * 365).to_dict()
    phi = {k: min(1.0, 91.25 / v) if v and v > 0 else 1.0 for k, v in dpo.items()}
    banka = b["banka_kredisi"].astype(float)
    if float(banka.sum()) <= 0:
        raise ValueError("SB banka kredisi toplamı yok; F.4 farkı dağıtılamaz")
    pay = (banka / banka.sum()).to_dict()
    fg = json.loads((KOK / "adim3_faiz_durma_sonuc.json").read_text(encoding="utf-8"))["psi"]["finansman_gideri_2024"]
    a3b = json.loads((KOK / "rev_adim3_sonuc.json").read_text(encoding="utf-8"))
    return {"s0": stok["2026-Q1"], "yp": yp["2026-Q1"], "yp_yayin": round(yp["2026-Q1"], 4),
            "rT": rT[max(rT)], "rU": rU[max(rU)], "G": G, "b": b, "personel": personel, "calisan": calisan,
            "dis": dis, "kenar": kenar, "phi": phi, "pay": pay, "fg": float(fg), "gsyh": _gsyh(),
            "kopru_kilit": _kopru_kilit(), "fg_ust": float(a3b["kappa1_oran_FG2024_2029_bandi"][1]),
            "k2": next(x for x in tk.PENCERELER if x.kod == "K2_stok"),
            "don": list(tk._iter_donem(tk.DONEM_BAS, tk.DONEM_SON))}


def _rpat(ad: str, donem: str, rT: float) -> float:
    y, q = int(donem[:4]), int(donem[-1])
    t = (y - 2026) * 4 + q - 3  # rev_adim3: 2026-Q3 = 0
    if ad == "sabit":
        return rT
    if ad == "dusus":
        return max(30.0, rT - (rT - 30.0) * t / 9)
    if ad == "yuksek":
        return 55.0
    raise ValueError(ad)


def faiz_yillik(kur_yuzde: int, g: float, rad: str, kappa: float, girdi: dict) -> dict[str, float]:
    """rev_adim3 satır 62–66. S0 ve YP payı kur şokuyla değerlenmiş stoktan gelir; ψ yok."""
    delta = kur_yuzde / 100
    s0, s_yp = degerle(girdi["s0"], girdi["yp"], delta)
    yl: dict[str, float] = {}
    for i, d in enumerate(girdi["don"]):
        S = s0 * (1 + g) ** (i + 2)
        D = kappa * tk.uygulama_orani(d, girdi["k2"]) * S
        I = D * ((1 - s_yp) * _rpat(rad, d, girdi["rT"]) + s_yp * girdi["rU"]) / 400
        yl[d[:4]] = yl.get(d[:4], 0.0) + I
    return yl


def _faiz_satir(kur_yuzde: int, gad: str, g: float, rad: str, kappa: float, girdi: dict) -> dict:
    yl = faiz_yillik(kur_yuzde, g, rad, kappa, girdi)
    i29, i31 = round(yl["2029"], 1), round(yl["2031"], 1)
    g29, g31 = girdi["gsyh"][2029], girdi["gsyh"][2031]
    return {"kur_yuzde": kur_yuzde, "g": gad, "r": rad, "kappa": kappa,
            "I_2029": i29, "I_2031": i31,
            "pay_2029": round(100 * yl["2029"] / g29, 2), "pay_2031": round(100 * yl["2031"] / g31, 2),
            "oran_FG_2029": round(yl["2029"] / girdi["fg"], 2),
            "nl_F": i29, "nl_karsi": -i29, "nl_toplam": 0.0}


def artis_stok(kur_yuzde: int, girdi: dict) -> float:
    return girdi["s0"] * girdi["yp"] * (kur_yuzde / 100)


def ag_kur(kur_yuzde: int, lam: float, girdi: dict, kenar: list | None = None):
    """Çeyreklik Adım 2 ağı. Kur farkı, SB banka kredisi paylarıyla BANKA'ya vade=1 borçtur.
    δ=0 iken düğüm eklenmez; kilitli ağ ile aynı kalır. Vade kırılımı ölçülmedi (aday)."""
    g = r2.ag(girdi["b"], girdi["kenar"] if kenar is None else kenar, girdi["personel"], girdi["calisan"],
              lam, girdi["dis"], girdi["phi"], 4)
    artis = artis_stok(kur_yuzde, girdi)
    if artis <= 0:
        return g, 0.0
    g.firma_ekle(Firma("BANKA", "holding"))
    kalem = [(k, float(sh)) for k, sh in girdi["pay"].items() if sh > 0]
    dolu = 0.0
    for k, sh in kalem[:-1]:
        t = sh * artis
        g.borc_ekle(k, "BANKA", t, vade=1)
        dolu += t
    g.borc_ekle(kalem[-1][0], "BANKA", artis - dolu, vade=1)
    return g, artis


def kopru_olc(kur_yuzde: int, lam: float, beta: float, girdi: dict, kenar: list | None = None) -> dict:
    g, artis = ag_kur(kur_yuzde, lam, girdi, kenar)
    p = Parametreler(holding_odeme_orani=0.5, sart_kaldiraci=True, ucret_gecis_beta=beta)
    a = calistir(g, p)["asamalar"]["4_sart_kaldiraci"]
    kenar_top = sum(b.tutar for b in g.borclar if b.alacakli == "BANKA")
    return {"temerrut": int(a["temerrut_sayisi"]), "kredi": float(a["kredi_ihtiyaci"]),
            "artis": artis, "kenar_top": kenar_top}


def _matris(girdi: dict):
    nodes = list(girdi["b"].index) + [a2.DIS]
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    W = np.zeros((n, n))
    for e in girdi["kenar"]:
        W[idx[e["borclu"]], idx[e["alacakli"]]] += float(e["milyar_tl"])
    return nodes, W, W.sum(1), W.sum(0)


def seyrek_kenar(girdi: dict, yogunluk: float, tohum: int) -> list[dict] | None:
    """rev_adim1.seyrek ile aynı maske: yoğunluk, tohum, DIŞ her düğüme bağlı; sonra aynı RAS."""
    nodes, W, tb, ta = _matris(girdi)
    n = len(nodes)
    rng = np.random.default_rng(tohum)
    M = (rng.random((n, n)) < yogunluk) if yogunluk < 1 else np.ones((n, n), bool)
    np.fill_diagonal(M, False)
    M[:, -1] |= True
    M[-1, :] |= True
    Ws = rev_adim1.ras(W * M, tb, ta)
    if abs(Ws.sum() - tb.sum()) / tb.sum() > 1e-3:
        return None
    out = []
    for i in range(n):
        for j in range(n):
            if Ws[i, j] > 1e-8:
                out.append({"borclu": nodes[i], "alacakli": nodes[j], "milyar_tl": float(Ws[i, j])})
    return out


def _medyan(xs: list[float]):
    s = sorted(xs)
    return s[len(s) // 2]


def _esik(yol: list[dict], olcut) -> int | None:
    for h in yol:
        if olcut(h):
            return int(h["kur_yuzde"])
    return None


def hesapla() -> dict:
    girdi = yukle()
    gsyh = girdi["gsyh"]
    faiz = [_faiz_satir(k, gad, girdi["G"][gad], rad, kap, girdi)
            for k in KUR for gad in G_AD for rad in R_AD for kap in KAPPA]
    kilit = girdi["kopru_kilit"]
    beta = kilit[0]["beta"]
    kopru = []
    for sec in kilit:
        for k in KUR:
            o = kopru_olc(k, sec["lambda"], beta, girdi)
            art = round(o["artis"], 1)
            kopru.append({"etiket": sec["etiket"], "lambda": sec["lambda"], "kur_yuzde": k,
                          "temerrut": o["temerrut"], "kredi": round(o["kredi"], 1),
                          "artis": art, "nl_F": -art, "nl_karsi": art, "nl_toplam": 0.0,
                          "kenar_top": round(o["kenar_top"], 4)})
    esik_yol = []
    for sec in kilit:
        for k in range(0, 11):
            o = kopru_olc(k, sec["lambda"], beta, girdi)
            esik_yol.append({"etiket": sec["etiket"], "lambda": sec["lambda"], "kur_yuzde": k,
                             "temerrut": o["temerrut"], "kredi": round(o["kredi"], 1)})
    band_ust = kilit[0]["kredi"]  # λ=1 yayımlanmış üst uç
    esik = {}
    for sec in kilit:
        yol = [h for h in esik_yol if h["etiket"] == sec["etiket"]]
        kop_y = _esik(yol, lambda h, u=band_ust: h["kredi"] > u + 0.05)
        tem_y = _esik(yol, lambda h, t0=sec["temerrut"]: h["temerrut"] > t0)
        oku = lambda y, alan: None if y is None else next(h[alan] for h in yol if h["kur_yuzde"] == y)
        esik[sec["etiket"]] = {
            "kopru_yuzde": kop_y, "temerrut_yuzde": tem_y,
            "kopru_kredi": oku(kop_y, "kredi"), "temerrut_adet": oku(tem_y, "temerrut"),
            "kredi_0": yol[0]["kredi"], "temerrut_0": yol[0]["temerrut"]}
    hucre = lambda k, gad, rad, kap: next(h for h in faiz if h["kur_yuzde"] == k and h["g"] == gad and h["r"] == rad and h["kappa"] == kap)
    tavan = hucre(0, "max", "yuksek", 1.0)
    faiz_esik = None
    for k in range(0, 11):
        oran = round(faiz_yillik(k, girdi["G"]["max"], "yuksek", 1.0, girdi)["2029"] / girdi["fg"], 2)
        if oran > girdi["fg_ust"]:
            faiz_esik = k
            break
    seyrek = []
    for d in YOGUNLUK:
        n_tohum = 1 if d >= 1 else TOHUM
        olcum = []
        for s in range(n_tohum):
            ken = seyrek_kenar(girdi, d, s)
            if ken is None:
                continue
            o = kopru_olc(0, 1.0, beta, girdi, ken)
            olcum.append({"tohum": s, "temerrut": o["temerrut"], "kredi": round(o["kredi"], 1)})
        if not olcum:
            raise RuntimeError(f"seyrek ağ yoğunluk {d} için hiç tohum oturmadı")
        seyrek.append({"yogunluk": d, "n": len(olcum),
                       "temerrut_min": min(x["temerrut"] for x in olcum),
                       "temerrut_medyan": _medyan([x["temerrut"] for x in olcum]),
                       "temerrut_max": max(x["temerrut"] for x in olcum),
                       "kredi_min": min(x["kredi"] for x in olcum),
                       "kredi_medyan": _medyan([x["kredi"] for x in olcum]),
                       "kredi_max": max(x["kredi"] for x in olcum)})
    stres = {"k025": hucre(30, "max", "yuksek", 0.25), "k1": hucre(30, "max", "yuksek", 1.0)}
    karar = _karar(esik, seyrek, stres, girdi, faiz_esik, tavan)
    g_yayin = {k: round(v, 6) for k, v in girdi["G"].items()}
    sonuc = {
        "faz": "rev sok",
        "girdi": {"S0_2026Q1": round(girdi["s0"], 4), "yp_2026Q1": girdi["yp_yayin"], "yp_ham": round(girdi["yp"], 6),
                  "r_TL": girdi["rT"], "r_USD": girdi["rU"], "g_ceyreklik": g_yayin,
                  "gsyh_2029": gsyh[2029], "gsyh_2031": gsyh[2031], "FG_2024": girdi["fg"],
                  "fg_ust_yayin": girdi["fg_ust"], "beta": beta,
                  "banka_sb_2024": round(float(girdi["b"]["banka_kredisi"].sum()), 1)},
        "etiketler": {
            "yp_payi": "kanıt, olcum_turevi (FKDFDVY×kur / ZP34, 2026-Q1; yayında 4 ondalık)",
            "S0": "kanıt, EVDS F.4 2026-Q1",
            "g_sifir_min_medyan_max": "kanıt, olcum_turevi (2024-Q1..2026-Q1 çeyreklik büyüme)",
            "g_stres": "aday, gözlenen azaminin iki katı",
            "r_TL": "aday patika (rev_adim3: düşüş→%30, sabit, %55)",
            "kappa": "aday",
            "kur_yuzde": "aday şok büyüklüğü",
            "faiz_formulu": "kanıt, rev_adim3 sözleşme faizi; ψ uygulanmaz; ΣNL=0 (F +, alacaklı −)",
            "kopru_dagitim": "aday, F.4 değerleme farkı SB 2024 banka kredisi paylarıyla bölünür (kapsam farklı)",
            "kopru_vade": "aday, vade kırılımı kapısı boş; fark bu çeyrekte isteniyor",
            "gsyh_payda": "aday, gsyh_pay.csv reel %3 yolu",
            "seyrek": "kanıt ki mevcut fonksiyonlarla koşulur; yoğunluk aday (rev_adim1)",
        },
        "faiz": faiz,
        "kopru": kopru,
        "esik_kopru": esik,
        "esik_faiz_fg_ust_yuzde": faiz_esik,
        "seyrek": seyrek,
        "stres": {"tanim": "kur %30 + r %55 + g azami", "hucre": stres,
                  "k1_delta0_oran_FG": tavan["oran_FG_2029"]},
        "karar": karar,
    }
    return sonuc


def _karar(esik, seyrek, stres, girdi, faiz_esik, tavan) -> dict:
    s25 = next(x for x in seyrek if x["yogunluk"] == 0.25)
    s1 = next(x for x in seyrek if x["yogunluk"] == 1.0)
    k1 = stres["k1"]
    k025 = stres["k025"]
    return {
        "adim1": {"cevirme": False,
                  "neden": "Karar zaten yoğunluğa koşullu. Kur ve stok büyümesi Adım 1 mahsup oranına girmez."},
        "adim2": {"kosul_bozulur": True,
                  "kopru_lambda1_yuzde": esik["olcum"]["kopru_yuzde"],
                  "temerrut_lambda1_yuzde": esik["olcum"]["temerrut_yuzde"],
                  "seyrek_0_25_kosulsuz": s25["temerrut_min"] > 3 or s25["kredi_min"] > girdi["kopru_kilit"][0]["kredi"] + 0.05,
                  "yogunluk_1_kilit": s1["temerrut_medyan"] == 3 and abs(s1["kredi_medyan"] - girdi["kopru_kilit"][0]["kredi"]) < 0.05,
                  "neden": "Koşul, çeyreklik köprünün yayımlanmış üst ucu ve 3 kısım temerrüttür. Tablo cümlesi koşullu kalır; eşik aşılınca koşul tutmaz."},
        "adim3": {"kosul_bozulur_stres": True,
                  "faiz_fg_ust_yuzde": faiz_esik,
                  "stres_k1_oran_FG": k1["oran_FG_2029"],
                  "stres_k025_oran_FG": k025["oran_FG_2029"],
                  "delta0_tavan_oran_FG": tavan["oran_FG_2029"],
                  "neden": "Koşul küçük κ ve düşüş patikasıdır. Birleşik stres %55 ve κ=1 kullanır. κ=1 azami büyüme hücresi kur eşiğinde yayımlanmış FG üst bandını aşar."},
        "adim4": {"cevirme": False, "kanal": False, "neden": "Bu şokların Adım 4 kredi katsayısına kanalı yok."},
        "adim45": {"cevirme": False, "kanal": False, "neden": "Parite plasebo; kur şoku birim dönüşümüne girmez."},
        "adim5": {"cevirme": False, "kanal": False, "neden": "Kira bandının kur, faiz veya F.4 büyümesi girdisi yok."},
    }


def _tr(x, n=1) -> str:
    neg = float(x) < 0
    mag = abs(float(x))
    if n <= 0:
        whole, frac = f"{mag:.0f}", ""
    else:
        whole, frac = f"{mag:.{n}f}".split(".")
    grup = []
    while whole:
        grup.append(whole[-3:])
        whole = whole[:-3]
    out = ".".join(reversed(grup))
    if frac:
        out += "," + frac
    return ("-" if neg else "") + out


def _bolum(s: dict) -> str:
    g = s["girdi"]
    e = s["esik_kopru"]["olcum"]
    em = s["esik_kopru"]["lambda*_max"]
    sy = {x["yogunluk"]: x for x in s["seyrek"]}
    st = s["stres"]["hucre"]
    k025 = lambda gad, rad, k=0: next(h for h in s["faiz"] if h["kur_yuzde"] == k and h["g"] == gad and h["r"] == rad and h["kappa"] == 0.25)
    k1 = lambda gad, rad, k=0: next(h for h in s["faiz"] if h["kur_yuzde"] == k and h["g"] == gad and h["r"] == rad and h["kappa"] == 1.0)
    kop = {(h["etiket"], h["kur_yuzde"]): h for h in s["kopru"]}
    L = ["## Şok testleri", "",
         "Çalıştır: `python3 rev_sok.py` (zincire bağlı). Çıktı: `rev_sok_sonuc.json`, `rev_sok_sonuc.csv`. "
         "Kilitli formül ve kilitli dosya değişmez. `kanıt` ölçülen veya mevcut formülün bu girdilerle ürettiği sayıdır; `aday` şok büyüklüğü, vade veya kapsam taşımasıdır.", "",
         f"Kur, F.4 2026-Q1 stokuna ({_tr(g['S0_2026Q1'], 1)} milyar TL) YP payı %{_tr(100 * g['yp_2026Q1'], 2)} ile uygulanır (kanıt, ölçüm türevi). "
         f"Yeni stok S = S0·(1+yp·δ), yeni pay yp·(1+δ)/(1+yp·δ). δ ızgarası 0/10/20/30/50 adaydır. "
         "Faiz, `rev_adim3` sözleşme formülüdür; ψ yok; F'ye yazılan faiz alacaklıdan düşülür, ΣNL = 0 (kanıt, kimlik).", "",
         f"Köprüye yalnız değerleme farkı girer. Dağılım, Sektör Bilançoları 2024 banka kredisinin kısım payıdır "
         f"(toplam {_tr(g['banka_sb_2024'], 1)} milyar TL; F.4 ile aynı stok değil, aday). "
         "Vade kırılımı kapısı boş olduğu için fark bu çeyrekte isteniyor (aday). δ=0 ağda ek düğüm yok.", "",
         f"Büyüme bandı çeyreklik: yok 0, min %{_tr(100 * g['g_ceyreklik']['min'], 2)}, medyan %{_tr(100 * g['g_ceyreklik']['medyan'], 2)}, "
         f"azami %{_tr(100 * g['g_ceyreklik']['max'], 2)} (kanıt, ölçüm türevi). Stres = azaminin iki katı, %{_tr(100 * g['g_ceyreklik']['stres'], 2)} (aday). "
         f"GSYH paydası 2029 {_tr(g['gsyh_2029'], 1)}, 2031 {_tr(g['gsyh_2031'], 1)} (aday, reel %3 yolu).", "",
         f"Kur, düz stok ve sabit faiz, 2029 sözleşme faizi: κ=0,25 için δ=0 {_tr(k025('sifir','sabit')['I_2029'])} (%{_tr(k025('sifir','sabit')['pay_2029'], 2)} GSYH), "
         f"δ=30 {_tr(k025('sifir','sabit', 30)['I_2029'])}, δ=50 {_tr(k025('sifir','sabit', 50)['I_2029'])}; "
         f"κ=1 için δ=0 {_tr(k1('sifir','sabit')['I_2029'])}, δ=50 {_tr(k1('sifir','sabit', 50)['I_2029'])}. "
         "USD stok faizi TL faizinin altında olduğu için kur, tutarı stok kadar şişirmez; yön yine artıştır.", "",
         f"Büyüme, δ=0 ve sabit faiz, 2029: κ=0,25 yok {_tr(k025('sifir','sabit')['I_2029'])} (%{_tr(k025('sifir','sabit')['pay_2029'], 2)}), "
         f"medyan {_tr(k025('medyan','sabit')['I_2029'])} (%{_tr(k025('medyan','sabit')['pay_2029'], 2)}), "
         f"azami {_tr(k025('max','sabit')['I_2029'])} (%{_tr(k025('max','sabit')['pay_2029'], 2)}), "
         f"stres {_tr(k025('stres','sabit')['I_2029'])} (%{_tr(k025('stres','sabit')['pay_2029'], 2)}). "
         f"Aynı sıra κ=1: {_tr(k1('sifir','sabit')['I_2029'])}, {_tr(k1('medyan','sabit')['I_2029'])}, {_tr(k1('max','sabit')['I_2029'])}, {_tr(k1('stres','sabit')['I_2029'])}.", "",
         f"Çeyreklik köprü, λ=1, β tavan: δ=0 iken {_tr(kop[('olcum', 0)]['kredi'])} milyar TL ve {kop[('olcum', 0)]['temerrut']} kısım "
         f"(kilitli hücre, kanıt). δ=10 {_tr(kop[('olcum', 10)]['kredi'])} ve {kop[('olcum', 10)]['temerrut']} kısım; "
         f"δ=30 {_tr(kop[('olcum', 30)]['kredi'])} ve {kop[('olcum', 30)]['temerrut']} kısım; "
         f"δ=50 {_tr(kop[('olcum', 50)]['kredi'])} ve {kop[('olcum', 50)]['temerrut']} kısım. "
         f"λ=1'de köprü yayımlanmış üst ucu kur %{_tr(e['kopru_yuzde'], 0)} iken aşar (kredi {_tr(e['kopru_kredi'])}). "
         f"Temerrüt 3'ün üstüne kur %{_tr(e['temerrut_yuzde'], 0)} iken çıkar ({e['temerrut_adet']} kısım). "
         f"λ* üst uçta (nakit 1,0471) köprü üst ucu kur %{_tr(em['kopru_yuzde'], 0)} (kredi {_tr(em['kopru_kredi'])}), "
         f"temerrüt artışı kur %{_tr(em['temerrut_yuzde'], 0)} ({em['temerrut_adet']} kısım).", "",
         "Seyrek ağ Adım 2'de koşulur: Adım 1 ile aynı kenar maskesi ve `rev_adim1.ras`, sonra mevcut `ag` ve `calistir`. "
         f"Yoğunluk 1, kilitli hücreyi yeniden üretir ({sy[1.0]['temerrut_medyan']} kısım, kredi {_tr(sy[1.0]['kredi_medyan'])}). "
         f"Yoğunluk 0,25, 30 tohum: temerrüt {sy[0.25]['temerrut_min']}–{sy[0.25]['temerrut_max']} "
         f"(ortanca {sy[0.25]['temerrut_medyan']}), köprü {_tr(sy[0.25]['kredi_min'])}–{_tr(sy[0.25]['kredi_max'])} "
         f"(ortanca {_tr(sy[0.25]['kredi_medyan'])}). Kur şoku olmadan da koşul bozulur. "
         "Adım 1'deki LP silinen oranı ile bu köprü aynı sayı değildir; biri mahsup tavanı, öteki çeyreklik ödeme açığıdır.", "",
         f"Birleşik stres (kur %30, faiz %55, azami büyüme): κ=1 için 2029 faizi {_tr(st['k1']['I_2029'])} milyar TL, "
         f"FG2024'ün {_tr(st['k1']['oran_FG_2029'], 2)} katı, 2029 GSYH'sinin %{_tr(st['k1']['pay_2029'], 2)}'i; "
         f"2031'de {_tr(st['k1']['I_2031'])} (%{_tr(st['k1']['pay_2031'], 2)}). "
         f"κ=0,25'te 2029 {_tr(st['k025']['I_2029'])} (%{_tr(st['k025']['pay_2029'], 2)}), FG katı {_tr(st['k025']['oran_FG_2029'], 2)}. "
         f"κ=1 ve azami büyüme, kur sıfırken FG katı yayımlanmış üst uçtur ({_tr(s['stres']['k1_delta0_oran_FG'], 2)}). "
         f"Bu uç, kur %{_tr(s['esik_faiz_fg_ust_yuzde'], 0)} iken aşılır.", "",
         "Karar cümleleri tabloda durur; bu şoklar onları 'yapılamaz' diye yeniden yazmaz. "
         "Adım 2'nin koşulu tam ağda kur eşiğinde, seyrek ağda kur olmadan bozulur. "
         "Adım 3'ün koşulu (küçük κ ve düşüş patikası) birleşik streste tutmaz; κ=1 tavan hücresi kur eşiğinde yayımlanmış FG bandının dışına çıkar. "
         "Adım 1 kararı zaten yoğunluğa bağlıdır. Adım 4, 4.5 ve 5 için bu şokların kanalı yoktur.", ""]
    return "\n".join(L)


def _csv_satir(s: dict) -> list[dict]:
    alan_bos = {"kur_yuzde": "", "g": "", "r": "", "kappa": "", "lambda": "", "yogunluk": "",
                "I_2029": "", "I_2031": "", "pay_2029": "", "pay_2031": "", "oran_FG_2029": "",
                "kredi": "", "temerrut": "", "artis": "", "nl_F": "", "nl_karsi": "", "nl_toplam": ""}
    out = []
    for h in s["faiz"]:
        out.append({**alan_bos, "blok": "faiz", **{k: h[k] for k in
                   ("kur_yuzde", "g", "r", "kappa", "I_2029", "I_2031", "pay_2029", "pay_2031", "oran_FG_2029", "nl_F", "nl_karsi", "nl_toplam")}})
    for h in s["kopru"]:
        out.append({**alan_bos, "blok": "kopru", "kur_yuzde": h["kur_yuzde"], "lambda": h["lambda"],
                    "kredi": h["kredi"], "temerrut": h["temerrut"], "artis": h["artis"],
                    "nl_F": h["nl_F"], "nl_karsi": h["nl_karsi"], "nl_toplam": h["nl_toplam"]})
    for h in s["seyrek"]:
        out.append({**alan_bos, "blok": "seyrek", "yogunluk": h["yogunluk"], "lambda": 1.0, "kur_yuzde": 0,
                    "kredi": h["kredi_medyan"], "temerrut": h["temerrut_medyan"]})
    return out


def _yaz_md(metin: str) -> None:
    p = KOK / "YAPILABILIRLIK.md"
    t = p.read_text(encoding="utf-8")
    govde = metin if metin.endswith("\n") else metin + "\n"
    bas = t.find("## Şok testleri")
    if bas >= 0:
        t = t[:bas].rstrip() + "\n\n" + govde
    else:
        t = t.rstrip() + "\n\n" + govde
    p.write_text(t, encoding="utf-8")


def main() -> dict:
    s = hesapla()
    (KOK / "rev_sok_sonuc.json").write_text(json.dumps(s, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    alan = ["blok", "kur_yuzde", "g", "r", "kappa", "lambda", "yogunluk", "I_2029", "I_2031", "pay_2029", "pay_2031",
            "oran_FG_2029", "kredi", "temerrut", "artis", "nl_F", "nl_karsi", "nl_toplam"]
    with (KOK / "rev_sok_sonuc.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=alan, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        for row in _csv_satir(s):
            w.writerow({k: row.get(k, "") for k in alan})
    _yaz_md(_bolum(s))
    print(json.dumps({"esik_kopru": s["esik_kopru"], "esik_faiz": s["esik_faiz_fg_ust_yuzde"],
                      "stres": s["stres"], "seyrek": s["seyrek"], "karar_adim2": s["karar"]["adim2"],
                      "karar_adim3": s["karar"]["adim3"]}, ensure_ascii=False, indent=1))
    return s


if __name__ == "__main__":
    main()
