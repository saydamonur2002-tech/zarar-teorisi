"""Yürütme maliyeti modeli (tespit + tahsil + idari), beş adıma bağlı. Girdi: adım 4 ve 5'in kendi bantları; çıktı: oran bandıyla çarpılmış maliyet.

Model: yürütme_t = program_akisi_t × ρ,  ρ = tespit + tahsil + idari payı (toplam; bileşenlere ayrılmadı).
Program akışı: adım 1'de ortak stok (silinebilecek üst sınır), adım 2'de mahsupla silinen tutar (Faz 2 düğümlü ağ), adım 3'te yıllık duran faiz (Faz 3), adım 4'te prim toplamı, adım 5'te Ho→Ha transferi (HEKİS sübvansiyonu).
Adım 1 ve 2'de akış bir STOK (tek seferlik temizleme/mahsup), adım 3 ve 5'te yıllık akış, adım 4'te 2029-2031 toplamı: birimler karıştırılmaz.
ρ bandı (varsayım, kaynaklı ama ikincil):
  alt  0,004  hedeflenmiş programlarda bireysel hedefleme idari maliyetinin alt ucu (Grosh'a atfedilen aralık 0,4%-29%; ikincil kaynak, doğrulanmadı)
  orta 0,09   aynı aralığın ortalaması (%9)
  pilot 0,25  hekis_model pilot payı (SAFETY=1,25; karar)
  üst  0,29   aynı aralığın üst ucu
Adım 1, 2 (stok mahsubu) ve 4 (senet) için ρ'nun dayanağı zayıf: hedeflenmiş transfer idaresi aralığı bu işlere taşınmıştır. Stok mahsubunda (adım 1, 2) yalnız alt uç (%0,4) kullanılır: %9 ve üstü ρ, ortak stoka uygulandığında 1.800-5.900 milyar TL gibi gerçekçi olmayan tutarlar verir (temizleme maliyeti stokla orantılı değildir). Kullanılan değer üst sınırdır."""
import collections
import csv
from pathlib import Path

KOK = Path(__file__).resolve().parent
RHO = {"alt": 0.004, "orta": 0.09, "pilot": 0.25, "ust": 0.29}
RHO_STOK = {"alt": RHO["alt"]}  # stok mahsubu (adım 1, 2): yalnız alt uç; üst oranlar gerçekçi değil (bkz. docstring)


def _oku(ad):
    return list(csv.DictReader(open(KOK / ad, encoding="utf-8-sig")))


def akis_adim4():
    """12 senaryo; prim toplamı (2029-2031, milyar TL)."""
    s = collections.defaultdict(float)
    for x in _oku("adim4_adres_yonlendirme.csv"):
        s[(float(x["theta"]), float(x["chi"]), float(x["pi"]))] += float(x["prim_ceyrek"])
    return dict(s)


def akis_adim1():
    """Ortak stok (milyar TL; adım 1 TOPLAM satırı): silinebilecek üst sınır. Silinen tutar boş (kimden-kime tablosu yok)."""
    for x in _oku("adim1_stok.csv"):
        if x["cift"] == "TOPLAM":
            return float(x["ortak_stok"])
    raise ValueError("adim1_stok.csv TOPLAM satırı yok")


def akis_adim2():
    """Mahsupla silinen tutar (milyar TL; adim2_nace_ag.csv, tüm satırlarda aynı)."""
    v = {round(float(x["silinen_milyar"]), 1) for x in _oku("adim2_nace_ag.csv")}
    assert len(v) == 1, v
    return v.pop()


def akis_adim3():
    """Yıllık duran faiz, etkin (milyar TL/yıl; 2029 = sürekli rejim yılı), κ başına."""
    s = collections.defaultdict(float)
    for x in _oku("adim3_faiz_durma.csv"):
        if x["donem"].startswith("2029"):
            s[float(x["kappa"])] += float(x["duran_faiz_etkin_milyar"])
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
    out = {}
    a1, a2, a3 = akis_adim1(), akis_adim2(), akis_adim3()
    out["1"] = {"akis": a1, "yurutme": {ad: a1 * r for ad, r in RHO_STOK.items()}, "uygulanmaz": {ad: a1 * r for ad, r in RHO.items() if ad not in RHO_STOK}}
    out["2"] = {"akis": a2, "yurutme": {ad: a2 * r for ad, r in RHO_STOK.items()}, "uygulanmaz": {ad: a2 * r for ad, r in RHO.items() if ad not in RHO_STOK}}
    out["3"] = {str(k): {"akis": v, "yurutme": {ad: v * r for ad, r in RHO.items()}} for k, v in sorted(a3.items())}
    out["4"] = {"akis_alt": min(a4.values()), "akis_ust": max(a4.values()), "orta_senaryo_akis": a4[(0.25, 0.5, 0.05)],
                "yurutme": yurutme(min(a4.values()), max(a4.values())),
                "yurutme_orta_senaryo": {ad: a4[(0.25, 0.5, 0.05)] * r for ad, r in RHO.items()}}
    out["5"] = {str(k): {"akis_alt": v[0], "akis_ust": v[1], "yurutme": yurutme(*v)} for k, v in a5.items()}
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(hepsi(), ensure_ascii=False, indent=1)[:1500])
