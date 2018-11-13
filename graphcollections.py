

from sage.all import *

import json
from sparsity import MyGraph

from IPython import embed
import sys,traceback


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
            json.dump([],initfile)
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
            'dart_partitions':[zip(graph.vertex_partition().keys(),graph.vertex_partition().values()),zip(graph.edge_partition().keys(),graph.edge_partition().values())],
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
        k = [(x['id'],MyGraph(dart_partitions=[dict(z) for z in x['dart_partitions']])) for x in l]

        out = []
        for y in k:
            isos = y[1].isomorphisms(g)
            if len(isos) >0:
                out.append( (y[0],zip(g.vertices(),isos[0])) )
        return out


class ORSCollection(Collection):
    def insert(self,ors,graph_collection_fp=None):
        if graph_collection_fp is not None:
            graph_coll = GraphCollection(graph_collection_fp)
            graphs = graph_coll.get_isomorphs(ors.mygraph())
            if len(graphs)==0:
                raise ValueError('underlying graph is not contained in given graph collection')
            if len(graphs)>1:
                raise ValueError('Graph collection contains more than one copy of underlying graph')
            self.data.append({
                'id': self.pk,
                'sigma_perm':[list(t) for t in ors.sigma_perm.cycle_tuples()],
                'tau_perm':[list(t) for t in ors.tau_perm.cycle_tuples()],
                'mygraph':[graph_collection_fp,graphs[0][0],graphs[0][1]]
                })
            self.pk+=1
        else:
            raise NotImplementedError('You must supply a GraphCollection object')

