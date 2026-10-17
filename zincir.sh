#!/bin/bash
# Tüm zincir. Kullanım: ZT_AG=cevrimdisi|kaydet ./zincir.sh   (varsayılan cevrimdisi)
cd "$(dirname "$0")"; export PYTHONPATH="$PWD" MPLBACKEND=Agg ZT_AG=${ZT_AG:-cevrimdisi}
PY=${PY:-/tmp/zt/v/bin/python}; mkdir -p log
ADIMLAR="tek_sistem_kopru stok_silim tavan_akis vadeli_kalicilik gecis_payi_band kalibre_lambda akis_model bilateral_D kur_kanali L_cift_kayit
rev_adim1 adim1_nace adim2_nace_ag rev_adim2 adim3_faiz_durma rev_adim3 adim4_adres_yonlendirme rev_adim4 adim45_birim rev_adim45 adim45_maliyet adim5_kira varsayim_esik bes_adim bes_adim_maliyet
maliyet_kar_orani uc_kural_senaryo odeme_dagilim odeme_gercek mahsup_sektor_evds rant_aktor entegre_ve_test takas_simulasyon ${EK_ADIMLAR}"
for s in $ADIMLAR; do [ -f $s.py ] || continue; timeout 900 $PY $s.py > log/$s.txt 2>&1; echo "$s rc=$?"; done
$PY -m pytest -q test_bes_adim.py test_adim45_maliyet.py test_rev.py ${EK_TESTLER} 2>&1 | tail -3
