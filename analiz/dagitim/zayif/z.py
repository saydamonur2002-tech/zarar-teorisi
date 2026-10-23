# zayif turu: ON_KAYIT_zayif.md ölçütleri. EVDS/EVDS3 yok.
import json, zipfile, io, re
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path("/workspace/analiz/dagitim")
OUT = ROOT / "zayif"
HAM = OUT / "ham"

def gdp_lcu():
    raw = json.loads((HAM / "wb_gdp_lcu.json").read_text())
    rows = raw[1]
    s = pd.Series({int(r["date"]): r["value"] for r in rows if r["value"] is not None})
    return s.sort_index()

def gdp_usd():
    raw = json.loads((HAM / "wb_gdp_usd.json").read_text())
    rows = raw[1]
    return pd.Series({int(r["date"]): r["value"] for r in rows if r["value"] is not None}).sort_index()

def pct_gdp(milyar, gsyh_tl):
    # ON_KAYIT: tutar_milyar × 1000 / (GSYH_TL/1e6) × 100
    return milyar * 1000 / (gsyh_tl / 1e6) * 100

# Hazine payı, nakit yılı. Bin TL tabloları milyar TL'ye çevrildi (÷1000).
# 2014-16: yasal kâr dağıtım tablosu, önceki yıl sütunu (GK'da devredilen). Özkaynak sayfası taramada ayrı okunamadı → SAPMA.
# 2017-18, 2022-25: özkaynak değişim. 2019-21 paylas2 ile aynı, değiştirilmedi.
# 2023 "Diğer" −30.000.000 bin TL deprem bağışı Hazine aktarımı değildir, dahil edilmedi.
TR_MLR = pd.Series({
    2014: 3362239272 / 1e9,          # 3.362.239.272 TL, 2014 denetim kâr dağıtım, 2013 sütunu
    2015: 5801437953 / 1e9,          # 2015 denetim / 2014 faaliyet tablosu 2014 sütunu
    2016: 9303012520 / 1e9,          # 2016 denetim önceki yıl; temiz rakam 2015 faaliyet tablosu
    2017: 6410951 / 1e6,             # 6.410.951 bin TL = 6,411 milyar TL
    2018: 12356541 / 1e6,            # 12.356.541 bin TL
    2019: 37.518596 + 40.769702,    # paylas2, Hazine temettü + Hazine'ye aktarılan
    2020: 39.109540 + 5.349978,
    2021: 30.207403 + 5.576195,
    2022: 50.038000 + 4.304257,     # 2023 yasal İngilizce özkaynak, 2022 sütunu
    2023: 32.618412 + 7.419058,     # 2023 sütunu; 2024 tablosu aynı nakit akışı
    2024: 0.0,                      # özkaynak ve nakit akış tire; zarar yılı, dağıtım yok
    2025: 0.0,
})
TR_KAYNAK = {
    2014: "VERİ yasal kâr dağıtım, GK 17.04.2014",
    2015: "VERİ yasal kâr dağıtım, GK 09.04.2015",
    2016: "VERİ yasal kâr dağıtım, GK 11.04.2016",
    2017: "VERİ 2018 yasal özkaynak",
    2018: "VERİ 2018 yasal özkaynak",
    2019: "VERİ paylas2, 2020 IFRS özkaynak",
    2020: "VERİ paylas2, 2021 yasal özkaynak",
    2021: "VERİ paylas2, 2021 yasal özkaynak",
    2022: "VERİ 2023 yasal özkaynak (İngilizce)",
    2023: "VERİ 2023 yasal özkaynak; deprem bağışı hariç",
    2024: "VERİ 2024 ve 2025 yasal: temettü ve ihtiyat aktarımı tire",
    2025: "VERİ 2025 yasal: temettü ve ihtiyat aktarımı tire",
}

def load_base():
    S1t = pd.read_csv(ROOT / "paylas/tablo_paylas.csv", index_col=0).drop("TOPLAM")
    Y = pd.read_csv(ROOT / "aktor_kanal_yil.csv", index_col=0)
    Y.index = Y.index.astype(int)
    E = pd.read_csv(ROOT / "eksik/yeni_kanallar_yil.csv", index_col=0)
    E.index = E.index.astype(int)
    q = pd.read_csv("/workspace/analiz/kalibre_faiz/ceyrek_veri.csv", index_col=0)
    q["yr"] = q.index.str[:4].astype(int)
    q["dl"] = np.log(q.E).diff()
    return S1t, Y.loc[2014:2025], E.loc[2014:2025], q

def scenario(S1t, Y, E, q, trg):
    ch = ["k1_TL", "k2_kur", "k3_KKM", "k5_senyoraj", "k7_bankaaltin", "k8_swap"]
    yr = q.groupby("yr").agg(
        dl=("dl", "sum"),
        xp=("x", lambda s: s.clip(lower=0).sum()),
        xn=("x", "sum"),
        pi=("pi", "last"),
    )
    yr["rd"] = yr.dl - np.log1p(yr.pi)
    psi = 3.4
    ext = {
        "dusuk(simetrik,k=1)": (yr.xn * psi / 4),
        "orta(asimetrik,k=.5)": 0.5 * psi * yr.xp / 4,
        "yuksek(asimetrik,k=1)": psi * yr.xp / 4,
    }
    beta = {"dusuk(simetrik,k=1)": 0.2, "orta(asimetrik,k=.5)": 0.3, "yuksek(asimetrik,k=1)": 0.45}
    yrs = list(range(2017, 2026))
    rd = yr.rd.loc[yrs]
    par = {"H": "k2_H", "F": "k2_F", "K": "k2_K", "TCMB": "k2_TCMB", "D": "k2_D"}
    p = {a: Y[c].loc[yrs].sum() / rd.sum() for a, c in par.items()}

    def sub(a):
        if a == "H":
            g = ["Hane_alt", "Hane_orta", "Hane_ust"]
            den = S1t.loc[g, "k2_kur"].sum()
            return {x: S1t.loc[x, "k2_kur"] / den for x in g}
        if a == "F":
            g = ["Firma_KOBI", "Firma_BUYUK"]
            den = S1t.loc[g, "k2_kur"].sum()
            return {x: S1t.loc[x, "k2_kur"] / den for x in g}
        return {{"K": "Hazine", "TCMB": "TCMB", "D": "Yurtdisi+artik"}[a]: 1.0}

    rB = pd.Series({2020: 0.001, 2021: 0.059, 2022: 0.061})
    eq = {"dusuk(simetrik,k=1)": 0.07, "orta(asimetrik,k=.5)": 0.085, "yuksek(asimetrik,k=1)": 0.10}
    tc_y = Y["k2_TCMB"].fillna(0) + E["k5_TCMB"].fillna(0) + E["k8_TCMB"].fillna(0)
    out = {}
    for lv in ext:
        ex = ext[lv].reindex(range(2014, 2026)).fillna(0)
        bank = rB * eq[lv] * rd.reindex(rB.index) * 100
        for sc in ["S1", "S2"]:
            T = S1t[ch].copy()
            if sc == "S2":
                T["k1_TL"] = 0
                T["k3_KKM"] = 0
                for a in par:
                    for g, s in sub(a).items():
                        T.loc[g, "k2_kur"] += p[a] * ex.sum() * s
                infl = (beta[lv] * ex / np.log1p(yr.pi).reindex(ex.index)).fillna(0)
                scale = 1 + (E["k5_TCMB"] * infl).sum() / E["k5_TCMB"].sum()
                for g in T.index:
                    T.loc[g, "k5_senyoraj"] = S1t.loc[g, "k5_senyoraj"] * scale
            T["D3_banka_kur"] = 0.0
            T.loc["Banka", "D3_banka_kur"] = bank.sum()
            T.loc["Yurtdisi+artik", "D3_banka_kur"] = -bank.sum()
            T["D2_TCMB_Hazine"] = 0.0
            T.loc["TCMB", "D2_TCMB_Hazine"] = -trg.sum()
            T.loc["Hazine", "D2_TCMB_Hazine"] = trg.sum()
            tcy = tc_y.copy()
            if sc == "S2":
                tcy = tcy + p["TCMB"] * ex
            else:
                tcy = tcy + E["k3_TCMB"].fillna(0)
            tcy = tcy.sub(trg, fill_value=0)
            cap = -tcy.clip(upper=0).sum() if sc == "S2" else 0.0
            T["TCMB_sermaye"] = 0.0
            T.loc["TCMB", "TCMB_sermaye"] = cap
            T.loc["Hazine", "TCMB_sermaye"] = -cap
            T[sc] = T.sum(axis=1)
            out[(lv, sc)] = T
            if sc == "S1":
                out[(lv, "negS1")] = -tcy.clip(upper=0).sum()
                out[(lv, "tcy")] = tcy
        out[(lv, "cap")] = cap
        out[(lv, "ext")] = ex
        out[(lv, "pi")] = yr.pi
    return out, ext, beta

def firma_anahtar():
    z = zipfile.ZipFile(HAM / "panel_2009_2023.zip")
    G = pd.read_csv(z.open("GELTAB.csv"), sep=";", decimal=",", encoding="utf-8-sig", low_memory=False)
    z2 = zipfile.ZipFile(HAM / "panel.zip")
    N = pd.read_csv(z2.open("Panel+Veri/GELTAB.csv"), sep="|", encoding="utf-8-sig", low_memory=False)

    def prep(d, kar, zar):
        n = d["NACE Kodu"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(2).str[:2]
        x = d[(d["Ölçek"] != "GENEL") & ~n.isin(["41", "42", "43", "68"])].copy()
        x["grp"] = np.where(x["Ölçek"] == "BUYUK", "BUYUK", "KOBI")
        x["nk"] = x[kar] - x[zar].abs()
        return x.groupby(["Yıl", "grp"])["nk"].sum().unstack()

    old = prep(G, "    7-Kambiyo Karları", "    4-Kambiyo Zararları (-)")
    new = prep(N, "gt_646_5028_p", "gt_656_5035_p")
    rows = []
    for src, tab in [("panel_2009_2023", old), ("panel_2023_2025", new)]:
        for y in tab.index:
            loss = tab.loc[y].clip(upper=0)
            den = -loss.sum()
            for g in ["BUYUK", "KOBI"]:
                rows.append({
                    "kaynak": src, "yil": int(y), "olcek": g,
                    "net_kambiyo": float(tab.loc[y, g]),
                    "zarar_payi": float((-min(tab.loc[y, g], 0)) / den) if den else np.nan,
                    "etiket": "HESAP",
                })
    R = pd.DataFrame(rows)
    s = old.loc[2014:2023].clip(upper=0).sum()
    share = (s / s.sum())
    return R, float(share["BUYUK"]), float(share["KOBI"]), old, new

def parse_millions_line(line, n=20):
    """TCMB bülten: 392.130 = 392.130 milyar USD (nokta binlik, birim milyon). Son n token yıllık seridir."""
    toks = re.findall(r"-?\d{1,3}(?:\.\d{3})+|-?\d+", line)
    vals = []
    for t in toks[-n:]:
        vals.append(int(t.replace(".", "")) / 1000.0)
    if len(vals) != n:
        raise ValueError(f"beklenen {n} değer, gelen {len(vals)}: {line[:80]}")
    return vals

def uyp_bridge():
    uyp = (ROOT / "eksik/ham/uyp.txt").read_text(errors="replace").splitlines()
    bop = (ROOT / "eksik/ham/bop.txt").read_text(errors="replace").splitlines()

    def find(lines, pred, start=0):
        for i, ln in enumerate(lines):
            if i >= start and pred(ln):
                return i, ln
        raise KeyError(pred)

    _, niip_ln = find(uyp, lambda ln: "-203.274" in ln and "-392.130" in ln)
    i_n = uyp.index(niip_ln)
    _, di_ln = find(uyp, lambda ln: "Doğrudan Yatırımlar" in ln and "95.504" in ln, i_n)
    _, eq_ln = find(uyp, lambda ln: "Hisse senetleri ve Yatırım Fonu Payları" in ln and "33.816" in ln, i_n)
    _, fa_ln = find(bop, lambda ln: "FINANCIAL ACCOUNT" in ln and "-36.515" in ln)
    i_f = bop.index(fa_ln)
    _, di_flow = find(bop, lambda ln: "Net incurrence of liabilities" in ln and "20.185" in ln, i_f)
    _, eq_flow = find(bop, lambda ln: "Equity Securities and Investment Fund Shares" in ln and "1.939" in ln, i_f)
    niip = parse_millions_line(niip_ln)
    di_s = parse_millions_line(di_ln)
    eq_s = parse_millions_line(eq_ln)
    fa = parse_millions_line(fa_ln)
    di_f = parse_millions_line(di_flow)
    eq_f = parse_millions_line(eq_flow)
    years = list(range(2006, 2006 + len(niip)))
    def ser(v):
        return pd.Series(v, index=years[: len(v)])
    N, FA, DI, EQ, DIf, EQf = map(ser, [niip, fa, di_s, eq_s, di_f, eq_f])
    rows = []
    g = gdp_usd()
    for t in range(2014, 2026):
        dN = N[t] - N[t - 1]
        dDI = DI[t] - DI[t - 1]
        dEQ = EQ[t] - EQ[t - 1]
        val = dN - FA[t]
        di_res = dDI - DIf[t]
        eq_res = dEQ - EQf[t]
        gdp_b = g.loc[t] / 1e9
        rows.append({
            "yil": t,
            "NIIP_mlrUSD": N[t],
            "dNIIP_mlrUSD": dN,
            "FA_mlrUSD": FA[t],
            "stok_akim_NIIP_mlrUSD": val,
            "stok_akim_NIIP_gsyh": val / gdp_b * 100,
            "DY_yuk_stok_fark_mlrUSD": dDI,
            "DY_yuk_akim_mlrUSD": DIf[t],
            "DY_stok_akim_mlrUSD": di_res,
            "DY_stok_akim_gsyh": di_res / gdp_b * 100,
            "hisse_yuk_stok_fark_mlrUSD": dEQ,
            "hisse_yuk_akim_mlrUSD": EQf[t],
            "hisse_stok_akim_mlrUSD": eq_res,
            "hisse_stok_akim_gsyh": eq_res / gdp_b * 100,
            "etiket": "HESAP",
        })
    return pd.DataFrame(rows), N, FA

def banka_tablosu(gsyh):
    # BDDK Aralık bülteni düz yazı. Yuvarlak milyar TL. 2022 giriş cümlesindeki 145 kullanılmadı.
    kar = {2014: 25, 2015: 26, 2016: 38, 2017: 49, 2018: 54, 2019: 50, 2020: 60, 2021: 92, 2022: 432, 2023: 604, 2024: 659, 2025: 940}
    faiz = {2014: (139, 73), 2015: (164, 87), 2016: (195, 103), 2017: (247, 134), 2018: (368, 222), 2019: (420, 258), 2020: (423, 209), 2021: (642, 376)}
    nii_veri = {2022: 764, 2023: 718, 2024: 986, 2025: 1725}
    ypngp = {2014: -6, 2015: 3.9, 2016: -4, 2017: 2, 2018: 5, 2019: -1, 2020: 33, 2021: 57, 2022: 40, 2023: 131, 2024: 44, 2025: 43}
    rows = []
    for y, k in kar.items():
        if y in faiz:
            gel, gid = faiz[y]
            nii, nii_et = gel - gid, "HESAP faiz geliri−gideri, yuvarlak"
        else:
            gel = gid = np.nan
            nii, nii_et = nii_veri[y], "VERİ bülten net faiz geliri, yuvarlak"
        rows.append({
            "yil": y,
            "net_kar_mlrTL": k,
            "net_kar_gsyh": pct_gdp(k, gsyh.loc[y]),
            "net_kar_etiket": "VERİ BDDK Aralık bülteni, yuvarlak milyar",
            "faiz_geliri_mlr": gel,
            "faiz_gideri_mlr": gid,
            "net_faiz_mlr": nii,
            "net_faiz_gsyh": pct_gdp(nii, gsyh.loc[y]),
            "net_faiz_etiket": nii_et,
            "NIM": np.nan,
            "NIM_etiket": "DOĞRULANMADI bülten metninde net faiz marjı yok",
            "KKM_komisyon": np.nan,
            "KKM_etiket": "DOĞRULANMADI kur farkı giderinden ayrı satır yok",
            "YPNGP_mlrTL": ypngp[y],
            "YPNGP_etiket": "VERİ yıl sonu stok, yuvarlak; kazanç değil, S1'e yazılmadı",
        })
    return pd.DataFrame(rows)

def main():
    gsyh = gdp_lcu()
    S1t, Y, E, q = load_base()
    trg_old = pd.Series({2019: 37.518596 + 40.769702, 2020: 39.109540 + 5.349978, 2021: 30.207403 + 5.576195})
    trg_old_g = pd.Series({y: pct_gdp(trg_old[y], gsyh.loc[y]) for y in trg_old.index})
    trg_new_g = pd.Series({y: pct_gdp(TR_MLR[y], gsyh.loc[y]) for y in TR_MLR.index})
    if (trg_new_g.abs() > 5).any():
        raise SystemExit("aktarım %GSYH beklenenden büyük:\n" + trg_new_g.to_string())
    tr = pd.DataFrame({
        "yil": TR_MLR.index,
        "milyar_TL": TR_MLR.values,
        "gsyh_puan": [trg_new_g[y] for y in TR_MLR.index],
        "etiket": [TR_KAYNAK[y] for y in TR_MLR.index],
    })
    tr.to_csv(OUT / "tcmb_hazine_aktarim.csv", index=False)

    out_old, ext, beta = scenario(S1t, Y, E, q, trg_old_g)
    out_new, _, _ = scenario(S1t, Y, E, q, trg_new_g)

    rows = []
    for lv in ext:
        a = out_new[(lv, "S1")]
        b = out_new[(lv, "S2")]
        ao = out_old[(lv, "S1")]
        bo = out_old[(lv, "S2")]
        for gname in a.index:
            rows.append({
                "duzey": lv, "aktor": gname,
                "S1_yeni": a.loc[gname, "S1"], "S2_yeni": b.loc[gname, "S2"],
                "S1_eksi_S2_yeni": a.loc[gname, "S1"] - b.loc[gname, "S2"],
                "S1_eski": ao.loc[gname, "S1"], "S2_eski": bo.loc[gname, "S2"],
                "S1_eksi_S2_eski": ao.loc[gname, "S1"] - bo.loc[gname, "S2"],
                "etiket": "HESAP; S2 VARSAYIM; aktarım VERİ",
            })
    R = pd.DataFrame(rows)
    # sıfır toplam
    chk = R.groupby("duzey")[["S1_yeni", "S2_yeni"]].sum()
    if chk.abs().max().max() > 0.02:
        raise SystemExit("sıfır toplam bozuldu\n" + chk.to_string())
    R.round(4).to_csv(OUT / "tablo_zayif_S1S2.csv", index=False)
    W = R.pivot(index="aktor", columns="duzey", values="S1_eksi_S2_yeni")
    for lv in ext:
        o = out_new[(lv, "S1")]
        hidden = -(o.loc["Hazine", "k3_KKM"]) + out_new[(lv, "negS1")] - o.loc[["Hane_alt", "Hane_orta", "Hane_ust"], "k1_TL"].sum()
        W.loc["_gizli", lv] = hidden
        W.loc["_gorunur", lv] = out_new[(lv, "cap")]
        W.loc["_ekkur", lv] = out_new[(lv, "ext")].sum()
        oo = out_old[(lv, "S1")]
        hidden_o = -(oo.loc["Hazine", "k3_KKM"]) + out_old[(lv, "negS1")] - oo.loc[["Hane_alt", "Hane_orta", "Hane_ust"], "k1_TL"].sum()
        W.loc["_gizli_eski", lv] = hidden_o
        W.loc["_gorunur_eski", lv] = out_old[(lv, "cap")]
    W.round(4).to_csv(OUT / "ozet_S1eksiS2_zayif.csv")

    # Z6 makro duyarlılık. Aktöre yazılmaz (TL stok yok).
    z6 = []
    for lv, ex in ((lv, out_new[(lv, "ext")]) for lv in ext):
        pi = out_new[(lv, "pi")]
        exs = ex.reindex(range(2014, 2026)).fillna(0)
        pi_ex = beta[lv] * exs
        for phi in (0.3, 1.0, 1.5):
            di = phi * pi_ex
            dr = (phi - 1) * pi_ex
            dgk = -0.45 * dr
            z6.append({
                "duzey": lv, "beta": beta[lv], "phi": phi,
                "ek_kur_kumulatif": exs.sum(),
                "pi_ex_kumulatif": pi_ex.sum(),
                "delta_i_kumulatif": di.sum(),
                "delta_r_kumulatif": dr.sum(),
                "delta_gk_kumulatif": dgk.sum(),
                "birim": "paylas2 ek kur ile aynı (log puan, kümülatif)",
                "etiket": "VARSAYIM katsayı, HESAP",
                "aktor_aktarimi": "yok, TL stok serisi yok",
            })
        for gam in (0.1, 0.3):
            dg = -gam * exs
            z6.append({
                "duzey": lv, "beta": beta[lv], "phi": np.nan, "gamma": gam,
                "ek_kur_kumulatif": exs.sum(),
                "delta_g_kumulatif": dg.sum(),
                "birim": "paylas2 ek kur ile aynı (log puan, kümülatif)",
                "etiket": "VARSAYIM gamma, HESAP",
                "aktor_aktarimi": "yok",
            })
    pd.DataFrame(z6).round(4).to_csv(OUT / "s2_faiz_buyume.csv", index=False)

    fr, buyuk, kobi, old, new = firma_anahtar()
    fr.round(6).to_csv(OUT / "firma_kambiyo_olcek.csv", index=False)
    s2425 = new.loc[[2024, 2025]].clip(upper=0).sum()
    s2425 = s2425 / s2425.sum()

    # Z5
    D = S1t.loc["Yurtdisi+artik"]
    uyp = E["D_UYP_dogrudan"].sum()
    bridge_rows = []
    for lv in ext:
        d3 = out_new[(lv, "S1")].loc["Yurtdisi+artik", "D3_banka_kur"]
        parts = {
            "k1_D": D["k1_TL"],
            "k2_D": D["k2_kur"],
            "k5_D": D["k5_senyoraj"],
            "k7_D": D["k7_bankaaltin"],
            "k8_D": D["k8_swap"],
            "D3_banka": d3,
        }
        model = sum(parts.values())
        non_uyp = parts["k1_D"] + parts["k5_D"] + parts["k7_D"] + parts["k8_D"] + parts["D3_banka"]
        fark = model - uyp
        kalan = fark - non_uyp  # = k2_D - UYP
        bridge_rows.append({
            "duzey": lv, **parts, "model_D": model, "UYP_dogrudan": uyp,
            "fark_model_eksi_UYP": fark, "D_icinde_UYP_disi": non_uyp,
            "kalan_k2_eksi_UYP": kalan, "etiket": "HESAP",
        })
    pd.DataFrame(bridge_rows).round(4).to_csv(OUT / "kopru_yurtdisi.csv", index=False)
    usd, N, FA = uyp_bridge()
    usd.round(4).to_csv(OUT / "uyp_stok_akim.csv", index=False)
    B = banka_tablosu(gsyh)
    B.round(4).to_csv(OUT / "banka_bddk.csv", index=False)

    # grafik
    o = ["Hane_alt", "Hane_orta", "Hane_ust", "Firma_KOBI", "Firma_BUYUK", "Banka", "Hazine", "TCMB", "Yurtdisi+artik"]
    Ww = W.loc[o]
    m = Ww["orta(asimetrik,k=.5)"]
    lo, hi = Ww.min(axis=1), Ww.max(axis=1)
    eski = R[R.duzey == "orta(asimetrik,k=.5)"].set_index("aktor").loc[o, "S1_eksi_S2_eski"]
    f, ax = plt.subplots(figsize=(10, 6.2))
    y = np.arange(len(o))
    ax.barh(y, m, color=["#2c7a3f" if v > 0 else "#a33b3b" for v in m], alpha=0.75, label="yeni orta")
    ax.errorbar(m, y, xerr=[m - lo, hi - m], fmt="none", ecolor="k", capsize=3, label="yeni düşük–yüksek")
    ax.scatter(eski, y, marker="D", c="k", s=28, label="paylas2 orta (eski aktarım)")
    ax.set_yticks(y)
    ax.set_yticklabels(o)
    ax.axvline(0, c="k", lw=0.8)
    ax.set_xlabel("Ertelemenin getirisi S1−S2, 2014–25, GSYH puanı [HESAP; S2 VARSAYIM]")
    ax.set_title("Zayıf tur: doğrulanan TCMB→Hazine aktarımı sonrası S1−S2")
    ax.legend(fontsize=8, loc="lower right")
    plt.tight_layout()
    plt.savefig(OUT / "zayif_S1S2.png", dpi=120)
    plt.close()

    # kambiyo pay grafiği
    f, ax = plt.subplots(figsize=(9, 4.2))
    for src, tab, mk in [("2009–23 panel", old, "o"), ("2023–25 panel", new, "s")]:
        sh = (-tab.clip(upper=0)).div((-tab.clip(upper=0)).sum(axis=1), axis=0)["BUYUK"]
        ax.plot(sh.index, sh.values, marker=mk, label=src)
    ax.axhline(0.690, color="gray", ls="--", lw=1, label="eski anahtar 0,690")
    ax.set_ylim(0.5, 1.0)
    ax.set_ylabel("Büyük firmanın net kambiyo zararı payı [HESAP]")
    ax.set_title("Ölçeğe göre kambiyo zararı payı (41–43 ve 68 hariç)")
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(OUT / "firma_kambiyo_pay.png", dpi=120)
    plt.close()

    summary = {
        "transfer_gsyh": trg_new_g.round(4).to_dict(),
        "transfer_eski_2019_21": trg_old_g.round(4).to_dict(),
        "transfer_toplam_yeni": round(float(trg_new_g.sum()), 4),
        "transfer_toplam_eski": round(float(trg_old_g.sum()), 4),
        "buyuk_2014_23": round(buyuk, 4),
        "kobi_2014_23": round(kobi, 4),
        "buyuk_2024": round(float((-new.loc[2024].clip(upper=0) / -new.loc[2024].clip(upper=0).sum())["BUYUK"]), 4),
        "buyuk_2025": round(float((-new.loc[2025].clip(upper=0) / -new.loc[2025].clip(upper=0).sum())["BUYUK"]), 4),
        "buyuk_2024_25": round(float(s2425["BUYUK"]), 4),
        "uyp": round(float(uyp), 4),
        "usd_stok_akim_gsyh_toplam": round(float(usd.stok_akim_NIIP_gsyh.sum()), 4),
        "dy_stok_akim_gsyh": round(float(usd.DY_stok_akim_gsyh.sum()), 4),
        "hisse_stok_akim_gsyh": round(float(usd.hisse_stok_akim_gsyh.sum()), 4),
        "kalan_k2_uyp": round(float(bridge_rows[1]["kalan_k2_eksi_UYP"]), 4),
        "fark_model_uyp_orta": round(float(bridge_rows[1]["fark_model_eksi_UYP"]), 4),
        "sifir": chk.round(4).to_dict(),
        "kar_gsyh_toplam": round(float(B.net_kar_gsyh.sum()), 4),
    }
    # S1 levels orta
    mid = R[R.duzey == "orta(asimetrik,k=.5)"].set_index("aktor")
    summary["S1_yeni_orta"] = mid["S1_yeni"].round(3).to_dict()
    summary["S1_eski_orta"] = mid["S1_eski"].round(3).to_dict()
    summary["S1S2_yeni_orta"] = mid["S1_eksi_S2_yeni"].round(3).to_dict()
    summary["S1S2_eski_orta"] = mid["S1_eksi_S2_eski"].round(3).to_dict()
    for lv in ext:
        summary[f"gizli_{lv}"] = round(float(W.loc["_gizli", lv]), 3)
        summary[f"gorunur_{lv}"] = round(float(W.loc["_gorunur", lv]), 3)
        summary[f"ekkur_{lv}"] = round(float(W.loc["_ekkur", lv]), 3)
    (OUT / "ozet_sayi.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
