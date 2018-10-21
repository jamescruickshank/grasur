
from sage.all import *
import time
import json


class NonUniqueLabelError(Exception):
    pass


class MyDiGraph(DiGraph):
    """Subclass of DiGraph with methods for two cycle splitting and Hennberg 
    extensions. edges **must** have unique postive integer labels"""

    def assign_edge_labels(self):
        for i in range(len(self.edges())):
            pass

    def get_edges_with_label(self,label):
        """return a list of edges with the given label"""
        return [e for e in self.edges() if e[2]==label]
        
    def get_edge_with_label(self,label):
        l = self.get_edges_with_label(label)
        if len(l)>1:
            raise NonUniqueLabelError()
        return l[0]



    def two_cycle_split(self, vertex, darts):
        """this needs all the edge labels to be unique. darts is a list of pairs (edge_label,j) where j is one of 0 or 1"""
        v = max(self.vertices())+1
        w = v+1
        l = max(self.edge_labels())+1
        other = MyDiGraph(self,multiedges=True,loops=True)
        other.add_vertices([v,w])
        for e in self.incoming_edges(vertex):
            label = e[2]
            if e[0]==e[1]:
                if (label,0) in  darts and (label,1) in darts:
                    other.add_edge(v,v,l)
                if (label,0) in  darts and (label,1) not in darts:
                    other.add_edge(v,w,l)
                if (label,0) not in  darts and (label,1) in darts:
                    other.add_edge(w,v,l)
                if (label,0) not in  darts and (label,1) not in darts:
                    other.add_edge(w,w,l)
            else:
                if (label,1) in darts:
                    other.add_edge(e[0],v,l)
                else:
                    other.add_edge(e[0],w,l)
            l+=1

        for e in self.outgoing_edges(vertex):
            label = e[2]
            if e[0]==e[1]:
                pass
            else:
                if (label,0) in darts:
                    other.add_edge(v,e[1],l)
                else:
                    other.add_edge(w,e[1],l)
            l+=1

        other.add_edges([(v,w,l),(w,v,l+1)])
        other.delete_vertex(vertex)
        return other


    def darts_at(self,vertex):
        return [(e[2],0) for e in self.outgoing_edges(vertex)]+[(e[2],1) for e in self.incoming_edges(vertex)]

    def in_list(self,graph_list):
        g = Graph(self)
        flag=False
        for c in graph_list:
            if g.is_isomorphic(Graph(c)):
                flag=True
                break
        return flag
 

    def edge_split(self,label,vertex):
        v = max(self.vertices())+1
        l = max(self.edge_labels())+1
        other = MyDiGraph(self,multiedges=True,loops=True)
        edge = other.get_edge_with_label(label)
        other.delete_edge(edge)
        other.add_edges([(edge[0],v,l),(v,edge[1],l+1),(v,vertex,l+2)])
        return other
    
    def extensions(self,graph_isomorphs=False):
        """returns a list of all digraphs obtained from self by applying either a single vertex to 2-cycle move or a single edge split. If graph_isomorphs==False then it filters out isomorphs"""
        out = []
        for v in self.vertices():
            for darts in subsets(self.darts_at(v)):
                new = self.two_cycle_split(v,darts)
                if new.in_list(out)==False:
                    out.append(new)
        for label in self.edge_labels():
            for v in self.vertices():
                new = self.edge_split(label,v)
                if new.in_list(out)==False:
                    out.append(new)
        return out

    @classmethod
    def load(cls,path):
        with open(path,'r') as jsonfile:
            data = json.load(jsonfile)
        out = [MyDiGraph(i) for i in data]
        return out

    @classmethod
    def dump(cls,graph_list,path):
        data_list = [ [ e for e in graph.edges()] for graph in graph_list]
        with open(path,'w') as jsonfile:
            out = json.dump(data_list,jsonfile)
        return out
    
    @classmethod
    def extend_list(cls,graph_list,out_file=None):
        """returns a list of all digraphs obtained by applying a single 
        extension move to one of the digraphs in the input list. Checks for 
        isomorphs and eliminates them"""
        if isinstance(graph_list,str):
            pass # probably not going to bother with this

        out = []
        for g in graph_list:
            exts = g.extensions()
            print("found %s extensions of %s id: %s"%(len(exts),str(g),str(id(g))))
            for h in exts:
                if h.in_list(out)==False:
                    out.append(h)
        if out_file is not None:
            return cls.dump(out,out_file)
        else:
            return out





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
        w = search.next()
        while self.vertex_weights[w] == 0:
            w = search.next()
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



