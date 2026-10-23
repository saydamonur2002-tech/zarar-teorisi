import sys,copy;sys.path.insert(0,'.');import numpy as np,sfc_model as M
def sc():
    d=M.all_scenarios(); d.update(M.ts_scenarios()); return d
rows=[]
for flag in (False,True):
    M.BASE["no_floor"]=flag
    for k,p in sc().items():
        p=copy.deepcopy(p); p["no_floor"]=flag
        o=M.simulate(p); pi=np.array(o["pi"])*100; y=M.real_gdp(o); c=o["_checks"]
        bal=c["balance"]; bal=max(abs(v) for v in bal.values()) if isinstance(bal,dict) else bal
        geri=pi[10:].max()-pi[9]
        rows.append((flag,k,pi[-1],y[-1]/y[0]*100,min(o["NR"]),int(np.argmin(o["NR"])),o["debt"][-1]*100,o["E"][-1],geri,min(o["R_usd"]) if "R_usd" in o else float('nan'),c["hidden_max"],c["SI_max"],bal))
print("esik|senaryo|pi29Q4|GSYH|NRmin|tmin|borc%|USDTL|2029geri|Rmin|gizli|SI|bil")
for r in rows: print("%s|%s|%.1f|%.1f|%.1f|%d|%.1f|%.1f|%.1f|%s|%.1e|%.1e|%s"%(("yok" if r[0] else "var"),*r[1:9],r[9] if not isinstance(r[9],float) else "%.1f"%r[9],r[10],r[11],r[12]))
