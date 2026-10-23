import pandas as pd,numpy as np
B='/workspace/gec_odeme_kredi/p0923/'
G=pd.read_csv(B+'GELTAB.csv',sep=';',decimal=',',encoding='utf-8-sig',low_memory=False)
BL=pd.read_csv(B+'BILANCO.csv',sep=';',decimal=',',encoding='utf-8-sig',low_memory=False)
def ex(d):
    n=d['NACE Kodu'].astype(str).str.zfill(2).str[:2]
    return d[(d['Ölçek']!='GENEL')&~n.isin(['41','42','43','68'])&d['Yıl'].between(2014,2023)].copy()
G=ex(G);BL=ex(BL)
for d in (G,BL): d['g']=np.where(d['Ölçek']=='BUYUK','BUYUK','KOBI')
G['nk']=G['    7-Kambiyo Karları']-G['    4-Kambiyo Zararları (-)'].abs()
BL['mb']=BL['. A. Mali Borçlar (kv)']+BL['. A. Mali Borçlar (uv)']
BL['hz']=BL['. A. Hazır Değerler (dov)']
def share(d,c):
    p=d.groupby(['Yıl','g'])[c].sum().unstack(); return p.div(p.sum(axis=1),axis=0)
nk=G.groupby(['Yıl','g'])['nk'].sum().unstack()
s_k2=nk.clip(upper=0).sum()/nk.clip(upper=0).sum().sum()  # kümülatif net kambiyo zararı payı
s_k1=share(BL,'mb').mean(); s_k3=share(BL,'hz').loc[2021:2023].mean(); s_ak=share(BL,'AKTİF TOPLAMI').mean()
keys=pd.DataFrame({'k2_kur(netkambiyo)':s_k2,'k1_TL(malıborc)':s_k1,'k3_KKM(hazırdeğer)':s_k3,'aktif':s_ak}).T
print(keys.round(3)); keys.to_csv('firma_anahtar.csv')
T=pd.read_csv('../eksik/tablo_aktor_kanal_tam.csv'); C=T[T.donem=='2014-25'].set_index('aktor')
H=pd.read_csv('../hane3/hane3_kanal_grup.csv');H=H[H.set=='ANA'].set_index('kanal')
ch=['k1_TL','k2_kur','k3_KKM','k5_senyoraj','k7_bankaaltin','k8_swap']
rows={}
for g in ['alt','orta','ust']: rows['Hane_'+g]={c:(H.loc[c,g] if c in H.index else 0) for c in ch}
F=C.loc['F']
for g in ['KOBI','BUYUK']:
    rows['Firma_'+g]={'k1_TL':F.k1_TL*s_k1[g],'k2_kur':F.k2_kur*s_k2[g],'k3_KKM':F.k3_KKM*s_k3[g],'k5_senyoraj':0,'k7_bankaaltin':0,'k8_swap':0}
for a,n in [('B','Banka'),('K','Hazine'),('TCMB','TCMB'),('D','Yurtdisi+artik')]:
    r=C.loc[a]; rows[n]={'k1_TL':r.k1_TL,'k2_kur':r.k2_kur,'k3_KKM':r.k3_KKM,'k5_senyoraj':r.k5_senyoraj,'k7_bankaaltin':r.k7_bankaaltin,'k8_swap':r.k8_swap}
S=pd.DataFrame(rows).T[ch]; S['S1']=S.sum(axis=1)
# S2
S2=S[ch].copy(); S2['k1_TL']=0; S2['k3_KKM']=0
# TCMB yıllık S2 -> negatif yıllar Hazine'ye
Y=pd.read_csv('../aktor_kanal_yil.csv',index_col=0); E=pd.read_csv('../eksik/yeni_kanallar_yil.csv',index_col=0)
tc=(Y['k2_TCMB'].fillna(0)+E['k5_TCMB'].fillna(0)+E['k8_TCMB'].fillna(0)).loc[2014:2025]
recap=-tc.clip(upper=0).sum()
tc1=(tc+E['k3_TCMB'].fillna(0).loc[2014:2025]); tcmb_neg_S1=tc1.clip(upper=0).sum()
print('TCMB S2 yıllık',tc.round(2).to_dict(),'recap',round(recap,3),'S1 negatif yıllar',round(tcmb_neg_S1,3))
S2['TCMB_sermaye']=0.0; S2.loc['TCMB','TCMB_sermaye']=recap; S2.loc['Hazine','TCMB_sermaye']=-recap
S['S2']=S2.sum(axis=1); S['S1_eksi_S2(ertelemenin_getirisi)']=S.S1-S.S2
S.loc['TOPLAM']=S.sum()
akt={'Firma_KOBI':s_ak['KOBI'],'Firma_BUYUK':s_ak['BUYUK']}
for k,v in akt.items(): S.loc[k,'S1_aktif_payi_basina']=S.loc[k,'S1']/v
print(S.round(2).to_string()); S.round(3).to_csv('tablo_paylas.csv')
# Bütçe satırları
b=pd.read_csv('/workspace/zt/butce_ham.csv'); b['yil']=b.Donem.str[:4].astype(int)
gdp=pd.read_csv('/workspace/gec_odeme_efektif_talep/mevduat_tikaniklik/dogrulama/r/aylik_veri.csv');gdp=gdp[gdp.ay.str.endswith('12')];gdp.index=gdp.ay.str[:4].astype(int);gdp=gdp.gsyh_4q
def ser(code):
    x=b[b.Seri==code].groupby('yil').Deger.sum(); return x
fz=ser('TP.KB.GID152'); 
nm=b[b.Seri=='TP.KB.GID152'].groupby('yil').Donem.nunique()
print('ay sayısı',nm.loc[2014:2026].to_dict()); print('gdp örnek',gdp.loc[2014:2025].round(0).to_dict())
fzg=(fz/1e3/(gdp)*100).loc[2014:2025]
print('faiz/gsyh',fzg.round(2).to_dict())
fzg.to_csv('faiz_gsyh_ham.csv')
