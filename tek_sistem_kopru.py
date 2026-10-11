"""Tek sistem köprüsü: saydamonur2002-tech/tek-sistem deposunun ölçüm tablolarını bu modelin
ölçülmüş katmanlarına bağlar.

İki iş yapar:
1. Mutabakat — tek-sistem `model/pasta/Kredi_Akisi.csv` stokları (BDDK banka kredisi tanımı) ile EVDS
   konsolide olmayan finansal hesap stokları (F.4 krediler, tüm borç verenler) yan yana. Fark açıklanır,
   kapatılmaz.
2. Eşleme — RAPOR.md'deki beş adım, bu depoda hangi katmanla ölçüldü / modellendi / modellenmedi.
   Katman sonuçları birbirine taşınmaz; her satır kendi dosyasını ve dönemini gösterir.

Girdi: model/pasta/*.csv (tek-sistem c01b60a), EVDS anahtarsız uç nokta, bu depodaki *_sonuc.json.
Çıktı: tek_sistem_kopru.csv (mutabakat), tek_sistem_esleme.csv (beş adım), tek_sistem_kopru_sonuc.json,
        TEK_SISTEM_KOPRU.md, tek_sistem_kopru_ham.csv (EVDS önbellek)
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from lider_mevduat import _fetch

KOK = Path(__file__).resolve().parent
KAYNAK_REPO = "https://github.com/saydamonur2002-tech/tek-sistem"
KAYNAK_COMMIT = "c01b60a"
URL_EVDS = "https://evds3.tcmb.gov.tr/tumSeriler"

YILLAR = ("2022", "2023", "2024", "2025")
DONEMLER = tuple(f"{y}-Q4" for y in YILLAR) + ("2026-Q1",)
Q_AY = {"Q1": "03", "Q2": "06", "Q3": "09", "Q4": "12"}

# EVDS konsolide olmayan stoklar (bin TL → milyar TL _fetch içinde). Hepsi dönem sonu.
SERI_CEYREK = {
    "F_F4_yuk": "TP.FINHESTNKS11.ZP34",     # firma kredi yükümlülüğü, tüm borç verenler
    "H_F4_yuk": "TP.FINHESTNKS14.ZP34",     # hane kredi yükümlülüğü
    "B_VF4_var": "TP.FINHESTNKS122.ZP12",   # mevduat bankaları kredi varlığı
    "S12_VF4_var": "TP.FINHESTNKS12.ZP12",  # tüm finansal kuruluşlar kredi varlığı
    "F_F8_yuk": "TP.FINHESTNKS11.ZP44",     # firma diğer borçlar (ticari borç dahil)
    "F_VF8_var": "TP.FINHESTNKS11.ZP22",    # firma diğer alacaklar
    "H_vadeli": "TP.FINHESTNKS14.ZP8",
    "F_vadeli": "TP.FINHESTNKS11.ZP8",
    "H_VF2": "TP.FINHESTNKS14.ZP5",
    "F_VF2": "TP.FINHESTNKS11.ZP5",
}
SERI_AYLIK = {
    "gercek_kisi_YP": "TP.HPBITABLO2.7",    # banka mevduatı, gerçek kişi YP, TL karşılığı
}

HAM = KOK / "tek_sistem_kopru_ham.csv"


def _oku_csv(p: Path) -> dict[str, dict[str, float | None]]:
    out: dict[str, dict[str, float | None]] = {}
    with p.open(encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        yillar = [c for c in r.fieldnames if c.isdigit()]
        for row in r:
            out[row["Kalem"]] = {y: _sayi(row[y]) for y in yillar}
    return out


def _sayi(x: str | None) -> float | None:
    try:
        return float(x) if x not in ("", None) else None
    except ValueError:  # metin etiket (ör. "Spekulatif-agir")
        return None


def tek_sistem_yukle() -> dict:
    return {
        "kredi": _oku_csv(KOK / "model/pasta/Kredi_Akisi.csv"),
        "olcum": _oku_csv(KOK / "model/pasta/Olcum.csv"),
        "c1c2": _oku_csv(KOK / "model/pasta/C1C2.csv"),
    }


def evds_cek() -> dict[str, dict[str, float | None]]:
    try:
        q = _fetch(list(SERI_CEYREK.values()), "6", start="01-01-2022")
        m = _fetch(list(SERI_AYLIK.values()), "5", start="01-01-2022")
    except Exception as exc:  # noqa: BLE001 — çevrimdışıysa önceki ham dosya
        if not HAM.exists():
            raise
        print("EVDS erişilemedi, ham dosya kullanılıyor:", exc)
        return _ham_oku()
    veri: dict[str, dict[str, float | None]] = {}
    for d in DONEMLER:
        yil, ck = d.split("-")
        ay = f"{yil}-{Q_AY[ck]}"
        row: dict[str, float | None] = {k: q.get(d, {}).get(s) for k, s in SERI_CEYREK.items()}
        row.update({k: m.get(ay, {}).get(s) for k, s in SERI_AYLIK.items()})
        veri[d] = row
    with HAM.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["donem", "anahtar", "seri", "milyar_tl"])
        for d, row in veri.items():
            for k, v in row.items():
                w.writerow([d, k, {**SERI_CEYREK, **SERI_AYLIK}[k], "" if v is None else f"{v:.4f}"])
    return veri


def _ham_oku() -> dict[str, dict[str, float | None]]:
    veri: dict[str, dict[str, float | None]] = {d: {} for d in DONEMLER}
    with HAM.open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            veri.setdefault(row["donem"], {})[row["anahtar"]] = float(row["milyar_tl"]) if row["milyar_tl"] else None
    return veri


def _r(x: float | None, n: int = 1) -> float | None:
    return None if x is None else round(x, n)


def _oran(a: float | None, b: float | None) -> float | None:
    return None if (a is None or not b) else round(a / b, 3)


def mutabakat(ts: dict, ev: dict) -> list[dict]:
    """Tek-sistem BDDK kredi stokları ↔ EVDS finansal hesap stokları. Tanım farkı satır notunda."""
    k = ts["kredi"]
    rows: list[dict] = []
    esle = (
        ("Ticari stok", "F_F4_yuk", "Firma (S.11) F.4 kredi yükümlülüğü; banka + banka dışı + yurt dışı borç veren"),
        ("Bireysel stok", "H_F4_yuk", "Hane (S.14) F.4 kredi yükümlülüğü; tüketici + kart + konut + banka dışı"),
        ("Toplam kredi stoku", "B_VF4_var", "Mevduat bankaları (S.122) VF.4 kredi varlığı; tüm sektörlere, yurt dışı dahil"),
        ("Toplam kredi stoku", "S12_VF4_var", "Tüm finansal kuruluşlar (S.12) VF.4 kredi varlığı; TCMB ve banka dışı dahil"),
    )
    for d in DONEMLER:
        yil = d.split("-")[0]
        for kalem, anahtar, tanim in esle:
            tsv = k.get(kalem, {}).get(yil)
            evv = ev[d].get(anahtar)
            rows.append({
                "blok": "mutabakat", "donem": d, "kalem": kalem, "tek_sistem_milyar": _r(tsv),
                "evds_anahtar": anahtar, "evds_milyar": _r(evv),
                "fark_milyar": None if (tsv is None or evv is None) else _r(evv - tsv),
                "evds_bolu_tek": _oran(evv, tsv),
                "seri": SERI_CEYREK[anahtar], "kaynak_url": f"{URL_EVDS}/bie_finhestnks{SERI_CEYREK[anahtar].split('.')[1][10:]}",
                "not": tanim + ("; tek-sistem yıl sonu BDDK banka kredisi" if tsv is not None else "; tek-sistem değeri yok"),
            })
    # Net akış ↔ stok farkı (değerleme dahil; akış değildir)
    for i in range(1, len(YILLAR)):
        y0, y1 = YILLAR[i - 1], YILLAR[i]
        for kalem, anahtar in (("Net akis ticari", "F_F4_yuk"), ("Net akis bireysel", "H_F4_yuk"), ("Net akis toplam", "B_VF4_var")):
            tsv = k.get(kalem, {}).get(y1)
            a, b = ev[f"{y0}-Q4"].get(anahtar), ev[f"{y1}-Q4"].get(anahtar)
            fark = None if (a is None or b is None) else b - a
            rows.append({
                "blok": "akis_stok_farki", "donem": f"{y1}-Q4", "kalem": kalem, "tek_sistem_milyar": _r(tsv),
                "evds_anahtar": anahtar, "evds_milyar": _r(fark),
                "fark_milyar": None if (tsv is None or fark is None) else _r(fark - tsv),
                "evds_bolu_tek": _oran(fark, tsv),
                "seri": SERI_CEYREK[anahtar], "kaynak_url": f"{URL_EVDS}/bie_finhestnks{SERI_CEYREK[anahtar].split('.')[1][10:]}",
                "not": "EVDS sütunu Q4−Q4 stok farkıdır; kur ve değerleme içerir, net akış değildir. Tek-sistem BDDK net akış.",
            })
    return rows


def _json(p: str) -> dict:
    f = KOK / p
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def esleme(ev: dict) -> list[dict]:
    """Beş adım → bu depodaki katman. Durum: olculdu / modellendi / modellenmedi / olculmedi."""
    ms = _json("mahsup_sektor_ozet.json")
    om = _json("odeme_mahsup_sonuc.json")
    ss = _json("stok_silim_sonuc.json")
    son = DONEMLER[-1]
    e = ev[son]
    rows: list[dict] = []

    ms_son = (ms.get("donem_ozet") or [{}])[-1]
    rows.append({
        "adim": 1, "tek_sistem": "Lira alacak ve borç e-fatura üzerinden eşleşir; kapalı döngü nakit dolaşmadan kapanır",
        "katman": "mahsup_sektor_evds.py", "nesne": "sektör akış ağı, optimal_mahsup, brüt çıkış silinen oranı",
        "donem": ms_son.get("donem"), "deger": _r(ms_son.get("silinen_oran"), 3), "birim": "oran",
        "durum": "olculdu",
        "not": "Sektör düzeyi akış; bilateral e-fatura eşleşmesi değil. tek-sistem mahsuplasma paketi (mahsup/) aynı kod.",
        "dosya": "mahsup_sektor_ozet.json",
    })
    tavan = ss.get("karsi_bacak_tavan_kapi", {})
    rows.append({
        "adim": 1, "tek_sistem": "Aynı adım, stok tarafı",
        "katman": "stok_silim.py", "nesne": "araç-ayrı karşı bacak tavanı (üst sınır)",
        "donem": ss.get("donem"), "deger": _r(tavan.get("arac_ayri_oran_ust_sinir"), 4), "birim": "oran (üst sınır)",
        "durum": ss.get("H-S", "test_edilemez"),
        "not": "Stok silimi akış oranına eşitlenmez; tavan dağılım değildir. H-S araç ayrı silinen yokken skorlanmaz.",
        "dosya": "stok_silim_sonuc.json",
    })
    oz = om.get("ozet", {})
    rows.append({
        "adim": 2, "tek_sistem": "Kalan net borç silinmez; üstten alta akış planıyla ödenir; alta inen pay ücret",
        "katman": "odeme_mahsup.py", "nesne": "mahsup sonrası akış + şart kaldıracı; temerrüt sayısı",
        "donem": "2026-Q1 (sentetik 150 firma)", "deger": oz.get("temerrut_sart"), "birim": "temerrüt sayısı",
        "durum": "modellendi",
        "not": f"holding_odeme_orani {om.get('parametreler', {}).get('holding_odeme_orani')}, ucret_gecis_beta "
               f"{om.get('parametreler', {}).get('ucret_gecis_beta')}; ağ sentetik, ölçüm değil.",
        "dosya": "odeme_mahsup_sonuc.json",
    })
    rows.append({
        "adim": 3, "tek_sistem": "Akış banka kredisiyle çevrilmez; eski stokun faizi durur",
        "katman": "odeme_mahsup.py", "nesne": "kredi ihtiyacı brüt → şart",
        "donem": "2026-Q1 (sentetik 150 firma)",
        "deger": None if oz.get("kredi_ihtiyaci_sart") is None else _r(oz.get("kredi_ihtiyaci_sart"), 2),
        "birim": "trilyon TL/ay", "durum": "modellendi",
        "not": f"brüt {oz.get('kredi_ihtiyaci_brut')} → şart {oz.get('kredi_ihtiyaci_sart')}. Faizin durması modellenmedi; "
               "tek-sistem 2025 firma finansman gideri 4.300 (RAPOR.md) bu depoda ölçülmedi.",
        "dosya": "odeme_mahsup_sonuc.json",
    })
    rows.append({
        "adim": 3, "tek_sistem": "Aynı adım, kredi stoku ölçüsü",
        "katman": "tek_sistem_kopru.py", "nesne": "firma F.4 kredi yükümlülüğü (EVDS)",
        "donem": son, "deger": _r(e.get("F_F4_yuk")), "birim": "milyar TL", "durum": "olculdu",
        "not": "tek-sistem ticari stok 2025 17.302 (BDDK) ile mutabakat tablosunda karşılaştırılır.",
        "dosya": "tek_sistem_kopru.csv",
    })
    for ad, anahtar, birim in (
        ("hane vadeli mevduat (VF.2 ZP8)", "H_vadeli", "milyar TL"),
        ("firma vadeli mevduat (VF.2 ZP8)", "F_vadeli", "milyar TL"),
        ("gerçek kişi YP mevduat (HPB tablo 2)", "gercek_kisi_YP", "milyar TL (TL karşılığı)"),
    ):
        rows.append({
            "adim": 4, "tek_sistem": "Tasarruf dolar ve arsa yerine hedef primli endeksli senede gider",
            "katman": "tek_sistem_kopru.py", "nesne": ad,
            "donem": son, "deger": _r(e.get(anahtar)), "birim": birim, "durum": "olculdu",
            "not": "Senedin adresi olacak stok; senet ve prim mekanizması bu depoda modellenmedi. Altın ve arsa stoku burada yok.",
            "dosya": "tek_sistem_kopru.csv",
        })
    rows.append({
        "adim": 4, "tek_sistem": "Hedef primli endeksli senet",
        "katman": "—", "nesne": "senet ihracı, prim kaynağı, ikincil piyasa çıkışı",
        "donem": None, "deger": None, "birim": None, "durum": "modellenmedi",
        "not": "Ne ödeme zinciri ne mahsup paketi bu enstrümanı içerir.", "dosya": "",
    })
    rows.append({
        "adim": 5, "tek_sistem": "Konut topluma açılırsa kira aynı akışın ikinci kolu",
        "katman": "—", "nesne": "kira akışı", "donem": None, "deger": None, "birim": None,
        "durum": "olculmedi", "not": "tek-sistem RAPOR.md de 'Bu kol ölçülmedi' der.", "dosya": "",
    })
    return rows


def _deger_str(x) -> str:
    if x is None:
        return ""
    if isinstance(x, int):
        return str(x)
    return f"{x:,.4f}" if abs(x) < 1 else f"{x:,.1f}"


def md_yaz(mut: list[dict], esl: list[dict], ts: dict, ev: dict) -> str:
    def f(x, n=1):
        return "" if x is None else f"{x:,.{n}f}"

    s = ["# Tek sistem köprüsü", "",
         f"Kaynak: [{KAYNAK_REPO}]({KAYNAK_REPO}) `{KAYNAK_COMMIT}`; tablolar `model/gercek`, `model/pasta`, metin `model/RAPOR.md`. "
         "Mahsup kodu `mahsup/mahsuplasma` ile bayt bayt aynı (önceden eklendi).", "",
         "Çalıştır: `python3 tek_sistem_kopru.py`. Çıktı: `tek_sistem_kopru.csv` (mutabakat), `tek_sistem_esleme.csv` (beş adım), `tek_sistem_kopru_sonuc.json`.", "",
         "Kural: katman sonuçları birbirine taşınmaz. Tek-sistem sayısı BDDK banka kredisidir; EVDS sayısı finansal "
         "hesap stokudur (tüm borç verenler, yurt dışı dahil). Fark açıklanır, kapatılmaz.", "",
         "## 1. Mutabakat: kredi stoku (milyar TL, dönem sonu)", "",
         "| Dönem | Kalem | Tek-sistem | EVDS | EVDS anahtar | Fark | EVDS/tek |", "| --- | --- | ---: | ---: | --- | ---: | ---: |"]
    for r in mut:
        if r["blok"] == "mutabakat" and r["tek_sistem_milyar"] is not None:
            s.append(f"| {r['donem']} | {r['kalem']} | {f(r['tek_sistem_milyar'])} | {f(r['evds_milyar'])} | {r['evds_anahtar']} | {f(r['fark_milyar'])} | {f(r['evds_bolu_tek'], 3)} |")
    s += ["", "EVDS 2026-Q1 (tek-sistem henüz yok): " + "; ".join(
        f"{k} {f(ev['2026-Q1'].get(k))}" for k in ("F_F4_yuk", "H_F4_yuk", "B_VF4_var", "S12_VF4_var")), "",
          "Ölçüm: firma F.4 / BDDK ticari 1,29–1,36; hane F.4 / BDDK bireysel 1,06–1,12; mevduat bankaları VF.4 / BDDK toplam "
          "1,00–1,04 (dört yıl sonu). Tanım: F.4 yükümlülüğü borç vereni ayırmaz (banka, banka dışı finansal, yurt dışı); "
          "BDDK sayısı yalnız banka kredisidir. Farkın hangi borç verene ait olduğu bu seriden ayrılmaz; ayrılmadı.", "",
          "## 2. Net akış ↔ stok farkı (milyar TL)", "",
          "| Yıl | Kalem | Tek-sistem net akış | EVDS Q4−Q4 stok farkı | Fark | EVDS/tek |", "| --- | --- | ---: | ---: | ---: | ---: |"]
    for r in mut:
        if r["blok"] == "akis_stok_farki" and r["tek_sistem_milyar"] is not None:
            s.append(f"| {r['donem'][:4]} | {r['kalem']} | {f(r['tek_sistem_milyar'])} | {f(r['evds_milyar'])} | {f(r['fark_milyar'])} | {f(r['evds_bolu_tek'], 3)} |")
    s += ["", "Stok farkı kur ve değerleme içerir; net akış değildir. Konsolide olmayan akış serisi bu köprüde çekilmedi.", "",
          "## 3. Beş adım → katman", "",
          "| Adım | Tek-sistem | Katman | Nesne | Dönem | Değer | Birim | Durum |", "| ---: | --- | --- | --- | --- | ---: | --- | --- |"]
    for r in esl:
        s.append(f"| {r['adim']} | {r['tek_sistem']} | `{r['katman']}` | {r['nesne']} | {r['donem'] or ''} | "
                 f"{_deger_str(r['deger'])} | {r['birim'] or ''} | {r['durum']} |")
    s += ["", "Notlar:", ""]
    for r in esl:
        s.append(f"- Adım {r['adim']} / {r['nesne']}: {r['not']}" + (f" (`{r['dosya']}`)" if r["dosya"] else ""))
    ol = ts["olcum"]
    s += ["", "## 4. Tek-sistem'in kendi ölçüsü (taşınmadı, yan yana)", "",
          f"- Kopma payı 2025: {f(ol.get('Kopma payi', {}).get('2025'), 4)}; hipotez {f(ol.get('Hipotez', {}).get('2025'), 2)} "
          f"(`model/pasta/Olcum.csv`). Bu depoda kopma payı tanımı yok; eşlenmez.",
          f"- Bireysel stok 2025: {f(ts['c1c2'].get('Bireysel stok milyar', {}).get('2025'))}; C2 payı "
          f"{f(ts['c1c2'].get('C2 payi', {}).get('2025'), 3)} (`model/pasta/C1C2.csv`). `hane_taksit.py` kartı orana almaz; birleştirilmez.", "",
          "## Ne denmez", "",
          "- 'Mahsup kredi stokunu şu kadar düşürür' denmez; stok tavanı üst sınırdır, akış oranı ayrı nesnedir.",
          "- 'Tasarruf senede gider' denmez; adres stokları ölçüldü, senet modellenmedi.",
          "- Tek-sistem BDDK sayısı ile EVDS sayısı aynı stok değildir; biri diğerine düzeltilmez."]
    return "\n".join(s) + "\n"


def main() -> None:
    ts = tek_sistem_yukle()
    ev = evds_cek()
    mut = mutabakat(ts, ev)
    esl = esleme(ev)

    alanlar = ["blok", "donem", "kalem", "tek_sistem_milyar", "evds_anahtar", "evds_milyar", "fark_milyar", "evds_bolu_tek", "seri", "kaynak_url", "not"]
    with (KOK / "tek_sistem_kopru.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=alanlar)
        w.writeheader()
        for r in mut:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in alanlar})
    alan_e = ["adim", "tek_sistem", "katman", "nesne", "donem", "deger", "birim", "durum", "not", "dosya"]
    with (KOK / "tek_sistem_esleme.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=alan_e)
        w.writeheader()
        for r in esl:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in alan_e})

    sonuc = {
        "kaynak_repo": KAYNAK_REPO, "kaynak_commit": KAYNAK_COMMIT,
        "mahsup_kodu": "mahsup/mahsuplasma == tek-sistem-mahsup.zip (bayt bayt aynı)",
        "donemler": list(DONEMLER),
        "evds": {d: {k: _r(v) for k, v in row.items()} for d, row in ev.items()},
        "mutabakat": mut, "esleme": esl,
        "kural": "katman sonuçları taşınmaz; BDDK ve EVDS farkı açıklanır, kapatılmaz",
    }
    (KOK / "tek_sistem_kopru_sonuc.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (KOK / "TEK_SISTEM_KOPRU.md").write_text(md_yaz(mut, esl, ts, ev), encoding="utf-8")

    print("=== Tek sistem köprüsü ===")
    for r in mut:
        if r["blok"] == "mutabakat" and r["tek_sistem_milyar"] is not None and r["donem"].startswith("2025"):
            print(f"{r['donem']} {r['kalem']:<20} tek {r['tek_sistem_milyar']:>10,.1f}  evds {r['evds_milyar']:>10,.1f}  {r['evds_anahtar']:<12} oran {r['evds_bolu_tek']}")
    for r in esl:
        print(f"adım {r['adim']} {r['durum']:<14} {r['katman']:<22} {r['nesne']} = {r['deger']}")


if __name__ == "__main__":
    main()
