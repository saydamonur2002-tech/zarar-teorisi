import csv
AN_YP,K_YP=9313.3,1285.5;B_YP=AN_YP-K_YP;f=1-4588.5/25339.8;r,rd=.0792,.0258;fx=49.797;G=85299
EQ,NP,CAR=4771.2,676.3*12/8,.166;RWA=EQ/CAR;EXT=134.72*fx;rows=[]
for kap in (.25,.5,1):
  for grp,st in (('Genel',AN_YP),('KOBİ',K_YP),('Büyük',B_YP)):
    I=kap*f*st*r
    for sc,bk,km in (('1 banka',I,0),('2 kamu',0,I),('3 paylaşım',I*(r-rd)/r,I*rd/r)):
      ext=EXT*r if grp in('Genel','Büyük') else 0
      rows.append([kap,grp,sc,round(bk,1),round(km,1),round(ext,1),round(bk/NP*100,1),round(bk/RWA*100,2),round(km/G*100,2),round(bk*1.9,1),round(km*1.9,1),round(bk*2.3,1),round(km*2.3,1),round(I/fx,2)])
h=['kappa','grup','senaryo','banka_mlrTL','kamu_mlrTL','firma_yurtdisi_mlrTL','banka_kar%','SYR_puan_dusus','kamu_GSYH%','banka_1.9y','kamu_1.9y','banka_2.3y','kamu_2.3y','toplam_mlr$']
w=csv.writer(open('yp_faiz.csv','w'));w.writerow(h);w.writerows(rows)
for x in rows:
  if x[0]==.5 and x[1]=='Genel': print(x)
print('ext',round(EXT*r,1),round(EXT*r/fx,2),round(EXT*r/G*100,2))
for k in (.25,1): print(k,[x[3] for x in rows if x[0]==k and x[1]=='Genel' and x[2]=='1 banka'])
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
s=[x for x in rows if x[0]==.5 and x[1]=='Genel'];fig,a=plt.subplots(figsize=(7,4))
lab=[x[2] for x in s];import numpy as np;b=np.array([x[3] for x in s]);k=np.array([x[4] for x in s]);e=np.array([x[5] for x in s])
a.bar(lab,b,label='banka');a.bar(lab,k,bottom=b,label='kamu');a.bar(lab,e,bottom=b+k,label='firma (yurt dışı kredi, durmaz)')
a.set_ylabel('mlr TL / yıl');a.set_title('YP faiz yükü kimde (κ=0,5, Genel)');a.legend();plt.tight_layout();plt.savefig('yp_faiz.png',dpi=110)
