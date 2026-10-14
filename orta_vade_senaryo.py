"""Orta vade: beş adım takvimi ile Hazine faiz faturası, aynı yıllar, ayrı sütunlar.

Pencere 2027–2029. 2027 K1 (adım 1 akış ve adım 2), 2028 K2 (adım 1 stok tavanı ve adım 3),
2029 K3 (adım 4). Adım 5'in penceresi yok.

Fatura kimliği faiz_fatura_kalibre ile aynı: r 2025'ten, eğim 2024-Q4→2026-Q2.
Beş adım r'yi ve kuru değiştirmez. Özel USD akışının sıfırlanması faturaya girmez.
Katman sayıları toplanmaz. Kilitli adım dosyalarına yazılmaz.

Çalıştır: python3 orta_vade_senaryo.py
Çıktı: orta_vade_senaryo.csv, orta_vade_senaryo.json, ORTA_VADE_SENARYO.md
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

import faiz_fatura_kalibre as fk

KOK = Path(__file__).resolve().parent
YILLAR = (2026, 2027, 2028, 2029)
N_2029 = 14  # 2026-Q3 .. 2029-Q4
KAPPA_SATIR = 0.25
THETA_SATIR = 0.25


def _panel() -> pd.DataFrame:
    p = pd.read_csv(KOK / "faiz_fatura_panel.csv", index_col=0)
    p.index = p.index.astype(str)
    return p


def _faturalar(panel: pd.DataFrame, kal: dict) -> dict:
    r = kal["r_2025"]
    egim = kal["egim"]
    kur_g = float(kal["kur_g"])
    yollar = {
        "mevcut": dict(ozel_dur=False, kamu_dur=False, kur_dur=False, ic_dur=False),
        "aktarim": dict(ozel_dur=True, kamu_dur=False, kur_dur=False, ic_dur=False),
        "donuk": dict(ozel_dur=True, kamu_dur=True, kur_dur=True, ic_dur=True),
    }
    ileri = {ad: fk._ileri(panel, egim, kur_g, n=N_2029, **k) for ad, k in yollar.items()}
    out = {}
    for ad, yol in ileri.items():
        out[ad] = {}
        for y in YILLAR:
            ic_ort, kamu_tl = fk._yil_ort(panel, yol, y)
            fat = fk._fatura(r, ic_ort, kamu_tl)
            son = yol.loc[f"{y}-Q4"] if f"{y}-Q4" in yol.index else panel.loc[f"{y}-Q4"]
            out[ad][str(y)] = {
                **{k: round(v, 1) for k, v in fat.items()},
                "ic_stok_ortalama": round(ic_ort, 1),
                "ic_stok_yil_sonu": round(float(son.ic_stok), 1),
                "kamu_usd_yil_sonu": round(float(son.kamu_usd), 1),
                "ozel_usd_yil_sonu": round(float(son.ozel_usd), 1),
                "kur_yil_sonu": round(float(son.kur), 2),
            }
    return out


def _kademe() -> dict[str, dict]:
    k = pd.read_csv(KOK / "tek_sistem_kademe.csv", dtype={"Donem": str})
    satir = {}
    for y in (2027, 2028, 2029):
        r = k[k.Donem == f"{y}-Q4"].iloc[0]
        satir[str(y)] = {
            "K1": float(r.K1_uygulama_orani),
            "K2": float(r.K2_uygulama_orani),
            "K3": float(r.K3_uygulama_orani),
            "k1_itis_tempo_yil": float(r.k1_itis_azalt_milyar_yillik),
            "k2_brut_ust": float(r.k2_brut_zincir_fazla_azalt_ust_milyar),
            "k3_kredi_tempo_yil": float(r.k3_kredi_itki_azalt_milyar_yillik),
            "f4_fark_kumul": float(r.f4_stok_fark_milyar),
        }
    return satir


def _duran_faiz() -> dict[str, float]:
    d = pd.read_csv(KOK / "adim3_faiz_durma.csv")
    d = d[d.kappa == KAPPA_SATIR].copy()
    d["yil"] = d.donem.str.slice(0, 4)
    return {y: round(float(g.duran_faiz_etkin_milyar.sum()), 1) for y, g in d.groupby("yil")}


def _prim() -> dict[str, dict]:
    a = pd.read_csv(KOK / "adim4_adres_yonlendirme.csv")
    a = a[(a.theta == THETA_SATIR) & (a.chi == 0.0)].copy()
    a["yil"] = a.donem.str.slice(0, 4)
    out = {}
    for y, g in a.groupby("yil"):
        if y not in ("2029",):
            # 2030 orta vadeyi aşar; 2029 ihraç yılı primini al
            if int(y) > 2029:
                continue
        alt = float(g[g.pi == 0.02].prim_ceyrek.sum())
        ust = float(g[g.pi == 0.05].prim_ceyrek.sum())
        out[str(y)] = {"alt": round(alt, 1), "ust": round(ust, 1)}
    return out


def _satirlar(fat: dict, kad: dict, duran: dict, prim: dict) -> list[dict]:
    es = {
        "2026": {
            "acik_adim": "hicbiri",
            "adim_nesne": "olcum ve kalibrasyon yili",
            "adim_sayi": 0.0,
            "adim_birim": "—",
            "adim_etiket": "olcum",
        },
        "2027": {
            "acik_adim": "1 akis + 2",
            "adim_nesne": "K1 itis freni, yil sonu tempo",
            "adim_sayi": kad["2027"]["k1_itis_tempo_yil"],
            "adim_birim": "milyar TL/yil",
            "adim_etiket": "senaryo_takvimi",
        },
        "2028": {
            "acik_adim": "1 stok tavani + 3",
            "adim_nesne": "adim 3 duran faiz, kappa 0.25, banka yazar",
            "adim_sayi": duran.get("2028", 0.0),
            "adim_birim": "milyar TL/yil",
            "adim_etiket": "varsayim_kappa",
        },
        "2029": {
            "acik_adim": "4",
            "adim_nesne": "adim 4 prim bandi, theta 0.25, pi 0.02-0.05",
            "adim_sayi": prim.get("2029", {}).get("ust", 0.0),
            "adim_birim": "milyar TL/yil",
            "adim_etiket": "band_varsayim",
        },
    }
    rows = []
    for y in YILLAR:
        ys = str(y)
        m = fat["mevcut"][ys]
        a = fat["aktarim"][ys]
        z = fat["donuk"][ys]
        rows.append({
            "yil": y,
            "hazine_mevcut": m["toplam"],
            "hazine_ic": m["ic"],
            "hazine_dis": m["dis"],
            "hazine_diger": m["diger"],
            "hazine_aktarim": a["toplam"],
            "hazine_fark_aktarim": round(a["toplam"] - m["toplam"], 1),
            "hazine_haziran_stok_donuk": z["toplam"],
            "ic_stok_yil_sonu": m["ic_stok_yil_sonu"],
            "ozel_usd_yil_sonu": m["ozel_usd_yil_sonu"],
            "ozel_usd_aktarim_yil_sonu": a["ozel_usd_yil_sonu"],
            "kur_model_yil_sonu": m["kur_yil_sonu"],
            **es[ys],
            "k2_brut_ust": kad.get(ys, {}).get("k2_brut_ust", 0.0),
            "f4_fark_kumul": kad.get(ys, {}).get("f4_fark_kumul", 0.0),
            "duran_faiz_kappa_025": duran.get(ys, 0.0),
            "prim_alt": prim.get(ys, {}).get("alt", 0.0),
            "prim_ust": prim.get(ys, {}).get("ust", 0.0),
        })
    return rows


def _md(rows: list[dict], fat: dict) -> str:
    def h(y: int) -> dict:
        return next(r for r in rows if r["yil"] == y)

    a, b, c = h(2027), h(2028), h(2029)
    m26 = fat["mevcut"]["2026"]["toplam"]
    return "\n".join([
        "# Orta vade senaryosu, 2027–2029",
        "",
        "Beş adım kendi yılında açılır. Hazine faiz faturası o yıllarda ayrı yürür. İki sütun toplanmaz.",
        "",
        "Fatura: r 2025 kuponu (kalibrasyon). Eğim 2024-Q4 → 2026-Q2 (ölçüm). Beş adımın faiz ve kur etkisi `modellenmedi`.",
        "",
        "## Hazine faturası, milyar TL",
        "",
        "| Yıl | Mevcut tempo | Özel USD akışı 0 | Haziran 2026 stoku donuk | İç stok yıl sonu | Özel USD yıl sonu | Kur model yıl sonu |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        f"| 2026 | {m26:.0f} | {fat['aktarim']['2026']['toplam']:.0f} | {fat['donuk']['2026']['toplam']:.0f} | {fat['mevcut']['2026']['ic_stok_yil_sonu']:.0f} | {fat['mevcut']['2026']['ozel_usd_yil_sonu']:.0f} | {fat['mevcut']['2026']['kur_yil_sonu']:.1f} |",
        f"| 2027 | {a['hazine_mevcut']:.0f} | {a['hazine_aktarim']:.0f} | {a['hazine_haziran_stok_donuk']:.0f} | {a['ic_stok_yil_sonu']:.0f} | {a['ozel_usd_yil_sonu']:.0f} | {a['kur_model_yil_sonu']:.1f} |",
        f"| 2028 | {b['hazine_mevcut']:.0f} | {b['hazine_aktarim']:.0f} | {b['hazine_haziran_stok_donuk']:.0f} | {b['ic_stok_yil_sonu']:.0f} | {b['ozel_usd_yil_sonu']:.0f} | {b['kur_model_yil_sonu']:.1f} |",
        f"| 2029 | {c['hazine_mevcut']:.0f} | {c['hazine_aktarim']:.0f} | {c['hazine_haziran_stok_donuk']:.0f} | {c['ic_stok_yil_sonu']:.0f} | {c['ozel_usd_yil_sonu']:.0f} | {c['kur_model_yil_sonu']:.1f} |",
        "",
        f"2026 modeli {m26:.0f}. Ödenek 2.742. Özel USD akışını sıfırlamak 2027 farkını **{a['hazine_fark_aktarim']:+.1f}**, 2028 farkını **{b['hazine_fark_aktarim']:+.1f}**, 2029 farkını **{c['hazine_fark_aktarim']:+.1f}** bırakır.",
        "",
        f"2029 mevcut tempo **{c['hazine_mevcut']:.0f}**. Bunun içi {c['hazine_ic']:.0f}, dışı {c['hazine_dis']:.0f}, diğer {c['hazine_diger']:.0f}. İç stok yıl sonu {c['ic_stok_yil_sonu']:.0f} milyar TL.",
        "",
        "2026’nın donuk sütunu 2.598’dir: ilk yarı ölçülmüş stok, ikinci yarı Haziran stoku. 2027’den itibaren yılın tamamı Haziran 2026 stokundadır: 2.625.",
        "",
        "Kur sütunu ölçülmüş çeyrek ortalamasının bileşik eğimidir. 2026-Q4 ve sonrası gerçekleşmiş kur değildir. 2027-Q4 model düzeyi 59,7; aynı yılın anketi 58,60. 2028 ve 2029 anketi yoktur. 71,7 ve 86,1 eğimin uzamasıdır.",
        "",
        "Ağustos 2026 iç stok ölçümü 9.545. Eğimin Haziran’dan düz çizgisi Ağustos’ta 9.464 eder. Düzey çizgiye yakındır. İki aylık tempo çeyreğe çekilirse +797 milyar TL olur; senaryo eğimi +676’da kalır.",
        "",
        "## Beş adım, aynı yıllar",
        "",
        "| Yıl | Açık adım | Adımın kendi sayısı | Birim | Etiket |",
        "| --- | --- | ---: | --- | --- |",
        "| 2026 | hiçbiri | 0 | — | ölçüm |",
        f"| 2027 | 1 akış ve 2, K1 | {a['adim_sayi']:.0f} | milyar TL/yıl, yıl sonu itiş temposu | senaryo takvimi |",
        f"| 2028 | 1 stok tavanı, K2; adım 3 | {b['duran_faiz_kappa_025']:.0f} | milyar TL/yıl, duran firma faizi, κ=0,25 | varsayım |",
        f"| 2029 | 4, K3 | {c['prim_alt']:.0f}–{c['prim_ust']:.0f} | milyar TL, prim, θ=0,25 | band varsayım |",
        "| 2027–2029 | 5 | — | kira satırı | ölçülmedi |",
        "",
        f"2027 yıl sonu K1 itiş temposu {a['adim_sayi']:.0f}. Yıl içinde biriken F.4 farkı {a['f4_fark_kumul']:.0f}. Bu, stoktan silinen tutar değildir. `silinen` boş kalır. Akış satırı 0,427 `baska_nesne` olarak durur.",
        "",
        f"2028 yıl sonu K2 brüt üst sınır {b['k2_brut_ust']:.0f}. Adım 3’ün duran faizi {b['duran_faiz_kappa_025']:.0f}. Bunu banka yazar. Hazine faiz satırından düşülmez. ΣNL = 0. K1 aynı yılda açık kalır; itiş temposu 2.058,5.",
        "",
        f"2029 prim bandı {c['prim_alt']:.0f}–{c['prim_ust']:.0f}. Aynı yıl adım 3 tam yıldır: duran faiz {c['duran_faiz_kappa_025']:.0f}. Prim ile duran faiz toplanmaz. İhraççı varsayımı K′. Senet satırı `modellenmedi` kalır. Adım 5’in orta vadede penceresi yoktur. Ho→Ha bandı (yüzde 20 kapsama, 52–160) bu tabloya yazılmaz.",
        "",
        "## Ne denmez",
        "",
        "- Beş adım Hazine faturasını 2029’da sabitledi denmez. Mevcut tempo faturası yürür.",
        "- Özel dış borç akışı durunca fatura değişir denmez. Üç yılda da fark 0,0.",
        "- Adım 3’ün 1.208’i 2029 Hazine faizinden düşülür denmez. Ödeyen bankadır.",
        "- Prim, duran faiz ve Hazine kuponu toplanır denmez.",
        "- Kur durur ya da politika faizi iner denmez. İkisi `modellenmedi`.",
        "- Stok yüzde 20 silindi denmez.",
        "",
    ])


def main() -> None:
    panel = _panel()
    kal = json.loads((KOK / "faiz_fatura_kalibre.json").read_text(encoding="utf-8"))
    fat = _faturalar(panel, kal)
    kad = _kademe()
    duran = _duran_faiz()
    prim = _prim()
    rows = _satirlar(fat, kad, duran, prim)
    pd.DataFrame(rows).to_csv(KOK / "orta_vade_senaryo.csv", index=False)
    blob = {
        "pencere": "2027-2029",
        "etiket": {
            "fatura": "kalibrasyon_2025_kimlik_olculen_egim",
            "adim_faiz_kur": "modellenmedi",
            "aktarim": "varsayim_ozel_usd_akisi_sifir",
            "adim3": "varsayim_kappa_0.25",
            "adim4": "band_varsayim_theta_0.25",
            "adim5": "olculmedi",
        },
        "faturalar": fat,
        "kademe_yil_sonu": kad,
        "duran_faiz_kappa_025": duran,
        "prim_theta_025": prim,
        "satirlar": rows,
    }
    (KOK / "orta_vade_senaryo.json").write_text(json.dumps(blob, ensure_ascii=False, indent=2), encoding="utf-8")
    (KOK / "ORTA_VADE_SENARYO.md").write_text(_md(rows, fat), encoding="utf-8")
    for r in rows:
        print(r["yil"], r["hazine_mevcut"], r["hazine_fark_aktarim"], r["acik_adim"], r["adim_sayi"])


if __name__ == "__main__":
    main()
