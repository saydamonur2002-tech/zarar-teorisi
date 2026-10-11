"""Enflasyon tavanı, işlem akımı: kredi itişinin fiyata geçen parçası.

Tanım: itiş = firma (S.11) F.4 kredi işlem akımı, dört çeyrek toplamı (konsolide olmayan AKIM). Stok farkı
değildir; stok farkı aynı tabloda ayrı sütundur, eşitlenmez. Geçiş payı ölçülmeden yazılmaz; 1/3 kullanılmaz.
Tavan = itiş × geçiş; geçiş yoksa tavan boş. "2,5 puan" yalnız referans notunda durur.

Girdi: EVDS TP.FINHESTNKS62011.ZP34 (akım), TP.FINHESTNKS11.ZP34 (stok), TP.GSYIH20.BY.B1GQ (GSYH, cari).
Adım 1 etiketi ve stok tavanı 0,0728 bu dosyaya girmez.
Çıktı: tavan_akis.csv (yil, f4_akim, stok_fark, gsyh, oran_akim, oran_stok, gecis, tavan, durum, seri),
       tavan_akis_sonuc.json, TAVAN_AKIS.md, tavan_akis_ham.csv
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from lider_mevduat import _fetch

KOK = Path(__file__).resolve().parent
YILLAR = ("2023", "2024", "2025")
S_AKIM = "TP.FINHESTNKS62011.ZP34"
S_STOK = "TP.FINHESTNKS11.ZP34"
S_GSYH = "TP.GSYIH20.BY.B1GQ"
URL = {
    S_AKIM: "https://evds3.tcmb.gov.tr/tumSeriler/bie_finhestnks62011",
    S_STOK: "https://evds3.tcmb.gov.tr/tumSeriler/bie_finhestnks11",
    S_GSYH: "https://evds3.tcmb.gov.tr/tumSeriler/bie_gsyhhrccar",
}
HAM = KOK / "tavan_akis_ham.csv"

# RAPOR.md (tek-sistem c01b60a) referans cümlesi; sonuç sütununa geçmez.
REFERANS = {"ticari_net_akis": 5208.0, "gsyh": 63021.0, "oran_yuzde": 8.3, "gecis_varsayim": "üçte biri", "puan": 2.5}

# Geçiş payı için birincil arama kaydı. Her satır: nerede, ne, sonuç.
GECIS_ARAMA = [
    ("EVDS katalog (evds_katalog_gruplar.json, 680 grup)", "'çıktı açığı' / 'cikti acigi'", "0 grup; TCMB çıktı açığı Enflasyon Raporu grafiğidir, EVDS serisi yok"),
    ("EVDS katalog", "'geçiş' / 'geçişkenlik' (kredi→fiyat)", "0 grup; kur geçişkenliği serisi de yok"),
    ("EVDS katalog", "fiyat: TÜFE (bie_tukfiy2025), Yİ-ÜFE (bie_tufe1yi), H-ÜFE (bie_hufe)", "endeks var; kredi itişinin fiyata geçen payı değil, katsayı değil"),
    ("EVDS katalog", "beklenti/anket: Piyasa Katılımcıları, Sektörel, Hanehalkı; KKO; Banka Kredileri Eğilim", "var; geçiş payı vermez"),
    ("Depo", "odeme_enf_sonuc.json, odeme_enf.py", "sentetik ağ; 'Sayılar ölçüm değildir' (dosya uyarısı); kullanılmaz"),
    ("Depo", "OKU.txt 'gecis'", "TGA geçiş hızı; fiyat geçişi değil"),
    ("tek-sistem RAPOR.md", "'Fiyata üçte biri geçse'", "varsayım cümlesi, kaynak yok; `varsayim`, tavan diye durmaz"),
]


def cek() -> dict[str, dict[str, float | None]]:
    try:
        q = _fetch([S_AKIM, S_STOK, S_GSYH], "6", start="01-01-2022", end="10-10-2026")
    except Exception as exc:  # noqa: BLE001
        if not HAM.exists():
            raise
        print("EVDS erişilemedi, ham dosya:", exc)
        q = {}
        with HAM.open(encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                q.setdefault(r["donem"], {})[r["seri"]] = float(r["milyar_tl"])
        return q
    with HAM.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["donem", "seri", "milyar_tl"])
        for d in sorted(q):
            for s, v in q[d].items():
                w.writerow([d, s, f"{v:.4f}"])
    return q


def yillik(q: dict) -> list[dict]:
    rows = []
    for y in YILLAR:
        ceyrek = [q.get(f"{y}-Q{i}", {}) for i in range(1, 5)]
        akim = [c.get(S_AKIM) for c in ceyrek]
        gsyh = [c.get(S_GSYH) for c in ceyrek]
        f4_akim = sum(akim) if all(a is not None for a in akim) else None
        g = sum(gsyh) if all(a is not None for a in gsyh) else None
        s1, s0 = q.get(f"{y}-Q4", {}).get(S_STOK), q.get(f"{int(y) - 1}-Q4", {}).get(S_STOK)
        stok_fark = None if (s1 is None or s0 is None) else s1 - s0
        oran_akim = None if (f4_akim is None or not g) else 100.0 * f4_akim / g
        oran_stok = None if (stok_fark is None or not g) else 100.0 * stok_fark / g
        rows.append({
            "yil": y,
            "f4_akim": None if f4_akim is None else round(f4_akim, 1),
            "stok_fark": None if stok_fark is None else round(stok_fark, 1),
            "gsyh": None if g is None else round(g, 1),
            "oran_akim": None if oran_akim is None else round(oran_akim, 2),
            "oran_stok": None if oran_stok is None else round(oran_stok, 2),
            "gecis": None,   # birincil bulunamadı; 1/3 yazılmaz
            "tavan": None,   # geçiş yok → boş
            "durum": "itis_olculdu; gecis_bulunamadi; tavan_bos" if f4_akim is not None else "itis_eksik_ceyrek",
            "seri": f"{S_AKIM}; {S_STOK}; {S_GSYH}",
        })
    return rows


def etiketler(rows: list[dict]) -> dict:
    r25 = next(r for r in rows if r["yil"] == "2025")
    if r25["oran_stok"] is None or r25["oran_akim"] is None:
        ht = "test_edilemez"
    elif abs(r25["oran_stok"] - r25["oran_akim"]) < 0.005:
        ht = "ayni"
    else:
        ht = "siser" if r25["oran_stok"] > r25["oran_akim"] else "dusurur"
    gecis_var = any(r["gecis"] is not None for r in rows)
    ht2 = "olculdu" if (gecis_var and r25["f4_akim"] is not None) else "test_edilemez"
    return {
        "H-T": ht,
        "H-T_not": f"2025 oran_stok {r25['oran_stok']} vs oran_akim {r25['oran_akim']} (yüzde GSYH); fark {None if ht == 'test_edilemez' else round(r25['oran_stok'] - r25['oran_akim'], 2)} puan. "
                   "RAPOR'un yüzde 8,3'ü stok farkıyla kurulmuştur.",
        "H-T2": ht2,
        "H-T2_not": "geçiş payı birincil bulunamadı; tavan boş; 2,5 puan lehte yazılmaz" if ht2 == "test_edilemez" else "itiş × geçiş yazıldı",
    }


def md(rows: list[dict], et: dict) -> str:
    def f(x, n=1):
        return "" if x is None else f"{x:,.{n}f}"

    s = ["# Enflasyon tavanı, işlem akımı", "",
         "Çalıştır: `python3 tavan_akis.py`. Çıktı: `tavan_akis.csv`, `tavan_akis_sonuc.json`.", "",
         "Tanım: tavan = kredi itişinin fiyata geçen parçası. İtiş = firma F.4 **işlem akımı** (dört çeyrek toplamı), stok farkı değil. "
         "Geçiş payı ölçülmeden yazılmaz; 1/3 kullanılmaz. Adım 1 etiketi ve stok tavanı bu dosyaya girmez.", "",
         "## 1. Üç yıl: itiş (akım) ve stok farkı ayrı (milyar TL; oranlar yüzde GSYH)", "",
         "| Yıl | F.4 işlem akımı | Stok farkı Q4−Q4 | GSYH (cari) | Oran akım | Oran stok | Geçiş | Tavan | Durum |",
         "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |"]
    for r in rows:
        s.append(f"| {r['yil']} | {f(r['f4_akim'])} | {f(r['stok_fark'])} | {f(r['gsyh'])} | {f(r['oran_akim'], 2)} | {f(r['oran_stok'], 2)} | "
                 f"{f(r['gecis'], 3)} | {f(r['tavan'], 2)} | {r['durum']} |")
    s += ["", f"Seriler: akım `{S_AKIM}` (konsolide olmayan, işlem, sum), stok `{S_STOK}` (konsolide olmayan, last), GSYH `{S_GSYH}` (harcama, cari, 4 çeyrek). "
          "Stok farkı kur ve değerleme içerir; akım sütunuyla eşitlenmez. Buradaki stok farkı EVDS firma F.4'tür (tüm borç verenler); "
          "RAPOR'un 5.208'i BDDK ticari stok farkıdır (yalnız banka) — ikisi de stok farkı, ikisi de akım değil.", "",
          "## 2. Geçiş payı: birincil arama", "", "| Nerede | Ne | Sonuç |", "| --- | --- | --- |"]
    for a, b, c in GECIS_ARAMA:
        s.append(f"| {a} | {b} | {c} |")
    s += ["", f"Sonuç: geçiş payı **bulunamadı**, {len(GECIS_ARAMA)} arama denendi. Geçiş sütunu boş; tavan sütunu boş.", "",
          "## 3. Yanlışlayıcılar", "",
          f"- **H-T** (stok farkı tavanı şişirir): `{et['H-T']}`. {et['H-T_not']}",
          f"- **H-T2** (tavan kurulur): `{et['H-T2']}`. {et['H-T2_not']}", "",
          "## 4. Referans notu (sonuç sütununa geçmez)", "",
          f"tek-sistem RAPOR.md (c01b60a): ticari net akış {REFERANS['ticari_net_akis']:,.0f} / milli gelir {REFERANS['gsyh']:,.0f} = yüzde {REFERANS['oran_yuzde']}; "
          f"'fiyata {REFERANS['gecis_varsayim']} geçse' yaklaşık {REFERANS['puan']} puan. 5.208 stok farkıdır (`TEK_SISTEM_KOPRU.md` 9/9). "
          "'Üçte biri' `varsayim`; tavan diye durmaz.", "",
          "## Ne denmez", "",
          "- 'Enflasyon 2,5 puan iner' denmez. İtiş şu, geçiş ölçülmedi, tavan boş.",
          "- Stok farkı akım diye kullanılmaz.",
          "- Oran akım, oran stokun yerine 'doğru tavan' diye de yazılmaz; geçiş olmadan ikisi de tavan değildir."]
    return "\n".join(s) + "\n"


def main() -> None:
    q = cek()
    rows = yillik(q)
    et = etiketler(rows)
    alan = ["yil", "f4_akim", "stok_fark", "gsyh", "oran_akim", "oran_stok", "gecis", "tavan", "durum", "seri"]
    with (KOK / "tavan_akis.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=alan)
        w.writeheader()
        for r in rows:
            w.writerow({a: ("" if r[a] is None else r[a]) for a in alan})
    (KOK / "tavan_akis_sonuc.json").write_text(json.dumps({
        "tanim": "tavan = itiş × geçiş; itiş = firma F.4 işlem akımı (4 çeyrek); stok farkı ayrı sütun",
        "satirlar": rows, **et,
        "gecis_arama": [{"nerede": a, "ne": b, "sonuc": c} for a, b, c in GECIS_ARAMA],
        "referans_rapor": REFERANS, "kaynak_url": URL,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (KOK / "TAVAN_AKIS.md").write_text(md(rows, et), encoding="utf-8")
    print("=== Enflasyon tavanı, işlem akımı ===")
    for r in rows:
        print(f"{r['yil']} akım {r['f4_akim']:>9,.1f}  stok farkı {r['stok_fark']:>9,.1f}  GSYH {r['gsyh']:>10,.1f}  "
              f"oran akım {r['oran_akim']:.2f}  oran stok {r['oran_stok']:.2f}  geçiş {r['gecis']}  tavan {r['tavan']}")
    print(f"H-T {et['H-T']} | H-T2 {et['H-T2']}")


if __name__ == "__main__":
    main()
