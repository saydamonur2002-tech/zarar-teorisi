"""Beş adımın maliyeti ve yürütme maliyeti, adım adım. Girdi: adim4_adres_yonlendirme.csv, adim5_kira_aralik.csv (kendi adım koşuları).
Çıktı: bes_adim_maliyet.csv, BES_ADIM_MALIYET.md. Yeni model değil: var olan bantların okunması.
Yürütme maliyeti (tespit, tahsil, idari) hiçbir adımda modellenmedi; tek referans hekis_model pilot payı (SAFETY = 1,25, karar)."""
import collections
import csv
from pathlib import Path

KOK = Path(__file__).resolve().parent
PILOT_PAY = 0.25  # hekis_model/hekis/pilot.py SAFETY - 1; karar, ölçüm değil


def oku(ad):
    return list(csv.DictReader(open(KOK / ad, encoding="utf-8-sig")))


def adim4():
    s = collections.defaultdict(lambda: collections.defaultdict(float))
    for x in oku("adim4_adres_yonlendirme.csv"):
        k = (float(x["theta"]), float(x["chi"]), float(x["pi"]))
        s[k]["prim"] += float(x["prim_ceyrek"])
        s[k]["kredi"] = max(s[k]["kredi"], float(x["kredi_itki_azalt_yillik"]))
        s[k]["stok"] = max(s[k]["stok"], float(x["stok"]))
    return s


def adim5():
    return {x["nesne"]: (float(x["alt"]), float(x["ust"])) for x in oku("adim5_kira_aralik.csv")}


def main():
    a4, a5 = adim4(), adim5()
    prim = [v["prim"] for v in a4.values()]
    kredi = [v["kredi"] for v in a4.values()]
    stok = [v["stok"] for v in a4.values()]
    orta = a4[(0.25, 0.5, 0.05)]
    tr = {k: a5[f"Ho→Ha yıllık transfer, kapsama payı {k}%"] for k in (20, 50, 100)}
    kira = a5["kira akışı yıllık (yol A)"]
    rows = [
        ("1", "maliyet", "yok", "", "", "milyar TL", "—", "Adım 1 stok; maliyet satırı yok."),
        ("1", "yürütme", "modellenmedi", "", "", "milyar TL", "—", "Tespit, tahsil, idari maliyet modelde yok."),
        ("2", "maliyet", "yok", "", "", "milyar TL", "—", "Temerrüt 0, parametre; maliyet satırı yok."),
        ("2", "yürütme", "modellenmedi", "", "", "milyar TL", "—", ""),
        ("3", "maliyet", "yok", "", "", "milyar TL", "—", "Kredi ihtiyacı 0; faizin durması modellenmedi."),
        ("3", "yürütme", "modellenmedi", "", "", "milyar TL", "—", ""),
        ("4", "maliyet: prim toplamı 2029-2031", "band_varsayim", f"{min(prim):.1f}", f"{max(prim):.1f}", "milyar TL", "adim4_adres_yonlendirme.csv", f"12 senaryo; orta (θ 0,25 χ 0,5 π 0,05) {orta['prim']:.1f}. Endeks bacağı hesaplanmadı: alt sınır olabilir."),
        ("4", "maliyet: kredi daralması (tepe, yıllık)", "band_varsayim", f"{min(kredi):.1f}", f"{max(kredi):.1f}", "milyar TL/yıl", "adim4_adres_yonlendirme.csv", f"Orta {orta['kredi']:.1f}. Banka mevduat kaybı × 0,08."),
        ("4", "yürütme", "modellenmedi", "", "", "milyar TL", "—", "İhraççı K′ varsayım. Prim sübvansiyon olmadığı için pilot payı uygulanmaz."),
        ("5", "maliyet: Ho→Ha transferi, kapsama %20", "band_varsayim", f"{tr[20][0]:.1f}", f"{tr[20][1]:.1f}", "milyar TL/yıl", "adim5_kira_aralik.csv", "H içi aktarım; H toplam NL 0."),
        ("5", "maliyet: Ho→Ha transferi, kapsama %50", "band_varsayim", f"{tr[50][0]:.1f}", f"{tr[50][1]:.1f}", "milyar TL/yıl", "adim5_kira_aralik.csv", ""),
        ("5", "maliyet: Ho→Ha transferi, kapsama %100", "band_varsayim", f"{tr[100][0]:.1f}", f"{tr[100][1]:.1f}", "milyar TL/yıl", "adim5_kira_aralik.csv", ""),
        ("5", "yürütme", "modellenmedi", "", "", "milyar TL/yıl", "—", "Tespit, tahsil, idari maliyet modelde yok."),
        ("5", "yürütme: ima edilen ödenek (pilot payı %25 × transfer %20-100)", "varsayim_pay", f"{PILOT_PAY*tr[20][0]:.1f}", f"{PILOT_PAY*tr[100][1]:.1f}", "milyar TL/yıl", "hekis_model pilot SAFETY=1,25", "Maliyet tahmini değil; yürütme için ayrılabilecek pay. Gerçek maliyet: tespit/tahsil/idari verisi yok."),
    ]
    with open(KOK / "bes_adim_maliyet.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["adim", "kalem", "durum", "alt", "ust", "birim", "kaynak", "not"])
        w.writerows(rows)
    L = ["# Beş adımın maliyeti ve yürütme maliyeti, adım adım", "",
         "Çalıştır: `python3 bes_adim_maliyet.py`. Çıktı: `bes_adim_maliyet.csv`. Yeni model değil: adım 4 ve 5'in kendi koşularındaki bantların okunması. Tüm sayılar varsayım bandı; ölçüm değil.", "",
         "Yürütme maliyeti = tespit + tahsil + idari maliyet. **Hiçbir adımda modellenmedi** (`hekis_model/PILOT.md`: 'tespit, tahsil ve idari maliyet modelde yok'). Repodaki tek referans pilot eşiğindeki %25 pay (bedel/sübvansiyon ≥ 1,25; karar).", ""]
    for n, ad in (("1", "stok"), ("2", "temerrüt ve ücret"), ("3", "faiz durma"), ("4", "adres yönlendirme (senet)"), ("5", "kira")):
        L += [f"## Adım {n}: {ad}", ""]
        for r in (x for x in rows if x[0] == n):
            if r[3]:
                L.append(f"- **{r[1]}**: {r[3]} – {r[4]} {r[5]} (`{r[2]}`). {r[7]}".rstrip())
            else:
                L.append(f"- **{r[1]}**: `{r[2]}`. {r[7]}".rstrip())
        L.append("")
    L += ["## Ne denmez", "",
          "- 'Yürütme maliyeti hesaplandı' denmez; satırlar `modellenmedi`. Yalnız adım 5'te pilot payına dayanan bir ödenek var (`varsayim_pay`).",
          "- Adım 4 ve 5 maliyetleri toplanmaz: biri prim ve kredi daralması, öteki hane içi aktarım.",
          "- Bantlar güven aralığı değil; varsayım aralığının uçları.", ""]
    (KOK / "BES_ADIM_MALIYET.md").write_text("\n".join(L), encoding="utf-8")
    print("BES_ADIM_MALIYET ok")


if __name__ == "__main__":
    main()
