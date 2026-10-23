import copy, json, numpy as np, warnings, sfc_model as M
warnings.filterwarnings('ignore')
rng = np.random.default_rng(7)
keys = ["gam_z", "n_r", "n_e", "gam_cr", "beta_e", "gam_r", "kappa", "psi", "s_r", "c1"]
sc = M.all_scenarios(); N = 400; rows = []
for n in range(N):
    draw = {k: M.BASE[k] * rng.uniform(0.6, 1.4) for k in keys}
    draw["c1"] = rng.uniform(0.94, 1.0)
    s4 = copy.deepcopy(sc["S4 Şok + erteleme"]); s5 = copy.deepcopy(sc["S5 Şok + erteleme → tanıma"])
    for k, v in draw.items(): s4[k] = v; s5[k] = v
    zero = rng.uniform(0, 1) < 0.5
    if zero: s4["gam_z"] = s5["gam_z"] = 0.0          # zombi kanalı tamamen kapalı çekilişler
    try:
        o4, o5 = M.simulate(s4), M.simulate(s5)
    except Exception: continue
    y4, y5 = M.real_gdp(o4), M.real_gdp(o5)
    if not (np.all(np.isfinite(y4)) and np.all(np.isfinite(y5))): continue
    rows.append(dict(zero=zero, dy=float(np.sum(y5 - y4) / 4 / 84), ddebt=o5["debt"][-1] - o4["debt"][-1]))
a = [r for r in rows]
def share(f, sub): return sum(1 for r in sub if f(r)) / max(1, len(sub))
res = dict(N=len(a),
    out_all=share(lambda r: r["dy"] > 0, a), debt_all=share(lambda r: r["ddebt"] < 0, a),
    out_z=share(lambda r: r["dy"] > 0, [r for r in a if not r["zero"]]),
    out_nz=share(lambda r: r["dy"] > 0, [r for r in a if r["zero"]]),
    debt_nz=share(lambda r: r["ddebt"] < 0, [r for r in a if r["zero"]]),
    dy_med_z=float(np.median([r["dy"] for r in a if not r["zero"]])),
    dy_med_nz=float(np.median([r["dy"] for r in a if r["zero"]])),
    dd_med_nz=float(np.median([r["ddebt"] for r in a if r["zero"]])))
# Yapısal nokta: γ_z = 0 kopya. Çekiliş değil. Model içi karşı-olgu; veri karşı-olgusu yok.
scz = M.all_scenarios()
o4, o4z = M.simulate(scz["S4 Şok + erteleme"]), M.simulate(scz["S4z Şok + erteleme, zombi kapalı"])
o5, o5z = M.simulate(scz["S5 Şok + erteleme → tanıma"]), M.simulate(scz["S5z Şok + erteleme → tanıma, zombi kapalı"])
y4, y4z, y5, y5z = M.real_gdp(o4), M.real_gdp(o4z), M.real_gdp(o5), M.real_gdp(o5z)
res["yapi"] = dict(
    tanim="S4z ve S5z: aynı şok, gam_z=0. Diğer katsayılar S4/S5 ile aynı.",
    karsilastirma="model içi karşı-olgu. Türkiye için zombi kanalının nedensel tahmini yok.",
    etiket="aday",
    dy_acik=float(np.sum(y5 - y4) / 4 / 84),
    dy_kapali=float(np.sum(y5z - y4z) / 4 / 84),
    gsyh_s4=float(y4[-1] / y4[0] * 100),
    gsyh_s4z=float(y4z[-1] / y4z[0] * 100),
    gsyh_s5=float(y5[-1] / y5[0] * 100),
    gsyh_s5z=float(y5z[-1] / y5z[0] * 100))
print(json.dumps(res, indent=1)); json.dump(res, open("sfc_sens.json", "w"))
