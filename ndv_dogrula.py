"""EVDS doğrulama. Katsayı yazılmaz.

Ön kayıt kilitlidir: gözlem eşiği 36, yerel projeksiyon ufukları 0, 1, 3, 6, 12,
karar ufku 3, gecikme 3, Newey-West gecikmesi floor(4*(T/100)**(2/9)).
Bir tanımın kodu yoksa o hipotez için regresyon çalıştırılmaz.
Brüt döviz rezervi net dış varlık diye kullanılmaz.
Kıymetli maden depo hesabı altın mevduatı diye kullanılmaz.
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

BASE = "https://evds3.tcmb.gov.tr/igmevdsms-dis/fe"
KOK = Path("/workspace")

# Kod, ad, hipoteze girer mi, not
SERILER = [
    ("TP.AB.C2", "Brüt döviz rezervi, milyon ABD doları", "NDV yerine kullanılmadı"),
    ("TP.AB.C1", "Brüt altın, milyon ABD doları", "fiyatlı stok; miktar değil"),
    ("TP.AB.A02", "Analitik bilanço dış varlıklar", "altın dahil"),
    ("TP.AB.A10", "Toplam döviz yükümlülükleri", "ZK ayrılmaz"),
    ("TP.AB.A14", "Bankalar döviz mevduatı", "ZK ile serbest mevduat birlikte"),
    ("TP.AB.A19", "Zorunlu karşılıklar bloke hesabı", "TL bloke; döviz ZK stoku değil"),
    ("TP.AB.A24", "Açık piyasa işlemleri", "NİV'nin tamamı değil"),
    ("TP.AB.A051", "Menkul kıymetler", "NİV'nin tamamı değil"),
    ("TP.REZVARPD.K11", "Resmi altın, milyon troy ons", "brüt miktar; net değil"),
    ("TP.REZVARPD.K10", "Altın, mevduat ve swap dahil değer", "miktar değil"),
    ("TP.DOVVARNC.K15", "Forward, future ve swap açık pozisyonu", "saf swap stoku değil"),
    ("TP.SWAPTEKTAR.TOTALSTOKALIMYONLU", "TCMB swap stoku, alım yönlü", "2021'den itibaren"),
    ("TP.SWAPTEKTAR.SWAPASTOKUSDTUTAR", "TL karşılığı altın swap stoku, ABD doları", "ton değil"),
    ("TP.KM.F19", "Döviz tevdiat hesapları", "mevduat bankaları; yerleşik ayrımı yok"),
    ("TP.KM.F22", "Kıymetli maden depo hesapları", "altın mevduatı kodu değil"),
    ("TP.KM.F35", "Mevduat bankaları toplam mevduat", "bankalararası dahil"),
    ("TP.KM.F25", "Bankalararası mevduat", "payda dışı bırakılacak kalem"),
    ("TP.HPBITABLO3.2", "Yurt içi yerleşik TL mevduat", "haftalık tablonun aylık hali"),
    ("TP.HPBITABLO4.2", "Yurt içi yerleşik YP mevduat", "haftalık tablonun aylık hali"),
    ("TP.HPBITABLO4.7", "Gerçek kişi kıymetli maden, ABD doları karşılığı", "gram değil"),
    ("TP.HPBITABLO4.12", "Tüzel kişi kıymetli maden, ABD doları karşılığı", "gram değil"),
    ("TP.MT210AGS.TRY.MT04", "TL mevduat faizi, 1 yıla kadar, stok, %", "yıllıklandırılmış"),
    ("TP.MT210AGS.USD.MT04", "ABD doları mevduat faizi, 1 yıla kadar, stok, %", "DTH sepeti değil"),
    ("TP.PKAUO.S05.C.U", "PKA 12 ay sonrası ABD doları kuru beklentisi, TL", "uygun ortalama"),
    ("TP.PKAUO.S01.F.U", "PKA 24 ay sonrası yıllık TÜFE beklentisi, %", "uygun ortalama"),
    ("TP.DK.USD.A.YTL", "ABD doları alış kuru", "aylık"),
    ("TP.MK.LON.YTL", "Londra ons altın, ABD doları/ons", "bitiş serinin kendi sonudur"),
    ("TP.KKM.K4", "TL KKM stoku, milyar TL", "banka mevduatı; TCMB yükümlülüğü değil"),
]


def cek(kodlar):
    body = {
        "type": "json",
        "series": "-".join(kodlar),
        "aggregationTypes": "-".join(["last"] * len(kodlar)),
        "formulas": "-".join(["0"] * len(kodlar)),
        "startDate": "01-01-2003",
        "endDate": "30-09-2026",
        "frequency": "5",
        "decimalSeperator": ".",
        "decimal": "4",
        "dateFormat": "0",
        "lang": "TR",
        "yon": "0",
        "sira": "0",
        "ozelFormuller": [],
        "groupSeperator": True,
        "isRaporSayfasi": False,
    }
    req = urllib.request.Request(
        BASE,
        data=json.dumps(body).encode(),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.loads(r.read().decode("utf-8-sig"))
    return data.get("items") or []


def ozet(items, kod):
    k = kod.replace(".", "_")
    vals = []
    for it in items:
        v = it.get(k)
        if v not in (None, ""):
            vals.append(str(it["Tarih"]))
    if not vals:
        return {"kod": kod, "baslangic": None, "bitis": None, "n": 0, "durum": "bulunamadı"}
    return {
        "kod": kod,
        "baslangic": vals[0],
        "bitis": vals[-1],
        "n": len(vals),
        "durum": "doğrulandı",
    }


def main():
    kodlar = [s[0] for s in SERILER]
    items = cek(kodlar)
    rows = []
    for kod, ad, notu in SERILER:
        row = ozet(items, kod)
        row["ad"] = ad
        row["not"] = notu
        rows.append(row)
    # Tanımı kurulamayan nesneler. Bunlar için regresyon yok.
    eksik = [
        {
            "ad": "Swap ve zorunlu karşılık düşülmüş net döviz rezervi",
            "durum": "bulunamadı",
            "neden": "Saf zorunlu karşılık stokunun EVDS kodu yok. TP.AB.A14 bankaların döviz mevduatıdır. TP.AB.C2 brüttür ve NDV diye kullanılmadı.",
            "hipotez": "H1, H3, H4, H6",
        },
        {
            "ad": "Net altın miktarı, ton",
            "durum": "bulunamadı",
            "neden": "TP.REZVARPD.K11 brüt ons miktarıdır. Altın swapının ons veya ton kodu yok. ABD doları stokundan tona çevirmek fiyatı miktara karıştırır; yapılmadı.",
            "hipotez": "H2, H3, H4, H6",
        },
        {
            "ad": "Altın mevduatı, gram ve TL",
            "durum": "bulunamadı",
            "neden": "Ayrı altın mevduatı kodu yok. TP.KM.F22 kıymetli maden depo hesabıdır ve altın vekili yapılmadı.",
            "hipotez": "H5",
        },
        {
            "ad": "Net iç varlık, repo + tahvil + KKM'den doğan TCMB yükümlülüğü",
            "durum": "bulunamadı",
            "neden": "Üç kalem tek yayımlanmış NİV kodunda yok. TP.KKM.K4 banka stokudur.",
            "hipotez": "H3",
        },
    ]
    sonuc = {
        "cekme": "EVDS3 frequency=5, aggregation=last, 2003-01 .. 2026-09",
        "esik": 36,
        "regresyon": "yok",
        "seriler": rows,
        "eksik_tanim": eksik,
        "kisa_dogrulanan": min((r for r in rows if r["n"]), key=lambda r: r["n"]),
    }
    (KOK / "ndv_dogrulama.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    for r in rows:
        print(f"{r['durum']:12} n={r['n']:4} {r['baslangic']} {r['kod']} {r['ad']}")
    print("REGRESYON YOK")


if __name__ == "__main__":
    main()
