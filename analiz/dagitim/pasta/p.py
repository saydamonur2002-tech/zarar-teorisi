import json,numpy as np,pandas as pd
from scipy.optimize import nnls
def L(f):
    r=json.load(open(f+'.json'))[1]
    return pd.DataFrame([(x['countryiso3code'],x['indicator']['id'],int(x['date']),x['value']) for x in r],columns=['c','i','y','v'])
pc=L('gdppc').pivot(index='y',columns='c',values='v'); g=L('gdp').pivot(index='y',columns='c',values='v')
inv=L('gfcf').pivot(index='y',columns='c',values='v'); gi=L('gini').pivot(index='y',columns='i',values='v')
pc.to_csv('wb_gdppc.csv');inv.to_csv('wb_gfcf.csv');gi.to_csv('wb_tur_dagilim.csv')
C=[c for c in pc.columns]; peers=[c for c in C if c!='TUR']
lg=np.log(pc)
def synth(t,donors):
    pre=lg.loc[2004:2013]; X=(pre[donors]-pre[donors].loc[2013]).values; Y=(pre[t]-pre[t].loc[2013]).values
    # also match investment level
    Xi=inv.loc[2004:2013,donors].mean().values/100; Yi=inv.loc[2004:2013,t].mean()/100
    A=np.vstack([X,Xi,np.ones(len(donors))*10]); b=np.r_[Y,Yi,10]
    w,_=nnls(A,b); w=w/w.sum()
    post=lg.loc[2013:2025]; gap=(post[t]-post[t].loc[2013])-((post[donors]-post[donors].loc[2013])@w)
    pre_rmse=np.sqrt(np.mean((Y-X@w)**2)); return w,gap,pre_rmse
out=[];W={}
for t in C:
    d=[c for c in C if c not in(t,) and c!='TUR'] if t!='TUR' else peers
    w,gap,r=synth(t,d); out.append((t,gap.loc[2025]*100,r*100,gap.loc[2025]/max(r,1e-6))); 
    if t=='TUR': W=dict(zip(d,w.round(3))); gapT=gap
res=pd.DataFrame(out,columns=['ulke','fark2025_logpuan','pre_rmse','oran']).set_index('ulke');res.to_csv('sentetik_placebo.csv')
print(res.round(2)); print('TUR agirlik',{k:v for k,v in W.items() if v>0})
print('TUR yol',(gapT*100).round(1).to_dict())
gr=lambda a,b:(pc.loc[b]/pc.loc[a])**(1/(b-a))*100-100
print('kb buyume 04-13',gr(2003,2013).round(2).to_dict());print('14-25',gr(2013,2025).round(2).to_dict())
gg=(g.loc[2025]/g.loc[2013])**(1/12)*100-100;print('GSYH 14-25',gg.round(2).to_dict())
# trend own
b=np.polyfit(range(2004,2014),lg.loc[2004:2013,'TUR'],1); tr=np.polyval(b,2025); print('kendi trend fark 2025 logp',(lg.loc[2025,'TUR']-tr)*100)
ia=inv.loc[2014:2025].mean(); ib=inv.loc[2004:2013].mean(); print('GSCF ort 04-13',ib.round(1).to_dict());print('14-25',ia.round(1).to_dict())
pe=ia[peers].mean(); pb=ib[peers].mean(); print('emsal',pb,pe,'TUR',ib.TUR,ia.TUR,'DiD',(ia.TUR-ib.TUR)-(pe-pb))
print('TUR gfcf yil',inv.loc[2013:2025,'TUR'].round(1).to_dict())
# ICOR
gT=g['TUR'].pct_change()*100; icor=(inv.loc[2014:2025,'TUR']/gT.loc[2014:2025]); print('ICOR 14-25 (ort I / ort g)',inv.loc[2014:2025,'TUR'].mean()/gT.loc[2014:2025].mean(), 'g ort',gT.loc[2014:2025].mean(),'04-13 g',gT.loc[2004:2013].mean())
print(gi.loc[2013:2024].round(1))
