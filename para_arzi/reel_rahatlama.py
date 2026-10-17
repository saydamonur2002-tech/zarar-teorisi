"""Adım 3 net reel rahatlama, faiz uyum hızı β.

Kurallar hesap öncesi para_arzi/REEL_RAHATLAMA_YANLISLAMA.md dosyasında kilitlendi.
Δπ, enflasyon_etki.json toplam bandının iki ucudur. Sayı uydurulmaz.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

BUR = Path(__file__).resolve().parent
KRITER = BUR / "REEL_RAHATLAMA_YANLISLAMA.md"
KAYNAK = BUR / "enflasyon_etki.json"
CIKTI = BUR / "reel_rahatlama.json"
RAPOR = BUR / "REEL_RAHATLAMA.md"

I0 = 53.1925
PI0 = 29.73
BETA = (0.0, 0.5, 1.0)
KAPPA = {"dusuk": 0.25, "orta": 0.5, "yuksek": 1.0}
I_KILIT = {"dusuk": 1207.6, "orta": 2415.6, "yuksek": 4830.8}
YILLAR = ("2029", "2030", "2031")
CULE = (
    "Net reel rahatlama β = 1'de bile modelin sabit tablosundan büyükse iddia ayaktadır. "
    "β = 0,5'te küçükse iddia yanlıştır."
)


def _sha(yol: Path) -> str:
    return hashlib.sha256(yol.read_bytes()).hexdigest()


def _fiyat(dpi: float) -> float:
    return 1.0 + (PI0 + dpi) / 100.0


def i_beta(beta: float, dpi: float) -> float:
    return max(0.0, I0 + beta * dpi)


def hucre(i0_milyar: float, beta: float, dpi: float) -> dict:
    p = _fiyat(dpi)
    if p <= 0:
        return {"durum": "tanimlanamadi", "delta_pi": dpi, "beta": beta}
    oran = i_beta(beta, dpi)
    nominal = i0_milyar * oran / I0
    sabit_reel = i0_milyar / _fiyat(0.0)
    reel = nominal / p
    net = reel - sabit_reel
    return {
        "durum": "olculdu",
        "beta": beta,
        "delta_pi": dpi,
        "tanim_disi": abs(dpi) > I0,
        "hukme_girer": dpi < 0 and abs(dpi) <= I0,
        "i": oran,
        "taban_bagli": I0 + beta * dpi < 0,
        "nominal": nominal,
        "fazlalik": i0_milyar - nominal,
        "reel": reel,
        "sabit_reel": sabit_reel,
        "net": net,
        "etiket": "aday",
    }


def hukum(hucreler: list[dict]) -> dict:
    kapsam = [h for h in hucreler if h.get("hukme_girer") and h["beta"] in (0.5, 1.0) and h["durum"] == "olculdu"]
    bir = [h for h in kapsam if h["beta"] == 1.0]
    yari = [h for h in kapsam if h["beta"] == 0.5]
    yanlis = any(h["net"] < 0 for h in yari)
    ayakta = bool(bir) and all(h["net"] > 0 for h in bir)
    if yanlis:
        ad = "yanlis"
    elif ayakta:
        ad = "ayakta"
    else:
        ad = "ayakta_degil"
    return {
        "hukum": ad,
        "cumle": CULE,
        "n_beta1": len(bir),
        "n_beta05": len(yari),
        "beta1_hepsi_pozitif": ayakta,
        "beta05_herhangi_negatif": yanlis,
    }


def hesap(doc: dict) -> dict:
    if not KRITER.exists():
        raise SystemExit("kriter dosyası yok")
    satirlar = []
    for s in doc["senaryo"]:
        ad = s["ad"]
        i0_milyar = float(s["maliyet"]["I"])
        if i0_milyar != I_KILIT[ad]:
            raise SystemExit(f"I₀ kilitli değil: {ad} {i0_milyar}")
        for yil in YILLAR:
            bant = s["yil"][yil]["toplam"]
            if len(bant) != 2:
                raise SystemExit("bant iki uç değil")
            for dpi in bant:
                for beta in BETA:
                    h = hucre(i0_milyar, beta, float(dpi))
                    h.update({"senaryo": ad, "kappa": KAPPA[ad], "yil": int(yil), "I0": i0_milyar})
                    satirlar.append(h)
    out = {
        "kriter_sha256": _sha(KRITER),
        "i0": I0,
        "pi0": PI0,
        "reel_oran_kanit": I0 - PI0,
        "beta": list(BETA),
        "kappa": KAPPA,
        "cumle": CULE,
        "satirlar": satirlar,
        "hukum": hukum(satirlar),
    }
    return _yuvarla(out)


def _yuvarla(x, n=8):
    if isinstance(x, dict):
        return {k: _yuvarla(v, n) for k, v in x.items()}
    if isinstance(x, list):
        return [_yuvarla(v, n) for v in x]
    if isinstance(x, float):
        return round(x, n)
    return x


def _tr(x, n=1) -> str:
    if x is None:
        return "—"
    if isinstance(x, float) and abs(x) < 5 * 10 ** (-(n + 1)):
        x = 0.0
    s = f"{x:,.{n}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def _hukuk_yazi(ad: str) -> str:
    return {
        "ayakta": "İddia ayaktadır. Tanım içi düşüş hücrelerinin hepsinde β = 1 neti pozitiftir.",
        "yanlis": "İddia yanlıştır. Tanım içi bir düşüş hücresinde β = 0,5 neti negatiftir.",
        "ayakta_degil": "İddia ayakta değildir. β = 1 her tanım içi düşüş hücresinde tabloyu geçmez. β = 0,5 kolu da yanlışı ilan etmez.",
    }[ad]


def rapor(d: dict) -> str:
    bas = ["| Senaryo | κ | Yıl | Δπ | β | i | Nominal | Fazlalık | Reel | Net | İşaret |",
           "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |"]
    for h in d["satirlar"]:
        if h["durum"] != "olculdu":
            continue
        isaret = []
        if h["tanim_disi"]:
            isaret.append("tanım dışı")
        if not h["hukme_girer"] and h["delta_pi"] > 0:
            isaret.append("artış")
        if h["delta_pi"] == 0:
            isaret.append("sapma yok")
        if h["taban_bagli"]:
            isaret.append("taban 0")
        bas.append(
            f"| {h['senaryo']} | {_tr(h['kappa'], 2)} | {h['yil']} | {_tr(h['delta_pi'], 2)} | {_tr(h['beta'], 1)} | "
            f"{_tr(h['i'], 2)} | {_tr(h['nominal'])} | {_tr(h['fazlalik'])} | {_tr(h['reel'])} | {_tr(h['net'])} | "
            f"{', '.join(isaret) or 'tanım içi'} |"
        )
    hk = d["hukum"]
    return "\n".join([
        "# Adım 3, net reel rahatlama",
        "",
        CULE,
        "",
        "Kurallar `REEL_RAHATLAMA_YANLISLAMA.md` dosyasında kilitlendi. "
        f"Kriter özeti `{d['kriter_sha256'][:12]}`. Sonuç `adim3_faiz_durma.py` dosyasına yazılmaz.",
        "",
        "## Tanım",
        "",
        f"i₀ = {_tr(d['i0'], 4)} (**kanıt**). π₀ = {_tr(d['pi0'], 2)} (**kanıt**). "
        f"Tam Fisher reel oranı {_tr(d['reel_oran_kanit'], 4)} puanda tutar. Bu oran 0'ın üzerindedir. "
        "Nominal taban 0'dır: ticari oran eksi yazılmaz. Reel oranın kendisi nominal taban yapılmaz; o seçim, yeni enflasyon eksiye inince reel oranı Fisher'ın tuttuğu düzeyin üzerine çıkarır.",
        "",
        "i(β) = max(0, i₀ + β·Δπ). Düşüşte bu, i₀ − β·|Δπ| ile aynıdır. "
        "I(β) = I₀ · i(β) / i₀. Fazlalık = I₀ − I(β). "
        "Reel = I(β) / (1 + (π₀+Δπ)/100). Net = reel − I₀/(1+π₀/100). **Aday.**",
        "",
        "κ senaryoya kilitlidir: düşük 0,25, orta 0,5, yüksek 1. Δπ, o yılın `toplam` bandının iki ucudur.",
        "",
        "## Hüküm",
        "",
        _hukuk_yazi(hk["hukum"]) + f" Tanım içi β = 1 hücresi {hk['n_beta1']}, β = 0,5 hücresi {hk['n_beta05']}.",
        "",
        "## Tablo",
        "",
        "Milyar TL. Net pozitifse sabit-fiyat tablo reel rahatlamayı küçük yazar. Net negatifse tablo büyük yazar.",
        "",
        *bas,
        "",
        "## Halk dili",
        "",
        _halk(d),
        "",
    ])


def _halk(d: dict) -> str:
    dusus = [h for h in d["satirlar"] if h["durum"] == "olculdu" and h["hukme_girer"]]
    def yon(beta: float) -> str:
        grup = [h["net"] for h in dusus if h["beta"] == beta]
        if not grup:
            return "tanım içi düşüş hücresi yok"
        if all(x > 0 for x in grup):
            return "küçültür"
        if all(x < 0 for x in grup):
            return "büyütür"
        return "bazı hücrelerde büyütür, bazılarında küçültür"
    return (
        "Enflasyon düştüğünde faiz yerinde kalırsa (β = 0) sabit tablo reel rahatlamayı "
        f"{yon(0.0)}. Fiyatlar daha yavaş arttığı için aynı nominalin reel karşılığı büyür. "
        f"Faiz yarı uyarsa (β = 0,5) tablo rahatlamayı {yon(0.5)}. "
        f"Faiz tam uyarsa (β = 1) tablo rahatlamayı {yon(1.0)}. "
        "Yüksek senaryoda düşüşün yüzde 53,19'u aşan ucu tanım dışıdır; o uç bu cümleye girmez."
    )


def main() -> dict:
    doc = json.loads(KAYNAK.read_text(encoding="utf-8"))
    out = hesap(doc)
    CIKTI.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    RAPOR.write_text(rapor(out), encoding="utf-8")
    return out


if __name__ == "__main__":
    main()
