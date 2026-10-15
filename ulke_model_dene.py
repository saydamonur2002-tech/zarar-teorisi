"""Deneme: karşılaştırma ülkelerinin yayımlanmış stoku.

Türkiye faiz faturasını çağırmaz. Beş adımı kurmaz. Kupon, kur yolu ve fatura boştur.
Yerli alacaklı düzeyi, aynı stokun yurt dışı payı biliniyorsa yazılır.
Para ve yerleşim çaprazı yoksa yazılan hücre boş kalır.
Kâğıt cinsinden konan döviz 0, ölçülmüş döviz stoku diye yazılmaz.

Çalıştır: python3 ulke_model_dene.py
Çıktı: ulke_model_dene.csv, ulke_model_dene.json, ULKE_MODEL_DENE.md
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import ulke_karsilastirma as kars

KOK = Path(__file__).resolve().parent

# Düzey, satırın kendi birimindedir. Pay ulke_karsilastirma satırından gelir.
# stok, yabanci payının paydasıdır. yabanci_stok yayımlanmış düzeydir.
# doviz_stok aynı stokun para kırılımıdır. doviz_ayri başka bir stoktur.
GIRDI = {
    "Türkiye": {
        "birim": "milyar TL",
        "stok": 8152.8,
        "stok_durum": "olcum",
        "yabanci_stok": None,
        "doviz_stok": 1745.8,
        "yerli_para_stok": 6407.0,
        "doviz_ayri": None,
        "capraz": False,
        "kagit": "",
    },
    "Japonya": {
        "birim": "trilyon yen",
        "stok": 1142.0,
        "stok_durum": "olcum",
        "yabanci_stok": 149.9,
        "doviz_stok": None,
        "yerli_para_stok": None,
        "doviz_ayri": None,
        "capraz": True,
        "kagit": "yen",
    },
    "Çin": {
        "birim": "trilyon yuan",
        "stok": 196.7,
        "stok_durum": "olcum",
        "yabanci_stok": 3.5,
        "doviz_stok": None,
        "yerli_para_stok": None,
        "doviz_ayri": None,
        "capraz": True,
        "kagit": "yuan",
    },
    "Arjantin": {
        "birim": "milyar dolar",
        "stok": 452.657,
        "stok_durum": "olcum",
        "yabanci_stok": 155.312,
        "doviz_stok": 261.753,
        "yerli_para_stok": 190.904,
        "doviz_ayri": None,
        "capraz": False,
        "kagit": "",
    },
    "Brezilya": {
        "birim": "milyar real",
        "stok": 8944.48,
        "stok_durum": "olcum",
        "yabanci_stok": None,
        "doviz_stok": None,
        "yerli_para_stok": None,
        "doviz_ayri": 348.26,
        "capraz": True,
        "kagit": "",
    },
    "Euro alanı": {
        "birim": "milyar euro",
        "stok": None,
        "stok_durum": "yok",
        "yabanci_stok": 2600.0,
        "doviz_stok": None,
        "yerli_para_stok": None,
        "doviz_ayri": None,
        "capraz": True,
        "kagit": "euro",
        "yaklasik": True,
    },
    "Güney Kore": {
        "birim": "trilyon won",
        "stok": None,
        "stok_durum": "yok",
        "yabanci_stok": 297.4,
        "doviz_stok": None,
        "yerli_para_stok": None,
        "doviz_ayri": None,
        "capraz": True,
        "kagit": "won",
    },
    "Polonya": {
        "birim": "milyar zloti",
        "stok": None,
        "stok_durum": "yok",
        "yabanci_stok": 169.6,
        "doviz_stok": None,
        "yerli_para_stok": None,
        "doviz_ayri": None,
        "capraz": True,
        "kagit": "zloti",
    },
    "Endonezya": {
        "birim": "trilyon rupiah",
        "stok": 6420.62,
        "stok_durum": "olcum",
        "yabanci_stok": 938.28,
        "doviz_stok": None,
        "yerli_para_stok": None,
        "doviz_ayri": None,
        "capraz": False,
        "kagit": "",
    },
}


def _yuvarla(x: float | None) -> float | str:
    return "" if x is None else round(x, 1)


def _payda(g: dict, yabanci_pay: float) -> tuple[float | None, str]:
    if g.get("stok") is not None:
        return g["stok"], g["stok_durum"]
    if g.get("yabanci_stok") is not None and yabanci_pay:
        durum = "yaklasik" if g.get("yaklasik") else "turev"
        return g["yabanci_stok"] / yabanci_pay, durum
    return None, "yok"


def _satir(r: dict) -> dict:
    g = GIRDI.get(r["ulke"], {})
    y = float(r["yabanci_pay"])
    d = r["doviz_pay"]
    stok, stok_durum = _payda(g, y) if g else (None, "yok")
    yabanci = g.get("yabanci_stok") if g else None
    if yabanci is None and stok is not None:
        yabanci = stok * y
        yabanci_durum = "turev"
    elif yabanci is not None:
        yabanci_durum = "yaklasik" if g.get("yaklasik") else "olcum"
    else:
        yabanci_durum = "yok"
    yerli = None if stok is None or yabanci is None else stok - yabanci

    if not g or stok is None:
        durum = "stok_yok"
        yazilan = None
    elif d is None:
        durum = "doviz_ayrilmadi"
        yazilan = None
    elif g.get("doviz_stok") is not None and not g.get("capraz"):
        durum = "capraz_yok"
        yazilan = None
    else:
        durum = "yazildi"
        yazilan = yerli

    return {
        "ulke": r["ulke"],
        "donem": r["donem"],
        "birim": g.get("birim", ""),
        "etiket": kars.etiket(y, d),
        "stok": _yuvarla(stok),
        "stok_durum": stok_durum,
        "yerli_alacakli": _yuvarla(yerli),
        "yabanci_alacakli": _yuvarla(yabanci),
        "yabanci_durum": yabanci_durum,
        "doviz_stok": _yuvarla(g.get("doviz_stok")) if g else "",
        "yerli_para_stok": _yuvarla(g.get("yerli_para_stok")) if g else "",
        "doviz_ayri": _yuvarla(g.get("doviz_ayri")) if g else "",
        "kagit": g.get("kagit", "") if g else "",
        "yazilan": _yuvarla(yazilan),
        "yazilan_durum": durum,
        "r_ic": "",
        "r_dis": "",
        "r_diger": "",
        "fatura": "",
        "fatura_durum": "modellenmedi",
        "bes_adim": "modellenmedi",
        "lam": 1 if yazilan is not None else "",
        "fark": 0 if yazilan is not None else "",
    }


def _sayi(x) -> str:
    if x == "":
        return "—"
    return f"{float(x):,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main() -> dict:
    rows = [_satir(r) for r in kars.SATIRLAR]
    alan = list(rows[0].keys())
    with (KOK / "ulke_model_dene.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=alan)
        w.writeheader()
        w.writerows(rows)
    yazilan = [r for r in rows if r["yazilan"] != ""]
    sonuc = {
        "dosya": "deneme",
        "cagri": "faiz_fatura_kalibre calismadi. bes adim kurulmadi.",
        "yazilan_n": len(yazilan),
        "fatura_n": 0,
        "satirlar": rows,
    }
    (KOK / "ulke_model_dene.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    md = [
        "# Ülke modeli denemesi",
        "",
        "Çalıştır: `python3 ulke_model_dene.py`.",
        "",
        "Ayrı dosyadır. Türkiye faiz faturası çağrılmaz. Beş adım kurulmaz. Kupon ve fatura boştur.",
        "",
        f"Yerli alacaklı stoku yazılan: **{len(yazilan)}**. Fatura hesaplanan: **0**.",
        "",
        "| Ülke | Dönem | Birim | Etiket | Stok | Yerli alacaklı | Yurt dışı | Döviz | Yazılan | Durum |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for r in rows:
        md.append(
            f"| {r['ulke']} | {r['donem']} | {r['birim'] or '—'} | {r['etiket']} | {_sayi(r['stok'])} | "
            f"{_sayi(r['yerli_alacakli'])} | {_sayi(r['yabanci_alacakli'])} | {_sayi(r['doviz_stok'])} | "
            f"{_sayi(r['yazilan'])} | {r['yazilan_durum']} |"
        )
    md += [
        "",
        "Yazılan, yerli alacaklı sütunudur. Para kırılımı ile yerleşim çaprazı olmayan satırda bu hücre boştur.",
        "Brezilya'da döviz sütunu boştur. Dış federal borç 348,3 milyar real, ayrı stoktur ve yazılana girmez.",
        "Euro alanı stoku, yaklaşık 2.600 milyar euro ve yaklaşık yüzde 23 payından türer.",
        "Güney Kore ve Polonya stoku, yayımlanan yurt dışı düzey ile paydan türer.",
        "λ=1 satırında fark 0'dır. Bu, yazılan stokun adını değiştirir. Faturayı hesaplamaz.",
        "",
        "## Ne denmez",
        "",
        "- Fatura durdu denmez. Kupon bu dosyada yoktur.",
        "- Beş adım bu ülkelerde kuruldu denmez.",
        "- Satırlar toplanmaz. Birimler ve tarihler ayrıdır.",
        "- Kâğıt cinsi, ölçülmüş döviz stoku 0 diye yazılmaz.",
        "",
    ]
    (KOK / "ULKE_MODEL_DENE.md").write_text("\n".join(md), encoding="utf-8")
    print(f"yazılan {len(yazilan)}  fatura 0")
    for r in rows:
        print(f"{r['ulke']:<12} {r['yazilan_durum']:<16} yazılan {_sayi(r['yazilan']):>10} {r['birim']}")
    return sonuc


if __name__ == "__main__":
    main()
