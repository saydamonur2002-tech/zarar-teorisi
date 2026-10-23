"""
SFC-DZT: Yeldan çekirdeğinin stok–akım tutarlı (SFC) genişlemesi + Dağıtılmış Zarar muhasebesi
==============================================================================================
Altı kesim: Haneler (H), Firmalar (F), Bankalar (B), Kamu (G), Merkez Bankası (CB), Dış dünya (X)
İki para birimi: TL ve ABD doları. Birimler: stoklar trilyon TL (TL) ya da milyar $ ($);
akımlar çeyreklik trilyon TL. Oranlar yıllık. dt = 0.25.

Tutarlılık (Godley & Lavoie):
  * Her işlem satırı sıfıra toplanır (bir kesimin ödemesi diğerinin geliri).
  * Her kesimde: tasarruf + sermaye transferi = finansal varlık değişimi − yükümlülük değişimi (+ yatırım).
  * GİZLİ DENKLEM: bankaların bütçesinden çıkan TCMB net pozisyonu (M_b) ile TCMB bütçesinden
    çıkan (M_cb) ayrı ayrı hesaplanır; eşit çıkmaları modelin tutarlılık testidir.
  * Bilanço: Σ net servet (dış dünya dahil) = sabit sermayenin değeri (pK).

Dağıtılmış Zarar Teorisi (revize) katmanı:
  * Zarar ayrıştırması: kesimlerin reel net servet farkı (senaryo − baz) = iç transfer + dışa ihraç + reel kayıp
  * Gizli (ertelenmiş) zarar Λ = yeniden yapılandırılmış/tanınmamış TGA + TCMB negatif özkaynağı + döviz endeksli koşullu yükümlülük
  * MAK_i: kesim bazında kalan maliyet absorpsiyon kapasitesi (bugün = 1, tükenmiş = 0)
  * EKY: edinilmiş karar yükü = Λ / GSYH ; politika alanı PS = 1 − EKY/EKY_max
"""
import csv, hashlib, json, copy, subprocess
from pathlib import Path
import numpy as np

DT = 0.25
T = 13
LABELS = ["2026Q3"] + [f"{y}Q{q}" for y in range(2026, 2030) for q in range(1, 5)][3:3 + T]

def ovp_anchor(t):
    pts = {0: 0.315, 1: 0.284, 5: 0.21, 9: 0.135, 13: 0.09}
    ks = sorted(pts)
    for k0, k1 in zip(ks, ks[1:]):
        if k0 <= t <= k1:
            return pts[k0] + (pts[k1] - pts[k0]) * (t - k0) / (k1 - k0)
    return 0.09

# ----------------------------------------------------------------------------------------------
# BAŞLANGIÇ STOKLARI (2026Q3)
# ----------------------------------------------------------------------------------------------
E0 = 48.7                       # TL/$ (22 Eylül 2026)
def usd(x, E=E0): return x * E / 1000.0     # mlr $ -> trilyon TL

INIT = dict(
    E=E0, P=1.0, Yq=21.0, C=11.97, yT=21.0, gap=0.0, pK=201.6,            # çeyreklik GSYH 21 tn (yıllık 84); K/Y = 2,4
    # Haneler
    Dh=10.6, Dh_usd=146.0, Lh=6.9, Cu=1.85,
    # Firmalar
    Df=7.06, Df_usd=98.0, FA_usd=55.0, Lf=10.76, Lf_usd=200.0, Xf_usd=164.0,
    # Bankalar
    Bb=6.02, FXL_usd=128.7, OFA_usd=35.3, Xb_usd=120.0,
    # Kamu
    Bt=7.75, Bf_usd=167.3,
    # TCMB
    R_usd=178.7, Bcb=0.90,
    # Dış dünya (TL varlıklar: sıcak paranın borç kısmı)
    Bx=0.83, Dx=0.60,
    # Gizli zarar stokları
    Lam_npl=0.0, Lam_kh_usd=30.0,
    # Pay senetleri (halka açık kısım, fiyat endeksi q; birim = q=1'de trilyon TL)
    q=1.0, qT=1.0, EqX_u=39.36 * 48.7 / 1000, EqH_u=39.36 * 48.7 / 1000 * (1 / 0.344 - 1),
    # Yeldan çekirdeği
    i=0.37, pi=0.3151, omega=0.381, v=105.04, ieff=0.32, g=0.023,
)
S0_ST = 248.1   # kalan vadeye göre KV dış borç (mlr $)

# Açılış banka net serveti. Yedek 4,65, BDDK Temmuz iddiası [DOĞRULANMADI].
# veriler.json banka_ozkaynak_tn varsa o okunur: TP.TOP.V28, 2026-07.
# Plug, VB_0 bu sabite eşitlensin diye Mb artıkına yazılır.
BANKA_OZKAYNAK_TN = 4.65

REPO_RHO_YILLIK = 0.68       # hekis/kalibre.py, tahmin, n=10, se 0,16. a_pi yerine konmadı.
REPO_RHO_CEYREK = 0.4513     # gecis_payi_band ana spesifikasyon, tahmin. Yerine konmadı.
REPO_OZKAYNAK_2026_06 = 4.530


def banka_mb(s):
    """Bankaların TCMB net pozisyonu. +BANKA_OZKAYNAK_TN, açılış net servetini bu sabite eşitler."""
    return (s["Dh"] + s["Df"] + s["Dx"] + usd(s["Dh_usd"] + s["Df_usd"] + s["Xb_usd"]) + BANKA_OZKAYNAK_TN
            - s["Lh"] - s["Lf"] - usd(s["Lf_usd"]) - s["Bb"] - usd(s["FXL_usd"] + s["OFA_usd"]))


def _repo_kok():
    return Path(__file__).resolve().parents[1]


def adres_stoklari():
    """adim4.csv ölçülmüş adres stokları. Dosya yoksa modelin kendi sabiti. Etiket: kanıt (stok)."""
    yol = _repo_kok() / "adim4.csv"
    if not yol.exists():
        return None
    rows = list(csv.DictReader(yol.open(encoding="utf-8-sig")))
    adr = [r for r in rows if r.get("durum") == "olculdu" and r.get("deger")]
    if len(adr) < 3:
        return None
    toplam = sum(float(r["deger"]) for r in adr)
    yp = next(float(r["deger"]) for r in adr if "YP" in r["nesne"])
    return {"toplam_milyar": toplam, "yp_milyar": yp, "n": len(adr), "kaynak": "adim4.csv", "etiket": "kanıt"}


def kod_surumu():
    """Haftalık loga yazılan kod kimliği. Anahtar değeri okunmaz."""
    kok = _repo_kok()
    src = Path(__file__).resolve()
    sha = hashlib.sha256(src.read_bytes()).hexdigest()
    git, kirli = None, None
    try:
        git = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=kok, text=True, stderr=subprocess.DEVNULL).strip()
        st = subprocess.check_output(["git", "status", "--porcelain"], cwd=kok, text=True, stderr=subprocess.DEVNULL)
        kirli = bool(st.strip())
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        pass
    return {"git": git, "sfc_sha256": sha, "kirli": kirli}

# ---- Haftalık güncelleme: veriler.json varsa gözlenen başlangıç değerlerini onunla değiştir ----
import os as _os
_VP = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "veriler.json")
if _os.path.exists(_VP):
    _V = json.load(open(_VP, encoding="utf-8"))["degerler"]
    E0 = _V.get("usd_try", E0)
    def usd(x, E=None): return x * (E0 if E is None else E) / 1000.0
    INIT.update(E=E0, i=_V.get("politika_faizi", INIT["i"]), pi=_V.get("tufe_yillik", INIT["pi"]),
                R_usd=_V.get("brut_rezerv", INIT["R_usd"]),
                FXL_usd=_V.get("brut_rezerv", INIT["R_usd"]) - _V.get("swap_haric_net_rezerv", 50.0),
                v=_V.get("reel_efektif_kur", INIT["v"]), omega=_V.get("emek_payi", INIT["omega"]),
                g=_V.get("buyume_yillik", INIT["g"]))
    S0_ST = _V.get("kv_dis_borc_kalan_vade", S0_ST)
    _yh, _tp = _V.get("yabanci_hisse", 39.36), _V.get("yabanci_takas_payi", 0.344)
    INIT.update(EqX_u=_yh * E0 / 1000, EqH_u=_yh * E0 / 1000 * (1 / _tp - 1))
    if "banka_ozkaynak_tn" in _V:
        BANKA_OZKAYNAK_TN = _V["banka_ozkaynak_tn"]

BASE = dict(
    # dış dünya ve risk
    istar=0.04, pistar=0.025, rho0=0.015, rho1=0.06,
    # sıcak para (borç kısmı: DİBS + yurt dışı yerleşik TL mevduat)
    Hbar=29.4, sbar=0.03, kappa=12.0, lam_in=0.35, lam_out=0.55, lam_panic=0.85, s_crit=0.02, bx_share=0.4,
    # kur politikası
    a0=0.02, a_phase=0, psi=2.5, psi_jump=3.0, NR_floor=15.0, cap_band=30.0,
    # dış borç çevirme (firma KV payı %37, banka %60)
    roll_sens=5.0, xf_growth=0.08, xb_growth=0.06, dBf_usd=1.25, stf=0.37, stb=0.60, fdi=0.006,
    # dolarizasyon
    s0=0.49, s_i=1.0, s_e=0.3, s_r=3.0, s_adj=0.15,
    # talep
    c1=0.97, c2=0.04, nx0=-0.004, eta_v=0.10, eta_g=0.0,
    gk0=0.054, delta=0.06, gam_r=0.45, rl_bar=0.15, eta_e=0.03, gam_z=0.8, gam_cr=1.5, gam_fx=0.5,
    gov_share=0.125, tr_share=0.09, G_extra=0.0,
    # bölüşüm ve vergiler
    w_share=0.90, t_ind=0.11, tau_h=0.18, tau_f=0.08, payout=0.50, tauK_extra=0.0,
    # çatışmacı enflasyon (Yeldan 1993)
    a_pi=0.70, lam_f=0.35, omega_f=0.365, lam_w=0.30, omega_w=0.40, beta_e=0.35, beta_y=0.20,
    prod=0.015, delta_e_f=0.8, gn=0.035,
    # para politikası
    r_target=0.06, phi_pi=0.3, i_smooth=0.6, i_floor=0.16, i_path=None,
    # banka
    sp_d=0.02, sp_l=0.05, i_l_usd=0.08, i_d_usd=0.01, i_fxl=0.005, i_ofa=0.04,
    fee=0.07, opex=0.13, tax_b=0.20, payout_b=0.10,
    # TGA (takipteki alacak) ve tanıma
    n0=0.012, n_r=0.25, n_e=0.30, phi_rec=0.6, recog_t=None,
    # kamu
    ifx=0.065, ieff_adj=0.15,
    # pay senedi bloğu
    kap_p=1.5, eq_rev=0.20, gam_q=0.02, c_eq=0.01, lam_eq=0.5, eq_out=0.0, eq_passive=0.0, eq_shock=0.0,
    shock=None,
)

# ----------------------------------------------------------------------------------------------
def acilis_bilanco():
    """Açılış stok-akım matrisi. Banka sütunundaki artık BANKA_OZKAYNAK_TN'dir."""
    s = copy.deepcopy(INIT)
    u = lambda x: usd(x)
    Mb = banka_mb(s)
    rows = [("Sabit sermaye (pK)", dict(F=s["pK"])), ("TL mevduat", dict(H=s["Dh"], F=s["Df"], B=-(s["Dh"] + s["Df"] + s["Dx"]), X=s["Dx"])),
            ("YP mevduat", dict(H=u(s["Dh_usd"]), F=u(s["Df_usd"]), B=-u(s["Dh_usd"] + s["Df_usd"]))), ("Nakit", dict(H=s["Cu"], CB=-s["Cu"])),
            ("TL kredi (hane)", dict(H=-s["Lh"], B=s["Lh"])), ("TL kredi (firma)", dict(F=-s["Lf"], B=s["Lf"])),
            ("YP kredi (firma)", dict(F=-u(s["Lf_usd"]), B=u(s["Lf_usd"]))), ("Firmaların dış borcu", dict(F=-u(s["Xf_usd"]), X=u(s["Xf_usd"]))),
            ("Firmaların yurt dışı YP varlığı", dict(F=u(s["FA_usd"]), X=-u(s["FA_usd"]))), ("Bankaların dış borcu", dict(B=-u(s["Xb_usd"]), X=u(s["Xb_usd"]))),
            ("Bankaların yurt dışı YP varlığı", dict(B=u(s["OFA_usd"]), X=-u(s["OFA_usd"]))), ("DİBS (TL)", dict(B=s["Bb"], G=-s["Bt"], CB=s["Bcb"], X=s["Bx"])),
            ("Eurobond (YP)", dict(G=-u(s["Bf_usd"]), X=u(s["Bf_usd"]))), ("TCMB brüt rezerv", dict(CB=u(s["R_usd"]), X=-u(s["R_usd"]))),
            ("Pay senetleri (halka açık)", dict(H=s["q"] * s["EqH_u"], F=-s["q"] * (s["EqH_u"] + s["EqX_u"]), X=s["q"] * s["EqX_u"])),
            ("Bankaların TCMB'deki YP'si", dict(B=u(s["FXL_usd"]), CB=-u(s["FXL_usd"]))), ("TCMB net TL pozisyonu (M)", dict(B=Mb, CB=-Mb))]
    secs = ["H", "F", "B", "G", "CB", "X"]
    tot = {k: 0.0 for k in secs}
    out = []
    finansal = 0.0
    for n, dd in rows:
        vals = [dd.get(k, 0.0) for k in secs]
        if n != "Sabit sermaye (pK)":
            finansal = max(finansal, abs(sum(vals)))
        for k, v in zip(secs, vals):
            tot[k] += v
        out.append((n, [round(v, 2) for v in vals], round(sum(vals), 2)))
    nw = [tot[k] for k in secs]
    return dict(rows=out, nw=[round(v, 2) for v in nw], finansal_satir_mutlak_max=finansal,
                nw_eksi_pk=sum(nw) - s["pK"], banka_ozkaynak=tot["B"], Mb=Mb)


def simulate(par, check=True):
    p = copy.deepcopy(par); s = copy.deepcopy(INIT)
    out = {}; checks = []
    def rec(**kw):
        for k, v in kw.items(): out.setdefault(k, []).append(float(v))

    def networths(s):
        E = s["E"]
        VH = s["Dh"] + usd(s["Dh_usd"], E) + s["Cu"] - s["Lh"] + s["q"] * s["EqH_u"]
        VF = (s["pK"] + s["Df"] + usd(s["Df_usd"] + s["FA_usd"], E) - s["Lf"] - usd(s["Lf_usd"] + s["Xf_usd"], E)
              - s["q"] * (s["EqH_u"] + s["EqX_u"]))
        VB = (s["Lh"] + s["Lf"] + usd(s["Lf_usd"], E) + s["Bb"] + usd(s["FXL_usd"] + s["OFA_usd"], E) + s["Mb"]
              - s["Dh"] - s["Df"] - s["Dx"] - usd(s["Dh_usd"] + s["Df_usd"] + s["Xb_usd"], E))
        VG = -s["Bt"] - usd(s["Bf_usd"], E)
        VCB = usd(s["R_usd"] - s["FXL_usd"], E) + s["Bcb"] - s["Mcb"] - s["Cu"]
        VX = (s["Bx"] + s["Dx"] + s["q"] * s["EqX_u"] + usd(s["Xf_usd"] + s["Xb_usd"] + s["Bf_usd"] - s["R_usd"]
              - s["FA_usd"] - s["OFA_usd"], E))
        return dict(H=VH, F=VF, B=VB, G=VG, CB=VCB, X=VX)

    # başlangıçta bankaların TCMB net pozisyonu bilanço artığıdır.
    # BANKA_OZKAYNAK_TN eklentisi kaynaksız bir dengeleyici değildir: açılış VB bu sabite sabitlenir.
    E = s["E"]
    s["Mb"] = banka_mb(s)
    s["Mcb"] = s["Mb"]
    s["G"] = p["gov_share"] * s["Yq"]; s["TR"] = p["tr_share"] * s["Yq"]
    V0 = networths(s)
    s.update(e_prev=np.nan, ee_prev=np.nan, Eprev=E, NRprev=s["R_usd"] - s["FXL_usd"])
    s["Lf_usd_prev_loss"] = 0.0
    pi_prev = s["pi"]
    MAK0 = None

    def mak(s, V, Lam_npl):
        E = s["E"]; Y = 4 * s["Yq"]
        YD = s.get("YD", 0.66 * s["Yq"]) * 4
        m_H = (s["Dh"] + usd(s["Dh_usd"], E) + s["Cu"] - s["Lh"]) / YD
        m_F = s.get("icr", 8.2)                                   # faiz karşılama oranı
        loans = s["Lh"] + s["Lf"] + usd(s["Lf_usd"], E)
        m_B = (V["B"] - Lam_npl) / loans
        m_G = 1 - (s["ieff"] * s["Bt"] + p["ifx"] * usd(s["Bf_usd"], E)) / (0.22 * Y)
        m_CB = (s["R_usd"] - s["FXL_usd"])
        return dict(H=m_H, F=m_F, B=m_B, G=m_G, CB=m_CB)
    MIN = dict(H=0.05, F=2.0, B=0.10, G=0.70, CB=p["NR_floor"])

    for t in range(0, T + 1):
        V = networths(s)
        Lam = s["Lam_npl"] + max(0.0, -V["CB"]) + usd(s["Lam_kh_usd"], s["E"])
        m = mak(s, V, s["Lam_npl"])
        if MAK0 is None: MAK0 = m
        MAK = {k: max(0.0, (m[k] - MIN[k]) / (MAK0[k] - MIN[k])) for k in m}
        Yann = 4 * s["Yq"]
        loans = s["Lh"] + s["Lf"] + usd(s["Lf_usd"], s["E"])
        rec(t=t, i=s["i"], pi=s["pi"], g=s["g"], omega=s["omega"], v=s["v"], E=s["E"], Yann=Yann,
            NR=s["R_usd"] - s["FXL_usd"], R=s["R_usd"], dollar=usd(s["Dh_usd"], s["E"]) / (s["Dh"] + usd(s["Dh_usd"], s["E"])),
            debt=(s["Bt"] + usd(s["Bf_usd"], s["E"])) / Yann, CAR=V["B"] / (0.85 * loans),
            CARadj=(V["B"] - s["Lam_npl"]) / (0.85 * loans),
            Lam=Lam / Yann, Lam_npl=s["Lam_npl"] / Yann, Lam_cb=max(0.0, -V["CB"]) / Yann,
            Lam_kh=usd(s["Lam_kh_usd"], s["E"]) / Yann,
            **{f"V_{k}": V[k] / s["P"] for k in V}, pK=s["pK"] / s["P"], P=s["P"],
            **{f"MAK_{k}": MAK[k] for k in MAK}, MAKmin=min(MAK.values()),
            EKY=Lam / Yann, e=s["e_prev"] if t else np.nan,
            q_real=s["q"] / s["P"] * 100, EqX_usd=s["q"] * s["EqX_u"] * 1000 / s["E"],
            q_usd=s["q"] * 48.7 / s["E"] * 100, Feq=s.get("Feq", 0.0))
        if t == T: break
        # ======================= t+1 dönemi =======================
        tt = t + 1
        pp = copy.deepcopy(p)
        if p["shock"]: p["shock"](tt, pp)
        E_1 = s["E"]
        anchor = ovp_anchor(tt)
        a = pp["a0"] * (max(0.0, 1 - tt / pp["a_phase"]) if pp["a_phase"] else 1.0)
        pie = pp["a_pi"] * pi_prev + (1 - pp["a_pi"]) * anchor
        ee = pie - pp["pistar"] - a
        if pp["i_path"]: i = pp["i_path"](tt)
        else:
            rule = pie + pp["r_target"] + pp["phi_pi"] * (pi_prev - anchor)
            i = float(np.clip(pp["i_smooth"] * s["i"] + (1 - pp["i_smooth"]) * rule, pp["i_floor"], 0.60))
        i_d, i_l = i - pp["sp_d"], i + pp["sp_l"]
        ieff = s["ieff"] + pp["ieff_adj"] * (i - s["ieff"])
        # --- risk primi (KV borç / brüt rezerv yaklaşık: 248/178,7 başlangıç, KV borç ~ Xf*0,37+Xb*0,6+ticari)
        S_st = S0_ST * (pp["stf"] * s["Xf_usd"] + pp["stb"] * s["Xb_usd"]) / (0.37 * 164 + 0.6 * 120)
        SR = S_st / s["R_usd"]
        rho = pp["rho0"] + pp["rho1"] * max(0.0, SR - 1.0)
        rho_hat = 0.015 + 0.06 * 0.39
        i_xf, i_xb = pp["istar"] + 0.5 * rho + 0.015, pp["istar"] + 0.01 + 0.5 * (rho - rho_hat)
        # --- sıcak para (Yeldan B3–B4)
        Hd = (s["Bx"] + s["Dx"]) * 1000 / E_1
        spread = i - pp["istar"] - ee - rho
        Hstar = pp["Hbar"] * np.exp(pp["kappa"] * (spread - pp["sbar"]))
        lam = pp["lam_in"] if Hstar >= Hd else (pp["lam_out"] if spread > pp["s_crit"] else pp["lam_panic"])
        Fh = lam * (Hstar - Hd)                                   # mlr $
        # --- dış borç akımları (mlr $)
        roll = float(np.clip(1 - pp["roll_sens"] * max(0.0, rho - rho_hat - 0.01), 0.6, 1.0))
        dXf = s["Xf_usd"] * (pp["xf_growth"] * DT) - (1 - roll) * pp["stf"] * s["Xf_usd"] * DT
        dXb = s["Xb_usd"] * (pp["xb_growth"] * DT) - (1 - roll) * pp["stb"] * s["Xb_usd"] * DT
        FDI = pp["fdi"] * (4 * s["Yq"] * 1000 / E_1) * DT
        # --- yabancı pay senedi akımı (mlr $, negatif = satış): endeks sınıflandırma şoku + risk primi
        EqX_usd = s["q"] * s["EqX_u"] * 1000 / E_1
        MV_usd = s["q"] * (s["EqX_u"] + s["EqH_u"]) * 1000 / E_1
        Feq = -(pp["eq_out"] + pp["eq_passive"]) * EqX_usd - pp["lam_eq"] * max(0.0, rho - rho_hat - 0.005) * EqX_usd * DT
        # --- dolarizasyon (hanehalkı portföy tercihi)
        Wh_fin = s["Dh"] + usd(s["Dh_usd"], E_1)
        surprise = 0.0 if np.isnan(s["e_prev"]) else max(0.0, s["e_prev"] - s["ee_prev"])
        s_now = usd(s["Dh_usd"], E_1) / Wh_fin
        diff = i_d - pp["i_d_usd"] - ee
        if "diff0" not in s: s["diff0"] = diff
        dDh_usd_des = pp["s_adj"] * (-pp["s_i"] * (diff - s["diff0"]) + pp["s_e"] * surprise
                                     + pp["s_r"] * max(0.0, rho - rho_hat)) * Wh_fin * 1000 / E_1
        dDh_usd_des -= pp.get("senet_usd", 0.0)           # Tek Sistem adım 4: döviz mevduatından senede kayma
        # --- reel talep (NX, yatırım): gecikmeli değişkenlerle
        Yq_1 = s["Yq"]
        nx = pp["nx0"] - pp["eta_v"] * (s["v"] / 105.04 - 1) - pp["eta_g"] * (s["g"] - 0.023) + pp.get("nx_gain", 0) * min(1, tt / 8) + pp["eta_e"] * surprise
        loans_1 = s["Lh"] + s["Lf"] + usd(s["Lf_usd"], E_1)
        Vb_1 = networths(s)["B"]
        car_adj = (Vb_1 - s["Lam_npl"]) / (0.85 * loans_1)
        zomb = s["Lam_npl"] / loans_1
        r_l = i_l - pie
        gk = (pp["gk0"] - pp["gam_r"] * (r_l - pp["rl_bar"]) - pp["gam_z"] * zomb
              - pp["gam_cr"] * max(0.0, 0.14 - car_adj) - pp["gam_fx"] * s["Lf_usd_prev_loss"])
        gk += pp["gam_q"] * (s["q"] / s["P"] / s["qT"] - 1)                  # Tobin q kanalı
        gk = float(np.clip(0.6 * s.get("gk", gk) + 0.4 * gk, -0.05, 0.15))   # yatırım ataleti
        # --- kur: rezerv hareketinden (ön tahmin, E_1 ile)
        int_ext = (pp["i_l_usd"] * 0 + i_xf * s["Xf_usd"] + i_xb * s["Xb_usd"] + pp["ifx"] * s["Bf_usd"]
                   - pp["istar"] * s["R_usd"] - pp["i_ofa"] * s["OFA_usd"] - 0.02 * s["FA_usd"]) * DT   # mlr $
        int_x_tl = (ieff * s["Bx"] + i_d * s["Dx"]) * DT                                                # tn TL
        # ön talep tahmini: nx·Yq_1
        CA_usd_pre = (nx * Yq_1 - int_x_tl) * 1000 / E_1 - int_ext
        dLf_usd = 0.0 + pp.get("dLf_usd", 0.0)
        dDf_usd = 0.0
        dFXL_pre = dDh_usd_des + dDf_usd + dXb - dLf_usd
        dR_pre = CA_usd_pre + Fh + dXf + dXb + FDI + pp["dBf_usd"] + Feq
        dNR_pre = dR_pre - dFXL_pre
        NR_1 = s["R_usd"] - s["FXL_usd"]
        cap = float(np.clip((NR_1 - pp["NR_floor"]) / pp["cap_band"], 0, 1))
        Yd = 4 * Yq_1 * 1000 / E_1
        unmet = 0.0
        if NR_1 + dNR_pre < pp["NR_floor"] and dNR_pre < 0:
            unmet = -dNR_pre - max(0.0, NR_1 - pp["NR_floor"])      # bu çeyreğin karşılanamayan döviz talebi
            # piyasa kurla temizlenir: dolarizasyon ve sıcak para çıkışı ölçeklenir
            demand = max(1e-9, max(0.0, dDh_usd_des) + max(0.0, -Fh))
            cut = min(1.0, unmet / demand)
            if dDh_usd_des > 0: dDh_usd_des *= (1 - cut)
            if Fh < 0: Fh *= (1 - cut)
            # yabancı pay satışı kısılmaz (endeks kuralı zorunlu); karşılanamazsa net rezerv tabanın altına iner
        if dNR_pre < 0:
            e = ee + pp["psi"] * (1 - cap) * (-dNR_pre) * 4 / Yd + pp["psi_jump"] * unmet * 4 / Yd
        else:
            e = ee - 0.2 * pp["psi"] * dNR_pre * 4 / Yd
        e = float(np.clip(e, -0.4, 1.2))
        E = E_1 * (1 + e * DT)
        # --- pay fiyatı: temel sürüklenme (nominal büyüme) + akım baskısı + sınıflandırma şoku
        gap_q = 1 - s["q"] / (s["P"] * s["qT"])                  # temel değerden sapma (pozitif = ucuz)
        q_new = s["q"] * max(0.2, 1 + (s["pi"] + pp["gn"]) * DT + pp["eq_rev"] * gap_q * DT
                             + pp["kap_p"] * Feq / max(1e-9, MV_usd) - pp["eq_shock"])
        du_X = usd(Feq, E) / q_new                          # yabancının sattığı pay (birim); haneler alır
        # --- enflasyon ve bölüşüm (Yeldan C blok)
        lam_f = pp["lam_f"] * (1 + pp["delta_e_f"] * max(0.0, e - ee))
        w_hat = pie + pp["lam_w"] * (pp["omega_w"] - s["omega"]) + pp["prod"]
        pi = (pie + lam_f * (s["omega"] - pp["omega_f"]) + pp["beta_e"] * (e - ee) + pp["beta_y"] * s["gap"])
        pi = pi - pp.get("pi_adj", 0.0)                   # Tek Sistem adım 5 (HEKİS): doğrudan kira etkisi
        omega = s["omega"] * (1 + (w_hat - pi - pp["prod"]) * DT)
        P = s["P"] * (1 + pi * DT)
        # --- kamu harcaması ve transfer (nominal endeksli)
        yT = s["yT"] * (1 + pp["gn"] * DT)                 # reel potansiyel (çeyreklik)
        Gq = (pp["gov_share"] + pp["G_extra"]) * P * yT        # reel kamu alımı potansiyelle büyür
        TRq = pp["tr_share"] * P * yT
        # --- faiz akımları (tn TL, çeyreklik; stoklar t-1, $ kalemler cari kurla)
        U = lambda x: usd(x, E)
        int_Dh = i_d * s["Dh"] * DT; int_Dh_usd = pp["i_d_usd"] * U(s["Dh_usd"]) * DT
        int_Df = i_d * s["Df"] * DT; int_Df_usd = pp["i_d_usd"] * U(s["Df_usd"]) * DT
        int_Dx = i_d * s["Dx"] * DT
        int_Lh = i_l * s["Lh"] * DT; int_Lf = i_l * s["Lf"] * DT * (1 - pp.get("stop_int", 0.0));
        stopped_int = i_l * s["Lf"] * DT * pp.get("stop_int", 0.0) * pp.get("stop_comp", 0.0)   # Hazine telafisi (0 = banka üstlenir)
        int_Lf_usd = pp["i_l_usd"] * U(s["Lf_usd"]) * DT
        int_Xf = i_xf * U(s["Xf_usd"]) * DT; int_Xb = i_xb * U(s["Xb_usd"]) * DT
        int_FA = 0.02 * U(s["FA_usd"]) * DT; int_OFA = pp["i_ofa"] * U(s["OFA_usd"]) * DT
        int_Bb, int_Bx, int_Bcb = ieff * s["Bb"] * DT, ieff * s["Bx"] * DT, ieff * s["Bcb"] * DT
        int_Bf = pp["ifx"] * U(s["Bf_usd"]) * DT
        int_R = pp["istar"] * U(s["R_usd"]) * DT; int_FXL = pp["i_fxl"] * U(s["FXL_usd"]) * DT
        int_M = i * s["Mb"] * DT                     # TCMB'nin bankalara ödediği (Mb<0 ise bankalar öder)
        # --- TGA akımı ve tanıma
        n_rate = (pp["n0"] + pp["n_r"] * max(0.0, r_l - 0.08)
                  + pp["n_e"] * max(0.0, e - ee) * U(s["Lf_usd"]) / loans_1)
        n_rate *= pp.get("npl_mult", 1.0)                 # Tek Sistem adım 1–2: mahsup + sıralı ödeme geç ödeme kaynaklı takibi azaltır
        npl_new = n_rate * loans_1 * DT
        recognized = pp["phi_rec"] * npl_new
        latent_add = npl_new - recognized
        recap_B = recap_CB = 0.0
        if pp["recog_t"] is not None and tt == pp["recog_t"]:
            recap_B = s["Lam_npl"]                    # gizli TGA'nın tamamı tanınır; Hazine bankaları DİBS ile sermayelendirir
            V_cb_now = networths(s)["CB"]
            recap_CB = max(0.0, -V_cb_now)            # TCMB negatif özkaynağı Hazine'ce kapatılır
            recognized += recap_B; latent_add -= 0.0
        Lam_npl = s["Lam_npl"] + latent_add - recap_B
        # yazılan kredi, kredi türlerine orantılı düşer (borçluya sermaye transferi)
        shL = np.array([s["Lh"], s["Lf"], U(s["Lf_usd"])]) / max(1e-9, s["Lh"] + s["Lf"] + U(s["Lf_usd"]))
        wo_h, wo_f, wo_fusd = recognized * shL
        # --- GSYH: sabit nokta iterasyonu
        pK_1 = s["pK"]
        Iq = (gk + pp["delta"]) * pK_1 * (1 + pi * DT) * DT
        CB_profit_pre = int_R + int_Bcb - int_FXL - int_M
        Yq = Yq_1
        Vh_fin = s["Dh"] + U(s["Dh_usd"]) + s["Cu"] - s["Lh"]
        NFW_TL = s["Dh"] + s["Cu"] - s["Lh"]
        fee_inc = pp["fee"] * loans_1 * DT
        for _ in range(200):
            W = pp["w_share"] * omega * Yq
            Tind = pp["t_ind"] * Yq
            opex = pp["opex"] * 0.25 * Yq          # bankaların firmalardan hizmet alımı (firmaya gelir)
            Pi_f = (Yq - W - Tind - int_Lf - int_Lf_usd - int_Xf + int_Df + int_Df_usd + int_FA + opex)
            Tf = (pp["tau_f"] + pp["tauK_extra"]) * max(0.0, Pi_f)
            Div = pp["payout"] * (Pi_f - Tf)
            Pi_b = (int_Lh + int_Lf + int_Lf_usd + int_Bb + int_FXL + int_OFA + int_M + fee_inc + stopped_int
                    - int_Dh - int_Df - int_Dx - int_Dh_usd - int_Df_usd - int_Xb - opex - recognized + recap_B)
            Tb = pp["tax_b"] * max(0.0, Pi_b)
            Div_b = pp["payout_b"] * max(0.0, Pi_b - Tb)
            Th = pp["tau_h"] * W
            YD = W - Th + TRq + Div + Div_b + int_Dh + int_Dh_usd - int_Lh - fee_inc
            C_tgt = (pp["c1"] * (YD - pi * DT * NFW_TL) + pp["c2"] * Vh_fin * DT
                     + pp["c_eq"] * s["q"] * s["EqH_u"] * DT)   # enflasyona göre düzeltilmiş gelir + pay serveti
            C = 0.5 * P * (s["C"] / s["P"]) * (1 + pp["gn"] * DT) + 0.5 * C_tgt   # tüketim alışkanlığı
            Ynew = C + Iq + Gq + nx * Yq
            if abs(Ynew - Yq) < 1e-12: break
            Yq = 0.5 * Yq + 0.5 * Ynew
        NXq = nx * Yq
        # TCMB kârı
        CB_profit = int_R + int_Bcb - int_FXL - int_M
        CB_transfer = max(0.0, CB_profit)
        # --- kamu bütçesi
        T_tot = Tind + Th + Tf + Tb
        Def = Gq + TRq + int_Bb + int_Bx + int_Bcb + int_Bf - T_tot - CB_transfer + stopped_int
        dBt = Def + recap_B + recap_CB - usd(pp["dBf_usd"], E)
        dBx = usd(pp["bx_share"] * Fh, E)
        dBcb = recap_CB
        dBb = dBt - dBx - dBcb
        # --- ödemeler dengesi (mlr $) ve rezerv
        CA_usd = (NXq - int_Xf - int_Xb - int_Bf - int_Bx - int_Dx + int_R + int_OFA + int_FA) * 1000 / E
        dDx = usd((1 - pp["bx_share"]) * Fh, E)
        dBf = pp["dBf_usd"]
        KA_usd = Fh + dXf + dXb + FDI + dBf + Feq          # Hazine eurobond net ihracı + yabancı pay akımı
        dR = CA_usd + KA_usd
        dDh_usd = dDh_usd_des
        dFXL = dDh_usd + dDf_usd + dXb - dLf_usd           # bankalar döviz pozisyonunu kare tutar (OFA sabit)
        # --- haneler
        dLh = s["Lh"] * ((pi + pp["gn"]) * DT) - wo_h * 0  # kredi nominal gelirle büyür
        dLh += 0.0
        dCu = 0.022 * 4 * Yq - s["Cu"]
        S_h = YD - C
        # haneler: S_h + borç affı(wo_h) = ΔDh + E·ΔDh$ + ΔCu − ΔLh_net
        # ΔLh_net = dLh − wo_h (yeni kredi − silinen)
        dDh = S_h - U(dDh_usd) - dCu + dLh + U(Feq)        # yabancının sattığı payı haneler mevduatla alır
        # --- firmalar
        RE = Pi_f - Tf - Div
        dDf = 0.02 * (Yq - Yq_1) * 4                       # işlem ihtiyacı
        # finansman: I − RE + ΔDf + E(ΔDf$+ΔFA$) − E·ΔXf$ − E·ΔLf$ − FDI(E) = ΔLf_yeni
        FDI_tl = U(FDI)
        dLf = Iq - RE + dDf + U(dDf_usd) - U(dXf) - U(dLf_usd) - FDI_tl   # brüt yeni kredi
        # Not: wo_f ve wo_fusd borç affı (sermaye transferi) firmanın finansman ihtiyacını azaltır
        # --- bankalar: TCMB net pozisyonu artık (M_b)
        S_b = Pi_b - Tb - Div_b - recap_B        # tasarruf (recap sermaye transferi ayrı)
        dLh_net, dLf_net, dLfusd_net_tl = dLh - wo_h, dLf, U(dLf_usd) - wo_fusd
        # Lf'nin yazılan kısmı: dLf yeni kredi; stok = Lf + dLf − wo_f
        dMb = (S_b + recap_B + (dDh + dDf + dDx) + U(dDh_usd + dDf_usd + dXb)
               - (dLh - wo_h) - (dLf - wo_f) - (U(dLf_usd) - wo_fusd) - dBb - U(dFXL))
        # --- TCMB: artık (M_cb)
        S_cb = CB_profit - CB_transfer
        dMcb = U(dR) - U(dFXL) + dBcb - dCu - S_cb - recap_CB
        # ======== TUTARLILIK KONTROLLERİ ========
        # (1) gizli denklem
        hid = dMb - dMcb
        # (2) tasarruf-yatırım: Σ S (X dahil) = I  — tüm kesimler cari fazla toplamı
        S_f = RE
        S_g = -Def
        S_x = -U(CA_usd)
        SI = S_h + S_f + S_b + S_g + S_cb + S_x + recognized - Iq   # silinen krediler borçluya sermaye transferi
        checks.append((hid, SI))
        # ======== STOK GÜNCELLEME ========
        wo_fusd_usd = wo_fusd * 1000 / E
        s.update(
            Dh=s["Dh"] + dDh, Dh_usd=s["Dh_usd"] + dDh_usd, Lh=s["Lh"] + dLh - wo_h, Cu=s["Cu"] + dCu,
            Df=s["Df"] + dDf, Df_usd=s["Df_usd"] + dDf_usd, Lf=s["Lf"] + dLf - wo_f,
            Lf_usd=s["Lf_usd"] + dLf_usd - wo_fusd_usd, Xf_usd=s["Xf_usd"] + dXf + FDI,
            Bb=s["Bb"] + dBb, FXL_usd=s["FXL_usd"] + dFXL, Xb_usd=s["Xb_usd"] + dXb, Mb=s["Mb"] + dMb,
            Bt=s["Bt"] + dBt, Bf_usd=s["Bf_usd"] + dBf, R_usd=s["R_usd"] + dR, Bcb=s["Bcb"] + dBcb, Mcb=s["Mcb"] + dMcb,
            Bx=s["Bx"] + dBx, Dx=s["Dx"] + dDx, Lam_npl=Lam_npl,
            q=q_new, qT=s["qT"] * (1 + pp["gn"] * DT), EqX_u=s["EqX_u"] + du_X, EqH_u=s["EqH_u"] - du_X, Feq=Feq,
            pK=pK_1 * (1 + pi * DT - pp["delta"] * DT) + Iq,
            E=E, P=P, Yq=Yq, C=C, gk=gk, G=Gq, TR=TRq, YD=YD, icr=(Yq - W - Tind + opex) / max(1e-9, int_Lf + int_Lf_usd + int_Xf),
            i=i, pi=pi, omega=omega, ieff=ieff, g=0.75 * s["g"] + 0.25 * (4 * ((Yq / P) / (Yq_1 / s["P"]) - 1)), yT=yT, gap=(Yq / P) / yT - 1,
            v=s["v"] * (1 + (pi - pp["pistar"] - e) * DT),
            e_prev=e, ee_prev=ee, Lf_usd_prev_loss=max(0.0, e - ee) * DT * U(s["Lf_usd"] + s["Xf_usd"]) / pK_1 * 4,
        )
        pi_prev = pi
    # bilanço kontrolü: Σ V = pK
    Vf = networths(s)
    bal = sum(Vf.values()) - s["pK"]
    out["_checks"] = dict(hidden_max=max(abs(c[0]) for c in checks), SI_max=max(abs(c[1]) for c in checks), balance=bal)
    return out

# ----------------------------------------------------------------------------------------------
def shock_external(t, pp):
    if 3 <= t <= 6:
        pp["istar"] += 0.01; pp["rho0"] += 0.04

def shock_msci(t, pp, sev=1.0):
    """MSCI/S&P: gelişmekte olandan sınır piyasaya düşürülme.
    2026Q4 danışma süreci (t=1), 2027Q2 karar (t=3), 2027Q4 uygulama: pasif çıkış (t=5)."""
    if 1 <= t <= 4: pp["eq_out"] += 0.04 * sev; pp["rho0"] += 0.010 * sev   # aktif fonlar önden çıkar
    if t == 1: pp["eq_shock"] += 0.08 * sev                                   # danışma süreci duyurusu
    if t == 3: pp["eq_shock"] += 0.08 * sev                                   # karar
    if t == 5: pp["eq_passive"] += 0.12 * sev; pp["rho0"] += 0.010 * sev      # uygulama: pasif EM fonları çıkar (FM girişi net)
    if t >= 6: pp["rho0"] += 0.005 * sev                                      # kalıcı likidite/risk primi

def scenarios():
    b = copy.deepcopy(BASE)
    s1 = copy.deepcopy(b); s1["shock"] = shock_external
    s4 = copy.deepcopy(s1); s4.update(phi_rec=0.2)                 # erteleme: yapılandırma/evergreening
    s5 = copy.deepcopy(s4); s5.update(recog_t=7)                   # 2028Q2'de toplu tanıma + sermayelendirme, sonra tam tanıma
    s5_after = s5
    s6 = copy.deepcopy(s1)
    s6.update(kappa=6.0, lam_out=0.30, lam_panic=0.45, a_phase=6, tauK_extra=0.035, G_extra=0.01, nx_gain=0.004,
              omega_w=0.39, omega_f=0.375)
    s2 = copy.deepcopy(b); s2.update(a0=0.05)
    s7 = copy.deepcopy(b); s7["shock"] = lambda t, pp: shock_msci(t, pp, 1.0)
    s8 = copy.deepcopy(b); s8["shock"] = lambda t, pp: shock_msci(t, pp, 1.6)
    # Yapısal varyant: zombi kanalı kapalı. Monte Carlo çekilişi değil; diğer katsayılar aynı.
    s4z = copy.deepcopy(s4); s4z["gam_z"] = 0.0
    s5z = copy.deepcopy(s5); s5z["gam_z"] = 0.0
    return {"S0 Baz": b, "S2 Reel değerlenme sürer": s2, "S1 Dış şok": s1,
            "S4 Şok + erteleme": s4, "S4z Şok + erteleme, zombi kapalı": s4z,
            "S5 Şok + erteleme → tanıma": s5, "S5z Şok + erteleme → tanıma, zombi kapalı": s5z,
            "S3 Şok + Yeldan seti": s6, "S6 Sınır piyasa (merkez)": s7, "S7 Sınır piyasa (sert)": s8}

# ----------------------------------------------------------------------------------------------
# TEK SİSTEM PAKETİ (5 adım) — iyimser / olası / kötümser
# Raporun kendi model dosyaları ayrı bir indirgenmiş model (π_t = c + ρπ_{t−1} − D_t − K_t). Burada paket,
# bu SFC modelin kaldıraçlarına çevrilir; her satırın dayanağı rapordaki aralıktır, katsayıların çoğu VARSAYIMDIR.
# ----------------------------------------------------------------------------------------------
TS_LEVELS = {            # kötümser, olası, iyimser
    "mahsup":   (0.14, 0.20, 0.25),   # adım 1: borcun silinen payı; gerçekçi bant %14–25 (rapor aralığı %12–90, üst ucu tam ağ sınırı)
    "kappa":    (0.50, 0.50, 0.50),   # adım 3: faizi duran pay — senaryo değil karar parametresi, hepsinde sabit
    "pool":     (0.02, 0.05, 0.10),   # adım 4: 19,4 trilyon TL'lik tasarruf havuzundan senede kayan pay (V1)
    "rho_drop": (0.000, 0.002, 0.005),# adım 4: risk primi düşüşü (V4)
    "rho_atalet": (0.59, 0.55, 0.45), # adım 4/5: atalet katsayısı, hedefe endeksleme (V3); 0,59 = bugünkü
    "hekis":    (0.0, 0.5, 1.0),      # adım 5: HEKİS kapsamı (tam ölçek = −0,16 puan)
}
TS_NAMES = ("Kötümser", "Olası", "İyimser")
_ADR = adres_stoklari()
# Havuz, adim4.csv üç ölçülmüş satırın toplamı. Yoksa rapor sabiti. Senet satırı modellenmedi; pay varsayımdır.
TS_HAVUZ_MILYAR = _ADR["toplam_milyar"] if _ADR else 19361.9
TS_FX_SHARE = (_ADR["yp_milyar"] / _ADR["toplam_milyar"]) if _ADR else (6639.4 / 19361.9)
TS_NPL_COEF = 0.5                   # VARSAYIM. Repo ölçümü bu nesneyi vermez (KATSAYI.md); yerine konmadı.
TS_SETUP = 0.14                     # adım 1+2 kurulum maliyeti, trilyon TL, tek seferlik (rapor üst sınırı)

def tek_sistem(par, k, kappa=None, comp=0.0, t12=1, t34=5, t3=None, t4=None):
    """par: arka plan senaryosu; k: 0 kötümser, 1 olası, 2 iyimser. Paketi arka planın şok fonksiyonuna ekler."""
    t3 = t34 if t3 is None else t3; t4 = t34 if t4 is None else t4      # adım 3 ve adım 4–5 başlangıçları ayrı verilebilir
    L = {n: v[k] for n, v in TS_LEVELS.items()}
    if kappa is not None: L["kappa"] = kappa
    orig = par.get("shock")
    a_pi0 = par["a_pi"]; rho0 = 0.59
    senet_total = L["pool"] * TS_HAVUZ_MILYAR / INIT["E"] * TS_FX_SHARE  # mlr $ (toplam, 4 çeyrekte); havuz adim4.csv
    clip = lambda x: min(1.0, max(0.0, x))
    def sh(t, pp):
        if orig: orig(t, pp)
        r12 = clip((t - t12) / 4)    # adım 1–2: varsayılan 2027Q1–Q4 kademeli (t=2..5)
        r3 = clip((t - t3) / 4)      # adım 3: varsayılan 2028Q1–Q4 kademeli (t=6..9)
        r4 = clip((t - t4) / 4)      # adım 4–5: varsayılan 2028Q1–Q4 kademeli
        pp["npl_mult"] = 1.0 - TS_NPL_COEF * L["mahsup"] * r12
        pp["stop_int"] = L["kappa"] * r3; pp["stop_comp"] = comp
        pp["rho0"] = pp["rho0"] - L["rho_drop"] * r4
        pp["a_pi"] = a_pi0 * (1.0 + (L["rho_atalet"] / rho0 - 1.0) * r4)
        if t4 + 1 <= t <= t4 + 4: pp["senet_usd"] = senet_total / 4
        if t >= t4 + 1: pp["pi_adj"] = L["hekis"] * 0.0016 / 2.0              # 0,16 puanlık düzey kaydırması 2 yıla yayılı
        if t in (t12 + 1, t12 + 2) and L["mahsup"] > 0: pp["G_extra"] += TS_SETUP / 2 / 21.0
    q = copy.deepcopy(par); q["shock"] = sh
    return q

def ts_scenarios():
    base = BASE; shock_bg = copy.deepcopy(BASE); shock_bg["shock"] = shock_external
    out = {}
    for bg_name, bg in (("Baz", base), ("Dış şok", shock_bg)):
        out[f"{bg_name} · paketsiz"] = copy.deepcopy(bg)
        for k, n in enumerate(TS_NAMES): out[f"{bg_name} · {n}"] = tek_sistem(bg, k)
    return out

def phi_after(par):
    """S5: tanıma sonrası tam tanıma rejimi."""
    orig = par.get("shock")
    def sh(t, pp):
        if orig: orig(t, pp)
        if par["recog_t"] is not None and t > par["recog_t"]: pp["phi_rec"] = 1.0
    par = copy.deepcopy(par); par["shock"] = sh
    return par

def all_scenarios():
    sc = scenarios()
    sc["S5 Şok + erteleme → tanıma"] = phi_after(sc["S5 Şok + erteleme → tanıma"])
    z = "S5z Şok + erteleme → tanıma, zombi kapalı"
    if z in sc:
        sc[z] = phi_after(sc[z])
    return sc

def real_gdp(o):
    return np.array(o["Yann"]) / np.array(o["P"])            # yıllıklandırılmış reel GSYH (2026Q3 fiyatları)

def decomposition(res, base="S0 Baz", k=None):
    """Dağıtılmış zarar ayrıştırması: senaryo − baz, reel net servet farkı (başlangıç yıllık GSYH'nin %'si)."""
    Y0 = 84.0
    b = res[base]; out = {}
    for n, o in res.items():
        if n == base: continue
        kk = len(o["V_H"]) - 1 if k is None else k
        d = {sec: (o[f"V_{sec}"][kk] - b[f"V_{sec}"][kk]) / Y0 for sec in ["H", "F", "B", "G", "CB", "X"]}
        d["pK"] = (o["pK"][kk] - b["pK"][kk]) / Y0
        dom = d["H"] + d["F"] + d["B"] + d["G"] + d["CB"]
        d["yurtici_toplam"] = dom
        d["kontrol"] = dom + d["X"] - d["pK"]                   # = 0 olmalı (dört katlı muhasebe)
        yb, ys = real_gdp(b), real_gdp(o)
        d["kumulatif_uretim_kaybi"] = float(np.sum((yb[1:kk + 1] - ys[1:kk + 1]) / 4) / Y0)
        d["gizli_zarar"] = o["Lam"][kk] - b["Lam"][kk]
        out[n] = d
    return out

if __name__ == "__main__":
    sc = all_scenarios()
    res = {n: simulate(p) for n, p in sc.items()}
    for n, o in res.items():
        y = real_gdp(o); o["yoy"] = [float("nan")] * 4 + list(y[4:] / y[:-4] - 1)
        o["ylevel"] = list(y / y[0] * 100)
        print("\n==", n, o["_checks"])
        for k in ["pi","yoy","E","NR","CARadj","Lam","Lam_npl","debt","MAKmin"]:
            print(f"{k:8s}", " ".join(f"{x:8.3f}" for x in o[k]))
    dec_end = decomposition(res); dec_peak = decomposition(res, k=7)
    for n, d in dec_end.items(): print(n, {k: round(v, 4) for k, v in d.items()})
    for r in res.values(): r.pop("_checks", None)
    json.dump({"labels": LABELS, "results": res, "dec_end": dec_end, "dec_peak": dec_peak},
              open("sfc_results.json", "w"), ensure_ascii=False, default=float)
