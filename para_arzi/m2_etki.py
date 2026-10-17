"""Beş adımın M2'ye etkisi.

Kurallar hesap öncesi para_arzi/M2_YANLISLAMA.md dosyasında kilitlendi.
Sayı uydurulmaz: M2 düzeyi EVDS'den gelir; adres, örtüşme ve kenarlar repodan okunur.
"""
from __future__ import annotations

import csv
import hashlib
import json
import urllib.request
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
BUR = Path(__file__).resolve().parent
KRITER = BUR / "M2_YANLISLAMA.md"
HAM = BUR / "m2_ham.json"
CIKTI = BUR / "m2_etki.json"
RAPOR = BUR / "M2_ETKI.md"

BASE = "https://evds3.tcmb.gov.tr/igmevdsms-dis"
HAFTA = "27-03-2026"  # 2026-Q1 son cuması (31 Mart salı)

# Adım 4 adresleri, 2026-Q1, milyar TL. adim4_adres_yonlendirme_sonuc.json
HANE_VADELI = 8322.4
FIRMA_VADELI = 4400.1
GERCEK_YP = 6639.4
ADRES_HAM = 19361.9
# rev_adim4_sonuc.json örtüşme bandı (yeniden tahmin değil)
ORTUSME_ALT = 285.3
ORTUSME_UST = 6639.4
A_ALT = 12722.5  # ham − üst örtüşme
A_UST = 19076.6  # ham − alt örtüşme

KREDI_PAY = 0.08  # tek_sistem_kademe.K3_MEVDUAT_KREDI_PAYI
DIBS_2026_03_27 = 10339.8  # rev_adim4_sonuc.json, milyar TL

TL_PARA_STOKU = 16472.8
EMISYON = 898.3
TL_MEVDUAT_TABLO3 = 15574.5

# stok_silim.py kenarlar_rapor_metni. (araç, alacaklı, borçlu, stok, karşı yok)
KENAR = (
    ("kredi", "PFK", "F", 18729.0, False),
    ("kredi", "PFK", "H", 6772.0, False),
    ("kredi", "ROW", "F", 6575.0, False),
    ("kredi", "ROW", "PFK", 4033.0, False),
    ("kredi", "ROW", "GY", 492.0, False),
    ("mevduat", "H", "PFK", 15361.0, False),
    ("mevduat", "F", "PFK", 7195.0, False),
    ("mevduat", "PFK", "PFK", 10258.0, True),
    ("mevduat", "PFK", "ROW", 4606.0, False),
    ("mevduat", "GY", "GY", 352.0, True),
    ("borclanma_senedi", "PFK", "GY", 10105.0, False),
    ("borclanma_senedi", "ROW", "GY", 2639.0, False),
)

SENARYO = (
    {"ad": "dusuk", "theta": 0.10, "chi": 0.0, "adres": A_ALT, "adim12": "ayri"},
    {"ad": "orta", "theta": 0.25, "chi": 0.5, "adres": A_UST, "adim12": "ayri"},
    {"ad": "yuksek", "theta": 0.50, "chi": 0.5, "adres": A_UST, "adim12": "birlesik"},
)


def _sha(yol: Path) -> str:
    return hashlib.sha256(yol.read_bytes()).hexdigest()


def _get(url: str, body: dict | None = None) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        method="POST" if body is not None else "GET",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8-sig"))


def _sayi(v) -> float:
    return float(str(v).replace(",", ""))


def evds_hafta() -> dict:
    """HPB tablo 1, 27-03-2026. Ham birim bin TL."""
    series = _get(f"{BASE}/serieList/fe/type=json&code=bie_hpbitablo1")
    kod = [s["SERIE_CODE"] for s in series]
    ad = {s["SERIE_CODE"]: s["SERIE_NAME"] for s in series}
    aggs = [s["DEFAULT_AGG_METHOD"] for s in series]
    body = {
        "type": "json",
        "series": "-".join(kod),
        "aggregationTypes": "-".join(aggs),
        "formulas": "-".join("0" for _ in kod),
        "startDate": "20-03-2026",
        "endDate": "03-04-2026",
        "frequency": "1",
        "decimalSeperator": ".",
        "decimal": "1",
        "dateFormat": "0",
        "lang": "TR",
        "yon": "0",
        "sira": "0",
        "ozelFormuller": [],
        "groupSeperator": True,
        "isRaporSayfasi": False,
    }
    data = _get(f"{BASE}/fe", body)
    satir = next(it for it in data["items"] if it.get("Tarih") == HAFTA)
    ham = {s["SERIE_CODE"]: _sayi(satir[s["SERIE_CODE"].replace(".", "_")]) for s in series}
    return {"tarih": HAFTA, "grup": "bie_hpbitablo1", "ad": ad, "ham_bin_tl": ham}


def birim_capasi() -> dict:
    """2026-03 hane TL mevduatı. Ham csv bin TL; /1e6 milyar TL."""
    yol = KOK / "veri/aktarim_matrisi/evds/evds_b_para_banka_aylik.csv"
    istenen = {"TP.KM.E041": None, "TP.KB.FON033": None}
    with yol.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if row["Donem"] == "2026-03" and row["Seri"] in istenen:
                istenen[row["Seri"]] = float(row["Deger"])
    if any(v is None for v in istenen.values()):
        raise RuntimeError("birim çapası serisi yok")
    toplam = sum(istenen.values()) / 1e6
    return {"ham_bin_tl": istenen, "milyar": round(toplam, 4), "repo_karsilik": 8037.1}


def milyar(ham_bin: float) -> float:
    return ham_bin / 1e6


def m2_parcala(ham: dict) -> dict:
    g = lambda k: milyar(ham[k])
    tl = g("TP.HPBITABLO1.3") + g("TP.HPBITABLO1.4") + g("TP.HPBITABLO1.12")
    yp = g("TP.HPBITABLO1.8") + g("TP.HPBITABLO1.15")
    m1 = g("TP.HPBITABLO1.3") + g("TP.HPBITABLO1.4") + g("TP.HPBITABLO1.8")
    m2 = g("TP.HPBITABLO1.11")
    m3 = g("TP.HPBITABLO1.18")
    repo = g("TP.HPBITABLO1.19")
    ppf = g("TP.HPBITABLO1.20")
    menkul = g("TP.HPBITABLO1.21")
    if abs((tl + yp) - m2) > 0.05:
        raise RuntimeError(f"M2 bileşen toplamı tutmuyor: {tl + yp} vs {m2}")
    if abs(m1 + g("TP.HPBITABLO1.12") + g("TP.HPBITABLO1.15") - m2) > 0.05:
        raise RuntimeError("M2 = M1 + vadeli TL + vadeli YP tutmuyor")
    if abs(m2 + repo + ppf + menkul - m3) > 0.05:
        raise RuntimeError("M3 kimliği tutmuyor")
    return {
        "milyar": {
            "dolasim": round(g("TP.HPBITABLO1.3"), 4),
            "vadesiz_tl": round(g("TP.HPBITABLO1.4"), 4),
            "vadesiz_yp": round(g("TP.HPBITABLO1.8"), 4),
            "vadeli_tl": round(g("TP.HPBITABLO1.12"), 4),
            "vadeli_yp": round(g("TP.HPBITABLO1.15"), 4),
            "tl": round(tl, 4),
            "yp": round(yp, 4),
            "m1": round(m1, 4),
            "m2": round(m2, 4),
            "m3": round(m3, 4),
            "repo": round(repo, 4),
            "ppf": round(ppf, 4),
            "menkul": round(menkul, 4),
        },
        "yp_m2_icinde": True,
        "menkul_m2_icinde": False,
    }


def _yon_topla() -> dict[tuple[str, str], dict[str, float]]:
    from collections import defaultdict
    yon: dict[tuple[str, str], dict[str, float]] = defaultdict(lambda: {"mevduat": 0.0, "diger": 0.0})
    for arac, alacakli, borclu, stok, karsi_yok in KENAR:
        if karsi_yok:
            continue
        kutu = yon[(alacakli, borclu)]
        if arac == "mevduat":
            kutu["mevduat"] += stok
        else:
            kutu["diger"] += stok
    return yon


def stok_silim_ayak() -> dict:
    """Mevduat ayağı. Öncelik iki uçta da aynı sonucu vermeli; vermezse dur."""
    yon = _yon_topla()
    gorulen: set[frozenset[str]] = set()
    ciftler = []
    for (a, b), kutu in sorted(yon.items()):
        pair = frozenset((a, b))
        if pair in gorulen or a == b:
            continue
        gorulen.add(pair)
        rev = yon.get((b, a))
        if rev is None:
            continue
        ileri = kutu["mevduat"] + kutu["diger"]
        geri = rev["mevduat"] + rev["diger"]
        if geri > ileri:
            a, b, kutu, rev, ileri, geri = b, a, rev, kutu, geri, ileri
        silinen = min(ileri, geri)
        def ayak(k, sil):
            once = min(k["mevduat"], sil)  # mevduat önce silinir
            son = max(0.0, sil - k["diger"])  # mevduat en son
            if abs(once - son) > 1e-9:
                raise RuntimeError(f"mevduat önceliği ısırdı: {once} vs {son}")
            return once
        dep = ayak(kutu, silinen) + ayak(rev, silinen)
        yurtici = dep if not ({a, b} == {"PFK", "ROW"}) else 0.0
        yurtdisi = dep if {a, b} == {"PFK", "ROW"} else 0.0
        ciftler.append({
            "cift": f"{a}–{b}",
            "silinen": silinen,
            "mevduat_ayak": dep,
            "yurtici": yurtici,
            "yurtdisi": yurtdisi,
        })
    yurtici = sum(c["yurtici"] for c in ciftler)
    yurtdisi = sum(c["yurtdisi"] for c in ciftler)
    silinen = sum(c["silinen"] for c in ciftler)
    if abs(silinen - 18000) > 1e-6:
        raise RuntimeError(f"birleşik silinen 18000 değil: {silinen}")
    if abs(yurtici - (7195 + 6772)) > 1e-6:
        raise RuntimeError(f"yurt içi ayak tutmuyor: {yurtici}")
    return {
        "ayri": {"mevduat_ayak": 0.0, "m2": 0.0, "etiket": "kanıt"},
        "mahsup_0421": {"mevduat_ayak": 0.0, "m2": 0.0, "etiket": "kanıt"},
        "birlesik": {
            "ciftler": ciftler,
            "silinen": silinen,
            "mevduat_ayak_yurtici": yurtici,
            "mevduat_ayak_yurtdisi": yurtdisi,
            "m2_aday": yurtici,
            "etiket_ayak": "kanıt",
            "etiket_m2": "aday",
        },
    }


def adim4(theta: float, chi: float, adres: float) -> dict:
    tepe = theta * adres
    kalici = chi * tepe
    return {
        "tepe": round(tepe, 4),
        "kalici": round(kalici, 4),
        "ikinci_tur_tepe_yillik": round(KREDI_PAY * tepe, 4),
        "ikinci_tur_kalici_yillik": round(KREDI_PAY * kalici, 4),
        "etiket_aritmetik": "kanıt",
        "etiket_m2": "aday",
        "etiket_ikinci_tur": "aday",
    }


def senaryo_satir(s: dict, ayak: dict, m2: float) -> dict:
    a4 = adim4(s["theta"], s["chi"], s["adres"])
    adim12 = 0.0 if s["adim12"] == "ayri" else ayak["birlesik"]["m2_aday"]
    adim12_etiket = "kanıt" if s["adim12"] == "ayri" else "aday"
    # Başlık: stok. Adım 3, 4.5, 5 doğrudan 0.
    baslik = adim12 + a4["kalici"]
    return {
        "ad": s["ad"],
        "theta": s["theta"],
        "chi": s["chi"],
        "adres": s["adres"],
        "adim12_sutun": s["adim12"],
        "adim12_m2": adim12,
        "adim12_etiket": adim12_etiket,
        "adim3_m2": 0.0,
        "adim45_m2": 0.0,
        "adim5_m2": 0.0,
        "adim4_tepe": a4["tepe"],
        "adim4_kalici": a4["kalici"],
        "ikinci_tur_tepe_yillik": a4["ikinci_tur_tepe_yillik"],
        "ikinci_tur_kalici_yillik": a4["ikinci_tur_kalici_yillik"],
        "baslik_stok": round(baslik, 4),
        "baslik_yuzde": round(100.0 * baslik / m2, 4),
        "tepe_stok": round(adim12 + a4["tepe"], 4),
        "tepe_yuzde": round(100.0 * (adim12 + a4["tepe"]) / m2, 4),
        "etiket_adim4": "aday",
        "etiket_345": "kanıt",
    }


def _yuzde(x: float, m2: float) -> float:
    return round(100.0 * x / m2, 2)


def rapor(d: dict) -> str:
    m = d["m2"]["milyar"]
    ay = d["adim12"]
    b = ay["birlesik"]
    def ml(x):
        return f"{x:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def yp(x):
        return f"%{x:.2f}".replace(".", ",")

    satir = []
    for s in d["senaryo"]:
        satir.append(
            f"| {s['ad']} | {s['theta']} | {s['chi']} | {ml(s['adres'])} | {s['adim12_sutun']} | "
            f"{ml(s['adim4_tepe'])} | {yp(100.0 * s['adim4_tepe'] / m['m2'])} | {ml(s['adim4_kalici'])} | {ml(s['baslik_stok'])} | "
            f"{yp(s['baslik_yuzde'])} | {ml(s['ikinci_tur_tepe_yillik'])} | {ml(s['ikinci_tur_kalici_yillik'])} |"
        )
    return "\n".join([
        "# Beş adımın M2 etkisi",
        "",
        "Kurallar `M2_YANLISLAMA.md` dosyasında kilitlendi; bu sayılar ondan sonra üretildi. "
        f"Kriter özeti `{d['kriter_sha256'][:12]}`.",
        "",
        "## M2 düzeyi",
        "",
        f"**Kanıt.** TCMB EVDS3, grup `bie_hpbitablo1` (Para Arzı), hafta {d['hafta']}. "
        "Ham birim bin TL; milyar TL = ham / 1e6. Birim çapası: 2026-03 "
        f"`TP.KM.E041 + TP.KB.FON033` = {d['birim_capasi']['milyar']} milyar TL, "
        f"repodaki 8.037,1 ile örtüşür (fark {d['birim_capasi']['fark']}).",
        "",
        f"| Kalem | milyar TL | M2 payı |",
        f"| --- | ---: | ---: |",
        f"| Dolaşımdaki para | {ml(m['dolasim'])} | {yp(_yuzde(m['dolasim'], m['m2']))} |",
        f"| Vadesiz TL | {ml(m['vadesiz_tl'])} | {yp(_yuzde(m['vadesiz_tl'], m['m2']))} |",
        f"| Vadeli TL | {ml(m['vadeli_tl'])} | {yp(_yuzde(m['vadeli_tl'], m['m2']))} |",
        f"| **M2 TL kısmı** | **{ml(m['tl'])}** | {yp(_yuzde(m['tl'], m['m2']))} |",
        f"| Vadesiz YP | {ml(m['vadesiz_yp'])} | {yp(_yuzde(m['vadesiz_yp'], m['m2']))} |",
        f"| Vadeli YP | {ml(m['vadeli_yp'])} | {yp(_yuzde(m['vadeli_yp'], m['m2']))} |",
        f"| **M2 YP kısmı** | **{ml(m['yp'])}** | {yp(_yuzde(m['yp'], m['m2']))} |",
        f"| **M2** | **{ml(m['m2'])}** | %100 |",
        f"| M3 menkul (3.3) | {ml(m['menkul'])} | M2 dışı |",
        f"| M3 | {ml(m['m3'])} | |",
        "",
        "M2 = TL kısmı + YP kısmı, sapma 0,05 milyar TL altında. "
        "M3 = M2 + repo + para piyasası fonu + ihraç edilen menkul. Menkul satırı M2 toplamına girmez.",
        "",
        "## 16.472,8 ile M2",
        "",
        f"**Kanıt.** TL para stoku 16.472,8 = emisyon {EMISYON} + tablo 3 yurt içi TL mevduat {TL_MEVDUAT_TABLO3} "
        f"(`adim45_birim.py`: «M1 değildir»). Aynı çeyreğin M2'si {ml(m['m2'])} milyar TL'dir. "
        f"Fark {ml(m['m2'] - TL_PARA_STOKU)} milyar TL. Eşitlik iddiası düşer.",
        "",
        "Farkın yazılabilen kanalları, ölçülmüş ayrıntı uydurulmadan:",
        "",
        f"- M2'nin YP kısmı {ml(m['yp'])} milyar TL'dir; 16.472,8 YP içermez. YP tek başına farkı aşar "
        f"({ml(m['yp'])} > {ml(m['m2'] - TL_PARA_STOKU)}): TL tarafları da aynı stok değildir.",
        "- 898,3 emisyondur, banka kasasını içerir. M2 dolaşımdaki parayı kullanır "
        f"({ml(m['dolasim'])}, haftalık). İki nakit ölçümü aynı an ve aynı tanımdır denmez.",
        f"- Tablo 3 TL mevduatı 15.574,5; M2'nin TL mevduatı (vadesiz + vadeli) "
        f"{ml(m['vadesiz_tl'] + m['vadeli_tl'])}. Kapsamlar ayrı yayımlanır.",
        "",
        "## Senet",
        "",
        "**Kanıt.** M2 bileşenleri dolaşımdaki para, vadesiz mevduat (TL ve YP) ve vadeli mevduat (TL ve YP). "
        "İhraç edilen menkul M3'ün 3.3 satırıdır, M2 toplamının içinde değildir. "
        f"Bu hafta o satır {ml(m['menkul'])} milyar TL. Repodaki 27.03.2026 DİBS stoku {DIBS_2026_03_27} milyar TL. "
        "Menkul satırı DİBS stoğu değildir. Hazine kâğıdı da banka kâğıdı da M2 toplananı değildir. "
        "Adım 4 SFC'si zaten VF.2'yi düşürüp VF.3'ü artırır. YP mevduat M2'nin içindedir; senede çıkan YP mevduat da M2'den çıkar.",
        "",
        "## Adım 1–2",
        "",
        "| | Araç ayrı | Araç birleşik |",
        "| --- | ---: | ---: |",
        f"| Mahsup 0,421, mevduat ayağı | 0 | 0 |",
        f"| Mahsup, M2 | 0 (**kanıt**) | 0 (**kanıt**) |",
        f"| Stok silimi, mevduat ayağı yurt içi | 0 | {ml(b['mevduat_ayak_yurtici'])} |",
        f"| Stok silimi, mevduat ayağı yurt dışı | 0 | {ml(b['mevduat_ayak_yurtdisi'])} |",
        f"| Stok silimi, M2 | 0 (**kanıt**) | {ml(b['m2_aday'])} (**aday**) |",
        "",
        "**Kanıt.** Mahsup, net pozisyonu sabit tutan bir akış oranıdır; mevduat stoku çıktısı yoktur. "
        "Araç ayrıda silinen 0; H–PFK ve F–PFK mevduat karşı bacağı yapısal 0'dır. "
        f"Birleşik üç çiftin silineni {ml(b['silinen'])} (F–PFK 7.195, H–PFK 6.772, PFK–ROW 4.033). "
        "İlk iki çiftte küçük bacak mevduattır: yurt içi mevduat ayağı 7.195 + 6.772. "
        "PFK–ROW'da alacaklı PFK, borçlu ROW: 4.033 yurt dışı mevduat varlığıdır, Türkiye M2'sine yazılmaz. "
        "Yurt içi ayağın M2'ye birebir inmesi adaydır: PFK bankadan ayrılmamıştır, metin kısmi çifttir, H-S bu sütunu skorlamaz.",
        "",
        "## Adım 3, 4.5, 5",
        "",
        "| Adım | Doğrudan M2 | Etiket |",
        "| --- | ---: | --- |",
        "| 3 faiz durması | 0 | **kanıt** (anapara ve mevduat stoku düşmez; faiz akışının mevduata oranı ölçülmedi, dolaylı tutar yok) |",
        "| 4.5 yeni birim, λ = 1 | 0 | **kanıt** (TL_yeni = TL_eski) |",
        "| 5 kira, Ho → Ha | 0 | **kanıt** (iki hane arasında aktarım) |",
        "",
        "## Adım 4 ve senaryolar",
        "",
        "Adresin M2'ye giren ayrı stoku 12.722,5 ile 19.076,6 arasındadır (**kanıt**, örtüşme aritmetiği). "
        "θ × bu stokun M2'den çıkması **aday**dır: VF.2 ZP8 ile HPB mevduatı aynı çevre diye ölçülmedi. "
        "Tepe = θ × adres. Kalıcı = χ × tepe. İkinci tur = 0,08 × eldeki stok, milyar TL/yıl, **aday**; stok toplamına eklenmez.",
        "",
        "| Senaryo | θ | χ | Adres | Adım 1–2 | Adım 4 tepe | Adım 4 tepe / M2 | Kalıcı | Başlık stok | Başlık / M2 | 2. tur tepe /yıl | 2. tur kalıcı /yıl |",
        "| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        *satir,
        "",
        "Başlık = adım 1–2 M2 + adım 4 kalıcı + adım 3/4.5/5 (0). Tepe başlığa girmez: senet eldeyken görülen düşüştür, vade sonunda χ payı kalır. "
        "Düşükte χ = 0 olduğu için kalıcı birinci tur 0'dır; senet vadesinde mevduata döner. "
        f"Yüksek başlığın {ml(d['senaryo'][2]['adim12_m2'])} milyar TL'si araç birleşik yurt içi ayaktır ve adaydır. "
        f"Bu aday çıkarılırsa yüksek başlık {ml(d['senaryo'][2]['adim4_kalici'])} milyar TL, "
        f"{yp(100.0 * d['senaryo'][2]['adim4_kalici'] / m['m2'])} olur. "
        f"Aday silim dururken senet tepedeyse toplam {ml(d['senaryo'][2]['adim12_m2'] + d['senaryo'][2]['adim4_tepe'])} milyar TL, "
        f"{yp(100.0 * (d['senaryo'][2]['adim12_m2'] + d['senaryo'][2]['adim4_tepe']) / m['m2'])} olur; bu başlık değildir.",
        "",
        "Adım adım, başlık stokunun içinde (milyar TL):",
        "",
        "| Adım | düşük | orta | yüksek |",
        "| --- | ---: | ---: | ---: |",
        _adim_tablosu(d),
        "",
        "İkinci tur bu tabloda yoktur. Düşük senaryoda tepe ikinci tur "
        f"{ml(d['senaryo'][0]['ikinci_tur_tepe_yillik'])} milyar TL/yıldır ve vade sonunda 0'a iner. "
        f"Ortada tepe {ml(d['senaryo'][1]['ikinci_tur_tepe_yillik'])}, kalıcı {ml(d['senaryo'][1]['ikinci_tur_kalici_yillik'])}. "
        f"Yüksekte tepe {ml(d['senaryo'][2]['ikinci_tur_tepe_yillik'])}, kalıcı {ml(d['senaryo'][2]['ikinci_tur_kalici_yillik'])}.",
        "",
    ])


def _adim_tablosu(d: dict) -> str:
    def hucre(s, anahtar):
        return f"{s[anahtar]:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
    satirlar = {
        "1–2 mahsup ve stok": "adim12_m2",
        "3": "adim3_m2",
        "4 kalıcı": "adim4_kalici",
        "4.5": "adim45_m2",
        "5": "adim5_m2",
        "Başlık": "baslik_stok",
    }
    out = []
    for ad, k in satirlar.items():
        h = " | ".join(hucre(s, k) for s in d["senaryo"])
        out.append(f"| {ad} | {h} |")
    yuzde = " | ".join(f"%{s['baslik_yuzde']:.2f}".replace(".", ",") for s in d["senaryo"])
    out.append(f"| Başlık / M2 | {yuzde} |")
    return "\n".join(out)


def main() -> dict:
    if not KRITER.exists():
        raise SystemExit("kriter dosyası yok")
    cap = birim_capasi()
    if abs(cap["milyar"] - cap["repo_karsilik"]) > 0.15:
        raise SystemExit(f"birim çapası tutmuyor: {cap['milyar']}")
    cap["fark"] = round(cap["milyar"] - cap["repo_karsilik"], 4)
    if abs(HANE_VADELI + FIRMA_VADELI + GERCEK_YP - ADRES_HAM) > 1e-6:
        raise SystemExit("adres toplamı tutmuyor")
    if abs(ADRES_HAM - ORTUSME_UST - A_ALT) > 1e-6 or abs(ADRES_HAM - ORTUSME_ALT - A_UST) > 1e-6:
        raise SystemExit("örtüşme bandı tutmuyor")
    hafta = evds_hafta()
    parca = m2_parcala(hafta["ham_bin_tl"])
    ayak = stok_silim_ayak()
    m2 = parca["milyar"]["m2"]
    sen = [senaryo_satir(s, ayak, m2) for s in SENARYO]
    tl_fark = {
        "tl_para_stoku": TL_PARA_STOKU,
        "m2": parca["milyar"]["m2"],
        "fark": round(parca["milyar"]["m2"] - TL_PARA_STOKU, 4),
        "esitlik": "dustu",
        "etiket": "kanıt",
    }
    doc = {
        "kriter_sha256": _sha(KRITER),
        "hafta": hafta["tarih"],
        "birim": "ham bin TL; milyar = ham/1e6",
        "birim_capasi": cap,
        "m2": parca,
        "tl_para_stoku": tl_fark,
        "senet_m2_disinda": True,
        "senet_etiket": "kanıt",
        "dibs_milyar": DIBS_2026_03_27,
        "menkul_dibs_degil": parca["milyar"]["menkul"] < DIBS_2026_03_27 / 10,
        "adim12": ayak,
        "adim345": {"adim3": 0.0, "adim45": 0.0, "adim5": 0.0, "etiket": "kanıt"},
        "senaryo": sen,
        "ad": hafta["ad"],
    }
    HAM.write_text(json.dumps({"tarih": hafta["tarih"], "ad": hafta["ad"], "ham_bin_tl": hafta["ham_bin_tl"]}, ensure_ascii=False, indent=2), encoding="utf-8")
    CIKTI.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    RAPOR.write_text(rapor(doc), encoding="utf-8")
    return doc


if __name__ == "__main__":
    main()
