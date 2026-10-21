import itertools as it
ic_tl,tic,kr,ka,st=7748.0,11260.7,28636.8,.743,19361;fak=.93
o=[]
def banka_npl(b,dp): return -b*(-dp)*kr*ka/100*(-1)  # kazanç: NPL düşüşü×kredi×karşılık
rows=[]
for b,dp,r,P in it.product((-.068,.119),(1.2,3.5),(0,.2,.5),(1.9,9.7,38.7)):
  dn=b*dp            # NPL düşüşü (puan); b>0 ise düşer
  bk=dn*kr*ka/100     # banka NPL geliri (eksi=kayıp)
  hz=ic_tl*r/100*fak; fr=tic*r/100
  # A
  A=(hz-.5*P, fr-.5*P, bk)
  # B
  bp=.3*bk if bk>0 else 0; Bv=(hz-.5*(P-bp), fr-.5*(P-bp), bk-bp)
  rows.append((b,dp,r,P,A,Bv,bk))
o.append('b dp r P | A: devlet firma banka | B: devlet firma banka')
for b,dp,r,P,A,Bv,bk in rows:
  o.append(f'{b:+.3f} {dp} {r} {P} | '+' '.join(f'{x:.1f}' for x in A)+' | '+' '.join(f'{x:.1f}' for x in Bv))
o.append('\nC: banka mevduat kayması fonlama maliyeti (mlr TL/yıl) kayma×s')
for k,s in it.product((.02,.05,.1),(0,1,3)): o.append(f' %{k*100:.0f} s={s}: {st*k*s/100:.1f}')
o.append('C destek ihtiyacı = max(0, −(NPL geliri) + fonlama maliyeti): b=−0,068 → dp1,2: 17 + fonlama; dp3,5: 51 + fonlama')
o.append('\nEşikler (50 pay): devlet r* = 0,5P/(ic_tl·0,93), firma r* = 0,5P/tic (toplam firma)')
for P in (1.9,9.7,38.7): o.append(f' P={P}: devlet {0.5*P/(ic_tl*fak)*100:.3f} puan, firma {0.5*P/tic*100:.3f} puan')
o.append('\nBedava binici: katılan firma neti = q·tic·r − 0,5P ; eşik r* = 0,5P/(q·tic)')
for q,P in it.product((.1,.3,.6),(1.9,9.7,38.7)):
  o.append(f' q={q} P={P}: r*={0.5*P/(q*tic)*100:.3f} puan; r=0,2 net {q*tic*.002-.5*P:.1f}; r=0,5 net {q*tic*.005-.5*P:.1f}')
open('cikti.txt','w').write('\n'.join(o));print('\n'.join(o[-40:]))
