"""Taslak çıktılarını sırayla yazar. Karar dosyalarına ve kilitlere dokunmaz.

  python3 analiz/senet/yaz.py
"""
from __future__ import annotations

import bacak
import fx_durdur
import olcek
import patika
import prim_tavan
import rant


def main():
    olcek.main()
    prim_tavan.main()
    bacak.main()
    rant.main()
    patika.main()
    fx_durdur.main()


if __name__ == "__main__":
    main()
