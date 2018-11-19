
from sparsity import MyGraph
from graphcollections import GraphCollection

import json


raw7 = GraphCollection('raw7.json')

fvs_list = [ tuple(x['degree_sequence']) for x in raw7.data]

fvs_set = set(fvs_list)

for y in fvs_set:
    x = list(y)
    l = raw7.select(degree_sequence=x)
    fn = "split/"+"_".join([str(i) for i in x])+".json"
    print("writing %s graphs to %s"%(str(len(l)),fn))
    with open(fn,'w+') as jsonfile:
        json.dump(l,jsonfile)




