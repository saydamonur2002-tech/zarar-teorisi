import csv,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
G=111207;K=59.26
S={'düşük':(27.93,35,1.0),'orta':(31.5,35.5,1.125),'yüksek':(35,36,1.25)}
rows=[]
for k,(r,r26,g) in S.items():
  q4=231*r26/38.75; s26=2187+q4; z27=923*r/38.75*g
  ert=s26+z27; fi=s26*r/100; don=s26+fi; fark=ert-don
  for ad,v in [('Erteleme: 2027 sonu stok',ert),('  içinden 2027 zararı',z27),('Dondurma: tanınan stok',s26),('  2027 DİBS faizi',fi),('Dondurma toplam',don),('Fark (ertelemenin ek yükü)',fark)]:
    rows.append([ad,k,round(v),round(v/K,1),round(v/G*100,2)])
csv.writer(open('tablo.csv','w')).writerows([['kalem','senaryo','mlr TL','mlr $','GSYH %']]+rows)
for r in rows:print(r)
fig,ax=plt.subplots(figsize=(7,4));import numpy as np;x=np.arange(3)
e=[r[4] for r in rows if r[0].startswith('Erteleme')];d=[r[4] for r in rows if r[0]=='Dondurma toplam']
ax.bar(x-.2,e,.4,label='Erteleme (2027 sonu stok)');ax.bar(x+.2,d,.4,label='Dondurma (stok+2027 faiz)')
ax.set_xticks(x);ax.set_xticklabels(S);ax.set_ylabel('GSYH %');ax.legend();ax.set_title('2027 sonu maliyet [HESAP/TAHMİN]')
plt.savefig('proj2027.png',dpi=120,bbox_inches='tight')
