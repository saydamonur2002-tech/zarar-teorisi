"""FH ölçülmüş E (B, TCMB'yi içerir) -> depo B'/K' konvansiyonu. Kaynak: EVDS Analitik Bilanço (bie_abanlbil), pbtop.
E[i alacaklı, j borçlu], bin TL, köşegen 0. SEC = H,F,B,K,D."""
import numpy as np, pandas as pd
SEC = ["H", "F", "B", "K", "D"]; I = {s: k for k, s in enumerate(SEC)}
from pathlib import Path as _P
_K = _P(__file__).resolve().parent
_AB = _PB = _FH = _TC = None
AG = {"S11":"F","S121_122_123":"B","S124_127":"B","S128_129":"B","S13":"K","S14":"H","S15":"H","S2":"D"}
def _load():
    global _AB, _PB, _FH, _TC
    if _AB is None:
        a = pd.read_csv(_K / "veri_dis/tcmb_bacak_evds.csv"); _AB = {(r.Donem, r.Seri): r.Deger for r in a.itertuples()}
        b = a
        _PB = {(r.Donem, r.Seri): r.Deger for r in b.itertuples()}
        f = pd.read_csv(_K / "veri_dis/fh_kimden_kime_uzun.csv"); _FH = f[f.borclu != "TOPLAM"]
        t = pd.read_csv(_K / "akim_ve_tcmb_ham.csv", dtype={"Donem": str}); t = t[t.Grup == "bie_finhestnks710121"]
        _TC = {(r.Donem, int(r.Seri.split("ZP")[1])): r.Deger for r in t.itertuples()}
def ay(p): y, q = p.split("-Q"); return f"{y}-{int(q)*3:02d}"
def E_fh(ens, p):
    _load(); d = _FH[(_FH.ens == ens) & (_FH.donem == p)]
    if d.empty: return None
    E = np.zeros((5, 5))
    for r in d.itertuples(): E[I[AG[r.alacakli]], I[AG[r.borclu]]] += r.bin_tl
    np.fill_diagonal(E, 0); return E
def bacaklar(p):
    """TCMB bacakları (bin TL) + kaynak kodları. None = veri yok."""
    _load(); m = ay(p); g = lambda s: _AB.get((m, s)); tc = lambda z: _TC.get((p, z))
    L = {"m": m, "mev_yuk_toplam_FH_S121": tc(27), "mev_var_toplam_FH_S121": tc(5), "kre_var_toplam_FH_S121": tc(12), "kre_yuk_toplam_FH_S121": tc(34),
         "mev_TCMB_B_TL_A18": g("TP.AB.A18"), "mev_TCMB_B_YP_A14": g("TP.AB.A14"), "mev_TCMB_K_TL_A25": g("TP.AB.A25"),
         "mev_TCMB_kamu_ve_diger_YP_A13": g("TP.AB.A13"), "mev_TCMB_banka_disi_A22": g("TP.AB.A22"), "mev_fon_A21": g("TP.AB.A21"),
         "emisyon_A17": g("TP.AB.A17"), "kre_TCMB_B_A06": g("TP.AB.A06"), "kre_TCMB_TMSF_A061": g("TP.AB.A061"), "banka_kasa_T01": _PB.get((m if m <= "2026-08" else "2026-08", "TP.TOP.T01"))}
    return L
def E_bk(ens, p, sinir="alt", nakit=None, A_repo=None):
    """sinir: 'alt' ayrılamayan kısımlar D'ye (sınırlı) / 'ust' B'ye. nakit: None | 'S1'(depo-FH H/F farkı oranı) | ('H', pay)."""
    E = E_fh(ens, p); L = bacaklar(p)
    if E is None or any(L[k] is None for k in ("mev_TCMB_B_TL_A18","mev_yuk_toplam_FH_S121","kre_TCMB_B_A06")): return None, None
    E = E.copy(); B, K, D, H, F = I["B"], I["K"], I["D"], I["H"], I["F"]; z = lambda x: 0.0 if x is None or np.isnan(x) else float(x)
    log = {}
    if ens == "para_mevduat":
        # TCMB borçlu (yükümlülük)
        bB = z(L["mev_TCMB_B_TL_A18"]) + z(L["mev_TCMB_B_YP_A14"])           # FH'de B içi (köşegen) -> şimdi K'->B
        bK = z(L["mev_TCMB_K_TL_A25"]); amb = z(L["mev_TCMB_kamu_ve_diger_YP_A13"])
        bHF = z(L["mev_TCMB_banka_disi_A22"]) + z(L["mev_fon_A21"])
        em = z(L["emisyon_A17"])
        res = z(L["mev_yuk_toplam_FH_S121"]) - (bB + bK + amb + bHF + em)     # dış + diğer; ayrılamadı
        aK = amb if sinir == "alt" else 0.0; aD = amb - aK
        rD = min(max(res, 0), E[D, B]) if sinir == "alt" else 0.0          # D hücresi sınırı
        # FH B sütunundan TCMB payını çıkar (B->K kamu, B->D dış, B->F banka dışı)
        tK = min(bK + aK, E[K, B]); tD = min(aD + rD, E[D, B]); tF = min(bHF, E[F, B])
        E[K, B] -= tK; E[D, B] -= tD; E[F, B] -= tF
        rB = max(res, 0) if sinir == "ust" else max(res, 0) - rD
        E[B, K] += bB + rB; E[D, K] += tD; E[F, K] += tF                         # K' sütunu (TCMB borçlu); TCMB-kamu = K' içi -> düşer
        # TCMB alacaklı (varlık 1.770): B veya D, ayrılamadı
        va = z(L["mev_var_toplam_FH_S121"]); vD = min(va, E[B, D]) if sinir == "alt" else 0.0; vB = va - vD
        E[B, D] -= vD; E[K, D] += vD; E[K, B] += vB
        log.update(TCMB_borclu_B=bB, TCMB_borclu_K_dustu=tK, ayrilamadi_A13=amb, ayrilamadi_artik=res, TCMB_borclu_D=tD, TCMB_borclu_F=tF, artik_B=rB,
                   TCMB_alacakli_D=vD, TCMB_alacakli_B=vB, emisyon=em)
        if nakit is not None and em > 0:                                    # nakit bacağı: K'(TCMB) borçlu
            kasa = min(z(L["banka_kasa_T01"]), em); kalan = em - kasa
            if nakit == "S1" and A_repo is not None:
                gH = max(A_repo[H] - E_fh(ens, p)[H].sum(), 0); gF = max(A_repo[F] - E_fh(ens, p)[F].sum(), 0)
                sH = gH / (gH + gF) if gH + gF > 0 else 0.5
            else: sH = nakit[1]
            E[B, K] += kasa; E[H, K] += kalan * sH; E[F, K] += kalan * (1 - sH)
            log.update(nakit_B_kasa=kasa, nakit_H=kalan * sH, nakit_F=kalan * (1 - sH), nakit_H_payi=sH)
    else:  # kredi
        va = z(L["kre_var_toplam_FH_S121"]); vB = min(z(L["kre_TCMB_B_A06"]) + z(L["kre_TCMB_TMSF_A061"]), va); res = va - vB
        rD = min(res, E[B, D]) if sinir == "alt" else 0.0; rB = res - rD
        E[K, B] += vB + rB; E[B, D] -= rD; E[K, D] += rD                    # TCMB alacaklı
        vy = z(L["kre_yuk_toplam_FH_S121"]); yD = min(vy, E[D, B]) if sinir == "alt" else 0.0; yB = vy - yD
        E[D, B] -= yD; E[D, K] += yD; E[B, K] += yB                         # TCMB borçlu
        log.update(TCMB_alacakli_B_A06=vB, ayrilamadi_alacak=res, TCMB_alacakli_D=rD, TCMB_borclu_D=yD, TCMB_borclu_B=yB)
    np.fill_diagonal(E, 0); E = np.maximum(E, 0)
    return E, {k: round(v / 1e6, 1) if isinstance(v, float) and k != "nakit_H_payi" else v for k, v in log.items()}


def x_bk(ens, p, sinir="alt"):
    """B' konsolidasyon düzeltmesi X (bin TL): bankaların TCMB'ye karşı varlık + yükümlülük bacağı, aynı enstrüman.
    Depo B' = konsolide S.12 − TCMB brüt; banka↔TCMB pozisyonları konsolidasyonda elendiği için B' varlık ve yükümlülüğe X geri eklenir.
    Gözlenen: mevduat A18+A14, kredi A06(+A061). Ayrılamayan kısım sinir='alt' -> 0 (FH hücre sınırı zorlamadıkça), 'ust' -> tamamı B."""
    E, log = E_bk(ens, p, sinir)
    L = bacaklar(p); z = lambda x: 0.0 if x is None or (isinstance(x, float) and np.isnan(x)) else float(x)
    if L.get("mev_TCMB_B_TL_A18") is None: return 0.0
    if ens == "para_mevduat":
        if log: return (log["TCMB_borclu_B"] + log.get("artik_B", 0) + log["TCMB_alacakli_B"]) * 1e6
        res = z(L["mev_yuk_toplam_FH_S121"]) - sum(z(L[k]) for k in ("mev_TCMB_B_TL_A18","mev_TCMB_B_YP_A14","mev_TCMB_K_TL_A25","mev_TCMB_kamu_ve_diger_YP_A13","mev_TCMB_banka_disi_A22","mev_fon_A21","emisyon_A17"))
        return z(L["mev_TCMB_B_TL_A18"]) + z(L["mev_TCMB_B_YP_A14"]) + ((max(res, 0) + z(L["mev_var_toplam_FH_S121"])) if sinir == "ust" else 0)
    if log: return (log["TCMB_alacakli_B_A06"] + log["ayrilamadi_alacak"] - log["TCMB_alacakli_D"] + log["TCMB_borclu_B"]) * 1e6
    va = z(L["kre_var_toplam_FH_S121"]); vb = min(z(L["kre_TCMB_B_A06"]) + z(L["kre_TCMB_TMSF_A061"]), va)
    return vb + ((va - vb + z(L["kre_yuk_toplam_FH_S121"])) if sinir == "ust" else 0)
