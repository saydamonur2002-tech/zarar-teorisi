"""Zarar Teorisi - stok-akış (SFC) modeli: temiz panel, akış (işlem + değerleme), matrisler, simülatör.

Çalıştırma: python akis_model.py   (finansal_hesaplar_uzun.csv ve akim_ve_tcmb_ham.csv gerekir)

Düzeltilen anomaliler (hepsi kodda işaretli):
  A1  EVDS S.2 (D) kalemleri Türkiye'ye göre ters etiketli  -> D çevrilir (stok ve akımda ayrı doğrulanır).
  A2  B (S.12) TCMB'yi içeriyor, kuramda TCMB kamu ile birlikte -> B' = S.12 - S.121, K' = S.13 + S.121.
  A3  2010-2020 D ile yerleşikler arası stok uyumsuzluğu (D'nin %2-12'si) -> 6. "U" (uyumsuzluk) haznesi
      enstrüman bazında kapatır; matrislere girmez ama raporlanır.
  A4  2010-2014 yalnızca yıl sonu -> akış/değerleme yalnızca ardışık çeyreklerde (2015-Q1+) hesaplanır.
  A5  K'nin özkaynak yükümlülüğü yok -> G matrisinde K satırı "kâr K'da kalır" (G[K,K]=1); vergi/transfer
      kanalı finansal hesaplarda görünmediği için ayrı bütçe verisiyle eklenecek (açık madde).
  A6  Toplulaştırılmış L enstrüman heterojenliğini gizliyor (yabancı para kredisi D'ye, TL kredisi bankaya)
      -> enstrüman bazlı L^m matrisleri üretilir; simülatör şoku enstrümana göre alır.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from kalibre_matris import INSTR, LOSS_INSTR, GAIN_INSTR, exposure

DIR = Path(__file__).parent
SEC = ["H", "F", "B", "K", "D"]
ALL = SEC + ["U"]
IDX = {s: i for i, s in enumerate(SEC)}
STOCK_GRP = {"H": "71014", "NPISH": "71015", "F": "71011", "B": "71012", "K": "71013", "D": "7102"}


# ------------------------------------------------------------------ veri
def _zp(s):
    return s.str.extract(r"ZP(\d+)$")[0].astype(int)


def load():
    st = pd.read_csv(DIR / "finansal_hesaplar_uzun.csv", dtype={"Donem": str})
    st["zp"] = _zp(st["Seri"])
    fl = pd.read_csv(DIR / "akim_ve_tcmb_ham.csv", dtype={"Donem": str})
    fl["zp"] = _zp(fl["Seri"])
    tc_st = fl[fl.Grup == "bie_finhestnks710121"]
    tc_fl = fl[fl.Grup == "bie_finhestnks610121"]
    fmap = {"bie_finhestnks61011": "F", "bie_finhestnks61012": "B", "bie_finhestnks61013": "K",
            "bie_finhestnks61014": "H", "bie_finhestnks61015": "NPISH", "bie_finhestnks6102": "D"}
    flow = fl[fl.Grup.isin(fmap)].assign(Hazne=lambda d: d.Grup.map(fmap))
    stock = st[st.Hazne != "TOPLAM"]

    def table(df):
        return {(r.Hazne, r.Donem, r.zp): r.Deger for r in df.itertuples()}

    def tc(df):
        return {(r.Donem, r.zp): r.Deger for r in df.itertuples()}

    return table(stock), table(flow), tc(tc_st), tc(tc_fl)


def panel(tab, tcmb, period, flip_d=True, move_tcmb=True):
    """-> A[m,s], Y[m,s] (5 hazne, U hariç). A = varlık, Y = yükümlülük, enstrüman satırları INSTR sırası."""
    m = len(INSTR)
    A, Y = np.zeros((m, 5)), np.zeros((m, 5))
    for k, (name, (za, zl)) in enumerate(INSTR.items()):
        def g(h, z):
            return tab.get((h, period, z), np.nan)
        for h, s in [("H", "H"), ("NPISH", "H"), ("F", "F"), ("B", "B"), ("K", "K"), ("D", "D")]:
            a, y = g(h, za), g(h, zl)
            if np.isnan(a) or np.isnan(y):
                continue
            if h == "D" and flip_d:
                a, y = y, a
            A[k, IDX[s]] += a
            Y[k, IDX[s]] += y
        if move_tcmb:
            ta, ty = tcmb.get((period, za), np.nan), tcmb.get((period, zl), np.nan)
            if not (np.isnan(ta) or np.isnan(ty)):
                A[k, IDX["B"]] -= ta
                Y[k, IDX["B"]] -= ty
                A[k, IDX["K"]] += ta
                Y[k, IDX["K"]] += ty
    return A, Y


def close_with_U(A, Y):
    """Enstrüman bazında kalıntıyı U haznesine yazar: kalıntı>0 varlık fazlası -> U yükümlülüğü."""
    r = A.sum(axis=1) - Y.sum(axis=1)
    AU, YU = np.maximum(-r, 0), np.maximum(r, 0)
    return AU, YU, r


# ------------------------------------------------------------------ matrisler
def mat(A, Y, names):
    """E toplamı -> satır = borçlu j, sütun = alacaklı i (satır normalize)."""
    E = sum(exposure(A[list(INSTR).index(n)], Y[list(INSTR).index(n)]) for n in names)
    col = E.sum(axis=0)
    M = np.zeros_like(E)
    for j in range(5):
        if col[j] > 1e-9:
            M[j] = E[:, j] / col[j]
    return M


def L_G(A, Y):
    L = mat(A, Y, LOSS_INSTR)
    G = mat(A, Y, GAIN_INSTR)
    # A5: K'nin özkaynak yükümlülüğü yoksa kâr K'da kalır (finansal kanal yok)
    for j in range(5):
        if G[j].sum() < 1e-9:
            G[j, j] = 1.0
    return L, G


def Lm(A, Y):
    return {n: mat(A, Y, [n]) for n in INSTR}


# ------------------------------------------------------------------ simülatör
def simulate(L, G, nfp, x, lam=0.5, kappa=0.1, hops=80):
    """x: sektör sonuç vektörü (+kâr, -zarar, bin TL). Zarar L ile, kâr G ile yayılır.
    Her adımda zararın yerleşik alacaklıya geçen kısmı lam, (1-lam) tamponda emilir; kendi payı
    min(1, kappa*max(NFP_j,0)/|x_j|) kadarı sahibinde kalır. Dönüş: sektör etkisi (bin TL), D payı."""
    nfp = np.asarray(nfp, float)
    x = np.asarray(x, float)
    impact = np.zeros(5)
    cur = x.copy()
    for h in range(hops):
        nxt = np.zeros(5)
        for j in range(5):
            if cur[j] == 0:
                continue
            if cur[j] < 0:  # zarar
                own = min(1.0, kappa * max(nfp[j], 0) / abs(cur[j])) if h == 0 else 0.0
                impact[j] += own * cur[j]
                rest = (1 - own) * cur[j]
                for i in range(5):
                    if i == j or L[j, i] == 0:
                        continue
                    if i == IDX["D"]:
                        impact[i] += L[j, i] * rest  # D soğurucu
                    else:
                        nxt[i] += lam * L[j, i] * rest
                        impact[i] += (1 - lam) * L[j, i] * rest
            else:  # kâr: sahiplerine
                for i in range(5):
                    impact[i] += G[j, i] * cur[j]
        cur = nxt
    return impact


# ------------------------------------------------------------------ ana
def main():
    stab, ftab, tcs, tcf = load()
    periods = sorted({k[1] for k in stab})
    q = [p for p in periods if p >= "2015-Q1"]
    out = {}

    # A1: D çevirme doğrulaması (akımda ayrı)
    def bal(tab, tc, p, flip):
        A, Y = panel(tab, tc, p, flip_d=flip)
        return np.round(A.sum(axis=1) / np.where(Y.sum(axis=1) == 0, np.nan, Y.sum(axis=1)), 3)

    out["A1_stok_oran_2026Q1_D_cevrilmis"] = bal(stab, tcs, "2026-Q1", True).tolist()
    out["A1_akim_oran_2026Q1_D_cevrilmis"] = bal(ftab, tcf, "2026-Q1", True).tolist()
    out["A1_akim_oran_2026Q1_D_cevrilmemis"] = bal(ftab, tcf, "2026-Q1", False).tolist()

    # A3: stok uyumsuzluğu
    rows_u = []
    for p in periods:
        A, Y = panel(stab, tcs, p)
        _, _, r = close_with_U(A, Y)
        rows_u.append({"Donem": p, **{n: r[k] for k, n in enumerate(INSTR)}})
    pd.DataFrame(rows_u).to_csv(DIR / "uyumsuzluk_U_enstruman.csv", index=False, encoding="utf-8-sig")

    # Temiz panel + akış (işlem, değerleme)
    recs = []
    A_prev = Y_prev = None
    names = list(INSTR)
    for idx, p in enumerate(q):
        As, Ys = panel(stab, tcs, p)
        AU, YU, _ = close_with_U(As, Ys)
        Af, Yf = panel(ftab, tcf, p)
        prev = "2014-Q4" if p == "2015-Q1" else q[idx - 1]
        Ap, Yp = panel(stab, tcs, prev)
        AUp, YUp, _ = close_with_U(Ap, Yp)
        R_A = As - Ap - Af
        R_Y = Ys - Yp - Yf
        for k, n in enumerate(names):
            for s in SEC:
                j = IDX[s]
                for taraf, S_, T_, R_ in (("varlik", As, Af, R_A), ("yukumluluk", Ys, Yf, R_Y)):
                    recs.append((p, n, s, taraf, S_[k, j], T_[k, j], R_[k, j]))
            recs.append((p, n, "U", "varlik", AU[k], np.nan, AU[k] - AUp[k]))
            recs.append((p, n, "U", "yukumluluk", YU[k], np.nan, YU[k] - YUp[k]))
    P = pd.DataFrame(recs, columns=["Donem", "Enstruman", "Hazne", "Taraf", "Stok", "Islem", "Degerleme_veya_Degisim"])
    P.to_csv(DIR / "temiz_stok_akis_paneli.csv", index=False, encoding="utf-8-sig")

    # SFC işlem-akış matrisi (satır enstrüman, sütun hazne): net edinim = varlık işlemi - yükümlülük işlemi
    sfc = []
    for p in q:
        Af, Yf = panel(ftab, tcf, p)
        net = Af - Yf
        for k, n in enumerate(names):
            sfc.append({"Donem": p, "Enstruman": n, **{s: net[k, IDX[s]] for s in SEC}, "satir_toplam": net[k].sum()})
        sfc.append({"Donem": p, "Enstruman": "NET_BORCLANMA(NL)", **{s: net[:, IDX[s]].sum() for s in SEC}, "satir_toplam": net.sum()})
    pd.DataFrame(sfc).to_csv(DIR / "sfc_islem_akis_matrisi.csv", index=False, encoding="utf-8-sig")

    # Değerleme transferi: enstrüman bazlı, yükümlülük değerlemesi (zarar) ve alacaklı değerlemesi (kazanç)
    # Homojenlik testi: aynı enstrümanı tutan hazneler benzer değerleme getirisi mi yaşıyor?
    disp = {}
    for n in names:
        rates = []
        for idx, p in enumerate(q):
            sub = P[(P.Donem == p) & (P.Enstruman == n) & (P.Taraf == "varlik") & (P.Hazne.isin(SEC))]
            prev = "2014-Q4" if p == "2015-Q1" else q[idx - 1]
            Ap, _ = panel(stab, tcs, prev)
            k = names.index(n)
            tot = Ap[k].sum()
            if tot <= 0:
                continue
            w = Ap[k] / tot
            r = np.array([sub[sub.Hazne == s].Degerleme_veya_Degisim.iloc[0] / Ap[k, IDX[s]] if Ap[k, IDX[s]] > 0 else np.nan for s in SEC])
            m = (w > 0.05) & ~np.isnan(r)
            if m.sum() >= 2:
                mu = np.average(r[m], weights=w[m])
                rates.append(np.sqrt(np.average((r[m] - mu) ** 2, weights=w[m])))
        disp[n] = float(np.nanmedian(rates)) if rates else None
    out["A6_degerleme_getirisi_medyan_agirlikli_std"] = disp

    # Orantılı dağıtım geriye dönük testi: öngörü_i = (A_i,t-1 / ΣA_t-1) * ΣR_A ; gözlem = R_A,i
    bt = {}
    for n in names:
        k = names.index(n)
        obs, pred = [], []
        for idx, p in enumerate(q):
            prev = "2014-Q4" if p == "2015-Q1" else q[idx - 1]
            Ap, _ = panel(stab, tcs, prev)
            sub = P[(P.Donem == p) & (P.Enstruman == n) & (P.Taraf == "varlik") & (P.Hazne.isin(SEC))].set_index("Hazne").Degerleme_veya_Degisim
            tot = sub.sum()
            if Ap[k].sum() <= 0:
                continue
            for s in SEC:
                obs.append(sub[s] / 1e9)
                pred.append(Ap[k, IDX[s]] / Ap[k].sum() * tot / 1e9)
        obs, pred = np.array(obs), np.array(pred)
        ss = ((obs - obs.mean()) ** 2).sum()
        bt[n] = {"R2": round(float(1 - ((obs - pred) ** 2).sum() / ss), 3) if ss > 0 else None,
                 "korelasyon": round(float(np.corrcoef(obs, pred)[0, 1]), 3)}
    out["A6_orantili_dagitim_testi"] = bt

    # Matrisler (2026-Q1, A2/A5 düzeltmeli) ve zaman serisi
    As, Ys = panel(stab, tcs, "2026-Q1")
    L, G = L_G(As, Ys)
    pd.DataFrame(L, index=SEC, columns=SEC).round(4).to_csv(DIR / "L_v2_2026-Q1.csv", encoding="utf-8-sig")
    pd.DataFrame(G, index=SEC, columns=SEC).round(4).to_csv(DIR / "G_v2_2026-Q1.csv", encoding="utf-8-sig")
    for n, M in Lm(As, Ys).items():
        pd.DataFrame(M, index=SEC, columns=SEC).round(4).to_csv(DIR / f"Lm_{n}_2026-Q1.csv", encoding="utf-8-sig")
    ts = []
    for p in q:
        A_, Y_ = panel(stab, tcs, p)
        L_, G_ = L_G(A_, Y_)
        for j, s in enumerate(SEC):
            ts.append({"Donem": p, "Kaynak": s, **{f"L_{t}": L_[j, i] for i, t in enumerate(SEC)}, **{f"G_{t}": G_[j, i] for i, t in enumerate(SEC)}})
    pd.DataFrame(ts).to_csv(DIR / "matris_v2_zaman_serisi.csv", index=False, encoding="utf-8-sig")

    # Simülatör demosu: firmaya 1 trilyon TL zarar, hane 1 trilyon TL kâr
    nfp = np.array([stab.get(("H", "2026-Q1", 1), 0) + stab.get(("NPISH", "2026-Q1", 1), 0),
                    stab[("F", "2026-Q1", 1)], stab[("B", "2026-Q1", 1)] - tcs[("2026-Q1", 1)],
                    stab[("K", "2026-Q1", 1)] + tcs[("2026-Q1", 1)], stab[("D", "2026-Q1", 1)]])
    out["nfp_2026Q1_trilyonTL"] = dict(zip(SEC, (nfp / 1e9).round(3).tolist()))
    for lam in (0.0, 0.5, 0.8):
        x = np.zeros(5)
        x[IDX["F"]] = -1e9  # -1 trilyon TL (bin TL cinsinden)
        out[f"sim_F_zarar_lam{lam}"] = dict(zip(SEC, (simulate(L, G, nfp, x, lam=lam) / 1e9).round(3).tolist()))
    x = np.zeros(5)
    x[IDX["F"]] = 1e9
    out["sim_F_kar"] = dict(zip(SEC, (simulate(L, G, nfp, x) / 1e9).round(3).tolist()))
    from hane_taksit import ozet as hane_taksit_ozeti
    out["hane_taksit"] = hane_taksit_ozeti()
    from hane_alt import ozet as hane_alt_ozeti
    out["hane_alt"] = hane_alt_ozeti()
    from vys_kanali import ozet as vys_ozeti
    out["vys_kanali"] = vys_ozeti()
    from temerrut_cift_kayit import ozet as cift_kayit_ozeti
    out["temerrut_cift_kayit"] = cift_kayit_ozeti()
    from odemeyen_gosterge import ozet as odemeyen_ozeti
    out["odemeyen_gosterge"] = odemeyen_ozeti()
    from L_cift_kayit import ozet as l_cift_ozeti
    out["L_cift_kayit"] = l_cift_ozeti()
    from dis_borc_artisi import ozet as dis_borc_ozeti
    out["dis_borc_artisi"] = dis_borc_ozeti()
    (DIR / "akis_model_ozeti.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
