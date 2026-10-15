#!/usr/bin/env python3
"""Dört kapı. Kuramı doğrulamaz. Ayırt edilemeyen satır lehte yazılmaz.

Kurallar, sonuçtan önce:
- Karar yönü: faiz artışı sıkı, azalış gevşek, eşit değil.
- Geri adım: son sıfır-dışı işaret ile yeni işaret ters ise ters, aynı ise devam.
- Gecikme kovası: rol başlangıcından ilk sıfır-dışı karara gün < 32 ise kısa, değilse uzun.
- Aynı ISO haftasında TCMB rol kararı ile PPK kararı varsa satır çöp. İki tarafa da yazılmaz.
- Beyan ile sonraki sıfır-dışı karar arasında TCMB rol kararı varsa satır çöp.
- Kasa sıkılığı, tur1 satırında belirsiz kalır. Kilit öncesi hücre sıkıya çevrilmez.
- tur2 satırı: karar haftasında USD/TRY yukarı ve TP.AB.TOPLAM aşağı ise sıkı adayı. Değilse belirsiz. Gevşek kodu yok.
- Haftalık birincil net rezerv serisi doğrulanmadı. Swap stoku net rezerv diye birleştirilmez.
- Cari denge aylıktır. Haftalık kasa kuralına girmez.
- Hizip kodu boşsa hizip cümlesi yazılmaz. Kohort ve aynı karar numarası hizip değildir.
- Destek yalnız yanlışlayıcı tutmamış ve ayırt eden satır varsa.
- "Ayakta değil" yazılmaz.
"""

from __future__ import annotations

import csv
import json
import sys
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

KOK = Path(__file__).resolve().parent
EVDS = "https://evds3.tcmb.gov.tr/igmevdsms-dis"
KISA_GUN = 32
ONBELLEK = KOK / "kapi_evds_onbellek.json"


def tarih(s: str) -> date | None:
    s = (s or "").strip()
    if not s:
        return None
    return datetime.strptime(s, "%Y-%m-%d").date()


def oku(ad: str) -> list[dict]:
    with (KOK / ad).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def yaz(ad: str, alanlar: list[str], satirlar: list[dict]) -> None:
    with (KOK / ad).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=alanlar, extrasaction="ignore")
        w.writeheader()
        w.writerows(satirlar)


def iso_hafta(d: date) -> tuple[int, int]:
    iso = d.isocalendar()
    return (iso[0], iso[1])


def evds_cek(seriler: list[str], bas: str, bit: str, frekans: str, agg: str) -> list[dict]:
    n = len(seriler)
    govde = {
        "type": "json",
        "series": "-".join(seriler),
        "aggregationTypes": "-".join([agg] * n),
        "formulas": "-".join(["0"] * n),
        "startDate": bas,
        "endDate": bit,
        "frequency": frekans,
        "decimalSeperator": ".",
        "decimal": "4",
        "dateFormat": "0",
        "lang": "TR",
        "yon": "0",
        "sira": "0",
        "ozelFormuller": [],
        "groupSeperator": False,
        "isRaporSayfasi": False,
    }
    istek = urllib.request.Request(
        f"{EVDS}/fe",
        data=json.dumps(govde).encode(),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "kapi-arastirma",
        },
        method="POST",
    )
    with urllib.request.urlopen(istek, timeout=180) as r:
        veri = json.loads(r.read().decode("utf-8-sig"))
    return veri["items"]


def sayi(v) -> float | None:
    if v in (None, ""):
        return None
    return float(str(v).replace(",", ""))


def evds_yukle() -> dict:
    if ONBELLEK.exists():
        on = json.loads(ONBELLEK.read_text(encoding="utf-8"))
    else:
        on = {}
    try:
        if "kur" not in on:
            on["kur"] = evds_cek(["TP.DK.USD.A.YTL"], "01-01-2018", "09-10-2026", "1", "last")
        if "brut" not in on:
            on["brut"] = evds_cek(["TP.AB.TOPLAM"], "01-01-2018", "09-10-2026", "3", "last")
        if "cari" not in on:
            on["cari"] = evds_cek(["TP.ODANA6.Q01"], "01-01-2018", "01-09-2026", "5", "sum")
        ONBELLEK.write_text(json.dumps(on), encoding="utf-8")
        on["hata"] = ""
    except Exception as exc:  # noqa: BLE001
        on["hata"] = f"{type(exc).__name__}: {exc}"
        if not on.get("kur"):
            on["kur_aciklamadi"] = "TP.DK.USD.A.YTL acilamadi"
        if not on.get("brut"):
            on["brut_aciklamadi"] = "TP.AB.TOPLAM acilamadi"
    return on


def seri_harita(kayitlar: list[dict], anahtar: str, deger: str) -> dict[date, float]:
    out = {}
    for it in kayitlar or []:
        ham = str(it.get("Tarih", ""))
        for bicim in ("%d-%m-%Y", "%Y-%m-%d", "%Y-%m"):
            try:
                if bicim == "%Y-%m":
                    d = datetime.strptime(ham, bicim).date().replace(day=1)
                else:
                    d = datetime.strptime(ham, bicim).date()
                break
            except ValueError:
                d = None
        if d is None:
            continue
        v = sayi(it.get(deger))
        if v is not None:
            out[d] = v
    return out


def onceki_deger(harita: dict[date, float], gun: date) -> tuple[date | None, float | None]:
    aday = [d for d in harita if d <= gun]
    if not aday:
        return None, None
    d = max(aday)
    return d, harita[d]


def yon_faiz(once: float, sonra: float) -> str:
    if sonra > once:
        return "siki"
    if sonra < once:
        return "gevsek"
    return "degil"


def isaret(yon: str) -> int:
    if yon == "siki":
        return 1
    if yon == "gevsek":
        return -1
    return 0


def ay_fark(a: date, b: date) -> str:
    return f"{(b - a).days / 30.437:.1f}"


def main() -> int:
    roller = oku("kapi_rol_donemi.csv")
    kararlar = oku("kapi_ppk_karar.csv")
    beyanlar = oku("kapi_beyan.csv")
    evds = evds_yukle()

    for k in kararlar:
        k["gun"] = tarih(k["tarih"])
        k["once"] = float(k["faiz_once"])
        k["sonra"] = float(k["faiz_sonra"])
        k["yon"] = yon_faiz(k["once"], k["sonra"])
        k["hafta"] = iso_hafta(k["gun"])

    tcmb = [r for r in roller if r["rol"].startswith("TCMB")]
    gecisler = []
    for r in tcmb:
        for alan in ("karar_baslangic", "karar_bitis"):
            d = tarih(r[alan])
            if d:
                gecisler.append({"gun": d, "hafta": iso_hafta(d), "rol_id": r["rol_id"], "alan": alan})

    gecis_hafta = {g["hafta"] for g in gecisler}
    for k in kararlar:
        k["cop"] = k["hafta"] in gecis_hafta
        k["cop_neden"] = "ayni_iso_hafta_tcmb_rol_karari" if k["cop"] else ""

    kur = seri_harita(evds.get("kur"), "Tarih", "TP_DK_USD_A_YTL")
    brut = seri_harita(evds.get("brut"), "Tarih", "TP_AB_TOPLAM")
    cari = {}
    for it in evds.get("cari") or []:
        ham = str(it.get("Tarih", ""))
        try:
            d = datetime.strptime(ham, "%Y-%m").date()
        except ValueError:
            continue
        v = sayi(it.get("TP_ODANA6_Q01"))
        if v is not None:
            cari[d] = v

    kasa_satir = []
    for k in kararlar:
        if k["yon"] == "degil":
            continue
        kur_gun, kur_simdi = onceki_deger(kur, k["gun"])
        kur_eski_gun, kur_eski = onceki_deger(kur, k["gun"] - timedelta(days=7))
        if kur_simdi is None or kur_eski is None:
            kur_yon = "seri_yok"
        elif kur_simdi > kur_eski:
            kur_yon = "yukari"
        elif kur_simdi < kur_eski:
            kur_yon = "asagi"
        else:
            kur_yon = "yatay"
        # Karar haftasının Cuma gözlemi: o ISO haftasının en geç brüt tarihi, önceki haftadan küçük eşit.
        hafta_bitis = k["gun"] + timedelta(days=(4 - k["gun"].weekday()) % 7)
        brut_gun, brut_simdi = onceki_deger(brut, hafta_bitis)
        brut_eski_gun, brut_eski = onceki_deger(brut, (brut_gun - timedelta(days=1)) if brut_gun else hafta_bitis)
        if brut_gun and brut_eski_gun and iso_hafta(brut_gun) != k["hafta"]:
            brut_yon = "hafta_gozlemi_yok"
            brut_simdi = None
        elif brut_simdi is None or brut_eski is None:
            brut_yon = "seri_yok"
        elif brut_simdi > brut_eski:
            brut_yon = "yukari"
        elif brut_simdi < brut_eski:
            brut_yon = "asagi"
        else:
            brut_yon = "yatay"
        ay = date(k["gun"].year, k["gun"].month, 1)
        cari_v = cari.get(ay)
        if cari_v is None:
            cari_yon = "seri_yok"
        elif cari_v < 0:
            cari_yon = "acik"
        elif cari_v > 0:
            cari_yon = "fazla"
        else:
            cari_yon = "sifir"
        kasa_satir.append({
            "tarih": k["tarih"],
            "yon": k["yon"],
            "cop": int(k["cop"]),
            "kur_yon": kur_yon,
            "kur_once": "" if kur_eski is None else f"{kur_eski:.4f}",
            "kur_sonra": "" if kur_simdi is None else f"{kur_simdi:.4f}",
            "brut_yon": brut_yon,
            "brut_once": "" if brut_eski is None else f"{brut_eski:.1f}",
            "brut_sonra": "" if brut_simdi is None else f"{brut_simdi:.1f}",
            "net_yon": "birincil_seri_yok",
            "cari_ay_yon": cari_yon,
            "cari_deger": "" if cari_v is None else f"{cari_v:.1f}",
            "kural": k.get("kural") or "tur1",
            "kasa_sikilik": "belirsiz",
            "kasa_neden": "",
        })
    for row, k in zip(kasa_satir, [x for x in kararlar if x["yon"] != "degil"]):
        if row["kural"] != "tur2":
            row["kasa_sikilik"] = "belirsiz"
            row["kasa_neden"] = "kilit oncesi satir; eski belirsiz hucre sikiliga cevrilmedi"
        elif row["kur_yon"] == "yukari" and row["brut_yon"] == "asagi":
            row["kasa_sikilik"] = "siki_aday"
            row["kasa_neden"] = "kilit: kur yukari ve TP.AB.TOPLAM asagi"
        else:
            row["kasa_sikilik"] = "belirsiz"
            row["kasa_neden"] = "kilit: iki yon ayni degil veya gozlem yok; gevsek kodu yok"

    onceki_yon = None
    for k in kararlar:
        if k["yon"] == "degil":
            k["geri_adim"] = "degil"
            continue
        if onceki_yon is None:
            k["geri_adim"] = "onceki_yok"
        elif isaret(k["yon"]) != isaret(onceki_yon):
            k["geri_adim"] = "ters"
        else:
            k["geri_adim"] = "devam"
        onceki_yon = k["yon"]
    geri_harita = {k["tarih"]: k["geri_adim"] for k in kararlar}
    for row in kasa_satir:
        row["geri_adim"] = geri_harita.get(row["tarih"], "")

    # TCMB rol profili
    def sifir_disi(gun: date, once: bool) -> dict | None:
        havuz = [k for k in kararlar if not k["cop"] and k["yon"] != "degil"]
        if once:
            havuz = [k for k in havuz if k["gun"] < gun]
            return havuz[-1] if havuz else None
        havuz = [k for k in havuz if k["gun"] > gun]
        return havuz[0] if havuz else None

    profiller = []
    for r in tcmb:
        bas = tarih(r["karar_baslangic"])
        if bas is None:
            continue
        ilk = sifir_disi(bas, once=False)
        son_once = sifir_disi(bas, once=True)
        if ilk is None or son_once is None:
            neden = "ilk_karar_gunu_acilmadi" if ilk is None else "onceki_karar_yok"
            profiller.append({
                "rol_id": r["rol_id"],
                "ad_rg": r["ad_rg"],
                "bas": bas,
                "durum": neden,
            })
            continue
        gun = (ilk["gun"] - bas).days
        kova = "kisa" if gun < KISA_GUN else "uzun"
        kural = "ters" if isaret(ilk["yon"]) != isaret(son_once["yon"]) else "devam"
        profiller.append({
            "rol_id": r["rol_id"],
            "ad_rg": r["ad_rg"],
            "bas": bas,
            "ilk_tarih": ilk["tarih"],
            "ilk_yon": ilk["yon"],
            "onceki_tarih": son_once["tarih"],
            "onceki_yon": son_once["yon"],
            "gecikme_gun": gun,
            "gecikme_kova": kova,
            "geri_adim_kurali": kural,
            "durum": "olculdu",
        })

    olculen = [p for p in profiller if p["durum"] == "olculdu"]
    donumler = []
    for a, b in zip(olculen, olculen[1:]):
        gecikme_kaydi = a["gecikme_kova"] != b["gecikme_kova"]
        kural_kaydi = a["geri_adim_kurali"] != b["geri_adim_kurali"]
        kayma = int(gecikme_kaydi) + int(kural_kaydi)
        donumler.append({
            "onceki": a["rol_id"],
            "sonraki": b["rol_id"],
            "gecikme": f"{a['gecikme_kova']}->{b['gecikme_kova']}",
            "kural": f"{a['geri_adim_kurali']}->{b['geri_adim_kurali']}",
            "kayma_sayisi": kayma,
            "yanlislayici": "tuttu" if kayma >= 2 else "tutmadi",
            "yaptirim": "yok",
        })

    # Zaman ölçümü. Küme şartı kapalı: hizip yok, kabine gün gün taranmadı.
    zaman = []
    cop_zaman = 0
    for b in beyanlar:
        bg = tarih(b["beyan_tarih"])
        sonraki = next((k for k in kararlar if k["gun"] > bg and k["yon"] != "degil"), None)
        onceki = next((k for k in reversed(kararlar) if k["gun"] < bg and k["yon"] != "degil"), None)
        arada = []
        if sonraki:
            arada = [g for g in gecisler if bg < g["gun"] < sonraki["gun"]]
        cop = bool(arada)
        if cop:
            cop_zaman += 1
        if onceki and b["yon_ilan"] in ("indirim", "siki"):
            yon_degisti = (b["yon_ilan"] == "indirim" and onceki["yon"] == "siki") or (
                b["yon_ilan"] == "siki" and onceki["yon"] == "gevsek"
            )
        else:
            yon_degisti = False
        ongordu = False
        if sonraki and b["yon_ilan"] == "indirim" and sonraki["yon"] == "gevsek":
            ongordu = True
        if sonraki and b["yon_ilan"] == "siki" and sonraki["yon"] == "siki":
            ongordu = True
        gun_ara = (sonraki["gun"] - bg).days if sonraki else ""
        zaman.append({
            "beyan_id": b["beyan_id"],
            "beyan_tarih": b["beyan_tarih"],
            "sonraki_karar": sonraki["tarih"] if sonraki else "",
            "gun": gun_ara,
            "yon_ilan": b["yon_ilan"],
            "yon_degisti": int(yon_degisti),
            "ongordu": int(ongordu),
            "cop": int(cop),
            "kume": "hizip_yok_kabine_taranmadi",
            "lehte": "hayir",
        })

    cop_kasa = sum(1 for k in kararlar if k["cop"] and k["yon"] != "degil")
    hc_tutan = sum(1 for d in donumler if d["yanlislayici"] == "tuttu")
    hc_tutmayan = sum(1 for d in donumler if d["yanlislayici"] == "tutmadi")

    if not donumler:
        hc = "test edilemez"
        hc_taraf = "yok"
        hc_ayirt = "hayır"
    elif hc_tutan and hc_tutmayan:
        hc = "karışık"
        hc_taraf = "rol düzeyi karışık; hizip adı yok"
        hc_ayirt = "kısmi"
    elif hc_tutan and not hc_tutmayan:
        hc = "yanlışlıyor"
        hc_taraf = "rol düzeyi iki gösterge kaydı; hizip adı yok"
        hc_ayirt = "evet"
    else:
        hc = "test edilemez"
        hc_taraf = "yok"
        hc_ayirt = "hayır"

    kapilar = [
        {
            "kapi": "zaman",
            "veri": "var",
            "ayirt_etti": "hayır",
            "taraf": "yok",
            "cop_satir": cop_zaman,
            "guven": "düşük",
            "neden": "Beyan ve karar günü var. Hizip kaydı yok. Kabine gün gün taranmadı. Küme sabit kapanmadan lehte yazılmadı.",
        },
        {
            "kapi": "ceza",
            "veri": "yok",
            "ayirt_etti": "hayır",
            "taraf": "yok",
            "cop_satir": 0,
            "guven": "yok",
            "neden": "4483 merci çarpı verildi çarpı suç tipi çarpı küme yok. Adalet İstatistikleri 2025 yalnız agregat satır.",
        },
        {
            "kapi": "tabela",
            "veri": "kısmi",
            "ayirt_etti": hc_ayirt,
            "taraf": hc_taraf,
            "cop_satir": cop_kasa,
            "guven": "düşük",
            "neden": f"Dönüm {len(donumler)}. İki gösterge birlikte kayan {hc_tutan} rol kuralı kaydıdır. Kaymayan {hc_tutmayan}. Yaptırım boş. Hizip adı yok.",
        },
        {
            "kapi": "kasa",
            "veri": "kısmi",
            "ayirt_etti": "hayır",
            "taraf": "yok",
            "cop_satir": cop_kasa,
            "guven": "düşük",
            "neden": "",
        },
        {
            "kapi": "nusha",
            "veri": "var",
            "ayirt_etti": "hayır",
            "taraf": "yok",
            "cop_satir": 0,
            "guven": "orta",
            "neden": "2023/284 ek listesi 20230604-1.pdf içinde okundu. Altı koltukta bitiş bulundu. Aynı karar atama kümesidir. Hizip kodu boş. Yeni atananların kendi bitişi bulunamadı.",
        },
    ]

    tur2_geri = [
        r for r in kasa_satir
        if r["kural"] == "tur2" and r["geri_adim"] == "ters" and r["cop"] == 0
    ]
    tur2_siki = [r for r in tur2_geri if r["kasa_sikilik"] == "siki_aday"]
    if not tur2_geri:
        hd = "test edilemez"
        hd_neden = "Yeni kodlanan geri adım satırı yok. Eski belirsiz satır teste girmedi."
        kasa_neden = "tur2 geri adım yok. Eski satır belirsiz kaldı."
    elif tur2_siki:
        hd = "test edilemez"
        tarihler = ", ".join(r["tarih"] for r in tur2_siki)
        hd_neden = (
            f"Sıkı adayı geri adım {len(tur2_siki)} ({tarihler}). Hizip kodu boş. "
            "Küme değişmeden şartı doğrulanamadı. Kasa gevşekken küme yenilgisi cümlesi yazılmadı."
        )
        kasa_neden = hd_neden
    else:
        hd = "test edilemez"
        hd_neden = (
            f"Yeni geri adım {len(tur2_geri)}. Kilit sıkı adayı demedi, belirsiz kaldı. "
            "Eski belirsiz hücre sıkıya çevrilmedi. Küme kodu yok."
        )
        kasa_neden = hd_neden
    for kapi in kapilar:
        if kapi["kapi"] == "kasa":
            kapi["neden"] = kasa_neden

    hipotez = [
        {
            "hipotez": "H-A",
            "sonuc": "test edilemez",
            "neden": "2024-W04, 2024-W12 ve 2024-W52 konuşmalar arşivi listesi kilitlendi, yön kodlanmadı. Eski beş konuşma evren değil. Küme sabit doğrulanamadı.",
        },
        {
            "hipotez": "H-B",
            "sonuc": "test edilemez",
            "neden": "4483 kırılımı yok. Katsayı yok. Haberle doldurulmadı.",
        },
        {
            "hipotez": "H-C",
            "sonuc": hc,
            "neden": "Rol dönümünde gecikme kovası ve geri adım kuralı. İki gösterge birlikte kayan dönüm rol kuralı kaydıdır. Hizip kodu boş. Oyuncu küme cümlesi yok.",
        },
        {
            "hipotez": "H-D",
            "sonuc": hd,
            "neden": hd_neden,
        },
        {
            "hipotez": "H-E",
            "sonuc": "test edilemez",
            "neden": "Hizip ve kasa kontrol edilemedi. Artık pay hesaplanmadı. Küçük n.",
        },
    ]

    teori = (
        "İkinci tur ölçümü. Nüsha: 2023/284 ek listesi okundu, ilgili koltuklarda bitiş bulundu. "
        "Aynı karar atama kümesidir, hizip kodu boş. "
        "Sıkılık kuralı yalnız tur2 satırında. "
        "Tıkaç adı konmadı: nüsha ile sıkılık aynı adı göstermiyor. "
        "Ceza kapalı. Bilgi kapısı açılmadı. Tek imza tıkaç ilanı değil."
    )

    yaz(
        "kapi_kasa_hafta.csv",
        ["tarih", "yon", "cop", "kural", "geri_adim", "kur_yon", "kur_once", "kur_sonra", "brut_yon", "brut_once", "brut_sonra",
         "net_yon", "cari_ay_yon", "cari_deger", "kasa_sikilik", "kasa_neden"],
        kasa_satir,
    )
    yaz("kapi_tablosu.csv", ["kapi", "veri", "ayirt_etti", "taraf", "cop_satir", "guven", "neden"], kapilar)
    yaz("kapi_hipotez.csv", ["hipotez", "sonuc", "neden"], hipotez)
    profil_yazi = []
    for p in profiller:
        profil_yazi.append({
            "rol_id": p["rol_id"],
            "ad_rg": p["ad_rg"],
            "bas": p["bas"].isoformat(),
            "durum": p["durum"],
            "ilk_tarih": p.get("ilk_tarih", ""),
            "ilk_yon": p.get("ilk_yon", ""),
            "onceki_tarih": p.get("onceki_tarih", ""),
            "onceki_yon": p.get("onceki_yon", ""),
            "gecikme_gun": p.get("gecikme_gun", ""),
            "gecikme_kova": p.get("gecikme_kova", ""),
            "geri_adim_kurali": p.get("geri_adim_kurali", ""),
        })
    yaz(
        "kapi_tabela_profil.csv",
        ["rol_id", "ad_rg", "bas", "durum", "ilk_tarih", "ilk_yon", "onceki_tarih", "onceki_yon",
         "gecikme_gun", "gecikme_kova", "geri_adim_kurali"],
        profil_yazi,
    )
    yaz(
        "kapi_tabela_donum.csv",
        ["onceki", "sonraki", "gecikme", "kural", "kayma_sayisi", "yanlislayici", "yaptirim"],
        donumler,
    )
    yaz(
        "kapi_zaman_olcum.csv",
        ["beyan_id", "beyan_tarih", "sonraki_karar", "gun", "yon_ilan", "yon_degisti", "ongordu", "cop", "kume", "lehte"],
        zaman,
    )

    sureler = []
    for r in roller:
        a, b = tarih(r["karar_baslangic"]), tarih(r["karar_bitis"])
        if a and b:
            sure = f"{(b - a).days / 30.437:.1f}"
        else:
            sure = ""
        sureler.append({**r, "sure_ay": sure})
    yaz("kapi_rol_sure.csv", list(sureler[0].keys()) if sureler else [], sureler)

    sonuc = {
        "teori": teori,
        "tikac_adi": "konmadi",
        "uyari": "Küçük n. OCR. Yeni atananların kendi bitişi bulunamadı. Haftalık net rezerv serisi doğrulanmadı. Hizip yok. 2023-06-23 ile 2024-01-24 arası gün satırı tek tek açılmadı. Kodlama hata payı var.",
        "nusha": "bitis_bulundu",
        "tikac_kapali": "ceza kapalı; bilgi kapısı açılmadı; sıkılık küme şartıyla ayırt etmedi",
        "evds_hata": evds.get("hata", ""),
        "cop_zaman": cop_zaman,
        "cop_kasa": cop_kasa,
    }
    (KOK / "kapi_sonuc.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8")

    print("KAPI")
    for k in kapilar:
        print(f"{k['kapi']}\tveri={k['veri']}\tayirt={k['ayirt_etti']}\ttaraf={k['taraf']}\tcop={k['cop_satir']}\tguven={k['guven']}")
    print("HIPOTEZ")
    for h in hipotez:
        print(f"{h['hipotez']}\t{h['sonuc']}")
    print("DONUM")
    for d in donumler:
        print(d)
    print("PROFIL")
    for p in profil_yazi:
        print(p["rol_id"], p["durum"], p.get("gecikme_gun"), p.get("gecikme_kova"), p.get("geri_adim_kurali"))
    print("TEORI")
    print(teori)
    if evds.get("hata"):
        print("EVDS", evds["hata"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
