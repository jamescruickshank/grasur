
from rotation import *
from sparsity import *
from graphcollections import *

from IPython import embed


irreds = []

graphs4 = GraphCollection('graphs4.json')


ors4 = ORSCollection('testors4.json')

for row in graphs4.data:
    mg = MyGraph(dart_partitions=[dict(z) for z in row['dart_partitions']])
    os = OrientedRotationSystem.from_mygraph(mg)
    print("%s maps found for graph id=%s"%(len(os),row['id']))
    irreds+=os

for ir in irreds:
    ors4.insert(ir,'graphs4.json')

embed()








graphs4 = GraphCollection('graphs4.json')


