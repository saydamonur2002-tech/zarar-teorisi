import csv
TLm,YPm,G=20495.3,12613.0,85299;NP=676.3*12/8;RWA=4771.2/.166
rt,ry=.4330,.0258;rows=[]
for k in (.25,.5,1):
  s=k/.5;dt,dy=1756.2*s,98.4*s;mt,my=dt/rt,dy/ry;bk=(401.1+203.6)*s
  for pi in (.02,.05):
    M=mt+my;rows.append([k,pi,round(mt,1),round(my,1),round(M,1),round(mt/TLm*100,1),round(my/YPm*100,1),round(M/33108.4*100,1),round(M*pi,1),round(M*pi/G*100,2),round(mt*(rt-pi)+my*max(ry-pi,0),1),round(my*(pi-ry),1) if pi>ry else 0,round(bk,1),round(bk/NP*100,1),round(bk/RWA*100,2)])
h=['kappa','prim','M_TL','M_YP','M_top','TL_mev%','YP_mev%','top_mev%','prim_K_mlr','prim_GSYH%','mevduat_sahibi_kayip','YP_sahibi_kazanc','banka_marj','banka_kar%','SYR_puan']
csv.writer(open('adim4_mevduat.csv','w')).writerows([h]+rows)
for r in rows: print(r)
print('mev/GSYH',round(33108.4/G*100,1),round(TLm/G*100,1),round(YPm/G*100,1))
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
fig,a=plt.subplots(figsize=(7,4));x=[r for r in rows if r[1]==.05]
a.bar([str(r[0]) for r in x],[r[5+0]*0+r[2]/TLm*100 for r in x],label='TL mevduatın %');a.bar([str(r[0]+.0) +' ' for r in x],[r[3]/YPm*100 for r in x],label='YP mevduatın %')
a.set_xlabel('κ');a.set_ylabel('% mevduat senede');a.set_title('Adım 4: senede geçen mevduat payı');a.legend();plt.tight_layout();plt.savefig('adim4_mevduat.png',dpi=110)
