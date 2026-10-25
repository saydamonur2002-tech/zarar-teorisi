#!/usr/bin/env python3
"""Zip içindeki etki cephesi testlerini çıkarılmış modele karşı çalıştırır.

İki paket:

- ``yayin/etki-cephesi-model.zip`` (güncel)
- ``etki_cephesi/zarar-teorisi/cursor/orta-vade-senaryo-f01a/yayin/etki-cephesi-model.zip``

Güncel pakette ``tests/test_etki_cephesi_sfc_revize.py`` iki testi ve
``etki_cephesi/bolge_stok_akis.py`` ``_incoming/zarar-teorisi-main`` altındaki
``akis_model.py`` ile ``akis_model_ozeti.json`` dosyasını ister. Bu dizin zip'te
yoktur. Betik, bu reponun kökünü oraya bağlar; kökte bu dosyalar vardır.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
PAKETLER = (
    ("guncel", KOK / "yayin" / "etki-cephesi-model.zip"),
    (
        "eski",
        KOK
        / "etki_cephesi"
        / "zarar-teorisi"
        / "cursor"
        / "orta-vade-senaryo-f01a"
        / "yayin"
        / "etki-cephesi-model.zip",
    ),
)


def _cikar(zip_yol: Path, hedef: Path) -> None:
    with zipfile.ZipFile(zip_yol) as arsiv:
        arsiv.extractall(hedef)


def _gelen_bagla(model: Path) -> None:
    gelen = model / "_incoming"
    gelen.mkdir(parents=True, exist_ok=True)
    bag = gelen / "zarar-teorisi-main"
    if bag.exists() or bag.is_symlink():
        bag.unlink()
    bag.symlink_to(KOK)


def _testler(model: Path) -> list[str]:
    dizin = model / "tests"
    bulunan = sorted(p.relative_to(model).as_posix() for p in dizin.glob("test_etki_cephesi_*.py"))
    if not bulunan:
        raise SystemExit(f"test yok: {dizin}")
    return bulunan


def calistir(ad: str, zip_yol: Path) -> int:
    print(f"== {ad}: {zip_yol.relative_to(KOK)}", flush=True)
    if not zip_yol.is_file():
        print(f"eksik: {zip_yol}", flush=True)
        return 1
    with tempfile.TemporaryDirectory(prefix=f"etki-{ad}-") as gecici:
        model = Path(gecici)
        _cikar(zip_yol, model)
        _gelen_bagla(model)
        testler = _testler(model)
        komut = [sys.executable, "-m", "pytest", *testler, "-q", "--tb=line"]
        sonuc = subprocess.run(komut, cwd=model, check=False)
        ozet = model / "etki_cephesi" / "durum_ozeti.py"
        if ozet.is_file() and sonuc.returncode == 0:
            ozet_sonuc = subprocess.run([sys.executable, str(ozet)], cwd=model, check=False)
            if ozet_sonuc.returncode != 0:
                print(f"{ad}: durum_ozeti.py çıkış {ozet_sonuc.returncode}", flush=True)
                return ozet_sonuc.returncode
        print(f"{ad}: pytest çıkış {sonuc.returncode}", flush=True)
        return sonuc.returncode


def main() -> None:
    kod = 0
    for ad, yol in PAKETLER:
        if calistir(ad, yol) != 0:
            kod = 1
    raise SystemExit(kod)


if __name__ == "__main__":
    main()
