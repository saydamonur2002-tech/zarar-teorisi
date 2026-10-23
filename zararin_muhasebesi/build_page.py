"""
Haftalık derleme: veriler.json -> model -> duyarlılık -> bilanço matrisi -> zararin-muhasebesi.html
Kullanım: python3 build_page.py   (aynı klasörde sfc_model.py, sfc_sens.py, sfc_body.html, css_block.txt, veriler.json)
Çıktılar: zararin-muhasebesi.html, sfc_results.json, haftalik_log.json (her çalıştırmada bir kayıt eklenir)
"""
import json, os, subprocess, sys, datetime, copy, math
os.chdir(os.path.dirname(os.path.abspath(__file__)))
V = json.load(open("veriler.json", encoding="utf-8"))
subprocess.run([sys.executable, "sfc_model.py"], check=True, stdout=subprocess.DEVNULL)
subprocess.run([sys.executable, "sfc_sens.py"], check=True, stdout=subprocess.DEVNULL)
import sfc_model as M
d = json.load(open("sfc_results.json", encoding="utf-8"))

# --- tutarlılık kontrolleri yeniden (rapor için)
chk = {n: M.simulate(p)["_checks"] for n, p in M.all_scenarios().items()}
hid = max(c["hidden_max"] for c in chk.values()); bal = max(abs(c["balance"]) for c in chk.values())
si = max(c["SI_max"] for c in chk.values())

# --- bilanço matrisi (BANKA_OZKAYNAK_TN, veriler.json banka_ozkaynak_tn)
_ac = M.acilis_bilanco()
bsm = dict(rows=_ac["rows"], nw=_ac["nw"])
json.dump(bsm, open("bsm.json", "w"), ensure_ascii=False)

# --- haftalık özet ve karşılaştırma
R = d["results"]
def snap():
    o = {}
    for n, r in R.items():
        o[n] = dict(ymin=min(r["ylevel"]), yend=r["ylevel"][-1], pi_end=r["pi"][-1], nr_min=min(r["NR"]),
                    nr_27q4=r["NR"][d["labels"].index("2027Q4")],
                    debt_end=r["debt"][-1], lam_end=r["Lam"][-1])
    o["_dec"] = {n: dict(yurtici=v["yurtici_toplam"], akim=v["kumulatif_uretim_kaybi"]) for n, v in d["dec_end"].items()}
    return o
LOG = "haftalik_log.json"
log = json.load(open(LOG, encoding="utf-8")) if os.path.exists(LOG) else []
entry = dict(tarih=datetime.date.today().isoformat(), veri_kesimi=V["veri_kesimi"], girdiler=V["degerler"], ozet=snap(),
             tutarlilik=dict(gizli_denklem=hid, stok_akim=si, bilanco=bal), kod_surumu=M.kod_surumu())
prev = log[-1] if log else None
ayni_veri = prev and prev["veri_kesimi"] == entry["veri_kesimi"] and prev["girdiler"] == entry["girdiler"]
ayni_kod = prev and prev.get("kod_surumu") == entry["kod_surumu"]
if ayni_veri and ayni_kod:
    log[-1] = entry
else:
    log.append(entry)
json.dump(log, open(LOG, "w"), ensure_ascii=False, indent=1)
base = log[-2] if len(log) >= 2 else None

fmt = lambda x, k=1: f"{x:.{k}f}".replace(".", ",").replace("-", "−")
labels = {"usd_try": ("USD/TL", 1, 2), "politika_faizi": ("Politika faizi", 100, 1), "tufe_yillik": ("TÜFE, yıllık", 100, 2),
          "brut_rezerv": ("Brüt rezerv (mlr $)", 1, 1), "swap_haric_net_rezerv": ("Swap hariç net rezerv (mlr $)", 1, 1),
          "kv_dis_borc_kalan_vade": ("KV dış borç, kalan vade (mlr $)", 1, 1), "reel_efektif_kur": ("Reel efektif kur", 1, 2),
          "emek_payi": ("Emek payı", 100, 1), "buyume_yillik": ("Büyüme, yıllık", 100, 1),
          "yabanci_hisse": ("Yabancının pay stoku (mlr $)", 1, 2), "yabanci_takas_payi": ("Yabancı takas payı", 100, 1),
          "bist100": ("BIST 100", 1, 0), "banka_ozkaynak_tn": ("Banka özkaynağı (tn TL)", 1, 3)}
if base:
    ch = []
    for k, (lab, mul, dg) in labels.items():
        a, b = base["girdiler"].get(k), V["degerler"].get(k)
        if a is None and k == "banka_ozkaynak_tn":
            a = 4.65  # önceki kayıtta anahtar yoktu; kod sabiti 4,65 idi
        if a is None or b is None or abs(a - b) < 1e-12: continue
        once, simdi = fmt(a * mul, dg), fmt(b * mul, dg)
        if once == simdi: continue
        ch.append(f"{lab}: {once} → <b>{simdi}</b>")
    o0, o1 = base["ozet"], entry["ozet"]
    out_ch = [f"S0 baz, 2029Q4 enflasyon: {fmt(o0['S0 Baz']['pi_end']*100)} → <b>{fmt(o1['S0 Baz']['pi_end']*100)}</b>",
              f"S0 baz, 2027Q4 net rezerv: {fmt(o0['S0 Baz']['nr_27q4'])} → <b>{fmt(o1['S0 Baz']['nr_27q4'])}</b> mlr $",
              f"S1 dış şok, 2027Q4 net rezerv: {fmt(o0['S1 Dış şok']['nr_27q4'])} → <b>{fmt(o1['S1 Dış şok']['nr_27q4'])}</b> mlr $",
              f"Erteleme − tanıma akım kaybı farkı: {fmt((o0['_dec']['S4 Şok + erteleme']['akim']-o0['_dec']['S5 Şok + erteleme → tanıma']['akim'])*100)} → <b>{fmt((o1['_dec']['S4 Şok + erteleme']['akim']-o1['_dec']['S5 Şok + erteleme → tanıma']['akim'])*100)}</b> GSYH puanı"]
    _g0 = M.INIT["FXL_usd"]; _ix = d["labels"].index("2027Q4")
    M.INIT["FXL_usd"] = _g0 - 2; _up = M.simulate(M.BASE)["NR"][_ix]
    M.INIT["FXL_usd"] = _g0 + 2; _dn = M.simulate(M.BASE)["NR"][_ix]
    M.INIT["FXL_usd"] = _g0; _gain = (_up - _dn) / 4
    out_ch.append(f"Duyarlılık: başlangıç net rezervi 1 mlr $ değişirse S0'ın 2027Q4 net rezervi yaklaşık <b>{fmt(_gain)}</b> mlr $ oynuyor (diğer girdiler sabitken; haftalık fark tek girdiye indirgenemez. “En düşük net rezerv” sıfıra yakın bir eşik noktasına bağlı olduğundan artık raporlanmıyor)")
    changes = ("<div class=\"callout\"><strong>Bu hafta ne değişti?</strong> Önceki güncelleme: " + base["veri_kesimi"] + ". "
               + ("Girdiler: " + " · ".join(ch) + ". " if ch else "Yeni veri yok, girdiler aynı. ")
               + "Sonuçlar: " + " · ".join(out_ch) + "." + (" " + V["not"] if V.get("not") else "") + "</div>")
else:
    changes = "<div class=\"callout\"><strong>Haftalık takip.</strong> Bu sayfa her cuma sabahı yeni verilerle yeniden hesaplanıyor. İlk karşılaştırma bir sonraki güncellemede görünecek.</div>"

# --- anlatıdaki sayılar (her hafta yeniden hesaplanır)
import numpy as np
DE = d["dec_end"]; SENS = json.load(open("sfc_sens.json"))
def pct(x, k=1, sign=False):
    t = f"{x*100:.{k}f}".replace(".", ",").replace("-", "−")
    return ("+" + t) if (sign and x > 0) else t
yoymin = lambda o: min(v for v in o["yoy"] if v is not None and v == v)
gmak = next((d["labels"][i] for i, v in enumerate(R["S4 Şok + erteleme"]["MAK_G"]) if v <= 0.05), None)
xs = [DE[n]["X"] for n in ["S1 Dış şok", "S4 Şok + erteleme", "S5 Şok + erteleme → tanıma", "S3 Şok + Yeldan seti"]]
TOK = {
 "S4_DOM": pct(DE["S4 Şok + erteleme"]["yurtici_toplam"]), "S5_DOM": pct(DE["S5 Şok + erteleme → tanıma"]["yurtici_toplam"]),
 "S4_B": pct(DE["S4 Şok + erteleme"]["B"], sign=True), "S4_LAM": pct(DE["S4 Şok + erteleme"]["gizli_zarar"], sign=True),
 "S4_DEBT": fmt(R["S4 Şok + erteleme"]["debt"][-1]*100), "S5_DEBT": fmt(R["S5 Şok + erteleme → tanıma"]["debt"][-1]*100),
 "DY_Z": fmt(SENS["dy_med_z"]*100, 0 if SENS["dy_med_z"]*100 >= 10 else 1), "DY_NZ": fmt(SENS["dy_med_nz"]*100),
 "S4_Q": fmt(DE["S4 Şok + erteleme"]["kumulatif_uretim_kaybi"]*100, 0), "S5_Q": fmt(DE["S5 Şok + erteleme → tanıma"]["kumulatif_uretim_kaybi"]*100, 0),
 "S2_NR": fmt(R["S2 Reel değerlenme sürer"]["NR"][-1]), "S4_G": fmt(-DE["S4 Şok + erteleme"]["G"]*100), "S5_G": fmt(-DE["S5 Şok + erteleme → tanıma"]["G"]*100),
 "S4_GMAK": (f"{gmak}'te" if gmak else "2029 sonuna kadar tükenmiyor"),
 "S0_YOY": fmt(-yoymin(R["S0 Baz"])*100), "S4_YOY": fmt(-yoymin(R["S4 Şok + erteleme"])*100),
 "X_MIN": fmt(min(-x for x in xs)*100), "X_MAX": fmt(max(-x for x in xs)*100), "S2_X": pct(DE["S2 Reel değerlenme sürer"]["X"], sign=True),
 "DEBT_HI": f"{(1-SENS['debt_nz'])*100:.0f}",
}
_yapi = SENS.get("yapi") or {}
if _yapi:
    TOK["YAPI_NOT"] = ("Yapısal kopya (çekiliş değil): S4z ve S5z, γ_z = 0. Tanımanın üretim avantajı zombi açıkken "
                       + fmt(_yapi["dy_acik"] * 100) + " puan, kapalıyken " + fmt(_yapi["dy_kapali"] * 100)
                       + " puan. Bu modelin kendi karşı-olgusudur; Türkiye verisinde bu kanalın nedensel tahmini yoktur.")
else:
    TOK["YAPI_NOT"] = ""
# --- sınır piyasa bölümü: kanal ayrıştırması
def mk(price=True, flows=True, rho=True, sev=1.0):
    def sh(t, pp):
        if 1 <= t <= 4:
            if flows: pp["eq_out"] += 0.04*sev
            if rho: pp["rho0"] += 0.010*sev
        if t == 1 and price: pp["eq_shock"] += 0.08*sev
        if t == 3 and price: pp["eq_shock"] += 0.08*sev
        if t == 5:
            if flows: pp["eq_passive"] += 0.12*sev
            if rho: pp["rho0"] += 0.010*sev
        if t >= 6 and rho: pp["rho0"] += 0.005*sev
    bb = copy.deepcopy(M.BASE); bb["shock"] = sh; return bb
ob = M.simulate(M.BASE); yb = M.real_gdp(ob); drows = []; chan = {}
for name, kw in [("Yalnız pay fiyatı şoku", dict(flows=False, rho=False)), ("Yalnız yabancı satışı", dict(price=False, rho=False)),
                 ("Yalnız risk primi", dict(price=False, flows=False)), ("Üçü birlikte (S6)", {})]:
    o = M.simulate(mk(**kw)); yy = M.real_gdp(o)
    cum = float(np.sum((yb[1:]-yy[1:])/4)/84); chan[name] = cum
    drows.append(f"<tr><td>{name}</td><td class=\"num\">{fmt(cum*100)}</td><td class=\"num\">{fmt((yy[-1]/yb[-1]-1)*100)}</td><td class=\"num\">{fmt(min(o['NR']))}</td><td class=\"num\">{fmt(sum(o['Feq']))}</td></tr>")
single = {k: v for k, v in chan.items() if k.startswith("Yalnız")}
smallest = min(single, key=single.get)
lead = {"Yalnız pay fiyatı şoku": "pay fiyatındaki düşüşün kendisi en küçük kanal.",
        "Yalnız yabancı satışı": "yabancı satışının kendisi en küçük kanal; fiyat ve risk primi daha çok hasar veriyor.",
        "Yalnız risk primi": "risk primi en küçük kanal; pay fiyatı ve yabancı satışı daha çok hasar veriyor."}[smallest]
if abs(sorted(single.values())[0] - sorted(single.values())[1]) < 0.002:
    lead = "pay fiyatındaki düşüş, en büyük kanal değil."
S0r, S6r, S7r = R["S0 Baz"], R["S6 Sınır piyasa (merkez)"], R["S7 Sınır piyasa (sert)"]
def share_end(n):
    import sfc_model as MM
    return None
def eqshare(o):  # yabancı payı: EqX_usd / toplam (dolar) — başlangıç oranıyla ölçeklenir
    return [e / (qv * 1.0) for e, qv in zip(o["EqX_usd"], o["q_usd"])]
tp0 = V["degerler"].get("yabanci_takas_payi", 0.344)
def takas(o):  # EqX birimi / toplam birim ≈ EqX_usd/(q_usd·MV0) oranı
    return tp0 * (o["EqX_usd"][-1] / o["EqX_usd"][0]) / (o["q_usd"][-1] / o["q_usd"][0])
mrows = [("Reel pay endeksi, en düşük (2026Q3=100)", lambda o: fmt(min(o["q_real"]))),
         ("Dolar bazlı pay endeksi, en düşük", lambda o: fmt(min(o["q_usd"]))),
         ("Yabancının pay stoku, 2029Q4 (mlr $)", lambda o: fmt(o["EqX_usd"][-1])),
         ("Yabancı payı, 2029Q4 (%)", lambda o: fmt(takas(o)*100)),
         ("Toplam yabancı pay satışı (mlr $)", lambda o: fmt(sum(o["Feq"]))),
         ("En düşük net rezerv (mlr $)", lambda o: fmt(min(o["NR"]))),
         ("USD/TL, 2029Q4", lambda o: fmt(o["E"][-1])),
         ("Enflasyon, 2029Q4 (%)", lambda o: fmt(o["pi"][-1]*100)),
         ("Reel GSYH, 2029Q4 (2026Q3=100)", lambda o: fmt(o["ylevel"][-1])),
         ("Toplam üretim kaybı, baza göre (GSYH %)", None)]
rows_html = ""
for lab, f in mrows:
    if f is None:
        cells = ["—", fmt(DE["S6 Sınır piyasa (merkez)"]["kumulatif_uretim_kaybi"]*100), fmt(DE["S7 Sınır piyasa (sert)"]["kumulatif_uretim_kaybi"]*100)]
    else:
        cells = [f(S0r), f(S6r), f(S7r)]
    rows_html += "<tr><td>" + lab + "</td>" + "".join(f"<td class=\"num\">{c}</td>" for c in cells) + "</tr>"
msci = open("msci_section.html", encoding="utf-8").read()
msci = (msci.replace("{{MSCI_ROWS}}", rows_html).replace("{{DECOMP_ROWS}}", "".join(drows)).replace("{{CHANNEL_LEAD}}", lead)
        .replace("{{TAKAS}}", fmt(tp0*100)).replace("{{TAKAS_S6}}", fmt(takas(S6r)*100))
        .replace("{{EQX0}}", fmt(V["degerler"].get("yabanci_hisse", 39.36))))
TOK["MSCI_SECTION"] = msci
# --- Tek Sistem paketi (iyimser / olası / kötümser)
import ts_run
_T, _D, _hid_ts, _bal_ts, _si_ts = ts_run.build()
hid = max(hid, _hid_ts); bal = max(bal, _bal_ts); si = max(si, _si_ts)
entry["tutarlilik"] = dict(gizli_denklem=hid, stok_akim=si, bilanco=bal)
json.dump(log, open(LOG, "w"), ensure_ascii=False, indent=1)
_ts = open("ts_section.html", encoding="utf-8").read()
for _k, _v in _T.items(): _ts = _ts.replace("{{" + _k + "}}", _v)
TOK["TS_SECTION"] = _ts.replace("{{TS_DATA}}", _D)

# --- sayfa
body = open("sfc_body.html", encoding="utf-8").read()
for k, v in TOK.items(): body = body.replace("{{" + k + "}}", v)
assert "{{" not in body, [x for x in body.split("{{")[1:3]]
tr_ay = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
y, m, g = map(int, V["veri_kesimi"].split("-")); asof = f"{g} {tr_ay[m-1]} {y}"
body = body.replace("Veri kesimi: 22 Eylül 2026", f"Veri kesimi: {asof}")
body = body.replace('<section class="col">\n  <h2><span class="sec">Özet</span>', changes.replace('<div class="callout">','<div class="callout" style="max-width:1040px">') + '\n<section class="col">\n  <h2><span class="sec">Özet</span>', 1)
for n, r in d["results"].items():
    for k, v in list(r.items()):
        if isinstance(v, list): r[k] = [None if (x is None or x != x) else round(x, 5) for x in v]
css = open("css_block.txt", encoding="utf-8").read()
head = ('<title>Zararın Muhasebesi</title>\n<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&family=IBM+Plex+Sans+Condensed:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">\n')
html = head + css + "\n" + body
html = html.replace("__DATA__", json.dumps(d, ensure_ascii=False)).replace("__BSM__", json.dumps(bsm, ensure_ascii=False)).replace("__SENS__", open("sfc_sens.json").read())
open("zararin-muhasebesi.html", "w", encoding="utf-8").write(html)
print(json.dumps(dict(veri_kesimi=V["veri_kesimi"], gizli_denklem=hid, bilanco=bal, degisim=changes), ensure_ascii=False))
