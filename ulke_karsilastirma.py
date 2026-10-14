"""Ülke karşılaştırması: yerli para alacaklısı yerli mi.

Model döviz sözleşmesini kapatmaz. Kayıp, yerli para kâğıdının yerli alacaklısının
defterine yazılırsa döngü ülke içinde kalır. Bu dosya beş adımı o ülkede kurmaz.
Yalnız alacaklı payını ve döviz payını yan yana koyar.

Kural (karşılaştırma kuralı, ölçüm değil):
  yurt dışı payı  < 0,20 ve döviz payı < 0,20  → yazilir
  yurt dışı payı  < 0,20 ve döviz payı ≥ 0,20  → yerli_para_bacagi
  yurt dışı payı ≥ 0,20 ve döviz payı ≥ 0,20  → doviz_bacagi_disarida
  yurt dışı payı ≥ 0,20 ve döviz payı < 0,20  → yabanci_alacakli_buyuk

Paylar aynı tanımdan gelmez. Her satır kendi stokunu ve tarihini taşır. Toplanmaz.
Çıktı: ulke_karsilastirma.csv, ulke_karsilastirma.json, ULKE_KARSILASTIRMA.md.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

KOK = Path(__file__).resolve().parent
YABANCI_ESIK = 0.20
DOVIZ_ESIK = 0.20

# Paylar resmi tablolardan. Birim, satırın kendi stokudur.
SATIRLAR = [
    {
        "ulke": "Türkiye",
        "stok": "merkezi yönetim iç borç",
        "donem": "2025-12",
        "yabanci_pay": 0.076,
        "doviz_pay": 1745.8 / 8152.8,
        "yerli_para_pay": 6407.0 / 8152.8,
        "kaynak": "Hazine, Kamu Borç Yönetimi Raporu 2026, s. iç borç kompozisyonu",
        "url": "https://ms.hmb.gov.tr/uploads/2026/08/Kamu-borc-Yonetimi-Raporu-2026-2f52a814a2d37854.pdf",
        "not": "Yurt dışı yerleşik payı yüzde 7,6. İç borcun 1.745,8 / 8.152,8'i döviz. ROW→F 6.575 ve ROW→GY 3.131 başka stoktur, bu paydaya girmez.",
    },
    {
        "ulke": "Japonya",
        "stok": "JGB + T-bill",
        "donem": "2026-06",
        "yabanci_pay": 149.9 / 1142.0,
        "doviz_pay": 0.0,
        "yerli_para_pay": 1.0,
        "kaynak": "MOF holder tablosu, BOJ flow of funds, 17 Eylül 2026 ön rakam",
        "url": "https://www.mof.go.jp/english/policy/jgbs/reference/Others/holdings01.pdf",
        "not": "Yabancı 149,9 / 1.142,0 trilyon yen. T-bill hariç JGB'de yabancı yüzde 7,9 (79,9 / 1.006,5). BOJ, JGB'nin yüzde 46,7'si. Kâğıt yen cinsidir.",
    },
    {
        "ulke": "ABD",
        "stok": "Treasury",
        "donem": "2025-06",
        "yabanci_pay": 0.34,
        "doviz_pay": 0.0,
        "yerli_para_pay": 1.0,
        "kaynak": "ABD Hazine / Fed, yabancı portföy anketi, 30 Haziran 2025",
        "url": "https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/shl2025r.pdf",
        "not": "Rapor: yabancılar Treasury'nin yüzde 34'ü. Uzun vadeli Treasury tutma 7.665 milyar dolar. Kâğıt dolar cinsidir.",
    },
    {
        "ulke": "Çin",
        "stok": "tahvil saklama, bütün piyasa",
        "donem": "2025-12",
        "yabanci_pay": 3.5 / 196.7,
        "doviz_pay": 0.0,
        "yerli_para_pay": 1.0,
        "kaynak": "PBOC, Xinhua 18 Şubat 2026",
        "url": "http://english.people.com.cn/n3/2026/0218/c90000-20426924.html",
        "not": "Yurt dışı kurum saklaması 3,5 / 196,7 trilyon yuan, yüzde 1,8. Stok bütün tahvil piyasasıdır, yalnız hazine kâğıdı değildir. Kâğıt yuan cinsidir.",
    },
    {
        "ulke": "Arjantin",
        "stok": "merkezi idare brüt borç",
        "donem": "2025-12",
        "yabanci_pay": 155.312 / 452.657,
        "doviz_pay": 261753419.99247962 / 452657028.55195695,
        "yerli_para_pay": 190903608.55947733 / 452657028.55195695,
        "kaynak": "Ekonomi Bakanlığı, deuda pública 31-12-2025, A.4.5 ve A.1.4",
        "url": "https://www.argentina.gob.ar/sites/default/files/deuda_publica_31-12-2025.xlsx",
        "not": "Yurt dışı yerleşik 155,3 / 452,7 milyar dolar, yüzde 34,3. Döviz 261,8 / 452,7. Yerli para yüzde 42,2. Para ve yerleşim çaprazı bu iki tabloda yok.",
    },
    {
        "ulke": "Brezilya",
        "stok": "federal kamu borcu",
        "donem": "2026-08",
        "yabanci_pay": 0.0991,
        "doviz_pay": 0.0375,
        "yerli_para_pay": 0.9625,
        "kaynak": "Tesouro Nacional, Federal Public Debt monthly, Ağustos 2026",
        "url": "https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/arquivos/publicacoes/55920_2565378/Texto_RMD_Ingles%20Aug26.pdf",
        "not": "Yerleşik olmayanlar DFPD'nin yüzde 9,91'i. Dış federal borç stokun yüzde 3,75'i (348,3 milyar real, 67,2 milyar dolar). DFPD 8.944,5 milyar real.",
    },
    {
        "ulke": "Almanya",
        "stok": "devlet borç kâğıdı",
        "donem": "2025-12",
        "yabanci_pay": 0.035 + 0.194 + 0.343,
        "doviz_pay": 0.0,
        "yerli_para_pay": 1.0,
        "kaynak": "Banco de España, FSR Spring 2026 kutu 4.2, ECB SHS",
        "url": "https://www.bde.es/f/webbe/Secciones/Publicaciones/InformesBoletinesRevistas/InformesEstabilidadFinancera/26/FSR_2026_1_Box4_2.pdf",
        "not": "Yurt dışı = euro alanı bankası 3,5 + euro alanı banka dışı 19,4 + euro dışı 34,3. Yerli banka ve banka dışı 14,9. Basılan satırlar 72,1 eder. Kalan 27,9 kutu metninde Eurosistemdir, ayrı satır basılmadı. Kâğıt euro cinsidir.",
    },
    {
        "ulke": "Fransa",
        "stok": "genel yönetim uzun vadeli borç kâğıdı",
        "donem": "2025-12",
        "yabanci_pay": 0.546,
        "doviz_pay": 0.0,
        "yerli_para_pay": 1.0,
        "kaynak": "Banque de France, securities issues, 2025-Q4",
        "url": "https://www.banque-france.fr/system/files/webstats/Emission_et_detention_de_titres_francais_2025T4_20260414/EN_Stat_Info_Securities_issues_by_French_residents_2025Q4.pdf",
        "not": "Yerleşik olmayanların payı yüzde 54,6. 2024 sonu yüzde 52,8. Kâğıt euro cinsidir.",
    },
    {
        "ulke": "İtalya",
        "stok": "devlet borç kâğıdı",
        "donem": "2025-12",
        "yabanci_pay": 0.061 + 0.136 + 0.121,
        "doviz_pay": 0.0,
        "yerli_para_pay": 1.0,
        "kaynak": "Banco de España, FSR Spring 2026 kutu 4.2, ECB SHS",
        "url": "https://www.bde.es/f/webbe/Secciones/Publicaciones/InformesBoletinesRevistas/InformesEstabilidadFinancera/26/FSR_2026_1_Box4_2.pdf",
        "not": "Yurt dışı = euro alanı bankası 6,1 + euro alanı banka dışı 13,6 + euro dışı 12,1. Yerli banka 14,5, yerli banka dışı 30,7. Kâğıt euro cinsidir.",
    },
    {
        "ulke": "İspanya",
        "stok": "devlet borç kâğıdı",
        "donem": "2025-12",
        "yabanci_pay": 0.103 + 0.192 + 0.178,
        "doviz_pay": 0.0,
        "yerli_para_pay": 1.0,
        "kaynak": "Banco de España, FSR Spring 2026 kutu 4.2, ECB SHS",
        "url": "https://www.bde.es/f/webbe/Secciones/Publicaciones/InformesBoletinesRevistas/InformesEstabilidadFinancera/26/FSR_2026_1_Box4_2.pdf",
        "not": "Yurt dışı = euro alanı bankası 10,3 + euro alanı banka dışı 19,2 + euro dışı 17,8. Yerli banka 14,0, yerli banka dışı 13,8. Kâğıt euro cinsidir.",
    },
    {
        "ulke": "Euro alanı",
        "stok": "genel yönetim borcu",
        "donem": "2024-Q4",
        "yabanci_pay": 0.23,
        "doviz_pay": 0.0,
        "yerli_para_pay": 1.0,
        "kaynak": "ECB, International Role of the Euro, 2025",
        "url": "https://www.ecb.europa.eu/press/other-publications/ire/article/html/ecb.ireart202506_01~a8b7241329.en.html",
        "not": "Alan dışı yerleşikler stokun yüzde 23'ü, yaklaşık 2.600 milyar euro. Alan içi tutma bu payda yerlidir. Ülke satırlarının toplamı değildir.",
    },
    {
        "ulke": "İngiltere",
        "stok": "gilt",
        "donem": "2024-09",
        "yabanci_pay": 0.32,
        "doviz_pay": 0.0,
        "yerli_para_pay": 1.0,
        "kaynak": "HM Treasury, Debt Management Report 2025-26",
        "url": "https://www.gov.uk/government/publications/debt-management-report-2025-26/debt-management-report-2025-26-accessible",
        "not": "Yurt dışı yatırımcı gilt stokunun yüzde 32'si. İngiltere Merkez Bankası APF yüzde 24. Sigorta ve emeklilik yüzde 21. Kâğıt sterlin cinsidir.",
    },
    {
        "ulke": "Güney Kore",
        "stok": "hazine tahvili",
        "donem": "2025-12",
        "yabanci_pay": 0.257,
        "doviz_pay": 0.0,
        "yerli_para_pay": 1.0,
        "kaynak": "Ekonomi ve Maliye Bakanlığı, Korea Treasury Bonds 2025",
        "url": "https://ktb.mofe.go.kr/eng/publications.do",
        "not": "Yabancı pay yüzde 25,7. Tutulan stok 297,4 trilyon won. 2024 payı yüzde 22,8. Kâğıt won cinsidir.",
    },
    {
        "ulke": "Meksika",
        "stok": "devlet iç kâğıdı",
        "donem": "2025-12",
        "yabanci_pay": 0.114,
        "doviz_pay": 0.0,
        "yerli_para_pay": 1.0,
        "kaynak": "Monex, Banxico yerleşik dağılımı",
        "url": "https://www.monex.com.mx/portal/download/reportes/260121%20Reconfiguracion%20demanda%20extranjera.pdf",
        "not": "Kayıtlı yerleşik pay yüzde 88,6. Kayıtlı yurt dışı pay yüzde 11,4. Not, yerleşik saklamanın bir kısmında lehtarın yabancı olabileceğini yazar. Bu satır Banxico kaydını kullanır. Kâğıt peso cinsidir.",
    },
    {
        "ulke": "Polonya",
        "stok": "yurt içi hazine kâğıdı",
        "donem": "2025-11",
        "yabanci_pay": 0.117,
        "doviz_pay": 0.0,
        "yerli_para_pay": 1.0,
        "kaynak": "Polonya Maliye Bakanlığı, 2026 birinci çeyrek finansman planı",
        "url": "https://www.gov.pl/attachment/fe7a3cce-e597-4289-b09e-972d337e798e",
        "not": "Yerleşik olmayan portföy 169,6 milyar zloti, yurt içi hazine kâğıdının yüzde 11,7'si. İhraç yeri yurt dışı olan borç, hazine borcunun yüzde 20,4'üdür ve bu paydanın dışındadır. Kâğıt zloti cinsidir.",
    },
    {
        "ulke": "Endonezya",
        "stok": "SBN",
        "donem": "2025-08-11",
        "yabanci_pay": 938.28 / 6420.62,
        "doviz_pay": None,
        "yerli_para_pay": None,
        "kaynak": "Bisnis, Maliye Bakanlığı borç kâğıdı müdürü, 13 Ağustos 2025",
        "url": "https://premium.bisnis.com/read/20250815/664/1902826/comparing-foreign-bondholders-in-the-government-bond-sbn-during-the-eras-of-sby-jokowi-and-prabowo",
        "not": "Yabancı 938,28 / 6.420,62 trilyon rupiah, yüzde 14,6. Bank Indonesia yüzde 24,2. Ticari banka yüzde 20,3. SBN'nin döviz kırılımı bu haberde yok.",
    },
]


def etiket(yabanci: float, doviz: float | None) -> str:
    if doviz is None:
        return "yerli_alacakli_doviz_ayrilmadi" if yabanci < YABANCI_ESIK else "yabanci_alacakli_doviz_ayrilmadi"
    if yabanci < YABANCI_ESIK and doviz < DOVIZ_ESIK:
        return "yazilir"
    if yabanci < YABANCI_ESIK and doviz >= DOVIZ_ESIK:
        return "yerli_para_bacagi"
    if yabanci >= YABANCI_ESIK and doviz >= DOVIZ_ESIK:
        return "doviz_bacagi_disarida"
    return "yabanci_alacakli_buyuk"


def _yuvarla(x: float | None) -> float | str:
    return "" if x is None else round(x, 4)


def _satir(r: dict) -> dict:
    y, d = r["yabanci_pay"], r["doviz_pay"]
    return {
        "ulke": r["ulke"],
        "stok": r["stok"],
        "donem": r["donem"],
        "yabanci_pay": round(y, 4),
        "yerli_pay": round(1.0 - y, 4),
        "doviz_pay": _yuvarla(d),
        "yerli_para_pay": _yuvarla(r["yerli_para_pay"]),
        "etiket": etiket(y, d),
        "kaynak": r["kaynak"],
        "url": r["url"],
        "not": r["not"],
    }


def main() -> dict:
    rows = [_satir(r) for r in SATIRLAR]
    with (KOK / "ulke_karsilastirma.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    grup: dict[str, list[str]] = {}
    for r in rows:
        grup.setdefault(r["etiket"], []).append(r["ulke"])
    sonuc = {
        "kural": {
            "yabanci_esik": YABANCI_ESIK,
            "doviz_esik": DOVIZ_ESIK,
            "etiket": "karsilastirma_kurali",
            "anlam": "Bes adim bu ulkelerde olculmedi. Test, yerli para alacaklisinin yerli olmasi ve doviz bacaginin disarida kalmasidir.",
        },
        "grup": grup,
        "yazilir": grup.get("yazilir", []),
        "satirlar": rows,
    }
    (KOK / "ulke_karsilastirma.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    ad = {
        "yazilir": "yazılır",
        "yerli_para_bacagi": "yerli para bacağı",
        "doviz_bacagi_disarida": "döviz bacağı dışarıda",
        "yabanci_alacakli_buyuk": "yabancı alacaklı büyük",
        "yerli_alacakli_doviz_ayrilmadi": "yerli alacaklı, döviz ayrılmadı",
        "yabanci_alacakli_doviz_ayrilmadi": "yabancı alacaklı, döviz ayrılmadı",
    }
    md = [
        "# Ülke karşılaştırması",
        "",
        "Çalıştır: `python3 ulke_karsilastirma.py`.",
        "",
        "Test, yerli para kâğıdının alacaklısının yerli olup olmadığıdır. Döviz sözleşmesi modelin dışında kalır. "
        "Beş adım bu ülkelerde ölçülmedi. Eşik 0,20 karşılaştırma kuralıdır.",
        "",
        f"Yazılanlar: **{', '.join(grup.get('yazilir', []))}**.",
        "",
        "| Ülke | Dönem | Stok | Yurt dışı | Yerli | Döviz | Yerli para | Etiket |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    def yuz(x) -> str:
        return "—" if x == "" else f"{float(x):.1%}"

    for r in rows:
        md.append(
            f"| {r['ulke']} | {r['donem']} | {r['stok']} | {yuz(r['yabanci_pay'])} | {yuz(r['yerli_pay'])} | "
            f"{yuz(r['doviz_pay'])} | {yuz(r['yerli_para_pay'])} | {ad[r['etiket']]} |"
        )
    md += ["", "## Satır notu", ""]
    for r in rows:
        md.append(f"- **{r['ulke']}** ({r['donem']}): {r['not']} Kaynak: {r['url']}")
    md += [
        "",
        "## Ne denmez",
        "",
        "- Japonya'da yen alacaklısı yabancıdır denmez. Haziran 2026'da yurt dışı payı yüzde 13,1'dir.",
        "- Beş adım bu ülkelerde kuruldu denmez. Burada yalnız alacaklı payı vardır.",
        "- Paylar toplanıp tek sıra yapılmaz. Stoklar ve tarihler ayrıdır.",
        "- Eşik 0,20 ölçülmüş bir yasa denmez. Karşılaştırma kuralıdır.",
        "",
    ]
    (KOK / "ULKE_KARSILASTIRMA.md").write_text("\n".join(md), encoding="utf-8")
    for r in rows:
        d = "—" if r["doviz_pay"] == "" else f"{float(r['doviz_pay']):.1%}"
        print(f"{r['ulke']:<12} yabancı {r['yabanci_pay']:.1%} döviz {d} {r['etiket']}")
    return sonuc


if __name__ == "__main__":
    main()
