P=[1.9,9.7,38.7];S={'A 1/3':(1/3,1/3,1/3),'B 20-40-40':(.2,.4,.4),'C 50-25-25':(.5,.25,.25),'D devlet':(1,0,0)}
o=['senaryo | P | devlet firma banka (mlr TL/yıl, başabaş kazanç)']
for k,s in S.items():
  for p in P: o.append(f'{k} | {p} | '+' '.join(f'{x*p:.2f}' for x in s))
open('cikti.txt','w').write('\n'.join(o));print('\n'.join(o))
