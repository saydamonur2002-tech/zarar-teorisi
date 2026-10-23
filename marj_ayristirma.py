"""KAP ilk 100 (2023 satış hasılatı) faaliyet marjı ayrıştırması, 2016-2023.

Evren, 16 Ekim 2026 İş Yatırım temel tablo sayfasındaki işlem gören şirketlerdir.
Sıralama ölçütü kilitli: 2023 yıllık satış gelirleri (XI_29, kalem 3C), nominal TL.
Piyasa değeri sıralaması kullanılmaz; 2026 piyasa değeri yalnız örtüşme kontrolüdür.

Banka, sigorta, GYO, faktoring/leasing, aracı kurum, varlık yönetim ve yatırım
ortaklığı dışarıdadır. Holdingler ayrı gruptur, ilk 100'e karışmaz.

Bu dosya dipnot okumaz. Diğer faaliyet gelirinin kur/faiz/enflasyon alt kırılımı
yüz satırda yoktur. TCMB sektör bilançosu tekdüzen kalemleri ayrı popülasyondur.
"""

from __future__ import annotations

import csv
import json
import math
import re
import statistics
import time
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from html import unescape
from pathlib import Path

import xlrd

ROOT = Path(__file__).resolve().parent
HAM = ROOT / "marj_ham.csv"
LISTE = ROOT / "marj_sirket_liste.csv"
FIRMA = ROOT / "marj_firma_ozet.csv"
SEKTOR = ROOT / "marj_sektor_ozet.csv"
SONUC = ROOT / "marj_ayristirma_sonuc.json"

YILLAR = list(range(2016, 2024))
UA = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
ISY = "https://www.isyatirim.com.tr/_layouts/15/IsYatirim.Website/Common/Data.aspx/MaliTablo"
TABLO = "https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/Temel-Degerler-Ve-Oranlar.aspx"
EVDS = "https://evds3.tcmb.gov.tr/igmevdsms-dis"

FINANS_DISI = {
    "Aracı Kurumlar",
    "Bankacılık",
    "Fin.Kiralama ve Faktoring",
    "GYO",
    "Sigorta",
    "Yatırım Ortaklıkları",
    "Varlık Yönetim",
}

# İş Yatırım alt sektör -> ana sektör. Eşleşmeyenler "Diğer" kalır ve raporda ayrıca yazılır.
ANA = {
    "Gıda": "Gıda ve içecek",
    "Meşrubat / İçecek": "Gıda ve içecek",
    "Hayvancılık": "Gıda ve içecek",
    "Kimyasal Ürün": "Kimya",
    "Tarım Kimyasalları": "Kimya",
    "Boya": "Kimya",
    "Petrol": "Kimya",
    "Sağlık ve İlaç": "Kimya",
    "Demir-Çelik Temel": "Ana metal",
    "Demir-Çelik Döküm": "Ana metal",
    "Otomotiv": "Otomotiv",
    "Otomotiv Parçası": "Otomotiv",
    "Otomotiv Lastiği": "Otomotiv",
    "Tekstil Entegre": "Tekstil ve giyim",
    "Endüstriyel Tekstil": "Tekstil ve giyim",
    "Deri Giyim": "Tekstil ve giyim",
    "Çimento": "Mineral ürünler",
    "Cam": "Mineral ürünler",
    "Seramik": "Mineral ürünler",
    "İnşaat Malzemeleri": "Mineral ürünler",
    "Dayanıklı Tüketim": "Dayanıklı tüketim",
    "Mobilya": "Dayanıklı tüketim",
    "Kağıt Ürünleri": "Kağıt",
    "Kırtasiye": "Kağıt",
    "Elektrik Üretim": "Enerji",
    "Elektrik - Doğalgaz Dağıtım": "Enerji",
    "Madencilik": "Madencilik",
    "Perakande - Ticaret": "Ticaret",
    "Pazarlama": "Ticaret",
    "Bilgisayar Toptancılığı": "Ticaret",
    "Ulaştırma-Lojistik": "Ulaştırma",
    "Havayolları ve Hizm.": "Ulaştırma",
    "İnşaat- Taahhüt": "İnşaat",
    "Turizm": "Hizmet",
    "Teknoloji": "Hizmet",
    "İletişim": "Hizmet",
    "Medya": "Hizmet",
    "Spor": "Hizmet",
    "Eğlence Hizmetleri": "Hizmet",
    "Savunma": "Makine ve teçhizat",
    "Endüstriyel Makine -Teçhizat Üretim": "Makine ve teçhizat",
    "Elektrik Enerji Ürt.Teçh/Tesis Kurulum": "Makine ve teçhizat",
    "İletişim Cihazları": "Makine ve teçhizat",
    "Kablo": "Makine ve teçhizat",
    "Diğer": "Diğer",
    "Holdingler": "Holding",
}

# Alt sektör -> Yİ-ÜFE seri adı parçası. Hizmetlerde ÜFE yok; TÜFE kullanılır.
UFE_PARCA = {
    "Gıda": "3.1. Gıda",
    "Meşrubat / İçecek": "3.2. İçecek",
    "Hayvancılık": "3.1. Gıda",
    "Kimyasal Ürün": "Kimyasallar ve kimyasal",
    "Tarım Kimyasalları": "Kimyasallar ve kimyasal",
    "Boya": "Kimyasallar ve kimyasal",
    "Petrol": "kok ve rafine",
    "Sağlık ve İlaç": "eczacılık",
    "Demir-Çelik Temel": "Ana metal",
    "Demir-Çelik Döküm": "Ana metal",
    "Otomotiv": "3.20. Motorlu kara taşıtları",
    "Otomotiv Parçası": "3.20.3. Motorlu kara taşıtlarının parça",
    "Otomotiv Lastiği": "3.13. Kauçuk",
    "Tekstil Entegre": "3.4. Tekstil",
    "Endüstriyel Tekstil": "3.4. Tekstil",
    "Deri Giyim": "3.5. Giyim",
    "Çimento": "metalik olmayan mineral",
    "Cam": "metalik olmayan mineral",
    "Seramik": "metalik olmayan mineral",
    "İnşaat Malzemeleri": "metalik olmayan mineral",
    "Mobilya": "3.22. Mobilya",
    "Dayanıklı Tüketim": "Elektrikli teçhizat",
    "Kağıt Ürünleri": "3.7. Kağıt",
    "Kırtasiye": "3.7. Kağıt",
    "Elektrik Üretim": "4.1.1. Elektrik enerjisinin",
    "Elektrik - Doğalgaz Dağıtım": "4.1.1. Elektrik enerjisinin",
    "Madencilik": "2. Madencilik",
    "Kablo": "Elektrikli teçhizat",
    "İletişim Cihazları": "Elektrikli teçhizat",
    "Endüstriyel Makine -Teçhizat Üretim": "3.19.",
    "Elektrik Enerji Ürt.Teçh/Tesis Kurulum": "Elektrikli teçhizat",
    "Savunma": "3. İmalat",
}

KALEM = {
    "3C": "satis",
    "3CA": "sm",
    "3D": "brut",
    "3DA": "paz",
    "3DB": "gy",
    "3DC": "arge",
    "3DD": "diger_gelir",
    "3DE": "diger_gider",
    "3DF": "faaliyet",
    "3HA": "yat_gelir",
    "3HAA": "yat_gider",
    "3HB": "fin_gelir",
    "3HC": "fin_gider",
    "3I": "vergi_oncesi",
    "4BC": "yurtici",
    "4BD": "yurtdisi",
}
ALANLAR = ["satis", "sm", "brut", "paz", "gy", "arge", "diger_gelir", "diger_gider",
           "faaliyet", "yat_gelir", "yat_gider", "fin_gelir", "fin_gider",
           "vergi_oncesi", "yurtici", "yurtdisi"]


def get(url, headers=None, timeout=60, deneme=4):
    h = dict(UA)
    if headers:
        h.update(headers)
    son = None
    for i in range(deneme):
        try:
            req = urllib.request.Request(url, headers=h)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as exc:  # noqa: BLE001
            son = exc
            time.sleep(0.6 * (i + 1))
    raise RuntimeError(son)


def sayi(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        if isinstance(v, float) and math.isnan(v):
            return None
        return float(v)
    s = str(v).strip().replace(" ", "")
    if s in {"", "None", "null", "-"}:
        return None
    s = s.replace(".", "").replace(",", ".") if s.count(",") == 1 and s.count(".") > 1 else s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def tr_sayi(s):
    """1.234,5 -> 1234.5"""
    s = unescape(str(s)).strip().replace(" ", "")
    if not s:
        return None
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def sirket_listesi():
    html = get(TABLO, headers={"Accept": "text/html"}).decode("utf-8", "replace")
    pat = re.compile(
        r'hisse=([A-Z0-9]+)">(.*?)</a></td><td>(.*?)</td><td>(.*?)</td>'
        r'<td class="text-right">(.*?)</td><td class="text-right">(.*?)</td>'
    )
    out = []
    for m in pat.finditer(html):
        kod, ad, sektor, _fiyat, pd_tl = m.group(1), m.group(3), m.group(4), m.group(5), m.group(6)
        sektor = unescape(sektor).strip()
        out.append({
            "kod": kod,
            "ad": unescape(ad).strip(),
            "sektor": sektor,
            "ana": ANA.get(sektor, "Diğer"),
            "pd_mn_tl_2026_10_16": tr_sayi(pd_tl),
            "grup": "finans_disi" if sektor in FINANS_DISI else ("holding" if sektor == "Holdingler" else "faaliyet"),
        })
    if len(out) < 400:
        raise RuntimeError(f"şirket listesi kısa: {len(out)}")
    return out


def mali_cek(kod):
    """Sekiz yıl, iki istek. XI_29 yüz tablosu."""
    bloklar = [(2023, 2022, 2021, 2020), (2019, 2018, 2017, 2016)]
    yil_deger = {y: {a: None for a in ALANLAR} for y in YILLAR}
    for years in bloklar:
        qs = "&".join(f"year{i}={y}&period{i}=12" for i, y in enumerate(years, 1))
        url = f"{ISY}?companyCode={kod}&exchange=TRY&financialGroup=XI_29&{qs}"
        raw = json.loads(get(url).decode("utf-8-sig"))
        if not raw.get("ok"):
            continue
        for it in raw.get("value") or []:
            code = str(it.get("itemCode") or "").strip()
            alan = KALEM.get(code)
            if not alan:
                continue
            for i, y in enumerate(years, 1):
                yil_deger[y][alan] = sayi(it.get(f"value{i}"))
    return yil_deger


def ham_yaz_veya_oku(sirketler):
    if HAM.exists() and HAM.stat().st_size > 1000:
        rows = list(csv.DictReader(HAM.open(encoding="utf-8")))
        return rows, False
    hedefler = [s for s in sirketler if s["grup"] != "finans_disi"]
    rows = []
    hatalar = []

    def bir(s):
        try:
            return s["kod"], mali_cek(s["kod"]), None
        except Exception as exc:  # noqa: BLE001
            return s["kod"], None, str(exc)

    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = [ex.submit(bir, s) for s in hedefler]
        bitti = 0
        for fut in as_completed(futs):
            kod, veri, err = fut.result()
            bitti += 1
            if bitti % 40 == 0:
                print(f"çekildi {bitti}/{len(hedefler)}", flush=True)
            if err or veri is None:
                hatalar.append({"kod": kod, "hata": err})
                continue
            for y, alanlar in veri.items():
                rec = {"kod": kod, "yil": y}
                rec.update(alanlar)
                rows.append(rec)
    with HAM.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["kod", "yil", *ALANLAR])
        w.writeheader()
        for rec in rows:
            w.writerow(rec)
    (ROOT / "marj_cek_hata.json").write_text(json.dumps(hatalar, ensure_ascii=False, indent=2), encoding="utf-8")
    print("hata", len(hatalar), "satır", len(rows))
    return [{k: (None if v == "" else v) for k, v in r.items()} for r in rows], True


def ffloat(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def evds_aylik(seri_kodlari):
    body = {
        "type": "json",
        "series": "-".join(seri_kodlari),
        "aggregationTypes": "-".join("avg" for _ in seri_kodlari),
        "formulas": "-".join("0" for _ in seri_kodlari),
        "startDate": "01-01-2015",
        "endDate": "31-12-2024",
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
        EVDS + "/fe",
        data=json.dumps(body).encode(),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as r:
        data = json.loads(r.read().decode("utf-8-sig"))
    out = {k: {} for k in seri_kodlari}
    for it in data.get("items") or []:
        tarih = str(it.get("Tarih"))
        for k in seri_kodlari:
            v = it.get(k.replace(".", "_"))
            fv = sayi(v)
            if fv is not None and tarih:
                out[k][tarih] = fv
    return out


def yillik_ort(aylar):
    yil = defaultdict(list)
    for tarih, v in aylar.items():
        yil[int(tarih[:4])].append(v)
    return {y: statistics.fmean(vs) for y, vs in yil.items() if len(vs) >= 10}


def ufe_seri_listesi():
    raw = get(f"{EVDS}/serieList/fe/type=json&code=bie_tufe1yi").decode("utf-8-sig")
    return json.loads(raw)


def deflatorler():
    ufe = ufe_seri_listesi()
    ad2kod = {}
    for s in ufe:
        ad2kod[s["SERIE_NAME"]] = s["SERIE_CODE"]
    secilen = {"tufe": "TP.GENENDEKS.T1", "ufe_genel": None, "ufe_imalat": None, "ith_ara": "TP.DT.IT.FIY.D04.2010"}
    for ad, kod in ad2kod.items():
        if ad.startswith("1.Yurt İçi Üretici"):
            secilen["ufe_genel"] = kod
        elif ad.startswith("3. İmalat"):
            secilen["ufe_imalat"] = kod
    sektor_kod = {}
    eslesme_notu = {}
    for alt, parca in UFE_PARCA.items():
        aday = [ad for ad in ad2kod if ad.lower().startswith(parca.lower())]
        aday.sort(key=lambda a: (a.count("."), len(a)))
        if not aday:
            eslesme_notu[alt] = "bulunamadı, imalat ÜFE yedek"
            continue
        sektor_kod[alt] = ad2kod[aday[0]]
        eslesme_notu[alt] = aday[0]
    kodlar = [c for c in secilen.values() if c] + sorted(set(sektor_kod.values()))
    aylik = evds_aylik(kodlar)
    yillik = {k: yillik_ort(v) for k, v in aylik.items()}
    return secilen, sektor_kod, eslesme_notu, yillik


def bol(a, b):
    if a is None or b is None or b == 0:
        return None
    return a / b


def cekirdek(r):
    parca = [ffloat(r.get(k)) for k in ("brut", "paz", "gy", "arge")]
    if any(x is None for x in parca):
        return None
    return sum(parca)


def _pct(xs, p):
    xs = sorted(x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x)))
    if not xs:
        return None
    if len(xs) == 1:
        return xs[0]
    k = (len(xs) - 1) * p
    lo = int(math.floor(k))
    hi = int(math.ceil(k))
    if lo == hi:
        return xs[lo]
    return xs[lo] * (hi - k) + xs[hi] * (k - lo)


def medyan(xs):
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    if not xs:
        return None
    return statistics.median(xs)


def ortalama(xs):
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    if not xs:
        return None
    return statistics.fmean(xs)


def ols(xs, ys):
    n = len(xs)
    if n < 5:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    varx = sum((x - mx) ** 2 for x in xs)
    if varx <= 0:
        return None
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / varx
    resid = [(y - (my - b * mx) - b * x) for x, y in zip(xs, ys)]
    vary = sum((y - my) ** 2 for y in ys)
    r2 = None if vary <= 0 else 1 - sum(e * e for e in resid) / vary
    return {"beta": b, "r2": r2, "n": n}


def dlog(a, b):
    if a is None or b is None or a <= 0 or b <= 0:
        return None
    return math.log(a) - math.log(b)


def dlog_reel(a, b, y, yb, endeks):
    if a is None or b is None or a <= 0 or b <= 0:
        return None
    if endeks.get(y) is None or endeks.get(yb) is None or endeks[y] <= 0 or endeks[yb] <= 0:
        return None
    return math.log(a / endeks[y]) - math.log(b / endeks[yb])


def pp(a, b):
    """yüzde puan farkı: a ve b oran ise (a-b)*100"""
    if a is None or b is None:
        return None
    return (a - b) * 100


def tcmb_sektor():
    wb = xlrd.open_workbook(ROOT / "Ekonomik faaliyetlere ve yıllara göre firmaların  gelir tablosu .xls")
    sh = wb.sheet_by_name("t7")
    yillar = [int(sh.cell_value(3, c)) for c in range(2, sh.ncols)]
    bloklar = []
    starts = [r for r in range(4, sh.nrows) if sh.cell_value(r, 0)]
    for i, r0 in enumerate(starts):
        r1 = starts[i + 1] if i + 1 < len(starts) else sh.nrows
        ad = str(sh.cell_value(r0, 0)).split("\n")[0].strip()
        if not ad or ad.startswith("TÜİK") or ad.startswith("TurkStat") or ad.startswith("Tablo"):
            continue
        kalem = {}
        for r in range(r0, r1):
            et = str(sh.cell_value(r, 1)).split("\n")[0].strip()
            if not et:
                continue
            vals = {}
            for j, y in enumerate(yillar):
                v = sh.cell_value(r, 2 + j)
                vals[y] = float(v) if isinstance(v, (int, float)) else None
            kalem[et] = vals
        bloklar.append((ad, kalem))

    def bul(kalem, parca):
        for et, vals in kalem.items():
            if parca in et:
                return vals
        return None

    ozet = []
    for ad, kalem in bloklar:
        net = bul(kalem, "C-Net satışlar")
        faal = bul(kalem, "Faaliyet karı veya zararı")
        ftop = bul(kalem, "F-Diğer faal")
        gtop = bul(kalem, "G-Diğer faal")
        donem = bul(kalem, "Dönem kar veya zararı")
        kamb_kar = bul(kalem, "7-Kambiyo karları")
        kamb_zar = bul(kalem, "4-Kambiyo zararları")
        faiz = bul(kalem, "3-Faiz gelirleri")
        enf_kar = bul(kalem, "9-Enflasyon düzeltmesi karları")
        enf_zar = bul(kalem, "6-Enflasyon düzeltmesi zararları")
        mk = bul(kalem, "6-Menkul kıymet satış karları")
        tem1 = bul(kalem, "1-İştiraklerden temettü")
        tem2 = bul(kalem, "2-Bağlı ortaklıklardan temettü")
        for y in YILLAR:
            if net is None or net.get(y) in (None, 0):
                continue
            ns = net[y]
            fk = faal[y] if faal else None
            F = ftop[y] if ftop else None
            G = gtop[y] if gtop else None
            P = donem[y] if donem else None
            kk = kamb_kar[y] if kamb_kar else None
            kz = kamb_zar[y] if kamb_zar else None
            ozet.append({
                "sektor": ad,
                "yil": y,
                "cekirdek_marj": bol(fk, ns),
                "genis_faaliyet_marj": bol((fk or 0) + (F or 0) - (G or 0), ns) if fk is not None and F is not None and G is not None else None,
                "vergi_oncesi_marj": bol(P, ns),
                "F_satis": bol(F, ns),
                "F_vergi_oncesi": bol(F, P) if P not in (None, 0) else None,
                "net_kambiyo_satis": bol((kk or 0) - (kz or 0), ns) if kk is not None and kz is not None else None,
                "kambiyo_kar_F": bol(kk, F) if F not in (None, 0) else None,
                "faiz_F": bol(faiz[y] if faiz else None, F) if F not in (None, 0) else None,
                "enf_net_satis": bol((enf_kar[y] if enf_kar else 0) - (enf_zar[y] if enf_zar else 0), ns) if enf_kar and enf_zar else None,
                "mk_F": bol(mk[y] if mk else None, F) if F not in (None, 0) else None,
                "temettu_F": bol(((tem1[y] if tem1 else 0) + (tem2[y] if tem2 else 0)), F) if F not in (None, 0) and tem1 and tem2 else None,
            })
    return ozet


def main():
    sirketler = sirket_listesi()
    with LISTE.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["kod", "ad", "sektor", "ana", "grup", "pd_mn_tl_2026_10_16"])
        w.writeheader()
        w.writerows(sirketler)
    print("şirket", len(sirketler), {g: sum(1 for s in sirketler if s["grup"] == g) for g in ("faaliyet", "holding", "finans_disi")})

    rows, _ = ham_yaz_veya_oku(sirketler)
    by = defaultdict(dict)
    for r in rows:
        y = int(float(r["yil"]))
        by[r["kod"]][y] = {a: ffloat(r.get(a)) for a in ALANLAR}

    meta = {s["kod"]: s for s in sirketler}
    secilen, sektor_kod, eslesme, yillik = deflatorler()
    cpi = yillik[secilen["tufe"]]
    ufe_im = yillik[secilen["ufe_imalat"]]
    ufe_gn = yillik[secilen["ufe_genel"]]
    ith = yillik[secilen["ith_ara"]]
    usd = yillik_ort(evds_aylik(["TP.DK.USD.A.YTL"])["TP.DK.USD.A.YTL"])
    # BEC birim değer endeksi döviz cinsidir (2018'de kur şokuna göre az hareket eder).
    # TL vekili = endeks × yıllık ortalama dolar alış. Firma ithalatı değildir.
    ith_tl = {y: ith[y] * usd[y] for y in ith if y in usd}

    def endeks(alt, y):
        kod = sektor_kod.get(alt)
        if kod and y in yillik.get(kod, {}):
            return yillik[kod][y], "Yİ-ÜFE:" + eslesme.get(alt, kod)
        if alt in UFE_PARCA and y in ufe_im:
            return ufe_im[y], "Yİ-ÜFE imalat (yedek)"
        return cpi.get(y), "TÜFE (hizmet/eşleşme yok)"

    def firma_olc(kod):
        seri = by.get(kod)
        if not seri:
            return None
        if any(y not in seri or seri[y]["satis"] is None or seri[y]["satis"] <= 0 for y in YILLAR):
            return None
        m = meta[kod]
        rec = {"kod": kod, "ad": m["ad"], "sektor": m["sektor"], "ana": m["ana"], "grup": m["grup"],
               "pd_mn_tl_2026_10_16": m["pd_mn_tl_2026_10_16"]}
        for y in YILLAR:
            r = seri[y]
            satis = r["satis"]
            ck = cekirdek(r)
            rec[f"cekirdek_{y}"] = bol(ck, satis)
            rec[f"faaliyet_{y}"] = bol(r["faaliyet"], satis)
            rec[f"vo_{y}"] = bol(r["vergi_oncesi"], satis)
            rec[f"diger_satis_{y}"] = bol(r["diger_gelir"], satis)
            rec[f"net_diger_satis_{y}"] = bol((r["diger_gelir"] or 0) + (r["diger_gider"] or 0), satis) if r["diger_gelir"] is not None and r["diger_gider"] is not None else None
            rec[f"diger_vo_{y}"] = bol(r["diger_gelir"], r["vergi_oncesi"]) if r["vergi_oncesi"] not in (None, 0) else None
            rec[f"fin_gelir_satis_{y}"] = bol(r["fin_gelir"], satis)
            rec[f"satis_{y}"] = satis
            rec[f"sm_{y}"] = r["sm"]
            yt, yd = r["yurtici"], r["yurtdisi"]
            rec[f"ihracat_pay_{y}"] = bol(yd, (yt or 0) + (yd or 0)) if yt is not None and yd is not None and (yt + yd) > 0 else None
        # 2016-2022 birincil (2023 TMS 29 yılı ayrı)
        rec["d_cek_16_22"] = pp(rec["cekirdek_2022"], rec["cekirdek_2016"])
        rec["d_faal_16_22"] = pp(rec["faaliyet_2022"], rec["faaliyet_2016"])
        rec["d_vo_16_22"] = pp(rec["vo_2022"], rec["vo_2016"])
        rec["d_cek_16_23"] = pp(rec["cekirdek_2023"], rec["cekirdek_2016"])
        rec["d_faal_16_23"] = pp(rec["faaliyet_2023"], rec["faaliyet_2016"])
        rec["d_vo_16_23"] = pp(rec["vo_2023"], rec["vo_2016"])
        rec["d_net_diger_16_22"] = pp(rec["net_diger_satis_2022"], rec["net_diger_satis_2016"])
        rec["d_fin_gelir_16_22"] = pp(rec["fin_gelir_satis_2022"], rec["fin_gelir_satis_2016"])
        fin_net_22 = bol((seri[2022]["fin_gelir"] or 0) + (seri[2022]["fin_gider"] or 0), seri[2022]["satis"]) if seri[2022]["fin_gelir"] is not None and seri[2022]["fin_gider"] is not None else None
        fin_net_16 = bol((seri[2016]["fin_gelir"] or 0) + (seri[2016]["fin_gider"] or 0), seri[2016]["satis"]) if seri[2016]["fin_gelir"] is not None and seri[2016]["fin_gider"] is not None else None
        rec["d_fin_net_16_22"] = pp(fin_net_22, fin_net_16)
        rec["diger_ort_16_22"] = ortalama([rec[f"diger_satis_{y}"] for y in range(2016, 2023)])
        xs, ys = [], []
        xs23, ys23 = [], []
        for y in range(2017, 2024):
            ds = dlog(seri[y]["satis"], seri[y - 1]["satis"])
            dc = dlog(abs(seri[y]["sm"]) if seri[y]["sm"] is not None else None,
                      abs(seri[y - 1]["sm"]) if seri[y - 1]["sm"] is not None else None)
            if ds is None or dc is None:
                continue
            xs23.append(dc)
            ys23.append(ds)
            if y <= 2022:
                xs.append(dc)
                ys.append(ds)
        b = ols(xs, ys)
        b23 = ols(xs23, ys23)
        rec["beta_16_22"] = None if not b else b["beta"]
        rec["beta_r2_16_22"] = None if not b else b["r2"]
        rec["beta_n"] = None if not b else b["n"]
        rec["beta_16_23"] = None if not b23 else b23["beta"]
        # Ortak TÜFE'yi her iki taraftan düş. Nominal beta enflasyonda mekanik olarak 1'e yapışır.
        xsr, ysr = [], []
        for y in range(2017, 2023):
            ds = dlog_reel(seri[y]["satis"], seri[y - 1]["satis"], y, y - 1, cpi)
            dc = dlog_reel(abs(seri[y]["sm"]) if seri[y]["sm"] is not None else None,
                           abs(seri[y - 1]["sm"]) if seri[y - 1]["sm"] is not None else None, y, y - 1, cpi)
            if ds is None or dc is None:
                continue
            xsr.append(dc)
            ysr.append(ds)
        br = ols(xsr, ysr)
        rec["beta_reel_16_22"] = None if not br else br["beta"]
        rec["beta_reel_r2"] = None if not br else br["r2"]
        # reel satış, ortak TÜFE yıllık ortalama, 2022 fiyatları (2023 TMS 29 karışmasın)
        def reel(y, baz=2022):
            if y not in cpi or baz not in cpi:
                return None
            return rec[f"satis_{y}"] * cpi[baz] / cpi[y]
        r16, r22, r23 = reel(2016), reel(2022), reel(2023, 2023)
        rec["reel_satis_2016_2022fiyat"] = r16
        rec["reel_artis_16_22"] = bol(r22, r16) - 1 if r16 and r22 else None
        # fiyat / miktar: sektör ÜFE. 2016-2022.
        p16, et16 = endeks(m["sektor"], 2016)
        p22, et22 = endeks(m["sektor"], 2022)
        rec["fiyat_endeks_not"] = et22
        if p16 and p22 and rec["satis_2016"] and rec["satis_2022"]:
            fiyat = p22 / p16
            nom = rec["satis_2022"] / rec["satis_2016"]
            rec["fiyat_carpan_16_22"] = fiyat - 1
            rec["miktar_carpan_16_22"] = (nom / fiyat) - 1
            rec["nom_carpan_16_22"] = nom - 1
        else:
            rec["fiyat_carpan_16_22"] = rec["miktar_carpan_16_22"] = rec["nom_carpan_16_22"] = None
        # maliyet nominal vs ithal ara mal fiyatı, 2016-2022
        if 2016 in ith and 2022 in ith and seri[2016]["sm"] and seri[2022]["sm"]:
            rec["sm_nom_16_22"] = abs(seri[2022]["sm"]) / abs(seri[2016]["sm"]) - 1
            rec["ith_fiyat_16_22"] = ith[2022] / ith[2016] - 1
        else:
            rec["sm_nom_16_22"] = rec["ith_fiyat_16_22"] = None
        rec["ihracat_pay_ort"] = ortalama([rec[f"ihracat_pay_{y}"] for y in YILLAR])
        # bayraklar, 2016-2022. Örtüşebilir; eleme yok.
        beta = rec["beta_16_22"]
        breel = rec["beta_reel_16_22"]
        dcek = rec["d_cek_16_22"]
        dfaal = rec["d_faal_16_22"]
        rec["A_yuksek_gecis"] = beta is not None and beta >= 0.8
        rec["A_reel"] = breel is not None and breel >= 0.8
        rec["B_dusuk_gecis_marj"] = breel is not None and breel < 0.5 and dcek is not None and dcek > 3
        rec["C_diger_gelir_farkı"] = (
            dfaal is not None and dcek is not None and (dfaal - dcek) > 3 and dcek <= 1
        )
        return rec

    olculer = []
    eksik_neden = defaultdict(int)
    for s in sirketler:
        if s["grup"] == "finans_disi":
            continue
        rec = firma_olc(s["kod"])
        if rec is None:
            seri = by.get(s["kod"])
            if not seri:
                eksik_neden["tablo_yok"] += 1
            else:
                eksik_neden["yil_eksik_veya_satis_yok"] += 1
                for y in YILLAR:
                    if y not in seri or seri[y]["satis"] is None or seri[y]["satis"] <= 0:
                        eksik_neden[f"eksik_{y}"] += 1
            continue
        olculer.append(rec)

    faaliyet = [r for r in olculer if r["grup"] == "faaliyet"]
    holding = [r for r in olculer if r["grup"] == "holding"]
    faaliyet.sort(key=lambda r: r["satis_2023"], reverse=True)
    ilk100 = faaliyet[:100]
    for i, r in enumerate(faaliyet, 1):
        r["sira_2023_satis"] = i
        r["ilk100"] = i <= 100
    holding.sort(key=lambda r: r["satis_2023"], reverse=True)
    esik = ilk100[-1]["satis_2023"] if ilk100 else None
    for r in holding:
        r["sira_2023_satis"] = None
        r["ilk100"] = False
        r["esigi_asardi"] = esik is not None and r["satis_2023"] >= esik

    # yüksek diğer gelir: ilk 100 içinde 2016-2022 ortalama diğer faaliyet geliri / satış, medyan üstü
    med_diger = medyan([r["diger_ort_16_22"] for r in ilk100])
    for r in ilk100:
        r["yuksek_diger"] = r["diger_ort_16_22"] is not None and med_diger is not None and r["diger_ort_16_22"] >= med_diger
    yuksek = [r for r in ilk100 if r.get("yuksek_diger")]
    dusuk = [r for r in ilk100 if not r.get("yuksek_diger")]

    # piyasa değeri örtüşmesi: aynı tam panel faaliyet evreninde 2026 PD ilk 100
    pd_sira = sorted([r for r in faaliyet if r["pd_mn_tl_2026_10_16"]], key=lambda r: r["pd_mn_tl_2026_10_16"], reverse=True)
    pd100 = {r["kod"] for r in pd_sira[:100]}
    ortus = len([r for r in ilk100 if r["kod"] in pd100])

    def ozet_grup(ad, grup):
        return {
            "grup": ad,
            "n": len(grup),
            "med_d_cek_16_22_pp": medyan([r["d_cek_16_22"] for r in grup]),
            "med_d_faal_16_22_pp": medyan([r["d_faal_16_22"] for r in grup]),
            "med_d_vo_16_22_pp": medyan([r["d_vo_16_22"] for r in grup]),
            "med_d_cek_16_23_pp": medyan([r["d_cek_16_23"] for r in grup]),
            "med_d_faal_16_23_pp": medyan([r["d_faal_16_23"] for r in grup]),
            "med_d_net_diger_16_22_pp": medyan([r["d_net_diger_16_22"] for r in grup]),
            "med_beta_16_22": medyan([r["beta_16_22"] for r in grup]),
            "med_beta_reel": medyan([r["beta_reel_16_22"] for r in grup]),
            "p25_d_cek": _pct([r["d_cek_16_22"] for r in grup], 0.25),
            "p75_d_cek": _pct([r["d_cek_16_22"] for r in grup], 0.75),
            "p25_d_faal": _pct([r["d_faal_16_22"] for r in grup], 0.25),
            "p75_d_faal": _pct([r["d_faal_16_22"] for r in grup], 0.75),
            "med_d_fin_net": medyan([r["d_fin_net_16_22"] for r in grup]),
            "pay_A_nominal": bol(sum(1 for r in grup if r["A_yuksek_gecis"]), len(grup)),
            "pay_A_reel": bol(sum(1 for r in grup if r["A_reel"]), len(grup)),
            "pay_B": bol(sum(1 for r in grup if r["B_dusuk_gecis_marj"]), len(grup)),
            "pay_C": bol(sum(1 for r in grup if r["C_diger_gelir_farkı"]), len(grup)),
            "med_diger_ort": medyan([r["diger_ort_16_22"] for r in grup]),
            "med_reel_artis_16_22": medyan([r["reel_artis_16_22"] for r in grup]),
            "med_fiyat": medyan([r["fiyat_carpan_16_22"] for r in grup]),
            "med_miktar": medyan([r["miktar_carpan_16_22"] for r in grup]),
            "med_ihracat": medyan([r["ihracat_pay_ort"] for r in grup]),
            "n_beta": sum(1 for r in grup if r["beta_16_22"] is not None),
        }

    sektor_ozet = []
    for ana in sorted({r["ana"] for r in ilk100}):
        g = [r for r in ilk100 if r["ana"] == ana]
        row = ozet_grup(ana, g)
        row["n_kucuk"] = len(g) < 5
        sektor_ozet.append(row)

    # yıl yıl medyan dlog maliyet vs ithalat fiyatı (2017-2022)
    yil_kars = []
    for y in range(2017, 2023):
        dsm = []
        for r in ilk100:
            seri = by[r["kod"]]
            dc = dlog(abs(seri[y]["sm"]) if seri[y]["sm"] else None, abs(seri[y - 1]["sm"]) if seri[y - 1]["sm"] else None)
            if dc is not None:
                dsm.append(dc)
        dith = dlog(ith.get(y), ith.get(y - 1))
        dufe = dlog(ufe_im.get(y), ufe_im.get(y - 1))
        dcpi = dlog(cpi.get(y), cpi.get(y - 1))
        dith_tl = dlog(ith_tl.get(y), ith_tl.get(y - 1))
        yil_kars.append({"yil": y, "med_dlog_sm": medyan(dsm), "dlog_ith_ara": dith, "dlog_ith_tl_vekil": dith_tl, "dlog_ufe_imalat": dufe, "dlog_tufe": dcpi, "n": len(dsm)})

    def korel(anahtar):
        xs = [k[anahtar] for k in yil_kars]
        ys = [k["med_dlog_sm"] for k in yil_kars]
        if any(v is None for v in xs + ys):
            return None
        return ols(xs, ys)

    tcmb = tcmb_sektor()
    # imalat ve birkaç bölüm, 2016 ve 2022 ve 2023
    tcmb_sec = []
    for row in tcmb:
        if row["yil"] in (2016, 2018, 2021, 2022, 2023):
            tcmb_sec.append(row)

    # 2023 nominal büyüme vs TÜFE, TMS 29 şüphesi
    buyume_23 = []
    for r in ilk100:
        g = bol(r["satis_2023"], r["satis_2022"])
        if g is not None:
            buyume_23.append(g - 1)
    cpi_23 = bol(cpi.get(2023), cpi.get(2022))

    sonuc = {
        "tanim": {
            "siralama": "2023 yıllık satış gelirleri, XI_29 kalem 3C, yayımlanmış nominal TL",
            "siralama_yili": 2023,
            "pd_kullanilmadi": "İş Yatırım tablosundaki piyasa değeri 16 Ekim 2026 anlık değeridir; sıralama ölçütü değildir",
            "evren_tarihi": "2026-10-16 İş Yatırım temel değerler tablosu, o tarihte listelenen şirketler",
            "finans_disi": sorted(FINANS_DISI),
            "holding_ayri": True,
            "marj": {
                "cekirdek": "(brüt kar + pazarlama + genel yönetim + Ar-Ge) / satış; diğer faaliyet geliri hariç",
                "faaliyet": "XI_29 3DF faaliyet karı / satış; diğer faaliyet geliri ve gideri dahildir",
                "vergi_oncesi": "XI_29 3I / satış",
                "diger_vo": "3DD diğer faaliyet gelirleri / 3I; vergi öncesi kar sıfırsa boş",
            },
            "birincil_pencere": "2016-2022. 2023 TMS 29 yılı olduğu için marj değişiminin birincil ölçüsü 2022-2016'dır; 2023 ayrıca yazılır.",
            "deflator": "TÜFE yıllık ortalama TP.GENENDEKS.T1 (2003=100), aylık endeksin yıl ortalaması. Fiyat-miktar ayrımı sektör Yİ-ÜFE yıllık ortalaması; eşleşme yoksa imalat ÜFE, hizmette TÜFE.",
            "gecis": "beta nominal = 2017-2022 dlog(satış) on dlog(|satışların maliyeti|). beta_reel aynı regresyon, her iki taraf TÜFE yıllık ortalamasına bölündükten sonra. İkisi de ithal girdi fiyatının geçiş oranı değildir.",
            "A_nominal": "beta>=0.8. Yüksek enflasyonda ayırt edici değildir.",
            "A_reel": "beta_reel>=0.8",
            "B": "beta_reel<0.5 ve çekirdek marj 2016-2022 artışı >3 yüzde puan",
            "C": "faaliyet marjı artışı çekirdek marj artışını 3 puandan fazla aşıyor ve çekirdek artış <=1 puan",
            "yuksek_diger": "ilk 100 içinde 2016-2022 ortalama (diğer faaliyet geliri/satış) medyan ve üstü",
            "yuksek_diger_esik": med_diger,
        },
        "sayim": {
            "listelenen": len(sirketler),
            "faaliyet_listelenen": sum(1 for s in sirketler if s["grup"] == "faaliyet"),
            "holding_listelenen": sum(1 for s in sirketler if s["grup"] == "holding"),
            "finans_dislanan": sum(1 for s in sirketler if s["grup"] == "finans_disi"),
            "tam_panel_faaliyet": len(faaliyet),
            "tam_panel_holding": len(holding),
            "eksik": eksik_neden,
            "ilk100_esik_satis_tl_2023": esik,
            "pd_ilk100_ortusme": ortus,
            "holding_esigi_asan": sum(1 for r in holding if r.get("esigi_asardi")),
        },
        "makro": {
            "tufe_yillik_ort": {str(y): cpi.get(y) for y in YILLAR},
            "ufe_imalat_yillik_ort": {str(y): ufe_im.get(y) for y in YILLAR},
            "ufe_genel_yillik_ort": {str(y): ufe_gn.get(y) for y in YILLAR},
            "ithalat_ara_mal_birim_deger": {str(y): ith.get(y) for y in YILLAR},
            "usd_alis_yillik_ort": {str(y): usd.get(y) for y in YILLAR},
            "ithalat_ara_tl_vekil": {str(y): ith_tl.get(y) for y in YILLAR},
            "ith_tl_vekil_carpan_16_22": bol(ith_tl.get(2022), ith_tl.get(2016)),
            "tufe_2023_2022": cpi_23,
            "med_nom_satis_buyume_2023": medyan(buyume_23),
            "tufe_carpan_16_22": bol(cpi.get(2022), cpi.get(2016)),
            "ufe_imalat_carpan_16_22": bol(ufe_im.get(2022), ufe_im.get(2016)),
            "ith_ara_carpan_16_22": bol(ith.get(2022), ith.get(2016)),
            "ufe_tufe_carpan_fark_16_22": (bol(ufe_im.get(2022), ufe_im.get(2016)) or 0) - (bol(cpi.get(2022), cpi.get(2016)) or 0),
        },
        "yil_maliyet_ithalat": yil_kars,
        "korel_sm_ithalat": korel("dlog_ith_ara"),
        "korel_sm_ithalat_tl": korel("dlog_ith_tl_vekil"),
        "korel_sm_ufe": korel("dlog_ufe_imalat"),
        "grup": {
            "ilk100": ozet_grup("ilk100", ilk100),
            "yuksek_diger": ozet_grup("yuksek_diger", yuksek),
            "dusuk_diger": ozet_grup("dusuk_diger", dusuk),
            "holding_tam_panel": ozet_grup("holding", holding),
        },
        "sektor": sektor_ozet,
        "ufe_eslesme": eslesme,
        "tcmb_secili": tcmb_sec,
    }
    SONUC.write_text(json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8")

    alanlar = ["kod", "ad", "sektor", "ana", "grup", "sira_2023_satis", "ilk100", "yuksek_diger",
               "satis_2023", "pd_mn_tl_2026_10_16", "d_cek_16_22", "d_faal_16_22", "d_vo_16_22",
               "d_cek_16_23", "d_faal_16_23", "d_net_diger_16_22", "diger_ort_16_22",
               "beta_16_22", "beta_r2_16_22", "beta_reel_16_22", "beta_16_23", "reel_artis_16_22",
               "fiyat_carpan_16_22", "miktar_carpan_16_22", "d_fin_net_16_22", "ihracat_pay_ort", "fiyat_endeks_not",
               "A_yuksek_gecis", "A_reel", "B_dusuk_gecis_marj", "C_diger_gelir_farkı",
               "cekirdek_2016", "cekirdek_2022", "cekirdek_2023", "faaliyet_2016", "faaliyet_2022", "faaliyet_2023",
               "vo_2016", "vo_2022", "diger_vo_2016", "diger_vo_2022", "diger_vo_2023"]
    with FIRMA.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=alanlar, extrasaction="ignore")
        w.writeheader()
        for r in ilk100 + holding:
            w.writerow(r)
    with SEKTOR.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(sektor_ozet[0].keys()))
        w.writeheader()
        w.writerows(sektor_ozet)
    print(json.dumps({"sayim": sonuc["sayim"], "grup": sonuc["grup"], "makro_carpan": {
        "tufe": sonuc["makro"]["tufe_carpan_16_22"],
        "ufe": sonuc["makro"]["ufe_imalat_carpan_16_22"],
        "ith": sonuc["makro"]["ith_ara_carpan_16_22"],
        "med_buyume_23": sonuc["makro"]["med_nom_satis_buyume_2023"],
        "tufe_23": sonuc["makro"]["tufe_2023_2022"],
    }}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
