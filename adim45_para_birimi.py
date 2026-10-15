"""Adım 4.5: yeni para birimine geçiş, plasebo (adım 4 ile 5 arası).

Plasebo: tüm TL değerleri sabit bir oranla yeni birime çevrilir; gerçek hiçbir şey değişmez. Modelde bunun karşılığı: birimsiz çıktılar (oranlar) aynı kalır,
parasal çıktılar yalnız ölçek alır. Test: adım 1-5 çıktılarından oran ve parasal kalemler alınır, s ile çevrilir, oranlar yeniden hesaplanır, eşitlik aranır.
Bu denklik aritmetik gereğidir (kurgu): modelde para yanılsaması, yuvarlama enflasyonu, fiyat belirleme alışkanlıkları yoktur; bu yüzden etki tanım gereği sıfırdır.
Tek gerçek terim: yürütme maliyeti.

Maliyet iki rejimle (milyar TL, tek sefer):
  A sıfır atma (YTL 2005 türü): banknot basımı ≈ 10 milyon $ (2004 tahmini, Hürriyet; 'ek maliyet değil' denmişti) + kurum başı yazılım 20-100 bin $ (TCMB Başkan Yardımcısı aktarımı) × kurum sayısı N (bilinmiyor; 100-1.000 varsayım).
  B yeni para birimi (euro türü tam değişim): GSYH'nin %0,3-1,0'ı (Avro bölgesine girenlerde ort. %0,3-0,5, Litvanya %0,5-0,7, Hırvatistan %0,5-1; ikincil kaynak, doğrulanmadı). Muhalif/kampanya kaynaklı %4,4 (Birleşik Krallık) kullanılmaz.
Üç dönüşüm kuralı (kullanıcı: "1 TL => 1 YTL veya sabit tutulmuş bir çapa, sonra geçiş"):
  1) başa baş (1 yeni = 1 eski, s=1): yalnız ad/etiket değişir; sıfır atılmaz.
  2) sıfır atma (YTL 2005: 1 yeni = 1.000.000 eski): s=1e-6.
  3) sabit çapa (1 yeni = 1 çapa birimi, örnek ABD doları, kur 32,87): s=1/32,87; sonra geçiş (çift dolaşım dönemi).
Maliyet eşlemesi: 1 → yalnız yazılım/etiket (A'nın yazılım terimi); 2 → A; 3 → B (yuvarlak olmayan çarpan, çift gösterim/dolaşım; avro türü). Çapanın savunma maliyeti (rezerv) modellenmedi.
GSYH ve kur: etki cephesi paketi gerceklik_capa.json (2024): 44.587.225,44 milyon TL; 32,87 TL/$."""
import csv
from pathlib import Path

KOK = Path(__file__).resolve().parent
S = 1 / 1000  # 1 yeni birim = 1.000 eski TL (örnek)
KURALLAR = {"basa_bas": 1.0, "sifir_atma": 1e-6, "sabit_capa": None}  # sabit_capa: 1/KUR (KUR aşağıda)
GSYH_MLR_TL = 44587.22544
KUR = 32.87
BANKNOT_MN_USD = 10.0
YAZILIM_USD = (20_000, 100_000)
KURUM_N = (100, 1000)  # varsayım
B_ORAN = (0.003, 0.010)
KURALLAR["sabit_capa"] = 1 / KUR


def _oku(ad):
    return list(csv.DictReader(open(KOK / ad, encoding="utf-8-sig")))


def kalemler():
    """(adım, ad, değer, tür) tür: 'para' (milyar TL ya da TL) veya 'oran' (birimsiz). Değerler adım koşularından okunur."""
    out = []
    for x in _oku("adim1_stok.csv"):
        if x["cift"] == "TOPLAM":
            out += [("1", "ortak stok", float(x["ortak_stok"]), "para"), ("1", "brüt stok", float(x["brut"]), "para")]
    ag = _oku("adim2_nace_ag.csv")[0]
    out += [("2", "silinen", float(ag["silinen_milyar"]), "para"), ("2", "kredi ihtiyacı brüt", float(ag["kredi_ihtiyaci_brut"]), "para")]
    d3 = [x for x in _oku("adim3_faiz_durma.csv") if x["donem"].startswith("2029") and float(x["kappa"]) == 0.5]
    out += [("3", "duran faiz 2029 κ=0,5", sum(float(x["duran_faiz_etkin_milyar"]) for x in d3), "para"), ("3", "durdurulan stok S0", 25339.8, "para")]
    a4 = _oku("adim4_adres_yonlendirme.csv")
    out += [("4", "adres toplamı", 19361.9, "para"), ("4", "prim toplamı (θ0,25 χ0,5 π0,05)", sum(float(x["prim_ceyrek"]) for x in a4 if (float(x["theta"]), float(x["chi"]), float(x["pi"])) == (0.25, 0.5, 0.05)), "para")]
    a5 = {x["nesne"]: float(x["alt"]) for x in _oku("adim5_kira_aralik.csv")}
    out += [("5", "HEKİS havuz kirası TL/ay", a5["HEKİS havuz kirası"], "para"), ("5", "aylık piyasa kirası alt TL/ay", a5["aylık piyasa kirası (kiracı başına)"], "para")]
    return out


def oranlar(k):
    """Birimsiz oranlar: parasal kalemlerin oranları (çevrilen ve çevrilmeyen aynı olmalı)."""
    d = {(a, n): v for a, n, v, t in k}
    return {
        "ortak/brüt (adım 1)": d[("1", "ortak stok")] / d[("1", "brüt stok")],
        "silinen/kredi ihtiyacı (adım 2)": d[("2", "silinen")] / d[("2", "kredi ihtiyacı brüt")],
        "duran faiz/S0 (adım 3)": d[("3", "duran faiz 2029 κ=0,5")] / d[("3", "durdurulan stok S0")],
        "prim/adres (adım 4)": d[("4", "prim toplamı (θ0,25 χ0,5 π0,05)")] / d[("4", "adres toplamı")],
        "HEKİS/piyasa kira (adım 5)": d[("5", "HEKİS havuz kirası TL/ay")] / d[("5", "aylık piyasa kirası alt TL/ay")],
    }


def cevir(k, s=S):
    return [(a, n, v * s if t == "para" else v, t) for a, n, v, t in k]


def maliyet():
    a_basim = BANKNOT_MN_USD * KUR / 1000  # milyar TL
    a_yaz = (YAZILIM_USD[0] * KURUM_N[0] * KUR / 1e9, YAZILIM_USD[1] * KURUM_N[1] * KUR / 1e9)
    A = (a_basim + a_yaz[0], a_basim + a_yaz[1])
    B = (B_ORAN[0] * GSYH_MLR_TL, B_ORAN[1] * GSYH_MLR_TL)
    return {"A_basim": a_basim, "A_yazilim": a_yaz, "A": A, "B": B}


def kural_maliyet():
    c = maliyet()
    return {"basa_bas": c["A_yazilim"], "sifir_atma": c["A"], "sabit_capa": c["B"]}


def main():
    k = kalemler()
    o0, o1 = oranlar(k), oranlar(cevir(k))
    fark = {a: abs(o0[a] - o1[a]) for a in o0}
    kural_fark = {ad: max(abs(o0[a] - oranlar(cevir(k, s))[a]) for a in o0) for ad, s in KURALLAR.items()}
    c = maliyet()
    rows = [["4.5", "plasebo: oran değişimi", "max |Δoran|", f"{max(fark.values()):.2e}", "", "birimsiz", "adim45_para_birimi.py", "s=1/1000; denklik aritmetik gereği (kurgu)."]]
    for a, v in o0.items():
        rows.append(["4.5", f"oran: {a}", "oran", f"{v:.6f}", f"{o1[a]:.6f}", "birimsiz", "adim45_para_birimi.py", "çevirmeden önce / sonra"])
    rows += [["4.5", "maliyet A: sıfır atma (basım + yazılım)", "modellendi_band", f"{c['A'][0]:.2f}", f"{c['A'][1]:.2f}", "milyar TL (tek sefer)", "adim45_para_birimi.py", f"Basım {c['A_basim']:.2f}; yazılım {c['A_yazilim'][0]:.2f}-{c['A_yazilim'][1]:.2f} (N=100-1.000 varsayım)."],
             ["4.5", "maliyet B: yeni para birimi (GSYH %0,3-1,0)", "modellendi_band", f"{c['B'][0]:.1f}", f"{c['B'][1]:.1f}", "milyar TL (tek sefer)", "adim45_para_birimi.py", "Avro bölgesine girenlerde bildirilen aralık; ikincil kaynak."]]
    kural_maliyet = {"basa_bas": c["A_yazilim"], "sifir_atma": c["A"], "sabit_capa": c["B"]}
    for ad, s in KURALLAR.items():
        rows.append(["4.5", f"kural {ad}: s={s:.3g}", "modellendi_band", f"{kural_maliyet[ad][0]:.2f}", f"{kural_maliyet[ad][1]:.2f}", "milyar TL (tek sefer)", "adim45_para_birimi.py", f"max |Δoran|={kural_fark[ad]:.1e}"])
    with open(KOK / "adim45.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["adim", "kalem", "durum", "alt", "ust", "birim", "kaynak", "not"])
        w.writerows(rows)
    L = ["# Adım 4.5: yeni para birimine geçiş (plasebo)", "",
         "Çalıştır: `python3 adim45_para_birimi.py`. Çıktı: `adim45.csv`. Adım 4 ile 5 arasında; adım 4 çıktısını okur, adım 5 girdisine dokunmaz.", "",
         "## Plasebo ne demek", "",
         "Tüm TL değerleri sabit bir oranla (örnek: 1 yeni birim = 1.000 eski TL) yeni birime çevrilir; gerçek bir şey değişmez. Modelde bunun karşılığı: oranlar aynı kalır, parasal kalemler yalnız ölçek alır. "
         f"Adım 1-5 çıktılarından beş oran çevirmeden önce ve sonra hesaplandı; en büyük fark {max(fark.values()):.1e} (kayan nokta düzeyi). Bu denklik **aritmetik gereğidir**: modelde para yanılsaması, yuvarlama enflasyonu veya fiyat belirleme alışkanlığı yok, dolayısıyla etki tanım gereği sıfırdır. Gerçekte bu terimler vardır ve yeni para birimi plasebo olmayabilir; model bunu ölçmez.", "",
         "| Oran | Çevirmeden önce | Sonra |", "| --- | ---: | ---: |"]
    L += [f"| {a} | {v:.6f} | {o1[a]:.6f} |" for a, v in o0.items()]
    L += ["", "## Üç dönüşüm kuralı ve maliyeti (milyar TL, tek sefer)", "",
          "| Kural | Çevirme oranı s | max \\|Δoran\\| | Maliyet alt – üst | Eşleme |", "| --- | ---: | ---: | ---: | --- |"]
    esl = {"basa_bas": "yalnız yazılım/etiket (A'nın yazılım terimi)", "sifir_atma": "A: basım + yazılım", "sabit_capa": "B: yuvarlak olmayan çarpan, çift dolaşım (avro türü)"}
    for ad, s in KURALLAR.items():
        L.append(f"| {ad} | {s:.3g} | {kural_fark[ad]:.1e} | {kural_maliyet[ad][0]:.2f} – {kural_maliyet[ad][1]:.2f} | {esl[ad]} |")
    L += ["", "Sabit çapa kuralında 1 yeni birim = 1 çapa birimidir (örnek ABD doları, kur 32,87); 'sonra geçiş' çift dolaşım dönemidir ve B maliyetine eşlenmiştir. Çapanın savunma maliyeti (rezerv, faiz) modellenmedi: çapa kuralı plasebo değildir, sabit kur rejimi gerçek bir kısıttır; burada yalnız birim dönüşümü plasebo sayılır.", "",
          "## Tek gerçek terim: yürütme maliyeti (milyar TL, tek sefer)", "",
          f"- **A. Sıfır atma (YTL 2005 türü):** {c['A'][0]:.2f} – {c['A'][1]:.2f}. Banknot basımı ≈ 10 milyon $ (2004 tahmini, Hürriyet; 'ek maliyet değil' denmişti) = {c['A_basim']:.2f} milyar TL (kur 32,87); yazılım kurum başına 20–100 bin $ (TCMB Başkan Yardımcısı aktarımı), kurum sayısı N bilinmiyor, 100–1.000 varsayım: {c['A_yazilim'][0]:.2f} – {c['A_yazilim'][1]:.2f} milyar TL.",
          f"- **B. Yeni para birimi (euro türü tam değişim):** GSYH'nin %0,3–1,0'ı = {c['B'][0]:.1f} – {c['B'][1]:.1f} milyar TL (GSYH 2024: 44.587,2 milyar TL). Avro bölgesine girenlerde ortalama %0,3–0,5, Litvanya %0,5–0,7, Hırvatistan %0,5–1 (bir Bulgaristan analizinde aktarılan, ikincil kaynak, doğrulanmadı). Birleşik Krallık için kampanya kaynaklı %4,4 kullanılmadı.", "",
          "Fayda sıfır (plasebo), maliyet pozitif: net etki = −maliyet. Adım 4 ve 5 ile toplanmaz (tek seferlik; öteki adımlar akış ve stok).", "",
          "## Ne denmez", "",
          "- 'Yeni para birimi bir şey değiştirmez' denmez; model değiştirmediğini varsayar, sınamaz.",
          "- 'Geçiş maliyeti ölçüldü' denmez; A rejimi 2004 tahmini ve kurum sayısı varsayımı, B rejimi başka ülkelerin ikincil aktarımı.",
          "- Yuvarlama, para yanılsaması ve fiyat belirleme alışkanlıkları modellenmedi; gerçek plasebo ihlali bu kanallardan gelir.", ""]
    (KOK / "ADIM45_PARA_BIRIMI.md").write_text("\n".join(L), encoding="utf-8")
    print("ADIM45 ok", max(fark.values()))


if __name__ == "__main__":
    main()
