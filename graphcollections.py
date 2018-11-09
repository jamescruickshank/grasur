

from sage.all import *

import json
from sparsity import MyGraph



class MyEncoder(json.JSONEncoder):
    def default(self,o):
        if isinstance(o,Integer):
            return int(o)
        else:
            return json.JSONEncoder.default(self,o)


class Collection(object):
    def __init__(self,fp):
        self.fp = fp
        try:
            datafile = open(fp)
        except IOError:
            initfile = open(fp,'w')
            json.dump(["a"],initfile)
            initfile.close()
            datafile=open(fp)
        self.data = json.load(datafile)
        datafile.close()
        self.pk = max([x['id'] for x in self.data]+[0])+1

    def insert(self):
        """override this in subclasses."""
        pass

    def commit(self):
        with open(self.fp,'w') as jsonfile:
            json.dump(self.data,jsonfile,cls=MyEncoder)

    def select(self,**kwargs):
        return [x for x in self.data if all([x[k] == kwargs[k] for k in kwargs])]




class GraphCollection(Collection):


    def insert(self,graph):
        self.data.append({
            'id':self.pk,
            'dart_partitions':[graph.vertex_partition(),graph.edge_partition()],
            'v':len(graph.vertices()),
            'degree_sequence':graph.degree_sequence()
            })
        self.pk+=1

    def get_isomorphs(self,g):
        """g should be an instance of MyGraph. Returns a list of 
        tuples (id,mapping) where mapping is a dict mapping vertices of 
        g to vertices of row id"""

        deg_seq = g.degree_sequence()
        l = self.select(degree_sequence=deg_seq)
        k = [(x['id'],MyGraph(dart_partitions=x['dart_partitions'])) for x in l]

        out = []
        for y in k:
            isos = y[1].isomorphisms(g)
            if len(isos) >0:
                out.append( (y[0],dict(zip(g.vertices(),isos[0]))) )
        return out


class ORSCollection(object):
    def insert(self,ors,graph_collection_fp=None):
        if graph_collection_fp is not None:
            graph_coll = GraphCollection(graph_collection_fp)
            
        pass
