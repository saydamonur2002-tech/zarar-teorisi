"""Çıpalı senaryo koşusu. Ölçüt: ON_KAYIT.md. Çıktı ölçüm değildir.

Kilitli üç senaryonun csv'sine yazmaz.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from uc_kural_senaryo import (
    KAMA_YARIMYIL,
    Params,
    _dti_carpan,
    _geri_bildirim,
    _init_state,
    _kilitli_buyume_yillik,
    _limit_yasam_korel,
    _mevcut_buyume_yillik,
    _quarters,
    _yarimyil_idx,
    load,
)

KOK = Path(__file__).resolve().parent
H = 5.0
IZGARA = (0.0, 0.25, 0.50, 0.75, 1.0)
UFUK = [q for q in _quarters() if q >= "2026-Q4"]


def _tr(x, n=2):
    if x is None:
        return "—"
    if isinstance(x, bool):
        return "evet" if x else "hayır"
    try:
        return f"{float(x):.{n}f}".replace(".", ",")
    except (TypeError, ValueError):
        return str(x)


def _katsayi(t: dict, rejim: str) -> dict | None:
    b, g, f, k = t["beklenti"].get(rejim, {}), t["gecis"].get(rejim, {}), t["faiz"].get(rejim, {}), t["kur"].get(rejim, {})
    if not all(d.get("kuruldu") for d in (b, g, f, k)):
        return None
    return {
        "w": b["w"], "phi": b["phi"],
        "alfa_pass": g["alfa"], "lam": g["lam"],
        "alfa_i": f["alfa"], "rho": f["rho"], "beta_pi": f["beta_pi"], "beta_e": f["beta_e"],
        "alfa_g": k["alfa_g"], "beta_i": k["beta_i"],
    }


def _karistir(a: dict, b: dict, k: int) -> dict:
    o = k / 20.0
    return {anahtar: a[anahtar] + (b[anahtar] - a[anahtar]) * o for anahtar in a}


def _yillik(parca: list[float]) -> float:
    carpan = 1.0
    for p in parca:
        carpan *= 1.0 + p / 100.0
    return 100.0 * (carpan - 1.0)


def _hazirla(t: dict) -> dict:
    bas = t["baslangic"]
    g = list(bas["g_ceyrek_son4"])
    p = list(bas["pi_ceyrek_son4"])
    sapma = []
    if any(x is None for x in g):
        g12 = float(bas["gozlem"]["g12"])
        g = [g12 / 4.0] * 4
        sapma.append("SAPMA-g12. Senaryo öncesi dört çeyrek kur farkı kurulamadı. g12 dört eşit parçaya bölündü. Eşik kaymadı.")
    if any(x is None for x in p):
        pi = float(bas["gozlem"]["pi"])
        p = [((1 + pi / 100.0) ** 0.25 - 1.0) * 100.0] * 4
        sapma.append("SAPMA-pi. Senaryo öncesi dört çeyrek fiyat farkı kurulamadı. Yıllık yüzde dört eşit çeyreğe bölündü. Eşik kaymadı.")
    return {
        "g": [float(x) for x in g],
        "p": [float(x) for x in p],
        "pi": float(bas["gozlem"]["pi"]),
        "g12": float(bas["gozlem"]["g12"]),
        "e": float(bas["gozlem"]["e"]),
        "i": float(bas["gozlem"]["i"]),
        "R": float(bas["rezerv_milyar"]),
        "sapma": sapma,
    }


def _stok_adim(st, yillik_ondalik: float, kilitli: bool, params: Params) -> None:
    for k in list(st.stok.keys()):
        if k == "D_korunmasiz_usd_mr":
            gy = 0.0 if kilitli else params.fx_unhedged_buyume_mevcut
            st.stok[k] *= (1 + gy) ** 0.25
            continue
        if kilitli:
            gy = _kilitli_buyume_yillik(k, yillik_ondalik, st)
        else:
            gy = _mevcut_buyume_yillik(k) if k in ("H_kart", "H_teminatsiz") else 0.12
        mult = _dti_carpan(st, params) if k in ("H_teminatsiz", "H_kart") else 1.0
        if kilitli and st.limit_dondur and k in ("H_teminatsiz", "H_kart"):
            mult = 0.0
        st.stok[k] *= (1 + gy * mult) ** 0.25


def calistir(cekirdek, t: dict, spec: dict) -> dict:
    """spec: mod, faiz (sabit|tepkili), kilitli, w, lam, beta_e_sifir."""
    params = Params()
    stab, _, tcs, _ = cekirdek
    st = _init_state(stab, tcs)
    kap0 = st.net_taban / st.yasam_maliyeti if st.yasam_maliyeti else 0.0
    bas = _hazirla(t)
    a = _katsayi(t, "R2426")
    b = _katsayi(t, "R2013")
    mod = spec["mod"]
    if mod == "a" or mod == "izgara":
        paket0 = None if a is None else dict(a)
    elif mod == "b":
        paket0 = None if b is None else dict(b)
    elif mod == "c1":
        paket0 = _katsayi(t, "R1617")
    elif mod == "c2":
        paket0 = _katsayi(t, "R1823")
    elif mod == "d":
        paket0 = None if a is None or b is None else dict(a)
    else:
        paket0 = None
    if paket0 is None:
        return {"kosuldu": False, "neden": "katsayı yok", "kap0": kap0, "sapma": bas["sapma"]}
    tepkili = spec["faiz"] == "tepkili"
    c = t["rezerv"].get("c") if tepkili else None
    durum = {
        "g": list(bas["g"]),
        "p": list(bas["p"]),
        "pi": bas["pi"],
        "g12": bas["g12"],
        "e": bas["e"],
        "i": bas["i"],
        "i_giren": bas["i"],
        "R": bas["R"],
    }
    senaryo = "uc_kural_kilitli" if spec["kilitli"] else "mevcut"
    rows = []
    patlama = False
    tuk_once = st.stok["H_teminatsiz"] + st.stok["H_kart"]
    for k, donem in enumerate(UFUK):
        if mod == "d":
            paket = _karistir(a, b, k)
        else:
            paket = dict(paket0)
        if spec.get("w") is not None:
            paket["w"] = spec["w"]
        if spec.get("lam") is not None:
            paket["lam"] = spec["lam"]["lam"]
            paket["alfa_pass"] = spec["lam"]["alfa"]
        if spec.get("beta_e_sifir"):
            paket["beta_e"] = 0.0
        if spec.get("phi") is not None:
            paket["phi"] = spec["phi"]
        e24 = paket["w"] * H + (1.0 - paket["w"]) * durum["pi"] + paket["phi"] * durum["g12"]
        if tepkili:
            i_yeni = (
                paket["alfa_i"]
                + paket["rho"] * durum["i"]
                + paket["beta_pi"] * durum["pi"]
                + paket["beta_e"] * (durum["e"] - H)
            )
        else:
            i_yeni = bas["i"]
        g_ham = 3.0 * (paket["alfa_g"] + paket["beta_i"] * durum["i_giren"])
        if tepkili and c not in (None, 0):
            satis = min(durum["R"], c * max(g_ham, 0.0))
            durum["R"] = durum["R"] - satis
            g = g_ham - satis / c
        else:
            satis = 0.0
            g = g_ham
        pi_q = 3.0 * paket["alfa_pass"] + paket["lam"] * g
        if not all(map(_sonlu, (e24, i_yeni, g, pi_q, durum["R"]))):
            patlama = True
            break
        yasam_once = st.yasam_maliyeti
        if spec["kilitli"]:
            st.net_taban *= 1.0 + e24 / 400.0
            yil = int(donem[:4])
            cey = int(donem[-1])
            if yil >= 2027 and cey in (1, 3):
                yi = _yarimyil_idx(donem)
                kama = KAMA_YARIMYIL[min(max(yi, 0), len(KAMA_YARIMYIL) - 1)] + st.kama_ek
                st.net_taban *= 1.0 + (kama / 100.0) * params.geciskenlik_kama_yansima * 0.5
        st.yasam_maliyeti *= 1.0 + pi_q / 100.0
        if st.yasam_maliyeti <= 0 or st.net_taban <= 0:
            patlama = True
            break
        st.kapsama = st.net_taban / st.yasam_maliyeti
        _limit_yasam_korel(st, yasam_once, donem, senaryo, params)
        cap0 = st.tuketim_cap_ek_pp
        doviz_once = st.stok["D_korunmasiz_usd_mr"]
        durum["p"] = durum["p"][1:] + [pi_q]
        durum["g"] = durum["g"][1:] + [g]
        pi_y = _yillik(durum["p"])
        if abs(pi_y) > 500:
            patlama = True
            break
        _stok_adim(st, pi_y / 100.0, spec["kilitli"], params)
        doviz_ara = st.stok["D_korunmasiz_usd_mr"]
        f_top = st.stok["F_kobi"] + st.stok["F_uretken"]
        uretken = st.stok["F_uretken"] / f_top if f_top else 0.0
        if spec["kilitli"]:
            _geri_bildirim(st, donem, senaryo, uretken, params)
        tuk = st.stok["H_teminatsiz"] + st.stok["H_kart"]
        buyume = 100.0 * (tuk / tuk_once - 1.0) if tuk_once else 0.0
        tuk_once = tuk
        oncul_pay = len(st.uretken_pay_gecmis) >= 2 and all(p < 0.35 for p in st.uretken_pay_gecmis[-2:])
        rows.append({
            "donem": donem,
            "e24": e24,
            "i": i_yeni,
            "g": g,
            "pi_q": pi_q,
            "pi_y": pi_y,
            "kapsama": st.kapsama,
            "net_taban": st.net_taban,
            "yasam": st.yasam_maliyeti,
            "R": durum["R"],
            "satis": satis,
            "buyume_tuketici": buyume,
            "tetik_cap": st.tuketim_cap_ek_pp < cap0 - 1e-9,
            "tetik_snap": st.stok["D_korunmasiz_usd_mr"] < doviz_ara - 1e-6,
            "oncul_pay": oncul_pay,
            "oncul_doviz": doviz_ara > doviz_once + 1e-6,
            "uretken": uretken,
            "limit_dondur": bool(st.limit_dondur),
        })
        durum["pi"] = pi_y
        durum["g12"] = sum(durum["g"])
        durum["e"] = e24
        durum["i"] = i_yeni
        durum["i_giren"] = i_yeni
    return {
        "kosuldu": True,
        "patlama": patlama,
        "kap0": kap0,
        "satir": rows,
        "sapma": bas["sapma"],
        "rezerv_aktif": bool(tepkili and c not in (None, 0)),
        "c": c,
    }


def _sonlu(x: float) -> bool:
    return x == x and abs(x) != float("inf")


def sarmal_mi(yol: dict, pi0: float) -> bool:
    if not yol.get("kosuldu"):
        return False
    if yol["patlama"]:
        return True
    satir = yol["satir"]
    if not satir:
        return False
    y = [r["pi_y"] for r in satir]
    ardisik = False
    for i in range(len(y) - 3):
        if y[i + 1] > y[i] and y[i + 2] > y[i + 1] and y[i + 3] > y[i + 2]:
            ardisik = True
            break
    return ardisik and y[-1] > pi0 + 5.0


def k1(yol: dict) -> str:
    if not yol.get("kosuldu"):
        return "sinanmadi"
    if yol["patlama"]:
        return "kaldi"
    kap0 = yol["kap0"]
    kap = [r["kapsama"] for r in yol["satir"]]
    if not kap or kap[-1] < kap0 - 0.02:
        return "kaldi"
    for a, b in zip(kap, kap[1:]):
        if a < 0.95 * kap0 and b < 0.95 * kap0:
            return "kaldi"
    return "gecti"


def k2(kilitli: dict, mevcut: dict) -> str:
    if not kilitli.get("kosuldu") or not mevcut.get("kosuldu"):
        return "sinanmadi"
    if kilitli["patlama"] or mevcut["patlama"]:
        return "sinanmadi"
    n = min(len(kilitli["satir"]), len(mevcut["satir"]))
    fark = [
        mevcut["satir"][i]["buyume_tuketici"] - kilitli["satir"][i]["buyume_tuketici"]
        for i in range(n)
    ]
    return "gecti" if sum(d > 0.5 for d in fark) >= 4 else "kaldi"


def k3(yol: dict) -> str:
    if not yol.get("kosuldu") or yol["patlama"]:
        return "sinanmadi"
    tetik = any(r["tetik_cap"] or r["tetik_snap"] for r in yol["satir"])
    oncul_cevapsiz = any(
        (r["oncul_pay"] and not r["tetik_cap"]) or (r["oncul_doviz"] and not r["tetik_snap"])
        for r in yol["satir"]
    )
    if oncul_cevapsiz:
        return "kaldi"
    if tetik:
        return "gecti"
    return "sinanmadi"


def birlikte(a: str, b: str, c: str) -> str:
    if "kaldi" in (a, b, c):
        return "kaldi"
    if "sinanmadi" in (a, b, c):
        return "belirsiz"
    return "gecti"


def tukendi(yol: dict) -> bool:
    if not yol.get("kosuldu"):
        return False
    return any(r["R"] <= 1e-9 for r in yol["satir"])


def _h_sarmal(a_var: list[bool], b_var: list[bool], kosuldu: bool) -> str:
    if not kosuldu:
        return "BELİRSİZ"
    if all(a_var) and not any(b_var):
        return "Ayakta"
    if any(a_var) and any(b_var):
        return "Yanlışlandı"
    return "BELİRSİZ"


def _h_rezerv(c_var: bool, a_tuken: bool, b_tuken: bool) -> str:
    if c_var and b_tuken:
        return "Yanlışlandı"
    if c_var and a_tuken and not b_tuken:
        return "Ayakta"
    return "BELİRSİZ"


def _h_gecis(tanim: str, eski: dict, yeni: dict) -> str:
    if tanim != "tutar" or not eski.get("kosuldu") or not yeni.get("kosuldu"):
        return "BELİRSİZ"
    eski_kotu = k1(eski) == "kaldi" or sarmal_mi(eski, eski.get("pi0", 0))
    yeni_kotu = k1(yeni) == "kaldi" or sarmal_mi(yeni, yeni.get("pi0", 0))
    yeni_iyi = k1(yeni) == "gecti" and not sarmal_mi(yeni, yeni.get("pi0", 0))
    if eski_kotu and yeni_iyi:
        return "Ayakta"
    if yeni_kotu:
        return "Yanlışlandı"
    return "BELİRSİZ"


def _h_c1(izgara_kayit: list[dict]) -> tuple[str, str | None]:
    """K3 bütün ızgarada sınanmadıysa BELİRSİZ. Eşik, w ≥ 0,50 ve iki varyantın birlikte geçtiği en küçük w."""
    k3_puan = any(
        s["k3_sabit"] in ("gecti", "kaldi") or s["k3_tepkili"] in ("gecti", "kaldi")
        for s in izgara_kayit
    )
    gecen = [
        s["w"] for s in izgara_kayit
        if s["w"] >= 0.50 and s["sabit"] == "gecti" and s["tepkili"] == "gecti"
    ]
    if not k3_puan:
        return "BELİRSİZ", None
    if gecen:
        return "Ayakta", str(min(gecen))
    return "Yanlışlandı", None


def _boot_aralik(b: dict | None) -> str:
    if not b or not b.get("kuruldu"):
        return "kurulamadı"
    return f"[{_tr(b['p2_5'], 3)}; {_tr(b['p97_5'], 3)}]"


def _boot_satir(ad: str, d: dict) -> str:
    return f"| {ad} | {_boot_aralik(d.get('boot_w'))} | {_boot_aralik(d.get('boot_phi'))} |"


def rapor(t: dict, ozet: dict) -> str:
    b = t["beklenti"]

    def satir_bek(ad: str) -> str:
        d = b.get(ad, {})
        if not d.get("kuruldu"):
            return f"| {ad} | kurulamadı | | | | |"
        return (
            f"| {ad} | {d['n']} | {_tr(d['w'], 3)} | {_tr(d['geriye'], 3)} | {_tr(d['phi'], 3)} | "
            f"[{_tr(d['uc_w'][0], 3)}; {_tr(d['uc_w'][1], 3)}] |"
        )

    def satir_lam(ad: str) -> str:
        d = t["gecis"].get(ad, {})
        if not d.get("kuruldu"):
            return f"| {ad} | kurulamadı | | |"
        return f"| {ad} | {d['n']} | {_tr(d['lam'], 3)} | [{_tr(d['uc_lam'][0], 3)}; {_tr(d['uc_lam'][1], 3)}] |"

    L = [
        "# Çıpalı üç kural",
        "",
        "Ön kayıt `cipali_uc_kural/ON_KAYIT.md` içinde 2026-10-21T07:01:45Z kilitlendi. Katsayılar ondan sonra hesaplandı. Eşikler kaydırılmadı.",
        "",
        "Bu metin senaryo çubuklarının tutup tutmadığını yazar. Çıpa bir sonucu doğurdu denmez. Katsayılar [TAHMİN]. Koşu ölçüm değildir.",
        "",
        "Veri çekimi EVDS3 herkese açık uçtur (`https://evds3.tcmb.gov.tr/igmevdsms-dis`), anahtarsız. EVDS anahtarı okunmadı.",
        "",
        "## Hüküm",
        "",
        f"- H-C1, çıpa geri gelince üç kural: **{ozet['H-C1']}**. Eşik çıpa düzeyi: **{ozet['esik'] or 'yok'}**.",
        f"- H-Sarmal: **{ozet['H-Sarmal']}**.",
        f"- H-Rezerv: **{ozet['H-Rezerv']}**.",
        f"- H-Gecis, 2024–25 geçiş çöküşü: **{ozet['H-Gecis']}**.",
        f"- Ücret ayağı (üç kural eşiği değildir): iki varyantta birden K1’in geçtiği en küçük ızgara w = **{ozet['ucret_esik'] or 'yok'}**. Geçen küme: {ozet['ucret_kume']}.",
        "",
        "## Beklenti [TAHMİN]",
        "",
        "Denklem serbest terimsiz: e − π = w (h − π) + φ g12. Geriye bakış 1 − w. 0,37 ve 0,71 girdi değildir.",
        "",
        "| Pencere | n | w | 1 − w | φ | w Newey-West %95 |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
        satir_bek("R2013"),
        satir_bek("R1617"),
        satir_bek("R1823"),
        satir_bek("R2426"),
        satir_bek("Y2018"),
        "",
        "Çiftler bootstrap, tohum 20261021, B = 1000, yüzdelik 2,5–97,5.",
        "",
        "| Pencere | w bootstrap | φ bootstrap |",
        "| --- | --- | --- |",
        *[
            _boot_satir(ad, b.get(ad, {}))
            for ad in ("R2013", "R1617", "R1823", "R2426", "Y2018")
        ],
        "",
        "Hedef her ay 5. Yıl yılı nokta hedef belgesi inip farklı bir sayı vermedi: [DOĞRULANMADI].",
        f"Hüküm faizi: {t.get('faiz_etiket')} TP.APIFON4 (ağırlıklı ortalama fonlama). Bir hafta repo tablosu hüküm serisi olmadı.",
        "",
        "## Geçiş [TAHMİN]",
        "",
        "π1 = α + λ g1. λ aynı ayın kurdan fiyata oranıdır.",
        "",
        "| Pencere | n | λ | Newey-West %95 |",
        "| --- | ---: | ---: | --- |",
        *[satir_lam(ad) for ad in ("R2013", "R1617", "R1823", "R2426", "Y2018")],
        "",
        f"2024-01..2025-12 çöküş tanımı: **{t['cokus_2024_2025'].get('tanim')}**. "
        f"λ = {_tr(t['cokus_2024_2025'].get('lam'), 3)}. "
        "Tanım, bu λ’nın 2013 noktasının yarısından küçük olmasını ve %95 üst ucunun 2013 noktasının altında kalmasını ister. Tutmayınca kaldırılacak çöküş yoktur.",
        "",
        "λ bootstrap: "
        + "; ".join(
            f"{ad} {_boot_aralik(t['gecis'].get(ad, {}).get('boot_lam'))}"
            for ad in ("R2013", "R2426")
        )
        + ".",
        "",
        "## Rezerv vekili",
        "",
        f"θ = {_tr(t['rezerv'].get('theta'), 4)}, c = {_tr(t['rezerv'].get('c'), 3)}. "
        f"{t['rezerv'].get('c_not') or 'c kuruldu'}. S, brüt rezerv düşüşüdür [VEKİL], yayımlanmış satış değildir.",
        "",
        "## Koşular",
        "",
        "Kilitli yol. Birlikte: K1 ücret, K2 tavan, K3 geri alma tetiki.",
        "",
        "| Paket | Faiz | K1 | K2 | K3 | Birlikte | Sarmal | Enflasyon 2031 | Kapsama 2031 |",
        "| --- | --- | --- | --- | --- | --- | --- | ---: | ---: |",
    ]
    for ad, hucre in ozet["tablolar"]:
        L.append(
            f"| {ad} | {hucre['faiz']} | {hucre['k1']} | {hucre['k2']} | {hucre['k3']} | {hucre['birlikte']} | "
            f"{'var' if hucre['sarmal'] else 'yok'} | {_tr(hucre.get('pi_son'), 1)} | {_tr(hucre['kapsama'], 3)} |"
        )
    L.append("")
    tetik_top = sum(h.get("tetik") or 0 for _, h in ozet["tablolar"])
    dondur_tam = all((h.get("dondur") or 0) == 21 for _, h in ozet["tablolar"])
    L.append(
        f"K3 tetik sayısı tablodaki kilitli yolların toplamında {tetik_top}. "
        + ("Tüketici tavanı dondurması her yolun 21 çeyreğinde açık. " if dondur_tam else "")
        + "Dondurma, alt dilim borç varsayımı eşik üstünde kaldığı için açıktır; çıpa ağırlığı bu sayacı değiştirmez. "
        + ("K3 öncülü oluşmadığı için sınanmadı." if tetik_top == 0 else "Tetik görülen yollar tabloda K3 sütunundadır.")
    )
    L += [
        "",
        "## Izgara",
        "",
        "Diğer katsayılar R2426 noktasında. Yalnız w değişir.",
        "",
        "| w | Sabit birlikte | Tepkili birlikte | K1 sabit | K1 tepkili |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for s in ozet["izgara"]:
        L.append(
            f"| {_tr(s['w'], 2)} | {s['sabit']} | {s['tepkili']} | {s['k1_sabit']} | {s['k1_tepkili']} |"
        )
    L.append("")
    L.append(
        "K1 iki varyantta birden yalnız tabloda geçtiği w düzeylerinde tutulur. "
        "w yükseldikçe ücret kuralı kalır: taban hedefe yakınsamış beklentiyi izler, yaşam maliyeti gerçekleşen enflasyonla yürür. "
        "Bu en küçük w, çıpa geri gelince üç kuralın açıldığı eşik değildir. O eşik H-C1’dedir ve kurulamadı."
    )
    L += ["", "## Duyarlılık", "", "Hükmü değiştirmez. [TAHMİN].", ""]
    L.append("| Pencere | 6 ay enflasyonda w | 3 ay kurda φ | gecikmeli λ |")
    L.append("| --- | ---: | ---: | ---: |")
    duy = t.get("duyarlilik", {}).get("beklenti", {})
    gecik = t.get("duyarlilik", {}).get("gecis_gecikme", {})
    for ad in ("R2013", "R1617", "R1823", "R2426", "Y2018"):
        p6 = (duy.get(ad) or {}).get("pi6")
        g3 = (duy.get(ad) or {}).get("g3")
        gl = gecik.get(ad)
        L.append(
            f"| {ad} | {_tr(None if not p6 else p6.get('w'), 3)} | {_tr(None if not g3 else g3.get('phi'), 3)} | "
            f"{_tr(None if not gl else gl.get('lam'), 3)} |"
        )
    L += [
        "",
        "## Zayıf noktalar",
        "",
        *ozet["zayif"],
        "",
        "## Ne denmez",
        "",
        "- Çıpa enflasyonu indirdi veya üç kuralı işletti denmez. Çubuk senaryo yolunda tutuldu veya tutulmadı.",
        "- 0,37 ve 0,71 bu turda yeniden bulunan katsayı diye yazılmaz.",
        "- Fonlama maliyeti bir hafta repo diye yazılmaz.",
        "- Brüt rezerv düşüşü müdahale satışı diye yazılmaz.",
        "",
    ]
    return "\n".join(L)


def _ozet_hucre(yol: dict, mevcut: dict, pi0: float) -> dict:
    kk1, kk2, kk3 = k1(yol), k2(yol, mevcut), k3(yol)
    satir = yol["satir"] if yol.get("kosuldu") else []
    R = satir[-1]["R"] if satir else None
    kap = satir[-1]["kapsama"] if satir else None
    pi_son = satir[-1]["pi_y"] if satir else None
    return {
        "k1": kk1, "k2": kk2, "k3": kk3,
        "birlikte": birlikte(kk1, kk2, kk3),
        "sarmal": sarmal_mi(yol, pi0) if yol.get("kosuldu") else False,
        "R": R, "kapsama": kap, "pi_son": pi_son,
        "dondur": sum(bool(r["limit_dondur"]) for r in satir),
        "tetik": sum(bool(r["tetik_cap"] or r["tetik_snap"]) for r in satir),
        "tuken": tukendi(yol),
        "patlama": yol.get("patlama"),
    }


def main() -> dict:
    t = json.loads((KOK / "tahmin.json").read_text(encoding="utf-8"))
    pi0 = float(t["baslangic"]["gozlem"]["pi"])
    cekirdek = load()
    sapma = list(t.get("sapma") or [])
    tablolar = []
    yollar = {}
    for mod in ("a", "b", "c1", "c2", "d"):
        for faiz in ("sabit", "tepkili"):
            for kilitli, adk in ((False, "mevcut"), (True, "kilitli")):
                spec = {"mod": mod, "faiz": faiz, "kilitli": kilitli}
                yol = calistir(cekirdek, t, spec)
                yollar[(mod, faiz, adk)] = yol
                sapma.extend(yol.get("sapma") or [])
            if yollar[(mod, faiz, "kilitli")].get("kosuldu"):
                h = _ozet_hucre(yollar[(mod, faiz, "kilitli")], yollar[(mod, faiz, "mevcut")], pi0)
                h["faiz"] = faiz
                tablolar.append((f"({mod}) {adk_etiket(mod)}", h))
    izgara = []
    for w in IZGARA:
        hucre = {"w": w}
        for faiz, anahtar in (("sabit", "sabit"), ("tepkili", "tepkili")):
            kil = calistir(cekirdek, t, {"mod": "izgara", "faiz": faiz, "kilitli": True, "w": w})
            mev = calistir(cekirdek, t, {"mod": "izgara", "faiz": faiz, "kilitli": False, "w": w})
            o = _ozet_hucre(kil, mev, pi0)
            hucre[anahtar] = o["birlikte"]
            hucre[f"k3_{anahtar}"] = o["k3"]
            hucre[f"k1_{anahtar}"] = o["k1"]
            hucre[f"yol_{anahtar}"] = o
        izgara.append(hucre)
    hc1, esik = _h_c1(izgara)
    a_sabit = yollar.get(("a", "sabit", "kilitli"), {})
    a_tep = yollar.get(("a", "tepkili", "kilitli"), {})
    b_sabit = yollar.get(("b", "sabit", "kilitli"), {})
    b_tep = yollar.get(("b", "tepkili", "kilitli"), {})
    kosuldu_ab = all(y.get("kosuldu") for y in (a_sabit, a_tep, b_sabit, b_tep))
    hs = _h_sarmal(
        [sarmal_mi(a_sabit, pi0), sarmal_mi(a_tep, pi0)],
        [sarmal_mi(b_sabit, pi0), sarmal_mi(b_tep, pi0)],
        kosuldu_ab,
    )
    hr = _h_rezerv(
        t["rezerv"].get("c") is not None,
        tukendi(a_tep),
        tukendi(b_tep),
    )
    # geçiş kontrastı
    cokus = t["cokus_2024_2025"]
    r2013g = t["gecis"].get("R2013", {})
    eski = yeni = {"kosuldu": False}
    if cokus.get("kuruldu") and r2013g.get("kuruldu"):
        eski = calistir(cekirdek, t, {"mod": "a", "faiz": "tepkili", "kilitli": True, "lam": cokus})
        yeni = calistir(cekirdek, t, {"mod": "a", "faiz": "tepkili", "kilitli": True, "lam": r2013g})
        eski["pi0"] = pi0
        yeni["pi0"] = pi0
    hg = _h_gecis(cokus.get("tanim", "belirsiz"), eski, yeni)
    ucret = [s["w"] for s in izgara if s["k1_sabit"] == "gecti" and s["k1_tepkili"] == "gecti"]
    # köşe
    phi = t["beklenti"]["R2426"]
    lam = t["gecis"]["R2426"]
    kose_esik = []
    if phi.get("kuruldu") and lam.get("kuruldu"):
        for fp in (phi["uc_phi"][0], phi["uc_phi"][1]):
            for lp_ad, lp in (("alt", lam["uc_lam"][0]), ("ust", lam["uc_lam"][1])):
                gecen_k = []
                for w in IZGARA:
                    ikisi = []
                    for faiz in ("sabit", "tepkili"):
                        yol = calistir(
                            cekirdek, t,
                            {"mod": "izgara", "faiz": faiz, "kilitli": True, "w": w, "phi": fp,
                             "lam": {"lam": lp, "alfa": lam["alfa"]}},
                        )
                        mev = calistir(
                            cekirdek, t,
                            {"mod": "izgara", "faiz": faiz, "kilitli": False, "w": w, "phi": fp,
                             "lam": {"lam": lp, "alfa": lam["alfa"]}},
                        )
                        ikisi.append(k1(yol) == "gecti")
                    if all(ikisi):
                        gecen_k.append(w)
                kose_esik.append(min(gecen_k) if gecen_k else None)
    zayif = [
        "- `uc_kural_senaryo.py` içinde faiz kuralı ve rezerv stoku yoktu. Bu koşu o iki katmanı ayrı kurdu; kilitli üç senaryonun 2031 tablosu yeniden yazılmadı.",
        "- Ücret kuralı PATIKA tablosunu ezmez. Taban, beklentiyle yürür. Bu, kilitli dosyanın kendi 2031 kapsama sayısının aynısı değildir.",
        "- K3, üretken pay ve korunmasız stok öncülü yolun içinde oluşmazsa sınanmadı kalır. Mekanik tavan (alt20 başlangıcı 2,8) K2’yi çıpadan bağımsız bağlayabilir; ölçüm yine de mevcut yolla farktır.",
        "- Faiz TP.APIFON4’tür [VEKİL]. Bir hafta repo ile aynı şey diye okunmaz.",
        "- Rezerv satışı brüt stok düşüşünden gelen c’dir [VEKİL]. c yoksa rezerv hükmü BELİRSİZ.",
        "- Hedef 5, yıl belgesi inmeden [DOĞRULANMADI].",
        "- Senaryo 2026-Q4’ten 2031-Q4’e kadardır. Patlama (yıllık enflasyonun mutlak değeri 500’ü aşarsa) sarmal ve ücret kalır diye yazılır; yol yapıştırılmaz.",
        "- R1617 kur denklemi 2016–17 fonlama aralığında kuruldu. Sabit faiz yolu onu 2026 fonlama düzeyine taşır; (c1) sabit yolda 2031 enflasyonu eksiye yazar. Bu ölçüm değildir.",
    ]
    if kose_esik:
        zayif.append(
            "- φ ve λ Newey-West uçlarında ücret ayağının geçen en küçük w kümesi: "
            + ", ".join("yok" if x is None else _tr(x, 2) for x in kose_esik)
            + ". Bu küme hükmü değiştirmez."
        )
    # βe = 0 duyarlılığı
    be0 = []
    for mod in ("a", "b"):
        yol = calistir(cekirdek, t, {"mod": mod, "faiz": "tepkili", "kilitli": True, "beta_e_sifir": True})
        be0.append(f"({mod}) K1 {k1(yol)}, sarmal {'var' if sarmal_mi(yol, pi0) else 'yok'}")
    zayif.append("- βe = 0 duyarlılığı, tepkili kilitli: " + "; ".join(be0) + ". Birincil hüküm βe’li denklemdedir.")
    ozet = {
        "H-C1": hc1,
        "esik": esik,
        "H-Sarmal": hs,
        "H-Rezerv": hr,
        "H-Gecis": hg,
        "ucret_esik": None if not ucret else _tr(min(ucret), 2),
        "ucret_kume": "yok" if not ucret else ", ".join(_tr(w, 2) for w in ucret),
        "izgara": [{k: v for k, v in s.items() if not k.startswith("yol_")} for s in izgara],
        "tablolar": [(a, h) for a, h in tablolar],
        "zayif": zayif,
        "pi0": pi0,
    }
    # JSON için tabloları düzleştir
    dump = {
        "H-C1": hc1,
        "esik": esik,
        "H-Sarmal": hs,
        "H-Rezerv": hr,
        "H-Gecis": hg,
        "ucret_esik": ozet["ucret_esik"],
        "izgara": ozet["izgara"],
        "kosular": [
            {"paket": a, **h} for a, h in tablolar
        ],
        "etiket": "TAHMIN",
        "olcum_degil": True,
    }
    (KOK / "sonuclar.json").write_text(json.dumps(dump, ensure_ascii=False, indent=1), encoding="utf-8")
    (KOK / "RAPOR.md").write_text(rapor(t, ozet), encoding="utf-8")
    _sapma_yaz(sapma)
    print(json.dumps({k: dump[k] for k in ("H-C1", "esik", "H-Sarmal", "H-Rezerv", "H-Gecis", "ucret_esik")}, ensure_ascii=False))
    return dump


def adk_etiket(mod: str) -> str:
    return {
        "a": "R2426 çıpasız",
        "b": "R2013",
        "c1": "R1617",
        "c2": "R1823",
        "d": "kademeli",
    }.get(mod, mod)


def _sapma_yaz(satirlar: list) -> None:
    tek = []
    gor = set()
    for s in satirlar:
        if isinstance(s, str):
            im = s
            govde = s
        else:
            im = s.get("kod", "") + str(s.get("ay", "")) + s.get("not", "")[:80]
            if s.get("kod") == "SAPMA-endeks":
                continue
            govde = s.get("not") or json.dumps(s, ensure_ascii=False)
        if im in gor:
            continue
        gor.add(im)
        tek.append(govde)
    n_endeks = sum(1 for s in satirlar if isinstance(s, dict) and s.get("kod") == "SAPMA-endeks")
    if n_endeks:
        tek.append(f"SAPMA-endeks. Arşiv ile 2025 baz yıllık yüzdesi 0,30 puandan fazla ayrılan ay sayısı {n_endeks}. O aylarda 2025 bazı kullanıldı. Eşik kaymadı.")
    if not tek:
        return
    damga = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    yol = KOK / "ON_KAYIT.md"
    ek = "\n".join(f"- {s}" for s in tek)
    metin = yol.read_text(encoding="utf-8")
    im = "\n## SAPMA (hesap sonrası"
    if im in metin:
        metin = metin[: metin.find(im)].rstrip() + "\n"
    yol.write_text(metin + f"\n## SAPMA (hesap sonrası, {damga})\n\n{ek}\n", encoding="utf-8")


if __name__ == "__main__":
    main()
