"""Hazine faiz faturası: ölçülmüş stok ve kupon, 2025'e kalibre, 2026 ilk yarıda sınanır.

Soru: özel sektör dış borç akışı durursa 2026 faiz ödeneği (2.742 milyar TL) sabit kalır mı?

Kimlik (yıl):
  iç faiz   = r_ic  * iç borç stoku ortalaması
  dış faiz  = r_dis * (kamu brüt dış borç USD * çeyrek ortalaması USD/TRY)
  diğer     = r_diger * iç borç stoku ortalaması
            (kira sertifikası + iskonto + türev)
  fatura    = iç + dış + diğer

r, 2025 gerçekleşmesinden çözülür (kimlik). Sınav: aynı r, 2024 stokuna ve 2026 ilk yarısına uygulanır.
Aktarımın durması, özel sektör USD akışını sıfırlar. İç stok, kamu USD stoku ve kur kendi ölçülmüş eğiminde kalır.
Beş adımın faiz ve kur etkisi bu dosyada da modellenmedi diye durur; burası bütçe faturasının stok hesabıdır.

Çalıştır: python3 faiz_fatura_kalibre.py
Çıktı: faiz_fatura_ic_stok.csv, faiz_fatura_panel.csv, faiz_fatura_kalibre.json, FAIZ_FATURA_KALIBRE.md
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

KOK = Path(__file__).resolve().parent
PENCERE = ("2024-Q4", "2026-Q2")  # bugünkü tempo
UZUN = ("2023-Q4", "2026-Q2")
O_DENEK_2026 = 2741.656  # SBB, milyar TL, ödenek
SBB_2025 = 2054.382  # SBB, 2025 faiz gerçekleşmesi, milyar TL


def _q_from_month(donem: str) -> str | None:
    y, m = donem.split("-")
    mi = int(m)
    if mi % 3:
        return None
    return f"{y}-Q{mi // 3}"


def _fetch_ic_stok() -> pd.Series:
    """TP.KB.A09 toplam iç borç stoku, çeyrek sonu, milyar TL. EVDS bin TL."""
    import json as _json
    import urllib.request

    body = {
        "type": "json", "series": "TP.KB.A09", "aggregationTypes": "last", "formulas": "0",
        "startDate": "01-01-2016", "endDate": "01-10-2026", "frequency": "1",
        "decimalSeperator": ".", "decimal": "2", "dateFormat": "0", "lang": "TR",
        "yon": "0", "sira": "0", "ozelFormuller": [], "groupSeperator": True, "isRaporSayfasi": False,
    }
    req = urllib.request.Request(
        "https://evds3.tcmb.gov.tr/igmevdsms-dis/fe",
        data=_json.dumps(body).encode(),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        method="POST",
    )
    raw = urllib.request.urlopen(req, timeout=120).read().decode("utf-8-sig")
    items = _json.loads(raw)["items"]
    rows = []
    for it in items:
        tarih = str(it["Tarih"])
        y, m = tarih.split("-")[:2]
        val = float(str(it["TP_KB_A09"]).replace(",", "")) / 1e6  # bin TL -> milyar TL
        rows.append({"Donem": f"{y}-{m}", "ic_stok_milyar_tl": round(val, 3)})
    pd.DataFrame(rows).to_csv(KOK / "faiz_fatura_ic_stok.csv", index=False)
    return _ic_from_csv()


def _ic_from_csv() -> pd.Series:
    d = pd.read_csv(KOK / "faiz_fatura_ic_stok.csv", dtype={"Donem": str})
    d["Q"] = d.Donem.map(_q_from_month)
    q = d.dropna(subset=["Q"]).set_index("Q")["ic_stok_milyar_tl"]
    return q.sort_index()


def _butce() -> pd.DataFrame:
    b = pd.read_csv(KOK / "butce_ham.csv", dtype={"Donem": str})
    kod = {
        "TP.KB.GID152": "toplam",
        "TP.KB.GID153": "ic",
        "TP.KB.GID160": "dis",
        "TP.KB.GID161": "iskonto",
        "TP.KB.GID162": "turev",
        "TP.KB.GID163": "kira",
    }
    s = b[b.Seri.isin(kod)].copy()
    s["kalem"] = s.Seri.map(kod)
    s["yil"], s["ay"] = s.Donem.str.slice(0, 4), s.Donem.str.slice(5, 7).astype(int)
    s["Q"] = s.yil + "-Q" + ((s.ay - 1) // 3 + 1).astype(str)
    n = s.groupby(["Q", "kalem"]).Donem.nunique()
    tam = n[n == 3].index
    q = s.groupby(["Q", "kalem"]).Deger.sum() / 1e6  # bin TL -> milyar TL
    q = q[q.index.isin(tam)].unstack("kalem").sort_index()
    q["diger"] = q[["iskonto", "turev", "kira"]].sum(axis=1)
    return q


def _dis_usd() -> pd.DataFrame:
    d = pd.read_csv(KOK / "dis_borc_ham.csv", dtype={"Donem": str})
    kod = {
        "TP.BRUTDBORCLU.G1": "toplam",
        "TP.BRUTDBORCLU.G2": "kamu",
        "TP.BRUTDBORCLU.G13": "tcmb",
        "TP.BRUTDBORCLU.G14": "ozel",
    }
    s = d[d.Seri.isin(kod)].copy()
    s["ad"] = s.Seri.map(kod)
    p = s.pivot_table(index="Donem", columns="ad", values="Deger", aggfunc="last") / 1000.0
    return p.sort_index()


def _kur() -> pd.Series:
    g = pd.read_csv(KOK / "gecis_payi_ham.csv", dtype={"donem": str})
    s = g[g.seri == "TP.DK.USD.A.YTL"].set_index("donem").deger
    # 2026-Q3 çeyreği dosyada yarım; kalibrasyona girmez
    return s[s.index <= "2026-Q2"].astype(float).sort_index()


def _egim(seri: pd.Series, a: str, b: str) -> float:
    i0, i1 = seri.index.get_loc(a), seri.index.get_loc(b)
    return float(seri.iloc[i1] - seri.iloc[i0]) / (i1 - i0)


def _kur_carpan(kur: pd.Series, a: str, b: str) -> float:
    i0, i1 = kur.index.get_loc(a), kur.index.get_loc(b)
    return float((kur.iloc[i1] / kur.iloc[i0]) ** (1 / (i1 - i0)) - 1)


def _yil(panel: pd.DataFrame, y: int) -> pd.DataFrame:
    return panel.loc[f"{y}-Q1":f"{y}-Q4"]


def _r(yil: pd.DataFrame) -> dict:
    s_ic = float(yil.ic_stok.mean())
    s_dis_tl = float((yil.kamu_usd * yil.kur).mean())
    return {
        "r_ic": float(yil.ic.sum()) / s_ic,
        "r_dis": float(yil.dis.sum()) / s_dis_tl,
        "r_diger": float(yil.diger.sum()) / s_ic,
        "ic_stok_ort": s_ic,
        "kamu_tl_ort": s_dis_tl,
    }


def _fatura(r: dict, ic_ort: float, kamu_tl_ort: float) -> dict:
    ic = r["r_ic"] * ic_ort
    dis = r["r_dis"] * kamu_tl_ort
    diger = r["r_diger"] * ic_ort
    return {"ic": ic, "dis": dis, "diger": diger, "toplam": ic + dis + diger}


def _ileri(panel: pd.DataFrame, egim: dict, kur_g: float, ozel_dur: bool, kamu_dur: bool, kur_dur: bool, ic_dur: bool, n: int) -> pd.DataFrame:
    son = panel.loc["2026-Q2"]
    rows = []
    ic, kamu, tcmb, ozel, kur = float(son.ic_stok), float(son.kamu_usd), float(son.tcmb_usd), float(son.ozel_usd), float(son.kur)
    y0, q0 = 2026, 2
    for k in range(1, n + 1):
        q0 += 1
        if q0 == 5:
            q0, y0 = 1, y0 + 1
        ic = ic if ic_dur else ic + egim["ic"]
        kamu = kamu if kamu_dur else kamu + egim["kamu"]
        tcmb = tcmb + egim["tcmb"]
        ozel = ozel if ozel_dur else ozel + egim["ozel"]
        kur = kur if kur_dur else kur * (1 + kur_g)
        rows.append({
            "Donem": f"{y0}-Q{q0}", "ic_stok": ic, "kamu_usd": kamu, "tcmb_usd": tcmb,
            "ozel_usd": ozel, "toplam_usd": kamu + tcmb + ozel, "kur": kur,
        })
    return pd.DataFrame(rows).set_index("Donem")


def _yil_ort(olculen: pd.DataFrame, ileri: pd.DataFrame, y: int) -> tuple[float, float]:
    parca = []
    for q in range(1, 5):
        k = f"{y}-Q{q}"
        if k in olculen.index:
            parca.append(olculen.loc[k])
        else:
            parca.append(ileri.loc[k])
    df = pd.DataFrame(parca)
    return float(df.ic_stok.mean()), float((df.kamu_usd * df.kur).mean())


def _md(s: dict) -> str:
    r = s["r_2025"]
    sinav = s["sinav"]
    m = s["mevcut_2027"]
    a = s["aktarim_2027"]
    d = s["donuk_kur_kamu_2027"]
    z = s["hepsi_sabit_2027"]
    o26 = s["mevcut_2026"]
    return "\n".join([
        "# Faiz faturası kalibrasyonu",
        "",
        "Soru: özel dış borç akışı durursa 2026 faiz ödeneği sabit kalır mı?",
        "",
        "Kimlik: iç faiz = r_ic × iç stok. Dış faiz = r_dis × (kamu brüt dış borç USD × kur). Diğer = r_diger × iç stok. r, 2025 yılından çözülür.",
        "",
        "## Kalibrasyon",
        "",
        f"- İç stok 2026-06: **{s['ic_2026_06']:.1f} milyar TL** (`TP.KB.A09`, çeyrek sonu). SBB Haziran iç stok 9.010,5. Fark {s['ic_fark_sbb']:.1f}.",
        f"- 2025 EVDS faiz toplamı **{s['faiz_2025_evds']:.1f} milyar TL**. SBB gerçekleşmesi {SBB_2025:.1f}. Fark {s['faiz_2025_evds'] - SBB_2025:.1f}.",
        f"- 2025 kuponu: iç **%{r['r_ic']*100:.2f}**, dış **%{r['r_dis']*100:.2f}** (kamu USD × kur üzerinden), diğer **%{r['r_diger']*100:.2f}**.",
        f"- 2024 kuponu 2025 stokuna uygulanınca fatura **{sinav['tahmin_2025_r2024']:.0f}** çıkar. Ölçülen {s['faiz_2025_evds']:.0f}. Sapma **{sinav['sapma_2025_yuzde']:.1f}%**. İç kupon %{s['r_2024']['r_ic']*100:.1f}'ten %{r['r_ic']*100:.1f}'e çıkmış, dış ve diğer kupon gerilemiş, toplam kapanmıştır.",
        f"- 2026 ilk yarı ölçüm **{sinav['h1_2026']:.0f}**. Düz yarıyıl kuponu **{sinav['h1_2026_tahmin']:.0f}** verir. Sapma **{sinav['h1_sapma_yuzde']:.1f}%**. 2025'te ilk yarı yılın %{sinav['h1_pay_2025']*100:.0f}'ünü taşımıştı. Yıl toplamı bu mevsimle ayrı tutulur.",
        "",
        "## Eğim, 2024-Q4 → 2026-Q2",
        "",
        f"- İç stok **{s['egim']['ic']:+.1f} milyar TL/çeyrek**.",
        f"- Kamu brüt dış borç **{s['egim']['kamu']:+.2f} milyar USD/çeyrek**. Özel **{s['egim']['ozel']:+.2f}**. TCMB **{s['egim']['tcmb']:+.2f}**.",
        f"- Kur çarpanı **çeyrek başına %{s['kur_g']*100:.2f}** (çeyrek ortalaması USD/TRY).",
        f"- Uzun pencere 2023-Q4 → 2026-Q2 özel eğim {s['egim_uzun']['ozel']:+.2f} milyar USD/çeyrek. İleri hesap son tempoyu kullanır.",
        "",
        "## 2027 faturası, milyar TL",
        "",
        "| Yol | İç | Dış | Diğer | Toplam | 2026 ödeneğine fark |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
        f"| Mevcut tempo | {m['ic']:.0f} | {m['dis']:.0f} | {m['diger']:.0f} | **{m['toplam']:.0f}** | {m['toplam']-O_DENEK_2026:+.0f} |",
        f"| Aktarım durdu (özel USD akışı 0) | {a['ic']:.0f} | {a['dis']:.0f} | {a['diger']:.0f} | **{a['toplam']:.0f}** | {a['toplam']-O_DENEK_2026:+.0f} |",
        f"| Kamu USD ve kur donuk, iç stok yürür | {d['ic']:.0f} | {d['dis']:.0f} | {d['diger']:.0f} | **{d['toplam']:.0f}** | {d['toplam']-O_DENEK_2026:+.0f} |",
        f"| İç stok, kamu USD ve kur donuk | {z['ic']:.0f} | {z['dis']:.0f} | {z['diger']:.0f} | **{z['toplam']:.0f}** | {z['toplam']-O_DENEK_2026:+.0f} |",
        "",
        f"2026 modeli, mevcut tempoda **{o26['toplam']:.0f}**. Ödenek {O_DENEK_2026:.0f}. Mevsimle şişirilmiş ilk yarı (2025 payı) **{sinav['olcek_2026']:.0f}**.",
        "",
        f"Aktarımın durması ile mevcut tempo arasındaki fark **{a['toplam']-m['toplam']:+.1f} milyar TL**. Özel USD stoku faturaya girmez. Faturaya giren dış stok kamu brüt dış borcudur.",
        "",
        f"Donuk Haziran 2026 stokundan 2027 mevcut yola fark **{m['toplam']-z['toplam']:+.0f}**. Tek tek açılınca iç stok **{s['katki']['ic']:+.0f}**, kur **{s['katki']['kur']:+.0f}**, kamu USD **{s['katki']['kamu']:+.0f}**. Üçü birlikte {s['katki']['ic']+s['katki']['kur']+s['katki']['kamu']:+.0f} eder. Kalan, üçünün aynı anda yürümesindendir.",
        "",
        "## Ne denmez",
        "",
        "- İlk yarı sapması yıl sapmasıdır denmez. 2026 model yılı ödeneğin üstündedir, fark 2 milyar TL mertebesindedir.",
        "- Özel dış borç durunca Hazine faizi sabitlenir denmez. İki yolun toplamı aynıdır.",
        "- Beş adım kuru veya politika faizini indirdi denmez. Kur eğimi ölçülmüş çeyrek ortalamasıdır. Faiz model etkisi `modellenmedi`.",
        "- Kamu brüt dış borç = merkezi yönetim dış borcu (Haziran 2026: 128,2 milyar USD) denmez. Bütçe dış faizi, kamu stokunun üstünden kalibre edildi.",
        "",
    ])


def main() -> None:
    ic = _ic_from_csv() if (KOK / "faiz_fatura_ic_stok.csv").exists() else _fetch_ic_stok()
    butce = _butce()
    dis = _dis_usd()
    kur = _kur()
    idx = butce.index.intersection(ic.index).intersection(dis.index).intersection(kur.index)
    idx = idx[(idx >= "2018-Q1") & (idx <= "2026-Q2")]
    panel = pd.DataFrame({
        "ic_stok": ic.reindex(idx),
        "kamu_usd": dis.kamu.reindex(idx),
        "tcmb_usd": dis.tcmb.reindex(idx),
        "ozel_usd": dis.ozel.reindex(idx),
        "toplam_usd": dis.toplam.reindex(idx),
        "kur": kur.reindex(idx),
        "ic": butce.ic.reindex(idx),
        "dis": butce.dis.reindex(idx),
        "diger": butce.diger.reindex(idx),
        "toplam": butce.toplam.reindex(idx),
    })
    panel.to_csv(KOK / "faiz_fatura_panel.csv", float_format="%.4f")

    r25 = _r(_yil(panel, 2025))
    r24 = _r(_yil(panel, 2024))
    y25 = _yil(panel, 2025)
    tahmin_2025 = _fatura(r24, float(y25.ic_stok.mean()), float((y25.kamu_usd * y25.kur).mean()))
    faiz_2025 = float(y25.toplam.sum())
    h1_2025 = float(panel.loc["2025-Q1":"2025-Q2"].toplam.sum())
    h1_2026 = float(panel.loc["2026-Q1":"2026-Q2"].toplam.sum())
    h1_tahmin = _fatura(
        r25,
        float(panel.loc["2026-Q1":"2026-Q2"].ic_stok.mean()),
        float((panel.loc["2026-Q1":"2026-Q2"].kamu_usd * panel.loc["2026-Q1":"2026-Q2"].kur).mean()),
    )["toplam"] / 2.0

    egim = {
        "ic": _egim(panel.ic_stok, *PENCERE),
        "kamu": _egim(panel.kamu_usd, *PENCERE),
        "ozel": _egim(panel.ozel_usd, *PENCERE),
        "tcmb": _egim(panel.tcmb_usd, *PENCERE),
    }
    egim_uzun = {
        "ic": _egim(panel.ic_stok, *UZUN),
        "kamu": _egim(panel.kamu_usd, *UZUN),
        "ozel": _egim(panel.ozel_usd, *UZUN),
        "tcmb": _egim(panel.tcmb_usd, *UZUN),
    }
    kur_g = _kur_carpan(panel.kur, *PENCERE)

    yollar = {
        "mevcut": dict(ozel_dur=False, kamu_dur=False, kur_dur=False, ic_dur=False),
        "aktarim": dict(ozel_dur=True, kamu_dur=False, kur_dur=False, ic_dur=False),
        "donuk_kur_kamu": dict(ozel_dur=True, kamu_dur=True, kur_dur=True, ic_dur=False),
        "hepsi_sabit": dict(ozel_dur=True, kamu_dur=True, kur_dur=True, ic_dur=True),
    }
    ileri = {ad: _ileri(panel, egim, kur_g, n=6, **k) for ad, k in yollar.items()}
    fat = {}
    for ad, yol in ileri.items():
        ic26, tl26 = _yil_ort(panel, yol, 2026)
        ic27, tl27 = _yil_ort(panel, yol, 2027)
        fat[ad] = {"2026": _fatura(r25, ic26, tl26), "2027": _fatura(r25, ic27, tl27),
                   "ozel_2027q4": float(yol.loc["2027-Q4"].ozel_usd),
                   "toplam_usd_2027q4": float(yol.loc["2027-Q4"].toplam_usd)}

    # katkı: tek tek dondur, 2027 mevcut eksi o yol
    sadece_ic = _ileri(panel, egim, kur_g, n=6, ozel_dur=False, kamu_dur=True, kur_dur=True, ic_dur=False)
    sadece_kur = _ileri(panel, egim, kur_g, n=6, ozel_dur=False, kamu_dur=True, kur_dur=False, ic_dur=True)
    sadece_kamu = _ileri(panel, egim, kur_g, n=6, ozel_dur=False, kamu_dur=False, kur_dur=True, ic_dur=True)
    baz = _fatura(r25, *_yil_ort(panel, ileri["hepsi_sabit"], 2027))["toplam"]
    katki = {
        "ic": _fatura(r25, *_yil_ort(panel, sadece_ic, 2027))["toplam"] - baz,
        "kur": _fatura(r25, *_yil_ort(panel, sadece_kur, 2027))["toplam"] - baz,
        "kamu": _fatura(r25, *_yil_ort(panel, sadece_kamu, 2027))["toplam"] - baz,
    }

    ic_haz = float(panel.loc["2026-Q2"].ic_stok)
    out = {
        "ic_2026_06": ic_haz,
        "ic_fark_sbb": ic_haz - 9010.5,
        "faiz_2025_evds": faiz_2025,
        "r_2025": r25,
        "r_2024": r24,
        "egim": egim,
        "egim_uzun": egim_uzun,
        "kur_g": kur_g,
        "sinav": {
            "tahmin_2025_r2024": tahmin_2025["toplam"],
            "sapma_2025_yuzde": 100 * (tahmin_2025["toplam"] / faiz_2025 - 1),
            "h1_2026": h1_2026,
            "h1_2026_tahmin": h1_tahmin,
            "h1_sapma_yuzde": 100 * (h1_tahmin / h1_2026 - 1),
            "h1_pay_2025": h1_2025 / faiz_2025,
            "olcek_2026": h1_2026 / (h1_2025 / faiz_2025),
        },
        "mevcut_2026": fat["mevcut"]["2026"],
        "mevcut_2027": fat["mevcut"]["2027"],
        "aktarim_2027": fat["aktarim"]["2027"],
        "donuk_kur_kamu_2027": fat["donuk_kur_kamu"]["2027"],
        "hepsi_sabit_2027": fat["hepsi_sabit"]["2027"],
        "katki": katki,
        "usd_2027q4": {ad: {"ozel": v["ozel_2027q4"], "toplam": v["toplam_usd_2027q4"]} for ad, v in fat.items()},
        "etiket": {
            "r": "kalibrasyon_2025_kimlik",
            "egim": "olculdu_2024Q4_2026Q2",
            "aktarim": "varsayim_ozel_usd_akisi_sifir",
            "faiz_model_etkisi": "modellenmedi",
        },
    }
    (KOK / "faiz_fatura_kalibre.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    (KOK / "FAIZ_FATURA_KALIBRE.md").write_text(_md(out), encoding="utf-8")
    print(json.dumps({
        "faiz_2025": round(faiz_2025, 1),
        "sapma_2025_r2024_%": round(out["sinav"]["sapma_2025_yuzde"], 2),
        "h1_2026": round(h1_2026, 1),
        "h1_tahmin": round(h1_tahmin, 1),
        "h1_sapma_%": round(out["sinav"]["h1_sapma_yuzde"], 2),
        "2026_model": round(fat["mevcut"]["2026"]["toplam"], 1),
        "2027_mevcut": round(fat["mevcut"]["2027"]["toplam"], 1),
        "2027_aktarim": round(fat["aktarim"]["2027"]["toplam"], 1),
        "fark_aktarim": round(fat["aktarim"]["2027"]["toplam"] - fat["mevcut"]["2027"]["toplam"], 2),
        "2027_kur_kamu_donuk": round(fat["donuk_kur_kamu"]["2027"]["toplam"], 1),
        "2027_hepsi_sabit": round(fat["hepsi_sabit"]["2027"]["toplam"], 1),
        "katki": {k: round(v, 1) for k, v in katki.items()},
        "r_ic_%": round(r25["r_ic"] * 100, 2),
        "r_dis_%": round(r25["r_dis"] * 100, 2),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
