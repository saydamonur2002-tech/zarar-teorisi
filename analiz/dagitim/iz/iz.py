import json,csv
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
L=open('../eksik/ham/bop.txt').read().split('\n')
def row(n):
    t=L[n-1].split()[-20:]; return {2006+i:float(x.replace('.',''))/1000 for i,x in enumerate(t)}  # mlr$
DI,PF,INT,BNK,OTH,ST,CRD=row(655),row(658),row(661),row(665),row(666),row(667),row(653+0)
def wb(i):
    d=json.load(open(f'ham/{i}.json'))[1]; return {int(r['date']):r['value'] for r in d if r['value'] is not None}
gdp=wb('NY.GDP.MKTP.CD'); pm=wb('BM.GSR.FCTY.CD'); px=wb('BX.GSR.FCTY.CD')
tx=wb('GC.TAX.YPKG.RV.ZS'); rv=wb('GC.REV.XGRT.GD.ZS')
tax={y:tx[y]*rv[y]/100 for y in tx if y in rv}; tax[2025]=tax[2024]  # VARSAYIM
ws={int(r['']):float(r['gap']) for r in csv.DictReader(open('../borc/yil_borc.csv'))}
Y=range(2015,2026)
g=lambda s,y: s[y]/(gdp[y]/1e9)*100
ser={'DY_odeme':lambda y:g(DI,y),'portfoy_odeme':lambda y:g(PF,y),
 'faiz_yd_firma(diger sektor UV+KV)':lambda y:g(OTH,y)+g(ST,y),'faiz_yd_banka_UV':lambda y:g(BNK,y),
 'net_birincil_gelir_cikisi':lambda y:(pm[y]-px[y])/gdp[y]*100,'gelir_kurumlar_vergisi':lambda y:tax[y]}
out=[];cum={}
for k,f in ser.items():
    b=f(2014); ex=[f(y)-b for y in Y]; cum[k]=(sum(ex),sum(f(y) for y in Y),b,f(2025))
    for y,e in zip(Y,ex): out.append([k,y,round(f(y),3),round(e,3)])
with open('seriler_iz.csv','w') as fh:
    w=csv.writer(fh); w.writerow(['seri','yil','pct_gsyh','2014e_gore_fark']); w.writerows(out)
ucret=-sum(ws[y] for y in Y)
for k,v in cum.items(): print(f'{k:40s} kum_fark={v[0]:6.2f} kum_duzey={v[1]:6.2f} 2014={v[2]:.2f} 2025={v[3]:.2f}')
print('ucret kazanci',round(ucret,2))
yd=cum['DY_odeme'][0]+cum['portfoy_odeme'][0]+cum['faiz_yd_firma(diger sektor UV+KV)'][0]
print('K1 yd sizinti (DY+portfoy+firma faiz) kum fark',round(yd,2),' K2 oran net birincil/3.85',round(cum['net_birincil_gelir_cikisi'][0]/3.85,2), 'yd/3.85',round(yd/3.85,2))
# emekli
old={}
for r in csv.DictReader(open('ham/old.csv')):
    if r['Unit of measure']=='Percentage of GDP': old[int(r['TIME_PERIOD'])]=float(r['OBS_VALUE'])
pl=sum(old[2014]-old[y] for y in range(2015,2022)); print('emekli kum kayip 2015-21',round(pl,2), {y:old[y] for y in range(2014,2022)})
gcn=json.load(open('../pasta/gdpcn.json'))[1]; g24=[r['value'] for r in gcn if r['date']=='2024'][0]
print('SGK 2024 odeme/GSYH [IKINCIL]',round(2.739292e12/g24*100,2))
m={};inf={}
for r in csv.DictReader(open('ham/min2ave.csv')): m.setdefault(r['AGGREGATION_OPERATION'],{})[int(r['TIME_PERIOD'])]=float(r['OBS_VALUE'])
seen=set()
for r in csv.DictReader(open('ham/nifl.csv')):
    y=int(r['TIME_PERIOD'])
    if r['SEX']=='SEX_T': inf[y]=float(r['OBS_VALUE'])
print('min/ort',{y:round(m['MEAN'][y],1) for y in (2004,2013,2014,2019,2021,2022,2023,2024,2025)})
print('min/medyan',{y:round(m['MEDIAN'][y],1) for y in (2014,2021,2022,2025)})
print('kayitdisi',{y:inf[y] for y in (2014,2019,2022,2025)})
json.dump({'cum':cum,'ucret':ucret,'yd':yd,'pl':pl},open('ozet.json','w'),indent=1)
fig,ax=plt.subplots(1,3,figsize=(16,4.8))
ax[0].plot(list(Y),[-ws[y] for y in Y],'k-o',label='firma ücret kazancı (ücret payı düşüşü)')
for k in ['DY_odeme','portfoy_odeme','faiz_yd_firma(diger sektor UV+KV)','gelir_kurumlar_vergisi']:
    ax[0].plot(list(Y),[x[3] for x in out if x[0]==k],label=k+' (2014 farkı)')
ax[0].axhline(0,c='gray',lw=.5);ax[0].set_title('+10 puan nereye? (%GSYH, 2014e göre fark)');ax[0].legend(fontsize=7)
ax[1].plot(sorted(old),[old[y] for y in sorted(old)],'o-');ax[1].set_title('Yaşlılık+dul/yetim nakit harcaması %GSYH (OECD SOCX)')
ax[2].plot(sorted(m['MEAN']),[m['MEAN'][y] for y in sorted(m['MEAN'])],label='asgari/ortalama (OECD)')
ax[2].plot(sorted(m['MEDIAN']),[m['MEDIAN'][y] for y in sorted(m['MEDIAN'])],label='asgari/medyan (OECD)')
ax[2].plot(sorted(inf),[inf[y] for y in sorted(inf)],label='kayıt dışı istihdam % (ILO)');ax[2].legend(fontsize=8);ax[2].set_title('Asgari ücret ve kayıt dışılık')
plt.tight_layout();plt.savefig('iz.png',dpi=110)
