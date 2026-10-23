import csv
AN,KB,YP,KYP=19219.0,6998.3,9313.3,1285.5;T=AN-YP;KT=KB-KYP;BT=T-KT;f=1-4588.5/25339.8;r,rd=.5319,.4330;G=85299
NP=676.3*12/8;RWA=4771.2/.166;rows=[]
for kap in (.25,.5,1):
  for grp,st in (('Genel',T),('KOBİ',KT),('Büyük',BT)):
    I=kap*f*st*r
    for sc,bk,km in (('1 banka',I,0),('2 kamu',0,I),('3 paylaşım',I*(r-rd)/r,I*rd/r)):
      rows.append([kap,grp,sc,round(I,1),round(bk,1),round(km,1),round(bk/NP*100,1),round(bk/RWA*100,2),round(km/G*100,2),round(bk*1.9,1),round(km*1.9,1),round(bk*2.3,1),round(km*2.3,1)])
h=['kappa','grup','senaryo','toplam_mlrTL','banka_mlrTL','kamu_mlrTL','banka_kar%','SYR_puan_dusus','kamu_GSYH%','banka_1.9y','kamu_1.9y','banka_2.3y','kamu_2.3y']
w=csv.writer(open('tl_faiz.csv','w'));w.writerow(h);w.writerows(rows)
print(T,KT,BT)
for x in rows:
  if x[0]==.5 or x[2]=='1 banka': print(x)
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
s=[x for x in rows if x[0]==.5 and x[1]=='Genel'];fig,a=plt.subplots(figsize=(7,4))
a.bar([x[2] for x in s],[x[4] for x in s],label='banka');a.bar([x[2] for x in s],[x[5] for x in s],bottom=[x[4] for x in s],label='kamu')
a.axhline(302,ls='--',c='k',label='YP toplam (302)');a.set_ylabel('mlr TL / yıl');a.set_title('TL faiz yükü kimde (κ=0,5, Genel)');a.legend();plt.tight_layout();plt.savefig('tl_faiz.png',dpi=110)
