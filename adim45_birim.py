"""Adım 4.5 — mevcut TL'den yeni fiat TL'ye geçiş (kimlik; kilit dışı).

Yeni lira altın ya da döviz üzerinde alacak değildir. Dolara çevrilerek ödenmez.
λ = 1 paritedir (varsayım). Sayılar durur; değişen, liranın bir rezerv varlığa
çevrilmemesidir. Başka bir λ ölçülmedi. 2005'teki sıfır atma bu dosyada yoktur.

  TL_yeni = TL_eski · (1 + u·(λ−1))     u=1 iken TL_yeni = λ · TL_eski
  kur_yeni = λ · kur_eski
  USD stok durur. Faiz oranı durur. İki taraf da ölçeklenir; transfer yoktur.
  ΣNL = 0. silinen boş. Borç silinmez.

Çevrilen stok (2026-Q1 ölçüm, 2030'a taşınmaz):
  TCMB F.2 para (nakit yükümlülüğü) + yurt içi TL mevduat (HPB tablo 3).
Yurt içi YP birime girmez. Adım 4 kâğıt stoku ayrı kattır, paraya eklenmez.
H VF.2 bu toplama girmez: YP'nin TL karşılığını da tutar ve HPB ile aynı çevre değildir.

Pencere 2030-Q1..2030-Q4, senaryo takvimi. K1–K3 pencerelerine eklenmez.
adim4.csv, adim5.csv, senet kilidi, üç kapı ve akış satırı yazılmaz.

Çıktı: adim45_birim.csv, adim45_birim.json, ADIM45_BIRIM.md.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

KOK = Path(__file__).resolve().parent
LAM = 1.0
PENCERE = ("2030-Q1", "2030-Q2", "2030-Q3", "2030-Q4")
OLCUM = "2026-Q1"


def _csv(ad: str) -> list[dict]:
    return list(csv.DictReader((KOK / ad).open(encoding="utf-8-sig")))


def _f(x) -> float:
    return float(x)


def olcek(eski: float, lam: float, u: float) -> float:
    """u=0 eski birim, u=1 yeni birim. λ=1 iken sonuç eskidir."""
    return eski * (1.0 + u * (lam - 1.0))


def _hucre(donem: str, blok: str, kalem: str, yon: str | None = None) -> dict:
    for r in _csv("diger_mevduat.csv"):
        if r["donem"] == donem and r["blok"] == blok and r["kalem"] == kalem and (yon is None or r["yon"] == yon):
            return r
    raise KeyError(f"{donem} {blok} {kalem} {yon}")


def _kagit() -> float:
    """θ=0,25, χ=0, π=0,02, 2030-Q4 stok. Ayrı kat; para toplamına girmez."""
    for r in _csv("adim4_adres_yonlendirme.csv"):
        if (r["donem"] == "2030-Q4" and abs(float(r["theta"]) - 0.25) < 1e-9
                and abs(float(r["chi"]) - 0.0) < 1e-9 and abs(float(r["pi"]) - 0.02) < 1e-9):
            return float(r["stok"])
    raise KeyError("kâğıt stoku 2030-Q4")


def stoklar() -> dict:
    tcmb = _hucre(OLCUM, "A_finansal_hesaplar", "TCMB", "ihrac_F2")
    banka = _hucre(OLCUM, "A_finansal_hesaplar", "Mevduat kabul eden kuruluşlar (bankalar)", "tutulan_VF2")
    nakit = _f(tcmb["para"])
    kasa = _f(banka["para"])
    tl = {
        "yurtici": _f(_hucre(OLCUM, "C_banka_sahip", "Yurt içi TL")["stok_milyar"]),
        "gercek": _f(_hucre(OLCUM, "C_banka_sahip", "Gerçek kişiler")["stok_milyar"]),
        "ticari": _f(_hucre(OLCUM, "C_banka_sahip", "Ticari kuruluşlar")["stok_milyar"]),
        "resmi": _f(_hucre(OLCUM, "C_banka_sahip", "Resmî kuruluşlar")["stok_milyar"]),
        "hhkaok": _f(_hucre(OLCUM, "C_banka_sahip", "HHKAOK")["stok_milyar"]),
        "bdfk": _f(_hucre(OLCUM, "C_banka_sahip", "Banka dışı finansal kuruluşlar")["stok_milyar"]),
    }
    parca = tl["gercek"] + tl["ticari"] + tl["resmi"] + tl["hhkaok"] + tl["bdfk"]
    if abs(parca - tl["yurtici"]) > 0.05:
        raise ValueError(f"TL mevduat parçaları {parca} toplam {tl['yurtici']} ile örtüşmüyor")
    yp = {
        "yurtici": _f(_hucre(OLCUM, "C_banka_sahip", "Yurt içi YP")["stok_milyar"]),
        "gercek": _f(_hucre(OLCUM, "C_banka_sahip", "Gerçek kişiler YP")["stok_milyar"]),
        "tuzel": _f(_hucre(OLCUM, "C_banka_sahip", "Tüzel kişiler YP (ticari+resmî+BDFK+HHKAOK ayrılmaz)")["stok_milyar"]),
    }
    toplam = nakit + tl["yurtici"]
    return {"nakit": nakit, "kasa_icinde": kasa, "tl": tl, "yp": yp, "toplam": toplam, "kagit": _kagit()}


def _satir(donem: str, u: str, nesne: str, eski, yeni, birim: str, etiket: str, notu: str) -> dict:
    if eski == "" or yeni == "":
        fark = ""
    else:
        fark = round(float(yeni) - float(eski), 4)
        eski, yeni = round(float(eski), 4), round(float(yeni), 4)
    return {"donem": donem, "u": u, "lam": LAM, "nesne": nesne, "eski": eski, "yeni": yeni,
            "fark": fark, "birim": birim, "etiket": etiket, "not": notu}


def _tablolar(s: dict) -> list[dict]:
    tl, yp = s["tl"], s["yp"]
    parca = [
        ("tcmb_nakit_yukumluluk", s["nakit"], "olcum", "TCMB F.2 para. Banka kasası bunun içindedir, eklenmez."),
        ("yurtici_tl_mevduat", tl["yurtici"], "olcum", "HPB tablo 3. YP yoktur."),
        ("gercek_kisi_tl", tl["gercek"], "olcum", "HPB tablo 3.3"),
        ("ticari_tl", tl["ticari"], "olcum", "HPB tablo 3.6"),
        ("resmi_tl", tl["resmi"], "olcum", "HPB tablo 3.9"),
        ("hhkaok_tl", tl["hhkaok"], "olcum", "HPB tablo 3.12"),
        ("bdfk_tl", tl["bdfk"], "olcum", "HPB tablo 3.15"),
        ("tl_para_toplam", s["toplam"], "olcum", "Nakit yükümlülüğü + yurt içi TL mevduat. M1 değildir."),
    ]
    rows = [_satir(OLCUM, "", ad, v, olcek(v, LAM, 1.0), "milyar TL", et, nt) for ad, v, et, nt in parca]
    rows.append(_satir(OLCUM, "", "yurtici_yp_tl_karsilik", yp["yurtici"], olcek(yp["yurtici"], LAM, 1.0),
                       "milyar TL karsilik", "olcum_cevrilemez", "USD stok durur. TL karşılığı kur ile ölçeklenir."))
    rows.append(_satir(OLCUM, "", "gercek_kisi_yp", yp["gercek"], olcek(yp["gercek"], LAM, 1.0),
                       "milyar TL karsilik", "olcum_cevrilemez", "Adım 4 adresidir. Fiat TL stokuna girmez."))
    rows.append(_satir(OLCUM, "", "tuzel_yp", yp["tuzel"], olcek(yp["tuzel"], LAM, 1.0),
                       "milyar TL karsilik", "olcum_cevrilemez", "USD stok durur."))
    rows.append(_satir("2030-Q4", "1", "kagit_stok_theta_025", s["kagit"], olcek(s["kagit"], LAM, 1.0),
                       "milyar TL", "band_varsayim", "Ayrı kat. Para toplamına eklenmez. θ=0,25, χ=0."))
    for i, d in enumerate(PENCERE):
        u = (i + 1) / len(PENCERE)
        rows.append(_satir(d, f"{u:.2f}", "tl_para_toplam", s["toplam"], olcek(s["toplam"], LAM, u),
                           "milyar TL", "senaryo_takvimi", "Stok 2026-Q1 ölçümüdür, 2030'a taşınmaz."))
        rows.append(_satir(d, f"{u:.2f}", "kur_carpan", 1.0, 1.0 + u * (LAM - 1.0),
                           "carpan", "kimlik", "kur_yeni = λ · kur_eski. Düzey tahmini bu dosyada yok."))
        rows.append(_satir(d, f"{u:.2f}", "usd_stok_carpan", 1.0, 1.0, "carpan", "kimlik", "USD stok durur."))
        rows.append(_satir(d, f"{u:.2f}", "faiz_orani_carpan", 1.0, 1.0, "carpan", "kimlik", "r ve AOFM ölçeklenmez."))
        rows.append(_satir(d, f"{u:.2f}", "nfp_fark", 0.0, 0.0, "milyar TL", "kimlik", "İki taraf da ölçeklenir. Transfer yoktur."))
        rows.append(_satir(d, f"{u:.2f}", "nl_toplam", 0.0, 0.0, "milyar TL", "kimlik", "ΣNL = 0."))
        rows.append(_satir(d, f"{u:.2f}", "silinen", "", "", "milyar TL", "bos", "Geçiş silme değildir."))
    return rows


def main() -> dict:
    s = stoklar()
    rows = _tablolar(s)
    with (KOK / "adim45_birim.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    toplam_yeni = olcek(s["toplam"], LAM, 1.0)
    r = json.loads((KOK / "faiz_fatura_kalibre.json").read_text(encoding="utf-8"))["r_2025"]
    sonuc = {
        "adim": 4.5,
        "pencere": list(PENCERE),
        "etiket_takvim": "senaryo_takvimi",
        "olcum_donem": OLCUM,
        "lam": LAM,
        "lam_etiket": "varsayim_parite",
        "fiat": "Yeni TL altın ya da döviz üzerinde alacak değildir. Dolara çevrilerek ödenmez.",
        "kimlik": "TL_yeni = TL_eski * (1 + u*(lam-1)); u=1 iken lam * eski. kur ayni carpan. USD stok ve faiz orani durur.",
        "stok_milyar": {
            "tcmb_nakit": s["nakit"],
            "banka_kasasi_nakit_icinde": s["kasa_icinde"],
            "yurtici_tl_mevduat": s["tl"]["yurtici"],
            "tl_para_toplam": round(s["toplam"], 1),
            "tl_para_yeni_lam1": round(toplam_yeni, 1),
            "fark_lam1": round(toplam_yeni - s["toplam"], 4),
            "yurtici_yp_tl_karsilik": s["yp"]["yurtici"],
            "gercek_kisi_yp": s["yp"]["gercek"],
            "kagit_theta_025": s["kagit"],
        },
        "r_2025_durur": {k: r[k] for k in ("r_ic", "r_dis", "r_diger")},
        "silinen": "",
        "yazilmayan": ["adim4.csv", "adim5.csv", "senet_kilit.txt", "kapi_kilit.txt", "tavan_akis.csv", "tek_sistem_kademe.py"],
    }
    (KOK / "adim45_birim.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    f = lambda x: f"{x:,.1f}"
    md = [
        "# Adım 4.5 — TL'den yeni fiat TL'ye geçiş",
        "",
        "Çalıştır: `python3 adim45_birim.py`. Çıktı: `adim45_birim.csv`, `adim45_birim.json`.",
        "",
        "Yeni lira altın ya da döviz üzerinde alacak değildir. Dolara çevrilerek ödenmez. λ = 1 paritedir; bu bir varsayımdır. "
        "Sayılar durur. Başka bir λ bütün TL stoklarını, TL akışlarını ve kuru aynı çarpanla ölçekler. USD stoku ve faiz oranı durur. "
        "Ölçülmüş bir sıfır atma yoktur.",
        "",
        f"Takvim {PENCERE[0]} .. {PENCERE[-1]}, senaryo takvimi. K3 bundan önce kapanır. Adım 5'in penceresi yoktur. "
        "Üç kademe penceresine dördüncü pencere eklenmez.",
        "",
        f"## Stok, {OLCUM} ölçümü (milyar TL)",
        "",
        "| Nesne | Eski | Yeni, λ=1 | Fark | Etiket |",
        "| --- | ---: | ---: | ---: | --- |",
        f"| TCMB nakit yükümlülüğü | {f(s['nakit'])} | {f(s['nakit'])} | 0 | ölçüm |",
        f"| Yurt içi TL mevduat | {f(s['tl']['yurtici'])} | {f(s['tl']['yurtici'])} | 0 | ölçüm |",
        f"| — gerçek kişi TL | {f(s['tl']['gercek'])} | {f(s['tl']['gercek'])} | 0 | ölçüm |",
        f"| — ticari TL | {f(s['tl']['ticari'])} | {f(s['tl']['ticari'])} | 0 | ölçüm |",
        f"| — resmî TL | {f(s['tl']['resmi'])} | {f(s['tl']['resmi'])} | 0 | ölçüm |",
        f"| — HHKAOK TL | {f(s['tl']['hhkaok'])} | {f(s['tl']['hhkaok'])} | 0 | ölçüm |",
        f"| — banka dışı finansal TL | {f(s['tl']['bdfk'])} | {f(s['tl']['bdfk'])} | 0 | ölçüm |",
        f"| **Toplam** | **{f(s['toplam'])}** | **{f(toplam_yeni)}** | **0** | ölçüm |",
        "",
        f"Banka kasasındaki para {f(s['kasa_icinde'])} bu nakit yükümlülüğünün içindedir. İkinci kez eklenmez.",
        "",
        "## Girmeyenler",
        "",
        f"| Nesne | TL karşılığı | λ=1 sonrası | |",
        "| --- | ---: | ---: | --- |",
        f"| Yurt içi YP | {f(s['yp']['yurtici'])} | {f(s['yp']['yurtici'])} | USD stok durur |",
        f"| Gerçek kişi YP | {f(s['yp']['gercek'])} | {f(s['yp']['gercek'])} | fiat TL stokuna girmez |",
        f"| Tüzel YP | {f(s['yp']['tuzel'])} | {f(s['yp']['tuzel'])} | USD stok durur |",
        f"| Kâğıt stoku, θ=0,25, 2030-Q4 | {f(s['kagit'])} | {f(s['kagit'])} | ayrı kat, paraya eklenmez |",
        "",
        "H VF.2 (15.356,8) toplama yazılmaz. YP'nin TL karşılığını da tutar. HPB yurt içi TL ile aynı çevre değildir.",
        "",
        "## Kimlik",
        "",
        "- TL_yeni = TL_eski · (1 + u·(λ−1)). 2030-Q4'te u=1, TL_yeni = λ · TL_eski.",
        "- kur_yeni = λ · kur_eski. Bu dosya 2030 kur düzeyi tahmin etmez.",
        "- USD stok ×1. r_ic, r_dis, r_diger ve AOFM ×1.",
        "- İki taraf da ölçeklenir. NFP farkı 0. ΣNL = 0. silinen boş.",
        "- TL cinsinden oran, payda da TL ise durur. GSYH patikası bu dosyada kurulmaz.",
        "",
        "## Ne denmez",
        "",
        "- Altı sıfır atıldı denmez. λ ölçülmedi. Parite 1'dir.",
        "- Borç silindi denmez. `silinen` boş kalır.",
        "- YP mevduat yeni TL'ye çevrildi denmez.",
        "- Kâğıt stoku para stokuna eklendi denmez.",
        "- Geçiş Hazine faiz faturasını indirdi denmez. λ=1 iken fatura farkı 0'dır.",
        "- Senet satırı doldu denmez. `adim4.csv` ve kilit durur.",
        "",
    ]
    (KOK / "ADIM45_BIRIM.md").write_text("\n".join(md), encoding="utf-8")
    print(f"lam {LAM} toplam {s['toplam']:.1f} yeni {toplam_yeni:.1f} fark {toplam_yeni - s['toplam']:.4f}")
    return sonuc


if __name__ == "__main__":
    main()
