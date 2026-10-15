"""Yürütme maliyeti modeli (tespit + tahsil + idari), beş adıma bağlı. Girdi: adım 4 ve 5'in kendi bantları; çıktı: oran bandıyla çarpılmış maliyet.

Model: yürütme_t = program_akisi_t × ρ,  ρ = tespit + tahsil + idari payı (toplam; bileşenlere ayrılmadı).
Program akışı: adım 5'te Ho→Ha transferi (HEKİS sübvansiyonu), adım 4'te prim toplamı. Adım 1-3'te yürütülen bir akış yok: yürütme maliyeti kurgu gereği 0 (maliyet yok demek değil).
ρ bandı (varsayım, kaynaklı ama ikincil):
  alt  0,004  hedeflenmiş programlarda bireysel hedefleme idari maliyetinin alt ucu (Grosh'a atfedilen aralık 0,4%-29%; ikincil kaynak, doğrulanmadı)
  orta 0,09   aynı aralığın ortalaması (%9)
  pilot 0,25  hekis_model pilot payı (SAFETY=1,25; karar)
  üst  0,29   aynı aralığın üst ucu
Adım 4 için ρ'nun dayanağı zayıf: hedeflenmiş transfer idaresi için ölçülmüş aralık, mevduat senedi ihracı ve prim ödemesine taşınmıştır."""
import collections
import csv
from pathlib import Path

KOK = Path(__file__).resolve().parent
RHO = {"alt": 0.004, "orta": 0.09, "pilot": 0.25, "ust": 0.29}


def _oku(ad):
    return list(csv.DictReader(open(KOK / ad, encoding="utf-8-sig")))


def akis_adim4():
    """12 senaryo; prim toplamı (2029-2031, milyar TL)."""
    s = collections.defaultdict(float)
    for x in _oku("adim4_adres_yonlendirme.csv"):
        s[(float(x["theta"]), float(x["chi"]), float(x["pi"]))] += float(x["prim_ceyrek"])
    return dict(s)


def akis_adim5():
    a = {x["nesne"]: (float(x["alt"]), float(x["ust"])) for x in _oku("adim5_kira_aralik.csv")}
    return {k: a[f"Ho→Ha yıllık transfer, kapsama payı {k}%"] for k in (20, 50, 100)}


def yurutme(akis_alt, akis_ust):
    """Akış bandı × ρ bandı: {ρ adı: (alt, ust)} (milyar TL)."""
    return {ad: (akis_alt * r, akis_ust * r) for ad, r in RHO.items()}


def hepsi():
    a4 = akis_adim4()
    a5 = akis_adim5()
    out = {"1": None, "2": None, "3": None}
    out["4"] = {"akis_alt": min(a4.values()), "akis_ust": max(a4.values()), "orta_senaryo_akis": a4[(0.25, 0.5, 0.05)],
                "yurutme": yurutme(min(a4.values()), max(a4.values())),
                "yurutme_orta_senaryo": {ad: a4[(0.25, 0.5, 0.05)] * r for ad, r in RHO.items()}}
    out["5"] = {str(k): {"akis_alt": v[0], "akis_ust": v[1], "yurutme": yurutme(*v)} for k, v in a5.items()}
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(hepsi(), ensure_ascii=False, indent=1)[:1500])
