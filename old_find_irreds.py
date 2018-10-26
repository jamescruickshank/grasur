from rotation import OrientedRotationSystem, is_irreducible
#from sparsity import MyDigraph
import time

from IPython import embed

now = time.time()
l = OrientedRotationSystem.from_digraph_data('data/fourvertex.json',max_f_vector=(0,0,0,2),max_genus=1,min_genus=1)
out = []
for k in l:
    for r in l[k]:
        if is_irreducible(r):
            out.append(r)

print(time.time()-now)

embed()
try:
    OrientedRotationSystem.dump(out,'irredsout.json')
except:
    embed()
