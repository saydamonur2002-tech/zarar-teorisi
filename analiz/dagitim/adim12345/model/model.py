"""Adım 1-5 kümülatif firma modeli. Çalıştır: python3 model.py"""
import json,os,numpy as np
D=os.path.dirname(os.path.abspath(__file__))
import sys;sys.path.insert(0,D);import model12 as m12
P=json.load(open(f'{D}/params.json'))
S0,PSI,R=25339.8,0.3584,0.5319; FDEP,ADR,KP=4400.1,19361.9,0.08
MER=dict(m12.P['merkez'],kappa=0.5,theta=0.25,pi=0.035)
def run(mahsup,spread,kredi_faizi,silme,kobi_payi,kappa,theta,pi):
    o=m12.run(mahsup,spread,kredi_faizi,silme,kobi_payi);F,E=m12.g('fin_gider_2025'),m12.g('efk_2025')
    o['A1_faiz']=o['net_faiz'];o['A1_stok']=o['borc_stoku']
    o['A2_faiz']=0*o['net_faiz'];o['A2_nakit']=o['serbest_nakit'];o['A2_stok']=o['ticari_borc']
    F1=F['G']-o['A1_faiz']
    o['A3_faiz']=np.minimum(kappa*PSI*R*(S0-o['A1_stok']),F1);o['A3_stok']=0*F1
    o['A4_nakit']=theta*pi*FDEP;o['A4_stok_kredi_daralma']=KP*theta*ADR;o['A4_faiz']=0*F1
    o['A5_faiz']=0*F1;o['A5_stok']=0*F1
    cum=0
    for a in ('A1','A2','A3','A4','A5'):
        cum=cum+o[a+'_faiz']
        for k,s in (('G',1),('K',kobi_payi),('B',1-kobi_payi)):
            o[f'oran_{a}_{k}']=100*np.maximum(F[k]-cum*s,0)/E[k]
    return o
def mc():
    r=np.random.default_rng(7);N=m12.P['mc']['n']
    def tri(a,c,b):return r.triangular(a,c,b,N)
    x=dict(kappa=tri(.25,.5,1),theta=tri(.1,.25,.5),pi=r.uniform(.02,.05,N))
    # A1-2 çekilişi model12 ile aynı (seed 1)
    rr=np.random.default_rng(1);m=m12.P['mc'];from scipy.stats import norm
    z=rr.multivariate_normal([0,0],[[1,m['korelasyon_mahsup_silme']],[m['korelasyon_mahsup_silme'],1]],N);u=norm.cdf(z)
    def t2(sp,uu):
        _,a,c,b=sp;Fc=(c-a)/(b-a);return np.where(uu<Fc,a+np.sqrt(uu*(b-a)*(c-a)),b-np.sqrt((1-uu)*(b-a)*(b-c)))
    x.update(mahsup=t2(m['mahsup'],u[:,0]),silme=t2(m['silme'],u[:,1]),spread=t2(m['spread'],rr.random(N)),
      kredi_faizi=t2(m['kredi_faizi'],rr.random(N)),kobi_payi=np.clip(rr.normal(*m['kobi_payi'][1:],N),.15,.5))
    return run(**x)
if __name__=='__main__':
    import csv,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
    c=run(**MER);s=mc();fx,gd=m12.g('usd_tl'),m12.g('gsyh');N=m12.P['mc']['n']
    ks=[k for k in c if k.startswith(('A','oran_A'))]
    with open(f'{D}/sonuc.csv','w') as fh:
        w=csv.writer(fh);w.writerow(['kalem','merkez','P10','P50','P90','P50_mlrUSD','P50_GSYH%'])
        for k in ks:
            p=np.percentile(s[k]*np.ones(N),[10,50,90]);pc='oran' in k
            w.writerow([k,round(float(c[k]),1)]+[round(v,1) for v in p]+(['',''] if pc else [round(p[1]/fx,1),round(100*p[1]/gd,2)]))
    print(open(f'{D}/sonuc.csv').read())
    fig,ax=plt.subplots(1,3,figsize=(13,4.5))
    for a,k in zip(ax,'GKB'):
        y=[100*m12.g('fin_gider_2025')[k]/m12.g('efk_2025')[k]]+[np.percentile(s[f'oran_A{i}_{k}'],[10,50,90]) for i in range(1,6)]
        p50=[y[0]]+[q[1] for q in y[1:]];lo=[y[0]]+[q[0] for q in y[1:]];hi=[y[0]]+[q[2] for q in y[1:]]
        xs=range(6);a.plot(xs,p50,'o-');a.fill_between(xs,lo,hi,alpha=.3)
        a.axhline(33,c='g',ls='--',label='%33 sağlıklı');a.axhline(67,c='r',ls='--',label='%67 riskli')
        a.set_xticks(xs,['önce','A1','A2','A3','A4','A5']);a.set_title({'G':'Genel','K':'KOBİ','B':'Büyük'}[k]);a.set_ylim(0,100)
    ax[0].set_ylabel('fin.gider/EFK % (kümülatif, P10-P90)');ax[0].legend()
    plt.tight_layout();plt.savefig(f'{D}/model_mc.png',dpi=110)
