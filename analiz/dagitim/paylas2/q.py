import pandas as pd,numpy as np
D='/workspace/grafik5/dagitim/'
S1t=pd.read_csv(D+'paylas/tablo_paylas.csv',index_col=0).drop('TOPLAM')
ch=['k1_TL','k2_kur','k3_KKM','k5_senyoraj','k7_bankaaltin','k8_swap']
Y=pd.read_csv(D+'aktor_kanal_yil.csv',index_col=0).loc[2014:2025];E=pd.read_csv(D+'eksik/yeni_kanallar_yil.csv',index_col=0).loc[2014:2025]
q=pd.read_csv('/workspace/grafik5/kalibre_faiz/ceyrek_veri.csv',index_col=0);q['yr']=q.index.str[:4].astype(int)
q['dl']=np.log(q.E).diff()
yr=q.groupby('yr').agg(dl=('dl','sum'),xp=('x',lambda s:s.clip(lower=0).sum()),xn=('x','sum'),pi=('pi','last'))
yr['rd']=yr.dl-np.log1p(yr.pi)
psi=3.4
ext={'dusuk(simetrik,k=1)':(yr.xn*psi/4).clip(lower=None),'orta(asimetrik,k=.5)':.5*psi*yr.xp/4,'yuksek(asimetrik,k=1)':psi*yr.xp/4}
beta={'dusuk(simetrik,k=1)':.2,'orta(asimetrik,k=.5)':.3,'yuksek(asimetrik,k=1)':.45}
yrs=list(range(2017,2026)); rd=yr.rd.loc[yrs]
par={'H':'k2_H','F':'k2_F','K':'k2_K','TCMB':'k2_TCMB','D':'k2_D'}
p={a:Y[c].loc[yrs].sum()/rd.sum() for a,c in par.items()}  # pozisyon / birim reel deg. kaybi
print('rd',rd.round(3).to_dict());print('p',{k:round(v,2) for k,v in p.items()})
# alt grup paylari (S1 k2 icindeki pay)
def sub(a):
    if a=='H': return {g:S1t.loc[g,'k2_kur']/S1t.loc[['Hane_alt','Hane_orta','Hane_ust'],'k2_kur'].sum() for g in ['Hane_alt','Hane_orta','Hane_ust']}
    if a=='F': return {g:S1t.loc[g,'k2_kur']/S1t.loc[['Firma_KOBI','Firma_BUYUK'],'k2_kur'].sum() for g in ['Firma_KOBI','Firma_BUYUK']}
    return {{'K':'Hazine','TCMB':'TCMB','D':'Yurtdisi+artik'}[a]:1.0}
# D2 TCMB->Hazine (milyar TL, TCMB yasal finansal tablolar, ozkaynak degisim tablosu)
gdp=pd.read_csv('/workspace/gec_odeme_efektif_talep/mevduat_tikaniklik/dogrulama/r/aylik_veri.csv');gdp=gdp[gdp.ay.str.endswith('12')];gdp.index=gdp.ay.str[:4].astype(int);gdp=gdp.gsyh_4q
tr=pd.Series({2019:37.518596+40.769702,2020:39.109540+5.349978,2021:30.207403+5.576195})
trg=(tr*1e3/gdp.loc[tr.index]*100); print('transfer %GSYH',trg.round(2).to_dict(),'gdp',gdp.loc[2019:2021].round(0).to_dict())
# D3 banka YP net genel pozisyon/ozkaynak [IKINCIL dergipark], ozkaynak/GSYH VARSAYIM
rB=pd.Series({2020:.001,2021:.059,2022:.061})
eq={'dusuk(simetrik,k=1)':.07,'orta(asimetrik,k=.5)':.085,'yuksek(asimetrik,k=1)':.10}
tc_y=(Y['k2_TCMB'].fillna(0)+E['k5_TCMB'].fillna(0)+E['k8_TCMB'].fillna(0))
out={};S1=None
for lv in ext:
    ex=ext[lv].reindex(range(2014,2026)).fillna(0)
    bank=(rB*eq[lv]*rd.reindex(rB.index)*100)  # %GSYH
    for sc in ['S1','S2']:
        T=S1t[ch].copy()
        if sc=='S2':
            T['k1_TL']=0;T['k3_KKM']=0
            for a,sh in [(a,sub(a)) for a in par]:
                for g,s in sh.items(): T.loc[g,'k2_kur']+=p[a]*ex.sum()*s
            # enflasyon gecisi -> senyoraj
            infl=(beta[lv]*ex/np.log1p(yr.pi).reindex(ex.index)).fillna(0)
            for g in T.index: T.loc[g,'k5_senyoraj']=S1t.loc[g,'k5_senyoraj']*(1+ (E['k5_TCMB']*infl).sum()/E['k5_TCMB'].sum())
        T['D3_banka_kur']=0.0;T.loc['Banka','D3_banka_kur']=bank.sum();T.loc['Yurtdisi+artik','D3_banka_kur']=-bank.sum()
        T['D2_TCMB_Hazine']=0.0;T.loc['TCMB','D2_TCMB_Hazine']=-trg.sum();T.loc['Hazine','D2_TCMB_Hazine']=trg.sum()
        # TCMB yillik -> negatif yillar Hazine sermaye
        tcy=tc_y.copy()
        if sc=='S2': tcy=tcy+p['TCMB']*ex
        else: tcy=tcy+E['k3_TCMB'].fillna(0)
        tcy=tcy.sub(trg,fill_value=0)
        cap=-tcy.clip(upper=0).sum() if sc=='S2' else 0.0
        T['TCMB_sermaye']=0.0;T.loc['TCMB','TCMB_sermaye']=cap;T.loc['Hazine','TCMB_sermaye']=-cap
        T[sc]=T.drop(columns=[c for c in T if c in('S1','S2')]).sum(axis=1)
        out[(lv,sc)]=T
        if sc=='S1': tcmb_neg_S1=-tcy.clip(upper=0).sum()
    out[(lv,'cap')]=cap; out[(lv,'negS1')]=tcmb_neg_S1; out[(lv,'ext')]=ex.sum()
rows=[]
for lv in ext:
    a=out[(lv,'S1')];b=out[(lv,'S2')]
    for g in a.index: rows.append({'duzey':lv,'aktor':g,'S1':a.loc[g,'S1'],'S2':b.loc[g,'S2'],'S1_eksi_S2':a.loc[g,'S1']-b.loc[g,'S2']})
R=pd.DataFrame(rows);R.round(3).to_csv('tablo_paylas2.csv',index=False)
W=R.pivot(index='aktor',columns='duzey',values='S1_eksi_S2');print(R.pivot(index='aktor',columns='duzey',values='S2').round(2).to_string());print(R.pivot(index='aktor',columns='duzey',values='S1').round(2).to_string());print(W.round(2).to_string())
for lv in ext:
    o=out[(lv,'S1')]; hidden=-(o.loc['Hazine','k3_KKM'])+out[(lv,'negS1')]-o.loc[['Hane_alt','Hane_orta','Hane_ust'],'k1_TL'].sum()
    print(lv,'ek kur(log)',round(out[(lv,'ext')],3),'S2 gorunur sermaye',round(out[(lv,'cap')],2),'S1 gizli',round(hidden,2),'TCMB neg yil S1',round(out[(lv,'negS1')],2))
    W.loc['_gizli',lv]=hidden;W.loc['_gorunur',lv]=out[(lv,'cap')];W.loc['_ekkur',lv]=out[(lv,'ext')]
W.round(3).to_csv('ozet_S1eksiS2.csv')
# UYP
print('D UYP dogrudan',E['D_UYP_dogrudan'].sum().round(3))
