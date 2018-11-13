
from rotation import *
from sparsity import *
from graphcollections import *

from IPython import embed


irreds = []

#graphs4 = GraphCollection('graphs4.json')
graphs6 = GraphCollection('graphs6.json')


#ors4 = ORSCollection('ors4.json')
ors6 = ORSCollection('ors6_noninductive.json')

for row in graphs6.data:
    mg = MyGraph(dart_partitions=[dict(z) for z in row['dart_partitions']])
    #os = OrientedRotationSystem.inductive_from_mygraph(mg,graphs4,ors4)
    os = OrientedRotationSystem.from_mygraph(mg)
    print("%s maps found for graph id=%s"%(len(os),row['id']))
    irreds+=os

for ir in irreds:
    ors6.insert(ir,'graphs6.json')


ors6.commit()

embed()










