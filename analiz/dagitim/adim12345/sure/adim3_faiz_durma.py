"""Faz 3 — Adım 3: faiz tahakkukunun durması kuralı, SFC transfer olarak.

`adim3.csv` yazılmaz (orada "Faizin durması modellenmedi" durur; H-A3 kilidi dokunulmaz). Kural burada ayrı dosyada:

  Durdurulan stok  D_t = κ · u2_t · S₀
      S₀   = firma F.4 kredi yükümlülüğü 2026-Q1 (tek_sistem_kopru.csv, `olculdu`)              → ölçüm
      u2_t = K2 stok penceresi uygulama oranı (tek_sistem_kademe.py, 2028-Q1..Q4 doğrusal)     → kademe kurgusu
      κ    = tek sisteme giren ve faizi duran pay ∈ {0,25; 0,5; 1,0}                          → varsayım
  Duran faiz (çeyrek)  I_t = ψ · (r_t / 4) · D_t
      r_t  = TP.KTF17 ticari kredi faizi (TL, akım, %); gözlem 2026-09'a kadar, sonrası son değer sabit → ölçüm + varsayım
      ψ    = etkin faiz payı 2024 = finansman gideri 2024 / (r̄₂₀₂₄ · S̄₂₀₂₄); kapsam ve döviz karışımı → ölçüm türevi
  SFC: F NL_t += I_t ; B′ NL_t −= I_t ; ΣNL değişmez (transfer). Alternatif: B′ yerine K′ üstlenir (ayrı sütun).
  Kontrol: yıllık ΣI_t / finansman gideri 2024 oranı raporlanır; eşitlenmez (dönem ve kapsam farklı).

Çıktı: adim3_faiz_durma.csv (çeyrek × κ), adim3_faiz_durma_sonuc.json, ADIM3_FAIZ_DURMA.md.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import tek_sistem_kademe as tk

KOK = Path(__file__).resolve().parent
KAPPA = (0.25, 0.5, 1.0)
FAIZ_SERI = "TP.KTF17"
REF_YIL = 2024


def _csv(ad: str) -> list[dict]:
    return list(csv.DictReader((KOK / ad).open(encoding="utf-8-sig")))


def faiz_aylik() -> dict[str, float]:
    return {r["Donem"]: float(r["Deger"]) for r in _csv("faiz_ham.csv") if r["Seri"] == FAIZ_SERI and r["Deger"] not in ("", "nan")}


def faiz_ceyrek(aylik: dict[str, float]) -> dict[str, float]:
    gr: dict[str, list[float]] = {}
    for d, v in aylik.items():
        y, m = d.split("-")
        gr.setdefault(f"{y}-Q{(int(m) - 1) // 3 + 1}", []).append(v)
    return {k: sum(v) / len(v) for k, v in gr.items()}


def f4_stok() -> dict[str, float]:
    return {r["donem"]: float(r["milyar_tl"]) for r in _csv("tavan_akis_ham.csv") if r["seri"] == "TP.FINHESTNKS11.ZP34"}


def psi_etkin(fq: dict[str, float], stok: dict[str, float]) -> dict:
    kop = _csv("tek_sistem_kopru.csv")
    fg = float(next(r for r in kop if r["blok"] == "referans" and r["donem"] == str(REF_YIL) and r["kalem"] == "firma finansman gideri")["evds_milyar"])
    r_bar = sum(fq[f"{REF_YIL}-Q{q}"] for q in range(1, 5)) / 4 / 100
    s_bar = sum(stok[f"{REF_YIL}-Q{q}"] for q in range(1, 5)) / 4
    return {"finansman_gideri_2024": fg, "r_bar_2024": round(r_bar, 4), "s_bar_2024": round(s_bar, 1), "nominal_faiz_2024": round(r_bar * s_bar, 1),
            "psi": round(fg / (r_bar * s_bar), 4), "durum": "olcum_turevi",
            "not": "Sektör Bilançoları kapsamı (bilanço veren firmalar) ve döviz kredisi karışımı; EVDS F.4 tüm firmalar. Oran, eşitlik değil."}


def main() -> dict:
    aylik = faiz_aylik()
    fq = faiz_ceyrek(aylik)
    son_ay = max(aylik)
    r_son = aylik[son_ay]
    stok = f4_stok()
    s0 = tk.F4_STOK_BAS_MILYAR
    assert abs(stok["2026-Q1"] - s0) < 0.1
    psi = psi_etkin(fq, stok)
    k2 = next(p for p in tk.PENCERELER if p.kod == "K2_stok")
    donemler = tk._iter_donem(tk.DONEM_BAS, tk.DONEM_SON)

    satirlar, yillik = [], {}
    for kap in KAPPA:
        for d in donemler:
            r_t, r_kaynak = (fq[d], "olcum") if d in fq and len([m for m in aylik if m.startswith(d[:4]) and (int(m[5:]) - 1) // 3 + 1 == int(d[-1])]) == 3 else (r_son, f"sabit {son_ay}")
            u2 = tk.uygulama_orani(d, k2)
            D = kap * u2 * s0
            I_nom = r_t / 100 / 4 * D
            I_etk = psi["psi"] * I_nom
            satirlar.append({"donem": d, "kappa": kap, "u2_K2": round(u2, 4), "durdurulan_stok_milyar": round(D, 1), "r_yillik_yuzde": round(r_t, 3),
                             "r_kaynak": r_kaynak, "psi": psi["psi"], "duran_faiz_nominal_milyar": round(I_nom, 1), "duran_faiz_etkin_milyar": round(I_etk, 1),
                             "F_NL_etkisi": round(I_etk, 1), "Bp_NL_etkisi_odeyen_B": round(-I_etk, 1), "Kp_NL_etkisi_odeyen_K": round(-I_etk, 1),
                             "toplam_NL_etkisi": 0.0, "durum": "modellendi_varsayim_kappa",
                             "not": "F.4 stoku nominal sabit (büyüme yok); ödeyen tek hazne (B′ ya da K′), ikisi toplanmaz."})
            yillik.setdefault(kap, {}).setdefault(d[:4], 0.0)
            yillik[kap][d[:4]] += I_etk
    alan = list(satirlar[0].keys())
    with (KOK / "adim3_faiz_durma.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=alan); w.writeheader(); w.writerows(satirlar)

    tam_yil = {kap: {y: round(v, 1) for y, v in yl.items() if y not in ("2026",)} for kap, yl in yillik.items()}
    oran_2024 = {kap: {y: round(v / psi["finansman_gideri_2024"], 3) for y, v in yl.items()} for kap, yl in tam_yil.items()}
    sonuc = {"faz": 3, "adim": 3, "adim3_csv": "yazilmadi (H-A3 kilidi durur; 'modellenmedi' metni orada kalır, kural burada)",
             "kural": "D_t = κ·u2_t·S₀; I_t = ψ·(r_t/4)·D_t; F NL += I_t, ödeyen hazne NL −= I_t; ΣNL = 0",
             "S0_milyar": s0, "S0_kaynak": "tek_sistem_kopru.csv 2026-Q1 F_F4_yuk (olculdu)", "faiz_seri": FAIZ_SERI, "faiz_son": {son_ay: r_son},
             "psi": psi, "kappa": list(KAPPA), "K2_pencere": [k2.baslangic, k2.bitis], "donem": [tk.DONEM_BAS, tk.DONEM_SON],
             "yillik_duran_faiz_etkin_milyar": tam_yil, "yillik_bolu_finansman_gideri_2024": oran_2024,
             "etiketler": {"S0": "olcum", "r_t": "olcum (2026-09'a kadar) + sabit varsayım", "psi": "olcum_turevi", "kappa": "varsayim", "u2": "kademe kurgusu"}}
    (KOK / "adim3_faiz_durma_sonuc.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    f = lambda x, n=1: "" if x is None else f"{x:,.{n}f}"
    yillar = sorted({y for yl in tam_yil.values() for y in yl})
    md = ["# Faz 3 — Adım 3: faiz tahakkukunun durması kuralı (SFC transfer)", "",
          "Çalıştır: `python3 adim3_faiz_durma.py`. Çıktı: `adim3_faiz_durma.csv`, `adim3_faiz_durma_sonuc.json`.", "",
          "`adim3.csv` yazılmaz; oradaki 'Faizin durması modellenmedi' ve H-A3 kilidi durur. Kural burada, ayrı dosyada.", "",
          "## Kural", "", f"- `{sonuc['kural']}`",
          f"- S₀ = {f(s0)} milyar (F F.4, 2026-Q1, `olculdu`). r_t = {FAIZ_SERI} ticari kredi faizi; son gözlem {son_ay}: {r_son:.2f}%; sonrası sabit (varsayım).",
          f"- ψ = {psi['finansman_gideri_2024']:,.1f} / ({psi['r_bar_2024']:.4f} × {f(psi['s_bar_2024'])}) = **{psi['psi']:.4f}** (`{psi['durum']}`). {psi['not']}",
          f"- κ ∈ {list(KAPPA)} varsayım; u2 K2 penceresi {k2.baslangic}..{k2.bitis} doğrusal (tek_sistem_kademe.py).",
          "- SFC: F'nin ödemediği faiz B′'nin almadığı faizdir; ΣNL değişmez. B′ yerine K′ üstlenirse sütun değişir, toplam değişmez. İkisi toplanmaz.", "",
          "## Yıllık duran faiz (etkin, milyar TL) ve 2024 finansman giderine oranı", "",
          "| κ | " + " | ".join(yillar) + " |", "| --- | " + " | ".join("---" for _ in yillar) + " |"]
    for kap in KAPPA:
        md.append(f"| {kap} | " + " | ".join(f"{f(tam_yil[kap].get(y))} ({oran_2024[kap].get(y, 0):.2f}×)" for y in yillar) + " |")
    md += ["", "## Ne denmez", "",
           "- 'Faiz durdu, firma rahatladı' denmez; κ varsayım, r_t ileri sabit, ψ 2024 kapsamından.",
           "- Yıllık duran faiz 2024 finansman giderine eşitlenmez; oran karşılaştırma içindir.",
           "- Bu sayılar `adim3.csv`'ye, `uc_kural_senaryo.csv`'ye taşınmaz.", ""]
    (KOK / "ADIM3_FAIZ_DURMA.md").write_text("\n".join(md), encoding="utf-8")
    print(f"S0 {s0:,.1f} | r_son {son_ay} {r_son:.2f}% | ψ {psi['psi']:.4f} | yıllık etkin duran faiz κ=1: {tam_yil[1.0]}")
    return sonuc


if __name__ == "__main__":
    main()
