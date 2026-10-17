"""Beş adımın maliyeti ve yürütme maliyeti, adım adım. Girdi: adim4_adres_yonlendirme.csv, adim5_kira_aralik.csv (kendi adım koşuları).
Çıktı: bes_adim_maliyet.csv, BES_ADIM_MALIYET.md. Yeni model değil: var olan bantların okunması.
Yürütme maliyeti (tespit + tahsil + idari) yurutme_maliyet.py modeliyle: program akışı × ρ (ρ bandı varsayım). Adım 1 ve 2 akışı stok (tek sefer), adım 3 ve 5 yıllık, adım 4 toplam."""
import collections
import csv
import json
from pathlib import Path

import adim45_maliyet as P45
import yurutme_maliyet as Y

KOK = Path(__file__).resolve().parent


def oku(ad):
    return list(csv.DictReader(open(KOK / ad, encoding="utf-8-sig")))


def adim4():
    s = collections.defaultdict(lambda: collections.defaultdict(float))
    for x in oku("adim4_adres_yonlendirme.csv"):
        k = (float(x["theta"]), float(x["chi"]), float(x["pi"]))
        s[k]["prim"] += float(x["prim_ceyrek"])
        s[k]["kredi"] = max(s[k]["kredi"], float(x["kredi_itki_azalt_yillik"]))
        s[k]["stok"] = max(s[k]["stok"], float(x["stok"]))
    return s


def adim5():
    return {x["nesne"]: (float(x["alt"]), float(x["ust"])) for x in oku("adim5_kira_aralik.csv")}


def _tr(x, n=1):
    return f"{float(x):,.{n}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _adim5_anlat(a5):
    j = json.loads((KOK / "adim5_kira_sonuc.json").read_text(encoding="utf-8"))
    bk = j["birim_kira"]
    piy = a5["aylık piyasa kirası (kiracı başına)"]
    fark = a5["kiracı başına aylık fark (piyasa − HEKİS)"]
    hekis = a5["HEKİS havuz kirası"]
    t20, t50, t100 = (a5[f"Ho→Ha yıllık transfer, kapsama payı {k}%"] for k in (20, 50, 100))
    return (
        "**Adım 5.** Akış, ev sahibinden (Ho) kiracıya (Ha) giden transferdir (`adim5_kira_aralik.csv`). "
        f"Birim kira {_tr(bk['tl_m2_ay'], 2)} TL/m²/ay, EVDS serisi {bk['seri']}, {bk['donem']} ({bk['kapsam']}), tek ölçüm. "
        f"Konut alanı 90–110 m², kiracı hane oranı %25–30 varsayım; toplam hane {_tr(j['hane_sayisi'], 0)} elle girilmiş dış kaynaktır. "
        f"Piyasa kirası {_tr(piy[0], 0)} – {_tr(piy[1], 0)} TL/ay, HEKİS havuz kirası {_tr(hekis[0], 0)} TL/ay (model varsayımı) olduğundan fark {_tr(fark[0], 0)} – {_tr(fark[1], 0)} TL/ay'dır. "
        f"Transfer = fark × kiracı hane × kapsama payı × 12: kapsama %20'de {_tr(t20[0], 1)} – {_tr(t20[1], 1)}, %50'de {_tr(t50[0], 1)} – {_tr(t50[1], 1)}, %100'de {_tr(t100[0], 1)} – {_tr(t100[1], 1)} milyar TL/yıl. "
        "Yürütme maliyeti transferin ρ katıdır; hane içi bir aktarım olduğu için H toplamında net maliyet değil dağılımdır."
    )


def main():
    a4, a5 = adim4(), adim5()
    prim = [v["prim"] for v in a4.values()]
    kredi = [v["kredi"] for v in a4.values()]
    stok = [v["stok"] for v in a4.values()]
    orta = a4[(0.25, 0.5, 0.05)]
    tr = {k: a5[f"Ho→Ha yıllık transfer, kapsama payı {k}%"] for k in (20, 50, 100)}
    kira = a5["kira akışı yıllık (yol A)"]
    h = Y.hepsi()
    y1, y2, y3, y4, y5 = h["1"], h["2"], h["3"], h["4"], h["5"]
    R = Y.RHO
    sat4 = lambda ad: (f"{y4['yurutme'][ad][0]:.1f}", f"{y4['yurutme'][ad][1]:.1f}")
    rows = [("1", "maliyet", "yok", "", "", "milyar TL", "—", "Adım 1 stok; maliyet satırı yok."),
            ("2", "maliyet", "yok", "", "", "milyar TL", "—", "Temerrüt 0, parametre; maliyet satırı yok."),
            ("3", "maliyet", "yok", "", "", "milyar TL", "—", "Kredi ihtiyacı 0; faizin durması modellenmedi.")]
    etk = {"alt": "alt", "orta": "orta", "pilot": "pilot payı", "ust": "üst"}
    fmt = lambda ad: f"{R[ad]:.1%}" if ad == "alt" else f"{R[ad]:.0%}"
    for n, y, ad_ in (("1", y1, "ortak stok"), ("2", y2, "silinen")):
        rows.append((n, f"yürütme ρ={fmt('alt')} (üst sınır): {ad_} {y['akis']:,.1f} × ρ", "modellendi_ust_sinir", f"{y['yurutme']['alt']:.1f}", f"{y['yurutme']['alt']:.1f}", "milyar TL (tek sefer)", "yurutme_maliyet.py",
                     ("Silinen tutar boş: ortak stok silinebilecek en çok. " if n == "1" else "Mahsupla silinen (Faz 2 düğümlü ağ; kenarlar varsayım, üst sınır). ") + f"ρ ≥ %9 uygulanmaz: {y['uygulanmaz']['orta']:,.0f}-{y['uygulanmaz']['ust']:,.0f} milyar TL gerçekçi değil."))
    for k, a in y3.items():
        for ad in R:
            rows.append(("3", f"yürütme ρ={fmt(ad)} ({etk[ad]}), κ={k}: duran faiz {a['akis']:,.1f} × ρ", "modellendi_band", f"{a['yurutme'][ad]:.1f}", f"{a['yurutme'][ad]:.1f}", "milyar TL/yıl (2029)", "yurutme_maliyet.py", "κ varsayım; r_t ileri sabit (Faz 3)." if (k, ad) == (min(y3), "alt") else ""))
    rows += [
        ("4", "maliyet: prim toplamı 2029-2031", "band_varsayim", f"{min(prim):.1f}", f"{max(prim):.1f}", "milyar TL", "adim4_adres_yonlendirme.csv", f"12 senaryo; orta (θ 0,25 χ 0,5 π 0,05) {orta['prim']:.1f}. Endeks bacağı hesaplanmadı: alt sınır olabilir."),
        ("4", "maliyet: kredi daralması (tepe, yıllık)", "band_varsayim", f"{min(kredi):.1f}", f"{max(kredi):.1f}", "milyar TL/yıl", "adim4_adres_yonlendirme.csv", f"Orta {orta['kredi']:.1f}. Banka mevduat kaybı × 0,08."),
        ("4", f"yürütme ρ={R['alt']:.1%} (alt)", "modellendi_band", *sat4("alt"), "milyar TL (2029-31)", "yurutme_maliyet.py", "Prim toplamı × ρ. ρ dayanağı zayıf: hedeflenmiş transfer idaresi aralığı senet ihracına taşındı."),
        ("4", f"yürütme ρ={R['orta']:.0%} (orta)", "modellendi_band", *sat4("orta"), "milyar TL (2029-31)", "yurutme_maliyet.py", f"Orta senaryo prim {y4['orta_senaryo_akis']:.1f} × ρ = {y4['yurutme_orta_senaryo']['orta']:.1f}."),
        ("4", f"yürütme ρ={R['pilot']:.0%} (pilot payı)", "modellendi_band", *sat4("pilot"), "milyar TL (2029-31)", "yurutme_maliyet.py", "hekis_model pilot SAFETY=1,25 (karar)."),
        ("4", f"yürütme ρ={R['ust']:.0%} (üst)", "modellendi_band", *sat4("ust"), "milyar TL (2029-31)", "yurutme_maliyet.py", ""),
    ]
    c45 = P45.maliyet()
    pl45, _ = P45.plasebo()
    rows += [("4.5", "fayda", "plasebo", "0", "0", "milyar TL", "adim45_maliyet.py", "TL bileşen payları λ'dan bağımsız (aritmetik gereği); repo tanımı: ADIM45_BIRIM.md, λ=1 parite."),
             ("4.5", "yürütme A: basım + yazılım", "modellendi_band", f"{c45['A'][0]:.2f}", f"{c45['A'][1]:.2f}", "milyar TL (tek sefer, 2030 penceresi)", "adim45_maliyet.py", f"Basım ≈ 10 milyon $ × 49,1274 (sabit çapa) + kurum başı yazılım 20-100 bin $ × N (100-1.000, varsayım)."),
             ("4.5", "yürütme B: tam yeni birim (GSYH %0,3-1,0), üst referans", "modellendi_band", f"{c45['B'][0]:.1f}", f"{c45['B'][1]:.1f}", "milyar TL (tek sefer)", "adim45_maliyet.py", f"GSYH 2025 {c45['gsyh']:,.1f} milyar TL (tavan_akis.csv); aralık ikincil kaynak.")]
    for k in ("20", "50", "100"):
        a = y5[k]
        rows.append(("5", f"maliyet: Ho→Ha transferi, kapsama %{k}", "band_varsayim", f"{a['akis_alt']:.1f}", f"{a['akis_ust']:.1f}", "milyar TL/yıl", "adim5_kira_aralik.csv", "H içi aktarım; H toplam NL 0." if k == "20" else ""))
    for k in ("20", "50", "100"):
        a = y5[k]
        for ad, etk in (("alt", "alt"), ("orta", "orta"), ("pilot", "pilot payı"), ("ust", "üst")):
            lo, hi = a["yurutme"][ad]
            rows.append(("5", f"yürütme ρ={R[ad]:.1%} ({etk}), kapsama %{k}" if ad == "alt" else f"yürütme ρ={R[ad]:.0%} ({etk}), kapsama %{k}", "modellendi_band", f"{lo:.1f}", f"{hi:.1f}", "milyar TL/yıl", "yurutme_maliyet.py", "Transfer × ρ." if (k, ad) == ("20", "alt") else ""))
    with open(KOK / "bes_adim_maliyet.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["adim", "kalem", "durum", "alt", "ust", "birim", "kaynak", "not"])
        w.writerows(rows)
    L = ["# Beş adımın maliyeti ve yürütme maliyeti, adım adım", "",
         "Çalıştır: `python3 bes_adim_maliyet.py`. Çıktı: `bes_adim_maliyet.csv`. Maliyet satırları adım 4 ve 5'in kendi koşularındaki bantlardan; yürütme satırları `yurutme_maliyet.py` modelinden. Tüm sayılar varsayım bandı; ölçüm değil.", "",
         "Yürütme maliyeti = tespit + tahsil + idari maliyet. Model (`yurutme_maliyet.py`): yürütme = program akışı × ρ. Program akışı: adım 1'de ortak stok, adım 2'de mahsupla silinen, adım 3'te yıllık duran faiz, adım 4'te prim toplamı, adım 5'te Ho→Ha transferi; adım 1 (ortak stok) ve 2 (mahsupla silinen) için stok, yalnız alt ρ ile üst sınır; adım 3 (duran faiz) için yıllık akış. ρ bandı varsayım: %0,4 / %9 / %25 (pilot payı) / %29; alt, orta ve üst uçlar Grosh'a atfedilen hedefleme idaresi aralığı (ikincil kaynak, doğrulanmadı), %25 `hekis_model` pilot payı (karar). Bileşenlere (tespit/tahsil/idari) ayrılmadı: yalnız toplam.", ""]

    L += ["## Maliyet nereden geliyor (sırayla)", "",
          "**Genel kural.** Yürütme maliyeti = program akışı × ρ. Akış her adımın kendi koşusundan okunur; ρ (tespit + tahsil + idari payı) dışarıdan gelen bir orandır ve hiçbir adımın ölçümü değildir. ρ'nun dört değeri: %0,4 / %9 / %29, Grosh'a atfedilen hedefleme idaresi aralığının alt ucu, bildirilen ortalaması ve üst ucu (ikincil kaynak, doğrulanmadı); %25 `hekis_model` pilotundaki pay (bedel/sübvansiyon ≥ 1,25; karar).", "",
          "**Adım 1.** Akış, `adim1_stok.csv` TOPLAM satırındaki ortak stoktur: 20.363,4 milyar TL. Altı sektör çiftinin her birinde iki yön bacağı metinden alınır; ters yön metinde yoksa EVDS konsolide olmayan aynı-araç üst sınırı konur, çift düzeyinde ortak = min. Silinen tutarı veren kimden-kime tablosu depoda yok, bu yüzden stok silinebilecek en çok tutardır. Bu stoğa yalnız ρ'nun alt ucu (%0,4) uygulanır, sonuç 81,5 milyar TL tek seferlik üst sınırdır; %9 ve üstü gerçekçi olmayan tutar verdiği için kullanılmaz.", "",
          "**Adım 2.** Akış, mahsupla silinen 14.602,3 milyar TL'dir (`adim2_nace_ag.csv`, silinen oranı %88,5). Ağ 17 NACE kısmı (Sektör Bilançoları 2024), 17 hane düğümü ve bir dış düğümden oluşur, 322 kenar vardır. Düğümler ölçümdür, kenar dağılımı çekim/RAS varsayımıdır ve tam grafta silinen oran üst sınırdır. Aynı nedenle yalnız %0,4 uygulanır: 58,4 milyar TL, tek seferlik üst sınır.", "",
          "**Adım 3.** Akış, duran faizdir (`adim3_faiz_durma.csv`): D = κ·u₂·S₀, I = ψ·(r/4)·D. S₀, EVDS'te firmaların kredi yükümlülüğüdür (F.4, 2026-Q1): 25.339,8 milyar TL, ölçüm. r, ticari kredi faizidir (TP.KTF17), son gözlem 2026-09'da %53,19 ve sonrası sabit tutulur (varsayım). ψ = 3.143,4 / (0,6038 × 14.527,5) = 0,3584, Sektör Bilançoları kapsamı ile EVDS arasındaki oran. κ (0,25; 0,5; 1,0) varsayımdır. 2029'da yıllık duran faiz 1.207,6 / 2.415,6 / 4.830,8 milyar TL olur ve yürütme maliyeti bunun ρ katıdır (ρ %9'da 108,7 / 217,4 / 434,8 milyar TL/yıl).", "",
          "**Adım 4.** İhraç, θ · 19.361,9 · Δu₃'tür; 19.361,9, üç ölçülmüş adres stokunun toplamıdır (hane vadeli mevduat 8.322,4 + firma vadeli mevduat 4.400,1 + gerçek kişi YP mevduat 6.639,4; 2026-Q1). θ ∈ {0,1; 0,25; 0,5}, yenileme χ ∈ {0; 0,5}, prim π ∈ {%2; %5} varsayımdır; ihraççı K′ de varsayımdır. 12 senaryoda 2029–2031 toplam prim 77,5 ile 1.058,9 milyar TL arasında, bankaların mevduat kaybından doğan yıllık kredi daralması (× 0,08) 154,9 ile 774,5 milyar TL arasındadır. Yürütme maliyeti prim toplamının ρ katıdır; ρ'nun bu adımdaki dayanağı en zayıftır, çünkü hedeflenmiş transfer idaresi için bildirilen aralık mevduat senedine taşınmıştır. Senedin endeks bacağı hesaplanmadığı için prim alt sınır olabilir.", "",
          "**Adım 4.5.** Tanım repodadır (`ADIM45_BIRIM.md`): mevcut TL'den yeni fiat TL'ye geçiş, λ = 1 parite (varsayım), yeni lira altın ya da döviz üzerinde alacak değil, kur çapası 49,1274 TL/USD (`bes_yil_senaryo.csv` taban, tüm yıllarda sabit), pencere 2030-Q1..Q4. TL para stoku 16.472,8 milyar TL (2026-Q1). Plasebo kontrolü (`ADIM45_MALIYET.md`): TL bileşen payları λ'dan bağımsız aynı kalır; bu aritmetik gereğidir, para yanılsaması ve yuvarlama enflasyonu modelde yok. Fayda sıfır; tek gerçek terim yürütme maliyeti: A (banknot basımı ≈ 10 milyon $ × 49,1274 + kurum başı yazılım 20–100 bin $ × 100–1.000 kurum, varsayım) 0,59 – 5,40 milyar TL; B (tam yeni birim, GSYH 2025'in %0,3–1,0'ı, ikincil kaynak) 189,7 – 632,4 milyar TL üst referans.", "",
          _adim5_anlat(a5), ""]
    for n, ad in (("1", "stok"), ("2", "temerrüt ve ücret"), ("3", "faiz durma"), ("4", "adres yönlendirme (senet)"), ("4.5", "yeni para birimi (plasebo)"), ("5", "kira")):
        L += [f"## Adım {n}: {ad}", ""]
        for r in (x for x in rows if x[0] == n):
            if r[3]:
                L.append(f"- **{r[1]}**: {r[3]} – {r[4]} {r[5]} (`{r[2]}`). {r[7]}".rstrip())
            else:
                L.append(f"- **{r[1]}**: `{r[2]}`. {r[7]}".rstrip())
        L.append("")
    L += ["## Ne denmez", "",
          "- 'Yürütme maliyeti ölçüldü' denmez; ρ bandı varsayım, program akışı bant. Adım 1 ve 2 stok mahsubu: yalnız alt ρ, üst sınır; bu oran stok temizliği için bile iyimser olabilir.",
          "- ρ'nun dayanağı ikincil kaynak (Grosh'a atfedilen %0,4-29); adım 4'te (mevduat senedi) daha da zayıf.",
          "- Adım 4 ve 5 maliyetleri toplanmaz: biri prim ve kredi daralması, öteki hane içi aktarım.",
          "- Bantlar güven aralığı değil; varsayım aralığının uçları.", ""]
    (KOK / "BES_ADIM_MALIYET.md").write_text("\n".join(L), encoding="utf-8")
    print("BES_ADIM_MALIYET ok")


if __name__ == "__main__":
    main()
