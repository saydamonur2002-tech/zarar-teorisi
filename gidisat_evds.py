"""Gidişat raporu: güncel EVDS verisiyle dış denge, rezerv, faiz yükü ve enflasyon seyri (anahtarsız EVDS3).
Çıktı: gidisat_ham.csv, GIDISAT_RAPORU.md. Model duyarlılığı bölümü gidisat_model_duyarlilik.json'dan gelir (elle koşulmuş, aşağıda yöntem yazılı).
Kullanım: python3 gidisat_evds.py"""
import csv
import json
from pathlib import Path

import evds_cek

HERE = Path(__file__).resolve().parent
BASLA = "01-01-2024"
BITIS = "15-10-2026"
SERILER = {
    "cari_islemler": ("bie_odeayrsunum6", "TP.ODEAYRSUNUM6.Q1", "1"),
    "ihracat": ("bie_odeayrsunum6", "TP.ODEAYRSUNUM6.Q5", "1"),
    "ithalat": ("bie_odeayrsunum6", "TP.ODEAYRSUNUM6.Q6", "1"),
    "yatirim_geliri_net": ("bie_odeayrsunum6", "TP.ODEAYRSUNUM6.Q74", "1"),
    "yatirim_geliri_gider": ("bie_odeayrsunum6", "TP.ODEAYRSUNUM6.Q76", "1"),
    "rezerv_toplam": ("bie_abres2", "TP.AB.TOPLAM", "1"),
    "tufe_endeks": ("bie_oktug2025", "TP.FE25.OKTG01", "1"),
    "butce_gelir": ("bie_kbmgel", "TP.KB.GEL001", "1"),
    "butce_faiz_gider": ("bie_kbmgid", "TP.KB.GID152", "1"),
}


def cek():
    grup = {}
    for ad, (g, kod, fr) in SERILER.items():
        if g not in grup:
            r = evds_cek.fetch_group(g, start=BASLA, end=BITIS, freq=fr)
            grup[g] = r[0] if isinstance(r, tuple) else r
    out = {}
    for ad, (g, kod, fr) in SERILER.items():
        out[ad] = {r[1]: float(r[5]) for r in grup[g] if r[2] == kod and r[5] is not None}
    return out


def roll12(s, m):
    ks = sorted(s)
    i = ks.index(m)
    return sum(s[k] for k in ks[i - 11:i + 1]) if i >= 11 else None


def main():
    S = cek()
    with open(HERE / "gidisat_ham.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["seri", "donem", "deger"])
        for ad, s in S.items():
            for k in sorted(s, key=lambda d: (d[6:], d[3:5], d[:2]) if "-" in d and len(d) == 10 else d):
                w.writerow([ad, k, s[k]])
    ay = sorted(S["cari_islemler"])
    son = ay[-1]
    mon = {
        "cari_12a": {m: roll12(S["cari_islemler"], m) for m in ("2024-12", "2025-06", "2025-12", "2026-06", son)},
        "ihracat_12a": {m: roll12(S["ihracat"], m) for m in ("2025-08", son)},
        "ithalat_12a": {m: roll12(S["ithalat"], m) for m in ("2025-08", son)},
        "yat_net_12a": {m: roll12(S["yatirim_geliri_net"], m) for m in ("2024-12", "2025-08", "2025-12", son)},
        "yat_gider_12a": {m: roll12(S["yatirim_geliri_gider"], m) for m in ("2024-12", son)},
        "faiz_gelir_12a": {m: roll12(S["butce_faiz_gider"], m) / roll12(S["butce_gelir"], m) for m in ("2024-12", "2025-08", "2025-12", son)},
    }
    rz = sorted(S["rezerv_toplam"].items(), key=lambda kv: (kv[0][6:], kv[0][3:5], kv[0][:2]))
    tf = S["tufe_endeks"]
    mon["rezerv"] = {"ilk": rz[0], "zirve_son_6ay": max(rz[-26:], key=lambda kv: kv[1]), "son": rz[-1], "dort_hafta_once": rz[-5]}
    mon["tufe_yoy"] = {son: tf[son] / tf[f"{int(son[:4]) - 1}{son[4:]}"] - 1}
    sens = json.loads((HERE / "gidisat_model_duyarlilik.json").read_text(encoding="utf-8"))
    L = ["# Gidişat raporu (güncel EVDS verisiyle)", "",
         f"Veri: TCMB EVDS3 (anahtarsız), son gözlem: ödemeler dengesi ve bütçe {son}, rezerv {rz[-1][0]}, TÜFE {son}. Ham seriler `gidisat_ham.csv`. 12 aylık kayan toplamlar mn $ (cari ve yatırım geliri) ve oran (faiz/gelir).", "",
         "## 1. Dış denge", "",
         "| 12 aylık | " + " | ".join(mon["cari_12a"]) + " |", "| --- | " + " | ".join("---:" for _ in mon["cari_12a"]) + " |",
         "| Cari işlemler (mrd $) | " + " | ".join(f"{v/1000:.1f}" for v in mon["cari_12a"].values()) + " |", "",
         f"- Mal ihracatı 12a {mon['ihracat_12a']['2025-08']/1000:.1f} → {mon['ihracat_12a'][son]/1000:.1f} mrd $ (%{(mon['ihracat_12a'][son]/mon['ihracat_12a']['2025-08']-1)*100:+.1f}); ithalat {mon['ithalat_12a']['2025-08']/1000:.1f} → {mon['ithalat_12a'][son]/1000:.1f} (%{(mon['ithalat_12a'][son]/mon['ithalat_12a']['2025-08']-1)*100:+.1f}). İthalat ihracattan hızlı büyüyor.",
         f"- Yatırım geliri dengesi (net, 12a): {mon['yat_net_12a']['2024-12']/1000:.1f} → {mon['yat_net_12a'][son]/1000:.1f} mrd $ ({(mon['yat_net_12a'][son]/mon['yat_net_12a']['2024-12']-1)*100:+.0f}%); gider (brüt) {mon['yat_gider_12a']['2024-12']/1000:.1f} → {mon['yat_gider_12a'][son]/1000:.1f} mrd $.", "",
         "## 2. Rezerv", "",
         f"- Toplam rezerv: {rz[0][0]} {rz[0][1]/1000:.1f} mrd $ → son 26 haftanın zirvesi {mon['rezerv']['zirve_son_6ay'][0]} {mon['rezerv']['zirve_son_6ay'][1]/1000:.1f} → son {rz[-1][0]} {rz[-1][1]/1000:.1f} mrd $. Son 4 haftada {(rz[-1][1]-rz[-5][1])/1000:+.1f} mrd $ ({(rz[-1][1]/rz[-5][1]-1)*100:+.1f}%).",
         f"- Rezerv / 12 aylık cari açık: {rz[-1][1]/-mon['cari_12a'][son]:.1f} yıl.", "",
         "## 3. Faiz yükü ve enflasyon", "",
         "- Merkezi yönetim faiz giderleri / gelirleri (12a): " + " → ".join(f"%{v*100:.1f} ({k})" for k, v in mon["faiz_gelir_12a"].items()) + ".",
         f"- TÜFE yıllık ({son}): %{mon['tufe_yoy'][son]*100:.1f}.", "",
         "## 4. Hane ve kredi (kullanıcı verisi ve haber aktarımı; resmî kaynaklardan doğrulanmadı)", "",
         "- Hane borcu / harcanabilir gelir %25 (TCMB Finansal Hesaplar 2026-I), borç/GSYİH %10,1, konut kredisi/GSYİH %1,1.",
         "- BDDK haftalık bülten (2 Ekim 2026, yıllık değişim): takip oranı konut %0,21 (+5 bp), taşıt %1,32 (+72), ihtiyaç %6,33 (+140), tüketici %4,86 (+112), bireysel kart %5,35 (+129), sektör %3,09 (+77).",
         "- Konut kredisi borçlusu (TCMB Risk Merkezi, tekil): 2,5 mn (2020) → 1,7 mn (2025-09); TBB konut bakiyesi 525 → 728 mrd TL (Haz 2025 → Haz 2026), borçlu sayısı %-8. Stres konutta değil, ihtiyaç ve kartta.", "",
         "## 5. Model: güncel çapalarla duyarlılık", "",
         sens["yontem"], "",
         "| Çapa | Zarar tavanı (mn $) | Finans tavanı (mn $) | Finans gerçekleşme | TR net 10y (C) | Skor | Karar |", "| --- | ---: | ---: | ---: | ---: | ---: | --- |"]
    for k in ("baz", "brut", "net"):
        v = sens["sonuclar"][k]
        L.append(f"| {v['ad']} | {v['tavan']['zarar']} | {v['tavan']['finans']} | {v['g']['finans_katman']} | {v['tr_net_10y']} | {v['skor']} | {v['karar']} |")
    L += ["", sens["okuma"], ""]
    (HERE / "GIDISAT_RAPORU.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("GIDISAT_RAPORU ok", son, rz[-1][0])


if __name__ == "__main__":
    main()
