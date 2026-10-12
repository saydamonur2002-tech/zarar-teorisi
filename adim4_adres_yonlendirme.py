"""Faz 4 — Adım 4: adres stoklarını ihraç / prim / çıkış ile bağlama (band; kilit dışı).

`adim4.csv` senet satırı `modellenmedi` ve `senet_kilit.txt` dokunulmaz; bu dosya o satırı doldurmaz. Burada üç adres stoku
(`olculdu`) üzerinde yönlendirme payı θ ile bir kâğıt (hedef primli endeksli) için SFC muhasebesi kurulur; her sayı band.

  Adresler A_j (adim4.csv, 2026-Q1, milyar TL): hane TL vadeli (H), firma vadeli (F), gerçek kişi YP (H, TL karşılığı).
  İhraç_t   = θ · ΣA_j · (u3_t − u3_{t−1})         θ ∈ {0,10; 0,25; 0,50} varsayım; u3 K3 penceresi (tek_sistem_kademe)
  Stok_t    = Stok_{t−1} + İhraç_t − Çıkış_t
  Çıkış_t   = (1 − χ) · İhraç_{t−V}                 V = 8 çeyrek vade varsayım; χ ∈ {0; 0,5} yenileme payı varsayım
  Prim_t    = π · Stok_{t−1} / 4                    π ∈ {0,02; 0,05} varsayım; endeks (hedef) bacağı: hedef patikası depoda yok → hesaplanmadı
  SFC (çeyrek): tutucu VF.2 −İhraç, VF.3 +İhraç (NFP 0); B′ F.2 −İhraç, rezerv −İhraç (0); K′ F.3 +İhraç, TCMB hesabı +İhraç (0);
                prim: K′ NL −Prim, tutucu NL +Prim (ΣNL 0). Çıkış ters yönde.
  Kredi itişi: B′ mevduat kaybı × K3_MEVDUAT_KREDI_PAYI (0,08; tek_sistem_kademe sabiti) yıllık kredi daralması.
  Karşılaştırma: Prim yıllık / Faz 3 duran faiz (κ=0,5) aynı yıl; oran, eşitlik değil.

Çıktı: adim4_adres_yonlendirme.csv, adim4_adres_yonlendirme_sonuc.json, ADIM4_ADRES_YONLENDIRME.md.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import tek_sistem_kademe as tk

KOK = Path(__file__).resolve().parent
THETA = (0.10, 0.25, 0.50)
CHI = (0.0, 0.5)
PI = (0.02, 0.05)
VADE_CEYREK = 8
IHRACCI = "K′"


def _csv(ad: str) -> list[dict]:
    return list(csv.DictReader((KOK / ad).open(encoding="utf-8-sig")))


def adresler() -> list[dict]:
    out = []
    for r in _csv("adim4.csv"):
        if r["durum"] != "olculdu":
            continue
        hazne = "F" if r["nesne"].startswith("firma") else "H"
        out.append({"nesne": r["nesne"], "hazne": hazne, "milyar": float(r["deger"]), "donem": r["donem"], "durum": "olcum",
                    "not": "TL karşılığı; kur riski kâğıda taşınır mı, karar yok" if "YP" in r["nesne"] else ""})
    return out


def kagit_patikasi(toplam: float, theta: float, chi: float, pi: float, donemler: list[str], k3) -> list[dict]:
    u_once, stok, ihraclar, satirlar = 0.0, 0.0, [], []
    for i, d in enumerate(donemler):
        u3 = tk.uygulama_orani(d, k3)
        ihrac = theta * toplam * (u3 - u_once)
        u_once = u3
        cikis = (1 - chi) * ihraclar[i - VADE_CEYREK] if i >= VADE_CEYREK else 0.0
        prim = pi * stok / 4
        ihraclar.append(ihrac)
        stok = stok + ihrac - cikis
        net_ihrac = ihrac - cikis
        satirlar.append({"donem": d, "theta": theta, "chi": chi, "pi": pi, "u3_K3": round(u3, 4), "ihrac": round(ihrac, 1), "cikis": round(cikis, 1),
                         "stok": round(stok, 1), "prim_ceyrek": round(prim, 1),
                         "tutucu_VF2_mevduat": round(-net_ihrac, 1), "tutucu_VF3_kagit": round(net_ihrac, 1), "tutucu_NFP": 0.0,
                         "Bp_F2_mevduat": round(-net_ihrac, 1), "Bp_rezerv": round(-net_ihrac, 1), "Bp_NFP": 0.0,
                         "Kp_F3_kagit": round(net_ihrac, 1), "Kp_TCMB_hesabi": round(net_ihrac, 1), "Kp_NFP": 0.0,
                         "Kp_NL_prim": round(-prim, 1), "tutucu_NL_prim": round(prim, 1), "toplam_NL": 0.0,
                         "kredi_itki_azalt_yillik": round(stok * tk.K3_MEVDUAT_KREDI_PAYI, 1),
                         "endeks_bacagi": "hesaplanmadi (hedef patikasi depoda yok)", "ihracci": IHRACCI, "durum": "band_varsayim"})
    return satirlar


def main() -> dict:
    adr = adresler()
    toplam = sum(a["milyar"] for a in adr)
    assert abs(toplam - tk.MEVDUAT_ADRES_MILYAR) < 0.1
    k3 = next(p for p in tk.PENCERELER if p.kod == "K3_mevduat")
    donemler = tk._iter_donem(tk.DONEM_BAS, tk.DONEM_SON)
    f3 = json.loads((KOK / "adim3_faiz_durma_sonuc.json").read_text(encoding="utf-8"))
    duran_05 = f3["yillik_duran_faiz_etkin_milyar"]["0.5"]

    satirlar, ozet = [], {}
    for th in THETA:
        for ch in CHI:
            for pi in PI:
                s = kagit_patikasi(toplam, th, ch, pi, donemler, k3)
                satirlar += s
                yil_prim: dict[str, float] = {}
                for r in s:
                    yil_prim[r["donem"][:4]] = yil_prim.get(r["donem"][:4], 0.0) + r["prim_ceyrek"]
                tepe = max(r["stok"] for r in s)
                ozet[f"th{th}_chi{ch}_pi{pi}"] = {
                    "theta": th, "chi": ch, "pi": pi, "toplam_ihrac": round(sum(r["ihrac"] for r in s), 1), "toplam_cikis": round(sum(r["cikis"] for r in s), 1),
                    "tepe_stok": round(tepe, 1), "son_stok": s[-1]["stok"], "prim_yillik": {y: round(v, 1) for y, v in yil_prim.items() if v},
                    "prim_bolu_duran_faiz_k05": {y: round(v / duran_05[y], 3) for y, v in yil_prim.items() if v and duran_05.get(y)},
                    "kredi_itki_azalt_tepe_yillik": round(tepe * tk.K3_MEVDUAT_KREDI_PAYI, 1)}
    alan = list(satirlar[0].keys())
    with (KOK / "adim4_adres_yonlendirme.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=alan); w.writeheader(); w.writerows(satirlar)

    sonuc = {"faz": 4, "adim": 4, "adim4_csv": "yazilmadi; senet satiri modellenmedi, senet_kilit.txt durur",
             "adresler": adr, "adres_toplam_milyar": round(toplam, 1), "ihracci": IHRACCI, "vade_ceyrek": VADE_CEYREK,
             "theta": list(THETA), "chi": list(CHI), "pi": list(PI), "K3_pencere": [k3.baslangic, k3.bitis],
             "kredi_payi_sabiti": tk.K3_MEVDUAT_KREDI_PAYI, "endeks_bacagi": "hesaplanmadi (hedef patikasi depoda yok)",
             "etiketler": {"A_j": "olcum", "u3": "kademe kurgusu", "theta/chi/pi/vade/ihracci": "varsayim", "kredi_payi": "kademe sabiti",
                           "prim_bolu_duran_faiz": "karsilastirma, esitlik degil"},
             "senaryolar": ozet}
    (KOK / "adim4_adres_yonlendirme_sonuc.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    f = lambda x, n=1: "" if x is None else f"{x:,.{n}f}"
    md = ["# Faz 4 — Adım 4: adres stoklarını ihraç / prim / çıkış ile bağlama (band)", "",
          "Çalıştır: `python3 adim4_adres_yonlendirme.py`. Çıktı: `adim4_adres_yonlendirme.csv`, `adim4_adres_yonlendirme_sonuc.json`.", "",
          "`adim4.csv` senet satırı `modellenmedi` kalır; `senet_kilit.txt` dokunulmaz. Burada kilidin dışında, üç ölçülmüş adres stoku üzerinde "
          "band kurulur: hiçbir sayı o satıra taşınmaz.", "",
          "## Adresler (ölçüm)", "",
          "| nesne | hazne | milyar TL | dönem |", "| --- | --- | --- | --- |"]
    md += [f"| {a['nesne']} | {a['hazne']} | {f(a['milyar'])} | {a['donem']} |" for a in adr]
    md += [f"| TOPLAM | | {f(toplam)} | |", "",
           "## Kural (varsayım)", "",
           f"- İhraç_t = θ · {f(toplam)} · Δu3_t; u3 K3 penceresi {k3.baslangic}..{k3.bitis}. θ ∈ {list(THETA)}.",
           f"- Vade {VADE_CEYREK} çeyrek; vadede (1−χ) mevduata döner, χ yenilenir; χ ∈ {list(CHI)}.",
           f"- Prim π ∈ {list(PI)} yıllık, stok üzerinden. Endeks (hedef) bacağı hesaplanmadı: hedef patikası depoda yok.",
           f"- İhraççı {IHRACCI} (varsayım). SFC: tutucu VF.2↓ VF.3↑ (NFP 0); B′ F.2↓ rezerv↓ (0); K′ F.3↑ TCMB hesabı↑ (0); prim K′→tutucu transfer (ΣNL 0).",
           f"- Kredi itişi: B′ mevduat kaybı × {tk.K3_MEVDUAT_KREDI_PAYI} (tek_sistem_kademe sabiti) yıllık kredi daralması.", "",
           "## Senaryo özeti (milyar TL)", "",
           "| θ | χ | π | toplam ihraç | toplam çıkış | tepe stok | son stok 2031-Q4 | prim 2030 | prim 2031 | prim/duran faiz κ=0,5 (2031) | kredi itki azalt (tepe, yıllık) |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for o in ozet.values():
        md.append(f"| {o['theta']} | {o['chi']} | {o['pi']} | {f(o['toplam_ihrac'])} | {f(o['toplam_cikis'])} | {f(o['tepe_stok'])} | {f(o['son_stok'])} | "
                  f"{f(o['prim_yillik'].get('2030'))} | {f(o['prim_yillik'].get('2031'))} | {o['prim_bolu_duran_faiz_k05'].get('2031', '')} | {f(o['kredi_itki_azalt_tepe_yillik'])} |")
    md += ["", "## Ne denmez", "",
           "- 'Senet modellendi' denmez; `adim4.csv` satırı `modellenmedi`, kilit duruyor. Burası band: θ, χ, π, vade, ihraççı varsayım.",
           "- HEKİS senedi (TÜFE endeksli, reel kupon 0) ile eşitlenmez; endeks bacağı burada hesaplanmadı.",
           "- Prim / duran faiz oranı karşılaştırmadır; Faz 3 κ varsayımına bağlıdır, iki sayı toplanmaz.", ""]
    (KOK / "ADIM4_ADRES_YONLENDIRME.md").write_text("\n".join(md), encoding="utf-8")
    for k, o in ozet.items():
        print(f"{k:<22} ihraç {o['toplam_ihrac']:>8,.1f} çıkış {o['toplam_cikis']:>8,.1f} tepe {o['tepe_stok']:>8,.1f} prim2031 {o['prim_yillik'].get('2031', 0):>7,.1f}")
    return sonuc


if __name__ == "__main__":
    main()
