
from sage.all import *
#from sage.combinat.combination import Combinations
import time
import json


from sparsity import PebbleGame,MyGraph
from IPython import embed

class OrientedRotationSystem(object):
    """
sigma is a cycle decomposition of 
a permutation of darts and tau is a cycle decomposition of 
a fixed point free involution of darts. Note that the set of 
darts must be a set of distinct integers, so tau and sigma must be permutations of that set 
for example 
    r = OrientedRotationSystem([(1,2,3),(4,5,6),(7,8,9),(10,11,12)],[(1,4),(2,12),(3,8),(5,11),(6,7),(9,10)])
creates OrientedRotationSystem instance corresponding to a copy of K_4 embedded in the torus with a quadrilateral face and an octagonal face
"""
    def __init__(self,sigma,tau,vertex_labels=None):
        if isinstance(tau,PermutationGroupElement):
            tau = tau.cycle_tuples()
            sigma = sigma.cycle_tuples()
        if isinstance(tau,list):
            if isinstance(tau[0],list):
                tau = [tuple(x) for x in tau]
                sigma = [tuple(x) for x in sigma]
        self.darts = []
        for e in tau:
            self.darts.append(list(e)[0])
            self.darts.append(list(e)[1])
        self.number_of_darts = len(self.darts)
        self.perm_group = PermutationGroup([sigma,tau],domain=self.darts)
        self.perm_group = PermutationGroup([sigma,tau],domain=self.darts)
        self.sigma_perm,self.tau_perm = self.perm_group(sigma),self.perm_group(tau)
        self.sigma_group = self.perm_group.subgroup([self.sigma_perm])
        self.tau_group = self.perm_group.subgroup([self.tau_perm])
        self.rho_perm = self.sigma_perm*self.tau_perm
        self.rho_group = self.perm_group.subgroup([self.rho_perm])
        #try:
        #    self.rho_group = self.perm_group.subgroup([self.rho_perm])
        #except:
        #    embed()
        
        #default labels are min of each vertex cycle
        if vertex_labels is None:
            self.vertex_mapping = {min(c): c for c in sigma}
        else:
            self.vertex_mapping = dict(zip(vertex_labels,sigma))

        self.dart_to_vertex = {}
        for v in self.vertex_mapping:
            for i in self.vertex_mapping[v]:
                self.dart_to_vertex[i] = v
        self.cache = {}

    @classmethod
    def from_mygraph(cls,my_graph,isomorphs=True,irreducible_only=True):
        """my_graph is an instance of MyGraph"""
        vert_part = my_graph.vertex_partition()
        edge_part = my_graph.edge_partition().values()

        #mapping = { x: min(vert_part[x]) for x in vert_part} 
        #raw = [[cls( x , edge_part ),mapping] for x in list_of_cycles(vert_part.values())]
        raw = [cls( x , edge_part ) for x in list_of_cycles(vert_part.values())]
        rs_list = []
        for r in raw:
            # now check for isomorphs
            if r.genus() ==1:
                for e in rs_list:
                    if r.is_isomorphic(e):
                        break
                else:
                    if is_irreducible(r) or irreducible_only==False:
                        rs_list.append(r)
            else:
                pass
        return rs_list

    @classmethod
    def inductive_from_mygraph(cls,my_graph,graph_collection,ors_collection,irreducible_only=True):
        """collection is an ORSCollection instance. If my_graph
        has a vertex of degree 2, we delete it and look for ORS in 
        collection with this underlying grpah"""
        if irreducible_only==False:
            raise NotImplementedError
        dvs = my_graph.find_divalent_vertex()
        #embed()
        if dvs is None:
            return cls.from_mygraph(my_graph)

        #import pdb; pdb.set_trace()
        smaller_graph = my_graph.vertex_deletion(dvs[0])
        pair = graph_collection.get_isomorphs(smaller_graph)[0]
        gid,isom = pair[0],dict(pair[1])
        a1,a2 = isom[dvs[1]],isom[dvs[2]]

        #small_ors_list = ors_collection.select(graph_id = gid)

        small_ors_list = [x for x in ors_collection.data if x['mygraph'][1]==gid]
        #embed()

        out = []
        for r in small_ors_list:
            o = OrientedRotationSystem(r["sigma_perm"],r["tau_perm"])
            inverse = dict(r["mygraph"][2])
            mapping = { inverse[key]:key for key in inverse}
            auto_group = smaller_graph.automorphism_group()
            orbt = { (s(dvs[1]),s(dvs[2]) ) for s in auto_group}
            for p in orbt:
                l = o.facial_vertex_additions(mapping[isom[p[0]]],mapping[isom[p[1]]])
                out+=l

        # not filter for isomorphs
        fout = []
        for o in out:
            for r in fout:
                if o.is_isomorphic(r):
                    break
            else:
                fout.append(o)


        return fout

    @classmethod
    def maps_from_graph(cls,graph,max_f_vector=(0,0,0),max_genus=None,min_genus=None,irreducible=False):
        l = OrientedRotationSystem.from_graph(graph)
        o = []
        length = len(max_f_vector)
        for r in l:
            fd = r.f_vector(length)
            if min([max_f_vector[i]-fd[i] for i in range(length)]) >=0:
                o.append(r)
        if max_genus is not None:
            o = filter(lambda x: x.genus()<=max_genus,o)
        if min_genus is not None:
            o = filter(lambda x: x.genus()>=min_genus,o)
        if irreducible:
            o = filter(lambda x: is_irreducible(x),o)
        print("found %s matching oriented rotation systems for %s"%(len(o),str(graph)))
        return o

    @classmethod
    def from_digraphs(cls,digraphs,out_file=None,*args,**kwargs):
        if isinstance(digraphs,str):
            digraphs = MyDiGraph.load(digraphs)
        graphs = [Graph(x.edges(),multiedges=True,loops=True) for x in digraphs]

        return {
                g.copy(immutable=True) : OrientedRotationSystem.maps_from_graph(g,*args,**kwargs)
            for g in graphs
        }

    @classmethod
    def from_digraph_data(cls,in_file,out_file=None,*args,**kwargs):
        digraphs = MyDiGraph.load(in_file)
        graphs = [Graph(x.edges(),multiedges=True,loops=True) for x in digraphs]

        return {
                g.copy(immutable=True) : OrientedRotationSystem.maps_from_graph(g,*args,**kwargs)
            for g in graphs
        }

    def components(self):
        return self.perm_group.orbits()

    def vertices(self):
        return self.vertex_mapping.keys()

    def edges(self):
        es = [ (self.dart_to_vertex[t[0]],self.dart_to_vertex[t[1]],t) for t in self.tau_perm.cycle_tuples()]
        return es
        #return self.tau_group.orbits()

    def faces(self):
        if 'faces' not in self.cache:
            self.cache['faces']=self.rho_group.orbits()
        return self.cache['faces']

    def undirected_graph(self):
        """returns the underlying undirected graph object"""
        vertex_labels = self.vertex_mapping.keys()
        gr = Graph(multiedges=True,loops=True)
        gr.add_vertices(vertex_labels)
        gr.add_edges(self.edges())
        return gr

    def face_degrees(self):
        face_list = self.faces()
        return[len(i) for i in face_list]

    def face_of(self,dart):
        out = [dart]
        nxt = self.rho_perm(dart)
        while nxt != dart:
            out.append(nxt)
            nxt = self.rho_perm(nxt)
        return out

    def f_vector(self,length=4):
        fds = self.face_degrees()
        return tuple([fds.count(i+1) for i in range(length)])

    def genus(self):
        return (2 - len(self.faces())+len(self.edges())-len(self.vertices()))/2

    def edge_contraction(self,dart):
        """edge should be a transposition of darts. NB There is no validation that 
        the input is actually an edge"""
        u,v = dart,self.tau_perm(dart)
        e_transp = PermutationGroupElement([(u,v)])
        x = PermutationGroupElement([(v,self.sigma_perm(u))])
        y = PermutationGroupElement([(u,self.sigma_perm(v))])

        con_sigma = self.sigma_perm*x*y*e_transp
        con_tau = self.tau_perm*e_transp
        return OrientedRotationSystem(con_sigma,con_tau)

    def edge_insertion(self,dart1,dart2,new_darts=None):
        """dart1 and dart2 should be on the same face"""
        if new_darts is not None:
            new1,new2 = new_darts
        else:
            new1 = max(self.darts)+1
            new2 = new1+1
        x = PermutationGroupElement([(self.sigma_perm(dart1),new1)])
        y = PermutationGroupElement([(self.sigma_perm(dart2),new2)])
        e_perm = PermutationGroupElement([(new1,new2)])

        in_sig = self.sigma_perm*x*y
        in_tau = self.tau_perm*e_perm
        return OrientedRotationSystem(in_sig,in_tau)

    def edge_deletion(self,dart):
        group = SymmetricGroup(domain=self.darts)

        u,v = dart,self.tau_perm(dart)
        e_transp = group(PermutationGroupElement([(u,v)]))
        x = group(PermutationGroupElement([(u,self.sigma_perm(u))]))
        y = group(PermutationGroupElement([(v,self.sigma_perm(v))]))

        del_sig = group(self.sigma_perm)*x*y
        del_tau = group(self.tau_perm)*e_transp

        return OrientedRotationSystem(del_sig,del_tau)

    def quad_contraction(self,dart):
        """The orbit of dart should be a quadrilateral. Returns the rot sys 
        obtained by contracting the quad face""" 
        rho = self.sigma_perm*self.tau_perm
        u,v,w,x = dart,rho(dart),(rho**2)(dart),(rho**3)(dart)
        d1 = max(self.darts)+1
        d2 = d1+1
        p = self.edge_insertion(u,w,new_darts=[d1,d2]).edge_deletion(v).edge_deletion(x).edge_contraction(d1)
        return p

    def edge_break(self,dart,new_darts=None):
        """split an edge (defined by dart) into a new vertex and two edges"""
        if new_darts is not None:
            new1,new2 = new_darts
        else:
            new1 = max(self.darts)+1
            new2 = new1+1

        s_perm = PermutationGroupElement([(new1,new2)])
        edge = PermutationGroupElement([(dart,self.tau_perm(dart))])
        nes = PermutationGroupElement([(dart,new1),(self.tau_perm(dart),new2)])

        br_sig = self.sigma_perm*s_perm
        br_tau = self.tau_perm*edge*nes
        return OrientedRotationSystem(br_sig,br_tau)
    
    def vertex_addition(self,dart1,dart2,new_darts=None):
        if new_darts is not None:
            new1,new2,new3,new4=new_darts
        else:
            new1 = max(self.darts)+1
            new2,new3,new4 = new1+1,new1+2,new1+3
        return self.edge_insertion(dart1,dart2,new_darts=(new1,new2)).edge_break(new1,new_darts=(new3,new4))

    def facial_vertex_additions(self,vert1,vert2,min_new_face_degree=5):
        """Find all facial vertex additions to self at the given vertices.
        min_new_face_degree is what it says"""
        # first we convert the vertices to ints because of json storage issues
        vert1 = int(vert1)
        vert2 = int(vert2)

        cycle1,cycle2 = self.vertex_mapping[vert1],self.vertex_mapping[vert2]
        out = []
        for dart1 in cycle1:
            face = self.face_of(dart1)
            if len(face)< 2*min_new_face_degree - 4:
                pass
            else:
                for dart2 in face[min_new_face_degree-2:len(face)-min_new_face_degree+3]:
                    if dart2 in cycle2:
                        out.append(self.vertex_addition(dart1,dart2))
        return out

    def is_isomorphic(self,other,mapping=False,orientation_preserving=False):
        """isomorphism checker for OrientedRotationSystem instances. R
        """
        # first check that the numbers of darts match  
        if self.number_of_darts != other.number_of_darts:
            return False
        # now loop through all darts of self and look for an isomorphism that maps that dart to fixed dart of other
        m = min(other.darts)
        for i in self.darts:
            val = self.based_isomorphism(other,i,m,mapping=mapping)
            if val !=False:
                return val

        if orientation_preserving==False:
            rev = OrientedRotationSystem(other.sigma_perm.inverse().cycle_tuples(),other.tau_perm.cycle_tuples())
            #other.sigma_perm = other.sigma_perm.inverse()
            return self.is_isomorphic(rev,mapping=mapping,orientation_preserving=True)
        
        return False

    def based_isomorphism(self,other,self_dart,other_dart,mapping=False):
        dart_mapping = {self_dart:other_dart}
        mapped_darts = [self_dart]

        # extend the mapping over an orbit of a dart, 
        # check for conflicts with existing mapping (return false)
        # and extend the mapping to the darts at the other end of the edge
        # while checking for conflicts
        # remove all the darts of the orbit from the mapped_darts list
        # but don't remove the other ends of the edges!
        while len(mapped_darts)>0:
            s = mapped_darts[0]
            t = dart_mapping[s]
            s_cycle = cycle_of(self.sigma_perm,s)
            t_cycle = cycle_of(other.sigma_perm,t)
            if len(s_cycle)!=len(t_cycle):
                return False
            for i in range(len(s_cycle)):
                if s_cycle[i] in dart_mapping:
                    if dart_mapping[s_cycle[i]] != t_cycle[i]:
                        return False
                dart_mapping[s_cycle[i]]=t_cycle[i]
                try:
                    mapped_darts.remove(s_cycle[i])
                except:
                    pass
                if self.tau_perm(s_cycle[i]) in dart_mapping:
                    if dart_mapping[self.tau_perm(s_cycle[i])]!=other.tau_perm(t_cycle[i]):
                        return False
                else:
                    dart_mapping[self.tau_perm(s_cycle[i])]=other.tau_perm(t_cycle[i])
                    mapped_darts.append(self.tau_perm(s_cycle[i]))

        if mapping:
            return dart_mapping
        else:
            return True
    
    def mygraph(self):
        return MyGraph(dart_partitions=[{min(x):list(x) for x in self.sigma_perm.cycle_tuples()},self.tau_perm.cycle_tuples()])


def cycle_of(perm,n):
    cycles = perm.cycle_tuples()
    for a in cycles:
        if n in a:
            return a[a.index(n):]+a[:a.index(n)]
    return (n,)


def list_of_cycles(l,pattern=None):

    if len(l) == 1:
        e = l[0]
        return [[tuple(e[:1])+tuple(x)] for x in Permutations(e[1:]).list()]
    else:
        return [  i+j for j in list_of_cycles(l[1:]) for i in list_of_cycles(l[:1])] 


def is_irreducible(rot_sys):
    # first check for digons or triangles
    f = rot_sys.f_vector(4)
    if f[1]>0 or f[2]>0:
        return False
    if f[3]==0:
        return True
    quads = [q for q in rot_sys.faces() if len(q) == 4]
    for q in quads:
        # first we check that the quad is non degenerate - quad contractions won't work
        # but we know that a non degen quad is contractible from the theory
        vs ={rot_sys.dart_to_vertex[d] for d in q}
        if len(vs) < 4:
            return False
        # now check that non of the quad vertices have degree two - qaud contraction fails there
        for v in vs:
            if len(rot_sys.vertex_mapping[v])==2:
                return False
        s = rot_sys.quad_contraction(q[0]).undirected_graph()
        pg = PebbleGame(s.vertices(),2,2)
        if pg.run(s):
            return False
        t = rot_sys.quad_contraction(q[1]).undirected_graph()
        pg = PebbleGame(t.vertices(),2,2)
        if pg.run(t):
            return False
    return True


def merges(l,k):
    if len(l)==0:
        return [k]
    if len(k)==0:
        return [l]
    return [l[:1]+i for i in merges(l[1:],k)]+[k[:1]+j for j in merges(l,k[1:])]


def old_merges(l,k):
    """returns all possible merges of all perms of l and k """
    m = len(l)
    n = len(k)
    out = []
    for z in Combinations(m+n,m).list():
        mge = k
        for i in range(m):
            mge.insert(z[i],l[i])
        out.append(mge)
    return out


def get_test_ors(fp='tests/fixtures/ors.json'):
    with open(fp,'r') as d:
        data = json.load(d)
    return {
            key : OrientedRotationSystem(
                data[key]['sigma_data'],
                data[key]['tau_data']
            ) for key in data.keys()
    }



