"""Adım 4.5 (repoda adim45_birim.py: TL'den yeni fiat TL'ye geçiş) için plasebo kontrolü ve yürütme maliyeti.

Repodaki tanım (ADIM45_BIRIM.md) olduğu gibi alınır: λ = 1 parite (varsayım), yeni lira altın/döviz üzerinde alacak değildir, TL_yeni = TL_eski·(1+u·(λ−1)),
kur_yeni = λ·kur_eski, USD stoku ve faiz oranları durur, pencere 2030-Q1..Q4 (u = 0,25 / 0,50 / 0,75 / 1,0), 2005 sıfır atması bu adımda yoktur.
Sabit çapa: `bes_yil_senaryo.csv` doviz_usd_try taban satırı, tüm yıllarda 49,1274 TL/USD (TP.DK.USD.A.YTL, 2026-10); kur_yeni = λ·49,1274.

Bu dosya yeni bir model kurmaz. Yaptığı iki şey:
 1) Plasebo: λ = 1 (repo) ve λ ≠ 1 (örnek; repoda ölçülmedi) için TL stok paylarını ve USD/faiz çarpanlarını `adim45_birim.olcek` ile çevirip değişmediğini sınar.
 2) Yürütme maliyeti: dönüştürülen birim için basım + yazılım (A) ve tam yeni birim için GSYH payı (B, üst referans).
Maliyet kaynakları: A banknot basımı ≈ 10 milyon $ (2004 sıfır atma tahmini, Hürriyet; 'ek maliyet değil' denmişti), yazılım kurum başına 20-100 bin $ (TCMB Başkan Yardımcısı aktarımı), kurum sayısı 100-1.000 (varsayım).
B: GSYH'nin %0,3-1,0'ı (Avro bölgesine girenlerde bildirilen aralık, ikincil kaynak, doğrulanmadı). GSYH 2025 cari: tavan_akis.csv (63.240,5 milyar TL); kur: 49,1274.
Aşamalama: maliyet pencere çeyreklerine Δu ile dağıtılır (varsayım)."""
import csv
import json
from pathlib import Path

import adim45_birim as B

KOK = Path(__file__).resolve().parent
KUR = 49.1274  # bes_yil_senaryo.csv, doviz_usd_try taban
BANKNOT_MN_USD = 10.0
YAZILIM_USD = (20_000, 100_000)
KURUM_N = (100, 1000)  # varsayım
B_ORAN = (0.003, 0.010)
LAMLAR = {"parite (repo, λ=1)": 1.0, "örnek: λ=0,001": 1e-3, "örnek: λ=1e-6 (2005 türü)": 1e-6}
U = {"2030-Q1": 0.25, "2030-Q2": 0.50, "2030-Q3": 0.75, "2030-Q4": 1.0}


def gsyh_2025():
    for x in csv.DictReader(open(KOK / "tavan_akis.csv", encoding="utf-8-sig")):
        if x["yil"] == "2025":
            return float(x["gsyh"])
    raise KeyError("tavan_akis.csv 2025")


def girdiler():
    d = json.loads((KOK / "adim45_birim.json").read_text(encoding="utf-8"))
    return d["stok_milyar"], d["r_2025_durur"]


def paylar(stok, lam, u=1.0):
    """TL para bileşenlerinin payları (çevrilmiş stoklardan); USD ve faiz çarpanı."""
    tl = {k: B.olcek(stok[k], lam, u) for k in ("tcmb_nakit", "yurtici_tl_mevduat")}
    top = sum(tl.values())
    return {"tcmb_nakit/TL para": tl["tcmb_nakit"] / top, "mevduat/TL para": tl["yurtici_tl_mevduat"] / top}, top


def plasebo():
    stok, r = girdiler()
    p0, t0 = paylar(stok, 1.0, 0.0)
    out = {}
    for ad, lam in LAMLAR.items():
        p1, t1 = paylar(stok, lam, 1.0)
        out[ad] = {"lam": lam, "max_fark_pay": max(abs(p0[k] - p1[k]) for k in p0), "tl_para_toplam_yeni": t1, "oran_t1_t0": t1 / t0,
                   "kur_yeni": lam * KUR, "usd_stok_carpan": 1.0, "faiz_carpan": 1.0}
    return out, stok


def maliyet():
    basim = BANKNOT_MN_USD * KUR / 1000
    yaz = (YAZILIM_USD[0] * KURUM_N[0] * KUR / 1e9, YAZILIM_USD[1] * KURUM_N[1] * KUR / 1e9)
    A = (basim + yaz[0], basim + yaz[1])
    g = gsyh_2025()
    Bm = (B_ORAN[0] * g, B_ORAN[1] * g)
    return {"basim": basim, "yazilim": yaz, "A": A, "B": Bm, "gsyh": g}


def asama(deger):
    """Çeyrek payı: Δu (varsayım)."""
    out, once = {}, 0.0
    for q, u in U.items():
        out[q] = deger * (u - once)
        once = u
    return out


def main():
    pl, stok = plasebo()
    c = maliyet()
    rows = []
    for ad, v in pl.items():
        rows.append(["4.5", f"plasebo: {ad}", "oran", f"{v['max_fark_pay']:.2e}", "", "birimsiz", "adim45_maliyet.py", f"TL para {stok['tl_para_toplam']:,.1f} → {v['tl_para_toplam_yeni']:,.4g}; kur_yeni {v['kur_yeni']:.4g}; USD stok ve faiz ×1."])
    rows += [["4.5", "yürütme A: basım + yazılım", "modellendi_band", f"{c['A'][0]:.2f}", f"{c['A'][1]:.2f}", "milyar TL (tek sefer, 2030 penceresi)", "adim45_maliyet.py", f"Basım {c['basim']:.2f}; yazılım {c['yazilim'][0]:.2f}-{c['yazilim'][1]:.2f} (N=100-1.000 varsayım). Yeni birim parite iken de yeni banknot gerekir (varsayım)."],
             ["4.5", "yürütme B: tam yeni birim (GSYH %0,3-1,0), üst referans", "modellendi_band", f"{c['B'][0]:.1f}", f"{c['B'][1]:.1f}", "milyar TL (tek sefer)", "adim45_maliyet.py", f"GSYH 2025 {c['gsyh']:,.1f} milyar TL (tavan_akis.csv); aralık ikincil kaynak."]]
    for q, v in asama(c["A"][1]).items():
        rows.append(["4.5", f"A üst ucu, {q} (Δu={0.25})", "modellendi_band", f"{asama(c['A'][0])[q]:.2f}", f"{v:.2f}", "milyar TL", "adim45_maliyet.py", "Δu ile eşit dağılım (varsayım)."])
    with open(KOK / "adim45_maliyet.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["adim", "kalem", "durum", "alt", "ust", "birim", "kaynak", "not"])
        w.writerows(rows)
    L = ["# Adım 4.5: plasebo kontrolü ve yürütme maliyeti", "",
         "Çalıştır: `python3 adim45_maliyet.py`. Çıktı: `adim45_maliyet.csv`. Adım 4.5'in tanımı `ADIM45_BIRIM.md`'dedir (yeni fiat TL, λ=1 parite, 2030-Q1..Q4); bu dosya o tanıma yalnız plasebo kontrolü ve yürütme maliyeti ekler.", "",
         "## Tanım (repodan)", "",
         "- Yeni lira altın ya da döviz üzerinde alacak değildir; dolara çevrilerek ödenmez. λ = 1 paritedir (varsayım). 2005'teki sıfır atma o adımda yoktur.",
         "- TL_yeni = TL_eski · (1 + u·(λ−1)); kur_yeni = λ · kur_eski; USD stoku ve faiz oranları durur; ΣNL = 0; `silinen` boş.",
         f"- Sabit çapa: `bes_yil_senaryo.csv` içinde USD/TRY taban satırı tüm yıllarda 49,1274 (TP.DK.USD.A.YTL, 2026-10). λ=1 iken kur_yeni = 49,1274.",
         "- Pencere: 2030-Q1..Q4, u = 0,25 / 0,50 / 0,75 / 1,0. TL para stoku (2026-Q1 ölçüm): " + f"{stok['tl_para_toplam']:,.1f} milyar TL (TCMB nakit {stok['tcmb_nakit']:,.1f} + yurt içi TL mevduat {stok['yurtici_tl_mevduat']:,.1f}).", "",
         "## Plasebo kontrolü", "",
         "TL para bileşenlerinin payları, repodaki `olcek` ile çevrilmiş stoklardan hesaplanır; kur λ ile ölçeklenir, USD stoku ve faiz çarpanı 1 kalır.", "",
         "| λ | max pay farkı | TL para (yeni) | kur_yeni | USD stok, faiz |", "| --- | ---: | ---: | ---: | --- |"]
    for ad, v in pl.items():
        L.append(f"| {ad} | {v['max_fark_pay']:.1e} | {v['tl_para_toplam_yeni']:,.4g} | {v['kur_yeni']:.4g} | ×1, ×1 |")
    L += ["", "Pay farkı sıfır düzeyindedir: λ ne olursa olsun TL bileşenlerin payları aynı kalır. Bu **aritmetik gereğidir**; modelde para yanılsaması ve yuvarlama enflasyonu yoktur. λ ≠ 1 satırları repoda ölçülmedi; yalnız kimliğin λ'dan bağımsız olduğunu göstermek için örnektir.", "",
          "## Yürütme maliyeti (milyar TL, tek sefer)", "",
          f"- **A. Basım + yazılım: {c['A'][0]:.2f} – {c['A'][1]:.2f}.** Banknot basımı ≈ 10 milyon $ (2004 sıfır atma tahmini; 'ek maliyet değil' denmişti) × 49,1274 = {c['basim']:.2f}; yazılım kurum başına 20–100 bin $, kurum sayısı 100–1.000 (varsayım): {c['yazilim'][0]:.2f} – {c['yazilim'][1]:.2f}. Yeni birim paritede bile yeni banknot gerektiği varsayılır.",
          f"- **B. Tam yeni birim, üst referans: {c['B'][0]:.1f} – {c['B'][1]:.1f}.** GSYH 2025 ({c['gsyh']:,.1f} milyar TL, `tavan_akis.csv`) × %0,3–1,0 (Avro bölgesine girenlerde bildirilen aralık, ikincil kaynak).",
          f"- **Pencereye dağılım (A üst ucu):** " + ", ".join(f"{q} {v:.2f}" for q, v in asama(c['A'][1]).items()) + " (Δu ile eşit, varsayım).", "",
          "Fayda sıfır (plasebo), maliyet pozitif. Adım 4 ve 5 maliyetleriyle toplanmaz (bu tek sefer, öteki adımlar akış ve stok).", "",
          "## Ne denmez", "",
          "- 'Yeni birim bir şey değiştirmez' denmez; model değiştirmediğini varsayar, sınamaz.",
          "- 'Geçiş maliyeti ölçüldü' denmez; A, 2004 haber tahmini ve kurum sayısı varsayımı; B ikincil aktarım.",
          "- 'Altı sıfır atıldı' denmez (`ADIM45_BIRIM.md`): λ ölçülmedi, parite 1'dir.",
          "- Yuvarlama, para yanılsaması ve fiyat belirleme alışkanlıkları modellenmedi.", ""]
    (KOK / "ADIM45_MALIYET.md").write_text("\n".join(L), encoding="utf-8")
    print("ADIM45_MALIYET ok")


if __name__ == "__main__":
    main()
