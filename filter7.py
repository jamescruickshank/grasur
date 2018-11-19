
from sparsity import MyGraph
from graphcollections import GraphCollection
from IPython import embed

raw7 = GraphCollection('raw7.json')

a = [MyGraph(dart_partitions=[dict(z) for z in x['dart_partitions']]) for x in raw7.data]

embed()

out = MyGraph.isomorphism_class_reps(a,verbose=True)


graphs7 = GraphCollection('graphs7.json')

for g in out:
    graphs7.insert(g)

graphs7.commit()

embed()




