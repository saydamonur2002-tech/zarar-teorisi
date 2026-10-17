import csv
import json
from datetime import datetime, timezone

import haftalik_guncelle as h

ZAMAN = datetime(2026, 10, 19, 5, 17, tzinfo=timezone.utc)


def satir(donem, seri, deger, grup="G1"):
    return (grup, donem, seri, f"{seri} adı", "last", deger)


def kur(tmp_path, donmus):
    """tmp_path altında bir 'x' kaynağı: dondurulmuş x_ham.csv + kaynaklar.json."""
    (tmp_path / "veri_canli").mkdir()
    (tmp_path / "veri_canli" / "kaynaklar.json").write_text(
        json.dumps([{"dosya": "x", "grup": "G1", "baslangic": "01-01-2025"}]), encoding="utf-8")
    with open(tmp_path / "x_ham.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(h.BASLIK)
        w.writerows(donmus)


def sahte(satirlar):
    return lambda grup, start, end, freq: ([s for s in satirlar if s[0] == grup], 1)


def kos(tmp_path, satirlar, **kw):
    return h.calistir(kok=tmp_path, bitis="19-10-2026", simdi=ZAMAN, getir=sahte(satirlar), bekle=lambda s: None, **kw)


def test_karsilastir_siniflari():
    eski = {("G", "2026-Q1", "S"): ("a", "last", 1.0), ("G", "2026-Q2", "S"): ("a", "last", 2.0),
            ("G", "2025-Q4", "S"): ("a", "last", 9.0)}
    yeni = {("G", "2026-Q1", "S"): ("a", "last", 1.5), ("G", "2026-Q2", "S"): ("a", "last", 2.5),
            ("G", "2026-Q3", "S"): ("a", "last", 3.0)}
    r = h.karsilastir(eski, yeni)
    assert r["yeni"] == [("G", "2026-Q3", "S")] and r["yeni_donemler"] == ["2026-Q3"]
    assert r["silinen"] == [("G", "2025-Q4", "S")]
    assert [k[1] for k, _, _ in r["gecmis"]] == ["2026-Q1", "2026-Q2"]  # ikisi de son dönem (Q3) değil
    assert r["acik"] == []
    assert r["son_once"] == "2026-Q2" and r["son_sonra"] == "2026-Q3"


def test_son_donem_revizyonu_acik_donemdir():
    eski = {("G", "2026-09", "S"): ("a", "last", 1.0)}
    yeni = {("G", "2026-09", "S"): ("a", "last", 1.1)}
    r = h.karsilastir(eski, yeni)
    assert len(r["acik"]) == 1 and r["gecmis"] == []


def test_nan_satiri_okunmaz(tmp_path):
    kur(tmp_path, [satir("2026-Q1", "S", "nan"), satir("2026-Q1", "T", 1.0)])
    assert list(h.oku(tmp_path / "x_ham.csv")) == [("G1", "2026-Q1", "T")]


def test_ilk_calisma_yeni_gozlem_ve_ozet(tmp_path, monkeypatch):
    kur(tmp_path, [satir("2026-Q1", "S", 1.0)])
    ozet = tmp_path / "ozet.txt"
    monkeypatch.setenv("OZET_DOSYASI", str(ozet))
    assert kos(tmp_path, [satir("2026-Q1", "S", 1.0), satir("2026-Q2", "S", 2.0)]) == 0
    assert (tmp_path / "veri_canli" / "x.csv").exists()
    md = (tmp_path / "SON_GUNCELLEME.md").read_text(encoding="utf-8")
    assert "| x | 1 | 2026-Q2 | 2026-Q1 → 2026-Q2 |" in md and "ilk kez oluşturuldu" in md
    assert "1 yeni gözlem" in ozet.read_text(encoding="utf-8")
    assert "- 2026-10-19: 1 yeni gözlem" in (tmp_path / "veri_canli" / "GUNLUK.md").read_text(encoding="utf-8")


def test_ilk_calisma_degisiklik_yoksa_kopya_yazilir_gunluk_yazilmaz(tmp_path):
    kur(tmp_path, [satir("2026-Q1", "S", 1.0)])
    assert kos(tmp_path, [satir("2026-Q1", "S", 1.0)]) == 0
    assert (tmp_path / "veri_canli" / "x.csv").exists() and not (tmp_path / "veri_canli" / "GUNLUK.md").exists()


def test_degisiklik_yoksa_hicbir_sey_yazilmaz(tmp_path):
    kur(tmp_path, [satir("2026-Q1", "S", 1.0)])
    veri = [satir("2026-Q1", "S", 1.0), satir("2026-Q2", "S", 2.0)]
    assert kos(tmp_path, veri) == 0
    (tmp_path / "SON_GUNCELLEME.md").unlink()
    onceki = (tmp_path / "veri_canli" / "x.csv").read_bytes()
    assert kos(tmp_path, veri) == 0
    assert not (tmp_path / "SON_GUNCELLEME.md").exists()
    assert (tmp_path / "veri_canli" / "x.csv").read_bytes() == onceki


def test_revizyon_sonraki_calismada_yakalanir(tmp_path):
    kur(tmp_path, [satir("2026-Q1", "S", 1.0)])
    assert kos(tmp_path, [satir("2026-Q1", "S", 1.0), satir("2026-Q2", "S", 2.0)]) == 0
    assert kos(tmp_path, [satir("2026-Q1", "S", 1.2), satir("2026-Q2", "S", 2.0)]) == 0
    md = (tmp_path / "SON_GUNCELLEME.md").read_text(encoding="utf-8")
    assert "En büyük geçmiş revizyonlar" in md and "1 → 1.2" in md
    gunluk = (tmp_path / "veri_canli" / "GUNLUK.md").read_text(encoding="utf-8").splitlines()
    assert sum(s.startswith("- ") for s in gunluk) == 2


def test_supheli_kuculme_reddedilir(tmp_path):
    kur(tmp_path, [satir(f"2026-{m:02d}", "S", float(m)) for m in range(1, 11)])
    assert kos(tmp_path, [satir("2026-01", "S", 1.0)]) == 1
    assert not (tmp_path / "veri_canli" / "x.csv").exists()


def test_cekme_hatasi_yeniden_dener_sonra_hata_verir(tmp_path):
    kur(tmp_path, [satir("2026-Q1", "S", 1.0)])
    cagri, bekleme = [], []

    def bozuk(grup, start, end, freq):
        cagri.append(grup)
        raise OSError("ağ yok")

    assert h.calistir(kok=tmp_path, bitis="19-10-2026", simdi=ZAMAN, getir=bozuk, bekle=bekleme.append) == 1
    assert len(cagri) == h.DENEME and bekleme == [2, 4]
    assert not (tmp_path / "veri_canli" / "x.csv").exists()


def test_bos_yanit_hatadir(tmp_path):
    kur(tmp_path, [satir("2026-Q1", "S", 1.0)])
    assert kos(tmp_path, []) == 1
