
from sparsity import MyGraph
from graphcollections import GraphCollection


graphs6 = GraphCollection('graphs6.json')

a = [MyGraph(dart_partitions=[dict(z) for z in x['dart_partitions']]) for x in graphs6.data]

b = MyGraph.extensions_of(a,no_iso_check=True)

raw7 = GraphCollection('raw7.json')

for g in b:
    raw7.insert(g)

raw7.commit()


