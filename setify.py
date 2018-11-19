
from sparsity import MyGraph
from graphcollections import GraphCollection


raw7 = GraphCollection('raw7.json')

fvs = { tuple(x['degree_sequence']) for x in raw7.data}

for fv in fvs:
    fp = "split/"+"_".join([str(i) for i in fv])+".json"
    gc = GraphCollection(fp)
    gs = [MyGraph(dart_partitions=[dict(z) for z in x['dart_partitions']]) for x in gc.data]
    print("setifying list of %s graphs"%str(len(gs)))
    sfp = "split/set"+"_".join([str(i) for i in fv])+".json"
    sgc = GraphCollection(sfp)
    sgs = MyGraph.isomorphism_class_reps(gs,verbose=True)
    for g in sgs:
        sgc.insert(g)
    sgc.commit()

    



