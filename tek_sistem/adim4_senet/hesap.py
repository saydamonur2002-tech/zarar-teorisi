import sys;sys.path.insert(0,'../bes_adim_birlikte')
import importlib.util as u
s=u.spec_from_file_location('h','../bes_adim_birlikte/hesap.py');
import os;cwd=os.getcwd();os.chdir('../bes_adim_birlikte');h=u.module_from_spec(s);s.loader.exec_module(h);os.chdir(cwd)
st=6639+8322+4400;o=[f'stok {st} mlr TL']
for k in (.02,.05,.10):
  for p in (.5,1,2): o.append(f'kaydırma %{k*100:.0f} = {st*k:.0f} mlr; prim %{p} → yıllık {st*k*p/100:.1f} mlr TL')
for r in (.59,.55,.45): o.append(f'ρ_son {r}: 2031 enf {h.yol(r)[2031]:.1f}')
open('cikti.txt','w').write('\n'.join(o));print('\n'.join(o))
