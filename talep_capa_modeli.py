"""
ÇAPALI TALEP MODELİ — Hanehalkı harcama kapasitesi (HC), resmî hesaplara bağlı
==============================================================================

Eski denklem (sorunlu):
    HC = W + TR + ΔK − DS ;  kısıt: HC/P ≤ Y* + FX − DS
    Sorunlar: kredi gelir sayılıyor, DS iki kez düşülüyor, birimler karışık.

Yeni denklem (ESA 2010 kodlarıyla):
    (1) YD  = D1 + B2B3 + D4_alinan − D41_odenen + D62 − D5 − D61 + D7_net
    (2) HC  = YD + dL                      (gelir + net borçlanma; kredi gelir DEĞİL)
    (3) Çapa: C + I_konut + dA ≈ YD + dL  (finansal hesap ile reel hesap buluşmalı)

    dL = hanehalkı yükümlülüklerinde NET İŞLEM (TCMB finansal hesaplar, F.4).
         Stok farkı KULLANILMAZ: kur ve yeniden değerleme içerir.
    dA = hanehalkı finansal varlıklarında net işlem.

Üç çapa:
    Çapa-1 (gelir):     hesaplanan YD  vs  TÜİK'in yayımladığı B6 (harcanabilir gelir)
    Çapa-2 (iki kurum): TÜİK B9 (reel hesaptan net borç verme) vs TCMB (dA − dL)
    Çapa-3 (bütünlük):  (P3 + P51 + dA) − (YD + dL) artığı

Önceden ilan edilen testler (sonuçtan önce yazıldı, sonradan değiştirilmez):
    H1  Kredi bağımlılık oranı dL/(P3+P51) toplam düzeyde %20–30 bandındadır.
        Beklenti: RED (üst sınır hesabı ~%18'in altını gösteriyor).
    H2  Faiz yükü D41/YD, kredi bağımlılığı arttığında artar (yön testi).
    H3  Hanehalkı B9 düştüğü yıllarda cari açık büyür (Türkiye tipi iz).
        Cari denge verisi girilmezse atlanır.

Kullanım:
    python talep_capa_modeli.py veri_hanehalki.csv
    python talep_capa_modeli.py --sablon      # boş veri şablonu üretir
    python talep_capa_modeli.py --deneme      # SENTETİK veriyle kod testi

Birim: Tüm akışlar AYNI birimde (ör. milyon TL, cari fiyat). Oranlar birimsizdir.
"""
import sys
import numpy as np
import pandas as pd

# ---------------------------------------------------------------- tanımlar
GELIR_KALEMLERI = {           # işaret: +1 ekle, −1 çıkar
    "D1": +1,                 # çalışanlara ödemeler (ücret)
    "B2B3": +1,               # işletme artığı / karma gelir (esnaf dahil!)
    "D4_alinan": +1,          # alınan mülk geliri (faiz, kira, temettü)
    "D41_odenen": -1,         # ödenen faiz
    "D62": +1,                # sosyal yardımlar
    "D5": -1,                 # gelir ve servet vergileri
    "D61": -1,                # sosyal katkılar
    "D7_net": +1,             # diğer cari transferler, net (yoksa 0)
}
ZORUNLU = ["yil", "D1", "B2B3", "D4_alinan", "D41_odenen", "D62", "D5", "D61",
           "P3", "P51", "dL"]
ISTEGE_BAGLI = ["D7_net", "B6_tuik", "B9_tuik", "dA", "L_stok",
                "deflator_tuketim", "GSYH", "cari_denge"]

TOLERANS_CAPA = 0.02          # çapa farkı harcanabilir gelirin %2'sini aşarsa uyarı


def sablon_yaz(yol="veri_hanehalki_SABLON.csv"):
    kolonlar = ZORUNLU + ISTEGE_BAGLI
    aciklama = {
        "yil": "Yıl", "D1": "TÜİK KSH: Çalışanlara ödemeler (alınan)",
        "B2B3": "TÜİK KSH: İşletme artığı + karma gelir", "D4_alinan": "TÜİK KSH: Mülk geliri (alınan)",
        "D41_odenen": "TÜİK KSH: Faiz (ödenen)", "D62": "TÜİK KSH: Sosyal yardımlar (alınan)",
        "D5": "TÜİK KSH: Gelir/servet vergileri (ödenen)", "D61": "TÜİK KSH: Sosyal katkılar (ödenen)",
        "P3": "TÜİK KSH: Nihai tüketim harcaması", "P51": "TÜİK KSH: Gayrisafi sabit sermaye (konut)",
        "dL": "TCMB Finansal Hesaplar: Yükümlülük NET İŞLEM (F.4 krediler; stok farkı değil)",
        "D7_net": "TÜİK KSH: Diğer cari transferler net (yoksa boş)",
        "B6_tuik": "TÜİK KSH: Gayrisafi harcanabilir gelir (çapa-1)",
        "B9_tuik": "TÜİK KSH: Net borç verme/alma (çapa-2)",
        "dA": "TCMB Finansal Hesaplar: Varlık NET İŞLEM",
        "L_stok": "TCMB/BDDK: Yıl sonu hanehalkı borç stoku (üst sınır testi)",
        "deflator_tuketim": "TÜİK: Hanehalkı tüketim deflatörü (endeks)",
        "GSYH": "TÜİK: Cari fiyatlarla GSYH", "cari_denge": "TCMB: Cari işlemler dengesi (TL)",
    }
    df = pd.DataFrame(columns=kolonlar)
    df.loc[0] = [aciklama[k] for k in kolonlar]
    df.to_csv(yol, index=False)
    print(f"Şablon yazıldı: {yol}  (ilk satır açıklamadır, silip veriyi gir)")


def yukle(yol):
    df = pd.read_csv(yol)
    if pd.isna(pd.to_numeric(df["yil"].iloc[0], errors="coerce")):
        df = df.iloc[1:]                       # şablondaki açıklama satırını at
    eksik = [k for k in ZORUNLU if k not in df.columns]
    if eksik:
        raise ValueError(f"Eksik zorunlu kolon(lar): {eksik}")
    for k in ISTEGE_BAGLI:
        if k not in df.columns:
            df[k] = np.nan
    df = df.apply(pd.to_numeric, errors="coerce").sort_values("yil").reset_index(drop=True)
    if df[ZORUNLU].isna().any().any():
        bos = df[ZORUNLU].isna().sum()
        print("UYARI: zorunlu kolonlarda boş hücre var:\n", bos[bos > 0])
    return df


def hesapla(df):
    df = df.copy()
    for k in ISTEGE_BAGLI:                 # eksik isteğe bağlı kolonları boş ekle
        if k not in df.columns:
            df[k] = np.nan
    r = pd.DataFrame({"yil": df.yil})
    d7 = df.D7_net.fillna(0)
    r["YD"] = sum(isaret * (d7 if k == "D7_net" else df[k]) for k, isaret in GELIR_KALEMLERI.items())
    r["HC"] = r.YD + df.dL                                 # (2)
    r["harcama"] = df.P3 + df.P51
    r["kredi_bagimlilik"] = df.dL / r.harcama              # H1
    r["faiz_yuku"] = df.D41_odenen / r.YD                  # H2
    r["ucret_payi_YD"] = df.D1 / r.YD                      # ücretin gelir içindeki payı
    r["esnaf_payi_YD"] = df.B2B3 / r.YD                    # bulanıklık uyarısı için
    # Çapa-1: hesaplanan YD vs TÜİK B6
    r["capa1_fark_orani"] = (r.YD - df.B6_tuik) / df.B6_tuik
    # Çapa-2: TÜİK B9 vs TCMB (dA − dL)
    r["B9_finansal"] = df.dA - df.dL
    r["capa2_fark_orani"] = (df.B9_tuik - r.B9_finansal) / r.YD
    # Çapa-3: (harcama + dA) − (YD + dL)
    r["capa3_artik_orani"] = (r.harcama + df.dA - (r.YD + df.dL)) / r.YD
    # Üst sınır: tüm stok tek yılda alınsaydı
    r["ust_sinir_bagimlilik"] = df.L_stok / r.harcama
    # Reel HC büyümesi (deflatör varsa)
    if df.deflator_tuketim.notna().any():
        reel = r.HC / df.deflator_tuketim
        r["reel_HC_buyume"] = reel.pct_change()
    if df.GSYH.notna().any():
        r["B9_hh_GSYH"] = df.B9_tuik / df.GSYH
        r["cari_GSYH"] = df.cari_denge / df.GSYH
    return r


def rapor(r):
    pd.set_option("display.width", 160)
    print("\n=== TEMEL SONUÇLAR ===")
    goster = ["yil", "kredi_bagimlilik", "ust_sinir_bagimlilik", "faiz_yuku",
              "ucret_payi_YD", "esnaf_payi_YD"]
    print(r[[c for c in goster if c in r]].round(3).to_string(index=False))

    print("\n=== ÇAPALAR (tolerans ±%.0f%% harcanabilir gelir) ===" % (TOLERANS_CAPA * 100))
    for c, ad in [("capa1_fark_orani", "Çapa-1 gelir"), ("capa2_fark_orani", "Çapa-2 iki kurum"),
                  ("capa3_artik_orani", "Çapa-3 bütünlük")]:
        s = r[c].dropna()
        if s.empty:
            print(f"{ad}: VERİ YOK — ilgili kolon girilmedi, bu çapa sınanmadı.")
            continue
        asim = r.loc[r[c].abs() > TOLERANS_CAPA, "yil"].astype(int).tolist()
        print(f"{ad}: ort. mutlak fark %{100*s.abs().mean():.2f} | toleransı aşan yıllar: {asim or 'yok'}")
    print("Not: Çapa tutmuyorsa önce dL'nin İŞLEM serisi olduğunu, sonra yayım sürümünü (vintage) kontrol et.")

    print("\n=== ÖNCEDEN İLAN EDİLEN TESTLER ===")
    kb = r.kredi_bagimlilik.dropna()
    if not kb.empty:
        bantta = kb.between(0.20, 0.30)
        print(f"H1 (%20–30 bandı): {int(bantta.sum())}/{len(kb)} yıl bantta | "
              f"aralık %{100*kb.min():.1f} – %{100*kb.max():.1f} → "
              f"{'DESTEKLENDİ' if bantta.mean() >= 0.5 else 'REDDEDİLDİ (toplam düzeyde)'}")
    x = r[["kredi_bagimlilik", "faiz_yuku"]].diff().dropna()
    if len(x) >= 5:
        k = x.corr().iloc[0, 1]
        if pd.isna(k):
            print("H2: seri(ler)den biri sabit, korelasyon HESAPLANAMADI (ret değil).")
        else:
            print(f"H2 (Δkredi bağımlılığı ~ Δfaiz yükü): korelasyon {k:.2f} → "
                  f"{'yön destekleniyor' if k > 0.3 else 'yön desteklenmiyor'}")
    else:
        print("H2: en az 6 yıl gerekli, atlandı.")
    if "B9_hh_GSYH" in r and "cari_GSYH" in r and r[["B9_hh_GSYH", "cari_GSYH"]].dropna().shape[0] >= 5:
        k = r[["B9_hh_GSYH", "cari_GSYH"]].diff().dropna().corr().iloc[0, 1]
        print(f"H3 (ΔB9 hanehalkı ~ Δcari denge): korelasyon {k:.2f} "
              f"(pozitif: hanehalkı net borç verme düşünce cari denge de bozuluyor)")
    else:
        print("H3: GSYH/cari_denge/B9_tuik verisi yok, atlandı.")

    print("\n=== SINIRLAR (rapora yaz) ===")
    print("- Toplam hanehalkı esnafı da içerir (esnaf_payi_YD'ye bak); ücretli hanenin oranı değildir.")
    print("- Toplam, dağılımı saklar: borç alan ve mevduat biriktiren aynı haneler değildir.")
    print("  H1 toplamda reddedilse bile alt gelir gruplarında geçerli olabilir; bu ayrı bir test ister.")
    print("- Brüt kart hacmi finansman değildir; dL net finansmandır.")


def deneme_verisi():
    """SENTETİK — yalnızca kodun çalıştığını göstermek için. Türkiye verisi DEĞİLDİR."""
    yil = np.arange(2015, 2025)
    b = 1000 * 1.25 ** (yil - 2015)
    df = pd.DataFrame({
        "yil": yil, "D1": .50*b, "B2B3": .35*b, "D4_alinan": .06*b, "D41_odenen": .03*b,
        "D62": .15*b, "D5": .04*b, "D61": .07*b, "D7_net": .01*b,
        "P3": .80*b, "P51": .08*b, "dL": np.linspace(.02, .06, 10)*b, "dA": .14*b,
        "L_stok": .15*b, "deflator_tuketim": 1.2 ** (yil - 2015),
    })
    yd = sum(s*df[k] for k, s in GELIR_KALEMLERI.items())
    df["B6_tuik"] = yd * 1.005
    df["B9_tuik"] = df.dA - df.dL + .003*b
    return df


if __name__ == "__main__":
    if "--sablon" in sys.argv:
        sablon_yaz(); sys.exit()
    if "--deneme" in sys.argv:
        print(">>> SENTETİK VERİ — sonuçlar hiçbir şey kanıtlamaz, yalnızca kod testidir <<<")
        df = deneme_verisi()
    elif len(sys.argv) > 1:
        df = yukle(sys.argv[1])
    else:
        print(__doc__); sys.exit()
    r = hesapla(df)
    rapor(r)
    r.to_csv("talep_capa_sonuc.csv", index=False)
    print("\nAyrıntılı tablo: talep_capa_sonuc.csv")
