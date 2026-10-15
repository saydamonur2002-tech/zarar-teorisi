"""Faz 7 — Girdi haritası: hangi çıktı hangi adıma, hangi etiketle girdi olabilir.

Kural: katman sonuçları birbirine taşınmaz. Bir dosyanın sayısı başka adıma yalnız GİRDİ olarak, kendi etiketiyle
(olcum / ust_sinir / varsayim / tahmin_ols / modellendi / kademe sabiti) girer; hedef adımın sonuç sütununa yazılmaz,
hedef adımın etiketi kaynağın etiketinden iyi olamaz. Harita bunu satır satır yazar ve kaynak dosyaların var olduğunu,
sayının bugün ne olduğunu okur.

Çıktı: girdi_haritasi.csv, GIRDI_HARITASI.md.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

KOK = Path(__file__).resolve().parent


def _j(ad: str) -> dict:
    p = KOK / ad
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _al(d: dict, yol: str):
    for k in yol.split("/"):
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


# (kaynak dosya, alan yolu, kaynak adım/faz, hedef adım, etiket, nasıl girer, nereye yazılmaz)
HARITA = [
    ("adim1_nace_sonuc.json", "b_nace_taban/silinen_max_oran", "Faz 1 (Adım 1 yan)", "Adım 2 (ağ)", "ust_sinir_nace",
     "NACE kenar matrisi (adim1_nace_kenar.csv) ağın kenarı olur; etiket varsayim_dagitim", "adim1_stok.csv silinen; adim2.csv"),
    ("adim1_nace_sonuc.json", "a_evds_fark/ZP44/sektor_ici", "Faz 1", "Adım 1 (yorum)", "olcum",
     "F içi brüt ticari borç; hazneler arası yeni_tavan ile karşılaştırılır, toplanmaz", "adim1_stok.csv; tek_sistem_esleme.csv"),
    ("adim1_nace.csv", "hazir_degerler, ticari_borc, personel_maliyeti (kısım)", "Faz 1", "Adım 2 (düğüm)", "olcum",
     "Düğüm nakdi, borcu, ücreti", "adim2.csv deger"),
    ("adim2_nace_ag_sonuc.json", "kalibrasyon/lambda", "Faz 2", "Adım 2 (duyarlılık)", "kalibrasyon_varsayim",
     "G1 çapasına oturan nakit çarpanı; duyarlılık satırı", "adim2.csv; uc_kural_senaryo.csv"),
    ("adim2_nace_ag_sonuc.json", "beta_tavan", "Faz 2", "Adım 2 parametre (β)", "ust_sinir",
     "ucret_gecis_beta için üst sınır; 0,3 ile karşılaştırılır", "odeme_mahsup_sonuc.json parametreler"),
    ("adim2_nace_ag_sonuc.json", "senaryolar/lam1.0_h0.5_b0.3/kredi_ihtiyaci_brut", "Faz 2", "Adım 3 (köprü kredi karşılaştırma)", "modellendi_olculmus_dugum",
     "Mahsup öncesi stok ölçekli köprü ihtiyacı; F.4 ile oran", "adim3.csv deger"),
    ("tek_sistem_kopru.csv", "2026-Q1 F_F4_yuk evds_milyar", "tek_sistem_kopru", "Adım 3 (Faz 3 S₀)", "olcum",
     "Faiz durma kuralının stok tabanı", "—"),
    ("faiz_ham.csv", "TP.KTF17 son ay", "EVDS", "Adım 3 (Faz 3 r_t)", "olcum",
     "Ticari kredi faizi; ileri dönem sabit (varsayım)", "—"),
    ("adim3_faiz_durma_sonuc.json", "psi/psi", "Faz 3", "Adım 3", "olcum_turevi",
     "Etkin faiz payı; finansman gideri 2024 / (r̄·S̄). Satır etiketi modellendi_varsayim_kappa", "adim3.csv deger olculdu yazılmaz; uc_kural_senaryo.csv"),
    ("adim3_faiz_durma_sonuc.json", "yillik_duran_faiz_etkin_milyar/0.5", "Faz 3", "Adım 4 (Faz 4 prim karşılaştırma)", "modellendi_varsayim_kappa",
     "Prim yıllık / duran faiz oranı; eşitlik değil", "adim4.csv; senet satırı"),
    ("adim4.csv", "üç adres satırı deger (olculdu)", "Adım 4", "Faz 4 (A_j)", "olcum",
     "Yönlendirme tabanı", "—"),
    ("tek_sistem_kademe.py", "K3_MEVDUAT_KREDI_PAYI", "kademe", "Faz 4 (kredi itişi)", "kademe sabiti",
     "B′ mevduat kaybı → kredi daralması", "—"),
    ("adim4_adres_yonlendirme_sonuc.json", "senaryolar/th0.25_chi0.0_pi0.02/tepe_stok", "Faz 4", "Adım 4 (band)", "band_varsayim",
     "İhraç/stok bandı; senet satırına yazılmaz", "adim4.csv senet satırı; senet_kilit.txt"),
    ("gecis_payi_band_sonuc.json", "ana/LR_gecis_payi", "Faz 5", "Geçiş payı kapısı (yorum)", "tahmin_ols",
     "Nokta tahmin ve bandlar; kapı birincil ölçüm ister", "tavan_akis.csv gecis/tavan; kapi_kilit.txt"),
    ("gecis_payi_band_sonuc.json", "ana/bes_yil_enflasyon_puan_68", "Faz 5", "bes_yil_senaryo enflasyon bandı", "tahmin_ols",
     "[0, −7,62] bandını daraltma önerisi; ayrı satırda durur", "bes_yil_senaryo.csv"),
    ("adim5_kira_sonuc.json", "birim_kira/tl_m2_ay", "Faz 6", "Adım 5 (band)", "olcum",
     "TCMB birim kira; kiracı hane ve alan varsayımıyla yıllık band", "adim5.csv kira satırı"),
    ("adim5_kira_sonuc.json", "yol_A_band_milyar", "Faz 6", "Adım 5 / HEKİS karşılaştırma", "band_varsayim",
     "Kira akışı bandı; HEKİS kirası ile oran", "adim5.csv; diger_repo_kopru.csv"),
    ("odeme_mahsup_sonuc.json", "ozet/temerrut_sart", "Adım 2 (sentetik)", "Adım 2", "modellendi",
     "Sentetik; Faz 2 ile yan yana okunur, eşitlenmez", "adim2_nace_ag.csv"),
]

FAZ_OZETI = [
    ("1", "adim1_stok.csv", "eski/yeni tavan üst sınır; silinen boş", "F içi netleştirme: EVDS konsolide fark (ölçüm), NACE taban (üst sınır), çekim/RAS kenar (varsayım)", "adim1_nace.py", "silinen hâlâ boş; firma düzeyi kimden-kime yok"),
    ("2", "adim2.csv", "sentetik 150 firma, temerrüt 0", "17 NACE + hane + dış düğüm; nakit/ücret/çalışan ölçüm; G1 çapası λ*; β tavanı", "adim2_nace_ag.py", "kenar dağılımı varsayım"),
    ("3", "adim3.csv", "kredi ihtiyacı 0; duran faiz satırı modellendi_varsayim_kappa", "D_t=κ·u2·S₀, I_t=ψ·r_t/4·D_t; F/B′ NL transferi; κ bandı", "adim3_faiz_durma.py", "etiket yükseltilmedi; κ varsayım; r_t ileri sabit"),
    ("4", "adim4.csv", "üç adres olculdu; senet modellenmedi", "θ yönlendirme, vade, χ çıkış, π prim; SFC muhasebesi; kredi itişi", "adim4_adres_yonlendirme.py", "senet satırı ve kilit dokunulmadı; endeks bacağı yok"),
    ("kapı", "tavan_akis.csv", "geçiş payı boş", "OLS+NW tahmin; 95 bandı daralmadı, 68 bandı [0,20; 1]", "gecis_payi_band.py", "tahmin_ols; kapı boş"),
    ("5", "adim5.csv", "kira olculmedi; HEKİS 20.000 TL/ay", "birim kira ölçümü × varsayım band; HEKİS/piyasa oranı", "adim5_kira.py", "N elle; κ, m² varsayım"),
]


def main() -> None:
    satirlar = []
    for kaynak, alan, kaynak_adim, hedef, etiket, nasil, yazilmaz in HARITA:
        p = KOK / kaynak
        deger = None
        if kaynak.endswith(".json") and p.exists():
            deger = _al(_j(kaynak), alan)
        satirlar.append({"kaynak_dosya": kaynak, "alan": alan, "kaynak_adim": kaynak_adim, "hedef_adim": hedef, "etiket": etiket,
                         "bugunku_deger": "" if deger is None or isinstance(deger, (dict, list)) and len(str(deger)) > 60 else json.dumps(deger, ensure_ascii=False),
                         "nasil_girer": nasil, "yazilmaz": yazilmaz, "dosya_var": p.exists()})
    alan = list(satirlar[0].keys())
    with (KOK / "girdi_haritasi.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=alan); w.writeheader(); w.writerows(satirlar)

    md = ["# Girdi haritası — hangi çıktı hangi adıma, hangi etiketle", "",
          "Çalıştır: `python3 girdi_haritasi.py`. Çıktı: `girdi_haritasi.csv`.", "",
          "Kural: bir sayı başka adıma yalnız girdi olarak, kendi etiketiyle girer; hedefin etiketi kaynağınkinden iyi olamaz. "
          "Kilitler (`test_bes_adim.py`) olduğu gibi durur: silinen boş, senet "
          "`modellenmedi`, üç kapı boş, akış 0,4270 `baska_nesne`.", "",
          "## Faz özeti: şu an ne var / ne eklendi / ne eksik", "",
          "| Adım | Kilitli dosya | Şu an ne var | Ne eklendi (yan dosya) | Kod | Ne eksik |", "| --- | --- | --- | --- | --- | --- |"]
    md += [f"| {a} | `{d}` | {v} | {e} | `{k}` | {x} |" for a, d, v, e, k, x in FAZ_OZETI]
    md += ["", "## Harita", "",
           "| Kaynak | Alan | Kaynak adım | Hedef adım | Etiket | Bugünkü değer | Nasıl girer | Yazılmaz |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    md += [f"| `{s['kaynak_dosya']}` | {s['alan']} | {s['kaynak_adim']} | {s['hedef_adim']} | `{s['etiket']}` | {s['bugunku_deger']} | {s['nasil_girer']} | {s['yazilmaz']} |"
           for s in satirlar]
    md += ["", "## Etiket sırası (iyiden kötüye)", "",
           "`olcum` > `olcum_turevi` > `ust_sinir` / `ust_sinir_nace` > `tahmin_ols` > `kalibrasyon_varsayim` > `modellendi` / `band_varsayim` > `varsayim` > `dis_kaynak_elle`.",
           "Bir hedef satırın etiketi, girdilerinin en kötüsünden iyi yazılamaz.", ""]
    (KOK / "GIRDI_HARITASI.md").write_text("\n".join(md), encoding="utf-8")
    eksik = [s["kaynak_dosya"] for s in satirlar if not s["dosya_var"]]
    print(f"{len(satirlar)} satır; eksik dosya: {eksik or 'yok'}")


if __name__ == "__main__":
    main()
