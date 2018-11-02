
from sage.all import *
import time
import json

from IPython import embed

class NonUniqueLabelError(Exception):
    pass


class MyGraph(DiGraph):
    def __init__(self,dart_partitions=None,*args,**kwargs):
        if dart_partitions is not None:
            v_parts,e_parts = dart_partitions
            if isinstance(v_parts,dict):
                self.vertex_partition = v_parts
            else:
                self.vertex_partition = dict(zip(range(len(v_parts)),v_parts))

            if isinstance(e_parts,dict):
                self.edge_partition = e_parts
            else:
                self.edge_partition = dict(zip(range(len(e_parts)),e_parts))


            self.dart_to_vertex = {}
            for v in self.vertex_partition:
                for dart in self.vertex_partition[v]:
                    self.dart_to_vertex[dart] = v
            self.darts = self.dart_to_vertex.keys()

            edges = []
            for label in self.edge_partition.keys():
                edges.append((self.dart_to_vertex[self.edge_partition[label][0]],self.dart_to_vertex[self.edge_partition[label][1]],label))
            kwargs.pop('data',None)
            super(MyGraph,self).__init__(data=[self.vertex_partition.keys(),edges],multiedges=True,loops=True,*args,**kwargs)

        else:
            dg = DiGraph(*args,**kwargs)
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


    def digon_split(self,vertex,dart_set,vertex_labels=None,edge_labels=None):
        # first define labels if not given
        if vertex_labels == None:
            if isinstance(vertex,int) or isinstance(vertex,Integer):
                label = max([i for i in self.vertices() if isinstance(i,int) or isinstance(i,Integer)])+1
                vertex_labels = (vertex,label)
            else:
                vertex_labels = (vertex+'_1',vertex+'_2')

        if edge_labels == None:
            e_label = max([i for i in self.vertices() if isinstance(i,int) or isinstance(i,Integer)]+[0])+1
            edge_labels = (e_label,e_label+1)

        dart1 = max(self.darts)+1
        dart2,dart3,dart4 = dart1+1,dart1+2,dart1+3



        vertex_partition = copy(self.vertex_partition)
        b_darts = vertex_partition.pop(vertex)
        for d in dart_set:
            b_darts.remove(d)
        vertex_partition[vertex_labels[0]]=dart_set+[dart1,dart3]
        vertex_partition[vertex_labels[1]]=b_darts+[dart2,dart4]

        edge_partition = copy(self.edge_partition)
        edge_partition[edge_labels[0]]=[dart1,dart2]
        edge_partition[edge_labels[1]]=[dart3,dart4]
        return MyGraph(dart_partitions=[vertex_partition,edge_partition])





class MyDiGraph(DiGraph):
    """Subclass of DiGraph with methods for two cycle splitting and Hennberg 
    extensions. edges **must** have unique postive integer labels"""

    def __init__(self,edges=[],*args,**kwargs):
        super(MyDiGraph,self).__init__(*args,**kwargs)
        self.add_edges(edges)

    def assign_edge_labels(self):
        raw_edges=self.edges()
        labelled_edges = [ raw_edges[i][:2] + (i,) for i in range(len(self.edges()))]
        self.delete_edges(self.edges())
        self.add_edges(labelled_edges)


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


    def parallels(self):
        """return a list of pairs of vertices that have multiedges joining them - ignoring direction"""
        vertices = self.vertices()
        v = len(vertices)
        out = []
        for i in range(v):
            for j in range(i+1,v):
                edges1 = [e for e in self.edges_incident(vertices[i]) if vertices[j]==e[1] ]
                edges2 = [e for e in self.edges_incident(vertices[j]) if vertices[i]==e[1] ]
                if len(edges1)+len(edges2)>1:
                    out.append([vertices[i],vertices[j]])
        return out

    def parallels_graph(self):
        """returns the Graph object that has an edge between any pair of vertices that are connected by parallel edges in self"""
        g = Graph()
        g.add_edges(self.parallels())
        return g

    def multisubgraph_find(self,other,max_parallel=2):
        if max_parallel != 2:
            raise NotImplementedError('')
        self_g = Graph(self.edges(),multiedges=True)
        other_g= Graph(other.edges(),multiedges=True)
        out = []
        other_skel = Graph(other,multiedges=False)
        self_skel = Graph(self,multiedges=False)
        sk_list = list(self_skel.subgraph_search_iterator(other_skel))
        if len(sk_list) == 0: 
            return []
        for cpy in sk_list:
            #mapping = dict(zip(cpy,self.vertices()))
            mapping = dict(zip(other.vertices(),cpy))
            is_copy = True
            self_copy = Graph(multiedges=True)
            self_copy.add_edges(self.edges())
            #embed()
            for e in other.edges():
                m = [mapping[e[0]],mapping[e[1]]]
                if self_copy.has_edge(m[0],m[1]):
                    self_copy.delete_edge(m[0],m[1])
                else:
                    is_copy=False 
                    break
            if is_copy:
                out.append(cpy)
        return out

    def has_subgraph(self,l):
        if isinstance(l,list):
            for i in l:
                if self.has_subgraph(i):
                    return True
            return False
        if len(self.multisubgraph_find(l)) > 0:
            return True
        else:
            return False




    @classmethod
    def load(cls,path):
        with open(path,'r') as jsonfile:
            data = json.load(jsonfile)
        out = [cls(i) for i in data]
        return out

    @classmethod
    def structured_dump(cls,graph_list,path):
        uid=1
        data_list = [
                {
                    "id": i,
                    "degree_sequence": graph_list[i].degree_sequence(),
                    "edges": graph_list[i].edges()
                }
            for i in range(len(graph_list))]
        with open(path,'w') as jsonfile:
            out = json.dump(data_list,jsonfile)
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


