
from sparsity import MyGraph
from graphcollections import GraphCollection


a = [MyGraph(dart_partitions=[[[]],[]])]

for i in range(6):
    print("computing graphs with %s vertices"%str(i+2))
    a = MyGraph.extensions_of(a)
    fp = "mygraphs%s.json"%str(i+2)

    print("storing to %s"%fp)
    coll = GraphCollection(fp)
    for g in a:
        coll.insert(g)
    coll.commit()
