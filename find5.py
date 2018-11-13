
from rotation import *
from sparsity import *
from graphcollections import *

from IPython import embed


irreds = []

graphs4 = GraphCollection('graphs4.json')
graphs5 = GraphCollection('graphs5.json')


ors4 = ORSCollection('ors4.json')
ors5 = ORSCollection('ors5.json')

for row in graphs5.data:
    mg = MyGraph(dart_partitions=[dict(z) for z in row['dart_partitions']])
    os = OrientedRotationSystem.inductive_from_mygraph(mg,graphs4,ors4)
    print("%s maps found for graph id=%s"%(len(os),row['id']))
    irreds+=os

for ir in irreds:
    ors5.insert(ir,'graphs5.json')

embed()










