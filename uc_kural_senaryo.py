"""SFC senaryo uzantısı: üç kural (sert taban) + maliyet ucuzlatma revizesi + mevcut.

Senaryo; ölçüm değil. Politika reçetesi değil; stok-akış tutarlı karşılaştırma.
Kimlik: NFP_t = NFP_{t-1} + NL_t + R_t (hazne H, F, B, K, D). Birim çıktı: milyar TL (stok/NFP);
NL/R çeyreklik akış. Panel tabanı 2026-Q1 (EVDS finansal hesaplar, OKU.txt düzeltmeleri).

Genişletme: akis_model.simulate() (F şoku yayılımı), butce_kanali.fiscal_shock() (K′ kanalı).
Hane alt: Ha/Hm/Ho (hane_alt.py); Ha borç payı varsayımdır (D_A_BASE=0,40).

Çalıştır: python3 uc_kural_senaryo.py
Çıktı: uc_kural_senaryo.csv, uc_kural_senaryo_sonuc.json, UC_KURAL_SENARYO.md
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from akis_model import IDX, L_G, SEC, load, panel, simulate
from butce_kanali import fiscal_shock
from hane_alt import ASGARI, D_A_BASE, N_A

KOK = Path(__file__).resolve().parent

# --- Eylül 2026 taban (prompt; kaynak depo dışı iddialar DOĞRULANMADI) ---
TABAN = {
    "tufe_yillik_2026": 29.73,  # bes_yil_senaryo / EVDS
    "kart_buyume_13h_yillik": 33.4,  # DOĞRULANMADI: prompt iddiası
    "tuketici_kredi_13h_yillik": 13.9,  # DOĞRULANMADI
    "asgari_net_ocak2026": ASGARI,
    "bekar_yasam_eyl2026": 48885.0,  # TÜRK-İŞ; DOĞRULANMADI bu betikte
    "telafi_tufe_varsayim_yuzde": 30.0,  # Ocak 2027 telafi formülü
}

KAMA_YARIMYIL = [3.5, 3.0, 2.5, 2.5, 2.0, 2.0, 1.5, 1.0]  # reel %, 2027-H1 .. 2030-H2

PATIKA = {
    (2027, 1): (36500, 51300, 0.71),
    (2027, 2): (40800, 55400, 0.74),
    (2028, 1): (45200, 59600, 0.76),
    (2028, 2): (49600, 63800, 0.78),
    (2029, 1): (54100, 68100, 0.80),
    (2029, 2): (58600, 69400, 0.82),
    (2030, 1): (60800, 71800, 0.83),
    (2030, 2): (62000, 73100, 0.84),
    (2031, 1): (63100, 74300, 0.85),
}

LIMIT_CARPAN = {2027: 3.0, 2028: 2.5, 2029: 2.0, 2030: 2.0, 2031: 2.0}

SEGMENT_CAP_PP = {  # yıllık stok büyümesi = TÜFE + pp (kilitli senaryo)
    "teminatsiz": -8,
    "ilk_konut": 0,
    "kobi": -2,
    "uretken": 10,
    "korunmasiz_doviz": 0,  # stok %0 hedef
}

NET_YENI_PAY = {  # yıl 1 -> yıl 3 hedef (lineer geçiş)
    1: {"teminatsiz": 0.15, "ilk_konut": 0.10, "kobi": 0.25, "uretken": 0.35},
    3: {"teminatsiz": 0.08, "ilk_konut": 0.12, "kobi": 0.18, "uretken": 0.47},
}

FIN_REEL_KAMA_100TL = {"isveren_buyuk": 70, "isveren_kobi": 45, "sgk_indirim": 35, "kamu_ucret": 20}
KOBİ_DESTEK = {2027: 0.70, 2028: 0.40, 2029: 0.15, 2030: 0.0, 2031: 0.0}
KOBİ_DESTEK_REVIZE = {2027: 0.35, 2028: 0.15, 2029: 0.05, 2030: 0.0, 2031: 0.0}
ACLik_ORAN = 37801.0 / 48885.0  # Eyl 2026 referans; DOĞRULANMADI

SENARYOLAR = ("mevcut", "uc_kural_kilitli", "maliyet_ucuz_revize")


def _get_taban() -> dict:
    """TABAN + acik_veri_ozet.json (varsa)."""
    t = dict(TABAN)
    try:
        from acik_veri_kopru import taban_girdi

        t.update({k: v for k, v in taban_girdi(t).items() if v is not None})
    except Exception:
        pass
    return t


@dataclass
class Params:
    """Açık varsayımlar; sonuç değildir."""

    ha_borc_payi: float = D_A_BASE  # VARSAYIM
    geciskenlik_kama_yansima: float = 1.0  # 0.5 -> 2031 kapsama ~%78 (prompt)
    tufe_yol: float = 0.28  # yıllık nominal, senaryo çapa (2027+)
    lam: float = 0.5  # simulate; TANIMLANAMADI ampirik
    kappa: float = 0.1
    fx_unhedged_buyume_mevcut: float = 0.06  # yıllık USD stok, VARSAYIM
    ponzi_servis_esik: float = 0.40
    hedge_servis_esik: float = 0.30
    # Revize: yaşam maliyeti öncelikli kanal (yıllık reel düşüş bandı %3–5)
    yasam_reel_dusus_yillik: float = 0.04  # VARSAYIM
    taban_yarimyil_nom_artis_yuzde: float = 0.85  # sınırlı zam; 2031 kapsama ~%75–80 bandı (maliyet düşüşü ile)
    kamu_makas_daraltma_milyarTL_ceyrek: float = 45.0  # memur standardizasyon, K′→H (VARSAYIM)
    isveren_pay_revize_100tl: float = 22.0  # sert senaryodan düşük
    sgk_indirim_revize_100tl: float = 18.0  # prim indirimi daraltıldı
    kapsama_hedef_2031: float = 0.78  # %75–80 bandı ortası


@dataclass
class State:
    nfp: np.ndarray  # trilyon TL, 5 hazne
    # borç stokları, trilyon TL (iç)
    stok: dict = field(default_factory=dict)
    net_taban: float = TABAN["asgari_net_ocak2026"]
    yasam_maliyeti: float = TABAN["bekar_yasam_eyl2026"]
    kapsama: float = 0.57  # Eyl 2026 öncesi, VARSAYIM
    kama_ek: float = 0.0  # geri bildirim +1 puan yarıyıl
    tuketim_cap_ek_pp: float = 0.0
    limit_dondur: bool = False
    uretken_pay_gecmis: list = field(default_factory=list)
    doviz_stok_gecmis: list = field(default_factory=list)
    alt20_borc_gelir_ay: float = 2.8  # VARSAYIM başlangıç
    yil_idx: int = 0  # 2027=1
    zam_faktor_ek_yuzde: float = 0.0  # geri bildirim: maliyet düşmezse taban hızlanır
    yasam_hedef_gerceklesen: float = 0.0  # izleme
    f_ucret_kanali_kumul_milyar: float = 0.0  # işveren+simulate F yükü


def _quarters():
    out = []
    for y in range(2026, 2032):
        for q in range(1, 5):
            out.append(f"{y}-Q{q}")
    return out


def _yil(donem: str) -> int:
    return int(donem.split("-")[0])


def _ceyrek(donem: str) -> int:
    return int(donem.split("-Q")[1])


def _yarimyil_idx(donem: str) -> int:
    y, q = _yil(donem), _ceyrek(donem)
    if y < 2027:
        return -1
    return (y - 2027) * 2 + (0 if q <= 2 else 1)


def _tufe_q(params: Params) -> float:
    return (1 + params.tufe_yol) ** 0.25 - 1


def _init_state(stab, tcs) -> State:
    A, Y = panel(stab, tcs, "2026-Q1")
    nfp = (A - Y).sum(axis=0) / 1e9
    h_borc = Y[:, IDX["H"]].sum() / 1e9
    f_borc = Y[:, IDX["F"]].sum() / 1e9
    d_net = nfp[IDX["D"]]
    tb = _get_taban()
    yas = float(tb.get("bekar_yasam_eyl2026") or TABAN["bekar_yasam_eyl2026"])
    net = float(tb.get("asgari_net_ocak2026") or TABAN["asgari_net_ocak2026"])
    kap = float(tb.get("kapsama_bekar_yasam") or (net / yas if yas else 0.57))
    st = State(
        nfp=nfp.copy(),
        stok={
            "H_teminatsiz": h_borc * 0.35,
            "H_kart": h_borc * 0.45,
            "H_konut": h_borc * 0.20,
            "F_kobi": f_borc * 0.55,
            "F_uretken": f_borc * 0.45,
            "D_korunmasiz_usd_mr": 120.0,  # milyar USD, VARSAYIM; DOĞRULANMADI
        },
        net_taban=net,
        yasam_maliyeti=yas,
        kapsama=kap,
    )
    return st


def _mevcut_buyume_yillik(kalem: str) -> float:
    tb = _get_taban()
    if kalem == "H_kart":
        return float(tb["kart_buyume_13h_yillik"]) / 100
    if kalem == "H_teminatsiz":
        return float(tb["tuketici_kredi_13h_yillik"]) / 100
    return 0.15  # diğer segmentler, VARSAYIM


def _kilitli_buyume_yillik(kalem: str, tufe: float, st: State) -> float:
    pp = SEGMENT_CAP_PP.get(
        {"H_teminatsiz": "teminatsiz", "H_konut": "ilk_konut", "F_kobi": "kobi", "F_uretken": "uretken"}.get(kalem, "kobi"),
        0,
    )
    if kalem == "H_kart":
        pp = SEGMENT_CAP_PP["teminatsiz"] + st.tuketim_cap_ek_pp
    g = tufe + pp / 100
    return max(g, -0.05)


def _mod(senaryo: str) -> str:
    if senaryo == "mevcut":
        return "mevcut"
    if senaryo == "uc_kural_kilitli":
        return "sert"
    return "revize"


def _kredi_kilitli(senaryo: str) -> bool:
    return senaryo in ("uc_kural_kilitli", "maliyet_ucuz_revize")


def _apply_taban_kural(st: State, donem: str, params: Params, senaryo: str):
    mod = _mod(senaryo)
    if mod == "mevcut":
        tb = _get_taban()
        st.net_taban = float(tb["asgari_net_ocak2026"])
        st.yasam_maliyeti = float(tb.get("bekar_yasam_eyl2026") or st.yasam_maliyeti)
        st.kapsama = st.net_taban / st.yasam_maliyeti if st.yasam_maliyeti else st.kapsama
        return
    y, q = _yil(donem), _ceyrek(donem)
    if mod == "sert":
        if donem == "2027-Q1":
            f = 1 + TABAN["telafi_tufe_varsayim_yuzde"] / 100
            st.net_taban = float(_get_taban()["asgari_net_ocak2026"]) * f
        yi = _yarimyil_idx(donem)
        if yi >= 0 and q in (1, 3):
            kama = KAMA_YARIMYIL[min(yi, len(KAMA_YARIMYIL) - 1)] + st.kama_ek
            st.net_taban *= 1 + (kama / 100) * params.geciskenlik_kama_yansima * 0.5
        key = (y, 1 if q <= 2 else 2)
        if key in PATIKA:
            tb, yas, kap = PATIKA[key]
            st.net_taban, st.yasam_maliyeti, st.kapsama = tb, yas, kap
        else:
            st.kapsama = st.net_taban / st.yasam_maliyeti if st.yasam_maliyeti else st.kapsama
        return
    # revize: maliyet düşüşü + sınırlı taban zamı (büyük telafi yok)
    # yasam_reel_dusus_yillik: sepet nominal düşüş hızı (kira/gıda/enerji kanalı; TÜFE ayrı yazılmaz)
    if y >= 2027 and q in (1, 3):
        yasam_once = st.yasam_maliyeti
        st.yasam_maliyeti *= 1 - params.yasam_reel_dusus_yillik / 2
        st.yasam_hedef_gerceklesen += (yasam_once - st.yasam_maliyeti) / yasam_once if yasam_once else 0.0
        artis = params.taban_yarimyil_nom_artis_yuzde + st.zam_faktor_ek_yuzde
        st.net_taban *= 1 + artis / 100
    st.kapsama = st.net_taban / st.yasam_maliyeti if st.yasam_maliyeti else st.kapsama


def _geri_bildirim(st: State, donem: str, senaryo: str, uretken_pay: float, params: Params):
    if not _kredi_kilitli(senaryo):
        return
    mod = _mod(senaryo)
    y = _yil(donem)
    st.uretken_pay_gecmis.append(uretken_pay)
    st.doviz_stok_gecmis.append(st.stok["D_korunmasiz_usd_mr"])
    if len(st.uretken_pay_gecmis) > 8:
        st.uretken_pay_gecmis.pop(0)
        st.doviz_stok_gecmis.pop(0)
    if mod == "sert":
        if y == 2027 and _ceyrek(donem) == 4 and st.kapsama < 0.73:
            st.kama_ek += 1.0
        if y == 2029 and _ceyrek(donem) == 4 and st.kapsama < 0.80:
            st.kama_ek += 1.0
    if mod == "revize" and _ceyrek(donem) == 4:
        hedef_dusus = params.yasam_reel_dusus_yillik
        gercek = min(hedef_dusus, st.yasam_hedef_gerceklesen / max(1, y - 2026))
        if gercek < hedef_dusus * 0.85:
            st.zam_faktor_ek_yuzde += 0.5  # maliyet düşmezse zam faktörü artar
        st.yasam_hedef_gerceklesen = 0.0
        if st.kapsama < params.kapsama_hedef_2031 - 0.05 and y >= 2029:
            st.zam_faktor_ek_yuzde += 0.25
    if len(st.uretken_pay_gecmis) >= 2 and all(p < 0.35 for p in st.uretken_pay_gecmis[-2:]):
        st.tuketim_cap_ek_pp -= 2.0
    if len(st.doviz_stok_gecmis) >= 2 and st.doviz_stok_gecmis[-1] > st.doviz_stok_gecmis[-2]:
        st.stok["D_korunmasiz_usd_mr"] = st.doviz_stok_gecmis[-2]  # sıfır tolerans: geri al
    if st.alt20_borc_gelir_ay > 2.5:
        st.limit_dondur = True
    else:
        st.limit_dondur = False


def _servis_orani_ha(st: State, params: Params) -> float:
    """Ha aylık servis / net gelir. Stok trilyon TL; servis oranı VARSAYIM (yıllık %35 / 12)."""
    borc_ha_tr = params.ha_borc_payi * sum(st.stok[k] for k in ("H_teminatsiz", "H_kart", "H_konut"))
    borc_tl = borc_ha_tr * 1e12
    aylik_servis = borc_tl * 0.35 / 12
    gelir = st.net_taban * N_A
    return float(aylik_servis / gelir) if gelir > 0 else 0.0


def _dti_carpan(st: State, params: Params) -> float:
    s = _servis_orani_ha(st, params)
    if s <= params.hedge_servis_esik:
        return 1.0
    if s <= params.ponzi_servis_esik:
        return 0.4
    return 0.05


def _step(
    st: State,
    donem: str,
    senaryo: str,
    params: Params,
    L,
    G,
    nfp_bin,
    kanal,
    prev_doviz,
) -> dict:
    mod = _mod(senaryo)
    kredi = _kredi_kilitli(senaryo)
    tufe_y = params.tufe_yol
    gq = _tufe_q(params)
    f_ucret_nl_milyar = 0.0

    _apply_taban_kural(st, donem, params, senaryo)

    # Stok büyümesi (çeyreklik)
    for k in list(st.stok.keys()):
        if k == "D_korunmasiz_usd_mr":
            if kredi:
                gy = SEGMENT_CAP_PP["korunmasiz_doviz"] / 100
            else:
                gy = params.fx_unhedged_buyume_mevcut
            st.stok[k] *= (1 + gy) ** 0.25
            continue
        if kredi:
            gy = _kilitli_buyume_yillik(k, tufe_y, st)
        else:
            gy = _mevcut_buyume_yillik(k) if k in ("H_kart", "H_teminatsiz") else 0.12
        mult = _dti_carpan(st, params) if k in ("H_teminatsiz", "H_kart") else 1.0
        if kredi and st.limit_dondur and k in ("H_teminatsiz", "H_kart"):
            mult = 0.0
        st.stok[k] *= (1 + gy * mult) ** 0.25

    h_top = st.stok["H_teminatsiz"] + st.stok["H_kart"] + st.stok["H_konut"]
    f_top = st.stok["F_kobi"] + st.stok["F_uretken"]
    net_yeni = (h_top + f_top) * gq * 0.15  # VARSAYIM: çeyrek net akış ~ stok * infl * 0.15
    uretken_pay = st.stok["F_uretken"] / f_top if f_top > 0 else 0.0
    _geri_bildirim(st, donem, senaryo, uretken_pay, params)

    # NL (trilyon TL / çeyrek), stok-akış tutarlı özet
    nl = np.zeros(5)
    dh = net_yeni * 0.55
    df = net_yeni * 0.45
    nl[IDX["H"]] = dh * 0.02  # net borçlanma H (tüketim kredisi açılımı)
    nl[IDX["F"]] = -df * 0.01  # F borç stok artışı karşılığı banka akışı (işaret VARSAYIM)
    nl[IDX["B"]] = (dh + df) * 0.008
    nl[IDX["D"]] = (st.stok["D_korunmasiz_usd_mr"] - prev_doviz) * 0.002  # kur kanalı kabaca

    if mod in ("sert", "revize") and _yil(donem) >= 2027:
        reel_kama_ay = max(0.0, (st.net_taban - float(_get_taban()["asgari_net_ocak2026"])) / 24)
        yil = _yil(donem)
        if mod == "sert":
            isveren_pay = FIN_REEL_KAMA_100TL["isveren_kobi"]
            destek = KOBİ_DESTEK.get(yil, 0.0)
            sgk_100 = FIN_REEL_KAMA_100TL["sgk_indirim"]
            acik_tl_bin = 10e9 / 4 if yil == 2027 else 0.0
        else:
            isveren_pay = params.isveren_pay_revize_100tl
            destek = KOBİ_DESTEK_REVIZE.get(yil, 0.0)
            sgk_100 = params.sgk_indirim_revize_100tl
            acik_tl_bin = 0.0
            # Maliyet düşüşü F marjına (girdi fiyatı), VARSAYIM
            nl[IDX["F"]] += params.yasam_reel_dusus_yillik * f_top * 0.08 / 4
        isveren_net = isveren_pay * (1 - destek) * reel_kama_ay / 100 * N_A * 1e-9
        f_hit = isveren_net * 0.25
        nl[IDX["F"]] -= f_hit
        nl[IDX["H"]] += isveren_net * 0.15
        f_ucret_nl_milyar = f_hit * 1000
        sgk_tl_bin = sgk_100 * reel_kama_ay / 100 * N_A * 1e-3 / 3
        fs = fiscal_shock("harcama", sgk_tl_bin, kanal)
        for i, s in enumerate(SEC):
            nl[i] += fs[s] / 1e9
        if acik_tl_bin:
            fs2 = fiscal_shock("vergi", acik_tl_bin * 0.5, kanal)
            for i, s in enumerate(SEC):
                nl[i] += fs2[s] / 1e9
        if mod == "revize" and _ceyrek(donem) in (1, 3):
            # Memur standardizasyon: K′ bütçe → H (Hm), F'ye yazılmaz
            fs_m = fiscal_shock("harcama", params.kamu_makas_daraltma_milyarTL_ceyrek * 1e3, kanal)
            for i, s in enumerate(SEC):
                nl[i] += fs_m[s] / 1e9
        x = np.zeros(5)
        x[IDX["F"]] = -isveren_net * 1e9
        imp = simulate(L, G, nfp_bin, x, lam=params.lam, kappa=params.kappa) / 1e9
        nl += imp * 0.05
        f_ucret_nl_milyar += float(imp[IDX["F"]] * 50)  # kısmi simulate payı, milyar
        st.f_ucret_kanali_kumul_milyar += f_ucret_nl_milyar

    if mod == "mevcut":
        # Ücret erimesi: H talep daralması (reel gelir düşüşü)
        enflasyon_kaybi = (1 + gq) ** 4 - 1
        nl[IDX["H"]] -= 0.02 * enflasyon_kaybi
        nl[IDX["F"]] += 0.01 * enflasyon_kaybi  # marj koruması VARSAYIM

    # Değerleme R: döviz maruziyet × çeyrek enflasyon/kur (basit)
    r = np.zeros(5)
    fx = np.array([0.15, 0.35, 0.25, 0.20, 0.55])  # VARSAYIM orta maruziyet
    r += fx * gq * st.nfp
    r[IDX["D"]] += (st.stok["D_korunmasiz_usd_mr"] - prev_doviz) * 0.015

    st.nfp = st.nfp + nl + r

    servis = _servis_orani_ha(st, params)
    k_butce = float(nl[IDX["K"]]) * 1000  # milyar TL

    return {
        "Donem": donem,
        "senaryo": senaryo,
        **{f"NFP_{s}": round(float(st.nfp[i]) * 1000, 1) for i, s in enumerate(SEC)},
        **{f"NL_{s}": round(float(nl[i]) * 1000, 1) for i, s in enumerate(SEC)},
        **{f"R_{s}": round(float(r[i]) * 1000, 1) for i, s in enumerate(SEC)},
        "borc_servis_orani_Ha": round(servis, 3),
        "uretken_zarf_payi": round(uretken_pay, 3),
        "korunmasiz_doviz_stok_mr_usd": round(st.stok["D_korunmasiz_usd_mr"], 1),
        "net_taban_TL": round(st.net_taban, 0),
        "yasam_maliyeti_TL": round(st.yasam_maliyeti, 0),
        "kapsama": round(st.kapsama, 3),
        "K_butce_NL_milyar": round(k_butce, 1),
        "limit_dondur": int(st.limit_dondur),
        "kama_ek_puan": st.kama_ek,
        "tuketim_cap_ek_pp": st.tuketim_cap_ek_pp,
        "zam_faktor_ek_yuzde": st.zam_faktor_ek_yuzde,
        "F_ucret_kanali_NL_milyar_ceyrek": round(f_ucret_nl_milyar, 2),
        "F_ucret_kanali_kumul_milyar": round(st.f_ucret_kanali_kumul_milyar, 1),
        "aclik_siniri_TL": round(st.yasam_maliyeti * ACLik_ORAN, 0),
        "durum": "senaryo",
    }


def run(params: Params | None = None) -> tuple[list[dict], dict]:
    params = params or Params()
    stab, _, tcs, _ = load()
    A, Y = panel(stab, tcs, "2026-Q1")
    L, G = L_G(A, Y)
    nfp_bin = (A - Y).sum(axis=0)
    kanal = pd.read_csv(KOK / "K_kanal_paylari_son4ceyrek.csv", index_col=0)

    rows = []
    tb = _get_taban()
    meta = {
        "durum": "senaryo",
        "olcum_degil": True,
        "taban_donem": "2026-Q1",
        "taban_girdi": tb,
        "parametreler": params.__dict__,
        "ha_borc_payi_not": "VARSAYIM; hane_alt D_A_BASE",
        "kredi_buyume_13h": {
            "kart_yuzde": tb.get("kart_buyume_13h_yillik"),
            "tuketici_yuzde": tb.get("tuketici_kredi_13h_yillik"),
            "kaynak": "acik_veri_ozet.json (EVDS BDDK tablo 6)",
        },
        "uc_kural_birlikte": "Eksik kural tek başına aynı sonucu vermez (prompt); karşılaştırma satırları",
    }

    for senaryo in SENARYOLAR:
        st = _init_state(stab, tcs)
        prev_d = st.stok["D_korunmasiz_usd_mr"]
        for donem in _quarters():
            if donem < "2026-Q4":
                continue
            row = _step(st, donem, senaryo, params, L, G, nfp_bin, kanal, prev_d)
            prev_d = st.stok["D_korunmasiz_usd_mr"]
            rows.append(row)

    end = "2031-Q4"
    keys = (
        "NFP_H",
        "NFP_F",
        "borc_servis_orani_Ha",
        "uretken_zarf_payi",
        "korunmasiz_doviz_stok_mr_usd",
        "kapsama",
        "net_taban_TL",
        "yasam_maliyeti_TL",
        "K_butce_NL_milyar",
        "F_ucret_kanali_kumul_milyar",
    )
    meta["karsilastirma_2031Q4"] = {
        k: {s: next(r for r in rows if r["Donem"] == end and r["senaryo"] == s)[k] for s in SENARYOLAR}
        for k in keys
    }
    sert = meta["karsilastirma_2031Q4"]["F_ucret_kanali_kumul_milyar"]["uc_kural_kilitli"]
    rev = meta["karsilastirma_2031Q4"]["F_ucret_kanali_kumul_milyar"]["maliyet_ucuz_revize"]
    meta["F_yuku_aciklama"] = (
        "Sert senaryoda yaşam maliyeti yüksek kalırken taban agresif artar; işveren payı (45 TL/100) "
        "ve geniş prim indirimi F NL yükünü büyütür. Revizede reel maliyet düşüşü marjı destekler, "
        "taban zamı küçük (%4/yarıyıl + geri bildirim), işveren payı düşük, KOBİ desteği dar, "
        "memur makası K′ kanalına yazılır → kümülatif F ücret kanalı sert: "
        f"{sert} milyar vs revize: {rev} milyar (senaryo birimi)."
    )
    meta["duyarlik_yasam_reel_dusus"] = {}
    for dusus in (0.03, 0.04, 0.05):
        p2 = Params(**{**params.__dict__, "yasam_reel_dusus_yillik": dusus})
        rows2, _ = run_one(p2, stab, tcs, L, G, nfp_bin, kanal, ("maliyet_ucuz_revize",))
        r2 = next(x for x in rows2 if x["Donem"] == end)
        meta["duyarlik_yasam_reel_dusus"][str(dusus)] = {
            "kapsama": r2["kapsama"],
            "NFP_F": r2["NFP_F"],
            "F_ucret_kanali_kumul_milyar": r2["F_ucret_kanali_kumul_milyar"],
        }
    return rows, meta


def run_one(params, stab, tcs, L, G, nfp_bin, kanal, senaryolar):
    rows = []
    for senaryo in senaryolar:
        st = _init_state(stab, tcs)
        prev_d = st.stok["D_korunmasiz_usd_mr"]
        for donem in _quarters():
            if donem < "2026-Q4":
                continue
            row = _step(st, donem, senaryo, params, L, G, nfp_bin, kanal, prev_d)
            prev_d = st.stok["D_korunmasiz_usd_mr"]
            rows.append(row)
    return rows, {}


def _md(meta: dict) -> str:
    lines = [
        "# SFC senaryo: sert taban vs maliyet ucuzlatma revizesi",
        "",
        "Stok-akış tutarlı **senaryo**; ölçüm değil. Çalıştır: `python3 uc_kural_senaryo.py`.",
        "",
        "## Senaryolar",
        "",
        "| Kod | İçerik |",
        "| --- | --- |",
        "| `mevcut` | Donuk nominal taban; kart/tüketici büyüme iddiası |",
        "| `uc_kural_kilitli` | Sert taban telafisi + kama; işveren yükü F′de |",
        "| `maliyet_ucuz_revize` | Yaşam maliyeti reel düşüş + sınırlı zam; memur K′; seçici kredi |",
        "",
        "## Revize parametreleri (VARSAYIM)",
        "",
        f"- Yaşam maliyeti reel düşüş (yıllık): `{meta['parametreler']['yasam_reel_dusus_yillik']}`",
        f"- Taban yarıyıl nominal artış %: `{meta['parametreler']['taban_yarimyil_nom_artis_yuzde']}`",
        f"- Kamu makas (milyar TL/çeyrek): `{meta['parametreler']['kamu_makas_daraltma_milyarTL_ceyrek']}`",
        "",
        "## 2031-Q4 üçlü karşılaştırma",
        "",
        "| Gösterge | Mevcut | Sert üç kural | Maliyet revize |",
        "| --- | ---: | ---: | ---: |",
    ]
    for k, v in meta["karsilastirma_2031Q4"].items():
        lines.append(
            f"| {k} | {v['mevcut']} | {v['uc_kural_kilitli']} | {v['maliyet_ucuz_revize']} |"
        )
    lines.extend(
        [
            "",
            "## F yükü",
            "",
            meta.get("F_yuku_aciklama", ""),
            "",
            "## Duyarlılık (yalnız revize; yaşam reel düşüş)",
            "",
        ]
    )
    for rate, d in meta.get("duyarlik_yasam_reel_dusus", {}).items():
        lines.append(f"- `{rate}`: kapsama {d['kapsama']}, NFP_F {d['NFP_F']}, F ücret kanalı küm. {d['F_ucret_kanali_kumul_milyar']} milyar")
    lines.extend(
        [
            "",
            "## Ne denmez",
            "",
            "- Politika önerisi veya uygulama vaadi değildir.",
            "- Kira/gıda/enerji kanalları ayrıştırılmadı; tek reel düşüş parametresi.",
            "",
        ]
    )
    return "\n".join(lines)


def main():
    try:
        from acik_veri_kopru import main as av_main

        av_main()
    except Exception as exc:  # noqa: BLE001
        print("acik_veri_kopru atlandı:", exc)
    rows, meta = run()
    cols = list(rows[0].keys())
    with (KOK / "uc_kural_senaryo.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    (KOK / "uc_kural_senaryo_sonuc.json").write_text(
        json.dumps({"meta": meta, "satirlar": rows}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (KOK / "UC_KURAL_SENARYO.md").write_text(_md(meta), encoding="utf-8")
    print("=== uc_kural_senaryo (senaryo; ölçüm değil) ===")
    print(json.dumps(meta["karsilastirma_2031Q4"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
