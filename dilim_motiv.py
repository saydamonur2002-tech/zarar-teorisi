"""Dilim, motiv ve sızıntı (v4).

Uydurma yok: tabloda olmayan hücre boş kalır. Test eşikleri burada değiştirilmez.
K2 beklentisi, şoktan önceki yıl sonuna göre izleyen yıl sonunda dış borç stokunun
ve kısa vadeli payın birlikte artmasıdır. K3 beklentisi, kurun yükseldiği şok yılında
yerleşik hanehalkı döviz tevdiat payının artmasıdır.
"""
import json
import urllib.request
from pathlib import Path

import pandas as pd

KOK = Path(__file__).parent
HAM = KOK / "ham"
EVDS = "https://evds3.tcmb.gov.tr/igmevdsms-dis"
CEKIM = "16 Ekim 2026"

DILIMLER = ["alt20", "ikinci20", "orta20", "dorduncu20", "ust20"]
YILLAR = list(range(2018, 2026))
SOK = {
    2018: {"oncesi": 2017, "sok": 2018, "sonrasi": 2019},
    2021: {"oncesi": 2020, "sok": 2021, "sonrasi": 2022},
    2023: {"oncesi": 2022, "sok": 2023, "sonrasi": 2024, "ikinci": 2025},
}


def evds_json(url, body=None):
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        method="POST" if body is not None else "GET",
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode("utf-8-sig"))


def evds_cek(kodlar, bas, bit, frekans):
    body = {
        "type": "json",
        "series": "-".join(kodlar),
        "aggregationTypes": "-".join("last" for _ in kodlar),
        "formulas": "-".join("0" for _ in kodlar),
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
        "groupSeperator": True,
        "isRaporSayfasi": False,
    }
    rows = []
    for it in evds_json(f"{EVDS}/fe", body)["items"]:
        for c in kodlar:
            v = it.get(c.replace(".", "_"))
            if v not in (None, ""):
                rows.append((str(it["Tarih"]), c, float(str(v).replace(",", ""))))
    return pd.DataFrame(rows, columns=["donem", "seri", "deger"])


def yil_sonu(ham, seri, aylik=True):
    d = ham[ham.seri == seri].copy()
    if d.empty:
        return pd.Series(dtype=float)
    # Günlük kur dd-mm-yyyy gelir. Aralık ayının son iş günü yıl sonudur.
    if d.donem.str.match(r"\d{2}-\d{2}-\d{4}$").all():
        dt = pd.to_datetime(d.donem, format="%d-%m-%Y")
        d = d.assign(yil=dt.dt.year, ay=dt.dt.month, gun=dt.dt.day)
        d = d[d.ay == 12].sort_values(["yil", "gun"]).groupby("yil").tail(1)
        return d.set_index("yil").deger
    if aylik:
        d = d[d.donem.str.endswith("-12")]
        d["yil"] = d.donem.str.slice(0, 4).astype(int)
    else:
        d = d[d.donem.str.endswith("-Q4")]
        d["yil"] = d.donem.str.slice(0, 4).astype(int)
    return d.drop_duplicates("yil").set_index("yil").deger


def pay(a, b):
    if pd.isna(a) or pd.isna(b) or (a + b) == 0:
        return float("nan")
    return a / (a + b)


def bos_tablo():
    """Yıl × dilim × gösterge ızgarası. Değerler boş: yayımlanmış tablo klasörde yok."""
    notlar = {
        "mulk_geliri": "TÜİK Gelir ve Yaşam Koşulları, gelir türünün %20 dilim payı bu klasörde yok. 16 Ekim 2026 araması tablo dosyası vermedi.",
        "faiz_yuku": "Dilim faiz yükü tablosu yok. Ulusal hesap D.41 hanesi boş olduğu için yük hesaplanmadı.",
        "borc_yuku_cok_yuk": "TÜİK 'çok yük' oranının dilim tablosu bu klasörde yok.",
        "tuketim": "TÜİK Hanehalkı Bütçe Araştırması dilim tüketimi bu klasörde yok. Vekil olarak GSYH kullanılmadı.",
    }
    rows = []
    for yil in YILLAR:
        for dilim in DILIMLER:
            for gosterge, notu in notlar.items():
                for duzeltme in ("ham", "duzeltilmis"):
                    ek = notu
                    if duzeltme == "duzeltilmis":
                        ek += " Düzeltme yapılmadı: dilim payı ve ulusal hesap faiz/kira toplamı birlikte yok."
                    rows.append({
                        "yil": yil,
                        "dilim": dilim,
                        "gosterge": gosterge,
                        "deger": "",
                        "birim": "",
                        "duzeltme": duzeltme,
                        "kaynak": "veri yok",
                        "not": ek,
                    })
        rows.append({
            "yil": yil,
            "dilim": "hesap_dilimi",
            "gosterge": "mevduat_tutar",
            "deger": "",
            "birim": "",
            "duzeltme": "ham",
            "kaynak": "veri yok",
            "not": "TBB/BDDK mevduat tutar dilimi bu klasörde yok. Hesap dilimi hane dilimi değildir; olsaydı da 'alt %20 şunu aldı' denmeyecekti.",
        })
    return pd.DataFrame(rows)


def kanal():
    mev = evds_cek(
        ["TP.KM.E040", "TP.KM.E050", "TP.KM.E056"],
        "01-01-2017", "01-10-2026", "1",
    )
    kur = evds_cek(["TP.DK.USD.A.YTL"], "01-01-2017", "01-10-2026", "1")
    kkm = evds_cek(
        ["TP.KKM.K1", "TP.KKM.K2", "TP.KKM.K4"],
        "01-01-2021", "01-10-2026", "1",
    )
    kredi = evds_cek(
        ["TP.HPBITABLO6.21", "TP.HPBITABLO6.26"],
        "01-01-2017", "01-10-2026", "1",
    )
    borc = evds_cek(
        ["TP.BRUTDBORCLU.G1", "TP.BRUTDBORCLU.G19"],
        "01-01-2017", "01-10-2026", "5",
    )
    ham = pd.concat([mev, kur, kkm, kredi, borc], ignore_index=True)
    ham.to_csv(HAM / "kanal_evds_ham.csv", index=False, encoding="utf-8-sig")

    gsyh = pd.read_csv(KOK / "veri_hanehalki.csv", skiprows=[1])
    gsyh["yil"] = pd.to_numeric(gsyh["yil"], errors="coerce")
    gsyh = gsyh.dropna(subset=["yil"]).set_index(gsyh.yil.astype(int))["GSYH"]
    tamp = pd.read_csv(KOK / "tampon_yillik.csv")
    dis = tamp.loc[tamp.sektor == "dis", ["yil", "NL"]].copy()
    dis["yil"] = dis.yil.astype(int)
    dis = dis.set_index("yil")["NL"]

    yillar = list(range(2017, 2026))
    rows = []
    for y in yillar:
        tl = yil_sonu(mev, "TP.KM.E040").get(y, float("nan"))
        dth = yil_sonu(mev, "TP.KM.E050").get(y, float("nan"))
        maden = yil_sonu(mev, "TP.KM.E056").get(y, float("nan"))
        stok = yil_sonu(borc, "TP.BRUTDBORCLU.G1", aylik=False).get(y, float("nan"))
        kisa = yil_sonu(borc, "TP.BRUTDBORCLU.G19", aylik=False).get(y, float("nan"))
        tic_tl = yil_sonu(kredi, "TP.HPBITABLO6.21").get(y, float("nan"))
        tic_yp = yil_sonu(kredi, "TP.HPBITABLO6.26").get(y, float("nan"))
        nl = dis.get(y, float("nan"))
        g = gsyh.get(y, float("nan"))
        rows.append({
            "yil": y,
            "dis_borc_milyon_usd": stok,
            "kisa_vade_milyon_usd": kisa,
            "kisa_pay": (kisa / stok) if pd.notna(kisa) and pd.notna(stok) and stok else float("nan"),
            "dis_alem_B9_milyon_tl": nl,
            "dis_alem_B9_gsyh": (nl / g) if pd.notna(nl) and pd.notna(g) and g else float("nan"),
            "usd_alis_aralik": yil_sonu(kur, "TP.DK.USD.A.YTL").get(y, float("nan")),
            "hane_tl_ham": tl,
            "hane_dth_ham": dth,
            "hane_maden_ham": maden,
            "dth_pay": pay(dth, tl),
            "dth_maden_pay": pay(dth + maden, tl) if pd.notna(dth) and pd.notna(maden) and pd.notna(tl) else float("nan"),
            "ticari_tl_ham": tic_tl,
            "ticari_yp_ham": tic_yp,
            "ticari_tl_pay": pay(tic_tl, tic_yp),
            "kkm_ddkkm_toplam_milyar_usd": yil_sonu(kkm, "TP.KKM.K1").get(y, float("nan")),
            "kkm_ddkkm_gercek_milyar_usd": yil_sonu(kkm, "TP.KKM.K2").get(y, float("nan")),
            "kkm_tl_toplam_milyar_tl": yil_sonu(kkm, "TP.KKM.K4").get(y, float("nan")),
            "yapilandirilmis_kredi_stoku": "",
            "k1_borc_vadesi_payi": "",
            "k2_borc_vadesi_payi": "",
            "k3_borc_vadesi_payi": "",
        })
    out = pd.DataFrame(rows)
    out.to_csv(KOK / "kanal_yil.csv", index=False, encoding="utf-8-sig")
    return out


def sok_tablosu(panel):
    p = panel.set_index("yil")
    rows = []
    for sok, pencere in SOK.items():
        for ad, y in pencere.items():
            r = p.loc[y]
            rows.append({
                "sok": sok,
                "pencere": ad,
                "yil": y,
                "k1_yapilandirma": "",
                "k2_stok_milyon_usd": r.dis_borc_milyon_usd,
                "k2_kisa_pay": r.kisa_pay,
                "k2_B9_gsyh": r.dis_alem_B9_gsyh,
                "k3_dth_pay": r.dth_pay,
                "k3_dth_maden_pay": r.dth_maden_pay,
                "k3_ticari_tl_pay": r.ticari_tl_pay,
                "usd_alis_aralik": r.usd_alis_aralik,
                "k1_pay": "",
                "k2_pay": "",
                "k3_pay": "",
            })
    out = pd.DataFrame(rows)
    out.to_csv(KOK / "sok_kanal.csv", index=False, encoding="utf-8-sig")
    return out


def takvim():
    faiz = pd.read_csv(KOK / "erteleme_yillik.csv")
    rows = []
    for _, r in faiz.iterrows():
        if int(r.yil) > 2025 or not bool(r.tam_yil):
            continue
        rows.append({
            "yil": int(r.yil),
            "olay": "kredi kartı azami akdi faiz tavanı, bileşik yıllık",
            "tur": "duzenleme_faiz_tavani",
            "deger": round(float(r.i_ust), 4),
            "kaynak": "ham/kart_azami_2011_2020.pdf, ham/kart_azami_2020_2025.pdf, ham/tcmb_kart_azami_2026.html; erteleme_yillik.csv",
            "not": "Kurtarma değildir. Kamu sermayesi veya yapılandırma yasası sayılmaz. M1 hizalamasında kullanılmadı.",
        })
    for olay in ("kamu sermayesi / banka veya firma kurtarması", "yeniden yapılandırma yasası veya BDDK yapılandırma kararı"):
        rows.append({
            "yil": "",
            "olay": olay,
            "tur": "kurtarma",
            "deger": "",
            "kaynak": "veri yok",
            "not": "Resmî Gazete ve BDDK duyurusu bu oturumda açılmadı. Tarih ezberden yazılmadı.",
        })
    out = pd.DataFrame(rows)
    out.to_csv(KOK / "motiv_takvim.csv", index=False, encoding="utf-8-sig")
    return out


def kaynak():
    rows = [
        ("brüt dış borç stoku", "TCMB", "EVDS bie_brutdbborclu TP.BRUTDBORCLU.G1, yılın 4. çeyreği", CEKIM, "milyon ABD doları", "ham/tcmb_dis_borc_metaveri.pdf: tüm değişkenler milyon ABD doları. 12 Mart 2026 yöntem değişikliği (piyasa değeri, elde tutanın yerleşikliği) sonrası seri."),
        ("kısa vadeli dış borç", "TCMB", "EVDS TP.BRUTDBORCLU.G19 / G1", CEKIM, "pay, birimsiz", "Kısa vade: orijinal vadesi 1 yıla kadar. Aynı metaveri."),
        ("dış âlem B.9", "TCMB", "finansal hesap BF.9 akımı, S.2, tampon_yillik.csv NL", "16 Ekim 2026 finansal hesap çekimi", "milyon TL; pay GSYH'ye bölünür", "Pozitif değer, dış âlemin o yıl net borç verdiği anlamına gelir. Stok pozisyonu bu sütun değildir."),
        ("GSYH", "TÜİK via EVDS", "TP.GSYIH20.BY.B1GQ, dört çeyrek toplamı", CEKIM, "milyon TL", "veri_hanehalki.csv. Bülten 58286 GSMH ile aynı sürüm değildir."),
        ("USD alış", "TCMB", "TP.DK.USD.A.YTL, aralık, aylık frekansta last", CEKIM, "TL / USD", "Yıl sonu kur. Kur şokunun ölçüsü budur."),
        ("hane TL mevduat", "TCMB", "TP.KM.E040, aralık, mevduat bankaları", CEKIM, "EVDS ham; seri listesinde birim alanı yok", "Pay hesabında birim sadeleşir. Düzey milyar TL'ye çevrilmedi."),
        ("hane döviz tevdiat", "TCMB", "TP.KM.E050, aralık", CEKIM, "EVDS ham; birim alanı yok", "Yerleşik gerçek kişiler. Kıymetli maden ayrıdır (E056)."),
        ("hane kıymetli maden", "TCMB", "TP.KM.E056, aralık", CEKIM, "EVDS ham; birim alanı yok", "Döviz tevdiatın içinde değildir. İkinci pay bunu paydaya katar."),
        ("ticari kredi TL / YP", "TCMB", "TP.HPBITABLO6.21 ve .26, aralık", CEKIM, "EVDS ham; 2024 öncesi gözlem yok", "Tüketici kredisinde TL/YP ayrımı yok. Şok yıllarında TL borç payı boş."),
        ("KKM", "TCMB", "TP.KKM.K1, K2, K4, aralık", CEKIM, "K1 ve K2 milyar ABD doları; K4 milyar TL (seri adında yazılı)", "K4 hane kırılımı vermez. Döviz payına eklenmedi."),
        ("yapılandırılmış kredi", "BDDK / TCMB", "katalogda ayrı seri bulunamadı", CEKIM, "", "veri yok"),
        ("gelir dilimi, mülk geliri", "TÜİK GYKA", "yayımlanmış %20 tablosu", "beklenen Ekim 2026 sürümü klasörde yok", "", "veri yok"),
        ("tüketim dilimi", "TÜİK HBA", "2018, 2021, 2023 dilim tablosu", "", "", "veri yok"),
        ("borç yükü dilimi", "TÜİK GYKA", "çok yük oranı, %20", "", "", "veri yok"),
        ("mevduat tutar dilimi", "TBB / BDDK", "hesap büyüklüğü dilimi", "", "", "veri yok. Hane dilimi değildir."),
        ("kurtarma tarihi", "Resmî Gazete, TCMB, BDDK", "kamu sermayesi, yapılandırma", "", "", "veri yok. Kart faiz tavanı ayrı satırda, kurtarma sayılmadı."),
        ("takip oranı", "TCMB", "bie_hpbitablo6, takip_aylik.csv", "seri 2024-06'da başlıyor", "oran", "2018, 2021, 2023 ile örtüşen gözlem yok."),
    ]
    df = pd.DataFrame(rows, columns=["gosterge", "kurum", "tablo", "surum", "birim", "not"])
    df.to_csv(KOK / "kaynak_tablo.csv", index=False, encoding="utf-8-sig")
    return df


def main():
    HAM.mkdir(exist_ok=True)
    dilim = bos_tablo()
    dilim.to_csv(KOK / "dilim.csv", index=False, encoding="utf-8-sig")
    panel = kanal()
    sok = sok_tablosu(panel)
    takvim()
    kaynak()
    print(panel[["yil", "dis_borc_milyon_usd", "kisa_pay", "dis_alem_B9_gsyh", "usd_alis_aralik", "dth_pay", "dth_maden_pay", "ticari_tl_pay"]].to_string(index=False))
    print("--- şok ---")
    print(sok.to_string(index=False))
    print("dilim satır", len(dilim), "boş değer", int((dilim.deger == "").sum()))


if __name__ == "__main__":
    main()
