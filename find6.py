
from rotation import *
from sparsity import *
from graphcollections import *

from IPython import embed


irreds = []

graphs5 = GraphCollection('graphs5.json')
graphs6 = GraphCollection('graphs6.json')


ors5 = ORSCollection('ors5_noninductive.json')
ors6 = ORSCollection('newtestors6.json')

for row in graphs6.data:
    mg = MyGraph(dart_partitions=[dict(z) for z in row['dart_partitions']])
    os = OrientedRotationSystem.inductive_from_mygraph(mg,graphs5,ors5)
    print("%s maps found for graph id=%s"%(len(os),row['id']))
    irreds+=os

for ir in irreds:
    ors6.insert(ir,'graphs6.json')

embed()










