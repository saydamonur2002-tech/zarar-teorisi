"""K'nin bütçe (gelir-gider) kanalı: vergi, faiz, transfer akışlarını hazne bazında aktarım matrisine çevirir.

Kaynak: EVDS Merkezi Yönetim Bütçe Gelirleri (bie_kbmgel) ve Harcamaları (bie_kbmgid), aylık -> çeyreklik toplam.
Φ[i -> K]: i haznesinin K'ya net ödemesi (vergi). Φ[K -> i]: K'nın i'ye net ödemesi (faiz, transfer, alım).
Hane ve firma ayrımı VERGİ YÜKÜ VARSAYIMLARINA dayanır (bütçe verisi mükellefi hazne olarak vermez):
  gelir vergisi, mülkiyet, tüketim (KDV/ÖTV/dahilde mal-hizmet) vergileri -> H; kurumlar vergisi, dış ticaret vergileri -> F;
  damga/harç/diğer vergiler -> yarı yarıya H/F; teşebbüs-mülkiyet, faiz-pay-ceza, sermaye, alacak tahsilatı gelirleri -> F.
  Harcamada: personel, hane/sosyal/tarım/NPO transferleri -> H; mal-hizmet, görevlendirme, sermaye gid./transferi, borç verme -> F;
  yurt dışı transferleri ve dış faiz -> D; iç faiz -> K tahvil alacaklıları (stok verisindeki pay: B, H, F, D).
  SGK devlet primi, Hazine yardımları, gelirden ayrılan paylar K içi (S.13 konsolide) sayılır, hariç tutulur.
"""
from pathlib import Path

import numpy as np
import pandas as pd

DIR = Path(__file__).parent
SEC = ["H", "F", "B", "K", "D"]

TAX_TO_H = ["GEL005", "GEL014", "GEL017"]  # gelir, mülkiyet, dahilde mal-hizmet (KDV, ÖTV dahil)
TAX_TO_F = ["GEL010", "GEL031"]  # kurumlar, dış ticaret
TAX_HALF = ["GEL035", "GEL036", "GEL037"]  # damga, harç, diğer
NONTAX_TO_F = ["GEL038", "GEL056", "GEL061", "GEL087", "GEL093", "GEL094", "GEL095"]
SPEND_TO_H = ["GID003", "GID057", "GID061", "GID067", "GID080", "GID087"]
SPEND_TO_F = ["GID014", "GID027", "GID110", "GID116", "GID131"]
SPEND_TO_D = ["GID092", "GID160"]
SPEND_INTERNAL = ["GID008", "GID033", "GID096"]
INT_DOMESTIC = ["GID153", "GID161", "GID162", "GID163"]


def quarter(m):
    y, mo = m.split("-")
    return f"{y}-Q{(int(mo) - 1) // 3 + 1}"


def load():
    d = pd.read_csv(DIR / "butce_ham.csv", dtype={"Donem": str})
    d["sc"] = d["Seri"].str.replace("TP.KB.", "", regex=False)
    d["Q"] = d["Donem"].map(quarter)
    d = d[d.Grup.isin(["bie_kbmgel", "bie_kbmgid"])]
    # çeyrek tamam mı? 3 ay şartı
    cnt = d.groupby(["Q", "sc"]).Donem.nunique()
    full = cnt[cnt == 3].index
    q = d.groupby(["Q", "sc"]).Deger.sum()
    return q[q.index.isin(full)].unstack()


def validate(q):
    """Alt kalemlerin toplamı üst kalemi veriyor mu?"""
    res = {}
    gel_parts = TAX_TO_H + TAX_TO_F + TAX_HALF + NONTAX_TO_F
    gel_sum = q[gel_parts].sum(axis=1)
    res["gelir: sum(parça)/GEL001 (medyan, maks sapma %)"] = (
        float((gel_sum / q["GEL001"]).median()),
        float((gel_sum / q["GEL001"] - 1).abs().max() * 100),
    )
    gid_parts = ["GID003", "GID008", "GID014", "GID026", "GID110", "GID116", "GID131", "GID142", "GID152"]
    gid_sum = q[gid_parts].sum(axis=1)
    res["gider: sum(ana kalem)/GID001"] = (
        float((gid_sum / q["GID001"]).median()),
        float((gid_sum / q["GID001"] - 1).abs().max() * 100),
    )
    cari = q[["GID027", "GID033", "GID057", "GID061", "GID067", "GID080", "GID087", "GID092", "GID096"]].sum(axis=1)
    res["cari transfer: sum(alt)/GID026"] = (float((cari / q["GID026"]).median()), float((cari / q["GID026"] - 1).abs().max() * 100))
    return res


def tcmb_share_dom_interest(Lm_tahvil_K):
    """İç faiz alacaklı payları: K'nın tahvil borcunun alacaklıları (H,F,B,D; K içi hariç)."""
    s = Lm_tahvil_K.copy()
    s[3] = 0.0  # K kendisi
    return s / s.sum()


def build(q, creditor_shares):
    rows = []
    for p in q.index:
        r = q.loc[p]
        H = F = B = D = 0.0
        H += r[TAX_TO_H].sum() + 0.5 * r[TAX_HALF].sum()
        F += r[TAX_TO_F].sum() + 0.5 * r[TAX_HALF].sum() + r[NONTAX_TO_F].sum()
        tax_in = {"H": H, "F": F}
        out = {"H": r[SPEND_TO_H].sum(), "F": r[SPEND_TO_F].sum(), "D": r[SPEND_TO_D].sum(), "B": 0.0}
        cs = creditor_shares
        interest_dom = r[INT_DOMESTIC].sum()
        for i, s in enumerate(SEC):
            if s != "K":
                out[s] += interest_dom * cs[i]
        rows.append({
            "Donem": p,
            **{f"odeme_{s}_to_K": tax_in.get(s, 0.0) for s in ("H", "F", "B", "D")},
            **{f"odeme_K_to_{s}": out.get(s, 0.0) for s in ("H", "F", "B", "D")},
            "ic_faiz": interest_dom,
            "dis_faiz": r["GID160"],
            "faiz_disi_denge_butce": r["GEL001"] - r["GID002"],
            "butce_dengesi": r["GEL001"] - r["GID001"],
        })
    out = pd.DataFrame(rows)
    for s in ("H", "F", "B", "D"):
        out[f"net_{s}_to_K"] = out[f"odeme_{s}_to_K"] - out[f"odeme_K_to_{s}"]
    return out


def fiscal_shock(kind, amount, kanal_paylari):
    """Bütçe şoku -> hazne etkisi (bin TL, + kazanç / - kayıp). Sıfır toplamlı transfer.
    kind='vergi': K kazanır, mükellefler (H,F) kaybeder (gelir kaynağı payı).
    kind='harcama': K kaybeder, alıcılar (H,F,B,D) kazanır (harcama alıcı payı).
    kanal_paylari: K_kanal_paylari_son4ceyrek.csv içeriği (DataFrame)."""
    res = {s: 0.0 for s in SEC}
    if kind == "vergi":
        sh = kanal_paylari.iloc[:, 0].dropna()
        res["K"] = amount
        for s, v in sh.items():
            res[s] -= amount * v
    elif kind == "harcama":
        sh = kanal_paylari.iloc[:, 1].dropna()
        res["K"] = -amount
        for s, v in sh.items():
            res[s] += amount * v
    else:
        raise ValueError(kind)
    return res


def main():
    q = load()
    v = validate(q)
    for k, x in v.items():
        print(k, "->", round(x[0], 4), "| maks sapma %", round(x[1], 2))
    return q


if __name__ == "__main__":
    main()
