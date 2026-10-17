"""Tek Sistem beş adım: sorun ve çözüm (parçalarıyla) — DOCX rapor.

Çalıştır: python3 yayin_bes_adim_rapor_docx.py
Çıktı: TEK_SISTEM_SORUN_COZUM.docx ve yayin/TEK_SISTEM_SORUN_COZUM.docx
Sayılar depo JSON/CSV'den okunur; yoksa boş bırakılır.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

KOK = Path(__file__).resolve().parent
OUT = KOK / "TEK_SISTEM_SORUN_COZUM.docx"
OUT_YAYIN = KOK / "yayin" / "TEK_SISTEM_SORUN_COZUM.docx"


def _j(ad: str) -> dict:
    p = KOK / ad
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _al(d: dict, *yol):
    for k in yol:
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


def _f(x, n=1):
    if x is None:
        return "—"
    try:
        return f"{float(x):,.{n}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        return str(x)


def _add_table(doc: Document, headers: list[str], rows: list[list[str]]) -> None:
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = "Table Grid"
    for j, h in enumerate(headers):
        t.rows[0].cells[j].text = h
        for p in t.rows[0].cells[j].paragraphs:
            for r in p.runs:
                r.bold = True
    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            t.rows[i].cells[j].text = str(val)
    doc.add_paragraph()


def build() -> Document:
    a1 = _j("adim1_nace_sonuc.json")
    a2 = _j("adim2_nace_ag_sonuc.json")
    a3 = _j("adim3_faiz_durma_sonuc.json")
    a4 = _j("adim4_adres_yonlendirme_sonuc.json")
    a5 = _j("adim5_kira_sonuc.json")
    gp = _j("gecis_payi_band_sonuc.json")
    ba = _j("bes_adim_sonuc.json")

    zp44 = _al(a1, "a_evds_fark", "ZP44") or {}
    taban = _al(a1, "b_nace_taban") or {}
    y20 = _al(a1, "e_senaryo_yuzde20", "satirlar") or []
    psi = _al(a3, "psi") or {}
    yil3 = _al(a3, "yillik_duran_faiz_etkin_milyar") or {}
    ana = _al(gp, "ana") or {}
    bk = _al(a5, "birim_kira") or {}
    band_a = _al(a5, "yol_A_band_milyar") or [None, None]

    def _band(ad):
        for x in a5.get("araliklar") or []:
            if x.get("nesne") == ad:
                return x
        return {}

    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = Cm(2)
    sec.bottom_margin = Cm(2)
    sec.left_margin = Cm(2.2)
    sec.right_margin = Cm(2.2)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = title.add_run("Tek Sistem: Sorun ve Çözüm\n")
    r.bold = True
    r.font.size = Pt(18)
    r2 = title.add_run("Beş adım, parçalarıyla — yüzde 20 eşiği ve her önerinin yaptığı iş\n")
    r2.font.size = Pt(13)
    r3 = title.add_run(f"Zarar Teorisi deposu — {date.today().isoformat()}\n")
    r3.italic = True
    r3.font.size = Pt(10)

    doc.add_paragraph(
        "Bu belge politika reçetesi değildir. Ölçüm, üst sınır, varsayım, tahmin ve senaryo ayrı durur. "
        "Bir katmanın sonucu diğerinin sonuç sütununa yazılmaz; yalnız etiketiyle girdi olur. "
        "Kilitli dosyalar (adim1_stok silinen, adim4 senet, üç kapı, akış 0,4210) boş/modellenmedi kalır. "
        "Sayılar 12 Ekim 2026 koşusuna bağlıdır; yenilemek için adim1_nace.py … test_bes_adim.py sırasına bakın."
    )

    # ------------------------------------------------------------------
    doc.add_heading("Özet", level=1)
    doc.add_paragraph(
        "Sorun tek bir açık değil: aynı yük beş yerde birikiyor. Firmalar birbirine borçlu olduğu için nakit "
        "dolaşmıyor; kalan stok üzerinden faiz işliyor; banka bu faizi ve yeni krediyi büyütüyor; mevduat aynı "
        "kredi itişini besliyor; kira ve yaşam maliyeti haneyi sıkıyor. Beş adım bu beş yeri sırayla keser. "
        "Birinci adımın eşiği yüzde 20’dir: karşılıklı borcun beşte biri silinebiliyorsa zincir işlemeye başlar. "
        "Eşik varsayımdır; üç tabanda da üst sınırın içindedir, gerçekleştiği ölçülmemiştir."
    )
    doc.add_paragraph(
        f"Koşu sözü: {ba.get('kosu', '—')}. Test sözü (test_bes_adim.py): {ba.get('son', '—')}. "
        "İkisi ayrıdır. Aşağıdaki sayılar kilit dışı yan dosyalardandır."
    )

    # ------------------------------------------------------------------
    doc.add_heading("1. Sorun", level=1)
    doc.add_heading("1.1 Tek cümle", level=2)
    doc.add_paragraph(
        "Türkiye’de firma, hane, banka ve kamu aynı yükü beş kanaldan taşıyor: kilitli ticari borç, "
        "ödenemeyen zincir, işleyen faiz, mevduattan beslenen yeni kredi, ve kiraya binen yaşam maliyeti. "
        "Kanallar birbirini besliyor; biri kesilmeden diğeri durmuyor."
    )

    doc.add_heading("1.2 Parça 1 — Kilitli borç (kim kime)", level=2)
    doc.add_paragraph(
        "A, B’ye borçlu; B de A’ya (veya C üzerinden A’ya) borçluysa, o kısım ödenmeden durur. Nakit yok diye "
        "zincir kırılır; net borçlu yine borçludur. EVDS 2026-Q1’de firma sektörünün kendi içindeki diğer "
        f"alacak/borç farkı {_f(zp44.get('sektor_ici'))} milyar TL’dir (ZP22 = ZP44, tutarlılık). Bu brüt stoktur; "
        "kaçının netleşeceğini söylemez. Sektör Bilançoları 2024’te 17 NACE kısmının ticari borcu "
        f"{_f(taban.get('brut_milyar'))} milyardır; kapsam ve dönem farklı, iki sayı eşitlenmez."
    )
    doc.add_paragraph(
        "Hazneler arası (hane–firma–banka–kamu–dış) brüt 78.870 milyar, ortak stok 20.363 milyar; "
        "yeni tavan 0,2582 üst sınırdır, skor değil. Kimden-kime xls depoda yoktur: adim1_stok.csv "
        "silinen sütunu boştur ve boş kalır."
    )

    doc.add_heading("1.3 Parça 2 — Ödenemeyen zincir", level=2)
    doc.add_paragraph(
        "Silinmeyen borç nakit ve tahsilat ister. Tepedeki taraf (holding) vadeyi uzatırsa alta inen para gecikir; "
        "aracı ücretini ödeyemez. Sentetik 150 firma ağında şart sonrası temerrüt 0 çıkar — ölçüm değil, model. "
        "Ölçülmüş düğümle (17 NACE, 2024 nakit ve ücret) brüt aşamada 15 kısım temerrütte, 14’ü ücret ödeyemez; "
        "köprü kredi ihtiyacı 8.329 milyar TL’dir. G1 firma takip oranı 2026-09: yüzde 2,52 (ölçüm)."
    )

    doc.add_heading("1.4 Parça 3 — İşleyen faiz", level=2)
    doc.add_paragraph(
        f"Firma F.4 kredi yükümlülüğü 2026-Q1: {_f(_al(a3, 'S0_milyar'))} milyar TL (ölçüm). "
        f"Ticari kredi faizi (TP.KTF17) 2026-09: yüzde 53,19. 2024 finansman gideri {_f(psi.get('finansman_gideri_2024'))} "
        f"milyar; etkin faiz payı ψ = {_f(psi.get('psi'), 4)} (ölçüm türevi: gider / (r̄·S̄)). "
        "Faiz durmazsa stok her çeyrek şişer; firmanın NL’si erir, bankanınki şişer."
    )

    doc.add_heading("1.5 Parça 4 — Mevduattan kredi itişi", level=2)
    adresler = a4.get("adresler") or []
    doc.add_paragraph(
        f"Üç ölçülmüş adres stoku (2026-Q1) toplam {_f(a4.get('adres_toplam_milyar'))} milyar TL: "
        + "; ".join(f"{x.get('nesne', '')} {_f(x.get('milyar'))}" for x in adresler)
        + ". Banka bu mevduatı krediye çevirir. 2025 firma F.4 işlem akımı 4.821 milyar = GSYH’nin yüzde 7,62’si "
        "(itiş). İtiş kesilmezse fiyat kanalı açıktır; geçiş payı birincil ölçümle bulunamamıştır (kapı boş)."
    )

    doc.add_heading("1.6 Parça 5 — Kira ve yaşam maliyeti", level=2)
    doc.add_paragraph(
        f"TCMB birim kira (değerlemesi yapılan konut, {bk.get('donem') or '—'}): {_f(bk.get('tl_m2_ay'), 2)} TL/m²/ay; "
        f"yıllık değişim {_f((bk.get('yoy') or 0) * 100) if bk.get('yoy') is not None else '—'} yüzde. "
        f"90–110 m² için kiracı başına piyasa {_f(_band('aylık piyasa kirası (kiracı başına)').get('alt'), 0)}–{_f(_band('aylık piyasa kirası (kiracı başına)').get('ust'), 0)} TL/ay. "
        f"HEKİS havuz kirası {_f(_band('HEKİS havuz kirası').get('alt'), 0)} TL/ay (modellendi). "
        "Tek sistem kira kolu birincil ölçülmedi (kiracı hane × ödenen kira); satır olculmedi durur. "
        "TÜFE yıllık 2026-09: yüzde 29,73."
    )

    doc.add_heading("1.7 Sorunun birleşmesi", level=2)
    doc.add_paragraph(
        "Kilitli borç ödenmeyince yeni kredi istenir; yeni kredi faiz doğurur; faiz mevduatı ve kârı şişirir; "
        "mevduat yine kredi olur; kira ve fiyat haneyi sıkar; hane tüketimi düşünce firmanın tahsilatı yine düşer. "
        "Döngü tek kapıdan kırılmaz. Beş parça, beş kesik ister."
    )
    _add_table(
        doc,
        ["Parça", "Nesne", "Büyüklük", "Etiket"],
        [
            ["1 Kilitli borç", "F içi diğer borç (ZP44 farkı)", f"{_f(zp44.get('sektor_ici'))} mr", "ölçüm (brüt)"],
            ["1 Tavan", "Hazneler arası yeni_tavan", "0,2582", "üst sınır"],
            ["2 Takip", "G1 firma 2026-09", "yüzde 2,52", "ölçüm"],
            ["3 Kredi stoğu", "F F.4 2026-Q1", f"{_f(_al(a3, 'S0_milyar'))} mr", "ölçüm"],
            ["3 Faiz", "TP.KTF17 2026-09", "yüzde 53,19", "ölçüm"],
            ["4 Adres", "Üç mevduat stoku", f"{_f(a4.get('adres_toplam_milyar'))} mr", "ölçüm"],
            ["4 İtiş", "F.4 akım / GSYH 2025", "yüzde 7,62", "ölçüm"],
            ["5 Birim kira", f"{bk.get('seri') or 'TP.BK.TR'} {bk.get('donem') or '—'}", f"{_f(bk.get('tl_m2_ay'), 2)} TL/m²/ay", "ölçüm"],
            ["5 TÜFE", "2026-09 yıllık", "yüzde 29,73", "ölçüm"],
        ],
    )

    # ------------------------------------------------------------------
    doc.add_heading("2. Çözüm: beş adım", level=1)
    doc.add_paragraph(
        "Tek sistem, aynı yükü beş yerden keser. Sıra vardır: önce kilitli borç (adım 1), sonra kalanın ödenmesi "
        "(adım 2), sonra giren stokta faizin durması (adım 3), sonra mevduatın kâğıda dönmesi (adım 4), sonra kira "
        "(adım 5). Zaman pencereleri örtüşmez: K1 mahsup 2027, K2 stok tavanı 2028, K3 adres 2029 (tek_sistem_kademe). "
        "Katman sayıları birbirine taşınmaz."
    )
    _add_table(
        doc,
        ["Adım", "Ne keser", "Kilitli dosya ne der", "Yan dosya"],
        [
            ["1 Mahsup", "Karşılıklı (kilitli) borç", "silinen boş; tavan 0,0728 / 0,2582", "adim1_nace.py"],
            ["2 Ödeme + şart", "Vadeyi uzatan davranış; ücret gecikmesi", "sentetik temerrüt 0, modellendi", "adim2_nace_ag.py"],
            ["3 Faiz durması", "Sisteme giren F.4 stoğunda tahakkuk", "faiz durması modellenmedi (orası kilit)", "adim3_faiz_durma.py"],
            ["4 Adres yönlendirme", "Mevduat → kâğıt; kredi itişi", "üç adres ölçüldü; senet modellenmedi", "adim4_adres_yonlendirme.py"],
            ["5 Kira", "Piyasa kirası → politika kirası", "kira olculmedi; HEKİS 20.000 modellendi", "adim5_kira.py"],
        ],
    )

    # ------------------------------------------------------------------
    doc.add_heading("3. Adım 1 — Karşılıklı borç silinir", level=1)
    doc.add_heading("3.1 Ne yapar", level=2)
    doc.add_paragraph(
        "A’nın B’ye, B’nin A’ya (veya döngüyle) borcunun ortak kısmı ödenmeden düşer. Net pozisyon değişmez: "
        "net borçlu yine borçludur, net alacaklı yine alacaklıdır. Yalnız kilitli brüt gider. "
        "Bu, iflas değildir; kayıtların birbirini götürmesidir."
    )
    doc.add_heading("3.2 Üç katman (toplanmaz)", level=2)
    doc.add_paragraph(
        f"(a) Ölçüm — F içi stok {_f(zp44.get('sektor_ici'))} milyar (2026-Q1). "
        f"(b) Üst sınır — NACE netleştirme tabanı: brüt {_f(taban.get('brut_milyar'))}, "
        f"silinen_max {_f(taban.get('silinen_max_milyar'))} = yüzde {_f((taban.get('silinen_max_oran') or 0) * 100, 1)}. "
        "Kısım içi borç düğümde görünmediği için gevşek üst sınırdır. "
        "(c) Varsayım — çekim/RAS kenar dağılımı + optimal mahsup: silinen yüzde 90,5. Tam graftadır; gerçek seyrek ağda daha az."
    )
    doc.add_heading("3.3 Yüzde 20 eşiği", level=2)
    doc.add_paragraph(
        "Eşik: brütün beşte biri silinebiliyorsa adım 1 kapıyı açar. Oran varsayımdır; 'yaklaşık yüzde 20' "
        "cümlesinin koşusudur. Üç tabanda sayı, hepsi kendi üst sınırının içinde:"
    )
    _add_table(
        doc,
        ["Taban", "Brüt (mr)", "Yüzde 20 silinen (mr)", "Üst sınır (mr)", "İçinde mi", "Üst sınıra oranı"],
        [
            [s.get("taban", ""), _f(s.get("brut_milyar")), _f(s.get("silinen_milyar")),
             _f(s.get("ust_sinir_milyar")), "evet" if s.get("ust_sinir_icinde") else "hayır",
             _f(s.get("ust_sinira_oran"), 2)]
            for s in y20
        ] or [["—", "—", "—", "—", "—", "—"]],
    )
    doc.add_paragraph(
        "Okuma: yüzde 20, NACE ve EVDS F-içi tabanda tavanın yüzde 22’sini, hazneler arasında yüzde 78’ini kullanır. "
        "Çekim koşusu yüzde 90,5 verdiği için yüzde 20 temkinlidir. Üst sınır içinde kalması olabilirliği gösterir, "
        "gerçekleştiğini değil. adim1_stok.csv silinen sütunu yine boştur."
    )

    # ------------------------------------------------------------------
    doc.add_heading("4. Adım 2 — Kalan borç ödenir, şart kalkar", level=1)
    doc.add_paragraph(
        "Silinmeyen kısım tur tur ödenir. Holding nakit yetse bile vadesi gelenin yalnız bir payını öder "
        "(sentetikte 0,5). Devlet şart kaldıracıyla bu payı 1’e çeker. Aracının serbest kalan nakdinden ücrete "
        "geçen pay β’dır. Sentetik β = 0,3 parametredir. Ölçülmüş tavan: personel_aylık / (ticari borç + personel_aylık) "
        f"= {_f(_al(a2, 'beta_tavan'), 4)}. 0,3 bunun yaklaşık yedi katıdır."
    )
    doc.add_paragraph(
        "Ölçülmüş ağ (17 NACE + 17 hane + dış düğüm; nakit = hazır değerler, ücret = personel/12): "
        "λ = 1 (ölçülen nakit) iken brüt 15 temerrüt → mahsup sonrası 0, kredi ihtiyacı 8.329 → 0, silinen yüzde 88,5. "
        f"G1 çapası λ* = {_f(_al(a2, 'kalibrasyon', 'lambda'), 4)}: nakit yüzde 11 kısılınca mahsup sonrası 1 kısım yine düşer. "
        "Yüzde 20 silindiğinde bu tam-graf sonucu geçerli değildir: kalan yüzde 80 hâlâ ödenir, temerrüt sıfıra inmez, "
        "şart kaldıracı gerekir."
    )
    doc.add_paragraph(
        "Kısım A (tarım) YSHİ kapsamı dışıdır: ücret ve çalışan 0; o kısımda ücret temerrüdü ölçülemez. "
        "Temerrüt eden kısım, o kısmın toplulaştırılmış nakdinin borcu karşılamadığı anlamına gelir; kısım içi dağılım görünmez."
    )

    # ------------------------------------------------------------------
    doc.add_heading("5. Adım 3 — Faiz tahakkuku durur", level=1)
    doc.add_paragraph(
        "Kural: durdurulan stok D_t = κ · u2_t · S₀; duran faiz (çeyrek) I_t = ψ · (r_t / 4) · D_t. "
        "S₀ F.4 stoğudur (ölçüm). u2, 2028 stok penceresinin rampa oranıdır. κ ∈ {0,25; 0,50; 1,00} varsayımdır: "
        "tek sisteme giren ve faizi duran pay. ψ = 0,358, 2024 finansman giderinin o yılın faiz×stok çarpımına oranıdır."
    )
    doc.add_paragraph(
        "SFC: firmanın ödemediği faiz, bankanın almadığı faizdir. F NL += I, B′ NL −= I, toplam 0. "
        "B′ yerine K′ üstlenirse sütun değişir, toplam değişmez. İkisi toplanmaz. "
        "Yüzde 20 eşiğine en yakın bant κ = 0,25’tir (ticari mahsup stoğu ile F.4 stoğu aynı nesne değildir; eşitlenmez)."
    )
    satir3 = []
    for kap in ("0.25", "0.5", "1.0"):
        yl = yil3.get(kap) or yil3.get(float(kap)) or {}
        satir3.append([kap] + [_f(yl.get(y)) for y in ("2027", "2028", "2029", "2030", "2031")])
    _add_table(doc, ["κ", "2027", "2028", "2029", "2030", "2031"], satir3 or [["—"] * 6])
    doc.add_paragraph(
        "2029’dan itibaren (rampa bitince) κ = 0,25 → 1.208 mr/yıl (2024 giderinin 0,38’i); "
        "κ = 0,50 → 2.415 mr (0,77); κ = 1 → 4.831 mr (1,54). "
        "r_t 2026-09’dan sonra sabit tutulmuştur (varsayım). 'Faiz durdu, firma rahatladı' denmez."
    )

    # ------------------------------------------------------------------
    doc.add_heading("6. Adım 4 — Mevduat kâğıda döner", level=1)
    doc.add_paragraph(
        "Üç adres stoku ölçülmüştür; senet satırı modellenmedi kalır, kilit durur. Kilit dışında band: "
        "İhraç_t = θ · 19.362 · Δu3_t (u3 = 2029 penceresi). Vade 8 çeyrek; vadede (1−χ) mevduata döner. "
        "Prim π · stok / 4. θ ∈ {0,10; 0,25; 0,50}, χ ∈ {0; 0,50}, π ∈ {0,02; 0,05} — hepsi varsayım. "
        "Endeks (hedef) bacağı hesaplanmadı: hedef patikası depoda yok. HEKİS senedi ile eşitlenmez."
    )
    doc.add_paragraph(
        "SFC (çeyrek): tutucu VF.2 (mevduat) düşer, VF.3 (kâğıt) artar, NFP 0. Banka F.2 ve rezerv düşer, NFP 0. "
        "İhraççı K′ F.3 ve TCMB hesabı artar, NFP 0. Prim K′’den tutucuya transfer, toplam NL 0. "
        "Kredi itişi: bankanın kaybettiği mevduat × 0,08 (kademe sabiti) yıllık kredi daralması."
    )
    ozet4 = a4.get("senaryolar") or {}
    secilen = [
        ozet4.get("th0.1_chi0.0_pi0.02") or {},
        ozet4.get("th0.25_chi0.0_pi0.02") or {},
        ozet4.get("th0.25_chi0.5_pi0.05") or {},
        ozet4.get("th0.5_chi0.0_pi0.05") or {},
    ]
    _add_table(
        doc,
        ["θ", "χ", "π", "Tepe stok (mr)", "Prim 2031 (mr)", "Kredi itki azalt, tepe, yıllık (mr)"],
        [
            [_f(o.get("theta"), 2), _f(o.get("chi"), 2), _f(o.get("pi"), 2),
             _f(o.get("tepe_stok")), _f((o.get("prim_yillik") or {}).get("2031")),
             _f(o.get("kredi_itki_azalt_tepe_yillik"))]
            for o in secilen if o
        ] or [["—"] * 6],
    )
    doc.add_paragraph(
        "Yüzde 20 eşiği adım 4’ü açmaz; adım 4 üçüncü kademedir (2029). Paket olarak: θ = 0,25’te tepe 4.840 mr, "
        "kredi itişi ≈ 387 mr/yıl zayıflar. Prim, κ = 0,5 duran faizin (2.415 mr) en fazla yüzde 16’sıdır."
    )

    # ------------------------------------------------------------------
    doc.add_heading("7. Adım 5 — Kira düşer", level=1)
    doc.add_paragraph(
        "Konut topluma açılırsa (HEKİS) politika kirası piyasanın altına iner. Kiracı (Ha) kazanır, ev sahibi (Ho) "
        "kaybeder; hane toplam NL değişmez. Kurumsal ev sahibi (F) payı ölçülmedi. "
        f"Birim kira ölçüm: {_f(bk.get('tl_m2_ay'), 2)} TL/m²/ay. Alan 90–110 m² ve kiracı oranı 0,25–0,30 varsayım; "
        f"hane sayısı {_f(a5.get('hane_sayisi'), 0)} elle (doğrulanmadı). Yol A yıllık kira akışı "
        f"{_f(band_a[0]) if len(band_a) > 0 else '—'}–{_f(band_a[1]) if len(band_a) > 1 else '—'} milyar. "
        "Depodaki konut_stok proxy’si 255 milyar: finansal varlık payıdır, yol A ile toplanmaz."
    )
    _add_table(
        doc,
        ["Nesne", "Alt", "Üst", "Etiket"],
        [
            ["Birim kira (TL/m²/ay)", _f(bk.get("tl_m2_ay"), 2), _f(bk.get("tl_m2_ay"), 2), "ölçüm"],
            ["Aylık piyasa kirası (kiracı)", _f(_band("aylık piyasa kirası (kiracı başına)").get("alt"), 0), _f(_band("aylık piyasa kirası (kiracı başına)").get("ust"), 0), "band, varsayım"],
            ["HEKİS havuz kirası (TL/ay)", _f(_band("HEKİS havuz kirası").get("alt"), 0), _f(_band("HEKİS havuz kirası").get("ust"), 0), "modellendi"],
            ["Kiracı başına fark (TL/ay)", _f(_band("kiracı başına aylık fark (piyasa − HEKİS)").get("alt"), 0), _f(_band("kiracı başına aylık fark (piyasa − HEKİS)").get("ust"), 0), "band, varsayım"],
            ["Kira akışı yıllık, yol A (mr)", _f(band_a[0]) if band_a else "—", _f(band_a[1]) if len(band_a) > 1 else "—", "band, varsayım"],
            ["Ho→Ha transfer, kapsama %20 (mr/yıl)", _f(_band("Ho→Ha yıllık transfer, kapsama payı 20%").get("alt")), _f(_band("Ho→Ha yıllık transfer, kapsama payı 20%").get("ust")), "band, varsayım"],
            ["Ho→Ha transfer, kapsama %50 (mr/yıl)", _f(_band("Ho→Ha yıllık transfer, kapsama payı 50%").get("alt")), _f(_band("Ho→Ha yıllık transfer, kapsama payı 50%").get("ust")), "band, varsayım"],
            ["Ho→Ha transfer, kapsama %100 (mr/yıl)", _f(_band("Ho→Ha yıllık transfer, kapsama payı 100%").get("alt")), _f(_band("Ho→Ha yıllık transfer, kapsama payı 100%").get("ust")), "band, varsayım"],
        ],
    )
    doc.add_paragraph(
        "Yüzde 20 burada kiracı kapsamasıdır (adım 1’deki silinen oranından başka nesne). "
        f"Kiracıların beşte biri girerse ev sahibinden kiracıya yılda {_f(_band('Ho→Ha yıllık transfer, kapsama payı 20%').get('alt'))}–{_f(_band('Ho→Ha yıllık transfer, kapsama payı 20%').get('ust'))} milyar geçer. "
        "adim5.csv kira satırı olculmedi kalır."
    )

    # ------------------------------------------------------------------
    doc.add_heading("8. Yüzde 20 sağlandığında beş öneri ne yapar", level=1)
    doc.add_paragraph(
        "Yüzde 20, birinci adımın eşiğidir. Sağlandığı varsayılırsa (ölçülmezse) beş önerinin birlikte yaptığı iş:"
    )
    _add_table(
        doc,
        ["Öneri", "Yaptığı iş", "Sayı (yüzde 20 bandı)", "Etiket"],
        [
            ["1 Mahsup", "Kilitli borcun beşte birini siler",
             "2.867 / 7.986 / 15.774 mr (üç taban)", "varsayım; üst sınır içinde"],
            ["2 Ödeme + şart", "Kalan yüzde 80’i ödetir; uzatmayı keser",
             "Tam grafta temerrüt 0; yüzde 20’de sıfıra inmez", "modellendi, ölçülmüş düğüm"],
            ["3 Faiz durması", "Giren F.4 stoğunda tahakkuku keser",
             "κ = 0,25 → 1.208 mr/yıl (2029+)", "κ varsayım; ψ ölçüm türevi"],
            ["4 Adres", "Mevduatı kâğıda çevirir, yeni krediyi kısar",
             "θ = 0,25 → tepe 4.840 mr; itiş −387 mr/yıl", "band, varsayım; senet kilitli"],
            ["5 Kira", "Politika kirasına çeker; Ha←Ho transfer",
             "Kapsama %20 → 52–160 mr/yıl", "band; satır olculmedi"],
        ],
    )
    doc.add_paragraph(
        "Beşi aynı anda 'enflasyon 7,6 puan iner' demez. Kredi itişinin fiyata geçen payı kapısı boştur. "
        "Aşağıdaki enflasyon bölümü bunu açar."
    )

    # ------------------------------------------------------------------
    doc.add_heading("9. Enflasyon — kapı boş, bant durur", level=1)
    doc.add_paragraph(
        "Kanal: 2025 itiş 7,62 puan GSYH; model itişi keser; etki = −geçiş × kesilen itiş. "
        f"OLS + Newey-West (2015-Q3..2025-Q4, n = {ana.get('n', '—')}): uzun dönem geçiş payı "
        f"LR = {_f(ana.get('LR_gecis_payi'), 3)}, se = {_f(ana.get('se_nw4'), 3)} (`tahmin_ols`). "
        "Kredi katsayıları her spesifikasyonda pozitif; kesinlik yok. 95 bandı [0, 1]’i daraltmaz. "
        "68 bandı [0,20; 1] → etki [−7,62; −1,5] puan. RAPOR'un 'üçte biri' 95 aralığının içindedir. "
        "tavan_akis.csv gecis/tavan boş kalır."
    )
    _add_table(
        doc,
        ["Yıl", "Anket (yüzde)", "Mevcut bant (geçiş 0..1)", "68 bandı (geçiş 0,20..1)"],
        [
            ["2026 (taban)", "29,73 (TÜFE 2026-09)", "—", "—"],
            ["2027", "22,69", "15,07 – 22,69", "15,07 – 21,2"],
            ["2028", "18,32", "10,70 – 18,32", "10,70 – 16,8"],
            ["2031", "12,09", "4,47 – 12,09", "4,47 – 10,6"],
        ],
    )
    doc.add_paragraph(
        "Adım 3 maliyet kanalı (faiz durması) ve adım 5 kira kanalı fiyata geçişi ölçülmediği için bu banda "
        "yazılmaz; yönleri aşağıdır. Adım 2 ücret kanalı (β tavanı 0,044) zayıf ve yukarıdır. "
        "Döviz ve politika faizi modellenmedi; senaryo ankete eşittir."
    )

    # ------------------------------------------------------------------
    doc.add_heading("10. Ne denmez", level=1)
    for line in [
        "Beş adım kuruldu. — Şu adım şu etiket; kilitli kapı boş.",
        "Stok yüzde 20 silindi. — Oran varsayım; silinen sütunu boş; üç taban üst sınırın içinde.",
        "Firmalar mahsupla battı / kurtuldu. — Net borçlu kurtulmaz; yalnız kilitli brüt gider.",
        "Faiz durdu, firma rahatladı. — κ varsayım, r ileri sabit, ψ 2024 kapsamından.",
        "Senet modellendi / HEKİS senedi budur. — adim4 senet satırı modellenmedi; HEKİS başka nesne.",
        "HEKİS döngüyü kırdı. — Kira satırı olculmedi; HEKİS kirası modellendi.",
        "Enflasyon 7,6 puan iner. — Bant [0, −7,62]; 68 ile [−7,62, −1,5]; kapı boş.",
        "Katman sonuçlarını toplamak. — Hazne tavanı + F içi oran + kira bandı toplanmaz.",
    ]:
        doc.add_paragraph(line, style="List Bullet")

    # ------------------------------------------------------------------
    doc.add_heading("11. Etiketler ve yenileme", level=1)
    doc.add_paragraph(
        "İyiden kötüye: ölçüm > ölçüm türevi > üst sınır > tahmin_ols > kalibrasyon varsayım > "
        "modellendi / band varsayım > varsayım > dış kaynak elle. Hedef satırın etiketi, girdilerinin "
        "en kötüsünden iyi yazılamaz."
    )
    doc.add_paragraph("Yenileme sırası:")
    for line in [
        "python3 adim1_nace.py",
        "python3 adim2_nace_ag.py",
        "python3 adim3_faiz_durma.py",
        "python3 adim4_adres_yonlendirme.py",
        "python3 gecis_payi_band.py",
        "python3 adim5_kira.py",
        "python3 girdi_haritasi.py",
        "python3 bes_adim.py && python3 test_bes_adim.py",
        "python3 yayin_bes_adim_rapor_docx.py",
    ]:
        doc.add_paragraph(line, style="List Bullet")
    doc.add_paragraph(
        "Kaynaklar: ADIM1_NACE.md, ADIM2_NACE_AG.md, ADIM3_FAIZ_DURMA.md, ADIM4_ADRES_YONLENDIRME.md, "
        "GECIS_PAYI_BAND.md, ADIM5_KIRA.md, GIRDI_HARITASI.md, BES_ADIM.md, BES_YIL_SENARYO.md. "
        "Markdown ile çelişirse JSON/CSV esas alınır."
    )
    doc.add_paragraph(
        "\n— Belge otomatik üretilmiştir. Politika tavsiyesi değildir."
    )
    return doc


def main() -> None:
    doc = build()
    doc.save(OUT)
    OUT_YAYIN.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT_YAYIN)
    print(f"Yazildi: {OUT}")
    print(f"Yazildi: {OUT_YAYIN}")


if __name__ == "__main__":
    main()
