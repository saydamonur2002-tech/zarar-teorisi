"""Tek Sistem paketi: senaryoları koşturur, tabloları ve grafik verisini üretir (build_page.py çağırır)."""
import copy, json
import numpy as np
import sfc_model as M

fmt = lambda x, k=1: f"{x:.{k}f}".replace(".", ",").replace("-", "−")
sgn = lambda x, k=1: ("+" if x > 0.0499 else "") + fmt(x, k)
BG = {"Baz": M.BASE, "Dış şok": None}
sb = copy.deepcopy(M.BASE); sb["shock"] = M.shock_external; BG["Dış şok"] = sb

def metrics(o):
    y = M.real_gdp(o)
    return dict(y29=y[-1] / y[0] * 100, pi_avg=float(np.mean(o["pi"][6:])) * 100, debt=o["debt"][-1] * 100,
                car=min(o["CARadj"]) * 100, nr28=o["NR"][9], E29=o["E"][-1],
                floor=next((M.LABELS[i] for i, v in enumerate(o["NR"]) if v < 15.0), "—"), _y=y)

def run(bg, k=None, **kw):
    par = BG[bg] if k is None else M.tek_sistem(BG[bg], k, **kw)
    o = M.simulate(par); m = metrics(o); m["_o"] = o; return m

def prod_gain(m, ref):          # toplam üretim farkı (başlangıç yıllık GSYH'sinin %'si), + = paketle daha yüksek
    return float(np.sum((m["_y"][1:] - ref["_y"][1:]) / 4) / 84.0) * 100

def build():
    R = {}
    for bg in BG:
        R[(bg, None, 0)] = run(bg)
        for k in range(3):
            for comp in (0.0, 1.0): R[(bg, k, comp)] = run(bg, k, comp=comp)
    names = ["Paketsiz"] + list(M.TS_NAMES)
    def row(lab, f, bg, comp):
        cells = [f(R[(bg, None, 0)], R[(bg, None, 0)])] + [f(R[(bg, k, comp)], R[(bg, None, 0)]) for k in range(3)]
        return f"<tr><td>{lab}</td>" + "".join(f'<td class="num">{c}</td>' for c in cells) + "</tr>"
    spec = [("Reel GSYH, 2029Q4 (2026Q3=100)", lambda m, r: fmt(m["y29"])),
            ("Toplam üretim farkı, paketsize göre (GSYH %)", lambda m, r: "—" if m is r else sgn(prod_gain(m, r))),
            ("Ortalama enflasyon, 2028–29 (%)", lambda m, r: fmt(m["pi_avg"])),
            ("Kamu borcu / GSYH, 2029Q4 (%)", lambda m, r: fmt(m["debt"])),
            ("Bankaların düzeltilmiş sermaye oranı, en düşük (%)", lambda m, r: fmt(m["car"])),
            ("Net rezerv, 2028Q4 (mlr $)", lambda m, r: fmt(m["nr28"])),
            ("Net rezerv tabana (15) ilk inen çeyrek", lambda m, r: m["floor"]),
            ("USD/TL, 2029Q4", lambda m, r: fmt(m["E29"]))]
    T = {}
    T["TS_MAIN_ROWS"] = "".join(row(l, f, "Baz", 0.0) for l, f in spec)
    T["TS_HAZ_ROWS"] = "".join(row(l, f, "Baz", 1.0) for l, f in spec[:5])
    T["TS_SHOCK_ROWS"] = "".join(row(l, f, "Dış şok", 0.0) for l, f in [spec[0], spec[1], spec[3], spec[4]])
    # adım 3 tasarımı (olası düzey, baz arka plan)
    rows = []; kap = {}
    ref = R[("Baz", None, 0)]
    for kappa in (0.0, 0.25, 0.5, 1.0):
        for comp, who in ((0.0, "Bankalar"), (1.0, "Hazine")):
            if kappa == 0 and comp == 1.0: continue
            m = run("Baz", 1, kappa=kappa, comp=comp); kap[(kappa, comp)] = m
            lab = "Adım 3 yok" if kappa == 0 else f"κ = {fmt(kappa, 2)}, bedeli {who.lower()} üstleniyor"
            rows.append(f'<tr><td>{lab}</td><td class="num">{fmt(m["y29"])}</td><td class="num">{fmt(m["debt"])}</td><td class="num">{fmt(m["car"])}</td><td class="num">{fmt(m["pi_avg"])}</td></tr>')
    T["TS_KAPPA_ROWS"] = "".join(rows)
    # kaldıraç bazında etki: her adım tek başına, olası düzeyde
    L = M.TS_LEVELS; neutral = dict(mahsup=0.0, kappa=0.0, pool=0.0, rho_drop=0.0, rho_atalet=0.59, hekis=0.0)
    orig = copy.deepcopy(M.TS_LEVELS); abl = []
    items = [("Adım 1–2 · mahsup ve sıralı ödeme", ["mahsup"]), ("Adım 3 · faiz durur (bankalar üstlenir)", ["kappa"]),
             ("Adım 4 · senet: döviz mevduatından kayma", ["pool"]), ("Adım 4 · senet: risk primi düşüşü", ["rho_drop"]),
             ("Adım 4–5 · atalet kırılması (endeksleme)", ["rho_atalet"]), ("Adım 5 · HEKİS", ["hekis"])]
    A = {}
    for lab, keys in items:
        M.TS_LEVELS = {n: tuple((orig[n][1] if n in keys else neutral[n]) for _ in range(3)) for n in orig}
        m = run("Baz", 1)
        A[lab] = m
        abl.append(f'<tr><td>{lab}</td><td class="num">{sgn(m["y29"] - ref["y29"])}</td><td class="num">{sgn(m["pi_avg"] - ref["pi_avg"])}</td><td class="num">{sgn(m["car"] - ref["car"])}</td><td class="num">{sgn(m["nr28"] - ref["nr28"])}</td></tr>')
    M.TS_LEVELS = orig
    T["TS_ABL_ROWS"] = "".join(abl)
    # kaldıraç tablosu
    lv = M.TS_LEVELS
    def trio(key, f): return "".join(f'<td class="num">{f(lv[key][k])}</td>' for k in range(3))
    T["TS_LEVER_ROWS"] = (
        f'<tr><td>Adım 1–2: borcun silinen payı</td>{trio("mahsup", lambda v: "%" + fmt(v*100, 0))}<td>Varsayım, bant %14–25. Repoda silinen boş; yeni_tavan 0,2582 üst sınırdır, yerine konmadı. TS_NPL_COEF=0,5 de varsayım</td></tr>'
        f'<tr><td>Adım 3: faizi duran pay (κ)</td>{trio("kappa", lambda v: fmt(v, 2))}<td>Karar parametresi; adım 3 ızgarasının ortası. Üçünde de sabit</td></tr>'
        f'<tr><td>Adım 4: havuzdan senede kayan pay</td>{trio("pool", lambda v: "%" + fmt(v*100, 0))}<td>Varsayım (rapor V1). Havuz {fmt(M.TS_HAVUZ_MILYAR, 1)} milyar TL, adim4.csv (kanıt); %{fmt(M.TS_FX_SHARE*100, 0)}\'ü YP. θ bandı (0,10–0,50) başka parametre, yerine konmadı</td></tr>'
        f'<tr><td>Adım 4: risk primi düşüşü (puan)</td>{trio("rho_drop", lambda v: fmt(v*100, 1))}<td>Rapor V4 (0 / 0,2 / 0,5), varsayım</td></tr>'
        f'<tr><td>Adım 4–5: atalet ρ</td>{trio("rho_atalet", lambda v: fmt(v, 2))}<td>Paket ölçeği 0,59. Repo yıllık ρ 0,68 (tahmin) ve çeyreklik ρ 0,45 (tahmin) başka denklem; yerine konmadı</td></tr>'
        f'<tr><td>Adım 5: HEKİS kapsamı (tam ölçek = 1)</td>{trio("hekis", lambda v: fmt(v, 1))}<td>Tam ölçekte ulusal TÜFE −0,16 puan (SISTEMLER.md, iki sistem, aday), iki yıla yayılı</td></tr>')
    # takvim: daha erken yapılabilir mi? (olası düzey, baz arka plan)
    def below14(o):
        return next((M.LABELS[i] for i, v in enumerate(o["CARadj"]) if v < 0.14), "—")
    variants = [("Mevcut takvim (adım 1–2: 2027, adım 3–5: 2028)", {}),
                ("Adım 1–2 bir çeyrek erken (2026Q4)", dict(t12=0)),
                ("Adım 3 bir yıl erken (2027)", dict(t3=1)),
                ("Adım 4–5 bir yıl erken (2027)", dict(t4=1)),
                ("Hepsi erken (adım 1–2: 2026Q4, adım 3–5: 2027)", dict(t12=0, t34=1)),
                ("Sıra ters (adım 3–5: 2027, adım 1–2: 2028)", dict(t12=5, t34=1))]
    trows = []; TV = {}
    for lab, kw in variants:
        mb = metrics(M.simulate(M.tek_sistem(BG["Baz"], 1, **kw)) and None) if False else None
        ob = M.simulate(M.tek_sistem(BG["Baz"], 1, **kw)); mb = metrics(ob)
        oh = M.simulate(M.tek_sistem(BG["Baz"], 1, comp=1.0, **kw)); mh = metrics(oh)
        TV[lab] = (mb, mh, ob)
        trows.append(f'<tr><td>{lab}</td><td class="num">{fmt(mb["y29"])}</td><td class="num">{fmt(mh["y29"])}</td><td class="num">{fmt(mb["pi_avg"])}</td><td class="num">{fmt(mb["debt"])}</td><td class="num">{fmt(mb["car"])}</td><td class="num">{below14(ob)}</td></tr>')
    T["TS_TIMING_ROWS"] = "".join(trows)
    tv = list(TV.values())
    T["TS_T_BASE_14"] = below14(tv[0][2]); T["TS_T3_14"] = below14(tv[2][2])
    T["TS_T3_Y"] = fmt(tv[2][0]["y29"]); T["TS_T3_YH"] = fmt(tv[2][1]["y29"]); T["TS_T_BASE_Y"] = fmt(tv[0][0]["y29"])
    T["TS_T12_D"] = sgn(tv[1][0]["y29"] - tv[0][0]["y29"]); T["TS_T4_D"] = sgn(tv[3][0]["y29"] - tv[0][0]["y29"])
    T["TS_T4_PI"] = sgn(tv[3][0]["pi_avg"] - tv[0][0]["pi_avg"]); T["TS_T_REV_Y"] = fmt(tv[5][0]["y29"])
    # anlatı sayıları
    ko, ol, iy = (R[("Baz", k, 0.0)] for k in range(3))
    olh = R[("Baz", 1, 1.0)]
    d3 = ol["y29"] - kap[(0.0, 0.0)]["y29"]
    T["TS_A3_VERDICT"] = ("bankalar üstlenirken adım 3 büyümeyi azaltıyor ve banka sermayesini eritiyor" if d3 < -1 else
                          "bankalar üstlenirken adım 3 büyümeye net bir şey katmıyor, ama banka sermayesini eritiyor" if d3 < 1 else
                          "adım 3 büyümeyi artırıyor ama banka sermayesini eritiyor")
    T.update(TS_CAR_A3=fmt(A["Adım 3 · faiz durur (bankalar üstlenir)"]["car"]), TS_PI_K=sgn(ko["pi_avg"] - ref["pi_avg"]), TS_PI_O=sgn(ol["pi_avg"] - ref["pi_avg"]), TS_PI_I=sgn(iy["pi_avg"] - ref["pi_avg"]),
             TS_Y_K=sgn(ko["y29"] - ref["y29"]), TS_Y_O=sgn(ol["y29"] - ref["y29"]), TS_Y_I=sgn(iy["y29"] - ref["y29"]),
             TS_CAR0=fmt(ref["car"]), TS_CAR_SHK0=fmt(R[("Dış şok", None, 0)]["car"]), TS_CAR_K=fmt(ko["car"]), TS_CAR_O=fmt(ol["car"]), TS_CAR_H=fmt(olh["car"]),
             TS_A3=sgn(A["Adım 3 · faiz durur (bankalar üstlenir)"]["y29"] - ref["y29"]),
             TS_A12=sgn(A["Adım 1–2 · mahsup ve sıralı ödeme"]["y29"] - ref["y29"]),
             TS_SUM=sgn(sum(a["y29"] - ref["y29"] for a in A.values())), TS_TOG=sgn(ol["y29"] - ref["y29"]),
             TS_K1=fmt(kap[(1.0, 0.0)]["y29"]), TS_K1H=fmt(kap[(1.0, 1.0)]["y29"]),
             TS_DEBT_H=sgn(olh["debt"] - ol["debt"]), TS_Y_H=sgn(olh["y29"] - ol["y29"]), TS_Y_NO3=sgn(kap[(0.0, 0.0)]["y29"] - ref["y29"]),
             TS_Y_SHK_K=sgn(R[("Dış şok", 0, 0.0)]["y29"] - R[("Dış şok", None, 0)]["y29"]),
             TS_Y_SHK_O=sgn(R[("Dış şok", 1, 0.0)]["y29"] - R[("Dış şok", None, 0)]["y29"]),
             TS_Y_SHK_I=sgn(R[("Dış şok", 2, 0.0)]["y29"] - R[("Dış şok", None, 0)]["y29"]))
    # grafik verisi (baz arka plan, bankalar üstlenir)
    keys = [("Paketsiz", R[("Baz", None, 0)])] + [(M.TS_NAMES[k], R[("Baz", k, 0.0)]) for k in range(3)]
    D = dict(labels=M.LABELS, names=[k for k, _ in keys])
    D["pi"] = [[round(v * 100, 3) for v in m["_o"]["pi"]] for _, m in keys]
    D["y"] = [[round(float(v / m["_y"][0] * 100), 3) for v in m["_y"]] for _, m in keys]
    D["NR"] = [[round(v, 3) for v in m["_o"]["NR"]] for _, m in keys]
    D["car"] = [[round(v * 100, 3) for v in m["_o"]["CARadj"]] for _, m in keys]
    chk = {}
    for (bg, k, comp), m in R.items(): chk[(bg, k, comp)] = m["_o"]["_checks"]
    for key, m in kap.items(): chk[("kappa",) + key] = m["_o"]["_checks"]
    hid = max(c["hidden_max"] for c in chk.values()); bal = max(abs(c["balance"]) for c in chk.values())
    si = max(c["SI_max"] for c in chk.values())
    return T, json.dumps(D, ensure_ascii=False), hid, bal, si
