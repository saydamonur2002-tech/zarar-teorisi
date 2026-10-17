#!/bin/bash
# Tüm zincir. Kullanım: ZT_AG=cevrimdisi|kaydet ./zincir.sh   (varsayılan cevrimdisi)
cd "$(dirname "$0")"; set -o pipefail; export PYTHONPATH="$PWD" MPLBACKEND=Agg ZT_AG=${ZT_AG:-cevrimdisi}
PY=${PY:-/tmp/zt/v/bin/python}; mkdir -p log
# akis_model iki kez: ilki paneli ve L_v2'yi yazar; bilateral_D L_bil'i ondan üretir;
# ikincisi özete taze L_bil'i gömer. kalibre, matris yazıldıktan sonra koşar.
# uc_kural, maliyet_kar_orani'ndan önce: maliyet diskteki csv'yi okur.
ADIMLAR="tek_sistem_kopru stok_silim tavan_akis vadeli_kalicilik gecis_payi_band
akis_model bilateral_D akis_model kalibre_lambda kur_kanali L_cift_kayit
rev_adim1 adim1_nace adim2_nace_ag rev_adim2 adim3_faiz_durma rev_adim3 rev_sok adim4_adres_yonlendirme rev_adim4 adim45_birim rev_adim45 adim45_maliyet adim5_kira varsayim_esik bes_adim bes_adim_maliyet
uc_kural_senaryo maliyet_kar_orani odeme_dagilim odeme_gercek mahsup_sektor_evds rant_aktor entegre_ve_test takas_simulasyon ${EK_ADIMLAR}"
for s in $ADIMLAR; do [ -f $s.py ] || continue; timeout 900 $PY $s.py > log/$s.txt 2>&1; echo "$s rc=$?"; done
$PY -m pytest -q ${EK_TESTLER} 2>&1 | tail -5
