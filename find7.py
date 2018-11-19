
from rotation import *
from sparsity import *
from graphcollections import *

from IPython import embed
import os

fns = os.listdir('seven/')

#with open('seven/filenames.txt') as fns:
filenames = [x.strip('\n') for x in fns if x.startswith('set') and x.endswith('3.json')]

stop = True
embed()
if stop:
    raise ValueError


run = True


for f in filenames:

    irreds = []
    graphs_fp = "seven/%s"%f

    graphs6 = GraphCollection('six/graphs6.json')
    graphs7 = GraphCollection(graphs_fp)


    print("source graphs in %s"%f)
    ors6 = ORSCollection('six/ors6.json')
    ors7 = ORSCollection('seven/ors_%s'%f)

    for row in graphs7.data:
        mg = MyGraph(dart_partitions=[dict(z) for z in row['dart_partitions']])
        os = OrientedRotationSystem.inductive_from_mygraph(mg,graphs6,ors6)
        print("%s maps found for graph id=%s"%(len(os),row['id']))
        irreds+=os

    for ir in irreds:
        ors7.insert(ir,graphs_fp)

    ors7.commit()

    if run == False:
        print( "set run to True to process all files")
        embed()










