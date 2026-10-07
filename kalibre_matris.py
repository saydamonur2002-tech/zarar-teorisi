"""G (kâr) ve L (zarar) aktarım matrislerinin kalibrasyonu.

Girdi : finansal_hesaplar_uzun.csv (TCMB EVDS3 sektörel finansal hesaplar, bin TL, konsolide stok)
Çıktı : matrisler_<dönem>.csv, matris_zaman_serisi.csv, kalibrasyon_ozeti.json

Yöntem (kimden-kime verisi yok; yalnızca her haznenin enstrüman bazlı varlık ve yükümlülüğü var):
  1. Her enstrüman m için alacaklı i ve borçlu j arasındaki maruziyet orantılı dağıtılır:
         E^m_ij = A^m_i * Y^m_j / sum_k Y^m_k          (i = alacaklı, j = borçlu)
     Bu, enstrüman içinde "borçlunun yükümlülüğü, alacaklılara varlık paylarıyla bölüşülür"
     varsayımıdır. Gerçek bilateral veri bu tahmini doğrulayabilir; elimizde yok.
  2. Zarar kanalı (L): borç benzeri enstrümanlar (mevduat, borçlanma senedi, kredi, sigorta, diğer).
     Borçlu j'nin zararı alacaklılarına, maruziyet payları oranında geçer:
         L[j -> i] = sum_m E^m_ij / sum_i sum_m E^m_ij
  3. Kâr kanalı (G): özkaynak enstrümanı (hisse ve fonlar). j'nin kârı hissedarlarına geçer:
         G[j -> i] = E^hisse_ij / sum_i E^hisse_ij
  4. Satır toplamı 1'dir; "D'ye giden pay" sızıntıdır (net kaynak kaybı). D soğurucu kabul edilip
     adım başına geçiş oranı lam ile u = (I - lam*Q)^-1 R hesaplanır (lam=0 doğrudan sızıntı).
     lam=1'de sonuç matematiksel olarak hep 1'dir; lam geriye dönük testle kalibre edilmelidir.
Diyagonal sıfırdır (konsolide veride hazne içi kalemler elenmiştir).
EVDS S.2 (D) kalemleri ters etiketli olduğundan D'nin varlık/yükümlülüğü çevrilir (bkz. stocks()).
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
SEC = ["H", "F", "B", "K", "D"]  # H = hane + NPISH

# seviye-1 enstrümanlar: (ad, varlık serisi ZP no, yükümlülük serisi ZP no)
INSTR = {
    "altin_sdr": (2, 24),
    "para_mevduat": (5, 27),
    "borclanma_senedi": (9, 31),
    "kredi": (12, 34),
    "hisse_ozkaynak": (15, 37),
    "sigorta_emeklilik": (20, 42),
    "turev": (21, 43),
    "diger": (22, 44),
}
LOSS_INSTR = ["para_mevduat", "borclanma_senedi", "kredi", "sigorta_emeklilik", "diger"]
GAIN_INSTR = ["hisse_ozkaynak"]

LAMS = [0.0, 0.5, 0.8]  # adım başına geçiş oranı (duyarlılık; gerçek değer geriye dönük testle kalibre edilecek)


def load():
    df = pd.read_csv(DIR / "finansal_hesaplar_uzun.csv", dtype={"Donem": str})
    df["zp"] = df["Seri"].str.extract(r"ZP(\d+)$").astype(int)
    return df[df["Hazne"] != "TOPLAM"]


def stocks(df, donem):
    d = df[df["Donem"] == donem]
    out = {}
    for name, (za, zl) in INSTR.items():
        a = d[d["zp"] == za].set_index("Hazne")["Deger"]
        y = d[d["zp"] == zl].set_index("Hazne")["Deger"]
        a = a.reindex(["H", "F", "B", "K", "D", "NPISH"]).fillna(0.0)
        y = y.reindex(["H", "F", "B", "K", "D", "NPISH"]).fillna(0.0)
        a["H"] += a.pop("NPISH")
        y["H"] += y.pop("NPISH")
        # EVDS S.2 (D) kalemleri Türkiye'ye göre ters etiketli: D'yi çevirince her enstrümanda
        # sum(varlık)/sum(yükümlülük) = 1,000 oluyor (2021-Q4 ve 2026-Q1'de doğrulandı).
        a["D"], y["D"] = y["D"], a["D"]
        out[name] = (a[SEC].to_numpy(float), y[SEC].to_numpy(float))
    return out


def exposure(a, y):
    """E[i, j]: i alacaklı, j borçlu. Satır toplamı = A_i."""
    sy = y.sum()
    if sy <= 0:
        return np.zeros((len(SEC), len(SEC)))
    E = np.outer(a, y / sy)
    np.fill_diagonal(E, 0.0)  # konsolide veri: hazne içi elenmiş
    return E


def channel(st, names):
    E = sum(exposure(*st[n]) for n in names)
    col = E.sum(axis=0)  # borçlu j'nin dış alacaklılarına toplam yükümlülüğü
    M = np.zeros_like(E)
    for j in range(len(SEC)):
        if col[j] > 0:
            M[j, :] = E[:, j] / col[j]  # M[j -> i]
    return M, E


def to_D(M, lam):
    """D soğurucu; yerleşik blok Q, D sütunu R. Her adımda yerleşik alacaklıya geçen kısım lam
    (1-lam tampon tarafından emilir): u = (I - lam*Q)^-1 R. lam=0 doğrudan sızıntı;
    lam=1 ise satır toplamı 1 olduğundan her yerde 1 çıkar (anlamsız), o yüzden lam<1 kullanılır."""
    n = len(SEC) - 1
    Q, R = M[:n, :n], M[:n, n]
    return np.linalg.solve(np.eye(n) - lam * Q, R)


def imbalance(st):
    """Enstrüman bazında varlık/yükümlülük uyumsuzluğu (tüm sektörler toplamı)."""
    return {n: float(a.sum() / y.sum()) if y.sum() else None for n, (a, y) in st.items()}


def main():
    df = load()
    periods = sorted(df["Donem"].unique())
    rows, summary = [], {}
    for p in periods:
        st = stocks(df, p)
        L, EL = channel(st, LOSS_INSTR)
        G, EG = channel(st, GAIN_INSTR)
        # kaldıraç: borç benzeri yükümlülük / toplam finansal varlık (hazne j); aktarım oranı DEĞİL,
        # ileride u_i = Y_i/B_i durum göstergesinin girdisi.
        assets = np.zeros(len(SEC))
        for n in INSTR:
            assets += st[n][0]
        debt = sum(st[n][1] for n in LOSS_INSTR)
        tau = np.divide(debt, assets, out=np.zeros_like(debt), where=assets > 0)
        us = {lam: (to_D(L, lam), to_D(G, lam)) for lam in LAMS}
        for j, s in enumerate(SEC):
            r = {"Donem": p, "Kaynak": s, "kaldirac_borc_varlik": tau[j]}
            for i, t in enumerate(SEC):
                r[f"L_{t}"] = L[j, i]
                r[f"G_{t}"] = G[j, i]
            if j < len(SEC) - 1:
                for lam, (uL, uG) in us.items():
                    r[f"L_D_lam{lam}"], r[f"G_D_lam{lam}"] = uL[j], uG[j]
            rows.append(r)
        if p in (periods[-1], "2023-Q4", "2018-Q3", "2021-Q4"):
            for nm, M in (("L", L), ("G", G)):
                pd.DataFrame(M, index=SEC, columns=SEC).round(4).to_csv(
                    DIR / f"matris_{nm}_{p}.csv", encoding="utf-8-sig"
                )
            summary[p] = {
                f"L_D_lam{lam}": dict(zip(SEC[:-1], us[lam][0].round(4).tolist())) for lam in LAMS
            }
            summary[p].update({
                f"G_D_lam{lam}": dict(zip(SEC[:-1], us[lam][1].round(4).tolist())) for lam in LAMS
            })
            summary[p]["kaldirac"] = dict(zip(SEC, tau.round(4).tolist()))
            summary[p]["enstruman_varlik_yukumluluk_orani"] = {
                k: (round(v, 4) if v is not None else None) for k, v in imbalance(st).items()
            }
    ts = pd.DataFrame(rows)
    ts.to_csv(DIR / "matris_zaman_serisi.csv", index=False, encoding="utf-8-sig")
    (DIR / "kalibrasyon_ozeti.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("donem:", periods[0], "->", periods[-1], "satir:", len(ts))


if __name__ == "__main__":
    main()
