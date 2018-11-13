
from sage.all import *
import time
import json

from IPython import embed

class NonUniqueLabelError(Exception):
    pass


class MyGraph(Graph):
    def __init__(self,*args,**kwargs):
        dart_partitions = kwargs.pop('dart_partitions',None)
        if dart_partitions is not None:
            super(MyGraph,self).__init__(multiedges=True,loops=True)
            v_parts,e_parts = dart_partitions
            if isinstance(v_parts,dict):
                self._vertex_partition = v_parts
            else:
                #self._vertex_partition = { min(x):list(x) for x in v_parts}
                self._vertex_partition = dict(zip(range(len(v_parts)),[list(x) for x in v_parts]))

            if isinstance(e_parts,dict):
                self._edge_partition = e_parts
            else:
                self._edge_partition = dict(zip(range(len(e_parts)),[list(x) for x in e_parts]))


            self.dart_to_edge = {}
            for e in self._edge_partition:
                for dart in self._edge_partition[e]:
                    self.dart_to_edge[dart] = e


            self.dart_to_vertex = {}
            for v in self._vertex_partition:
                for dart in self._vertex_partition[v]:
                    self.dart_to_vertex[dart] = v
            self.darts = self.dart_to_vertex.keys()

            edges = []
            for label in self._edge_partition.keys():
                try:
                    edges.append((self.dart_to_vertex[self._edge_partition[label][0]],self.dart_to_vertex[self._edge_partition[label][1]],label))
                except:
                    embed()
            kwargs.pop('data',None)
            self.add_vertices(self._vertex_partition.keys())
            self.add_edges(edges)


        else:
            dg = Graph(*args,**kwargs)
            vertex_partition = { v:[] for v in dg.vertices() }
            edge_partition = {}
            current_edge_label = max([ e[2] for e in dg.edges() if isinstance(e[2],int) ]+[-1])+1
            current_dart = 1
            for edge in dg.edges():
                if edge[2] is None:
                    edge = edge[:2]+(current_edge_label,)
                    current_edge_label +=1
                vertex_partition[edge[0]].append(current_dart)
                vertex_partition[edge[1]].append(current_dart+1)
                edge_partition[edge[2]]=[current_dart,current_dart+1]
                current_dart +=2
            self.__init__(dart_partitions=[vertex_partition,edge_partition],*args,**kwargs)


    def vertex_partition(self):
        return deepcopy(self._vertex_partition)

    def edge_partition(self):
        return deepcopy(self._edge_partition)


    def _new_vertex_labels(self,n):
        m = max([i for i in self.vertex_partition().keys() if isinstance(i,int) or isinstance(i,Integer)]+[-1])
        return range(m+1,m+n+1)

    def _new_edge_labels(self,n):
        m = max([i for i in self.edge_partition().keys() if isinstance(i,int) or isinstance(i,Integer)]+[-1])
        return range(m+1,m+n+1)

    def _new_darts(self,n):
        m = max(self.darts+[0])
        return range(m+1, m+n+1)

    def digon_split(self,vertex,dart_set,vertex_labels=None,edge_labels=None):
        # first define labels if not given
        if vertex_labels == None:
            vertex_labels = self._new_vertex_labels(2)
        if edge_labels == None:
            edge_labels = self._new_edge_labels(2)
        dart1,dart2,dart3,dart4 = self._new_darts(4)

        # now split the darts at the specified vertex and add the new darts
        vertex_partition = self.vertex_partition()
        b_darts = vertex_partition.pop(vertex)
        for x in dart_set:
            b_darts.remove(x)
        vertex_partition[vertex_labels[0]] = dart_set+[dart1,dart3]
        vertex_partition[vertex_labels[1]] = b_darts+[dart2,dart4]

        edge_partition = self.edge_partition()
        edge_partition[edge_labels[0]]=[dart1,dart2]
        edge_partition[edge_labels[1]]=[dart3,dart4]
        
        return MyGraph(dart_partitions=[vertex_partition,edge_partition])

    def one_extension(self,edge,vertex,vertex_label=None,edge_labels=None):
        if vertex_label is None:
            vertex_label = self._new_vertex_labels(1)[0]
        if edge_labels is None:
            edge_labels = self._new_edge_labels(3)
        dart1,dart2,dart3,dart4 = self._new_darts(4)
        e1,e2,e3 = edge_labels

        vertex_partition = self.vertex_partition()
        vertex_partition[vertex_label] = [dart2,dart3,dart4]
        vertex_partition[vertex] += [dart1]

        edge_partition = self.edge_partition()

        de1,de2 = edge_partition.pop(edge)

        edge_partition[e1] = [de1,dart2]
        edge_partition[e2] = [dart3,de2]
        edge_partition[e3] = [dart4,dart1]

        return MyGraph(dart_partitions = [vertex_partition,edge_partition])

    def adjacencies(self,v1,v2,count=True):
        """if count is True returns the number of edges between the two vertices, otherwise returns a list of the edges. Not tested for loops but might work"""
        edges1 = {self.dart_to_edge[d] for d in self.vertex_partition()[v1]}
        edges2 = {self.dart_to_edge[d] for d in self.vertex_partition()[v2]}
        out = edges1.intersection(edges2)
        if count:
            return len(out)
        return out


    def subgraph_find(self,other,first_match_only=True):
        """finds a list of subgraphs of self that are isomorphic to other. returns a list of lists where each list represents a subset of the vertices of self that spans a subgraph isomorphic to other. If first_match_only is true returns as soon as it finds a subgrpah match"""
        self_skel = Graph(data=[self.vertices(),self.edges()],multiedges=False,loops=False)
        other_skel = Graph(data=[other.vertices(),other.edges()],multiedges=False,loops=False)

        potentials = list(self_skel.subgraph_search_iterator(other_skel))
        out = []
        for pot in potentials:
            mp = dict(zip(other.vertices(),pot))
            valid = True
            for e in other_skel.edges():
                #try:
                if self.adjacencies(mp[e[0]],mp[e[1]]) < other.adjacencies(e[0],e[1]):
                        valid = False
                        break
                #except:
                #    embed()
            if valid==True:
                out.append(pot)
                if first_match_only:
                    break
        return out

    def isomorphisms(self,other,first_match_only=True):
        if len(self.vertices())!=len(other.vertices()) or len(self.edges())!=len(other.edges()):
            return []
        return self.subgraph_find(other,first_match_only=first_match_only)


    def digon_split_extensions(self,no_isomorphs=False):
        out = []
        for v in self.vertices():
            for darts in subsets(self.vertex_partition()[v]):
                out.append(self.digon_split(v,darts))
        if no_isomorphs==False:
            out = MyGraph.isomorphism_class_reps(out)

        return out 

    def one_extensions(self,include_digon_splits=False,no_isomorphs=False):
        out = []
        for e in self.edges():
            for v in self.vertices():
                if v not in [e[0],e[1]] or include_digon_splits:
                    out.append(self.one_extension(e[2],v))
        if no_isomorphs==False:
            out = MyGraph.isomorphism_class_reps(out)
        return out

    def edge_deletion(self,edge_label):
        vert_part = self.vertex_partition()
        edge_part = self.edge_partition()
        d1,d2 = edge_part.pop(edge_label)
        v1 = self.dart_to_vertex[d1]
        vert_part[v1].remove(d1)
        v2 = self.dart_to_vertex[d2]
        vert_part[v2].remove(d2)
        return MyGraph(dart_partitions=[vert_part,edge_part])

    def vertex_deletion(self,vertex):
        vert_part = self.vertex_partition()
        edge_part = self.edge_partition()
        edge_labels = {self.dart_to_edge[d] for d in self.vertex_partition()[vertex]}
        for el in edge_labels:
            d1,d2 = edge_part.pop(el)
            v1 = self.dart_to_vertex[d1]
            vert_part[v1].remove(d1)
            v2 = self.dart_to_vertex[d2]
            vert_part[v2].remove(d2)
            
        vert_part.pop(vertex)
        return MyGraph(dart_partitions=[vert_part,edge_part])

    def matching_dart(self,dart):
        e = self.dart_to_edge[dart]
        l = [d for d in self.edge_partition()[e] if d != dart]
        return l[0]


    def find_divalent_vertex(self):
        """Note that this will return a vertex that is incident to a single loop edge.
        That obviously never happens for a (2,2)-tight graph"""
        for v in self.vertex_iterator():
            darts = self.vertex_partition()[v]
            if len(darts)==2:
                u0 = self.dart_to_vertex[self.matching_dart(darts[0])]
                u1 = self.dart_to_vertex[self.matching_dart(darts[1])]
                return (v,u0,u1)
        return None






    @classmethod
    def isomorphism_class_reps(cls,l):
        """return a list of reps of iso classes for the given list of MyGraph instnaces"""
        out = []
        while l:
            cand = l.pop()
            new = True
            for x in out:
                if len(cand.isomorphisms(x,first_match_only=True))>0:
                    new = False
                    break
            if new:
                out.append(cand)
        return out

    @classmethod
    def extensions_of(cls,obj):
        """returns a list of all digon ore one extensions of obj (or of all elements of obj if ibj is a list - recursively unpacking). Filters out all isomorphs"""
        if isinstance(obj,list):
            raw = []
            for g in obj:
                raw += cls.extensions_of(g)
        else:
            raw = obj.digon_split_extensions()+obj.one_extensions()

        return cls.isomorphism_class_reps(raw)

    @classmethod
    def dump(cls,mygraphs,fp):
        data = [ {"dart_partitions": [ x.vertex_partition(),x.edge_partition() ]} for x in mygraphs]
        json.dump(data,fp)

    @classmethod
    def load(cls,fp):
        data = json.load(fp)
        return [ cls(dart_partitions=x["dart_partitions"]) for x in data]










class PebbleGame(object):
    """ WARNING!!! THIS IS ONLY WORKING FOR l >= k AT THE MOMENT"""
    def __init__(self,vertex_set,k,l):
        """Create a (k,l) sparsity checker for graphs on a given vertex set"""
        self.k,self.l,self.vertex_set = k,l,vertex_set
        self.digraph = DiGraph(multiedges=True,loops=True)
        self.digraph.add_vertices(vertex_set)
        self.vertex_weights = { label: k for label in self.digraph.vertices()}

    def move_pebble_to(self,vertex_set):
        search_list = list(self.digraph.depth_first_search(vertex_set))
        for v in vertex_set:
            search_list.remove(v)

        search = iter(search_list)
        w = next(search)
        while self.vertex_weights[w] == 0:
            w = next(search)
        distances = [self.digraph.distance(x,w) for x in vertex_set]
        v = vertex_set[distances.index(min(distances))]
        p = self.digraph.shortest_path(v,w)
        for j in range(len(p)-1,0,-1):
            self.digraph.delete_edge(p[j-1],p[j])
            self.digraph.add_edge(p[j],p[j-1])
        self.vertex_weights[v]+=1
        self.vertex_weights[w]-=1


        """moves a pebble into vertex_set according to the allowed moves of the (k,l) pebble game"""

    def add_edge(self,u,v):
        while self.vertex_weights[u]+self.vertex_weights[v] < max(self.l+1,1):
            self.move_pebble_to([u,v])

        if u==v:
            raise ValueError('')
            # THIS IS A HUGE GAP!!!!!! ONLY WORKS IF l >=k 

        if self.vertex_weights[u] >=self.vertex_weights[v]:
            self.digraph.add_edge([u,v])
            self.vertex_weights[u] -=1
        else:
            self.digraph.add_edge([v,u])
            self.vertex_weights[v] -=1


    def run(self,graph,test_only=True,reset=True):
        if reset:
            self.__init__(self.vertex_set,self.k,self.l)
        for e in graph.edges():
            try:
                self.add_edge(e[0],e[1])
            except:
                if test_only:
                    return False
                else:
                    print("cannot add edge (%s,%s)"%(e[0],e[1]))
        return self.digraph




def get_test_graphs(f='tests/fixtures/dg.json'):
    with open(f,'r') as jsonfile:
        data = json.load(jsonfile)
    return {
            key: MyDiGraph(edges=data[key],multiedges=True)
            for key in data
    }


