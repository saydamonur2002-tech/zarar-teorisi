# Veriler [VERİ]: HMB Kamu Borç Yön. Raporu Ağu-2026 (milyon TL→mlr); BDDK haftalık 2 Eki 2026
ic_borc=9545.4; tufe_end=764.9; ic_tl=7748.0; kredi=28642.3; ticari_tl=11260.7; npl=914.6; mevduat=32365
gider={(k,p):19361*k*p for k in (.02,.05,.10) for p in (.005,.01,.02)}
S={'1/3':(1/3,1/3,1/3),'20-40-40':(.2,.4,.4),'50-25-25':(.5,.25,.25),'40-30-30':(.4,.3,.3)}
o=['GİDER (mlr TL/yıl) kaydırma×prim → toplam']
for (k,p),g in gider.items(): o.append(f' %{k*100:.0f}×%{p*100:.1f}: {g:.1f}')
o.append('\nGELİR (reel, mlr TL/yıl, hedef tutarsa; r=risk primi düşüşü puan)')
G={}
for r in (0,.5,1,2):
  for dn in (0,.25,.5):
    hz=ic_tl*r/100; bk=kredi*dn/100*0.743; fr=ticari_tl*r/100   # banka: NPL düşüşü×karşılık oranı %74,3
    G[(r,dn)]=(hz,fr,bk); o.append(f' r={r} NPLdüşüş={dn}: Hazine {hz:.0f} | firma {fr:.0f} | banka {bk:.0f}')
o.append('\nNET (gider üst uç 38,7; r=0,5, NPL 0,25) devlet/firma/banka')
for k,s in S.items():
  for (r,dn) in ((0,0),(.5,.25)):
    g=G[(r,dn)];n=[g[i]-s[i]*38.7 for i in range(3)]
    o.append(f' {k} r={r} npl={dn}: '+' / '.join(f'{x:.1f}' for x in n))
o.append('\nBanka yansıtma: borçluya düşen = banka payı×yansıtma; 40-30-30, 38,7 üst uç: '+', '.join(f'%{y*100:.0f}→{.3*38.7*y:.1f} mlr; kredi faizine {.3*38.7*y/kredi*1e4:.1f} bp' for y in (0,.5,1)))
o.append('Kısmi tutma (gelir ve prim yarıya): netler yarıya, işaret aynı. Tutmazsa: prim 0, gelir 0, net 0 (senet TÜFE+kupon maliyeti ayrı, nominal DİBS ile Fisher altında nötr).')
open('cikti.txt','w').write('\n'.join(o));print('\n'.join(o))
