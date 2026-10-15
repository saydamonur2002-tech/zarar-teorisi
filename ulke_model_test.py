"""Ülke modeli çalışıyor mu: kapı kapı test.

Çalıştır: python3 ulke_model_test.py
Çıktı: ulke_model_test.csv, ulke_model_test.json, ULKE_MODEL_TEST.md

Tam koşu üç kapıyı birlikte ister: yazılan stok, fatura kuponu, beş adım bir arada.
Biri yoksa ülke kalır. Türkiye faiz dosyası bu koşuya girmez.
Yerli = stok − yurt dışı ise toplam tanım gereği tutar; bağımsız test sayılmaz.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import ulke_karsilastirma as kars
import ulke_model_dene as dene

KOK = Path(__file__).resolve().parent
TOL = 1e-6

# uluslararasi_uygulamalar.csv durumları. Yeni sorgu yok.
ADIM_KAYIT = {
    "Çin": "uygulandi_tarihsel; adım 3 tersi, kredi enjeksiyonu",
    "Meksika": "adim2_4_kismi; nesne banka kredisi, 1995",
    "Brezilya": "adim4_5_kismi; yeni inşa, 1964",
    "İtalya": "ozel_platform",
    "İspanya": "ozel_platform; adim5_bulundu",
}


def _bos(x) -> bool:
    return x is None or x == ""


def _ham() -> list[dict]:
    out = []
    for r in kars.SATIRLAR:
        g = dene.GIRDI.get(r["ulke"], {})
        y = float(r["yabanci_pay"])
        stok, stok_durum = dene._payda(g, y) if g else (None, "yok")
        yabanci = g.get("yabanci_stok") if g else None
        yabanci_bagimsiz = yabanci is not None
        if yabanci is None and stok is not None:
            yabanci = stok * y
        yerli = None if stok is None or yabanci is None else stok - yabanci
        satir = dene._satir(r)
        out.append({
            "ulke": r["ulke"],
            "stok": stok,
            "stok_durum": stok_durum,
            "yerli": yerli,
            "yabanci": yabanci,
            "yabanci_bagimsiz": yabanci_bagimsiz,
            "yazilan": satir["yazilan"],
            "yazilan_durum": satir["yazilan_durum"],
            "fatura": satir["fatura"],
            "kagit": satir["kagit"],
        })
    return out


def _kimlik(h: dict) -> str:
    if h["stok"] is None or h["yerli"] is None or h["yabanci"] is None:
        return "veri_yok"
    fark = abs(h["yerli"] + h["yabanci"] - h["stok"])
    if fark > TOL:
        return "kaldi"
    if h["stok_durum"] == "olcum" and h["yabanci_bagimsiz"]:
        return "bagimsiz_gecti"
    return "kurulum"


def _para_kimlik() -> dict:
    tr = dene.GIRDI["Türkiye"]
    ar = dene.GIRDI["Arjantin"]
    tr_fark = abs(tr["yerli_para_stok"] + tr["doviz_stok"] - tr["stok"])
    ar_yer = abs((ar["stok"] - ar["yabanci_stok"]) + ar["yabanci_stok"] - ar["stok"])
    ar_para = abs(ar["yerli_para_stok"] + ar["doviz_stok"] - ar["stok"])
    return {
        "turkiye_para": "gecti" if tr_fark <= TOL else "kaldi",
        "turkiye_para_fark": tr_fark,
        "arjantin_yerlesim": "gecti" if ar_yer <= TOL else "kaldi",
        "arjantin_para": "gecti" if ar_para <= TOL else "kaldi",
        "arjantin_para_fark": ar_para,
    }


def _satir_test(h: dict) -> dict:
    kimlik = _kimlik(h)
    yazilan = "gecti" if not _bos(h["yazilan"]) else "kaldi"
    fatura = "veri_yok" if _bos(h["fatura"]) else "gecti"
    adim = ADIM_KAYIT.get(h["ulke"], "taramada_yok")
    paket = "bulunamadi"
    calisiyor = yazilan == "gecti" and fatura == "gecti" and paket == "gecti"
    neden = []
    if yazilan != "gecti":
        neden.append(h["yazilan_durum"])
    if fatura != "gecti":
        neden.append("fatura_yok")
    if paket != "gecti":
        neden.append("bes_adim_yok")
    return {
        "ulke": h["ulke"],
        "kimlik": kimlik,
        "yazilan": yazilan,
        "yazilan_durum": h["yazilan_durum"],
        "fatura": fatura,
        "adim_kayit": adim,
        "bes_adim": paket,
        "calisiyor": "evet" if calisiyor else "hayir",
        "neden": ", ".join(neden),
    }


def _band() -> dict:
    baz = {r["ulke"]: kars.etiket(r["yabanci_pay"], r["doviz_pay"]) for r in kars.SATIRLAR}
    alt = {r["ulke"]: kars.etiket(r["yabanci_pay"], r["doviz_pay"], 0.15, 0.15) for r in kars.SATIRLAR}
    ust = {r["ulke"]: kars.etiket(r["yabanci_pay"], r["doviz_pay"], 0.25, 0.25) for r in kars.SATIRLAR}
    return {
        "min_degisen": sorted(u for u in baz if baz[u] != alt[u]),
        "max_degisen": sorted(u for u in baz if baz[u] != ust[u]),
    }


def main() -> dict:
    ham = _ham()
    rows = [_satir_test(h) for h in ham]
    para = _para_kimlik()
    band = _band()
    paket_satir = next(
        r for r in csv.DictReader((KOK / "uluslararasi_uygulamalar.csv").open(encoding="utf-8-sig"))
        if r["sistem"].startswith("Beş adım")
    )
    calisan = [r["ulke"] for r in rows if r["calisiyor"] == "evet"]
    sonuc = {
        "n": len(rows),
        "calisan": len(calisan),
        "calisan_ulkeler": calisan,
        "yazilan_gecti": sum(r["yazilan"] == "gecti" for r in rows),
        "fatura_gecti": sum(r["fatura"] == "gecti" for r in rows),
        "bes_adim": paket_satir["durum"],
        "bes_adim_sorgu": paket_satir["sorgu"],
        "kimlik_bagimsiz": para,
        "band": band,
        "turkiye_fatura_baska_dosya": {
            "dosya": "orta_vade_senaryo.json",
            "yil": 2029,
            "faiz_37": 5338.0,
            "durum": "bu kosuya girmez",
        },
        "satirlar": rows,
    }
    if sonuc["calisan"] != 0:
        raise SystemExit(f"beklenen calisan 0, gelen {sonuc['calisan']}")
    if sonuc["yazilan_gecti"] != 6:
        raise SystemExit(f"beklenen yazilan 6, gelen {sonuc['yazilan_gecti']}")
    if para["turkiye_para"] != "gecti" or para["arjantin_para"] != "gecti" or para["arjantin_yerlesim"] != "gecti":
        raise SystemExit(f"bagimsiz kimlik kaldi: {para}")
    if band["min_degisen"] or band["max_degisen"] != ["Euro alanı", "Türkiye"]:
        raise SystemExit(f"band kaydi: {band}")
    if paket_satir["durum"] != "bulunamadi":
        raise SystemExit("bes adim satiri degismis")

    alan = list(rows[0].keys())
    with (KOK / "ulke_model_test.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=alan)
        w.writeheader()
        w.writerows(rows)
    (KOK / "ulke_model_test.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    md = [
        "# Ülke modeli testi",
        "",
        "Çalıştır: `python3 ulke_model_test.py`.",
        "",
        f"Tam model çalışan: **{sonuc['calisan']} / {sonuc['n']}**.",
        "",
        "Kapı: yazılan stok, fatura kuponu, beş adım bir arada. Üçü birlikte yoksa ülke kalır.",
        f"Yazılan kapısı geçen: {sonuc['yazilan_gecti']}. Fatura kapısı geçen: {sonuc['fatura_gecti']}. "
        f"Beş adım bir arada: {paket_satir['durum']} ({paket_satir['sorgu']} sorgu).",
        "",
        "Bağımsız toplam, ölçüm: Türkiye yerli para 6.407,0 + döviz 1.745,8 = 8.152,8. "
        "Arjantin yerleşim 155,312 + 297,345 = 452,657. Arjantin para 190,904 + 261,753 = 452,657.",
        "Yerli alacaklı = stok − yurt dışı olan satırda toplam kurulumdur. Ayrı ölçüm sayılmaz.",
        "",
        "Türkiye 2029 faiz-37 faturası 5.338, `orta_vade_senaryo.json`. Bu koşuya girmez.",
        "",
        "| Ülke | Kimlik | Yazılan | Fatura | Adım kaydı | Beş adım | Çalışıyor |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        md.append(
            f"| {r['ulke']} | {r['kimlik']} | {r['yazilan']} | {r['fatura']} | {r['adim_kayit']} | "
            f"{r['bes_adim']} | {r['calisiyor']} |"
        )
    md += [
        "",
        f"Aralık 0,15'te etiket değişen: {len(band['min_degisen'])}. "
        f"0,25'te etiket değişen: {', '.join(band['max_degisen'])}.",
        "",
        "## Ne denmez",
        "",
        "- Model bu ülkelerde çalışıyor denmez. Tam kapı 0 ülkede kapandı.",
        "- Kurulum toplamı bağımsız ölçüm denmez.",
        "- Kısmi adım kaydı, beş adımın kurulduğu anlamına gelmez.",
        "- 5.338 bu testin faturası denmez. Ayrı dosyadadır.",
        "",
    ]
    (KOK / "ULKE_MODEL_TEST.md").write_text("\n".join(md), encoding="utf-8")
    print(f"calisan {sonuc['calisan']} / {sonuc['n']}")
    print(f"yazilan {sonuc['yazilan_gecti']}  fatura {sonuc['fatura_gecti']}  bes_adim {paket_satir['durum']}")
    print(f"bagimsiz {para['turkiye_para']} {para['arjantin_yerlesim']} {para['arjantin_para']}")
    for r in rows:
        print(f"{r['ulke']:<12} {r['calisiyor']:<6} {r['neden']}")
    return sonuc


if __name__ == "__main__":
    main()
